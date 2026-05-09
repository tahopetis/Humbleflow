<!-- HARNESS-TEMPLATE: Project-specific sections use {{PLACEHOLDER}} syntax -->

# Architecture — {{PROJECT_NAME}}

> This is the project-specific domain map. For the generic architectural rules
> (layers, dependency direction, cross-cutting concerns), see:
> `.pi/skills/humbleflow/references/architecture.md`.

## Overview

{{PROJECT_NAME}} is a {{PROJECT_DESCRIPTION}}.

**Status:** {{PROJECT_STATUS}}

{{DOMAIN_ARCHITECTURE}}

## Shared Package (`shared/`)

Cross-domain utilities. These have 100% test coverage and must not import from any
domain.

**Expected utilities:**
- `concurrency.ts` — `mapWithConcurrency` and other async primitives
- `pagination.ts` — cursor-based pagination helpers
- `result.ts` — `Result<T, E>` type for explicit error handling
- `datetime.ts` — date/time formatting and relative time
- `id.ts` — ID generation (ULID, not UUID — sortable, URL-safe)
- `validation.ts` — common Zod refinements (email, URL, non-empty, etc.)

## Providers (`providers/`)

Provider implementations are the *how*, not the *what*. Domains define interfaces;
providers implement them. This is dependency inversion at the application boundary.

| Provider | Interface defined in | Implementation lives in | Provides |
|----------|---------------------|------------------------|----------|
| Auth | `providers/types/auth.ts` | `providers/auth/` | User identity, session tokens, permissions |
| Telemetry | `providers/types/telemetry.ts` | `providers/telemetry/` | OpenTelemetry traces, metrics, logs |
| Logging | `providers/types/logging.ts` | `providers/logging/` | Structured JSON logger (injected, not global) |
| Feature Flags | `providers/types/feature-flags.ts` | `providers/feature-flags/` | Flag evaluation, gradual rollout |
| Connector | `providers/types/connector.ts` | `providers/connectors/` | External API adapters (Slack, GitHub, etc.) |

## Application Root (`app/`)

Wires everything together. Responsibilities:
- **Bootstrap:** Initialize providers, connect to databases, load config.
- **Routing:** Map URL paths to domain runtimes.
- **Middleware:** Auth checks, telemetry instrumentation, error boundaries.
- **Composition:** Wire domain services together, inject providers.

The app root is the only place where concrete provider implementations are
imported. Domains only reference provider *interfaces* through their Config layer.

## Dependency Rules

### Allowed Edges

```
app/ → any domain (runtime, ui layers only)
domain-ui → domain-runtime → domain-service → domain-repo → domain-config → domain-types
domain-types → shared/
shared/ → (standard library only)
providers/ → shared/, external libraries
```

### Forbidden Edges

```
domain-A/service → domain-B/service        (cross-domain service import)
domain/types → domain/service               (backward import)
domain/ui → domain/repo                     (skip-layer import)
domain/anything → providers/auth           (direct provider import — use Config layer)
domain/anything → any domain without typed interface  (cross-domain without DI)
shared/ → any domain                       (shared must not know about domains)
```

### Cross-Domain Communication

When Domain A needs something from Domain B:

1. Domain B exposes a typed interface in its `types/` layer.
2. Domain A depends on that interface (type-only import).
3. The actual implementation is injected through Domain A's Config layer at
   application bootstrap time.

This is dependency inversion: both domains depend on abstractions (types), not
on each other's implementations.

{{PROJECT_DECISIONS}}
