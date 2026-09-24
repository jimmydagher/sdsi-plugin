# SDSI Companion — Middleware & Integration

For projects whose profile says **Project type: mw** — services that move and
reconcile data between external systems (sync jobs, ETL, connector layers
feeding a system of record). Not a skill: `sdsi:core` §1 Step 2 reads this
file when the project type is mw, and a running skill applies **only the
section headed with its own name**. A skill with no section here has no
middleware-specific additions; it proceeds on its own rules.

Language-neutral. Distilled from building `ariel` (job, workforce, and spend
data from several source systems into a financial system of record and on to
a warehouse); grow it from a second real project, not speculation.

## sdsi:standards

- **Mechanical work and business rules are separate units with a file
  between them.** A connector calls a vendor, pages, retries, flattens, and
  caches — it never applies a rule. Business rules read a cached extract and
  write another — they never call a vendor. A rule inside a connector (or a
  vendor call inside a rule) is an architecture finding.
- **Data moves in three fixed stages, run by one shared piece of
  orchestration:**

  ```
  extract    vendor API → download → retry → flatten → cache
  business   cache      → rules → transform → cache
  load       cache      → the destination's shape → write → destination
  ```

- **The cache holds the connector's flattened output** and is scratch space,
  not storage — safe to lose, purged at the start of a run.
- **Period/incremental filters apply to cached rows, after the extract** —
  keyed on the *flattened* field name. The vendor's original spelling
  silently matches nothing and reports a clean, empty, wrong success.
- **Declare per source whether it can answer "changed since X"**, and log
  loudly whenever a window is emulated locally (full fetch, filtered after).
- **Every record written to a destination carries lineage** — source system,
  dataset, run ID, load time, and where useful a content hash — so a bad
  load can be found and removed.
- **One task per operation, from a registry that asserts completeness at
  startup**, selected when the run is invoked.

## sdsi:config

- **Every external system is configured with the same shape**, so the
  connector base needs no per-system special cases:

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

  Every system declares every key, marking the ones that don't apply, so
  "unused" reads differently from "forgot to configure".
- **Three derived values, named the same way every time:** `environment`
  (from the applied override), the reporting mode (from whether the invoker
  supplied a callback address), and the running version (from `VERSION`
  baked into the artifact — config ships on its own schedule).
- **A validate-config task is mandatory** — the deploy runs it before
  trusting a new artifact.

## sdsi:secrets

- **Secret names are derived from the system's `auth:` value:**

  | `auth:` | Name shape | Example |
  |---|---|---|
  | `api_key` | `<system>-api-key` | `crm-api-key` |
  | `oauth2` | `<system>-client-secret` | `payroll-client-secret` |
  | `bearer` | `<system>-bearer-token` | `banking-bearer-token` |
  | `basic` | `<system>-basic-pwd` | `ledger-basic-pwd` |
  | a database | `<system>-database-pwd` | `warehouse-database-pwd` |
  | a paired credential | `<system>-<purpose>-pair` | `payroll-client-pair` |
  | the platform's own | `container-<purpose>-<kind>` | `container-validation-key` |

- **Identity and grants are two lists for two callers:**

  | Who | Needs | Symptom without it |
  |---|---|---|
  | The running workload's identity | Read on the secrets store; pull on the artifact registry | No store access: starts, fails on first read. No registry access: never starts, often with a generic error |
  | Whatever invokes it (orchestrator, scheduler) | Its own grant to create and manage runs | Looks nothing like a workload-identity failure — don't debug one as the other |

- **Anything creating a fresh instance per run uses a pre-provisioned,
  reusable identity** — a per-instance identity is new and ungranted every
  run.

## sdsi:errors

- **The reporting mode comes from what the invoker supplied** — a callback
  address present means report there; otherwise print and exit with a code.
  Never a second flag saying the same thing.
- **A caller blocked on a callback always hears something**, including a
  startup failure before the callback mechanism is wired.
- **A disabled system fails its task** — never an empty success that looks
  like "no new data".

## sdsi:logging

- **A warning discovered after the log file closes can only reach the
  console** (and any alert payload) — say so in code.

## sdsi:concurrency

- **Batch runs are resumable** — they pick up after an interruption rather
  than reprocessing everything.
- **The log drain on shutdown fits inside the platform's grace period.**

## sdsi:testing

- **A rotation wait, a retry, or a paging walk is tested against the real
  system at least once**, deliberately, outside CI — a mock can't prove the
  vendor's real error shape or page boundary.
- **A new connector starts from reading an existing one's code in full** —
  it may show the reference never faced this system's problem.

## sdsi:docs

- **Keep the "what changed → what else to update" table concrete for this
  service:** a new task touches the registry and wherever a human picks a
  task by hand (debugger launch config, runbook); a new secret touches setup
  docs and the cheat sheet; a new environment variable touches every place
  local runs mirror deployed wiring.

## sdsi:deploy

- **One artifact, several run shapes** — the same image with a different
  task and wiring is a scheduled batch in one deployment and a
  callback-driven one-off in another.
- **The pipeline stops at a validated, tagged artifact** (or a published
  config bundle). Nothing restarts onto it because a build finished.
- **One shared config store for every environment means publishing the
  default is a production change** — scope automatic publishing to that
  environment's own override.
- **Name tooling folders for what runs them** — human/deploy scripts apart
  from CI definitions, and a pipeline never also deploys.
