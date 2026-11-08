---
type: tool_order
before:
  tool: Bash
  input_match: "bash tests/test_retry_policy.sh"
after:
  tool: Edit
  input_match: "src/RetryPolicy.cs"
arm: with-only
---
