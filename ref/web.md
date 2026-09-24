# SDSI Companion — Web

For projects whose profile says **Project type: web** — anything serving
pages or an HTTP API to users. Not a skill: `sdsi:core` §1 Step 2 reads this
file when the project type is web, and a running skill applies **only the
section headed with its own name**. A skill with no section here has no
web-specific additions; it proceeds on its own rules.

Language- and framework-neutral: apply each rule through the framework the
project uses. Framework-specific lessons belong in the project's own
`CLAUDE.md`, not here.

**A seed, not a finished standard.** Grow a section when a real web project
teaches something that holds across frameworks.

## sdsi:standards

- **The request layer is thin.** A route/handler parses and validates input
  at the boundary, calls one service, and shapes the response. A business
  rule inside a handler is a finding.
- **Services never see request or response objects** — they take plain,
  validated values, so they can be called from a job, a test, or another
  handler unchanged.
- **UI code reuses the established design** — palette, type, spacing,
  components. Load a design skill before writing new markup or styles, and
  ground new tokens in what's already on the page rather than starting a
  parallel visual language.
- **A served asset is never edited in place** when it's built from a source
  asset; the source is edited and the served copy rebuilt. Name the two so
  which is which is obvious.

## sdsi:config

- **Forcing HTTPS is its own explicit setting, never derived from debug
  mode.** Turning debug off without stating HTTPS forcing inherits a default
  that redirects to an `https://` nothing serves and sets secure-only cookies
  the browser refuses, anywhere without TLS termination. Every environment
  override states it.
- **Allowed hosts list both the bare domain and its `www.` variant** for
  every environment reachable by either — the forgotten one fails with a 400
  or a silent CSRF rejection.
- **Trusted origins are added only when needed** — when a request's `Origin`
  won't match its own scheme and host (a TLS-terminating proxy changes the
  scheme). A plain-HTTP deployment reached at its own address usually needs
  none.
- **The framework's settings module is a bridge, not a source.** It maps
  validated SDSI config onto framework settings; no setting is authored
  there and no environment variable is read there for an ordinary setting.

## sdsi:secrets

- **Session, signing, and CSRF keys are secrets** — from the secrets store,
  one per environment, never a framework-generated default left in a
  settings file.
- **Nothing secret reaches the browser.** Client-side bundles, page source,
  and API responses never carry a server credential; a public client key is
  labelled as public where it's configured.

## sdsi:logging

- **Every request gets a correlation ID**, carried on every log line the
  request produces and returned in a response header, so a user's report can
  be traced to its lines.
- **One access line per request:** method, path, status, duration,
  correlation ID.
- **Never log request bodies, cookies, or authorization headers** — they
  carry credentials and personal data.

## sdsi:errors

- **Map error types to HTTP status in one place:** validation → 400/422,
  unauthenticated → 401, forbidden → 403, not found → 404, conflict → 409,
  anything unexpected → 500. Handlers raise typed errors; they don't choose
  status codes ad hoc.
- **A deployed error response never exposes internals** — no stack trace,
  exception message, SQL, or file path. The user sees a generic message and
  the correlation ID; the detail goes to the log.
- **API errors have one machine-readable shape** (an error code, a message,
  the correlation ID), the same for every endpoint. Never a `200` carrying an
  error inside.
- **Unexpected errors pass through the global error handler** (`sdsi:errors`) and
  are logged with the correlation ID before the 500 goes out.

## sdsi:concurrency

- **Request handlers are stateless.** No mutable module- or process-level
  state shared across requests; anything shared lives in a store built for
  it.
- **Slow work leaves the request.** Anything that can outlast a normal
  response time goes to a background job queue; the request returns with a
  way to check progress.
- **Outbound calls from a request have timeouts inside the request's own
  budget**, so one slow dependency can't hold every worker.

## sdsi:testing

- **Services are tested directly**, without the HTTP layer.
- **Request-level tests use the framework's test client** — status codes,
  error shapes, and auth behavior.
- **A few end-to-end browser tests cover the critical user flows** (sign-in,
  the main task), not every page.

## sdsi:deploy

- **A self-hosted, LAN-only deployment gets its own security settings** —
  HTTPS forcing off, its own address in allowed hosts — never a cloud
  deployment's settings inherited as a default.
