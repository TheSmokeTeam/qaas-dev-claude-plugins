# qaas-dev-claude-plugins

A Claude Code plugin (+ portable `AGENTS.md`) that makes any AI agent productive
at **building the QaaS platform** — the [TheSmokeTeam](https://github.com/TheSmokeTeam)
C#/.NET monorepo. It owns the cross-repo seams (repo map, framework dependency
graph, release ripple, the Type A vs Type B extension distinction) and delegates
in-repo detail to each repo's own `CLAUDE.md`.

> Distinct from `eldarush/qaas-copilot` (which is for *using* QaaS to author
> tests). This plugin is for *developing the platform itself*.

## Install (Claude Code)

```text
/plugin marketplace add TheSmokeTeam/qaas-dev-claude-plugins
/plugin install qaas-platform-dev@qaas-dev-claude-plugins
```

## What you get

| Surface | Purpose |
|---|---|
| `qaas-platform-overview` (always-on skill) | Repo map, dependency graph, release ripple, repo router, Type A/B decision gate. |
| `add-framework-hook` skill | Add a Type A reflection hook (assertion/generator/probe/processor → `Common.*`). |
| `extend-framework-core` skill | Add a Type B compiled-core member (protocol/serializer/policy → `QaaS.Framework`). |
| `release-and-mirror` skill | The PackageMirror pipeline + source-repo CI contract. |
| `find-qaas-knowledge` skill | Docs-or-silence knowledge router. |
| `/qaas-where <task>` | Route a task to the right repo + skill. |
| `/qaas-release [<repo> <version>]` | Walk the release/mirror flow. |

## Other AI agents

Non-Claude-Code agents can ingest [`AGENTS.md`](./AGENTS.md), generated from the
skills. Regenerate after editing any skill:

```bash
./scripts/build-agents-md.sh
```

## Development

```bash
./scripts/validate-plugin.sh      # manifests, frontmatter, URL liveness (OFFLINE=1 to skip URLs)
./scripts/build-agents-md.sh      # regenerate AGENTS.md
```

CI runs both on every push (`.github/workflows/validate.yml`).
