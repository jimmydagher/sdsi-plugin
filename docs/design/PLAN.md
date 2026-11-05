# PLAN

## ⛏️ In progress

### TTD016 — Review and expand companion instructions (TODO #16)
Design: `SPEC.md` › TTD016. Each step is one reviewable diff, verified before the next starts.

1. **Guardrail test first.** Add `test_companions` to `tests/test_skills.py`. It checks four things:
   - Every heading names a skill.
   - Every core type has its file.
   - Every companion has `## Sources`.
   - No block has more than 7 top-level bullets.

   Run `python -m unittest discover tests` (local shell, repo root). The bullet-count check should fail on today's companions: web, cli, mw, desktop, and mobile are over. That failure is the proof the test can catch the problem.
2. **Core §1 Step 2: the declaration.**
   - Add the `Companions` field to the profile block and the scoping rule for secondary companions.
   - Add the fallback for a missing field, derived from `Project type`.
   - Sharpen the evidence column. Add the mixed-project list and the tie-breaker question.
   - Add "skip a rule for a surface the project doesn't have".
   - Check the `core` and `all` descriptions: they stay ≤ 1024 chars and need no change unless the wording mentions the profile.
3. **`sdsi:workflow`.** Add the Upkeep line *new surface → update `Companions` (`sdsi:core`)* and its Review-checklist item.
4. **`ref/cli.md`.** Trim standards from 9 to 5, and move the registry rule into testing. Settle the secrets-through-environment deviation and the `--json` error stream. Then apply the config, logging (pager), and errors corrections, and update the header and Sources.
5. **`ref/mw.md`.** Trim standards from 14 to 7 and errors from 9 to 5. Move reconciliation to logging and per-step progress to concurrency. Apply the retry and cache corrections and the outbox consequence. Add the contract-versioning rule, the freshness target, minimisation and retention, the drift warning, and the contract in the integration sheet. Fix Sources.
6. **`ref/web.md`.** Trim standards from 8 to 6. Regroup security from 18 to 12 under three `###` groups, adding SSRF and redirects, uploads, CSRF, and the TLS floor. Move the security tests into testing. Apply the header, cookie, idempotency, deprecation-date, health, and allowed-hosts corrections, plus the cookie-banner qualifier. Update Sources.
7. **`ref/lib.md`.** Merge standards from 7 to 5, adding type information shipped. Apply the corrections to environment reads, the silent handler, timeout defaults, dependency ranges, support-drop MINOR, and optional removal. Add peer dependencies, experimental marking, the license and SPDX identifier, and the drop schedule in workflow.
8. **`ref/desktop.md`.** Add the new workflow section. Trim security from 8 to 7, adding least privilege and portals, and deploy from 8 to 7. Correct signing per OS with hardware-held keys and a backed-up update key. Correct freeze protection to "where supported" and uninstall to "what the format allows". Update the runtime cadence and Sources.
9. **`ref/mobile.md`.** Trim security from 9 to 5, moving signing keys to deploy. Add the pinning rule and biometric gating. Apply the cleartext/ATS, account-deletion web link, privacy-manifest scope, undated store-schedule, and third-party-AI corrections. Drop "size is a cost" and move telemetry batching to concurrency.
10. **`README.md`.** Add "Which companion applies", pointing to core §1 Step 2.
11. **Changelog and verify.** Write `meta/CHANGELOG.md` Unreleased notes citing `TODO #16`. Under Changed, tell projects with workflow upkeep to run `/sdsi:upkeep`. Then verify:
    - `python -m unittest discover tests` passes, including the step-1 test.
    - A grep confirms each moved rule appears only at its new home: registry, reconciliation, per-step progress, served asset, signing keys, telemetry batching, and dependency types.
    - Every `## sdsi:<topic>` heading still matches a skill.
    - A second read of each diff against `SPEC.md` › TTD016.

    Commit.

## ✅ Done

### TTD022 — `sdsi:optimize` (TODO #22)
New topic `skills/optimize/SKILL.md`, step 9 of core §4 (13 steps): the ladder and size check, reuse, the pass (reuse, simplification, efficiency, altitude), the maintenance sweep (`/sdsi:optimize --review` on the whole project, with proof lists and approval), performance from measurement, lazy loading, and `shortcut:` markers, plus six upkeep lines. Rules moved out of core §2, `sdsi:standards`, `sdsi:dependencies`, and `ref/cli.md`; `ref/cli.md` and `ref/web.md` gained `## sdsi:optimize`; `sdsi:all`, `ref/findings.md`, `README.md`, and the `plugin.json` description follow the new order; `sdsi:upkeep` drops a topic whose `## Upkeep` is gone. Verified by `python -m unittest discover tests`, the description-length guardrail against a padded description, and greps showing each moved rule stated only in `sdsi:optimize`.

### TTD017 — Ponytail-inspired coding discipline
The ladder, read before cutting, and lazy-not-negligent in core §2 (moving to `sdsi:optimize` under TTD022); a test for risky logic in `sdsi:testing`; honest reporting in `sdsi:workflow`; the `shortcut:` marker in `sdsi:standards` (moving to `sdsi:optimize`); matching Review-checklist items.
