#!/usr/bin/env python3
"""Validate the structural and lifecycle contract of a QaaS change plan."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path


ALLOWED_STATUS = {
    "DRAFT",
    "NEEDS_DECISION",
    "BLOCKED",
    "AWAITING_APPROVAL",
    "APPROVED",
    "STALE",
}
ALLOWED_REVIEW = {"PENDING", "APPROVE", "REVISE", "BLOCK"}
ALLOWED_DEVELOPER_APPROVAL = {"PENDING", "APPROVED", "CHANGES_REQUESTED"}
FULL_PLAN_STATUSES = {"AWAITING_APPROVAL", "APPROVED"}
ALLOWED_KIND = {"feature", "bugfix", "refactor"}
ALLOWED_COMPLEXITY = {"small", "standard", "cross-repo"}
ALLOWED_CLASSIFICATION = {
    "type-a",
    "type-b",
    "existing-behavior",
    "not-applicable",
    "undetermined",
}
ALLOWED_RELEASE_AUTHORIZATION = {
    "NOT_AUTHORIZED",
    "AUTHORIZED_AFTER_VERIFICATION",
}
REQUIRED_HEADINGS = [
    "## 1. Context and Request",
    "## 2. Developer Decisions and Non-goals",
    "## 3. Current State and Evidence",
    "## 4. Desired State and Acceptance Criteria",
    "## 5. Impact, Alternatives, and Minimality",
    "## 6. Exact Test-First Implementation Sequence",
    "## 7. Verification and Traceability",
    "## 8. Review and Approval Record",
    "## 9. Implementation Handoff and Staleness Triggers",
]
KNOW_QAAS_SUBHEADINGS = [
    "#### Platform scope",
    "#### Ecosystem location",
    "#### Dependency position",
    "#### Extension model",
    "#### Release ripple",
    "#### Authority map",
    "#### Known unknowns",
]
STEP_FIELDS = [
    "Repository",
    "File",
    "Symbol",
    "Exact change",
    "Existing convention",
    "Dependencies",
    "Acceptance criteria",
    "Tests",
    "Verification command",
]
PLACEHOLDER_PATTERNS = [
    (r"\bTBD\b", "TBD"),
    (r"\bTODO\b", "TODO"),
    (r"\bas needed\b", "as needed"),
    (r"\brelevant files?\b", "relevant files"),
    (r"\bto be determined\b", "to be determined"),
    (r"(?m)(?::|\|)\s*\.\.\.\s*(?:\||$)", "ellipsis placeholder"),
    (r"(?m)^\s*\.\.\.\s*$", "ellipsis placeholder"),
]
NULL_VALUES = {"null", "none", "~"}
MUTABLE_DIGEST_KEYS = {"status", "plan_digest", "review", "developer_approval"}
KNOWN_ANGLE_PLACEHOLDERS = {
    "change title",
    "feature, bugfix, or refactor title",
    "short-slug",
    "absolute checkout path",
    "40-character commit sha",
    "64 hexadecimal characters",
    "64 lowercase hexadecimal characters",
    "plan revision",
    "plan digest",
    "qaas-plan-reviewer result reference",
    "developer message or trusted handoff reference",
    "explicit packages, workflows, and documentation handoff, or n/a",
    "repo",
    "command from repository instructions",
}


def _frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("plan must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("plan frontmatter is not closed with ---")
    return text[4:end], text[end + 5 :]


def _scalar(block: str, key: str) -> str | None:
    match = re.search(
        rf"(?m)^\s*{re.escape(key)}:\s*[\"']?([^\n\"']+?)[\"']?\s*$",
        block,
    )
    if not match:
        return None
    value = match.group(1).strip()
    return (
        None
        if re.fullmatch(r"[|>][+\-1-9]*(?:\s+#.*)?", value)
        else value
    )


def _top_scalar(block: str, key: str) -> str | None:
    match = re.search(
        rf"(?m)^{re.escape(key)}:\s*[\"']?([^\n\"']+?)[\"']?\s*$",
        block,
    )
    if not match:
        return None
    value = match.group(1).strip()
    return (
        None
        if re.fullmatch(r"[|>][+\-1-9]*(?:\s+#.*)?", value)
        else value
    )


def _mapping(frontmatter: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*$", frontmatter)
    if not match:
        return ""
    remainder = frontmatter[match.end() :]
    next_top = re.search(r"(?m)^[A-Za-z_][A-Za-z0-9_-]*:\s*", remainder)
    block = remainder[: next_top.start()] if next_top else remainder
    return "\n".join(
        line[2:] if line.startswith("  ") else line
        for line in block.strip("\n").splitlines()
    )


def _top_level_keys(block: str) -> list[str]:
    return re.findall(r"(?m)^([A-Za-z_][A-Za-z0-9_-]*):", block)


def _field_count(block: str, key: str) -> int:
    return len(
        re.findall(rf"(?m)^\s*(?:-\s*)?{re.escape(key)}:\s*", block)
    )


def _canonical_review_unit(frontmatter: str, body: str) -> str:
    """Return the stable plan content reviewed and approved by humans."""
    kept_frontmatter: list[str] = []
    skip = False
    for line in frontmatter.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        top_level = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):", line)
        if top_level:
            skip = top_level.group(1) in MUTABLE_DIGEST_KEYS
        if not skip:
            kept_frontmatter.append(line.rstrip())

    normalized_body = body.replace("\r\n", "\n").replace("\r", "\n")
    review_start = re.search(r"(?m)^## 8\. Review and Approval Record\s*$", normalized_body)
    if review_start:
        handoff_start = re.search(
            r"(?m)^## 9\. Implementation Handoff and Staleness Triggers\s*$",
            normalized_body[review_start.end() :],
        )
        if handoff_start:
            handoff_offset = review_start.end() + handoff_start.start()
            normalized_body = (
                normalized_body[: review_start.start()] + normalized_body[handoff_offset:]
            )
        else:
            normalized_body = normalized_body[: review_start.start()]

    body_lines = [line.rstrip() for line in normalized_body.splitlines()]
    canonical = "\n".join(kept_frontmatter).strip() + "\n---\n"
    canonical += "\n".join(body_lines).strip() + "\n"
    return canonical


def compute_plan_digest(text: str) -> str:
    frontmatter, body = _frontmatter(text)
    canonical = _canonical_review_unit(frontmatter, body)
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def _angle_placeholder_present(text: str) -> bool:
    for match in re.finditer(r"<([^>\n]+)>", text):
        if match.group(1).strip().casefold() in KNOWN_ANGLE_PLACEHOLDERS:
            return True
    return False


def _section(body: str, heading: str) -> str:
    start = body.find(heading)
    if start == -1:
        return ""
    content_start = start + len(heading)
    next_heading = re.search(r"(?m)^## \d+\. ", body[content_start:])
    end = content_start + next_heading.start() if next_heading else len(body)
    return body[content_start:end].strip()


def _subsection(section: str, heading: str) -> str:
    start = section.find(heading)
    if start == -1:
        return ""
    content_start = start + len(heading)
    next_heading = re.search(r"(?m)^### ", section[content_start:])
    end = content_start + next_heading.start() if next_heading else len(section)
    return section[content_start:end].strip()


def _is_null(value: str | None) -> bool:
    return value is not None and value.casefold() in NULL_VALUES


def _is_unresolved_evidence(value: str | None) -> bool:
    if not value:
        return True
    normalized = value.strip().casefold().rstrip(".")
    return normalized in NULL_VALUES or normalized.startswith(("pending", "awaiting"))


def _repository_entries(frontmatter: str) -> list[str]:
    block = _mapping(frontmatter, "repositories")
    if not block:
        return []
    starts = list(re.finditer(r"(?m)^- name:\s*", block))
    entries: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(block)
        entries.append(block[start.start() : end])
    return entries


def _validate_frontmatter(
    frontmatter: str,
    computed_digest: str,
    errors: list[str],
) -> dict[str, str | None]:
    duplicate_top_level = sorted(
        key for key, count in Counter(_top_level_keys(frontmatter)).items() if count > 1
    )
    for key in duplicate_top_level:
        errors.append(f"frontmatter contains duplicate top-level key: {key}")

    keys = [
        "schema_version",
        "plan_revision",
        "plan_digest",
        "change_id",
        "title",
        "change_kind",
        "complexity",
        "status",
        "qaas_classification",
    ]
    values = {key: _top_scalar(frontmatter, key) for key in keys}
    for key, value in values.items():
        if not value:
            errors.append(f"frontmatter is missing {key}")

    if values["schema_version"] not in {None, "4"}:
        errors.append('schema_version must be "4"')
    revision = values["plan_revision"]
    if revision and (not revision.isdigit() or int(revision) < 1):
        errors.append("plan_revision must be a positive integer")
    if values["change_kind"] and values["change_kind"] not in ALLOWED_KIND:
        errors.append(f"change_kind must be one of {sorted(ALLOWED_KIND)}")
    if values["complexity"] and values["complexity"] not in ALLOWED_COMPLEXITY:
        errors.append(f"complexity must be one of {sorted(ALLOWED_COMPLEXITY)}")
    if values["status"] and values["status"] not in ALLOWED_STATUS:
        errors.append(f"status must be one of {sorted(ALLOWED_STATUS)}")
    if (
        values["qaas_classification"]
        and values["qaas_classification"] not in ALLOWED_CLASSIFICATION
    ):
        errors.append(
            f"qaas_classification must be one of {sorted(ALLOWED_CLASSIFICATION)}"
        )

    if values["change_id"] and not re.fullmatch(
        r"qaas-[a-z0-9]+(?:-[a-z0-9]+)*", values["change_id"]
    ):
        errors.append("change_id must be a lowercase qaas-<slug>")

    plan_digest = values["plan_digest"]
    if plan_digest and not _is_null(plan_digest):
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", plan_digest):
            errors.append("plan_digest must be sha256 plus 64 lowercase hex characters")
        elif plan_digest != computed_digest:
            errors.append("plan_digest does not match the frozen plan content")

    entries = _repository_entries(frontmatter)
    if not entries:
        errors.append("frontmatter must list at least one inspected repository")
    for index, entry in enumerate(entries, start=1):
        prefix = f"repository {index}"
        for key in ("name", "checkout", "inspected_commit", "worktree_fingerprint"):
            if _field_count(entry, key) > 1:
                errors.append(f"{prefix} contains duplicate field: {key}")
        name = _scalar(entry, "- name") or _scalar(entry, "name")
        checkout = _scalar(entry, "checkout")
        commit = _scalar(entry, "inspected_commit")
        fingerprint = _scalar(entry, "worktree_fingerprint")
        if not name:
            errors.append(f"{prefix} is missing name")
        elif not re.fullmatch(r"TheSmokeTeam/[A-Za-z0-9._-]+", name):
            errors.append(f"{prefix} name must be TheSmokeTeam/<repository>")
        if not checkout:
            errors.append(f"{prefix} is missing checkout")
        elif not Path(checkout).is_absolute():
            errors.append(f"{prefix} checkout must be an absolute path")
        if not commit or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
            errors.append(f"{prefix} inspected_commit must be a full 40-character SHA")
        if not fingerprint or not re.fullmatch(r"sha256:[0-9a-fA-F]{64}", fingerprint):
            errors.append(f"{prefix} worktree_fingerprint must be sha256 plus 64 hex characters")

    review = _mapping(frontmatter, "review")
    for key in ("verdict", "reviewed_revision", "reviewed_digest", "evidence"):
        if _field_count(review, key) > 1:
            errors.append(f"review contains duplicate field: {key}")
    verdict = _scalar(review, "verdict")
    reviewed_revision = _scalar(review, "reviewed_revision")
    reviewed_digest = _scalar(review, "reviewed_digest")
    review_evidence = _scalar(review, "evidence")
    if not review:
        errors.append("frontmatter must include review")
    if not verdict:
        errors.append("review is missing verdict")
    elif verdict not in ALLOWED_REVIEW:
        errors.append(f"review verdict must be one of {sorted(ALLOWED_REVIEW)}")
    if reviewed_revision is None:
        errors.append("review is missing reviewed_revision")
    elif verdict == "PENDING" and not _is_null(reviewed_revision):
        errors.append("PENDING review must not record reviewed_revision")
    elif verdict and verdict != "PENDING" and reviewed_revision != revision:
        errors.append("reviewed_revision must match plan_revision for a completed review")
    if reviewed_digest is None:
        errors.append("review is missing reviewed_digest")
    elif verdict == "PENDING" and not _is_null(reviewed_digest):
        errors.append("PENDING review must not record reviewed_digest")
    elif verdict and verdict != "PENDING" and reviewed_digest != plan_digest:
        errors.append("reviewed_digest must match plan_digest for a completed review")
    if not review_evidence:
        errors.append("review is missing evidence")
    elif verdict and verdict != "PENDING" and _is_unresolved_evidence(review_evidence):
        errors.append("completed review requires resolved evidence")

    approval = _mapping(frontmatter, "developer_approval")
    for key in ("status", "approved_revision", "approved_digest", "evidence"):
        if _field_count(approval, key) > 1:
            errors.append(f"developer_approval contains duplicate field: {key}")
    developer_status = _scalar(approval, "status")
    approved_revision = _scalar(approval, "approved_revision")
    approved_digest = _scalar(approval, "approved_digest")
    approval_evidence = _scalar(approval, "evidence")
    if not approval:
        errors.append("frontmatter must include developer_approval")
    if not developer_status:
        errors.append("developer_approval is missing status")
    elif developer_status not in ALLOWED_DEVELOPER_APPROVAL:
        errors.append(
            "developer_approval status must be one of "
            f"{sorted(ALLOWED_DEVELOPER_APPROVAL)}"
        )
    if approved_revision is None:
        errors.append("developer_approval is missing approved_revision")
    if approved_digest is None:
        errors.append("developer_approval is missing approved_digest")
    if not approval_evidence:
        errors.append("developer_approval is missing evidence")
    elif (
        developer_status
        and developer_status != "PENDING"
        and _is_unresolved_evidence(approval_evidence)
    ):
        errors.append("completed developer approval decision requires resolved evidence")

    release = _mapping(frontmatter, "release")
    for key in ("authorization", "targets"):
        if _field_count(release, key) > 1:
            errors.append(f"release contains duplicate field: {key}")
    release_authorization = _scalar(release, "authorization")
    release_targets = _scalar(release, "targets")
    if not release:
        errors.append("frontmatter must include release")
    if release_authorization not in ALLOWED_RELEASE_AUTHORIZATION:
        errors.append(
            "release authorization must be one of "
            f"{sorted(ALLOWED_RELEASE_AUTHORIZATION)}"
        )
    if not release_targets:
        errors.append("release is missing targets")
    elif (
        release_authorization == "AUTHORIZED_AFTER_VERIFICATION"
        and release_targets.strip().casefold() in {"n/a", "none", "null", "~"}
    ):
        errors.append("authorized release requires explicit targets")

    status = values["status"]
    if status in FULL_PLAN_STATUSES:
        if plan_digest != computed_digest:
            errors.append(f"{status} plan requires a current plan_digest")
        if values["qaas_classification"] == "undetermined":
            errors.append(f"{status} plan cannot have undetermined classification")
        if verdict != "APPROVE":
            errors.append(f"{status} plan requires review verdict APPROVE")
        if reviewed_revision != revision:
            errors.append("reviewed_revision must match the current plan_revision")
        if reviewed_digest != plan_digest:
            errors.append("reviewed_digest must match the current plan_digest")
    if status == "AWAITING_APPROVAL":
        if developer_status != "PENDING":
            errors.append("AWAITING_APPROVAL requires developer approval PENDING")
        if not _is_null(approved_revision):
            errors.append("AWAITING_APPROVAL must not record approved_revision")
        if not _is_null(approved_digest):
            errors.append("AWAITING_APPROVAL must not record approved_digest")
    elif status == "APPROVED":
        if developer_status != "APPROVED":
            errors.append("APPROVED plan requires explicit developer approval")
        if approved_revision != revision:
            errors.append("approved_revision must match the current plan_revision")
        if approved_digest != plan_digest:
            errors.append("approved_digest must match the current plan_digest")
    elif (
        developer_status == "APPROVED"
        or (approved_revision is not None and not _is_null(approved_revision))
        or (approved_digest is not None and not _is_null(approved_digest))
    ):
        errors.append("non-APPROVED plan must reset developer approval and revision")

    values.update(
        {
            "review_verdict": verdict,
            "reviewed_revision": reviewed_revision,
            "reviewed_digest": reviewed_digest,
            "developer_status": developer_status,
            "approved_revision": approved_revision,
            "approved_digest": approved_digest,
            "release_authorization": release_authorization,
        }
    )
    return values


def _validate_full_body(body: str, values: dict[str, str | None], errors: list[str]) -> None:
    positions: list[int] = []
    for heading in REQUIRED_HEADINGS:
        position = body.find(heading)
        if position == -1:
            errors.append(f"review-ready plan is missing heading: {heading}")
        positions.append(position)
    present_positions = [position for position in positions if position >= 0]
    if present_positions != sorted(present_positions):
        errors.append("numbered plan sections must appear in schema order")

    context = _section(body, REQUIRED_HEADINGS[0])
    if "### Know QaaS Context Brief" not in context:
        errors.append("Context and Request is missing Know QaaS Context Brief")
    previous = -1
    for index, heading in enumerate(KNOW_QAAS_SUBHEADINGS):
        position = context.find(heading)
        if position == -1:
            errors.append(f"Know QaaS Context Brief is missing heading: {heading}")
            continue
        if position < previous:
            errors.append("Know QaaS Context Brief headings are out of order")
        previous = position
        content_start = position + len(heading)
        next_positions = [
            context.find(candidate, content_start)
            for candidate in KNOW_QAAS_SUBHEADINGS[index + 1 :]
        ]
        next_positions = [item for item in next_positions if item >= 0]
        content_end = min(next_positions) if next_positions else len(context)
        if not context[content_start:content_end].strip():
            errors.append(f"Know QaaS Context Brief has empty section: {heading}")

    decisions = _section(body, REQUIRED_HEADINGS[1])
    if not re.search(r"(?im)^Confirmed by the developer:\s*Yes\s*$", decisions):
        errors.append("developer must confirm shared understanding before review")
    if not re.search(r"(?m)^\|\s*D-\d+\s*\|", decisions) and not re.search(
        r"(?im)^No material developer-owned decisions after research\.\s*$",
        decisions,
    ):
        errors.append(
            "developer interview must record D-<n> decisions or state that research "
            "found no material developer-owned decisions"
        )

    implementation = _section(body, REQUIRED_HEADINGS[5])
    steps = list(re.finditer(r"(?m)^### Step (P\d+)\b.*$", implementation))
    if not steps:
        errors.append("review-ready plan must contain at least one numbered Step P<n>")
    step_ids = [match.group(1) for match in steps]
    if len(step_ids) != len(set(step_ids)):
        errors.append("implementation step IDs must be unique")
    expected_step_ids = [f"P{index}" for index in range(1, len(step_ids) + 1)]
    if step_ids and step_ids != expected_step_ids:
        errors.append("implementation steps must be contiguous and ordered P1..Pn")
    for index, match in enumerate(steps):
        step_id = match.group(1)
        end = steps[index + 1].start() if index + 1 < len(steps) else len(implementation)
        block = implementation[match.end() : end]
        for field in STEP_FIELDS:
            if not re.search(rf"(?m)^- {re.escape(field)}:\s*\S", block):
                errors.append(f"{step_id} is missing populated field: {field}")

    desired = _section(body, REQUIRED_HEADINGS[3])
    acceptance_section = _subsection(desired, "### Acceptance criteria")
    acceptance_definitions = re.findall(r"(?m)^- (AC-\d+):", acceptance_section)
    if len(acceptance_definitions) != len(set(acceptance_definitions)):
        errors.append("acceptance criterion IDs must be unique")
    acceptance_ids = sorted(set(acceptance_definitions))
    if not acceptance_ids:
        errors.append("review-ready plan must define at least one acceptance criterion")

    verification = _section(body, REQUIRED_HEADINGS[6])
    test_plan = _subsection(verification, "### Test plan")
    traceability = _subsection(verification, "### Traceability matrix")
    test_definitions = re.findall(r"(?m)^\|\s*(T-\d+)\s*\|", test_plan)
    if len(test_definitions) != len(set(test_definitions)):
        errors.append("test IDs must be unique")
    test_ids = sorted(set(test_definitions))
    if not test_ids:
        errors.append("review-ready plan must define at least one T-<n> test row")

    for criterion in acceptance_ids:
        if not re.search(rf"(?m)^\|\s*{re.escape(criterion)}\s*\|", traceability):
            errors.append(f"{criterion} is missing from the traceability matrix")
        if not re.search(rf"(?m)^- Acceptance criteria:.*\b{re.escape(criterion)}\b", implementation):
            errors.append(f"{criterion} is not referenced by an implementation step")
    for test_id in test_ids:
        if not re.search(rf"(?m)^- Tests:.*\b{re.escape(test_id)}\b", implementation):
            errors.append(f"{test_id} is not referenced by an implementation step")

    review_section = _section(body, REQUIRED_HEADINGS[7])
    open_items = _subsection(review_section, "### Open decisions and missing evidence")
    if re.sub(r"[\s.]", "", open_items).casefold() != "none":
        errors.append("review-ready plan must have no open decisions or missing evidence")

    revision = values["plan_revision"] or ""
    if not re.search(
        rf"(?m)^\|\s*{re.escape(revision)}\s*\|\s*APPROVE\s*\|",
        review_section,
    ):
        errors.append("technical review history must approve the current revision")
    expected_decision = "Pending" if values["status"] == "AWAITING_APPROVAL" else "Approved"
    if not re.search(
        rf"(?im)^\|\s*{re.escape(revision)}\s*\|\s*{expected_decision}\s*\|\s*\S",
        review_section,
    ):
        errors.append(
            "developer approval history must record the current revision and "
            f"decision {expected_decision} with evidence"
        )


def validate_text(text: str) -> list[str]:
    errors: list[str] = []
    try:
        frontmatter, body = _frontmatter(text)
    except ValueError as exc:
        return [str(exc)]

    computed_digest = compute_plan_digest(text)
    values = _validate_frontmatter(frontmatter, computed_digest, errors)
    if values["status"] in FULL_PLAN_STATUSES:
        for pattern, label in PLACEHOLDER_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                errors.append(
                    f"review-ready plan contains forbidden placeholder: {label}"
                )
        if _angle_placeholder_present(text):
            errors.append(
                "review-ready plan contains forbidden placeholder: "
                "angle-bracket placeholder"
            )
        _validate_full_body(body, values, errors)
    return errors


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a QaaS change plan.")
    parser.add_argument("plan", help="plan Markdown path, or - for stdin")
    parser.add_argument(
        "--print-digest",
        action="store_true",
        help="print the canonical frozen-plan digest and exit",
    )
    args = parser.parse_args()
    try:
        text = _read(args.plan)
    except (OSError, UnicodeError) as exc:
        print(f"validate-plan: unable to read plan: {exc}", file=sys.stderr)
        return 2

    if args.print_digest:
        try:
            print(compute_plan_digest(text))
        except ValueError as exc:
            print(f"validate-plan: {exc}", file=sys.stderr)
            return 2
        return 0

    errors = validate_text(text)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"validate-plan: FAILED ({len(errors)} error(s))", file=sys.stderr)
        return 1
    print("validate-plan: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
