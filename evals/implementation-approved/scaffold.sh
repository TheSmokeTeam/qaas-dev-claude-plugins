#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SCRIPT_DIR/../lib/init-repository.sh"

mkdir -p QaaS.Framework/src QaaS.Framework/tests
cat > QaaS.Framework/CLAUDE.md <<'EOF'
# QaaS.Framework implementation fixture

Run `bash tests/test_retry_policy.sh` for the focused and full fixture check.
Change tests before production behavior and capture the expected failure.
EOF
cat > QaaS.Framework/project_specs.md <<'EOF'
# Retry policy

RetryPolicy.Attempts is observable behavior. Preserve every property except the
approved default-attempt count.
EOF
cat > QaaS.Framework/.gitignore <<'EOF'
.eval-focused-test-passed
EOF
cat > QaaS.Framework/src/RetryPolicy.cs <<'EOF'
public sealed class RetryPolicy
{
    public int Attempts => 3;
}
EOF
cat > QaaS.Framework/tests/test_retry_policy.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
rm -f .eval-focused-test-passed
grep -q 'Attempts => 3;' src/RetryPolicy.cs
printf 'focused-test: passed\n' > .eval-focused-test-passed
EOF

init_fixture_repository \
  QaaS.Framework \
  https://github.com/TheSmokeTeam/QaaS.Framework.git

checkout="$(git -C QaaS.Framework rev-parse --show-toplevel)"
commit="$(git -C QaaS.Framework rev-parse HEAD)"
fingerprint="$(
  python3 "$PLUGIN_ROOT/skills/plan-qaas-change/scripts/repo_snapshot.py" QaaS.Framework \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["worktree_fingerprint"])'
)"

sed \
  -e "s|__CHECKOUT__|$checkout|g" \
  -e "s|__COMMIT__|$commit|g" \
  -e "s|__FINGERPRINT__|$fingerprint|g" \
  "$SCRIPT_DIR/approved-plan.template.md" > approved-plan.md

digest="$(
  python3 "$PLUGIN_ROOT/skills/plan-qaas-change/scripts/validate_plan.py" \
    --print-digest approved-plan.md
)"
sed "s|__DIGEST__|$digest|g" approved-plan.md > approved-plan.bound.md
mv approved-plan.bound.md approved-plan.md
python3 "$PLUGIN_ROOT/skills/plan-qaas-change/scripts/validate_plan.py" approved-plan.md
