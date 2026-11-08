#!/usr/bin/env python3
"""Unit tests for validate_plan.py."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_plan import compute_plan_digest, validate_text


FIXTURE = Path(__file__).parent / "tests" / "fixtures" / "approved-plan.md"
VALID_PLAN = FIXTURE.read_text(encoding="utf-8")


def rebind_digest(text: str) -> str:
    digest = compute_plan_digest(text)
    text = re.sub(r"(?m)^plan_digest:.*$", f"plan_digest: {digest}", text)

    def replace_bound_digest(match: re.Match[str]) -> str:
        value = match.group(2).strip()
        return match.group(0) if value == "null" else f"{match.group(1)} {digest}"

    text = re.sub(
        r"(?m)^(  reviewed_digest:)\s*(.+)$", replace_bound_digest, text
    )
    text = re.sub(
        r"(?m)^(  approved_digest:)\s*(.+)$", replace_bound_digest, text
    )
    return text


class ValidatePlanTests(unittest.TestCase):
    def assert_error(self, text: str, fragment: str) -> None:
        errors = validate_text(text)
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected {fragment!r} in {errors!r}",
        )

    def test_approved_complete_plan_passes(self) -> None:
        self.assertEqual(validate_text(VALID_PLAN), [])

    def test_reviewed_plan_can_wait_for_developer_approval(self) -> None:
        awaiting = VALID_PLAN.replace("status: APPROVED", "status: AWAITING_APPROVAL", 1)
        awaiting = awaiting.replace("  status: APPROVED", "  status: PENDING", 1)
        awaiting = awaiting.replace("  approved_revision: 2", "  approved_revision: null", 1)
        awaiting = awaiting.replace(
            "  approved_digest: sha256:7323bf628fc95679add0ac02fad6b4a5c31de979e7671b704f0048d73272f16a",
            "  approved_digest: null",
            1,
        )
        awaiting = awaiting.replace("| 2 | Approved |", "| 2 | Pending |", 1)
        self.assertEqual(validate_text(awaiting), [])

    def test_review_must_be_tied_to_current_revision(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("  reviewed_revision: 2", "  reviewed_revision: 1"),
            "reviewed_revision must match",
        )

    def test_approved_revision_must_match_current_revision(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("  approved_revision: 2", "  approved_revision: 1"),
            "approved_revision must match",
        )

    def test_short_commit_is_rejected(self) -> None:
        self.assert_error(
            VALID_PLAN.replace(
                "0123456789abcdef0123456789abcdef01234567", "0123456"
            ),
            "full 40-character SHA",
        )

    def test_invalid_fingerprint_is_rejected(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("sha256:" + "a" * 64, "sha256:abc"),
            "worktree_fingerprint",
        )

    def test_review_verdict_outside_review_mapping_does_not_count(self) -> None:
        moved = VALID_PLAN.replace("  verdict: APPROVE\n", "  verdict: PENDING\n", 1)
        moved = moved.replace("  reviewed_revision: 2", "  reviewed_revision: null", 1)
        moved = moved.replace("developer_approval:\n", "verdict: APPROVE\ndeveloper_approval:\n", 1)
        self.assert_error(moved, "requires review verdict APPROVE")

    def test_non_approved_state_resets_developer_approval(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("status: APPROVED", "status: STALE", 1),
            "non-APPROVED plan must reset",
        )

    def test_approved_plan_rejects_placeholder(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("Normalize the name", "TODO"),
            "placeholder: TODO",
        )

    def test_approved_plan_rejects_frontmatter_placeholder(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("title: Normalize validator names", "title: <change title>"),
            "placeholder: angle-bracket placeholder",
        )

    def test_completed_review_rejects_pending_evidence(self) -> None:
        self.assert_error(
            VALID_PLAN.replace(
                "evidence: qaas-plan-reviewer approved revision 2 and its digest.",
                "evidence: Pending",
                1,
            ),
            "completed review requires resolved evidence",
        )

    def test_completed_approval_rejects_pending_evidence(self) -> None:
        self.assert_error(
            VALID_PLAN.replace(
                "evidence: Developer explicitly approved revision 2 and its digest in this task.",
                "evidence: Pending",
                1,
            ),
            "completed developer approval decision requires resolved evidence",
        )

    def test_review_block_scalar_marker_is_not_evidence(self) -> None:
        plan = VALID_PLAN.replace(
            "evidence: qaas-plan-reviewer approved revision 2 and its digest.",
            "evidence: |",
            1,
        )
        self.assert_error(rebind_digest(plan), "review is missing evidence")

    def test_commented_block_scalar_marker_is_not_evidence(self) -> None:
        plan = VALID_PLAN.replace(
            "evidence: qaas-plan-reviewer approved revision 2 and its digest.",
            "evidence: | # intentionally empty",
            1,
        )
        self.assert_error(rebind_digest(plan), "review is missing evidence")

    def test_approval_block_scalar_marker_is_not_evidence(self) -> None:
        plan = VALID_PLAN.replace(
            "evidence: Developer explicitly approved revision 2 and its digest in this task.",
            "evidence: >-",
            1,
        )
        self.assert_error(rebind_digest(plan), "developer_approval is missing evidence")

    def test_release_block_scalar_marker_is_not_a_target(self) -> None:
        plan = VALID_PLAN.replace(
            "authorization: NOT_AUTHORIZED",
            "authorization: AUTHORIZED_AFTER_VERIFICATION",
            1,
        ).replace(
            "targets: QaaS.Framework package and verified downstream handoff",
            "targets: |",
            1,
        )
        self.assert_error(rebind_digest(plan), "release is missing targets")

    def test_material_body_change_breaks_plan_digest(self) -> None:
        self.assert_error(
            VALID_PLAN.replace(
                "Normalize the name before the existing comparison.",
                "Replace the validator with a permissive implementation.",
            ),
            "plan_digest does not match",
        )

    def test_duplicate_top_level_lifecycle_key_is_rejected(self) -> None:
        self.assert_error(
            VALID_PLAN.replace(
                "status: APPROVED", "status: APPROVED\nstatus: STALE", 1
            ),
            "duplicate top-level key: status",
        )

    def test_nested_approval_status_cannot_replace_top_level_status(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("status: APPROVED\n", "", 1),
            "frontmatter is missing status",
        )

    def test_checkout_must_be_absolute(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("checkout: /workspace/", "checkout: workspace/", 1),
            "checkout must be an absolute path",
        )

    def test_authorized_release_requires_explicit_targets(self) -> None:
        authorized = VALID_PLAN.replace(
            "authorization: NOT_AUTHORIZED",
            "authorization: AUTHORIZED_AFTER_VERIFICATION",
            1,
        ).replace(
            "targets: QaaS.Framework package and verified downstream handoff",
            "targets: N/A",
            1,
        )
        self.assert_error(
            rebind_digest(authorized),
            "authorized release requires explicit targets",
        )

    def test_csharp_generic_is_not_an_angle_placeholder(self) -> None:
        generic = rebind_digest(
            VALID_PLAN.replace("`Validator.Validate`", "`Validator<T>.Validate`", 1)
        )
        self.assertEqual(validate_text(generic), [])

    def test_dotnet_xml_name_is_not_an_angle_placeholder(self) -> None:
        xml = rebind_digest(
            VALID_PLAN.replace(
                "The validator is existing framework behavior with no new dependency edge.",
                "The <PackageReference> remains unchanged and adds no dependency edge.",
                1,
            )
        )
        self.assertEqual(validate_text(xml), [])

    def test_ellipsis_step_value_is_rejected(self) -> None:
        self.assert_error(
            VALID_PLAN.replace(
                "- Exact change: Normalize the name before the existing comparison.",
                "- Exact change: ...",
            ),
            "placeholder: ellipsis placeholder",
        )

    def test_step_requires_all_fields(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("- Symbol: `Validator.Validate`\n", ""),
            "P2 is missing populated field: Symbol",
        )

    def test_implementation_step_ids_must_be_unique(self) -> None:
        duplicate = rebind_digest(
            VALID_PLAN.replace("### Step P2", "### Step P1", 1)
        )
        self.assert_error(duplicate, "implementation step IDs must be unique")

    def test_implementation_step_ids_must_be_contiguous(self) -> None:
        skipped = rebind_digest(
            VALID_PLAN.replace("### Step P2", "### Step P3", 1)
        )
        self.assert_error(skipped, "contiguous and ordered P1..Pn")

    def test_acceptance_criterion_ids_must_be_unique(self) -> None:
        original = (
            "- AC-1: Given a mixed-case valid name, when the fourth validator runs, "
            "then validation succeeds."
        )
        duplicate = rebind_digest(VALID_PLAN.replace(original, f"{original}\n{original}", 1))
        self.assert_error(duplicate, "acceptance criterion IDs must be unique")

    def test_test_ids_must_be_unique(self) -> None:
        row = (
            "| T-1 | unit | `ValidatorTests.AcceptsMixedCaseName` | Mixed-case "
            "valid name | Yes | Validation succeeds |"
        )
        duplicate = rebind_digest(VALID_PLAN.replace(row, f"{row}\n{row}", 1))
        self.assert_error(duplicate, "test IDs must be unique")

    def test_know_qaas_section_cannot_be_empty(self) -> None:
        self.assert_error(
            VALID_PLAN.replace(
                "#### Dependency position\nThe validator is existing framework behavior with no new dependency edge.\n",
                "#### Dependency position\n",
            ),
            "Know QaaS Context Brief has empty section",
        )

    def test_developer_must_confirm_shared_understanding(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("Confirmed by the developer: Yes", "Confirmed by the developer: No"),
            "confirm shared understanding",
        )

    def test_acceptance_criterion_requires_traceability_row(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("| AC-1 | E-1 | P1, P2 | T-1 | `dotnet test QaaS.Framework.sln` |\n", ""),
            "AC-1 is missing from the traceability matrix",
        )

    def test_numbered_sections_must_be_in_order(self) -> None:
        heading_a = "## 3. Current State and Evidence"
        heading_b = "## 4. Desired State and Acceptance Criteria"
        swapped = VALID_PLAN.replace(heading_a, "## TEMP", 1)
        swapped = swapped.replace(heading_b, heading_a, 1).replace("## TEMP", heading_b, 1)
        self.assert_error(swapped, "sections must appear in schema order")

    def test_blocked_plan_may_have_incomplete_body(self) -> None:
        blocked = VALID_PLAN.replace("status: APPROVED", "status: BLOCKED", 1)
        blocked = blocked.replace("  verdict: APPROVE", "  verdict: BLOCK", 1)
        blocked = blocked.replace("  reviewed_revision: 2", "  reviewed_revision: null", 1)
        blocked = re.sub(
            r"(?m)^  reviewed_digest:.*$", "  reviewed_digest: null", blocked, count=1
        )
        blocked = blocked.replace(
            "  evidence: qaas-plan-reviewer approved revision 2 and its digest.",
            "  evidence: Pending",
            1,
        )
        blocked = blocked.replace("  verdict: BLOCK", "  verdict: PENDING", 1)
        blocked = blocked.replace("  status: APPROVED", "  status: PENDING", 1)
        blocked = blocked.replace("  approved_revision: 2", "  approved_revision: null", 1)
        blocked = re.sub(
            r"(?m)^  approved_digest:.*$", "  approved_digest: null", blocked, count=1
        )
        blocked = blocked.split("# QaaS Change", 1)[0] + "# QaaS Change\nMissing source access.\n"
        blocked = rebind_digest(blocked)
        self.assertEqual(validate_text(blocked), [])

    def test_refactor_is_a_supported_change_kind(self) -> None:
        self.assertEqual(
            validate_text(
                rebind_digest(
                    VALID_PLAN.replace(
                        "change_kind: bugfix", "change_kind: refactor", 1
                    )
                )
            ),
            [],
        )

    def test_approved_plan_cannot_remain_undetermined(self) -> None:
        self.assert_error(
            VALID_PLAN.replace("qaas_classification: existing-behavior", "qaas_classification: undetermined"),
            "cannot have undetermined classification",
        )


if __name__ == "__main__":
    unittest.main()
