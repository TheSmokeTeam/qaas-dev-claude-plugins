# QaaS Ecosystem Map

Use this reference for stable cross-repository relationships. Confirm current
repository membership, project names, package versions, and implementation
mechanics from live sources before relying on them.

## Platform layers

| Layer | Stable responsibility | Typical evidence |
|---|---|---|
| `QaaS.Framework` | Core contracts, configuration, protocols, serialization, policies, providers, and execution | Root `CLAUDE.md`, project `project_specs.md`, source |
| `QaaS.Common.*` | Separately shipped reflection hooks implementing Framework SDK contracts | Owning Common repository instructions and siblings |
| Runner and Mocker | Executables and their communication boundary | Runner/Mocker instructions, source, package references |
| PackageMirror | Restored-package aggregation, generated schemas, releases, and docs handoff | PackageMirror instructions and workflows |
| Docs | Deterministic generation and published user-facing documentation | Generator repository, `qaas-docs`, `docs.qaas.online` |

The organization may contain templates, samples, and standalone tools that are
not part of a requested platform change. Do not infer ownership from a repository
name alone.

## Framework dependency direction

The stable dependency direction is:

`Infrastructure -> Serialization, Configurations -> SDK -> Protocols, Policies -> Providers -> Executions`

Treat this as an orientation map, not proof of a current project reference. Use
the knowledge graph and project files for the exact live edge.

## Extension ownership gate

The discriminator is who can extend the family, not whether the implementation
uses a factory, switch, or builder.

| | Type A: reflection hook | Type B: compiled core |
|---|---|---|
| Extensible by | An external assembly/package | The platform team by editing Framework |
| Typical capability | Assertion, generator, probe, processor | Transport/protocol, serialization format, runtime policy |
| Runtime model | Discovered by Framework provider behavior | Compiled into an owning Framework project |
| Implementation owner | Matching `QaaS.Common.*` repository | `QaaS.Framework` |
| Release shape | Common package -> mirror -> docs | Framework release -> downstream rebuilds -> mirror -> docs |

If live evidence does not prove the ownership model, classify it as
`undetermined`; do not route from keywords alone.

## Release ripple

A Framework change normally requires a new Framework package version, updates
to affected downstream package references in dependency order, rebuilt restore
artifacts, a PackageMirror sync, regenerated schemas or catalogs where affected,
and the documentation handoff. A Common hook change begins with that Common
package rather than a Framework edit.

The exact tracked repositories, dependency tiers, CI contract, and workflow
names are volatile. Obtain them from `release-and-mirror`, PackageMirror's live
instructions, project files, and current workflow runs.

## Authority order

1. Owning repository `CLAUDE.md`, then relevant `project_specs.md` and source.
2. `docs.qaas.online` for published configuration and user-facing behavior.
3. `qaas-knowledge-graph` for cross-repository ownership, dependency, impact,
   path, and call-flow evidence.
4. This plugin for stable lifecycle and cross-repository architecture.

If these sources disagree, report the conflict and stop before planning or
editing.
