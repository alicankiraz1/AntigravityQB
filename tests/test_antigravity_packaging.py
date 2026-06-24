from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AntigravityPackagingTests(unittest.TestCase):
    def test_required_antigravity_skill_files_exist(self) -> None:
        required = [
            "skills/antigravityqb/SKILL.md",
            "skills/antigravityqb/scripts/validate_planner_docs.py",
            "skills/antigravityqb/scripts/task_run.py",
            "skills/antigravityqb/scripts/task_apply.py",
            "skills/antigravityqb/references/First-Planner.md",
            "skills/antigravityqb/references/Autopsy-Planner.md",
            "skills/antigravityqb/references/Second-Planner.md",
            "skills/antigravityqb/references/Third-Planner.md",
            "skills/antigravityqb/references/Fourth-Planner.md",
            "docs/INSTALLATION.md",
            "docs/USAGE.md",
            "docs/MAINTAINING.md",
            "scripts/check_public_privacy.py",
            "scripts/export_sanitized.py",
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

    def test_app_global_install_writes_030_plugin_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env = os.environ.copy()
            env["HOME"] = temp_dir
            result = subprocess.run(
                ["bash", "scripts/install.sh", "--scope", "app-global", "--force"],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            plugin_root = Path(temp_dir) / ".gemini/config/plugins/antigravityqb"
            plugin_json = json.loads((plugin_root / "plugin.json").read_text(encoding="utf-8"))
            installed = json.loads((plugin_root / "installed_version.json").read_text(encoding="utf-8"))
            self.assertEqual(plugin_json["version"], "0.3.0")
            self.assertEqual(installed["version"], "0.3.0")

    def test_public_privacy_scan_reports_pattern_without_value(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package_root = Path(temp_dir)
            (package_root / "README.md").write_text("Local path: /Users/alice/private-project\n", encoding="utf-8")

            result = subprocess.run(
                ["python3", str(REPO_ROOT / "scripts/check_public_privacy.py"), "--root", str(package_root)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("release_pii_hygiene_failed", result.stdout)
            self.assertIn("absolute_user_path", result.stdout)
            self.assertNotIn("/Users/alice/private-project", result.stdout)

    def test_export_sanitized_writes_manifest_and_excludes_ignored_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package_root = Path(temp_dir)
            (package_root / "scripts").mkdir()
            shutil.copy2(REPO_ROOT / "scripts/check_public_privacy.py", package_root / "scripts/check_public_privacy.py")
            shutil.copy2(REPO_ROOT / "scripts/export_sanitized.py", package_root / "scripts/export_sanitized.py")
            (package_root / "README.md").write_text("# AntigravityQB\n", encoding="utf-8")
            (package_root / "CHANGELOG.md").write_text("# Changelog\n\n## 0.3.0\n", encoding="utf-8")
            (package_root / ".gitignore").write_text("__pycache__/\nlocal-note.txt\n*.zip\n", encoding="utf-8")
            (package_root / "local-note.txt").write_text("do not ship\n", encoding="utf-8")

            subprocess.run(["git", "init"], cwd=package_root, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=package_root, check=True, capture_output=True)
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "fixture"],
                cwd=package_root,
                check=True,
                capture_output=True,
            )

            result = subprocess.run(
                ["python3", "scripts/export_sanitized.py"],
                cwd=package_root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            archive_path = package_root / "AntigravityQB-sanitized.zip"
            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()
                self.assertIn("AntigravityQB/PACKAGE-MANIFEST.json", names)
                self.assertIn("AntigravityQB/README.md", names)
                self.assertNotIn("AntigravityQB/local-note.txt", names)
                manifest = json.loads(archive.read("AntigravityQB/PACKAGE-MANIFEST.json"))

            self.assertEqual(manifest["package_version"], "0.3.0")
            self.assertTrue(manifest["archive"]["tracked_only"])
            self.assertTrue(manifest["archive"]["symlink_safe"])
            self.assertEqual(manifest["archive"]["secret_scan"], "passed")
            self.assertEqual(manifest["archive"]["privacy_scan"], "passed")


if __name__ == "__main__":
    unittest.main()
