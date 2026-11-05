# SDSI Companion — Command-Line Tool

For projects whose profile lists **cli** in `Companions`: a tool meant to be run and reused, not a one-off script. This is not a skill. `sdsi:core` §1 Step 2 reads this file when the profile names it, and a running skill applies **only the section headed with its own name**, within the scope the profile gives (the whole project, or only the command surface of a library or web app). A skill with no section here has no CLI-specific additions and proceeds on its own rules.

Language- and framework-neutral: apply each rule through the project language's own argument parser and packaging. Parser-specific lessons belong in the project's own `CLAUDE.md`, not here.

**A researched base, checked in 2026-11** against the widely shared CLI conventions (POSIX utility syntax, the GNU coding standards, the Command Line Interface Guidelines, NO_COLOR, XDG) and the documented behavior of mature tools (gh, kubectl, the AWS CLI, terraform, npm, cargo, go). It hasn't been distilled from a real CLI project of ours yet. Correct it from the first one that disagrees.

## sdsi:workflow

- **The command surface is designed in `SPEC.md` before code:** every command, flag, positional argument, output shape, and exit code. Once scripts depend on a CLI it is hard to change, so a later rename costs a MAJOR bump (`sdsi:versioning` below).

## sdsi:standards

- **The command grammar is regular.** One callable per command, dispatched from a registry. Group commands by the noun they act on (`tool user add`, `tool user list`) once there are more than a handful, not before a second command needs the grouping; a group name on its own is an area, not an action: it shows that group's help and exits as invalid input. Use the same verb for the same action across every noun. No catch-all command and no implicit prefix abbreviation (`tool inst` for `tool install`) — either one blocks adding a command later without breaking someone's script.
- **Follow the platform's argument syntax through a real parser, never hand-rolled `argv` splitting.** Every option has a long form, and a one-letter alias only if it's used often. `--` ends option parsing. `-` as a file operand means stdin or stdout. The parser also gives you usage errors, help, and completion for free. Names are lowercase and kebab-case (`--dry-run`, `user-group`); option names are nouns and leaf commands are verbs; plural or singular is consistent across options that take several values.
- **Conventional flag names keep their conventional meaning.** The long names `--help`, `--version`, `--quiet`, `--verbose`, `--dry-run`, `--force`, `--json`, `--no-input`, and `--no-color` are never used for anything else, nor are `-h` and `-q`. Other short aliases (`-v`, `-f`, `-n`, `-o`) mean different things across real tools, so give one only when this tool's users expect it, and never with a meaning that contradicts its long name. Prefer flags to positional arguments once a command takes more than one kind of value; several positionals of the same kind (`tool rm a b c`) are fine, and two different things by position (`cp src dest`) only where the convention is universal.
- **Changes are safe to make.** A destructive action takes `--yes`/`--force` for scripted use and prompts only when stdin is a real terminal — a prompt never blocks CI. `--no-input` turns off every prompt, and a missing answer then fails as invalid input naming the flag that supplies it. A severe, hard-to-undo action asks for the target's name (`--confirm=<name>`), not just yes. A command that changes state non-trivially supports `--dry-run`, so you can see what it would do before it does it.

## sdsi:config

- **A sanctioned deviation from `sdsi:config`'s single source of truth.** A flag is how a user overrides a value for one run, so precedence is:

  ```text
  explicit flag  >  environment variable  >  project config file  >  user config file  >  system config file  >  packaged default file
  ```

  The last layer is `sdsi:config`'s default file shipped inside the package, never a default written in code. Every layer is merged first, and then the merged result is schema-validated once.
- **Say which layer won:** a `--show-config` or verbose mode reports where each effective value came from.
- **Each layer has its job:** a config file holds what persists across runs, an environment variable what varies with the context the tool runs in (a CI job, a shell session), and a flag what the user decides now. The tool's own variables share one uppercase prefix (`TOOL_ENDPOINT`), and each one is documented.
- **User files go where the platform expects them:** the XDG base directories on Linux and similar systems (`$XDG_CONFIG_HOME`, defaulting to `~/.config/<tool>`, plus the data, state, and cache homes for each kind of file), and the platform's own locations elsewhere. Never a new dotfile in the home directory. Ignore a relative XDG path, and create missing directories as user-only.
- **Respect the standard environment variables for capabilities the tool has:** `NO_COLOR`, `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`, `TMPDIR`, `PAGER`, `EDITOR`, `HOME`. This is a second sanctioned deviation from `sdsi:config`'s rule about environment variables, because users set these once for every tool they use.
- **Never edit a file the tool doesn't own** (a shell profile, another tool's config) without asking first.

## sdsi:security

- **A secret is never accepted as a flag** — it would show up in shell history and process listings. The tool accepts one, in this order: the platform's credential store or a credential helper; a file or stdin the user points to (`--token-file <path>`, or `-`), including a `TOOL_<NAME>_FILE` variable holding a path; and an environment variable (`TOOL_TOKEN`), documented as the input for headless and CI runs — never the first thing the docs show an interactive user. **A sanctioned deviation from `sdsi:security`'s "environment variable as a last resort":** the tool runs in its caller's environment, not in a deployment the project controls, and a CI runner has no secrets store to offer it.
- **A secret from the environment is read once and contained:** never echoed, logged, shown by `--show-config`, written to a config file, or passed into the environment of a subprocess the tool starts unless that subprocess needs it.
- **Interactive secret input is never echoed**, and a prompt for it only appears when stdin is a terminal.
- **A credential the tool caches** (a login token) lives in the platform's credential store, or else in a user-only file under the config or state directory. Never in the config file, and never readable by other users. Falling back to a plain file because no store is available is said to the user when it happens.

## sdsi:logging

- **stdout is the tool's output; stderr is everything else:** progress, warnings, and diagnostics. A caller piping stdout never has to filter out noise.
- **Color is decided once, from whether stdout is an interactive terminal.** Piped output is plain unless the user forces it (`--color=always`). Color is also off when `NO_COLOR` is set to a non-empty value, when `TERM=dumb`, or with `--no-color`. An explicit flag overrides `NO_COLOR`. stderr's color is decided from stderr's own terminal check.
- **Terminal tricks only run on a terminal.** Spinners, progress bars, and cursor redraws only when stderr is a terminal; in a pipe or CI, report progress as occasional plain lines or not at all, and never redraw a line into a log file. Long output goes through a pager only when stdout is a terminal, honoring `PAGER`, with `--no-pager` to turn it off.
- **`-q` and `-v` set the logger's floor for this run** (a flag overriding the configured level). Quiet still prints errors. Verbose or debug detail (stack traces, timings, request details) is never shown by default.
- **What a person reads on the console is messages, not log records.** No timestamps or level labels on normal output. The full structured record goes to the log file or the verbose mode. Both still go through the one central logger, with a console format chosen at startup.
- **No usage data is sent anywhere without opt-in consent.** If the tool collects telemetry, the docs and the opt-in prompt say what it collects, why, and how long it's kept.

## sdsi:errors

- **Exit codes are documented, stable, and clear of the shell's.** `0` is success and each outcome class in `sdsi:errors`' table gets a distinct code, listed in the help text or README and kept as stable as flag names. `2` is the default usage error (Invalid input); a tool that diverges documents its own table. Never use `126`, `127`, or `128` and above for the tool's own outcomes — the shell uses them for "not executable", "not found", and "killed by signal N" — except `Interrupted`, which exits `128 + signal number` (130 for Ctrl-C) so a calling shell sees what really happened. Pick other custom codes from a small documented range (`64`–`113` is the traditional one). Don't adopt `sysexits` wholesale: its own maintainers have deprecated it.
- **A command whose answer can be "no" says so with its own code**, not a failure: no match, or differences found, exits `1`, as `grep` and `diff` do, and the command's real failures use a different code.
- **No command given is an invalid-input error** with usage on stderr, never a silent success. When the tool expects input on stdin and stdin is a terminal with nothing piped, show usage instead of waiting silently.
- **A machine-readable mode (`--json`) for any command a script might wrap.** Scripts never parse the human-readable text; the machine-readable shape is a versioned contract. stdout carries only success data and is empty on failure; the error goes to stderr — with `--json`, as one JSON object of a documented shape — and the exit code is the authority, so `tool --json | jq` never receives an error as data. The one exception is a command that is itself a stream of events (a build, a plan): its diagnostics are records in that stream, and it still exits non-zero.
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
- **The command registry asserts its completeness at startup, and a wiring test names what it catches:** a flag silently ignored, a command left unregistered. An unwired command then fails immediately instead of the first time someone runs it.
- **Assert the exit code of every outcome class** at least once through the subprocess path. A wrong exit code passes every assertion on stdout and breaks every script that wraps the tool.
- **Test the non-interactive path the way CI runs it:** stdout and stdin not a terminal, `NO_COLOR` set, `--no-input`. Assert no escape codes, no prompt, and nothing hanging. A tool that only works in a terminal breaks the first time it's scripted.
- **Run the subprocess tests on every operating system the tool ships for.** Paths, line endings, signals, and terminal detection differ between them.

## sdsi:optimize

- **Startup time is a budget.** `--help`, `--version`, and a usage error should feel instant, and anything else should show output within about a tenth of a second. Load each command's heavy dependencies only when that command runs (`sdsi:optimize`'s lazy loading, applied per command).

## sdsi:dependencies

- **Keep the dependency tree especially small.** The tool has to coexist with whatever is already installed where it lands.

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
- GitHub CLI, environment variables and exit codes — https://cli.github.com/manual/gh_help_environment, https://cli.github.com/manual/gh_help_exit-codes
- AWS CLI, environment variables and return codes — https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html, https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-returncodes.html
- Terraform, machine-readable UI — https://developer.hashicorp.com/terraform/internals/machine-readable-ui
- Cargo, JSON messages for external tools — https://doc.rust-lang.org/cargo/reference/external-tools.html
- npm/cli #5716, JSON errors on stdout reported as breaking — https://github.com/npm/cli/issues/5716
