---
name: concurrency
description: >
  SDSI's concurrency standard, language-neutral — choosing the model (async
  event loop, thread or process pools, a dedicated worker with its own
  queue), parallelism with bounded pools, the right synchronization
  primitive (mutex, semaphore, future, event, latch, barrier, condition),
  making key steps wait for what they depend on, preventing deadlocks and
  starvation, the Asynchronous Request-Reply pattern behind one reusable
  job harness, owning shared state, timeouts on every wait, bounded queues,
  graceful shutdown, and testing concurrent code. Use when adding threads,
  async code, worker pools, locks, background jobs, long-running
  operations, or signal handling, or when reviewing any of them. Reads
  sdsi:core first. Triggers on "/sdsi:concurrency", "threading", "async",
  "parallel", "deadlock", "semaphore", "mutex", "background worker",
  "long-running job", "graceful shutdown".
argument-hint: "[--review|--apply] [path|branch]"
---

# SDSI: Concurrency

Before anything else, read `../core/SKILL.md` and run its steps.

The shutdown rules come from real projects; the rest is drawn from widely accepted practice. Grow it from real project lessons, not speculation (core §2, "no over-engineering").

## Rules

- **Don't add concurrency without a measured reason.** A sequential program is easier to reason about, test, and debug. Add threads, async, or processes when there's a real bottleneck (I/O wait, a blocking write, CPU-bound work that can split), and write the reason next to it.
- **Every piece of shared mutable state has one owner.** Prefer passing messages (a queue) over sharing memory; where state must be shared, one type owns it and guards every access. Shared singletons — the central logger, the config object, the secrets accessor — are safe to call from any worker.
- **Every wait has a timeout** — a lock, a semaphore, a queue read, a future, a network call, a join. An unbounded wait turns a slow dependency into a hung process.
- **Blocking work never runs on the main/event path.** A slow disk or network call moves to a background worker (the log file writer is the standard example, `sdsi:logging`).
- **Queues are bounded.** An unbounded queue hides a slow consumer until memory runs out; a bounded one surfaces it as back-pressure.
- **Errors in a worker are never lost.** A failure in a background thread or task reaches the main flow and the global error handler (`sdsi:errors`) — never silently dies with the worker.

## Choosing the model

**One concurrency model per program**, chosen from the shape of the work and written in `CLAUDE.md`. Mixing models without a clear boundary is where deadlocks and lost errors come from.

| The work | Use |
|---|---|
| Many concurrent waits on I/O — network, disk, other services — with little CPU | An async event loop |
| CPU-heavy work that must run in parallel | A pool of processes — or threads, where the runtime runs them truly in parallel |
| A blocking call that async code can't avoid (a library with no async API) | The runtime's offload to a thread pool, never a blocking call on the loop |
| A few long-lived background duties (a log writer, a poller, a sender) | A dedicated worker thread with its own bounded queue |
| Work that outlasts a request or must survive a restart | A durable job, run through the job harness (Asynchronous Request-Reply, below) |

- **The boundary between two models is one explicit hand-off** — a queue, or the runtime's offload call — in one place, never sync and async code calling each other ad hoc.
- **Reuse pools; never create a thread or process per task.** A pool is created once, sized from config, and shut down with the program.

## Parallelism

- **Pools are bounded and sized from config** — not "one per core" by assumption, and never unbounded. CPU-bound pools size near the core count; I/O-bound concurrency sizes from what the downstream system tolerates.
- **Separate pools for separate kinds of work** — CPU-bound apart from I/O-bound, slow apart from fast — so one class of work can't occupy every worker and starve the other.
- **Fan out with a bound, fan in completely.** Running N things at once goes through a semaphore or bounded pool; the fan-in waits for every one, collects every result *and* every error, and decides explicitly — fail all, or return partial results — never takes the first and leaves the rest running unobserved.
- **When one branch's failure makes the rest pointless, cancel the siblings** through the runtime's structured cancellation (a task group, a cancellation token), so nothing keeps working on a result nobody will read.
- **Partition the data so workers share nothing**, and combine the parts once at the end. Shared accumulators under a lock are the slow, error-prone version of the same thing.
- **Results are ordered on purpose** — by key or by input order — never by whichever worker finished first, unless completion order is the requirement.

## Synchronization — the right primitive

Prefer the highest-level tool that fits — a queue or a future over a raw lock — and pick by what you actually need:

| Need | Primitive |
|---|---|
| One at a time through a critical section | A mutex (lock) |
| At most N at once — a connection limit, a cap on concurrent calls to a system | A counting semaphore |
| Wait until X has finished before running | A future/promise/task join — or an event/latch when several things wait on one signal |
| Wait until N things have finished | A countdown latch, or join all N futures |
| All workers reach a point before any continues | A barrier |
| Wait for a condition on shared state to become true | A condition variable, always re-checking the predicate in a loop |
| Many readers, rare writers | A read-write lock — only when measured contention justifies it |

- **Hold a lock briefly and never across I/O, a callback, or an `await`.** Copy what you need, release, then do the slow work.
- **Acquire and release are paired in one scope** — the language's `with`/`using`/`defer`/`finally` form — so an error can't leave a lock held or a semaphore permit lost.
- **Async code uses the runtime's async primitives** (async lock, async semaphore, async event), never thread locks: a thread lock blocks the whole event loop.
- **Key steps wait for what they depend on, never on time.** A process that must not run until another finishes waits on that one's future, event, or latch — with a timeout, failing loudly when it expires. A `sleep` that "should be long enough", or a loop polling a flag, is a race waiting for a slow day.
- **Startup is gated the same way:** a component that needs another ready (a connection pool, a loaded cache) waits on its readiness signal with a timeout, and the program reports not-ready until every gate opens.

## Preventing deadlocks

- **One global lock order, written next to the locks.** Every code path that holds two locks takes them in that order. Two paths taking the same pair in opposite orders is a deadlock waiting for load.
- **Hold one lock at a time where possible.** Needing two is a design smell; merge the state under one owner or pass a message instead.
- **Never call unknown code while holding a lock** — a callback, an overridable method, an event handler, a log handler that might lock — because you can't know what it will try to take.
- **Every acquisition has a timeout** (a try-lock with a deadline). On timeout, release what you hold, log which locks were involved, and fail or retry with backoff — never wait forever.
- **A task never waits on a task queued behind it in the same bounded pool** — when every worker is waiting, nothing is left to run what they wait for. Run the dependent work inline, or on a separate pool.
- **No circular waits through bounded queues** — two workers each blocked putting into the other's full queue deadlock just like two locks. Break the cycle or make one direction non-blocking.
- **Async code never blocks synchronously on async work** — waiting on a task from the event loop's own thread waits forever for a loop that can't run it.

## Preventing starvation and livelock

- **Critical sections are short**, so no waiter is stuck behind long work holding a lock.
- **Queues are FIFO by default.** Priorities, when needed, are few and age upward, so low-priority work still runs; a read-write lock that lets readers starve writers is replaced or made fair.
- **A shared resource is shared fairly** — per caller, tenant, or source quotas on a shared pool or rate limit — so one heavy caller can't take every slot.
- **Retries use jittered backoff** (`sdsi:errors`), so competing workers don't collide and retry in lockstep forever — the usual livelock.
- **Starvation is observable:** log or measure queue wait time, pool saturation, and how long the oldest item has waited, with a configured threshold that warns before users notice.

## Long-running work — the Asynchronous Request-Reply pattern

When an operation can outlast the caller's timeout or a normal response time — a report, an import, a batch, a slow external call — the caller doesn't wait on an open connection. It submits, gets a handle back at once, and asks for the result later.

1. **Submit:** validate the request, **persist the job before starting it**, and answer immediately with its ID and a status location (`202 Accepted` with `Location` over HTTP, plus `Retry-After`). A repeated submit with the same idempotency key returns the same job, never a second one.
2. **Run:** a worker takes the job from a durable queue under a lease it renews with a heartbeat. The job moves through one state machine — `queued → running → succeeded | failed | cancelled | expired` — and every transition is atomic.
3. **Status:** asking for the job returns its state, progress, and — when finished — where the result is (`303 See Other` to the result over HTTP), or the error code and correlation ID (`sdsi:errors`).
4. **Result:** kept for a configured time, then expired; asking after that is a clear "gone", never a silent empty success.
5. **The caller** polls honoring `Retry-After` with backoff, or registers a callback — signed, retried, and with polling still available as the fallback.
6. **Cancel:** an explicit cancel request; the worker checks for it at safe points and leaves data consistent.
7. **Stuck work is reclaimed:** a job past its maximum runtime fails as timed out, and a lease whose heartbeat stopped (a crashed worker) returns the job to the queue — which is why every handler must be safe to run again (`sdsi:errors`, idempotency).

### Build the harness once

**One job harness per program** (core §2, "one front door per capability") owns everything above: submission and idempotency, persistence, the state machine, leases and heartbeats, retries for transient failures, timeouts, progress, cancellation, result retention and expiry, the status interface, callbacks, the correlation ID carried from submit to worker to result, and the metrics — queue depth, oldest job's age, run time, failures. Each long operation is a **handler registered with the harness**, holding only its business logic. A handler that builds its own polling, retry, or status plumbing is a finding.

## Graceful shutdown

- **Convert the platform's graceful-stop signal into the normal shutdown path**, so logs drain and the global error handler still runs on a routine stop, not only on a crash. A forceful kill usually can't be caught; plan for it.
- **Stop taking new work first, then drain.** Pools and the job harness refuse new work, finish or hand back (release the lease of) what's in flight, then exit.
- **Every drain is bounded**, and the total bound sits comfortably under the platform's stop-to-kill grace period — a drain still running at the kill loses whatever hadn't flushed.
- **An interrupted run reports `Interrupted`** (`sdsi:errors`), not a failure — it's routine.
- **Work that moves data in batches is resumable**: it can pick up cleanly after an interruption rather than reprocessing everything.

## Testing concurrent code

- **Test the logic sequentially first; test concurrency behavior separately.**
- **A test of concurrent behavior is deterministic** — control the timing (fake clocks, explicit synchronization points, an injectable scheduler), never `sleep` and hope.
- **Every concurrent test has its own timeout**, so a deadlock fails the test instead of hanging CI.
- **Run the language's race detector or thread sanitizer in CI** where one exists; it finds races a test only hits once in a thousand runs.
- **Code that guards shared state gets a stress test** — many workers, many iterations — marked so it runs selectively (`sdsi:testing`).
- **The job harness is tested once, thoroughly**, with a fake clock: a duplicate submit, a cancellation, a crash mid-run and lease reclaim, a timeout, result expiry. Each handler is then tested directly, without the harness.
- **A flaky concurrent test is a bug report, not noise** — find the race.

## Upkeep

The line `sdsi:upkeep` installs in the project's `.claude/rules/sdsi.md`:

- Adding threads, async code, a pool, a lock, or a long-running operation → choose the model and primitive per `sdsi:concurrency`, give every wait a timeout, keep one lock order, and run long work through the project's job harness (`sdsi:concurrency`)

## Review checklist

Concurrency with no stated reason · two concurrency models mixed without one explicit boundary · a thread or process created per task instead of a pool · an unbounded pool · CPU-bound and I/O-bound work sharing one pool · a fan-out with no bound, or a fan-in that drops errors or leaves work running · shared mutable state without one owner · a lock held across I/O, a callback, or an `await` · a thread lock in async code · locks taken in inconsistent order · a lock or semaphore acquired outside a scoped block · a wait with no timeout · a `sleep` or polling loop standing in for a dependency wait · a task waiting on work queued behind it in the same pool · blocking I/O on the main/event path · an unbounded queue · no fairness or aging where priorities exist · no visibility into queue wait time · a long operation holding the caller's connection open · a job started before it's persisted · job plumbing (polling, status, retries) rebuilt in a handler instead of the harness · a worker whose errors vanish · no handling of the graceful-stop signal · an unbounded shutdown drain · sleep-based concurrency tests · a concurrent test with no timeout.
