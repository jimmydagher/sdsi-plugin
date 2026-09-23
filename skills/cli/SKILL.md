---
name: cli
description: >
  SDSI project type for command-line tools — owns the source layout and
  entry point of a tool meant to be run and reused: command/subcommand
  design through a registry, the sanctioned flag > env > file > default
  config precedence, stdout vs stderr, exit codes, machine-readable output
  modes, safe confirmation for destructive actions, packaging, and testing
  the CLI surface. Silent unless the SDSI profile's project type is cli, or
  it's invoked by name. Reads sdsi:core first. Triggers on "/sdsi:cli",
  "command-line tool", "build a CLI".
---

# SDSI: Command-Line Tool Project

Before anything else, read `../core/SKILL.md` and run its steps. This skill
owns the source layout, entry point, and design shape for a command-line
tool. Topics still apply in full; this skill only adds what's true because
the project is a CLI.

**This one is a draft** — written generically, not yet distilled from a real
project the way `sdsi:web` and `sdsi:mw` were. Apply it, and correct it from
the first real CLI project that disagrees.

## Layout

```
src/
├── <entry point>   # no logic — parses arguments, dispatches the command, exits with its code
├── helpers/        # the one home for shared code
├── integrations/   # one module per external system the tool talks to
└── commands/       # one callable per subcommand + the registry mapping name → handler
```

- **Dependencies point one way:** `helpers` ← `integrations` ← `commands` ←
  entry point.
- **The registry asserts completeness at startup** — an unwired subcommand
  fails immediately, not the first time someone runs it.

## Commands

- **One callable per subcommand.** Group by the noun they act on (`tool user
  add`, `tool user list`) once the tool grows past a handful — not before
  there's a second subcommand that needs the grouping.
- **Help text is documentation** and is updated in the same change as the
  flag it describes (`sdsi:docs`).
- **Flags are the public interface.** A renamed or removed flag breaks
  callers — a MAJOR bump (`sdsi:versioning`).
- **No command given is an error**, not a silent no-op (`sdsi:errors`).

## Configuration precedence — a sanctioned deviation from sdsi:config

A flag *is* how a user overrides a default for one invocation, so a CLI is the
one place a setting may come from more than the config file:

```
explicit flag  >  environment variable  >  config file  >  built-in default
```

- **Say which layer won** — a `--show-config` or verbose mode reports where
  each effective value came from; a stale environment variable silently
  overriding a config value is a common, confusing bug.
- **An environment variable is for what persists across invocations** (an
  endpoint, a default profile); a flag is for what the user decides now.
- **Secrets never come from a flag** — they'd be visible in shell history and
  process listings (`sdsi:secrets`).

## Output

- **stdout is the tool's output; stderr is everything else** — progress,
  warnings, diagnostics. A caller piping stdout never filters out noise.
- **Color is decided once, from whether stdout is an interactive terminal**
  (`sdsi:logging`); piped output is plain unless the user forces it
  (`--color=always`).
- **Exit codes are documented and stable**: `0` for success, a small set of
  distinct codes for the outcome classes in `sdsi:errors` — kept stable
  across releases like flag names.
- **A machine-readable mode (`--json`) for any command a script might wrap.**
  Scripts never parse the human-readable text; the machine-readable shape is
  a versioned contract.
- **Destructive actions confirm safely:** `--yes`/`--force` for scripted use;
  an interactive prompt only when stdin is a real terminal — never a prompt
  that blocks CI forever.

## Packaging

- **`--version` prints `VERSION`** — never a second hand-maintained string
  (`sdsi:versioning`).
- **Keep the dependency tree especially small** — it has to coexist with
  whatever is already installed where the tool lands (`sdsi:dependencies`).
- **The distribution shape is chosen with `sdsi:deploy`** (usually
  "distributed package").

## Testing a CLI

- **Test each command's callable directly**, not by shelling out; reserve a
  few end-to-end subprocess tests for the packaged entry point itself.
- **Snapshot `--help` and machine-readable output** so an unexpected change
  fails loudly.
- **An argument-wiring test must name what it catches** (a flag silently
  ignored, a subcommand unregistered) (`sdsi:testing`).

## Review checklist

Logic in the entry point · a subcommand missing from the registry · a
renamed flag shipped as MINOR/PATCH · output data on stderr or noise on
stdout · undocumented or unstable exit codes · a script-facing command with
no machine-readable mode · a prompt that can block CI · a secret accepted as
a flag · `--version` not reading `VERSION`.
