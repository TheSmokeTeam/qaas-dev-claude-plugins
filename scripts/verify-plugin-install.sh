#!/usr/bin/env bash
# Networked integration check for native provider installation and load failures.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPECTED_VERSION="0.5.0"
EXPECTED_GRILLING_SHA="4ae2317ddb22b046e26455e4f9c9b3aaaf62212d"
EXPECTED_PONYTAIL_SHA="96608e078b2d5ea607c5c3b8b5a54d1c1fba6846"

python3 "$ROOT/scripts/test_plugin_dependencies.py"
command -v claude >/dev/null 2>&1 || {
  echo "verify-plugin-install: claude CLI is required" >&2
  exit 1
}

temp_root="$(mktemp -d)"
trap 'rm -rf "$temp_root"' EXIT
isolated_home="$temp_root/home"
isolated_xdg="$temp_root/xdg"
isolated_config="$temp_root/claude"
mkdir -p "$isolated_home" "$isolated_xdg" "$isolated_config"

run_claude() {
  env \
    HOME="$isolated_home" \
    XDG_CONFIG_HOME="$isolated_xdg" \
    CLAUDE_CONFIG_DIR="$isolated_config" \
    claude "$@"
}

check_missing_dependency() {
  local provider="$1"
  local case_root="$temp_root/missing-$provider"
  local broken_marketplace="$case_root/marketplace"
  mkdir -p "$case_root/home" "$case_root/xdg" "$case_root/claude"
  cp -R "$ROOT" "$broken_marketplace"
  python3 - "$broken_marketplace/.claude-plugin/marketplace.json" "$provider" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
provider = sys.argv[2]
marketplace = json.loads(path.read_text(encoding="utf-8"))
marketplace["plugins"] = [
    plugin for plugin in marketplace["plugins"] if plugin["name"] != provider
]
path.write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
PY
  env \
    HOME="$case_root/home" \
    XDG_CONFIG_HOME="$case_root/xdg" \
    CLAUDE_CONFIG_DIR="$case_root/claude" \
    claude plugin install qaas-platform-dev \
      --marketplace "$broken_marketplace" \
      --scope user \
      --json >"$case_root/result.json"
  grep -Fqi "$provider" "$case_root/result.json" || {
    echo "missing-dependency install warning did not name $provider" >&2
    cat "$case_root/result.json" >&2
    exit 1
  }
  grep -Fqi "will not load without it" "$case_root/result.json" || {
    echo "missing-dependency install did not report the load block" >&2
    cat "$case_root/result.json" >&2
    exit 1
  }
  env \
    HOME="$case_root/home" \
    XDG_CONFIG_HOME="$case_root/xdg" \
    CLAUDE_CONFIG_DIR="$case_root/claude" \
    claude plugin list --json >"$case_root/plugins.json"
  python3 - "$case_root/plugins.json" "$provider" <<'PY'
import json
import sys

plugins = json.load(open(sys.argv[1], encoding="utf-8"))
qaas = next(
    item for item in plugins if item.get("id", "").startswith("qaas-platform-dev@")
)
errors = "\n".join(qaas.get("errors", []))
if sys.argv[2] not in errors:
    raise SystemExit(f"QaaS load error did not name missing dependency: {sys.argv[2]}")
PY
}

check_missing_dependency mattpocock-skills
check_missing_dependency ponytail

run_claude plugin install qaas-platform-dev \
  --marketplace "$ROOT" \
  --scope user \
  --json >"$temp_root/install.json"
run_claude plugin list --json >"$temp_root/plugins.json"

python3 - "$temp_root/plugins.json" "$EXPECTED_VERSION" <<'PY'
import json
import sys

plugins = json.load(open(sys.argv[1], encoding="utf-8"))
expected = {
    "qaas-platform-dev": sys.argv[2],
    "mattpocock-skills": "1.3.2",
    "ponytail": "5.3.3",
}
by_name = {item.get("id", "").split("@", 1)[0]: item for item in plugins}
for name, version in expected.items():
    item = by_name.get(name)
    if not item:
        raise SystemExit(f"missing installed plugin: {name}")
    if item.get("version", "").split("-", 1)[0] != version:
        raise SystemExit(f"unexpected {name} version: {item.get('version')}")
    if item.get("enabled") is not True:
        raise SystemExit(f"plugin is not enabled: {name}")
PY

check_disabled_dependency() {
  local provider="$1"
  local provider_id="$provider@qaas-dev-claude-plugins"
  local qaas_id="qaas-platform-dev@qaas-dev-claude-plugins"

  if run_claude plugin disable "$provider_id" --scope user --json \
    >"$temp_root/reverse-dependent-$provider.json" 2>&1; then
    echo "$provider unexpectedly disabled while QaaS was enabled" >&2
    exit 1
  fi
  grep -Fqi "qaas-platform-dev" "$temp_root/reverse-dependent-$provider.json" || {
    echo "$provider disable failure did not name its QaaS reverse dependent" >&2
    cat "$temp_root/reverse-dependent-$provider.json" >&2
    exit 1
  }

  run_claude plugin disable "$qaas_id" --scope user --json >/dev/null
  run_claude plugin disable "$provider_id" --scope user --json >/dev/null
  run_claude plugin enable "$qaas_id" --scope user --json \
    >"$temp_root/auto-enable-$provider.json"
  grep -Fqi "dependenc" "$temp_root/auto-enable-$provider.json" || {
    echo "QaaS enable output did not report dependency auto-enable" >&2
    cat "$temp_root/auto-enable-$provider.json" >&2
    exit 1
  }

  run_claude plugin list --json >"$temp_root/plugins-after-$provider.json"
  python3 - "$temp_root/plugins-after-$provider.json" "$provider" <<'PY'
import json
import sys

plugins = json.load(open(sys.argv[1], encoding="utf-8"))
enabled = {
    item.get("id", "").split("@", 1)[0]
    for item in plugins
    if item.get("enabled") is True
}
required = {"qaas-platform-dev", sys.argv[2]}
if not required <= enabled:
    raise SystemExit(f"dependent auto-enable missing: {sorted(required - enabled)}")
PY
}

check_disabled_dependency mattpocock-skills
check_disabled_dependency ponytail

echo "verify-plugin-install: OK ($EXPECTED_GRILLING_SHA, $EXPECTED_PONYTAIL_SHA)"
