---
name: optimize
description: >
  SDSI's lean-code standard, language-neutral — the ladder before writing
  code (needed at all → already in the codebase → standard library →
  platform feature → installed dependency → one line → only then the
  minimum), the size check after, reuse over reimplementation (DRY), the
  pass when a feature is finished (reuse, simplification, efficiency,
  altitude), the maintenance sweep for dead code, duplicates, and unused
  settings, flags, assets, and dependencies (proof before deleting, never
  deleting externally called code without asking), every element earning
  its place, performance tuning only from measurement, lazy loading of
  heavy modules, and marked shortcuts. Use when writing code, finishing a
  feature, doing maintenance, cleaning up, or making something faster.
  Reads sdsi:core first. Triggers on "/sdsi:optimize", "optimize", "dead
  code", "cleanup sweep", "remove unused code", "make it faster",
  "simplify this code".
argument-hint: "[--review|--apply] [path|branch]"
---

# SDSI: Optimize

Before anything else, read `../core/SKILL.md` and run its steps. Every rule here is applied in the project language's own idioms and tooling (core §1, Step 2).

Code is small because it's necessary, not because it's golfed; lower cost and faster runs are side effects, not the goal. The rules hold through the whole life of the code: the ladder before writing, the size check after, the pass when a feature is finished, and the sweep for maintenance. Drawn from Ponytail ([github.com/dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail)), Impeccable's `optimize` and `distill` ([github.com/pbakaus/impeccable](https://github.com/pbakaus/impeccable)), and Claude Code's `/simplify`.

**In review mode**, the scope decides the run: `branch` or a path reviews the changed code through the pass's lenses; the whole project is the sweep.

## Before writing: the ladder

First read the code the change touches and trace its real flow — lazy about the solution, never about reading. Then climb the ladder and stop at the first rung that solves it:

1. Is it needed at all?
2. Does the codebase already have it?
3. The standard library.
4. A native platform feature.
5. An already-installed dependency (a new one goes through `sdsi:dependencies`).
6. One line.
7. Only then the minimum that works, with a small test when it has logic (`sdsi:testing`).

**Lazy, not negligent.** The ladder never cuts trust-boundary validation, data-loss handling, security, or accessibility.

## After writing: the size check

Code far longer than the problem needs (200 lines that could be 50) gets rewritten before it's called done.

## Reuse over reimplementation

Before writing something, check whether the shared layer already provides it; a helper that doesn't quite fit is extended for everyone (core §2, "One front door per capability") — a capability implemented twice will eventually disagree with itself.

One source of truth for logic, constants, types, and validation rules. Refactor into a shared home the **second** time the same semantic rule appears — not preemptively, and not for code that merely looks similar but means something different (coincidental duplication stays).

## The pass — when a feature is finished

Run over the code the feature changed (scope `branch` by default), through four lenses:

- **Reuse** — something the codebase, standard library, or platform already provides; a rule now implemented twice (above).
- **Simplification** — needless indirection (a wrapper or interface with one caller), options nobody sets, deep nesting, dead branches, code that restates what a library already does.
- **Efficiency** — obvious waste: the same I/O, query, or computation repeated in a loop, reading everything to use one item, a collection that grows without bound.
- **Altitude** — logic at the wrong layer: a workaround in a caller that belongs in the shared front door (core §2), a business rule in an entry point or handler.

The pass removes what the change made unused — an import, a variable, a function. Pre-existing dead code it finds is mentioned, not deleted; it goes to a sweep (core §2, "No random or pointless changes"). Where the host has Claude Code's `/simplify`, it may run the pass with this skill's Review checklist as the lens.

## The sweep — maintenance

An AI agent treats dead code as a live pattern and copies it into new work, and every unused line is context it has to read. So unused and duplicated code gets removed, but only in a sweep, as a change of its own (core §2).

- **What it looks for:** unreferenced files, functions, exports, types, and constants; config keys nothing reads (`sdsi:config`); feature flags past their rollout; unused assets, styles, and tests for code that's gone; dependencies nothing imports (removed through `sdsi:dependencies`, lockfile and all); `shortcut:` markers whose revisit condition has come (below).
- **Start from a checkpoint.** The working tree is clean and the human has committed before anything is deleted, so one revert undoes the whole sweep.
- **List before deleting, with proof.** Every item is listed with the evidence that nothing uses it (a search with no callers, or the language's unused-code analyzer). Nothing is deleted until the human approves the list (core §2, "Confirm before anything destructive or bulk").
- **Merge duplicates.** The same rule implemented in two places becomes one shared function, and every caller moves to it (Reuse over reimplementation, above). Otherwise a bug fixed in one copy stays live in the other.
- **Start from `sdsi:security`'s inventory of entry points** (reused from the `sdsi:all` run, or built by its rule when this skill runs alone) and flag any that nothing calls.
- **Never delete code called from outside the codebase without asking.** That means webhooks, scheduled jobs, auth callbacks, queue consumers, plugin hooks, and anything invoked through configuration or reflection. A reference search can't see their callers, so they always look unused. The list marks them as external, not dead.
- **Every element earns its place.** A setting, flag, option, variant, or code path with no real user is a sweep item. Removing one a user or caller can see is a change in behavior: it goes through `sdsi:workflow` (design documents first) and gets a `Removed` changelog note saying why (`sdsi:versioning`).
- **Cadence.** A sweep runs on a regular schedule (weekly on an active project) and before a release: `/sdsi:optimize --review` over the whole project.

## Performance from measurement

- **Obvious waste is fixed without a benchmark** — the efficiency lens of the pass.
- **Tuning happens only on a path measured to be slow**, biggest bottleneck first. Caching, precomputation, parallelism, batching, or a lower-level rewrite is measured before and after — against the `SPEC.md` target when one exists (`sdsi:workflow`) — and the numbers are shown; one that adds complexity without a measured gain is reverted. Tuning code carries a comment with the reason and the measurement, so a later sweep doesn't simplify it away.
- **Load heavy or environment-specific modules lazily, by name from config**, so a deployment only pays for what it uses.
- **Speed never costs correctness, security, or accessibility.**

## Marked shortcuts

**A deliberate shortcut is marked `shortcut:`** with a comment saying what was skipped and when to revisit it (`shortcut: linear scan, fine under ~1k rows`). Each one also gets a line in `meta/TODO.md` (`sdsi:docs`), the one list of deferred work. A project may rename the tag in its `CLAUDE.md`. The sweep revisits them.

## Upkeep

The lines `sdsi:upkeep` installs in the project's `.claude/rules/sdsi.md`:

- Before writing code → read what it touches, then take the first rung that solves it: needed at all → in the codebase → standard library → platform → installed dependency → one line → the minimum; never cut validation, data-loss handling, security, or accessibility (`sdsi:optimize`)
- Finishing a feature → run the pass over the code it changed (reuse, simplification, efficiency, altitude) and remove what it made unused; leave pre-existing dead code for a sweep of its own (`sdsi:optimize`)
- Taking a deliberate shortcut → mark it with a `shortcut:` comment saying when to revisit it, and add it to `meta/TODO.md` (`sdsi:optimize`)
- Changing code for speed → measure the slow path before and after, and keep the change only with a measured gain (`sdsi:optimize`)
- Before deleting code that looks unused → have the human commit first, list each item with proof that nothing calls it, and wait for approval; never delete a webhook, scheduled job, auth callback, or anything else called from outside the codebase without asking (`sdsi:optimize`)
- Starting maintenance work or preparing a release → run `/sdsi:optimize --review` over the whole project (`sdsi:optimize`)

## Review checklist

Something built that the codebase, standard library, or platform already provides · code far longer than the problem needs · the same rule implemented twice · a local workaround instead of extending the shared helper · a wrapper or interface with one caller, or an option nobody sets · work repeated in a loop that could run once · reading everything to use one item · logic at the wrong layer · an import, variable, or function the change made unused and left behind · pre-existing dead code deleted in an unrelated change (core §2) · unused code, config keys, flags, assets, or dependencies piled up with no sweep · a sweep that deleted code without a listed proof and approval, or from an uncommitted tree · an externally invoked entry point (webhook, scheduled job, auth callback) deleted as unused · a route, page, or job that nothing calls left in place unflagged · a user-visible option removed without a design update or `Removed` changelog note · tuning with no before-and-after measurement, or kept without a gain · speed bought with correctness, security, or accessibility · a heavy or environment-specific module loaded eagerly · a deliberate shortcut with no `shortcut:` comment or TODO line · a `shortcut:` whose revisit condition has come and gone.
