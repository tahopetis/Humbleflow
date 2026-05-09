---
description: Adversarial code review. Launch fresh-context reviewers with distinct angles, then synthesize.
argument-hint: "[PR-URL or description]"
---
Review the following change with adversarial, fresh-context reviewers.

## Target
$ARGUMENTS

## Workflow

Launch 3 fresh-context reviewer agents, each with a distinct angle:

### Reviewer 1: Correctness & Regressions
- Does the change do what it claims to do?
- Are there logic errors, edge cases missed, or off-by-one issues?
- Could this change cause regressions in related functionality?
- Are error paths handled correctly?

### Reviewer 2: Tests & Validation
- Are tests adequate for the changed behavior?
- Do tests cover edge cases and error paths?
- Are there brittleness risks (timing, ordering, global state)?
- If user-facing: is QA evidence captured?

### Reviewer 3: Simplicity & Maintainability
- Is the change as simple as it could be?
- Are there unnecessary abstractions or premature optimizations?
- Does it follow the existing patterns in the codebase?
- Would a future agent understand this code?

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
