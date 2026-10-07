#!/usr/bin/env python3
"""SDSI release chain: VERSION bump, CHANGELOG promotion, TODO.md closure.

Run by scripts/git/pre-commit on every commit to the target branch — not
meant to be run by hand. The AI's only job in a release is writing bullets
into CHANGELOG.md's "## 🚧 Unreleased" section (referencing any TODO.md
item a change fixes as "TODO #<n>"); everything after the human approves
the code and commits is done here, deterministically:

  code commit       bump VERSION (PATCH, unless a new version is already
                    staged by hand) → promote Unreleased to a new version heading
                    → close referenced TODO.md items with that version →
                    sync any mirrored version files and the README's
                    version line → stage it all.
  docs-only commit  no bump → fold Unreleased into the current version's
                    entry and date it today → close referenced TODO.md items
                    with the current version → sync the README's version
                    line → stage it.

A commit with nothing in Unreleased — the human changed files without the
AI, so no one wrote notes — gets notes written from the staged diff before
either path runs: one plain-English bullet per changed file (added, removed,
renamed, edited with line counts), item by item for TODO.md, and the old and
new value for a hand-set VERSION, each tagged "_(from the diff)_". With
"auto_notes": false in the settings, a code commit with an empty Unreleased
is refused instead and a docs-only one leaves the changelog alone.

The README's version line is required by sdsi:versioning: a README.md
holding a line in the changelog's heading format ("## 🆕VERSION x.y.z
📅 YYYY-MM-DD") has it rewritten to the changelog's current heading. A
README without one is left untouched; review catches the missing line.

All three files live in meta/, the project's record — the root holds only
README.md (sdsi:core §3). A staged meta/VERSION is always a release,
whatever docs_patterns match.

scripts/git/commit-msg then overwrites the message with the version line.

A commit that would consume Unreleased notes (a release, or a docs-only
fold) is refused while any change is left out of it — a tracked file with
unstaged edits, or an untracked file git doesn't ignore — so notes never
ship in a version that lacks the work they describe. The release files
themselves don't count: this script rewrites and stages them.

Everything is computed before anything is written: on any error the files
are left untouched and the commit is refused (exit 1).

Per-project settings live in an optional scripts/git/release.json:
  {"docs_patterns": ["docs/*", "*.md"], "version_files": ["package.json"],
   "auto_notes": true}
docs_patterns decide what counts as a docs-only commit (fnmatch against
each staged path); version_files are JSON files whose top-level "version"
string is kept equal to VERSION; auto_notes (default true) turns notes
written from the diff on or off.
"""
import fnmatch
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Callable, Optional

# Keep VERSION_FILE in sync with scripts/git/commit-msg.
VERSION_FILE = "meta/VERSION"
CHANGELOG_FILE = "meta/CHANGELOG.md"
TODO_FILE = "meta/TODO.md"
README_FILE = "README.md"
SETTINGS_FILE = "scripts/git/release.json"

DEFAULT_DOCS_PATTERNS = ["docs/*", "*.md"]

# The files the release rewrites and stages itself — unstaged edits to them
# never make a commit partial.
RELEASE_FILES = frozenset({VERSION_FILE, CHANGELOG_FILE, TODO_FILE})
# How many left-behind paths a partial-commit refusal lists before counting the rest.
LISTED_PATHS = 10

# The fixed rotation every already-shipped entry's marker cycles through,
# wrapping back to the first after the last.
COLORS = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫"]

SUBSECTIONS = ["Added or New Features", "Removed", "Changed", "Bug/Issues/Fixes"]
NONE_MARKER = "(none)"
UNRELEASED_HEADING = "## 🚧 Unreleased"

UNRELEASED_RE = re.compile(r"^## 🚧 Unreleased\n(.*?)(?=^## |\Z)", re.M | re.S)
CURRENT_ENTRY_RE = re.compile(r"^(## 🆕VERSION [^\n]*\n)(.*?)(?=^## |\Z)", re.M | re.S)
CURRENT_VERSION_RE = re.compile(r"^## 🆕VERSION (\S+)", re.M)
CURRENT_DATE_RE = re.compile(r"^(## 🆕VERSION \S+ 📅 )\S+", re.M)
CURRENT_HEADING_RE = re.compile(r"^## 🆕VERSION \S+ 📅 \S+$", re.M)
TODO_REF_RE = re.compile(r"TODO #(\d+)")
OPEN_TODO_RE = r"^- \[ \] #{number} (.*)$"
DONE_TODO_RE = r"^- \[x\] #{number} "
JSON_VERSION_RE = re.compile(r'("version"\s*:\s*")[^"]*(")')
TODO_ITEM_RE = re.compile(r"^- \[( |x)\] #(\d+) (.*)$", re.M)

# Notes written from the diff when Unreleased is empty (see the header).
AUTO_NOTES_SETTING = "auto_notes"
AUTO_TAG = "_(from the diff)_"
# How much of a TODO item's text a note quotes before cutting it off.
QUOTED_CHARS = 80
# Git's ref for the staged version of a path ("git show :path").
INDEX = ""
# Which subsection a file's git status letter files it under; anything else is Changed.
STATUS_SUBSECTIONS = {"A": "Added or New Features", "D": "Removed"}
CHANGED = "Changed"

# One staged change: (git status letter, path, the path it was renamed from or "").
Change = tuple[str, str, str]
# Lines added and deleted in one file; None for a binary file.
LineCounts = tuple[Optional[int], Optional[int]]


class ReleaseError(Exception):
    """A reason to refuse the commit. The message is shown to the committer."""


def empty_body() -> str:
    """The body of a fresh, contentless Unreleased section.

    Output:
        str: every subsection heading followed by (none).
    """
    return "".join(f"\n### {name}\n{NONE_MARKER}\n" for name in SUBSECTIONS)


def unreleased_body(changelog: str) -> str:
    """The text between the Unreleased heading and the next '## ' heading.

    Input:
        changelog (str): CHANGELOG.md contents.
    Output:
        str: the section body.
    Raises:
        ReleaseError: the changelog has no Unreleased section.
    """
    match = UNRELEASED_RE.search(changelog)
    if match is None:
        raise ReleaseError(f"{CHANGELOG_FILE} has no '{UNRELEASED_HEADING}' section.")
    return match.group(1)


def parse_subsections(body: str) -> dict[str, list[str]]:
    """Split a version entry's body into its subsections' content lines.

    Input:
        body (str): text under a '## ' heading.
    Output:
        dict[str, list[str]]: subsection name → its lines, with (none)
        markers and surrounding blank lines removed. Every name in
        SUBSECTIONS is present, empty when the entry had nothing.
    """
    sections: dict[str, list[str]] = {name: [] for name in SUBSECTIONS}
    current = None
    for line in body.splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
            sections.setdefault(current, [])
        elif current is not None and line.strip() != NONE_MARKER:
            sections[current].append(line)
    for name, lines in sections.items():
        while lines and not lines[-1].strip():
            lines.pop()
        while lines and not lines[0].strip():
            lines.pop(0)
    return sections


def render_subsections(sections: dict[str, list[str]]) -> str:
    """Inverse of parse_subsections: a body with (none) for empty ones.

    Input:
        sections (dict[str, list[str]]): subsection name → content lines.
    Output:
        str: the rendered body, ending with a blank line.
    """
    parts = []
    for name, lines in sections.items():
        content = "\n".join(lines) if lines else NONE_MARKER
        parts.append(f"\n### {name}\n{content}\n")
    return "".join(parts) + "\n"


def has_entries(body: str) -> bool:
    """True if any subsection in body holds a bullet.

    Input:
        body (str): a version entry's body.
    Output:
        bool: whether there is anything to release.
    """
    return any(
        line.startswith("- ")
        for lines in parse_subsections(body).values()
        for line in lines
    )


def next_color(changelog: str) -> str:
    """The color the entry currently holding 🆕 takes when it's replaced.

    Input:
        changelog (str): CHANGELOG.md contents.
    Output:
        str: the next color in COLORS' rotation.
    """
    colored = re.findall(r"^## (?:" + "|".join(COLORS) + r")VERSION", changelog, re.M)
    return COLORS[len(colored) % len(COLORS)]


def promote(changelog: str, version: str, today: str) -> str:
    """Turn Unreleased into the new 🆕 version entry; roll the old 🆕 color.

    Input:
        changelog (str): CHANGELOG.md contents, with a non-empty Unreleased.
        version (str): the new version, e.g. "1.2.4".
        today (str): the release date, YYYY-MM-DD.
    Output:
        str: the updated changelog, with a fresh empty Unreleased on top.
    """
    body = unreleased_body(changelog)
    color = next_color(changelog)
    changelog = re.sub(r"^## 🆕VERSION", f"## {color}VERSION", changelog, count=1, flags=re.M)
    promoted = (
        f"{UNRELEASED_HEADING}\n{empty_body()}\n"
        f"## 🆕VERSION {version} 📅 {today}\n"
        f"{render_subsections(parse_subsections(body))}"
    )
    return UNRELEASED_RE.sub(lambda _: promoted, changelog, count=1)


def fold_into_current(changelog: str, today: str) -> str:
    """Move Unreleased's bullets into the current 🆕 entry (no version bump).

    The entry's 📅 moves to today, so it reads as the day of its latest change.

    Input:
        changelog (str): CHANGELOG.md contents.
        today (str): the commit date, YYYY-MM-DD.
    Output:
        str: the updated changelog, or the input unchanged when no version
        has been released yet (the notes then ride with the first release).
    """
    current = CURRENT_ENTRY_RE.search(changelog)
    if current is None:
        return changelog
    pending = parse_subsections(unreleased_body(changelog))
    merged = parse_subsections(current.group(2))
    for name, lines in pending.items():
        merged.setdefault(name, []).extend(lines)
    changelog = (
        changelog[: current.start(2)]
        + render_subsections(merged)
        + changelog[current.end(2):]
    )
    changelog = CURRENT_DATE_RE.sub(lambda heading: heading.group(1) + today, changelog, count=1)
    return UNRELEASED_RE.sub(
        lambda _: f"{UNRELEASED_HEADING}\n{empty_body()}\n", changelog, count=1
    )


def sync_readme(readme: str, changelog: str) -> str:
    """Rewrite the README's version line to the changelog's current heading.

    Input:
        readme (str): README.md contents.
        changelog (str): CHANGELOG.md contents, after this commit's changes.
    Output:
        str: the updated README, or the input unchanged when either file
        has no "## 🆕VERSION x.y.z 📅 YYYY-MM-DD" line.
    """
    current = CURRENT_HEADING_RE.search(changelog)
    if current is None:
        return readme
    return CURRENT_HEADING_RE.sub(lambda _: current.group(0), readme, count=1)


def todo_refs(body: str) -> list[int]:
    """The TODO.md item numbers an Unreleased body says it closes.

    Input:
        body (str): the Unreleased section body.
    Output:
        list[int]: distinct item numbers, ascending.
    """
    return sorted({int(number) for number in TODO_REF_RE.findall(body)})


def close_todos(todo: str, numbers: list[int], version: str, today: str) -> str:
    """Check off the given items and move them to the end of the Done section.

    Input:
        todo (str): TODO.md contents.
        numbers (list[int]): items to close.
        version (str): the version that closed them.
        today (str): the closing date, YYYY-MM-DD.
    Output:
        str: the updated TODO.md.
    Raises:
        ReleaseError: a referenced item is neither open nor already done.
    """
    closed = []
    for number in numbers:
        match = re.search(OPEN_TODO_RE.format(number=number), todo, re.M)
        if match is None:
            if re.search(DONE_TODO_RE.format(number=number), todo, re.M):
                continue  # already closed by an earlier commit
            raise ReleaseError(
                f"{CHANGELOG_FILE} references TODO #{number}, but {TODO_FILE} has no open item #{number}."
            )
        todo = todo[: match.start()] + todo[match.end() + 1:]
        closed.append(f"- [x] #{number} {match.group(1)} — completed {today} · VERSION {version}")
    if not closed:
        return todo
    todo = todo.rstrip("\n") + "\n"
    if not re.search(r"^## Done\s*$", todo, re.M):
        todo += "\n---\n\n## Done\n"
    return todo + "\n".join(closed) + "\n"


def quote(text: str) -> str:
    """A TODO item's text, shortened for a note and unable to close an item.

    Input:
        text (str): the item's text.
    Output:
        str: at most QUOTED_CHARS characters, with any "TODO #<n>" escaped to
        "TODO \\#<n>" — it renders the same, but a note left in Unreleased
        can't close that item at the next release.
    """
    if len(text) > QUOTED_CHARS:
        text = text[: QUOTED_CHARS - 1].rstrip() + "…"
    return TODO_REF_RE.sub(r"TODO \\#\1", text)


def todo_items(todo: str) -> dict[int, tuple[bool, str]]:
    """Every numbered item in a TODO.md.

    Input:
        todo (str): TODO.md contents.
    Output:
        dict[int, tuple[bool, str]]: item number → (checked off, its text).
    """
    return {int(number): (mark == "x", text) for mark, number, text in TODO_ITEM_RE.findall(todo)}


def describe_todo(before: str, after: str) -> list[str]:
    """What changed in TODO.md, item by item, in plain English.

    Input:
        before (str): TODO.md at HEAD ("" if it didn't exist).
        after (str): TODO.md as staged.
    Output:
        list[str]: one phrase per item added, removed, checked off, reopened,
        or reworded; empty when no item changed (only the layout did).
    """
    old, new = todo_items(before), todo_items(after)
    notes = []
    for number in sorted(old.keys() | new.keys()):
        if number not in old:
            notes.append(f"added item #{number} — {quote(new[number][1])}")
        elif number not in new:
            notes.append(f"removed item #{number} — {quote(old[number][1])}")
        elif new[number][0] and not old[number][0]:
            notes.append(f"checked off item #{number} by hand")
        elif old[number][0] and not new[number][0]:
            notes.append(f"reopened item #{number}")
        elif new[number] != old[number]:
            notes.append(f"reworded item #{number}")
    return notes


def describe_file(status: str, path: str, old_path: str, counts: LineCounts) -> str:
    """One staged file's change in plain English.

    Input:
        status (str): git's status letter (A, D, M, R, T, …).
        path (str): the file's path as staged.
        old_path (str): the path it was renamed from, or "".
        counts (LineCounts): lines added and deleted; None for a binary file.
    Output:
        str: e.g. "Edited `src/app.py` (+12 −3 lines)".
    """
    added, deleted = counts
    if status == "A":
        return f"Added `{path}`" + (f" ({added} lines)" if added is not None else "")
    if status == "D":
        return f"Removed `{path}`"
    size = f"+{added} −{deleted} lines" if added is not None else "binary"
    if status == "R":
        edited = f", edited ({size})" if added is None or added or deleted else ""
        return f"Renamed `{old_path}` to `{path}`{edited}"
    return f"Edited `{path}` ({size})"


def diff_notes(
    changes: list[Change],
    counts: dict[str, LineCounts],
    text_at: Callable[[str, str], str],
) -> dict[str, list[str]]:
    """Changelog notes describing a staged diff, for when no one wrote any.

    Input:
        changes (list[Change]): the staged changes, in git's order.
        counts (dict[str, LineCounts]): each staged path's line counts.
        text_at (Callable[[str, str], str]): (revision, path) → that file's
            text, "" when it doesn't exist; INDEX is the staged revision.
    Output:
        dict[str, list[str]]: subsection name → bullets, each tagged AUTO_TAG.
        Past LISTED_PATHS files the rest are counted, not listed.
    """
    sections: dict[str, list[str]] = {name: [] for name in SUBSECTIONS}
    for status, path, old_path in changes[:LISTED_PATHS]:
        subsection = STATUS_SUBSECTIONS.get(status, CHANGED)
        phrases = []
        if path == TODO_FILE and status != "D":
            phrases = [f"`{TODO_FILE}`: {note}" for note in describe_todo(
                text_at("HEAD", path), text_at(INDEX, path))]
            subsection = CHANGED
        elif path == VERSION_FILE and status == "M":
            old, new = text_at("HEAD", path).strip(), text_at(INDEX, path).strip()
            phrases = [f"`{VERSION_FILE}` set to {new} by hand (was {old})"]
        if not phrases:
            phrases = [describe_file(status, path, old_path, counts.get(path, (None, None)))]
        sections[subsection].extend(f"- {phrase} {AUTO_TAG}" for phrase in phrases)
    if len(changes) > LISTED_PATHS:
        sections[CHANGED].append(f"- … and {len(changes) - LISTED_PATHS} more file(s) {AUTO_TAG}")
    return sections


def with_unreleased(changelog: str, sections: dict[str, list[str]]) -> str:
    """Replace the Unreleased section's body.

    Input:
        changelog (str): CHANGELOG.md contents.
        sections (dict[str, list[str]]): subsection name → content lines.
    Output:
        str: the changelog with those sections under Unreleased.
    """
    return UNRELEASED_RE.sub(
        lambda _: f"{UNRELEASED_HEADING}\n{render_subsections(sections)}", changelog, count=1
    )


def bump_patch(version: str) -> str:
    """The next PATCH version.

    Input:
        version (str): a MAJOR.MINOR.PATCH version.
    Output:
        str: the same version with PATCH incremented.
    Raises:
        ReleaseError: the version isn't MAJOR.MINOR.PATCH.
    """
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if match is None:
        raise ReleaseError(f"{VERSION_FILE} holds '{version}', not MAJOR.MINOR.PATCH.")
    major, minor, patch = (int(part) for part in match.groups())
    return f"{major}.{minor}.{patch + 1}"


def set_json_version(text: str, path: str, version: str) -> str:
    """Rewrite the first "version" string in a JSON file's text.

    Input:
        text (str): the file's contents.
        path (str): the file's path, for the error message.
        version (str): the version to write.
    Output:
        str: the updated text.
    Raises:
        ReleaseError: the file has no "version" key.
    """
    updated, count = JSON_VERSION_RE.subn(rf"\g<1>{version}\g<2>", text, count=1)
    if count == 0:
        raise ReleaseError(f'{path} is listed in version_files but has no "version" key.')
    return updated


def is_docs_only(staged: list[str], patterns: list[str]) -> bool:
    """True if every staged path matches a docs pattern.

    Input:
        staged (list[str]): staged paths, relative to the repo root.
        patterns (list[str]): fnmatch patterns counting as documentation.
    Output:
        bool: whether the commit is docs-only.
    """
    return all(any(fnmatch.fnmatch(path, pattern) for pattern in patterns) for path in staged)


def git(*args: str) -> str:
    """Run a git command in the current directory and return its stdout."""
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True, encoding="utf-8", errors="replace"
    ).stdout


def git_text(revision: str, path: str) -> str:
    """A file's text at a revision (INDEX for the staged one), "" if it has none."""
    try:
        return git("show", f"{revision}:{path}")
    except subprocess.CalledProcessError:
        return ""


def staged_changes() -> list[Change]:
    """Every staged change against HEAD, renames detected.

    Output:
        list[Change]: (status letter, path, renamed-from path or "").
    """
    fields = git("diff", "--cached", "--name-status", "-M", "-z").split("\0")
    changes: list[Change] = []
    index = 0
    while index < len(fields) and fields[index]:
        status = fields[index][0]
        if status in "RC":
            changes.append((status, fields[index + 2], fields[index + 1]))
            index += 3
        else:
            changes.append((status, fields[index + 1], ""))
            index += 2
    return changes


def staged_line_counts() -> dict[str, LineCounts]:
    """Lines added and deleted in each staged file, keyed by its staged path.

    Output:
        dict[str, LineCounts]: path → (added, deleted); None for a binary file.
    """
    fields = git("diff", "--cached", "--numstat", "-M", "-z").split("\0")
    counts: dict[str, LineCounts] = {}
    index = 0
    while index < len(fields) and fields[index]:
        added, deleted, path = fields[index].split("\t", 2)
        index += 1
        if not path:  # a rename: the old and new paths follow as their own fields
            path = fields[index + 1]
            index += 2
        counts[path] = (None, None) if added == "-" else (int(added), int(deleted))
    return counts


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def left_behind() -> list[str]:
    """Changed paths this commit doesn't include: tracked files with unstaged
    edits, and untracked files git doesn't ignore.

    The release files are left out: the release rewrites and stages them
    itself, and notes written but not yet staged are the normal case, not a
    partial commit.

    Output:
        list[str]: repo-relative paths, sorted.
    """
    unstaged = git("diff", "--name-only").splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    return sorted({path for path in unstaged + untracked if path and path not in RELEASE_FILES})


def refuse_partial_commit(paths: list[str]) -> None:
    """Refuse a commit that would release the notes without all of the change.

    Input:
        paths (list[str]): left_behind() — what the commit doesn't include.
    Raises:
        ReleaseError: when any path was left behind, naming them.
    """
    if not paths:
        return
    listed = "\n    ".join(paths[:LISTED_PATHS])
    more = f"\n    … and {len(paths) - LISTED_PATHS} more" if len(paths) > LISTED_PATHS else ""
    raise ReleaseError(
        f"{len(paths)} changed file(s) aren't in this commit, but it would release every "
        f"note under '{UNRELEASED_HEADING}' — notes for work it doesn't contain:\n    "
        f"{listed}{more}\n  Stage the whole change (git add -A) and commit again, or commit "
        "--no-verify if this genuinely isn't a release."
    )


def run(root: Path, today: str) -> None:
    """Compute and write the release for whatever is staged under root.

    Input:
        root (Path): the repository root (the current directory).
        today (str): the release date, YYYY-MM-DD.
    Raises:
        ReleaseError: the commit must be refused; nothing was written.
    """
    staged = [line for line in git("diff", "--cached", "--name-only").splitlines() if line]
    if not staged:
        return

    settings_path = root / SETTINGS_FILE
    settings = json.loads(read(settings_path)) if settings_path.exists() else {}
    docs_patterns = settings.get("docs_patterns", DEFAULT_DOCS_PATTERNS)
    version_files = settings.get("version_files", [])
    auto_notes = settings.get(AUTO_NOTES_SETTING, True)

    for required in (VERSION_FILE, CHANGELOG_FILE):
        if not (root / required).exists():
            raise ReleaseError(
                f"There is no {required}. VERSION, CHANGELOG.md, and TODO.md live in meta/; "
                "a project that keeps them at the root moves them there (sdsi:versioning)."
            )

    changelog = read(root / CHANGELOG_FILE)
    pending = unreleased_body(changelog)
    # Taken before any notes are written from the diff: those quote TODO items,
    # and quoting one must never close it.
    refs = todo_refs(pending)
    if has_entries(pending):
        # The notes describe the whole change; releasing them from a commit that
        # holds only part of it strands the rest with nothing left to release.
        refuse_partial_commit(left_behind())
    elif auto_notes:
        # No one wrote notes — the human changed files without the AI. Notes
        # written from the diff describe exactly what's staged, so a partial
        # commit strands nothing.
        notes = diff_notes(staged_changes(), staged_line_counts(), git_text)
        changelog = with_unreleased(changelog, notes)
        pending = unreleased_body(changelog)
        written = sum(len(lines) for lines in notes.values())
        print(
            f"\n  No notes under '{UNRELEASED_HEADING}' — wrote {written} from the diff "
            f"into {CHANGELOG_FILE}.\n",
            file=sys.stderr,
        )
    todo_path = root / TODO_FILE
    if refs and not todo_path.exists():
        raise ReleaseError(f"{CHANGELOG_FILE} references TODO items, but there is no {TODO_FILE}.")

    current_version = read(root / VERSION_FILE).strip()
    version_staged = VERSION_FILE in staged
    writes: dict[Path, str] = {}

    # A staged version is always a release, even where docs_patterns match it.
    if not version_staged and is_docs_only(staged, docs_patterns):
        if not has_entries(pending):
            return
        version = current_version
        writes[root / CHANGELOG_FILE] = fold_into_current(changelog, today)
    else:
        if not has_entries(pending):
            raise ReleaseError(
                f"'{UNRELEASED_HEADING}' in {CHANGELOG_FILE} has no entries. Add a bullet "
                "describing this change under Added/Removed/Changed/Bug fixes, then commit "
                f"(or commit --no-verify if this genuinely isn't a release). Notes from the "
                f"diff are off: '{AUTO_NOTES_SETTING}' is false in {SETTINGS_FILE}."
            )
        # A version staged unchanged — moving the file does that — isn't a bump set
        # by hand; taken as one, it would write a second entry for a shipped version.
        released = CURRENT_VERSION_RE.search(changelog)
        hand_bumped = version_staged and (released is None or released.group(1) != current_version)
        version = current_version if hand_bumped else bump_patch(current_version)
        writes[root / VERSION_FILE] = version + "\n"
        writes[root / CHANGELOG_FILE] = promote(changelog, version, today)
        for path in version_files:
            writes[root / path] = set_json_version(read(root / path), path, version)

    if refs:
        writes[todo_path] = close_todos(read(todo_path), refs, version, today)

    readme_path = root / README_FILE
    if readme_path.exists():
        readme = read(readme_path)
        synced = sync_readme(readme, writes[root / CHANGELOG_FILE])
        if synced != readme:
            writes[readme_path] = synced

    for path, text in writes.items():
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    git("add", "--", *(str(path.relative_to(root)) for path in writes))


def main() -> int:
    """Entry point for scripts/git/pre-commit.

    Output:
        int: 0 when the commit may proceed, 1 when it's refused.
    """
    try:
        run(Path.cwd(), date.today().isoformat())
    except ReleaseError as error:
        print(f"\n  COMMIT REFUSED — {error}\n", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
