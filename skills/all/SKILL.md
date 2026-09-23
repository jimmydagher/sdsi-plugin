---
name: all
description: >
  Runs the full SDSI standard against a project, every topic in core's
  fixed order — workflow, the project-type layout, standards, config,
  secrets, logging, errors, concurrency, testing, dependencies, docs,
  versioning, deploy. Use when the human wants all the core standards
  applied or reviewed at once ("apply SDSI to this project", "run all the
  standards", "full SDSI review"), or when scaffolding a brand-new project.
  Also the entry a skill in another plugin invokes by name for the full
  standard. Triggers on "/sdsi:all" or "sdsi all".
---

# SDSI: All

Before anything else, read `../core/SKILL.md` — it defines the steps, the
order, and the rules this skill runs.

## How the run goes

1. **Core's steps, once for the whole run** (core §1): say what's running,
   load or ask the project profile (language, project type), and — if code
   already exists — ask **review first or just apply** once, not once per
   topic.
2. **Walk core §4's table in order**, top to bottom. For each row, read that
   skill's `SKILL.md` (`../<name>/SKILL.md`) and apply it. For row 2, read
   only the project-type skill the profile names; if the type is "other",
   apply core §3's universal invariants and say so. Before each step, tell
   the human which step it is (e.g. "Step 6/13 — `sdsi:logging`").
3. **Topic questions are asked when their step comes up** (e.g.
   `sdsi:deploy` asks the deploy target at step 13), and recorded in the
   profile like any other answer.
4. **Review mode:** collect findings from every step into one table,
   grouped by step, each with rule, `file:line`, severity, and proposed fix.
   Present it once at the end and let the human pick what to apply. Order
   the fixes in core §4's order when applying them — earlier steps are the
   foundation later ones build on.
5. **Apply mode:** apply each step's changes before moving to the next, so
   later steps build on a corrected foundation. Verify at the end (core §2,
   "double-check your work") — run the tests, the build, or the program —
   and show the evidence.
6. **Close out** through `sdsi:versioning`'s release chain: every change
   gets its bullet in `CHANGELOG.md`'s Unreleased section, referencing any
   `TODO.md` item it closes. The human commits when satisfied; the hooks do
   the rest.

## New, empty project

Run the same order, but step 1 (`sdsi:workflow`) drives: its "Starting a new
project" sequence brainstorms, asks the decisions, writes the planning
artifacts, and scaffolds the skeleton. Steps 2–13 then fill in each part of
that skeleton rather than reviewing code that doesn't exist yet.
