---
name: logging
description: >
  SDSI's logging and output standard — one central logger that every log
  line funnels through, standard levels with clear jobs, a cheap
  would-this-be-written check, a single fan-out point for multiple
  destinations, deciding color once at startup, non-blocking file writes
  with a bounded shutdown drain, and messages that arrive after the log
  closes. Use when adding logging to a project, reviewing log output, or
  replacing ad-hoc print statements. Reads sdsi:core first. Triggers on
  "/sdsi:logging", "logging", "add logs".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Logging & Output

Before anything else, read `../core/SKILL.md` and run its steps.

## Rules

- **One central logger.** Structured logging through one logger type, never
  bare console printing for anything that matters. One method actually
  produces a log line; the level shorthands (`info`, `warning`, …) all funnel
  through it, so there's one answer to "was this written, and what did it
  look like". Use the language's standard logging facility underneath if it
  has a good one — the rule is the single front door, not a custom
  implementation.
- **Standard levels, each with one job:**

  | Level | Use for |
  |---|---|
  | `DEBUG` | Dev-only detail; hidden in deployed environments |
  | `INFO` | Normal progress — what the run is doing now |
  | `WARNING` | Something's wrong; the run continues |
  | `ERROR` | One unit of work failed; the run may complete others |
  | `CRITICAL` | The run can't be trusted or can't continue — someone must act tonight |

- **The level is a floor**, set from config (`sdsi:config`). Make the
  "would this even be written?" check public and cheap, so an expensive debug
  line isn't built only to be discarded.
- **Many destinations, one write.** When output goes to several places at
  once (console, file, a response payload), write through a single fan-out
  point rather than duplicating calls per destination.
- **Decide color/styling once, at startup, for the whole run** — from the
  destination (interactive terminal: yes; file or structured output: no).
  Every destination gets identical content, and a log file never gets
  escape codes.
- **File writes never block the work.** Write on a background worker; bound
  how long shutdown waits for it to drain, and keep that bound under the
  platform's stop-to-kill grace period (`sdsi:concurrency`).
- **Say where late messages go.** A message discovered after the log file
  closes can only reach the console — state that in code, don't let it
  vanish silently.
- **Never log a secret value** (`sdsi:secrets`). Name the secret; never print
  it.

## Review checklist

Console printing used for real diagnostics · more than one logger or logging
path · levels used inconsistently (errors at `INFO`, noise at `WARNING`) ·
an expensive debug message built unconditionally · per-line color decisions
or escape codes in a log file · synchronous file writes on the hot path · an
unbounded shutdown drain · a secret value in a log line.
