# Behavioral evals

Cases follow the lifecycle rather than the repository tree:

| Lifecycle concern | Cases |
|---|---|
| Know QaaS and routing | `knowledge-only` |
| Interview and planning | `developer-interview`, `mixed-intent-routing`, `missing-evidence`, `plan-bugfix`, `type-a-feature`, `type-b-feature` |
| Approval and implementation gate | `implementation-pending`, `implementation-approved` |

Every case keeps its prompt, execution metadata, graders, and optional fixture
local. `case.yaml` owns metadata; `prompt.md` contains only the user request.
Tool-use graders are scored in the conformance lane (`--ablation none`). The
optional ablation lane measures lift and treats plugin-only tool graders as
indicators, following Claude Code's eval semantics.

Planning cases intentionally do not grant editing tools. `implementation-pending`
is the dedicated negative case: it grants mutation tools and verifies that they
remain unused before approval. `implementation-approved` exercises the positive
test-first path, plan digest and repository-baseline checks, independent verifier,
and no-release boundary. Its deterministic graders inspect the final source and
test, require test-edit/failing-run/source-edit ordering, and accept the success
sentinel only after the focused check passes. The eval command must grant gated
tools with `--allow-tools`; each case still limits which granted tools reach the
agent.
