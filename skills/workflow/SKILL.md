---
name: workflow
description: >
  SDSI's development workflow — plan before code, the project's living
  design documents (docs/design/INTENT.md, SPEC.md, PLAN.md with its
  ⛏️ In progress section), reverse-engineering them for an existing
  project, updating them for every new feature, verifying before calling anything done, flagging scope
  growth, stage gates, closing the loop on production issues, keeping
  institutional knowledge in CLAUDE.md, and the kickoff sequence for a
  brand-new project, sizing plan steps, reading a change's dependents
  first, and two-level verification. Use when starting a new project, planning a feature,
  or deciding how a change should move from idea to commit. Reads sdsi:core
  first. Triggers on "/sdsi:workflow", "start a new project", "how should
  we plan this".
argument-hint: "[--review|--apply] [path|branch]"
---

# SDSI: Workflow

Before anything else, read `../core/SKILL.md` and run its steps.

Adapted from Anthropic's AI-Native SDLC playbook ([claude.com/blog/the-ai-native-sdlc-playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)). Applies in full on new projects; on established code, adopt what fits.

## The design documents

Idea → Intent (why) → Spec (what) → Plan (how) → Implementation → Validation. Every project has three design documents in `docs/design/`, each describing **the whole project as it stands** — not one change:

| Document | Answers | Holds |
|---|---|---|
| `INTENT.md` | Why | The problem in the requester's words, who it's for, goals, constraints, non-goals, open questions — open questions stay open here until answered |
| `SPEC.md` | What | Every feature and its behavior, interfaces, data, and the non-functional requirements — performance, availability, security — each stated so it can be checked; the testing strategy (`sdsi:testing`) and the monitoring strategy; written against SDSI |
| `PLAN.md` | How | Architecture, components, and how each is built and verified — plus **⛏️ In progress** (below) |

- **They're living documents**, rewritten in place (`sdsi:docs`): after any change they read as if the project had been designed that way from the start. A feature that's dropped is removed, not struck through.
- **⛏️ In progress** is the first section of `PLAN.md`: the steps of the change underway — which files change, in what order, and what proves each step worked. A step that rests on an assumption that could turn out false names its **STOP condition** — what would mean stop and report rather than improvise ("if the callers rely on the empty-list return, stop"). The human approves it before code. When the change is done, its steps are merged into the plan's body, and the section goes back to `(none)`.
- **Brainstorming sits above SDSI.** A brainstorming skill (such as `superpowers:brainstorming`) turns an idea into something concrete; its result is merged into these three documents, and any per-topic design file it writes isn't kept.

## Plan before code, always

Nothing is implemented from an unstated plan. **Every new feature — from `TODO.md` or straight from a prompt — updates the design documents before any code:** `INTENT.md` if the why changes, then `SPEC.md`, then `PLAN.md`'s ⛏️ In progress. It scales down — a one-line fix doesn't touch the documents, but it still needs a stated reason, and if it isn't self-evidently safe, a one-sentence plan beats none.

**A project without the documents gets them reverse-engineered** from the code, `README.md`, config, tests, and history. Mark every inferred statement `(inferred — confirm)` and ask the human about each; `INTENT.md` most of all, since code shows what and how but rarely why. Until the human confirms them, they're a draft.

## Size the steps

Each step in ⛏️ In progress is small enough to finish and verify in one focused session — a rough guide is under ~30 minutes and ~5 files. A step past that gets split before work starts, because errors compound across a large step and a failure deep into one is expensive to unwind. A step that turns out bigger than planned is a scope change (below), not something to push through.

## Read what depends on it before changing it

Before modifying or removing a function, type, config key, or file, read what uses it — every caller, importer, and reader — not just the target. And the code around it: match how the codebase already solves the problem rather than introducing a second way (core: consistency). After a removal, run the tests; small deletions cascade.

## Reference a system by reading it, not recalling it

"Do it the way X does it" means reading X's actual implementation before designing. Reading it in full may reveal that X never solved the exact problem in front of you — bring that back before designing, don't discover it mid-implementation.

## Verify before calling anything done

Every task has a way to check itself, and the check runs before the work is reported done. Validation closes the chain: the change does what `SPEC.md` says, and the deployed system meets its non-functional requirements (`sdsi:deploy`). For a bug fix: write the failing test, confirm it fails for the expected reason, then make it pass without touching the test. The project's own linter and type checker run as part of the check, not after it.

Verification has two levels, and **both are required**:

1. **Did the change do its job?** The task's own check — tests, a run.
2. **Did the change break a guardrail?** When the change touches the scaffolding the work runs on — a hook, a release or CI script, a lint or type-check config, a `CLAUDE.md` rule, a skill, a test harness — prove the guardrail still fires: run it against a known-bad input and see it refuse. A guardrail nobody has tested since it was changed is assumed broken.

## Institutional knowledge lives in files

A project's conventions, gotchas, and repeated corrections live in its `CLAUDE.md` — under a page, updated the moment a mistake happens twice. SDSI is the standard; `CLAUDE.md` holds only what's particular to this project (including its `## SDSI profile` and any deliberate deviations). Anything that must be applied consistently from one place is a candidate for a skill, not a paragraph someone has to remember.

## Review runs in both directions

A change is reviewed against SDSI, `SPEC.md`, and `PLAN.md`'s approved ⛏️ In progress. Findings carry a severity; only ones that break behavior, leak data, or breach a stated policy block. The same mistake caught twice goes into `CLAUDE.md`.

## Scope changes get flagged, not absorbed

When a request grows past what was understood — a small fix that turns out to touch secret handling, a decision that starts affecting every deploy target — stop, say so, and get a fresh, explicitly scoped decision before designing further. A behavior that's someone else's contract (a flag, an API field, an output format) doesn't get quietly widened or narrowed while fixing something next to it.

## Stage gates

Human judgment concentrates at the gates — approving the `INTENT.md` and `SPEC.md` changes, approving ⛏️ In progress, approving the code for commit — not on re-litigating each line. Departing from an approved plan means updating ⛏️ In progress in the same change.

## Closing the loop

Production issues re-enter as a `TODO.md` item or a design-document update, not an off-process hotfix. Every incident that ships a fix earns a permanent regression test.

## Starting a new project

The kickoff for a brand-new, empty project:

1. **Brainstorm before planning.** Turn the first ask into something concrete (a brainstorming skill such as `superpowers:brainstorming` if available): scope, users, constraints, what success looks like.
2. **Ask every real decision with `AskUserQuestion`** — core's profile (language, project type) plus: MVP scope, real constraints (deadline, systems to integrate, data sensitivity), and anywhere the project should deviate from SDSI. The deploy target is asked by `sdsi:deploy`.
3. **Write `docs/design/INTENT.md`** from the brainstorm and decisions; let the human correct it.
4. **Write `docs/design/SPEC.md`** against SDSI and the project's constraints.
5. **Scaffold the full skeleton before any real logic** — explicitly, not organically:
   - Root: `README.md`, `.gitignore`, `.gitattributes` — and nothing else loose at the root (core §3).
   - `.claude/CLAUDE.md` (with the SDSI profile).
   - `meta/` with `TODO.md`, `CHANGELOG.md` (intro plus an empty Unreleased), and `VERSION` (`0.1.0`).
   - The source layout, following the language's and framework's conventions within core §3's invariants.
   - `tests/`, `config/`, `docs/`, `scripts/`.
   - **The release chain:** copy it from this plugin and wire it — `sdsi:versioning`, "Installing the release chain".
   - Commit the skeleton on its own, before feature work.
   - Once the skeleton exists, it's worth scanning it for the MCP servers, skills, and hooks suited to this stack (e.g. the `claude-code-setup` plugin) rather than guessing before anything exists.
6. **`docs/design/PLAN.md`, then build** — the first feature's steps in ⛏️ In progress.

## Upkeep

The lines `sdsi:upkeep` installs in the project's `.claude/rules/sdsi.md`:

- Before code for a new feature or a change in behavior — from `meta/TODO.md` or a prompt → update `docs/design/` first (`INTENT.md` if the why changes, `SPEC.md`, then `PLAN.md`'s ⛏️ In progress) and wait for approval of ⛏️ In progress (`sdsi:workflow`)
- Before calling a change done → run the project's tests, linter, and type checker, plus the check that proves the change itself, and show the result (`sdsi:workflow`)
- When a change is done → merge its ⛏️ In progress steps into `PLAN.md` and set the section back to `(none)` (`sdsi:workflow`)

## Review checklist

No `.claude/CLAUDE.md`, or one without an SDSI profile · a file loose at the root other than `README.md` and the ones core §3 allows · a deviation from SDSI used in the code but not written in `CLAUDE.md` · a missing `docs/design/INTENT.md`, `SPEC.md`, or `PLAN.md` · a feature in the code the design documents don't describe, or one they describe that's gone · a non-functional requirement that can't be checked · a non-trivial change with no approved ⛏️ In progress · ⛏️ In progress left holding a finished change · a per-change design file kept beside the documents · a bug fix without a regression test · a mistake that recurs and isn't in `CLAUDE.md` · an empty project scaffolded without the release chain · a plan step too big to verify in one session · a plan step resting on an assumption it never checks, with no STOP condition · a function, type, or key changed or removed without its callers read · a change to a hook, script, lint/type config, or skill with no proof the guardrail still fires · lint or type-check not part of the verification.
