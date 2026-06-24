#!/usr/bin/env python3
"""Create a tracked-only sanitized AntigravityQB release archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import check_public_privacy


PACKAGE_NAME = "AntigravityQB"
PACKAGE_VERSION = "0.3.0"
DEFAULT_OUTPUT = "AntigravityQB-sanitized.zip"
MANIFEST_NAME = "PACKAGE-MANIFEST.json"

FORBIDDEN_ARCHIVE_PATTERN = re.compile(
    r"(^|/)(\.git|__pycache__|\.env|artifacts|logs|tmp|__MACOSX)(/|$)"
    r"|\.pyc$|\.pem$|\.key$|\.local($|\.)"
)
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("openrouter_api_key", re.compile(r"\bsk-or-v1-[A-Za-z0-9_-]{20,}\b")),
    ("openai_api_key", re.compile(r"\bsk-(?!or-v1-)[A-Za-z0-9_-]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("github_legacy_pat", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"BEGIN (?:RSA|OPENSSH|DSA|EC|PRIVATE) KEY")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
)
OPENROUTER_ENV = re.compile(r"\bOPENROUTER_API_KEY\s*=\s*([^\s#]+)", re.IGNORECASE)
ALLOWED_OPENROUTER_VALUES = {
    "$OPENROUTER_API_KEY",
    "<redacted>",
    "redacted",
    "your_openrouter_api_key",
}


class ExportError(RuntimeError):
    pass


def run_git(root: Path, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise ExportError(detail)
    return result


def ensure_clean_tree(root: Path) -> None:
    checks = [
        (["diff", "--quiet"], "working_tree_dirty"),
        (["diff", "--cached", "--quiet"], "index_dirty"),
        (["status", "--porcelain", "--untracked-files=all"], "untracked_or_dirty_files"),
    ]
    for args, label in checks:
        result = run_git(root, args, check=False)
        if result.returncode != 0 or result.stdout.strip():
            raise ExportError(label)


def tracked_files(root: Path) -> list[Path]:
    result = run_git(root, ["ls-files", "-z"])
    files = [Path(item) for item in result.stdout.split("\0") if item]
    return sorted(files, key=lambda path: path.as_posix())


def reject_unsafe_paths(root: Path, files: list[Path]) -> None:
    findings: list[str] = []
    for rel in files:
        rel_text = rel.as_posix()
        full = root / rel
        if rel.is_absolute() or ".." in rel.parts:
            findings.append(f"{rel_text}: unsafe_path")
        if FORBIDDEN_ARCHIVE_PATTERN.search(rel_text):
            findings.append(f"{rel_text}: forbidden_archive_path")
        if full.is_symlink():
            findings.append(f"{rel_text}: symlink_not_allowed")
        if not full.is_file():
            findings.append(f"{rel_text}: not_regular_file")
    if findings:
        raise ExportError("archive_path_hygiene_failed\n" + "\n".join(findings))


def secret_findings(root: Path, files: list[Path]) -> list[str]:
    findings: list[str] = []
    for rel in files:
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for name, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{rel}:{line_number}: {name}")
            match = OPENROUTER_ENV.search(line)
            if match:
                value = match.group(1).strip().strip("'\"")
                if value and value not in ALLOWED_OPENROUTER_VALUES:
                    findings.append(f"{rel}:{line_number}: openrouter_env_value")
    return findings


def public_privacy_findings(root: Path) -> list[str]:
    paths = check_public_privacy.iter_scan_paths(root)
    return check_public_privacy.scan_paths(root, paths)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(root: Path, files: list[Path]) -> dict[str, object]:
    commit = run_git(root, ["rev-parse", "HEAD"]).stdout.strip()
    tree = run_git(root, ["rev-parse", "HEAD^{tree}"]).stdout.strip()
    branch = run_git(root, ["branch", "--show-current"], check=False).stdout.strip() or "detached"
    entries = []
    for rel in files:
        path = root / rel
        mode = path.stat().st_mode
        entries.append(
            {
                "path": rel.as_posix(),
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
                "executable": bool(mode & stat.S_IXUSR),
            }
        )
    return {
        "package_name": PACKAGE_NAME,
        "package_version": PACKAGE_VERSION,
        "manifest_version": 1,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "git": {
            "commit": commit,
            "tree": tree,
            "branch": branch,
            "working_tree_clean": True,
        },
        "archive": {
            "prefix": f"{PACKAGE_NAME}/",
            "tracked_only": True,
            "symlink_safe": True,
            "secret_scan": "passed",
            "privacy_scan": "passed",
            "generated_files": [MANIFEST_NAME],
        },
        "tracked_file_count": len(entries),
        "tracked_files": entries,
    }


def write_zip(root: Path, output: Path, files: list[Path], manifest: dict[str, object]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for rel in files:
            source = root / rel
            info = zipfile.ZipInfo(f"{PACKAGE_NAME}/{rel.as_posix()}")
            info.date_time = (1980, 1, 1, 0, 0, 0)
            mode = source.stat().st_mode
            info.external_attr = (mode & 0o777) << 16
            archive.writestr(info, source.read_bytes())

        manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        info = zipfile.ZipInfo(f"{PACKAGE_NAME}/{MANIFEST_NAME}")
        info.date_time = (1980, 1, 1, 0, 0, 0)
        info.external_attr = 0o644 << 16
        archive.writestr(info, manifest_bytes)


def create_export(root: Path, output: Path) -> dict[str, object]:
    if run_git(root, ["rev-parse", "--is-inside-work-tree"], check=False).returncode != 0:
        raise ExportError("git_checkout_required")
    ensure_clean_tree(root)
    files = tracked_files(root)
    reject_unsafe_paths(root, files)

    secret_hits = secret_findings(root, files)
    if secret_hits:
        raise ExportError("release_secret_hygiene_failed\n" + "\n".join(secret_hits))

    privacy_hits = public_privacy_findings(root)
    if privacy_hits:
        raise ExportError("release_pii_hygiene_failed\n" + "\n".join(privacy_hits))

    manifest = build_manifest(root, files)
    write_zip(root, output, files, manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to export.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output zip path.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output

    try:
        manifest = create_export(root, output)
    except ExportError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"sanitized_export={output}")
    print(f"manifest={PACKAGE_NAME}/{MANIFEST_NAME}")
    print(f"commit={manifest['git']['commit']}")
    print(f"tracked_file_count={manifest['tracked_file_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
