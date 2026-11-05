# SDSI Companion — Middleware & Integration

For projects whose profile lists **mw** in `Companions` — services that move and reconcile data between external systems (sync jobs, ETL, connector layers feeding a system of record). Not a skill: `sdsi:core` §1 Step 2 reads this file when the profile names it, and a running skill applies **only the section headed with its own name**. A skill with no section here has no middleware-specific additions; it proceeds on its own rules.

Language- and framework-neutral: apply each rule through whatever integration framework, scheduler, or broker the project uses. Framework- or vendor-specific lessons belong in the project's own `CLAUDE.md`, not here.

**A seed, not a finished standard.** Distilled from building `ariel` (job, workforce, and spend data from several source systems into a financial system of record and on to a warehouse), then checked in 2026-11 against widely accepted integration and data-pipeline guidance and the connector protocols of Airbyte and dbt (sources at the end). Grow it from a second real project, not speculation.

## sdsi:workflow

- **A change to a mapping or business rule states what happens to data already loaded** — reprocess a stated window, leave history as it is, or correct it with a one-off run. Write the decision into the plan; a rule change that silently applies only from "now" leaves the destination with two meanings for the same field.
- **A backfill or replay is a planned run, not a side effect** — its window, the systems it touches, and the expected record count are stated before it runs, so the bulk-change approval (`sdsi:core` §2) has a real scope to approve.

## sdsi:standards

- **Data moves in three fixed stages, run by one shared piece of orchestration, with a file between each:**

  ```text
  extract    vendor API → download → retry → flatten → cache
  business   cache      → rules → transform → cache
  load       cache      → the destination's shape → write → destination
  ```

  A connector calls a vendor, pages, retries, flattens, and caches — it never applies a rule. Business rules read a cached extract and write another — they never call a vendor. A rule inside a connector (or a vendor call inside a rule) is an architecture finding. The cache holds the connector's flattened output and is scratch space, not storage: safe to lose, purged at the start of a fresh run, and kept by a run that resumes (`## sdsi:concurrency`). One task per operation, from a registry that asserts completeness at startup, selected when the run is invoked.
- **Every destination write is idempotent: running the same load twice leaves the destination exactly as running it once.** Upsert on a stable business key and write absolute values, never increments or blind inserts. Exactly-once delivery can't be guaranteed across systems; at-least-once delivery plus idempotent writes is the design. The deduplication key is stable across every retry and redelivery — the source system plus the record's own identifier (or a producer-assigned message ID), never a receive timestamp, an attempt number, or a transport ID the broker regenerates — and the destination enforces it (a uniqueness constraint, a conditional write), not a check-then-write in code that two workers can both pass. A write that can't be made idempotent is retried only with an idempotency key the destination honors (the same key on every attempt), or not retried at all — a timeout doesn't say whether the first attempt landed.
- **Incremental extracts advance a watermark only after the load commits.** The watermark is the highest value actually observed in the source (a sequence, log position, or modified-time), never the local clock; each run re-reads a configured overlap window behind it, and the idempotent write absorbs the repeats. Period and incremental filters apply to cached rows, after the extract, keyed on the *flattened* field name — the vendor's original spelling silently matches nothing and reports a clean, empty, wrong success. Declare per source whether it can answer "changed since X", and log loudly whenever a window is emulated locally (full fetch, filtered after).
- **A paging walk ends only on the source's own end signal** (an empty next-page token, an explicit last-page flag) — never on a short or empty page — and repeats every other parameter unchanged on each page. Page tokens are opaque: passed back as received, never parsed or built.
- **Read tolerantly, validate what you use.** A connector checks the fields the flow actually consumes and ignores fields it doesn't, so a vendor adding a field breaks nothing; a used field that's missing or mistyped rejects the record (`sdsi:errors`). Drift in a used field — a type, a format, a field gone from the source's schema — is logged as a warning the first time a run sees it, so a vendor change reads as a change, not as a rising rejection count.
- **Every record written to a destination carries lineage** — source system, dataset, run ID, load time, and where useful a content hash — so a bad load can be found and removed.
- **A flow that updates its own store and must also notify another system writes both in one local transaction** — the outgoing message goes into an outbox table that a separate relay sends. Never write the store and then call the other system as two steps a crash can split. The relay delivers at least once, so the receiving side is idempotent.

## sdsi:config

- **Every external system is configured with the same shape**, so the connector base needs no per-system special cases:

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
      backoff_base: 1        # seconds, first retry delay before jitter
      backoff_cap: 60        # seconds, the most any one retry waits
      retry_budget: 300      # seconds, the most all retries of one call wait in total
      rate_limit: <not configured>   # requests per second the system allows
      page_size: 100
      overlap: 300           # seconds re-read behind the watermark
  ```

  Every system declares every key, marking the ones that don't apply, so "unused" reads differently from "forgot to configure".

- **The watermark is state, not config.** It lives in durable storage the run reads and writes (a state table, the destination itself), never in a config file a deploy can overwrite or roll back.
- **Three derived values, named the same way every time:** `environment` (from the applied override), the reporting mode (from whether the invoker supplied a callback address), and the running version (from `VERSION` baked into the artifact — config ships on its own schedule).
- **A validate-config task is mandatory** — the deploy runs it before trusting a new artifact.

## sdsi:security

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

- **Each system's credential carries only what the flow needs from it** — read-only on a source, write on only the destination objects the load touches. An integration account with admin rights turns a mapping bug into a data-loss incident.
- **Move only the data the flow needs.** An extract requests the fields the flow uses, not the whole record, and the cache and the rejected-records store each have a stated retention after which their copies of personal or financial data are deleted.
- **Identity and grants are two lists for two callers:**

  | Who | Needs | Symptom without it |
  |---|---|---|
  | The running workload's identity | Read on the secrets store; pull on the artifact registry | No store access: starts, fails on first read. No registry access: never starts, often with a generic error |
  | Whatever invokes it (orchestrator, scheduler) | Its own grant to create and manage runs | Looks nothing like a workload-identity failure — don't debug one as the other |

- **Anything creating a fresh instance per run uses a pre-provisioned, reusable identity** — a per-instance identity is new and ungranted every run.

## sdsi:logging

- **Every load reconciles before it reports success, and every task ends with one summary line saying so:** run ID, source, the window extracted, records read, written, rejected, and skipped as duplicates, and duration. Read must equal written + rejected + skipped, per source and run, and where the data carries amounts, a control total is compared between the extract and the destination. A mismatch fails the task — a count that doesn't add up is lost or invented data.
- **Each flow has a freshness target** (its data in the destination within a stated time of the source), stated in `SPEC.md` and alerted on when missed — a flow that silently stops running reports nothing at all.
- **Log record keys, never record payloads.** Moved data is usually personal or financial; a source ID and the run ID find the record without copying it into the log.
- **Each retry logs a warning naming the system, the attempt, and the cause** — throttled versus connection failure versus server error — so a rising throttle count reads as a capacity problem, not noise.
- **A warning discovered after the log file closes can only reach the console** (and any alert payload) — say so in code.

## sdsi:errors

- **Retries are for transient failures only, back off exponentially with jitter, and are bounded.** Retry timeouts, `408`, `429`, `502`, `503`, and `504`; another status (any other 4xx, `500`, `501`) only when the system documents it as transient. Each wait is a random value between zero and `min(backoff_cap, backoff_base × 2^attempt)`, since fixed or un-jittered intervals make every client retry together and keep a struggling system down. A `Retry-After` from the system wins over the computed backoff — wait at least that long — and the total wait for one call never exceeds `retry_budget`, even when `Retry-After` asks for more.
- **Retry at one layer only.** A vendor SDK with its own retry is either that layer, or its retry is switched off — three retries wrapped around three retries is nine calls against a system that's already failing.
- **A bad record is quarantined, not dropped and not fatal.** It goes to a rejected-records store (a dead-letter queue, a rejects table) with the reason, source key, and run ID, and the run continues; a rejection rate above a configured threshold fails the task. A failure of the system itself still fails the task.
- **The reporting mode comes from what the invoker supplied** — a callback address present means report there; otherwise print and exit with a code. Never a second flag saying the same thing. A caller blocked on a callback always hears something, including a startup failure before the callback mechanism is wired, and a disabled system fails its task rather than reporting an empty success that looks like "no new data".

## sdsi:concurrency

- **Two runs of the same task never overlap.** A scheduled run takes a lease or lock per task (with an expiry, so a crashed run doesn't hold it forever); a run that can't take it exits saying another is in progress.
- **A system's rate limit is one budget shared by every worker calling it** — one limiter per system, not one per worker, so adding workers can't multiply the request rate past what the system allows.
- **Parallel writes preserve per-record order where it matters** — partition work by the record's key, or carry a version or modified-time so the destination rejects an update older than the one it holds.
- **Batch runs are resumable.** A load that can't be one transaction records its progress per step, so an interrupted run picks up from the step that failed — or runs an idempotent compensating step for what it already wrote — rather than reprocessing everything or leaving a half-applied load with no record of where it stopped.
- **The log drain on shutdown fits inside the platform's grace period.**

## sdsi:testing

- **Every load has an idempotency test:** run it twice on the same input and assert the destination is unchanged by the second run — no new rows, no doubled amounts.
- **Watermark and paging boundaries are tested explicitly** — a record exactly at the watermark, one inside the overlap window, an empty page, a short page that isn't the last, and the last page.
- **Connector unit tests use fixtures recorded from real responses** (redacted), including a real error body and a real throttling response, not hand-written shapes that match what the code expects.
- **Where the project owns both sides of an integration, a contract test pins the shape between them**, so a producer change that breaks a consumer fails in CI rather than in the next run.
- **A rotation wait, a retry, or a paging walk is tested against the real system at least once**, deliberately, outside CI — a mock can't prove the vendor's real error shape or page boundary.
- **A new connector starts from reading an existing one's code in full** — it may show the reference never faced this system's problem.

## sdsi:docs

- **Each external system gets one integration sheet** in `docs/`: what the flow reads or writes there, the auth type and secret name, the paging style, the rate limit, whether it answers "changed since X", the delivery and retry behavior, and who owns the system on the other side. A destination's sheet also holds its contract — the shape written, its version, and its status (active, deprecated, retired) — which `## sdsi:versioning` governs.
- **A replay/backfill runbook** says how to rerun a window, reprocess quarantined records, and remove a bad load by its run ID — written before it's needed at 2 a.m.
- **Keep the "what changed → what else to update" table concrete for this service:** a new task touches the registry and wherever a human picks a task by hand (debugger launch config, runbook); a new secret touches setup docs and the cheat sheet; a new environment variable touches every place local runs mirror deployed wiring.

## sdsi:versioning

- **The shape written to a destination is a contract with its own version.** Where anything downstream reads what the service writes, the contract records the field names, types, nullability, and meaning. Adding an optional field is a MINOR contract change. Removing, renaming, or retyping a field, making one required, or changing what a field means to its existing readers breaks the contract: its version goes up a MAJOR, and the service releases as MAJOR too, because a deployed consumer breaks until someone acts (`sdsi:versioning`). Evolve by expanding, then contracting — add the new field beside the old one, mark the old one deprecated with its removal date for at least one release, and remove it in a later MAJOR — so producer and consumer never have to deploy in lockstep.

## sdsi:deploy

- **One artifact, several run shapes** — the same image with a different task and wiring is a scheduled batch in one deployment and a callback-driven one-off in another.
- **The first run in a new environment, or of a new or changed flow, is a narrow one** — a short window or a dry run that extracts, transforms, and reconciles without writing — before it runs at full volume.
- **A backfill is its own invocation with an explicit window** — never done by hand-editing the stored watermark.
- **The pipeline stops at a validated, tagged artifact** (or a published config bundle). Nothing restarts onto it because a build finished.
- **One shared config store for every environment means publishing the default is a production change** — scope automatic publishing to that environment's own override.
- **Name tooling folders for what runs them** — human/deploy scripts apart from CI definitions, and a pipeline never also deploys.

## Sources

- Enterprise Integration Patterns — Idempotent Receiver — https://www.enterpriseintegrationpatterns.com/patterns/messaging/IdempotentReceiver.html
- Enterprise Integration Patterns — Dead Letter Channel — https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html
- Enterprise Integration Patterns — Message Translator — https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageTranslator.html
- microservices.io — Transactional outbox — https://microservices.io/patterns/data/transactional-outbox.html
- Microsoft Azure Architecture Center — Idempotent Consumer pattern — https://learn.microsoft.com/en-us/azure/architecture/patterns/idempotent-consumer
- Microsoft Azure Architecture Center — Transient fault handling — https://learn.microsoft.com/en-us/azure/architecture/best-practices/transient-faults
- Microsoft Azure Architecture Center — Compensating Transaction pattern — https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction
- AWS Architecture Blog — Exponential Backoff and Jitter — https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- AWS Builders' Library — Making retries safe with idempotent APIs — https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
- Stripe — Designing robust and predictable APIs with idempotency — https://stripe.com/blog/idempotency
- IETF draft (not yet an RFC) — The Idempotency-Key HTTP Header Field — https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
- RFC 9110 — HTTP Semantics (Retry-After, idempotent methods) — https://www.rfc-editor.org/rfc/rfc9110.html
- RFC 6585 — 429 Too Many Requests — https://www.rfc-editor.org/rfc/rfc6585.html#section-4
- Google AIP-158 — Pagination — https://google.aip.dev/158
- Google SRE Workbook — Data Processing Pipelines — https://sre.google/workbook/data-processing/
- Airbyte protocol — state and checkpointing — https://docs.airbyte.com/platform/understanding-airbyte/airbyte-protocol
- Martin Fowler (Ian Robinson) — Consumer-Driven Contracts — https://martinfowler.com/articles/consumerDrivenContracts.html
- Pact — Contract testing introduction — https://docs.pact.io/
- Confluent — Schema evolution and compatibility — https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
- dbt — Model versions — https://docs.getdbt.com/docs/mesh/govern/model-versions
- Open Data Contract Standard (ODCS) — https://bitol-io.github.io/open-data-contract-standard/
- OpenLineage — Object model (job, run, dataset) — https://openlineage.io/docs/
