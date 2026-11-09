---
name: develop-qaas-change
description: >-
  Orchestrate a QaaS platform feature, bugfix, or refactor from ecosystem
  understanding through developer interview, a short reviewed plan, explicit
  approval, test-first implementation, independent verification, and optional
  release handoff. Use when the developer expects the complete change lifecycle.
---

# Develop a QaaS Change

Own the end-to-end lifecycle while delegating each stage to its specialist.

## Lifecycle

1. **Request.** Preserve the raw request and whether the developer asked only for
   a plan or for the complete change lifecycle.
2. **Know QaaS.** Apply `qaas-platform-overview` and pass its context brief
   forward.
3. **Research/design.** Apply `plan-qaas-change` to establish source-backed facts,
   integration seams, scope, and design options.
4. **Interview.** Continue `plan-qaas-change` to resolve material
   developer-owned decisions after research.
5. **Create short plan.** Continue `plan-qaas-change` to produce the smallest
   evidence-backed, test-first plan.
6. **Review.** Have `qaas-plan-reviewer` check the complete plan independently.
   Requested changes return to plan creation and review; return to research or
   interview too when facts or developer-owned decisions changed.
7. **Developer approves.** Present the reviewed plan unchanged and pause until
   the developer explicitly approves it. Keep the original request so the same
   task can resume naturally.
8. **Implement and test.** Apply `implement-qaas-change` to recheck source facts,
   implement test-first, and run focused and repository checks.
9. **Verify.** Have `qaas-verifier` independently compare the request, plan,
   diff, and observed check output. Resolve in-scope findings and verify again;
   return material changes to planning.
10. **Release if authorized.** Apply `release-and-mirror` only after successful
    verification and explicit authorization for the exact release targets.

Reviewer readiness never substitutes for developer approval. If the plan changes
materially, review the changed plan and ask the developer to approve it again.
Only successful independent verification permits completion or release.

## Handoff rules

- Carry the raw request, Know QaaS brief, confirmed decisions, reviewed plan,
  developer approval evidence, and unresolved findings between stages.
- Stop at the first unmet gate and explain what is needed in plain language.
- A plan-only request never authorizes implementation.
- Release or publishing requires separate explicit authorization for the exact
  targets.

## Done when

The approved outcome is implemented, checked against the reviewed plan,
independently verified with real evidence, and either released as authorized or
handed off with the remaining release work stated clearly.
