# Changelog

All notable changes to the `sdsi` plugin, newest first. See `VERSION` for the
current release and `sdsi:versioning` for what a version bump means.

## 🚧 Unreleased

### Added or New Features
(none)

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
(none)

## 🆕VERSION 1.0.0 📅 2026-09-23

### Added or New Features
- Topic skills, each growing independently in its own `SKILL.md`: `sdsi:workflow`, `sdsi:standards`, `sdsi:config`, `sdsi:secrets`, `sdsi:logging`, `sdsi:errors`, `sdsi:concurrency` (new topic), `sdsi:testing`, `sdsi:dependencies`, `sdsi:docs`, `sdsi:versioning`, `sdsi:deploy`.
- `sdsi:core` — the non-negotiable rules, the project profile (language and project type asked with AskUserQuestion and recorded in the project's `CLAUDE.md`), the review-first-or-just-apply question before changing existing code, the universal root layout, and the fixed order the skills run in.
- `sdsi:all` — runs every step in core's order, asking review-or-apply once for the whole run.
- `sdsi:deploy` asks the deploy target (containers recommended, not assumed).
- `scripts/python/release.py` — one scripted release chain: VERSION bump, CHANGELOG promotion, automatic TODO.md closure from "TODO #n" references in the notes, docs-only folding into the current version, and version-file sync — configured per project by an optional `scripts/git/release.json`.
- `tests/test_release.py` — unit tests plus end-to-end commits through the real hooks.

### Removed
- `sdsi:base` and `references/shared-context.md` — replaced by `sdsi:core` and the topic skills. Anything invoking `sdsi:base` must invoke `sdsi:core` (the rules) or `sdsi:all` (the full run) instead.
- `scripts/python/bump_changelog.py` — replaced by `scripts/python/release.py`. Projects that copied the old hook pair should copy all three scripts again.
- Section-number references ("SDSI §6") — skills are referenced by name (`sdsi:config`).

### Changed
- The standard is language-neutral: rules are applied in the project language's own idioms, chosen from the recorded profile, instead of assuming Python.
- `sdsi:web`, `sdsi:mw`, and `sdsi:cli` are project types: each owns its project's source layout, entry point, and design, and stays silent unless the profile names that type. They read only `sdsi:core` and point to topics by name.
- `TODO.md` items are numbered (`- [ ] #n`) so the release script can close them.
- The plugin moved out of the `claude-plugins` monorepo into its own repository (`jimmydagher/sdsi-plugin`), registered in the `claude-marketplace` marketplace (`jimmydagher/claude-marketplace`). Reinstall with `/plugin install sdsi@claude-marketplace`. (TODO #1)

### Bug/Issues/Fixes
- A docs-only commit now folds its Unreleased notes into the current version automatically; previously the hook skipped them and they were left in Unreleased.
- `.gitattributes` forces LF line endings, so the hooks run after a Windows checkout; `sdsi:versioning` now requires it in every project.
- The pre-commit hook probes each Python candidate by running it, so a Windows Store `python3` placeholder on PATH no longer breaks the hook.
- The marketplace is now `jtag-claude-marketplace` everywhere — name, repository (`jimmydagher/jtag-claude-marketplace`), and folder — because Claude Code rejects `claude-marketplace` as impersonating an official marketplace. The 1.0.0 install lines no longer work; use `/plugin marketplace add jimmydagher/jtag-claude-marketplace` then `/plugin install sdsi@jtag-claude-marketplace`.

