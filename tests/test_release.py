"""Tests for scripts/python/release.py and the git hooks that call it.

Unit tests cover the text transforms; the end-to-end tests build a
throwaway git repo with the real hooks installed and commit through them,
since a hook is only proven by a real commit.

Run from the repo root:  python -m unittest discover tests
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
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
        result = release.fold_into_current(CHANGELOG)
        current = result.split("## 🆕VERSION 1.0.0")[1]
        self.assertIn("- Initial release.\n- New export command (TODO #2)", current)
        self.assertIn("### Bug/Issues/Fixes\n- Fixed crash on empty input (TODO #1)", current)
        self.assertFalse(release.has_entries(release.unreleased_body(result)))

    def test_fold_without_any_release_is_a_no_op(self) -> None:
        # Regression: before the first release there is no entry to fold into.
        unreleased_only = CHANGELOG.split("## 🆕VERSION")[0]
        self.assertEqual(release.fold_into_current(unreleased_only), unreleased_only)


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
        for relative in ("scripts/git/pre-commit", "scripts/git/commit-msg", "scripts/python/release.py"):
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / relative, target)
        self.write("VERSION", "1.0.0\n")
        self.write("CHANGELOG.md", CHANGELOG)
        self.write("TODO.md", TODO)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "seed")  # hooks not installed yet
        self.git("config", "core.hooksPath", "scripts/git")

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *args], cwd=self.repo, check=check, capture_output=True,
            text=True, encoding="utf-8",
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
        self.assertEqual(self.read("VERSION").strip(), "1.0.1")
        self.assertIn("## 🆕VERSION 1.0.1", self.read("CHANGELOG.md"))
        self.assertIn("- [x] #1 Crash on empty input", self.read("TODO.md"))
        self.assertIn("- [ ] #3 Unrelated item", self.read("TODO.md"))
        self.assertEqual(self.last_message(), "VERSION 1.0.1")
        self.assertEqual(self.git("status", "--porcelain").stdout, "")

    def test_code_commit_with_empty_unreleased_is_refused(self) -> None:
        self.write("CHANGELOG.md", release.promote(CHANGELOG, "1.0.1", TODAY))
        self.git("add", "CHANGELOG.md")
        self.git("commit", "-q", "-m", "x", "--no-verify")
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        result = self.git("commit", "-q", "-m", "x", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COMMIT REFUSED", result.stderr)

    def test_hand_staged_minor_bump_is_respected(self) -> None:
        self.write("VERSION", "1.1.0\n")
        self.write("src/app.txt", "code\n")
        self.git("add", "VERSION", "src/app.txt")
        self.git("commit", "-q", "-m", "x")
        self.assertEqual(self.read("VERSION").strip(), "1.1.0")
        self.assertEqual(self.last_message(), "VERSION 1.1.0")

    def test_docs_only_commit_folds_without_bump(self) -> None:
        self.write("docs/setup.md", "setup\n")
        self.git("add", "docs/setup.md")
        self.git("commit", "-q", "-m", "x")
        self.assertEqual(self.read("VERSION").strip(), "1.0.0")
        self.assertIn("- Initial release.\n- New export command (TODO #2)", self.read("CHANGELOG.md"))
        self.assertIn("completed", self.read("TODO.md"))
        self.assertEqual(self.last_message(), "VERSION 1.0.0-updated")

    def test_feature_branch_is_exempt(self) -> None:
        self.git("checkout", "-q", "-b", "feature")
        self.write("src/app.txt", "code\n")
        self.git("add", "src/app.txt")
        self.git("commit", "-q", "-m", "wip")
        self.assertEqual(self.read("VERSION").strip(), "1.0.0")
        self.assertEqual(self.last_message(), "wip")


if __name__ == "__main__":
    unittest.main()
