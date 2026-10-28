---
description: Route a QaaS platform task to the right repo(s) and skill — which repo to open, which CLAUDE.md to read, and whether it is a Type A or Type B change.
argument-hint: "<task>  e.g. 'add a Kafka retry assertion' | 'add an Oracle protocol' | 'cut a Framework release'"
---

Route this QaaS platform-development task: $ARGUMENTS

Apply the `qaas-platform-overview` skill's router and Type A/B decision gate:
1. Identify the owning repo(s) under https://github.com/TheSmokeTeam.
2. If it is an extension, classify Type A (reflection hook → `add-framework-hook`)
   vs Type B (compiled core → `extend-framework-core`).
3. Name the in-tree `CLAUDE.md` / `project_specs.md` to read first.
4. If anything is unknown, say what is missing — do not invent. (docs-or-silence)
