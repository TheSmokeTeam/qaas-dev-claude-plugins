# qaas-dev-claude-plugins

A Claude Code plugin (+ portable `AGENTS.md`) that makes any AI agent productive
at **building the QaaS platform** — the [TheSmokeTeam](https://github.com/TheSmokeTeam)
C#/.NET monorepo. It owns the cross-repo seams (repo map, framework dependency
graph, release ripple, the Type A vs Type B extension distinction), prepares an
independently reviewed exact plan before feature or bugfix work, and delegates
in-repo detail to each repo's own `CLAUDE.md`.

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
| `qaas-platform-overview` (always-on skill) | Repo map, dependency graph, release ripple, repo router, Type A/B decision gate. |
| `plan-qaas-change` skill | Strict SDD: current/desired state, verified evidence, exact test-first steps, independent review, and stale-plan detection. |
| `add-framework-hook` skill | Add a Type A reflection hook (assertion/generator/probe/processor → `Common.*`). |
| `extend-framework-core` skill | Add a Type B compiled-core member (protocol/serializer/policy → `QaaS.Framework`). |
| `release-and-mirror` skill | The PackageMirror pipeline + source-repo CI contract. |
| `qaas-knowledge-graph` skill | Read-only queries against the canonical QaaS source graph for architecture and relationships. |
| `find-qaas-knowledge` skill | Evidence router across repo docs, live docs, the knowledge graph, and cross-repo skills. |
| `qaas-change-planner` (subagent) | Read-only source investigation and first draft of a QaaS Change Specification and Implementation Plan. |
| `qaas-plan-reviewer` (subagent) | Independent read-only plan review for evidence, architecture, traceability, exactness, and freshness. |
| `qaas-verifier` (subagent) | Independent read-only verification that a change builds/tests green, incl. framework blast radius. |
| `/qaas-where <task>` | Route a task to the right repo + skill. |
| `/qaas-plan <request>` | Prepare and review an exact plan without editing production code. |
| `/qaas-release [<repo> <version>]` | Walk the release/mirror flow. |

## Feature and bugfix flow

1. **Know QaaS:** establish repository ownership, Type A/Type B classification,
   live documentation, graph relationships, and release ripple.
2. **Specify and plan:** model current and desired state, define acceptance
   criteria, map impact, and write exact test-first steps.
3. **Review:** independently verify paths, symbols, tests, dependencies, and
   inspected commits. Implementation starts only from `APPROVED`; stop on
   `NEEDS_DECISION`, `BLOCKED`, or `STALE`.
4. **Implement and verify:** follow the approved plan and finish with the
   read-only `qaas-verifier`.

The QaaS commands and agents are namespaced and do not require, configure, or
replace other developer plugins.

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

CI runs both on every push (`.github/workflows/validate.yml`).
