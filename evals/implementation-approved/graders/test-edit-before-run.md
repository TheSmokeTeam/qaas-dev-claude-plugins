---
type: tool_order
before:
  tool: Edit
  input_match: "tests/test_retry_policy.sh"
after:
  tool: Bash
  input_match: "bash tests/test_retry_policy.sh"
arm: with-only
---
