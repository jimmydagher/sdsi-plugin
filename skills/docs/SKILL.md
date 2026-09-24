---
name: docs
description: >
  SDSI's documentation standard — the root README, operational docs under
  docs/ (setup, deployment, cheat sheet, index, features), updating a
  document in the same change as the code it describes, naming where every
  command runs, a what-changed-to-what-to-update table, and TODO.md as the
  numbered, cross-session list of outstanding work that the release scripts
  close automatically. Use when writing or reviewing documentation, or
  tracking outstanding work. Reads sdsi:core first. Triggers on
  "/sdsi:docs", "documentation", "README", "TODO.md".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Documentation

Before anything else, read `../core/SKILL.md` and run its steps.

## The golden rule

**Any change that affects a document updates that document in the same
change** — not eventually, not in a follow-up. A document that lags is worse
than a missing one, because it's still believed.

## What exists, and what each answers

| Document | Answers | Update when… |
|---|---|---|
| `README.md` (root) | What it does, local setup, how to run/debug/test locally, how to deploy, every config key and environment variable it depends on | Any of those change |
| `CLAUDE.md` (root) | Project-specific conventions, the SDSI profile, deliberate deviations (`sdsi:workflow`) | A convention is set, a mistake recurs, a deviation is made |
| `CHANGELOG.md` (root) | What changed per release and what an operator must do (`sdsi:versioning`) | Every change — the AI writes to Unreleased as it works |
| `TODO.md` (root) | What's outstanding (below) | Continuously |
| A setup doc, in `docs/` (one per deployable shape) | Standing up an environment from nothing | A resource, credential, or one-time step is added |
| A deployment doc, in `docs/` | How to ship a change | The deploy sequence, a check, or a rollback step changes |
| A cheat sheet, in `docs/` | The commands reached for when something's wrong — every operation, every flag, where output lands | An operation is added, renamed, or removed |
| A documentation index, in `docs/` | What each document covers and doesn't | A document is added, renamed, or removed |
| A features doc, in `docs/` (optional) | What's been built, for a non-technical reader | A user-visible capability ships |
| Review reports, in `docs/reviews/` | What an SDSI review found and what happened to each finding — `YYYY-MM-DD-<skill>.md` | Never — written once per review when the human exports it (`ref/findings.md`); a new review writes a new file |

- **Every command block names where it runs** — local shell, CI, inside a
  container, a cloud console. The same command can fail in one place for
  reasons unrelated to the command.
- **Keep a "what changed → what else must be updated" table** for the
  project's own moving parts (adding an operation touches its registry and
  the cheat sheet and the local run config; adding a secret touches the
  setup doc). The table above is the starting point. Extend it the moment a
  new kind of moving part appears.
- **Document local run/debug separately from deployment** — they solve
  different problems.

## TODO.md — outstanding work across sessions

`CHANGELOG.md` is the permanent record of what shipped; `TODO.md` is the
working list of what hasn't. Cheap to add to, reword, or drop.

**What goes in it:** anything a session leaves undone — a follow-up, a
deferred decision, a bug found but not fixed, an open question. Anything
bigger than a line item gets promoted to its own `INTENT.md`
(`sdsi:workflow`).

**Format** — numbered, so items can be referenced and closed by script:

```markdown
# TODO

- [ ] #4 <what needs doing, in plain language> — <why, if not obvious>
- [ ] #5 <...>

---

## Done

- [x] #1 <what was done> — completed 2026-09-23 · VERSION 1.0.1
```

- **A deferred review finding** keeps its finding ID and skill in brackets, so
  it can be traced to its review:
  `- [ ] #12 [F-003 sdsi:errors] Retry wraps a non-transient DB error — src/db.py:44`
  (`ref/findings.md` adds these automatically for findings not applied).
- **Numbers are never reused.** A new item takes the highest number in the
  file (open or done) plus one.
- **The AI updates it continuously** — a session that ends without a pass
  over `TODO.md` leaves it stale. **The human can add items any time**, in
  the same format.
- **Closing is automated, not manual.** When a change fixes an item, the AI
  references it in the changelog bullet it writes — `(TODO #4)`. At commit,
  the release script checks the item off, moves it to **Done** with the date
  and version, and refuses the commit if the referenced item doesn't exist
  (`sdsi:versioning`). The AI doesn't move items to Done by hand.
- No priority tiers, assignees, or due dates unless the project genuinely
  needs them. If **Done** gets long, lean on `CHANGELOG.md` and git history —
  **Done** is a convenience, not the archive.

## Review checklist

A code change without its matching doc update · a README missing setup,
run, test, deploy, or config keys · a command block that doesn't say where it
runs · no docs index · `TODO.md` items without numbers · items closed by hand
instead of by the release script.
