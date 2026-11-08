---
schema_version: "4"
plan_revision: 2
plan_digest: sha256:7323bf628fc95679add0ac02fad6b4a5c31de979e7671b704f0048d73272f16a
change_id: qaas-normalize-name
title: Normalize validator names
change_kind: bugfix
complexity: small
status: APPROVED
qaas_classification: existing-behavior
repositories:
  - name: TheSmokeTeam/QaaS.Framework
    checkout: /workspace/QaaS.Framework
    inspected_commit: 0123456789abcdef0123456789abcdef01234567
    worktree_fingerprint: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
review:
  verdict: APPROVE
  reviewed_revision: 2
  reviewed_digest: sha256:7323bf628fc95679add0ac02fad6b4a5c31de979e7671b704f0048d73272f16a
  evidence: qaas-plan-reviewer approved revision 2 and its digest.
developer_approval:
  status: APPROVED
  approved_revision: 2
  approved_digest: sha256:7323bf628fc95679add0ac02fad6b4a5c31de979e7671b704f0048d73272f16a
  evidence: Developer explicitly approved revision 2 and its digest in this task.
release:
  authorization: NOT_AUTHORIZED
  targets: QaaS.Framework package and verified downstream handoff
---

# QaaS Change Specification and Implementation Plan

## 1. Context and Request

### Know QaaS Context Brief

#### Platform scope
This changes QaaS platform validation, not end-user test authoring.
#### Ecosystem location
QaaS.Framework owns the validator and its consumers remain in the framework.
#### Dependency position
The validator is existing framework behavior with no new dependency edge.
#### Extension model
Existing behavior; this is neither a new Type A hook nor a Type B family.
#### Release ripple
The framework package follows its verified downstream release ripple if published.
#### Authority map
The repository instructions, source, tests, and graph evidence are authoritative.
#### Known unknowns
None.

### Problem or use case
The fourth validator rejects mixed-case names accepted by its siblings.

### Requested outcome and user-visible behavior
Mixed-case names validate consistently.

### Constraints and scope
Preserve every other validation behavior and exclude naming cleanup.

## 2. Developer Decisions and Non-goals

### Shared understanding
Confirmed by the developer: Yes

### Decisions
| ID | Decision question | Agent recommendation | Developer decision | Rationale |
|---|---|---|---|---|
| D-1 | Include nearby naming cleanup? | Exclude unrelated cleanup. | Exclude it. | Keep the bugfix minimal. |

### Non-goals and rejected alternatives
Renaming validators and adding a new abstraction are excluded.

## 3. Current State and Evidence

| ID | Kind | Claim | Evidence | Confidence |
|---|---|---|---|---|
| E-1 | fact | Three siblings normalize names. | `QaaS.Framework/src/Validator.cs:10` | verified |

The fourth validator skips the existing normalization helper. A mixed-case input
reproduces the mismatch, and the missing helper call is the proven root cause.

## 4. Desired State and Acceptance Criteria

### Invariants
Canonical-name and invalid-name behavior remain unchanged.

### Acceptance criteria
- AC-1: Given a mixed-case valid name, when the fourth validator runs, then validation succeeds.

## 5. Impact, Alternatives, and Minimality

### Impact map
| Surface | Impact | Evidence or N/A reason |
|---|---|---|
| Public API/contracts | None | Existing contract remains unchanged. |
| Configuration/schema | None | No configuration change. |
| Runtime selection/discovery | None | Existing validator path only. |
| Callers/consumers | Corrected comparison | E-1 |
| Tests | Add one regression test. | Existing test project. |
| Documentation | None | Internal consistency fix. |
| Packaging/release | Normal Framework release if shipped. | Repository instructions. |
| Compatibility/migration | Compatible | Existing valid inputs only expand. |
| Security/performance/observability | None | One existing helper call. |

### Minimality and alternatives
Reuse the existing helper; reject a new abstraction and unrelated renames.

### Release, rollout, and rollback
Use the normal Framework release only when authorized; rollback reverts the helper call.

### Risks
| Risk | Likelihood | Impact | Mitigation | Verification |
|---|---|---|---|---|
| Behavior drift | Low | Medium | Reuse the sibling helper. | T-1 and full tests |

## 6. Exact Test-First Implementation Sequence

### Step P1 — Establish the failing behavioral test
- Repository: `TheSmokeTeam/QaaS.Framework`
- File: `QaaS.Framework.Tests/ValidatorTests.cs`
- Symbol: `ValidatorTests.AcceptsMixedCaseName`
- Exact change: Add a regression test supplying a mixed-case valid name.
- Existing convention: `QaaS.Framework.Tests/ValidatorTests.cs:20`
- Dependencies: None
- Acceptance criteria: AC-1
- Tests: T-1
- Verification command: `dotnet test QaaS.Framework.sln`

### Step P2 — Reuse the existing normalization helper
- Repository: `TheSmokeTeam/QaaS.Framework`
- File: `QaaS.Framework/src/Validator.cs`
- Symbol: `Validator.Validate`
- Exact change: Normalize the name before the existing comparison.
- Existing convention: `QaaS.Framework/src/Validator.cs:10`
- Dependencies: P1
- Acceptance criteria: AC-1
- Tests: T-1
- Verification command: `dotnet test QaaS.Framework.sln`

## 7. Verification and Traceability

### Test plan
| Test ID | Level | Location | Scenario | Fails before? | Expected result |
|---|---|---|---|---|---|
| T-1 | unit | `ValidatorTests.AcceptsMixedCaseName` | Mixed-case valid name | Yes | Validation succeeds |

### Traceability matrix
| Acceptance criterion | Evidence | Implementation steps | Tests | Final verification |
|---|---|---|---|---|
| AC-1 | E-1 | P1, P2 | T-1 | `dotnet test QaaS.Framework.sln` |

Run the focused test, full solution tests, build, and formatter check from repository instructions.

## 8. Review and Approval Record

### Open decisions and missing evidence
None.

### Technical review history
| Revision | Verdict | Findings | Disposition |
|---|---|---|---|
| 2 | APPROVE | None | Approved without findings |

### Developer approval history
| Revision | Decision | Evidence |
|---|---|---|
| 2 | Approved | Developer explicitly approved revision 2 in the conversation. |

## 9. Implementation Handoff and Staleness Triggers

- Starting repository and file: `QaaS.Framework.Tests/ValidatorTests.cs`
- Repository order: QaaS.Framework
- First failing test: T-1
- Checkpoint commands: `dotnet test QaaS.Framework.sln`
- Independent verifier: `qaas-verifier`
- Release owner when authorized: `release-and-mirror`
- Stop and re-plan when: the baseline changes or the named symbol is absent.
