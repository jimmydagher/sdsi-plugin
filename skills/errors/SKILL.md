---
name: errors
description: >
  SDSI's error-handling standard — one global error handler in every
  project that logs every unhandled error, keeps long-running processes
  alive, never itself fails, and takes pluggable reporters (a queue,
  ServiceNow, a pager); try/catch only where the logic requires it; a typed
  error hierarchy; retries only for transient failures; failing loudly
  instead of returning an empty success; and a machine-readable outcome on
  every exit path. Use when designing error handling, adding a global
  handler or error reporting, adding retries, reviewing how failures
  surface, or defining exit codes. Reads sdsi:core first. Triggers
  on "/sdsi:errors", "error handling", "exceptions", "exit codes".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Error Handling

Before anything else, read `../core/SKILL.md` and run its steps.

## Rules

- **A typed error hierarchy.** One root type for everything the program
  raises deliberately, with a specific subtype per layer or concern (an API
  call, a cache, a database, configuration). Never raise or catch the
  language's generic error type for an anticipated failure — a handler must
  be able to tell an outage from bad config from a bug. In a language
  without exceptions, the same rule applies to its error values: typed,
  distinguishable, never a bare string.
- **One global error handler — every project has one.** It's the single
  place any unhandled error ends up:
  1. **Registered first**, at the outermost level, before configuration or
     logging exist — wired into the language's own uncaught-error hooks
     (unhandled exceptions, unhandled async rejections) and the framework's
     error hook where there is one. Errors escaping worker threads and async
     tasks reach it too (`sdsi:concurrency`).
  2. **It logs every error it receives** through the central logger
     (`sdsi:logging`) — type, message, stack trace, and context (correlation
     ID, task, run) — redacted. If logging isn't up yet, it writes to stderr.
  3. **The program never ends in a raw crash.** A long-running process (web
     server, worker, service) fails only the request or unit of work that
     raised — with the right outcome — and keeps serving. A run-once program
     (CLI, batch job) logs and exits with the documented failure code.
  4. **Reporting is an extension point.** The handler calls a list of
     reporters, logging always first; a project adds its own — a queue,
     ServiceNow, a pager, an error-tracking service — by adding a reporter,
     never by editing the handler. A failing reporter never stops the others.
  5. **Nothing inside it may fail.** A handler that throws replaces the real
     failure with its own. Guard every internal step and degrade to silence
     rather than propagate.
  6. **Nothing it hands off leaves the process unredacted**
     (`sdsi:secrets`).
- **try/catch only where the logic requires it** — retrying a transient
  failure, translating a vendor/library error into a typed one, releasing a
  resource, or a business rule with a genuine fallback. Everything else lets
  the error propagate to the global handler. A try/catch that only logs and
  re-raises, logs and continues, or swallows the error is a finding: it
  duplicates the handler or hides the failure.
- **Retry only what's transient.** A shared retry helper for expected,
  transient failures (a flaky network call, a locked file) re-raises the
  last error once attempts run out, so a real bug still fails loudly.
  Non-transient failures propagate to the global error handler. Retrying
  the non-transient just delays the same failure; treating the transient as
  fatal costs reliability for nothing.
- **A disabled capability fails its task — it never returns an empty
  success.** An empty result and a broken one look identical to whatever's
  watching.
- **A run with no instruction** (no task or command given) **fails** — a
  scheduled job that does nothing and reports "fine" is the failure nobody
  notices.
- **Every exit path reports a machine-readable outcome**, separate from any
  free-text reason (which may be redacted and must never be branched on):

  | Outcome | Roughly means |
  |---|---|
  | Succeeded | Ran fine |
  | Failed | Ran, and the work itself failed |
  | Invalid input | Bad or missing arguments — a usage error |
  | Critical / startup failure | Couldn't even get configured — alert, don't retry |
  | Interrupted | Stopped by the platform mid-run — routine, not an incident |

  Map each to a distinct, documented exit code (or status). Every exit path
  — including failures before config finishes loading — reports
  *something*; a caller waiting for an answer that never comes just times
  out.

## Review checklist

No global error handler, or one not wired into the language's
uncaught-error hooks · a global handler that doesn't log, or has no reporter
extension point · a long-running process that dies on one bad request or
unit of work · a try/catch with no logic reason (log-and-rethrow,
log-and-continue) · a generic error type raised or caught for an
anticipated failure · a catch-all that swallows errors · an error handler
that can itself throw ·
retries around a non-transient failure · a retry loop that doesn't re-raise
· a disabled feature returning empty success · a no-op run reporting success
· exit paths without a distinct outcome · branching on an error's message
text.
