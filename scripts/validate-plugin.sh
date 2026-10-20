#!/usr/bin/env bash
# Validates the qaas-platform-dev plugin: manifests parse, skills and bundled
# resources are complete, and referenced TheSmokeTeam repos + docs resolve.
# This script manages its own failures via the `fail` accumulator and exits at
# the end, so we intentionally do NOT use `set -e` (which would abort early).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail=0
err() { echo "FAIL: $*" >&2; fail=1; }

# 1. Manifests parse as JSON.
for f in "$ROOT/.claude-plugin/plugin.json" "$ROOT/.claude-plugin/marketplace.json"; do
  [ -f "$f" ] || { err "missing $f"; continue; }
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" || err "invalid JSON: $f"
done
python3 -c 'import json,sys; p=json.load(open(sys.argv[1])); m=json.load(open(sys.argv[2])); assert p["version"] == m["metadata"]["version"] == m["plugins"][0]["version"]' \
  "$ROOT/.claude-plugin/plugin.json" "$ROOT/.claude-plugin/marketplace.json" \
  || err "plugin and marketplace versions must match"

# 2. Every skill has name + description frontmatter; name matches its directory.
# Note: when a glob matches nothing, bash yields the literal pattern; the
# `[ -f ... ] || continue` guard below skips that non-existent path.
for skill in "$ROOT"/skills/*/SKILL.md; do
  [ -f "$skill" ] || continue
  dir="$(basename "$(dirname "$skill")")"
  fm="$(awk 'NR==1&&$0=="---"{f=1;next} f&&$0=="---"{exit} f' "$skill")"
  echo "$fm" | grep -q "^name: *$dir\$" || err "$skill: name must equal '$dir'"
  echo "$fm" | grep -Eq "^description: *([>|].*|\S.+)" || err "$skill: missing description"
done

# 2b. Skill UI metadata, when present, has the required interface fields.
for metadata in "$ROOT"/skills/*/agents/openai.yaml; do
  [ -f "$metadata" ] || continue
  grep -q '^interface:' "$metadata" || err "$metadata: missing interface"
  grep -Eq '^  display_name: *[^[:space:]]' "$metadata" || err "$metadata: missing display_name"
  grep -Eq '^  short_description: *[^[:space:]]' "$metadata" || err "$metadata: missing short_description"
  grep -Eq '^  default_prompt: *[^[:space:]]' "$metadata" || err "$metadata: missing default_prompt"
done

# 2c. The graph workflow's deterministic helper is bundled and parses as Python.
graph_helper="$ROOT/skills/qaas-graph-workflow/scripts/repo_sync.py"
if [ -f "$ROOT/skills/qaas-graph-workflow/SKILL.md" ]; then
  [ -f "$graph_helper" ] || err "missing $graph_helper"
  if [ -f "$graph_helper" ]; then
    python3 -c 'import ast,sys; ast.parse(open(sys.argv[1], encoding="utf-8").read())' "$graph_helper" \
      || err "invalid Python: $graph_helper"
  fi
fi

# 3. Every command has a description.
for cmd in "$ROOT"/commands/*.md; do
  [ -f "$cmd" ] || continue
  awk 'NR==1&&$0=="---"{f=1;next} f&&$0=="---"{exit} f' "$cmd" \
    | grep -Eq "^description: *\S" || err "$cmd: missing description"
done

# 3b. Every agent has name + description frontmatter; name matches its filename.
for agent in "$ROOT"/agents/*.md; do
  [ -f "$agent" ] || continue
  base="$(basename "$agent" .md)"
  fm="$(awk 'NR==1&&$0=="---"{f=1;next} f&&$0=="---"{exit} f' "$agent")"
  echo "$fm" | grep -q "^name: *$base\$" || err "$agent: name must equal '$base'"
  echo "$fm" | grep -Eq "^description: *([>|].*|\S.+)" || err "$agent: missing description"
done

# 4. Referenced URLs resolve (skipped when OFFLINE=1).
if [ "${OFFLINE:-0}" != "1" ]; then
  while read -r url; do
    code="$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 15 "$url" || echo 000)"
    case "$code" in 2*|3*) ;; *) err "unreachable ($code): $url";; esac
  done < <(grep -rhoE 'https://(github\.com/TheSmokeTeam/[A-Za-z0-9._-]+|docs\.qaas\.online[A-Za-z0-9./_-]*)' \
            "$ROOT/skills" "$ROOT/commands" "$ROOT/agents" 2>/dev/null | sort -u)
fi

[ "$fail" -eq 0 ] && echo "validate-plugin: OK" || { echo "validate-plugin: FAILED"; exit 1; }
