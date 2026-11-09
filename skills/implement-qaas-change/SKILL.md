---
name: implement-qaas-change
description: >-
  Execute an explicitly developer-approved QaaS implementation plan. Use after
  planning when a QaaS feature, bugfix, or refactor is ready for code changes,
  including ordinary Runner, Mocker, PackageMirror, docs, and existing-behavior
  work as well as Type A hooks and Type B Framework extensions. Enforces exact
  revision approval, source freshness, test-first execution, plan conformance,
  independent verification, and release authorization.
---

# Implement an Approved QaaS Plan

Own implementation for every QaaS change kind. Type A and Type B skills provide
domain-specific overlays; they do not replace this gate.

## Required inputs

- The raw request and Know QaaS Context Brief.
- A plan whose status is `APPROVED`.
- `review.verdict: APPROVE` and
  `review.reviewed_revision == plan_revision` and
  `review.reviewed_digest == plan_digest`.
- `developer_approval.status: APPROVED` and
  `developer_approval.approved_revision == plan_revision` and
  `developer_approval.approved_digest == plan_digest`.
- Repository commit and worktree fingerprints captured by the approved plan.

Stop on a missing input, `DRAFT`, `AWAITING_APPROVAL`, `NEEDS_DECISION`,
`BLOCKED`, or `STALE`.

## Execution workflow

1. **Rebuild context.** Apply `qaas-platform-overview` if the supplied brief no
   longer matches the request or affected repositories.
2. **Validate the plan and approval provenance.** Run the bundled
   `${CLAUDE_PLUGIN_ROOT}/skills/plan-qaas-change/scripts/validate_plan.py`.
   Reject a revision, content-digest, review, or approval mismatch. Plan metadata
   records approval; it is not proof by itself. Before the first production edit,
   verify the `qaas-plan-reviewer` result and the developer's exact revision and
   digest approval in the current conversation or a trusted handoff. If the
   reviewer result is unavailable, rerun the independent reviewer. If only the
   file claims developer approval, ask the developer to reaffirm it.
3. **Check freshness.** Recompute every repository baseline with the bundled
   `repo_snapshot.py`, passing the expected repository identity, commit, and
   fingerprint. If any value differs, set the plan to `STALE` and return to
   `plan-qaas-change`. Replacing any captured baseline creates a new revision and
   digest and requires fresh technical review and developer approval.
4. **Load local authority.** Read each repository's current `CLAUDE.md` and
   relevant `project_specs.md`. Stop if they contradict the plan.
5. **Run full minimality analysis.** Explicitly invoke `ponytail:ponytail` with
   `full` before selecting implementation scope or making edits. Emit
   `Provider: ponytail:ponytail — SUCCEEDED` after success. On a post-load
   invocation failure emit `BLOCKED_PROVIDER: ponytail:ponytail — cause` and
   stop with no downstream work or source mutation; there is no internal
   fallback. Ponytail may reduce accidental scope but may not remove requested
   behavior or any QaaS gate.
6. **Select the domain overlay.** Use `add-framework-hook` for a verified Type A
   hook and `extend-framework-core` for a verified Type B family. Otherwise
   execute the approved ordinary-change steps directly.
7. **Execute in approved order.** Establish the planned failing behavioral test
   first and capture its expected failure before production changes. An exception
   is valid only when the reviewed plan documents why a pre-change failure cannot
   be demonstrated and names equivalent regression evidence. Implement the
   smallest approved behavior change, then run focused and full checks from the
   repository instructions.
8. **Control divergence.** Stop and return to planning when a named path or
   symbol is absent, an assumption becomes false, requested behavior changes,
   or implementation requires material scope not present in the plan. A material
   plan edit invalidates review and developer approval.
9. **Verify independently.** Delegate the final diff, approved plan, and raw
   command output to `qaas-verifier`. Only `verified` permits completion or a
   release. On `partially-verified` or `not-verified`, stop for an in-plan fix,
   re-planning, or an explicit incomplete handoff, then verify again.
10. **Handle release scope.** Apply `release-and-mirror` only after `verified` and
   when the approved plan records
   `release.authorization: AUTHORIZED_AFTER_VERIFICATION`, or the developer
   separately authorizes the exact targets. Otherwise report the release handoff
   without tagging or publishing.

Provider output never bypasses QaaS evidence, the approved plan, repository
instructions, tests, independent verification, or release authorization.

## Done when

The diff matches the approved revision and digest, planned tests and repository
checks have real outcomes, the independent verifier returned `verified`, and any
remaining release work is explicit.
