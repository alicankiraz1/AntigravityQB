from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AntigravityPackagingTests(unittest.TestCase):
    def test_required_antigravity_skill_files_exist(self) -> None:
        required = [
            "skills/antigravityqb/SKILL.md",
            "skills/antigravityqb/scripts/validate_planner_docs.py",
            "skills/antigravityqb/references/First-Planner.md",
            "skills/antigravityqb/references/Autopsy-Planner.md",
            "skills/antigravityqb/references/Second-Planner.md",
            "skills/antigravityqb/references/Third-Planner.md",
            "skills/antigravityqb/references/Fourth-Planner.md",
            "docs/INSTALLATION.md",
            "docs/USAGE.md",
            "docs/MAINTAINING.md",
            "scripts/install.sh",
            "scripts/validate.sh",
            "README.md",
            "LICENSE",
        ]
        for path in required:
            self.assertTrue((REPO_ROOT / path).is_file(), path)

    def test_codex_plugin_manifests_are_absent(self) -> None:
        forbidden = [
            REPO_ROOT / "plugins/antigravityqb/.codex-plugin/plugin.json",
            REPO_ROOT / "plugins/codexqb/.codex-plugin/plugin.json",
            REPO_ROOT / ".agents/plugins/marketplace.json",
            REPO_ROOT / "skills/antigravityqb/agents/openai.yaml",
        ]
        for path in forbidden:
            self.assertFalse(path.exists(), str(path))

    def test_docs_name_all_antigravity_install_targets(self) -> None:
        docs = "\n".join(
            (REPO_ROOT / path).read_text(encoding="utf-8")
            for path in ["README.md", "docs/INSTALLATION.md", "docs/USAGE.md"]
        )
        for needle in [
            ".gemini/config/plugins/antigravityqb/skills/antigravityqb",
            ".agents/skills/antigravityqb",
            "~/.agents/skills/antigravityqb",
            ".agent/skills/antigravityqb",
            "~/.gemini/antigravity-cli/skills/antigravityqb",
            "Use the antigravityqb skill to inspect this repo and plan this project.",
        ]:
            self.assertIn(needle, docs)

    def test_install_dry_run_project_scopes_do_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            for scope in ["ide-project", "cli-project"]:
                result = subprocess.run(
                    ["bash", "scripts/install.sh", "--scope", scope, "--target", str(target), "--dry-run"],
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("would_install=true", result.stdout)
            self.assertFalse((target / ".agents").exists())
            self.assertFalse((target / ".agent").exists())

    def test_install_dry_run_app_global_reports_plugin_root(self) -> None:
        result = subprocess.run(
            ["bash", "scripts/install.sh", "--scope", "app-global", "--dry-run"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(".gemini/config/plugins/antigravityqb", result.stdout)
        self.assertIn("skills/antigravityqb", result.stdout)

    def test_project_scope_requires_target(self) -> None:
        result = subprocess.run(
            ["bash", "scripts/install.sh", "--scope", "ide-project", "--dry-run"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("target_required_for_scope=ide-project", result.stdout)


if __name__ == "__main__":
    unittest.main()
