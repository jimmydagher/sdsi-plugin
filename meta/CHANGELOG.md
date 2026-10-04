# Changelog

All notable changes to the `sdsi` plugin, newest first. See `VERSION` for the current release and `sdsi:versioning` for what a version bump means.

## 🚧 Unreleased

### Added or New Features
(none)

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
(none)

## 🆕VERSION 1.3.10 📅 2026-10-04

### Added or New Features
(none)

### Removed
(none)

### Changed
- **The README's version line is now required** (`sdsi:versioning`): every project's root `README.md` carries `## 🆕VERSION x.y.z 📅 YYYY-MM-DD` under its title, followed by a pointer to `meta/CHANGELOG.md`, and the release script keeps it in sync. A README without it is a review finding; the script still doesn't refuse the commit. `sdsi:docs` lists it among what the README holds. Operator: add the line to any project whose README lacks it.

### Bug/Issues/Fixes
(none)

## 🟥VERSION 1.3.9 📅 2026-10-04

### Added or New Features
- **`sdsi:security` — one home for every security rule**, at step 4 of the order, where `sdsi:secrets` was. It holds the secrets rules (unchanged), untrusted-input validation (moved from `sdsi:standards`), per-trust-boundary security settings (moved from `sdsi:deploy`), and a new rule: protected data reaches only its owner. Personal, key, or restricted data is never returned to anyone not signed in with their own account, whether through a page, an API response, an error, a message, or a file. A guest flow that must confirm identity, like paying a cable or electric bill with an account number and a card, gets only server-side redacted fragments ("Jane D.", the last four digits). `SPEC.md` names every guest flow and the fields it returns, guest sessions are limited to their one transaction, and guest lookups are rate-limited. Core §2 adds the matching principle, and an Upkeep line keeps it on between runs. The other skills now point to `sdsi:security` instead of restating its rules. The audit trail stays in `sdsi:logging`.

### Removed
- **`sdsi:secrets`** — replaced by `sdsi:security`, which keeps all its rules. Run `/sdsi:security` instead, and refresh any project's `.claude/rules/sdsi.md` with `/sdsi:upkeep`.

### Changed
- **`sdsi:logging` — logging is a message queue.** Whatever the language or system, and whether the program is single- or multi-threaded, a log call only builds a record, stamped at call time, and enqueues it. One log writer per process pulls the records in order of arrival and writes each one to every destination in turn, so lines never interleave. With threads, the writer is a background worker; on an event loop, it's a task; with neither, the queue is drained right after each enqueue. The queue is bounded, and the `when_full` setting decides what a full queue does: `wait` makes the log call wait for room, and `drop` discards `DEBUG`–`WARNING` records (`ERROR` and `CRITICAL` still wait) and then logs a warning with the drop count. A failing destination never breaks the program, and shutdown drains the queue within a bounded time. Log files roll over at a configured time of day (`rotate_at`, e.g. midnight, in a configured time zone) into date-named files, and `keep` sets how many rotated files stay before the oldest is deleted (7, 15, 30…). A restart catches up a missed rotation. The desktop companion's size-based rotation now defers to these settings.
- **The companions' `## sdsi:secrets` sections are now `## sdsi:security`**, and they pick up the security rules that sat in other sections. Web: access control, guest response types, output encoding, HTTPS/HSTS, trusted origins and proxies, CORS, security headers, the LAN-only settings, and the security tests. Mobile: untrusted entry points, transport security, and pinning. Desktop: untrusted entry points, the external-open allowlist, embedded web content, and running as a standard user. Each old section keeps a pointer.

### Bug/Issues/Fixes
(none)

## 🟫VERSION 1.3.8 📅 2026-10-04

### Added or New Features
- **The README's version line** (`sdsi:versioning`): a root `README.md` holding a line in the changelog's heading format (`## 🆕VERSION x.y.z 📅 YYYY-MM-DD`) has it kept equal to the changelog's current heading by the release script, on release and docs-only commits alike. Opt-in — a README without the line is untouched. This plugin's README now carries one, with a pointer to the changelog.

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
(none)

## 🟪VERSION 1.3.7 📅 2026-10-04

### Added or New Features
- **`sdsi:logging` — the audit trail** (TODO #11): wherever a program makes security decisions, every one of them — sign-ins, authorization grants and denials, permission and role changes, admin actions, security-setting changes, access to sensitive data — is recorded through one audit recorder as its own stream, separate from the application logs and never filtered by the log level. Events have a fixed, versioned shape (when, who, from, action, target, outcome, change, context), are written at the decision, append-only and tamper-evident, never silently lost — permission and admin changes fail closed when their record can't be written — and tested like a contract. `SPEC.md` states whether a project has one. An Upkeep line keeps it on between runs.

### Removed
(none)

### Changed
- **Core §3:** the logging invariant includes the audit trail wherever the program makes security decisions.
- **`ref/web.md`:** security decisions go to the audit trail; security anomalies that aren't decisions (rejected input, CSRF or session anomalies, rate-limit trips) stay in the application log.

### Bug/Issues/Fixes
(none)

## 🟦VERSION 1.3.6 📅 2026-10-04

### Added or New Features
- **`sdsi:concurrency` grows from a seed into a full standard** (TODO #5):
  - **Choosing the model:** an async event loop for many I/O waits, process or thread pools for CPU work, a thread-pool offload for blocking calls in async code, a dedicated worker with its own queue for long-lived duties, a durable job for work that outlasts a request — with one explicit boundary between models.
  - **Parallelism:** bounded pools sized from config, separate pools per kind of work, bounded fan-out with a complete fan-in, structured cancellation, partitioned data, deliberate result order.
  - **Synchronization:** which primitive for which need — mutex, semaphore, future, event, latch, barrier, condition variable, read-write lock; locks never held across I/O or an `await`; async primitives in async code; key steps wait on what they depend on, with a timeout, never on a `sleep`.
  - **Deadlocks:** one global lock order, one lock at a time, no unknown code under a lock, timed acquisition, no task waiting on work queued behind it in the same pool, no circular waits through bounded queues.
  - **Starvation and livelock:** short critical sections, FIFO with aging priorities, fair shares of shared resources, jittered retries, queue wait time made visible.
  - **The Asynchronous Request-Reply pattern** for long-running work — persist, return a handle at once, run under a leased worker, report status, retain and expire results, cancel, reclaim stuck jobs — built **once** as a job harness that each long operation registers a handler with.
  - **Testing:** timeouts on every concurrent test, race detectors in CI, stress tests, and the harness tested once with a fake clock.
  - **An Upkeep line**, so the rules can stay on in a project between runs (`sdsi:upkeep`).

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
(none)

## 🟩VERSION 1.3.5 📅 2026-10-04

### Added or New Features
- **Three new project-type companions:** `ref/lib.md` (libraries and packages — the public API is the contract; the library configures no logging, error handler, or threads of its own; dependency ranges instead of pins), `ref/desktop.md` (installed GUI apps — per-user file locations, OS credential store, signed and authenticated updates, never losing the user's work), and `ref/mobile.md` (app stores — build-time config, secure on-device storage, offline-first sync, staged rollouts, a minimum supported version). Each is a researched base with its sources listed, not yet grown from a real project. Core §1 Step 2's type table detects `lib`, `desktop`, and `mobile`, and a project can record a second type whose companion also applies. (TODO #9)
- **`ref/web.md` — two health endpoints, always:** a basic one (no auth, no dependencies) for the platform's probe, and a full one that checks every service the app depends on, gated by an admin key from the secrets store, sent in a header and compared in constant time. (TODO #15)

### Removed
(none)

### Changed
- **`ref/web.md`, `ref/cli.md`, and `ref/mw.md` expanded from published guidelines**, keeping every rule learned from real projects. Web: access control, output encoding, security headers, CORS, session cookies, RFC 9457 errors, security-event logging, conditional updates and idempotency keys, WCAG 2.2 AA, Core Web Vitals targets, API deprecation headers. CLI: argument syntax, conventional flag names, exit-code ranges, `NO_COLOR`, XDG locations, Ctrl-C and broken-pipe handling, generated help and completion. Middleware: idempotent writes, watermarks, paging, reconciliation, quarantine, the outbox, jittered backoff, shared rate limits, lineage. Each companion lists its sources. (TODO #4, TODO #7, TODO #8)
- Core, the README, the plugin description, and `.claude/CLAUDE.md` list the six project types.

### Bug/Issues/Fixes
(none)

## 🟨VERSION 1.3.4 📅 2026-10-03

### Added or New Features
- **`sdsi:upkeep`** (new): leaves a project's standing instructions — the rules that must hold every session, not only while a skill runs — in `.claude/rules/sdsi.md`, which Claude Code loads at every session start. It assembles them from each topic's new `## Upkeep` section; installs, refreshes after a plugin upgrade, removes, or reviews them. The project's own `CLAUDE.md` is untouched apart from a new profile field, `Upkeep`.
- **Upkeep sections** in `sdsi:workflow` (design documents first; verify before calling it done; merge ⛏️ In progress when done), `sdsi:docs` (rewrite in place with a changelog sentence; clean up and document after a TODO item; leftover work becomes a TODO item), `sdsi:versioning` (a changelog bullet for every change; never commit), and `sdsi:testing` (a failing test before a bug fix).

### Removed
(none)

### Changed
- **Core §1 Step 5:** a skill with an Upkeep section ends by asking whether to leave its upkeep instructions in the project — optional, asked once, and remembered in the profile when declined. `sdsi:all` asks once at the end of the run, for every topic it ran.
- README and the plugin description list `sdsi:upkeep`.
- `.claude/CLAUDE.md`: a rule that must hold every session goes in its topic's `## Upkeep` section.

### Bug/Issues/Fixes
(none)

## 🟧VERSION 1.3.3 📅 2026-10-03

### Added or New Features
- `sdsi:deploy`: a deploy is verified against `SPEC.md`'s non-functional requirements before it counts as done; `SPEC.md` states performance, availability, and security targets so they can be checked, plus the testing and monitoring strategy. (TODO #10)

### Removed
(none)

### Changed
- `sdsi:workflow`: every project has three living design documents in `docs/design/` — `INTENT.md` (why), `SPEC.md` (what), `PLAN.md` (how) — describing the whole project, not one change. Every new feature updates them before code; the change's steps go in `PLAN.md`'s ⛏️ In progress section, merged into the plan once done. A project without them gets them reverse-engineered, with every inference marked for the human to confirm. Brainstorming stays above SDSI and its result is merged in. `sdsi:docs`, core §3, and `sdsi:all` follow; planning documents are no longer write-once records.
- README: the skills table describes `sdsi:workflow`'s design documents.

### Bug/Issues/Fixes
(none)

## 🟥VERSION 1.3.2 📅 2026-10-03

### Added or New Features
- `sdsi:docs`: a document is rewritten in place as the single source of truth — never a correction appended under stale text — and each document change gets one short sentence under Changed in the changelog. (TODO #13)
- A docs-only commit files its notes under the current 🆕 version and moves that version's 📅 to the day of the commit (`release.py`, `sdsi:versioning`); a commit with no notes, such as a `TODO.md` edit, leaves the changelog alone.
- `ref/web.md` gains a `sdsi:versioning` section: the running version shows in the UI — every page's footer, the about or help screen, every error page — and showing it on pages reachable without signing in is a stated decision. Its `sdsi:deploy` section checks a deploy by reading the version off the deployed page. (TODO #14)

### Removed
(none)

### Changed
- `.claude/CLAUDE.md`: docs-only commits cover every Markdown file in `meta/`.

### Bug/Issues/Fixes
(none)

## 🟫VERSION 1.3.1 📅 2026-10-03

### Added or New Features
- `scripts/git/commit-template`: with `git config commit.template scripts/git/commit-template`, the editor's commit box is pre-filled (VS Code reads it), so committing no longer stops at a `COMMIT_EDITMSG` tab asking for a message. On `main` the hook still replaces it with the version line. A project copies the file and runs the command (`sdsi:versioning`, "Installing the release chain").

### Removed
(none)

### Changed
- Docs-only commits are labelled `VERSION x.y.z+k` — the k-th since x.y.z, as SemVer build metadata — instead of `VERSION x.y.z-updated`, which SemVer reads as a pre-release *before* x.y.z. `VERSION` and the changelog are untouched and no Unreleased notes are needed. A project re-copies `scripts/git/commit-msg`.
- `sdsi:versioning`: don't amend on `main` — the hook labels an amend as a new docs-only commit. The `commit-msg` header no longer claims amending is safe (it already relabelled a release commit `-updated`).

### Bug/Issues/Fixes
(none)

## 🟪VERSION 1.3.0 📅 2026-10-03

### Added or New Features
- `release.py` gives a moved `meta/VERSION` — staged, but still holding the current release — the usual PATCH bump, instead of taking it as a hand-set bump and writing a second changelog entry for a version that already shipped. A missing `meta/VERSION` or `meta/CHANGELOG.md` is refused with a message pointing to the move steps, instead of a traceback.

### Removed
- `docs/specs/2026-09-23-review-apply-modes-design.md`, the design spec for the review/apply modes shipped in 1.1.0.

### Changed
- **The project root holds only `README.md` and folders** (`sdsi:core` §3), plus files a tool reads nowhere else (`.gitignore`, `.gitattributes`, a manifest and lockfile where the language's tooling requires the root). `CLAUDE.md` moves to `.claude/CLAUDE.md`; `VERSION`, `CHANGELOG.md`, and `TODO.md` move to a new `meta/` folder, the project's record; `docs/` is for what people read to understand or operate the project (processes, how-tos, setup, deployment, transitions), including `sdsi:workflow`'s planning artifacts in a per-change folder. `sdsi:docs`, `sdsi:versioning`, `sdsi:workflow`, and `sdsi:standards` follow, and their review checklists flag a stray root file. (TODO #12)
- **The release scripts read `meta/VERSION`, `meta/CHANGELOG.md`, and `meta/TODO.md`.** A project that re-copies `pre-commit`, `commit-msg`, and `release.py` must move those files in the same commit and point any `docs_patterns` entry for them at the new path — the commit gets a PATCH bump on its own; a MINOR or MAJOR is written into `meta/VERSION` by hand as before — see `sdsi:versioning`, "Moving the release files out of the root". A project keeping its current copies is unaffected. A staged `meta/VERSION` always counts as a release, even if a `docs_patterns` entry matches it.
- This repo follows the new layout: `.claude/CLAUDE.md`, `meta/VERSION`, `meta/CHANGELOG.md`, `meta/TODO.md`, with `scripts/git/release.json`'s `docs_patterns` to match.

### Bug/Issues/Fixes
- `tests/test_release.py`: the end-to-end tests of a refused commit failed on Windows with Python 3.14 — the hook's message reached the test as cp1252 and couldn't be decoded. The harness now runs the hooks with UTF-8 output.

## 🟦VERSION 1.2.2 📅 2026-09-26

### Added or New Features
(none)

### Removed
(none)

### Changed
- Markdown formatting standards applied to the READMEs, docs, refs and skills (blank-line spacing only; no content changes).

### Bug/Issues/Fixes
(none)

## 🟩VERSION 1.2.1 📅 2026-09-26

### Added or New Features
- `ref/web.md` › `sdsi:config`: review the files and assets each environment needs when it's created, and create any that are missing (e.g. `favicon.ico`).

### Removed
(none)

### Changed
- Markdown across the plugin puts each paragraph and list item on one line (no hard wraps), and every code block names its language (`text`, `markdown`, `bash`).
- `sdsi:workflow`: "Verification has two levels" is a plain sentence instead of a bold line standing in for a heading.

### Bug/Issues/Fixes
- `ref/findings.md` and `sdsi:all`: a wrapped `+ cli` / `+ web` line rendered as a stray nested bullet; it's back in its sentence.

## 🟨VERSION 1.2.0 📅 2026-09-25

### Added or New Features
- `sdsi:core` non-negotiable: **confirm before anything destructive or bulk** — explicit approval with the scope stated (what, and how many), not carried over from one action to the next.
- `sdsi:workflow` gains **Size the steps** (a plan step should be finishable and verifiable in one session; split past ~30 minutes / ~5 files) and **Read what depends on it before changing it** (read callers first, match existing patterns, run tests after any removal).
- `sdsi:workflow` verification becomes **two-level**: did the change do its job, and did it break a guardrail (hook, script, lint/type config, `CLAUDE.md` rule, skill) — proved by running the guardrail against a known-bad input. Lint and type check are part of the check. The Review checklist covers all four.

### Removed
(none)

### Changed
(none)

### Bug/Issues/Fixes
(none)

## 🟧VERSION 1.1.0 📅 2026-09-23

### Added or New Features
- Every skill runs in **review** or **apply** mode: `/sdsi:<skill> [--review | --apply] [path]`, stated in plain language, or asked. Review scans the code against the skill, catalogs findings (ID, severity, effort, `file:line`, recommendation), presents them, and asks what to apply; apply changes the code directly and verifies it. (TODO #2)
- `ref/findings.md` — the shared review process (intake → catalog → present → ask → route), replacing the `code-reviewer` plugin's intake and catalog phases. `ref/` is a new folder for shared reference files read on demand.
- Findings not applied become numbered `TODO.md` items (`- [ ] #n [F-003 sdsi:errors] …`) that the release chain closes when fixed; a review can be exported to `docs/reviews/YYYY-MM-DD-<skill>.md`.
- `argument-hint` on every skill, so the flags are suggested as the command is typed.
- `sdsi:workflow` gains the Review checklist every other skill already had.
- Project-type companions — `ref/web.md`, `ref/mw.md`, `ref/cli.md` — rewritten as language-neutral guidance with one `## sdsi:<topic>` section per topic. Every skill detects the project type from the code (asking only when the evidence is mixed), then adds the companion's section for itself to its rules and its review lens; no section means nothing extra.

### Removed
- `sdsi:web`, `sdsi:mw`, and `sdsi:cli` skills — replaced by the companions above, which apply automatically instead of being invoked. Their layout/structure sections and Python/Django-specific rules are dropped: source layout now follows the language's and framework's conventions within core's universal invariants, and framework-specific lessons belong in the project's own `CLAUDE.md`.
- The project-type step from `sdsi:all`'s order — it now runs 12 steps (`sdsi:workflow` through `sdsi:deploy`).

### Changed
- `sdsi:core` Step 3 "review first, or just apply?" becomes "Resolve the mode" — flags, then plain language, then the question. `sdsi:all` resolves it once and, in review mode, produces one deduplicated report across all steps.
- `sdsi:errors`: the fatal-error handler becomes a **global error handler** every project must have — wired into the language's uncaught-error hooks, logging every unhandled error, keeping long-running processes alive (only the failing request or unit of work fails), and calling a list of pluggable reporters so a project can add a queue, ServiceNow, or a pager without editing the handler. New rule: try/catch only where the logic requires it; log-and-rethrow or log-and-continue blocks are findings.
- Changelog notes cite the finding IDs they apply, e.g. `(F-003)`.
- Apply mode writes changelog notes in `sdsi:versioning`'s template (creating `CHANGELOG.md` from it when missing) and leaves no verification scripts behind in the project.

### Bug/Issues/Fixes
(none)

## 🟥VERSION 1.0.0 📅 2026-09-23

### Added or New Features
- Topic skills, each growing independently in its own `SKILL.md`: `sdsi:workflow`, `sdsi:standards`, `sdsi:config`, `sdsi:secrets`, `sdsi:logging`, `sdsi:errors`, `sdsi:concurrency` (new topic), `sdsi:testing`, `sdsi:dependencies`, `sdsi:docs`, `sdsi:versioning`, `sdsi:deploy`.
- `sdsi:core` — the non-negotiable rules, the project profile (language and project type asked with AskUserQuestion and recorded in the project's `CLAUDE.md`), the review-first-or-just-apply question before changing existing code, the universal root layout, and the fixed order the skills run in.
- `sdsi:all` — runs every step in core's order, asking review-or-apply once for the whole run.
- `sdsi:deploy` asks the deploy target (containers recommended, not assumed).
- `scripts/python/release.py` — one scripted release chain: VERSION bump, CHANGELOG promotion, automatic TODO.md closure from "TODO #n" references in the notes, docs-only folding into the current version, and version-file sync — configured per project by an optional `scripts/git/release.json`.
- `tests/test_release.py` — unit tests plus end-to-end commits through the real hooks.

### Removed
- `sdsi:base` and `references/shared-context.md` — replaced by `sdsi:core` and the topic skills. Anything invoking `sdsi:base` must invoke `sdsi:core` (the rules) or `sdsi:all` (the full run) instead.
- `scripts/python/bump_changelog.py` — replaced by `scripts/python/release.py`. Projects that copied the old hook pair should copy all three scripts again.
- Section-number references ("SDSI §6") — skills are referenced by name (`sdsi:config`).

### Changed
- The standard is language-neutral: rules are applied in the project language's own idioms, chosen from the recorded profile, instead of assuming Python.
- `sdsi:web`, `sdsi:mw`, and `sdsi:cli` are project types: each owns its project's source layout, entry point, and design, and stays silent unless the profile names that type. They read only `sdsi:core` and point to topics by name.
- `TODO.md` items are numbered (`- [ ] #n`) so the release script can close them.
- The plugin moved out of the `claude-plugins` monorepo into its own repository (`jimmydagher/sdsi-plugin`), registered in the `claude-marketplace` marketplace (`jimmydagher/claude-marketplace`). Reinstall with `/plugin install sdsi@claude-marketplace`. (TODO #1)

### Bug/Issues/Fixes
- A docs-only commit now folds its Unreleased notes into the current version automatically; previously the hook skipped them and they were left in Unreleased.
- `.gitattributes` forces LF line endings, so the hooks run after a Windows checkout; `sdsi:versioning` now requires it in every project.
- The pre-commit hook probes each Python candidate by running it, so a Windows Store `python3` placeholder on PATH no longer breaks the hook.
- The marketplace is now `jtag-claude-marketplace` everywhere — name, repository (`jimmydagher/jtag-claude-marketplace`), and folder — because Claude Code rejects `claude-marketplace` as impersonating an official marketplace. The 1.0.0 install lines no longer work; use `/plugin marketplace add jimmydagher/jtag-claude-marketplace` then `/plugin install sdsi@jtag-claude-marketplace`.

