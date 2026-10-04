---
name: logging
description: >
  SDSI's logging and output standard — one central logger that every log
  line funnels through, standard levels with clear jobs, a cheap
  would-this-be-written check, a single fan-out point for multiple
  destinations, deciding color once at startup, non-blocking file writes
  with a bounded shutdown drain, and messages that arrive after the log
  closes — plus the audit trail: security-relevant decisions (sign-ins,
  authorization grants and denials, permission and role changes, admin
  actions) recorded as their own structured, append-only, replayable stream,
  separate from application logs. Use when adding logging to a project,
  reviewing log output, replacing ad-hoc print statements, or adding
  authentication, authorization, or permission management. Reads sdsi:core
  first. Triggers on "/sdsi:logging", "logging", "add logs", "audit trail",
  "audit log".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Logging & Output

Before anything else, read `../core/SKILL.md` and run its steps.

## Rules

- **One central logger.** Structured logging through one logger type, never bare console printing for anything that matters. One method actually produces a log line; the level shorthands (`info`, `warning`, …) all funnel through it, so there's one answer to "was this written, and what did it look like". Use the language's standard logging facility underneath if it has a good one — the rule is the single front door, not a custom implementation.
- **Standard levels, each with one job:**

  | Level | Use for |
  |---|---|
  | `DEBUG` | Dev-only detail; hidden in deployed environments |
  | `INFO` | Normal progress — what the run is doing now |
  | `WARNING` | Something's wrong; the run continues |
  | `ERROR` | One unit of work failed; the run may complete others |
  | `CRITICAL` | The run can't be trusted or can't continue — someone must act tonight |

- **The level is a floor**, set from config (`sdsi:config`). Make the "would this even be written?" check public and cheap, so an expensive debug line isn't built only to be discarded.
- **Many destinations, one write.** When output goes to several places at once (console, file, a response payload), write through a single fan-out point rather than duplicating calls per destination.
- **Decide color/styling once, at startup, for the whole run** — from the destination (interactive terminal: yes; file or structured output: no). Every destination gets identical content, and a log file never gets escape codes.
- **File writes never block the work.** Write on a background worker; bound how long shutdown waits for it to drain, and keep that bound under the platform's stop-to-kill grace period (`sdsi:concurrency`).
- **Say where late messages go.** A message discovered after the log file closes can only reach the console — state that in code, don't let it vanish silently.
- **Never log a secret value** (`sdsi:secrets`). Name the secret; never print it.

## Audit trail

Application logs answer "what went wrong?"; the audit trail answers "who was allowed to do what, and when?" — for an investigation, a compliance review, or rebuilding who had which access on a given day. They're different records with different readers, so they're kept apart.

- **Needed wherever the program makes security decisions** — it has users, roles, permissions, or administrative actions, or a compliance requirement asks for one. `SPEC.md` says whether the project has an audit trail and why; a program with no users and no permissions says so instead.
- **Its own stream, through its own front door.** One audit recorder (core §2, "one front door per capability") writes every audit event to a destination separate from the application logs. It isn't a log level: the level floor and log configuration never filter, sample, or switch it off.
- **What's recorded — every security-relevant decision, granted or denied:** sign-in success and failure, sign-out, and session revocation; authorization grants and denials; permission, role, and group changes; account creation, disabling, and deletion; administrative actions; changes to security settings (an access policy, an allowed host, a key rotation); access to or export of data the project marks sensitive; and the audit trail's own start, stop, and failures.
- **Each event has a fixed, structured shape** with a schema version, so it can be read back and replayed by a program, not just a person:

  | Field | Holds |
  |---|---|
  | `when` | UTC timestamp, from a synchronized clock |
  | `who` | The actor's stable ID and kind (user, service, system) — and whom it acted for, if anyone |
  | `from` | Source address, session, and correlation ID — ties the event to the application logs |
  | `action` | A named event type from a fixed set (an enum, `sdsi:standards`), never free text |
  | `target` | The resource's type and ID |
  | `outcome` | Granted / denied, or succeeded / failed — with a reason code |
  | `change` | For a change: the before and after values — never a secret |
  | `context` | Environment and running version |

- **Recorded where the decision is made**, in the same code path that grants, denies, or changes — never reconstructed afterwards from application log lines.
- **Append-only and tamper-evident.** The program can add audit events but never change or delete them — a write-only destination, or storage that won't overwrite. Records are chained by sequence number or hash, so a gap or an edit is detectable. Access to read the audit trail is itself restricted and audited.
- **Never silently lost.** Audit writes are durable before the action they record is acknowledged, or buffered in a durable, bounded queue that the shutdown drain flushes (`sdsi:concurrency`). When the trail can't be written, that's a `CRITICAL` reported through the global error handler's reporters (`sdsi:errors`). For actions that may only happen on the record — permission and role changes, administrative actions — the action **fails closed**: it's refused rather than done without its record. Which actions fail closed is stated in `SPEC.md`.
- **Identifiers, not payloads.** An event names the actor and target by ID; it never copies document contents, request bodies, or secrets (`sdsi:secrets`). Personal data is kept to what the record needs.
- **Retention is a setting** (`sdsi:config`), separate from application-log retention and long enough for the project's compliance requirement. Records leave only by that policy.
- **Tested like a contract.** Each audited decision has a test asserting it emits exactly one event with the right action, actor, target, and outcome — denials included — and a test proves that an audit write failure on a fail-closed action refuses the action.

## Upkeep

The line `sdsi:upkeep` installs in the project's `.claude/rules/sdsi.md`:

- Adding or changing a sign-in, authorization, permission, or administrative action → record its audit event through the project's audit recorder, granted and denied, and test it (`sdsi:logging`)

## Review checklist

Console printing used for real diagnostics · more than one logger or logging path · levels used inconsistently (errors at `INFO`, noise at `WARNING`) · an expensive debug message built unconditionally · per-line color decisions or escape codes in a log file · synchronous file writes on the hot path · an unbounded shutdown drain · a secret value in a log line · a program that makes security decisions with no audit trail, or no statement in `SPEC.md` either way · audit events mixed into the application logs, or filtered by the log level · a security decision — a denial especially — with no audit event · audit events in free text or without a fixed action set · audit events reconstructed from log lines instead of written at the decision · audit records the program can edit or delete · an audit write failure that's silent · a permission or admin change that proceeds when its record can't be written · secrets or payloads in an audit event · no tests for audit events.
