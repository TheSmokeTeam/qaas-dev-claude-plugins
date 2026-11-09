#!/usr/bin/env python3
"""Contract tests for QaaS's external workflow-provider dependencies."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

QAAS_VERSION = "0.5.0"
PROVIDERS = {
    "mattpocock-skills": {
        "repo": "mattpocock/skills",
        "sha": "4ae2317ddb22b046e26455e4f9c9b3aaaf62212d",
        "version": "1.3.2",
    },
    "ponytail": {
        "repo": "DietrichGebert/ponytail",
        "sha": "96608e078b2d5ea607c5c3b8b5a54d1c1fba6846",
        "version": "5.3.3",
    },
}


class PluginDependencyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
        cls.marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        cls.entries = {
            entry["name"]: entry for entry in cls.marketplace["plugins"]
        }

    def test_qaas_versions_match_050(self) -> None:
        self.assertEqual(self.plugin["version"], QAAS_VERSION)
        self.assertEqual(self.marketplace["metadata"]["version"], QAAS_VERSION)
        self.assertEqual(self.entries["qaas-platform-dev"]["version"], QAAS_VERSION)

    def test_root_declares_only_bare_same_marketplace_dependencies(self) -> None:
        self.assertEqual(self.plugin.get("dependencies"), list(PROVIDERS))

    def test_marketplace_pins_exact_upstream_sources(self) -> None:
        self.assertEqual(set(self.entries), {"qaas-platform-dev", *PROVIDERS})
        for name, expected in PROVIDERS.items():
            entry = self.entries[name]
            self.assertEqual(entry["version"], expected["version"])
            self.assertEqual(entry["source"], {
                "source": "github",
                "repo": expected["repo"],
                "sha": expected["sha"],
            })

    def test_provider_code_is_not_vendored(self) -> None:
        unexpected = [
            path
            for path in ROOT.rglob("*")
            if path.is_file()
            and any(part in {"mattpocock-skills", "ponytail"} for part in path.parts)
        ]
        self.assertEqual(unexpected, [])


if __name__ == "__main__":
    unittest.main()
