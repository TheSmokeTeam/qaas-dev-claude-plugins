from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import qaas_graph


class QaasGraphTests(unittest.TestCase):
    def test_sparse_checkout_includes_graph_and_locked_project(self) -> None:
        self.assertEqual(
            qaas_graph.SPARSE_CHECKOUT_PATHS,
            (
                "/graphify-out/graph.json",
                "/pyproject.toml",
                "/uv.lock",
            ),
        )

    def test_query_uses_uv_locked_project_and_preserves_query_flags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            graph = project / "graphify-out" / "graph.json"
            graph.parent.mkdir()
            graph.write_text("{}", encoding="utf-8")

            completed = subprocess.CompletedProcess([], 0, stdout="", stderr="")
            with (
                mock.patch.object(qaas_graph.shutil, "which", return_value="/usr/bin/uv"),
                mock.patch.object(qaas_graph.subprocess, "run", return_value=completed) as run,
            ):
                result = qaas_graph.query_graph(
                    graph, "Who owns transports?", dfs=True, budget=321
                )

            self.assertEqual(result, 0)
            command = run.call_args.args[0]
            self.assertEqual(
                command[:7],
                [
                    "/usr/bin/uv",
                    "run",
                    "--project",
                    str(project),
                    "--locked",
                    "graphify",
                    "query",
                ],
            )
            self.assertIn("Who owns transports?", command)
            self.assertIn("--budget", command)
            self.assertIn("321", command)
            self.assertIn("--graph", command)
            self.assertIn("--dfs", command)
            self.assertEqual(
                run.call_args.kwargs["env"]["GRAPHIFY_QUERY_LOG_DISABLE"], "1"
            )

    def test_missing_uv_is_blocking_without_an_install_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            graph = Path(directory) / "graphify-out" / "graph.json"
            graph.parent.mkdir()
            graph.write_text("{}", encoding="utf-8")

            with mock.patch.object(qaas_graph.shutil, "which", return_value=None):
                with self.assertRaisesRegex(
                    qaas_graph.QaasGraphError, "uv 0.13.7 is required"
                ):
                    qaas_graph.query_graph(graph, "question", dfs=False, budget=10)

    def test_locked_query_failure_is_actionable_and_has_no_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            graph = project / "graphify-out" / "graph.json"
            graph.parent.mkdir()
            graph.write_text("{}", encoding="utf-8")
            completed = subprocess.CompletedProcess(
                [], 2, stdout="", stderr="lockfile needs to be updated"
            )

            with (
                mock.patch.object(qaas_graph.shutil, "which", return_value="/usr/bin/uv"),
                mock.patch.object(qaas_graph.subprocess, "run", return_value=completed),
            ):
                with self.assertRaisesRegex(
                    qaas_graph.QaasGraphError, "lockfile needs to be updated"
                ):
                    qaas_graph.query_graph(graph, "question", dfs=False, budget=10)

    def test_source_has_no_requirements_or_global_graphify_fallback(self) -> None:
        source = Path(qaas_graph.__file__).read_text(encoding="utf-8")

        self.assertNotIn("requirements.txt", source)
        self.assertNotIn("_graphify_requirement", source)
        self.assertNotIn('shutil.which("graphify")', source)
        self.assertNotIn("pip install", source)
        self.assertNotIn("graphifyy", source)
        self.assertNotRegex(source, r"graphify(?:y)?\s*[<=>~!]")


if __name__ == "__main__":
    unittest.main()
