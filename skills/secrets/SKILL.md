---
name: secrets
description: >
  SDSI's secrets and credentials standard — nothing sensitive in source,
  config, images, or history; a real secrets store read at runtime; the
  owner-purpose-kind naming convention; one store per environment; paired
  credentials; rotation and waiting out a mid-rotation secret; redaction of
  anything leaving the process; and how a workload authenticates to the
  store. Use when a project handles any credential, API key, token, or
  connection string. Reads sdsi:core first. Triggers on "/sdsi:secrets",
  "secrets", "credentials", "key vault".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Secrets & Credentials

Before anything else, read `../core/SKILL.md` and run its steps.

## Storing secrets

- **No credential, API key, connection string, or token appears in source
  control, config files, deployment templates, or the built artifact** — not
  even in commit history.
- **Use a real secrets store** (a cloud key vault, a secrets manager), read
  at runtime and held in memory only for the life of the process. Config
  holds only the secret's *name*.
- **Naming: `<owner>-<purpose>-<kind>`** — lowercase, hyphens, three parts,
  no exceptions (`payments-client-secret`, `reporting-database-pwd`).
  Purpose and kind are derivable from how the credential is used, so a name
  can't drift from what it belongs to.
- **One store per environment**, never the environment encoded in the
  secret's name — that's two places that can disagree, and invites
  copy-pasting a dev name into prod.
- **A paired credential that must always rotate together** (client id +
  secret) can be one delimited value — only when it truly must move
  atomically. Otherwise keep a non-sensitive half (a username) in config.
- **A local-dev fallback** (an environment variable) is for developers
  without store access only, and is **explicitly disabled in every deployed
  environment**, so an unreachable store fails loudly there.

## Rotation

- **Disable old → change at the source → set new.** Disabling first means
  nothing can authenticate with a value already known wrong; setting a new
  value creates a new enabled version every future read picks up.
- **Wait out a secret caught mid-rotation instead of failing on the spot.**
  Tell "this version is disabled" apart from "this identity may not read it"
  using the store's actual error detail (not just the HTTP status — both
  often share one). Poll the first on a short interval up to a bounded
  ceiling, then fail loudly naming the secret and the wait — never fall back
  to a stale in-memory copy. A caller that must answer immediately (a deploy
  pre-flight) opts out of the wait explicitly.
- **Test the rotation wait against a real store at least once**, on demand,
  outside the normal unit run — a mock can't prove the store's real error
  shape.

## Never leaking a value

- **A secret value is never logged, printed, cached to disk, or put in an
  error message.** Errors may name *which* secret and *which* store.
- **Redact any text that could leave the process** — tracebacks, alert
  payloads, callback bodies — by pattern (query-string credentials,
  `key = value` pairs whose name suggests a secret, bearer tokens). A local
  log that never leaves the machine doesn't need this.
- **The one sanctioned exception:** a dedicated *validation* secret holding
  no real credential (e.g. the environment's own name), read and printed by
  a pre-flight to prove the identity can reach the store.

## Authenticating to the store

Tried in priority order, each gated by its own config flag:

1. **The platform's workload identity** (a cloud managed identity or
   equivalent) — the only path in a real deployment. No credential exists in
   the image, the environment, or the repo.
2. **The developer's own signed-in CLI session** — for local development
   against the real store. Log a visible warning each time; this is a
   convenience, not the deployed path.
3. **A named environment variable** — last resort for developers with no
   store access; disabled in every deployment.

**A workload outside the platform's identity fabric** (on-prem, a home
server) has neither workload identity nor a persistent session to borrow.
Decide explicitly — never silently: give it its own bootstrap credential
(one secret held outside the store to reach the rest), or leave that target
on a simpler mechanism if it's genuinely low-stakes. Before building any
workaround, check whether the platform already has a native secrets/identity
mechanism — it's usually simpler.

## Review checklist

A credential in source, config, a template, or history · a secret value in a
log line or error message · an environment-variable fallback left enabled in
a deployed environment · a secret name that isn't three parts · an
environment name baked into a secret name · off-box text sent without
redaction · a mid-rotation read that fails immediately or falls back to a
stale copy.
