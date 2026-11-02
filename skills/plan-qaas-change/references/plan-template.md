# QaaS Change Specification and Implementation Plan Template

Use this schema exactly. Remove instructional placeholders from a completed plan.
An `APPROVED` plan must pass `scripts/validate_plan.py` when saved.

```markdown
---
schema_version: "1"
change_id: qaas-<short-slug>
title: <feature or bugfix title>
change_kind: feature | bugfix
complexity: small | standard | cross-repo
status: DRAFT | NEEDS_DECISION | BLOCKED | APPROVED | STALE
qaas_classification: type-a | type-b | existing-behavior | not-applicable
repositories:
  - name: TheSmokeTeam/<repo>
    inspected_commit: <full SHA>
review:
  verdict: APPROVE | REVISE | BLOCK
---

# QaaS Change Specification and Implementation Plan

## 1. Developer summary

Explain what changes, why it belongs in these repositories, how the affected
QaaS flow works, and what success looks like in language useful to a developer
who is only semi-fluent in QaaS.

## 2. Request

### Problem or use case
### Constraints
### Non-goals
### User-visible behavior

## 3. Current-state evidence

| ID | Kind | Fact | Evidence | Confidence |
|---|---|---|---|---|
| E-1 | fact | ... | `repo/path:line` | verified |

Kinds: `fact`, `inference`, `assumption`, or `decision`. An assumption that
changes implementation prevents approval.

## 4. Current behavior

Describe the relevant control/data flow.

For a bugfix include reproduction conditions, observed and expected results,
failure mechanism, and root cause. For a feature include use cases, integration
seam, sibling convention, material alternatives, and selection rationale.

## 5. Desired-state specification

### Invariants

### Acceptance criteria

- AC-1: Given ..., when ..., then ...
- AC-2: ...

## 6. Impact map

| Surface | Impact | Evidence or N/A reason |
|---|---|---|
| Public API/contracts | ... | ... |
| Configuration/schema | ... | ... |
| Runtime discovery/factories | ... | ... |
| Callers/consumers | ... | ... |
| Tests | ... | ... |
| Documentation | ... | ... |
| Packaging/release | ... | ... |
| Compatibility/migration | ... | ... |
| Security/performance/observability | ... | ... |

## 7. Exact implementation sequence

### Step P1 — Add the failing behavioral test

- Repository: `TheSmokeTeam/<repo>`
- File: `path/to/file`
- Symbol: `TypeOrTest.Member`
- Exact change: ...
- Existing convention: `path/to/sibling:line`
- Dependencies: None
- Acceptance criteria: AC-1
- Tests: T-1
- Verification command: `<command copied from repository docs>`

### Step P2 — Implement the smallest behavior change

- Repository: `TheSmokeTeam/<repo>`
- File: `path/to/file`
- Symbol: `Type.Member`
- Exact change: ...
- Existing convention: `path/to/sibling:line`
- Dependencies: P1
- Acceptance criteria: AC-1, AC-2
- Tests: T-1, T-2
- Verification command: `<command copied from repository docs>`

## 8. Traceability matrix

| Acceptance criterion | Evidence | Implementation steps | Tests | Final verification |
|---|---|---|---|---|
| AC-1 | E-1 | P1, P2 | T-1 | ... |

## 9. Test-first verification plan

| Test ID | Level | Location | Scenario | Fails before? | Expected result |
|---|---|---|---|---|---|
| T-1 | unit | `path:Symbol` | ... | Yes | ... |

List focused tests, affected-project tests, full repository tests, formatting or
static checks, and cross-repository verification when required.

## 10. Release and rollout

Cover versioning, downstream package-reference changes, PackageMirror,
schema/docs regeneration, compatibility/migration, and rollback. Use
evidence-backed `N/A` entries for a local change.

## 11. Risks

| Risk | Likelihood | Impact | Mitigation | Verification |
|---|---|---|---|---|

## 12. Open decisions and missing evidence

None.

## 13. Review record

| Finding | Severity | Disposition | Resulting plan change |
|---|---|---|---|
| None | — | — | Reviewer approved without findings |

## 14. Implementation handoff

- Starting repository and file: ...
- Repository order: ...
- First failing test: T-1
- Checkpoint commands: ...
- Stop and re-plan when: an inspected commit changes, an asserted symbol is
  absent, or implementation reveals behavior inconsistent with the evidence.
```

## Complexity scaling

- `small`: keep sections concise, but retain provenance, root-cause/integration
  evidence, acceptance criteria, exact steps, tests, and review.
- `standard`: use the complete template.
- `cross-repo`: include a per-repository sequence, dependency ordering, release
  ripple, compatibility, migration, schemas, and documentation.
