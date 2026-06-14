# Design — `qaas-platform-dev` plugin (+ portable AGENTS.md bundle)

**Date:** 2026-06-14
**Repo:** `TheSmokeTeam/qaas-dev-claude-plugins`
**Status:** Approved design — ready for implementation planning

## 1. Purpose & niche

A Claude Code plugin (plus a portable `AGENTS.md` bundle for non-CC agents) that
makes any AI agent productive at **building the QaaS platform** — the
`TheSmokeTeam` C# / .NET 10 monorepo-of-repos (Framework, Runner, Mocker,
Docs.Generator, PackageMirror, Common.\*, steak, qaas-docs).

This is deliberately distinct from the two existing `eldarush` plugins:

- **`eldarush/qaas-copilot`** — for *end-users of QaaS* authoring Runner/Mocker
  test YAML and custom hooks against a system-under-test (airgapped, snapshot
  Fact Base). **This plugin does NOT overlap it.**
- **`eldarush/firefly-workspace`** — a domain-agnostic self-improving
  engineering harness. We borrow its *format* (contract-style skills,
  docs-or-silence discipline) but none of its content.

This plugin's audience: **Smoke-team developers contributing to the QaaS C#
codebase itself.**

## 2. Guiding principles

1. **Own the seams, not the parts.** The plugin holds only knowledge that lives
   *between* repos. Anything inside a single repo is delegated to that repo's
   in-tree `CLAUDE.md` / `project_specs.md` / live `docs.qaas.online`. Every repo
   already ships an excellent root `CLAUDE.md` and per-project `project_specs.md`;
   re-documenting their internals here would rot instantly. The plugin's recurring
   instruction is *"clone/open repo X and read its CLAUDE.md first."*
2. **Point to live sources, never snapshot.** No copied schemas or per-hook docs.
   The team auto-generates docs via `QaaS.Docs.Generator` → `qaas-docs` → GitHub
   Pages; the plugin teaches the agent to fetch live detail on demand.
3. **Single source → two outputs.** Skill markdown is the source of truth; a build
   script renders a portable `AGENTS.md` so Cursor/Copilot/Codex/Gemini users get
   identical knowledge. One place to edit; both consumers stay in sync.
4. **Docs-or-silence.** Skills must never invent a repo name, package, config key,
   or CI step — cite the in-tree `CLAUDE.md` or live docs, else stop and ask.
5. **Reliable auto-invocation via sharp descriptions.** Claude Code loads only each
   skill's `name` + `description` at session start and model-invokes by matching
   the request against those one-liners. Descriptions must be concrete and
   keyword-rich. One always-on overview skill is the reliability backstop.

## 3. The cross-repo gaps this plugin fills

No single repo's `CLAUDE.md` can know these:

1. **Org map & dependency topology** — 18 repos, the framework dep graph
   (`Infrastructure → Serialization, Configurations → SDK → Protocols, Policies →
   Providers → Executions`), and the **release ripple** (a change in
   `QaaS.Framework.SDK` flows through `Common.*` → `PackageMirror` → `qaas-docs`).
2. **Cross-repo workflows** — e.g. "add a new assertion" spans `Common.Assertions`
   (impl + tests) → restore/bump → `PackageMirror` sync → `qaas-docs` regen.
3. **Release / package-mirror / docs pipeline** — the `restored-packages` artifact
   contract, family schemas, the synced `qaas-docs` PR.
4. **"Where do I start" routing** — given a task, which repo(s) to open and which
   in-tree doc to read first.

## 4. The two extension mechanisms (core architectural knowledge)

Verified from `QaaS.Framework` source. The discriminator is **extensibility /
ownership**, NOT internal selection wiring.

### Type A — reflection hooks, externally extensible
- Contracts in `QaaS.Framework.SDK`: `IGenerator`, `IAssertion`, `IProbe`,
  `IProcessor`.
- Discovered at **runtime** by `QaaS.Framework.Providers` scanning assemblies
  (entry asm + `AppDomain` + every `*.dll` under `BaseDirectory`), instantiated by
  name via `ByNameObjectCreator`, **selected by string name in YAML**.
- Anyone can add one by dropping a DLL — they live in separate `QaaS.Common.*`
  NuGet packages: **Assertions, Generators, Probes, Processors**.
- No framework change. Release ripple: new/bumped `Common.*` → restore →
  PackageMirror → qaas-docs.

### Type B — compiled into the framework core, team-only, closed set
- Adding one means **editing `QaaS.Framework` itself** + a new framework release
  that ripples to all downstream repos. No DLL-drop / reflection path exists.
- Members (verified from source), each with a *different* internal selection
  mechanism:
  - **Protocols** (`QaaS.Framework.Protocols`) — factory-selected
    (`ReaderFactory`/`SenderFactory`/…) keyed by `SerializationType` + a
    protocol-specific config record. Closed set of 15+ (Kafka, RabbitMQ, HTTP,
    gRPC, MS-SQL, PostgreSQL, Oracle, Trino, Redis, MongoDB, Elastic, Prometheus,
    S3, SFTP, Socket, IBM MQ, Mocker proxy).
  - **Serialization** (`QaaS.Framework.Serialization`) — serializer/deserializer
    factories (Binary, Json, MessagePack, Xml, Yaml, ProtobufMessage, XmlElement).
  - **Policies** (`QaaS.Framework.Policies`) — selected by a typed `switch` over
    `IPolicyConfig` in `PolicyBuilder.Configure`/`Build` (a `default: throw`
    closed set), chained via `Add` in ascending `Index` order (`CountPolicy`,
    `TimeoutPolicy`, `LoadBalancePolicy`, `IncreasingLoadBalancePolicy`,
    `AdvancedLoadBalancePolicy`).

**Key insight:** internal wiring differs across Type B families (factory vs
switch+builder), so "factory-selected" is the WRONG discriminator — it makes
Policies look ambiguous when they're clearly Type B. The only clean test:
*can an external user add one via reflection/DLL-drop (A), or must you edit +
re-release the framework core (B)?*

## 5. Structure

```
qaas-dev-claude-plugins/
├── .claude-plugin/
│   ├── plugin.json                 # plugin manifest
│   └── marketplace.json            # enables `/plugin marketplace add TheSmokeTeam/...`
├── skills/
│   ├── qaas-platform-overview/SKILL.md   # ALWAYS-ON
│   ├── add-framework-hook/SKILL.md        # Type A
│   ├── extend-framework-core/SKILL.md     # Type B
│   ├── release-and-mirror/SKILL.md
│   └── find-qaas-knowledge/SKILL.md
├── commands/
│   ├── qaas-where.md               # /qaas-where <task>
│   └── qaas-release.md             # /qaas-release
├── AGENTS.md                       # GENERATED portable bundle (do-not-edit header)
├── scripts/
│   ├── build-agents-md.sh          # skills → AGENTS.md
│   └── validate-plugin.sh          # frontmatter + manifest + URL liveness checks
└── README.md                       # install + usage for the team
```

## 6. The skills

All follow the eldarush **contract format**: a done-rubric, failure modes, and
docs-or-silence discipline. All delegate in-repo detail to that repo's own
`CLAUDE.md` / `project_specs.md`.

| Skill | Fires on (description gist) | Owns |
|---|---|---|
| **qaas-platform-overview** *(always-on)* | "Use at the start of ANY work in the QaaS platform codebase / TheSmokeTeam repos." | 18-repo map, framework dep graph, release ripple, repo router, **and the Type A vs Type B decision gate** (the §4 comparison: what differs, why, use cases) that routes to the two implementation skills. |
| **add-framework-hook** | "Adding a new assertion/generator/probe/processor to QaaS (reflection hook, Common.\* package). Keywords: new hook, IAssertion, IGenerator, IProbe, IProcessor, add assertion, custom hook, Common.\* package." | Type A flow: `Common.*` (impl + tests) → restore/bump → PackageMirror sync → qaas-docs regen. |
| **extend-framework-core** | "Adding a new protocol/transport/broker/DB, serializer/serialization format, or policy — compiled into QaaS.Framework. Keywords: new protocol, transport, broker, serializer, policy, factory, edit QaaS.Framework." | Type B flow: which framework project + its selection mechanism (factory vs switch+Index), then the framework-release ripple. Enumerates the current Type B set by pointing at `QaaS.Framework`'s CLAUDE.md so it never goes stale. |
| **release-and-mirror** | "Releasing/publishing QaaS packages, version bumps, PackageMirror sync, family schemas, synced qaas-docs PR. Keywords: release, restored-packages artifact, NuGet, schema, version bump." | The operational pipeline + the source-repo CI contract (restore into `RestoredPackages`, `workflow_dispatch`, stable-tag metadata, `restored-packages` artifact). |
| **find-qaas-knowledge** | "Where is X in QaaS / which repo or doc covers Y. Keywords: where is, which package, which repo, docs." | Docs-or-silence router across in-tree CLAUDE.md, project_specs.md, and live docs.qaas.online. |

The repo doubles as its own single-plugin **marketplace** (`marketplace.json`), so
the team installs with `/plugin marketplace add TheSmokeTeam/qaas-dev-claude-plugins`
then `/plugin install`.

## 7. Commands & portability

- `/qaas-where <task>` and `/qaas-release` — thin deterministic wrappers that
  invoke the matching skill, for devs who prefer typing a command over relying on
  auto-fire.
- `scripts/build-agents-md.sh` concatenates the five `SKILL.md` bodies into a
  single `AGENTS.md` with a "generated — do not edit" header. Committed to the
  repo so non-CC agents (Cursor/Copilot/Codex/Gemini) ingest identical knowledge.

## 8. Auto-invocation model (decided)

**Skill + sharp descriptions, no hooks.** One always-on `qaas-platform-overview`
skill (broad "use when working in QaaS platform" description) loads the org map +
A/B decision gate every session; trigger-rich descriptions on the rest let the
model invoke them by intent. No `SessionStart` hook unless the overview proves
unreliable in practice.

## 9. Testing & freshness

- **Manifest/frontmatter validation** — `plugin.json` / `marketplace.json` parse;
  every skill has valid frontmatter (`name` + `description`). (`validate-plugin.sh`)
- **Repo + docs URL liveness** — assert every `TheSmokeTeam` repo and docs URL the
  skills reference still resolves (catches the org drifting out from under the
  plugin).
- **AGENTS.md in sync** — CI regenerates it and fails if the committed copy
  differs, so the portable bundle can't silently rot.
- No "run real QaaS" corpus (unlike qaas-copilot): this plugin asserts
  *navigation*, not *generated-test correctness*, so liveness checks are the right
  bar.

## 10. Out of scope (YAGNI)

- Coding-standards / code-review skills (per-repo CLAUDE.md already covers this).
- Snapshotting docs or schemas into the plugin.
- A self-improving memory/lessons loop (firefly's domain; not this plugin's job).
- Any test-authoring capability (qaas-copilot's domain).
