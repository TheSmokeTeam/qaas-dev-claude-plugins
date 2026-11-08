---
description: Interview the developer, prepare and independently review an exact QaaS implementation plan, then request explicit developer approval before code changes.
argument-hint: "<feature or bugfix request>"
---

Prepare a QaaS Change Specification and Implementation Plan for: $ARGUMENTS

1. Apply `qaas-platform-overview` and build a Know QaaS Context Brief covering
   platform scope, ecosystem location, dependencies, extension model, release
   ripple, authorities, and known unknowns.
2. Research codebase facts, then interview the developer about decisions. Use
   the model-invoked `grilling` skill when available; otherwise follow the
   `plan-qaas-change` interview protocol. Require confirmation of shared
   understanding before drafting.
3. Apply Ponytail's active minimality discipline when available; otherwise use
   the built-in smallest-complete-change gate. Do not install or configure an
   optional plugin.
4. Pass the raw request, complete brief, and numbered developer decisions to
   `plan-qaas-change`; do not implement or edit production files.
5. Delegate source investigation and the first draft to `qaas-change-planner`.
6. Delegate the finished draft, context brief, decisions, and raw request to
   `qaas-plan-reviewer` in a fresh context. Do not pass private planner
   conclusions.
7. Resolve findings and re-review material revisions.
8. Present the reviewed revision as `AWAITING_APPROVAL` and ask the developer to
   explicitly approve it or request changes. This command never implements.
9. Mark the plan `APPROVED` only after the developer approves that exact revision.

An `APPROVED` plan must record the interview, reviewer verdict, and developer
approval for the matching plan revision, and must name repositories, commits, paths, symbols,
test-first steps, acceptance criteria, verification commands, cross-repo impact,
and release work. Never guess missing evidence.
