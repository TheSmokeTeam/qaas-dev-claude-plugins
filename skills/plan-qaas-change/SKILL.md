---
name: plan-qaas-change
description: >-
  Interview the developer, prepare, independently review, and obtain explicit
  developer approval for an exact evidence-backed implementation plan for a QaaS
  platform feature or bugfix before code changes begin. Use for plan, design,
  implementation-plan, feature, bugfix, refactor, or "how should we implement"
  requests in TheSmokeTeam QaaS repositories. Produces a strict spec-driven
  current-state/desired-state plan with verified files and symbols, test-first
  steps, cross-repo impact, release work, and an AWAITING_APPROVAL, APPROVED,
  NEEDS_DECISION, BLOCKED, or STALE gate.
---

# Plan a QaaS Change

Prepare a QaaS Change Specification and Implementation Plan before editing
production code. Make the result executable by a developer who is only
semi-fluent in the QaaS codebase without copying volatile in-repo documentation
into this plugin.

## Non-negotiable boundaries

- Do not implement the feature or bugfix while planning.
- Do not edit source, tests, configuration, manifests, or generated files.
- Do not treat technical-review approval as developer approval. Only the
  developer can approve the current plan revision for implementation.
- Require a Know QaaS Context Brief before detailed planning. The brief must
  cover platform scope, ecosystem location, dependency position, extension
  model, release ripple, authority map, and known unknowns.
- Read each owning repository's `CLAUDE.md` first, then the relevant
  `project_specs.md`; use `README.md` only where the repository has no
  `CLAUDE.md`.
- Use `qaas-platform-overview` to establish repository ownership, Type A/Type B
  classification, and release ripple before choosing an implementation.
- Use `qaas-knowledge-graph` for cross-repo relationships and impact, then verify
  implementation details in source. A graph edge is not a substitute for reading
  the owning code and specifications.
- Never invent a repository, path, symbol, signature, command, dependency, or
  configuration key. Missing evidence makes the plan `BLOCKED`, not approximate.
- Do not require, install, configure, or alter another developer plugin. Compose
  with optional Grill Me and Ponytail skills when they are already available;
  use the built-in interview and minimality rules otherwise.

## Optional plugin interoperability

- **Grill Me:** if the model-invoked `grilling` skill is available, invoke it as
  the developer-interview engine. Do not invoke the user-only `/grill-me`
  wrapper from this skill. If unavailable, follow the interview protocol below.
- **Ponytail:** if `ponytail` is installed or already active, apply its current
  level when comparing solutions and reviewing plan scope. Do not switch its
  global mode. If unavailable, prefer the smallest complete change by reusing
  existing QaaS patterns, platform features, and installed dependencies.
- Optional plugins may strengthen the workflow but never replace QaaS evidence,
  the independent reviewer, tests, safety, release work, or developer approval.

## Workflow

1. **Ingest Know QaaS.** Apply `qaas-platform-overview` to the raw request and
   build the mandatory Know QaaS Context Brief. If a brief already exists,
   verify that it matches the current request and evidence; refresh it otherwise.
   Do not reduce this step to choosing a repository.
2. **Research facts before interviewing.** Inspect the owning instructions,
   source, tests, graph relationships, and sibling conventions. Never ask the
   developer for a fact the repositories or canonical sources can answer.
3. **Interview the developer.** Use `grilling` when available; otherwise map the
   open design decisions as a dependency tree. Ask the current decision frontier
   in numbered rounds, give a recommended answer and tradeoff for every question,
   wait for the developer's answers, and recompute the next frontier. Decisions
   belong to the developer; do not silently answer them. Finish by summarizing
   the decisions and require explicit confirmation of shared understanding.
4. **Set scope.** Restate the confirmed outcome, constraints, non-goals, and
   complexity: `small`, `standard`, or `cross-repo`. Record the interview as
   numbered decisions (`D-1`, `D-2`, ...). An unresolved decision makes the plan
   `NEEDS_DECISION`.
5. **Capture provenance.** Record every inspected repository and its full commit
   SHA. The plan becomes `STALE` when an affected repository moves before
   implementation.
6. **Build the current-state model.** Locate entry points, implementations,
   callers, configurations, tests, generated artifacts, docs, and release edges.
   Cite each important fact as `repo/path:line` or graph provenance.
7. **Apply the change-kind gate.**
   - Bugfix: establish reproduction conditions, observed versus expected result,
     failure mechanism, evidence-backed root cause, and a regression test that
     fails before the fix.
   - Feature: establish use cases, the verified integration seam, a sibling
     convention, material alternatives, and compatibility implications.
8. **Specify the desired state.** Write implementation-independent invariants and
   numbered acceptance criteria (`AC-1`, `AC-2`, ...), including error and boundary
   behavior.
9. **Map impact.** Address API/contracts, configuration/schema, runtime selection,
   callers, tests, docs, packaging/release, compatibility/migration, security,
   performance, and observability. Use an evidence-backed `N/A` where irrelevant.
10. **Draft test-first implementation steps.** Start with the failing behavioral
   test when practical. Every step must name a repository, file, symbol, exact
   behavior change, convention to follow, dependencies, acceptance criteria,
   test IDs, and verification command. Do not write "relevant files", "as
   needed", or another discovery placeholder.
11. **Build traceability.** Map every acceptance criterion to evidence,
   implementation steps, tests, and final verification. Include focused and full
   repository commands from repository documentation.
12. **Apply the minimality gate.** Use Ponytail when available. Otherwise test
    the proposal in order: is the change needed, can existing code solve it, can
    a platform feature solve it, can an installed dependency solve it, and what
    is the smallest complete diff? Record rejected scope. Never cut required
    validation, error handling, security, compatibility, tests, or release work.
13. **Review independently.** Delegate the finished draft, raw request, Know QaaS
    brief, and developer decisions to
    `qaas-plan-reviewer`. Do not provide private planner conclusions. Resolve all
    critical and major findings, record their dispositions, and request another
    review after material changes.
14. **Request developer approval.** After reviewer `APPROVE`, increment and
    present the complete plan revision as `AWAITING_APPROVAL`. Ask the developer
    to explicitly approve that revision or request changes. A reviewer cannot
    answer this gate. Any material revision resets approval to pending and must
    be reviewed again.
15. **Gate the result.** Emit exactly one status:
    - `AWAITING_APPROVAL`: technical review passed and the current revision is
      waiting for the developer's explicit decision.
    - `APPROVED`: the developer explicitly approved the same revision after
      technical review, all evidence and traceability exist, no implementation-
      changing decision remains, and inspected commits still match.
    - `NEEDS_DECISION`: a user/product/architecture choice changes the plan.
    - `BLOCKED`: required repository evidence, reproduction, root cause, or
      integration seam is unavailable.
    - `STALE`: an inspected repository changed after review; revalidate only the
      affected evidence and steps.

## Output contract

Read [references/plan-template.md](references/plan-template.md) and follow it.
For independent review, use
[references/review-rubric.md](references/review-rubric.md).

Return the complete Markdown plan in the conversation by default. Save it only
when the user requests a persistent artifact; never place planning artifacts in a
QaaS source repository merely for convenience.

Before presenting a saved plan for approval or marking it `APPROVED`, run:

```bash
python3 <skill-directory>/scripts/validate_plan.py <plan.md>
```

For a conversation-only plan, apply the same checks manually. The validator is a
structural gate; reviewer approval supplies the technical gate; explicit
developer approval supplies the implementation authorization.

## Done when

The plan carries the Know QaaS Context Brief forward, distinguishes
fact/inference/assumption/decision, specifies current and desired state, cites
live evidence, maps acceptance criteria through tests and implementation, covers
cross-repo and release effects, records repository commits, and carries an
independent verdict, and explicit developer approval state for the current plan
revision. No production change has been made during planning.

## Failure modes

- Producing a generic checklist that forces the implementer to rediscover files,
  symbols, or architecture.
- Starting detailed planning without first understanding the QaaS ecosystem or
  replacing the Know QaaS Context Brief with a one-line repository route.
- Calling a bug hypothesis the root cause without reproduction or source
  evidence.
- Designing a feature before locating its actual integration seam and sibling
  conventions.
- Treating knowledge-graph output as sufficient code-level evidence.
- Approving a plan with unresolved decisions, placeholders, missing tests, or
  stale repository commits.
- Asking the developer to discover codebase facts instead of asking only for
  product, scope, compatibility, and architecture decisions.
- Starting implementation after reviewer approval but before the developer
  explicitly approves the same plan revision.
- Letting a Ponytail minimality pass remove requested behavior or required
  correctness, safety, tests, compatibility, or release work.
- Invoking generic commands, installing dependencies, or changing hooks/settings
  owned by another plugin.
