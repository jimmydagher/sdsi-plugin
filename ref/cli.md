# SDSI Companion — Command-Line Tool

For projects whose profile says **Project type: cli** — a tool meant to be run and reused, not a one-off script. Not a skill: `sdsi:core` §1 Step 2 reads this file when the project type is cli, and a running skill applies **only the section headed with its own name**. A skill with no section here has no CLI-specific additions; it proceeds on its own rules.

Language-neutral: apply each rule through the project language's own argument parser and packaging.

**A seed, not a finished standard** — written generically, not yet distilled from a real CLI project. Correct it from the first one that disagrees.

## sdsi:standards

- **One callable per command, dispatched from a registry** that asserts completeness at startup — an unwired command fails immediately, not the first time someone runs it.
- **Group commands by the noun they act on** (`tool user add`, `tool user list`) once there are more than a handful — not before a second command needs the grouping.
- **Destructive actions confirm safely:** a `--yes`/`--force` flag for scripted use, and an interactive prompt only when stdin is a real terminal — never a prompt that blocks CI forever.

## sdsi:config

- **A sanctioned deviation from `sdsi:config`'s single source of truth.** A flag is how a user overrides a default for one run, so precedence is:

  ```text
  explicit flag  >  environment variable  >  config file  >  built-in default
  ```

- **Say which layer won** — a `--show-config` or verbose mode reports where each effective value came from.
- **An environment variable is for what persists across runs** (an endpoint, a default profile); a flag is for what the user decides now.

## sdsi:secrets

- **A secret is never accepted as a flag** — it would show up in shell history and process listings. Read it from the secrets store, or from an environment variable or file the user points to.

## sdsi:logging

- **stdout is the tool's output; stderr is everything else** — progress, warnings, diagnostics. A caller piping stdout never has to filter noise.
- **Color is decided once, from whether stdout is an interactive terminal**; piped output is plain unless the user forces it (`--color=always`).

## sdsi:errors

- **Exit codes are documented and stable** — `0` for success and a distinct code for each outcome class in `sdsi:errors`' table, listed in the help text or README and kept stable like flag names.
- **No command given is an invalid-input error** with usage on stderr, never a silent success.
- **A machine-readable mode (`--json`) for any command a script might wrap**, including its errors. Scripts never parse the human-readable text; the machine-readable shape is a versioned contract.

## sdsi:testing

- **Test each command's callable directly**; keep a few end-to-end tests that run the packaged entry point as a subprocess.
- **Snapshot `--help` and machine-readable output** so an unexpected change fails loudly.
- **An argument-wiring test names what it catches** — a flag silently ignored, a command unregistered.

## sdsi:dependencies

- **Keep the dependency tree especially small** — the tool has to coexist with whatever is already installed where it lands.

## sdsi:docs

- **Help text is documentation** — updated in the same change as the flag or command it describes.

## sdsi:versioning

- **`--version` prints `VERSION`**, never a second hand-kept string.
- **Flags, commands, exit codes, and the machine-readable shape are the public interface.** Renaming or removing any of them is a MAJOR bump.

## sdsi:deploy

- **The deploy target is usually "distributed package"**; decide the shape — a package-manager install, a self-contained binary, or an image — and write it down.
