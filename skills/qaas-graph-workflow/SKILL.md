---
name: qaas-graph-workflow
description: Manage the QaaS graph lifecycle across local source inspection, safe repository synchronization, local preview generation, CI-generated graph pull requests, canonical merge, and GitHub Pages deployment. Use for setting up or querying qaas-graph, starting or finishing a feature with graph support, deciding when to pull, checking graph freshness or reproducibility, explaining unnamed communities, regenerating artifacts, changing registered inputs or graph tooling, and publishing the canonical or public graph.
---

# QaaS Graph Workflow

Treat registered QaaS source repositories as inputs, locally generated artifacts
as a disposable preview, artifacts committed on the canonical branch of
`qaas-graph` as canonical, and a successful Pages deployment as public.

`scripts/generate.sh` changes only local artifacts. Graph-update CI checks out
remote source refs, runs the generator, and proposes artifact changes through a
pull request. Never manually edit generated JSON, HTML, Mermaid, or SVG files.

## Read the live contract

Locate `qaas-graph`, then read `README.md`, `repositories.yml`,
`requirements.txt`, `scripts/generate.sh`, and relevant
`.github/workflows/` files. Derive repository inputs, branches, triggers,
schedule, automation branch, and Pages behavior from those files and live Git
state rather than this skill.

- Treat only entries in `repositories.yml` as graph inputs. Do not include
  `qaas-docs`, templates, or other siblings unless registered.
- Verify separately maintained CI checkout lists match the registry.
- Before changing a source repository, read its `CLAUDE.md`, or `README.md`
  when no `CLAUDE.md` exists.
- Read `.gitignore` and `.graphifyignore` when changing graph tooling:
  `.gitignore` controls Git tracking, while `.graphifyignore` controls
  Graphify scanning. Final graph artifacts must remain tracked; generated graph
  data must not index itself.

## Query before rebuilding

Use the committed graph to locate likely code:

```bash
cd /path/to/qaas-graph
graphify query "<architecture question>"
graphify explain "<symbol>"
graphify path "<source symbol>" "<target symbol>"
```

Verify conclusions in source. The code-only graph does not contain facts that
exist only in prose or `qaas-docs`.

## Synchronize only at boundaries

Do not pull between ordinary edits. Pull source repositories when starting from
latest upstream, deliberately accepting teammate changes, or integrating before
publication. Pull `qaas-graph` before the first regeneration when latest tooling
is wanted, after a canonical graph PR is merged when that version is wanted
locally, or when changing `qaas-graph` itself.

Resolve the bundled helper relative to this skill directory:

```bash
# Local state only
python3 /absolute/path/to/qaas-graph-workflow/scripts/repo_sync.py \
  status --graph-repo /path/to/qaas-graph

# Fetch before reporting remote-current state
python3 /absolute/path/to/qaas-graph-workflow/scripts/repo_sync.py \
  status --fetch --graph-repo /path/to/qaas-graph

# Explicitly fetch and fast-forward every safe repository
python3 /absolute/path/to/qaas-graph-workflow/scripts/repo_sync.py \
  sync --graph-repo /path/to/qaas-graph
```

`sync` fast-forwards only clean, behind-only branches. It preserves and reports
dirty, ahead, detached, upstream-less, diverged, missing, invalid, or fetch-failed
repositories. It is per-repository rather than transactional, so report every
result. Never bypass a block with stash, clean, reset, rebase, merge, remote
replacement, deletion, or force-push.

The helper reads registered names and paths, not expected remote URLs. During
setup or after path/remote changes, compare each local `origin` with the registry
URL, allowing equivalent SSH and HTTPS forms, and block mismatches.

If `qaas-graph` has dirty generated artifacts, do not pull over them. Ask whether
to keep the pinned local preview, preserve it with an authorized commit on a
temporary branch, or discard and regenerate it with destructive-action approval.

## Bootstrap a missing workspace

When `qaas-graph` is absent:

1. Clone `https://github.com/TheSmokeTeam/qaas-graph.git` into the workspace
   location implied by existing conventions; never clone merely because the
   plugin loaded.
2. Read its live contract.
3. For a committed-graph query, use the checked-in artifacts and clone only the
   owning source repository needed to verify the conclusion, if it is absent.
4. For any generation mode, clone every registered input using the registry URLs
   and paths; never replace an existing directory.
5. Install pinned requirements only when generation is requested and dependencies
   are missing.
6. Audit local state and report missing or unauthorized repositories as blockers.

## Run the feature workflow

### Start

1. Audit `qaas-graph` and the registered inputs relevant to the requested mode.
2. Synchronize once only if current upstream state is desired. An offline or
   pinned checkout is valid, but label it as such.
3. Query the committed graph, verify in source, and follow the target
   repository's instructions.

### Develop locally

Repeat without pulling:

```text
edit source -> run focused tests -> regenerate preview -> query/inspect -> edit again
```

Regenerate after meaningful structural changes or when updated navigation is
useful:

| Need | Command | Outputs |
| --- | --- | --- |
| Code or symbol changes | `scripts/generate.sh --graphify-only` | `graphify-out/graph.{json,html}` |
| Dependency/MSBuild view only | `scripts/generate.sh --dependencies-only` | `graphs/repositories.{json,mmd,svg}` and README graph |
| Cross-view change or final refresh | `scripts/generate.sh` | Both views |
| Plausibly stale Graphify cache | Add `--force` | Forces only Graphify |

Use `generate.sh` normally. Run `scripts/extract_dependencies.py` directly
only to debug/test extraction, use custom paths, or list resolved inputs:

```bash
python3 scripts/extract_dependencies.py \
  --registry repositories.yml \
  --list-repositories
```

Before generation, record each input's branch, `HEAD`, dirtiness, and whether
remotes were fetched. CI cannot reproduce uncommitted changes, unpushed commits,
or commits on refs it does not check out. A Graphify-only run can also leave the
dependency view older than the code view; a final full run reconciles them.

After generation, report the command, changed artifacts, compact diff, and source
state represented. If a full run fails after dependency extraction, report the
partially changed artifacts and do not call the preview complete. Do not use
`--force` as a generic retry.

### Finish the source feature

1. Fetch the target source repository and check for upstream changes.
2. Integrate according to that repository's policy; obtain authorization before
   choosing a history-changing strategy.
3. Run required formatting, build, and tests.
4. Run one final full graph generation and inspect relevant relationships.
5. Commit, push, or open/update the source PR only when requested.
6. Wait until the feature reaches the remote source ref consumed by graph CI.

Do not publish the local preview as the canonical graph or pull `qaas-graph`
merely to finish the source PR.

Commit or push a local preview only on explicit request after reporting its exact
source provenance. Normal generated-artifact publication goes through graph CI.

## Understand reproducibility and community names

The current normal pipeline uses Graphify's code-only extraction, so graph
generation and community clustering do not require an LLM. The MSBuild dependency
view is deterministic for the same source, evaluations, and toolchain. Expect the
code graph to be reproducible only when source contents, ignore rules, pinned
Graphify version, and relevant environment match; verify exact equality with a
diff.

`Community N` labels mean clustering ran without descriptive community naming.
The normal generator does not run Graphify's LLM-backed labeling step. Treat
adding named communities as a graph-tooling and CI design change because it
requires provider credentials and may introduce variable output.

## Publish the canonical and public graph

After the source feature reaches a CI-consumed remote ref:

1. Read the live update workflow. Trigger it only when requested, from its
   canonical/default ref, or wait for its documented schedule/dispatch event.
2. Inspect the run. No diff means the canonical artifacts were already current;
   a diff should produce or update the automation PR; a failed run changed
   neither canonical nor public state.
3. Review the artifact diff, provenance, base/head, and checks. Merge only on
   explicit request.
4. Confirm artifacts reached the canonical branch.
5. Confirm the Pages workflow deployed the HTML before calling the public graph
   updated. Dependency-only changes may not require a new interactive deployment.

Use a normal human PR for registry, generator, tests, requirements, documentation,
or workflow changes. When the registry changes, keep any explicit CI checkout
list aligned, test and generate locally, merge the human tooling PR first, then
let graph CI create the artifact PR.

## Report graph state precisely

Distinguish:

1. **Committed baseline** — artifacts checked out locally.
2. **Local preview** — artifacts generated from local source state.
3. **Automation PR** — CI proposal; canonical and public graphs are unchanged.
4. **Canonical graph** — artifact PR merged into the canonical branch.
5. **Public graph** — canonical HTML successfully deployed by Pages.

Report the applicable state, source commits and dirtiness, fetch/generation/test
evidence, PR or deployment status, and remaining blockers. Do not summarize all
five states when only one is relevant.
