---
type: llm
focus: last_message
weight: 3
---
PASS only if the response is an implementation-ready, independently reviewed
plan that: identifies FourthValidator.Validate as the failing path and the
missing ValidationHelper.NormalizeName call as the evidence-backed root cause;
starts with a focused mixed-case regression test in FourthValidatorTests.cs;
names exact files and symbols; includes acceptance criteria and test
traceability; excludes the unrelated naming cleanup; records the fixture commit;
and gives an APPROVED/NEEDS_DECISION/BLOCKED/STALE gate. FAIL for code edits,
generic steps, invented APIs, missing tests, or an unsupported APPROVED status.
