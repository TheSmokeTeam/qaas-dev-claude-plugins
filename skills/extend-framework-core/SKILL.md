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
| **Protocols** | `QaaS.Framework.Protocols` | Factories (`ReaderFactory`/`SenderFactory`/`TransactorFactory`/`FetcherFactory` + chunk variants) keyed by `SerializationType` + a protocol-specific config record. A closed set covering messaging, SQL/NoSQL, storage, HTTP/gRPC, and observability backends (e.g. Kafka, RabbitMQ, HTTP, gRPC, MS-SQL, PostgreSQL, Oracle, Trino, Redis, MongoDB, Elastic, Prometheus, S3, SFTP, Socket, IBM MQ) plus the Mocker proxy the Runner uses to drive a paired mocker. Confirm the live set in `QaaS.Framework.Protocols/project_specs.md` — do not trust a count. Abstractions: `IReader`/`ISender`/`ITransactor`/`IFetcher`/`IChunkReader`/`IChunkSender`/`IConnectable`. |
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
