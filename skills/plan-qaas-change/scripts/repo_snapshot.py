#!/usr/bin/env python3
"""Capture or verify the Git baseline used by a QaaS change plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path


class SnapshotError(RuntimeError):
    """Raised when a repository baseline cannot be captured."""


GITHUB_REMOTE_PATTERNS = (
    re.compile(
        r"^(?:https?://|git://|ssh://(?:git@)?)github\.com/"
        r"(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)"
        r"(?:\.git)?/?$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^git@github\.com:(?P<owner>[A-Za-z0-9_.-]+)/"
        r"(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?$",
        re.IGNORECASE,
    ),
)


def _git(repo: Path, *args: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args], stderr=subprocess.PIPE
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", b"").decode("utf-8", errors="replace").strip()
        raise SnapshotError(detail or str(exc)) from exc


def _hash_untracked(hasher: "hashlib._Hash", root: Path, relative: bytes) -> None:
    path_text = os.fsdecode(relative)
    path = root / path_text
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise SnapshotError(f"unable to inspect untracked path {path}: {exc}") from exc
    mode = stat.S_IFMT(metadata.st_mode) | stat.S_IMODE(metadata.st_mode)
    hasher.update(b"untracked\0" + relative + b"\0")
    hasher.update(f"mode:{mode:o}\0".encode("ascii"))
    if path.is_symlink():
        hasher.update(b"symlink\0" + os.fsencode(os.readlink(path)))
    else:
        try:
            hasher.update(b"file\0" + path.read_bytes())
        except OSError as exc:
            raise SnapshotError(f"unable to read untracked path {path}: {exc}") from exc
    hasher.update(b"\0")


def _repository_identity(root: Path) -> str | None:
    try:
        remote = _git(root, "remote", "get-url", "origin").decode().strip()
    except SnapshotError:
        return None
    for pattern in GITHUB_REMOTE_PATTERNS:
        match = pattern.fullmatch(remote)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def snapshot(path: str | Path) -> dict[str, object]:
    requested = Path(path).expanduser().resolve()
    root_text = _git(requested, "rev-parse", "--show-toplevel").decode().strip()
    root = Path(root_text).resolve()
    commit = _git(root, "rev-parse", "HEAD").decode().strip()
    if len(commit) != 40:
        raise SnapshotError("repository HEAD did not resolve to a full commit SHA")

    tracked_diff = _git(root, "diff", "--binary", "HEAD", "--", ".")
    untracked_raw = _git(root, "ls-files", "--others", "--exclude-standard", "-z")
    untracked = sorted(item for item in untracked_raw.split(b"\0") if item)
    status = _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")

    hasher = hashlib.sha256()
    hasher.update(b"qaas-worktree-v2\0tracked\0")
    hasher.update(tracked_diff)
    hasher.update(b"\0")
    for relative in untracked:
        _hash_untracked(hasher, root, relative)

    return {
        "checkout": str(root),
        "repository": _repository_identity(root),
        "inspected_commit": commit,
        "worktree_fingerprint": f"sha256:{hasher.hexdigest()}",
        "worktree_clean": not bool(status),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture or verify a QaaS plan repository baseline."
    )
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--expect-commit")
    parser.add_argument("--expect-fingerprint")
    parser.add_argument("--expect-repository")
    args = parser.parse_args()

    try:
        result = snapshot(args.repository)
    except SnapshotError as exc:
        print(f"repo-snapshot: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    mismatches: list[str] = []
    if args.expect_repository and result["repository"] != args.expect_repository:
        mismatches.append("repository identity")
    if args.expect_commit and result["inspected_commit"] != args.expect_commit:
        mismatches.append("commit")
    if (
        args.expect_fingerprint
        and result["worktree_fingerprint"] != args.expect_fingerprint
    ):
        mismatches.append("worktree fingerprint")
    if mismatches:
        print(f"repo-snapshot: STALE ({', '.join(mismatches)} changed)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
