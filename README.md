# SDSI — Software Development Standard Instructions

A language-neutral development standard for Claude Code, split into skills that each own one area and grow on their own. Every skill enforces the same short core; each adds web, middleware, or CLI guidance automatically when the project is that type; `sdsi:all` runs everything in a fixed order.

## Install

```text
/plugin marketplace add jimmydagher/jtag-claude-marketplace
/plugin install sdsi@jtag-claude-marketplace
```

## How it works

1. **Every skill reads `sdsi:core` first** — the non-negotiable rules.
2. **The project profile** (language, project type, deploy target) is recorded in the project's `.claude/CLAUDE.md` under `## SDSI profile` — the project type is detected from the code, anything unclear is asked once. Rules are applied in that language's idioms.
3. **Project-type companions add to every skill automatically.** For a web, middleware (`mw`), or CLI project, each skill also applies its section of `ref/web.md`, `ref/mw.md`, or `ref/cli.md` — "review my project for error handling" on a CLI adds the CLI's exit-code rules. No section for that skill means nothing extra.
4. **Every skill runs in review or apply mode** — pass it, or you're asked:

   ```text
   /sdsi:<skill> [--review | --apply] [path]
   /sdsi:errors --review src/payments
   /sdsi:all --apply
   ```

**Review** scans the code against the skill, catalogs findings (ID, severity, effort, `file:line`, recommendation), shows them, and asks what to apply. Findings you don't apply go to `TODO.md`; you can export the report to `docs/reviews/`. **Apply** changes the code to meet the skill directly and verifies it.

5. **The release chain is scripted.** The AI writes notes to `CHANGELOG.md`'s Unreleased section; when you commit, the hooks bump `VERSION`, promote the notes, close the `TODO.md` items they reference, and set the commit message to the version.

## Skills

Run in this order by `sdsi:all`; each can also be run alone (e.g. "apply `/sdsi:logging` to my project").

| # | Skill | Covers |
|---|---|---|
| 0 | `sdsi:core` | Non-negotiables, profile, project type, review/apply mode, universal layout, the order |
| 1 | `sdsi:workflow` | Plan before code, the living design documents (`docs/design/` INTENT/SPEC/PLAN), scope, new-project kickoff |
| 2 | `sdsi:standards` | Naming, constants, comments, reuse, SOLID, typing, input validation |
| 3 | `sdsi:config` | Config files, schema, validation |
| 4 | `sdsi:secrets` | Secrets store, naming, rotation, redaction |
| 5 | `sdsi:logging` | Central logger, levels, destinations |
| 6 | `sdsi:errors` | Global error handler, try/catch discipline, error hierarchy, retries, exit outcomes |
| 7 | `sdsi:concurrency` | Threads/async, timeouts, shutdown |
| 8 | `sdsi:testing` | Test layout, pyramid, meaningful coverage |
| 9 | `sdsi:dependencies` | Adding, pinning, scanning |
| 10 | `sdsi:docs` | README, `docs/`, numbered `TODO.md` |
| 11 | `sdsi:versioning` | `VERSION`, `CHANGELOG.md`, commits, the release hooks |
| 12 | `sdsi:deploy` | Deploy target (asked), local env, containers |
| — | `sdsi:all` | Everything above, in order |

From another plugin, invoke `sdsi:core` or `sdsi:all` by name.

## The release chain in a project

Copy these four files into the project and wire them (local shell, project root):

```text
scripts/git/pre-commit
scripts/git/commit-msg
scripts/git/commit-template
scripts/python/release.py

git config core.hooksPath scripts/git
git config commit.template scripts/git/commit-template
```

On `main`, every commit message is written for you: `VERSION x.y.z` for a release, `VERSION x.y.z+k` for the k-th docs-only commit after it. The template pre-fills the editor's commit box, so just commit.

They need Python 3.9+ on `PATH`, whatever language the project uses, and read `VERSION`, `CHANGELOG.md`, and `TODO.md` from `meta/` — SDSI keeps only `README.md` at the root. Full behavior, the optional `scripts/git/release.json` settings, and the steps for moving an older project's files out of the root are in `skills/versioning/SKILL.md`.

## Developing this plugin

- This repo follows SDSI itself: see `.claude/CLAUDE.md` for its profile and conventions, `meta/TODO.md` for outstanding work, `meta/CHANGELOG.md` for releases.
- Wire the hooks after cloning: `git config core.hooksPath scripts/git` and `git config commit.template scripts/git/commit-template`.
- Test the release chain (local shell, repo root): `python -m unittest discover tests`.
- To grow a topic, edit only its `skills/<topic>/SKILL.md`; to grow a project type, edit its `ref/<type>.md` under the `## sdsi:<topic>` heading it adds to. To add a topic, add its folder and a row in `sdsi:core` §4; to add a project type, add `ref/<type>.md` and a row in core §1 Step 2.
