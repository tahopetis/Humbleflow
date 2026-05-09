# Architecture — Layered Domain Model

> See also: `docs/architecture.md` for the project-specific domain map.
> This document defines the architectural *rules*. The project-specific doc
> defines the architectural *instance*.

## The Rule: Fixed Layered Architecture

Every business domain in the codebase follows this layer stack:

```
┌────────────────────────────────────┐
│                 UI                 │  ← User-facing components, pages, views
├────────────────────────────────────┤
│              Runtime               │  ← App bootstrap, routing, middleware
├────────────────────────────────────┤
│              Service               │  ← Business logic, orchestration
├────────────────────────────────────┤
│               Repo                 │  ← Data access, persistence
├────────────────────────────────────┤
│              Config                │  ← Domain configuration, feature flags
├────────────────────────────────────┤
│              Types                 │  ← Schemas, types, constants
└────────────────────────────────────┘
```

## Dependency Direction

**Code may only depend "forward" (downward) through the layers.**

```
Types ← Config ← Repo ← Service ← Runtime ← UI
```

A file in `Service` may import from `Repo`, `Config`, or `Types`.
A file in `Repo` may import from `Config` or `Types`.
A file in `Types` may not import from anything except standard libraries and shared utilities.

**Backward imports are forbidden.** `Types` importing from `Service` is a violation.
This is mechanically enforced by `tools/lint-boundaries.py`.

## Cross-Domain Dependencies

Domains are independent. One domain's `Service` may not import from another domain's `Service`.

**Allowed cross-domain patterns:**
- Domain A's `Service` calls Domain B's `Service` through a typed interface defined
  in Domain B's `Types` layer (dependency inversion).
- Domains share types through a `shared/` package (only types and constants).

**Forbidden:**
- Direct import of another domain's `Repo`, `Config`, `Service`, `Runtime`, or `UI`.
- Circular dependencies between domains.

## Cross-Cutting Concerns

Cross-cutting concerns (auth, connectors, telemetry, feature flags, logging) enter
each domain through a single explicit interface: **Providers**.

```
┌──────────────────────────────────────────┐
│               Providers                   │
│  Auth │ Telemetry │ Logging │ Connectors  │
└──────┬──────┬──────────┬──────────┬───────┘
       │      │          │          │
       ▼      ▼          ▼          ▼
    ┌──────────────────────────────────┐
    │         Domain Layers            │
    └──────────────────────────────────┘
```

A domain does not import `auth` directly. It receives an `AuthProvider` interface
through its `Config` layer. The actual implementation is injected at runtime.

## Shared Utilities

Code that is used by multiple domains lives in a `shared/` package. Shared utilities:
- Must have 100% test coverage.
- Must be tightly integrated with OpenTelemetry instrumentation.
- Must not import from any domain.
- Should be "boring" — simple, composable, stable APIs.

If a third-party library does something simple that can be implemented in-house with
better instrumentation and test coverage, prefer in-house. The `p-limit` → custom
`mapWithConcurrency` example from the Harness article is a canonical case.

## File Organization

```
src/
├── domains/
│   ├── <domain-name>/
│   │   ├── types/          # Schemas, types, constants
│   │   ├── config/         # Domain configuration
│   │   ├── repo/           # Data access
│   │   ├── service/        # Business logic
│   │   ├── runtime/        # Bootstrap, routing
│   │   └── ui/             # Components, pages
│   └── ...
├── shared/                 # Cross-domain utilities
├── providers/              # Provider implementations
└── app/                    # Application root (orchestrates domains)
```

## Validation Rules (enforced by `lint-boundaries.py`)

1. No file imports a layer above its own layer within the same domain.
2. No file imports from another domain's layers (except shared types).
3. No circular imports between any files.
4. All cross-cutting concerns are accessed through Providers — no direct imports of
   `auth`, `telemetry`, `logging`, or `connectors` from domain code.
5. Shared utilities import only from standard library and other shared utilities.
