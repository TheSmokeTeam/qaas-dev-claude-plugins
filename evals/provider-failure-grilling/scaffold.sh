#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${QAAS_EVAL_GRILLING_ROOT:-}" ]]; then
  exit 0
fi

mkdir -p providers
cp -R "$QAAS_EVAL_GRILLING_ROOT" providers/grilling
rm providers/grilling/skills/productivity/grilling/SKILL.md
