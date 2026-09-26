---
name: concurrency
description: >
  SDSI's concurrency standard, language-neutral — choosing one concurrency
  model per program, owning shared state, timeouts on every wait, keeping
  blocking work off the main path, bounded queues, graceful shutdown on a
  stop signal with a drain that fits the platform's grace period, and
  testing concurrent code. Use when adding threads, async code, worker
  pools, background jobs, or signal handling, or when reviewing shutdown
  behavior. Reads sdsi:core first. Triggers on "/sdsi:concurrency",
  "threading", "async", "background worker", "graceful shutdown".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Concurrency

Before anything else, read `../core/SKILL.md` and run its steps.

This topic is a seed: the shutdown rules come from real projects, the rest is a starting position. Extend it from real project lessons, not speculation (core §2, "no over-engineering").

## Rules

- **Don't add concurrency without a measured reason.** A sequential program is easier to reason about, test, and debug. Add threads, async, or processes when there's a real bottleneck (I/O wait, a blocking write), and write the reason next to it.
- **One concurrency model per program**, chosen deliberately and written in `CLAUDE.md` — the language's async runtime, threads, or processes. Mixing them without a clear boundary is where deadlocks and lost errors come from.
- **Every piece of shared mutable state has one owner.** Prefer passing messages (a queue) over sharing memory; where state must be shared, one type owns it and guards every access. Shared singletons — the central logger, the config object, the secrets accessor — are safe to call from any worker.
- **Every wait has a timeout** — a lock, a queue read, a network call, a join. An unbounded wait turns a slow dependency into a hung process.
- **Blocking work never runs on the main/event path.** A slow disk or network call moves to a background worker (the log file writer is the standard example, `sdsi:logging`).
- **Queues are bounded.** An unbounded queue hides a slow consumer until memory runs out; a bounded one surfaces it as back-pressure.
- **Errors in a worker are never lost.** A failure in a background thread or task reaches the main flow and the global error handler (`sdsi:errors`) — never silently dies with the worker.

## Graceful shutdown

- **Convert the platform's graceful-stop signal into the normal shutdown path**, so logs drain and the global error handler still runs on a routine stop, not only on a crash. A forceful kill usually can't be caught; plan for it.
- **Every drain is bounded**, and the total bound sits comfortably under the platform's stop-to-kill grace period — a drain still running at the kill loses whatever hadn't flushed.
- **An interrupted run reports `Interrupted`** (`sdsi:errors`), not a failure — it's routine.
- **Work that moves data in batches is resumable**: it can pick up cleanly after an interruption rather than reprocessing everything.

## Testing concurrent code

- Test the logic sequentially first; test concurrency behavior separately.
- A test of concurrent behavior must be deterministic — control the timing (fake clocks, explicit synchronization points), never `sleep` and hope.
- A flaky concurrent test is a bug report, not noise — find the race.

## Review checklist

Concurrency with no stated reason · two concurrency models mixed without a boundary · shared mutable state without one owner · a wait with no timeout · blocking I/O on the main/event path · an unbounded queue · a worker whose errors vanish · no handling of the graceful-stop signal · an unbounded shutdown drain · sleep-based concurrency tests.
