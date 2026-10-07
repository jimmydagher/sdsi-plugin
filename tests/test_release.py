"""Tests for scripts/python/release.py and the git hooks that call it.

Unit tests cover the text transforms; the end-to-end tests build a
throwaway git repo with the real hooks installed and commit through them,
since a hook is only proven by a real commit.

Run from the repo root:  python -m unittest discover tests
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "python"))

import release  # noqa: E402

TODAY = "2026-09-23"

CHANGELOG = """# Changelog

Intro.

## 🚧 Unreleased

### Added or New Features
- New export command (TODO #2)

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
- Fixed crash on empty input (TODO #1)

## 🆕VERSION 1.0.0 📅 2026-09-01

### Added or New Features
- Initial release.

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
(none)
"""

TODO = """# TODO

- [ ] #1 Crash on empty input — reported by ops
- [ ] #2 Add an export command
- [ ] #3 Unrelated item

---

## Done

- [x] #0 Scaffold — completed 2026-09-01 · VERSION 1.0.0
"""


class PromoteTest(unittest.TestCase):
    def test_promote_creates_new_entry_and_rolls_color(self) -> None:
        # Regression: the old 🆕 must take the next color, and exactly one 🆕 remains.
        result = release.promote(CHANGELOG, "1.0.1", TODAY)
        self.assertIn("## 🆕VERSION 1.0.1 📅 2026-09-23", result)
        self.assertIn("## 🟥VERSION 1.0.0 📅 2026-09-01", result)
        self.assertEqual(result.count("🆕"), 1)

    def test_promote_leaves_fresh_empty_unreleased_on_top(self) -> None:
        result = release.promote(CHANGELOG, "1.0.1", TODAY)
        self.assertLess(result.index("## 🚧 Unreleased"), result.index("## 🆕VERSION 1.0.1"))
        self.assertFalse(release.has_entries(release.unreleased_body(result)))

    def test_promote_moves_bullets_to_new_version(self) -> None:
        result = release.promote(CHANGELOG, "1.0.1", TODAY)
        new_entry = result.split("## 🆕VERSION 1.0.1")[1].split("## 🟥")[0]
        self.assertIn("- New export command (TODO #2)", new_entry)
        self.assertIn("- Fixed crash on empty input (TODO #1)", new_entry)

    def test_color_rotation_wraps(self) -> None:
        # Regression: after 🟫 the rotation must wrap back to 🟥.
        shipped = "".join(f"## {color}VERSION 0.0.{i}\n" for i, color in enumerate(release.COLORS))
        self.assertEqual(release.next_color(shipped), "🟥")


class FoldTest(unittest.TestCase):
    def test_fold_appends_to_current_entry_and_replaces_none(self) -> None:
        result = release.fold_into_current(CHANGELOG, TODAY)
        current = result.split("## 🆕VERSION 1.0.0")[1]
        self.assertIn("- Initial release.\n- New export command (TODO #2)", current)
        self.assertIn("### Bug/Issues/Fixes\n- Fixed crash on empty input (TODO #1)", current)
        self.assertFalse(release.has_entries(release.unreleased_body(result)))

    def test_fold_dates_the_current_entry_by_the_change(self) -> None:
        # Regression: a docs change folded into 1.0.0 must move its date to the
        # day of the change, and leave every older entry's date alone.
        shipped = CHANGELOG + "\n## 🟥VERSION 0.9.0 📅 2026-08-01\n"
        result = release.fold_into_current(shipped, TODAY)
        self.assertIn("## 🆕VERSION 1.0.0 📅 2026-09-23\n", result)
        self.assertNotIn("2026-09-01", result)
        self.assertIn("## 🟥VERSION 0.9.0 📅 2026-08-01\n", result)

    def test_fold_without_any_release_is_a_no_op(self) -> None:
        # Regression: before the first release there is no entry to fold into.
        unreleased_only = CHANGELOG.split("## 🆕VERSION")[0]
        self.assertEqual(release.fold_into_current(unreleased_only, TODAY), unreleased_only)


class TodoTest(unittest.TestCase):
    def test_close_moves_items_to_end_of_done(self) -> None:
        result = release.close_todos(TODO, [1, 2], "1.0.1", TODAY)
        self.assertNotIn("- [ ] #1", result)
        self.assertNotIn("- [ ] #2", result)
        self.assertIn("- [ ] #3 Unrelated item", result)
        self.assertTrue(result.endswith(
            "- [x] #1 Crash on empty input — reported by ops — completed 2026-09-23 · VERSION 1.0.1\n"
            "- [x] #2 Add an export command — completed 2026-09-23 · VERSION 1.0.1\n"
        ))

    def test_unknown_reference_refuses(self) -> None:
        with self.assertRaises(release.ReleaseError):
            release.close_todos(TODO, [9], "1.0.1", TODAY)

    def test_already_done_reference_is_skipped(self) -> None:
        self.assertEqual(release.close_todos(TODO, [0], "1.0.1", TODAY), TODO)

    def test_done_section_created_when_missing(self) -> None:
        result = release.close_todos("# TODO\n\n- [ ] #1 Thing\n", [1], "0.1.1", TODAY)
        self.assertIn("## Done\n- [x] #1 Thing — completed", result)

    def test_refs_are_distinct_and_sorted(self) -> None:
        self.assertEqual(release.todo_refs("TODO #3 and TODO #1, again TODO #3"), [1, 3])


class ReadmeTest(unittest.TestCase):
    def test_sync_rewrites_the_version_line_to_the_current_heading(self) -> None:
        readme = "# App\n\n## 🆕VERSION 1.0.0 📅 2026-09-01\n\nSee the changelog.\n"
        result = release.sync_readme(readme, release.promote(CHANGELOG, "1.0.1", TODAY))
        self.assertEqual(result, "# App\n\n## 🆕VERSION 1.0.1 📅 2026-09-23\n\nSee the changelog.\n")

    def test_readme_without_a_version_line_is_untouched(self) -> None:
        readme = "# App\n\n## Install\n"
        self.assertEqual(release.sync_readme(readme, CHANGELOG), readme)


class HelpersTest(unittest.TestCase):
    def test_bump_patch(self) -> None:
        self.assertEqual(release.bump_patch("1.2.9"), "1.2.10")

    def test_bump_patch_rejects_non_semver(self) -> None:
        with self.assertRaises(release.ReleaseError):
            release.bump_patch("1.2")

    def test_docs_only(self) -> None:
        patterns = release.DEFAULT_DOCS_PATTERNS
        self.assertTrue(release.is_docs_only(["README.md", "docs/setup.txt"], patterns))
        self.assertFalse(release.is_docs_only(["README.md", "src/app.py"], patterns))

    def test_set_json_version(self) -> None:
        text = '{\n  "name": "x",\n  "version": "0.1.0"\n}\n'
        self.assertIn('"version": "0.2.0"', release.set_json_version(text, "p.json", "0.2.0"))

    def test_set_json_version_requires_key(self) -> None:
        with self.assertRaises(release.ReleaseError):
            release.set_json_version('{"name": "x"}', "p.json", "0.2.0")


class DiffNotesTest(unittest.TestCase):
    def test_describe_todo_names_each_item_change(self) -> None:
        after = TODO.replace("- [ ] #3 Unrelated item\n", "- [ ] #3 Unrelated item, reworded\n- [ ] #4 New idea\n")
        after = after.replace("- [ ] #2 Add an export command\n", "")
        self.assertEqual(release.describe_todo(TODO, after), [
            "removed item #2 — Add an export command",
            "reworded item #3",
            "added item #4 — New idea",
        ])

    def test_describe_todo_checked_off_by_hand(self) -> None:
        after = TODO.replace("- [ ] #1 Crash", "- [x] #1 Crash")
        self.assertEqual(release.describe_todo(TODO, after), ["checked off item #1 by hand"])

    def test_quoted_item_cannot_close_another(self) -> None:
        # Regression guard: a note left in Unreleased (no release yet) is scanned
        # for "TODO #n" at the next release; a quoted item must not close #1.
        quoted = release.quote("Follow-up to TODO #1")
        self.assertEqual(release.todo_refs(quoted), [])
        self.assertIn("TODO \\#1", quoted)

    def test_quote_shortens_long_text(self) -> None:
        quoted = release.quote("x" * 200)
        self.assertEqual(len(quoted), release.QUOTED_CHARS)
        self.assertTrue(quoted.endswith("…"))

    def test_describe_file(self) -> None:
        self.assertEqual(release.describe_file("A", "a.py", "", (4, 0)), "Added `a.py` (4 lines)")
        self.assertEqual(release.describe_file("D", "a.py", "", (0, 4)), "Removed `a.py`")
        self.assertEqual(release.describe_file("M", "a.py", "", (2, 1)), "Edited `a.py` (+2 −1 lines)")
        self.assertEqual(release.describe_file("M", "a.png", "", (None, None)), "Edited `a.png` (binary)")
        self.assertEqual(release.describe_file("R", "b.py", "a.py", (0, 0)), "Renamed `a.py` to `b.py`")
        self.assertEqual(
            release.describe_file("R", "b.py", "a.py", (1, 1)),
            "Renamed `a.py` to `b.py`, edited (+1 −1 lines)",
        )

    def test_diff_notes_files_each_change_under_its_subsection(self) -> None:
        texts = {
            ("HEAD", "meta/VERSION"): "1.0.0\n", (release.INDEX, "meta/VERSION"): "1.1.0\n",
            ("HEAD", "meta/TODO.md"): TODO, (release.INDEX, "meta/TODO.md"): TODO + "- [ ] #5 Later\n",
        }
        changes = [("A", "new.py", ""), ("D", "old.py", ""), ("M", "meta/VERSION", ""), ("M", "meta/TODO.md", "")]
        notes = release.diff_notes(changes, {"new.py": (3, 0)}, lambda rev, path: texts.get((rev, path), ""))
        tag = release.AUTO_TAG
        self.assertEqual(notes["Added or New Features"], [f"- Added `new.py` (3 lines) {tag}"])
        self.assertEqual(notes["Removed"], [f"- Removed `old.py` {tag}"])
        self.assertEqual(notes["Changed"], [
            f"- `meta/VERSION` set to 1.1.0 by hand (was 1.0.0) {tag}",
            f"- `meta/TODO.md`: added item #5 — Later {tag}",
        ])

    def test_diff_notes_counts_files_past_the_listing_limit(self) -> None:
        changes = [("M", f"f{i}.py", "") for i in range(release.LISTED_PATHS + 3)]
        notes = release.diff_notes(changes, {}, lambda rev, path: "")
        self.assertEqual(len(notes["Changed"]), release.LISTED_PATHS + 1)
        self.assertIn("… and 3 more file(s)", notes["Changed"][-1])


class HookEndToEndTest(unittest.TestCase):
    """Commits for real through the installed hooks in a throwaway repo."""

    def setUp(self) -> None:
        self.repo = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("config", "core.autocrlf", "false")
        for relative in (
            "scripts/git/pre-commit", "scripts/git/commit-msg",
            "scripts/git/commit-template", "scripts/python/release.py",
        ):
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / relative, target)
        self.write("meta/VERSION", "1.0.0\n")
        self.write("meta/CHANGELOG.md", CHANGELOG)
        self.write("meta/TODO.md", TODO)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "seed")  # hooks not installed yet
        self.git("config", "core.hooksPath", "scripts/git")

    def git(self, *args: str, check: bool = True, editor: str = "") -> subprocess.CompletedProcess:
        # The hooks' Python writes to a pipe here, in the locale's encoding unless
        # told otherwise (cp1252 on Windows), and the "—" in a refusal then fails
        # to decode as UTF-8 and loses stderr entirely.
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        if editor:
            env["GIT_EDITOR"] = editor
        return subprocess.run(
            ["git", *args], cwd=self.repo, check=check, capture_output=True,
            text=True, encoding="utf-8", env=env,
        )

    def write(self, relative: str, text: str) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)

    def read(self, relative: str) -> str:
        return (self.repo / relative).read_text(encoding="utf-8")

    def last_message(self) -> str:
        return self.git("log", "-1", "--format=%s").stdout.strip()

    def test_code_commit_runs_the_whole_chain(self) -> None:
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        self.git("commit", "-q", "-m", "anything typed here is replaced")
        self.assertEqual(self.read("meta/VERSION").strip(), "1.0.1")
        self.assertIn("## 🆕VERSION 1.0.1", self.read("meta/CHANGELOG.md"))
        self.assertIn("- [x] #1 Crash on empty input", self.read("meta/TODO.md"))
        self.assertIn("- [ ] #3 Unrelated item", self.read("meta/TODO.md"))
        self.assertEqual(self.last_message(), "VERSION 1.0.1")
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_code_commit_updates_the_readme_version_line(self) -> None:
        self.write("README.md", "# App\n\n## 🆕VERSION 1.0.0 📅 2026-09-01\n")
        self.git("add", "README.md")
        self.git("commit", "-q", "-m", "readme", "--no-verify")
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        self.git("commit", "-q", "-m", "x")
        self.assertEqual(
            self.read("README.md"),
            f"# App\n\n## 🆕VERSION 1.0.1 📅 {date.today().isoformat()}\n",
        )
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_docs_only_commit_redates_the_readme_version_line(self) -> None:
        self.write("README.md", "# App\n\n## 🆕VERSION 1.0.0 📅 2026-09-01\n")
        self.git("add", "README.md")
        self.git("commit", "-q", "-m", "readme", "--no-verify")
        self.write("docs/setup.md", "setup\n")
        self.git("add", "docs/setup.md")
        self.git("commit", "-q", "-m", "x")
        self.assertIn(f"## 🆕VERSION 1.0.0 📅 {date.today().isoformat()}\n", self.read("README.md"))
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def empty_unreleased(self) -> None:
        self.write("meta/CHANGELOG.md", release.promote(CHANGELOG, "1.0.1", TODAY))
        self.write("meta/VERSION", "1.0.1\n")
        self.git("add", "meta/CHANGELOG.md", "meta/VERSION")
        self.git("commit", "-q", "-m", "x", "--no-verify")

    def test_code_commit_with_empty_unreleased_releases_notes_from_the_diff(self) -> None:
        # TODO #17: a human's own change, with no notes written, still ships
        # with a changelog entry saying what changed.
        self.empty_unreleased()
        self.write("src/app.txt", "one\ntwo\n")
        self.git("add", "src/app.txt")
        result = self.git("commit", "-q", "-m", "x")
        self.assertIn("wrote 1 from the diff", result.stderr)
        self.assertEqual(self.last_message(), "VERSION 1.0.2")
        entry = self.read("meta/CHANGELOG.md").split("## 🆕VERSION 1.0.2")[1].split("## 🟧")[0]
        self.assertIn(f"### Added or New Features\n- Added `src/app.txt` (2 lines) {release.AUTO_TAG}", entry)
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_todo_edit_alone_folds_a_note_into_the_current_version(self) -> None:
        # TODO #17's own case: the human adds a TODO item and commits.
        self.empty_unreleased()
        self.write("meta/TODO.md", self.read("meta/TODO.md").replace(
            "- [ ] #3 Unrelated item\n", "- [ ] #3 Unrelated item\n- [ ] #4 Follow up on TODO #1\n"))
        self.git("add", "meta/TODO.md")
        self.git("commit", "-q", "-m", "x")
        self.assertEqual(self.last_message(), "VERSION 1.0.1+1")
        self.assertIn(
            f"- `meta/TODO.md`: added item #4 — Follow up on TODO \\#1 {release.AUTO_TAG}",
            self.read("meta/CHANGELOG.md").split("## 🆕VERSION 1.0.1")[1],
        )
        self.assertIn("- [ ] #1 Crash", self.read("meta/TODO.md"))  # quoting it didn't close it

    def test_written_notes_are_never_replaced_by_the_diff(self) -> None:
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        result = self.git("commit", "-q", "-m", "x")
        self.assertNotIn("from the diff", result.stderr)
        self.assertNotIn(release.AUTO_TAG, self.read("meta/CHANGELOG.md"))

    def test_code_commit_with_empty_unreleased_is_refused_when_auto_notes_are_off(self) -> None:
        self.write("scripts/git/release.json", '{"auto_notes": false}\n')
        self.git("add", "scripts/git/release.json")
        self.git("commit", "-q", "-m", "settings", "--no-verify")
        self.empty_unreleased()
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        result = self.git("commit", "-q", "-m", "x", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COMMIT REFUSED", result.stderr)

    def test_partial_commit_is_refused_while_it_would_release_the_notes(self) -> None:
        # Regression: with only part of a change staged, the commit took the
        # whole Unreleased section — notes for work it didn't contain — and
        # the next commit, carrying the rest, was refused for empty notes.
        self.write("src/staged.txt", "code\n")
        self.write("src/also.txt", "more\n")
        self.git("add", "src/staged.txt")
        result = self.git("commit", "-q", "-m", "x", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COMMIT REFUSED", result.stderr)
        self.assertIn("src/also.txt", result.stderr)
        self.assertEqual(self.read("meta/VERSION").strip(), "1.0.0")  # nothing released

    def test_partial_commit_is_refused_for_unstaged_edits_to_tracked_files(self) -> None:
        self.write("src/app.txt", "v1\n")
        self.git("add", "src/app.txt")
        self.git("commit", "-q", "-m", "x", "--no-verify")
        self.write("src/app.txt", "v2\n")
        self.write("src/other.txt", "new\n")
        self.git("add", "src/other.txt")
        result = self.git("commit", "-q", "-m", "x", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("src/app.txt", result.stderr)

    def test_unstaged_release_files_dont_count_as_a_partial_commit(self) -> None:
        # The hook stages CHANGELOG/VERSION/TODO itself; notes written but not
        # staged are the normal case, not a partial commit.
        changelog = self.read("meta/CHANGELOG.md").replace(
            "- New export command (TODO #2)", "- New export command, documented (TODO #2)"
        )
        self.write("meta/CHANGELOG.md", changelog)
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        self.git("commit", "-q", "-m", "x")
        self.assertEqual(self.last_message(), "VERSION 1.0.1")
        self.assertIn("documented", self.read("meta/CHANGELOG.md"))

    def test_partial_commit_is_allowed_when_it_releases_no_notes(self) -> None:
        # With nothing in Unreleased the notes come from the staged diff alone,
        # so committing part of the tree can't strand anyone's notes.
        self.write("meta/CHANGELOG.md", release.promote(CHANGELOG, "1.0.1", TODAY))
        self.git("add", "meta/CHANGELOG.md")
        self.git("commit", "-q", "-m", "x", "--no-verify")
        self.write("docs/guide.md", "guide\n")
        self.write("src/later.txt", "not yet\n")
        self.git("add", "docs/guide.md")
        self.git("commit", "-q", "-m", "x")
        self.assertIn("docs/guide.md", self.git("show", "--name-only", "--format=").stdout)

    def test_hand_staged_minor_bump_is_respected(self) -> None:
        self.write("meta/VERSION", "1.1.0\n")
        self.write("src/app.txt", "code\n")
        self.git("add", "meta/VERSION", "src/app.txt")
        self.git("commit", "-q", "-m", "x")
        self.assertEqual(self.read("meta/VERSION").strip(), "1.1.0")
        self.assertEqual(self.last_message(), "VERSION 1.1.0")

    def test_hand_staged_bump_is_a_release_even_when_docs_patterns_match_it(self) -> None:
        # Regression: with meta/* counted as docs, a hand-set bump plus a doc edit
        # folded the notes into 1.0.0 while commit-msg labelled the commit 1.1.0.
        self.write("scripts/git/release.json", '{"docs_patterns": ["docs/*", "meta/*"]}\n')
        self.git("add", "scripts/git/release.json")
        self.git("commit", "-q", "-m", "settings", "--no-verify")
        self.write("meta/VERSION", "1.1.0\n")
        self.write("docs/setup.md", "setup\n")
        self.git("add", "meta/VERSION", "docs/setup.md")
        self.git("commit", "-q", "-m", "x")
        self.assertIn("## 🆕VERSION 1.1.0", self.read("meta/CHANGELOG.md"))
        self.assertEqual(self.last_message(), "VERSION 1.1.0")

    def test_moved_version_file_gets_a_patch_bump(self) -> None:
        # Regression: a moved VERSION is staged unchanged; taken as a hand-set bump,
        # it wrote a second changelog entry for 1.0.0 (and then was refused outright).
        self.git("mv", "meta/VERSION", "VERSION")
        self.git("commit", "-q", "-m", "old root layout", "--no-verify")
        self.git("mv", "VERSION", "meta/VERSION")
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        self.git("commit", "-q", "-m", "")
        self.assertEqual(self.read("meta/VERSION").strip(), "1.0.1")
        self.assertEqual(self.read("meta/CHANGELOG.md").count("VERSION 1.0.0"), 1)
        self.assertIn("## 🆕VERSION 1.0.1", self.read("meta/CHANGELOG.md"))
        self.assertEqual(self.last_message(), "VERSION 1.0.1")

    def test_release_files_at_the_root_are_refused_with_a_pointer(self) -> None:
        # Regression: a project still on the root layout got a bare traceback.
        for name in ("VERSION", "CHANGELOG.md", "TODO.md"):
            self.git("mv", f"meta/{name}", name)
        self.git("commit", "-q", "-m", "old root layout", "--no-verify")
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        result = self.git("commit", "-q", "-m", "x", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COMMIT REFUSED — There is no meta/VERSION", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_docs_only_commit_folds_without_bump(self) -> None:
        self.write("docs/setup.md", "setup\n")
        self.git("add", "docs/setup.md")
        self.git("commit", "-q", "-m", "x")
        self.assertEqual(self.read("meta/VERSION").strip(), "1.0.0")
        self.assertIn("- Initial release.\n- New export command (TODO #2)", self.read("meta/CHANGELOG.md"))
        self.assertIn(f"## 🆕VERSION 1.0.0 📅 {date.today().isoformat()}\n", self.read("meta/CHANGELOG.md"))
        self.assertIn("completed", self.read("meta/TODO.md"))
        self.assertEqual(self.last_message(), "VERSION 1.0.0+1")

    def test_docs_only_labels_count_up_and_restart_after_a_release(self) -> None:
        # Regression: each docs-only commit needs its own label, counted from the
        # release it follows — never a repeat of an earlier one.
        for k, name in enumerate(("a", "b"), start=1):
            self.write(f"docs/{name}.md", f"{name}\n")
            self.git("add", f"docs/{name}.md")
            self.git("commit", "-q", "-m", "")
            self.assertEqual(self.last_message(), f"VERSION 1.0.0+{k}")
        changelog = self.read("meta/CHANGELOG.md")
        self.write("meta/CHANGELOG.md", changelog.replace(
            "### Added or New Features\n(none)", "### Added or New Features\n- Thing.", 1))
        self.write("src/app.txt", "code\n")
        self.git("add", "meta/CHANGELOG.md", "src/app.txt")
        self.git("commit", "-q", "-m", "")
        self.assertEqual(self.last_message(), "VERSION 1.0.1")
        self.write("docs/c.md", "c\n")
        self.git("add", "docs/c.md")
        self.git("commit", "-q", "-m", "")
        self.assertEqual(self.last_message(), "VERSION 1.0.1+1")

    def test_untouched_template_is_replaced_on_main(self) -> None:
        # Regression: git aborts a commit whose message is the untouched template
        # ("you did not edit the message"); on main the hook must replace it first,
        # so closing the editor without typing still commits.
        self.git("config", "commit.template", "scripts/git/commit-template")
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        self.git("commit", "-q", editor="true")
        self.assertEqual(self.last_message(), "VERSION 1.0.1")

    def test_feature_branch_is_exempt(self) -> None:
        self.git("checkout", "-q", "-b", "feature")
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        self.git("commit", "-q", "-m", "wip")
        self.assertEqual(self.read("meta/VERSION").strip(), "1.0.0")
        self.assertEqual(self.last_message(), "wip")


if __name__ == "__main__":
    unittest.main()
