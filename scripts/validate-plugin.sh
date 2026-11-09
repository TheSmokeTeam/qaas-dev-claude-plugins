#!/usr/bin/env bash
# Deterministic repository validation. Pass --online to add URL reachability.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail=0
online=0

if [ "${1:-}" = "--online" ]; then
  online=1
elif [ -n "${1:-}" ]; then
  echo "usage: $0 [--online]" >&2
  exit 2
fi

err() {
  echo "FAIL: $*" >&2
  fail=1
}

run_check() {
  local label="$1"
  shift
  echo "==> $label"
  "$@" || err "$label"
}

frontmatter() {
  awk 'NR == 1 && $0 == "---" { active = 1; next } active && $0 == "---" { exit } active' "$1"
}

echo "==> manifests and versions"
for manifest in "$ROOT/.claude-plugin/plugin.json" "$ROOT/.claude-plugin/marketplace.json"; do
  [ -f "$manifest" ] || { err "missing $manifest"; continue; }
  python3 -c 'import json,sys; json.load(open(sys.argv[1], encoding="utf-8"))' "$manifest" \
    || err "invalid JSON: $manifest"
done
python3 -c '
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
plugin = json.loads((root / ".claude-plugin/plugin.json").read_text())
market = json.loads((root / ".claude-plugin/marketplace.json").read_text())
versions = {plugin["version"], market["metadata"]["version"], market["plugins"][0]["version"]}
names = {plugin["name"], market["plugins"][0]["name"]}
raise SystemExit(0 if len(versions) == 1 and len(names) == 1 else 1)
' "$ROOT" || err "plugin and marketplace name/version metadata must match"

echo "==> component frontmatter"
for skill in "$ROOT"/skills/*/SKILL.md; do
  [ -f "$skill" ] || continue
  directory="$(basename "$(dirname "$skill")")"
  fm="$(frontmatter "$skill")"
  grep -q "^name: *$directory\$" <<<"$fm" || err "$skill: name must equal $directory"
  grep -Eq '^description: *([>|].*|\S.+)' <<<"$fm" || err "$skill: missing description"
  grep -Fq "(skills/$directory/SKILL.md)" "$ROOT/AGENTS.md" \
    || err "AGENTS.md omits skill: $directory"
done
for command in "$ROOT"/commands/*.md; do
  [ -f "$command" ] || continue
  grep -Eq '^description: *\S' <<<"$(frontmatter "$command")" \
    || err "$command: missing description"
done
for agent in "$ROOT"/agents/*.md; do
  [ -f "$agent" ] || continue
  name="$(basename "$agent" .md)"
  fm="$(frontmatter "$agent")"
  grep -q "^name: *$name\$" <<<"$fm" || err "$agent: name must equal $name"
  grep -Eq '^description: *([>|].*|\S.+)' <<<"$fm" || err "$agent: missing description"
done

echo "==> non-editing agent boundaries"
for name in qaas-change-planner qaas-plan-reviewer qaas-verifier; do
  agent="$ROOT/agents/$name.md"
  [ -f "$agent" ] || { err "missing agent: $agent"; continue; }
  fm="$(frontmatter "$agent")"
  grep -Eq '^disallowedTools:.*\bWrite\b' <<<"$fm" || err "$agent: must disallow Write"
  grep -Eq '^disallowedTools:.*\bEdit\b' <<<"$fm" || err "$agent: must disallow Edit"
done

run_check "portable AGENTS.md is current" "$ROOT/scripts/build-agents-md.sh" --check
run_check "Python syntax" python3 -m compileall -q "$ROOT/scripts" "$ROOT/skills"
run_check "repository utility unit tests" python3 -m unittest discover -q "$ROOT/scripts"
run_check "plan and baseline unit tests" \
  python3 -m unittest discover -q "$ROOT/skills/plan-qaas-change/scripts"
run_check "knowledge graph wrapper unit tests" \
  python3 -m unittest discover -q "$ROOT/skills/qaas-knowledge-graph/scripts"
run_check "eval layout" python3 "$ROOT/scripts/lint-evals.py" "$ROOT/evals"

echo "==> shell syntax and eval fixtures"
while IFS= read -r script; do
  bash -n "$script" || err "shell syntax: $script"
done < <(find "$ROOT/scripts" "$ROOT/evals" -type f -name '*.sh' -print | sort)
while IFS= read -r scaffold; do
  fixture_dir="$(mktemp -d)"
  if ! (cd "$fixture_dir" && bash "$scaffold"); then
    err "eval scaffold failed: $scaffold"
  fi
  find "$fixture_dir" -depth -delete
done < <(find "$ROOT/evals" -type f -name 'scaffold.sh' -print | sort)

if command -v claude >/dev/null 2>&1; then
  run_check "Claude plugin schema" claude plugin validate "$ROOT"
else
  err "claude CLI is required for plugin schema validation"
fi

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  run_check "Git whitespace" git -C "$ROOT" diff --check
fi

if [ "$online" -eq 1 ]; then
  echo "==> referenced URL reachability"
  while IFS= read -r url; do
    code="$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 15 "$url" || echo 000)"
    case "$code" in
      2*|3*) ;;
      *) err "unreachable ($code): $url" ;;
    esac
  done < <(
    grep -rhoE 'https://(github\.com/[A-Za-z0-9._/-]+|docs\.qaas\.online[A-Za-z0-9./_-]*)' \
      "$ROOT/README.md" "$ROOT/skills" "$ROOT/commands" "$ROOT/agents" 2>/dev/null \
      | sed 's/[),.;:]$//' | sort -u
  )
fi

if [ "$fail" -eq 0 ]; then
  echo "validate-plugin: OK"
else
  echo "validate-plugin: FAILED"
  exit 1
fi
