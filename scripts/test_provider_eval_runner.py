from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import provider_eval_runner as runner


class ProviderEvalRunnerTests(unittest.TestCase):
    def test_agent_command_loads_all_plugins_and_enforces_case_controls(self) -> None:
        case = runner.EvalCase(
            name="sample",
            directory=Path("/cases/sample"),
            prompt="Do the work",
            allowed_tools=("Read", "Skill"),
            max_turns=7,
            timeout_seconds=90,
            scaffold_script=None,
            threshold=None,
            graders=(),
        )

        command = runner.build_agent_command(
            case,
            model="agent-model",
            plugin_roots=(Path("/qaas"), Path("/grilling"), Path("/ponytail")),
        )

        self.assertEqual(command.count("--plugin-dir"), 3)
        for root in ("/qaas", "/grilling", "/ponytail"):
            self.assertIn(root, command)
        for option in (
            "--tools",
            "--allowedTools",
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
        ):
            self.assertIn(option, command)

    def test_judge_command_is_bare_and_schema_bound(self) -> None:
        command = runner.build_judge_command("judge-model", max_budget_usd=2.5)

        self.assertIn("--bare", command)
        self.assertEqual(command[command.index("--tools") + 1], "")
        self.assertIn("--json-schema", command)
        schema = json.loads(command[command.index("--json-schema") + 1])
        self.assertEqual(set(schema["required"]), {"pass", "reason"})
        self.assertEqual(command[command.index("--max-budget-usd") + 1], "2.5")

    @mock.patch("scripts.provider_eval_runner.subprocess.run")
    def test_judge_returns_reported_cost(self, run: mock.Mock) -> None:
        run.return_value = mock.Mock(
            returncode=0,
            stderr="",
            stdout=json.dumps(
                {
                    "structured_output": {"pass": True, "reason": "good"},
                    "total_cost_usd": 0.37,
                }
            ),
        )

        passed, reason, cost = runner._judge(
            "judge-model", "rubric", "target", max_budget_usd=1.5
        )

        self.assertTrue(passed)
        self.assertEqual(reason, "good")
        self.assertEqual(cost, 0.37)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("--max-budget-usd") + 1], "1.5")

    def test_arm_filtering_preserves_with_only_and_both(self) -> None:
        graders = (
            runner.Grader("with", "tool_used", {"arm": "with-only"}, ""),
            runner.Grader("both", "tool_used", {"arm": "both"}, ""),
            runner.Grader("default", "regex", {}, ""),
        )

        self.assertEqual(
            [grader.name for grader in runner.filter_graders(graders, ablation=False)],
            ["with", "both", "default"],
        )
        self.assertEqual(
            [grader.name for grader in runner.filter_graders(graders, ablation=True)],
            ["both", "default"],
        )

    def test_workspace_can_replace_only_the_broken_provider_copy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "providers/grilling").mkdir(parents=True)
            roots = runner.provider_roots_for_workspace(
                workspace,
                (Path("/qaas"), Path("/grilling"), Path("/ponytail")),
            )

        self.assertEqual(
            roots,
            (Path("/qaas"), workspace / "providers/grilling", Path("/ponytail")),
        )

    def test_every_repository_case_and_grader_parses(self) -> None:
        root = Path(__file__).parents[1] / "evals"
        cases = [runner.load_case(path.parent) for path in sorted(root.glob("*/case.yaml"))]

        self.assertEqual(len(cases), 11)
        self.assertEqual(
            {grader.type for case in cases for grader in case.graders},
            {"file_exists", "llm", "regex", "tool_order", "tool_used"},
        )

    def test_real_pending_case_ignores_scaffold_baseline_but_detects_new_paths(self) -> None:
        case_dir = Path(__file__).parents[1] / "evals/implementation-pending"
        case = runner.load_case(case_dir)
        grader = next(grader for grader in case.graders if grader.name == "no-files-created")
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            runner._run_scaffold(case, workspace, os.environ.copy())
            baseline = runner.snapshot_workspace_paths(workspace)

            untouched = runner.evaluate_grader(
                grader,
                trace=[],
                workspace=workspace,
                last_message="",
                baseline_paths=baseline,
            )
            (workspace / "unexpected.txt").write_text("mutation", encoding="utf-8")
            mutated = runner.evaluate_grader(
                grader,
                trace=[],
                workspace=workspace,
                last_message="",
                baseline_paths=baseline,
            )

        self.assertTrue(untouched.passed)
        self.assertFalse(mutated.passed)

    def test_all_deterministic_grader_types(self) -> None:
        trace = [
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "tool_use", "name": "Read", "input": {"file_path": "a.txt"}},
                        {"type": "tool_use", "name": "Bash", "input": {"command": "run tests"}},
                    ]
                },
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "result.txt").write_text("provider succeeded", encoding="utf-8")

            used = runner.evaluate_grader(
                runner.Grader("used", "tool_used", {"tool": "Bash", "input_match": "tests", "min": 1}, ""),
                trace=trace,
                workspace=workspace,
                last_message="done",
            )
            ordered = runner.evaluate_grader(
                runner.Grader(
                    "ordered",
                    "tool_order",
                    {"before": {"tool": "Read"}, "after": {"tool": "Bash"}},
                    "",
                ),
                trace=trace,
                workspace=workspace,
                last_message="done",
            )
            regex = runner.evaluate_grader(
                runner.Grader(
                    "regex",
                    "regex",
                    {"target": {"source": "file", "path": "result.txt"}, "pattern": "succeeded"},
                    "",
                ),
                trace=trace,
                workspace=workspace,
                last_message="done",
            )
            exists = runner.evaluate_grader(
                runner.Grader("exists", "file_exists", {"path": "result.txt", "exists": True}, ""),
                trace=trace,
                workspace=workspace,
                last_message="done",
            )
            llm = runner.evaluate_grader(
                runner.Grader("judge", "llm", {"focus": "last_message"}, "rubric"),
                trace=trace,
                workspace=workspace,
                last_message="done",
                llm_judge=lambda rubric, target: (True, "meets rubric"),
            )

        self.assertTrue(all(result.passed for result in (used, ordered, regex, exists, llm)))

    def test_turn_limit_threshold_and_budget(self) -> None:
        trace = [
            {"type": "assistant", "message": {"stop_reason": "end_turn", "content": []}},
            {"type": "assistant", "message": {"stop_reason": "end_turn", "content": []}},
        ]
        self.assertEqual(runner.completed_assistant_turns(trace), 2)
        with self.assertRaises(runner.TurnLimitExceeded):
            runner.enforce_turn_limit(trace, 1)
        self.assertTrue(runner.meets_threshold([True, True, False], 2 / 3))
        self.assertFalse(runner.meets_threshold([True, False], 0.75))
        with self.assertRaises(runner.BudgetExceeded):
            runner.enforce_budget(spent=9.5, next_cost=1.0, ceiling=10.0)

    def test_ablation_is_recorded_but_does_not_gate_conformance(self) -> None:
        self.assertTrue(
            runner.conformance_passed(
                [
                    {"arm": "with", "passed": True},
                    {"arm": "ablation", "passed": False},
                ]
            )
        )
        self.assertFalse(
            runner.conformance_passed(
                [
                    {"arm": "with", "passed": False},
                    {"arm": "ablation", "passed": True},
                ]
            )
        )


if __name__ == "__main__":
    unittest.main()
