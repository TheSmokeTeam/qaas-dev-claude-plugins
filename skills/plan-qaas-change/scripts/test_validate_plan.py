#!/usr/bin/env python3
"""Unit tests for validate_plan.py."""

from __future__ import annotations

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_plan import validate_text


VALID_PLAN = """---
schema_version: "3"
plan_revision: 2
change_id: qaas-normalize-name
title: Normalize validator names
change_kind: bugfix
complexity: small
status: APPROVED
qaas_classification: existing-behavior
repositories:
  - name: TheSmokeTeam/QaaS.Framework
    inspected_commit: 0123456789abcdef0123456789abcdef01234567
review:
  verdict: APPROVE
developer_approval:
  status: APPROVED
  approved_revision: 2
---

# QaaS Change Specification and Implementation Plan

## 1. Know QaaS Context Brief
### Platform scope
This changes QaaS platform validation, not end-user test authoring.
### Ecosystem location
QaaS.Framework owns the validator and its consumers remain in the framework.
### Dependency position
The validator sits in existing framework behavior with no new dependency edge.
### Extension model
Existing behavior; this is neither a Type A hook nor a new Type B family.
### Release ripple
The framework package follows its normal downstream release ripple if published.
### Authority map
The repository instructions and Validator source are authoritative.
### Known unknowns
None.

## 2. Developer interview record
### Shared understanding
Confirmed by the developer: Yes
### Decisions
| ID | Decision question | Agent recommendation | Developer decision | Rationale |
|---|---|---|---|---|
| D-1 | Include the nearby naming cleanup? | Exclude unrelated cleanup. | Exclude it. | Keep the bugfix minimal. |
### Rejected scope and alternatives
Renaming validators was rejected as unrelated scope.

## 3. Developer summary
Normalize the fourth validator exactly like its three siblings.

## 4. Request
Fix mixed-case validation without unrelated cleanup.

## 5. Current-state evidence
| ID | Kind | Fact | Evidence | Confidence |
|---|---|---|---|---|
| E-1 | fact | Three siblings normalize names. | `QaaS.Framework/Validator.cs:10` | verified |

## 6. Current behavior
The fourth validator skips normalization and rejects mixed-case names.

## 7. Desired-state specification
### Invariants
Existing validation behavior remains unchanged.
### Acceptance criteria
- AC-1: Given a mixed-case name, when the fourth validator runs, then validation succeeds.

## 8. Impact map
| Surface | Impact | Evidence or N/A reason |
|---|---|---|
| Tests | Add one regression test. | E-1 |

## 9. Exact implementation sequence
### Step P1 — Add the failing behavioral test
- Repository: `TheSmokeTeam/QaaS.Framework`
- File: `QaaS.Framework.Tests/ValidatorTests.cs`
- Symbol: `ValidatorTests.AcceptsMixedCaseName`
- Exact change: Add a regression test that supplies a mixed-case name.
- Existing convention: `QaaS.Framework.Tests/ValidatorTests.cs:20`
- Dependencies: None
- Acceptance criteria: AC-1
- Tests: T-1
- Verification command: `dotnet test QaaS.Framework.sln`

### Step P2 — Reuse the existing normalization helper
- Repository: `TheSmokeTeam/QaaS.Framework`
- File: `QaaS.Framework/Validator.cs`
- Symbol: `Validator.Validate`
- Exact change: Normalize the name before the existing comparison.
- Existing convention: `QaaS.Framework/Validator.cs:10`
- Dependencies: P1
- Acceptance criteria: AC-1
- Tests: T-1
- Verification command: `dotnet test QaaS.Framework.sln`

## 10. Traceability matrix
| Acceptance criterion | Evidence | Implementation steps | Tests | Final verification |
|---|---|---|---|---|
| AC-1 | E-1 | P1, P2 | T-1 | `dotnet test QaaS.Framework.sln` |

## 11. Test-first verification plan
| Test ID | Level | Location | Scenario | Fails before? | Expected result |
|---|---|---|---|---|---|
| T-1 | unit | `ValidatorTests.AcceptsMixedCaseName` | Mixed-case name | Yes | Passes validation |

## 12. Release and rollout
N/A: local bugfix with no package contract change.

## 13. Risks
| Risk | Likelihood | Impact | Mitigation | Verification |
|---|---|---|---|---|
| Regression | Low | Medium | Reuse sibling helper | T-1 |

## 14. Open decisions and missing evidence
None.

## 15. Review record
| Finding | Severity | Disposition | Resulting plan change |
|---|---|---|---|
| None | — | — | Approved |

## 16. Developer approval
- Plan revision: 2
- Presented to: developer
- Decision: Approved
- Approval evidence: developer explicitly approved revision 2 in the conversation
- Invalidated by: material plan or inspected commit changes

## 17. Implementation handoff
- Starting repository and file: `QaaS.Framework.Tests/ValidatorTests.cs`
- Repository order: QaaS.Framework
- First failing test: T-1
- Checkpoint commands: `dotnet test QaaS.Framework.sln`
- Stop and re-plan when: inspected commit changes.
"""


class ValidatePlanTests(unittest.TestCase):
    def test_approved_complete_plan_passes(self) -> None:
        self.assertEqual(validate_text(VALID_PLAN), [])

    def test_reviewed_plan_can_wait_for_developer_approval(self) -> None:
        awaiting = VALID_PLAN.replace(
            "\nstatus: APPROVED\n", "\nstatus: AWAITING_APPROVAL\n"
        )
        awaiting = awaiting.replace("  status: APPROVED", "  status: PENDING")
        awaiting = awaiting.replace("  approved_revision: 2", "  approved_revision: null")
        awaiting = awaiting.replace("- Decision: Approved", "- Decision: Pending")
        awaiting = awaiting.replace(
            "developer explicitly approved revision 2 in the conversation",
            "pending explicit developer approval",
        )
        self.assertEqual(validate_text(awaiting), [])

    def test_approved_plan_requires_explicit_developer_approval(self) -> None:
        pending = VALID_PLAN.replace("  status: APPROVED", "  status: PENDING")
        pending = pending.replace("  approved_revision: 2", "  approved_revision: null")
        errors = validate_text(pending)
        self.assertTrue(any("requires explicit developer approval" in error for error in errors))

    def test_approved_revision_must_match_current_revision(self) -> None:
        errors = validate_text(VALID_PLAN.replace("  approved_revision: 2", "  approved_revision: 1"))
        self.assertTrue(any("must match" in error for error in errors))

    def test_developer_approval_requires_revision_field(self) -> None:
        errors = validate_text(VALID_PLAN.replace("  approved_revision: 2\n", ""))
        self.assertTrue(any("missing approved_revision" in error for error in errors))

    def test_approved_plan_rejects_placeholder(self) -> None:
        errors = validate_text(VALID_PLAN.replace("Normalize the name", "TODO"))
        self.assertTrue(any("placeholder: TODO" in error for error in errors))

    def test_approved_plan_requires_step_fields(self) -> None:
        errors = validate_text(
            VALID_PLAN.replace("- Symbol: `Validator.Validate`\n", "")
        )
        self.assertTrue(any("P2 is missing populated field: Symbol" in error for error in errors))

    def test_approved_plan_requires_complete_know_qaas_brief(self) -> None:
        errors = validate_text(
            VALID_PLAN.replace("### Dependency position\n", "")
        )
        self.assertTrue(
            any("Know QaaS Context Brief is missing heading" in error for error in errors)
        )

    def test_approved_plan_rejects_empty_know_qaas_section(self) -> None:
        errors = validate_text(
            VALID_PLAN.replace(
                "### Dependency position\nThe validator sits in existing framework behavior with no new dependency edge.\n",
                "### Dependency position\n",
            )
        )
        self.assertTrue(
            any("Know QaaS Context Brief has empty section" in error for error in errors)
        )

    def test_reviewed_plan_requires_confirmed_developer_interview(self) -> None:
        errors = validate_text(
            VALID_PLAN.replace("Confirmed by the developer: Yes", "Confirmed by the developer: No")
        )
        self.assertTrue(any("confirm shared understanding" in error for error in errors))

    def test_blocked_plan_allows_incomplete_body(self) -> None:
        blocked = VALID_PLAN.replace("\nstatus: APPROVED\n", "\nstatus: BLOCKED\n")
        blocked = blocked.replace("  verdict: APPROVE", "  verdict: BLOCK")
        blocked = blocked.replace("  status: APPROVED", "  status: PENDING")
        blocked = blocked.replace("  approved_revision: 2", "  approved_revision: null")
        blocked = blocked.split("# QaaS Change", 1)[0] + "# QaaS Change\nMissing source access.\n"
        self.assertEqual(validate_text(blocked), [])


if __name__ == "__main__":
    unittest.main()
