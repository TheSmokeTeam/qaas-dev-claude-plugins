---
description: Prepare and independently review an exact spec-driven implementation plan for a QaaS platform feature or bugfix before editing code.
argument-hint: "<feature or bugfix request>"
---

Prepare a QaaS Change Specification and Implementation Plan for: $ARGUMENTS

1. Apply `qaas-platform-overview` and build a Know QaaS Context Brief covering
   platform scope, ecosystem location, dependencies, extension model, release
   ripple, authorities, and known unknowns.
2. Pass the raw request and the complete brief to `plan-qaas-change`; do not
   implement or edit production files.
3. Delegate source investigation and the first draft to `qaas-change-planner`.
4. Delegate the finished draft, context brief, and raw request to
   `qaas-plan-reviewer` in a fresh context. Do not pass private planner
   conclusions.
5. Resolve findings and re-review material revisions.
6. Return the complete plan with exactly one gate: `APPROVED`,
   `NEEDS_DECISION`, `BLOCKED`, or `STALE`.

An `APPROVED` plan must name verified repositories, commits, paths, symbols,
test-first steps, acceptance criteria, verification commands, cross-repo impact,
and release work. Never guess missing evidence.
