---
name: add-framework-hook
description: >-
  Apply the Type A implementation overlay for a QaaS assertion, generator,
  probe, or processor after implement-qaas-change validates an approved plan.
  Use when live evidence proves the capability is an externally extensible,
  reflection-discovered SDK hook shipped from a QaaS.Common.* package rather
  than compiled into QaaS.Framework.
---

# Add a Type A Reflection Hook

Use this domain overlay through `implement-qaas-change`. If no current approved
plan has passed that skill's approval and source-freshness gates, stop there.

## Stable architecture

A Type A capability implements a public Framework SDK hook contract in the
matching `QaaS.Common.*` package and is discovered at runtime. External packages
can add one without editing Framework core. If live evidence shows that the
platform team must edit and re-release Framework to add the member, route to
`extend-framework-core` instead.

## Execution overlay

1. Confirm the hook family, SDK contract, owning Common repository, and current
   discovery/configuration convention from the live repository instructions and
   Framework provider evidence.
2. Follow the approved implementation sequence in order: establish the planned
   failing behavioral test, implement the smallest contract/configuration
   change by following a verified sibling, then run focused and full repository
   checks.
3. Confirm that the implementation depends only on the supported public SDK
   surface and that its runtime name/configuration shape is covered by tests.
4. Preserve the approved release handoff: Common package publication, restored
   package evidence, PackageMirror sync, generated schema/catalog impact, and
   documentation update where applicable.

Do not hardcode current discovery priorities, base classes, signatures, package
versions, or hook inventories from this plugin. Those facts belong to the live
Common and Framework repositories.

## Domain completion

The hook, configuration shape, behavioral tests, and repository checks match the
approved plan, and the Common-package release work is either verified as
authorized or handed off explicitly.
