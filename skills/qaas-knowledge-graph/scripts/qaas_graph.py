#!/usr/bin/env python3
"""Synchronize and query the canonical QaaS Graphify graph without mutating it."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import IO, Sequence


REMOTE_URL = "https://github.com/TheSmokeTeam/qaas-graph.git"
BRANCH = "main"
GRAPH_RELATIVE_PATH = Path("graphify-out/graph.json")
MANAGED_KEY = "qaas.graphCacheManaged"
SYNCED_COMMIT_KEY = "qaas.graphCacheCommit"


class QaasGraphError(RuntimeError):
    """A safe, user-actionable failure."""


def _command(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    timeout: int = 30,
    capture: bool = True,
    stdout: IO[bytes] | int | None = None,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    kwargs: dict[str, object] = {
        "cwd": str(cwd) if cwd else None,
        "env": env,
        "timeout": timeout,
        "check": False,
    }
    if stdout is not None:
        kwargs["stdout"] = stdout
        kwargs["stderr"] = subprocess.PIPE
    elif capture:
        kwargs["capture_output"] = True
        kwargs["text"] = True
    return subprocess.run(list(args), **kwargs)  # type: ignore[arg-type,return-value]


def _git(
    repo: Path,
    *args: str,
    timeout: int = 30,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = _command(["git", "-C", str(repo), *args], timeout=timeout)
    assert isinstance(result.stdout, (str, type(None)))
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "git command failed").strip()
        raise QaasGraphError(detail)
    return result


def _stdout(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stdout or "").strip()


def _canonical_remote(value: str) -> str:
    value = value.strip().rstrip("/")
    ssh_match = re.fullmatch(r"git@github\.com:(.+)", value, re.IGNORECASE)
    if ssh_match:
        value = f"https://github.com/{ssh_match.group(1)}"
    value = re.sub(r"\.git$", "", value, flags=re.IGNORECASE)
    github_match = re.fullmatch(
        r"https?://github\.com/([^/]+/[^/]+)", value, re.IGNORECASE
    )
    if github_match:
        return f"github.com/{github_match.group(1).lower()}"
    try:
        return str(Path(value.removeprefix("file://")).expanduser().resolve())
    except OSError:
        return value


def _same_remote(actual: str, expected: str | None = None) -> bool:
    return _canonical_remote(actual) == _canonical_remote(expected or REMOTE_URL)


def resolve_graph_repo(workspace: Path) -> Path:
    workspace = workspace.expanduser().resolve()
    if not workspace.is_dir():
        raise QaasGraphError(f"workspace is not a directory: {workspace}")

    top = _command(
        ["git", "-C", str(workspace), "rev-parse", "--show-toplevel"]
    )
    if top.returncode == 0 and isinstance(top.stdout, str):
        repo_root = Path(top.stdout.strip()).resolve()
        if repo_root.name.casefold() == "qaas-graph":
            return repo_root
        return repo_root.parent / "qaas-graph"
    return workspace / "qaas-graph"


def validate_graph(path: Path) -> None:
    try:
        with path.open("r", encoding="utf-8") as graph_file:
            graph = json.load(graph_file)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise QaasGraphError(f"invalid graph at {path}: {exc}") from exc

    if not isinstance(graph, dict):
        raise QaasGraphError(f"invalid graph at {path}: root must be an object")
    nodes = graph.get("nodes")
    links = graph.get("links")
    metadata = graph.get("graph")
    if not isinstance(nodes, list) or not nodes:
        raise QaasGraphError(f"invalid graph at {path}: nodes must be non-empty")
    if not isinstance(links, list) or not links:
        raise QaasGraphError(f"invalid graph at {path}: links must be non-empty")
    if not isinstance(metadata, dict) or "schema_version" not in metadata:
        raise QaasGraphError(f"invalid graph at {path}: schema metadata is missing")
    first_node = nodes[0]
    first_link = links[0]
    if not isinstance(first_node, dict) or not {"id", "label"} <= first_node.keys():
        raise QaasGraphError(f"invalid graph at {path}: node structure is invalid")
    if not isinstance(first_link, dict) or not {"source", "target"} <= first_link.keys():
        raise QaasGraphError(f"invalid graph at {path}: link structure is invalid")
    if not any(
        isinstance(node, dict)
        and node.get("repo")
        and node.get("source_file")
        and node.get("source_location")
        for node in nodes
    ):
        raise QaasGraphError(f"invalid graph at {path}: source provenance is missing")


def _remote_head() -> tuple[str | None, str | None]:
    result = _command(
        ["git", "ls-remote", REMOTE_URL, f"refs/heads/{BRANCH}"], timeout=30
    )
    if result.returncode != 0 or not isinstance(result.stdout, str):
        detail = (result.stderr or "remote check failed").strip()
        return None, detail
    fields = result.stdout.strip().split()
    if len(fields) < 2 or fields[1] != f"refs/heads/{BRANCH}":
        return None, f"remote branch {BRANCH!r} was not found"
    return fields[0], None


def _is_git_repo(repo: Path) -> bool:
    return _git(repo, "rev-parse", "--is-inside-work-tree", check=False).returncode == 0


def _origin(repo: Path) -> str:
    result = _git(repo, "remote", "get-url", "origin", check=False)
    if result.returncode != 0:
        raise QaasGraphError(f"existing directory has no origin remote: {repo}")
    return _stdout(result)


def _head(repo: Path) -> str:
    return _stdout(_git(repo, "rev-parse", "HEAD"))


def _config(repo: Path, key: str) -> str | None:
    result = _git(repo, "config", "--local", "--get", key, check=False)
    return _stdout(result) if result.returncode == 0 else None


def _mark_managed(repo: Path, commit: str) -> None:
    _git(repo, "config", "--local", MANAGED_KEY, "true")
    _git(repo, "config", "--local", SYNCED_COMMIT_KEY, commit)


def _is_managed(repo: Path) -> bool:
    return (_config(repo, MANAGED_KEY) or "").casefold() == "true"


def _ensure_clean_checkout(repo: Path) -> None:
    status = _stdout(_git(repo, "status", "--porcelain", "--untracked-files=no"))
    if status:
        raise QaasGraphError(
            f"qaas-graph checkout has tracked modifications; refusing to use {repo}"
        )


def _ensure_clean_managed_state(repo: Path) -> None:
    expected = _config(repo, SYNCED_COMMIT_KEY)
    current = _head(repo)
    if not expected or current != expected:
        raise QaasGraphError(
            f"managed cache HEAD changed locally; refusing to overwrite {repo}"
        )
    _ensure_clean_checkout(repo)


def _validate_commit_graph(repo: Path, commit: str) -> None:
    with tempfile.NamedTemporaryFile(prefix="qaas-graph-", suffix=".json") as temp:
        result = _command(
            ["git", "-C", str(repo), "show", f"{commit}:{GRAPH_RELATIVE_PATH.as_posix()}"],
            timeout=120,
            capture=False,
            stdout=temp,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
            raise QaasGraphError(
                f"remote commit does not contain a usable graph: {stderr.strip()}"
            )
        temp.flush()
        validate_graph(Path(temp.name))


def _clone(repo: Path) -> None:
    if repo.exists():
        raise QaasGraphError(f"refusing to overwrite existing path: {repo}")
    repo.parent.mkdir(parents=True, exist_ok=True)
    result = _command(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--single-branch",
            "--branch",
            BRANCH,
            REMOTE_URL,
            str(repo),
        ],
        timeout=300,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "clone failed").strip()
        raise QaasGraphError(detail)
    commit = _head(repo)
    validate_graph(repo / GRAPH_RELATIVE_PATH)
    _mark_managed(repo, commit)
    print(f"qaas-graph: cloned {commit[:12]} into {repo}", file=sys.stderr)


def _sync_managed(repo: Path, remote_commit: str) -> None:
    _ensure_clean_managed_state(repo)
    result = _git(
        repo,
        "fetch",
        "--depth",
        "1",
        "origin",
        f"refs/heads/{BRANCH}",
        timeout=300,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "fetch failed").strip()
        raise QaasGraphError(detail)
    fetched = _stdout(_git(repo, "rev-parse", "FETCH_HEAD"))
    if fetched != remote_commit:
        raise QaasGraphError(
            "remote changed during synchronization; rerun the query to retry safely"
        )
    _validate_commit_graph(repo, fetched)
    _git(repo, "reset", "--hard", fetched)
    validate_graph(repo / GRAPH_RELATIVE_PATH)
    _mark_managed(repo, fetched)
    print(f"qaas-graph: synchronized {fetched[:12]}", file=sys.stderr)


def ensure_graph(workspace: Path) -> Path:
    repo = resolve_graph_repo(workspace)
    remote_commit, remote_error = _remote_head()

    if not repo.exists():
        if remote_commit is None:
            raise QaasGraphError(
                f"cannot clone the canonical graph because GitHub is unavailable: {remote_error}"
            )
        _clone(repo)
        return repo / GRAPH_RELATIVE_PATH

    if not repo.is_dir() or not _is_git_repo(repo):
        raise QaasGraphError(f"existing qaas-graph path is not a Git checkout: {repo}")
    actual_origin = _origin(repo)
    if not _same_remote(actual_origin):
        raise QaasGraphError(
            f"existing qaas-graph checkout has an unexpected origin; refusing to use {repo}"
        )

    graph_path = repo / GRAPH_RELATIVE_PATH
    if remote_commit is None:
        if not _is_managed(repo):
            raise QaasGraphError(
                "GitHub freshness could not be checked and the existing checkout is not a managed cache"
            )
        _ensure_clean_managed_state(repo)
        validate_graph(graph_path)
        print(
            f"WARNING: GitHub freshness could not be verified; using valid cached graph at {_head(repo)[:12]} ({remote_error})",
            file=sys.stderr,
        )
        return graph_path

    current = _head(repo)
    if current == remote_commit:
        _ensure_clean_checkout(repo)
        validate_graph(graph_path)
        print(f"qaas-graph: current at {current[:12]}", file=sys.stderr)
        return graph_path

    if not _is_managed(repo):
        raise QaasGraphError(
            f"existing qaas-graph checkout is not the current remote main and is not managed; refusing to overwrite {repo}"
        )
    _sync_managed(repo, remote_commit)
    return graph_path


def _graphify_requirement(repo: Path) -> str:
    requirements = repo / "requirements.txt"
    if requirements.is_file():
        try:
            for line in requirements.read_text(encoding="utf-8").splitlines():
                if line.strip().casefold().startswith("graphifyy"):
                    return f"{line.strip()} from {requirements}"
        except OSError:
            pass
    return f"the Graphify requirement declared by {repo}"


def query_graph(graph_path: Path, question: str, *, dfs: bool, budget: int) -> int:
    graphify = shutil.which("graphify")
    if not graphify:
        requirement = _graphify_requirement(graph_path.parent.parent)
        raise QaasGraphError(
            f"Graphify CLI is not installed. Install {requirement}, then rerun; no installation was attempted."
        )

    with tempfile.TemporaryDirectory(prefix="qaas-graph-query-") as temp_dir:
        temp_root = Path(temp_dir)
        temp_output = temp_root / "graphify-out"
        temp_output.mkdir()
        temp_graph = temp_output / "graph.json"
        shutil.copyfile(graph_path, temp_graph)

        command = [
            graphify,
            "query",
            question,
            "--budget",
            str(budget),
            "--graph",
            str(temp_graph),
        ]
        if dfs:
            command.append("--dfs")
        env = os.environ.copy()
        env["GRAPHIFY_QUERY_LOG_DISABLE"] = "1"
        result = subprocess.run(command, cwd=temp_root, env=env, check=False)
        return result.returncode


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query the canonical QaaS graph without mutating it."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    query = subparsers.add_parser("query", help="synchronize and query the graph")
    query.add_argument("--workspace", type=Path, default=Path.cwd())
    query.add_argument("--question", required=True)
    query.add_argument("--dfs", action="store_true")
    query.add_argument("--budget", type=_positive_int, default=2000)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "query":
            graph_path = ensure_graph(args.workspace)
            return query_graph(
                graph_path, args.question, dfs=args.dfs, budget=args.budget
            )
    except (QaasGraphError, subprocess.TimeoutExpired) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
