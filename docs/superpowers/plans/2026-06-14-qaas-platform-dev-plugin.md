# qaas-platform-dev Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code plugin (+ portable `AGENTS.md`) that makes any AI agent productive at *building the QaaS platform*, owning the cross-repo seams and delegating in-repo detail to each repo's existing `CLAUDE.md`.

**Architecture:** A single plugin at repo root: `.claude-plugin/{plugin.json,marketplace.json}`, five `skills/*/SKILL.md` (one always-on overview holding the Type A/B decision gate, two extension skills, a release skill, a knowledge-router skill), two `commands/*.md`, a `scripts/build-agents-md.sh` that renders all skill bodies into a committed `AGENTS.md`, and a `scripts/validate-plugin.sh` that checks manifests + frontmatter + referenced-URL liveness. CI runs validation and an AGENTS.md drift check.

**Tech Stack:** Markdown (skills/commands), JSON (plugin manifests), Bash (build + validation scripts), `jq` + `python3` for JSON parsing, GitHub Actions for CI.

**Source of truth for content:** the approved spec `docs/superpowers/specs/2026-06-14-qaas-platform-dev-plugin-design.md`. All QaaS facts in the skills below are verified from `TheSmokeTeam` source; do not invent beyond them.

**Branch:** work continues on `design/qaas-platform-dev-plugin` (already checked out, spec already committed there).

---

## File Structure

| File | Responsibility |
|---|---|
| `.claude-plugin/plugin.json` | Plugin manifest (name, version, description, keywords). |
| `.claude-plugin/marketplace.json` | Single-plugin marketplace pointing `source: "."`. |
| `skills/qaas-platform-overview/SKILL.md` | Always-on: org map, dep graph, release ripple, repo router, **Type A/B decision gate**. |
| `skills/add-framework-hook/SKILL.md` | Type A workflow (assertions/generators/probes/processors → `Common.*`). |
| `skills/extend-framework-core/SKILL.md` | Type B workflow (protocols/serialization/policies inside `QaaS.Framework`). |
| `skills/release-and-mirror/SKILL.md` | PackageMirror pipeline + source-repo CI contract. |
| `skills/find-qaas-knowledge/SKILL.md` | Docs-or-silence knowledge router. |
| `commands/qaas-where.md` | `/qaas-where <task>` — deterministic router wrapper. |
| `commands/qaas-release.md` | `/qaas-release` — deterministic release-flow wrapper. |
| `scripts/validate-plugin.sh` | Manifest JSON parse + skill/command frontmatter + URL liveness checks. |
| `scripts/build-agents-md.sh` | Concatenate skill bodies → `AGENTS.md`. |
| `AGENTS.md` | GENERATED portable bundle (do-not-edit header). |
| `README.md` | Install + usage for the team. |
| `.github/workflows/validate.yml` | CI: run validation + AGENTS.md drift check. |

**Conventions for all skills:** YAML frontmatter with `name` (matches directory) and a `description` that is one sentence of purpose + an explicit `Keywords:` clause. Body follows the eldarush contract format: a short mission line, a **Done when** rubric, **Failure modes**, and the **docs-or-silence** rule (never invent a repo/package/key; cite the in-tree `CLAUDE.md` or `docs.qaas.online`).

---

## Phase 1 — Installable plugin scaffold

### Task 1: Validation script (the "test" harness)

**Files:**
- Create: `scripts/validate-plugin.sh`

- [ ] **Step 1: Write the validation script**

```bash
#!/usr/bin/env bash
# Validates the qaas-platform-dev plugin: manifests parse, every skill/command
# has required frontmatter, and referenced TheSmokeTeam repos + docs resolve.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail=0
err() { echo "FAIL: $*" >&2; fail=1; }

# 1. Manifests parse as JSON.
for f in "$ROOT/.claude-plugin/plugin.json" "$ROOT/.claude-plugin/marketplace.json"; do
  [ -f "$f" ] || { err "missing $f"; continue; }
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" || err "invalid JSON: $f"
done

# 2. Every skill has name + description frontmatter; name matches its directory.
for skill in "$ROOT"/skills/*/SKILL.md; do
  [ -f "$skill" ] || continue
  dir="$(basename "$(dirname "$skill")")"
  fm="$(awk 'NR==1&&$0=="---"{f=1;next} f&&$0=="---"{exit} f' "$skill")"
  echo "$fm" | grep -q "^name: *$dir\$" || err "$skill: name must equal '$dir'"
  echo "$fm" | grep -Eq "^description: *([>|].*|\S.+)" || err "$skill: missing description"
done

# 3. Every command has a description.
for cmd in "$ROOT"/commands/*.md; do
  [ -f "$cmd" ] || continue
  awk 'NR==1&&$0=="---"{f=1;next} f&&$0=="---"{exit} f' "$cmd" \
    | grep -Eq "^description: *\S" || err "$cmd: missing description"
done

# 4. Referenced URLs resolve (skipped when OFFLINE=1).
if [ "${OFFLINE:-0}" != "1" ]; then
  while read -r url; do
    code="$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 15 "$url" || echo 000)"
    case "$code" in 2*|3*) ;; *) err "unreachable ($code): $url";; esac
  done < <(grep -rhoE 'https://(github\.com/TheSmokeTeam/[A-Za-z0-9._-]+|docs\.qaas\.online[A-Za-z0-9./_-]*)' \
            "$ROOT/skills" "$ROOT/commands" 2>/dev/null | sort -u)
fi

[ "$fail" -eq 0 ] && echo "validate-plugin: OK" || { echo "validate-plugin: FAILED"; exit 1; }
```

- [ ] **Step 2: Make it executable and run it (expect failure — no manifests yet)**

Run: `chmod +x scripts/validate-plugin.sh && OFFLINE=1 ./scripts/validate-plugin.sh`
Expected: FAIL with `missing .../.claude-plugin/plugin.json`

- [ ] **Step 3: Commit**

```bash
git add scripts/validate-plugin.sh
git commit -m "Add plugin validation script"
```

### Task 2: Plugin + marketplace manifests

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Write `plugin.json`**

```json
{
  "name": "qaas-platform-dev",
  "version": "0.1.0",
  "description": "Cross-repo guide for Smoke-team developers building the QaaS platform (TheSmokeTeam C#/.NET monorepo). Knows the 18-repo map, the framework dependency graph, the release ripple, and the two extension mechanisms — Type A reflection hooks (Common.* packages) vs Type B compiled framework core (protocols, serialization, policies). Delegates in-repo detail to each repo's CLAUDE.md and the live docs at docs.qaas.online.",
  "author": { "name": "TheSmokeTeam" },
  "homepage": "https://github.com/TheSmokeTeam/qaas-dev-claude-plugins",
  "repository": "https://github.com/TheSmokeTeam/qaas-dev-claude-plugins",
  "license": "MIT",
  "keywords": ["qaas", "platform-development", "csharp", "dotnet", "monorepo", "framework", "hooks", "thesmoketeam"]
}
```

- [ ] **Step 2: Write `marketplace.json`**

```json
{
  "name": "qaas-dev-claude-plugins",
  "owner": { "name": "TheSmokeTeam" },
  "metadata": {
    "description": "Smoke-team plugin marketplace for QaaS platform development.",
    "version": "0.1.0"
  },
  "plugins": [
    {
      "name": "qaas-platform-dev",
      "source": ".",
      "description": "Cross-repo guide for building the QaaS platform: repo map, framework dependency graph, release ripple, and the Type A (reflection hooks) vs Type B (compiled framework core) extension mechanisms.",
      "version": "0.1.0",
      "category": "development",
      "tags": ["qaas", "platform-development", "csharp", "dotnet", "monorepo"]
    }
  ]
}
```

- [ ] **Step 3: Run validation (manifests now pass; skills still absent but globs are empty so no skill errors)**

Run: `OFFLINE=1 ./scripts/validate-plugin.sh`
Expected: `validate-plugin: OK` (no skills/commands yet → loops are no-ops)

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "Add plugin and marketplace manifests"
```

---

## Phase 2 — Always-on overview skill (org map + A/B decision gate)

### Task 3: `qaas-platform-overview` skill

**Files:**
- Create: `skills/qaas-platform-overview/SKILL.md`

- [ ] **Step 1: Write the skill**

````markdown
---
name: qaas-platform-overview
description: >-
  Master guide for DEVELOPING the QaaS platform (TheSmokeTeam C#/.NET monorepo).
  ALWAYS read this FIRST for ANY work in the QaaS codebase — changing the
  framework, adding an assertion/generator/probe/processor, adding a
  protocol/serializer/policy, cutting a release, or finding where something lives.
  Loads the 18-repo map, the framework dependency graph, the release ripple, the
  repo router, and the Type A vs Type B extension decision gate. Keywords: QaaS,
  TheSmokeTeam, QaaS.Framework, Runner, Mocker, PackageMirror, monorepo, hook,
  protocol, serializer, policy, release, where is.
---

# Building the QaaS Platform — Master Guide

You help Smoke-team developers **build the QaaS platform itself** (the C#/.NET
monorepo), NOT author QaaS tests (that is `eldarush/qaas-copilot`'s job). This
plugin owns the knowledge that lives *between* repos; everything inside a repo
belongs to that repo's own docs.

## Constitution (non-negotiable)

1. **DELEGATE IN-REPO.** Every repo ships a root `CLAUDE.md` and per-project
   `project_specs.md`. For anything inside a repo, open that repo and read its
   `CLAUDE.md` FIRST. Do not duplicate or guess its contents.
2. **DOCS-OR-SILENCE.** Never invent a repo name, package id, config key, type, or
   CI step. Cite an in-tree `CLAUDE.md`/`project_specs.md` or `docs.qaas.online`.
   If a fact is not in front of you, say what is missing and stop.
3. **LIVE OVER MEMORY.** QaaS evolves and your training is stale. Confirm the repo
   set and the Type B family list against the live `QaaS.Framework` CLAUDE.md.

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
- **QaaS.Configuration**, **QaaS.PackageMirror**, **steak** (Kafka viewer),
  **DummyAppMock / DummyAppTests** (samples).

Always confirm the current set with `gh repo list TheSmokeTeam` or by reading the
PackageMirror "Tracked source repositories" list.

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

## Routing — which skill / repo for a task

- "add an assertion/generator/probe/processor" → `add-framework-hook`.
- "add a protocol / serializer / policy / edit the framework core" → `extend-framework-core`.
- "release / version bump / mirror / publish packages" → `release-and-mirror`.
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
````

- [ ] **Step 2: Run validation (offline) to verify frontmatter passes**

Run: `OFFLINE=1 ./scripts/validate-plugin.sh`
Expected: `validate-plugin: OK`

- [ ] **Step 3: Verify referenced URLs resolve (online)**

Run: `./scripts/validate-plugin.sh`
Expected: `validate-plugin: OK` (all `TheSmokeTeam/*` and `docs.qaas.online` links 2xx/3xx)

- [ ] **Step 4: Commit**

```bash
git add skills/qaas-platform-overview/SKILL.md
git commit -m "Add always-on qaas-platform-overview skill with A/B decision gate"
```

---

## Phase 3 — Extension skills (Type A and Type B)

### Task 4: `add-framework-hook` skill (Type A)

**Files:**
- Create: `skills/add-framework-hook/SKILL.md`

- [ ] **Step 1: Write the skill**

````markdown
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
````

- [ ] **Step 2: Validate (offline) + commit**

```bash
OFFLINE=1 ./scripts/validate-plugin.sh
git add skills/add-framework-hook/SKILL.md
git commit -m "Add add-framework-hook skill (Type A extension flow)"
```

### Task 5: `extend-framework-core` skill (Type B)

**Files:**
- Create: `skills/extend-framework-core/SKILL.md`

- [ ] **Step 1: Write the skill**

````markdown
---
name: extend-framework-core
description: >-
  Use when adding something that lives INSIDE QaaS.Framework and cannot be
  extended by external packages — a new protocol/transport (broker, DB, storage),
  a serialization format, or a rate/stop policy. These are Type B extensions:
  compiled into the framework core, selected at compile time (factory or typed
  switch/builder, not reflection), and adding one requires a new QaaS.Framework
  release that ripples to all downstream repos. Keywords: new protocol, transport,
  broker, database, storage, serializer, serialization format, policy, load
  balance, factory, edit QaaS.Framework, framework core.
---

# Extend the Framework Core (Type B)

Type B families are **owned by the platform team and closed to external
extension**. Adding one means editing `QaaS.Framework` and releasing a new
framework version. If an external user could add it by dropping a DLL, it is NOT
Type B — it is a hook; use `add-framework-hook` instead.

## The Type B families (verified — confirm current set in QaaS.Framework CLAUDE.md)

| Family | Project | Selection mechanism |
|---|---|---|
| **Protocols** | `QaaS.Framework.Protocols` | Factories (`ReaderFactory`/`SenderFactory`/`TransactorFactory`/`FetcherFactory` + chunk variants) keyed by `SerializationType` + a protocol-specific config record. Closed set of 15+ (Kafka, RabbitMQ, HTTP, gRPC, MS-SQL, PostgreSQL, Oracle, Trino, Redis, MongoDB, Elastic, Prometheus, S3, SFTP, Socket, IBM MQ, Mocker proxy). Abstractions: `IReader`/`ISender`/`ITransactor`/`IFetcher`/`IChunkReader`/`IChunkSender`/`IConnectable`. |
| **Serialization** | `QaaS.Framework.Serialization` | Serializer/deserializer factories. Formats: Binary, Json, MessagePack, Xml, Yaml, ProtobufMessage, XmlElement. |
| **Policies** | `QaaS.Framework.Policies` | Typed `switch` over `IPolicyConfig` in `PolicyBuilder.Configure`/`Build` (a `default: throw` closed set), chained via `Add` in ascending `Index` order. Members: `CountPolicy`, `TimeoutPolicy`, `LoadBalancePolicy`, `IncreasingLoadBalancePolicy`, `AdvancedLoadBalancePolicy`. |

**Note:** internal wiring differs per family (factory vs switch+builder). That is
NOT the discriminator — extensibility/ownership is. All three are Type B because
no reflection/DLL-drop path exists; you must edit the framework.

## Workflow

1. **Open `QaaS.Framework` and read the root `CLAUDE.md` plus the target
   project's `project_specs.md` first.** Confirm the family is still Type B and
   learn the exact abstractions, factory/builder, and "Forbidden in this project"
   rules. Do not guess.
2. Implement the new member in the correct project, registering it in its
   selection point:
   - Protocol/serializer → add the implementation + wire it into the relevant
     factory keyed by its `SerializationType`/config record.
   - Policy → add a `*PolicyConfig : IPolicyConfig`, a `*Policy : Policy` with an
     `Index`, and a `case` in BOTH `PolicyBuilder.Configure` and
     `PolicyBuilder.Build`.
3. Add tests in the matching `QaaS.Framework.*.Tests` project, following siblings.
4. Build & test with the commands in `QaaS.Framework/CLAUDE.md`
   (`dotnet build QaaS.Framework.sln` / `dotnet test ...`), then `csharpier`.
5. **Release ripple (mandatory):** a new `QaaS.Framework` version ripples to ALL
   downstream repos (Common.*, Runner, Mocker, PackageMirror, qaas-docs). Hand off
   to `release-and-mirror`.

## Done when

The new member is implemented in the correct framework project, registered in its
selection point, tested, the framework solution builds/tests green, and the
downstream release ripple is noted.

## Failure modes

- Treating a transport/serializer/policy as a droppable hook (it is not
  reflection-discovered — it will never be found).
- Forgetting one of the two `PolicyBuilder` switches (`Configure` AND `Build`).
- Shipping a framework change without planning the downstream release ripple.
````

- [ ] **Step 2: Validate (offline) + commit**

```bash
OFFLINE=1 ./scripts/validate-plugin.sh
git add skills/extend-framework-core/SKILL.md
git commit -m "Add extend-framework-core skill (Type B extension flow)"
```

---

## Phase 4 — Release and knowledge-router skills

### Task 6: `release-and-mirror` skill

**Files:**
- Create: `skills/release-and-mirror/SKILL.md`

- [ ] **Step 1: Write the skill**

````markdown
---
name: release-and-mirror
description: >-
  Use when releasing or publishing QaaS packages, bumping versions, running the
  PackageMirror sync, regenerating family schemas, or producing the synced
  qaas-docs PR. Explains the QaaS.PackageMirror pipeline and the CI contract every
  source repo must satisfy. Keywords: release, publish, version bump, NuGet,
  PackageMirror, restored-packages artifact, family schema, qaas-docs PR, mirror
  sync.
---

# Release & Package Mirror

`QaaS.PackageMirror` is the central mirror: each sync rebuilds `packages/` from
the latest successful restore artifact of every tracked source repo, regenerates
Runner/Mocker family schemas, rewrites `state/`, publishes a GitHub release, and
opens a synced `qaas-docs` PR. Read `QaaS.PackageMirror/README.md` and its
`CLAUDE.md` for the authoritative current rules before acting.

## The pipeline (high level)

1. A source repo (Framework, Common.*, Runner, Mocker, Mocker.CommunicationObjects)
   is tagged with a stable version `X.X.X`.
2. Its CI restores packages and uploads the `restored-packages` artifact.
3. `QaaS.PackageMirror`'s `sync-packages.yml` rebuilds the mirror:
   `packages/qaas/<id>/<version>` (latest only, excluding `QaaS.Configuration` +
   templates) and `packages/not-qaas/<id>/<version>` (all used external versions),
   regenerates `schemas/<family>/latest/{schema.json,docs-manifest.json,hook-catalog.json}`,
   rewrites `state/`, publishes a release marked latest, appends `CHANGELOG.md`,
   and opens a `qaas-docs` PR.

## Source-repo CI contract (each tracked repo must)

1. restore packages into `${{ github.workspace }}\RestoredPackages`,
2. support `workflow_dispatch` (manual + API trigger),
3. on stable tags `X.X.X`, write `restore-artifact-metadata.json` into that folder,
4. upload that folder as the artifact named `restored-packages`.

## Tracked source repos

QaaS.Common.Assertions, QaaS.Common.Generators, QaaS.Common.Probes,
QaaS.Common.Processors, QaaS.Framework, QaaS.Mocker,
Qaas.Mocker.CommunicationObjects, QaaS.Runner. (Confirm against the live
PackageMirror README.)

## Done when

The version is tagged, the source repo produced a valid `restored-packages`
artifact, the PackageMirror sync succeeded (release + schemas + state updated),
and the synced qaas-docs PR is open. Verify against the actual workflow run, not
assumption.

## Failure modes

- Tagging without the `restore-artifact-metadata.json` → mirror skips the repo.
- Assuming the mirror auto-ran; confirm the `sync-packages.yml` run.
- Hand-editing `packages/` or `schemas/` instead of letting the sync rebuild them.
````

- [ ] **Step 2: Validate (offline) + commit**

```bash
OFFLINE=1 ./scripts/validate-plugin.sh
git add skills/release-and-mirror/SKILL.md
git commit -m "Add release-and-mirror skill (PackageMirror pipeline)"
```

### Task 7: `find-qaas-knowledge` skill

**Files:**
- Create: `skills/find-qaas-knowledge/SKILL.md`

- [ ] **Step 1: Write the skill**

````markdown
---
name: find-qaas-knowledge
description: >-
  Use when you need to locate QaaS knowledge — which repo, which in-tree doc, or
  which live docs page covers a topic — before answering or editing. Enforces
  docs-or-silence: cite a source or stop. Keywords: where is, which repo, which
  package, which doc, find, locate, look up QaaS, documentation.
---

# Find QaaS Knowledge (docs-or-silence router)

Resolve any "where is X / which doc covers Y" question to a concrete source. Never
answer QaaS specifics from memory.

## Resolution order

1. **In-tree repo docs (authoritative for in-repo detail).** Every `TheSmokeTeam`
   repo has a root `CLAUDE.md` and per-project `project_specs.md`. For code-level
   questions, open the owning repo and read these first. Map of owners:
   - hook contracts, protocols, policies, serialization, providers, config loader,
     executions → `QaaS.Framework` (per-project `project_specs.md`).
   - a specific assertion/generator/probe/processor → the matching `QaaS.Common.*`.
   - runner/mocker behavior → `QaaS.Runner` / `QaaS.Mocker`.
   - release/mirror/schemas → `QaaS.PackageMirror`.
2. **Live docs (authoritative for user-facing config).** `https://docs.qaas.online/`
   (regenerated by `QaaS.Docs.Generator`). Per-hook `overview` / `yamlView` /
   `tableView` pages and `_generated/schemas/*` are ground truth for YAML shapes.
3. **Cross-repo seams** → this plugin's other skills (`qaas-platform-overview`,
   `add-framework-hook`, `extend-framework-core`, `release-and-mirror`).
4. **Not found?** State exactly what is missing and stop. Do not invent.

## Done when

You have named a concrete source (a repo file path or a docs URL) for the answer,
or explicitly reported what could not be found.

## Failure modes

- Answering from stale training memory instead of the live source.
- Pointing at this plugin for in-repo detail that belongs in a repo's CLAUDE.md.
````

- [ ] **Step 2: Validate (offline) + commit**

```bash
OFFLINE=1 ./scripts/validate-plugin.sh
git add skills/find-qaas-knowledge/SKILL.md
git commit -m "Add find-qaas-knowledge skill (docs-or-silence router)"
```

---

## Phase 5 — Slash commands

### Task 8: `/qaas-where` and `/qaas-release` commands

**Files:**
- Create: `commands/qaas-where.md`
- Create: `commands/qaas-release.md`

- [ ] **Step 1: Write `commands/qaas-where.md`**

```markdown
---
description: Route a QaaS platform task to the right repo(s) and skill — which repo to open, which CLAUDE.md to read, and whether it is a Type A or Type B change.
argument-hint: "<task>  e.g. 'add a Kafka retry assertion' | 'add an Oracle protocol' | 'cut a Framework release'"
---

Route this QaaS platform-development task: $ARGUMENTS

Apply the `qaas-platform-overview` skill's router and Type A/B decision gate:
1. Identify the owning repo(s) under https://github.com/TheSmokeTeam.
2. If it is an extension, classify Type A (reflection hook → `add-framework-hook`)
   vs Type B (compiled core → `extend-framework-core`).
3. Name the in-tree `CLAUDE.md` / `project_specs.md` to read first.
4. If anything is unknown, say what is missing — do not invent. (docs-or-silence)
```

- [ ] **Step 2: Write `commands/qaas-release.md`**

```markdown
---
description: Walk the QaaS release + PackageMirror pipeline for a version bump — source-repo CI contract, the mirror sync, family schemas, and the synced qaas-docs PR.
argument-hint: "[<repo and version>]  e.g. 'QaaS.Framework 2.4.0'"
---

Walk the QaaS release/mirror flow for: $ARGUMENTS

Apply the `release-and-mirror` skill. Confirm the source-repo CI contract
(restore into RestoredPackages, workflow_dispatch, stable-tag metadata,
`restored-packages` artifact), then the PackageMirror sync (release, regenerated
schemas, state, synced qaas-docs PR). Verify against the actual workflow run, not
assumption. Read QaaS.PackageMirror's README/CLAUDE.md for current rules.
```

- [ ] **Step 3: Validate (offline) + commit**

```bash
OFFLINE=1 ./scripts/validate-plugin.sh
git add commands/qaas-where.md commands/qaas-release.md
git commit -m "Add /qaas-where and /qaas-release commands"
```

---

## Phase 6 — Portable AGENTS.md generation

### Task 9: `build-agents-md.sh` generator

**Files:**
- Create: `scripts/build-agents-md.sh`

- [ ] **Step 1: Write the generator**

```bash
#!/usr/bin/env bash
# Renders all SKILL.md bodies into a single portable AGENTS.md for non-CC agents.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/AGENTS.md"

# Strip YAML frontmatter (first --- ... --- block) from a file.
strip_fm() { awk 'BEGIN{f=0;done=0} NR==1&&$0=="---"{f=1;next} f&&!done&&$0=="---"{done=1;next} {print}' "$1"; }

{
  echo "<!-- GENERATED by scripts/build-agents-md.sh from skills/*/SKILL.md — DO NOT EDIT. Run the script to regenerate. -->"
  echo
  echo "# QaaS Platform Development — Agent Guide"
  echo
  echo "Portable bundle of the qaas-platform-dev plugin's skills, for AI agents"
  echo "other than Claude Code (Cursor, Copilot, Codex, Gemini). Source of truth is"
  echo "\`skills/*/SKILL.md\`; regenerate with \`scripts/build-agents-md.sh\`."
  echo
  # Overview first, then the rest in stable alphabetical order.
  order=("qaas-platform-overview" "add-framework-hook" "extend-framework-core" "release-and-mirror" "find-qaas-knowledge")
  for name in "${order[@]}"; do
    f="$ROOT/skills/$name/SKILL.md"
    [ -f "$f" ] || continue
    echo "---"
    echo
    strip_fm "$f"
    echo
  done
} > "$OUT"

echo "build-agents-md: wrote $OUT"
```

- [ ] **Step 2: Make executable and generate**

Run: `chmod +x scripts/build-agents-md.sh && ./scripts/build-agents-md.sh`
Expected: `build-agents-md: wrote .../AGENTS.md`

- [ ] **Step 3: Verify AGENTS.md contains all five skills and no frontmatter `name:` lines**

Run: `grep -c '^# ' AGENTS.md && ! grep -q '^name: ' AGENTS.md && echo "FM-STRIPPED-OK"`
Expected: a count ≥ 6 (title + per-skill headings) and `FM-STRIPPED-OK`

- [ ] **Step 4: Commit**

```bash
git add scripts/build-agents-md.sh AGENTS.md
git commit -m "Add AGENTS.md generator and generated portable bundle"
```

---

## Phase 7 — CI + README + final validation

### Task 10: CI workflow (validation + AGENTS.md drift check)

**Files:**
- Create: `.github/workflows/validate.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: validate
on:
  push:
    branches: ["**"]
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate plugin (manifests, frontmatter, URL liveness)
        run: ./scripts/validate-plugin.sh
      - name: AGENTS.md is in sync
        run: |
          ./scripts/build-agents-md.sh
          if ! git diff --quiet -- AGENTS.md; then
            echo "AGENTS.md is stale — run scripts/build-agents-md.sh and commit." >&2
            git --no-pager diff -- AGENTS.md
            exit 1
          fi
```

- [ ] **Step 2: Run both checks locally to confirm they pass**

Run: `./scripts/validate-plugin.sh && ./scripts/build-agents-md.sh && git diff --quiet -- AGENTS.md && echo "CI-CHECKS-PASS"`
Expected: `validate-plugin: OK`, `build-agents-md: wrote ...`, then `CI-CHECKS-PASS`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/validate.yml
git commit -m "Add CI: plugin validation + AGENTS.md drift check"
```

### Task 11: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write the README**

```markdown
# qaas-dev-claude-plugins

A Claude Code plugin (+ portable `AGENTS.md`) that makes any AI agent productive
at **building the QaaS platform** — the [TheSmokeTeam](https://github.com/TheSmokeTeam)
C#/.NET monorepo. It owns the cross-repo seams (repo map, framework dependency
graph, release ripple, the Type A vs Type B extension distinction) and delegates
in-repo detail to each repo's own `CLAUDE.md`.

> Distinct from `eldarush/qaas-copilot` (which is for *using* QaaS to author
> tests). This plugin is for *developing the platform itself*.

## Install (Claude Code)

```text
/plugin marketplace add TheSmokeTeam/qaas-dev-claude-plugins
/plugin install qaas-platform-dev@qaas-dev-claude-plugins
```

## What you get

| Surface | Purpose |
|---|---|
| `qaas-platform-overview` (always-on skill) | Repo map, dependency graph, release ripple, repo router, Type A/B decision gate. |
| `add-framework-hook` skill | Add a Type A reflection hook (assertion/generator/probe/processor → `Common.*`). |
| `extend-framework-core` skill | Add a Type B compiled-core member (protocol/serializer/policy → `QaaS.Framework`). |
| `release-and-mirror` skill | The PackageMirror pipeline + source-repo CI contract. |
| `find-qaas-knowledge` skill | Docs-or-silence knowledge router. |
| `/qaas-where <task>` | Route a task to the right repo + skill. |
| `/qaas-release [<repo> <version>]` | Walk the release/mirror flow. |

## Other AI agents

Non-Claude-Code agents can ingest [`AGENTS.md`](./AGENTS.md), generated from the
skills. Regenerate after editing any skill:

```bash
./scripts/build-agents-md.sh
```

## Development

```bash
./scripts/validate-plugin.sh      # manifests, frontmatter, URL liveness (OFFLINE=1 to skip URLs)
./scripts/build-agents-md.sh      # regenerate AGENTS.md
```

CI runs both on every push (`.github/workflows/validate.yml`).
```

- [ ] **Step 2: Final full validation (online) + AGENTS.md sync**

Run: `./scripts/validate-plugin.sh && ./scripts/build-agents-md.sh && git diff --quiet -- AGENTS.md && echo ALL-GREEN`
Expected: `validate-plugin: OK` … `ALL-GREEN`

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "Add README with install and usage"
```

---

## Self-Review (completed by plan author)

**Spec coverage:**
- §1 purpose/niche → README + plugin.json description + overview skill mission. ✓
- §2 principles (own the seams, point to live sources, single source→two outputs, docs-or-silence, sharp descriptions) → overview Constitution + all skill bodies + AGENTS.md generator. ✓
- §3 cross-repo gaps → overview skill (map, graph, ripple, router). ✓
- §4 Type A/B (incl. all three Type B families + discriminator) → overview decision gate + add-framework-hook + extend-framework-core. ✓
- §5 structure → File Structure table + Tasks 1–11 create every listed file. ✓
- §6 skills (all five, with the exact trigger descriptions) → Tasks 3–7. ✓
- §7 commands + marketplace install → Task 8 + README. ✓
- §8 auto-invocation (skill + sharp descriptions, no hooks) → no hook tasks; always-on overview created. ✓
- §9 testing (manifest/frontmatter validation, URL liveness, AGENTS.md sync) → Tasks 1, 9, 10. ✓
- §10 out-of-scope → nothing in plan adds coding-standards/test-authoring/memory-loop. ✓

**Placeholder scan:** every step contains the full file content or an exact command + expected output. No TBD/TODO/"similar to". ✓

**Type consistency:** skill directory names match their frontmatter `name:` everywhere (`qaas-platform-overview`, `add-framework-hook`, `extend-framework-core`, `release-and-mirror`, `find-qaas-knowledge`); the AGENTS.md `order=()` array uses those exact names; the validation script checks `name == directory`; commands reference the skills by those names. ✓
