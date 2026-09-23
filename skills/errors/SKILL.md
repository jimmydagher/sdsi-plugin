---
name: errors
description: >
  SDSI's error-handling standard — a typed error hierarchy, one fatal-error
  handler built before config or logging exist and that never itself
  raises, retries only for transient failures, failing loudly instead of
  returning an empty success, and a machine-readable outcome on every exit
  path. Use when designing error handling, adding retries, reviewing how
  failures surface, or defining exit codes. Reads sdsi:core first. Triggers
  on "/sdsi:errors", "error handling", "exceptions", "exit codes".
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
- **One fatal-error handler**, called once from the outermost level and
  built **before** configuration or logging exist, so a failure at any
  startup stage is still handled. Two invariants:
  1. **Nothing inside it may fail.** A handler that throws replaces the real
     failure with its own. Guard every internal step and degrade to silence
     rather than propagate.
  2. **Nothing it hands off leaves the process unredacted**
     (`sdsi:secrets`).
- **Retry only what's transient.** A shared retry helper for expected,
  transient failures (a flaky network call, a locked file) re-raises the
  last error once attempts run out, so a real bug still fails loudly.
  Non-transient failures go to the fatal handler. Retrying the non-transient
  just delays the same failure; treating the transient as fatal costs
  reliability for nothing.
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

A generic error type raised or caught for an anticipated failure · a
catch-all that swallows errors · an error handler that can itself throw ·
retries around a non-transient failure · a retry loop that doesn't re-raise
· a disabled feature returning empty success · a no-op run reporting success
· exit paths without a distinct outcome · branching on an error's message
text.
