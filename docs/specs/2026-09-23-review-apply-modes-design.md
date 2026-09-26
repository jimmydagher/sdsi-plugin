# Review and Apply Modes for Every SDSI Skill — Design

**Date:** 2026-09-23 · **Status:** awaiting review · **Target version:** 1.1.0 (MINOR — new capability, nothing existing breaks)

## Intent

When the human runs an SDSI skill against code — "execute `sdsi:errors` on the code" — they mean one of two things:

- **Review:** check the code against that skill's standard and report findings and recommendations, changing nothing until they choose.
- **Apply:** they trust the skill; change the code to meet the standard now.

This works the same for every SDSI skill. `sdsi:all` is the heaviest case (every topic in order — slow and token-heavy, suited to small projects). The review half replaces what the separate `code-reviewer` plugin's `intake` and `catalog` phases did, rebuilt as shared background context rather than a skill of its own.

## Decisions

| # | Decision | Chosen |
|---|---|---|
| 1 | Where the mode logic lives | In `sdsi:core` (resolve the mode) plus one shared reference file for the review process — not per topic, not separate `sdsi:review`/`sdsi:apply` skills |
| 2 | Where the review process lives | `ref/findings.md` — a new top-level `ref/` folder for shared reference files, read on demand |
| 3 | What happens to findings not applied | They become numbered `TODO.md` items, closed later by the existing release chain |
| 4 | Where an exported report goes | `docs/reviews/YYYY-MM-DD-<skill>.md`, committed, written once |
| 5 | code-reviewer's `strategy` / `execute` / `validate` phases | Out of scope — `sdsi:all`'s fixed order is the sequencing for small projects; revisit when a large codebase needs staged, multi-session remediation |

## 1. Invocation and mode resolution

```text
/sdsi:<skill> [--review | --apply] [path]

/sdsi:errors --review src/payments
/sdsi:logging --apply
/sdsi:all --review
```

`sdsi:core` Step 3 ("Existing code: review first, or just apply?") becomes **"Resolve the mode"**:

1. **From the arguments** — `--review` or `--apply` anywhere in what follows the command.
2. **From plain language** — "review my error handling" → review; "apply the logging standard" → apply.
3. **Otherwise ask** with `AskUserQuestion`: *Review findings first* / *Apply directly*.

- **Scope** is the path given in the arguments, else the whole project — and the skill states which (core's "communicate what you're doing").
- **An empty project** skips the question: there's nothing to review, so the skill scaffolds (apply).
- `sdsi:all` resolves the mode **once** for the whole run.
- Every skill's frontmatter gains `argument-hint: "[--review|--apply] [path]"` so the flags are suggested when the command is typed.

## 2. Review mode — `ref/findings.md`

Read only in review mode, by relative path `../../ref/findings.md` from any skill. It defines:

1. **Intake** — scan the in-scope code against the invoking skill's rules and its **Review checklist**. The skill is the lens. For `sdsi:all`, every step in core's order is a lens, run in that order.
2. **Catalog** — one entry per underlying issue:
   - **Deduplicate:** the same `file:line` flagged by several topics is one entry listing each.
   - **Classify:**

     | Field | Values |
     |---|---|
     | ID | `F-001`, `F-002`, … — unique within the review |
     | Skill | The topic whose rule is broken (several if merged) |
     | Rule | The specific rule, quoted briefly |
     | Location | `file:line` (or a file/folder for structural findings) |
     | Severity | Critical · High · Medium · Low |
     | Effort | S · M · L |
     | Recommendation | The concrete fix |

   - **Severity guide:** Critical — leaks data, loses data, or breaks in production; High — breaks a non-negotiable (core §2) or hides failures; Medium — breaks a topic rule with contained impact; Low — consistency and readability.
3. **Present in the session** — counts by severity, the full table (grouped by step for `sdsi:all`), and the top recommendations. A clean scope says so plainly: "no findings against `sdsi:errors`".
4. **Ask what's next** — `AskUserQuestion`, multi-select:
   - Apply all findings
   - Apply Critical + High only
   - Export the report to `docs/reviews/`
   - (Other) specific IDs, e.g. "F-002, F-005", or "discard"

## 3. Where each finding ends up

- **Applied** — the code change is made (apply mode, §4, limited to the selected findings) and each changelog note cites the finding ID(s).
- **Not applied** — added to `TODO.md` automatically, numbered like any item:

  ```markdown
  - [ ] #12 [F-003 sdsi:errors] Retry wraps a non-transient DB error — src/db.py:44
  ```

When a later change fixes it, its changelog note says `(TODO #12)` and the release script closes it. Typing "discard" drops unapplied findings instead.

- **Exported** — `docs/reviews/YYYY-MM-DD-<skill>.md` holds the full catalog with each row's outcome (`Applied` or `TODO #n`). Written once, never edited; a later review makes a new file (a second one the same day gets a `-2` suffix).

## 4. Apply mode

- Apply the skill's rules to the scope — directly, or only the selected findings when coming from review.
- Verify (tests, build, or a run) and show the evidence (core §2).
- Report what changed and write the changelog Unreleased notes.
- **Never commit** — the human approves and commits; the release chain does the rest.
- `sdsi:all --apply` applies step by step in core's order, so later steps build on corrected code.

## 5. Files changed

| File | Change |
|---|---|
| `ref/findings.md` | **New** — the review process in §2–§3 |
| `skills/core/SKILL.md` | Step 3 → "Resolve the mode" + invocation syntax; §5 Loading notes `ref/` holds shared reference files read on demand; root layout unchanged (this is the plugin's folder, not a project's) |
| `skills/all/SKILL.md` | Mode resolved once; review collects every step's findings via `ref/findings.md`; apply walks the order |
| All 17 `skills/*/SKILL.md` | Add `argument-hint` frontmatter |
| `skills/workflow/SKILL.md` | Add the Review checklist it lacks (every other skill has one) |
| `skills/docs/SKILL.md` | Finding-TODO format; `docs/reviews/` row in the documents table |
| `skills/versioning/SKILL.md` | Changelog notes cite finding IDs when applying reviewed findings |
| `README.md` | Invocation syntax and the two modes |
| `CLAUDE.md` | `ref/` convention: shared reference files live there, read by relative path |
| `CHANGELOG.md` | Unreleased notes for 1.1.0 |
| `VERSION` | Staged by hand to `1.1.0` (MINOR can't be inferred from a diff) |

## 6. Verification

Skills can't be unit-tested. Proof is a real run on a throwaway project in the scratchpad with deliberately planted error-handling violations (a bare catch-all, a retry around a non-transient error, a disabled feature returning empty success):

1. `/sdsi:errors --review` → findings table lists each planted violation with a sensible severity; the follow-up question appears.
2. Choosing "Apply Critical + High" → only those change; the rest land in `TODO.md` in the finding format.
3. Export → `docs/reviews/<date>-errors.md` exists with outcomes filled in.

The release-script tests (`tests/test_release.py`) still pass, and `claude plugin validate` passes.

## Out of scope

- code-reviewer's `strategy` / `execute` / `validate` staging.
- Retiring the `code-reviewer` plugin from the old monorepo (`TODO.md` #2, #3).
- A bare `/sdsi` entry point.
