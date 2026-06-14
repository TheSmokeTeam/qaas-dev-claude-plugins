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
