---
name: config
description: >
  SDSI's configuration standard, language-neutral — one default file plus
  per-environment overrides, no defaults in code, schema validation of the
  merged config before any work starts, a validate-config command, derived
  vs configured values, the narrow role of environment variables, and
  placeholder conventions. Use when adding a setting, building a config
  loader, or reviewing how a project is configured. Reads sdsi:core first.
  Triggers on "/sdsi:config", "configuration", "add a setting".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Configuration

Before anything else, read `../core/SKILL.md` and run its steps.

## Rules

- **All tuneables live in `config/default.yaml`**, with per-environment
  differences only in `config/override/<env>.yaml`, deep-merged over the
  default at load time. An override states only what differs.
- **No default values live in code.** A setting has exactly one source of
  truth — the config file — and reading a missing key is an error, not a
  silent fallback.
- **The merged config is validated against a schema before any work
  starts** — every key's type, allowed values, and range declared up front.
  A missing, null, mistyped, or out-of-range value stops the run and reports
  **every** problem at once.
- **Provide a validate-config command/task** that checks configuration and
  credential access without doing real work — safe to run as a deploy
  pre-flight.
- **Derived values are not configured values.** A few values come from the
  run's own context — which environment override was applied, how the run
  was invoked, which version of the code is running. Derive them, let them
  override anything the file says, and never keep two places that could
  disagree. They still appear in the validated schema, so validate-config
  reports what they resolved to.
- **Never derive one independently toggleable setting from another**, even
  when they usually move together. State each explicitly in every override;
  a default that's safe in one deployment and breaks another surfaces late.
- **Environment variables are only for wiring that must exist before config
  can load** — the config directory, which environment this is, mount paths
  the platform controls. Keep that list explicit near the loader; every
  addition deserves a second look, because it bypasses the schema.
- **Business logic never reads the environment directly** as a substitute for
  config — that's a second, silently competing source of truth.
- **Placeholders:** a key that must be supplied by an override is written as
  `<not configured>` in the default file (never a plausible fake value); a
  key computed at load time is written as `<set at runtime>`.
- **Config files hold non-secret settings only.** A secret's *name* can live
  in config; its value never does (`sdsi:secrets`).

**Adding a setting is three steps, in this order:** add the config key → add
its named constant (`sdsi:standards`) → add its schema entry. Skipping the
schema leaves it unvalidated.

## Where a project type differs

A project type may legitimately refine these rules — a CLI allows
per-invocation flag overrides; a website maps config into the framework's
settings module. That refinement lives in the project-type companion's
`## sdsi:config` section (`ref/<type>.md`, core §1 Step 2), not here.

## Review checklist

A default value in code · an environment read inside business logic · a
setting with no schema entry · validation that stops at the first error · a
secret value in a config file · a fake-but-plausible value in the default
file · two settings where one silently derives from the other · no
validate-config command.
