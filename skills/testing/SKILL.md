---
name: testing
description: >
  SDSI's testing standard, language-neutral — every test and test config
  under one tests/ folder, the language's standard test runner, mocking
  external systems in unit tests, separately marked integration tests, the
  full unit/integration/end-to-end pyramid, CI gating, and coverage as a
  signal where a test that can't name its regression counts as zero. Use
  when writing tests, setting up a test suite, or reviewing test quality.
  Reads sdsi:core first. Triggers on "/sdsi:testing", "tests", "test
  coverage".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: Testing

Before anything else, read `../core/SKILL.md` and run its steps.

## Rules

- **Every test, fixture, test data file, and test-tool config lives under one `tests/` folder** — nothing scattered next to the source, no per-module test folder inside the source tree. Mirroring the source structure inside `tests/` is fine. Where a language's convention strongly requires colocated tests, follow the language and record the deviation in `CLAUDE.md` (core §1, Step 4).
- **Use the language's standard or dominant test runner** — don't introduce a second one.
- **Unit tests cover business logic and mock external systems** (APIs, databases, cloud services).
- **Integration tests that hit real dev/sandbox endpoints are welcome**, but are marked so they run selectively, not on every commit.
- **Aim for the full pyramid** — unit, integration, and end-to-end. Which layers matter varies by project; a missing layer is a stated decision, not a silent gap.
- **Tests run in CI and must pass before merge.**
- **Coverage is a signal, not a target.** A test that only pads the number — a snapshot with no real assertion, a tautology, a test that mocks the thing it claims to test — counts as zero. If you can't name the regression a test would catch, delete it.
- **A bug fix starts with a failing test** that fails for the expected reason, then passes without being edited (`sdsi:workflow`). Every incident fix earns a permanent regression test.
- **Something protecting a real external behavior** (a rotation, a retry, a paging walk) is tested against the real thing at least once, deliberately — a mock only proves the method was called.

## Review checklist

Tests or test config outside `tests/` · two test runners · unit tests calling real external systems · unmarked slow/integration tests in the default run · assertions that can't fail · a test that mocks what it's testing · a bug fix with no regression test · no CI gate.
