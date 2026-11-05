# SDSI Companion — Library / Package

For projects whose profile lists **lib** in `Companions` — code other code imports: a package published to a registry, or shared internally between projects. Not a skill: `sdsi:core` §1 Step 2 reads this file when the profile names it, and a running skill applies **only the section headed with its own name**. A skill with no section here has no library-specific additions; it proceeds on its own rules.

Language-neutral: apply each rule through the project language's own module system, visibility mechanism, package manifest, and registry.

**A researched base, not yet grown from a real project** — drawn from SemVer, the Rust API Guidelines, the PyPA and Python logging guides, Microsoft's .NET library guidance, Google's API compatibility rules, Go's module-compatibility guidance, and the OpenSSF/SLSA supply-chain guides, and checked in 2026-11 against how mature libraries (httpx, requests, Guava) behave (Sources, below). Correct it from the first library that disagrees.

**The one idea behind every deviation here: a library is a guest in someone else's process.** The application that imports it owns configuration, logging, error handling, threads, and shutdown. Where a base rule assumes the program owns those, this companion says so and narrows it.

## sdsi:workflow

- **`SPEC.md` names the public API and the support policy** — every exported module, type, and function a consumer may rely on, plus the language versions and platforms supported and when each is dropped (a schedule, or "only in a MAJOR"). An export not in the spec is a finding, so nothing becomes public by accident. The minimum language version also goes in the manifest's own field where the ecosystem has one, so an unsupported install fails at install time.
- **A change's plan states its compatibility class** — additive, deprecating, or breaking (`sdsi:versioning`) — before code, because that decides the design: a breaking change usually has an additive alternative.

## sdsi:standards

- **The public surface is explicit and small.** Export only what's in `SPEC.md`; everything else uses the language's internal mechanism. Every public name is a promise carried through every release until the next MAJOR.
- **Add, don't change or remove — and design for adding.** Evolve by adding a new function, overload, or optional parameter beside the old one, never by changing an existing signature or meaning. From the first release, use an options object (or the language's keyword/builder equivalent) instead of a long positional parameter list, constructors instead of public field-by-field construction, closed sets that consumers match on marked extensible where the language allows, and interfaces consumers aren't meant to implement sealed — so a later version can add a field, a case, or a method without breaking callers.
- **The library leaves the host process as it found it.** No side effects on import — no I/O, no network, no threads started, no global state mutated, no patching of the language or other libraries; work happens when the caller calls something. No process-global mutable state either: state lives in an instance the caller creates, so two parts of one application (or two tests) can use the library differently without interfering.
- **Public types implement the language's standard protocols** where they make sense — equality, hashing, string/debug representation, conversion, iteration — so they behave like the rest of the ecosystem.
- **A library in a typed language, or one with optional typing, ships its type information** — every public item annotated, and the ecosystem's marker or declaration files included in the package — so consumers' type checkers see the contract.

## sdsi:config

- **A sanctioned deviation from `sdsi:config`.** A library has no `config/` files, no loader, and no validate-config command of its own: the caller passes settings in (constructor arguments or an options object), and the application's own config is where the values come from.
- **Defaults live in code and are part of the public API** — documented on the parameter, and changing one is a breaking change (`sdsi:versioning`). The base rule's "no defaults in code" binds the application that configures the library, not the library.
- **No library-specific environment variable or file is read unprompted.** The only implicit reads are the ecosystem's standard variables for what the library does (proxy settings, a CA bundle path), each documented and all switchable off with one option. Any other environment fallback is opt-in, named with the library's prefix, and documented.
- **Validate options at construction and fail with a typed error naming the bad option** — the fail-early rule, applied at the library's front door.

## sdsi:security

- **The library never fetches its own credentials from a store.** The caller passes a credential, or better a credential provider (a callable or object the library asks when it needs a token), so the application keeps one secrets accessor and rotation works without rebuilding the client.
- **Credential-holding types redact themselves** in their string/debug representation and in every error they raise.

## sdsi:logging

- **A sanctioned deviation from `sdsi:logging`'s "one central logger".** The library never configures logging — no handlers, destinations, formats, levels, or color. It writes through the language's standard logging facade under a logger named for the library, and the application's central logger decides where it goes.
- **Silent by default.** With no logging configured by the application, the library produces no output; it never prints to stdout or stderr directly. Where the facade prints on its own when nothing is configured, the library attaches the facade's no-op handler to its logger.
- **Log sparingly and at low levels.** `DEBUG` for internals, `WARNING` for something the caller should fix (a deprecated call, a degraded fallback); an error the caller receives as a raised error is not also logged as one.

## sdsi:errors

- **A sanctioned deviation from core §3's "one global error handler".** A library installs no global handler, signal handler, or unhandled-error hook, and never exits or aborts the process — those belong to the application. The library's job is to raise well-typed errors to it.
- **Errors raised are part of the public API** — documented per function (what it raises and when), and changing which type a call raises is a breaking change.
- **Translate every dependency's error into the library's own type at the boundary**, keeping the original as the cause — a caller should never need to import a library's dependency to catch its errors.
- **Validate arguments on public entry points** and raise an invalid-argument error immediately, rather than failing deep inside with something the caller can't relate to their call.

## sdsi:concurrency

- **Document each public type's thread/async safety** — safe to share, or one per caller. Undocumented means the caller has to guess.
- **Don't start background threads, timers, or event loops the caller didn't ask for.** Where the library needs background work, the caller starts it and gets an explicit close/dispose that drains it.
- **Respect the caller's concurrency model.** An async API never blocks the caller's event loop; a sync API never spins up a hidden one. Offer both only when there's a real caller for each.
- **Every operation that waits accepts a timeout or cancellation from the caller**, using the language's standard mechanism, and its default is documented — a network call with no default timeout hangs the caller who didn't know to pass one.

## sdsi:testing

- **Test through the public API.** A test that reaches into internals pins implementation, not the contract consumers rely on.
- **Run the suite across the support matrix** in `SPEC.md` — each supported language version and platform — and against both the lowest and the newest dependency versions the manifest allows (`sdsi:dependencies`).
- **Check the public API against the last release in CI** with the ecosystem's API-diff or semver-check tool where one exists, so an accidental break fails the build instead of reaching a consumer.
- **Test the built package, not just the source tree** — install the artifact into a clean environment and import it, catching missing files and wrong entry points.
- **Documentation examples run as tests**, so an example can never drift from the API.

## sdsi:dependencies

- **A sanctioned deviation from `sdsi:dependencies`' pinning rule.** A library's manifest declares compatible *ranges*, because the application resolves one version of each package for everything it imports, and a tight constraint makes the library uninstallable beside others. Every dependency has a tested minimum; none is pinned exactly; none is capped beyond the ecosystem's default compatible range (the caret, or a MAJOR boundary) unless a specific incompatibility is known and named; and the language version is never capped. The lockfile still exists, committed, for the library's own development and CI; it isn't what consumers get.
- **Every dependency is a dependency of every consumer.** The bar is higher than for an application: prefer the standard library, reimplement a small piece, or make the dependency optional.
- **Never expose a dependency's types in the public API** unless that dependency is a deliberate, documented part of the contract — otherwise its next MAJOR becomes yours.
- **Heavy or niche capability is an optional extra** (the ecosystem's extras/features/optional-dependency mechanism), so consumers who don't use it don't install it.
- **A plugin or adapter for a host framework declares the host as a peer or optional dependency** with a broad range, never as a hard dependency that installs a second copy of it.
- **Test, development, and build tools are development-only dependencies**, never declared as runtime requirements.

## sdsi:docs

- **An API reference generated from the doc comments**, published with each release and covering every public item — with an example for every entry point and the errors each function raises.
- **The README opens with install and a minimal working example**, then the supported language versions and platforms, and links to the API reference and changelog.
- **Every MAJOR ships a migration guide** in `docs/` — each breaking change, and its exact replacement.
- **A security policy** says how to report a vulnerability privately and which versions get fixes.
- **A license file ships in the package**, and the manifest names the license by its SPDX identifier, so consumers' license checks can read it.

## sdsi:versioning

- **The public API is what SemVer protects**, so for a library MAJOR means a consumer's code or behavior can break: a removed or renamed public item, a changed signature, a changed default, a different error type raised, or a stricter accepted input. Dropping a language version or platform is MAJOR too — unless `SPEC.md`'s support policy declares a drop schedule and the release notes cite it, which makes it MINOR. MINOR adds; PATCH fixes without changing the contract.
- **Deprecate in a MINOR before removing in a MAJOR.** Mark the item with the language's deprecation mechanism (so callers get a compile-time or runtime warning), name the replacement in the message and the changelog bullet, and keep it working at least until the MAJOR. A MAJOR may remove it; a widely used item can stay deprecated for longer.
- **Unstable public items are marked experimental** with the language's mechanism (an opt-in annotation, an `experimental`/`beta` marker, an unstable module) and are exempted from the SemVer promise in writing, in the README and the item's docs.
- **`0.y.z` means the API isn't stable** — say so in the README; `1.0.0` is a commitment, made deliberately.
- **A published version is immutable.** Never re-publish or overwrite one; a broken release is withdrawn with the registry's yank/deprecate mechanism and fixed by a new version.

## sdsi:deploy

- **The deploy target is "distributed package"** — publishing to a registry (public or internal) is the deployment.
- **Publish from CI, never a laptop**, from the released commit, building the artifact once and uploading exactly what was tested.
- **Authenticate to the registry with short-lived CI identity (trusted publishing/OIDC) where the registry supports it**, not a long-lived token stored in CI; maintainer accounts use MFA.
- **Ship only what's meant to ship** — an explicit allow-list of files in the manifest, and the built package's contents inspected before the first publish and after any packaging change. No tests, fixtures, local config, or secrets in the artifact.
- **Publish provenance with the release where the registry supports it** — a signed build attestation (SLSA Build L2 or better) and, where consumers require one, an SBOM.

## Sources

- Semantic Versioning 2.0.0 — https://semver.org/
- Keep a Changelog 1.1.0 — https://keepachangelog.com/en/1.1.0/
- Rust API Guidelines, checklist — https://rust-lang.github.io/api-guidelines/checklist.html
- Rust API Guidelines, interoperability (C-GOOD-ERR) — https://rust-lang.github.io/api-guidelines/interoperability.html
- The Cargo Book, SemVer compatibility — https://doc.rust-lang.org/cargo/reference/semver.html
- Python Logging HOWTO, configuring logging for a library — https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
- Python typing, providing type information in libraries — https://typing.python.org/en/latest/guides/libraries.html
- PyPA, install_requires vs requirements files — https://packaging.python.org/en/latest/discussions/install-requires-vs-requirements/
- Henry Schreiner, Should you use upper bound version constraints? — https://iscinumpy.dev/post/bound-version-constraints/
- Scientific Python SPEC 0, minimum supported dependencies — https://scientific-python.org/specs/spec-0000/
- PyPI, Trusted Publishers — https://docs.pypi.org/trusted-publishers/
- HTTPX, environment variables — https://www.python-httpx.org/environment_variables/
- npm, package.json reference — https://docs.npmjs.com/cli/v10/configuring-npm/package-json
- npm, generating provenance statements — https://docs.npmjs.com/generating-provenance-statements
- Microsoft, .NET library guidance — https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/
- Microsoft, breaking changes and .NET libraries — https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/breaking-changes
- Microsoft, dependencies and .NET libraries — https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/dependencies
- Google AIP-180, backwards compatibility — https://google.aip.dev/180
- Guava, philosophy and API compatibility — https://github.com/google/guava/wiki/PhilosophyExplained
- The Go Blog, keeping your modules compatible — https://go.dev/blog/module-compatibility
- SLSA v1.0, security levels — https://slsa.dev/spec/v1.0/levels
- OpenSSF Scorecard, checks — https://github.com/ossf/scorecard/blob/main/docs/checks.md
- OpenSSF, Concise Guide for Developing More Secure Software — https://best.openssf.org/Concise-Guide-for-Developing-More-Secure-Software
