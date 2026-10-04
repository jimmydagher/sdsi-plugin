# SDSI Companion — Web

For projects whose profile says **Project type: web** — anything serving pages or an HTTP API to users. Not a skill: `sdsi:core` §1 Step 2 reads this file when the project type is web, and a running skill applies **only the section headed with its own name**. A skill with no section here has no web-specific additions; it proceeds on its own rules.

Language- and framework-neutral: apply each rule through the framework the project uses. Framework-specific lessons belong in the project's own `CLAUDE.md`, not here. The security rules follow OWASP (Top 10, ASVS, cheat sheets); where a rule names a header or status code, it is the standard one, not a house invention.

**A seed, not a finished standard.** Grow a section when a real web project teaches something that holds across frameworks.

## sdsi:workflow

- **`SPEC.md` states the web non-functional targets up front** — the accessibility level (WCAG 2.2 AA unless stated otherwise), the performance budget (Core Web Vitals "good" at the 75th percentile: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1), and the browsers supported. A target nobody wrote down can't be verified at deploy.
- **An HTTP API is designed contract-first.** The endpoint's request, response, and error shapes are written in the project's API description (an OpenAPI document or the framework's equivalent) and approved with the plan, before the handler is written.
- **Every new endpoint or page names who may use it** in the plan — anonymous, signed in, or a specific role — so access control is designed, not discovered in review.

## sdsi:standards

- **The request layer is thin.** A route/handler parses and validates input at the boundary, calls one service, and shapes the response. A business rule inside a handler is a finding.
- **Services never see request or response objects** — they take plain, validated values, so they can be called from a job, a test, or another handler unchanged.
- **Access control is deny-by-default and checked server-side on every request**, including per object: loading a record by an ID from the request checks that this user may see that record. A route with no stated rule, or a check that exists only in the UI, is a finding (broken access control is OWASP's #1 risk).
- **Output is encoded for its context by the template engine's auto-escaping**, and every query is parameterized. A bypass of either (a raw-HTML marker, string-built SQL or shell) is justified in a comment next to the line, or it's a finding.
- **Safe methods never change state.** `GET` and `HEAD` only read; anything that writes uses `POST`, `PUT`, `PATCH`, or `DELETE`, and an endpoint rejects methods it doesn't support with `405`.
- **API shapes are conservative and extensible** — a JSON response's root is an object, never a bare array; unknown or read-only input fields are rejected rather than silently bound (no mass assignment); field naming follows one casing across the whole API; every list endpoint is paginated.
- **UI code reuses the established design** — palette, type, spacing, components. Load a design skill before writing new markup or styles, and ground new tokens in what's already on the page rather than starting a parallel visual language.
- **UI meets WCAG 2.2 AA** — semantic elements before ARIA, a label on every form control, everything operable by keyboard with a visible focus, text contrast at least 4.5:1 (3:1 for large text), and pointer targets at least 24×24 CSS px.
- **A served asset is never edited in place** when it's built from a source asset; the source is edited and the served copy rebuilt. Name the two so which is which is obvious.

## sdsi:config

- **Forcing HTTPS is its own explicit setting, never derived from debug mode.** Turning debug off without stating HTTPS forcing inherits a default that redirects to an `https://` nothing serves and sets secure-only cookies the browser refuses, anywhere without TLS termination. Every environment override states it.
- **HSTS, secure-only cookies, and the HTTPS redirect are each stated per environment** alongside HTTPS forcing — same reason. HSTS (`Strict-Transport-Security`) is only ever sent from an environment that genuinely serves HTTPS, since browsers remember it.
- **Allowed hosts list both the bare domain and its `www.` variant** for every environment reachable by either — the forgotten one fails with a 400 or a silent CSRF rejection.
- **Trusted origins are added only when needed** — when a request's `Origin` won't match its own scheme and host (a TLS-terminating proxy changes the scheme). A plain-HTTP deployment reached at its own address usually needs none.
- **Trusted proxies are configured explicitly**, so the client address, scheme, and host read from forwarding headers come only from a proxy you run — never trusted from any caller.
- **CORS is an explicit allowlist of origins in config**, off when nothing cross-origin needs it. Never `*` with credentials, and a response that varies by origin sends `Vary: Origin`.
- **Security headers are set once, centrally, from config** — a `Content-Security-Policy` (strict: nonces or hashes, no `unsafe-inline`, `object-src 'none'`, `base-uri 'none'`; rolled out first as `Content-Security-Policy-Report-Only`), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, framing denied (`frame-ancestors 'none'` or `X-Frame-Options: DENY`), and a `Permissions-Policy` for unused features. Headers that only advertise the stack (`Server` detail, `X-Powered-By`) are removed.
- **Session and timeout values are settings** — idle timeout, absolute session lifetime, upload size limit, and rate limits live in config with the rest, not as framework defaults nobody chose.
- **The framework's settings module is a bridge, not a source.** It maps validated SDSI config onto framework settings; no setting is authored there and no environment variable is read there for an ordinary setting.
- **Every environment has the files and assets it serves.** When creating an environment, check that each file the site expects (`favicon.ico`, `robots.txt`, error pages, static assets) is in place for it, and create any that's missing rather than letting it 404.

## sdsi:secrets

- **Session, signing, and CSRF keys are secrets** — from the secrets store, one per environment, never a framework-generated default left in a settings file.
- **Nothing secret reaches the browser.** Client-side bundles, page source, and API responses never carry a server credential; a public client key is labelled as public where it's configured.
- **A credential never travels in a URL** — not an API key, token, password, or session ID in a path or query string, where it lands in access logs, browser history, and `Referer` headers. It goes in a header or the body.
- **Session cookies are `Secure`, `HttpOnly`, and `SameSite=Lax` or `Strict`**, and use the `__Host-` prefix where the deployment allows. The session ID is regenerated at sign-in and any privilege change, and destroyed server-side at sign-out.
- **Passwords are stored only with a slow, salted password-hashing function** built for the job (Argon2id first; scrypt; bcrypt for legacy; PBKDF2 where FIPS is required — at OWASP's current recommended cost), never a fast general hash or reversible encryption.

## sdsi:logging

- **Every request gets a correlation ID**, carried on every log line the request produces and returned in a response header, so a user's report can be traced to its lines. Where tracing exists, take it from the W3C `traceparent` header rather than inventing a second ID.
- **One access line per request:** method, path, status, duration, correlation ID.
- **Never log request bodies, cookies, or authorization headers** — they carry credentials and personal data. The same goes for session IDs and query strings that may hold tokens; mask or hash a value that's needed only to correlate.
- **Security decisions go to the audit trail** (`sdsi:logging`) — sign-in success and failure, sign-out, access denied, and every administrative or privilege change. Security anomalies that aren't decisions — input rejected at validation, CSRF or session anomalies, rate-limit trips — go to the application log at warning or above, with the user ID, client address, and correlation ID.

## sdsi:errors

- **Map error types to HTTP status in one place:** validation → 400/422, unauthenticated → 401, forbidden → 403, not found → 404, method not allowed → 405, unsupported media type → 415, conflict → 409, failed precondition → 412, rate limited → 429, anything unexpected → 500. Handlers raise typed errors; they don't choose status codes ad hoc.
- **A deployed error response never exposes internals** — no stack trace, exception message, SQL, or file path. The user sees a generic message and the correlation ID; the detail goes to the log.
- **API errors have one machine-readable shape** (an error code, a message, the correlation ID), the same for every endpoint. Never a `200` carrying an error inside. Prefer RFC 9457 Problem Details (`application/problem+json`: `type`, `title`, `status`, `detail`, `instance`) with the code and correlation ID as extension members, over a home-grown shape.
- **`429` and `503` responses carry `Retry-After`**, so a well-behaved client knows when to come back instead of hammering.
- **Pages get real error pages** — a styled 404, 403, and 500 that keep the site's layout, show the correlation ID, and return the correct status code (never a 200 "not found" page).
- **Unexpected errors pass through the global error handler** (`sdsi:errors`) and are logged with the correlation ID before the 500 goes out.

## sdsi:concurrency

- **Request handlers are stateless.** No mutable module- or process-level state shared across requests; anything shared lives in a store built for it.
- **Slow work leaves the request.** Anything that can outlast a normal response time goes to a background job queue; the request returns with a way to check progress (`202 Accepted` with the status URL in `Location`).
- **Outbound calls from a request have timeouts inside the request's own budget**, so one slow dependency can't hold every worker.
- **Shutdown stops accepting before it drains** — on the stop signal the server stops listening (and reports not-ready), lets in-flight requests finish within the bounded drain, then exits.
- **Concurrent updates don't silently overwrite each other.** An update to a resource two users can edit is conditional — an `ETag` with `If-Match`, or a version column — and the loser gets `412` or `409`, not a lost write.
- **A non-idempotent operation a client may retry is made safe to repeat** — a payment, an order, a send accepts an idempotency key and returns the first result for a repeat, rather than doing the work twice.
- **Expensive or abusable endpoints are rate-limited** — sign-in, password reset, sign-up, search, and anything that sends mail or costs money — with the limit in config and `429` on excess.

## sdsi:testing

- **Services are tested directly**, without the HTTP layer.
- **Request-level tests use the framework's test client** — status codes, error shapes, and auth behavior.
- **Access control is tested as denial, not only as success:** for each protected route, a test proves an anonymous caller, the wrong role, and a different user's object are all refused.
- **A test asserts the security headers and cookie attributes** on a representative page and API response, so a framework upgrade or middleware reorder can't drop them silently.
- **A few end-to-end browser tests cover the critical user flows** (sign-in, the main task), not every page — and run an automated accessibility check on the pages they visit. Automated checks catch only part of WCAG; they are a floor, not a pass.

## sdsi:dependencies

- **Client-side packages follow the same rules as server-side ones** — their own lockfile committed, their own vulnerability scan in CI — and count toward "few dependencies": every one ships to every user's browser.
- **A script or stylesheet loaded from a third-party origin is pinned to an exact version and carries Subresource Integrity** (`integrity` + `crossorigin`), or is served from the project's own origin instead.

## sdsi:docs

- **The API description is documentation and changes with the endpoint** — an added, changed, or removed route updates the OpenAPI document (or equivalent) in the same change, and the cheat sheet points to where it's served or rendered.
- **The "what changed → what to update" table includes the web moving parts** — a new route touches its access rule and the API description; a new external origin touches the CSP and CORS config; a new setting touches every environment override.

## sdsi:versioning

- **The running version shows in the UI, in several places** — the footer of every page, the about or help screen, and every error page beside the correlation ID, so a user's screenshot of a problem names the release it happened on. It's read from `VERSION` at build or startup, never typed into a template.
- **On pages anyone can reach without signing in** — the login page, public error pages — showing the version is a stated decision, recorded in `CLAUDE.md`. It helps support, but security scans flag version disclosure.
- **A public API's breaking change is a MAJOR bump** — removing or renaming a field, making an optional input required, adding an output enum value clients must handle, changing a status code. Prefer a compatible extension (add an optional field) over a break.
- **A deprecated endpoint says so in its responses** — the `Deprecation` header (RFC 9745), a `Sunset` header with the removal date, and a `Link` with `rel="deprecation"` to the migration note — and the changelog names the release that removes it.
- **Built static assets carry a content hash in their file name**, so a release can cache them for a long time and still never serve a stale file; the HTML that references them is not long-cached.

## sdsi:deploy

- **A self-hosted, LAN-only deployment gets its own security settings** — HTTPS forcing off, its own address in allowed hosts — never a cloud deployment's settings inherited as a default.
- **Every web project has two health endpoints, always.** A **basic** one (e.g. `/healthz/`) — no authentication, no dependencies, it only proves the process answers — for the platform's probe and uptime checks. A **full** one (e.g. `/healthz/deep/`) checks every service the app depends on — database, secrets store, queues and caches, outbound services, writable storage — and reports each as ok or failed, returning `200` when all pass and `503` otherwise.
- **The full health endpoint is gated by an admin key** from the secrets store, sent in a header (never the query string) and compared in constant time: `404` when no key is configured for the environment, `403` with no detail for a wrong key. Its report is redacted — no secret, connection string, or file path — and it never serves as the platform's probe, so one slow dependency can't get a healthy container restarted.
- **A deploy is checked by reading the version off the deployed page** and comparing it with the release just shipped — proof the new build is the one serving, not a cached or previous one.
- **The deploy check also reads the response headers off the deployed site** — HTTPS redirect, HSTS, CSP, and cookie flags as configured for that environment — since a proxy or platform in front can add, strip, or rewrite them.
- **Debug mode, debug toolbars, and interactive error pages are off in every deployed environment**, stated explicitly in each override and confirmed by the deploy check (an unknown URL returns the plain 404 page).

## Sources

- OWASP Top 10:2025 — https://top10.owasp.org/2025
- OWASP Application Security Verification Standard (ASVS) 5.0 — https://owasp.org/www-project-application-security-verification-standard/
- OWASP HTTP Security Response Headers Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html
- OWASP Session Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- OWASP Cross-Site Request Forgery Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP Content Security Policy Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
- OWASP REST Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
- OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- OWASP Logging Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- OWASP Password Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- RFC 9457, Problem Details for HTTP APIs — https://www.rfc-editor.org/rfc/rfc9457.html
- RFC 9745, The Deprecation HTTP Response Header Field — https://www.rfc-editor.org/rfc/rfc9745.html
- W3C Trace Context — https://www.w3.org/TR/trace-context/
- W3C Web Content Accessibility Guidelines (WCAG) 2.2 — https://www.w3.org/TR/WCAG22/
- web.dev, Web Vitals — https://web.dev/articles/vitals
- MDN, Cross-Origin Resource Sharing (CORS) — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
- Zalando RESTful API Guidelines, Compatibility — https://github.com/zalando/restful-api-guidelines/blob/main/chapters/compatibility.adoc
- Microsoft Azure REST API Guidelines — https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md
- The Twelve-Factor App, Disposability — https://12factor.net/disposability
