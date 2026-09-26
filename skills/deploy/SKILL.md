---
name: deploy
description: >
  SDSI's local-environment and deployment standard — asks the human which
  deploy target to implement (containers are the default recommendation,
  but not everyone works that way), then applies it: versioned local run
  configuration, local wiring that mirrors deployment, config kept out of
  the built artifact, environment naming, promotion by retag, managed
  volume-mount traps, native identity before workarounds, and per-target
  trust boundaries. Use when setting up how a project runs locally or
  ships. Reads sdsi:core first. Triggers on "/sdsi:deploy", "deploy",
  "docker", "containerize", "run locally".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Local Environment & Deployment

Before anything else, read `../core/SKILL.md` and run its steps.

## Step 1 — Ask the deploy target

If the project profile has no `Deploy target`, ask with `AskUserQuestion` and record the answer in the profile (core §1, Step 2). Offer:

- **Containers (recommended)** — one image, promoted across environments by retag; runs the same locally and deployed.
- **Cloud platform service** — a managed app/function service deploying code directly.
- **Self-hosted host** — a VM, on-prem server, or home server running the program directly under a service manager.
- **Distributed package** — installed by users (a package registry, a binary release); there's no "deployment" beyond publishing.

Don't assume containers because it's the default recommendation — the human decides. Apply the target-specific section below, plus every universal rule.

## Universal rules

- **Local run/debug configuration is part of the application** (IDE launch configs, compose files, task runners) — versioned, and updated in the same change as anything that changes how the program is invoked (a new operation, a new required environment variable, a new environment).
- **No credential in a committed local-run file.** Local secrets come from the developer's shell or a gitignored local env file (`sdsi:secrets`).
- **Local wiring mirrors deployed wiring** — the same environment variables and the same config-loading path — so a local run previews the deployed one instead of being a separate code path.
- **Config stays out of the built artifact.** Mount or inject it per environment, so one artifact is promotable without rebuilding.
- **Promote by retagging the tested artifact, never by rebuilding** (`sdsi:versioning`).
- **A clear naming/tagging convention per environment**, so what's running where is never ambiguous.
- **Prefer a job that does one thing and exits** over a long-running service when the workload is batch or triggered.
- **Each target's security settings are configured for its own trust boundary**, explicitly. Never inherit another environment's settings (a TLS-terminated cloud deployment's, say) as a safe default for a differently exposed one.
- **The build definition lives in the repo**, not typed into a CI tool's UI; the CI tool holds only a registration pointing at it plus genuinely environment-specific bits (connections, approvals).
- **Document local run/debug separately from deployment** (`sdsi:docs`).

## Containers

- One image for every environment; environment differences come from mounted config and injected wiring only.
- Pin the base image to a digest (`sdsi:dependencies`); no floating tags.
- Keep a compose file (or equivalent) for local runs, versioned.
- **Managed platforms often mount a whole directory, not a single file** — unlike a local bind-mount. Mounting a managed volume over a directory that also holds files baked into the image clobbers them. Mount at a separate path and point the program at it with one setting that defaults to the in-image location.
- Handle the platform's graceful-stop signal and keep shutdown inside its grace period (`sdsi:concurrency`).

## Cloud platform service

- Prefer the platform's native scheduling and orchestration over standing up separate infrastructure, unless there's a concrete reason it doesn't fit.
- **Check for the platform's native identity and secrets mechanism before building any workaround** (`sdsi:secrets`) — it's usually simpler than provisioning storage just to avoid environment variables.

## Self-hosted host

- Run under the OS's service manager, with restart policy and log location stated in the deployment doc.
- There's no workload identity here — decide the secrets approach explicitly (`sdsi:secrets`, "a workload outside the platform's identity fabric").
- Its trust boundary (LAN-only, no TLS termination) usually differs from any cloud target; configure its security settings for that, explicitly.

## Distributed package

- The published version is `VERSION`; the package manifest is kept in sync by the release script's `version_files` (`sdsi:versioning`).
- Decide the distribution shape deliberately (package manager, self-contained binary, image) and write it down — each is a different commitment for the people installing it.

## Review checklist

No recorded deploy target · local run config missing or out of date · a credential in a committed run file · local wiring that differs from deployed wiring · config baked into the artifact · promotion by rebuild · a floating base-image tag · a managed volume mounted over baked-in files · security settings inherited across trust boundaries · a build definition that lives only in the CI tool.
