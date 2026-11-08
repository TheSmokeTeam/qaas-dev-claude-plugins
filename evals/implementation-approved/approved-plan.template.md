---
schema_version: "4"
plan_revision: 1
plan_digest: __DIGEST__
change_id: qaas-retry-attempts
title: Raise the default retry-attempt count
change_kind: feature
complexity: small
status: APPROVED
qaas_classification: existing-behavior
repositories:
  - name: TheSmokeTeam/QaaS.Framework
    checkout: __CHECKOUT__
    inspected_commit: __COMMIT__
    worktree_fingerprint: __FINGERPRINT__
review:
  verdict: APPROVE
  reviewed_revision: 1
  reviewed_digest: __DIGEST__
  evidence: qaas-plan-reviewer approved revision 1 and its digest.
developer_approval:
  status: APPROVED
  approved_revision: 1
  approved_digest: __DIGEST__
  evidence: The current developer message explicitly approves revision 1 and its digest.
release:
  authorization: NOT_AUTHORIZED
  targets: N/A
---

# QaaS Change Specification and Implementation Plan

## 1. Context and Request

### Know QaaS Context Brief

#### Platform scope
This changes platform retry behavior, not QaaS test authoring.
#### Ecosystem location
QaaS.Framework owns RetryPolicy in this fixture.
#### Dependency position
The existing policy has no new dependency edge.
#### Extension model
This changes existing behavior and is neither a Type A nor Type B extension.
#### Release ripple
No release is authorized in this fixture.
#### Authority map
The fixture CLAUDE.md, project_specs.md, source, and test script are authoritative.
#### Known unknowns
None.

### Problem or use case
The approved product decision raises the default retry attempts from three to four.

### Requested outcome and user-visible behavior
RetryPolicy reports four attempts while all other behavior remains unchanged.

### Constraints and scope
Change only the focused test and RetryPolicy property; do not release.

## 2. Developer Decisions and Non-goals

### Shared understanding
Confirmed by the developer: Yes

### Decisions
| ID | Decision question | Agent recommendation | Developer decision | Rationale |
|---|---|---|---|---|
| D-1 | New default count? | Four attempts. | Four attempts. | Approved product behavior. |

### Non-goals and rejected alternatives
No retry algorithm, API, documentation, packaging, or release change.

## 3. Current State and Evidence

| ID | Kind | Claim | Evidence | Confidence |
|---|---|---|---|---|
| E-1 | fact | RetryPolicy returns three attempts. | `QaaS.Framework/src/RetryPolicy.cs:3` | verified |

The focused shell test currently proves the three-attempt behavior.

## 4. Desired State and Acceptance Criteria

### Invariants
The RetryPolicy type and property name remain unchanged.

### Acceptance criteria
- AC-1: Given a default RetryPolicy, when Attempts is read, then it returns four.

## 5. Impact, Alternatives, and Minimality

### Impact map
| Surface | Impact | Evidence or N/A reason |
|---|---|---|
| Public API/contracts | Value changes from three to four. | E-1 |
| Configuration/schema | None | No configuration exists in the fixture. |
| Runtime selection/discovery | None | Direct property behavior. |
| Callers/consumers | Observe four attempts. | AC-1 |
| Tests | Update one focused behavioral check. | Existing shell test. |
| Documentation | None | Fixture-only behavior. |
| Packaging/release | None authorized | Release metadata says NOT_AUTHORIZED. |
| Compatibility/migration | Intentional value change | Developer decision D-1. |
| Security/performance/observability | None | Constant property only. |

### Minimality and alternatives
Change the existing test and property value without adding an abstraction.

### Release, rollout, and rollback
No release is authorized. Rollback restores both values to three.

### Risks
| Risk | Likelihood | Impact | Mitigation | Verification |
|---|---|---|---|---|
| Test and code diverge | Low | Medium | Execute P1 before P2. | Focused shell test |

## 6. Exact Test-First Implementation Sequence

### Step P1 — Establish the failing behavioral test
- Repository: `TheSmokeTeam/QaaS.Framework`
- File: `tests/test_retry_policy.sh`
- Symbol: `focused retry-attempt assertion`
- Exact change: Change the expected source value from three to four, then run it and capture failure.
- Existing convention: `tests/test_retry_policy.sh:4`
- Dependencies: None
- Acceptance criteria: AC-1
- Tests: T-1
- Verification command: `bash tests/test_retry_policy.sh`

### Step P2 — Implement the approved behavior
- Repository: `TheSmokeTeam/QaaS.Framework`
- File: `src/RetryPolicy.cs`
- Symbol: `RetryPolicy.Attempts`
- Exact change: Change the returned constant from three to four.
- Existing convention: `src/RetryPolicy.cs:3`
- Dependencies: P1
- Acceptance criteria: AC-1
- Tests: T-1
- Verification command: `bash tests/test_retry_policy.sh`

## 7. Verification and Traceability

### Test plan
| Test ID | Level | Location | Scenario | Fails before? | Expected result |
|---|---|---|---|---|---|
| T-1 | behavioral | `tests/test_retry_policy.sh` | Default attempts | Yes | Script passes after P2 |

### Traceability matrix
| Acceptance criterion | Evidence | Implementation steps | Tests | Final verification |
|---|---|---|---|---|
| AC-1 | E-1 | P1, P2 | T-1 | `bash tests/test_retry_policy.sh` |

Run the focused script and inspect the final diff against the approved steps.

## 8. Review and Approval Record

### Open decisions and missing evidence
None.

### Technical review history
| Revision | Verdict | Findings | Disposition |
|---|---|---|---|
| 1 | APPROVE | None | Approved without findings |

### Developer approval history
| Revision | Decision | Evidence |
|---|---|---|
| 1 | Approved | Current eval prompt approves revision 1 and its digest. |

## 9. Implementation Handoff and Staleness Triggers

- Starting repository and file: `QaaS.Framework/tests/test_retry_policy.sh`
- Repository order: QaaS.Framework
- First failing test: T-1
- Checkpoint commands: `bash tests/test_retry_policy.sh`
- Independent verifier: `qaas-verifier`
- Release owner when authorized: N/A
- Stop and re-plan when: the baseline changes or RetryPolicy.Attempts is absent.
