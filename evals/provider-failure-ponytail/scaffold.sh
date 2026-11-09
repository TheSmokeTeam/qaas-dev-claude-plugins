#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/../implementation-approved/scaffold.sh"
if [[ -z "${QAAS_EVAL_PONYTAIL_ROOT:-}" ]]; then
  exit 0
fi

mkdir -p providers
cp -R "$QAAS_EVAL_PONYTAIL_ROOT" providers/ponytail
rm providers/ponytail/skills/ponytail/SKILL.md
