from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_validate_planner_docs import write_main_plan, write_valid_step2_fixture


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_RUN = REPO_ROOT / "skills/antigravityqb/scripts/task_run.py"


def run_task(root: Path, stage: str, suffix: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(TASK_RUN),
            "--root",
            str(root),
            "--stage",
            stage,
            "--run-id-suffix",
            suffix,
        ],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


class TaskRunTests(unittest.TestCase):
    def test_step2_preview_blocks_without_main_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = run_task(root, "step2", "missing-main")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run_dir = root / "Planner-docs/Task-Runs/tr-step2-missing-main"
            run = json.loads((run_dir / "Task-Run.json").read_text(encoding="utf-8"))
            prompt = (run_dir / "Task-Prompt.md").read_text(encoding="utf-8")
            task_result = json.loads((run_dir / "Task-Result.json").read_text(encoding="utf-8"))

            self.assertEqual(run["status"], "BLOCKED")
            self.assertEqual(task_result["status"], "blocked")
            self.assertIn("missing_file=Planner-docs/Main-Planing.md", run["blocked_reasons"])
            self.assertIn("Do not start execution", prompt)

    def test_step2_preview_writes_ready_artifacts_without_executing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs = root / "Planner-docs"
            docs.mkdir()
            write_main_plan(docs)
            result = run_task(root, "step2", "ready-step2")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run_dir = root / "Planner-docs/Task-Runs/tr-step2-ready-step2"
            run = json.loads((run_dir / "Task-Run.json").read_text(encoding="utf-8"))
            prompt = (run_dir / "Task-Prompt.md").read_text(encoding="utf-8")

            self.assertEqual(run["status"], "READY")
            self.assertEqual(run["task_run_schema_version"], 1)
            self.assertIn("task_policy_digest", run)
            self.assertFalse(run["safety"]["executes_commands"])
            self.assertIn("Planner-docs/Sub-Planing-Index.md", run["stage_snapshot"]["mutable_outputs"])
            self.assertIn("references/handoffs/run-step2.md", prompt)

    def test_step3_preview_includes_subplans_in_source_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_valid_step2_fixture(root)
            result = run_task(root, "step3", "ready-step3")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run_dir = root / "Planner-docs/Task-Runs/tr-step3-ready-step3"
            run = json.loads((run_dir / "Task-Run.json").read_text(encoding="utf-8"))
            source_paths = {item["path"] for item in run["source_snapshot"]}

            self.assertEqual(run["status"], "READY")
            self.assertIn("Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md", source_paths)
            self.assertIn("Planner-docs/Faz-2-Plans/Faz2.1-live-gateway.md", source_paths)
            self.assertEqual(run["stage_snapshot"]["mutable_outputs"], ["Planner-docs/Sub-Planing-Audit.md"])


if __name__ == "__main__":
    unittest.main()
