# SDSI Companion — Desktop Application

For projects whose profile says **Project type: desktop**: a GUI application installed on users' own machines (Windows, macOS, Linux), whether it's built on a native toolkit, a cross-platform toolkit, or embedded web technology. This file isn't a skill. `sdsi:core` §1 Step 2 reads it when the project type is desktop, and a running skill applies **only the section headed with its own name**. A skill with no section here has no desktop-specific additions and proceeds on its own rules.

Language- and framework-neutral: apply each rule through the toolkit and packaging tools the project uses. Lessons specific to a toolkit or framework belong in the project's own `CLAUDE.md`, not here.

**A researched base, not yet grown from a real project.** These rules are drawn from platform vendors' guidance and widely used standards (sources at the end), not from a real desktop project yet. When the first real project disagrees with a rule, correct the rule.

## sdsi:standards

- **The UI layer is thin.** A window, view, or event handler reads input, calls one service, and renders the result. Business rules in an event handler are a finding: they can't be tested without driving the UI, and they can't be reused from a menu, a shortcut, or a command-line entry point.
- **Every way into the app is an untrusted boundary.** That includes files the user opens, drag-and-drop, the clipboard, command-line arguments, URL-scheme or deep-link activations, file-type associations, and messages from other processes (IPC between the app's own processes included). Validate each one once, at the point it enters (`sdsi:standards`). A deep link that becomes a file path or a shell command without validation is a remote-code-execution bug.
- **Opening something externally goes through one helper with an allowlist.** URLs handed to the OS's "open" mechanism are limited to an explicit allowlist of schemes (typically `https:` and `mailto:`), and never come straight from content. Without it, a crafted link runs whatever handler the OS has registered.
- **Embedded web content is treated as hostile.** When the UI renders web content, the renderer gets no direct OS or file-system access: keep it isolated and sandboxed, apply a restrictive content-security policy, don't load remote code over plain HTTP, restrict navigation and new windows, and check the sender of every message the privileged side receives. Each relaxation is written down with its reason.
- **Runs as a standard user.** No feature needs elevation or writes to machine-wide locations at runtime. A task that truly needs admin rights is split into a separate, minimal, explicitly elevated helper, never the whole app.
- **Accessible through the platform's accessibility API.** Every interactive control has an accessible name and can be reached and operated with the keyboard alone, in a logical tab order. Color is never the only signal, text contrast is at least 4.5:1, and the app follows the OS's text-size, high-contrast, and reduced-motion settings. A custom-drawn control exposes itself to the accessibility API, or screen readers can't see it.
- **Scales with the display.** Layouts, fonts, and images follow the OS scale factor, including a window moving between monitors with different scales. No pixel sizes are hard-coded on the assumption of a 100% display, and image assets come at the resolutions the platform asks for.

## sdsi:config

- **A sanctioned deviation from `sdsi:config`: three layers instead of a default file plus per-environment overrides.** There's no deploy that can mount config onto a user's machine, so:

  ```text
  admin-managed policy  >  user preferences  >  shipped defaults
  ```

  The shipped defaults are `config/default.yaml`, bundled read-only into the package. User preferences are a per-user file the app writes, holding only the keys the user changed. Managed policy is whatever the OS's managed-settings mechanism provides, and it applies only where the app supports central management. A key that policy locks is shown as locked in the UI.
- **Validation splits by layer, another deliberate deviation.** An invalid shipped default is a build bug and fails loudly in tests, never on a user's machine. If the user-preferences file is invalid or corrupt, the app doesn't refuse to start. It sets the bad file aside under a backup name, tells the user which settings were reset, logs every problem in one pass, and runs on the defaults for those keys.
- **Every file goes in the OS's designated per-user location for its kind, never in the install folder.** The kinds are settings, user data, state (window layout, recent files), cache, and logs. These locations are the platform's application-data/support directories on Windows and macOS, and the XDG base directories on Linux, which keep `config`, `data`, `state`, and `cache` separate. The install folder is read-only at runtime: packaged and sandboxed installs make writes there fail or get redirected.
- **Resolve every location through one path helper** that asks the OS, not by building paths from a hard-coded home directory or by relying on the working directory, which a launcher or package virtualization can change.
- **The update channel is a configured value** (for example `stable` or `beta`), changed through the UI, so one build can move between channels without a reinstall.

## sdsi:secrets

- **Everything shipped to a user's machine is public.** An API key, client secret, or signing key bundled into the app, its config, or its resources can be extracted. A credential that must stay secret stays on a server the app calls. The only keys that ship are public client identifiers, labeled as public where they're configured.
- **The user's own credentials go in the OS credential store**: the platform keychain, credential vault, or Secret Service, read at runtime. They never go into a preferences file, a plain local database, or the cache. Locally persisted sensitive data that doesn't fit a credential store is encrypted with the OS's per-user data-protection API.
- **Sign-in follows OAuth for native apps.** Use the system browser, not an embedded web view; use PKCE; and redirect to a loopback address, a private-use URI scheme, or a claimed HTTPS URI. Never ship a client secret.
- **Code-signing and update-signing keys never live on a developer machine or in the repository.** They're held in a hardware security module, a cloud signing service, or the CI secrets store, and only the release pipeline can use them. If one leaks, every user is exposed.

## sdsi:logging

- **Logs are written to the OS's per-user log or state location**, with size-bounded rotation, so a long-running install never fills the disk.
- **The user can find them.** A menu item or the about screen opens the log folder or copies a diagnostics bundle, which is how a support request gets evidence.
- **Logs stay on the machine unless the user agrees otherwise.** Sending diagnostics or usage data off the device requires the user's explicit consent, is off until they give it, and is redacted before it leaves (`sdsi:secrets`). Never log the contents of the user's documents, file paths under their home folder beyond what's needed, or personal data.

## sdsi:errors

- **The global error handler ends in a dialog the user can act on, never a silent exit or a raw crash.** The dialog says what happened in plain words, what the user can do, and where the log is. Technical detail goes to the log, not into the message. Errors on worker threads and in any secondary process (a renderer, a helper) reach the same handler.
- **Crash reports are collected with consent and are useful when they arrive.** Native crashes are captured as minidumps or the platform's crash report. Each release's debug symbols (or source maps) are uploaded from the release pipeline, tagged with the exact `VERSION`, so a report can be symbolicated. A crash reporter is one of the handler's pluggable reporters (`sdsi:errors`).
- **Never lose the user's work.** Save unsaved work or recovery state on a schedule and before risky operations, and offer to restore it after an abnormal exit. A crash that also destroys a document is two incidents.
- **Being offline is an expected state, not an error.** Features that need the network say they're unavailable and recover when the connection returns. Local features keep working. No error dialog for a transient network drop.

## sdsi:concurrency

- **The UI thread never blocks.** File and network I/O and any computation the user could notice moves off the UI thread. Results come back to it through the toolkit's dispatch mechanism, because UI objects are touched only from the thread that owns them.
- **Long operations show progress and can be cancelled.** Cancelling stops the work at the next safe point and leaves data consistent.
- **Closing a window is not the same as exiting.** On the OS's quit, log-off, or shutdown signal, the app saves state and drains background work within the OS's bounded grace period (`sdsi:concurrency`). If it handles the OS's session-end or restart notification, an installer or update can close it cleanly instead of forcing a reboot.
- **Single instance is a stated decision.** If the app allows one instance, a second launch passes its arguments (a file to open, a deep link) to the running instance through IPC and exits. That IPC channel is an input boundary (`sdsi:standards` above).

## sdsi:testing

- **CI builds and tests on every target OS and architecture**, not only the developer's. Path handling, file locking, case sensitivity, and line endings differ between them.
- **The packaged artifact is tested, not just the source.** Install, launch, upgrade from the previous release with real user data in place, and uninstall the signed installer on a clean machine or VM. Upgrade with existing preferences and data is where desktop regressions hide.
- **UI automation drives the app through the accessibility tree**, the same interface assistive technology uses, with a few end-to-end tests for the critical flows. Automated accessibility checks on key screens gate merges.
- **A short manual matrix covers what automation can't**: high-contrast mode, a large text size, a high-DPI display and moving between monitors, keyboard-only use, and a screen reader on the main flow. Run it before a release and record the result.
- **The update path gets its own test.** Install release N-1, update to N through the real update mechanism, and confirm a tampered or wrongly signed update is rejected.

## sdsi:dependencies

- **A bundled runtime or embedded browser engine is a dependency, with its own update cadence.** When it falls behind its supported line, security fixes stop reaching users. Track it, scan it, and update it like any other dependency.
- **Native libraries are pinned per OS and architecture**, and the lockfile covers each target, so every platform build resolves the same versions.
- **Every dependency that ships to users is a license obligation.** Keep the third-party notices the licenses require inside the app (an about or licenses screen), generated from the lockfile.

## sdsi:docs

- **The README states supported OS versions and architectures**, how to install and uninstall on each, and where the app keeps settings, data, and logs on each OS. Support needs this before anything else.
- **A user-facing release-notes view** (in the app or linked from it) is generated from `CHANGELOG.md`, never written separately.

## sdsi:versioning

- **One version everywhere the OS shows it.** The installer metadata, the executable's version resource or bundle version, the package manifest, and the about screen all come from `VERSION` through the release script's `version_files`. The about screen also shows the build's OS and architecture.
- **User data has its own schema version.** On first launch after an upgrade, the app migrates the data forward and keeps a backup. If it meets data from a newer version than itself (after a downgrade), it refuses to overwrite that data.
- **The update mechanism rejects older versions.** An updater never installs a version lower than the one running unless the user explicitly asks for a downgrade. That closes off rollback attacks.

## sdsi:deploy

- **The deploy target is "distributed package."** Decide the shape per OS and write it down: a store package, a signed installer, a platform package format, or a portable archive. Each one decides how updates, uninstall, and sandboxing work.
- **A sanctioned deviation from `sdsi:deploy`'s "config stays out of the built artifact."** The shipped defaults (`config/default.yaml`) are bundled read-only, because nothing can mount config onto a user's machine; the user and policy layers (`sdsi:config` above) are what stay outside the package.
- **Every executable and installer is code-signed with a consistent publisher identity and timestamped.** That covers helper binaries and bundled libraries as well as the installer. On macOS, distribution outside the store also requires the hardened runtime and notarization. An unsigned or untimestamped build is never published.
- **Updates are authenticated end to end.** Updates are served over HTTPS, the update metadata and payload are signed with a key separate from transport TLS, and the app verifies the signature before installing anything. The design defends against the attacks described by The Update Framework: arbitrary or mismatched packages, rollback, and freeze.
- **Promote the signed artifact, never rebuild it.** The exact binaries tested on the beta channel are the ones published to stable (`sdsi:versioning`).
- **Install as a standard user where the platform allows it**, and support a silent, unattended install for managed deployment. The installer brings every prerequisite that isn't on a clean OS image.
- **Uninstall removes everything the installer put down**: files, shortcuts, file associations, URL-scheme registrations, scheduled tasks, and registry or desktop entries. User data is left alone unless the user chooses to remove it. Upgrading from release N-1 to N leaves nothing behind from N-1.
- **Integrate with the desktop through the platform's declarative mechanism**: a package manifest, a bundle property list, or a desktop entry file and its MIME registration. Integration is declared, not done by writing shell or registry hooks at runtime, so it installs and uninstalls cleanly.

## Sources

- Microsoft Learn — Prepare to package a desktop application (MSIX): https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-prepare
- Microsoft Learn — Understanding how packaged desktop apps run on Windows: https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes
- Microsoft Learn — Code signing options for Windows app developers: https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options
- Microsoft Learn (archive) — Everything you need to know about Authenticode code signing: https://learn.microsoft.com/en-us/archive/blogs/ieinternals/everything-you-need-to-know-about-authenticode-code-signing
- Microsoft Learn — Accessibility checklist (Windows apps): https://learn.microsoft.com/en-us/windows/apps/design/accessibility/accessibility-checklist
- Microsoft Learn — High DPI desktop application development on Windows: https://learn.microsoft.com/en-us/windows/win32/hidpi/high-dpi-desktop-application-development-on-windows
- Microsoft Learn — Keep the UI thread responsive: https://learn.microsoft.com/en-us/windows/uwp/debug-test-perf/keep-the-ui-thread-responsive
- Microsoft Learn — Restart Manager: https://learn.microsoft.com/en-us/windows/win32/rstmgr/restart-manager-portal
- Microsoft Learn — Handling passwords (Win32 security best practices): https://learn.microsoft.com/en-us/windows/win32/secbp/handling-passwords
- Apple Developer — Notarizing macOS software before distribution: https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution
- Apple Developer — macOS Library directory details (File System Programming Guide): https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/MacOSXDirectories/MacOSXDirectories.html
- Apple Human Interface Guidelines — Accessibility: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Apple Platform Security — Keychain data protection: https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
- freedesktop.org — XDG Base Directory Specification: https://specifications.freedesktop.org/basedir/latest/
- freedesktop.org — Desktop Entry Specification: https://specifications.freedesktop.org/desktop-entry/latest/
- freedesktop.org — Secret Service API: https://specifications.freedesktop.org/secret-service/latest-single/
- The Update Framework — Security (attacks and design principles): https://theupdateframework.io/docs/security/
- Sparkle — Documentation (EdDSA-signed updates, HTTPS): https://sparkle-project.org/documentation/
- Electron — Security checklist: https://www.electronjs.org/docs/latest/tutorial/security
- IETF RFC 8252 — OAuth 2.0 for Native Apps: https://datatracker.ietf.org/doc/html/rfc8252
- OWASP — Desktop App Security Top 10: https://owasp.org/www-project-desktop-app-security-top-10/
- Sentry — Minidumps (crash reports and debug symbols): https://docs.sentry.io/platforms/native/guides/minidumps/
