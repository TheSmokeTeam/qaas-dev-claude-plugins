#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/init-repository.sh"

mkdir -p QaaS.Framework/Serialization QaaS.Framework/Serialization.Tests QaaS.Runner
cat > QaaS.Framework/CLAUDE.md <<'EOF'
# QaaS.Framework fixture

Serialization formats are a closed, compiled framework family. Build with
`dotnet build QaaS.Framework.sln`, test with `dotnet test QaaS.Framework.sln`,
and check formatting with `dotnet csharpier check .`.
EOF
cat > QaaS.Framework/Serialization/project_specs.md <<'EOF'
# Serialization

SerializationType is the public discriminator. SerializerFactory and
DeserializerFactory are the two selection points. Every format has round-trip,
invalid-input, and factory-selection tests. Mirror the YAML implementation.
EOF
cat > QaaS.Framework/Serialization/SerializationType.cs <<'EOF'
public enum SerializationType { Json, Yaml }
EOF
cat > QaaS.Framework/Serialization/SerializerFactory.cs <<'EOF'
public static class SerializerFactory
{
    public static ISerializer Create(SerializationType type) => type switch
    {
        SerializationType.Json => new JsonSerializer(),
        SerializationType.Yaml => new YamlSerializer(),
        _ => throw new ArgumentOutOfRangeException(nameof(type))
    };
}
EOF
cat > QaaS.Framework/Serialization/DeserializerFactory.cs <<'EOF'
public static class DeserializerFactory
{
    public static IDeserializer Create(SerializationType type) => type switch
    {
        SerializationType.Json => new JsonDeserializer(),
        SerializationType.Yaml => new YamlDeserializer(),
        _ => throw new ArgumentOutOfRangeException(nameof(type))
    };
}
EOF
cat > QaaS.Framework/Serialization/YamlSerializer.cs <<'EOF'
public sealed class YamlSerializer : ISerializer { }
public sealed class YamlDeserializer : IDeserializer { }
EOF
cat > QaaS.Framework/Serialization.Tests/YamlSerializationTests.cs <<'EOF'
public sealed class YamlSerializationTests
{
    [Fact] public void RoundTrips() { }
    [Fact] public void RejectsInvalidInput() { }
    [Fact] public void FactoriesSelectYaml() { }
}
EOF
cat > QaaS.Runner/CLAUDE.md <<'EOF'
# QaaS.Runner fixture

Runner consumes released QaaS.Framework packages. Verify package edges in csproj
and build with `dotnet build QaaS.Runner.sln`.
EOF
cat > QaaS.Runner/QaaS.Runner.csproj <<'EOF'
<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="QaaS.Framework.Serialization" Version="2.3.0" />
  </ItemGroup>
</Project>
EOF

init_fixture_repository \
  QaaS.Framework \
  https://github.com/TheSmokeTeam/QaaS.Framework.git
init_fixture_repository \
  QaaS.Runner \
  https://github.com/TheSmokeTeam/QaaS.Runner.git
