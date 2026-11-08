# QaaS Plan Review Rubric

Review the frozen plan revision independently against the raw request, Know QaaS
brief, developer decisions, repository baselines, and live source. Do not rewrite
the plan, answer developer-owned decisions, or grant developer approval.

## Verdicts

- `APPROVE`: no critical or major finding; the frozen revision is executable
  without architectural rediscovery or an implementation-changing decision.
- `REVISE`: evidence or plan content is available but incomplete, incorrect,
  vague, untraceable, stale, or unnecessarily broad.
- `BLOCK`: approval requires unavailable evidence, access, reproduction, or a
  developer/product/architecture decision.

## Review checks

1. **Request and decision fidelity:** scope, behavior, constraints, non-goals,
   and every `D-n` match the raw request and confirmed interview.
2. **Ecosystem comprehension:** the Know QaaS brief correctly covers ownership,
   dependency position, extension model, release ripple, authorities, and
   unknowns before code-level detail.
3. **Baseline integrity:** every checkout has a full commit and worktree
   fingerprint; recomputed values match the frozen revision.
4. **Evidence integrity:** cited repositories, files, symbols, signatures,
   commands, conventions, and dependency claims exist and support the plan.
5. **Current-state proof:** a bug root cause or feature/refactor integration seam
   is proven, and callers, configuration, tests, generated surfaces, and release
   edges are accounted for.
6. **Desired-state quality:** invariants and acceptance criteria are observable,
   unambiguous, and cover boundary and error behavior.
7. **Exact test-first sequence:** every step names the repository, file, symbol,
   exact change, existing convention, dependency, acceptance criteria, tests,
   and verification command. The behavioral test and observed failure come
   first, or the plan gives a concrete reason this cannot be demonstrated and
   names equivalent regression evidence.
8. **Traceability:** every acceptance criterion maps to evidence, steps, tests,
   and final verification with no orphan step or test.
9. **Completeness:** API, configuration, schema, callers, docs, packaging,
   release, compatibility, migration, security, performance, observability,
   rollout, and rollback are addressed or validly `N/A`.
10. **Minimality:** existing code, platform capabilities, and installed
    dependencies were preferred before new abstractions; unrelated cleanup and
    speculative flexibility are excluded without cutting required quality work.
11. **Review-unit integrity:** recompute `plan_digest`; the verdict names the
    current `plan_revision` and digest. Material corrections or baseline
    replacements create a new revision and digest and require another review.
12. **Handoff quality:** a semi-fluent QaaS developer can start with the named
    test, execute the plan without rediscovery, stop on divergence, and invoke
    independent verification.

## Finding format

```markdown
### [critical|major|minor] Short title

- Plan location: <section or step>
- Evidence: <repo/path:line or missing evidence>
- Problem: <concrete failure>
- Required correction: <smallest change needed>
```

End with:

```text
Reviewed revision: <plan_revision>
Reviewed digest: <plan_digest>
Verdict: APPROVE | REVISE | BLOCK
Critical findings: <count>
Major findings: <count>
Minor findings: <count>
```

`APPROVE` means that exact revision is technically ready to present to the
developer. It never authorizes implementation.
