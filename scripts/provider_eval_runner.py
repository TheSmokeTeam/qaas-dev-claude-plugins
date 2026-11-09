#!/usr/bin/env python3
"""Focused provider-aware runner for this repository's lifecycle eval cases."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import re
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


ROOT = Path(__file__).parents[1]
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "pass": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["pass", "reason"],
    "additionalProperties": False,
}


class EvalRunnerError(RuntimeError):
    pass


class TurnLimitExceeded(EvalRunnerError):
    pass


class BudgetExceeded(EvalRunnerError):
    pass


@dataclasses.dataclass(frozen=True)
class Grader:
    name: str
    type: str
    config: dict[str, Any]
    rubric: str


@dataclasses.dataclass(frozen=True)
class EvalCase:
    name: str
    directory: Path
    prompt: str
    allowed_tools: tuple[str, ...]
    max_turns: int
    timeout_seconds: int
    scaffold_script: str | None
    threshold: float | None
    graders: tuple[Grader, ...]


@dataclasses.dataclass(frozen=True)
class GraderResult:
    name: str
    type: str
    passed: bool
    reason: str
    weight: float


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return json.loads(value)
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if value.startswith("[") and value.endswith("]"):
        contents = value[1:-1].strip()
        return [] if not contents else [_parse_scalar(item) for item in contents.split(",")]
    if value.casefold() in {"true", "false"}:
        return value.casefold() == "true"
    if value.casefold() in {"null", "none", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?(?:\d+\.\d*|\d*\.\d+)", value):
        return float(value)
    return value


def parse_mapping(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for number, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            raise ValueError(f"line {number}: expected key: value")
        key, value = line.split(":", 1)
        while indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        key = key.strip()
        if value.strip():
            parent[key] = _parse_scalar(value)
        else:
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
    return root


def _markdown_parts(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError(f"{path}: invalid grader frontmatter")
    end = text.find("\n---\n", 4)
    return parse_mapping(text[4:end]), text[end + 5 :].strip()


def load_case(directory: Path) -> EvalCase:
    metadata = parse_mapping((directory / "case.yaml").read_text(encoding="utf-8"))
    execution = metadata.get("execution", {})
    context = metadata.get("context", {})
    graders: list[Grader] = []
    for path in sorted((directory / "graders").glob("*.md")):
        config, rubric = _markdown_parts(path)
        graders.append(
            Grader(path.stem, str(config.pop("type")), config, rubric)
        )
    return EvalCase(
        name=str(metadata["name"]),
        directory=directory,
        prompt=(directory / "prompt.md").read_text(encoding="utf-8").strip(),
        allowed_tools=tuple(str(item) for item in execution.get("allowed_tools", [])),
        max_turns=int(execution["max_turns"]),
        timeout_seconds=int(execution["timeout_seconds"]),
        scaffold_script=context.get("scaffold_script"),
        threshold=(
            float(execution["threshold"])
            if execution.get("threshold") is not None
            else None
        ),
        graders=tuple(graders),
    )


def build_agent_command(
    case: EvalCase,
    *,
    model: str,
    plugin_roots: Sequence[Path],
) -> list[str]:
    tools = ",".join(case.allowed_tools)
    command = [
        "claude",
        "-p",
        "--model",
        model,
        "--tools",
        tools,
        "--allowedTools",
        tools,
        "--permission-mode",
        "acceptEdits",
        "--permission-prompts",
        "none",
        "--no-session-persistence",
        "--forward-subagent-text",
        "--output-format",
        "stream-json",
        "--verbose",
        "--include-hook-events",
    ]
    for root in plugin_roots:
        command.extend(("--plugin-dir", str(root)))
    return command


def build_judge_command(
    model: str, *, max_budget_usd: float | None = None
) -> list[str]:
    command = [
        "claude",
        "-p",
        "--bare",
        "--model",
        model,
        "--tools",
        "",
        "--permission-prompts",
        "none",
        "--no-session-persistence",
        "--output-format",
        "json",
        "--json-schema",
        json.dumps(JUDGE_SCHEMA, separators=(",", ":")),
    ]
    if max_budget_usd is not None:
        command.extend(("--max-budget-usd", str(max_budget_usd)))
    return command


def filter_graders(graders: Sequence[Grader], *, ablation: bool) -> tuple[Grader, ...]:
    if not ablation:
        return tuple(graders)
    return tuple(grader for grader in graders if grader.config.get("arm") != "with-only")


def _walk(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def tool_events(trace: Sequence[dict[str, Any]]) -> list[tuple[str, str]]:
    events: list[tuple[str, str]] = []
    for event in trace:
        for item in _walk(event):
            if item.get("type") != "tool_use" or not item.get("name"):
                continue
            rendered = json.dumps(item.get("input", {}), sort_keys=True)
            events.append((str(item["name"]), rendered))
    return events


def completed_assistant_turns(trace: Sequence[dict[str, Any]]) -> int:
    return sum(
        1
        for event in trace
        if event.get("type") == "assistant"
        and isinstance(event.get("message"), dict)
        and event["message"].get("stop_reason") is not None
    )


def enforce_turn_limit(trace: Sequence[dict[str, Any]], maximum: int) -> None:
    completed = completed_assistant_turns(trace)
    if completed > maximum:
        raise TurnLimitExceeded(
            f"completed assistant turns {completed} exceeded maximum {maximum}"
        )


def enforce_budget(*, spent: float, next_cost: float, ceiling: float) -> None:
    if spent + next_cost > ceiling:
        raise BudgetExceeded(
            f"cost ceiling ${ceiling:.2f} would be exceeded by ${spent + next_cost:.4f}"
        )


def meets_threshold(results: Sequence[bool], threshold: float) -> bool:
    return bool(results) and sum(results) / len(results) >= threshold


def conformance_passed(aggregates: Sequence[dict[str, Any]]) -> bool:
    conformance = [case for case in aggregates if case.get("arm") == "with"]
    return bool(conformance) and all(bool(case.get("passed")) for case in conformance)


def snapshot_workspace_paths(workspace: Path) -> frozenset[str]:
    return frozenset(
        path.relative_to(workspace).as_posix() for path in workspace.rglob("*")
    )


def _matching_workspace_paths(workspace: Path, pattern: str) -> set[str]:
    return {
        path.relative_to(workspace).as_posix()
        for path in workspace.glob(pattern)
    }


def _regex_flags(value: Any) -> int:
    flags = 0
    for flag in str(value or ""):
        flags |= {"i": re.IGNORECASE, "m": re.MULTILINE, "s": re.DOTALL}.get(flag, 0)
    return flags


def _target_text(
    config: dict[str, Any],
    *,
    trace: Sequence[dict[str, Any]],
    workspace: Path,
    last_message: str,
) -> str:
    target = config.get("target", config.get("focus", "last_message"))
    if target == "last_message":
        return last_message
    if target == "trace":
        return json.dumps(trace, sort_keys=True)
    if isinstance(target, dict) and target.get("source") == "file":
        path = workspace / str(target["path"])
        return path.read_text(encoding="utf-8") if path.is_file() else ""
    raise ValueError(f"unsupported grader target: {target!r}")


def evaluate_grader(
    grader: Grader,
    *,
    trace: Sequence[dict[str, Any]],
    workspace: Path,
    last_message: str,
    llm_judge: Callable[[str, str], tuple[bool, str]] | None = None,
    baseline_paths: frozenset[str] | None = None,
) -> GraderResult:
    config = grader.config
    passed = False
    reason = ""
    if grader.type == "tool_used":
        tool = str(config["tool"])
        pattern = str(config.get("input_match", ".*"))
        count = sum(
            1
            for event_tool, event_input in tool_events(trace)
            if event_tool == tool and re.search(pattern, event_input)
        )
        minimum = int(config.get("min", 1))
        maximum = int(config.get("max", 2**31 - 1))
        passed = minimum <= count <= maximum
        reason = f"observed {count}; expected {minimum}..{maximum}"
    elif grader.type == "tool_order":
        events = tool_events(trace)

        def index(spec: dict[str, Any]) -> int | None:
            pattern = str(spec.get("input_match", ".*"))
            return next(
                (
                    offset
                    for offset, (tool, rendered) in enumerate(events)
                    if tool == str(spec["tool"]) and re.search(pattern, rendered)
                ),
                None,
            )

        before = index(config["before"])
        after = index(config["after"])
        passed = before is not None and after is not None and before < after
        reason = f"before={before}, after={after}"
    elif grader.type == "regex":
        target = _target_text(
            config, trace=trace, workspace=workspace, last_message=last_message
        )
        passed = re.search(
            str(config["pattern"]), target, _regex_flags(config.get("flags"))
        ) is not None
        reason = "pattern matched" if passed else "pattern did not match"
    elif grader.type == "file_exists":
        matches = _matching_workspace_paths(workspace, str(config["path"]))
        expected = bool(config.get("exists", True))
        if not expected and baseline_paths is not None:
            matches -= baseline_paths
        passed = bool(matches) is expected
        reason = f"found {len(matches)} paths; expected exists={expected}"
    elif grader.type == "llm":
        if llm_judge is None:
            raise ValueError("llm grader requires a judge")
        target = _target_text(
            config, trace=trace, workspace=workspace, last_message=last_message
        )
        passed, reason = llm_judge(grader.rubric, target)
    else:
        raise ValueError(f"unsupported grader type: {grader.type}")
    return GraderResult(
        name=grader.name,
        type=grader.type,
        passed=passed,
        reason=reason,
        weight=float(config.get("weight", 1)),
    )


def _last_message(trace: Sequence[dict[str, Any]]) -> str:
    messages: list[str] = []
    for event in trace:
        if event.get("type") != "assistant":
            continue
        message = event.get("message", {})
        for item in message.get("content", []) if isinstance(message, dict) else []:
            if isinstance(item, dict) and item.get("type") == "text":
                messages.append(str(item.get("text", "")))
    return messages[-1] if messages else ""


def _trace_cost(trace: Sequence[dict[str, Any]]) -> float:
    costs = [
        float(item["total_cost_usd"])
        for event in trace
        for item in _walk(event)
        if isinstance(item.get("total_cost_usd"), (int, float))
    ]
    return max(costs, default=0.0)


def _judge(
    model: str,
    rubric: str,
    target: str,
    *,
    max_budget_usd: float,
) -> tuple[bool, str, float]:
    prompt = (
        "Evaluate the target against the rubric. Return only the requested JSON.\n\n"
        f"RUBRIC:\n{rubric}\n\nTARGET:\n{target}"
    )
    completed = subprocess.run(
        [*build_judge_command(model, max_budget_usd=max_budget_usd), prompt],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise EvalRunnerError(completed.stderr.strip() or "judge process failed")
    payload = json.loads(completed.stdout)
    structured: Any = payload.get("structured_output") if isinstance(payload, dict) else payload
    if structured is None and isinstance(payload, dict):
        structured = payload.get("result")
    if isinstance(structured, str):
        structured = json.loads(structured)
    return (
        bool(structured["pass"]),
        str(structured["reason"]),
        _trace_cost([payload]) if isinstance(payload, dict) else 0.0,
    )


def _run_scaffold(case: EvalCase, workspace: Path, environment: dict[str, str]) -> None:
    if not case.scaffold_script:
        return
    completed = subprocess.run(
        ["bash", str(case.directory / case.scaffold_script)],
        cwd=workspace,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise EvalRunnerError(completed.stderr.strip() or "scaffold failed")


def provider_roots_for_workspace(
    workspace: Path, defaults: Sequence[Path]
) -> tuple[Path, ...]:
    local = workspace / "providers"
    candidates = (
        defaults[0],
        local / "grilling" if (local / "grilling").is_dir() else defaults[1],
        local / "ponytail" if (local / "ponytail").is_dir() else defaults[2],
    )
    return tuple(Path(path) for path in candidates)


def _run_agent(
    command: Sequence[str],
    *,
    prompt: str,
    workspace: Path,
    environment: dict[str, str],
    timeout_seconds: int,
    max_turns: int,
) -> tuple[list[str], list[dict[str, Any]], str, int]:
    process = subprocess.Popen(
        [*command, prompt],
        cwd=workspace,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
    )
    assert process.stdout and process.stderr
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ, "stdout")
    selector.register(process.stderr, selectors.EVENT_READ, "stderr")
    raw: list[str] = []
    trace: list[dict[str, Any]] = []
    errors: list[str] = []
    deadline = time.monotonic() + timeout_seconds
    try:
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(command, timeout_seconds)
            ready = selector.select(min(remaining, 1.0))
            if not ready and process.poll() is not None:
                break
            for key, _ in ready:
                line = key.fileobj.readline()
                if not line:
                    selector.unregister(key.fileobj)
                    continue
                if key.data == "stderr":
                    errors.append(line)
                    continue
                raw.append(line)
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                trace.append(event)
                enforce_turn_limit(trace, max_turns)
        returncode = process.wait(timeout=max(deadline - time.monotonic(), 0.1))
    except BaseException:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        raise
    return raw, trace, "".join(errors), returncode


def _score(results: Sequence[GraderResult]) -> float:
    total = sum(result.weight for result in results)
    earned = sum(result.weight for result in results if result.passed)
    return earned / total if total else 0.0


def _write_summary(output: Path, aggregate: dict[str, Any]) -> None:
    lines = ["# Provider-aware eval summary", ""]
    lines.append(f"Total cost: ${aggregate['total_cost_usd']:.4f}")
    lines.append("")
    lines.append("| Case | Arm | Passed runs | Total runs | Pass |")
    lines.append("|---|---:|---:|---:|---:|")
    for case in aggregate["cases"]:
        lines.append(
            f"| {case['name']} | {case['arm']} | {case['passed_runs']} | "
            f"{case['runs']} | {str(case['passed']).lower()} |"
        )
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output_root / timestamp
    output.mkdir(parents=True)
    cases = [load_case(path.parent) for path in sorted(args.eval_root.glob("*/case.yaml"))]
    arms = [("with", False)] + ([("ablation", True)] if args.ablation else [])
    total_cost = 0.0
    aggregates: list[dict[str, Any]] = []

    for arm_name, ablation in arms:
        for case in cases:
            run_passes: list[bool] = []
            run_records: list[dict[str, Any]] = []
            threshold = case.threshold if case.threshold is not None else args.threshold
            for run_number in range(1, args.runs + 1):
                enforce_budget(spent=total_cost, next_cost=0.0, ceiling=args.max_cost_usd)
                with tempfile.TemporaryDirectory(prefix=f"qaas-eval-{case.name}-") as directory:
                    workspace = Path(directory)
                    environment = os.environ.copy()
                    for name in ("home", "xdg", "claude"):
                        (workspace / name).mkdir()
                    environment.update(
                        HOME=str(workspace / "home"),
                        XDG_CONFIG_HOME=str(workspace / "xdg"),
                        CLAUDE_CONFIG_DIR=str(workspace / "claude"),
                        QAAS_EVAL_GRILLING_ROOT=str(args.grilling_root),
                        QAAS_EVAL_PONYTAIL_ROOT=str(args.ponytail_root),
                    )
                    _run_scaffold(case, workspace, environment)
                    plugin_roots: tuple[Path, ...] = () if ablation else provider_roots_for_workspace(
                        workspace,
                        (
                            args.plugin_root,
                            args.grilling_root,
                            args.ponytail_root,
                        ),
                    )
                    baseline_paths = snapshot_workspace_paths(workspace)
                    command = build_agent_command(
                        case, model=args.model, plugin_roots=plugin_roots
                    )
                    remaining = args.max_cost_usd - total_cost
                    if remaining <= 0:
                        raise BudgetExceeded(
                            f"cost ceiling ${args.max_cost_usd:.2f} leaves no budget for agent"
                        )
                    command.extend(("--max-budget-usd", str(remaining)))
                    raw, trace, stderr, returncode = _run_agent(
                        command,
                        prompt=case.prompt,
                        workspace=workspace,
                        environment=environment,
                        timeout_seconds=case.timeout_seconds,
                        max_turns=case.max_turns,
                    )
                    stem = f"{case.name}-{arm_name}-{run_number}"
                    (output / f"{stem}.jsonl").write_text(
                        "".join(raw), encoding="utf-8"
                    )
                    cost = _trace_cost(trace)
                    enforce_budget(
                        spent=total_cost, next_cost=cost, ceiling=args.max_cost_usd
                    )
                    total_cost += cost
                    last_message = _last_message(trace)
                    judge_cost = 0.0

                    def run_judge(rubric: str, target: str) -> tuple[bool, str]:
                        nonlocal judge_cost
                        remaining_judge_budget = (
                            args.max_cost_usd - total_cost - judge_cost
                        )
                        if remaining_judge_budget <= 0:
                            raise BudgetExceeded(
                                f"cost ceiling ${args.max_cost_usd:.2f} leaves no budget for judge"
                            )
                        passed, reason, next_cost = _judge(
                            args.judge_model,
                            rubric,
                            target,
                            max_budget_usd=remaining_judge_budget,
                        )
                        enforce_budget(
                            spent=total_cost + judge_cost,
                            next_cost=next_cost,
                            ceiling=args.max_cost_usd,
                        )
                        judge_cost += next_cost
                        return passed, reason

                    results = [
                        evaluate_grader(
                            grader,
                            trace=trace,
                            workspace=workspace,
                            last_message=last_message,
                            llm_judge=run_judge,
                            baseline_paths=baseline_paths,
                        )
                        for grader in filter_graders(case.graders, ablation=ablation)
                    ]
                    total_cost += judge_cost
                    score = _score(results)
                    passed = returncode == 0 and score >= threshold
                    run_passes.append(passed)
                    record = {
                        "run": run_number,
                        "returncode": returncode,
                        "stderr": stderr,
                        "cost_usd": cost + judge_cost,
                        "agent_cost_usd": cost,
                        "judge_cost_usd": judge_cost,
                        "score": score,
                        "threshold": threshold,
                        "passed": passed,
                        "graders": [dataclasses.asdict(result) for result in results],
                    }
                    run_records.append(record)
                    (output / f"{stem}.graders.json").write_text(
                        json.dumps(record, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
            case_passed = meets_threshold(run_passes, threshold)
            aggregates.append(
                {
                    "name": case.name,
                    "arm": arm_name,
                    "runs": args.runs,
                    "passed_runs": sum(run_passes),
                    "threshold": threshold,
                    "passed": case_passed,
                    "results": run_records,
                }
            )

    aggregate = {"total_cost_usd": total_cost, "cases": aggregates}
    (output / "aggregate.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_summary(output, aggregate)
    print(output)
    return 0 if conformance_passed(aggregates) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-root", type=Path, required=True)
    parser.add_argument("--grilling-root", type=Path, required=True)
    parser.add_argument("--ponytail-root", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--judge-model", required=True)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--threshold", type=float, default=0.8)
    parser.add_argument("--max-cost-usd", type=float, default=30.0)
    parser.add_argument("--ablation", action="store_true")
    parser.add_argument("--eval-root", type=Path, default=ROOT / "evals")
    parser.add_argument(
        "--output-root", type=Path, default=ROOT / "evals/provider-results"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
