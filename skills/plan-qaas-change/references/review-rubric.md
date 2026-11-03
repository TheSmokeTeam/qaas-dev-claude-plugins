# QaaS Plan Review Rubric

Review the raw request and plan against the repositories. Do not trust the plan's
citations until sampled in source. Do not rewrite the plan; return findings that
the planner must disposition.

## Verdicts

- `APPROVE`: no critical or major finding; the plan is executable without
  architectural rediscovery or implementation-changing decisions.
- `REVISE`: evidence or plan content is available but incomplete, incorrect,
  vague, untraceable, or unnecessarily broad.
- `BLOCK`: approval requires unavailable evidence, reproduction, repository
  access, or a user/product/architecture decision.

## Checks

1. **Request fidelity** — desired behavior, constraints, and non-goals match the
   raw request; no silent scope expansion.
2. **Ecosystem comprehension** — the Know QaaS Context Brief explains platform
   scope, ecosystem location, dependency position, extension model, release
   ripple, authorities, and known unknowns before narrowing into code details.
   A repository list alone is insufficient.
3. **Evidence integrity** — repositories, commit SHAs, files, symbols, commands,
   signatures, and dependency claims exist and support the stated conclusions.
4. **Architecture** — ownership and Type A/Type B classification are correct;
   framework dependency and release effects are complete.
5. **Current-state model** — bug root cause or feature integration seam is proven,
   not merely plausible; callers, configuration, tests, and generated surfaces
   are accounted for.
6. **Desired-state specification** — invariants and acceptance criteria are
   observable, unambiguous, and cover errors and boundaries.
7. **Exactness** — every step names a real repository, file, symbol, exact change,
   convention, dependency, acceptance criterion, test, and command.
8. **Test quality** — a regression or behavioral test fails before the change
   where practical; tests assert outcomes rather than implementation details;
   focused and full verification are included.
9. **Traceability** — every acceptance criterion maps to evidence, steps, tests,
   and verification, with no orphan step or test.
10. **Completeness** — API, configuration, schemas, docs, compatibility,
   migration, security, performance, observability, rollout, rollback, packaging,
   and release are addressed or validly `N/A`.
11. **Minimality and sequencing** — the smallest complete change is proposed;
    unrelated cleanup and speculative abstractions are excluded; repository and
    task ordering respects dependencies.
12. **Freshness** — inspected commits still match and the review records the same
    provenance.
13. **Handoff quality** — a semi-fluent QaaS developer can begin with the named
    first test and finish without rediscovering architecture.

## Finding format

```markdown
### [critical|major|minor] Short title

- Plan location: <section or step>
- Evidence: <repo/path:line or missing evidence>
- Problem: <concrete failure>
- Required correction: <smallest change needed>
```

End with:

```markdown
Verdict: APPROVE | REVISE | BLOCK
Critical findings: <count>
Major findings: <count>
Minor findings: <count>
```
