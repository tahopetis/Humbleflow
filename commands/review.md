---
description: Adversarial code review. Launch fresh-context reviewer subagents with distinct angles, then synthesize.
argument-hint: "[PR-URL or description]"
---
Review the following change with adversarial, fresh-context reviewer subagents.

## Target
$ARGUMENTS

## Workflow

Invoke three review subagents, each with a distinct angle. Use the following subagents:

### @humbleflow:review-correctness — Correctness & Regressions
Verify correctness: does the change do what it claims? Check for logic errors, edge cases, and regression risks.

### @humbleflow:review-tests — Tests & Validation
Verify test coverage: are tests adequate? Check for brittleness risks and edge case coverage.

### @humbleflow:review-simplicity — Simplicity & Maintainability
Verify simplicity: is the change as simple as it could be? Check for unnecessary abstractions and pattern consistency.

## Rules for Reviewers

1. Read the actual diff or changed files. Do not rely on descriptions.
2. Reference specific file paths and line numbers.
3. Return findings as: severity (blocking/major/minor/nit), finding, evidence (file:line), suggested fix.
4. Do NOT edit code unless explicitly asked.
5. If you find a golden principle violation, reference the specific rule from docs/principles.md.

## Synthesize

After all reviewers return, synthesize into three categories:
- **Must fix** (blocking — merge blocked until resolved)
- **Should fix** (important but not blocking — create follow-up issues)
- **Nits & observations** (optional, for consideration)

Apply must-fix changes. Create issues for should-fix items. Note nits for future reference.
