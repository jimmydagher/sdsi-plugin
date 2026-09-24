---
name: workflow
description: >
  SDSI's development workflow — plan before code, the INTENT/SPEC/PLAN
  artifact chain, verifying before calling anything done, flagging scope
  growth, stage gates, closing the loop on production issues, keeping
  institutional knowledge in CLAUDE.md, and the kickoff sequence for a
  brand-new project. Use when starting a new project, planning a feature,
  or deciding how a change should move from idea to commit. Reads sdsi:core
  first. Triggers on "/sdsi:workflow", "start a new project", "how should
  we plan this".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Workflow

Before anything else, read `../core/SKILL.md` and run its steps.

Adapted from Anthropic's AI-Native SDLC playbook
([claude.com/blog/the-ai-native-sdlc-playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)).
Applies in full on new projects; on established code, adopt what fits.

## The artifact chain

Every stage ends by committing a markdown artifact the next stage reads. The
chain is the audit trail — what was asked, decided, built, and found — and
it's what makes core's "no assumptions" and "double-check your work"
enforceable.

| Stage | Artifact | Captures |
|---|---|---|
| Plan | `INTENT.md` | The problem in the requester's words — what, why, constraints. Open questions stay open here. |
| Design | `SPEC.md` | Requirements and design, checked against SDSI as it's written. |
| Build | `PLAN.md` | Which files change, in what order, and what proves it worked — reviewed before code. |
| Build | the diff + tests | The implementation and what verifies it (`sdsi:testing`). |
| Deploy | the PR + review findings | What was checked, by whom, what was decided. |
| Maintain | a new `INTENT.md` | Anything production surfaces re-enters at Plan. |

- **A historical artifact is left alone when later work changes what it
  describes** — it's a permanent record, not a living reference. **The
  exception:** when it's actively misleading (a superseded direction still
  written as current), update it or mark it superseded — and flag that
  judgment call explicitly each time.
- **On an established codebase** a per-change folder of three files often
  goes unread. It's fine to land each stage elsewhere — intent in the commit
  body or a `TODO.md` item, a standing design decision in `CLAUDE.md`, the
  plan in the change itself — as long as every stage lands somewhere
  version-controlled and the plan existed before the code.

## Plan before code, always

Nothing is implemented from an unstated plan. Beyond a trivial fix:
`INTENT.md` → `SPEC.md` → `PLAN.md`, then code. It scales down — a one-line
fix doesn't need three files, but it still needs a stated reason, and if it
isn't self-evidently safe, a one-sentence plan beats none.

## Reference a system by reading it, not recalling it

"Do it the way X does it" means reading X's actual implementation before
designing. Reading it in full may reveal that X never solved the exact
problem in front of you — bring that back before designing, don't discover
it mid-implementation.

## Verify before calling anything done

Every task has a way to check itself, and the check runs before the work is
reported done. For a bug fix: write the failing test, confirm it fails for
the expected reason, then make it pass without touching the test.

## Institutional knowledge lives in files

A project's conventions, gotchas, and repeated corrections live in its
`CLAUDE.md` — under a page, updated the moment a mistake happens twice. SDSI
is the standard; `CLAUDE.md` holds only what's particular to this project
(including its `## SDSI profile` and any deliberate deviations). Anything
that must be applied consistently from one place is a candidate for a
skill, not a paragraph someone has to remember.

## Review runs in both directions

A change is reviewed against SDSI, the accepted `SPEC.md`, and the accepted
`PLAN.md`. Findings carry a severity; only ones that break behavior, leak
data, or breach a stated policy block. The same mistake caught twice goes
into `CLAUDE.md`.

## Scope changes get flagged, not absorbed

When a request grows past what was understood — a small fix that turns out
to touch secret handling, a decision that starts affecting every deploy
target — stop, say so, and get a fresh, explicitly scoped decision before
designing further. A behavior that's someone else's contract (a flag, an API
field, an output format) doesn't get quietly widened or narrowed while
fixing something next to it.

## Stage gates

Human judgment concentrates at the gates — approving `INTENT.md`, accepting
`SPEC.md`, approving `PLAN.md`, approving the code for commit — not on
re-litigating each line. Departing from an approved plan means updating
`PLAN.md` in the same change.

## Closing the loop

Production issues re-enter as a new `INTENT.md` (or `TODO.md` item), not an
off-process hotfix. Every incident that ships a fix earns a permanent
regression test.

## Starting a new project

The kickoff for a brand-new, empty project:

1. **Brainstorm before planning.** Turn the first ask into something
   concrete (a brainstorming skill such as `superpowers:brainstorming` if
   available): scope, users, constraints, what success looks like.
2. **Ask every real decision with `AskUserQuestion`** — core's profile
   (language, project type) plus: MVP scope, real constraints (deadline,
   systems to integrate, data sensitivity), and anywhere the project should
   deviate from SDSI. The deploy target is asked by `sdsi:deploy`.
3. **Write `INTENT.md`** from the brainstorm and decisions; let the human
   correct it.
4. **Write `SPEC.md`** against SDSI and the project's constraints.
5. **Scaffold the full skeleton before any real logic** — explicitly, not
   organically:
   - Root: `README.md`, `CLAUDE.md` (with the SDSI profile), `TODO.md`,
     `CHANGELOG.md` (intro plus an empty Unreleased), `VERSION` (`0.1.0`),
     `.gitignore`, `.gitattributes` — and nothing else loose at the root.
   - The source layout, following the language's and framework's
     conventions within core §3's invariants.
   - `tests/`, `config/`, `docs/`, `scripts/`.
   - **The release chain:** copy `scripts/git/{pre-commit,commit-msg}` and
     `scripts/python/release.py` from this plugin into the project and run
     `git config core.hooksPath scripts/git` (`sdsi:versioning`).
   - Commit the skeleton on its own, before feature work.
   - Once the skeleton exists, it's worth scanning it for the MCP servers,
     skills, and hooks suited to this stack (e.g. the `claude-code-setup`
     plugin) rather than guessing before anything exists.
6. **`PLAN.md`, then build.**

## Review checklist

No `CLAUDE.md`, or one without an SDSI profile · a deviation from SDSI used
in the code but not written in `CLAUDE.md` · a non-trivial change with no
recorded intent or plan · a historical planning artifact rewritten to match
new reality (or a superseded one still read as current) · a bug fix without
a regression test · a mistake that recurs and isn't in `CLAUDE.md` · an
empty project scaffolded without the release chain.
