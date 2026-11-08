#!/usr/bin/env python3
"""Deterministically lint the local Claude Code behavioral-eval layout."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ALLOWED_GRADER_TYPES = {
    "baseline",
    "file_exists",
    "llm",
    "regex",
    "tool_order",
    "tool_used",
}


def frontmatter(text: str, path: Path) -> str:
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: unclosed frontmatter")
    return text[4:end]


def scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*[\"']?([^\n\"']+)", text)
    return match.group(1).strip() if match else None


def lint(root: Path) -> list[str]:
    errors: list[str] = []
    cases = sorted(
        path
        for path in root.rglob("*")
        if path.is_dir() and ((path / "prompt.md").exists() or (path / "case.yaml").exists())
    )
    if not cases:
        return [f"{root}: no eval cases found"]

    for case in cases:
        prompt = case / "prompt.md"
        metadata = case / "case.yaml"
        graders = case / "graders"
        for required in (prompt, metadata):
            if not required.is_file():
                errors.append(f"{case}: missing {required.name}")
        if not prompt.is_file() or not metadata.is_file():
            continue

        prompt_text = prompt.read_text(encoding="utf-8")
        if prompt_text.startswith("---\n"):
            errors.append(f"{prompt}: metadata belongs in case.yaml")
        if not prompt_text.strip():
            errors.append(f"{prompt}: prompt is empty")

        case_text = metadata.read_text(encoding="utf-8")
        if scalar(case_text, "schema_version") != "1.1":
            errors.append(f'{metadata}: schema_version must be "1.1"')
        if scalar(case_text, "name") != case.name:
            errors.append(f"{metadata}: name must match directory {case.name}")
        if not re.search(r"(?m)^execution:\s*$", case_text):
            errors.append(f"{metadata}: missing execution mapping")
        if not re.search(r"(?m)^\s+allowed_tools:\s*\[", case_text):
            errors.append(f"{metadata}: execution must declare allowed_tools")
        scaffold = scalar(case_text, "scaffold_script")
        if scaffold and not (case / scaffold).is_file():
            errors.append(f"{metadata}: missing scaffold script {scaffold}")

        grader_files = sorted(graders.glob("*.md")) if graders.is_dir() else []
        if not grader_files:
            errors.append(f"{case}: missing graders")
            continue
        if not (graders / "result.md").is_file() and case.name != "knowledge-only":
            errors.append(f"{case}: missing result.md outcome grader")
        for grader in grader_files:
            try:
                fm = frontmatter(grader.read_text(encoding="utf-8"), grader)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            grader_type = scalar(fm, "type")
            if grader_type not in ALLOWED_GRADER_TYPES:
                errors.append(f"{grader}: unsupported grader type {grader_type!r}")
            if grader_type == "tool_order" and not (
                re.search(r"(?m)^before:\s*$", fm)
                and re.search(r"(?m)^after:\s*$", fm)
            ):
                errors.append(f"{grader}: tool_order requires before and after")
            if grader.name in {"no-edit.md", "no-editing.md", "no-write.md"}:
                errors.append(
                    f"{grader}: mutation graders belong only in a case that grants mutation tools"
                )
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "evals")
    errors = lint(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"lint-evals: FAILED ({len(errors)} error(s))", file=sys.stderr)
        return 1
    print("lint-evals: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
