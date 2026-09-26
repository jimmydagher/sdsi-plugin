---
name: core
description: >
  The core of the Software Development Standard Instructions (SDSI) — the
  short set of non-negotiable rules every SDSI skill enforces, the project
  profile (language, and the project type — web, middleware, or CLI —
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

The rules here apply to every project, every language, every SDSI skill.
They are deliberately short: the detail lives in the topic skills, each of
which reads this file first and then adds its own rules. Where a topic says
more about something mentioned here, the topic is the detail and this file
is the floor.

## 1. How every SDSI skill runs

Every SDSI skill — a topic like `sdsi:logging`, or the full run `sdsi:all`
— follows these steps, in order, before doing its own work.

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
- **Project type** — what kind of program this is, which decides the
  companion (below):

  | Type | Companion | For | Evidence in the code |
  |---|---|---|---|
  | `web` | `ref/web.md` | Anything serving pages or an HTTP API to users | A web framework dependency, routes/handlers, templates |
  | `mw` | `ref/mw.md` | Services moving and reconciling data between systems (sync, ETL, connectors) | Connectors to external systems, scheduled or triggered sync tasks, a destination write |
  | `cli` | `ref/cli.md` | A tool meant to be run and reused, not a one-off | An argument parser at the entry point, commands, no server |
  | `other` | — | Anything else | — |

  **Identify it from the code when it isn't recorded** — say what you found
  and why ("web: a web framework dependency and route handlers in
  `src/app/`") and record it. Ask with `AskUserQuestion` only when the
  evidence is mixed or the project is empty. Never pick one silently.

A topic may ask its own questions (e.g. `sdsi:deploy` asks the deploy
target); it records its answer in the same profile section.

**The project-type companion.** Once the type is known, a skill reads its
companion (`../../ref/<type>.md`) and applies **only the section headed with
its own name** (`## sdsi:errors` for `sdsi:errors`) on top of its own rules —
in apply mode as extra rules, in review mode as part of the lens. When the
companion has no section for the running skill, or the type is `other`,
there's nothing to add: say so in one line ("no web-specific considerations
for errors") and continue. A companion never overrides core or the skill;
where it deliberately deviates (e.g. the CLI's flag precedence over
`sdsi:config`), it says so.

### Step 3 — Resolve the mode: review or apply

Every skill runs against code in one of two modes:

```
/sdsi:<skill> [--review | --apply] [path]

/sdsi:errors --review src/payments
/sdsi:all --apply
```

- **Review** — report findings and recommendations; change nothing until the
  human chooses. Follow `../../ref/findings.md` (intake → catalog → present
  → ask → route each finding).
- **Apply** — the human trusts the skill: change the code to meet it, verify
  (core §2, "double-check your work"), report what changed, and write the
  changelog notes. Never commit (`sdsi:versioning`).
  - **Changelog notes use `sdsi:versioning`'s format** — the `🚧 Unreleased`
    section with its four fixed subsections. If the project has no
    `CHANGELOG.md`, create it from that template, never an improvised shape.
  - **Verification leaves nothing behind.** A throwaway check script runs
    from outside the project (a scratch or temp directory) or is removed
    before reporting; never leave one in the project, least of all at the
    root.

Resolve the mode in this order:

1. **The arguments** — `--review` or `--apply` anywhere after the command.
2. **Plain language** — "review my error handling" is review; "apply the
   logging standard" is apply.
3. **Otherwise ask** with `AskUserQuestion`: *Review findings first* or
   *Apply directly*.

**Scope** is the path in the arguments, else the whole project — say which.
**An empty project** skips the question: there's nothing to review, so the
skill scaffolds (apply). `sdsi:all` resolves the mode once for the whole
run, not once per topic.

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
- **Confirm before anything destructive or bulk.** Deleting, overwriting,
  or mutating data that can't be trivially restored, and any run over many
  items (a batch job, a migration, a bulk edit), needs the human's explicit
  approval first — with the scope stated (what, and how many). Read-only
  actions and changes a `git checkout` undoes don't need it. Approval for one
  action or one scope doesn't carry to the next.
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
| An entry point | Holds no logic — wires things together and exits with the outcome the orchestration layer returns | the language's and framework's conventions |
| A layout | Root holds only project files and top-level folders — no loose code. Dependencies point one way (shared helpers ← integrations ← operations ← entry point). One home for shared code, never a second `utils/`/`common/` beside it | the language's and framework's conventions |
| Code conventions | Named constants, no magic strings, typed boundaries, reuse over reimplementation | `sdsi:standards` |
| Configuration | One source of truth, schema-validated before work starts, no defaults in code | `sdsi:config` |
| Secrets | Never in code/config/history; read at runtime from a secrets store | `sdsi:secrets` |
| Logging | One central logger, standard levels | `sdsi:logging` |
| Error handling | One global error handler that logs every unhandled error, typed errors, try/catch only where logic requires it, a machine-readable outcome on every exit | `sdsi:errors` |
| Concurrency | Shared state owned, background work bounded and drained on shutdown | `sdsi:concurrency` |
| Tests | Under one `tests/` folder; every test names the regression it catches | `sdsi:testing` |
| Dependencies | Few, pinned, locked, scanned | `sdsi:dependencies` |
| Documentation | `README.md`, `docs/`, `TODO.md`, updated in the same change | `sdsi:docs` |
| A version | `VERSION` + `CHANGELOG.md` + the release hooks, automated by script | `sdsi:versioning` |
| A way to run it | Local run config versioned; deploy target chosen by the human | `sdsi:deploy` |

**The project root is the same for every type** — only these files and
folders, nothing runnable loose at this level. What goes inside the source
folder follows the language's and framework's own conventions, within the
invariants above:

```
project-root/
├── <source>/        # named by language/framework convention (src/ by default)
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
deliberate — how work is done, then the code itself, then what surrounds
it, then how it ships. Every step also applies its section of the
project-type companion (§1 Step 2).

| # | Skill | Owns |
|---|---|---|
| 0 | `sdsi:core` | This file — profile, project type, review/apply mode, non-negotiables |
| 1 | `sdsi:workflow` | Plan before code, the artifact chain, scope, starting a new project |
| 2 | `sdsi:standards` | Naming, constants, comments, reuse, SOLID, typing, input validation |
| 3 | `sdsi:config` | Configuration files, schema, validation |
| 4 | `sdsi:secrets` | Secrets store, naming, rotation, redaction |
| 5 | `sdsi:logging` | Central logger, levels, output destinations |
| 6 | `sdsi:errors` | Global error handler, error hierarchy, retries, exit outcomes |
| 7 | `sdsi:concurrency` | Threads, async, background work, shutdown |
| 8 | `sdsi:testing` | Test layout, pyramid, meaningful coverage |
| 9 | `sdsi:dependencies` | Adding, pinning, scanning dependencies |
| 10 | `sdsi:docs` | README, `docs/`, `TODO.md` |
| 11 | `sdsi:versioning` | Git hygiene, `VERSION`, `CHANGELOG.md`, the release hooks |
| 12 | `sdsi:deploy` | Local run environment, deploy target, containers |

A topic grows by editing its own `SKILL.md` — nothing else. A new topic gets
a row in this table and a slot in the order. A new project type gets a row
in Step 2's table and a `ref/<type>.md` companion with one `## sdsi:<topic>`
section per topic it adds to.

## 5. Loading

- **A skill in this plugin** reads `../core/SKILL.md` by relative path as
  its first action.
- **Shared reference files live in the plugin's `ref/` folder** and are read
  on demand by relative path (`../../ref/<file>.md`) — only when a step needs
  them: `ref/findings.md` in review mode, and the project-type companion
  (`ref/web.md`, `ref/mw.md`, `ref/cli.md`) once the type is known.
- **A skill in a different plugin** invokes `sdsi:core` (the rules) or
  `sdsi:all` (the full run) by name — never a relative path across plugins,
  since where two plugins sit on disk isn't something either can assume.
