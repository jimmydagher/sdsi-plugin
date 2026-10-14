# PLAN

## ⛏️ In progress

### TTD017 — Ponytail-inspired coding discipline (see SPEC.md)
1. Read `skills/core`, `standards`, `testing`, `workflow`, `docs`, `dependencies` fully to pick the single home for each rule and confirm nothing is already stated.
2. `skills/core/SKILL.md` §2: extend "No over-engineering" with the ladder, read-before-cutting, and lazy-not-negligent; keep it compact.
3. `skills/testing/SKILL.md`: ensure the risky-logic-gets-a-test rule exists; add if absent. Core only points to it.
4. `skills/workflow/SKILL.md`: add the honest-reporting rule (what was skipped / not checked / risks).
5. `skills/standards/SKILL.md`: add the `shortcut:` marker rule (comments section), with TODO.md as the ledger via `sdsi:docs`; add an Upkeep trigger line if it must hold every session.
6. Add matching Review checklist items to each touched skill.
7. `meta/CHANGELOG.md`: entries under Unreleased citing `TTD017`.
8. Run `python -m unittest discover tests`; fix any failures (description length, structure).
9. Commit.

## ✅ Done
(none)
