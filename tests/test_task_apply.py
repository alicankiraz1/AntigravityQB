from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tests.test_validate_planner_docs import write_main_plan


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_APPLY = REPO_ROOT / "skills/antigravityqb/scripts/task_apply.py"


def run_apply(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TASK_APPLY), *args],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


class TaskApplyTests(unittest.TestCase):
    def test_prepare_validate_and_finalize_run_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs = root / "Planner-docs"
            docs.mkdir()
            write_main_plan(docs)

            prepared = run_apply(
                [
                    "prepare",
                    "--root",
                    str(root),
                    "--stage",
                    "step2",
                    "--run-id-suffix",
                    "apply-ready",
                    "--actor",
                    "controller",
                    "--evidence",
                    "main plan validated",
                ]
            )
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            run_dir = root / "Planner-docs/Task-Runs/tr-step2-apply-ready"
            self.assertTrue((run_dir / "Progress.json").is_file())
            self.assertTrue((run_dir / "Events.jsonl").is_file())
            self.assertTrue((run_dir / "Writer-Lock.json").is_file())

            validated = run_apply(["validate", "--run-dir", str(run_dir)])
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            self.assertIn("task_apply_validation=passed", validated.stdout)

            finalized = run_apply(
                [
                    "finalize",
                    "--run-dir",
                    str(run_dir),
                    "--actor",
                    "controller",
                    "--evidence",
                    "review complete",
                ]
            )
            self.assertEqual(finalized.returncode, 0, finalized.stdout + finalized.stderr)
            progress = json.loads((run_dir / "Progress.json").read_text(encoding="utf-8"))
            result = json.loads((run_dir / "Result.json").read_text(encoding="utf-8"))
            events = (run_dir / "Events.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(progress["state"], "FINALIZED")
            self.assertEqual(result["status"], "finalized")
            self.assertGreaterEqual(len(events), 2)

    def test_recover_lock_requires_expired_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs = root / "Planner-docs"
            docs.mkdir()
            write_main_plan(docs)
            prepared = run_apply(
                [
                    "prepare",
                    "--root",
                    str(root),
                    "--stage",
                    "step2",
                    "--run-id-suffix",
                    "recover-lock",
                    "--evidence",
                    "main plan validated",
                ]
            )
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            run_dir = root / "Planner-docs/Task-Runs/tr-step2-recover-lock"
            lock_path = run_dir / "Writer-Lock.json"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            lock["lock_state"] = "held"
            lock["owner"] = "worker-1"
            lock["expires_at"] = (datetime.now(timezone.utc) - timedelta(minutes=5)).replace(microsecond=0).isoformat()
            lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            recovered = run_apply(
                [
                    "recover-lock",
                    "--run-dir",
                    str(run_dir),
                    "--actor",
                    "controller",
                    "--evidence",
                    "writer lock expired",
                ]
            )
            self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
            recovered_lock = json.loads(lock_path.read_text(encoding="utf-8"))
            self.assertEqual(recovered_lock["lock_state"], "recovered")
            self.assertEqual(recovered_lock["owner"], "")


if __name__ == "__main__":
    unittest.main()
