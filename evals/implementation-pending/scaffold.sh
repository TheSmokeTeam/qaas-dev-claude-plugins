#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/init-repository.sh"

mkdir -p QaaS.Framework/src
cat > QaaS.Framework/CLAUDE.md <<'EOF'
# QaaS.Framework approval-gate fixture

Never modify production code before the developer approves the reviewed plan.
EOF
cat > QaaS.Framework/src/RetryPolicy.cs <<'EOF'
public sealed class RetryPolicy
{
    public int Attempts => 3;
}
EOF

init_fixture_repository \
  QaaS.Framework \
  https://github.com/TheSmokeTeam/QaaS.Framework.git
