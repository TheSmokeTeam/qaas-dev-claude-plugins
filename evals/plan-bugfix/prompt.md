---
max_turns: 24
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent]
tags: [planning, bugfix, smoke]
---

Mixed-case validator names pass through the first three validators but fail in
FourthValidator. Prepare and independently review an exact implementation plan
for the smallest bugfix. Do not change any files and do not include the nearby
validator naming cleanup.
