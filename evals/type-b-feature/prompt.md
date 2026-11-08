---
max_turns: 28
timeout_seconds: 700
allowed_tools: [Read, Glob, Grep, Skill, Agent]
tags: [planning, feature, type-b, cross-repo]
---

Add TOML as a supported QaaS serialization format. Prepare and independently
review the exact cross-repository implementation plan, including tests and
release impact. Do not implement it. The developer interview already confirmed
D-1: TOML is a compiled framework serialization format; D-2: support both
serialization and deserialization; D-3: follow the verified YAML sibling
convention; D-4: preserve current formats and reject unrelated refactoring.
Shared understanding is confirmed. This is not approval of the resulting plan.
