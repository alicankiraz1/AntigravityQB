#!/usr/bin/env python3
"""Scan public AntigravityQB surfaces for local/private release leaks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DEFAULT_SCAN_ROOTS = ("README.md", "CHANGELOG.md", "docs", "skills")
IGNORED_PARTS = {
    ".git",
    "__MACOSX",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "artifacts",
    "build",
    "dist",
    "logs",
    "tmp",
}
BLOCKED_SUFFIXES = {".key", ".pem", ".pyc", ".zip"}
ALLOWED_LINE_FRAGMENTS = {
    "example.com",
    "noreply.github.com",
    "users.noreply.github.com",
    "/path/to/project",
    "<target>",
}

PRIVACY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("absolute_user_path", re.compile(r"(?<![\w.-])/(?:Users|home)/[A-Za-z0-9._-]+(?:/|$)")),
    ("mac_private_temp_path", re.compile(r"(?<![\w.-])/private/(?:tmp|var/folders)(?:/|$)")),
    ("sandbox_or_attachment_uri", re.compile(r"\b(?:sandbox:/mnt/data/|attachment://|file://)\S+")),
    (
        "thread_or_session_reference",
        re.compile(r"\b(?:thread_id|session_id|conversation_id|attachment_id|rollout_path)\s*[:=]\s*\S+", re.IGNORECASE),
    ),
    ("runtime_log_reference", re.compile(r"\b(?:rollout-\d{4}-|\.?[a-z][a-z0-9_-]*/sessions|runtime_id=)\S*", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("us_ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("turkish_tckn", re.compile(r"\b[1-9]\d{10}\b")),
    ("passport_like_id", re.compile(r"\b[A-Z][0-9]{8}\b")),
)


def iter_scan_paths(root: Path, scan_roots: tuple[str, ...] = DEFAULT_SCAN_ROOTS) -> list[Path]:
    paths: list[Path] = []
    for item in scan_roots:
        candidate = root / item
        if candidate.is_file():
            paths.append(candidate)
        elif candidate.is_dir():
            paths.extend(path for path in candidate.rglob("*") if path.is_file())
    return sorted(set(paths))


def should_skip(path: Path) -> bool:
    return bool(IGNORED_PARTS.intersection(path.parts)) or path.suffix in BLOCKED_SUFFIXES


def scan_paths(root: Path, paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in sorted(paths):
        if should_skip(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        rel = path.relative_to(root)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(fragment in line for fragment in ALLOWED_LINE_FRAGMENTS):
                continue
            for name, pattern in PRIVACY_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{rel}:{line_number}: {name}")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository or extracted package root.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    findings = scan_paths(root, iter_scan_paths(root))
    if findings:
        print("release_pii_hygiene_failed")
        for finding in findings:
            print(finding)
        return 1

    print("release_pii_hygiene=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
