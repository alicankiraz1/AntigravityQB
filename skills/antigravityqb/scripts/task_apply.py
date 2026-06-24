#!/usr/bin/env python3
"""Manage local AntigravityQB task-run state artifacts without executing work."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import task_run


APPLY_STATE_SCHEMA_VERSION = 1
VALID_MODES = {"direct", "no_action"}
VALID_PROGRESS_STATES = {"PREPARED", "FINALIZED", "BLOCKED"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_event(run_dir: Path, event: dict[str, object]) -> None:
    event = {"at": utc_now(), **event}
    with (run_dir / "Events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def load_run(run_dir: Path) -> dict[str, object]:
    run_path = run_dir / "Task-Run.json"
    if not run_path.is_file():
        raise ValueError("missing_task_run_json")
    return read_json(run_path)


def default_progress(run: dict[str, object], mode: str, actor: str) -> dict[str, object]:
    status = str(run.get("status", ""))
    state = "BLOCKED" if status == "BLOCKED" else "PREPARED"
    return {
        "apply_state_schema_version": APPLY_STATE_SCHEMA_VERSION,
        "task_run_id": run.get("task_run_id"),
        "mode": mode,
        "state": state,
        "actor": actor,
        "prepared_at": utc_now(),
        "finalized_at": "",
        "selected_tasks": [],
        "one_writer_per_slice": True,
        "blocked_reasons": run.get("blocked_reasons", []),
    }


def default_writer_lock(actor: str) -> dict[str, object]:
    return {
        "apply_state_schema_version": APPLY_STATE_SCHEMA_VERSION,
        "lock_state": "available",
        "owner": "",
        "created_by": actor,
        "created_at": utc_now(),
        "expires_at": "",
    }


def validate_run_dir(run_dir: Path) -> list[str]:
    errors: list[str] = []
    try:
        run = load_run(run_dir)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]

    progress_path = run_dir / "Progress.json"
    events_path = run_dir / "Events.jsonl"
    lock_path = run_dir / "Writer-Lock.json"
    for path in [progress_path, events_path, lock_path]:
        if not path.is_file():
            errors.append(f"missing_file={path.name}")

    if progress_path.is_file():
        try:
            progress = read_json(progress_path)
        except json.JSONDecodeError:
            errors.append("invalid_json=Progress.json")
        else:
            if progress.get("apply_state_schema_version") != APPLY_STATE_SCHEMA_VERSION:
                errors.append("invalid_progress_schema_version")
            if progress.get("task_run_id") != run.get("task_run_id"):
                errors.append("progress_task_run_id_mismatch")
            if progress.get("mode") not in VALID_MODES:
                errors.append("invalid_progress_mode")
            if progress.get("state") not in VALID_PROGRESS_STATES:
                errors.append("invalid_progress_state")
            if progress.get("one_writer_per_slice") is not True:
                errors.append("progress_must_require_one_writer")

    if events_path.is_file():
        try:
            lines = [line for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            parsed_events = [json.loads(line) for line in lines]
        except json.JSONDecodeError:
            errors.append("invalid_jsonl=Events.jsonl")
        else:
            if not parsed_events:
                errors.append("events_missing")
            for event in parsed_events:
                if not event.get("event") or not event.get("actor") or not event.get("evidence"):
                    errors.append("event_missing_required_fields")
                    break

    if lock_path.is_file():
        try:
            lock = read_json(lock_path)
        except json.JSONDecodeError:
            errors.append("invalid_json=Writer-Lock.json")
        else:
            if lock.get("apply_state_schema_version") != APPLY_STATE_SCHEMA_VERSION:
                errors.append("invalid_writer_lock_schema_version")
            if lock.get("lock_state") not in {"available", "held", "recovered"}:
                errors.append("invalid_writer_lock_state")
            if lock.get("lock_state") == "held" and not lock.get("owner"):
                errors.append("held_writer_lock_missing_owner")
    return sorted(set(errors))


def prepare(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if args.mode not in VALID_MODES:
        print("task_apply_error=invalid_mode")
        return 2
    try:
        run_dir = task_run.create_task_run(root, args.stage, None, args.run_id_suffix)
    except (ValueError, FileExistsError) as exc:
        print(f"task_apply_error={exc}")
        return 2
    run = load_run(run_dir)
    write_json(run_dir / "Progress.json", default_progress(run, args.mode, args.actor))
    write_json(run_dir / "Writer-Lock.json", default_writer_lock(args.actor))
    append_event(
        run_dir,
        {
            "event": "prepared",
            "actor": args.actor,
            "evidence": args.evidence,
            "mode": args.mode,
            "stage": args.stage,
        },
    )
    print(f"task_apply_run_dir={run_dir}")
    return 0


def validate(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    errors = validate_run_dir(run_dir)
    if errors:
        for error in errors:
            print(f"task_apply_error={error}")
        return 1
    print("task_apply_validation=passed")
    return 0


def finalize(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    errors = validate_run_dir(run_dir)
    if errors:
        for error in errors:
            print(f"task_apply_error={error}")
        return 1
    progress = read_json(run_dir / "Progress.json")
    progress["state"] = "FINALIZED"
    progress["finalized_at"] = utc_now()
    write_json(run_dir / "Progress.json", progress)
    write_json(
        run_dir / "Result.json",
        {
            "apply_state_schema_version": APPLY_STATE_SCHEMA_VERSION,
            "task_run_id": progress.get("task_run_id"),
            "status": "finalized",
            "actor": args.actor,
            "evidence": args.evidence,
            "finalized_at": progress["finalized_at"],
        },
    )
    append_event(run_dir, {"event": "finalized", "actor": args.actor, "evidence": args.evidence})
    print("task_apply_finalize=passed")
    return 0


def recover_lock(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    lock_path = run_dir / "Writer-Lock.json"
    if not lock_path.is_file():
        print("task_apply_error=missing_file=Writer-Lock.json")
        return 1
    lock = read_json(lock_path)
    expires_at = str(lock.get("expires_at") or "")
    if lock.get("lock_state") == "held":
        if not expires_at:
            print("task_apply_error=held_writer_lock_missing_expiry")
            return 1
        try:
            expiry = datetime.fromisoformat(expires_at)
        except ValueError:
            print("task_apply_error=invalid_writer_lock_expiry")
            return 1
        if expiry > datetime.now(timezone.utc):
            print("task_apply_error=writer_lock_not_expired")
            return 1
    lock["lock_state"] = "recovered"
    lock["owner"] = ""
    lock["recovered_by"] = args.actor
    lock["recovered_at"] = utc_now()
    write_json(lock_path, lock)
    append_event(run_dir, {"event": "lock_recovered", "actor": args.actor, "evidence": args.evidence})
    print("task_apply_recover_lock=passed")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage AntigravityQB local task-run state artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--root", default=".")
    prepare_parser.add_argument("--stage", required=True, choices=sorted(task_run.STAGES))
    prepare_parser.add_argument("--mode", default="direct", choices=sorted(VALID_MODES))
    prepare_parser.add_argument("--actor", default="controller")
    prepare_parser.add_argument("--evidence", required=True)
    prepare_parser.add_argument("--run-id-suffix")
    prepare_parser.set_defaults(func=prepare)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--run-dir", required=True)
    validate_parser.set_defaults(func=validate)

    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("--run-dir", required=True)
    finalize_parser.add_argument("--actor", default="controller")
    finalize_parser.add_argument("--evidence", required=True)
    finalize_parser.set_defaults(func=finalize)

    recover_parser = subparsers.add_parser("recover-lock")
    recover_parser.add_argument("--run-dir", required=True)
    recover_parser.add_argument("--actor", default="controller")
    recover_parser.add_argument("--evidence", required=True)
    recover_parser.set_defaults(func=recover_lock)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
