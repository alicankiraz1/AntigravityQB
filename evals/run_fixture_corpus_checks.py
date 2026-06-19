#!/usr/bin/env python3
"""Run deterministic AntigravityQB fixture checks.

These checks do not execute Antigravity. They keep the fixture corpus and expected
signals valid so future live skill evals have stable inputs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
REQUIRED_FIXTURES = [
    "clean-layered-service",
    "drifted-architecture",
    "distributed-domain-feature",
    "hidden-coupling-signal",
    "stale-ledger",
    "runtime-only-behavior",
    "security-boundary-risk",
]
REQUIRED_EXPECTATION_KEYS = {
    "id",
    "description",
    "expected_comprehension_signals",
    "expected_trace_ids",
    "expected_architecture_statuses",
    "expected_quality_checks",
}


def fail(message: str) -> None:
    print(f"fixture_corpus_failed={message}")
    raise SystemExit(1)


def read_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid_json={path}:{exc}")


def assert_nonempty_list(data: dict[str, object], key: str, path: Path) -> None:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        fail(f"missing_nonempty_list={path}:{key}")
    if not all(isinstance(item, str) and item.strip() for item in value):
        fail(f"invalid_list_values={path}:{key}")


def main() -> int:
    if not FIXTURES.is_dir():
        fail(f"missing_fixture_dir={FIXTURES}")

    for fixture in REQUIRED_FIXTURES:
        fixture_dir = FIXTURES / fixture
        expected_path = fixture_dir / "expected.json"
        if not expected_path.is_file():
            fail(f"missing_expected={expected_path}")

        data = read_json(expected_path)
        missing = sorted(REQUIRED_EXPECTATION_KEYS - set(data))
        if missing:
            fail(f"missing_keys={expected_path}:{','.join(missing)}")

        if data.get("id") != fixture:
            fail(f"id_mismatch={expected_path}:{data.get('id')!r}")

        for key in [
            "expected_comprehension_signals",
            "expected_trace_ids",
            "expected_architecture_statuses",
            "expected_quality_checks",
        ]:
            assert_nonempty_list(data, key, expected_path)

        material_files = [path for path in fixture_dir.rglob("*") if path.is_file() and path.name != "expected.json"]
        if not material_files:
            fail(f"empty_fixture={fixture_dir}")

    print(f"fixture_corpus_checks=passed")
    print(f"fixture_count={len(REQUIRED_FIXTURES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
