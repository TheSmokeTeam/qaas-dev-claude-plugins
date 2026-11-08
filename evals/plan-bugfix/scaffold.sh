#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/init-repository.sh"

mkdir -p QaaS.Framework/src QaaS.Framework/tests
cat > QaaS.Framework/CLAUDE.md <<'EOF'
# QaaS.Framework fixture

Build: `dotnet build QaaS.Framework.sln`
Test: `dotnet test QaaS.Framework.sln`
Format: `dotnet csharpier check .`
Follow sibling validators and add regression tests before behavior changes.
EOF
cat > QaaS.Framework/project_specs.md <<'EOF'
# Validation

Validators compare normalized names through ValidationHelper.NormalizeName.
Do not rename validators as part of behavioral fixes.
EOF
cat > QaaS.Framework/src/Validators.cs <<'EOF'
internal static class ValidationHelper
{
    internal static string NormalizeName(string value) => value.ToUpperInvariant();
}

internal sealed class FirstValidator
{
    internal bool Validate(string value) => ValidationHelper.NormalizeName(value) == "EXPECTED";
}

internal sealed class SecondValidator
{
    internal bool Validate(string value) => ValidationHelper.NormalizeName(value) == "EXPECTED";
}

internal sealed class ThirdValidator
{
    internal bool Validate(string value) => ValidationHelper.NormalizeName(value) == "EXPECTED";
}

internal sealed class FourthValidator
{
    internal bool Validate(string value) => value == "EXPECTED";
}
EOF
cat > QaaS.Framework/tests/FourthValidatorTests.cs <<'EOF'
public sealed class FourthValidatorTests
{
    [Fact]
    public void AcceptsCanonicalName() => Assert.True(new FourthValidator().Validate("EXPECTED"));
}
EOF

init_fixture_repository \
  QaaS.Framework \
  https://github.com/TheSmokeTeam/QaaS.Framework.git
