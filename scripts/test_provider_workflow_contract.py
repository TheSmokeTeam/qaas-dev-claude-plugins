from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
INTERVIEW = ROOT / "skills/plan-qaas-change/references/developer-interview.md"
PLANNER_SKILL = ROOT / "skills/plan-qaas-change/SKILL.md"
IMPLEMENTER = ROOT / "skills/implement-qaas-change/SKILL.md"
AGENTS = {
    name: ROOT / f"agents/{name}.md"
    for name in ("qaas-change-planner", "qaas-plan-reviewer", "qaas-verifier")
}


class ProviderWorkflowContractTests(unittest.TestCase):
    def text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def test_interview_uses_exact_grilling_skill_without_local_algorithm(self) -> None:
        interview = self.text(INTERVIEW)

        self.assertIn("`mattpocock-skills:grilling`", interview)
        self.assertIn("Provider: mattpocock-skills:grilling — SUCCEEDED", interview)
        self.assertIn("BLOCKED_PROVIDER: mattpocock-skills:grilling — cause", interview)
        self.assertNotIn("Map unresolved decisions as a dependency tree", interview)
        self.assertNotIn("current decision frontier", interview)

    def test_planning_routes_interview_only_when_a_decision_interview_is_needed(self) -> None:
        planning = self.text(PLANNER_SKILL)

        self.assertIn("`mattpocock-skills:grilling`", planning)
        for exclusion in (
            "knowledge-only",
            "status",
            "release-only",
            "exact approved-plan execution",
        ):
            self.assertIn(exclusion, planning)

    def test_ponytail_full_is_required_by_every_scope_owner(self) -> None:
        owners = {
            "planner": self.text(AGENTS["qaas-change-planner"]),
            "implementer": self.text(IMPLEMENTER),
            "reviewer": self.text(AGENTS["qaas-plan-reviewer"]),
            "verifier": self.text(AGENTS["qaas-verifier"]),
        }
        for owner, text in owners.items():
            with self.subTest(owner=owner):
                self.assertIn("`ponytail:ponytail`", text)
                self.assertRegex(text, r"(?is)ponytail:ponytail.{0,240}\bfull\b")
                self.assertIn("Provider: ponytail:ponytail — SUCCEEDED", text)
                self.assertIn("BLOCKED_PROVIDER: ponytail:ponytail — cause", text)

    def test_provider_failure_stops_before_downstream_work(self) -> None:
        for path in (INTERVIEW, PLANNER_SKILL, IMPLEMENTER, *AGENTS.values()):
            with self.subTest(path=path):
                text = self.text(path)
                self.assertRegex(
                    text,
                    r"(?is)BLOCKED_PROVIDER.{0,300}(stop|do not continue|no downstream)",
                )

    def test_internal_minimality_fallback_is_deleted(self) -> None:
        corpus = "\n".join(
            self.text(path)
            for path in (INTERVIEW, PLANNER_SKILL, IMPLEMENTER, *AGENTS.values())
        )

        self.assertNotIn("built-in minimality sequence", corpus)
        self.assertNotIn("If the level cannot be read", corpus)
        for numbered_step in (
            "Is a code change required?",
            "Can existing QaaS code solve the problem?",
            "Can an existing platform capability solve it?",
            "Can an already installed dependency solve it?",
        ):
            self.assertNotIn(numbered_step, corpus)

    def test_agents_do_not_preload_ponytail_as_invocation_proof(self) -> None:
        for path in AGENTS.values():
            with self.subTest(path=path):
                frontmatter = self.text(path).split("\n---\n", 1)[0]
                self.assertNotRegex(frontmatter, r"(?m)^\s+- ponytail")

    def test_plan_schema_remains_version_four(self) -> None:
        template = self.text(
            ROOT / "skills/plan-qaas-change/references/plan-template.md"
        )
        validator = self.text(
            ROOT / "skills/plan-qaas-change/scripts/validate_plan.py"
        )
        fixture = self.text(
            ROOT
            / "skills/plan-qaas-change/scripts/tests/fixtures/approved-plan.md"
        )

        self.assertRegex(template, r'(?m)^schema_version: "4"$')
        self.assertRegex(fixture, r'(?m)^schema_version: "4"$')
        self.assertNotRegex(validator, r"schema_version[^\n]*[" + "']5")

    def test_manual_eval_ci_loads_pinned_providers_and_focused_runner(self) -> None:
        workflow = self.text(ROOT / ".github/workflows/plugin-evals.yml")

        self.assertIn("mattpocock/skills", workflow)
        self.assertIn("4ae2317ddb22b046e26455e4f9c9b3aaaf62212d", workflow)
        self.assertIn("DietrichGebert/ponytail", workflow)
        self.assertIn("96608e078b2d5ea607c5c3b8b5a54d1c1fba6846", workflow)
        self.assertIn("scripts/provider_eval_runner.py", workflow)
        self.assertIn("--max-cost-usd 30", workflow)
        self.assertIn("if: always()", workflow)
        self.assertNotIn("claude plugin eval", workflow)

    def test_readme_discloses_provider_trust_and_ponytail_side_effects(self) -> None:
        readme = self.text(ROOT / "README.md")

        for required in (
            "SessionStart",
            "SubagentStart",
            "UserPromptSubmit",
            "~/.config/ponytail/band/<project>.csv",
            "webhookUrl",
            "Bearer token",
            "ledger` user setting to false",
            "schema-4",
            "BLOCKED_PROVIDER",
        ):
            self.assertIn(required, readme)


if __name__ == "__main__":
    unittest.main()
