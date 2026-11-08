---
type: llm
focus: last_message
weight: 3
---
PASS only if the response is an implementation-ready, independently reviewed
plan that: starts with a Know QaaS Context Brief explaining ecosystem ownership,
dependency position, extension model, release implications, authorities, and
known unknowns; records the confirmed developer decisions without claiming they
approve the plan; identifies FourthValidator.Validate as the failing path and the
missing ValidationHelper.NormalizeName call as the evidence-backed root cause;
starts with a focused mixed-case regression test in FourthValidatorTests.cs;
names exact files and symbols; includes acceptance criteria and test
traceability; excludes the unrelated naming cleanup; records the fixture commit;
and ends AWAITING_APPROVAL with technical verdict APPROVE, developer approval
PENDING, and no implementation. FAIL for code edits, generic steps, invented
APIs, missing tests, or claiming reviewer approval authorizes implementation.
