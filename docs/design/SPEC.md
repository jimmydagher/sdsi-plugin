# SPEC — sdsi plugin

## TTD017 — Ponytail-inspired coding discipline

Source reviewed: https://github.com/dietrichgebert/ponytail (MIT, "the best code is the code you never wrote"; benchmark figures are self-reported, so none are copied in).

### What SDSI already has (not repeated)
`sdsi:core` §2 already covers no over-engineering (with a post-write size check), no assumptions, standard library first, one front door, and no pointless changes; `sdsi:standards` covers reuse over reimplementation and dead code.

### Behavior changes (the gaps Ponytail fills)
1. **The ladder** — before writing code, stop at the first rung that solves it: needed at all → already in the codebase → standard library → native platform feature → already-installed dependency → one line → only then the minimum that works. New dependencies stay governed by `sdsi:dependencies`; the ladder only points to it. Lives in `sdsi:optimize` (TTD022); core §2 keeps the one-line principle.
2. **Read before cutting** — the ladder runs after reading the code the change touches and tracing the real flow; lazy about the solution, never about reading. Lives with the ladder in `sdsi:optimize`.
3. **Lazy, not negligent** — the ladder never removes trust-boundary validation, data-loss handling, security, or accessibility. Stated in core §2's principle and in `sdsi:optimize`.
4. **Tests for risky logic** — code with a branch, loop, parser, money handling, or security meaning gets at least one small test; a pointer from core, the rule itself lives in `sdsi:testing` (add/confirm there, no restating).
5. **Honest reporting** — every finished change states what was skipped or not checked and the known risks. Lives in `sdsi:workflow`, one place only.
6. **Marked shortcuts** — a deliberate shortcut gets a `shortcut:` comment saying when to revisit it; the tag word may be overridden in the project's `CLAUDE.md`. Collected into outstanding work via `meta/TODO.md` (`sdsi:docs`) rather than a new ledger command, to avoid a second list. Lives in `sdsi:optimize` (TTD022), whose sweep revisits them.
7. **Review checklists** — the touched skills' Review checklists gain the matching smells (built before checking existing code, a shortcut with no `shortcut:` note, risky logic with no test, a final report that omits what was skipped).

### Explicitly not adopted
- Intensity levels (`lite/full/ultra`), `/ponytail-*` commands, the benchmark scoreboard, and the separate audit/debt/gain commands: SDSI already has `--review`/`--apply` and `meta/TODO.md`.
- Installing or depending on the ponytail plugin itself.

### Constraints
- One topic, one file; language-neutral; skill descriptions ≤ 1024 chars; changelog entries cite `TTD017`; no hand edits to `plugin.json` version.

## TTD022 — `sdsi:optimize`: one topic for lean, simple, fast code (TODO #22)

Sources reviewed: Ponytail (https://github.com/dietrichgebert/ponytail, MIT — already absorbed by TTD017), Impeccable (https://github.com/pbakaus/impeccable, Apache-2.0 — its `optimize`, `distill`, and `extract` references; only the language-neutral ideas are taken, no text copied, and its UI-design commands stay out), and Claude Code's built-in `/simplify` (its four lenses: reuse, simplification, efficiency, altitude).

### Goal
The rules that keep code small, simple, and fast are spread across `sdsi:core` §2, `sdsi:standards`, `sdsi:dependencies`, and `ref/cli.md`. They move into one new topic, `sdsi:optimize`, which:
- **runs in `sdsi:all`** as its own step;
- **holds through the whole coding lifecycle** — its `## Upkeep` lines (installed by `sdsi:upkeep`) fire before writing code, when a feature is finished, when a shortcut is taken, when code is changed for speed, and before deleting anything;
- **is re-run on its own for maintenance** — `/sdsi:optimize --review` over the whole project is the cleanup sweep (lists dead code, duplicates, and waste with proof); `--apply` removes what the human approves.

### What moves (one topic, one file)

| Rule | From | To | What stays behind |
|---|---|---|---|
| The ladder, read before cutting, lazy-not-negligent, the post-write size check | `sdsi:core` §2 "No over-engineering" | `sdsi:optimize` | Core §2 keeps the principle in two sentences: solve the problem in front of you, a pattern earns its place with a second real caller today; climb the ladder before writing and check the size after (`sdsi:optimize`), never cutting validation, data-loss handling, security, or accessibility |
| Reuse over reimplementation (DRY on the second occurrence; coincidental duplication stays) | `sdsi:standards` | `sdsi:optimize` | Nothing; core §3's "Code conventions" row drops "reuse over reimplementation", and a new "Lean code" row points to `sdsi:optimize` |
| Dead code and cleanup sweeps (checkpoint, proof list, merge duplicates, entry-point inventory, never delete externally called code, cadence) | `sdsi:standards` | `sdsi:optimize` | Nothing |
| The `shortcut:` marker and its `meta/TODO.md` line | `sdsi:standards` (comments) | `sdsi:optimize` | Nothing |
| Load heavy or environment-specific modules lazily, by name from config | `sdsi:dependencies` | `sdsi:optimize` | Nothing; dependencies' description drops it |
| CLI startup time is a budget | `ref/cli.md` `## sdsi:dependencies` | `ref/cli.md` `## sdsi:optimize` | Nothing |
| Standards' three Upkeep lines (simplification pass, shortcut, before deleting) and matching Review-checklist items | `sdsi:standards` | `sdsi:optimize` | Standards loses its `## Upkeep` section |
| Pointers: core §2 "No random changes" → cleanup sweep; security's entry-point inventory → "cleanup sweeps use this list" | `sdsi:standards` | `sdsi:optimize` | Only the pointer name changes |

Stays where it is (pointed to, not restated): honest reporting and "read what depends on it" (`sdsi:workflow`), a test for risky logic (`sdsi:testing`), standard library first and few dependencies (`sdsi:dependencies`, core §2), the exposed-entry-point inventory (`sdsi:security`), performance targets in `SPEC.md` and their check at deploy (`sdsi:workflow`, `sdsi:deploy`), bounded queues (`sdsi:concurrency`), and "UI code reuses the established design" (`ref/web.md` `## sdsi:standards`).

### `sdsi:optimize` — behavior

1. **Before writing: the ladder** (moved, unchanged in substance).
2. **After writing: the size check** (moved) — code far longer than the problem needs is rewritten before it's called done.
3. **The pass — when a feature is finished**, over the code it changed (scope `branch` by default). Four lenses, from `/simplify`:
   - **Reuse** — something the codebase, standard library, or platform already provides; a rule now implemented twice.
   - **Simplification** — needless indirection (a wrapper or interface with one caller), speculative options nobody sets, deep nesting, dead branches, code that restates what a library does.
   - **Efficiency** — obvious waste: the same I/O, query, or computation repeated in a loop, reading everything to use one item, unbounded growth.
   - **Altitude** — logic at the wrong layer: a workaround in a caller that belongs in the shared front door (core §2), a business rule in an entry point or handler.
   The pass removes what the change made unused. Where the host has Claude Code's `/simplify`, it may run the pass with this skill's checklist as the lens; the deletion rules below still apply.
4. **The sweep — maintenance**, over the whole codebase, on a cadence (weekly on an active project, and before a release): unreferenced files, functions, exports, types, constants, config keys, feature flags past their rollout, assets, styles, and dependencies; duplicated rules; `shortcut:` markers whose revisit condition has come; entry points nothing calls (`sdsi:security`'s inventory). Each item is listed with proof; nothing is deleted without a clean checkpoint and the human's approval; externally invoked code is never deleted without asking (all moved).
5. **Every element earns its place** (from Impeccable's `distill`) — a setting, flag, option, variant, or code path with no real user is a sweep item. Removing something a user or caller can see is a behavior change: it goes through `sdsi:workflow` (design documents first) and gets a `Removed` changelog note saying why.
6. **Performance from measurement** (from Impeccable's `optimize`):
   - Obvious waste (lens 3) is fixed in the pass without a benchmark.
   - **Tuning** — caching, precomputation, parallelism, batching, a lower-level rewrite — happens only on a path measured to be slow, against the `SPEC.md` target when one exists, biggest bottleneck first. The before and after numbers are shown; a tuning that adds complexity without a measured gain is reverted. Tuning code carries a comment with the reason and the measurement.
   - Never trades correctness, security, or accessibility for speed.
7. **Lazy loading** of heavy or environment-specific modules (moved from `sdsi:dependencies`).
8. **Marked shortcuts** (moved) — and revisited by the sweep.

### Order — step 9 in core §4
`sdsi:optimize` runs **after `sdsi:testing`** and before `sdsi:dependencies`: tests exist to prove a removal safe; it trims what the earlier steps added; unused dependencies are gone before the dependency audit; and `sdsi:docs` then describes the code that remains. Dependencies, docs, versioning, and deploy become steps 10–13; `sdsi:all` grows from 12 to 13 steps.

### Project-type companions
- `ref/cli.md` gets `## sdsi:optimize` holding the moved startup budget.
- `ref/web.md` gets `## sdsi:optimize` (from Impeccable's `optimize`, framework-neutral): measure against the `SPEC.md` Core Web Vitals budget on a throttled mobile profile; images sized for their display size and lazy-loaded below the fold; space reserved for media and embeds so nothing shifts the layout; a script or third-party tag that loads on every page but runs on one is a sweep item.
- Other companions get no section — the skill says "no considerations" for them (core §1 Step 2). Sections are added only from a real project's lesson.

### Upkeep lines (`sdsi:optimize`)
- Before writing code → read what the change touches and trace its flow, then climb the ladder and stop at the first rung that solves it
- Finishing a feature → run the pass (reuse, simplification, efficiency, altitude) over the code it changed and remove what it made unused; leave pre-existing dead code for a sweep
- Taking a deliberate shortcut → `shortcut:` comment + `meta/TODO.md` line (moved)
- Changing code for speed → measure before and after on the slow path; keep the change only with a measured gain
- Before deleting code that looks unused → checkpoint, proof list, approval; never delete externally called code without asking (moved)
- Starting maintenance work or preparing a release → run `/sdsi:optimize --review` over the whole project

### Interfaces touched
New `skills/optimize/SKILL.md` (`argument-hint: "[--review|--apply] [path|branch]"`, Upkeep, Review checklist, description ≤ 1024 chars). Edited: `skills/core` (§2, §3, §4), `skills/standards`, `skills/dependencies`, `skills/security` (pointer), `skills/upkeep` (one sentence), `skills/all` (description, step count), `ref/findings.md` (step count example), `ref/cli.md`, `ref/web.md`, `README.md` (skills table), `.claude-plugin/plugin.json` description (topic list only — never the version), `meta/CHANGELOG.md`.

**Projects with standards' upkeep installed:** their `.claude/rules/sdsi.md` goes stale on upgrade; `sdsi:upkeep`'s review already flags a stale section; `sdsi:upkeep` gains one sentence: a refresh drops, and reports, an installed topic whose `## Upkeep` section no longer exists. The changelog note tells them to run `/sdsi:upkeep` and pick `optimize`.

### Explicitly not adopted
Impeccable's visual-design commands (bolder, colorize, typeset, …), its detector, `PRODUCT.md`/`DESIGN.md`, and framework-specific tips (React memoization, specific image formats); Ponytail's intensity levels, band, and scoreboard; a separate `/sdsi:sweep` command (the sweep is `/sdsi:optimize --review` on the whole project).

### Constraints
One topic, one file (each moved rule exists only in `sdsi:optimize` afterwards); language-neutral; descriptions ≤ 1024 chars; changelog notes cite `TODO #22`; `plugin.json`'s version untouched.

## TTD016 — Companion review and companion declaration (TODO #16)

Sources reviewed (Nov 2026), one research pass per companion: clig.dev, POSIX and GNU conventions, Microsoft System.CommandLine guidance, and the documented behavior of gh, kubectl, aws, terraform, npm, cargo, go, and docker (cli). OWASP Top 10:2025, ASVS 5.0, and the cheat sheets, RFC 9457, 9745, and 8594, Zalando, and WCAG 2.2 (web). EIP, the Azure, AWS, and Google SRE pipeline guidance, the Airbyte protocol, dbt model versions, Confluent schema evolution, and ODCS (mw). SemVer, the Rust API Guidelines, PyPA, Python logging, .NET library guidance, Go modules, AIP-180, Scientific Python SPEC 0, OpenSSF Scorecard, and SLSA, plus how httpx, requests, and Guava behave (lib). Microsoft signing and MSIX, Apple notarization, XDG and Flatpak, the Electron and Tauri security and updater docs, TUF, and RFC 8252 (desktop). OWASP MASVS 2.1, MASTG, and MASWE, Apple's review guidelines and privacy manifests, Android network-security config and target-SDK pages, and Google Play policy (mobile). No text is copied.

### Goal
1. **Confirm or correct every companion rule** against that guidance and against how mature real projects behave. About 300 rules were checked: roughly 85% are confirmed, and the rest are corrected, merged, moved, or dropped below.
2. **Trim every section to about 7 top-level bullets.** Merge first, move second, and drop only what a base skill already states.
3. **Settle the four open points** the research flagged.
4. **Close a few broadly accepted gaps**, at most five per companion and fewer where possible.
5. **Make SDSI declare which companions apply to a project**, why, and to which part of the code.

### Behavior change 1 — the companion declaration (core §1 Step 2)

**Where the declaration lives: the project's `.claude/CLAUDE.md` `## SDSI profile`.** That file is already the profile's only home. Claude Code loads it every session, and every skill reads it first.
- The project README is for people (`sdsi:docs`), so a declaration there would be a second copy that drifts.
- `.claude/rules/sdsi.md` is regenerated whole from the topics' `## Upkeep` lines (`sdsi:upkeep`), so a declaration there would be overwritten or duplicated.

The profile gains a `Companions` field. `Project type` stays as the main type:

```markdown
- Project type: web
- Companions: web — route handlers and templates in `src/app/`; cli (`src/app/cli/` only) — an argument parser for the admin commands
```

- **Every companion that applies is listed**, main type first. Each one carries its evidence in one clause and, for a secondary companion, the part of the code it covers. A secondary companion's rules apply only inside that scope. For example, the CLI's exit codes and global handler never reach a library's importable modules.
- **When `Companions` is missing**, it is derived from `Project type` (one companion, the whole project), recorded, and reported. Profiles written before this change keep working.
- **`other` records `Companions: none`.**
- **Core's type table gains sharper evidence** in its "Evidence in the code" column. Under it goes a short **mixed-project list**, each entry giving the main type plus the scoped extra:

  | Project | Main type | Extra companion |
  |---|---|---|
  | Library with a thin CLI wrapper | lib | cli, on the wrapper only |
  | Web app with a management CLI | web | cli, on the command surface |
  | Integration service with a webhook receiver | mw | web, on the receiver |
  | Electron or Tauri app | desktop | — (not web) |
  | Terminal UI (TUI) | cli | — |
  | API-only service, static site, or PWA | web | — |
  | Backend for a mobile app | web or mw | — (mobile only where an app project exists) |
  | Cross-platform toolkit with `ios/`/`android/` targets | mobile | desktop, when desktop targets also ship |
  | SDK for the company's own API | lib | — |

- **The tie-breaker question:** what ships, and who consumes it? A person typing a command means cli. Code importing it means lib. An HTTP client or browser means web. A schedule or another system means mw. An installer means desktop. A store means mobile. When the answer is still tied, ask with `AskUserQuestion`. Never pick silently, which core already requires.
- **A rule for a surface the project doesn't have is skipped and said in one line.** A static site has no sessions, so the session rules don't apply to it. This joins the companion paragraph.
- **The declaration is kept current.** `sdsi:workflow` gets one Upkeep line: *when a change adds a new kind of surface (a CLI, an HTTP API, an app project, a scheduled sync) → update the profile's `Companions` (`sdsi:core`)*. Workflow owns scope changes. The line only points to core.
- **The plugin `README.md`** gets a "Which companion applies" paragraph that points to core §1 Step 2. It doesn't restate the table.

### Behavior change 2 — the four open points, settled

1. **CLI secrets through environment variables (`ref/cli.md` `## sdsi:security`).** Real CLIs (gh, aws, terraform, cargo, npm) and CI runners pass secrets through the environment, because a runner has no store. A CLI's caller sits on a different trust boundary from a service the project deploys. This is a **sanctioned deviation** from `sdsi:security`'s "environment variable is a last-resort developer fallback", and the companion says so.
   - A secret is never accepted as a flag.
   - Accept secrets in this order:
     1. The platform credential store or a credential helper.
     2. A file or stdin (`--token-file <path>`, `-`), including a `<TOOL>_<NAME>_FILE` variable that holds a path.
     3. An environment variable, documented as the headless and CI input. It is never the first thing the docs show an interactive user.
   - An environment-variable secret is read once. It is never echoed, logged, shown by `--show-config`, written to a config file, or passed to a child process that doesn't need it.
   - A plaintext credential-cache fallback (no store available) is disclosed to the user when it happens.
2. **Where `--json` errors go (`ref/cli.md` `## sdsi:errors`).** gh, kubectl, and go send errors to stderr. npm's errors on stdout were reported as a breaking bug.
   - stdout carries only success data, and it is empty on failure.
   - The error goes to stderr. With `--json` it is one JSON object of a documented shape, which is part of the versioned machine-readable contract.
   - The exit code is the authority.
   - **One exception: a command that is itself an event stream** (a build, a plan) reports diagnostics as in-band records and still exits nonzero.
   - `tool --json | jq` therefore never receives an error as data.
3. **mw's schema-change-is-MAJOR (`ref/mw.md` `## sdsi:versioning`).** This is right in intent but was one rule doing two jobs. The new rule follows dbt model versions, Confluent compatibility, and ODCS.
   - **The destination's shape is a contract with its own version**: field names, types, nullability, and meaning.
   - Adding an optional field is MINOR.
   - These are breaking: removing, renaming, or retyping a field, making a field required, or changing what a field means to existing readers. A breaking change bumps the contract MAJOR, and the service ships as MAJOR. That matches `sdsi:versioning`'s MAJOR, because a deployed consumer breaks until someone acts.
   - Evolve by expand-then-contract: add the new field beside the old one, deprecate the old one with a date for at least one release, then remove it in a later MAJOR.
   - The contract is published per destination, extending the existing integration sheet in `## sdsi:docs`.
4. **Mobile certificate pinning (`ref/mobile.md` `## sdsi:security`).** Pinning stays **off by default and is turned on by a decision recorded in `CLAUDE.md`**.
   - **What triggers the decision:** high-risk data (financial, health, credentials, private messages), a MASVS L2 target, or a regulatory or contract requirement.
   - **Scope:** only endpoints the team controls. Never third-party, CDN, or user-configured hosts.
   - **When pinning is used:**
     - Pin the SPKI hash of a key the team controls (its own CA or the issuing intermediate), never a public-CA leaf, which rotates within 90 days.
     - Ship at least one offline backup pin.
     - Set a recorded pin expiry where the platform supports one, and state its fail-open trade-off.
     - Ship a new pin several supported releases before the server changes.
     - Run a rotation drill in staging.
     - Code-level pinning gets a validated remote-config off switch.

### Behavior change 3 — per-companion corrections, trims, and additions

Counts are top-level bullets per section, before → after. A section not named here keeps its rules, with wording fixes only.

**`ref/web.md`**
- **standards (8 → 6).**
  - Merge the thin request layer with "services never see request objects".
  - Move "served asset never edited in place" to versioning, beside the content-hash bullet.
  - "One UI framework" stays. It is an owner rule (TTD019).
- **security (18 → 12, in three `###` groups of at most 5):**
  - *Access and data* (5): deny-by-default per route, pointing to base isolation for per-object checks; the guest redacted type; encoding and parameterized queries; **new**: server-side fetches of a user-supplied URL and post-sign-in redirects go through an allowlist (SSRF and open-redirect rules); **new**: uploads have an allowlisted type and a capped size, are stored outside the served root, and are never executed.
  - *Transport and headers* (4):
    - HTTPS forcing, HSTS, secure cookies, and the redirect are each stated per environment. The LAN-only bullet merges in here, and a TLS 1.2+ floor is added.
    - Trusted origins and trusted proxies merge into one bullet.
    - CORS.
    - Security headers: CSP `frame-ancestors` first and `X-Frame-Options` only as a fallback; don't send `X-XSS-Protection` or `Expect-CT`.
  - *Sessions and credentials* (3):
    - A credential never travels in a URL. This absorbs "nothing secret reaches the browser".
    - Session cookies, with `SameSite=Strict` preferred and `__Host-` winning over path scoping. **New**: a cookie-authenticated state-changing request also needs a CSRF token or an `Origin` check, because SameSite is defense in depth, not the defense.
    - Password hashing per the OWASP cheat sheet, without restating its costs.
  - Dropped: "session, signing, and CSRF keys are secrets". `sdsi:security` already states it.
  - The three test bullets (access denial, guest bodies, headers and cookies) move to testing, replacing its circular pointer. Base security's regression test covers only a fixed finding, so the per-route denial test stays (testing 5 → 7).
- **concurrency.** The idempotency key is described as an IETF draft, not a standard. Try a natural conditional or unique key first. A reused key with a different payload returns `422`, and a retry while the original is still running returns `409`.
- **versioning.** The `Deprecation` value is a structured-field date (RFC 9745). `Sunset` is an HTTP-date (RFC 8594, added to Sources).
- **deploy.** Keep the two health endpoints (basic and gated full). Add readiness where an orchestrator routes traffic by it. A static site needs none.
- **config.** The allowed-hosts bullet is reworded to be framework-neutral: the host allowlist covers every hostname the app is reached by, including the bare and `www.` forms.
- **workflow.** The launch checklist stays as the owner wrote it (TTD019). Only the cookie banner is qualified: "where privacy law requires consent".
- **Sources.** Add OWASP SSRF, File Upload, Unvalidated Redirects, and TLS cheat sheets, RFC 8594, and Google Search Central.

**`ref/cli.md`**
- **standards (9 → 4):**
  - *Command grammar*: noun groups plus no catch-all and no prefix abbreviation.
  - *Parser and names*: the real parser plus kebab-case names.
  - *Flags*:
    - Conventional names plus flags over positionals.
    - Corrected: reserve only the long names (`--help`, `--version`, `--quiet`, `--verbose`, `--dry-run`, `--force`, `--json`, `--no-input`, `--no-color`) plus `-h` and `-q`. Any short alias a tool does use keeps its conventional meaning, because `-v`, `-f`, `-n`, and `-o` collide across real tools.
  - *Safe changes*: confirmation, `--no-input`, `--dry-run`, and **new**: `--confirm=<name>` for severe actions.
  - The registry-completeness rule moves into testing's wiring-test bullet.
- **config.** Corrected: an environment variable is for what varies by context (a CI job, a shell session), a config file for what persists, and a flag for this run.
- **security.** Open point 1 replaces the two environment-variable bullets. The credential-cache bullet gains the plaintext-fallback disclosure.
- **logging.** **New**: page output only when stdout is a terminal. Honor `PAGER`, and offer `--no-pager`. This merges into the terminal-detection bullet.
- **errors (7 → 7):**
  - Merge the two exit-code bullets.
  - `2` stays the default usage error, and a tool that diverges documents its table.
  - **New**: a documented code for non-error outcomes ("no match", "differences found" → `1`, as grep and diff do).
  - Open point 2 replaces the `--json` bullet.
- **Header.** "Seed, not distilled from a real CLI project" becomes "checked against the documented behavior of gh, kubectl, aws, terraform, npm, cargo, and go". It still invites correction from the first real project.

**`ref/mw.md`**
- **standards (14 → 7):**
  1. *Stages*: separation plus the three-stage block plus the cache plus the registry clause. The cache is corrected: it is purged at the start of a fresh run, and a resumed run keeps it.
  2. *Idempotent writes*: idempotent writes plus the stable dedup key, plus the idempotency-key rule moved from errors.
  3. *Incremental extraction*: the watermark, the flattened-field filter, and "changed since X".
  4. *Paging.*
  5. *Read tolerantly*, plus **new**: drift in a used field is detected and logged as a warning before it rejects records.
  6. *Lineage.*
  7. *Outbox*, plus the relay being at-least-once, so the receiver is idempotent.
  - Reconciliation moves to logging, merged with the summary-line bullet that already points to it.
- **errors (9 → 4):**
  - Retry policy merges backoff and `Retry-After`, and is corrected: retry `408`, `429`, `502`, `503`, `504`, and timeouts. Don't retry other 5xx or 4xx unless the system documents them as transient. Total retry time is capped by a new `retry_budget` key in the per-system config shape, even when `Retry-After` is longer.
  - Retry at one layer.
  - Quarantine.
  - Reporting merges the reporting mode, the callback, and the disabled-system bullet, which is folded in as its example.
  - Per-step progress moves to concurrency, merged with "batch runs are resumable".
- **logging.** **New**: a freshness target per flow (data within N minutes), with an alert when it's missed.
- **security.** **New**: move only the fields the flow needs, and give the cache and the rejects store a stated retention.
- **versioning.** Open point 3.
- **docs.** The integration sheet gains the destination contract and its status (active, deprecated, retired).
- **Sources.** Drop the third-party DAMA PDF, which no rule relied on. Label the Idempotency-Key reference as a draft. Add the Airbyte protocol, dbt model versions, and ODCS.

**`ref/lib.md`**
- **standards (7 → 5):**
  - Merge "add, don't change" with "design for growth", plus **new**: interfaces consumers mustn't implement are sealed.
  - Merge "no side effects on import" with "no process-global state".
  - Move "never expose a dependency's types" to dependencies.
  - "Standard protocols" stays.
  - **New**: a typed library ships its type information (stub or declaration files, a typed marker).
- **config.** Corrected, after httpx and requests: implicit reads are limited to ecosystem-standard variables (proxy, CA bundle), documented, and switchable off with one option. Never read library-specific variables or files unprompted.
- **logging.** Corrected: silent by default, which means attaching the facade's no-op handler where the facade's default isn't silent.
- **concurrency.** Corrected: every wait accepts a timeout or cancellation, and its default is documented.
- **dependencies.** Corrected range rule: a tested floor is required. No exact pin, and no cap beyond the ecosystem's default compatible-range operator unless an incompatibility is known. Never cap the language version. Plus the moved dependency-types bullet, and **new**: a plugin or adapter library declares its host as a peer or optional dependency with a broad range.
- **versioning.**
  - Corrected: dropping a language version or platform is MAJOR, unless the `SPEC.md` support policy declares a drop schedule that the release notes cite. Then it's MINOR.
  - Corrected: a MAJOR may remove deprecated items but isn't required to.
  - **New**: unstable public items are marked experimental and exempted from the SemVer promise in writing.
- **workflow.** The support matrix gains its drop schedule. The minimum language version goes in the manifest's own field where one exists.
- **docs.** **New**: a license file, with its SPDX identifier in the manifest.

**`ref/desktop.md`**
- **New `## sdsi:workflow` (2):**
  - `SPEC.md` states the supported OS versions and architectures, the distribution shape and update channels per OS, offline behavior, the single-instance decision, the downgrade policy for user data, and the telemetry and crash-report consent stance.
  - A change touching stored user data plans an upgrade-from-N-1 check.
- **security (8 → 5):**
  - Merge the open-externally allowlist into the embedded-web-content bullet, as navigation and links.
  - Merge "everything shipped is public" with the OS-credential-store bullet.
  - Move the signing-key bullet to deploy.
  - Merge "runs as a standard user" with **new** least-privilege packaging: entitlements, sandbox permissions, and capabilities, each justified, with user files reached through portals or user-granted scoped access when sandboxed.
- **deploy (8 → 6):**
  - Merge the target with the config deviation.
  - Merge uninstall with declarative integration.
  - Code signing absorbs the signing-key bullet and is corrected per OS. Windows: Authenticode with a timestamp. macOS: Developer ID, hardened runtime, and notarization. Linux: repository or package signing. OS code-signing keys sit in an HSM or a cloud signing service, as the CA/B Forum has required since June 2023. The update-signing key sits in the CI secret store and is backed up, because a lost key strands every install.
  - Updates corrected: authentic payloads and no rollback are required, and freeze protection is required only where the updater supports signed, expiring metadata.
  - Uninstall corrected: remove everything the format allows, document what remains and how to remove it, and register no login items or launch agents at runtime.
- **logging.** Default-off telemetry stays, recorded as the `SPEC.md` decision above.
- **dependencies.** The bundled-runtime bullet gains "move up one major line at a time".
- **Sources.** Drop the 2012 Authenticode blog. Add Flatpak sandbox permissions, the Tauri updater, and the CA/B code-signing key requirement.

**`ref/mobile.md`**
- **security (9 → 6):**
  1. Entry points.
  2. *Transport*: never opt in to cleartext in a release variant (Android has disabled it by default since API 28; iOS uses ATS), plus debug-only anchors.
  3. *Pinning*: open point 4, a bullet of its own.
  4. *The shipped app is public*: no server credential, and a key that must ship is restricted and labelled public.
  5. *Credentials at rest*: the secure store, non-exportable keys, and exclusion from backups, plus **new**: sensitive operations are gated by biometrics or re-authentication bound to the secure store.
  6. OS leaks.
  - Signing keys move to deploy (6 → 7).
- **workflow.** Corrected: account deletion also has a web link for requests without the app (Play). On iOS it starts in the app.
- **logging.** Telemetry batching moves to concurrency's no-polling bullet. **New**, merged into "what's collected is what's declared": personal data shared with a third-party AI service needs disclosure and consent first (Apple 5.1.2(i)).
- **dependencies.**
  - Corrected: a privacy manifest is required of SDKs on Apple's listed set, and the app declares its own required-reason APIs.
  - The store-schedule rule keeps no dates and links to the Play target-SDK page and Apple's upcoming-requirements page.
  - "Size is a cost" is dropped, because `sdsi:dependencies` and `sdsi:optimize` own it.

**Every companion's header paragraph** is updated to say what it was checked against and when (2026-11), and still says it's corrected from the first real project that disagrees.

### Guardrail test
`tests/test_skills.py` gains `test_companions`. It checks four things:
- Every `## sdsi:<topic>` heading in `ref/<type>.md` names an existing skill folder.
- Every type in core §1 Step 2's table has its companion file.
- Every companion has a `## Sources` section.
- No `##` or `###` block of a companion holds more than 7 top-level bullets.

### Interfaces touched
- `ref/web.md`, `ref/cli.md`, `ref/mw.md`, `ref/lib.md`, `ref/desktop.md`, `ref/mobile.md`.
- `skills/core/SKILL.md`: §1 Step 2's profile block, type table, mixed-project list, and companion paragraph.
- `skills/workflow/SKILL.md`: one Upkeep line and its Review-checklist item, *a new surface not reflected in `Companions`*.
- `skills/all/SKILL.md`: steps 1–2 read every listed companion, each within its scope.
- `README.md`: "Which companion applies".
- `tests/test_skills.py`.
- `meta/CHANGELOG.md`.
- Projects with workflow upkeep installed get the new line on their next `/sdsi:upkeep` refresh, and the changelog note says so.

### Explicitly not adopted
- Upkeep lines inside companions. Companions stay lookup sections, and only topics own Upkeep.
- Dated store deadlines in mobile.md: Play's 16 KB page size, the age-rating questionnaire, and specific API-level dates.
- Device and app attestation, until a real project needs it.
- web's "liveness + readiness" replacing the two health endpoints.
- Dropping the owner's launch-checklist items or the one-UI-framework rule.
- CLI `--plain` output.
- Configurable CLI network timeouts, which base `sdsi:concurrency` already covers.
- Reproducible builds for libraries, which neither Scorecard nor SLSA L2 requires.

### Constraints
- One topic, one file.
- Companions stay language-neutral. Framework names appear only as examples.
- A companion that deviates from a base skill says so.
- Skill descriptions stay ≤ 1024 characters.
- Changelog notes cite `TODO #16`.
- `plugin.json`'s version is never edited.
