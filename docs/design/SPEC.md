# SPEC — sdsi plugin

## TTD017 — Ponytail-inspired coding discipline

Source reviewed: https://github.com/dietrichgebert/ponytail (MIT, "the best code is the code you never wrote"; benchmark figures are self-reported, so none are copied in).

### What SDSI already has (not repeated)
`sdsi:core` §2 already covers no over-engineering (with a post-write size check), no assumptions, standard library first, one front door, and no pointless changes; `sdsi:standards` covers reuse over reimplementation and dead code.

### Behavior changes (the gaps Ponytail fills)
1. **The ladder** — before writing code, stop at the first rung that solves it: needed at all → already in the codebase → standard library → native platform feature → already-installed dependency → one line → only then the minimum that works. New dependencies stay governed by `sdsi:dependencies`; the ladder only points to it. Lives in `sdsi:optimize` (TTD022); core §2 keeps the one-line principle.
2. **Read before cutting** — the ladder runs after reading the code the change touches and tracing the real flow; lazy about the solution, never about reading. Lives with the ladder in `sdsi:optimize`.
3. **Lazy, not negligent** — the ladder never removes trust-boundary validation, data-loss handling, security, or accessibility. Stated in core §2's principle and in `sdsi:optimize`.
4. **Tests for risky logic** — code with a branch, loop, parser, money handling, or security meaning gets at least one small test; a pointer from core, the rule itself lives in `sdsi:testing` (add/confirm there, no restating).
5. **Honest reporting** — every finished change states what was skipped or not checked and the known risks. Lives in `sdsi:workflow`, one place only.
6. **Marked shortcuts** — a deliberate shortcut gets a `shortcut:` comment saying when to revisit it; the tag word may be overridden in the project's `CLAUDE.md`. Collected into outstanding work via `meta/TODO.md` (`sdsi:docs`) rather than a new ledger command, to avoid a second list. Lives in `sdsi:optimize` (TTD022), whose sweep revisits them.
7. **Review checklists** — the touched skills' Review checklists gain the matching smells (built before checking existing code, a shortcut with no `shortcut:` note, risky logic with no test, a final report that omits what was skipped).

### Explicitly not adopted
- Intensity levels (`lite/full/ultra`), `/ponytail-*` commands, the benchmark scoreboard, and the separate audit/debt/gain commands: SDSI already has `--review`/`--apply` and `meta/TODO.md`.
- Installing or depending on the ponytail plugin itself.

### Constraints
- One topic, one file; language-neutral; skill descriptions ≤ 1024 chars; changelog entries cite `TTD017`; no hand edits to `plugin.json` version.

## TTD022 — `sdsi:optimize`: one topic for lean, simple, fast code (TODO #22)

Sources reviewed: Ponytail (https://github.com/dietrichgebert/ponytail, MIT — already absorbed by TTD017), Impeccable (https://github.com/pbakaus/impeccable, Apache-2.0 — its `optimize`, `distill`, and `extract` references; only the language-neutral ideas are taken, no text copied, and its UI-design commands stay out), and Claude Code's built-in `/simplify` (its four lenses: reuse, simplification, efficiency, altitude).

### Goal
The rules that keep code small, simple, and fast are spread across `sdsi:core` §2, `sdsi:standards`, `sdsi:dependencies`, and `ref/cli.md`. They move into one new topic, `sdsi:optimize`, which:
- **runs in `sdsi:all`** as its own step;
- **holds through the whole coding lifecycle** — its `## Upkeep` lines (installed by `sdsi:upkeep`) fire before writing code, when a feature is finished, when a shortcut is taken, when code is changed for speed, and before deleting anything;
- **is re-run on its own for maintenance** — `/sdsi:optimize --review` over the whole project is the cleanup sweep (lists dead code, duplicates, and waste with proof); `--apply` removes what the human approves.

### What moves (one topic, one file)

| Rule | From | To | What stays behind |
|---|---|---|---|
| The ladder, read before cutting, lazy-not-negligent, the post-write size check | `sdsi:core` §2 "No over-engineering" | `sdsi:optimize` | Core §2 keeps the principle in two sentences: solve the problem in front of you, a pattern earns its place with a second real caller today; climb the ladder before writing and check the size after (`sdsi:optimize`), never cutting validation, data-loss handling, security, or accessibility |
| Reuse over reimplementation (DRY on the second occurrence; coincidental duplication stays) | `sdsi:standards` | `sdsi:optimize` | Nothing; core §3's "Code conventions" row drops "reuse over reimplementation", and a new "Lean code" row points to `sdsi:optimize` |
| Dead code and cleanup sweeps (checkpoint, proof list, merge duplicates, entry-point inventory, never delete externally called code, cadence) | `sdsi:standards` | `sdsi:optimize` | Nothing |
| The `shortcut:` marker and its `meta/TODO.md` line | `sdsi:standards` (comments) | `sdsi:optimize` | Nothing |
| Load heavy or environment-specific modules lazily, by name from config | `sdsi:dependencies` | `sdsi:optimize` | Nothing; dependencies' description drops it |
| CLI startup time is a budget | `ref/cli.md` `## sdsi:dependencies` | `ref/cli.md` `## sdsi:optimize` | Nothing |
| Standards' three Upkeep lines (simplification pass, shortcut, before deleting) and matching Review-checklist items | `sdsi:standards` | `sdsi:optimize` | Standards loses its `## Upkeep` section |
| Pointers: core §2 "No random changes" → cleanup sweep; security's entry-point inventory → "cleanup sweeps use this list" | `sdsi:standards` | `sdsi:optimize` | Only the pointer name changes |

Stays where it is (pointed to, not restated): honest reporting and "read what depends on it" (`sdsi:workflow`), a test for risky logic (`sdsi:testing`), standard library first and few dependencies (`sdsi:dependencies`, core §2), the exposed-entry-point inventory (`sdsi:security`), performance targets in `SPEC.md` and their check at deploy (`sdsi:workflow`, `sdsi:deploy`), bounded queues (`sdsi:concurrency`), and "UI code reuses the established design" (`ref/web.md` `## sdsi:standards`).

### `sdsi:optimize` — behavior

1. **Before writing: the ladder** (moved, unchanged in substance).
2. **After writing: the size check** (moved) — code far longer than the problem needs is rewritten before it's called done.
3. **The pass — when a feature is finished**, over the code it changed (scope `branch` by default). Four lenses, from `/simplify`:
   - **Reuse** — something the codebase, standard library, or platform already provides; a rule now implemented twice.
   - **Simplification** — needless indirection (a wrapper or interface with one caller), speculative options nobody sets, deep nesting, dead branches, code that restates what a library does.
   - **Efficiency** — obvious waste: the same I/O, query, or computation repeated in a loop, reading everything to use one item, unbounded growth.
   - **Altitude** — logic at the wrong layer: a workaround in a caller that belongs in the shared front door (core §2), a business rule in an entry point or handler.
   The pass removes what the change made unused. Where the host has Claude Code's `/simplify`, it may run the pass with this skill's checklist as the lens; the deletion rules below still apply.
4. **The sweep — maintenance**, over the whole codebase, on a cadence (weekly on an active project, and before a release): unreferenced files, functions, exports, types, constants, config keys, feature flags past their rollout, assets, styles, and dependencies; duplicated rules; `shortcut:` markers whose revisit condition has come; entry points nothing calls (`sdsi:security`'s inventory). Each item is listed with proof; nothing is deleted without a clean checkpoint and the human's approval; externally invoked code is never deleted without asking (all moved).
5. **Every element earns its place** (from Impeccable's `distill`) — a setting, flag, option, variant, or code path with no real user is a sweep item. Removing something a user or caller can see is a behavior change: it goes through `sdsi:workflow` (design documents first) and gets a `Removed` changelog note saying why.
6. **Performance from measurement** (from Impeccable's `optimize`):
   - Obvious waste (lens 3) is fixed in the pass without a benchmark.
   - **Tuning** — caching, precomputation, parallelism, batching, a lower-level rewrite — happens only on a path measured to be slow, against the `SPEC.md` target when one exists, biggest bottleneck first. The before and after numbers are shown; a tuning that adds complexity without a measured gain is reverted. Tuning code carries a comment with the reason and the measurement.
   - Never trades correctness, security, or accessibility for speed.
7. **Lazy loading** of heavy or environment-specific modules (moved from `sdsi:dependencies`).
8. **Marked shortcuts** (moved) — and revisited by the sweep.

### Order — step 9 in core §4
`sdsi:optimize` runs **after `sdsi:testing`** and before `sdsi:dependencies`: tests exist to prove a removal safe; it trims what the earlier steps added; unused dependencies are gone before the dependency audit; and `sdsi:docs` then describes the code that remains. Dependencies, docs, versioning, and deploy become steps 10–13; `sdsi:all` grows from 12 to 13 steps.

### Project-type companions
- `ref/cli.md` gets `## sdsi:optimize` holding the moved startup budget.
- `ref/web.md` gets `## sdsi:optimize` (from Impeccable's `optimize`, framework-neutral): measure against the `SPEC.md` Core Web Vitals budget on a throttled mobile profile; images sized for their display size and lazy-loaded below the fold; space reserved for media and embeds so nothing shifts the layout; a script or third-party tag that loads on every page but runs on one is a sweep item.
- Other companions get no section — the skill says "no considerations" for them (core §1 Step 2). Sections are added only from a real project's lesson.

### Upkeep lines (`sdsi:optimize`)
- Before writing code → read what the change touches and trace its flow, then climb the ladder and stop at the first rung that solves it
- Finishing a feature → run the pass (reuse, simplification, efficiency, altitude) over the code it changed and remove what it made unused; leave pre-existing dead code for a sweep
- Taking a deliberate shortcut → `shortcut:` comment + `meta/TODO.md` line (moved)
- Changing code for speed → measure before and after on the slow path; keep the change only with a measured gain
- Before deleting code that looks unused → checkpoint, proof list, approval; never delete externally called code without asking (moved)
- Starting maintenance work or preparing a release → run `/sdsi:optimize --review` over the whole project

### Interfaces touched
New `skills/optimize/SKILL.md` (`argument-hint: "[--review|--apply] [path|branch]"`, Upkeep, Review checklist, description ≤ 1024 chars). Edited: `skills/core` (§2, §3, §4), `skills/standards`, `skills/dependencies`, `skills/security` (pointer), `skills/upkeep` (one sentence), `skills/all` (description, step count), `ref/findings.md` (step count example), `ref/cli.md`, `ref/web.md`, `README.md` (skills table), `.claude-plugin/plugin.json` description (topic list only — never the version), `meta/CHANGELOG.md`.

**Projects with standards' upkeep installed:** their `.claude/rules/sdsi.md` goes stale on upgrade; `sdsi:upkeep`'s review already flags a stale section; `sdsi:upkeep` gains one sentence: a refresh drops, and reports, an installed topic whose `## Upkeep` section no longer exists. The changelog note tells them to run `/sdsi:upkeep` and pick `optimize`.

### Explicitly not adopted
Impeccable's visual-design commands (bolder, colorize, typeset, …), its detector, `PRODUCT.md`/`DESIGN.md`, and framework-specific tips (React memoization, specific image formats); Ponytail's intensity levels, band, and scoreboard; a separate `/sdsi:sweep` command (the sweep is `/sdsi:optimize --review` on the whole project).

### Constraints
One topic, one file (each moved rule exists only in `sdsi:optimize` afterwards); language-neutral; descriptions ≤ 1024 chars; changelog notes cite `TODO #22`; `plugin.json`'s version untouched.
