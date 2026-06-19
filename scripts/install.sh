#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/skills/antigravityqb"
SCOPE=""
TARGET=""
DRY_RUN="false"
FORCE="false"

usage() {
  cat <<'EOF'
Usage: scripts/install.sh --scope app-global|ide-global|ide-project|cli-global|cli-project [--target PATH] [--dry-run] [--force]

Scopes:
  app-global   -> ~/.gemini/config/plugins/antigravityqb/skills/antigravityqb
  ide-global   -> ~/.agents/skills/antigravityqb
  ide-project  -> <target>/.agents/skills/antigravityqb
  cli-global   -> ~/.gemini/antigravity-cli/skills/antigravityqb
  cli-project  -> <target>/.agent/skills/antigravityqb
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      SCOPE="${2:-}"
      shift 2
      ;;
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    --force)
      FORCE="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown_argument=$1"
      usage
      exit 2
      ;;
  esac
done

if [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "missing_skill_source=$SRC"
  exit 1
fi

case "$SCOPE" in
  app-global)
    PLUGIN_ROOT="$HOME/.gemini/config/plugins/antigravityqb"
    DEST="$PLUGIN_ROOT/skills/antigravityqb"
    ;;
  ide-global)
    DEST="$HOME/.agents/skills/antigravityqb"
    ;;
  cli-global)
    DEST="$HOME/.gemini/antigravity-cli/skills/antigravityqb"
    ;;
  ide-project)
    if [[ -z "$TARGET" ]]; then
      echo "target_required_for_scope=$SCOPE"
      exit 2
    fi
    DEST="$TARGET/.agents/skills/antigravityqb"
    ;;
  cli-project)
    if [[ -z "$TARGET" ]]; then
      echo "target_required_for_scope=$SCOPE"
      exit 2
    fi
    DEST="$TARGET/.agent/skills/antigravityqb"
    ;;
  "")
    echo "scope_required=true"
    usage
    exit 2
    ;;
  *)
    echo "invalid_scope=$SCOPE"
    usage
    exit 2
    ;;
esac

PARENT="$(dirname "$DEST")"

echo "source=$SRC"
if [[ -n "${PLUGIN_ROOT:-}" ]]; then
  echo "plugin_root=$PLUGIN_ROOT"
fi
echo "destination=$DEST"
echo "dry_run=$DRY_RUN"
echo "force=$FORCE"

if [[ "$DRY_RUN" == "true" ]]; then
  check_path="${PLUGIN_ROOT:-$DEST}"
  if [[ -e "$check_path" && "$FORCE" != "true" ]]; then
    echo "destination_exists=$check_path"
    echo "would_fail_without_force=true"
  else
    echo "would_install=true"
  fi
  exit 0
fi

check_path="${PLUGIN_ROOT:-$DEST}"
if [[ -e "$check_path" ]]; then
  if [[ "$FORCE" != "true" ]]; then
    echo "destination_exists=$check_path"
    echo "use_force_to_replace=true"
    exit 1
  fi
  rm -rf "$check_path"
fi

mkdir -p "$PARENT"
cp -R "$SRC" "$DEST"
if [[ -n "${PLUGIN_ROOT:-}" ]]; then
  cat > "$PLUGIN_ROOT/plugin.json" <<'JSON'
{
  "name": "antigravityqb",
  "version": "0.2.1",
  "description": "Repo-aware planning, evidence-backed comprehension, autopsy, audit, and gated implementation handoff for Google Antigravity.",
  "author": {
    "name": "AntigravityQB maintainers"
  },
  "license": "MIT",
  "keywords": [
    "antigravity",
    "planning",
    "skills",
    "project-management"
  ]
}
JSON
  cat > "$PLUGIN_ROOT/installed_version.json" <<'JSON'
{"version": "0.2.1"}
JSON
fi
echo "installed_skill=$DEST"
