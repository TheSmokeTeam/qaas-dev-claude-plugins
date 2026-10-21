---
description: Route a QaaS platform task with graph evidence to the right repo(s) and skill — which repo to open, which instructions/docs to read, and whether it is a Type A or Type B change.
argument-hint: "<task>  e.g. 'add a Kafka retry assertion' | 'add an Oracle protocol' | 'cut a Framework release'"
---

Route this QaaS platform-development task: $ARGUMENTS

Apply the `qaas-platform-overview` skill's router and Type A/B decision gate:
1. Apply `find-qaas-knowledge`: query the available `qaas-graph` code or evaluated
   dependency view, then verify the result in source/docs.
2. Identify the owning repo(s) under https://github.com/TheSmokeTeam.
3. If it is an extension, classify Type A (reflection hook → `add-framework-hook`)
   vs Type B (compiled core → `extend-framework-core`).
4. Name the applicable in-tree `AGENTS.md`, `CLAUDE.md`, `project_specs.md`, or
   `README.md` to read first.
5. If anything is unknown, say what is missing — do not invent. (docs-or-silence)
