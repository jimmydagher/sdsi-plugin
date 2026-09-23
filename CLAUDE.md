# CLAUDE.md — sdsi plugin

## SDSI profile

- Language: Markdown (skills) + Python 3.9+ (release tooling in `scripts/python/`)
- Project type: other — a Claude Code skills plugin
- Deploy target: distributed package — published through the `claude-marketplace` marketplace

## Conventions

- **One topic, one file.** A topic's rules live only in `skills/<topic>/SKILL.md`. Never restate a topic's rule in another skill — point to it by name (`sdsi:config`).
- **Every skill's first action is reading `../core/SKILL.md`.** A new topic or project type also gets a row in core's §4 table (and §1 Step 2's type table for a project type).
- **Rules are language-neutral.** Language-specific idioms appear only in project-type skills, grouped under the framework they belong to (e.g. `sdsi:web` → Django).
- **Markdown is the product here**, so `scripts/git/release.json` narrows docs-only commits to `README.md`, `CHANGELOG.md`, `TODO.md`, `CLAUDE.md`, and `docs/` — a change to any `SKILL.md` is a release.
- **`.claude-plugin/plugin.json`'s version is synced from `VERSION` by the release script** — never edit it by hand.
- **Run the tests after touching the release scripts:** `python -m unittest discover tests` (local shell, repo root).
