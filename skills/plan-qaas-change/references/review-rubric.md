# QaaS Plan Review Rubric

Review the raw request, developer interview record, and plan against the
repositories. Do not trust the plan's citations until sampled in source. Do not
rewrite the plan, answer developer decisions, or grant developer approval;
return findings that the planner must disposition.

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
4. **Interview fidelity** — facts were researched rather than delegated to the
   developer; material decisions are numbered; the developer's answers and
   shared-understanding confirmation are recorded without reinterpretation.
5. **Architecture** — ownership and Type A/Type B classification are correct;
   framework dependency and release effects are complete.
6. **Current-state model** — bug root cause or feature integration seam is proven,
   not merely plausible; callers, configuration, tests, and generated surfaces
   are accounted for.
7. **Desired-state specification** — invariants and acceptance criteria are
   observable, unambiguous, and cover errors and boundaries.
8. **Exactness** — every step names a real repository, file, symbol, exact change,
   convention, dependency, acceptance criterion, test, and command.
9. **Test quality** — a regression or behavioral test fails before the change
   where practical; tests assert outcomes rather than implementation details;
   focused and full verification are included.
10. **Traceability** — every acceptance criterion maps to evidence, steps, tests,
   and verification, with no orphan step or test.
11. **Completeness** — API, configuration, schemas, docs, compatibility,
   migration, security, performance, observability, rollout, rollback, packaging,
   and release are addressed or validly `N/A`.
12. **Minimality and sequencing** — the smallest complete change is proposed by
    reusing existing code, platform features, or installed dependencies before
    adding abstractions or dependencies; unrelated cleanup and speculative work
    are rejected; correctness, safety, tests, and release work remain intact.
13. **Freshness** — inspected commits still match and the review records the same
    provenance.
14. **Approval integrity** — technical review leaves the plan
    `AWAITING_APPROVAL`; only an explicit developer decision on the same revision
    may change it to `APPROVED`.
15. **Handoff quality** — a semi-fluent QaaS developer can begin with the named
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

An `APPROVE` verdict means the plan is technically ready to present to the
developer. It does not authorize implementation.
