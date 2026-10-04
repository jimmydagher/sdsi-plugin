---
name: versioning
description: >
  SDSI's versioning, changelog, and commit standard — and the automated
  release chain that ties VERSION, CHANGELOG.md, TODO.md, and the commit
  message together. The AI writes notes to CHANGELOG's Unreleased section;
  when the human approves and commits, shipped git hooks bump the version,
  promote the notes, close the TODO items they reference, and write the
  version as the commit message. Covers version semantics, the changelog's
  fixed structure, git hygiene, .gitignore, and installing the hooks. Use
  when committing, releasing, setting up a repo, or reviewing version and
  changelog discipline. Reads sdsi:core first. Triggers on
  "/sdsi:versioning", "version bump", "changelog", "commit", "release".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Versioning, Changelog & Commits

Before anything else, read `../core/SKILL.md` and run its steps.

**Non-negotiable, on every project, from day one** — regardless of size, stack, or number of committers.

The chain's files live in `meta/`, the project's record — `meta/VERSION`, `meta/CHANGELOG.md`, `meta/TODO.md` — never at the root and never in `docs/` (core §3). Below, each is named without its folder.

## The release chain

```text
AI writes code
  → AI writes notes to CHANGELOG.md "🚧 Unreleased" (with "TODO #n" refs)
  → human reviews and approves the code, and commits
  → [pre-commit]  scripts/python/release.py:
        bump VERSION → promote Unreleased to the new version
        → close referenced TODO.md items → sync version files → stage
  → [commit-msg]  message overwritten with "VERSION x.y.z"
  → commit lands
```

**Everything after "human commits" is script, not AI.** The AI's part of a release is exactly two things:

1. **Write the Unreleased notes as the work happens** — one bullet per change, under the right subsection, written for whoever deploys the release. When a change fixes a `TODO.md` item, end the bullet with `(TODO #<n>)`; when it applies a finding from an SDSI review, cite the finding ID too (`(F-003)`).
2. **Never commit on its own.** The human's approval of the code is the trigger; the AI commits only when the human asks it to.

The AI never bumps `VERSION` for a PATCH, promotes the changelog, ticks `TODO.md` items, or composes a version commit message by hand — the scripts do that, so it happens the same way every time.

**A MAJOR or MINOR bump is the one manual step:** a diff can't tell PATCH from MINOR, so when the change warrants it, the AI proposes the bump, the human confirms, and the new number is written to `VERSION` and staged before committing. The script respects a staged bump as-is.

## Version semantics

One `meta/VERSION` file is the single source of truth, starting at `0.1.0`. Semantics follow **operational impact on whoever deploys it**:

| Bump | Means | Operator has to… |
|---|---|---|
| **MAJOR** | A deployed environment breaks until someone acts — a renamed/removed config key, a new required secret or grant, a removed operation, a renamed flag | Plan the deploy; read the whole entry |
| **MINOR** | New capability, existing behavior unchanged, but new required settings | Update config, then deploy |
| **PATCH** | Code only — no config or secret change | Drop it in |

Anything else that displays a version (`--version`, a package manifest) reads `VERSION` or is kept in sync by the script's `version_files` setting — never a second, hand-maintained version string.

## CHANGELOG.md

Written for **whoever deploys the release**, not whoever reviewed the diff. A commit describes a change; a changelog entry describes a release.

```markdown
# Changelog

All notable changes, newest first. See `VERSION` for the current release.

## 🚧 Unreleased

### Added or New Features
(none)

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
(none)

## 🆕VERSION 1.1.0 📅 2026-09-08

### Added or New Features
- <what's new, in plain language>

### Removed
- <what's gone, and what replaces it>

### Changed
- <what behaves differently — including anything an operator must do:
  a new config key, secret, or grant, right in the bullet>

### Bug/Issues/Fixes
- <what was broken, now fixed> (TODO #7)

## 🟥VERSION 1.0.0 📅 2026-08-15
...
```

- **🚧 Unreleased** sits permanently at the top and is the only section the AI edits. Log each change as it's made, not saved for the end.
- **Four fixed subsections, always in that order.** An empty one stays, marked `(none)`, so a reader never wonders whether it was skipped.
- **Exactly one 🆕** — the current version. Every shipped version gets a color square when it's replaced, cycling 🟥 🟧 🟨 🟩 🟦 🟪 🟫 and wrapping — assigned once, never changed.
- **📅 date** in `YYYY-MM-DD` — the day of the entry's latest change: the releasing commit, then any docs-only commit folded into it.
- **Only the 🆕 entry ever changes after release**, and only by a docs-only commit (below). Every older entry is final: a mistake there is corrected by a new version and a new entry, never a rewrite.
- **Code commit** → new version. **Docs-only commit** (by the script's `docs_patterns`) → no bump; the notes in Unreleased — one short sentence under Changed per document changed (`sdsi:docs`) — fold into the current 🆕 entry, and its 📅 moves to the day of the commit. With nothing in Unreleased (an edit to `TODO.md`, say), the changelog is left alone. The message becomes `VERSION x.y.z+k`, the k-th docs-only commit since x.y.z. `+k` is SemVer build metadata, so every tool still reads the version as x.y.z, and `VERSION` itself doesn't change.
- **A code commit with an empty Unreleased is refused.** Add the bullet, then commit. `--no-verify` is the escape hatch for a commit that genuinely isn't a release.
- **A commit referencing a `TODO #n` that doesn't exist is refused**, so a typo can't silently leave an item open.

## Commits and git hygiene

- **The commit message is the version, nothing else** — `VERSION x.y.z` for a release or `VERSION x.y.z+k` for a docs-only commit, overwritten by the hook. What changed lives only in `CHANGELOG.md`. `git log` reads as a clean version timeline.
- **Don't amend on `main`** — the hook labels an amend as a new docs-only commit (`+k`). Make a new commit instead.
- **Feature branches off `main`**, reviewed before merge. The hooks only act on the target branch (`main` by default, set in both hooks); a merge commit is exempt, since its commits were released on their own branch.
- **Promoting a build is a retag of the tested artifact**, never a rebuild.
- **No secrets in history, ever** — gitignore local secret files and use a secret-scanning pre-commit step where possible (`sdsi:secrets`).
- **`.gitignore` excludes everything that isn't reviewable source** — build/compiled output, caches, local environment files, scratch/log folders, editor backups, and any config rendered with real values by a deploy script. Use the language's standard ignore template as the base.
- **Repeat the changelog check server-side in CI**, where `--no-verify` can't reach.
- **Never hard-reset to undo a commit when the working tree may hold other uncommitted work** — it discards every uncommitted change, not just the commit. Use a soft or mixed reset unless the tree is known clean.

## Installing the release chain

This plugin ships the working, tested scripts. Copy them into the project — never rewrite them per project:

```text
<plugin>/scripts/git/pre-commit        → <project>/scripts/git/pre-commit
<plugin>/scripts/git/commit-msg        → <project>/scripts/git/commit-msg
<plugin>/scripts/git/commit-template   → <project>/scripts/git/commit-template
<plugin>/scripts/python/release.py     → <project>/scripts/python/release.py
```

Then, in the project root (local shell):

```bash
git config core.hooksPath scripts/git
git config commit.template scripts/git/commit-template
```

Put those commands in whatever script bootstraps local development, so a fresh clone gets them. The template pre-fills an editor's commit box (VS Code reads it), so committing never stops to ask for a message; on `main` the hook replaces it with the version line. Commit a `.gitattributes` containing `* text=auto eol=lf` (at minimum for `scripts/git/*`) — a hook checked out with Windows line endings fails to run. The scripts need Python 3.9+ on `PATH` whatever language the project itself is written in — they're repo tooling, not application code.

**Optional per-project settings** — `scripts/git/release.json`:

```json
{
  "docs_patterns": ["docs/*", "*.md"],
  "version_files": ["package.json"]
}
```

`docs_patterns` (fnmatch) decide what counts as docs-only; the default is shown. A staged `meta/VERSION` is always a release, even if a pattern matches it. A repo where Markdown *is* the product (a skills plugin, a docs site) narrows it to the true docs. `version_files` lists JSON files whose `"version"` is kept equal to `VERSION`.

**Test the hooks with a real, throwaway commit before trusting them** — don't reason from the scripts alone. The plugin's own `tests/test_release.py` does this end to end.

## Moving the release files out of the root

A project set up before the files lived in `meta/` keeps the old scripts working until it moves. The current scripts read only `meta/` and refuse a commit without `meta/VERSION` and `meta/CHANGELOG.md` — so the files and the scripts move together, in one commit:

1. **Move the files** (local shell, project root):

   ```bash
   mkdir meta
   git mv VERSION meta/VERSION
   git mv CHANGELOG.md meta/CHANGELOG.md
   git mv TODO.md meta/TODO.md
   ```

2. **Re-copy the scripts and run both config commands** (Installing, above) — never patch the old copies by hand.
3. **Fix `scripts/git/release.json`**, if the project has one — every `docs_patterns` entry for a moved file takes its new path (`CHANGELOG.md` → `meta/CHANGELOG.md`).
4. **Update everything that reads a moved file by path** — a build step that copies `VERSION` into the artifact, a `--version` implementation, the README, the docs index.
5. **Decide the bump.** The move stages `meta/VERSION` unchanged; the script reads that as no bump and makes the usual PATCH. For a MINOR or MAJOR, write the new number into `meta/VERSION` and stage it before committing (The release chain, above).
6. **Add an Unreleased bullet** under Changed, naming the move and anything an operator must update.
7. **Stage everything before committing** — `git add -A`, or every change in the editor's source-control view. `git mv` stages only the moves; a commit without the re-copied scripts and edited files ships old scripts that can't find the moved ones.

## Review checklist

No `VERSION`, `CHANGELOG.md`, or hooks installed · `VERSION`, `CHANGELOG.md`, or `TODO.md` anywhere but `meta/`, or scripts older than that layout · `core.hooksPath` or `commit.template` not set · changelog missing subsections or out of order · more than one 🆕 · an older (colored) entry rewritten, or the 🆕 one changed other than by a docs-only commit · a commit message that isn't a version line · `TODO.md` items closed by hand · a version string maintained in two places · build output or local env files tracked in git.
