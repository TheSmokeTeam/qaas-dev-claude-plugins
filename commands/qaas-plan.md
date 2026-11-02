---
description: Prepare and independently review an exact spec-driven implementation plan for a QaaS platform feature or bugfix before editing code.
argument-hint: "<feature or bugfix request>"
---

Prepare a QaaS Change Specification and Implementation Plan for: $ARGUMENTS

1. Apply `qaas-platform-overview` and reuse any existing Know QaaS evidence.
2. Apply `plan-qaas-change` without implementing or editing production files.
3. Delegate source investigation and the first draft to `qaas-change-planner`.
4. Delegate the finished draft plus the raw request to `qaas-plan-reviewer` in a
   fresh context. Do not pass private planner conclusions.
5. Resolve findings and re-review material revisions.
6. Return the complete plan with exactly one gate: `APPROVED`,
   `NEEDS_DECISION`, `BLOCKED`, or `STALE`.

An `APPROVED` plan must name verified repositories, commits, paths, symbols,
test-first steps, acceptance criteria, verification commands, cross-repo impact,
and release work. Never guess missing evidence.
