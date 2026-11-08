---
name: extend-framework-core
description: >-
  Apply the Type B implementation overlay for a QaaS protocol or transport,
  serialization format, policy, or other closed Framework family after
  implement-qaas-change validates an approved plan. Use when live evidence
  proves the capability must be compiled into and released from QaaS.Framework.
---

# Extend Type B Framework Core

Use this domain overlay through `implement-qaas-change`. If no current approved
plan has passed that skill's revision and freshness gates, stop there.

## Stable architecture

A Type B capability is owned by the platform team and cannot be added by dropping
an external assembly. Adding a member requires an edit to the owning Framework
project and a new Framework release. Internal wiring may be a factory, switch,
builder, or another verified pattern; that mechanism is not the Type A/Type B
discriminator.

## Execution overlay

1. Confirm from the live Framework `CLAUDE.md`, target `project_specs.md`, source,
   and tests that the family remains closed and identify every current selection
   point and forbidden dependency rule.
2. Follow the approved sequence in order: establish the planned failing
   behavioral or selection test, implement the smallest member and registration
   changes by following a verified sibling, then run focused and full Framework
   checks.
3. Verify configuration/serialization compatibility, every relevant selection
   path, invalid-input behavior, and affected callers named by the plan.
4. Preserve the approved release ripple: Framework version, affected downstream
   package references and rebuild order, restore artifacts, PackageMirror,
   schemas/catalogs, documentation, and rollback.

Do not hardcode current family members, factory names, switch locations,
interfaces, package versions, or downstream repository lists in this plugin.
Those facts must come from the live Framework and consumer repositories.

## Domain completion

The compiled-core change, selection paths, tests, Framework checks, and downstream
verification match the approved plan, and release work is either verified as
authorized or handed off explicitly.
