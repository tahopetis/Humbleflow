# Golden Principles

> These principles are mechanically enforced by `tools/lint-golden.py`.
> Violations block your PR. The linter output includes remediation instructions —
> read them and fix the violation. Do not work around the linter.

## 1. Parse, Don't Validate

**Rule:** Data entering the system must be parsed into typed schemas at the boundary.
Never probe data shapes or guess field types deep in the codebase.

**Why:** When data shapes are only validated (checked) rather than parsed (transformed
into typed structures), the type information is lost. Downstream code must re-validate
or guess, leading to defensive "YOLO-style" probing.

**How to comply:**
- Define Zod schemas (or equivalent) for all external data: API responses, form inputs,
  database records, WebSocket messages, CLI arguments.
- Parse at the boundary (Repo layer for data, Runtime layer for requests).
- All downstream code receives fully typed data — never `unknown` or `any`.
- If you see `as` casts or type guards deep in service/UI code, that's a violation.

**Example — violation:**
```typescript
// In Service layer — YOLO probing
const userName = (data as any).user?.name ?? "unknown";
```

**Example — compliant:**
```typescript
// In Repo layer — parse at boundary
const UserSchema = z.object({ name: z.string() });
const user = UserSchema.parse(rawData);
// Downstream: user.name is typed as string
```

## 2. Shared Utilities Over Hand-Rolled Helpers

**Rule:** When functionality is needed by multiple domains, it belongs in `shared/`,
not copy-pasted or re-implemented in each domain.

**Why:** Centralized utilities keep invariants in one place. When a bug is fixed or
instrumentation is added, all domains benefit immediately. Hand-rolled copies diverge
and become inconsistent.

**How to comply:**
- Before writing a helper function, check if `shared/` already has it.
- If you need it in 2+ places, extract to `shared/`.
- Shared utilities must have 100% test coverage.
- Shared utilities must be integrated with OpenTelemetry.

**Example — violation:**
```typescript
// In domain-a/service.ts
async function processBatch<T>(items: T[], fn: (item: T) => Promise<void>, concurrency: number) { ... }

// In domain-b/service.ts
async function processBatch<T>(items: T[], fn: (item: T) => Promise<void>, concurrency: number) { ... }
```

**Example — compliant:**
```typescript
// In shared/concurrency.ts
export async function mapWithConcurrency<T, R>(
  items: T[], fn: (item: T) => Promise<R>, concurrency: number
): Promise<R[]> { ... }

// In domain-a/service.ts
import { mapWithConcurrency } from "@/shared/concurrency";
```

## 3. No YOLO Data Probing

**Rule:** Never use `any`, unchecked `as` casts, or optional chaining to probe into
data whose shape is unknown. If you don't know the shape, parse it. If you can't
parse it, type it as `unknown` and handle the unknown case explicitly.

**Why:** YOLO probing creates silent failures. When data shape changes upstream,
downstream code doesn't fail at compile time — it produces `undefined` or wrong values
that surface as bugs far from the source.

**How to comply:**
- `as` casts are only allowed at parse boundaries (in Repo/Runtime layers where
  schemas are applied).
- `any` is never allowed in production code.
- Optional chaining (`?.`) on external data is a red flag — parse the data instead.

**Example — violation:**
```typescript
const email = (response?.data?.user?.profile?.email ?? "") as string;
```

**Example — compliant:**
```typescript
const ResponseSchema = z.object({
  data: z.object({
    user: z.object({
      profile: z.object({
        email: z.string().email()
      })
    })
  })
});
const { email } = ResponseSchema.parse(response).data.user.profile;
```

## 4. Structured Logging

**Rule:** All log output must be structured (JSON). No `console.log` with concatenated
strings. Logs must include trace IDs, span IDs, and domain context.

**Why:** Agents query logs with LogQL and PromQL. Unstructured logs are invisible to
the observability tooling. Structured logs enable agents to self-diagnose issues.

**How to comply:**
- Use the project's logger (injected via Providers).
- Every log entry includes: level, message, timestamp, traceId, spanId, domain.
- Never use `console.log`, `console.error`, or `console.warn` directly.

**Example — violation:**
```typescript
console.log("User " + userId + " logged in");
```

**Example — compliant:**
```typescript
logger.info("User logged in", { userId, domain: "auth" });
```

## 5. Naming Conventions

**Rule:** Follow consistent naming conventions.

| Construct | Convention | Example |
|-----------|-----------|---------|
| Domain directories | kebab-case | `app-settings/` |
| Type files | PascalCase for schemas | `UserProfile.ts` |
| Config files | camelCase | `appConfig.ts` |
| Service files | camelCase | `userService.ts` |
| Repository files | camelCase | `userRepo.ts` |
| Test files | `*.test.ts` co-located | `userService.test.ts` |
| React components | PascalCase | `UserProfileCard.tsx` |
| Hooks | `use` prefix, camelCase | `useUserProfile.ts` |
| Zod schemas | PascalCase, `Schema` suffix | `UserProfileSchema` |
| Database tables | snake_case, plural | `user_profiles` |

## 6. File Size Limits

**Rule:** Files must not exceed reasonable size limits.

| File type | Max lines |
|-----------|----------|
| Type/schema files | 200 |
| Config files | 150 |
| Service files | 300 |
| Repository files | 250 |
| UI components | 300 |
| Test files | 500 |
| Documentation (markdown) | 400 |

**Why:** Large files are hard for agents to reason about in context. They indicate
a missing abstraction. Break large files into smaller, focused modules.

## 7. Test Coverage Expectations

**Rule:** New code must include tests.

| Code type | Minimum coverage |
|-----------|-----------------|
| Shared utilities | 100% |
| Service business logic | 90% |
| Repository methods | 80% |
| UI components | Snapshot + interaction tests |
| Config | Type-level validation (ensure schema parsing works) |
| Types | Type-level tests (ensure types are correct) |

**Why:** In an agent-generated codebase, tests are how agents validate their own
work. Without tests, agents cannot confidently refactor or extend code.

**Test quality:** Test names and assertions should encode *why* the behavior matters,
not just *what* it does. `it("applies 8.5% sales tax to comply with CA regulation")`
is better than `it("calculates total with tax")`. If the business rule changes,
the test name should make it obvious which tests need updating.

## Enforcement

Run `make lint` before opening a PR. The linter output includes:
- The violated principle (with a link to this document).
- The file and line number.
- A remediation hint specific to the violation.

Example linter output:
```
ERROR: Golden principle violation in src/domains/auth/service/loginService.ts:42
  Rule: No YOLO Data Probing
  Found: (response?.data?.user as any)?.profile
  Fix: Parse response with a Zod schema in the repo layer. See docs/principles.md#3-no-yolo-data-probing
```

## Agent Escalation

If an agent believes a principle or convention is causing harm (producing worse code
than ignoring it), it must NOT silently deviate. Instead:

1. Follow the principle as written.
2. Leave a comment in the PR explaining the concern.
3. Escalate to a human for a principle change.

Principles evolve through human judgment, not agent rebellion. The "How Principles
Evolve" section in `docs/principles.md` describes the update process.
