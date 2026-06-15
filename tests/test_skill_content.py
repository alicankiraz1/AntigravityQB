from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills/antigravityqb"


class SkillContentTests(unittest.TestCase):
    def test_skill_frontmatter_is_antigravity_native(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        self.assertIn("name: antigravityqb", skill)
        self.assertIn("Vibecoding-first Antigravity planning", skill)
        self.assertIn("Use the antigravityqb skill", skill)
        self.assertNotIn("$codexqb", skill)

    def test_public_skill_and_docs_are_antigravity_native(self) -> None:
        checked_roots = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "docs",
            SKILL_ROOT,
        ]
        forbidden = [
            "Codex",
            "codex",
            "$codexqb",
            ".codex-plugin",
            "openai.yaml",
            "codex plugin",
            ".agents/plugins/marketplace.json",
        ]
        for root in checked_roots:
            paths = [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
            for path in paths:
                if path.suffix == ".pyc" or "__pycache__" in path.parts:
                    continue
                text = path.read_text(encoding="utf-8")
                for needle in forbidden:
                    self.assertNotIn(needle, text, str(path))

    def test_public_skill_and_docs_do_not_contain_turkish_prose(self) -> None:
        turkish_chars = re.compile(r"[çğıöşüÇĞİÖŞÜ]")
        checked_roots = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "docs",
            SKILL_ROOT,
        ]
        for root in checked_roots:
            paths = [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
            for path in paths:
                if path.suffix == ".pyc" or "__pycache__" in path.parts:
                    continue
                self.assertIsNone(turkish_chars.search(path.read_text(encoding="utf-8")), str(path))

    def test_skill_references_repo_aware_intake(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/repo-aware-intake.md", skill)
        self.assertIn("repo-aware", skill.lower())

    def test_language_contract_is_documented(self) -> None:
        required_phrases = [
            "AntigravityQB asks intake questions in the user's language when practical.",
            "Generated Planner-docs artifacts are English by default unless the user explicitly requests another body language.",
            "Required document headings remain English for validator stability.",
        ]
        checked_files = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "docs/USAGE.md",
            SKILL_ROOT / "SKILL.md",
        ]
        for path in checked_files:
            text = path.read_text(encoding="utf-8")
            for phrase in required_phrases:
                self.assertIn(phrase, text, path.name)

        for path in [
            SKILL_ROOT / "references/First-Planner.md",
            SKILL_ROOT / "references/Autopsy-Planner.md",
            SKILL_ROOT / "references/Second-Planner.md",
            SKILL_ROOT / "references/Third-Planner.md",
        ]:
            text = path.read_text(encoding="utf-8")
            self.assertIn("English by default unless the user explicitly requests another body language", text, path.name)
            self.assertIn("Required document headings remain English", text, path.name)

    def test_repo_aware_intake_keeps_stable_four_fields(self) -> None:
        intake = (SKILL_ROOT / "references/repo-aware-intake.md").read_text(encoding="utf-8")
        for field in ["PROJECT_NAME", "PROJECT_INTENT", "TARGET_END_STATE", "KNOWN_CONSTRAINTS"]:
            self.assertIn(field, intake)
        for number in range(1, 5):
            self.assertIn(f"Question {number} / 4", intake)
        self.assertIn("Use plain text only", intake)
        self.assertIn("Pre-Intake Scan", intake)

    def test_first_planner_required_placeholders_remain_stable(self) -> None:
        first_planner = (SKILL_ROOT / "references/First-Planner.md").read_text(encoding="utf-8")
        headings = re.findall(r"^([A-Z_]+):$", first_planner, flags=re.MULTILINE)
        required = ["PROJECT_NAME", "PROJECT_INTENT", "TARGET_END_STATE", "KNOWN_CONSTRAINTS"]
        for field in required:
            self.assertIn(field, headings)
        positions = [headings.index(field) for field in required]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("INTAKE_EVIDENCE_SUMMARY:", first_planner)

    def test_autopsy_planner_is_wired_into_skill_and_step2(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        second = (SKILL_ROOT / "references/Second-Planner.md").read_text(encoding="utf-8")
        autopsy = (SKILL_ROOT / "references/Autopsy-Planner.md").read_text(encoding="utf-8")

        self.assertIn("references/Autopsy-Planner.md", skill)
        self.assertIn("Step 1.5", skill)
        self.assertIn("Planner-docs/Autopsy.md", second)
        self.assertIn("Autopsy.md is not a replacement for Main-Planing.md", second)

        required_headings = [
            "# Project Autopsy",
            "## 1. Executive Summary",
            "## 2. Reviewed Sources",
            "## 3. Project Areas and Ownership Boundaries",
            "## 4. Feature Inventory",
            "## 5. Placeholder, Stub, and Skeleton Analysis",
            "## 6. Technical Debt and Maintenance Risks",
            "## 7. Broken or Missing Integrations",
            "## 8. Test, CI, and Validation Gaps",
            "## 9. Security, Secret, and Governance Findings",
            "## 10. Operational Readiness and Observability",
            "## 11. Alignment Analysis with the Main Plan",
            "## 12. Autopsy Feedback for Step 2",
            "## 13. Priority Fix and Planning Signals",
        ]
        for heading in required_headings:
            self.assertIn(heading, autopsy)

    def test_validator_guidance_uses_repo_relative_antigravity_path(self) -> None:
        checked_files = [
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "references/workflow-quality.md",
            SKILL_ROOT / "references/Second-Planner.md",
            SKILL_ROOT / "references/Third-Planner.md",
        ]
        for path in checked_files:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("~/.codex/skills/codexqb/scripts/validate_planner_docs.py", text, path.name)
            self.assertNotIn("plugins/codexqb/skills/codexqb/scripts/validate_planner_docs.py", text, path.name)
            self.assertIn("bundled validator", text, path.name)
            self.assertIn("skills/antigravityqb/scripts/validate_planner_docs.py", text, path.name)
            self.assertIn("equivalent all-file validation", text, path.name)

    def test_fourth_planner_external_support_is_optional(self) -> None:
        fourth = (SKILL_ROOT / "references/Fourth-Planner.md").read_text(encoding="utf-8")
        self.assertIn("If installed/available in Antigravity", fourth)
        self.assertIn("If no supporting skill or helper agent is available", fourth)
        self.assertIn("continue using the audit", fourth)
        self.assertNotIn("Codex skills/plugins", fourth)

    def test_fourth_planner_runs_queue_continuously_with_stop_gates(self) -> None:
        fourth = (SKILL_ROOT / "references/Fourth-Planner.md").read_text(encoding="utf-8")
        self.assertIn("Build an ordered implementation queue", fourth)
        self.assertIn("Execute the queue continuously", fourth)
        self.assertIn("instead of stopping", fourth)
        self.assertIn("Stop only when one of these stop gates is hit", fourth)
        self.assertIn("token/context budget too low to continue safely", fourth)
        self.assertNotIn("Codex skills/plugins", fourth)

    def test_fourth_planner_has_mechanical_per_slice_loop(self) -> None:
        fourth = (SKILL_ROOT / "references/Fourth-Planner.md").read_text(encoding="utf-8")
        for phrase in [
            "For each implementation slice:",
            "Name the active phase/sub-plan",
            "Read AGENTS.md",
            "Run git status",
            "Inspect relevant files before editing",
            "focused failing test",
            "smallest change",
            "Run targeted validation",
            "Run the repo-level gate",
            "Summarize:",
            "scope would exceed the selected sub-plan",
        ]:
            self.assertIn(phrase, fourth)
        self.assertNotIn("Codex skills/plugins", fourth)

    def test_validate_script_covers_archive_and_secret_hygiene(self) -> None:
        validate_script = (REPO_ROOT / "scripts/validate.sh").read_text(encoding="utf-8")
        for phrase in [
            "release_secret_hygiene_failed",
            "package_secret_hygiene_failed",
            "package_secret_hygiene_mode=filesystem",
            "release_pii_hygiene_failed",
            "openrouter_api_key",
            "OPENROUTER_API_KEY",
            "git\", \"archive\"",
            "archive_hygiene_failed",
            "package_hygiene_failed",
            "package_hygiene_mode=filesystem",
            "ANTIGRAVITYQB_VALIDATE_SKIP_UNITTESTS",
            "__MACOSX",
            ".local",
        ]:
            self.assertIn(phrase, validate_script)

    def test_validate_script_runs_without_git_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package_root = Path(temp_dir) / "AntigravityQB"

            def ignore(_dir: str, names: list[str]) -> set[str]:
                ignored = {
                    ".git",
                    "__pycache__",
                    ".pytest_cache",
                    ".mypy_cache",
                    ".ruff_cache",
                    "AntigravityQB-sanitized.zip",
                }
                return ignored.intersection(names)

            shutil.copytree(REPO_ROOT, package_root, ignore=ignore)
            env = os.environ.copy()
            env["ANTIGRAVITYQB_VALIDATE_SKIP_UNITTESTS"] = "1"
            result = subprocess.run(
                ["bash", "scripts/validate.sh"],
                cwd=package_root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("package_secret_hygiene_mode=filesystem", result.stdout)
            self.assertIn("package_hygiene_mode=filesystem", result.stdout)
            self.assertIn("unit_tests_skipped=1", result.stdout)

    def test_archive_hygiene_pattern_matches_forbidden_paths(self) -> None:
        pattern = re.compile(
            r"(^|/)(\.git|__pycache__|\.env|artifacts|logs|tmp|__MACOSX)(/|$)"
            r"|\.pyc$|\.pem$|\.key$|\.local($|\.)"
        )
        forbidden = [
            ".git/config",
            "pkg/__pycache__/module.pyc",
            ".env",
            "artifacts/build.log",
            "logs/run.txt",
            "tmp/cache.txt",
            "__MACOSX/file",
            "keys/prod.pem",
            "keys/prod.key",
            "settings.local",
            "settings.local.json",
        ]
        allowed = [
            "README.md",
            "docs/MAINTAINING.md",
            "skills/antigravityqb/SKILL.md",
        ]
        for path in forbidden:
            self.assertRegex(path, pattern)
        for path in allowed:
            self.assertNotRegex(path, pattern)

    def test_autopsy_validator_mode_is_documented(self) -> None:
        validator = (SKILL_ROOT / "scripts/validate_planner_docs.py").read_text(encoding="utf-8")
        autopsy = (SKILL_ROOT / "references/Autopsy-Planner.md").read_text(encoding="utf-8")
        maintaining = (REPO_ROOT / "docs/MAINTAINING.md").read_text(encoding="utf-8")
        self.assertIn('"autopsy"', validator)
        self.assertIn("--mode autopsy --strict", autopsy)
        self.assertIn("--mode autopsy --strict", maintaining)

    def test_vibecoding_and_task_delegation_references_are_wired(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        usage = (REPO_ROOT / "docs/USAGE.md").read_text(encoding="utf-8")

        expected_refs = [
            "vibecoding-principles.md",
            "task-delegation-playbook.md",
            "planning-ledger.md",
            "project-ontology.md",
            "assessment-and-budget.md",
            "engineering-principles.md",
        ]
        for ref in expected_refs:
            self.assertTrue((SKILL_ROOT / "references" / ref).is_file(), ref)
            self.assertIn(ref, skill, ref)

        for text_blob in [skill, readme, usage]:
            self.assertIn("vibecoding-first", text_blob.lower())
            self.assertIn("helper agent", text_blob.lower())

    def test_planning_ledger_and_ontology_are_documented(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        usage = (REPO_ROOT / "docs/USAGE.md").read_text(encoding="utf-8")
        second = (SKILL_ROOT / "references/Second-Planner.md").read_text(encoding="utf-8")
        fourth = (SKILL_ROOT / "references/Fourth-Planner.md").read_text(encoding="utf-8")

        for artifact in ["Planner-docs/Planing-Ledger.md", "Planner-docs/Project-Ontology.md"]:
            self.assertIn(artifact, skill)
            self.assertIn(artifact, usage)

        self.assertIn("Planing-Ledger.md", second)
        self.assertIn("Project-Ontology.md", second)
        self.assertIn("Planing-Ledger.md", fourth)

    def test_prompt_secret_scans_do_not_print_secret_values(self) -> None:
        prompt_paths = list((SKILL_ROOT / "references").glob("*.md")) + [SKILL_ROOT / "SKILL.md"]
        for path in prompt_paths:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn('rg -n "sk-', text, path.name)
        workflow_quality = (SKILL_ROOT / "references/workflow-quality.md").read_text(encoding="utf-8")
        self.assertIn("file-name-only", workflow_quality)

    def test_fourth_planner_mentions_helper_roles_and_ledger(self) -> None:
        fourth = (SKILL_ROOT / "references/Fourth-Planner.md").read_text(encoding="utf-8")
        for phrase in [
            "explorer maps relevant files and risks",
            "tester/verifier identifies validation path",
            "implementer/worker makes the smallest change",
            "reviewer/security reviews the diff",
            "Only one writer should modify files per slice",
            "Planner-docs/Planing-Ledger.md",
        ]:
            self.assertIn(phrase, fourth)

    def test_validator_supports_optional_ontology_and_ledger_headings(self) -> None:
        validator = (SKILL_ROOT / "scripts/validate_planner_docs.py").read_text(encoding="utf-8")
        for phrase in [
            "ONTOLOGY_HEADINGS",
            "LEDGER_HEADINGS",
            "Project-Ontology.md",
            "Planing-Ledger.md",
            "validate_optional_continuity_docs",
        ]:
            self.assertIn(phrase, validator)

    def test_github_actions_validate_workflow_pins_python(self) -> None:
        workflow = (REPO_ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertIn("actions/checkout@v6", workflow)
        self.assertIn("actions/setup-python@v6", workflow)
        self.assertIn('python-version: "3.12"', workflow)
        self.assertIn("make check", workflow)


if __name__ == "__main__":
    unittest.main()
