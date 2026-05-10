---
description: Full implementation flow: validate state > plan > implement > review > iterate > PR.
argument-hint: "<feature-or-change-description>"
---
Implement the following change following the Humbleflow workflow.

## Target
$ARGUMENTS

## Pre-implementation

1. **Load the map:**
   - Read `AGENTS.md` (already in context)
   - Load the `humbleflow` skill
   - Read `docs/architecture.md` for the affected domain(s)

2. **Validate current state:**
   - Read the files you'll modify
   - Confirm the change still makes sense against current code

3. **Check quality:**
   - Read `docs/quality.md` for the affected domain(s)
   - Note any existing issues to avoid compounding

## Implementation

Follow the layered architecture, depth-first. Build in this order:

1. **Types** — Define schemas, types, constants first. Everything above depends on these.
2. **Config** — Domain configuration, feature flags.
3. **Repo** — Data access, persistence. Parse external data at this boundary.
4. **Service** — Business logic. Orchestrate repo calls.
5. **Runtime** — Application bootstrap, routing, middleware.
6. **UI** — Components, pages, views. Never before the service layer exists.

At each layer:
- Write tests alongside code (test file co-located as `foo.test.ts`)
- Follow golden principles (see docs/principles.md)
- Use structured logging (never console.log)
- Parse data at boundaries (Zod schemas, no YOLO probing)

## Self-Review

Before opening a PR:

```bash
make lint           # Must pass
make validate-plan  # Must pass (if you created a plan)
```

Read your entire diff. Check against:
- [ ] Data shapes validated at boundaries? (Principle 1)
- [ ] Shared utilities used instead of hand-rolled? (Principle 2)
- [ ] No YOLO probing (any, unchecked as, deep ?.)? (Principle 3)
- [ ] Structured logging used? (Principle 4)
- [ ] Naming conventions followed? (Principle 5)
- [ ] File size limits respected? (Principle 6)
- [ ] Tests co-located and adequate? (Principle 7)

## After PR Opens

1. **Request agent review** using `/humbleflow-review`
2. **Respond to all feedback** — agree+fix, disagree+explain, or ask for clarification
3. **Iterate** until all reviewers are satisfied
4. **Human review** is optional but respected if given

## Escalation

Escalate to a human when:
- Implementation reveals a flaw in the plan
- A capability is missing (do NOT work around it)
- The change requires a judgment call
- You've been stuck for > 3 iterations
