#!/usr/bin/env python3
"""Integration tests for repo_snapshot.py."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from repo_snapshot import snapshot


class RepoSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self._git("init", "-q")
        self._git("config", "user.name", "QaaS Test")
        self._git("config", "user.email", "qaas@example.invalid")
        (self.repo / "tracked.txt").write_text("one\n", encoding="utf-8")
        self._git("add", "tracked.txt")
        self._git("commit", "-qm", "fixture")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_clean_snapshot_is_stable(self) -> None:
        first = snapshot(self.repo)
        second = snapshot(self.repo)
        self.assertEqual(first, second)
        self.assertIsNone(first["repository"])
        self.assertTrue(first["worktree_clean"])
        self.assertRegex(str(first["inspected_commit"]), r"^[0-9a-f]{40}$")
        self.assertRegex(str(first["worktree_fingerprint"]), r"^sha256:[0-9a-f]{64}$")

    def test_tracked_change_changes_fingerprint(self) -> None:
        clean = snapshot(self.repo)
        (self.repo / "tracked.txt").write_text("two\n", encoding="utf-8")
        dirty = snapshot(self.repo)
        self.assertEqual(clean["inspected_commit"], dirty["inspected_commit"])
        self.assertNotEqual(clean["worktree_fingerprint"], dirty["worktree_fingerprint"])
        self.assertFalse(dirty["worktree_clean"])

    def test_untracked_content_changes_fingerprint(self) -> None:
        (self.repo / "new.txt").write_text("first\n", encoding="utf-8")
        first = snapshot(self.repo)
        (self.repo / "new.txt").write_text("second\n", encoding="utf-8")
        second = snapshot(self.repo)
        self.assertNotEqual(first["worktree_fingerprint"], second["worktree_fingerprint"])

    def test_untracked_executable_bit_changes_fingerprint(self) -> None:
        path = self.repo / "script.sh"
        path.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
        path.chmod(0o644)
        before = snapshot(self.repo)
        path.chmod(0o755)
        after = snapshot(self.repo)
        self.assertNotEqual(before["worktree_fingerprint"], after["worktree_fingerprint"])

    def test_github_origin_identifies_repository(self) -> None:
        self._git(
            "remote",
            "add",
            "origin",
            "git@github.com:TheSmokeTeam/QaaS.Framework.git",
        )
        self.assertEqual(snapshot(self.repo)["repository"], "TheSmokeTeam/QaaS.Framework")

    def test_https_github_origin_identifies_repository(self) -> None:
        self._git(
            "remote",
            "add",
            "origin",
            "https://github.com/TheSmokeTeam/QaaS.Framework.git",
        )
        self.assertEqual(snapshot(self.repo)["repository"], "TheSmokeTeam/QaaS.Framework")

    def test_lookalike_host_is_not_trusted_as_github(self) -> None:
        self._git(
            "remote",
            "add",
            "origin",
            "https://evilgithub.com/TheSmokeTeam/QaaS.Framework.git",
        )
        self.assertIsNone(snapshot(self.repo)["repository"])


if __name__ == "__main__":
    unittest.main()
