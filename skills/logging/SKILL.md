---
name: logging
description: >
  SDSI's logging and output standard — one central logger that every log
  line funnels through, standard levels with clear jobs, a cheap
  would-this-be-written check, deciding color once at startup, and logging
  as a message queue: log calls enqueue records, one writer pulls them in
  order of arrival and writes them sequentially to each destination, the
  same whether the program is single- or multi-threaded, with a bounded
  queue whose full behavior (wait or drop) is a setting, and a bounded
  shutdown drain; log files that roll over at a
  configured time of day and keep a configured number of files — plus the audit trail: security-relevant decisions (sign-ins,
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
- **Decide color/styling once, at startup, for the whole run** — from the destination (interactive terminal: yes; file or structured output: no). Every destination gets identical content, and a log file never gets escape codes.
- **Never log a secret value** (`sdsi:security`). Name the secret; never print it.

## The log queue

Logging works as a message queue, whatever the language or system, and whether the program runs one thread or many. Code that logs only hands a record over. One writer does every write, in the order the records arrived.

```text
log call (any thread, task, or component)
  → build the record → enqueue                  the caller's part ends here
log queue (one per process, first in, first out)
  → the log writer pulls the oldest record → writes it to each destination, in turn
```

- **A log call builds the record and enqueues it, nothing more.** The record is stamped when the call is made, not when it's written: UTC time, level, logger name, thread or task ID, correlation ID, and the message. A log call never opens, writes, or flushes a file or a stream itself.
- **One queue per process, first in, first out.** Records wait in the queue until the writer pulls them, oldest first. Nothing reorders them, filters them after enqueue, or writes around the queue.
- **One log writer pulls and writes sequentially.** It takes one record at a time, writes it to every configured destination (the file first, then the console or any other), and only then takes the next. Two records are never written at once, so lines never interleave and the file reads in arrival order. This is the single fan-out point: adding a destination means adding it to the writer, never another call at each log site.
- **The same design, single-threaded or not.** Only how the writer runs differs. With threads, it's a dedicated background worker (`sdsi:concurrency`). On a single-threaded event loop, it's a task on that loop. In a program with neither, the logger drains the queue right after each enqueue. The calls, the order, and the output are identical in all three.
- **The queue is bounded, and what happens when it's full is a setting.** Both its capacity (`queue_capacity`) and its full-queue behavior (`when_full`) are settings, with no default in code:
  - **`wait`:** the log call waits for room. Nothing is lost, but a flood of logging slows the program down.
  - **`drop`:** a `DEBUG`, `INFO`, or `WARNING` record that arrives at a full queue is discarded, and the program never slows down for logging. `ERROR` and `CRITICAL` records still wait, because they're the ones an investigation needs. Drops are never silent: the writer counts them and, once there's room, writes one `WARNING` saying how many records were dropped and over what period.

  Wait time, queue depth, and drop counts are observable (`sdsi:concurrency`, "starvation is observable").
- **A failing destination never breaks the program.** If the writer can't write (a full disk, a closed console), it reports that once to the console, keeps the other destinations going, and retries the failed one on the next record. A log call never raises because of a write failure.
- **Shutdown drains the queue.** On stop, the logger stops accepting new records, the writer finishes everything already queued, and then the destinations close. How long shutdown waits for the drain is a bounded setting, kept under the platform's stop-to-kill grace period (`sdsi:concurrency`). Anything the drain can't finish is counted and reported on the console.
- **Say where late messages go.** A message logged after the writer has closed can only reach the console — state that in code, don't let it vanish silently.
- **Use the language's own facility when it already works this way** (a queue handler with a listener, an async appender). The rule is the behavior described here, not a custom implementation.

## Log files: rotation and retention

When a destination is a file — the primary one for most programs — two settings govern its life:

```yaml
logging:
  level: INFO
  queue_capacity: 10000
  when_full: wait           # wait | drop — what a log call does when the queue is full
  drain_timeout: 5          # seconds shutdown waits for the queue to empty
  file:
    directory: <not configured>
    name: <not configured>  # e.g. app → app.log
    rotate_at: "00:00"      # time of day the file rolls over
    timezone: UTC           # the clock rotate_at is read on
    keep: 7                 # rotated files kept live before the oldest is deleted
```

- **The file rolls over at a configured time of day** (`rotate_at`, midnight being the usual choice), in a configured time zone. The writer does the rotation, between two records, so no line is ever split across files or lost. A record goes to the file for the period its timestamp falls in.
- **The active file has a fixed name; a rotated file carries its date.** `app.log` is always the current file. At rotation it's renamed to `app.YYYY-MM-DD.log`, the date it covers, and a new `app.log` is opened.
- **`keep` sets how many rotated files stay live** — 7, 15, 30, whatever the project needs. At each rotation, rotated files beyond that number are deleted, oldest first. Only files matching this log's own name pattern in its own directory are ever deleted.
- **A restart catches up.** At startup, if the active file belongs to an earlier period, it's rotated first, so a program that was down at midnight doesn't append a new day to yesterday's file.
- **Both are settings, in every environment** (`sdsi:config`): no rotation time or retention count is written in code. The audit trail has its own retention (below) and is never rotated away by this setting.
- **A program whose platform collects its output** (a container writing to the console) may have no file destination. The queue rules still apply in full, and rotation and retention then belong to the platform's log collector.

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
- **Identifiers, not payloads.** An event names the actor and target by ID; it never copies document contents, request bodies, or secrets (`sdsi:security`). Personal data is kept to what the record needs.
- **Retention is a setting** (`sdsi:config`), separate from application-log retention and long enough for the project's compliance requirement. Records leave only by that policy.
- **Tested like a contract.** Each audited decision has a test asserting it emits exactly one event with the right action, actor, target, and outcome — denials included — and a test proves that an audit write failure on a fail-closed action refuses the action.

## Upkeep

The line `sdsi:upkeep` installs in the project's `.claude/rules/sdsi.md`:

- Adding or changing a sign-in, authorization, permission, or administrative action → record its audit event through the project's audit recorder, granted and denied, and test it (`sdsi:logging`)

## Review checklist

Console printing used for real diagnostics · more than one logger or logging path · levels used inconsistently (errors at `INFO`, noise at `WARNING`) · an expensive debug message built unconditionally · per-line color decisions or escape codes in a log file · a log call that writes to a file or stream itself instead of enqueueing · more than one queue or writer per process · records written out of arrival order, or interleaved · a record stamped at write time instead of call time · an unbounded queue · full-queue behavior not set in config · a full queue that drops records silently, or drops `ERROR` or `CRITICAL` · a write failure that raises into the caller or stops the other destinations · an unbounded shutdown drain · a log file with no time-based rotation or no retention count, or either written in code · rotation that can split or lose a line · retention that can delete files other than this log's own · a secret value in a log line · a program that makes security decisions with no audit trail, or no statement in `SPEC.md` either way · audit events mixed into the application logs, or filtered by the log level · a security decision — a denial especially — with no audit event · audit events in free text or without a fixed action set · audit events reconstructed from log lines instead of written at the decision · audit records the program can edit or delete · an audit write failure that's silent · a permission or admin change that proceeds when its record can't be written · secrets or payloads in an audit event · no tests for audit events.
