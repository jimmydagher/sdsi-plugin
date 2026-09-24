---
name: all
description: >
  Runs the full SDSI standard against a project, every topic in core's
  fixed order — workflow, standards, config,
  secrets, logging, errors, concurrency, testing, dependencies, docs,
  versioning, deploy — in review mode (one combined findings report) or
  apply mode (fix step by step). Use when the human wants all the core
  standards applied or reviewed at once ("apply SDSI to this project", "run
  all the standards", "full SDSI review"), or when scaffolding a brand-new
  project. Slow and token-heavy by design; best suited to small projects.
  Also the entry a skill in another plugin invokes by name for the full
  standard. Triggers on "/sdsi:all" or "sdsi all".
argument-hint: "[--review|--apply] [path]"
---

# SDSI: All

Before anything else, read `../core/SKILL.md` — it defines the steps, the
order, the modes, and the rules this skill runs.

## How the run goes

1. **Core's steps, once for the whole run** (core §1): say what's running,
   load the project profile (language, and the project type — detected from
   the code or asked), read the project-type companion once, and resolve the
   mode — review or apply — **once**, not once per topic.
2. **Walk core §4's table in order**, top to bottom. For each row, read that
   skill's `SKILL.md` (`../<name>/SKILL.md`) and add the companion's section
   for that skill, if it has one. Before each step, tell the human which it
   is and whether the companion adds anything ("Step 5/12 — `sdsi:logging`
   + web").
3. **Topic questions are asked when their step comes up** (e.g.
   `sdsi:deploy` asks the deploy target at step 12) and recorded in the
   profile like any other answer.

## Review mode

Follow `../../ref/findings.md` with every step as a lens, in core's order:
scan all steps first, then build **one** catalog for the whole run
(deduplicated across steps), present it grouped by step, and ask what's next
once. Export goes to `docs/reviews/YYYY-MM-DD-sdsi-all.md`. When applying the
chosen findings, apply them in core's order — earlier steps are the
foundation later ones build on.

## Apply mode

Apply each step's rules before moving to the next, so later steps build on a
corrected foundation. Verify at the end — run the tests, the build, or the
program — and show the evidence. Write the changelog notes as each step's
changes are made; never commit (`sdsi:versioning`).

## New, empty project

There's nothing to review, so the run applies. Step 1 (`sdsi:workflow`)
drives: its "Starting a new project" sequence brainstorms, asks the
decisions, writes the planning artifacts, and scaffolds the skeleton. Steps
2–12 then fill in each part of that skeleton.
