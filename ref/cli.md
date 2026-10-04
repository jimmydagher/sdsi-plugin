# SDSI Companion — Command-Line Tool

For projects whose profile says **Project type: cli**: a tool meant to be run and reused, not a one-off script. This is not a skill. `sdsi:core` §1 Step 2 reads this file when the project type is cli, and a running skill applies **only the section headed with its own name**. A skill with no section here has no CLI-specific additions and proceeds on its own rules.

Language- and framework-neutral: apply each rule through the project language's own argument parser and packaging. Parser-specific lessons belong in the project's own `CLAUDE.md`, not here.

**A seed, not a finished standard.** It's built on the widely shared CLI conventions (POSIX utility syntax, the GNU coding standards, the Command Line Interface Guidelines, NO_COLOR, XDG) and has not yet been distilled from a real CLI project. Correct it from the first one that disagrees.

## sdsi:workflow

- **The command surface is designed in `SPEC.md` before code:** every command, flag, positional argument, output shape, and exit code. Once scripts depend on a CLI it is hard to change, so a later rename costs a MAJOR bump (`sdsi:versioning` below).

## sdsi:standards

- **One callable per command, dispatched from a registry** that asserts completeness at startup. An unwired command fails immediately instead of the first time someone runs it.
- **Group commands by the noun they act on** (`tool user add`, `tool user list`) once there are more than a handful, not before a second command needs the grouping. A group name on its own is an area, not an action: it shows that group's help and exits as invalid input. Use the same verb for the same action across every noun.
- **Follow the platform's argument syntax through a real parser, never hand-rolled `argv` splitting.** Every option has a long form, and a one-letter alias only if it's used often. `--` ends option parsing. `-` as a file operand means stdin or stdout. Options and their order work wherever the parser allows. The parser also gives you usage errors, help, and completion for free.
- **Names are lowercase and kebab-case** (`--dry-run`, `user-group`). Option names are nouns and leaf commands are verbs. Plural or singular is consistent across options that take several values.
- **Reuse the conventional flag names, never with another meaning:** `-h/--help`, `--version`, `-q/--quiet`, `-v/--verbose`, `-n/--dry-run`, `-f/--force`, `-o/--output`, `--json`, `--no-input`, `--no-color`. A user's muscle memory is part of the interface.
- **No catch-all command and no implicit prefix abbreviation** (`tool inst` for `tool install`). Either one blocks adding a command later without breaking someone's script.
- **Prefer flags to positional arguments** once a command takes more than one kind of value. Several positionals of the same kind (`tool rm a b c`) are fine. Two different things by position (`cp src dest`) are fine only when the convention is universal.
- **Destructive actions confirm safely:** a `--yes`/`--force` flag for scripted use, and an interactive prompt only when stdin is a real terminal. A prompt must never block CI forever. `--no-input` turns off every prompt, and a missing answer then fails as invalid input naming the flag that supplies it.
- **A command that changes state supports `--dry-run`** when the change is non-trivial, so you can see what it would do before it does it.

## sdsi:config

- **A sanctioned deviation from `sdsi:config`'s single source of truth.** A flag is how a user overrides a value for one run, so precedence is:

  ```text
  explicit flag  >  environment variable  >  project config file  >  user config file  >  system config file  >  packaged default file
  ```

  The last layer is `sdsi:config`'s default file shipped inside the package, never a default written in code. Every layer is merged first, and then the merged result is schema-validated once.
- **Say which layer won:** a `--show-config` or verbose mode reports where each effective value came from.
- **An environment variable is for what persists across runs** (an endpoint, a default profile). A flag is for what the user decides now. The tool's own variables share one uppercase prefix (`TOOL_ENDPOINT`), and each one is documented.
- **User files go where the platform expects them:** the XDG base directories on Linux and similar systems (`$XDG_CONFIG_HOME`, defaulting to `~/.config/<tool>`, plus the data, state, and cache homes for each kind of file), and the platform's own locations elsewhere. Never a new dotfile in the home directory. Ignore a relative XDG path, and create missing directories as user-only.
- **Respect the standard environment variables for capabilities the tool has:** `NO_COLOR`, `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`, `TMPDIR`, `PAGER`, `EDITOR`, `HOME`. This is a second sanctioned deviation from `sdsi:config`'s rule about environment variables, because users set these once for every tool they use.
- **Never edit a file the tool doesn't own** (a shell profile, another tool's config) without asking first.

## sdsi:secrets

- **A secret is never accepted as a flag.** It would show up in shell history and process listings. Read it from the secrets store, or from an environment variable or file the user points to.
- **Prefer a file or stdin to an environment variable** (`--token-file <path>`, or `-` for stdin). Environment variables are inherited by every child process and show up in crash dumps and container inspection. Never put a secret in the environment of a subprocess the tool starts unless that subprocess needs it.
- **Interactive secret input is never echoed**, and a prompt for it only appears when stdin is a terminal.
- **A credential the tool caches** (a login token) lives in the platform's credential store, or else in a user-only file under the config or state directory. Never in the config file, and never readable by other users.

## sdsi:logging

- **stdout is the tool's output; stderr is everything else:** progress, warnings, and diagnostics. A caller piping stdout never has to filter out noise.
- **Color is decided once, from whether stdout is an interactive terminal.** Piped output is plain unless the user forces it (`--color=always`). Color is also off when `NO_COLOR` is set to a non-empty value, when `TERM=dumb`, or with `--no-color`. An explicit flag overrides `NO_COLOR`. stderr's color is decided from stderr's own terminal check.
- **Spinners, progress bars, and cursor tricks only run when stderr is a terminal.** In a pipe or CI, report progress as occasional plain lines or not at all. Never redraw a line into a log file.
- **`-q` and `-v` set the logger's floor for this run** (a flag overriding the configured level). Quiet still prints errors. Verbose or debug detail (stack traces, timings, request details) is never shown by default.
- **What a person reads on the console is messages, not log records.** No timestamps or level labels on normal output. The full structured record goes to the log file or the verbose mode. Both still go through the one central logger, with a console format chosen at startup.
- **No usage data is sent anywhere without opt-in consent.** If the tool collects telemetry, the docs and the opt-in prompt say what it collects, why, and how long it's kept.

## sdsi:errors

- **Exit codes are documented and stable:** `0` for success and a distinct code for each outcome class in `sdsi:errors`' table. They're listed in the help text or README and kept as stable as flag names.
- **Choose codes that don't collide with what the shell reserves.** `2` is the conventional usage error (Invalid input). Never use `126`, `127`, or `128` and above for the tool's own outcomes, because the shell uses them for "not executable", "not found", and "killed by signal N". `Interrupted` exits `128 + signal number` (130 for Ctrl-C) so a calling shell sees what really happened. Pick any other custom codes from a small documented range (`64`–`113` is the traditional one). Don't adopt `sysexits` wholesale: its own maintainers have deprecated it.
- **No command given is an invalid-input error** with usage on stderr, never a silent success. When the tool expects input on stdin and stdin is a terminal with nothing piped, show usage instead of waiting silently.
- **A machine-readable mode (`--json`) for any command a script might wrap**, including its errors. Scripts never parse the human-readable text. The machine-readable shape is a versioned contract.
- **An expected error reads like an instruction, not a trace:** what failed, the value or file involved, and what to do next, on stderr. Put the most important line last, where the eye lands. The stack trace still goes to the log through the global handler, and to the console only in verbose mode.
- **An unexpected error tells the user how to report it:** where the full detail was written and where to file the bug. Never just a bare trace.
- **A closed output pipe is not a failure** (`tool list | head`). Exit quietly, the way the platform's own tools do, with no error message and no stack trace.

## sdsi:concurrency

- **Ctrl-C is answered immediately.** Say on stderr that the tool is stopping, run a bounded cleanup, and exit with the interrupted code. A second Ctrl-C skips the remaining cleanup and says what was left undone.
- **Design so being killed is survivable:** write to a temporary file and rename it into place, and expect the previous run to have left a lock or partial file behind. Detect and recover from it on the next start; never fail forever on a stale lock.
- **Plan for two copies running at once** against the same state (two terminals, a cron overlap). Either make that safe or take a lock and fail with a clear message naming the other run.

## sdsi:testing

- **Test each command's callable directly**, and keep a few end-to-end tests that run the packaged entry point as a subprocess.
- **Snapshot `--help` and machine-readable output** so an unexpected change fails loudly.
- **An argument-wiring test names what it catches:** a flag silently ignored, a command left unregistered.
- **Assert the exit code of every outcome class** at least once through the subprocess path. A wrong exit code passes every assertion on stdout and breaks every script that wraps the tool.
- **Test the non-interactive path the way CI runs it:** stdout and stdin not a terminal, `NO_COLOR` set, `--no-input`. Assert no escape codes, no prompt, and nothing hanging. A tool that only works in a terminal breaks the first time it's scripted.
- **Run the subprocess tests on every operating system the tool ships for.** Paths, line endings, signals, and terminal detection differ between them.

## sdsi:dependencies

- **Keep the dependency tree especially small.** The tool has to coexist with whatever is already installed where it lands.
- **Startup time is a budget.** `--help`, `--version`, and a usage error should feel instant, and anything else should show output within about a tenth of a second. Load each command's heavy dependencies only when that command runs (`sdsi:dependencies`' lazy loading, applied per command).

## sdsi:docs

- **Help text is documentation**, updated in the same change as the flag or command it describes.
- **`--help` (and `-h`, and `help <command>`) prints to stdout and exits `0`, ignoring every other argument.** It leads with a one-line description and an example, lists the most common flags first, and ends with where the full docs live and where to report a bug. A usage error prints a concise version to stderr instead.
- **The reference documentation and the shell completion scripts are generated from the parser's own definitions**, never hand-maintained next to it. A flag added in code then appears in `--help`, the reference page, and tab completion together.
- **The README covers installing, upgrading, and uninstalling**, and how to enable shell completion, with each command block naming the shell it runs in.

## sdsi:versioning

- **`--version` prints `VERSION`**, never a second hand-kept string. It goes to stdout as `<tool> <x.y.z>` on the first line, exits `0`, and ignores every other argument.
- **Flags, commands, exit codes, and the machine-readable shape are the public interface.** Renaming or removing any of them is a MAJOR bump.
- **The human-readable output is not the contract.** It can be reworded in a PATCH. That's why scripts are pointed to `--json`.
- **Deprecate before removing:** a deprecated flag or command keeps working for at least one MINOR release and prints a warning on stderr naming its replacement. The changelog entry says when it will go.

## sdsi:deploy

- **The deploy target is usually "distributed package".** Decide the shape (a package-manager install, a self-contained binary, or an image) and write it down.
- **Prefer a self-contained binary or the platform's own package manager**, so installing the tool doesn't mean first installing and managing a language runtime. Whatever the shape, uninstalling is one documented step that removes everything the tool installed.
- **The package installs the shell completion scripts** for the shells it supports, or the docs give the single command that does.
- **The command name is short, lowercase, easy to type, and doesn't shadow a common command** already on users' machines. Check before publishing, because a rename later is a MAJOR bump.

## Sources

- Command Line Interface Guidelines — https://clig.dev/
- POSIX.1-2024, Base Definitions, Chapter 12: Utility Conventions — https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap12.html
- GNU Coding Standards, --version — https://www.gnu.org/prep/standards/html_node/_002d_002dversion.html
- GNU Coding Standards, --help — https://www.gnu.org/prep/standards/html_node/_002d_002dhelp.html
- NO_COLOR — https://no-color.org/
- XDG Base Directory Specification — https://specifications.freedesktop.org/basedir/latest/
- Command-line design guidance for System.CommandLine (Microsoft Learn) — https://learn.microsoft.com/en-us/dotnet/standard/commandline/design-guidance
- sysexits(3), FreeBSD manual (deprecation note) — https://man.freebsd.org/cgi/man.cgi?query=sysexits&sektion=3
- Advanced Bash-Scripting Guide, Exit Codes With Special Meanings — https://tldp.org/LDP/abs/html/exitcodes.html
- 12 Factor CLI Apps (Jeff Dickey) — https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46
- hyperfine PR #932, handling a broken stdout pipe gracefully — https://github.com/sharkdp/hyperfine/pull/932
