# Behavioral evals

Cases follow the lifecycle rather than the repository tree:

| Lifecycle concern | Cases |
|---|---|
| Know QaaS and routing | `knowledge-only` |
| Interview and planning | `developer-interview`, `mixed-intent-routing`, `missing-evidence`, `plan-bugfix`, `type-a-feature`, `type-b-feature` |
| Approval and implementation gate | `implementation-pending`, `implementation-approved` |
| Required-provider failure | `provider-failure-grilling`, `provider-failure-ponytail` |

Every case keeps its prompt, execution metadata, graders, and optional fixture
local. `case.yaml` owns metadata; `prompt.md` contains only the user request.
The focused standard-library runner loads the QaaS, Grilling, and Ponytail plugin
directories directly because Claude's isolated plugin-eval command does not load
external dependencies. It supports exactly the repository's `tool_used`,
`tool_order`, `regex`, `file_exists`, and `llm` graders. `with-only` graders run
only in the provider lane; `both` and unscoped graders also run in optional
no-plugin ablation.

Planning cases intentionally do not grant editing tools. `implementation-pending`
is the dedicated negative case: it grants mutation tools and verifies that they
remain unused before approval. `implementation-approved` exercises the positive
test-first path, source-fact refresh, independent verifier, and no-release
boundary. Its deterministic graders inspect the final source and test, require
test-edit/failing-run/source-edit ordering, and accept the success sentinel only
after the focused check passes. The runner passes matching
`--tools` and `--allowedTools` values from each case, so only declared tools reach
the agent.

`provider-failure-grilling` and `provider-failure-ponytail` copy the pinned real
provider to the isolated run directory and hide only the target `SKILL.md`. They
require the exact `BLOCKED_PROVIDER` marker and prove that no downstream agent or
source mutation occurs.

Run all eleven cases with:

```bash
python3 scripts/provider_eval_runner.py \
  --plugin-root . \
  --grilling-root provider-checkouts/mattpocock-skills \
  --ponytail-root provider-checkouts/ponytail \
  --model "$AGENT_MODEL" \
  --judge-model "$JUDGE_MODEL" \
  --runs "$RUNS" \
  --threshold "$THRESHOLD" \
  --max-cost-usd 30
```

Add `--ablation` for a no-plugin lane. Each invocation writes raw JSONL traces,
per-run grader JSON, `aggregate.json`, and `summary.md`. The manual GitHub Actions
workflow uploads the output even when a case fails.
