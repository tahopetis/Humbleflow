---
description: Scan for codebase drift and golden principle violations, open cleanup PRs.
---
Run a garbage collection pass on the Humbleflow codebase.

## Steps

### 1. Scan
```bash
make garden    # Find stale docs
make quality   # Update quality grades
make lint      # Find all violations
```

### 2. Analyze
Read `docs/quality.md`. Identify:
- Domains with grade C or below
- Violation clusters (multiple violations of the same principle)
- Stale documentation reports from `make garden`

### 3. Prioritize
Order work by impact:
1. **Boundary violations** — These block merges. Fix first.
2. **Golden principle violations** — Group by principle. Fix in batches.
3. **Test coverage gaps** — Add tests for untested service/repo code.
4. **Stale docs** — Update or tombstone outdated documentation.
5. **Duplicated helpers** — Extract to shared/.

### 4. Create PRs
For each independent fix, open a small, targeted PR:
- One PR per concern (don't mix boundary fixes with doc updates)
- Keep PRs reviewable in < 1 minute
- Use the lightweight plan template for tracking
- Run `make lint` before opening each PR

### 5. Update Grades
After PRs are merged, run `make quality` to update grades.

## Principles
- Don't do large-scale refactoring in a single PR.
- Don't change architectural decisions without human approval.
- Don't delete docs without checking if they're referenced elsewhere.
- If drift is systemic (>20% of domains), escalate to a human.
- If a domain has grade D or F, flag it for human discussion.

## Output
A summary comment on the garbage collection issue/task:
- What was fixed (PR links)
- What was deferred (with reasons)
- Updated quality grades
- Recommendations for human attention
