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
