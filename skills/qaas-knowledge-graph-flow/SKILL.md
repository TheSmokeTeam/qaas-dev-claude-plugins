---
name: qaas-knowledge-graph-flow
description: >-
  Guide QaaS work with the ecosystem knowledge graph: discover and query the
  committed code and evaluated dependency graphs, verify graph findings in
  source/docs, audit provenance and freshness, regenerate local previews, safely
  synchronize registered repositories, and distinguish local, canonical, and
  public graph state. Use for QaaS architecture, symbols, paths, dependencies,
  graph availability/freshness, graph tooling, or graph publication.
---

# QaaS Knowledge Graph Flow

Use `qaas-graph` as a navigation and verification aid throughout QaaS work. Treat
source repositories as inputs, committed local artifacts as a baseline, locally
regenerated artifacts as a preview, merged artifacts on the canonical branch as
canonical, and a successful Pages deployment as public.

## Establish the live contract

Locate `qaas-graph`. Before relying on commands, repository names, branches, or
versions, read its:

- `README.md`
- `repositories.yml`
- `requirements.txt`
- `scripts/generate.sh`
- `scripts/extract_dependencies.py`
- `.gitignore` and `.graphifyignore`
- relevant `.github/workflows/` files

Derive paths, registered inputs, pinned versions, CI triggers, and deployment
behavior from those files. Live files override examples in this skill. Read
[references/workspace-and-commands.md](references/workspace-and-commands.md) when
setting up a workspace or selecting audit, query, generation, or publication
commands.

Never edit generated JSON, HTML, Mermaid, SVG, or README graph blocks manually.
Change source, registry, or generator code and regenerate.

## Discover an available graph

Search the current directory, its ancestors, and their immediate workspace roots
for a `qaas-graph` directory containing `repositories.yml`. Do not assume a fixed
absolute path.

If `qaas-graph` is present:

1. Inspect its branch, upstream, HEAD, and dirtiness.
2. Confirm whether `graphify-out/graph.json` and `graphs/repositories.json` exist.
3. Use those committed artifacts immediately for exploration; do not rebuild,
   fetch, or pull merely because a question was asked.
4. Resolve registered source paths relative to `repositories.yml`.
5. Label graph provenance precisely: committed baseline or local preview.

If `qaas-graph` is absent:

1. Continue with source and documentation when possible.
2. State that graph evidence is unavailable.
3. Clone `qaas-graph` only when the user authorizes obtaining it.
4. After cloning, read the live contract before cloning any registered inputs.

Any generation mode requires all registered source repositories to exist. Never
replace an existing directory. Verify every existing input is a Git repository
whose `origin` matches the registry URL; equivalent GitHub SSH and HTTPS forms
are acceptable.

## Query before broad source search

Choose the graph view that matches the question:

| Question | Evidence |
| --- | --- |
| Code symbol, implementation, caller, path, or architecture | `graphify-out/graph.json` via Graphify query tools |
| Repository/project/package ownership or dependency | `graphs/repositories.json` |
| Public YAML/configuration contract | `docs.qaas.online`, using the graph only to locate implementation |
| Prose-only behavior or team policy | In-tree `AGENTS.md`, `CLAUDE.md`, `project_specs.md`, or `README.md` |

Run code queries from `qaas-graph` so Graphify finds the committed graph:

```bash
graphify query "<architecture question>"
graphify explain "<exact symbol>"
graphify path "<source symbol>" "<target symbol>"
```

Start with exact repository, project, class, interface, or method names. If a
broad query selects noisy start nodes, narrow it with identifiers found in graph
output or source. A noisy traversal is not evidence that no relationship exists.

For every implementation claim:

1. Record the graph artifact and cited `source_file` / `source_location`.
2. Open that source in the registered repository.
3. Read applicable repo-local `AGENTS.md` and `CLAUDE.md`, plus the relevant
   `project_specs.md`; use `README.md` as fallback/context.
4. Verify user-facing configuration against `docs.qaas.online`.
5. Report graph provenance and any missing evidence.

The code graph is code-only. It cannot establish facts that live only in prose,
issues, or generated QaaS docs. The evaluated dependency graph can establish the
relationships it records, but freshness is bounded by its recorded source commits.

## Audit and synchronize only at boundaries

Use local status for provenance. Fetch before claiming a checkout is current
relative to a remote. Pull only when deliberately adopting upstream work.

```bash
python3 /path/to/this-skill/scripts/repo_sync.py \
  status --graph-repo /path/to/qaas-graph

python3 /path/to/this-skill/scripts/repo_sync.py \
  status --fetch --graph-repo /path/to/qaas-graph

python3 /path/to/this-skill/scripts/repo_sync.py \
  sync --graph-repo /path/to/qaas-graph
```

The helper fetches and fast-forwards only clean, behind-only branches. It reports
dirty, ahead, diverged, detached, upstream-less, missing, invalid,
remote-mismatched, and fetch-failed repositories without rewriting them. Never
bypass a block with stash, clean, reset, rebase, merge, remote replacement,
deletion, or force-push.

Synchronize when:

- starting work that explicitly requires latest upstream;
- deliberately accepting teammate changes;
- integrating before publication;
- updating graph tooling itself; or
- obtaining a newly merged canonical graph locally.

Do not pull between ordinary feature edits or before a read-only graph query.

## Regenerate only for changed local inputs

Use the smallest truthful preview:

| Change | Command |
| --- | --- |
| Classes, methods, symbols, or code relationships | `scripts/generate.sh --graphify-only` |
| Project/package references, target frameworks, or MSBuild evaluation | `scripts/generate.sh --dependencies-only` |
| Both views changed, or final verification | `scripts/generate.sh` |
| Graphify cache is demonstrably stale | Add `--force` to a Graphify-producing run |

Use `scripts/generate.sh` for normal generation. Run
`scripts/extract_dependencies.py` directly only to list resolved inputs,
debug/test dependency extraction, or supply custom paths.

Before generation, record each input's branch, HEAD, dirtiness, and fetch status.
After generation, report the exact command, changed artifacts, compact diff, and
source state represented. CI cannot reproduce uncommitted changes, unpushed
commits, or refs it does not check out. A failed full run may leave partial
artifacts; do not call that preview complete.

## Publish through the canonical flow

For feature work:

```text
local source edit -> source tests -> local graph preview -> source commit/PR
-> source reaches the ref consumed by graph CI -> graph update workflow
-> automation artifact PR -> merge -> Pages deployment
```

Do not push a local preview as a substitute for graph CI. Trigger workflows,
push, open/merge PRs, or change published state only when requested.

When changing `repositories.yml`, generators, tests, requirements, documentation,
or workflows, use a normal human PR. Keep the registry and any explicit CI
checkout list aligned, test and generate locally, merge the tooling change first,
then allow graph CI to propose generated artifacts.

## Report state precisely

1. **Committed baseline**: generated artifacts checked out locally.
2. **Local preview**: artifacts regenerated from stated local source commits and
   possibly uncommitted changes.
3. **Automation PR**: CI proposal; canonical and public state are unchanged.
4. **Canonical graph**: generated artifacts merged to the canonical branch.
5. **Public graph**: canonical interactive HTML successfully deployed.

Report source commits, dirtiness, whether remotes were fetched, query/generation
evidence, and remaining blockers. Do not infer freshness from timestamps.

## Done when

For knowledge questions, query the relevant available graph, verify findings in
source/docs, and report provenance. For graph changes, regenerate from recorded
inputs, run graph-repo tests, inspect the artifact diff, and name the furthest
publication state actually reached.

## Guardrails

- Treat only `repositories.yml` entries as graph inputs.
- Keep generated outputs tracked while excluding caches and generated graph data
  from Graphify's own scan.
- Do not claim exact reproducibility without identical source commits, ignore
  rules, pinned Graphify version, and relevant toolchain.
- Treat `Community N` labels as unnamed clusters, not missing extraction.
- Never use a graph result to bypass repo-local instructions or authoritative docs.
