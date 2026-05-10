# SDLC Phases — Detailed Instructions

## 1. Specify

**Entry criteria:** Human provides a feature request, bug report, or user feedback.

**Agent instructions:**

1. Read the human's prompt carefully. Identify:
   - The desired outcome (what changes for the user?)
   - Constraints (performance, security, compatibility)
   - Acceptance criteria (how do we know it's done?)
2. If anything is ambiguous, ask ONE clarifying question. Do not ask multiple questions
   at once — pick the single most important unknown.
3. Translate the specification into acceptance criteria in the execution plan.
4. Identify which domains are affected (check `docs/architecture.md`).

**Exit criteria:**
- Acceptance criteria are written and unambiguous.
- Affected domains are identified.
- An execution plan has been created (or the task is small enough for a lightweight plan).

**Escalation triggers:**
- The human's prompt is fundamentally unclear even after one clarifying question.
- The feature conflicts with documented architectural constraints.

---

## 2. Plan

**Entry criteria:** Acceptance criteria exist. Domain scope is known.

**Agent instructions:**

1. Load `docs/architecture.md` for the affected domains.
2. Check `docs/quality.md` for current quality grades in those domains.
3. Choose the right plan template:
   - **Full plan** (`plans/template.md`): multi-day features, architectural changes, cross-domain work.
   - **Lightweight plan** (`plans/template-lightweight.md`): single-domain, < 1 day of work.
4. Fill in the plan: goal, constraints, unknowns, success criteria, approach.
5. Identify risks and unknowns. Surface them — don't hide gaps.
6. Estimate the work in terms of affected files/components, not hours.
7. Save the plan to `plans/YYYY-MM-DD-<slug>.md`.

**Exit criteria:**
- Plan has all required sections filled.
- Unknowns are surfaced, not hidden.
- Plan passes `make validate-plan`.
- Human has approved the plan (for full plans; lightweight plans can proceed).

**Escalation triggers:**
- Unknowns that are blockers (need human decision).
- Architectural concerns not covered by existing docs.

---

## 3. Implement

**Entry criteria:** Approved execution plan (or lightweight plan for small changes).

**Agent instructions:**

1. **Validate current state.** Read the files you'll modify. Confirm the plan still makes sense.
2. **Implement in depth-first order.** Start with the lowest-level building block
   (types/schemas), then config, then repository, then service, then runtime, then UI.
3. **Write tests alongside code.** Every new behavior gets a test. Every bug fix gets a
   regression test.
4. **Self-review locally.** Read your entire diff. Check against `docs/principles.md`:
   - Are data shapes validated at boundaries?
   - Is structured logging used?
   - Are naming conventions followed?
   - Are file sizes reasonable?
5. **Run the enforcement tools:**
   ```bash
   make lint
   make validate-plan plans/<your-plan>.md
   ```
6. **Fix all violations.** The linter output includes remediation instructions.
7. **Iterate locally** until all checks pass and you're satisfied.
8. **Open a PR.** Use the execution plan as the PR description.

**What NOT to do:**
- Do not implement UI before the service layer exists.
- Do not skip tests because "the change is simple."
- Do not work around linter failures — fix the violation.
- Do not implement cross-domain changes in a single PR without explicit approval.

**Exit criteria:**
- All code, tests, and docs are written.
- `make lint` passes.
- Self-review complete, no known violations of golden principles.
- PR is open.

**Escalation triggers:**
- Implementation reveals a flaw in the plan that requires a human decision.
- Missing tool or API that blocks progress (do NOT work around it).

---

## 4. Review

**Entry criteria:** PR is open.

**Agent instructions:**

1. **Request agent review.** Use the `/review` workflow:
   - Launches 2-3 fresh-context reviewer agents with distinct angles.
   - Angles: correctness/regressions, tests/validation, simplicity/maintainability.
2. **Read all review feedback.** Do not dismiss any comment.
3. **Respond to every comment:**
   - If you agree: implement the fix, push an update, reply "Done in [commit]."
   - If you disagree: explain why clearly, reference docs/principles.
   - If you don't understand: ask the reviewer to clarify.
4. **Iterate** until all reviewers are satisfied.
5. **Human review is optional.** Humans may review but aren't required to. If a human
   leaves feedback, treat it as blocking and respond within the same iteration.

**What NOT to do:**
- Do not argue with reviewers about style unless it violates a documented principle.
- Do not resolve conversations yourself — let the reviewer resolve.
- Do not merge until all review threads are resolved.

**Exit criteria:**
- All agent reviewers have approved (or their concerns are resolved).
- All human feedback (if any) is addressed.
- CI passes (lint, tests, plan validation).

**Escalation triggers:**
- Reviewer feedback requires a judgment call (e.g., architectural tradeoff).
- Reviewer finds a fundamental flaw that requires re-planning.

---

## 5. QA

**Entry criteria:** Implementation is complete and reviewed. Change is user-facing or
fixes a reported bug.

**Agent instructions:**

1. **For bug fixes — reproduce the bug first:**
   - Launch the application in an isolated worktree.
   - Drive the application to reproduce the reported bug.
   - Capture evidence: screenshot, video, or log output demonstrating the failure.
2. **Apply the fix** (if not already applied in the same worktree).
3. **Validate the fix:**
   - Drive the application through the same scenario.
   - Capture evidence demonstrating the resolution.
   - Verify no regression in related functionality.
4. **For features — validate acceptance criteria:**
   - Walk through each acceptance criterion from the execution plan.
   - Capture evidence for each.
5. **Check observability** (if available):
   - Verify service startup time, trace spans, log output.
   - Confirm no unexpected errors or warnings.

**What NOT to do:**
- Do not skip QA because "the change is simple" — every user-facing change gets QA.
- Do not manually test — use the application driver tools.

**Exit criteria:**
- Bug is reproduced with evidence.
- Fix is validated with evidence.
- All acceptance criteria are verified.
- No regressions detected.

**Escalation triggers:**
- Cannot reproduce the bug (ask human for clearer reproduction steps).
- Fix introduces a regression that requires re-planning.
- QA tooling is insufficient (missing CDP access, worktree isolation, etc.).

---

## 6. Merge

**Entry criteria:** All reviews approved. QA passed. CI green.

**Agent instructions:**

1. **Final pre-merge checks:**
   - Rebase on latest main (or merge main into branch).
   - Re-run `make lint` after rebase.
   - Confirm CI is still green.
2. **Squash and merge** (preferred) or merge commit. Use conventional commit format:
   ```
   type(domain): description

   Closes #<issue>
   ```
3. **Post-merge:**
   - Update the execution plan: mark as completed, add completion notes and decision log.
   - **Update SPEC.md:** Append the completed feature to the `## Capabilities` section with a checkmark.
     Format: `- [x] Feature name — brief outcome of what was built`
     Example: `- [x] Recurring invoice scheduling — users can create weekly/monthly recurring invoices`
   - **Check BACKLOG.md:** If `BACKLOG.md` exists and has pending items, report the next item to the human.
     Ask: "Done. Next in backlog: [item]. Want to start it?"
   - Run `make quality` to update domain quality grades.
   - Move the plan to `plans/completed/` if the convention exists.
4. **Clean up:** Delete the worktree and any ephemeral resources.

**What NOT to do:**
- Do not merge with failing CI (even "known flakes" — re-run until green).
- Do not leave the execution plan in an incomplete state.

**Exit criteria:**
- PR is merged.
- Execution plan is updated and completed.
- SPEC.md Capabilities updated with completed feature.
- BACKLOG.md checked (next item reported to human if pending).
- Quality grades are updated.
- Ephemeral resources are cleaned up.

**Escalation triggers:**
- Merge conflicts that require human judgment to resolve.
- CI failure that cannot be fixed without architectural changes.

---

## 7. Maintain (Garbage Collection)

**Entry criteria:** Recurring (scheduled) or triggered by quality grade degradation.

**Agent instructions:**

1. **Check BACKLOG.md:** If `BACKLOG.md` exists and has pending items, report the next item to the human.
   Ask if they want to start it. Do not start backlog work without human confirmation.
2. **Scan for drift:**
   ```bash
   make garden    # Find stale docs
   make quality   # Update quality grades
   ```
3. **Review the `docs/quality.md` report.** Identify domains with degraded grades.
4. **For each degraded domain:**
   - Identify the specific violations (boundary, golden principle, test coverage, etc.).
   - Open a targeted refactoring PR for each independent issue.
   - Keep PRs small and reviewable in < 1 minute.
5. **For stale docs:**
   - Update docs to reflect current code behavior.
   - Delete docs that are no longer relevant (with a tombstone note).
6. **For pattern drift:**
   - Scan for hand-rolled implementations of shared utilities.
   - Scan for YOLO-style data probing.
   - Open fix-up PRs.

**What NOT to do:**
- Do not do large-scale refactoring in a single PR.
- Do not change architectural decisions without human approval.
- Do not delete docs without checking if they're referenced elsewhere.

**Exit criteria:**
- Quality grades are updated.
- Stale docs are refreshed or tombstoned.
- Drift PRs are open (or already merged).
- Report is posted to the execution log.

**Escalation triggers:**
- Drift is systemic (pattern appears in > 20% of domains) — requires human discussion.
- Quality grade is "D" or "F" and requires architectural rework.
