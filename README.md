# qaas-dev-claude-plugins

A Claude Code plugin (+ portable `AGENTS.md`) that makes any AI agent productive
at **building the QaaS platform** — the [TheSmokeTeam](https://github.com/TheSmokeTeam)
C#/.NET monorepo. It owns the cross-repo seams (repo map, framework dependency
graph, release ripple, the Type A vs Type B extension distinction), prepares an
exact plan through a developer interview, independent technical review, and
explicit developer approval before feature or bugfix work, and delegates in-repo
detail to each repo's own `CLAUDE.md`.

> This plugin is for *developing the QaaS platform itself* — not for *using* QaaS
> to author tests, which is a separate end-user concern.

## Install (Claude Code)

```text
/plugin marketplace add TheSmokeTeam/qaas-dev-claude-plugins
/plugin install qaas-platform-dev@qaas-dev-claude-plugins
```

## What you get

| Surface | Purpose |
|---|---|
| `qaas-platform-overview` (always-on skill) | Mandatory Know QaaS stage: builds the agent's ecosystem mental model before routing or planning. |
| `plan-qaas-change` skill | Strict SDD: developer interview, current/desired state, exact test-first steps, independent review, explicit approval, and stale-plan detection. |
| `add-framework-hook` skill | Add a Type A reflection hook (assertion/generator/probe/processor → `Common.*`). |
| `extend-framework-core` skill | Add a Type B compiled-core member (protocol/serializer/policy → `QaaS.Framework`). |
| `release-and-mirror` skill | The PackageMirror pipeline + source-repo CI contract. |
| `qaas-knowledge-graph` skill | Read-only queries against the canonical QaaS source graph for architecture and relationships. |
| `find-qaas-knowledge` skill | Evidence router across repo docs, live docs, the knowledge graph, and cross-repo skills. |
| `qaas-change-planner` (subagent) | Read-only source investigation and first draft of a QaaS Change Specification and Implementation Plan. |
| `qaas-plan-reviewer` (subagent) | Independent read-only plan review for evidence, architecture, traceability, exactness, and freshness. |
| `qaas-verifier` (subagent) | Independent read-only verification that a change builds/tests green, incl. framework blast radius. |
| `/qaas-where <task>` | Route a task to the right repo + skill. |
| `/qaas-plan <request>` | Interview the developer, prepare and review an exact plan, and request approval without editing production code. |
| `/qaas-release [<repo> <version>]` | Walk the release/mirror flow. |

## Feature and bugfix flow

1. **Know QaaS:** first build a concise ecosystem context brief—platform scope,
   owning and consuming repositories, dependency position, Type A/Type B model,
   release ripple, authoritative sources, and known unknowns. This step helps the
   agent understand QaaS; it does not plan or edit the requested change.
2. **Route:** select the correct repository and downstream skill from that
   ecosystem understanding.
3. **Interview the developer:** research facts from code and ask the developer
   only for decisions. Walk the decision tree with recommendations until the
   developer confirms shared understanding.
4. **Specify and plan:** model current and desired state, apply the smallest-
   complete-change gate, define acceptance criteria, map impact, and write exact
   test-first steps.
5. **Review:** independently verify decisions, paths, symbols, tests,
   dependencies, minimality, and inspected commits.
6. **Developer approval:** present the reviewed plan as `AWAITING_APPROVAL`.
   Implementation remains blocked until the developer explicitly approves that
   exact revision. Material changes reset approval.
7. **Implement and verify:** follow the approved plan and finish with the
   read-only `qaas-verifier`.

The QaaS commands and agents are namespaced and do not require, configure, or
replace other developer plugins.

## Ponytail and Grill Me compatibility

- When Matt Pocock's model-invoked `grilling` skill is available, the planning
  stage uses it for the developer interview. Without it, the QaaS skill runs the
  same facts-versus-decisions and explicit-confirmation gates itself.
- When Dietrich Gebert's Ponytail is installed or active, its current minimality
  level is applied while selecting and reviewing the solution. Without it, the
  QaaS skill uses its built-in smallest-complete-change check.
- Neither plugin is installed, configured, or required by this plugin. Ponytail
  cannot remove requested scope, correctness, safety, tests, compatibility, or
  release work; Grill Me cannot grant developer approval on the user's behalf.

Interoperability targets the MIT-licensed
[Grill Me/grilling skills](https://github.com/mattpocock/skills) and
[Ponytail](https://github.com/DietrichGebert/ponytail); their code is not
vendored into this plugin.

## Other AI agents

Non-Claude-Code agents can ingest [`AGENTS.md`](./AGENTS.md), generated from the
skills. Regenerate after editing any skill:

```bash
./scripts/build-agents-md.sh
```

## Development

```bash
./scripts/validate-plugin.sh       # manifests, frontmatter, plan-validator tests, URLs
./scripts/build-agents-md.sh       # regenerate AGENTS.md
claude plugin validate .           # Claude Code plugin schema validation
claude plugin eval . --scaffold    # behavioral evals (model usage/cost applies)
```

Structural validation runs on every push (`.github/workflows/validate.yml`). The
model-based eval suite is manually dispatched because it requires explicit model
IDs, credentials, and a cost budget (`.github/workflows/plugin-evals.yml`).
