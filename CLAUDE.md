# CLAUDE.md — sdsi plugin

## SDSI profile

- Language: Markdown (skills) + Python 3.9+ (release tooling in `scripts/python/`)
- Project type: other — a Claude Code skills plugin
- Deploy target: distributed package — published through the `jtag-claude-marketplace` marketplace

## Conventions

- **One topic, one file.** A topic's rules live only in `skills/<topic>/SKILL.md`. Never restate a topic's rule in another skill — point to it by name (`sdsi:config`).
- **Every skill's first action is reading `../core/SKILL.md`.** A new topic also gets a row in core's §4 table.
- **Project types are companions, not skills:** `ref/web.md`, `ref/mw.md`, `ref/cli.md`, one `## sdsi:<topic>` section per topic they add to — that heading is the lookup key core uses, so it must match the skill name exactly. A new project type gets a companion and a row in core §1 Step 2's type table.
- **Shared reference files live in `ref/`**, read on demand by relative path (`../../ref/<file>.md`) — e.g. `ref/findings.md`, the review process every skill follows in review mode. A skill's own rules still live only in its `SKILL.md`.
- **Every skill supports `--review` / `--apply`** through core §1 Step 3 and carries `argument-hint: "[--review|--apply] [path]"`; every skill needs a **Review checklist** section, since review mode uses it as the lens.
- **Rules are language-neutral — companions included.** Language- or framework-specific lessons belong in the project that taught them (its `CLAUDE.md`), not in this plugin.
- **Markdown is the product here**, so `scripts/git/release.json` narrows docs-only commits to `README.md`, `CHANGELOG.md`, `TODO.md`, `CLAUDE.md`, and `docs/` — a change to any `SKILL.md` is a release.
- **`.claude-plugin/plugin.json`'s version is synced from `VERSION` by the release script** — never edit it by hand.
- **Run the tests after touching the release scripts:** `python -m unittest discover tests` (local shell, repo root).
