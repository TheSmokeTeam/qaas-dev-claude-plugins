---
name: qaas-platform-overview
description: >-
  Master guide for DEVELOPING the QaaS platform (TheSmokeTeam C#/.NET monorepo).
  ALWAYS read this FIRST for ANY work in the QaaS codebase — changing the
  framework, adding an assertion/generator/probe/processor, adding a
  protocol/serializer/policy, cutting a release, or finding where something lives.
  Loads the multi-repo map, the qaas-graph architecture source, the framework
  dependency graph, the release ripple, the repo router, and the Type A vs Type B
  extension decision gate. Keywords: QaaS, qaas-graph, Graphify, TheSmokeTeam,
  QaaS.Framework, Runner, Mocker, PackageMirror, monorepo, hook, protocol,
  serializer, policy, release, where is.
---

# Building the QaaS Platform — Master Guide

You help Smoke-team developers **build the QaaS platform itself** (the C#/.NET
monorepo) — NOT author QaaS tests with it (that is a separate, end-user concern).
This plugin owns the knowledge that lives *between* repos; everything inside a
repo belongs to that repo's own docs.

## Constitution (non-negotiable)

1. **DELEGATE IN-REPO.** Most implementation repos (Framework, Runner, Mocker,
   the `Common.*` packages) ship a root `CLAUDE.md` and per-project
   `project_specs.md`. For anything inside a repo, open it and read its `CLAUDE.md`
   FIRST; if it has none (common for tooling/template/sample repos), fall back to
   its `README.md`. Do not duplicate or guess in-repo contents.
2. **SOURCES-OR-SILENCE.** Never invent a repo name, package id, config key,
   type, dependency, or CI step. Use a committed `qaas-graph` artifact with
   recorded provenance for cross-repo discovery, then verify code-level claims
   in an in-tree `CLAUDE.md`/`project_specs.md`, source file, or
   `docs.qaas.online`. If the evidence is not in front of you, say what is
   missing and stop.
3. **LIVE OVER MEMORY.** QaaS evolves and your training is stale. Confirm the repo
   set and the Type B family list against the live `QaaS.Framework` CLAUDE.md.
4. **GRAPH FOR DISCOVERY, SOURCE FOR PROOF.** Use the committed `qaas-graph`
   artifacts to find likely repositories, dependencies, symbols, and paths across
   the platform. Verify every conclusion in the owning repo's docs or source.

## The repos (https://github.com/TheSmokeTeam)

- **QaaS.Framework** — foundational layer. Projects: SDK (hook contracts),
  Protocols, Policies, Configurations, Serialization, Providers, Executions,
  Infrastructure. Every breaking change here ripples downstream.
- **QaaS.Common.Assertions / .Generators / .Probes / .Processors** — reflection
  hook packages (Type A). Implement SDK contracts; shipped as separate NuGets.
- **QaaS.Runner / QaaS.Mocker** (+ `.Template` repos, `Qaas.Mocker.CommunicationObjects`, `QaaS.Mocker.Template`) — the executables.
- **QaaS.PackageMirror** — central mirror of restored package trees + generated
  family schemas; publishes releases and opens synced qaas-docs PRs.
- **QaaS.Docs.Generator** + **qaas-docs** — deterministic docs renderer and the
  published site (https://docs.qaas.online / GitHub Pages).
- **QaaS.Configuration** — internal configuration package.
- **QaaS.Runner.Template / QaaS.Mocker.Template** — `dotnet new` project templates.
- **qaas-graph** — reproducible, derived architecture map. Its committed MSBuild
  dependency model and merged code graph are navigation sources, not replacements
  for the registered repositories' docs and source.

These are the repos you touch when *developing the platform*. The org also
contains repos that are NOT part of QaaS platform development — e.g. standalone
tools and sample/demo apps — ignore those for this work. This list is neither
exhaustive nor fixed; confirm the current set with `gh repo list TheSmokeTeam` or
the PackageMirror "Tracked source repositories" list rather than trusting a count.

## QaaS graph as a knowledge source

Use `qaas-graph` when a question crosses repository boundaries or the owning code
is not yet known:

- `graphs/repositories.json` contains evaluated project/package dependencies,
  versions, target frameworks, evaluation modes, and source commit SHAs.
- `graphify-out/graph.json` contains the merged code-level symbol and relationship
  graph; use `graphify query`, `graphify explain`, or `graphify path` against it.

Apply the `qaas-graph-workflow` skill to locate an existing checkout or clone
`https://github.com/TheSmokeTeam/qaas-graph.git` only when graph functionality is
needed. Query committed artifacts before considering regeneration. For a query,
the graph checkout is sufficient; clone only the owning source repo needed for
verification. Generation requires every input registered in `repositories.yml`.

The graph contains only registered code inputs. It does not replace facts that
exist only in repo prose, `qaas-docs`, PackageMirror, templates, or other
unregistered repositories. Report whether a conclusion came from the committed
baseline or a locally generated preview.

## Framework dependency graph (acyclic)

`Infrastructure → Serialization, Configurations → SDK → Protocols, Policies (independent) → Providers → Executions`

## The release ripple

A change in `QaaS.Framework.SDK` (or any framework project) flows:
`QaaS.Framework` release → `Common.*` rebuild/restore → `PackageMirror` sync
(new schemas + bootstrap package set) → synced `qaas-docs` PR (regenerated by
`QaaS.Docs.Generator`). See the `release-and-mirror` skill for the mechanics.

## The Type A vs Type B decision gate (read before extending anything)

QaaS has TWO architecturally distinct extension mechanisms. The ONLY discriminator
is **extensibility/ownership** — *can an external user add one by dropping a DLL
(Type A), or must you edit and re-release the framework core (Type B)?* Internal
wiring (factory vs switch vs builder) is NOT the discriminator.

| | **Type A — reflection hook** | **Type B — compiled framework core** |
|---|---|---|
| Contracts in | `QaaS.Framework.SDK` (`IGenerator`/`IAssertion`/`IProbe`/`IProcessor`) | `QaaS.Framework.Protocols` / `.Serialization` / `.Policies` |
| Discovery | Runtime assembly scan by `QaaS.Framework.Providers` (`ByNameObjectCreator`), selected by name in YAML | Compile-time: factory or typed switch/builder inside the framework |
| Extensible by | Anyone — drop a DLL / new `Common.*` package | Platform team only — edit `QaaS.Framework` |
| Where you work | A `QaaS.Common.*` repo | Inside the relevant `QaaS.Framework.*` project |
| Release ripple | new/bumped `Common.*` → PackageMirror → qaas-docs | new **`QaaS.Framework`** version → ALL downstream repos rebuild |
| Use when | Adding test-domain logic (assertion rule, data generator, probe, processor) | Adding transport/IO (broker, DB, storage), a serialization format, or a rate/stop policy |

- **Type A members:** assertions, generators, probes, processors. → use the
  `add-framework-hook` skill.
- **Type B members (verified):** Protocols (factory keyed by `SerializationType`
  + config record), Serialization (serializer/deserializer factories), Policies
  (typed `switch` over `IPolicyConfig` in `PolicyBuilder`, chained by ascending
  `Index`). → use the `extend-framework-core` skill. Confirm the current Type B
  set against `QaaS.Framework`'s CLAUDE.md before relying on it.

## Working discipline (QaaS-specific)

Before claiming any change works, run these — evidence, not belief:

- **TDD / verify in-repo.** Add or update a test in the repo's `*.Tests` project
  for the behavior you changed, then run that repo's real commands from its
  `CLAUDE.md` (typically `dotnet build <sln>` then `dotnet test <sln>`, plus
  `csharpier`). A change is "done" only when you have pasted-real build+test output
  — never on the assumption that it compiles.
- **Spec-anchored, anti-hallucination.** Every QaaS type, package id, config key,
  or CI step you rely on must trace to an in-tree `CLAUDE.md`/`project_specs.md`
  or `docs.qaas.online`. If it is not in front of you, say what is missing and
  stop (docs-or-silence). Do not invent signatures, defaults, or repo names.
- **Grill your own claims.** Before reporting, challenge each assertion: "what's
  my evidence? did I run it, or assume it? what would a skeptic check?" Surface
  the weakest claim explicitly rather than presenting guesses as facts.

## Routing — which skill / repo for a task

- "add an assertion/generator/probe/processor" → `add-framework-hook`.
- "add a protocol / serializer / policy / edit the framework core" → `extend-framework-core`.
- "release / version bump / mirror / publish packages" → `release-and-mirror`.
- "query / refresh / publish the QaaS graph" → `qaas-graph-workflow`.
- "where is X / which repo or doc covers Y" → `find-qaas-knowledge`.
- Otherwise: open the most relevant repo and read its `CLAUDE.md` first.

## Done when

You have (a) identified the correct repo(s) for the task, (b) classified any
extension work as Type A or Type B, and (c) read the relevant in-tree `CLAUDE.md`
before proposing changes.

## Failure modes

- Editing `QaaS.Framework` for something that should be a `Common.*` package
  (Type A misclassified as B) — or the reverse.
- Forgetting the release ripple after a framework change.
- Duplicating in-repo facts here instead of reading the repo's `CLAUDE.md`.
- Treating a graph hit as authoritative without verifying it in source, or
  cloning/regenerating the graph when the task does not need it.
