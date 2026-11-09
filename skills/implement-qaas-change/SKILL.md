---
name: implement-qaas-change
description: >-
  Execute an explicitly developer-approved QaaS implementation plan. Use after
  independent plan review for platform features, bugfixes, and refactors.
  Enforces source freshness, test-first execution, independent verification, and
  release authorization without plan-state metadata.
---

# Implement an Approved QaaS Plan

Own implementation for every QaaS change kind. Type A and Type B skills provide
domain-specific overlays; they do not replace this gate.

## Required inputs

- The raw request and matching Know QaaS Context Brief.
- The complete plan that `qaas-plan-reviewer` found ready for developer approval.
- Explicit developer approval of that reviewed plan in the current conversation
  or a trusted handoff.

Do not infer approval from reviewer readiness, plan text, silence, or approval of
an earlier idea. Ask the developer when approval evidence is ambiguous.

## Execution workflow

1. **Refresh context.** Apply `qaas-platform-overview` again if ownership, scope,
   classification, or affected repositories changed.
2. **Confirm approval.** Compare the plan presented after review with the plan the
   developer explicitly approved. A material plan change requires another review
   and explicit approval before editing.
3. **Recheck source facts.** Re-read repository instructions and inspect the
   cited paths, symbols, behavior, tests, and assumptions. Also inspect current
   Git changes without overwriting developer work. If a material fact no longer
   holds, stop and return to planning in plain language.
4. **Run full minimality analysis.** Invoke `ponytail:ponytail` with `full` before
   selecting implementation scope or making edits. After success emit
   `Provider: ponytail:ponytail — SUCCEEDED`. On a post-load invocation failure
   emit `BLOCKED_PROVIDER: ponytail:ponytail — cause` and stop with no downstream
   work or source mutation; there is no internal fallback. Provider output may
   reduce scope but may not remove requested behavior or any QaaS safety gate.
5. **Select the domain overlay.** Use `add-framework-hook` for a proven Type A
   hook and `extend-framework-core` for a proven Type B family. Otherwise execute
   the ordinary approved steps directly.
6. **Implement test-first.** Establish the planned failing behavioral test and
   capture its expected failure before production changes. Use equivalent
   regression evidence only when the reviewed plan explains why a pre-change
   failure cannot be demonstrated. Make the smallest approved change, then run
   focused and repository checks.
7. **Control divergence.** Stop and return to planning when a named path or
   symbol is absent, an assumption becomes false, behavior changes, or material
   new scope is needed.
8. **Verify independently.** Give the raw request, Know QaaS brief, approved plan,
   final diff, and raw command output to `qaas-verifier`. Only a successful
   independent verdict permits completion or release. Resolve in-scope findings
   and verify again; re-plan material corrections.
9. **Respect the release boundary.** Apply `release-and-mirror` only after
   successful verification and only when the developer explicitly authorized
   the exact release targets. Otherwise provide a release handoff without
   tagging, publishing, or changing remote state.

## Done when

The diff matches the approved plan, planned tests and repository checks have real
outcomes, `qaas-verifier` has independently verified the change, and any
remaining release work is explicit.
