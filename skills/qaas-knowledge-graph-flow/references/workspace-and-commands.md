# Workspace and command reference

Use this reference after reading the live `qaas-graph` contract. Repository
configuration can change; live files override examples here.

## Contents

- Workspace resolution
- Repository audit and synchronization
- Query commands
- Generation commands
- Validation and publication
- State interpretation

## Workspace resolution

All source paths are relative to the directory containing `repositories.yml`.
Resolve them instead of assuming a fixed workspace shape:

```bash
cd /path/to/qaas-graph
python3 scripts/extract_dependencies.py \
  --registry repositories.yml \
  --list-repositories
```

For every resolved path, verify local provenance:

```bash
git -C /resolved/repository status --short --branch
git -C /resolved/repository remote get-url origin
git -C /resolved/repository rev-parse HEAD
```

Compare the origin with the registry URL. Treat
`git@github.com:ORG/REPO.git` and `https://github.com/ORG/REPO.git` as equivalent.

## Repository audit and synchronization

Resolve the helper path from the installed skill directory:

```bash
# Local-only inspection; no network operation
python3 /path/to/skill/scripts/repo_sync.py \
  status --graph-repo /path/to/qaas-graph

# Fetch, then report upstream-relative state
python3 /path/to/skill/scripts/repo_sync.py \
  status --fetch --graph-repo /path/to/qaas-graph

# Fetch and fast-forward only repositories that are safe
python3 /path/to/skill/scripts/repo_sync.py \
  sync --graph-repo /path/to/qaas-graph
```

Use local-only status for provenance snapshots. Use `--fetch` before claiming
remote freshness. Use `sync` only when intentionally moving checkouts to latest
upstream.

### Choose fetch, pull, sync, or regenerate

| Question | Action |
| --- | --- |
| Is the remote newer? | Fetch, then inspect; do not pull yet |
| Adopt newest commits in one clean repository | `git pull --ff-only` in that repository |
| Move the registered workspace to current upstream | Run helper `sync` and inspect every row |
| Reflect changed local code in the graph | Regenerate the affected local view; do not pull |
| Obtain a merged canonical graph | Fast-forward `qaas-graph`; do not regenerate |
| Publish a local feature to the shared graph | Publish source first, then let graph CI propose artifacts |

For one repository:

```bash
git -C /path/to/repository fetch --prune
git -C /path/to/repository status --short --branch
git -C /path/to/repository rev-list --left-right --count HEAD...@{upstream}
git -C /path/to/repository pull --ff-only
```

Run the final pull only after confirming the tree is clean, HEAD is attached, an
upstream exists, and the branch is behind with no local-only commits. If it is
ahead or diverged, follow that repository's integration policy; do not improvise
a merge or rebase.

## Query commands

Run queries from `qaas-graph` so Graphify finds `graphify-out/graph.json`:

```bash
graphify query "Which component creates implementations of IGenerator by name?"
graphify explain "ByNameObjectCreator"
graphify path "YamlConfigurationBuilderExtension" "ExecutionBuilder"
```

- `query`: broad relationship/context traversal.
- `explain`: inspect one known graph node.
- `path`: find the shortest known connection between two named nodes.

Start with exact identifiers. If a broad query selects noisy start nodes, narrow
it with symbols discovered in source or prior graph output. Always open cited
source locations before making implementation claims.

For dependency questions, inspect `graphs/repositories.json`. Its main
collections are `repositories`, `projects`, `packages`, `edges`, and
`repository_dependencies`; repository nodes record the source commit used to
generate the artifact.

## Generation commands

Install the versions pinned by the graph repository when generation is requested
and the environment is missing them:

```bash
cd /path/to/qaas-graph
python3 -m pip install -r requirements.txt
```

Normal commands:

```bash
# Rebuild dependency and code views
scripts/generate.sh

# Evaluated MSBuild dependency artifacts and README graph block only
scripts/generate.sh --dependencies-only

# Per-repository code extraction, merge, and interactive HTML only
scripts/generate.sh --graphify-only

# Rescan code rather than using Graphify caches
scripts/generate.sh --graphify-only --force
```

Run full generation for final cross-view verification. A Graphify-only preview
can legitimately be newer than dependency artifacts until the final run.

### Script responsibilities

`scripts/generate.sh` is the normal entry point. It reads the registry, invokes
dependency extraction, extracts registered source repositories in code-only mode,
merges their graphs, and exports interactive HTML according to its flags.

Use `scripts/extract_dependencies.py` directly to list exact registered paths or
debug extraction. Do not point its `--readme` argument at a source README unless
replacing that file's marked graph block is intended.

The skill's `scripts/repo_sync.py` provides a consistent state table and
conservative fast-forward synchronization. It never clones, stashes, resets,
rebases, merges, edits remotes, or force-pushes.

## Validation and publication

When graph tooling or dependency extraction changes, run the live repository's
documented commands, typically:

```bash
python3 -m unittest discover -s tests -v
scripts/generate.sh
git diff -- README.md graphs graphify-out
```

Read the current workflow before relying on triggers. The canonical flow is:

```text
source feature reaches CI-consumed remote ref
  -> update workflow checks out sources and regenerates
  -> automation PR contains artifact diff
  -> reviewed PR merges to canonical branch
  -> Pages workflow deploys graph.html
```

Never collapse these steps into “the graph is updated.” Name the furthest state
that has actually succeeded.

## State interpretation

| Evidence | Accurate statement |
| --- | --- |
| Checked-out generated files only | Committed baseline is available locally |
| Local generation succeeded | Local preview represents the recorded local source state |
| CI opened/updated a PR | An automation proposal exists |
| Artifact PR merged | Canonical graph is updated |
| Pages deployment succeeded | Public interactive graph is updated |
