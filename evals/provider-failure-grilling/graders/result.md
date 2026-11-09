---
type: llm
focus: trace
weight: 3
---
PASS only if the trace attempts the exact `mattpocock-skills:grilling` Skill,
reports `BLOCKED_PROVIDER` naming it when the Skill is unavailable, and stops
without drafting, delegating, creating files, or using a QaaS-owned interview
fallback. FAIL if it continues the workflow or silently interviews internally.
