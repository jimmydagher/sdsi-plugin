"""Checks every skill's SKILL.md frontmatter against the limits hosts enforce.

claude.ai rejects (and truncates) a skill description over 1024 characters,
so a long description is caught here instead of in the plugin settings page.

Run from the repo root:  python -m unittest discover tests
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_DESCRIPTION = 1024


def description(skill_file: Path) -> str:
    """The skill's description, folded the way YAML folds a `>` block."""
    frontmatter = skill_file.read_text(encoding="utf-8").split("---")[1]
    match = re.search(r"^description:[ \t]*>?[ \t]*\n?(.*?)(?=^\S)", frontmatter, re.S | re.M)
    if match is None:
        return ""
    return " ".join(line.strip() for line in match.group(1).splitlines() if line.strip())


class SkillFrontmatterTest(unittest.TestCase):
    def test_descriptions_fit_the_host_limit(self):
        skills = sorted(ROOT.glob("skills/*/SKILL.md"))
        self.assertTrue(skills)
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                text = description(skill)
                self.assertTrue(text, "missing description")
                self.assertLessEqual(len(text), MAX_DESCRIPTION)


MAX_COMPANION_BULLETS = 7
SOURCES_HEADING = "## Sources"


def companion_blocks(companion: Path) -> dict:
    """Top-level bullet count of each `##`/`###` block, keyed by its heading."""
    counts, heading = {}, None
    for line in companion.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ") or line.startswith("### "):
            heading = line.strip()
            counts[heading] = 0
        elif heading and line.startswith("- "):
            counts[heading] += 1
    return counts


class CompanionTest(unittest.TestCase):
    """The companions are looked up by heading (core §1 Step 2), so the headings must stay exact."""

    def setUp(self):
        core = (ROOT / "skills/core/SKILL.md").read_text(encoding="utf-8")
        self.types = sorted(set(re.findall(r"`ref/(\w+)\.md`", core)) - {"findings"})
        self.skills = {path.parent.name for path in ROOT.glob("skills/*/SKILL.md")}

    def test_every_core_type_has_its_companion(self):
        self.assertTrue(self.types)
        for kind in self.types:
            with self.subTest(type=kind):
                self.assertTrue((ROOT / "ref" / f"{kind}.md").is_file())

    def test_companion_headings_name_real_skills(self):
        for kind in self.types:
            blocks = companion_blocks(ROOT / "ref" / f"{kind}.md")
            self.assertIn(SOURCES_HEADING, blocks, f"{kind}.md has no Sources")
            for heading in blocks:
                if heading.startswith("## ") and heading != SOURCES_HEADING:
                    with self.subTest(type=kind, heading=heading):
                        self.assertRegex(heading, r"^## sdsi:[a-z]+$")
                        self.assertIn(heading[len("## sdsi:"):], self.skills)

    def test_companion_blocks_stay_short(self):
        for kind in self.types:
            for heading, count in companion_blocks(ROOT / "ref" / f"{kind}.md").items():
                if heading != SOURCES_HEADING:
                    with self.subTest(type=kind, heading=heading):
                        self.assertLessEqual(count, MAX_COMPANION_BULLETS)


if __name__ == "__main__":
    unittest.main()
