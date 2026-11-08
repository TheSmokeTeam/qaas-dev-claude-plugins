---
name: develop-qaas-change
description: >-
  Orchestrate a QaaS platform feature, bugfix, or refactor from ecosystem
  understanding through developer interview, exact reviewed plan, explicit
  approval, test-first implementation, independent verification, and optional
  release handoff. Use when the developer asks to build, add, fix, change, or
  implement QaaS behavior and expects the complete lifecycle rather than only a
  plan or knowledge answer.
---

# Develop a QaaS Change

Own the end-to-end lifecycle while delegating each stage to its specialist. Do
not duplicate a stage's detailed rules here.

## Lifecycle

1. **Enter understanding once.** Apply `qaas-platform-overview` and pass its Know
   QaaS Context Brief to the next owner.
2. **Delegate planning once.** Apply `plan-qaas-change` and consume its returned
   state. That skill owns research, interview, drafting, independent review, and
   the developer approval record. If it returns `NEEDS_DECISION`, `BLOCKED`, or
   `AWAITING_APPROVAL`, preserve the original implementation request and stop.
   On the developer's next message, resume that same planning owner to record the
   decision; do not independently present or reinterpret the approval gate.
3. **Delegate delivery once.** Only after planning returns `APPROVED`, apply
   `implement-qaas-change` and consume its result. That skill owns freshness,
   test-first execution, the domain overlay, independent verification, and the
   release-authorization boundary, including any call to `release-and-mirror`.

The orchestrator transitions between owners. It never repeats a specialist's
interview, review, approval, verification, or release action.

## State transitions

```text
request
  -> Know QaaS brief
  -> NEEDS_DECISION | BLOCKED | reviewed revision
  -> AWAITING_APPROVAL
  -> APPROVED
  -> implementing
  -> verified | partially-verified | not-verified
  -> released (only when authorized)
```

Any material plan change creates a new revision and digest and returns to
technical review. Any source-baseline change makes the plan `STALE`; replacing
the baseline also requires a new revision, review, and developer approval.
Reviewer approval never substitutes for developer approval, and only a
`verified` verifier verdict permits completion or release.

## Handoff rules

- Carry the raw request, Know QaaS brief, developer decisions, plan revision and
  digest, repository baselines, approval provenance, and unresolved findings
  between stages.
- Stop at the first unmet gate. Do not silently weaken a stage to keep moving.
- A plan-only request ends after the approval decision; it does not imply
  implementation authorization.
- An implementation request resumes after approval without requiring the
  developer to restate the original request.

## Done when

The requested outcome is implemented against the approved revision, independently
verified with real evidence, and either released as authorized or handed off with
the exact remaining release work.
