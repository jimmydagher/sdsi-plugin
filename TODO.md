# TODO

- [ ] #2 Add a review skill (from the `code-reviewer` plugin) as the "review first" path of core's review-or-apply question — core currently does the findings pass itself
- [ ] #3 Retire `sdsi/` and `code-reviewer/` from the `claude-plugins` monorepo and its `jimmy-plugins` marketplace once the new marketplace is live; point `code-reviewer`'s `sdsi:base` calls at `sdsi:core`
- [ ] #4 Grow `sdsi:cli` from a real CLI project — it's still a generic draft
- [ ] #5 Grow `sdsi:concurrency` from a real project — only its shutdown rules come from practice so far
- [ ] #6 Add a CI check that repeats the changelog rule server-side, where `--no-verify` can't reach

---

## Done
- [x] #1 Create the GitHub repos `jimmydagher/sdsi-plugin` and `jimmydagher/claude-marketplace` and push both — the marketplace resolves the plugin from GitHub — completed 2026-09-23 · VERSION 1.0.0
