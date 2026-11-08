#!/usr/bin/env python3
"""Unit tests for check-qaas-edit.py helpers."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("check-qaas-edit.py")
SPEC = importlib.util.spec_from_file_location("check_qaas_edit", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CheckQaaSEditTests(unittest.TestCase):
    def initialize_repository(self, directory: str, remote: str) -> Path:
        root = Path(directory)
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", str(root), "remote", "add", "origin", remote],
            check=True,
        )
        return root

    def test_extracts_supported_file_path(self) -> None:
        path = MODULE.edited_path({"tool_input": {"file_path": "/tmp/example.cs"}})
        self.assertEqual(path, Path("/tmp/example.cs").resolve())

    def test_ignores_payload_without_path(self) -> None:
        self.assertIsNone(MODULE.edited_path({"tool_input": {"content": "x"}}))

    def test_detects_trailing_whitespace_in_untracked_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.cs"
            path.write_bytes(b"clean\ntrailing \n")
            errors = MODULE.untracked_whitespace_errors(path)
        self.assertEqual(len(errors), 1)
        self.assertIn(":2: trailing whitespace", errors[0])

    def test_skips_binary_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.bin"
            path.write_bytes(b"binary\0content \n")
            self.assertEqual(MODULE.untracked_whitespace_errors(path), [])

    def test_recognizes_the_smoke_team_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.initialize_repository(
                directory,
                "git@github.com:TheSmokeTeam/QaaS.Framework.git",
            )
            path = root / "example.cs"
            path.write_text("clean\n", encoding="utf-8")
            self.assertEqual(MODULE.repository_for(path), root.resolve())

    def test_ignores_other_github_organizations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.initialize_repository(
                directory,
                "https://github.com/example/QaaS.Framework.git",
            )
            path = root / "example.cs"
            path.write_text("clean\n", encoding="utf-8")
            self.assertIsNone(MODULE.repository_for(path))

    def test_ignores_lookalike_github_host(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.initialize_repository(
                directory,
                "https://evilgithub.com/TheSmokeTeam/QaaS.Framework.git",
            )
            path = root / "example.cs"
            path.write_text("clean\n", encoding="utf-8")
            self.assertIsNone(MODULE.repository_for(path))

    def test_non_origin_remote_does_not_claim_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.initialize_repository(
                directory,
                "https://github.com/example/QaaS.Framework.git",
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "remote",
                    "add",
                    "upstream",
                    "https://github.com/TheSmokeTeam/QaaS.Framework.git",
                ],
                check=True,
            )
            path = root / "example.cs"
            path.write_text("clean\n", encoding="utf-8")
            self.assertIsNone(MODULE.repository_for(path))


if __name__ == "__main__":
    unittest.main()
