---
type: regex
target:
  source: file
  path: QaaS.Framework/tests/test_retry_policy.sh
pattern: "^#!/usr/bin/env bash\\s+set -euo pipefail\\s+rm -f \\.eval-focused-test-passed\\s+grep -q 'Attempts => 4;' src/RetryPolicy\\.cs\\s+printf 'focused-test: passed\\\\n' > \\.eval-focused-test-passed\\s*$"
---
