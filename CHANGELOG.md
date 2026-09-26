# Changelog

All notable changes to the `sdsi` plugin, newest first. See `VERSION` for the current release and `sdsi:versioning` for what a version bump means.

## 🚧 Unreleased

### Added or New Features
(none)

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
(none)

## 🆕VERSION 1.2.2 📅 2026-09-26

### Added or New Features
(none)

### Removed
(none)

### Changed
- Markdown formatting standards applied to the READMEs, docs, refs and skills (blank-line spacing only; no content changes).

### Bug/Issues/Fixes
(none)

## 🟩VERSION 1.2.1 📅 2026-09-26

### Added or New Features
- `ref/web.md` › `sdsi:config`: review the files and assets each environment needs when it's created, and create any that are missing (e.g. `favicon.ico`).

### Removed
(none)

### Changed
- Markdown across the plugin puts each paragraph and list item on one line (no hard wraps), and every code block names its language (`text`, `markdown`, `bash`).
- `sdsi:workflow`: "Verification has two levels" is a plain sentence instead of a bold line standing in for a heading.

### Bug/Issues/Fixes
- `ref/findings.md` and `sdsi:all`: a wrapped `+ cli` / `+ web` line rendered as a stray nested bullet; it's back in its sentence.

## 🟨VERSION 1.2.0 📅 2026-09-25

### Added or New Features
- `sdsi:core` non-negotiable: **confirm before anything destructive or bulk** — explicit approval with the scope stated (what, and how many), not carried over from one action to the next.
- `sdsi:workflow` gains **Size the steps** (a plan step should be finishable and verifiable in one session; split past ~30 minutes / ~5 files) and **Read what depends on it before changing it** (read callers first, match existing patterns, run tests after any removal).
- `sdsi:workflow` verification becomes **two-level**: did the change do its job, and did it break a guardrail (hook, script, lint/type config, `CLAUDE.md` rule, skill) — proved by running the guardrail against a known-bad input. Lint and type check are part of the check. The Review checklist covers all four.

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
(none)

## 🟧VERSION 1.1.0 📅 2026-09-23

### Added or New Features
- Every skill runs in **review** or **apply** mode: `/sdsi:<skill> [--review | --apply] [path]`, stated in plain language, or asked. Review scans the code against the skill, catalogs findings (ID, severity, effort, `file:line`, recommendation), presents them, and asks what to apply; apply changes the code directly and verifies it. (TODO #2)
- `ref/findings.md` — the shared review process (intake → catalog → present → ask → route), replacing the `code-reviewer` plugin's intake and catalog phases. `ref/` is a new folder for shared reference files read on demand.
- Findings not applied become numbered `TODO.md` items (`- [ ] #n [F-003 sdsi:errors] …`) that the release chain closes when fixed; a review can be exported to `docs/reviews/YYYY-MM-DD-<skill>.md`.
- `argument-hint` on every skill, so the flags are suggested as the command is typed.
- `sdsi:workflow` gains the Review checklist every other skill already had.
- Project-type companions — `ref/web.md`, `ref/mw.md`, `ref/cli.md` — rewritten as language-neutral guidance with one `## sdsi:<topic>` section per topic. Every skill detects the project type from the code (asking only when the evidence is mixed), then adds the companion's section for itself to its rules and its review lens; no section means nothing extra.

### Removed
- `sdsi:web`, `sdsi:mw`, and `sdsi:cli` skills — replaced by the companions above, which apply automatically instead of being invoked. Their layout/structure sections and Python/Django-specific rules are dropped: source layout now follows the language's and framework's conventions within core's universal invariants, and framework-specific lessons belong in the project's own `CLAUDE.md`.
- The project-type step from `sdsi:all`'s order — it now runs 12 steps (`sdsi:workflow` through `sdsi:deploy`).

### Changed
- `sdsi:core` Step 3 "review first, or just apply?" becomes "Resolve the mode" — flags, then plain language, then the question. `sdsi:all` resolves it once and, in review mode, produces one deduplicated report across all steps.
- `sdsi:errors`: the fatal-error handler becomes a **global error handler** every project must have — wired into the language's uncaught-error hooks, logging every unhandled error, keeping long-running processes alive (only the failing request or unit of work fails), and calling a list of pluggable reporters so a project can add a queue, ServiceNow, or a pager without editing the handler. New rule: try/catch only where the logic requires it; log-and-rethrow or log-and-continue blocks are findings.
- Changelog notes cite the finding IDs they apply, e.g. `(F-003)`.
- Apply mode writes changelog notes in `sdsi:versioning`'s template (creating `CHANGELOG.md` from it when missing) and leaves no verification scripts behind in the project.

### Bug/Issues/Fixes
(none)

## 🟥VERSION 1.0.0 📅 2026-09-23

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

