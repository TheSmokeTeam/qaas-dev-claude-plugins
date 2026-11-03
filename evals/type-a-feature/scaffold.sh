#!/usr/bin/env bash
set -euo pipefail
mkdir -p QaaS.Common.Generators/src QaaS.Common.Generators/tests
cat > QaaS.Common.Generators/CLAUDE.md <<'EOF'
# QaaS.Common.Generators fixture

Snapshot commit: 2222222222222222222222222222222222222222
Generators implement QaaS.Framework.SDK IGenerator, use a sibling config record,
and are runtime-discovered by name. Build with `dotnet build
QaaS.Common.Generators.sln`; test with `dotnet test QaaS.Common.Generators.sln`.
EOF
cat > QaaS.Common.Generators/project_specs.md <<'EOF'
# Generator convention

Place generators in src and tests in tests. Mirror ConstantGenerator and
ConstantGeneratorConfig. Do not edit QaaS.Framework for a new generator.
EOF
cat > QaaS.Common.Generators/src/ConstantGenerator.cs <<'EOF'
public sealed record ConstantGeneratorConfig(string Value);
public sealed class ConstantGenerator : IGenerator
{
    public object Generate(ConstantGeneratorConfig config) => config.Value;
}
EOF
cat > QaaS.Common.Generators/tests/ConstantGeneratorTests.cs <<'EOF'
public sealed class ConstantGeneratorTests
{
    [Fact]
    public void ReturnsConfiguredValue() { }
}
EOF
