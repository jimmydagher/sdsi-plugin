---
name: core
description: >
  The core of the Software Development Standard Instructions (SDSI) — the
  short set of non-negotiable rules every SDSI skill enforces, the project
  profile (language, project type) every skill works from, the
  review-or-apply question asked before touching existing code, and the
  fixed order the topic skills run in. Every other sdsi skill reads this
  first. Use it whenever writing, reviewing, planning, or scaffolding code
  under SDSI, or when a skill in another plugin needs SDSI's rules (invoke
  `sdsi:core` by name). Also triggers on "/sdsi", "/sdsi:core", "SDSI", or
  "our dev standards".
---

# SDSI Core

The rules here apply to every project, every language, every SDSI skill.
They are deliberately short: the detail lives in the topic skills, each of
which reads this file first and then adds its own rules. Where a topic says
more about something mentioned here, the topic is the detail and this file
is the floor.

## 1. How every SDSI skill runs

Every SDSI skill — a topic like `sdsi:logging`, a project type like
`sdsi:web`, or the full run `sdsi:all` — follows these steps, in order,
before doing its own work.

### Step 1 — Say what you're doing

Tell the human which SDSI skill is running, which files it read to get
there (e.g. "`sdsi:logging` → `sdsi:core` → project `CLAUDE.md`"), which
rules it's applying, and when it switches to another skill or tool. Nothing
about how the standard is being applied should be invisible.

### Step 2 — Load the project profile

Every rule is applied through the project's profile. Look for an
`## SDSI profile` section in the project's `CLAUDE.md`:

```markdown
## SDSI profile

- Language: <e.g. Python 3.13>
- Project type: <web | mw | cli | other: short description>
- Deploy target: <recorded by sdsi:deploy when first asked>
```

If the section or a field the current skill needs is missing, **ask with
`AskUserQuestion` — never infer it silently** — then write the answer into
`CLAUDE.md` (creating the file if needed) so no later session asks again:

- **Language** — which language (and major version) the project uses. SDSI's
  rules are language-neutral; apply each one using that language's own
  idioms, tooling, and conventions (its casing rules, its enum construct,
  its standard test runner, package manager, lockfile, and vulnerability
  scanner). Where a language convention and an SDSI example disagree on
  *form* (casing, file naming), the language convention wins; the rule's
  *intent* doesn't bend.
- **Project type** — which project-type skill owns the project's layout,
  entry point, and design:

  | Type | Skill | For |
  |---|---|---|
  | Website / web app | `sdsi:web` | Anything serving pages or an HTTP API to users |
  | Middleware / integration | `sdsi:mw` | Services moving and reconciling data between systems (sync, ETL, connectors) |
  | Command-line tool | `sdsi:cli` | A tool or script meant to be run and reused, not a one-off |
  | Other | — | Apply §3's universal invariants only; say so, and add a `TODO.md` item to grow a project-type skill from this project |

  A project-type skill stays silent unless the profile says the project is
  that type (or the human invokes it by name).

A topic may ask its own questions (e.g. `sdsi:deploy` asks the deploy
target); it records its answer in the same profile section.

### Step 3 — Existing code: review first, or just apply?

If the skill is about to change code that already exists, ask once per run
with `AskUserQuestion`:

- **Review first** — scan the code against the skill's rules and present
  the findings (rule, `file:line`, severity, proposed fix) as a table.
  Change nothing until the human says which findings to apply.
- **Just apply** — make the changes directly, then report what changed.

On an empty project there's nothing to review; skip the question.
`sdsi:all` asks it once for the whole run, not once per topic.

### Step 4 — Respect the project's own deviations

A deliberate, written-down deviation in the project's `CLAUDE.md` wins for
that project. Everywhere else SDSI governs. A new deviation gets written
into `CLAUDE.md` the moment it's made, so a later session doesn't quietly
regress toward SDSI's default.

## 2. Non-negotiable principles

These hold regardless of project, language, or how small the change looks.
Every SDSI skill enforces them.

- **Communicate what you are doing.** See Step 1.
- **No over-engineering.** Solve the problem in front of you, not the one
  that might show up later. A pattern, abstraction, or config option earns
  its place by having a second real caller today.
- **No assumptions.** A requirement, value, or behavior that isn't stated
  gets surfaced — asked, or written down as an open question — never
  silently decided.
- **No random or pointless changes.** Every line in a change traces to a
  stated reason. Reformatting, renaming, or "while I'm in here" edits get
  their own change.
- **Double-check your work.** Nothing is done on the strength of its own
  judgment. It's done once verified against something outside it — a test,
  a build, a run, a second read — and the evidence is shown.
- **Consistency over cleverness.** Predictable code is what makes handoffs,
  debugging, and AI-assisted work fast.
- **Config and secrets are never code.** No setting falls back to a value
  baked into code; no credential appears in source, config, or history.
- **Fail loud, fail early, fail once.** Stop at the earliest point and report
  everything wrong in one pass.
- **Observable by default.** Logging and error reporting are designed in
  from the start.
- **One front door per capability.** One logger, one config loader, one
  secrets accessor, one error handler, one HTTP client. Extend it for
  everyone rather than working around it in one place.
- **Standard library first.** If it can be built with the language's own
  standard library, don't add a dependency for it.

## 3. Universal invariants — every program has these

Whatever the language or project type, every program SDSI governs has:

| Element | Invariant | Detail |
|---|---|---|
| An entry point | Holds no logic — wires things together and exits with the outcome the orchestration layer returns | project-type skill |
| A layout | Root holds only project files and top-level folders — no loose code. Dependencies point one way (shared helpers ← integrations ← operations ← entry point). One home for shared code, never a second `utils/`/`common/` beside it | project-type skill |
| Code conventions | Named constants, no magic strings, typed boundaries, reuse over reimplementation | `sdsi:standards` |
| Configuration | One source of truth, schema-validated before work starts, no defaults in code | `sdsi:config` |
| Secrets | Never in code/config/history; read at runtime from a secrets store | `sdsi:secrets` |
| Logging | One central logger, standard levels | `sdsi:logging` |
| Error handling | Typed errors, one fatal handler, a machine-readable outcome on every exit | `sdsi:errors` |
| Concurrency | Shared state owned, background work bounded and drained on shutdown | `sdsi:concurrency` |
| Tests | Under one `tests/` folder; every test names the regression it catches | `sdsi:testing` |
| Dependencies | Few, pinned, locked, scanned | `sdsi:dependencies` |
| Documentation | `README.md`, `docs/`, `TODO.md`, updated in the same change | `sdsi:docs` |
| A version | `VERSION` + `CHANGELOG.md` + the release hooks, automated by script | `sdsi:versioning` |
| A way to run it | Local run config versioned; deploy target chosen by the human | `sdsi:deploy` |

**The project root is the same for every type** — only these files and
folders, nothing runnable loose at this level. The project-type skill
defines what goes inside the source folder:

```
project-root/
├── <source>/        # named by the project-type skill (src/, site/, …)
├── tests/           # sdsi:testing
├── config/          # default.yaml + override/<env>.yaml — sdsi:config
├── docs/            # sdsi:docs
├── scripts/         # operational tooling, never imported by <source>
│   ├── git/         #   release hooks — mandatory (sdsi:versioning)
│   └── python/      #   release.py — mandatory; other tooling by language
├── <deploy files>   # e.g. docker/ — per sdsi:deploy's target
├── <IDE run config> # e.g. .vscode/ — versioned (sdsi:deploy)
├── <manifest + lockfile>  # the language's own (sdsi:dependencies)
├── .gitignore  .gitattributes
├── VERSION  CHANGELOG.md  TODO.md  CLAUDE.md  README.md
```

**The release chain is automated from day one on every project** — the
`scripts/git/` hooks and `scripts/python/release.py` this plugin ships.
The AI writes changelog notes; scripts do the bump, promotion, `TODO.md`
closure, and commit message. See `sdsi:versioning`.

## 4. The skills, and the order they run in

`sdsi:all` runs every step below in this order; each skill can also be
invoked on its own (it still runs §1's steps first). The order is
deliberate — how work is done, then where code lives, then the code
itself, then what surrounds it, then how it ships.

| # | Skill | Owns |
|---|---|---|
| 0 | `sdsi:core` | This file — profile, review-or-apply, non-negotiables |
| 1 | `sdsi:workflow` | Plan before code, the artifact chain, scope, starting a new project |
| 2 | `sdsi:web` / `sdsi:mw` / `sdsi:cli` | Layout, entry point, and design for the project's type (only the one matching the profile) |
| 3 | `sdsi:standards` | Naming, constants, comments, reuse, SOLID, typing, input validation |
| 4 | `sdsi:config` | Configuration files, schema, validation |
| 5 | `sdsi:secrets` | Secrets store, naming, rotation, redaction |
| 6 | `sdsi:logging` | Central logger, levels, output destinations |
| 7 | `sdsi:errors` | Exception hierarchy, fatal handler, retries, exit outcomes |
| 8 | `sdsi:concurrency` | Threads, async, background work, shutdown |
| 9 | `sdsi:testing` | Test layout, pyramid, meaningful coverage |
| 10 | `sdsi:dependencies` | Adding, pinning, scanning dependencies |
| 11 | `sdsi:docs` | README, `docs/`, `TODO.md` |
| 12 | `sdsi:versioning` | Git hygiene, `VERSION`, `CHANGELOG.md`, the release hooks |
| 13 | `sdsi:deploy` | Local run environment, deploy target, containers |

A topic grows by editing its own `SKILL.md` — nothing else. A new topic gets
a row in this table and a slot in the order; a new project type gets a row
in Step 2's table.

## 5. Loading

- **A skill in this plugin** reads `../core/SKILL.md` by relative path as
  its first action.
- **A skill in a different plugin** invokes `sdsi:core` (the rules) or
  `sdsi:all` (the full run) by name — never a relative path across plugins,
  since where two plugins sit on disk isn't something either can assume.
