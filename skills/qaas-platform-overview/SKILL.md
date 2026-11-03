---
name: qaas-platform-overview
description: >-
  Master guide for DEVELOPING the QaaS platform (TheSmokeTeam C#/.NET monorepo).
  ALWAYS read this FIRST for ANY work in the QaaS codebase — changing the
  framework, adding an assertion/generator/probe/processor, adding a
  protocol/serializer/policy, planning or implementing a feature/bugfix, cutting
  a release, or finding where something lives.
  Loads the multi-repo map, the framework dependency graph, the release ripple, the
  repo router, and the Type A vs Type B extension decision gate. Keywords: QaaS,
  TheSmokeTeam, QaaS.Framework, Runner, Mocker, PackageMirror, monorepo, hook,
  protocol, serializer, policy, release, where is.
---

# Building the QaaS Platform — Master Guide

You help Smoke-team developers **build the QaaS platform itself** (the C#/.NET
monorepo) — NOT author QaaS tests with it (that is a separate, end-user concern).
This plugin owns the knowledge that lives *between* repos; everything inside a
repo belongs to that repo's own docs.

## Step 1 — Know QaaS (mandatory ecosystem context)

Run this stage before routing, planning, implementing, verifying, or releasing a
QaaS platform change. Its purpose is to give the agent a correct working mental
model of the QaaS ecosystem. It is context acquisition, not an implementation
plan and not permission to edit code.

Build a concise **Know QaaS Context Brief** for the raw request:

- **Platform scope:** confirm that the request concerns developing the QaaS
  platform rather than authoring tests with QaaS.
- **Ecosystem location:** identify the affected capability and likely owning and
  consuming repositories without claiming unverified code-level details.
- **Dependency position:** explain where the capability sits in the framework
  dependency graph and which upstream/downstream relationships matter.
- **Extension model:** classify Type A, Type B, existing behavior, or not yet
  classifiable, with the ownership reason for that classification.
- **Release ripple:** state the likely package, PackageMirror, schema, docs, and
  downstream implications, or explain why they do not apply.
- **Authority map:** name the repository instructions, source, live docs, and
  knowledge-graph evidence that the next stage must inspect.
- **Known unknowns:** record missing ecosystem facts explicitly; never fill them
  from memory.

Keep the brief proportional to the request. Pass it intact to the next stage and
refresh it when scope, classification, or repository evidence changes. Do not
route a change request or begin detailed source planning until this brief exists.

## Constitution (non-negotiable)

1. **DELEGATE IN-REPO.** Most implementation repos (Framework, Runner, Mocker,
   the `Common.*` packages) ship a root `CLAUDE.md` and per-project
   `project_specs.md`. For anything inside a repo, open it and read its `CLAUDE.md`
   FIRST; if it has none (common for tooling/template/sample repos), fall back to
   its `README.md`. Do not duplicate or guess in-repo contents.
2. **EVIDENCE-OR-SILENCE.** Never invent a repo name, package id, config key,
   type, relationship, or CI step. Cite an in-tree `CLAUDE.md`/`project_specs.md`,
   `docs.qaas.online`, or `qaas-knowledge-graph` for source relationships. If a
   fact is not in front of you, say what is missing and stop.
3. **LIVE OVER MEMORY.** QaaS evolves and your training is stale. Confirm the repo
   set and the Type B family list against the live `QaaS.Framework` CLAUDE.md.
4. **SPECIFY BEFORE IMPLEMENTING.** For a feature or bugfix, use
   `plan-qaas-change` to establish current state, desired state, acceptance
   criteria, exact test-first steps, and an independent `APPROVED` review before
   editing production code. Revalidate a plan when an inspected repository moves.

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

These are the repos you touch when *developing the platform*. The org also
contains repos that are NOT part of QaaS platform development — e.g. standalone
tools and sample/demo apps — ignore those for this work. This list is neither
exhaustive nor fixed; confirm the current set with `gh repo list TheSmokeTeam` or
the PackageMirror "Tracked source repositories" list rather than trusting a count.

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

- **Strict SDD / plan gate.** Do not begin a feature or bugfix from an informal
  checklist. Produce and review a QaaS Change Specification and Implementation
  Plan with verified repositories, commits, files, symbols, tests, impact, and
  release work. `NEEDS_DECISION`, `BLOCKED`, and `STALE` are stop states.
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

Route only after completing the Know QaaS Context Brief. Routing chooses the
next workflow; it does not replace ecosystem understanding.

- "plan/design/implement a QaaS feature or bugfix" → `plan-qaas-change` first;
  implementation may start only from a current `APPROVED` plan.
- "add an assertion/generator/probe/processor" → `add-framework-hook`.
- "add a protocol / serializer / policy / edit the framework core" → `extend-framework-core`.
- "release / version bump / mirror / publish packages" → `release-and-mirror`.
- "where is X / which repo or doc covers Y" → `find-qaas-knowledge`.
- Otherwise: open the most relevant repo and read its `CLAUDE.md` first.

## Done when

The downstream agent has a concise Know QaaS Context Brief, the correct next
workflow is selected, the relevant in-tree instructions are identified, and no
ecosystem claim depends on unverified memory. For feature/bugfix work, planning
and implementation remain separate later stages.

## Failure modes

- Editing `QaaS.Framework` for something that should be a `Common.*` package
  (Type A misclassified as B) — or the reverse.
- Forgetting the release ripple after a framework change.
- Duplicating in-repo facts here instead of reading the repo's `CLAUDE.md`.
- Treating Know QaaS as a repository lookup or plan instead of ecosystem context.
- Routing from keywords before understanding ownership, dependencies, and ripple.
- Editing code from a vague, unreviewed, blocked, or stale plan.
