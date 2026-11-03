#!/usr/bin/env python3
"""Validate the structural contract of a QaaS implementation plan."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ALLOWED_STATUS = {"DRAFT", "NEEDS_DECISION", "BLOCKED", "APPROVED", "STALE"}
ALLOWED_KIND = {"feature", "bugfix"}
ALLOWED_COMPLEXITY = {"small", "standard", "cross-repo"}
ALLOWED_CLASSIFICATION = {
    "type-a",
    "type-b",
    "existing-behavior",
    "not-applicable",
}
REQUIRED_APPROVED_HEADINGS = [
    "## 1. Know QaaS Context Brief",
    "## 2. Developer summary",
    "## 3. Request",
    "## 4. Current-state evidence",
    "## 5. Current behavior",
    "## 6. Desired-state specification",
    "## 7. Impact map",
    "## 8. Exact implementation sequence",
    "## 9. Traceability matrix",
    "## 10. Test-first verification plan",
    "## 11. Release and rollout",
    "## 12. Risks",
    "## 13. Open decisions and missing evidence",
    "## 14. Review record",
    "## 15. Implementation handoff",
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

    if values["schema_version"] not in {None, "2"}:
        errors.append("schema_version must be \"2\"")
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

    status = values["status"]
    if status != "APPROVED":
        return errors

    for heading in REQUIRED_APPROVED_HEADINGS:
        if heading not in body:
            errors.append(f"approved plan is missing heading: {heading}")

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

    verdicts = re.findall(r"(?m)^\s*verdict:\s*(\S+)\s*$", frontmatter)
    if "APPROVE" not in verdicts:
        errors.append("approved plan must record review verdict APPROVE")

    for pattern, label in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"approved plan contains forbidden placeholder: {label}")

    step_matches = list(re.finditer(r"(?m)^### Step (P\d+)\b.*$", body))
    if not step_matches:
        errors.append("approved plan must contain at least one numbered Step P<n>")
    for index, match in enumerate(step_matches):
        step_id = match.group(1)
        end = step_matches[index + 1].start() if index + 1 < len(step_matches) else len(body)
        block = body[match.end() : end]
        for field in STEP_FIELDS:
            if not re.search(rf"(?m)^- {re.escape(field)}:\s*\S", block):
                errors.append(f"{step_id} is missing populated field: {field}")

    acceptance_ids = sorted(set(re.findall(r"(?m)^- (AC-\d+):", body)))
    if not acceptance_ids:
        errors.append("approved plan must define at least one acceptance criterion")
    for criterion in acceptance_ids:
        if len(re.findall(rf"\b{re.escape(criterion)}\b", body)) < 3:
            errors.append(
                f"{criterion} must appear in its definition, an implementation step, and traceability"
            )

    test_ids = sorted(set(re.findall(r"(?m)^\|\s*(T-\d+)\s*\|", body)))
    if not test_ids:
        errors.append("approved plan must define at least one T-<n> test row")
    for test_id in test_ids:
        if len(re.findall(rf"\b{re.escape(test_id)}\b", body)) < 2:
            errors.append(f"{test_id} must be referenced by an implementation step")

    open_items = _section(body, "## 13. Open decisions and missing evidence")
    normalized_open_items = re.sub(r"[\s.]", "", open_items).casefold()
    if normalized_open_items != "none":
        errors.append(
            "approved plan must contain only 'None.' under open decisions and missing evidence"
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
