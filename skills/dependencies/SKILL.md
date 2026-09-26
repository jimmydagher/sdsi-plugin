---
name: dependencies
description: >
  SDSI's dependency-management standard, language-neutral — standard library
  first, few well-trusted dependencies, latest stable at the time a
  dependency is added, pinned versions with a committed lockfile, isolated
  environments, vulnerability scanning that must actually be clean before
  merge, lazy loading of heavy or environment-specific modules, and no
  floating tags in anything deployed. Use when adding, upgrading, or
  auditing dependencies. Reads sdsi:core first. Triggers on
  "/sdsi:dependencies", "add a package", "dependency audit".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Dependencies

Before anything else, read `../core/SKILL.md` and run its steps. Apply each rule with the project language's own package manager, lockfile, and vulnerability scanner.

## Rules

- **Standard library first.** If it can be built with the language's own standard library, build it that way. A third-party package is added only when genuinely necessary and it has a long, trustworthy track record.
- **Few, well-understood dependencies** over a large transitive tree — a couple of direct REST calls beat a full vendor SDK when that's all you need. Every dependency must be scanned, updated, and trusted.
- **Add at the latest stable version** at the time it's added — not an old pin copied from another project.
- **Pin versions and commit the lockfile**, so resolution is reproducible.
- **Always develop in an isolated environment** (the language's virtual environment, a project-local install) — never against global packages.
- **Scan for known vulnerabilities in CI.** A scan that's merely scheduled doesn't count — it has to be clean, or explicitly and visibly waived, before merge.
- **Review and update on a regular cadence**, not only when something breaks.
- **Load heavy or environment-specific modules lazily, by name from config**, so a deployment only pays for what it uses.
- **No floating versions in anything deployed** — no `latest`, `main`, or `HEAD` for a dependency or base image. Pin container images to a digest, not just a tag.

## Review checklist

A dependency the standard library already covers · a heavy SDK used for one call · unpinned versions or no committed lockfile · global installs · no vulnerability scan in CI, or an unwaived finding · a floating tag or undigested image in a deployed artifact.
