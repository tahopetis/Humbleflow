---
description: Reproduce bugs, validate fixes, and capture QA evidence.
argument-hint: "[bug-or-issue-description]"
---
Validate the following bug fix or user-facing change following the Humbleflow QA phase.

## Target
$ARGUMENTS

## Process

### 1. Reproduce
If this is a bug fix:
- Launch the application in an isolated worktree
- Drive the application to reproduce the reported bug
- Capture evidence: screenshot, video, or log output demonstrating the failure

### 2. Validate
- Apply the fix (if not already applied)
- Drive the application through the same scenario
- Capture evidence demonstrating the resolution
- Verify no regression in related functionality

### 3. For New Features
- Walk through each acceptance criterion from the execution plan
- Capture evidence for each criterion
- Verify observability: startup time, traces, log output

## Evidence
Document what you validated and attach evidence (screenshots, logs, videos).

## Escalation
Escalate to a human when:
- Bug cannot be reproduced (ask for clearer steps)
- Fix introduces a regression requiring re-planning
- QA tooling is insufficient (missing CDP access, worktree isolation)
