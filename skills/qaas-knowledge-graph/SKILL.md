---
name: qaas-knowledge-graph
description: >-
  Query the CI-generated QaaS ecosystem Graphify graph as a source of evidence
  for QaaS codebase architecture, dependencies, call flows, ownership, impact,
  paths, and relationships. Use directly for those questions and whenever
  find-qaas-knowledge needs source-graph evidence alongside repository or live
  documentation. Synchronizes a read-only local cache from
  TheSmokeTeam/qaas-graph main and queries its existing graphify-out/graph.json.
---

# Query the QaaS Knowledge Graph

Use the committed graph from `TheSmokeTeam/qaas-graph` as the only graph source.
Never build a graph from the open repository.

## Query workflow

1. Select BFS for broad architecture and relationship questions. Select `--dfs`
   only when the user asks to trace a chain or flow.
2. Run the bundled wrapper from the user's current workspace:

   ```bash
   python3 <skill-directory>/scripts/qaas_graph.py query \
     --workspace "$PWD" \
     --question "<question>" \
     --budget 2000
   ```

   Add `--dfs` for a trace. Pass a different absolute directory to `--workspace`
   only when the opened workspace cannot be inferred from the current directory.
3. Treat a freshness warning as part of the answer: the cached graph was valid,
   but GitHub could not be checked. Treat any other wrapper error as blocking.
4. Answer only from the returned nodes and edges. Cite concrete evidence as
   `repo/source_file:source_location`. State when the graph does not contain
   enough evidence; never invent a relationship.

The wrapper places `qaas-graph` beside an opened Git repository, or directly
under a non-Git workspace root. It clones or synchronizes only the canonical
`main` branch. It updates only a clean cache that it previously marked as
managed, and never overwrites another checkout.

## Knowledge-source boundary

- Use the graph for observed code structure and relationships: architecture,
  dependencies, call flow, ownership, impact, and paths.
- Use in-tree repository docs and `docs.qaas.online` for normative contracts,
  configuration shapes, release procedures, and user-facing behavior.
- When graph and docs differ, report the difference and their freshness. Do not
  silently reinterpret one source as the other.

## Hard boundaries

- Never run Graphify `extract`, `update`, `cluster-only`, `add`, `watch`, or an
  export command for this workflow.
- Never run `save-result` or `reflect`; do not add memory, vocabulary, cache, or
  learning files to the canonical clone.
- Never scan local QaaS repositories or create `graphify-out` in them.
- Never edit, regenerate, recluster, enrich, or directly write the cached graph.
- Do not install Graphify automatically. If the wrapper reports it missing,
  show the pinned requirement path it provides and request permission before
  changing the machine's toolchain.
