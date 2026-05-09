---
description: QA flow: reproduce bugs, validate fixes, capture evidence.
argument-hint: "<bug-description-or-issue>"
---
Validate the following bug fix or user-facing change following the Humbleflow QA phase.

## Target
$ARGUMENTS

## Bug Reproduction (for bugs)

1. **Set up isolated environment:**
   - Boot the application in an isolated worktree (if available)
   - Ensure the environment matches the bug report's context

2. **Reproduce the bug:**
   - Follow the reproduction steps from the bug report
   - Drive the application through the failing scenario
   - Capture evidence: screenshot, video, or log output demonstrating the failure

3. **Document the reproduction:**
   - What steps were taken
   - What the expected behavior was
   - What actually happened
   - Evidence captured (screenshots/videos/logs)

## Fix Validation

1. **Apply the fix** (if not already applied in this worktree)

2. **Validate the fix:**
   - Drive the application through the same scenario
   - Confirm the bug no longer occurs
   - Capture evidence demonstrating the resolution

3. **Check for regressions:**
   - Test related functionality
   - Run the test suite
   - Check logs for unexpected errors

## Feature Validation (for features)

1. **Walk through acceptance criteria** from the execution plan
2. **For each criterion:**
   - Describe what was tested
   - What the expected outcome was
   - What actually happened
   - Evidence captured
3. **Edge cases:** Test boundaries, empty states, error states

## Observability Check (if available)

- Verify service startup time is within expected range
- Check trace spans for the changed user journeys
- Confirm no unexpected errors or warnings in logs
- Verify metrics are within expected ranges

## Output

A QA report with:
- **Summary:** What was tested and the result
- **Bug reproduction evidence** (if applicable)
- **Fix validation evidence** (if applicable)
- **Acceptance criteria verification** (for features)
- **Regression check results**
- **Observability findings** (if available)
- **Recommendation:** Ready to merge / needs more work

## Escalation

Escalate to a human when:
- The bug cannot be reproduced (ask for clearer steps)
- The fix introduces a regression
- QA tooling is insufficient (missing CDP access, worktree isolation, etc.)
