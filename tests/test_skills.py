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


if __name__ == "__main__":
    unittest.main()
