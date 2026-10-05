---
name: core
description: >
  The core of the Software Development Standard Instructions (SDSI) — the
  short set of non-negotiable rules every SDSI skill enforces, the project
  profile (language, and the project type — web, middleware, CLI,
  library, desktop, or mobile —
  detected from the code, whose companion guidance every skill adds to its
  own) every skill works from, the review or
  apply mode every skill runs in (--review / --apply, or asked), and the
  fixed order the topic skills run in. Every other sdsi skill reads this
  first. Use it whenever writing, reviewing, planning, or scaffolding code
  under SDSI, or when a skill in another plugin needs SDSI's rules (invoke
  `sdsi:core` by name). Also triggers on "/sdsi", "/sdsi:core", "SDSI", or
  "our dev standards".
argument-hint: "[--review|--apply] [path]"
---

# SDSI Core

The rules here apply to every project, every language, every SDSI skill. They are deliberately short: the detail lives in the topic skills, each of which reads this file first and then adds its own rules. Where a topic says more about something mentioned here, the topic is the detail and this file is the floor.

## 1. How every SDSI skill runs

Every SDSI skill — a topic like `sdsi:logging`, or the full run `sdsi:all` — follows these steps, in order, before doing its own work.

### Step 1 — Say what you're doing

Tell the human which SDSI skill is running, which files it read to get there (e.g. "`sdsi:logging` → `sdsi:core` → project `CLAUDE.md`"), which rules it's applying, and when it switches to another skill or tool. Nothing about how the standard is being applied should be invisible.

### Step 2 — Load the project profile

Every rule is applied through the project's profile. Look for an `## SDSI profile` section in the project's `.claude/CLAUDE.md` — a `CLAUDE.md` still at the root moves there first (§3):

```markdown
## SDSI profile

- Language: <e.g. Python 3.13>
- Project type: <web | mw | cli | lib | desktop | mobile | other: short description>
- Deploy target: <recorded by sdsi:deploy when first asked>
- Upkeep: <recorded by sdsi:upkeep — the installed topics, or declined>
```

If the section or a field the current skill needs is missing, **ask with `AskUserQuestion` — never infer it silently** — then write the answer into `.claude/CLAUDE.md` (creating the file if needed) so no later session asks again:

- **Language** — which language (and major version) the project uses. SDSI's rules are language-neutral; apply each one using that language's own idioms, tooling, and conventions (its casing rules, its enum construct, its standard test runner, package manager, lockfile, and vulnerability scanner). Where a language convention and an SDSI example disagree on *form* (casing, file naming), the language convention wins; the rule's *intent* doesn't bend.
- **Project type** — what kind of program this is, which decides the companion (below):

  | Type | Companion | For | Evidence in the code |
  |---|---|---|---|
  | `web` | `ref/web.md` | Anything serving pages or an HTTP API to users | A web framework dependency, routes/handlers, templates |
  | `mw` | `ref/mw.md` | Services moving and reconciling data between systems (sync, ETL, connectors) | Connectors to external systems, scheduled or triggered sync tasks, a destination write |
  | `cli` | `ref/cli.md` | A tool meant to be run and reused, not a one-off | An argument parser at the entry point, commands, no server |
  | `lib` | `ref/lib.md` | A library or package other code imports — published to a registry or shared internally | A package manifest with an exported API and no entry point of its own; consumers import it |
  | `desktop` | `ref/desktop.md` | A GUI application installed on users' machines (Windows, macOS, Linux) | A desktop UI toolkit dependency, windows/views, an installer or app bundle definition |
  | `mobile` | `ref/mobile.md` | An iOS, Android, or cross-platform mobile app | A mobile SDK or framework, app manifests (`Info.plist`, `AndroidManifest.xml`), store build config |
  | `other` | — | Anything else | — |

  A project can be more than one (a web app that ships a CLI); record the main type, and name the second in the profile when its companion should apply too.

  **Identify it from the code when it isn't recorded** — say what you found and why ("web: a web framework dependency and route handlers in `src/app/`") and record it. Ask with `AskUserQuestion` only when the evidence is mixed or the project is empty. Never pick one silently.

A topic may ask its own questions (e.g. `sdsi:deploy` asks the deploy target); it records its answer in the same profile section.

**The project-type companion.** Once the type is known, a skill reads its companion (`../../ref/<type>.md` — each recorded type's, when there are two) and applies **only the section headed with its own name** (`## sdsi:errors` for `sdsi:errors`) on top of its own rules — in apply mode as extra rules, in review mode as part of the lens. When the companion has no section for the running skill, or the type is `other`, there's nothing to add: say so in one line ("no web-specific considerations for errors") and continue. A companion never overrides core or the skill; where it deliberately deviates (e.g. the CLI's flag precedence over `sdsi:config`), it says so.

### Step 3 — Resolve the mode: review or apply

Every skill runs against code in one of two modes:

```text
/sdsi:<skill> [--review | --apply] [path]

/sdsi:errors --review src/payments
/sdsi:all --apply
```

- **Review** — report findings and recommendations; change nothing until the human chooses. Follow `../../ref/findings.md` (intake → catalog → present → ask → route each finding).
- **Apply** — the human trusts the skill: change the code to meet it, verify (core §2, "double-check your work"), report what changed, and write the changelog notes. Never commit (`sdsi:versioning`).
  - **Changelog notes use `sdsi:versioning`'s format** — the `🚧 Unreleased` section with its four fixed subsections. If the project has no `meta/CHANGELOG.md`, create it from that template, never an improvised shape.
  - **Verification leaves nothing behind.** A throwaway check script runs from outside the project (a scratch or temp directory) or is removed before reporting; never leave one in the project, least of all at the root.

Resolve the mode in this order:

1. **The arguments** — `--review` or `--apply` anywhere after the command.
2. **Plain language** — "review my error handling" is review; "apply the logging standard" is apply.
3. **Otherwise ask** with `AskUserQuestion`: *Review findings first* or *Apply directly*.

**Scope** is the path in the arguments, else the whole project — say which. **An empty project** skips the question: there's nothing to review, so the skill scaffolds (apply). `sdsi:all` resolves the mode once for the whole run, not once per topic.

### Step 4 — Respect the project's own deviations

A deliberate, written-down deviation in the project's `CLAUDE.md` wins for that project. Everywhere else SDSI governs. A new deviation gets written into `CLAUDE.md` the moment it's made, so a later session doesn't quietly regress toward SDSI's default.

### Step 5 — Offer upkeep, last

A skill only loads when it's invoked or its triggers match, so its rules lapse between runs. A skill with an `## Upkeep` section ends — after changes were made, in apply mode or by applying review findings — by asking with `AskUserQuestion` whether to leave its upkeep lines in the project: *Leave upkeep instructions* or *Not now*. On yes, install them through `sdsi:upkeep` into `.claude/rules/sdsi.md`, which Claude Code loads every session. Skip the question when the project already has this skill's lines, or the human has declined it before (recorded in `CLAUDE.md`). `sdsi:all` asks once, at the end of the run, for every topic it ran.

## 2. Non-negotiable principles

These hold regardless of project, language, or how small the change looks. Every SDSI skill enforces them.

- **Communicate what you are doing.** See Step 1.
- **No over-engineering.** Solve the problem in front of you, not the one that might show up later. A pattern, abstraction, or config option earns its place by having a second real caller today. The check runs again after writing: code far longer than the problem needs (200 lines that could be 50) gets rewritten before it's called done.
- **No assumptions.** A requirement, value, or behavior that isn't stated gets surfaced — asked, or written down as an open question — never silently decided. A request that reads two ways gets both readings laid out instead of one picked; when a simpler approach than the one asked for exists, say so and push back.
- **No random or pointless changes.** Every line in a change traces to a stated reason. Reformatting, renaming, or "while I'm in here" edits get their own change. Clean up only your own leftovers: remove what this change made unused (an import, a variable, a function); dead code that was already there gets mentioned, not deleted.
- **Double-check your work.** Nothing is done on the strength of its own judgment. It's done once verified against something outside it — a test, a build, a run, a second read — and the evidence is shown.
- **Confirm before anything destructive or bulk.** Deleting, overwriting, or mutating data that can't be trivially restored, and any run over many items (a batch job, a migration, a bulk edit), needs the human's explicit approval first — with the scope stated (what, and how many). Read-only actions and changes a `git checkout` undoes don't need it. Approval for one action or one scope doesn't carry to the next.
- **Consistency over cleverness.** Predictable code is what makes handoffs, debugging, and AI-assisted work fast.
- **Config and secrets are never code.** No setting falls back to a value baked into code; no credential appears in source, config, or history.
- **Protected data reaches only its owner.** Personal, key, or restricted data is never returned to anyone not signed in with their own account. A guest flow that must confirm identity, like paying a bill, gets server-side redacted fragments only (`sdsi:security`).
- **Fail loud, fail early, fail once.** Stop at the earliest point and report everything wrong in one pass.
- **Observable by default.** Logging and error reporting are designed in from the start.
- **One front door per capability.** One logger, one config loader, one secrets accessor, one error handler, one HTTP client. Extend it for everyone rather than working around it in one place.
- **Standard library first.** If it can be built with the language's own standard library, don't add a dependency for it.

## 3. Universal invariants — every program has these

Whatever the language or project type, every program SDSI governs has:

| Element | Invariant | Detail |
|---|---|---|
| An entry point | Holds no logic — wires things together and exits with the outcome the orchestration layer returns | the language's and framework's conventions |
| A layout | Root holds `README.md` and top-level folders — no other loose file (below). Dependencies point one way (shared helpers ← integrations ← operations ← entry point). One home for shared code, never a second `utils/`/`common/` beside it | the language's and framework's conventions |
| Code conventions | Named constants, no magic strings, typed boundaries, reuse over reimplementation | `sdsi:standards` |
| Configuration | One source of truth, schema-validated before work starts, no defaults in code | `sdsi:config` |
| Security | Secrets never in code/config/history, read at runtime from a secrets store; untrusted input validated at the boundary; protected data only to its owner; security settings per trust boundary | `sdsi:security` |
| Logging | One central logger, standard levels, log calls enqueue and one writer writes in arrival order, files rotated on a schedule — plus a separate audit trail wherever the program makes security decisions | `sdsi:logging` |
| Error handling | One global error handler that logs every unhandled error, typed errors, try/catch only where logic requires it, a machine-readable outcome on every exit | `sdsi:errors` |
| Concurrency | Shared state owned, background work bounded and drained on shutdown | `sdsi:concurrency` |
| Tests | Under one `tests/` folder; every test names the regression it catches | `sdsi:testing` |
| Dependencies | Few, pinned, locked, scanned | `sdsi:dependencies` |
| Documentation | `README.md`, `docs/`, `meta/TODO.md`, updated in the same change | `sdsi:docs` |
| A version | `meta/VERSION` + `meta/CHANGELOG.md` + the release hooks, automated by script | `sdsi:versioning` |
| A way to run it | Local run config versioned; deploy target chosen by the human | `sdsi:deploy` |

**The project root is the same for every type: `README.md` is the only file a person puts there — everything else lives in a folder.** The only other files allowed at the root are ones a tool reads nowhere else: git's `.gitignore` and `.gitattributes`, and the language's manifest and lockfile when its tooling requires the root. Habit isn't a reason — a file that works from a folder goes in one. What goes inside the source folder follows the language's and framework's own conventions, within the invariants above:

```text
project-root/
├── README.md        # the only document at the root (sdsi:docs)
├── .claude/
│   └── CLAUDE.md    # conventions + SDSI profile (§1 Step 2); Claude Code loads it from here
├── <source>/        # named by language/framework convention (src/ by default)
├── tests/           # sdsi:testing
├── config/          # default.yaml + override/<env>.yaml — sdsi:config
├── docs/            # documents people read: processes, how-tos, setup, deployment — sdsi:docs
│   └── design/      #   INTENT.md, SPEC.md, PLAN.md — the whole project's design (sdsi:workflow)
├── meta/            # the project's record — version, history, outstanding work
│   ├── CHANGELOG.md #   sdsi:versioning
│   ├── TODO.md      #   sdsi:docs
│   └── VERSION      #   sdsi:versioning
├── scripts/         # operational tooling, never imported by <source>
│   ├── git/         #   release hooks — mandatory (sdsi:versioning)
│   └── python/      #   release.py — mandatory; other tooling by language
├── <deploy files>   # e.g. docker/ — per sdsi:deploy's target
├── <IDE run config> # e.g. .vscode/ — versioned (sdsi:deploy)
├── <manifest + lockfile>  # the language's own, only where its tooling needs the root (sdsi:dependencies)
└── .gitignore  .gitattributes  # git applies these repo-wide only from the root
```

**An existing project with other files at the root moves them in one change**, with `git mv` so history follows, and updates everything that references a moved file by path in the same change:

| At the root | Moves to | Steps |
|---|---|---|
| `CLAUDE.md` | `.claude/CLAUDE.md` | Just the move |
| `VERSION`, `CHANGELOG.md`, `TODO.md` | `meta/` | Together with the release scripts that read them there — `sdsi:versioning`, "Moving the release files out of the root" |
| Anything else | The folder that owns it — `docs/`, `scripts/`, `config/`, the deploy folder | Ask with `AskUserQuestion` when the right home isn't clear |

**The release chain is automated from day one on every project** — the `scripts/git/` hooks and `scripts/python/release.py` this plugin ships. The AI writes changelog notes; scripts do the bump, promotion, `TODO.md` closure, and commit message. See `sdsi:versioning`.

## 4. The skills, and the order they run in

`sdsi:all` runs every step below in this order; each skill can also be invoked on its own (it still runs §1's steps first). The order is deliberate — how work is done, then the code itself, then what surrounds it, then how it ships. Every step also applies its section of the project-type companion (§1 Step 2).

| # | Skill | Owns |
|---|---|---|
| 0 | `sdsi:core` | This file — profile, project type, review/apply mode, non-negotiables |
| 1 | `sdsi:workflow` | Plan before code, the artifact chain, scope, starting a new project |
| 2 | `sdsi:standards` | Naming, constants, comments, reuse, SOLID, typing |
| 3 | `sdsi:config` | Configuration files, schema, validation |
| 4 | `sdsi:security` | Secrets (store, naming, rotation, redaction), untrusted input, protected-data exposure, trust-boundary settings |
| 5 | `sdsi:logging` | Central logger, levels, output destinations |
| 6 | `sdsi:errors` | Global error handler, error hierarchy, retries, exit outcomes |
| 7 | `sdsi:concurrency` | Threads, async, background work, shutdown |
| 8 | `sdsi:testing` | Test layout, pyramid, meaningful coverage |
| 9 | `sdsi:dependencies` | Adding, pinning, scanning dependencies |
| 10 | `sdsi:docs` | README, `docs/`, `TODO.md` |
| 11 | `sdsi:versioning` | Git hygiene, `VERSION`, `CHANGELOG.md`, the release hooks |
| 12 | `sdsi:deploy` | Local run environment, deploy target, containers |

Outside the order: **`sdsi:upkeep`** keeps a project's `.claude/rules/sdsi.md` — the standing instructions assembled from each topic's `## Upkeep` section (§1 Step 5).

A topic grows by editing its own `SKILL.md` — nothing else. A new topic gets a row in this table and a slot in the order. A new project type gets a row in Step 2's table and a `ref/<type>.md` companion with one `## sdsi:<topic>` section per topic it adds to.

## 5. Loading

- **A skill in this plugin** reads `../core/SKILL.md` by relative path as its first action.
- **Shared reference files live in the plugin's `ref/` folder** and are read on demand by relative path (`../../ref/<file>.md`) — only when a step needs them: `ref/findings.md` in review mode, and the project-type companion (`ref/<type>.md`, §1 Step 2's table) once the type is known.
- **A skill in a different plugin** invokes `sdsi:core` (the rules) or `sdsi:all` (the full run) by name — never a relative path across plugins, since where two plugins sit on disk isn't something either can assume.
