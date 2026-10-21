#!/usr/bin/env python3
"""Inspect or safely fast-forward qaas-graph and its registered repositories."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Repository:
    name: str
    path: Path
    expected_url: str | None = None


@dataclass
class State:
    repository: Repository
    branch: str = "-"
    head: str = "-"
    upstream: str = "-"
    dirty: bool = False
    ahead: int | None = None
    behind: int | None = None
    origin: str = "-"
    result: str = ""


def git(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(path), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def locate_graph_repo(value: str | None) -> Path:
    if value:
        candidate = Path(value).expanduser().resolve()
        if (candidate / "repositories.yml").is_file():
            return candidate
        raise SystemExit(f"error: not a qaas-graph repository: {candidate}")

    cwd = Path.cwd().resolve()
    seen: set[Path] = set()
    for base in (cwd, *cwd.parents):
        for candidate in (base, base / "qaas-graph"):
            candidate = candidate.resolve()
            if candidate in seen:
                continue
            seen.add(candidate)
            if (candidate / "repositories.yml").is_file():
                return candidate
    raise SystemExit("error: could not locate qaas-graph; pass --graph-repo PATH")


def parse_registry(graph_repo: Path) -> list[Repository]:
    registry = graph_repo / "repositories.yml"
    try:
        import yaml  # type: ignore

        payload = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
        rows = payload.get("repositories", [])
        repositories = [
            Repository(
                str(row["name"]),
                (graph_repo / str(row["path"])).resolve(),
                str(row.get("url") or "") or None,
            )
            for row in rows
        ]
        if not repositories:
            raise SystemExit(f"error: no repositories found in {registry}")
        return repositories
    except ModuleNotFoundError:
        pass

    repositories: list[Repository] = []
    current: dict[str, str] = {}
    in_repositories = False
    for raw_line in registry.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped == "repositories:":
            in_repositories = True
            continue
        if in_repositories and raw_line and not raw_line.startswith((" ", "\t")):
            break
        if not in_repositories:
            continue
        if stripped.startswith("- name:"):
            if current.get("name") and current.get("path"):
                repositories.append(
                    Repository(
                        current["name"],
                        (graph_repo / current["path"]).resolve(),
                        current.get("url"),
                    )
                )
            current = {"name": stripped.split(":", 1)[1].strip().strip("\"'")}
        elif ":" in stripped and current:
            key, value = stripped.split(":", 1)
            if key in {"path", "url"}:
                current[key] = value.strip().strip("\"'")
    if current.get("name") and current.get("path"):
        repositories.append(
            Repository(
                current["name"],
                (graph_repo / current["path"]).resolve(),
                current.get("url"),
            )
        )
    if not repositories:
        raise SystemExit(f"error: no repositories found in {registry}")
    return repositories


def canonical_remote(value: str) -> str:
    remote = value.strip().rstrip("/")
    ssh_match = re.fullmatch(r"git@([^:]+):(.+)", remote)
    if ssh_match:
        remote = f"{ssh_match.group(1)}/{ssh_match.group(2)}"
    else:
        remote = re.sub(r"^(?:https?|ssh)://(?:git@)?", "", remote)
    return remote.removesuffix(".git").casefold()


def inspect(repository: Repository) -> State:
    state = State(repository=repository)
    if not repository.path.is_dir():
        state.result = "BLOCKED missing directory"
        return state
    if git(repository.path, "rev-parse", "--is-inside-work-tree").stdout.strip() != "true":
        state.result = "BLOCKED not a Git repository"
        return state

    state.head = git(repository.path, "rev-parse", "--short", "HEAD").stdout.strip() or "-"
    state.branch = (
        git(repository.path, "symbolic-ref", "--short", "-q", "HEAD").stdout.strip()
        or "DETACHED"
    )
    state.dirty = bool(git(repository.path, "status", "--porcelain").stdout.strip())
    state.origin = git(repository.path, "remote", "get-url", "origin").stdout.strip() or "-"
    if repository.expected_url and canonical_remote(state.origin) != canonical_remote(
        repository.expected_url
    ):
        state.result = "BLOCKED origin mismatch"

    upstream = git(
        repository.path,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    if upstream.returncode == 0:
        state.upstream = upstream.stdout.strip()
        counts = git(
            repository.path,
            "rev-list",
            "--left-right",
            "--count",
            "HEAD...@{upstream}",
        )
        if counts.returncode == 0:
            left, right = counts.stdout.split()
            state.ahead, state.behind = int(left), int(right)
    if not state.result:
        state.result = "DIRTY" if state.dirty else "OK"
    return state


def fetch(repository: Repository) -> str | None:
    result = git(repository.path, "fetch", "--prune")
    if result.returncode == 0:
        return None
    message = result.stderr.strip() or result.stdout.strip() or "git fetch failed"
    return " ".join(message.splitlines())


def sync(repository: Repository) -> State:
    initial = inspect(repository)
    if initial.result.startswith("BLOCKED"):
        return initial
    fetch_error = fetch(repository)
    if fetch_error:
        initial.result = f"BLOCKED fetch failed: {fetch_error}"
        return initial

    state = inspect(repository)
    if state.result.startswith("BLOCKED"):
        return state
    if state.dirty:
        state.result = "BLOCKED dirty working tree"
    elif state.branch == "DETACHED":
        state.result = "BLOCKED detached HEAD"
    elif state.upstream == "-" or state.ahead is None or state.behind is None:
        state.result = "BLOCKED no upstream"
    elif state.ahead and state.behind:
        state.result = "BLOCKED diverged"
    elif state.behind == 0:
        state.result = "CURRENT" if state.ahead == 0 else "SKIPPED local branch ahead"
    elif state.ahead == 0:
        pulled = git(repository.path, "pull", "--ff-only")
        if pulled.returncode != 0:
            message = pulled.stderr.strip() or pulled.stdout.strip() or "git pull failed"
            state.result = f"BLOCKED pull failed: {' '.join(message.splitlines())}"
        else:
            state = inspect(repository)
            state.result = "PULLED"
    return state


def format_count(value: int | None) -> str:
    return "-" if value is None else str(value)


def print_states(states: list[State]) -> None:
    rows = [
        [
            state.repository.name,
            state.branch,
            state.head,
            "yes" if state.dirty else "no",
            format_count(state.ahead),
            format_count(state.behind),
            state.result,
        ]
        for state in states
    ]
    headers = ["repository", "branch", "head", "dirty", "ahead", "behind", "result"]
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    print("  ".join(value.ljust(widths[index]) for index, value in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect or safely fast-forward qaas-graph and its registered repositories."
    )
    parser.add_argument("command", choices=("status", "sync"))
    parser.add_argument("--graph-repo", help="Path to the qaas-graph repository")
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch before status inspection (status only; sync always fetches)",
    )
    args = parser.parse_args()
    if args.fetch and args.command != "status":
        parser.error("--fetch is valid only with status")

    graph_repo = locate_graph_repo(args.graph_repo)
    repositories = [Repository("qaas-graph", graph_repo), *parse_registry(graph_repo)]
    states: list[State] = []
    for repository in repositories:
        if args.command == "sync":
            states.append(sync(repository))
            continue
        state = inspect(repository)
        if args.fetch and not state.result.startswith("BLOCKED"):
            error = fetch(repository)
            if error:
                state.result = f"BLOCKED fetch failed: {error}"
            else:
                state = inspect(repository)
        states.append(state)

    print(f"qaas-graph: {graph_repo}")
    print_states(states)
    return 1 if any(state.result.startswith("BLOCKED") for state in states) else 0


if __name__ == "__main__":
    sys.exit(main())
