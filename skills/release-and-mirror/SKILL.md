---
name: release-and-mirror
description: >-
  Plan or execute an explicitly authorized QaaS package release, downstream
  dependency ripple, restored-package handoff, PackageMirror sync, generated
  schemas, and qaas-docs update. Use for release, publish, tag, version bump,
  NuGet, PackageMirror, restored-packages, schema generation, or docs sync.
---

# Release and Mirror QaaS Packages

Own release execution only. A release is a distinct externally visible action;
planning or implementation approval does not authorize tagging or publishing
unless the approved scope says so.

## Entry gate

1. Require or build a current Know QaaS Context Brief with
   `qaas-platform-overview`.
2. Read the current source repository instructions and
   `QaaS.PackageMirror`'s `CLAUDE.md`, `README.md`, and workflows.
3. Confirm explicit release authorization, target repositories, versions,
   dependency order, and rollback expectation.
4. For a planned change, require a verified implementation and explicit
   developer authorization for the exact release targets in the current
   conversation or a trusted handoff.
5. Stop rather than infer a package version, tag, workflow, tracked repository,
   artifact contract, or downstream edge.

## Workflow

1. **Resolve the live dependency graph.** Inspect current project package
   references and use the knowledge graph for cross-repository impact. Build the
   release tiers from evidence; do not use a hardcoded repository list.
2. **Validate each source repository.** Confirm its stable-tag convention,
   restore location, metadata file, artifact name, manual trigger, and required
   build/test checks from live instructions and workflows.
3. **Release in dependency order.** Publish upstream packages before consumers,
   and wait for each required package/artifact result before moving to its
   dependants. Independent repositories in one verified tier may run in parallel.
4. **Run or observe PackageMirror.** Verify the actual sync run rebuilt the
   expected package tree and generated artifacts, updated state, and created the
   documented release/docs handoff.
5. **Verify outcomes.** Capture tag/release URLs, workflow runs, artifacts,
   versions, schema/catalog changes, and the documentation PR. Never report an
   assumed run as successful.
6. **Handle failure explicitly.** Stop the cascade on an upstream failure and
   report the last known-good stage plus the documented retry or rollback path.

The exact PackageMirror mechanics, tracked sources, dependency tiers, generated
files, and workflow names are volatile. Keep them in live repository evidence,
not this plugin.

## Done when

Every authorized source release and downstream bump has observed build/artifact
evidence, the mirror outcome is verified, and the generated documentation
handoff is complete—or the precise remaining stage and blocker are reported.
