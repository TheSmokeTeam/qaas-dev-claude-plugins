---
name: qaas-platform-overview
description: >-
  Build the mandatory Know QaaS Context Brief before any QaaS platform task.
  Use first for QaaS architecture, planning, implementation, verification,
  release, ownership, dependency, or repository questions in TheSmokeTeam. It
  establishes ecosystem scope, Type A versus Type B ownership, release ripple,
  authoritative sources, and the next workflow without inventing in-repository
  details.
---

# Know QaaS

Build the ecosystem understanding needed for the request, then route it. This
stage acquires context; it does not produce an implementation plan, authorize an
edit, or repeat details owned by a repository.

Read [references/ecosystem-map.md](references/ecosystem-map.md) before producing
the brief. Verify any current repository member, symbol, package, command, or
selection mechanism against live repository evidence.

## Evidence rules

1. Read the owning repository's `CLAUDE.md` before source-level work. Read the
   relevant `project_specs.md` next. Use `README.md` only when no `CLAUDE.md`
   exists.
2. Use `find-qaas-knowledge` to locate authoritative sources and
   `qaas-knowledge-graph` for cross-repository relationships.
3. Treat this plugin as the authority for stable cross-repository architecture,
   not for volatile file, symbol, package-version, or family-member inventories.
4. State missing evidence explicitly. Never replace it with memory.

## Output: Know QaaS Context Brief

Keep the brief proportional to the request and include every field:

- **Platform scope:** distinguish platform development from authoring tests with
  QaaS.
- **Ecosystem location:** identify the capability, likely owner, and consumers
  at repository level.
- **Dependency position:** explain the relevant upstream and downstream edges.
- **Extension model:** classify `type-a`, `type-b`, `existing-behavior`,
  `not-applicable`, or `undetermined`, with the ownership reason.
- **Release ripple:** summarize likely package, mirror, schema, documentation,
  and consumer effects, or why they do not apply.
- **Authority map:** name the repository instructions, source areas, live docs,
  and graph evidence the next stage must inspect.
- **Known unknowns:** list unverified ecosystem facts and decisions.

Pass the brief intact to the next stage. Refresh it when scope, classification,
or repository evidence changes.

## Route after understanding

| Request | Next owner |
|---|---|
| Locate or explain QaaS knowledge | `find-qaas-knowledge` |
| Prepare a feature, bugfix, or refactor plan | `plan-qaas-change` |
| Deliver a feature, bugfix, or refactor end to end | `develop-qaas-change` |
| Execute an already approved plan | `implement-qaas-change` |
| Add a reflection-discovered hook | `add-framework-hook`, through the implementation owner |
| Extend compiled framework core | `extend-framework-core`, through the implementation owner |
| Release or mirror packages | `release-and-mirror` |

Knowledge-only requests stop after answering from evidence. Plan-only requests
stop after the developer's approval decision. Implementation requests pause
after independent review and resume only when the developer explicitly approves
the reviewed plan.

An `undetermined` extension model is a valid brief result, not permission to
guess and not a reason to bypass the next owner. Do not select a Type A or Type B
overlay while it remains undetermined. Pass the missing evidence forward; the
planning or implementation owner stops and names the missing evidence if it
cannot resolve the classification safely.

## Done when

The brief gives the next stage a correct ecosystem mental model, identifies the
right evidence and workflow, and labels every unknown instead of guessing it.

## Stop when

- The request is about using QaaS to author tests rather than developing the
  platform.
- A requested code-level claim would depend on unavailable evidence or stale
  training memory. Return the brief with `undetermined` and explicit known
  unknowns instead of making that claim.
