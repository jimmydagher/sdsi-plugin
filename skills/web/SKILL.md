---
name: web
description: >
  SDSI project type for websites and web applications — owns the source
  layout, entry point, and design of anything serving pages or an HTTP API:
  the site/ source folder, a thin request layer over services, per-
  environment security settings (HTTPS forcing, allowed hosts, trusted
  origins), served vs source assets, visual consistency, and Django-
  specific rules (manage.py placement, app naming, the settings.py config
  bridge). Silent unless the SDSI profile's project type is web, or it's
  invoked by name. Reads sdsi:core first. Triggers on "/sdsi:web", "build a
  website", "Django site", "web app".
---

# SDSI: Web Project

Before anything else, read `../core/SKILL.md` and run its steps. This skill
owns the parts of core §3 that depend on project type — the source layout,
the entry point, and the design shape — for a website or web application.
Topics (`sdsi:config`, `sdsi:secrets`, …) still apply in full; this skill
only adds what's true because the project is a website.

Distilled from building `flammeau` (Django). Framework-specific rules are
grouped under their framework; add a section when a project on another
framework teaches something.

## Layout

The source folder is `site/` — a more accurate name than `src/` when the
package is a whole website.

```
site/
├── <app entry>        # the framework's application entry — wiring only, no logic
├── helpers/           # the one home for shared code — infrastructure that knows
│                      #   nothing about any feature
├── <feature>/         # one per domain area, each holding its own:
│   ├── routes/views   #   request layer — parse, validate, call a service, respond
│   ├── services       #   business logic — no request/response objects
│   ├── models         #   persistence
│   └── templates      #   presentation
├── static/            # served, processed assets
└── assets-src/        # raw design sources (unprocessed logos, brand files)
```

- **Dependencies point one way:** `helpers` ← services ← routes/views ← app
  entry. A service never imports from the request layer; `helpers` never
  imports from a feature.
- **The request layer is thin.** A route/view validates input at the
  boundary (`sdsi:standards`), calls one service, and shapes the response.
  Business rules in a view are a finding.
- **Raw design sources live under `site/`, colocated with what consumes them,
  and are named clearly apart from their served copies under `static/`.** A
  served copy edited in place and drifting from its source is a real trap.
- **A runner script doesn't have to sit where the framework's scaffolding
  puts it.** Moving it is legitimate, but every invocation (Dockerfile,
  compose, docs, scripts, CI) must be updated, and the location written in
  `CLAUDE.md` — or a later session regresses to the framework default.

## Security settings per environment

- **Forcing HTTPS is its own explicit setting, never derived from debug
  mode.** Turning debug off without stating HTTPS forcing silently inherits
  the default — redirecting to an `https://` nothing serves and setting
  secure-only cookies the browser refuses, anywhere without TLS termination.
  Every environment override states it explicitly (`sdsi:config`).
- **Allowed hosts include both the bare domain and its `www.` variant** for
  every environment reachable by either — the forgotten one fails with a
  clean 400 or a silent CSRF failure.
- **Don't over-populate trusted origins.** An explicit trusted origin is only
  needed when a request's `Origin` wouldn't already match its own
  scheme+host (a TLS-terminating proxy changes the scheme, for instance). A
  plain-HTTP LAN deployment reached by its own address usually needs none.
- **A self-hosted, LAN-only target gets its own security settings** — HTTPS
  forcing off, its own address in allowed hosts — never the cloud target's
  (`sdsi:deploy`).

## Visual consistency

**Load a dedicated design skill before writing new CSS or markup**, and
ground new design tokens in what's already on the page — reuse the palette,
type, and spacing rather than introducing a parallel visual language for one
new section. Consistency across the site is an explicit expectation.

## Django

- **`manage.py` may live outside the repo root** (e.g. `site/admin/manage.py`)
  — it only needs the project package importable via the import path. The
  runner-script rule above applies.
- **Name the shared-code app `helpers`, never `core`** — `core` collides
  conceptually with Django's own internals and reads ambiguously.
- **Set `AppConfig.name` to the dotted path (`mysite.accounts`) but never set
  an explicit `app_label`.** Django's derived label is what applied
  migrations and table prefixes assume; setting one silently diverges from
  them.
- **`settings.py` is a bridge from SDSI config, not a config source.** It
  reads the validated config (`sdsi:config`) and maps it onto Django
  settings; no setting is authored in `settings.py` itself and no
  environment variable is read there for an ordinary setting.
- **A secret's name is an ordinary schema-validated string in config**; the
  resolver that turns it into a value (`sdsi:secrets`) is a separate layer.
  The schema has no awareness of "this one is secret" beyond requiring the
  name.

## Review checklist

Business logic in a view/route · a service importing request objects ·
shared code outside `helpers/` · HTTPS forcing derived from debug · an
environment missing the `www.` (or bare) host · speculative trusted origins
· a served asset edited instead of its source · a moved runner script not
recorded in `CLAUDE.md` · (Django) an explicit `app_label` or an app named
`core` · settings authored in `settings.py`.
