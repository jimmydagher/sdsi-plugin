# SPEC — sdsi plugin

## TTD017 — Ponytail-inspired coding discipline

Source reviewed: https://github.com/dietrichgebert/ponytail (MIT, "the best code is the code you never wrote"; benchmark figures are self-reported, so none are copied in).

### What SDSI already has (not repeated)
`sdsi:core` §2 already covers no over-engineering (with a post-write size check), no assumptions, standard library first, one front door, and no pointless changes; `sdsi:standards` covers reuse over reimplementation and dead code.

### Behavior changes (the gaps Ponytail fills)
1. **The ladder** — in `sdsi:core` §2 "No over-engineering" is extended: before writing code, stop at the first rung that solves it: needed at all → already in the codebase → standard library → native platform feature → already-installed dependency → one line → only then the minimum that works. New dependencies stay governed by `sdsi:dependencies`; the ladder only points to it.
2. **Read before cutting** — the ladder runs after reading the code the change touches and tracing the real flow; lazy about the solution, never about reading. Stated once in core §2.
3. **Lazy, not negligent** — the ladder never removes trust-boundary validation, data-loss handling, security, or accessibility. One sentence in core §2.
4. **Tests for risky logic** — code with a branch, loop, parser, money handling, or security meaning gets at least one small test; a pointer from core, the rule itself lives in `sdsi:testing` (add/confirm there, no restating).
5. **Honest reporting** — every finished change states what was skipped or not checked and the known risks. Lives in `sdsi:workflow` (or core Step 1 if a better fit is found while reading), one place only.
6. **Marked shortcuts** — a deliberate shortcut gets a `shortcut:` comment saying when to revisit it; the tag word may be overridden in the project's `CLAUDE.md`. Collected into outstanding work via `meta/TODO.md` (`sdsi:docs`) rather than a new ledger command, to avoid a second list. Rule lives in `sdsi:standards` (comments section).
7. **Review checklists** — the touched skills' Review checklists gain the matching smells (built before checking existing code, a shortcut with no `shortcut:` note, risky logic with no test, a final report that omits what was skipped).

### Explicitly not adopted
- Intensity levels (`lite/full/ultra`), `/ponytail-*` commands, the benchmark scoreboard, and the separate audit/debt/gain commands: SDSI already has `--review`/`--apply` and `meta/TODO.md`.
- Installing or depending on the ponytail plugin itself.

### Constraints
- One topic, one file; language-neutral; skill descriptions ≤ 1024 chars; changelog entries cite `TTD017`; no hand edits to `plugin.json` version.
