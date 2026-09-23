# SDSI — Software Development Standard Instructions

A language-neutral development standard for Claude Code, split into skills
that each own one area and grow on their own. Every skill enforces the same
short core; project-type skills own layout; `sdsi:all` runs everything in a
fixed order.

## Install

```
/plugin marketplace add jimmydagher/claude-marketplace
/plugin install sdsi@claude-marketplace
```

## How it works

1. **Every skill reads `sdsi:core` first** — the non-negotiable rules.
2. **The project profile** (language, project type, deploy target) is asked
   once with `AskUserQuestion` and recorded in the project's `CLAUDE.md`
   under `## SDSI profile`. Rules are applied in that language's idioms.
3. **Before touching existing code, you're asked: review first, or just
   apply?** Review presents findings and waits; apply makes the changes.
4. **The release chain is scripted.** The AI writes notes to `CHANGELOG.md`'s
   Unreleased section; when you commit, the hooks bump `VERSION`, promote the
   notes, close the `TODO.md` items they reference, and set the commit
   message to the version.

## Skills

Run in this order by `sdsi:all`; each can also be run alone (e.g. "apply
`/sdsi:logging` to my project").

| # | Skill | Covers |
|---|---|---|
| 0 | `sdsi:core` | Non-negotiables, profile, review-or-apply, universal layout, the order |
| 1 | `sdsi:workflow` | Plan before code, INTENT/SPEC/PLAN, scope, new-project kickoff |
| 2 | `sdsi:web` · `sdsi:mw` · `sdsi:cli` | Project types — source layout, entry point, design (only the profile's type runs) |
| 3 | `sdsi:standards` | Naming, constants, comments, reuse, SOLID, typing, input validation |
| 4 | `sdsi:config` | Config files, schema, validation |
| 5 | `sdsi:secrets` | Secrets store, naming, rotation, redaction |
| 6 | `sdsi:logging` | Central logger, levels, destinations |
| 7 | `sdsi:errors` | Error hierarchy, fatal handler, retries, exit outcomes |
| 8 | `sdsi:concurrency` | Threads/async, timeouts, shutdown |
| 9 | `sdsi:testing` | Test layout, pyramid, meaningful coverage |
| 10 | `sdsi:dependencies` | Adding, pinning, scanning |
| 11 | `sdsi:docs` | README, `docs/`, numbered `TODO.md` |
| 12 | `sdsi:versioning` | `VERSION`, `CHANGELOG.md`, commits, the release hooks |
| 13 | `sdsi:deploy` | Deploy target (asked), local env, containers |
| — | `sdsi:all` | Everything above, in order |

From another plugin, invoke `sdsi:core` or `sdsi:all` by name.

## The release chain in a project

Copy these three files into the project and wire them (local shell, project
root):

```
scripts/git/pre-commit
scripts/git/commit-msg
scripts/python/release.py

git config core.hooksPath scripts/git
```

They need Python 3.9+ on `PATH`, whatever language the project uses. Full
behavior and the optional `scripts/git/release.json` settings are in
`skills/versioning/SKILL.md`.

## Developing this plugin

- This repo follows SDSI itself: see `CLAUDE.md` for its profile and
  conventions, `TODO.md` for outstanding work.
- Wire the hooks after cloning: `git config core.hooksPath scripts/git`.
- Test the release chain (local shell, repo root):
  `python -m unittest discover tests`.
- To grow a topic, edit only its `skills/<topic>/SKILL.md`. To add a topic
  or project type, add its folder and a row in `sdsi:core`'s tables.
