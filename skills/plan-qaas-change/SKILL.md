---
name: plan-qaas-change
description: >-
  Research a QaaS platform feature, bugfix, or refactor, interview the developer,
  and prepare a short evidence-backed implementation plan for independent
  review and explicit approval before code changes.
---

# Plan a QaaS Change

Own planning from a completed Know QaaS brief through presentation of the
reviewed plan and the developer's approval decision. Do not implement the change.

Read [references/developer-interview.md](references/developer-interview.md) before
interviewing the developer.

## Boundaries

- Require a complete Know QaaS Context Brief from `qaas-platform-overview`.
- Read every owning repository's `CLAUDE.md` and relevant `project_specs.md`
  before source-level conclusions.
- Use `qaas-knowledge-graph` for cross-repository relationships, then verify
  implementation facts in source.
- Never invent a repository, file, symbol, signature, command, dependency,
  configuration key, root cause, or integration seam.
- Keep planning read-only. Technical review and developer approval remain
  separate gates.

## Workflow

1. **Research and design.** Inspect instructions, source, callers, tests, sibling
   conventions, generated surfaces, graph relationships, and release edges.
   Prove the bug cause or feature/refactor integration seam before asking the
   developer anything the codebase can answer.
2. **Interview when decisions remain.** For a new or materially replanned change,
   follow `developer-interview.md`, which owns the required Grilling provider
   dispatch and failure behavior. Do not interview for knowledge-only, status,
   release-only, or exact approved-plan execution routes.
3. **Confirm shared understanding.** Summarize the requested outcome, constraints,
   confirmed decisions, and non-goals. Wait for confirmation when a developer-owned
   choice changed or remains ambiguous.
4. **Create the plan.** Invoke `ponytail:ponytail` with `full` before deciding
   plan scope or drafting. After success emit
   `Provider: ponytail:ponytail — SUCCEEDED`. On failure emit
   `BLOCKED_PROVIDER: ponytail:ponytail — cause` and stop without drafting,
   review, or other downstream work; there is no internal fallback. Then create
   the short plan directly. It must proportionally cover:
   - goal and scope;
   - confirmed decisions and non-goals;
   - source evidence and design;
   - affected repositories and files;
   - ordered test-first steps;
   - verification commands; and
   - release impact.
5. **Review independently.** Give the raw request, brief, confirmed decisions,
   and complete plan to `qaas-plan-reviewer`. Resolve every material finding and
   repeat the review when a correction changes implementation scope or behavior.
6. **Ask for approval.** Present the reviewed plan unchanged and ask the developer
   to approve it explicitly or request changes. Reviewer readiness never
   authorizes implementation. Silence and earlier approval of an idea are not
   approval of the reviewed plan.

## Plan format

Use ordinary Markdown proportional to the change. Do not require frontmatter,
fixed headings, lifecycle metadata, history tables, hashes, or a prescribed
number of sections. Exact paths and symbols are required only when source
evidence proves them and they help the implementer act without rediscovery.

If required evidence is unavailable, say what is missing and stop. Requested
changes return to plan creation and review; update the plan, review it again,
and ask for explicit developer approval again.

## Done when

Explicit developer approval is the successful planning outcome. The plan must
be short, evidence-backed, test-first, independently reviewed, and explicitly
approved before implementation. Planning itself never edits production files.
