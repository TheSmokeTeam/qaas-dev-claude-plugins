from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
DEVELOP = ROOT / "skills/develop-qaas-change/SKILL.md"
PLAN = ROOT / "skills/plan-qaas-change/SKILL.md"
IMPLEMENT = ROOT / "skills/implement-qaas-change/SKILL.md"
README = ROOT / "README.md"
AGENT_NAMES = ("qaas-plan-reviewer", "qaas-verifier")

REMOVED_FILES = (
    "skills/plan-qaas-change/references/plan-template.md",
    "skills/plan-qaas-change/references/review-rubric.md",
    "skills/plan-qaas-change/scripts/validate_plan.py",
    "skills/plan-qaas-change/scripts/repo_snapshot.py",
    "skills/plan-qaas-change/scripts/test_validate_plan.py",
    "skills/plan-qaas-change/scripts/test_repo_snapshot.py",
    "skills/plan-qaas-change/scripts/tests/fixtures/approved-plan.md",
    "evals/implementation-approved/approved-plan.template.md",
    "agents/qaas-change-planner.md",
)

FORBIDDEN_WORKFLOW_TERMS = (
    "plan_revision",
    "plan_digest",
    "AWAITING_APPROVAL",
    "NEEDS_DECISION",
    "DRAFT",
    "STALE",
    "worktree_fingerprint",
    "validate_plan.py",
    "repo_snapshot.py",
    "plan-template.md",
    "review-rubric.md",
    "schema-4",
    "nine-section",
)


class SimplifiedWorkflowContractTests(unittest.TestCase):
    def text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def workflow_corpus(self) -> str:
        paths = {
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "scripts/build-agents-md.sh",
            ROOT / ".claude-plugin/plugin.json",
            ROOT / ".claude-plugin/marketplace.json",
            *ROOT.glob("skills/**/SKILL.md"),
            *ROOT.glob("skills/**/references/*.md"),
            *ROOT.glob("agents/*.md"),
            *ROOT.glob("commands/*.md"),
            *(
                path
                for pattern in ("*.md", "*.sh")
                for path in ROOT.glob(f"evals/**/{pattern}")
                if "results" not in path.parts
            ),
        }
        return "\n".join(self.text(path) for path in sorted(paths))

    def test_lifecycle_is_the_exact_numbered_flow(self) -> None:
        develop = self.text(DEVELOP)
        stages = (
            "Request",
            "Know QaaS",
            "Research/design",
            "Interview",
            "Create short plan",
            "Review",
            "Developer approves",
            "Implement and test",
            "Verify",
            "Release if authorized",
        )
        positions = []
        for number, stage in enumerate(stages, start=1):
            marker = f"{number}. **{stage}.**"
            with self.subTest(stage=stage):
                self.assertIn(marker, develop)
                positions.append(develop.index(marker))
        self.assertEqual(positions, sorted(positions))

    def test_readme_matches_flow_ownership_and_change_loop(self) -> None:
        readme = self.text(README)
        self.assertIn('G -- "changes" --> E', readme)
        self.assertNotIn('G -- "changes" --> C', readme)

        expected_rows = (
            "| Request | Developer |",
            "| Know QaaS | `qaas-platform-overview` |",
            "| Research/design | `plan-qaas-change` |",
            "| Interview | `plan-qaas-change` |",
            "| Create short plan | `plan-qaas-change` |",
            "| Review | `qaas-plan-reviewer` agent |",
            "| Developer approves | Developer |",
            "| Implement and test | `implement-qaas-change` |",
            "| Verify | `qaas-verifier` agent |",
            "| Release if authorized | `release-and-mirror` |",
        )
        for row in expected_rows:
            with self.subTest(row=row):
                self.assertIn(row, readme)

    def test_short_plan_is_the_consistent_public_term(self) -> None:
        corpus = self.workflow_corpus().lower()
        self.assertNotIn("concise plan", corpus)
        self.assertNotIn("concise-plan", corpus)
        self.assertNotIn("concise reviewed", corpus)

    def test_only_reviewer_and_verifier_agents_remain_routed(self) -> None:
        for name in AGENT_NAMES:
            with self.subTest(agent=name):
                path = ROOT / f"agents/{name}.md"
                self.assertTrue(path.is_file())

        planning = self.text(PLAN)
        implementation = self.text(IMPLEMENT)
        self.assertNotIn("qaas-change-planner", self.workflow_corpus())
        self.assertIn("qaas-plan-reviewer", planning)
        self.assertIn("qaas-verifier", implementation)

    def test_short_plan_keeps_the_real_safety_content(self) -> None:
        planning = self.text(PLAN)
        normalized = " ".join(planning.split())
        for requirement in (
            "goal and scope",
            "confirmed decisions",
            "source evidence and design",
            "affected repositories and files",
            "ordered test-first steps",
            "verification commands",
            "release impact",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, planning)

        self.assertIn("explicit developer approval", normalized)
        self.assertIn(
            "Reviewer readiness never authorizes implementation", normalized
        )
        self.assertIn(
            "Requested changes return to plan creation and review", normalized
        )
        self.assertIn(
            "Explicit developer approval is the successful planning outcome",
            normalized,
        )

    def test_implementation_rechecks_facts_and_preserves_delivery_gates(self) -> None:
        implementation = " ".join(self.text(IMPLEMENT).lower().split())
        for requirement in (
            "re-read",
            "cited paths",
            "test-first",
            "qaas-verifier",
            "explicitly authorized",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, implementation)

    def test_formal_plan_machinery_is_deleted(self) -> None:
        for relative in REMOVED_FILES:
            with self.subTest(path=relative):
                self.assertFalse((ROOT / relative).exists())

        corpus = self.workflow_corpus()
        for term in FORBIDDEN_WORKFLOW_TERMS:
            with self.subTest(term=term):
                self.assertNotIn(term, corpus)


if __name__ == "__main__":
    unittest.main()
