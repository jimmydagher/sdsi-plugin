# SDSI Companion — Mobile App

For projects whose profile says **Project type: mobile** — an app installed on phones or tablets (iOS, Android, or both from one cross-platform codebase) and distributed through an app store. Not a skill: `sdsi:core` §1 Step 2 reads this file when the project type is mobile, and a running skill applies **only the section headed with its own name**. A skill with no section here has no mobile-specific additions; it proceeds on its own rules.

Language-, framework-, and platform-neutral: apply each rule through the toolkit the project uses — native or cross-platform. Where a rule names a platform mechanism (the iOS Keychain, the Android Keystore), it's an example of the kind of thing to use, not a requirement to call it directly. Framework-specific lessons belong in the project's own `CLAUDE.md`, not here.

**A seed, not a finished standard** — a researched base drawn from OWASP MASVS/MASTG and Apple's and Google's published platform and store guidance (Sources, below), not yet grown from a real mobile project. Correct it from the first one that disagrees.

## sdsi:workflow

- **`SPEC.md` states the supported platforms and their minimum OS versions, the form factors (phone, tablet, foldable), and each feature's offline behavior** — what works with no network, what queues, what refuses. Each is checkable on a device, and each later decides the test matrix (`sdsi:testing`).
- **Store requirements are acceptance criteria, written into `SPEC.md` before the feature that triggers them:** a privacy policy linked in the app and the listing; in-app account deletion wherever accounts can be created; a working reviewer demo account or demo mode for anything behind sign-in. A store rejection is a spec gap found late.
- **A change that adds a permission, a data type collected, or a third-party SDK is flagged as scope** (`sdsi:workflow`, "scope changes get flagged"), because it also changes the store's privacy declarations (`sdsi:docs`).

## sdsi:standards

- **The UI layer only renders state and forwards events.** Screens hold no business rules and no network or storage calls; a state holder per screen exposes immutable state built from the data layer, and user events flow back to it — state down, events up. Business and data code doesn't depend on platform UI types, so it's testable without a device.
- **Every data type has one owner** (a repository or equivalent) that alone writes it; everything else reads its exposed state. Two screens caching and editing their own copy of the same record is a finding.
- **User state survives the lifecycle** — backgrounding, rotation or resize, and the OS killing the process to reclaim memory. Restoring to the same screen with in-progress input intact is expected behavior, not polish.
- **Permissions are requested at the moment of use, with a purpose string that says why**, only for what a core feature needs — and the app keeps working, with that feature degraded, when the user says no.
- **Accessibility is a coding standard, not an audit:** every interactive element has an accessibility label, touch targets meet the platform minimum (44×44 pt on iOS, 48×48 dp on Android), text scales with the system text-size setting without clipping, contrast meets WCAG AA, meaning never rests on color alone, and the system reduce-motion setting is honored.

## sdsi:config

- **A sanctioned deviation from `sdsi:config`'s runtime loading:** the app can't read `config/` from the device, so config is resolved **at build time** — `config/default.yaml` deep-merged with the environment's override, schema-validated by the build, and baked into that environment's build variant. A build with invalid config fails; the build, not app start, is where "before any work starts" happens. Everything in it ships to every user, so it holds nothing secret (`sdsi:security`).
- **Build variants map one-to-one to the project's environments** (one variant per `config/override/<env>.yaml`), selected by the build, never by an in-code `if` on a flag. The backend base URL and every other per-environment value comes from that environment's config.
- **Transport security and certificate pinning are configured per build variant**, under the rules in `## sdsi:security` below.
- **Remote configuration (feature flags, kill switches, the minimum supported version) is a second, runtime layer with the same discipline:** its keys are in the schema, its bundled fallback values are generated from `config/default.yaml` rather than written as literals in code, and a fetched payload that fails validation is rejected whole and logged.

## sdsi:security

- **Every externally reachable entry is an untrusted boundary**: deep links and universal/app links, push-notification payloads, data shared in from other apps, exported components, and anything a web view passes back. Validate there (`sdsi:security`); a component that isn't meant to be reached from outside isn't exposed, and a web view never bridges native functions to content the app doesn't control.
- **Transport security is configured, not left to defaults:** cleartext traffic is disabled in every release variant through the platform's network-security configuration; debug-only trust anchors (a proxy's CA) live in a debug-only override the release build ignores.
- **Certificate or public-key pinning is a stated decision recorded in `CLAUDE.md`, not a default.** It applies only to endpoints the team controls; when used, it carries at least one backup pin and a written rotation plan, since a pin the server outgrows cuts off every installed copy until users update.
- **The shipped app is public.** Anything in the binary or its resources — config, strings, obfuscated or not — can be extracted by anyone who installs it. No server credential ships in the app; an operation that needs one goes through the project's own backend, which holds it.
- **A key that has to ship** (a maps key, a public client ID, an analytics write key) is restricted at its provider to this app's bundle identifier or signing certificate and to the narrowest scope, and is labelled as public where it's configured.
- **Credentials at rest on the device live only in the platform's secure store** (Keychain on iOS, the Keystore on Android, or a wrapper over them) — never in preferences, plain files, or the app's database. Keys are generated non-exportable and hardware-backed where the device supports it.
- **Tokens, keys, and device-bound identifiers are excluded from device and cloud backups** (the platform's backup rules, device-only accessibility on secure-store items), so restoring onto another device can't carry them across.
- **Sensitive values never leak through the OS:** not into the clipboard, notifications, the keyboard's learning cache (sensitive fields are marked secure or no-suggestions), or the app-switcher snapshot of a sensitive screen.
- **App-signing keys and store-upload credentials are secrets** — held in CI's secret store, never in the repo or a developer's machine alone. Use the store's managed app signing where it's offered, so a lost upload key is recoverable.

## sdsi:logging

- **The device's system log is readable off the device** (attached debuggers, other tools, bug reports). Release builds strip debug and verbose logging at compile time — not just filter it at runtime — and nothing user-identifying goes to the system log at any level.
- **Crash reporting and analytics are log destinations that leave the device**, so they're fed through the central logger's fan-out (`sdsi:logging`) and redacted (`sdsi:security`) like any other off-box text — never wired up as a parallel logging path.
- **Every request to the backend carries a per-session correlation ID** that also tags the app's own logs and crash reports, so one user's problem can be traced across device and server. It's random per install or session — never a hardware identifier or the advertising ID.
- **Telemetry upload respects the device:** buffered on disk with a size cap, sent in batches when the network is available, never a request per event.
- **What's collected is what's declared.** Every analytics event or crash field that carries user data matches the store privacy declarations (`sdsi:docs`); tracking a user across other companies' apps or sites needs the platform's tracking consent (App Tracking Transparency on iOS) before any tracking call.

## sdsi:errors

- **The crash reporter is a reporter on the global error handler** (`sdsi:errors`), not a second handler — and every release build uploads its symbol and deobfuscation files (iOS dSYMs, Android mapping files) in the pipeline, so production stack traces are readable. A release without its symbols is incomplete.
- **Offline is a state, not an error.** Every network-backed screen has distinct loading, empty, offline, and failed states; "no network", "the server failed", and "there's nothing here" never render the same.
- **Retries wait for connectivity and back off with jitter** — a retry fired while the device is offline just drains battery and fails again. Work that must eventually happen queues instead (`sdsi:concurrency`).
- **An unsupported-version response from the backend is a typed error with its own screen** — a blocking "please update" with a link to the store — never a generic failure the user can't act on.

## sdsi:concurrency

- **A sanctioned deviation from `sdsi:concurrency`'s graceful shutdown:** the OS can suspend or kill the app at any time without a catchable stop signal. Persist anything that matters when the app moves to the background, and make every local write atomic, so a kill mid-write leaves the old or the new state, never half of each.
- **The UI is updated only from the main thread**, and the main thread never waits on disk or network — the platform watchdog terminates an unresponsive app.
- **Work tied to a screen is cancelled with that screen**, through the toolkit's lifecycle-scoped work, so it neither leaks nor writes to a UI that's gone.
- **Work that must outlive the screen or the process goes through the platform's scheduled-work API**, with stated constraints (network, charging), never an in-process thread that the OS will freeze. Long-running foreground work uses the platform's sanctioned mechanism and its required user-visible notice.
- **Offline-first data: the local store is the source of truth for reads.** Writes land locally first, then sync; each sync operation is idempotent (a client-generated ID or idempotency key), and the conflict rule — last write wins, or a merge — is stated in `SPEC.md`, never left to whichever request arrives last.
- **No polling to stay current.** Use server push, or scheduled sync the OS can batch; foreground refresh is on user action or screen entry.

## sdsi:testing

- **The device matrix comes from `SPEC.md`:** at least the minimum supported OS and the latest, a small and a large screen, and each form factor claimed. UI tests run on emulators or simulators in CI; a real-device run (a device farm counts) gates each store release.
- **Lifecycle and environment are tested deliberately:** rotation or resize mid-input, process death and restoration, background/foreground, airplane mode and a flaky network, and every permission denied.
- **Upgrade is tested, not just fresh install:** install the previous released build, create data, upgrade to the new one, and check that local-schema migrations and stored credentials survive.
- **Accessibility checks run in UI tests** through the platform's automated accessibility checker, plus a manual screen-reader pass (VoiceOver, TalkBack) over the critical flows before release.
- **The release variant itself is tested** — at least a smoke run of the minified, obfuscated, signed build — because shrinking and obfuscation break things the debug build never shows.

## sdsi:dependencies

- **Every SDK's data collection is the app's data collection.** Before adding one, find out what it collects and transmits; adding it updates the store privacy declarations in the same change (`sdsi:docs`), and on iOS it must ship its own privacy manifest.
- **The stores require targeting a recent OS API level on a schedule**, and new builds must use a current toolchain — keeping the platform SDK and build tools current is on `sdsi:dependencies`' regular cadence, because falling behind blocks the next release, not just a scan.
- **Size is a cost:** every dependency adds to download and install size; a heavy SDK for one feature needs the same justification as any other (`sdsi:dependencies`).
- **No downloaded executable code that changes the app's behavior** — store policy forbids it. Remote config changes behavior only through code paths already shipped in the binary.

## sdsi:docs

- **The store privacy declarations live in the repo as documents** — the data-safety answers, the privacy labels, each permission's purpose string, and the privacy manifest — and change in the same change as the code that changes what's collected. Copy them into the store console from the repo, never the other way round.
- **A release doc covers the store path end to end:** building and signing, the beta track, submission, where the reviewer demo account lives (named, from the secrets store), the staged-rollout steps, halt criteria, and how to halt.
- **The README names the supported OS versions and devices**, and how to run the app on a simulator, an emulator, and a physical device — each a separate setup.
- **Add the mobile rows to the "what changed → what to update" table:** a new permission touches the purpose strings and privacy declarations; a new SDK touches the privacy declarations; a new local-schema version touches the migration tests.

## sdsi:versioning

- **Two numbers, two jobs.** The user-visible version is `VERSION` (synced into the platform manifests by the release script's `version_files`, `sdsi:versioning`). The build number the stores compare (Android's `versionCode`, iOS's build number) is a separate, strictly increasing integer, generated by the build — derived from `VERSION` or the CI run — never hand-edited and never reused.
- **The running version and build number show in the app's settings or about screen and are attached to every crash report and backend request**, so a user's report names the exact build. They're read from the build, never typed into a screen.
- **Released versions can't be recalled.** Users stay on old builds for months, so every backend contract the app depends on stays compatible with every app version still supported; breaking one is a MAJOR change for the backend.
- **The minimum supported version is server-side config** (`sdsi:config`, remote configuration), checked at launch. Raising it — forcing users to update — is a stated decision with its reason written in the changelog's notes.
- **Every local data schema version migrates forward** from every supported prior one, without data loss. A destructive migration (dropping user data on upgrade) needs explicit approval (core §2).

## sdsi:deploy

- **The deploy target is "distributed package" through the app stores** — record which stores and which tracks (internal, beta, production) in the profile's deploy notes.
- **One signed build is promoted, never rebuilt:** CI builds and signs it once, then the same artifact moves internal → beta → production, the store-track form of `sdsi:deploy`'s promote-by-retag.
- **Every production release is staged** — the store's phased or percentage rollout — with the crash-free rate and the key flows watched at each step, and the halt criteria written down before it starts.
- **A store release can't be rolled back, only halted and superseded** by a new, higher build that also has to pass review. Risky features ship behind a remote kill switch so they can be turned off without a release.
- **A release build is checked before submission:** not debuggable, no debug trust anchors, cleartext disabled, logging stripped, minified and obfuscated, symbols uploaded, and the version and build number both as expected.
- **A deploy is verified by installing from the store track** and reading the version and build number off the app's about screen — proof the release users get is the one just shipped.

## Sources

- OWASP Mobile Application Security Verification Standard (MASVS) v2.1 — https://mas.owasp.org/MASVS/
- OWASP MASVS-STORAGE-1, "The app securely stores sensitive data" — https://mas.owasp.org/MASVS/controls/MASVS-STORAGE-1/
- OWASP MASVS-NETWORK-2, identity pinning — https://mas.owasp.org/MASVS/controls/MASVS-NETWORK-2/
- OWASP MASVS-CODE-2, enforced updating — https://mas.owasp.org/MASVS/controls/MASVS-CODE-2/
- OWASP MASWE-0005, API keys hardcoded in the app package — https://mas.owasp.org/MASWE/MASVS-STORAGE/MASWE-0005/
- OWASP MASWE-0001, sensitive data in logs — https://mas.owasp.org/MASWE/MASVS-STORAGE/MASWE-0001/
- Apple App Store Review Guidelines — https://developer.apple.com/app-store/review/guidelines/
- Apple Human Interface Guidelines: Accessibility — https://developer.apple.com/design/human-interface-guidelines/accessibility
- Apple privacy manifest files — https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
- Apple App Tracking Transparency — https://developer.apple.com/documentation/apptrackingtransparency
- Apple Keychain Services — https://developer.apple.com/documentation/security/keychain-services
- App Store Connect: Release a version update in phases — https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases/
- Android Core app quality guidelines — https://developer.android.com/docs/quality-guidelines/core-app-quality
- Android Guide to app architecture — https://developer.android.com/topic/architecture
- Android Build an offline-first app — https://developer.android.com/topic/architecture/data-layer/offline-first
- Android Background work overview — https://developer.android.com/develop/background-work/background-tasks
- Android Security best practices — https://developer.android.com/privacy-and-security/security-best-practices
- Android Network security configuration — https://developer.android.com/privacy-and-security/security-config
- Android Keystore system — https://developer.android.com/privacy-and-security/keystore
- Android Back up user data with Auto Backup — https://developer.android.com/identity/data/autobackup
- Android Version your app — https://developer.android.com/studio/publish/versioning
- Google Play: Data safety section — https://support.google.com/googleplay/android-developer/answer/10787469
- Google Play: Release app updates with staged rollouts — https://support.google.com/googleplay/android-developer/answer/6346149
