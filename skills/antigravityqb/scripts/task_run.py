#!/usr/bin/env python3
"""Create AntigravityQB task preview artifacts without executing work."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TASK_RUN_SCHEMA_VERSION = 1
PLUGIN_VERSION = "0.3.0"
STAGES = {"step2", "step3", "step4"}
FORBIDDEN_WRITES = ["~/.gemini/**", "~/.agents/**", ".git/**", ".env", "**/*.key", "**/*.pem"]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_json_digest(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def repo_relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def safe_output_dir(root: Path, output_dir: Path) -> Path:
    resolved_root = root.resolve()
    resolved_output = output_dir.resolve()
    try:
        resolved_output.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("output_dir_must_be_inside_repo") from exc
    if ".git" in resolved_output.parts:
        raise ValueError("output_dir_must_not_be_git")
    return resolved_output


def read_file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def source_entry(root: Path, path: Path, scope: str) -> dict[str, str]:
    return {"scope": scope, "path": repo_relative(root, path), "sha256": read_file_digest(path)}


def existing_repo_sources(root: Path, rel_paths: list[str]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    for rel in rel_paths:
        path = root / rel
        if path.is_file():
            sources.append(source_entry(root, path, "repo"))
    return sources


def skill_sources(root: Path, rel_paths: list[str]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    for rel in rel_paths:
        path = SKILL_ROOT / rel
        if path.is_file():
            sources.append({"scope": "skill", "path": rel, "sha256": read_file_digest(path)})
    return sources


def subplan_sources(root: Path) -> list[dict[str, str]]:
    planner = root / "Planner-docs"
    if not planner.is_dir():
        return []
    return [source_entry(root, path, "repo") for path in sorted(planner.glob("Faz-*-Plans/*.md")) if path.is_file()]


def collect_sources(root: Path, stage: str) -> list[dict[str, str]]:
    common_repo = [
        "Planner-docs/Main-Planing.md",
        "Planner-docs/Autopsy.md",
        "Planner-docs/Project-Ontology.md",
        "Planner-docs/Project-Comprehension.md",
        "Planner-docs/Planing-Ledger.md",
    ]
    if stage == "step2":
        return skill_sources(root, ["references/Second-Planner.md", "references/handoffs/run-step2.md"]) + existing_repo_sources(root, common_repo)
    if stage == "step3":
        return (
            skill_sources(root, ["references/Third-Planner.md", "references/handoffs/run-step3.md"])
            + existing_repo_sources(root, [*common_repo, "Planner-docs/Sub-Planing-Index.md"])
            + subplan_sources(root)
        )
    return (
        skill_sources(root, ["references/Fourth-Planner.md", "references/handoffs/run-step4.md"])
        + existing_repo_sources(root, [*common_repo, "Planner-docs/Sub-Planing-Index.md", "Planner-docs/Sub-Planing-Audit.md"])
        + subplan_sources(root)
    )


def mutable_outputs(stage: str) -> list[str]:
    if stage == "step2":
        return [
            "Planner-docs/Sub-Planing-Index.md",
            "Planner-docs/Faz-*-Plans/*.md",
            "Planner-docs/Planing-Ledger.md",
        ]
    if stage == "step3":
        return ["Planner-docs/Sub-Planing-Audit.md"]
    return ["Planner-docs/Planing-Ledger.md"]


def validation_mode_for(stage: str) -> str:
    return {"step2": "step1", "step3": "step3-preflight", "step4": "step4"}[stage]


def stage_prereq_errors(root: Path, stage: str) -> list[str]:
    errors: list[str] = []
    if not (root / "Planner-docs/Main-Planing.md").is_file():
        errors.append("missing_file=Planner-docs/Main-Planing.md")
    if stage in {"step3", "step4"}:
        if not (root / "Planner-docs/Sub-Planing-Index.md").is_file():
            errors.append("missing_file=Planner-docs/Sub-Planing-Index.md")
        if not list((root / "Planner-docs").glob("Faz-*-Plans/*.md")):
            errors.append("missing_subplans=Planner-docs/Faz-*-Plans/*.md")
    if stage == "step4" and not (root / "Planner-docs/Sub-Planing-Audit.md").is_file():
        errors.append("missing_file=Planner-docs/Sub-Planing-Audit.md")
    return errors


def validate_stage(root: Path, stage: str) -> list[str]:
    errors = stage_prereq_errors(root, stage)
    if errors:
        return errors
    try:
        import validate_planner_docs
    except ImportError:
        return []
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        validator_state_code = validate_planner_docs.run_validation(root, validation_mode_for(stage), strict=True)
    if validator_state_code != 0:
        errors.append(f"validator_failed={validation_mode_for(stage)}")
    return errors


def task_policy(stage: str, sources: list[dict[str, str]]) -> dict[str, object]:
    return {
        "required_inputs": [item["path"] for item in sources],
        "allowed_writes": mutable_outputs(stage),
        "forbidden_writes": list(FORBIDDEN_WRITES),
        "validation_mode": validation_mode_for(stage),
        "safety": {
            "executes_commands": False,
            "allows_global_config_edits": False,
            "allows_commit_push_pr_deploy": False,
            "output_dir_must_be_inside_repo": True,
        },
    }


def invocation_suffix(value: str | None = None) -> str:
    raw = value or f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip("-._")


def build_prompt(stage: str, status: str, errors: list[str]) -> str:
    if status == "BLOCKED":
        return "\n".join(
            [
                f"# AntigravityQB {stage} task preview blocked",
                "",
                "Do not start execution from this preview.",
                "Repair the listed prerequisites, then regenerate the task run.",
                "",
                "Blockers:",
                *[f"- {error}" for error in errors],
                "",
            ]
        )
    handoff = {
        "step2": "Use the antigravityqb skill. Read and return the exact canonical handoff from references/handoffs/run-step2.md, then execute it.",
        "step3": "Use the antigravityqb skill. Read and return the exact canonical handoff from references/handoffs/run-step3.md, then execute it.",
        "step4": "Use the antigravityqb skill. Read and return the exact canonical handoff from references/handoffs/run-step4.md, then execute it.",
    }[stage]
    return f"{handoff}\n"


def create_task_run(root: Path, stage: str, output_dir: Path | None, run_id_suffix: str | None) -> Path:
    root = root.resolve()
    suffix = invocation_suffix(run_id_suffix)
    run_id = f"tr-{stage}-{suffix}"
    selected_output = output_dir or root / "Planner-docs" / "Task-Runs" / run_id
    run_dir = safe_output_dir(root, selected_output)
    sources = collect_sources(root, stage)
    source_digest = canonical_json_digest(sources)
    policy = task_policy(stage, sources)
    policy_digest = canonical_json_digest(policy)
    errors = validate_stage(root, stage)
    status = "BLOCKED" if errors else "READY"
    run = {
        "task_run_schema_version": TASK_RUN_SCHEMA_VERSION,
        "plugin_version": PLUGIN_VERSION,
        "task_run_id": run_id,
        "stage": stage,
        "status": status,
        "source_snapshot": sources,
        "source_snapshot_digest": source_digest,
        "stage_snapshot": {
            "immutable_inputs": sources,
            "immutable_input_digest": source_digest,
            "mutable_outputs": mutable_outputs(stage),
        },
        "task_policy": policy,
        "task_policy_digest": policy_digest,
        "blocked_reasons": errors,
        "safety": policy["safety"],
        "generated_at": f"invocation:{suffix}",
    }
    result = {
        "task_run_id": run_id,
        "stage": stage,
        "status": "blocked" if errors else "ready",
        "blocked_reasons": errors,
        "prompt_file": "Task-Prompt.md",
    }
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "Task-Run.json").write_text(json.dumps(run, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (run_dir / "Task-Prompt.md").write_text(build_prompt(stage, status, errors), encoding="utf-8")
    (run_dir / "Task-Result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return run_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create AntigravityQB task preview artifacts.")
    parser.add_argument("--root", default=".", help="Target project root.")
    parser.add_argument("--stage", required=True, choices=sorted(STAGES), help="Planning stage to preview.")
    parser.add_argument("--output-dir", help="Optional output directory inside the project root.")
    parser.add_argument("--run-id-suffix", help="Stable suffix for deterministic tests.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else None
    try:
        run_dir = create_task_run(root, args.stage, output_dir, args.run_id_suffix)
    except ValueError as exc:
        print(f"task_run_error={exc}")
        return 2
    except FileExistsError:
        print("task_run_error=output_dir_exists")
        return 2
    print(f"task_run_dir={run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
