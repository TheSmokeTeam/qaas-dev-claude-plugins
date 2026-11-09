---
name: plan-qaas-change
description: >-
  Interview the developer and prepare an exact evidence-backed implementation
  plan for a QaaS platform feature, bugfix, or refactor before code changes.
  Use when the developer explicitly asks for a plan, design, implementation plan,
  or "how should we implement" answer without implementation, or when
  develop-qaas-change enters its planning stage. Produces a frozen plan revision
  with verified source baselines, test-first steps, independent technical review,
  and explicit developer approval state.
---

# Plan a QaaS Change

Own the lifecycle from a completed Know QaaS brief through the developer's plan
approval decision. Do not implement the requested production change.

## Read before planning

- [references/developer-interview.md](references/developer-interview.md) for the
  facts-versus-decisions interview and required provider dispatch.
- [references/plan-template.md](references/plan-template.md) for the output
  schema.
- [references/review-rubric.md](references/review-rubric.md) when delegating
  independent review.

## Boundaries

- Require a complete Know QaaS Context Brief from `qaas-platform-overview`.
- Read every owning repository's `CLAUDE.md` and relevant `project_specs.md`
  before source-level conclusions.
- Use `qaas-knowledge-graph` for cross-repository relationships, then verify
  implementation facts in source.
- Never invent a repository, file, symbol, signature, command, dependency,
  configuration key, root cause, or integration seam.
- Do not edit source, tests, configuration, manifests, generated files, or Git
  state while planning.
- Technical review and developer approval are separate gates.

## Workflow

1. **Validate context.** Refresh the Know QaaS brief when the request, ownership,
   classification, or evidence changed.
2. **Research facts.** Inspect instructions, source, callers, tests, sibling
   conventions, generated surfaces, graph relationships, and release edges
   before asking the developer anything the codebase can answer.
3. **Interview the developer on interview-required routes.** For a new or
   materially replanned feature, bugfix, or refactor, follow
   `developer-interview.md` and explicitly invoke
   `mattpocock-skills:grilling`. Emit
   `Provider: mattpocock-skills:grilling — SUCCEEDED` after success. On a
   post-load invocation failure emit
   `BLOCKED_PROVIDER: mattpocock-skills:grilling — cause` and stop before plan
   drafting or downstream delegation; there is no internal fallback. Record
   numbered decisions (`D-1`, `D-2`, ...) when material choices exist; otherwise
   record that research found no material developer-owned decision. Require
   explicit confirmation of shared understanding. Unresolved material decisions
   produce `NEEDS_DECISION`. Do not invoke Grilling for knowledge-only, status,
   release-only, or exact approved-plan execution routes.
4. **Capture repository baselines.** Run
   `${CLAUDE_PLUGIN_ROOT}/skills/plan-qaas-change/scripts/repo_snapshot.py` for
   every inspected checkout. Record its repository identity, full commit, and
   worktree fingerprint; do not pair a snapshot with a different repository name.
5. **Prove the current state.** For a bugfix, prove reproduction, observed versus
   expected behavior, failure mechanism, root cause, and regression-test seam.
   For a feature or refactor, prove use cases, integration seam, sibling
   convention, alternatives, and compatibility effects.
6. **Specify the desired state.** Define invariants and observable numbered
   acceptance criteria, including error and boundary behavior.
7. **Draft the smallest complete plan.** Delegate read-only source investigation
   and the first draft to `qaas-change-planner`. Require exact repositories,
   files, symbols, conventions, dependencies, test IDs, commands, release work,
   and traceability. Missing evidence produces `BLOCKED`.
8. **Freeze the revision.** Assign `plan_revision`, then compute `plan_digest`
   with the bundled validator before technical review. The substantive content,
   repository baselines, revision, and digest form one immutable review unit.
9. **Review independently.** Delegate the raw request, brief, developer decisions,
   and frozen plan to `qaas-plan-reviewer`. Resolve every critical and major
   finding. Any material correction creates the next revision and requires a
   fresh review.
10. **Present for developer approval.** When the reviewer approves revision N,
    record `review.reviewed_revision: N` and the matching `reviewed_digest`, set
    `AWAITING_APPROVAL`, and present that unchanged review unit. Do not increment
    after review.
11. **Record the developer decision.** Only explicit approval of revision N may
    set `APPROVED`, `developer_approval.approved_revision: N`, and the matching
    `approved_digest`. Record the developer message or trusted handoff reference.
    Requested changes return the plan to revision and review; silence is not
    approval.

## State contract

| Status | Meaning | May implement? |
|---|---|---|
| `DRAFT` | Research or drafting is in progress | No |
| `NEEDS_DECISION` | A developer-owned decision is unresolved | No |
| `BLOCKED` | Required evidence or access is unavailable | No |
| `AWAITING_APPROVAL` | Current revision passed review and awaits the developer | No |
| `APPROVED` | Reviewer and developer approved the same current revision | Yes, through `implement-qaas-change` |
| `STALE` | A captured repository baseline changed | No |

For `AWAITING_APPROVAL` and `APPROVED`:

```text
review.reviewed_revision == plan_revision
review.reviewed_digest == plan_digest
```

For `APPROVED` only:

```text
developer_approval.approved_revision == plan_revision
developer_approval.approved_digest == plan_digest
```

A material edit or repository-baseline replacement increments `plan_revision`,
recomputes `plan_digest`, resets review to `PENDING`, and resets developer
approval to `PENDING`. A detected baseline change sets `STALE` until a new
revision is reviewed and approved.

## Output and validation

Return the complete Markdown plan in the conversation. Save it only when the
developer requests a persistent artifact, and never save it inside a QaaS source
repository merely for convenience.

Validate a saved plan or stdin before presenting it for approval:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/plan-qaas-change/scripts/validate_plan.py" <plan.md-or->
python3 "${CLAUDE_PLUGIN_ROOT}/skills/plan-qaas-change/scripts/validate_plan.py" --print-digest <plan.md-or->
```

The validator supplies the structural gate. `qaas-plan-reviewer` supplies the
technical gate. The developer supplies implementation authorization.

## Done when

The plan is evidence-backed, test-first, traceable, minimal, tied to exact source
baselines, independently reviewed at its current revision, and records the
developer's decision without any production edit during planning.
