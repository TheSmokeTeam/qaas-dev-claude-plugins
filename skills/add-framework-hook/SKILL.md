---
name: add-framework-hook
description: >-
  Use when adding a new reflection-discovered hook to QaaS — an assertion,
  generator, probe, or processor. These are Type A extensions: they implement an
  interface from QaaS.Framework.SDK, ship in a separate QaaS.Common.* NuGet
  package, and are discovered at runtime by name (no framework edit). Covers the
  cross-repo flow from QaaS.Common.* through restore and PackageMirror to
  qaas-docs. Keywords: new hook, add assertion, add generator, add probe, add
  processor, IAssertion, IGenerator, IProbe, IProcessor, custom hook, Common
  package.
---

# Add a Reflection Hook (Type A)

A hook (assertion/generator/probe/processor) is **externally extensible**: you
implement an `QaaS.Framework.SDK` contract in a `QaaS.Common.*` package; the
runtime finds it by name via `QaaS.Framework.Providers`. You do NOT edit the
framework. If you need a transport/serializer/policy instead, STOP — that is
Type B; use `extend-framework-core`.

## Which contract

- `IAssertion` → `QaaS.Common.Assertions`
- `IGenerator` → `QaaS.Common.Generators`
- `IProbe` → `QaaS.Common.Probes`
- `IProcessor` (incl. transaction processors) → `QaaS.Common.Processors`

## Workflow

1. **Open the target `QaaS.Common.*` repo and read its `CLAUDE.md` and
   `project_specs.md` first** — they define the exact base classes, config-object
   convention, naming, and `dotnet build/test` commands. Do not guess signatures.
2. Implement the contract + its config object following the existing siblings in
   that repo (e.g. mirror an existing assertion's structure).
3. Add tests in the repo's `*.Tests` project (the repos use xUnit/NUnit; follow
   the sibling tests).
4. Build & test locally with the commands from that repo's `CLAUDE.md`
   (typically `dotnet build <sln>` / `dotnet test <sln>`), then `csharpier`.
5. The hook is selected by **string name in YAML**; confirm the discovery rules in
   `QaaS.Framework.Providers/project_specs.md` (priority: `QaaS.*`=0, `Common.*`=1,
   others=2; unique `FullName` else simple `Type.Name`).
6. **Release ripple:** a new/bumped `Common.*` version → restore artifact →
   `PackageMirror` sync → regenerated `qaas-docs` page. Hand off to the
   `release-and-mirror` skill for that flow.

## Done when

The hook + config object + tests exist in the correct `Common.*` repo, the repo's
own build and test commands pass, and you have noted the release-ripple follow-up.

## Failure modes

- Putting the hook in `QaaS.Framework` (that makes it Type B and breaks the
  open-extension model).
- Inventing a base-class or config signature instead of reading the repo's
  `CLAUDE.md`/siblings.
- A `Common.*` package that depends on framework internals beyond the SDK contract.
