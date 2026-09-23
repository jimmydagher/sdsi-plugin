---
name: mw
description: >
  SDSI project type for middleware and integration services — processes
  that move and reconcile data between external systems (sync jobs, ETL,
  connector layers feeding a system of record). Owns the source layout
  (helpers / connectors / business / tasks), the no-logic entry point with
  a task selector, the extract → business rules → destination data flow
  with a staging cache and lineage, the systems-block config pattern,
  secrets for many systems, the response contract, and one artifact run in
  several shapes. Silent unless the SDSI profile's project type is mw, or
  it's invoked by name. Reads sdsi:core first. Triggers on "/sdsi:mw",
  "integration service", "sync job", "data pipeline", "ETL".
---

# SDSI: Middleware & Integration Project

Before anything else, read `../core/SKILL.md` and run its steps. This skill
owns the source layout, entry point, and design shape for a service whose
whole job is moving and reconciling data between systems. Topics still apply
in full; this skill only adds what's true because the project is middleware.

Distilled from building `ariel` (job, workforce, and spend data from several
source systems into a financial system of record and on to a warehouse).
Extend it from an actual second project, not speculation.

## Layout

```
src/
├── <entry point>   # no logic — wires startup, dispatches the task, exits with its outcome
├── helpers/        # infrastructure that knows no vendor — the one shared-code home
├── connectors/     # one module per external system + the pipeline joining them.
│                   #   Output is a flat cached file: call, page, retry, flatten,
│                   #   cache — and stop. No business rule lives here.
├── business/       # rules that decide something: read a cached extract, write another
└── tasks/          # one callable per operation + the registry mapping name → handler
```

- **Dependencies point one way:** `helpers` ← `connectors` ← `business` ←
  `tasks` ← entry point.
- **The mechanical/business boundary is a file, not a convention.** A
  connector never applies a rule; `business/` never calls a vendor. A rule
  inside a connector (or a vendor call inside `business/`) is an
  architecture bug, reviewed like one.
- **Name tooling folders for what runs them.** `scripts/<shell>/` for what a
  human or deploy step runs, `scripts/python/` (or the project's language)
  for tooling, and a separate `pipelines/` for CI/CD definitions — kept
  strictly upstream of `scripts/`. A pipeline builds and pushes; a script
  runs or deploys. Never one file that does both.

## Entry point and tasks

A single entry point with a task selector keeps each operation small,
testable, and independently retriable:

```
<run the program> --task SOME-OPERATION
```

- **Each task does one job** and can be run, scheduled, or retried alone.
- **The registry asserts completeness at startup** — every declared task has
  a handler.
- **A per-system or per-task on/off toggle** in config gives operational
  control without a redeploy; a disabled one fails its task rather than
  returning empty success (`sdsi:errors`).
- **Prefer a job that runs one task and exits** over a long-running service
  when the workload is batch or triggered.
- **A validate-config task** (`sdsi:config`) that checks config and
  credential access without real work is mandatory here — it's what a
  deploy runs before trusting a new artifact.

## Data movement

```
extract    vendor API → download → retry → flatten → cache
business   cache      → rules → transform → cache
load       cache      → the destination's shape → write → destination
```

- **The cache holds what the connector returned, already flattened** — not
  the vendor's raw nested payload. That keeps the mechanical/business
  boundary a physical file. The cost is real: a deeply nested value is
  harder to re-model later. If a raw copy is ever needed, add it as a second
  cache write behind its own setting; don't reorder the pipeline.
- **The cache is scratch space, not storage** — safe to lose; purge old
  entries at the start of a run.
- **Period/incremental filters apply to cached rows, after the extract,
  never before** — so the cache holds the full response and another window
  can be replayed. Key the filter on the *cached, flattened* field name; the
  vendor's original spelling silently matches nothing and reports a clean,
  empty, wrong success.
- **Declare per source whether it can answer "changed since X"**, and log
  loudly whenever a window is emulated locally (full fetch, filtered after)
  — the cost is easy to miss.
- **Every record written to a destination carries lineage** — source system,
  scope/dataset, run id, load time, and where useful a content hash — so a
  bad load can be found and removed.
- **Batch work is resumable** (`sdsi:concurrency`).

## Configuration: the systems block

Every external system is configured with the same shape, so the connector
base type needs no per-system special cases:

```yaml
systems:
  <system-name>:
    enabled: true
    base_url: <not configured>
    auth: oauth2          # or api_key / bearer / basic / database
    secret_name: <not configured>
    username: <not configured>   # only when auth needs one
    timeout: 30
    retries: 3
    page_size: 100
```

- **Every system declares every key**, marking the ones that don't apply
  explicitly, so "unused" reads differently from "forgot to configure".
- **The pre-config environment variables are a short, enumerated list** near
  the loader — config directory, environment name, where logs/cache land,
  and what the platform injects for identity.
- **Three derived values, named the same way every time:** `environment`
  (from the applied override), the reporting mode (from whether the invoker
  supplied a callback address), and the running version (from `VERSION`
  baked into the artifact — not from config, which ships on its own
  schedule).

## Secrets for many systems

- **Name = `<system>-<purpose>-<kind>`, derived from the system's `auth:`**:

  | `auth:` | Name shape | Example |
  |---|---|---|
  | `api_key` | `<system>-api-key` | `crm-api-key` |
  | `oauth2` | `<system>-client-secret` | `payroll-client-secret` |
  | `bearer` | `<system>-bearer-token` | `banking-bearer-token` |
  | `basic` | `<system>-basic-pwd` | `ledger-basic-pwd` |
  | a database | `<system>-database-pwd` | `warehouse-database-pwd` |
  | a paired credential | `<system>-<purpose>-pair` | `payroll-client-pair` |
  | the platform's own | `container-<purpose>-<kind>` | `container-validation-key` |

- **A short per-environment suffix on the store's own name** (not the
  secret's) keeps the store → local override mapping legible.
- **Identity and grants are two lists for two callers:**

  | Who | Needs | Symptom without it |
  |---|---|---|
  | The running workload's identity | Read on the secrets store; pull on the artifact registry | No store access: starts, fails on first read. No registry access: never starts, often with a generic error |
  | Whatever invokes it (orchestrator, scheduler) | Its own grant to create/manage runs | Looks nothing like a workload-identity failure — don't debug one as the other |

  **Anything creating a fresh instance per run uses a pre-provisioned,
  reusable identity** attached to each instance — a per-instance identity is
  new and ungranted every run.

## The response contract

- **The reporting mode comes from what the invoker supplied**, not a flag
  saying the same thing: a callback address present → report there;
  otherwise print and exit with a code. A second way to express it is a
  second source of truth.
- **Outcomes and exit codes** follow `sdsi:errors`' table; the caller branches
  on the code, never the free-text reason.
- **A caller blocked on a callback always hears something** — including on a
  startup failure before the callback mechanism is wired.
- **A warning discovered after the log closes can only reach the console**
  (and any alert payload) — say so in code (`sdsi:logging`).
- **Shutdown:** convert the graceful-stop signal into the normal path; bound
  the log drain under the platform's grace period (`sdsi:concurrency`).

## One artifact, several run shapes

- **Build one artifact; how it's invoked decides its shape** — the same
  image with a different task and wiring is a scheduled batch in one
  deployment and a callback-driven one-off in another.
- **The pipeline stops at a validated, tagged artifact** (or a published,
  validated config bundle). Nothing restarts onto it because a build
  finished — a person or an explicit deploy step decides.
- **One shared config store for every environment means publishing the
  default is a production change** — scope an automatic publish to that
  environment's own override; publishing wider needs a deliberate action.

## Change discipline on an established service

- **Keep a concrete "what changed → what else to update" table**
  (`sdsi:docs`) for this service's moving parts: a new task touches the
  registry and wherever a human picks a task by hand (debugger launch
  config, runbook); a new secret touches setup docs and the cheat sheet; a
  new environment variable touches every place local dev mirrors deployed
  wiring; a deploy script's parameters touch its deployment doc.
- **Build a new connector by reading an existing one's code in full** —
  it may reveal that the reference never faced this system's problem (no
  paging, a paired credential, no "changed since" filter).
- **Test a rotation wait, a retry, or a paging walk against the real system
  at least once**, deliberately, outside CI.

## Review checklist

Logic in the entry point · a business rule in a connector or a vendor call in
`business/` · a task registry without a startup completeness check · a
filter applied before the cache write, or keyed on the vendor's field name ·
destination rows without lineage · systems with differing config shapes ·
secret names not derived from `auth:` · a reporting mode set by flag · a
pipeline that also deploys · config published to the shared default
automatically.
