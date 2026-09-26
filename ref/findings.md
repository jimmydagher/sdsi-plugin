# Findings — the SDSI review process

Read by any SDSI skill running in **review mode** (`sdsi:core` §1, Step 3), by relative path `../../ref/findings.md`. Not a skill: it's the shared process every skill follows when the human wants findings before changes. Nothing in the code changes until the human chooses what to apply.

## 1. Intake — scan against the skill's standard

- **The invoking skill is the lens.** Check the in-scope code against that skill's rules and its **Review checklist**, plus the project-type companion's section for that skill, if it has one (core §1 Step 2). Apply them in the project language's idioms.
- **For `sdsi:all`, every step is a lens**, run in core §4's order, one at a time. Tell the human which step is scanning ("Step 6/12 — `sdsi:errors` + cli").
- **Scope** is the path the human gave, else the whole project — say which.
- **Read the real code.** A finding cites a location you actually read, never one inferred from a file name or a pattern you expect to be there.

## 2. Catalog — one entry per underlying issue

- **Deduplicate.** The same `file:line` flagged by several skills is one entry that lists each skill.
- **Classify every entry:**

  | Field | Values |
  |---|---|
  | ID | `F-001`, `F-002`, … — unique within this review |
  | Skill | The skill whose rule is broken (several if merged); a rule from the companion adds its type — `sdsi:errors + cli` |
  | Rule | The specific rule, quoted briefly |
  | Location | `file:line`, or a file/folder for a structural finding |
  | Severity | Critical · High · Medium · Low |
  | Effort | S · M · L |
  | Recommendation | The concrete fix |

- **Severity guide** — rate by consequence, the same way in every skill:

  | Severity | Means |
  |---|---|
  | Critical | Leaks a secret or data, loses data, or breaks in production |
  | High | Breaks a non-negotiable (core §2) or hides failures |
  | Medium | Breaks a topic rule; impact is contained |
  | Low | Consistency and readability |

- **Effort:** S — a few lines in one place; M — several places or one module; L — a structural change across modules.

## 3. Present in the session

1. One line of scope: skill(s), path, files read.
2. Counts by severity (`Critical 1 · High 3 · Medium 4 · Low 2`).
3. The full table, sorted by severity then ID — for `sdsi:all`, grouped by step in core's order.
4. The top recommendations — the few fixes that matter most, in plain words.

A clean scope says so plainly: "No findings against `sdsi:errors` in `src/`." Don't invent findings to fill a table.

## 4. Ask what's next

`AskUserQuestion`, **multi-select**:

- **Apply all findings**
- **Apply Critical + High only**
- **Export the report** to `docs/reviews/`
- (Other) specific IDs — "F-002, F-005" — or "discard"

Then act on every choice (§5). Choosing nothing to apply is valid: all findings then go to `TODO.md`.

## 5. Where each finding ends up

- **Applied** — make the change using apply mode as core §1 Step 3 defines it (verify without leaving files behind, report, write changelog notes in `sdsi:versioning`'s format), limited to the selected findings. A finding not selected but fully fixed as a side effect of another is marked `Applied (with F-00n)` and doesn't go to `TODO.md`. Each changelog note cites its finding ID(s): `- Retries only transient failures in the DB client (F-003).`
- **Not applied** — appended to `TODO.md` as numbered items, next number after the highest in the file (`sdsi:docs`):

  ```markdown
  - [ ] #12 [F-003 sdsi:errors] Retry wraps a non-transient DB error — src/db.py:44
  ```

When a later change fixes one, its changelog note says `(TODO #12)` and the release script closes it. If the human answered "discard", unapplied findings are dropped instead — say how many.

- **Exported** — write `docs/reviews/YYYY-MM-DD-<skill>.md` (`sdsi-all` for a full run; a second review the same day adds `-2`):

  ```markdown
  # Review — sdsi:errors — 2026-09-23

  Scope: src/ · Files read: 14 · Findings: Critical 1 · High 3 · Medium 4 · Low 2

  | ID | Skill | Rule | Location | Severity | Effort | Recommendation | Outcome |
  |---|---|---|---|---|---|---|---|
  | F-001 | sdsi:errors | One global error handler that logs and never throws | src/main.py:12 | High | S | … | Applied |
  | F-002 | sdsi:errors | Retry only what's transient | src/db.py:44 | High | M | … | TODO #12 |
  ```

The outcome column is filled in after §4's choices are acted on. The file is written once and never edited — a later review writes a new file.

## 6. Close

End with one line: how many findings were applied, how many went to `TODO.md`, and where the export is (if any). Never commit — the human approves and commits; the release chain does the rest (`sdsi:versioning`).
