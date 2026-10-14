---
name: standards
description: >
  SDSI's coding standards, language-neutral — naming and casing, no magic
  strings (constants and enums), comments and docstrings, reuse over
  reimplementation (DRY), dead-code cleanup sweeps (proof before deleting,
  never deleting externally called code without asking), SOLID applied
  practically, and strict typing
  (input validation and every other security rule live in sdsi:security). Use when writing or reviewing
  code for readability and consistency, or when asked to apply coding
  standards to a project. Reads sdsi:core first and applies each rule in the
  project language's own idioms. Triggers on "/sdsi:standards", "coding
  standards", "clean up this code".
argument-hint: "[--review|--apply] [path|branch]"
---

# SDSI: Coding Standards

Before anything else, read `../core/SKILL.md` and run its steps. Every rule here is applied in the project language's own idioms (core §1, Step 2).

## Naming

- **Spell names in full.** `response`, not `r`; `error`, not `e`. Loop indices and well-known math symbols are the only short names.
- **Follow the language's casing convention** for functions, variables, types, constants, and files — consistently, everywhere. Uppercase constant style is reserved for true constants.
- **Types/classes are as short as stays unambiguous.** Prefer one clear word over a compound; keep a qualifier only when dropping it would collide with or blur against something else in the codebase (`LogFile` because `Log` is the logger; `HttpStatus` because `Status` is the run outcome).
- **Modules/files are named for the capability they own** (`logs`, `secrets`, `config`), not forced to mirror one class name.
- **Folders:** `kebab-case` unless the language requires otherwise (a package name that must be a valid identifier, for instance).
- **Markdown:** the fixed-name project documents are `UPPERCASE.md` wherever they live (`README.md`, `CLAUDE.md`, `CHANGELOG.md`, `TODO.md`); every other Markdown file, including the rest of `docs/`, is `lowercase-kebab-case.md`.
- **Config files:** YAML, unless the project type or language gives a strong reason otherwise (write that reason in `CLAUDE.md`).
- **Mark internal members as internal** using the language's mechanism (a leading underscore, `private`, unexported names).

## No magic strings — constants and enums

Any value used for a comparison, dispatch, lookup key, or config/environment name is a named member of an enum or constants module, never a bare literal repeated at each call site. A typo in a member name fails loudly; a typo in a bare string silently takes the wrong branch.

- **A closed set of values that gets compared or dispatched on** (statuses, task names, environment names) → the language's enum construct, ideally a string-valued one.
- **Formats, templates, and defaults that are only read** → a plain group of named constants.
- **The one exception:** a literal specific to one integration and used nowhere else (an endpoint path, a header name) lives as a constant on that integration's own type — centralizing it only makes it harder to find.
- **Never resolve a variable by string name** from a dynamic namespace (reflection on locals/globals and similar); bind it directly.

## Comments and docstrings

- **Every module opens with a short header comment/docstring**: what it's for and why it's separate from its neighbors.
- **Every public function/method is documented** in the language's standard doc format, covering: a one-line summary, each input (type and meaning), and the output. Note what it raises/returns on failure when that isn't obvious.
- **Comments explain why, not what.** A comment earns its place by recording a decision, constraint, or trap the code can't show.
- **A deliberate shortcut is marked `shortcut:`** with a comment saying what was skipped and when to revisit it (`shortcut: linear scan, fine under ~1k rows`). Each one also gets a line in `meta/TODO.md` (`sdsi:docs`), the one list of deferred work. A project may rename the tag in its `CLAUDE.md`.

## Reuse over reimplementation

Before writing something, check whether the shared layer already provides it (an HTTP client, a secrets accessor, a cache, a logger, file I/O). If a shared helper doesn't quite fit, **extend it for everyone** rather than working around it locally — a capability implemented twice will eventually disagree with itself.

One source of truth for logic, constants, types, and validation rules. Refactor into a shared home the **second** time the same semantic rule appears — not preemptively, and not for code that merely looks similar but means something different (coincidental duplication stays).

## Dead code and cleanup sweeps

An AI agent treats dead code as a live pattern and copies it into new work, and every unused line is context it has to read. So unused and duplicated code gets removed, but only in a cleanup sweep, as a change of its own (core §2).

- **Start from a checkpoint.** The working tree is clean and the human has committed before anything is deleted, so one revert undoes the whole sweep.
- **List before deleting, with proof.** Every unreferenced file, function, export, type, and constant is listed with the evidence that nothing uses it (a search with no callers, or the language's unused-code analyzer). Nothing is deleted until the human approves the list (core §2, "Confirm before anything destructive or bulk").
- **Merge duplicates.** The same rule implemented in two places becomes one shared function, and every caller moves to it (Reuse over reimplementation, above). Otherwise a bug fixed in one copy stays live in the other.
- **Inventory the entry points.** List every route, page, server action, command, and scheduled job with what calls each. Flag any that nothing calls: removing a UI doesn't remove the endpoint behind it (`sdsi:security`).
- **Never delete code called from outside the codebase without asking.** That means webhooks, scheduled jobs, auth callbacks, queue consumers, plugin hooks, and anything invoked through configuration or reflection. A reference search can't see their callers, so they always look unused. The list marks them as external, not dead.
- **Cadence.** Run a simplification pass over the changed code when a feature is finished (Claude Code's `/simplify`), and a full sweep of the codebase on a regular schedule (weekly on an active project).

## SOLID, applied practically

- **Single responsibility.** A type or module has one reason to change; if describing it needs "and", it's probably two things.
- **Open/closed.** Add a case by adding an implementation (a new class, a new registered handler), not by growing an `if`/`switch` chain keyed on type. A name→handler registry asserts completeness at startup, so a missed wiring step fails immediately, not at first use.
- **Liskov substitution.** A subtype honors its parent's contract — same input expectations, same category of outcome.
- **Interface segregation.** Size an interface to what the caller needs.
- **Dependency inversion.** Infrastructure (HTTP client, database connection, secrets accessor) is passed in, never constructed inside business logic.

## Strict typing

- **Every public signature is fully typed**, using the language's type system or its standard type-annotation layer. Types are load-bearing, not decorative; run the language's type checker where one exists.
- **No blanket suppression** (an unexplained ignore comment, a cast to the "any" type) in place of fixing the mismatch. A justified suppression says why, next to the line.
- **Untrusted input is validated once, at the boundary** (`sdsi:security`). Once validated, it's typed like any other value.
- **Give easily confused primitives their own small type** (an ID, a money amount, a currency code) so they can't be passed in the wrong order.

## Upkeep

The lines `sdsi:upkeep` installs in the project's `.claude/rules/sdsi.md`:

- Finishing a feature → run a simplification pass over the code it changed and remove what it made unused; leave pre-existing dead code for a cleanup sweep of its own (`sdsi:standards`)
- Taking a deliberate shortcut → mark it with a `shortcut:` comment saying when to revisit it, and add it to `meta/TODO.md` (`sdsi:standards`)
- Before deleting code that looks unused → have the human commit first, list each item with proof that nothing calls it, and wait for approval; never delete a webhook, scheduled job, auth callback, or anything else called from outside the codebase without asking (`sdsi:standards`)

## Review checklist

Single-letter names · a repeated bare string used for dispatch or lookup · a public function without a doc comment · a comment that restates the code · the same rule implemented twice · a type-keyed `if`/`switch` chain that keeps growing · infrastructure constructed inside business logic · an untyped public signature or blanket suppression · code far longer than the problem needs · something built that the codebase, standard library, or platform already provides · a deliberate shortcut with no `shortcut:` comment or TODO line · an import, variable, or function the change made unused and left behind · pre-existing dead code deleted in an unrelated change (core §2) · unused code that has piled up with no cleanup sweep · a sweep that deleted code without a listed proof and approval, or from an uncommitted tree · an externally invoked entry point (webhook, scheduled job, auth callback) deleted as unused · a route, page, or job that nothing calls left in place unflagged.
