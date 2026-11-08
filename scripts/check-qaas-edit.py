#!/usr/bin/env python3
"""Post-edit whitespace guard for files in TheSmokeTeam Git repositories."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


THESMOKETEAM_REMOTE_PATTERNS = (
    re.compile(
        r"^(?:https?://|git://|ssh://(?:git@)?)github\.com/"
        r"TheSmokeTeam/[A-Za-z0-9_.-]+(?:\.git)?/?$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^git@github\.com:TheSmokeTeam/[A-Za-z0-9_.-]+(?:\.git)?$",
        re.IGNORECASE,
    ),
)


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _existing_parent(path: Path) -> Path:
    candidate = path
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return candidate if candidate.is_dir() else candidate.parent


def repository_for(path: Path) -> Path | None:
    result = _git(_existing_parent(path), "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        return None
    root = Path(result.stdout.strip()).resolve()
    origin = _git(root, "remote", "get-url", "--all", "origin")
    origin_urls = origin.stdout.splitlines()
    if origin.returncode != 0 or not any(
        pattern.fullmatch(url)
        for url in origin_urls
        for pattern in THESMOKETEAM_REMOTE_PATTERNS
    ):
        return None
    return root


def edited_path(payload: dict[str, object]) -> Path | None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    value = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(value, str) or not value:
        return None
    return Path(value).expanduser().resolve()


def untracked_whitespace_errors(path: Path) -> list[str]:
    try:
        data = path.read_bytes()
    except OSError:
        return []
    if b"\0" in data:
        return []
    errors: list[str] = []
    for number, line in enumerate(data.splitlines(keepends=True), start=1):
        content = line.rstrip(b"\r\n")
        if content.endswith((b" ", b"\t")):
            errors.append(f"{path}:{number}: trailing whitespace")
    return errors


def check(path: Path) -> list[str]:
    root = repository_for(path)
    if root is None or not path.exists() or path.is_dir():
        return []
    try:
        relative = path.relative_to(root)
    except ValueError:
        return []

    tracked = _git(root, "ls-files", "--error-unmatch", "--", str(relative))
    if tracked.returncode != 0:
        return untracked_whitespace_errors(path)
    result = _git(root, "diff", "--check", "--", str(relative))
    if result.returncode == 0:
        return []
    output = (result.stdout + result.stderr).strip()
    return output.splitlines() or [f"{relative}: git diff --check failed"]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    path = edited_path(payload)
    if path is None:
        return 0
    errors = check(path)
    if not errors:
        return 0
    print("QaaS post-edit check found whitespace errors:", file=sys.stderr)
    for error in errors:
        print(error, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
