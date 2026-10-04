# SDSI

- [ ] #5 Grow `sdsi:concurrency` from a real project — only its shutdown rules come from practice so far
- [ ] #11 Add an audit trail to `sdsi:logging` — security-relevant decisions (authorization grants and denials, permission changes) recorded as their own replayable stream, separate from application logs; read `sdsi:logging` and `sdsi:errors` in full first — from the Simple-AI-DLC review; matters most for larger organizations
- [ ] #16 Review and expand the companion instructions (`ref/web.md`, `cli.md`, `mw.md`, `lib.md`, `desktop.md`, `mobile.md`) — they're a researched base; confirm or correct each rule against real projects, trim sections over ~7 bullets, and settle the open points the research flagged (CLI secrets via environment variables, where `--json` errors go, mw's schema-change-is-MAJOR rule, mobile pinning)


---

## Done

- [x] #1 Create the GitHub repos `jimmydagher/sdsi-plugin` and `jimmydagher/claude-marketplace` and push both — the marketplace resolves the plugin from GitHub — completed 2026-09-23 · VERSION 1.0.0
- [x] #2 Add a review skill (from the `code-reviewer` plugin) as the "review first" path of core's review-or-apply question — core currently does the findings pass itself — completed 2026-09-23 · VERSION 1.1.0
- [x] #12 Move non-essential files from the root to another folder. — completed 2026-10-03 · VERSION 1.3.0
- [x] #3 Retire `sdsi/` and `code-reviewer/` from the `claude-plugins` monorepo and its `jimmy-plugins` marketplace once the new marketplace is live; point `code-reviewer`'s `sdsi:base` calls at `sdsi:core`
- [x] #13 When updating documentation, in the project update the source of truth not appending, do keep a documentation change log separate on what has been appended. — completed 2026-10-03 · VERSION 1.3.2
- [x] #14 for the web.md companion, when deploying a GUI environment, make sure that the version number of the software is showing to the user in several key parts of the sofware. — completed 2026-10-03 · VERSION 1.3.2
- [x] #6 Add a CI check that repeats the changelog rule server-side, where `--no-verify` can't reach — closed 2026-10-03 without shipping: it assumes GitHub Actions, and many projects use Azure DevOps or another git host; revisit when someone requests it
- [x] #10 Have `SPEC.md`/`PLAN.md` name the non-functional requirements (performance, availability, security) and the testing and monitoring strategy, and have `sdsi:deploy` verify the deployed system against them — from the Simple-AI-DLC review; matters most for larger organizations — completed 2026-10-03 · VERSION 1.3.3
- [x] #4 Grow `ref/cli.md` from a real CLI project — it's still a generic draft — completed 2026-10-04 · VERSION 1.3.5
- [x] #7 Grow `ref/web.md` from real web projects — a seed; the Django-specific lessons from `flammeau` (manage.py placement, `app_label`, the `helpers` app name) belong in that project's `CLAUDE.md` — completed 2026-10-04 · VERSION 1.3.5
- [x] #8 Grow `ref/mw.md` from a second middleware project — so far distilled from `ariel` alone — completed 2026-10-04 · VERSION 1.3.5
- [x] #9 Add companions for more project types (e.g. library, desktop, mobile) as real projects need them — completed 2026-10-04 · VERSION 1.3.5
- [x] #15 for `ref/web.md` include the ability to always have a health endpoint to check the services, basic and one full using an admin key. — completed 2026-10-04 · VERSION 1.3.5
