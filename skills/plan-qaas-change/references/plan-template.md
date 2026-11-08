# QaaS Change Plan Schema

Use this schema exactly. Keep small changes concise inside the same nine
sections; do not remove the evidence, interview, review, approval, or
traceability gates.

```markdown
---
schema_version: "4"
plan_revision: 1
plan_digest: null | sha256:<64 lowercase hexadecimal characters>
change_id: qaas-<short-slug>
title: <feature, bugfix, or refactor title>
change_kind: feature | bugfix | refactor
complexity: small | standard | cross-repo
status: DRAFT | NEEDS_DECISION | BLOCKED | AWAITING_APPROVAL | APPROVED | STALE
qaas_classification: type-a | type-b | existing-behavior | not-applicable | undetermined
repositories:
  - name: TheSmokeTeam/<repo>
    checkout: <absolute checkout path>
    inspected_commit: <40-character commit SHA>
    worktree_fingerprint: sha256:<64 hexadecimal characters>
review:
  verdict: PENDING | APPROVE | REVISE | BLOCK
  reviewed_revision: null | <plan revision>
  reviewed_digest: null | <plan digest>
  evidence: Pending | <qaas-plan-reviewer result reference>
developer_approval:
  status: PENDING | APPROVED | CHANGES_REQUESTED
  approved_revision: null | <plan revision>
  approved_digest: null | <plan digest>
  evidence: Pending | <developer message or trusted handoff reference>
release:
  authorization: NOT_AUTHORIZED | AUTHORIZED_AFTER_VERIFICATION
  targets: <explicit packages, workflows, and documentation handoff, or N/A>
---

# QaaS Change Specification and Implementation Plan

## 1. Context and Request

### Know QaaS Context Brief

#### Platform scope
#### Ecosystem location
#### Dependency position
#### Extension model
#### Release ripple
#### Authority map
#### Known unknowns

### Problem or use case

### Requested outcome and user-visible behavior

### Constraints and scope

## 2. Developer Decisions and Non-goals

### Shared understanding

Confirmed by the developer: Yes | No

### Decisions

| ID | Decision question | Agent recommendation | Developer decision | Rationale |
|---|---|---|---|---|
| D-1 | ... | ... | ... | ... |

If research leaves no material developer-owned decision, replace the table row
with: `No material developer-owned decisions after research.` Shared-understanding
confirmation is still required.

### Non-goals and rejected alternatives

Record rejected scope and the minimality rationale. This section contains
developer decisions, not facts the agent could have researched.

## 3. Current State and Evidence

| ID | Kind | Claim | Evidence | Confidence |
|---|---|---|---|---|
| E-1 | fact | ... | `repo/path:line` | verified |

Describe the current control/data flow. For a bugfix, include reproduction,
observed and expected results, failure mechanism, root cause, and the regression
test seam. For a feature or refactor, include use cases, integration seam,
sibling convention, material alternatives, and compatibility implications.

## 4. Desired State and Acceptance Criteria

### Invariants

### Acceptance criteria

- AC-1: Given ..., when ..., then ...
- AC-2: ...

## 5. Impact, Alternatives, and Minimality

### Impact map

| Surface | Impact | Evidence or N/A reason |
|---|---|---|
| Public API/contracts | ... | ... |
| Configuration/schema | ... | ... |
| Runtime selection/discovery | ... | ... |
| Callers/consumers | ... | ... |
| Tests | ... | ... |
| Documentation | ... | ... |
| Packaging/release | ... | ... |
| Compatibility/migration | ... | ... |
| Security/performance/observability | ... | ... |

### Minimality and alternatives

### Release, rollout, and rollback

### Risks

| Risk | Likelihood | Impact | Mitigation | Verification |
|---|---|---|---|---|

## 6. Exact Test-First Implementation Sequence

### Step P1 — Establish the failing behavioral test

- Repository: `TheSmokeTeam/<repo>`
- File: `path/to/file`
- Symbol: `TypeOrTest.Member`
- Exact change: ...
- Existing convention: `path/to/sibling:line`
- Dependencies: None
- Acceptance criteria: AC-1
- Tests: T-1
- Verification command: `<command from repository instructions>`

### Step P2 — Implement the smallest behavior change

- Repository: `TheSmokeTeam/<repo>`
- File: `path/to/file`
- Symbol: `Type.Member`
- Exact change: ...
- Existing convention: `path/to/sibling:line`
- Dependencies: P1
- Acceptance criteria: AC-1, AC-2
- Tests: T-1, T-2
- Verification command: `<command from repository instructions>`

## 7. Verification and Traceability

### Test plan

| Test ID | Level | Location | Scenario | Fails before? | Expected result |
|---|---|---|---|---|---|
| T-1 | unit | `path:Symbol` | ... | Yes | ... |

### Traceability matrix

| Acceptance criterion | Evidence | Implementation steps | Tests | Final verification |
|---|---|---|---|---|
| AC-1 | E-1 | P1, P2 | T-1 | ... |

List focused tests, affected-project tests, full repository checks, formatting
or static checks, and cross-repository verification where required.

## 8. Review and Approval Record

### Open decisions and missing evidence

None.

### Technical review history

| Revision | Verdict | Findings | Disposition |
|---|---|---|---|
| 1 | PENDING | Independent review not run | Awaiting reviewer |

### Developer approval history

| Revision | Decision | Evidence |
|---|---|---|
| 1 | Pending | Awaiting explicit developer decision on revision 1 |

Reviewer approval is technical readiness, not implementation authorization.

## 9. Implementation Handoff and Staleness Triggers

- Starting repository and file: ...
- Repository order: ...
- First failing test: T-1
- Checkpoint commands: ...
- Independent verifier: `qaas-verifier`
- Release owner when authorized: `release-and-mirror` | N/A
- Stop and re-plan when: a captured baseline changes, a named symbol is absent,
  or implementation contradicts the evidence.
```

## State rules

- Freeze `plan_revision` before review.
- Compute `plan_digest` with `validate_plan.py --print-digest` after freezing the
  substantive plan. The digest excludes only lifecycle status, review/developer
  approval metadata, and section 8 history.
- `AWAITING_APPROVAL` requires reviewer `APPROVE` on that revision and pending
  developer approval. `reviewed_digest` must match `plan_digest`.
- `APPROVED` additionally requires explicit developer approval of that revision.
  `approved_digest` must match `plan_digest`.
- Any material change or repository-baseline replacement increments the revision,
  recomputes the digest, and resets both gates.
- A detected repository baseline change makes the plan `STALE` until the new
  revision is independently reviewed and explicitly approved.
- `undetermined` classification is valid only before independent review approves
  the plan for developer approval.
- Release execution is forbidden unless the approved plan records
  `AUTHORIZED_AFTER_VERIFICATION`; a `verified` verdict is still required first.
