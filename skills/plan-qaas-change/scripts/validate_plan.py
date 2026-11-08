#!/usr/bin/env python3
"""Validate the structural contract of a QaaS implementation plan."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ALLOWED_STATUS = {
    "DRAFT",
    "NEEDS_DECISION",
    "BLOCKED",
    "AWAITING_APPROVAL",
    "APPROVED",
    "STALE",
}
ALLOWED_DEVELOPER_APPROVAL = {"PENDING", "APPROVED", "CHANGES_REQUESTED"}
FULL_PLAN_STATUSES = {"AWAITING_APPROVAL", "APPROVED"}
ALLOWED_KIND = {"feature", "bugfix"}
ALLOWED_COMPLEXITY = {"small", "standard", "cross-repo"}
ALLOWED_CLASSIFICATION = {
    "type-a",
    "type-b",
    "existing-behavior",
    "not-applicable",
}
REQUIRED_REVIEWED_HEADINGS = [
    "## 1. Know QaaS Context Brief",
    "## 2. Developer interview record",
    "## 3. Developer summary",
    "## 4. Request",
    "## 5. Current-state evidence",
    "## 6. Current behavior",
    "## 7. Desired-state specification",
    "## 8. Impact map",
    "## 9. Exact implementation sequence",
    "## 10. Traceability matrix",
    "## 11. Test-first verification plan",
    "## 12. Release and rollout",
    "## 13. Risks",
    "## 14. Open decisions and missing evidence",
    "## 15. Review record",
    "## 16. Developer approval",
    "## 17. Implementation handoff",
]
KNOW_QAAS_SUBHEADINGS = [
    "### Platform scope",
    "### Ecosystem location",
    "### Dependency position",
    "### Extension model",
    "### Release ripple",
    "### Authority map",
    "### Known unknowns",
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
    (r"<[^>\n]+>", "angle-bracket placeholder"),
    (r"\bas needed\b", "as needed"),
    (r"\brelevant files?\b", "relevant files"),
    (r"\bto be determined\b", "to be determined"),
]


def _frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("plan must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("plan frontmatter is not closed with ---")
    return text[4:end], text[end + 5 :]


def _scalar(frontmatter: str, key: str) -> str | None:
    match = re.search(
        rf"(?m)^{re.escape(key)}:\s*[\"']?([^\n\"']+?)[\"']?\s*$",
        frontmatter,
    )
    return match.group(1).strip() if match else None


def _mapping(frontmatter: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*$", frontmatter)
    if not match:
        return ""
    remainder = frontmatter[match.end() :]
    next_top_level = re.search(r"(?m)^[A-Za-z_][A-Za-z0-9_-]*:\s*", remainder)
    block = remainder[: next_top_level.start()] if next_top_level else remainder
    return "\n".join(
        line[2:] if line.startswith("  ") else line
        for line in block.strip("\n").splitlines()
    )


def _section(body: str, heading: str) -> str:
    start = body.find(heading)
    if start == -1:
        return ""
    content_start = start + len(heading)
    next_heading = re.search(r"(?m)^## \d+\. ", body[content_start:])
    end = (
        content_start + next_heading.start()
        if next_heading
        else len(body)
    )
    return body[content_start:end].strip()


def validate_text(text: str) -> list[str]:
    errors: list[str] = []
    try:
        frontmatter, body = _frontmatter(text)
    except ValueError as exc:
        return [str(exc)]

    required_scalars = [
        "schema_version",
        "plan_revision",
        "change_id",
        "title",
        "change_kind",
        "complexity",
        "status",
        "qaas_classification",
    ]
    values = {key: _scalar(frontmatter, key) for key in required_scalars}
    for key, value in values.items():
        if not value:
            errors.append(f"frontmatter is missing {key}")

    if values["schema_version"] not in {None, "3"}:
        errors.append("schema_version must be \"3\"")
    plan_revision = values["plan_revision"]
    if plan_revision and (not plan_revision.isdigit() or int(plan_revision) < 1):
        errors.append("plan_revision must be a positive integer")
    if values["change_kind"] and values["change_kind"] not in ALLOWED_KIND:
        errors.append("change_kind must be feature or bugfix")
    if values["complexity"] and values["complexity"] not in ALLOWED_COMPLEXITY:
        errors.append("complexity must be small, standard, or cross-repo")
    if values["status"] and values["status"] not in ALLOWED_STATUS:
        errors.append(f"status must be one of {sorted(ALLOWED_STATUS)}")
    if (
        values["qaas_classification"]
        and values["qaas_classification"] not in ALLOWED_CLASSIFICATION
    ):
        errors.append(
            f"qaas_classification must be one of {sorted(ALLOWED_CLASSIFICATION)}"
        )

    repo_names = re.findall(r"(?m)^\s*- name:\s*(\S+)\s*$", frontmatter)
    commits = re.findall(
        r"(?m)^\s*inspected_commit:\s*([0-9a-fA-F]{7,40})\s*$", frontmatter
    )
    if not repo_names:
        errors.append("frontmatter must list at least one inspected repository")
    if len(commits) != len(repo_names):
        errors.append("every inspected repository must have a 7-40 character commit SHA")

    developer_approval = _mapping(frontmatter, "developer_approval")
    developer_status = _scalar(developer_approval, "status")
    approved_revision = _scalar(developer_approval, "approved_revision")
    if not developer_approval:
        errors.append("frontmatter must include developer_approval")
    elif not developer_status:
        errors.append("developer_approval is missing status")
    elif developer_status not in ALLOWED_DEVELOPER_APPROVAL:
        errors.append(
            f"developer_approval status must be one of {sorted(ALLOWED_DEVELOPER_APPROVAL)}"
        )
    if developer_approval and approved_revision is None:
        errors.append("developer_approval is missing approved_revision")

    status = values["status"]
    if status not in FULL_PLAN_STATUSES:
        return errors

    for heading in REQUIRED_REVIEWED_HEADINGS:
        if heading not in body:
            errors.append(f"reviewed plan is missing heading: {heading}")

    know_qaas = _section(body, "## 1. Know QaaS Context Brief")
    for index, heading in enumerate(KNOW_QAAS_SUBHEADINGS):
        if heading not in know_qaas:
            errors.append(f"Know QaaS Context Brief is missing heading: {heading}")
            continue
        content_start = know_qaas.find(heading) + len(heading)
        content_end = (
            know_qaas.find(KNOW_QAAS_SUBHEADINGS[index + 1], content_start)
            if index + 1 < len(KNOW_QAAS_SUBHEADINGS)
            else len(know_qaas)
        )
        if content_end == -1:
            content_end = len(know_qaas)
        if not know_qaas[content_start:content_end].strip():
            errors.append(f"Know QaaS Context Brief has empty section: {heading}")

    interview = _section(body, "## 2. Developer interview record")
    if "### Shared understanding" not in interview:
        errors.append("developer interview is missing Shared understanding")
    if "### Decisions" not in interview:
        errors.append("developer interview is missing Decisions")
    if "### Rejected scope and alternatives" not in interview:
        errors.append("developer interview is missing Rejected scope and alternatives")
    if not re.search(
        r"(?im)^Confirmed by the developer:\s*Yes\s*$", interview
    ):
        errors.append("developer must confirm shared understanding before review")
    if not re.search(r"(?m)^\|\s*D-\d+\s*\|", interview):
        errors.append("developer interview must record at least one D-<n> decision")

    verdicts = re.findall(r"(?m)^\s*verdict:\s*(\S+)\s*$", frontmatter)
    if "APPROVE" not in verdicts:
        errors.append("reviewed plan must record review verdict APPROVE")

    if status == "AWAITING_APPROVAL":
        if developer_status != "PENDING":
            errors.append(
                "AWAITING_APPROVAL plan must have developer_approval status PENDING"
            )
        if approved_revision and approved_revision.casefold() not in {"null", "none", "~"}:
            errors.append(
                "AWAITING_APPROVAL plan must not record an approved_revision"
            )
    elif status == "APPROVED":
        if developer_status != "APPROVED":
            errors.append("APPROVED plan requires explicit developer approval")
        if approved_revision != plan_revision:
            errors.append(
                "developer approved_revision must match the current plan_revision"
            )

    approval_section = _section(body, "## 16. Developer approval")
    if not re.search(
        rf"(?m)^- Plan revision:\s*{re.escape(plan_revision or '')}\s*$",
        approval_section,
    ):
        errors.append("Developer approval section must name the current plan revision")
    expected_decision = "Pending" if status == "AWAITING_APPROVAL" else "Approved"
    if not re.search(
        rf"(?im)^- Decision:\s*{expected_decision}\s*$", approval_section
    ):
        errors.append(
            f"Developer approval section must record decision {expected_decision}"
        )

    for pattern, label in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"reviewed plan contains forbidden placeholder: {label}")

    step_matches = list(re.finditer(r"(?m)^### Step (P\d+)\b.*$", body))
    if not step_matches:
        errors.append("reviewed plan must contain at least one numbered Step P<n>")
    for index, match in enumerate(step_matches):
        step_id = match.group(1)
        end = step_matches[index + 1].start() if index + 1 < len(step_matches) else len(body)
        block = body[match.end() : end]
        for field in STEP_FIELDS:
            if not re.search(rf"(?m)^- {re.escape(field)}:\s*\S", block):
                errors.append(f"{step_id} is missing populated field: {field}")

    acceptance_ids = sorted(set(re.findall(r"(?m)^- (AC-\d+):", body)))
    if not acceptance_ids:
        errors.append("reviewed plan must define at least one acceptance criterion")
    for criterion in acceptance_ids:
        if len(re.findall(rf"\b{re.escape(criterion)}\b", body)) < 3:
            errors.append(
                f"{criterion} must appear in its definition, an implementation step, and traceability"
            )

    test_ids = sorted(set(re.findall(r"(?m)^\|\s*(T-\d+)\s*\|", body)))
    if not test_ids:
        errors.append("reviewed plan must define at least one T-<n> test row")
    for test_id in test_ids:
        if len(re.findall(rf"\b{re.escape(test_id)}\b", body)) < 2:
            errors.append(f"{test_id} must be referenced by an implementation step")

    open_items = _section(body, "## 14. Open decisions and missing evidence")
    normalized_open_items = re.sub(r"[\s.]", "", open_items).casefold()
    if normalized_open_items != "none":
        errors.append(
            "reviewed plan must contain only 'None.' under open decisions and missing evidence"
        )

    return errors


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a QaaS Change Specification and Implementation Plan."
    )
    parser.add_argument("plan", help="plan Markdown path, or - for stdin")
    args = parser.parse_args()
    try:
        text = _read(args.plan)
    except (OSError, UnicodeError) as exc:
        print(f"validate-plan: unable to read plan: {exc}", file=sys.stderr)
        return 2

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
