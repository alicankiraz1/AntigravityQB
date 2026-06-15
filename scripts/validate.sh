#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

required_files=(
  "skills/antigravityqb/SKILL.md"
  "skills/antigravityqb/scripts/validate_planner_docs.py"
  "skills/antigravityqb/references/First-Planner.md"
  "skills/antigravityqb/references/Autopsy-Planner.md"
  "skills/antigravityqb/references/Second-Planner.md"
  "skills/antigravityqb/references/Third-Planner.md"
  "skills/antigravityqb/references/Fourth-Planner.md"
  "skills/antigravityqb/references/repo-aware-intake.md"
  "skills/antigravityqb/references/workflow-quality.md"
  "README.md"
  "docs/INSTALLATION.md"
  "docs/USAGE.md"
  "docs/MAINTAINING.md"
  ".github/workflows/validate.yml"
  "scripts/install.sh"
  "tests/test_skill_content.py"
  "tests/test_validate_planner_docs.py"
  "tests/test_antigravity_packaging.py"
  "LICENSE"
)

for path in "${required_files[@]}"; do
  if [[ ! -f "$path" ]]; then
    echo "missing_required_file=$path"
    exit 1
  fi
done

python3 - <<'PY'
from pathlib import Path
import re
import sys

text = Path("skills/antigravityqb/SKILL.md").read_text(encoding="utf-8")
match = re.match(r"---\n(.*?)\n---\n", text, flags=re.DOTALL)
if not match:
    print("skill_frontmatter_missing=true")
    sys.exit(1)
frontmatter = match.group(1)
required = {
    "name: antigravityqb",
    "description: Repo-aware project planning workflow for Google Antigravity. Use Markdown-based stable planning, validation gates, existing-project autopsy, phase sub-plans, QA audit, and a gated implementation handoff that continues through the ready queue.",
}
missing = sorted(item for item in required if item not in frontmatter)
if missing:
    print("skill_frontmatter_missing_keys=" + ",".join(missing))
    sys.exit(1)
PY

python3 - <<'PY'
from pathlib import Path
import sys

blocked_needles = (
    "$" + "codexqb",
    "plugins/codexqb",
    ".codex-plugin",
    "openai.yaml",
    "codex plugin add",
    "codex plugin marketplace",
    ".agents/plugins/marketplace.json",
)
scan_roots = [
    Path("README.md"),
    Path("Makefile"),
    Path("docs"),
    Path("skills"),
    Path("scripts/install.sh"),
]
ignored_parts = {
    "__pycache__",
}
blocked_suffixes = {".pyc", ".zip"}
findings: list[str] = []
paths: list[Path] = []
for root in scan_roots:
    if root.is_file():
        paths.append(root)
    elif root.is_dir():
        paths.extend(path for path in root.rglob("*") if path.is_file())

for path in paths:
    if not path.is_file():
        continue
    if ignored_parts.intersection(path.parts):
        continue
    if path.suffix in blocked_suffixes:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for needle in blocked_needles:
        if needle in text:
            findings.append(f"{path}: contains stale platform text {needle}")
            break

if findings:
    print("stale_platform_references_found")
    for finding in findings:
        print(finding)
    sys.exit(1)
PY

python3 - <<'PY'
from pathlib import Path
import re
import sys

secret_patterns = [
    ("openrouter_api_key", re.compile(r"\bsk-or-v1-[A-Za-z0-9_-]{20,}\b")),
    ("openai_api_key", re.compile(r"\bsk-(?!or-v1-)[A-Za-z0-9_-]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("github_legacy_pat", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"BEGIN (?:RSA|OPENSSH|DSA|EC|PRIVATE) KEY")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
]
openrouter_env = re.compile(r"\bOPENROUTER_API_KEY\s*=\s*([^\s#]+)", re.IGNORECASE)
allowed_openrouter_values = {
    "$OPENROUTER_API_KEY",
    "<redacted>",
    "redacted",
    "your_openrouter_api_key",
}
scan_roots = [
    Path("README.md"),
    Path("Makefile"),
    Path(".github"),
    Path("docs"),
    Path("skills"),
    Path("scripts"),
    Path("tests"),
]
ignored_parts = {
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
blocked_suffixes = {".key", ".pem", ".pyc", ".zip"}

paths: list[Path] = []
for root in scan_roots:
    if root.is_file():
        paths.append(root)
    elif root.is_dir():
        paths.extend(path for path in root.rglob("*") if path.is_file())

findings: list[str] = []
for path in sorted(paths):
    if ignored_parts.intersection(path.parts):
        continue
    if path.suffix in blocked_suffixes:
        continue
    if path.name == ".DS_Store" or path.name.startswith(".env"):
        continue
    if path.name.endswith(".local") or ".local." in path.name:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    for line_number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in secret_patterns:
            if pattern.search(line):
                findings.append(f"{path}:{line_number}: {name}")

        match = openrouter_env.search(line)
        if match:
            value = match.group(1).strip().strip("'\"")
            if value and value not in allowed_openrouter_values:
                findings.append(f"{path}:{line_number}: openrouter_env_value")

if findings:
    print("release_secret_hygiene_failed")
    for finding in findings:
        print(finding)
    sys.exit(1)
PY

python3 - <<'PY'
from pathlib import Path
import re
import sys

pii_patterns = [
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("us_ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("turkish_tckn", re.compile(r"\b[1-9]\d{10}\b")),
    ("passport_like_id", re.compile(r"\b[A-Z][0-9]{8}\b")),
    ("phone_number", re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}\b")),
]
scan_roots = [
    Path("README.md"),
    Path("Makefile"),
    Path(".github"),
    Path("docs"),
    Path("skills"),
    Path("scripts"),
    Path("tests"),
]
ignored_parts = {
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
blocked_suffixes = {".key", ".pem", ".pyc", ".zip"}
allowed_fragments = {
    "noreply.github.com",
    "users.noreply.github.com",
    "example.com",
    "example-root",
}

paths: list[Path] = []
for root in scan_roots:
    if root.is_file():
        paths.append(root)
    elif root.is_dir():
        paths.extend(path for path in root.rglob("*") if path.is_file())

findings: list[str] = []
for path in sorted(paths):
    if ignored_parts.intersection(path.parts):
        continue
    if path.suffix in blocked_suffixes:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(fragment in line for fragment in allowed_fragments):
            continue
        for name, pattern in pii_patterns:
            if pattern.search(line):
                findings.append(f"{path}:{line_number}: {name}")

if findings:
    print("release_pii_hygiene_failed")
    for finding in findings:
        print(finding)
    sys.exit(1)
PY

python3 - <<'PY'
import io
import re
import subprocess
import sys
import tarfile

inside_git = subprocess.run(
    ["git", "rev-parse", "--is-inside-work-tree"],
    text=True,
    capture_output=True,
    check=False,
)
if inside_git.returncode != 0:
    print("archive_hygiene_skipped_no_git=true")
    sys.exit(0)

archive = subprocess.run(["git", "archive", "--format=tar", "HEAD"], check=True, capture_output=True).stdout
bad = re.compile(
    r"(^|/)(\.git|__pycache__|\.env|artifacts|logs|tmp|__MACOSX)(/|$)"
    r"|\.pyc$|\.pem$|\.key$|\.local($|\.)"
)

with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
    offenders = [member.name for member in tar.getmembers() if bad.search(member.name)]

if offenders:
    print("archive_hygiene_failed")
    for offender in offenders:
        print(offender)
    sys.exit(1)
PY

tmp_project="$(mktemp -d)"
trap 'rm -rf "$tmp_project"' EXIT
bash scripts/install.sh --scope ide-project --target "$tmp_project" --dry-run >/dev/null
bash scripts/install.sh --scope cli-project --target "$tmp_project" --dry-run >/dev/null
bash scripts/install.sh --scope ide-project --dry-run >/tmp/antigravityqb-missing-target.log 2>&1 && {
  echo "expected_missing_target_failure=false"
  exit 1
}

python3 -m unittest discover -s tests -v
