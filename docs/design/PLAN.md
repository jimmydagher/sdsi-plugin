# PLAN

## ⛏️ In progress

(none)

## ✅ Done

### TTD022 — `sdsi:optimize` (TODO #22)
New topic `skills/optimize/SKILL.md`, step 9 of core §4 (13 steps): the ladder and size check, reuse, the pass (reuse, simplification, efficiency, altitude), the maintenance sweep (`/sdsi:optimize --review` on the whole project, with proof lists and approval), performance from measurement, lazy loading, and `shortcut:` markers, plus six upkeep lines. Rules moved out of core §2, `sdsi:standards`, `sdsi:dependencies`, and `ref/cli.md`; `ref/cli.md` and `ref/web.md` gained `## sdsi:optimize`; `sdsi:all`, `ref/findings.md`, `README.md`, and the `plugin.json` description follow the new order; `sdsi:upkeep` drops a topic whose `## Upkeep` is gone. Verified by `python -m unittest discover tests`, the description-length guardrail against a padded description, and greps showing each moved rule stated only in `sdsi:optimize`.

### TTD017 — Ponytail-inspired coding discipline
The ladder, read before cutting, and lazy-not-negligent in core §2 (moving to `sdsi:optimize` under TTD022); a test for risky logic in `sdsi:testing`; honest reporting in `sdsi:workflow`; the `shortcut:` marker in `sdsi:standards` (moving to `sdsi:optimize`); matching Review-checklist items.
