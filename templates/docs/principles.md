# Golden Principles

> **System of record for codebase invariants.**
> This document defines the mechanical rules that keep the Humbleflow codebase legible,
> consistent, and maintainable in a fully agent-driven development environment. Every
> principle here is enforced by `tools/lint-golden.py`. Violations block pull requests.
> The linter output includes remediation instructions — read them and fix the violation.
> Do not work around the linter.
>
> **Related:** The concise agent reference at `.pi/skills/humbleflow/references/golden-principles.md`
> is derived from this document. This document is authoritative.

---

## Principle 1: Parse, Don't Validate

### Rule

Data entering the system must be **parsed** into typed schemas at the boundary. Never
probe data shapes or guess field types deep in the codebase.

### Why This Matters

"Parse, don't validate" is a well-established principle (see
[Alexis King's essay](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)).
In an agent-generated codebase, the cost of violating it is amplified:

- **Type information loss.** When data is validated (checked) rather than parsed
  (transformed into typed structures), the type system doesn't know the shape.
  Downstream code must re-validate or guess, leading to defensive programming.

- **Silent failures at a distance.** A shape change in an API response causes failures
  deep in service or UI code — far from the actual source of the data. Agents cannot
  trace the root cause without the full parse chain.

- **Agent confusion.** Agents pattern-match on code. When they see `any`, `as` casts,
  and optional chaining on external data, they replicate the pattern. The codebase
  accumulates YOLO-style probing that is impossible to mechanically enforce.

### How to Comply

1. **Define schemas at the boundary layer** (Types layer for types, Repo layer for
   persistence, Runtime layer for incoming requests).
2. **Use Zod schemas** or an equivalent typed parsing library. The specific library is
   not mandated — Zod is preferred by the agent and is the convention.
3. **Parse eagerly.** Parse as soon as data enters the system. Do not pass raw data
   between modules. The Repo layer should return fully typed domain objects, not raw
   database rows or API responses.
4. **Handle parse failures explicitly.** A failed parse must produce a typed error with
   context (which field failed, why, what was expected). Never silently fall back to
   a default value.
5. **Never use `as` casts on data of unknown provenance.** `as` casts are only
   acceptable at the boundary where a schema has already been applied, and even then,
   prefer `parse()` over `as` because `parse()` throws on mismatch.

### Violation Example

```typescript
// In Service layer — no schema, YOLO probing
async function getUserProfile(apiResponse: unknown) {
  const data = apiResponse as any;
  const name = data?.user?.profile?.name ?? "Unknown";
  const email = data?.user?.profile?.email ?? "";
  const plan = data?.user?.subscription?.plan ?? "free";
  return { name, email, plan };
}
```

**Why this is a violation:**
- `as any` throws away type information.
- Optional chaining on `unknown` data is YOLO probing.
- If the API changes the shape (e.g., `profile` → `userProfile`), this function
  silently returns defaults with no error.
- Agents reading this code cannot know the actual shape of `apiResponse`.

### Compliant Example

```typescript
// In Types layer — define the schema once
import { z } from "zod";

export const UserProfileResponseSchema = z.object({
  user: z.object({
    profile: z.object({
      name: z.string().min(1),
      email: z.string().email(),
    }),
    subscription: z.object({
      plan: z.enum(["free", "pro", "enterprise"]),
    }),
  }),
});

export type UserProfileResponse = z.infer<typeof UserProfileResponseSchema>;

// In Repo layer — parse at the boundary
async function fetchUserProfile(userId: string): Promise<UserProfileResponse> {
  const raw = await api.get(\`/users/\${userId}\`);
  return UserProfileResponseSchema.parse(raw);
}

// In Service layer — fully typed, no guessing
async function getUserDisplayInfo(userId: string) {
  const profile = await fetchUserProfile(userId);
  return {
    name: profile.user.profile.name,
    email: profile.user.profile.email,
    plan: profile.user.subscription.plan,
  };
}
```

### Edge Cases

- **Partial data (PATCH requests).** Use `z.partial()` or `z.deepPartial()` to parse
  partial updates. Still parse — don't bypass the schema.
- **Union types.** Use `z.discriminatedUnion()` for data that can take multiple shapes.
  Parse the discriminator first, then the variant.
- **Unknown future fields.** Use `z.passthrough()` or `z.strict()` explicitly. Do not
  silently ignore extra fields — make the choice visible.
- **Very large responses.** If parsing a large response is too expensive, parse a
  "header" with the shape metadata, then lazily parse sections. The shape must still
  be defined.

---

## Principle 2: Shared Utilities Over Hand-Rolled Helpers

### Rule

When functionality is needed by multiple domains, it belongs in `shared/`, not
copy-pasted or re-implemented in each domain.

### Why This Matters

- **Invariant centralization.** Shared utilities keep invariants in one place. When a
  bug is fixed or instrumentation is added, all domains benefit immediately.
- **Consistency.** Hand-rolled copies diverge subtly — one domain adds a timeout,
  another adds retry logic, a third changes the concurrency model. The codebase
  accumulates N inconsistent implementations of the same concept.
- **Agent replication.** Agents pattern-match. If they see `processBatch` in three
  domains, they'll create a fourth copy rather than refactoring to shared.
- **Test coverage compounding.** A shared utility with 100% test coverage benefits
  every domain that uses it. N copies each with partial coverage do not compound.

### How to Comply

1. **Search before you write.** Check `src/shared/` for existing utilities before
   implementing in a domain.
2. **Extract at the second use.** If you need a function in two domains, extract it
   to `shared/`. Do not wait for three or four uses.
3. **Shared utilities must have 100% test coverage.** Non-negotiable. Shared code
   must be absolutely trustworthy.
4. **Shared utilities must be OpenTelemetry-instrumented.** Every shared utility
   should create spans, record attributes, and report errors.
5. **Favor "boring" APIs.** Simple, composable, stable interfaces. Avoid clever
   abstractions that are hard for agents to understand.

### Violation Example

```typescript
// In src/domains/billing/service/invoiceService.ts
async function processBatch<T>(items: T[], fn: (item: T) => Promise<void>, concurrency: number) {
  const chunks = [];
  for (let i = 0; i < items.length; i += concurrency) {
    chunks.push(items.slice(i, i + concurrency));
  }
  for (const chunk of chunks) {
    await Promise.all(chunk.map(fn));
  }
}

// In src/domains/notifications/service/notificationService.ts
async function processBatch<T>(items: T[], fn: (item: T) => Promise<void>, concurrency: number) {
  const queue = [...items];
  const workers = Array(concurrency).fill(null).map(async () => {
    while (queue.length) { const item = queue.shift()!; await fn(item); }
  });
  await Promise.all(workers);
}
```

**Why this is a violation:** Two implementations with different behaviors. Neither has
instrumentation or tests. An agent will copy the pattern to a third domain.

### Compliant Example

```typescript
// In src/shared/concurrency.ts
import { trace } from "@opentelemetry/api";

const tracer = trace.getTracer("shared/concurrency");

export async function mapWithConcurrency<T, R>(
  items: T[],
  fn: (item: T, index: number) => Promise<R>,
  concurrency: number,
): Promise<R[]> {
  return tracer.startActiveSpan("mapWithConcurrency", async (span) => {
    span.setAttribute("items.count", items.length);
    span.setAttribute("concurrency", concurrency);
    try {
      const results: R[] = new Array(items.length);
      let nextIndex = 0;
      const worker = async (): Promise<void> => {
        while (nextIndex < items.length) {
          const index = nextIndex++;
          results[index] = await fn(items[index], index);
        }
      };
      await Promise.all(Array(Math.min(concurrency, items.length)).fill(null).map(() => worker()));
      return results;
    } catch (error) {
      span.recordException(error);
      throw error;
    } finally { span.end(); }
  });
}
```

### When NOT to Extract to Shared

- **Single-domain logic** unlikely to be reused. Keep it in the domain.
- **Thin wrappers** around a third-party library without significant behavior added.
- **Domain-specific validation** that depends on domain types and rules.

---

## Principle 3: No YOLO Data Probing

### Rule

Never use `any`, unchecked `as` casts, or optional chaining (`?.`) to probe into data
whose shape is unknown. If you don't know the shape, parse it. If you can't parse it,
type it as `unknown` and handle the unknown case explicitly.

### Why This Matters

This principle is the operational side of "Parse, Don't Validate." While Principle 1
is about architecture (where parsing happens), Principle 3 is about code patterns
(what you must never do).

- **Silent failures.** `response?.data?.user?.name` silently produces `undefined` when
  the API changes. No error is thrown. The bug surfaces far from the source.
- **Untraceable bugs.** When an agent sees `undefined` in a value, it cannot determine
  whether the data was always missing, was removed, or was lost in a failed parse.
- **Compounding uncertainty.** One `any` cast cascades — through the Service, into the
  UI, making the entire chain type-unsafe.

### How to Comply

1. **Zod at the boundary.** All external data is parsed into a typed schema before
   entering domain logic.
2. **Never `any`.** Use `unknown` if the type is truly unknown, and narrow it with
   parsing or type guards.
3. **`as` casts only at boundaries.** Immediately after a Zod parse, and even then
   prefer the return value of `parse()`.
4. **Optional chaining audit.** Any `?.` on a value from an external source (API, DB,
   file, message queue) is a violation. Acceptable only on known-optional fields of
   parsed types.
5. **Explicit unknown handling.** When dealing with `unknown` data, use discriminated
   unions or exhaustive checks — never `as` or `any`.

### Violation Examples

```typescript
// VIOLATION: as any cast on external data
const config = (await fetchConfig()) as any;
if (config.featureFlags?.newDashboard) { ... }

// VIOLATION: deep optional chaining on unknown data
const userName = event?.payload?.data?.user?.name ?? "Unknown";

// VIOLATION: any in function signature
function processEvent(event: any): void { ... }

// VIOLATION: as cast to bypass type error
const userId = (request.body as UserRequest).user.id;
```

### Compliant Examples

```typescript
// COMPLIANT: Parse with Zod
const ConfigSchema = z.object({
  featureFlags: z.object({ newDashboard: z.boolean() }),
});
const config = ConfigSchema.parse(await fetchConfig());
if (config.featureFlags.newDashboard) { ... }

// COMPLIANT: Parse event at boundary
const EventSchema = z.object({
  payload: z.object({
    data: z.object({ user: z.object({ name: z.string() }) }),
  }),
});
const event = EventSchema.parse(rawEvent);
const userName = event.payload.data.user.name; // no ?., typed string

// COMPLIANT: unknown with discriminated union
function processEvent(event: unknown): void {
  if (!isKnownEvent(event)) {
    logger.warn("Unknown event type", { eventType: typeof event });
    return;
  }
  // event is now typed as KnownEvent
}
```

---

## Principle 4: Structured Logging

### Rule

All log output must be structured as JSON. No `console.log` with concatenated strings.
Logs must include trace IDs, span IDs, and domain context.

### Why This Matters

In the Harness Engineering model, agents query logs directly (LogQL, PromQL) to
self-diagnose issues. Unstructured logs are invisible to this tooling.

- **Machine queryability.** Structured logs enable `logql: {domain="billing"} |= "error"`.
  String concatenation requires regex parsing.
- **Trace correlation.** Trace IDs and span IDs connect logs to distributed traces.
- **Automated QA.** Agents validating fixes need to query logs for error rates, latency
  spikes, and unexpected warnings. Structured logs make this programmatic.
- **Context window efficiency.** When an agent loads logs into context, structured
  fields can be projected efficiently. Free-text logs waste context window tokens.

### How to Comply

1. **Use the project's logger** injected via Providers. Do not import a logging library
   directly — go through the Provider interface.
2. **Every log entry must include:** level, message (static string), timestamp,
   traceId, spanId, domain, and contextual attributes.
3. **Never use `console.log`, `console.error`, `console.warn`.**
4. **Log messages are static strings.** Put dynamic data in the attributes object.
5. **Log at the right level:**
   - `debug` — detailed info for debugging (disabled in production by default)
   - `info` — notable events (user logged in, invoice created)
   - `warn` — unexpected but handled (retry, fallback, degraded mode)
   - `error` — failures needing attention (exceptions, validation failures, timeouts)

### Violation Examples

```typescript
// VIOLATION: console.log with string concatenation
console.log("User " + userId + " logged in at " + new Date());

// VIOLATION: Dynamic message string
logger.info(\`User \${userId} \${action} on \${resource}\`);

// VIOLATION: Missing domain and trace context
logger.error("Something went wrong", { error: err.message });
```

### Compliant Examples

```typescript
// COMPLIANT: Structured log with static message
logger.info("User logged in", { userId, domain: "auth", method: "password" });

// COMPLIANT: Static message, dynamic data in attributes
logger.info("Resource action completed", { userId, action, resource, domain: "billing" });

// COMPLIANT: Error with full context
logger.error("Payment processing failed", {
  domain: "billing", paymentId,
  errorCode: error.code, retryable: error.retryable,
  error: error.message, stack: error.stack,
});

// COMPLIANT: Warning for degraded mode
logger.warn("Using fallback payment provider", {
  domain: "billing", primaryProvider, fallbackProvider,
  reason: "primary timeout",
});
```

---

## Principle 5: Naming Conventions

### Rule

Follow consistent naming conventions across the codebase. Enforced mechanically for
discoverability, predictability, and agent pattern-matching.

### Why This Matters

Agents pattern-match on file and symbol names. Inconsistent naming creates ambiguity —
an agent doesn't know whether to search for `userService.ts`, `UserService.ts`, or
`user-service.ts`. Consistent conventions make the codebase navigable without loading
every file into context.

### Conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| Domain directories | `kebab-case` | `app-settings/`, `user-profiles/` |
| Type/schema files | `PascalCase` | `UserProfile.ts`, `InvoiceSchema.ts` |
| Zod schema variables | `PascalCase` + `Schema` suffix | `UserProfileSchema` |
| Config files | `camelCase` | `appConfig.ts`, `dbConfig.ts` |
| Service files | `camelCase` | `userService.ts`, `invoiceService.ts` |
| Repository files | `camelCase` | `userRepo.ts`, `invoiceRepo.ts` |
| Test files | `*.test.ts` co-located | `userService.test.ts` |
| React components | `PascalCase` | `UserProfileCard.tsx` |
| React hooks | `use` prefix, `camelCase` | `useUserProfile.ts` |
| Event handlers | `handle` prefix, `camelCase` | `handleSubmit` |
| Callback props | `on` prefix, `camelCase` | `onSubmit` |
| Database tables | `snake_case`, plural | `user_profiles` |
| Database columns | `snake_case` | `created_at` |
| Environment variables | `UPPER_SNAKE_CASE` | `DATABASE_URL` |
| API routes | `kebab-case` | `/api/user-profiles` |
| Git branches | `kebab-case`, type prefix | `feat/user-profiles` |
| Commit messages | Conventional Commits | `feat(auth): add session refresh` |

### Additional Rules

- **No abbreviations.** Prefer `userProfile` over `usrProf`. Exceptions: widely
  understood acronyms like `API`, `URL`, `JSON`, `DOM`, `ID`.
- **No type prefixes.** No Hungarian notation (`strName`) or interface prefixes
  (`IUser`, `TConfig`). TypeScript's type system makes these redundant.
- **Descriptive over clever.** `fetchActiveUsers` > `getUsers` > `getUsrs`.
- **One concept, one name.** If it's `UserProfile` in types, it's `UserProfile`
  everywhere. Do not rename across layers.

---

## Principle 6: File Size Limits

### Rule

Files must not exceed reasonable size limits. A file that exceeds its limit signals
a missing abstraction and must be split.

### Why This Matters

Agent context windows are finite. Large files crowd out other context — the agent
loses sight of the broader task. Large files are also a code smell: a single module
doing too much.

### Limits

| File type | Max lines | Rationale |
|-----------|----------|-----------|
| Type/schema files | 200 | Schema files should be focused: one aggregate root per file |
| Config files | 150 | Config should be thin: declare, don't compute |
| Service files | 300 | If a service exceeds 300 lines, it likely orchestrates too many concerns |
| Repository files | 250 | Repos should be straightforward CRUD + parsing |
| UI components | 300 | Large components should be decomposed into sub-components |
| Test files | 500 | If tests exceed 500 lines, the source file is probably too large |
| Documentation (markdown) | 400 | Large docs should be split into sections with a TOC |

### What Counts as a Line

- All lines including comments, blank lines, and imports.
- Generated code (e.g., Zod schemas from OpenAPI) is exempt if committed as-is with
  a `// @generated` comment and regenerated from source of truth.

### How to Split

1. **Extract sub-modules.** A 350-line service → `userService.ts` + `userValidation.ts`
   + `userQueries.ts`.
2. **Extract shared utilities.** If reusable, extract to `shared/` (Principle 2).
3. **Decompose UI.** A large component → sub-components in their own files.
4. **Split tests.** Co-locate: `userService.test.ts` + `userValidation.test.ts`.

---

## Principle 7: Test Coverage

### Rule

New code must include tests. Required coverage depends on code type. Tests are how
agents validate their own work — without them, the codebase is not refactorable.

### Why This Matters

In a human-first codebase, tests catch regressions. In an agent-first codebase, tests
are also how agents **self-validate**:

- Agents cannot confidently refactor or extend code without test coverage.
- Garbage collection passes cannot verify they didn't break anything.
- QA validation is limited to manual testing, which doesn't scale with agent throughput.

### Coverage Requirements

| Code type | Minimum coverage | What "covered" means |
|-----------|-----------------|---------------------|
| Shared utilities | 100% | Every line, branch, and error path |
| Service business logic | 90% | Core logic paths, error handling, edge cases |
| Repository methods | 80% | CRUD operations, query logic, schema parsing |
| UI components | Snapshot + interaction | Render test, key interactions, error states |
| Config | Type-level | Schema parsing succeeds/fails correctly |
| Types | Type-level | `expectTypeOf` assertions |

### What Makes a Good Test

- **Independent.** No dependency on execution order or shared mutable state.
- **Readable.** Descriptive names: `it("returns 401 when token is expired")`, not
  `it("test auth error")`.
- **Fast.** Unit tests in milliseconds. Integration tests use ephemeral resources.
- **Deterministic.** No flaky tests. No reliance on real time (`jest.useFakeTimers()`),
  no reliance on network (mock at boundary), no reliance on file system order.
- **Coverage of error paths.** Happy-path tests are table stakes. The real value is
  in testing failures: validation errors, network timeouts, malformed data, concurrency
  edge cases.
- **Intent-encoding.** Test names and assertions should encode *why* the behavior
  matters, not just *what* it does. `it("applies 8.5% sales tax to comply with CA regulation")`
  is better than `it("calculates total with tax")`. If the business rule changes,
  the test name should make it obvious which tests need updating.

### Test Organization

```typescript
// Co-located: src/domains/auth/service/loginService.test.ts
import { describe, it, expect } from "vitest";
import { loginService } from "./loginService";

describe("loginService", () => {
  describe("authenticate", () => {
    it("returns session when credentials are valid", async () => { ... });
    it("throws InvalidCredentialsError when password is wrong", async () => { ... });
    it("throws AccountLockedError after 5 failed attempts", async () => { ... });
    it("records audit log on successful login", async () => { ... });
    it("sanitizes input to prevent injection", async () => { ... });
  });
});
```

---

## Enforcement

All golden principles are mechanically enforced by `tools/lint-golden.py`. Run it
before opening a pull request:

```bash
make lint
```

### What the Linter Checks

| Principle | Linter Check |
|-----------|-------------|
| Parse, Don't Validate | Zod schemas at API boundaries; no `unknown` crossing domain boundaries |
| Shared Utilities | No duplicate function implementations across domains |
| No YOLO Probing | No `any` types; `as` casts only at parse boundaries; optional chaining on external data flagged |
| Structured Logging | No `console.log/error/warn`; log calls include `domain`; message is static string |
| Naming Conventions | File names match conventions; Zod schemas have `Schema` suffix; no Hungarian notation |
| File Size Limits | Files checked against max line limits |
| Test Coverage | Coverage thresholds checked; test files co-located with source |

### Linter Output Format

```
ERROR: Golden principle violation
  File: src/domains/auth/service/loginService.ts
  Line: 42
  Rule: No YOLO Data Probing (Principle 3)
  Found: (response?.data?.user as any)?.profile
  Remediation: Parse response with a Zod schema in the repo layer.
               See docs/principles.md#principle-3-no-yolo-data-probing
```

---

## How Principles Evolve

1. **Human identifies a pattern** they want enforced.
2. **Principle is added here** with clear rationale and examples.
3. **Linter rule is added** to `tools/lint-golden.py`.
4. **Existing violations are flagged** by the next garbage collection pass.
5. **Recurring enforcement** keeps the codebase aligned.

This is the "taste is code" loop: human preference → documentation → mechanical
enforcement → continuous application.

### Agent Escalation

If an agent believes a principle or convention is causing harm (producing worse code
than ignoring it), it must NOT silently deviate. Instead:

1. **Follow the principle as written.**
2. **Leave a comment in the PR** explaining the concern and why the principle feels
   wrong in this case.
3. **Escalate to a human** for a principle change.

Principles evolve through human judgment, not agent rebellion. If the escalation
reveals a real problem, follow the "How Principles Evolve" steps above to update the
principle document and the linter.

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-05-09 | Initial golden principles document created. Principles 1-7 defined with rationale, violation examples, compliant examples, and enforcement rules. | agent |
