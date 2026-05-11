---
created: 2026-05-11
status: draft
---

# Adopt 12-Rule Behavioral Guardrails into Humbleflow

## Goal

Merge the behavioral discipline from the 12-rule CLAUDE.md template into Humbleflow's
phase instructions and golden principles — 5 adoptions, 2 adaptations — without
duplicating what Humbleflow already covers.

## Source Analysis

The 12 rules break down into three buckets:

| Bucket | Rules | Action |
|--------|-------|--------|
| Already covered | 4 (Goal-Driven), 8 (Read Before Write), 10 (Checkpoint), 12 (Fail Loud) | None |
| Adopt directly | 1 (Think Before Coding), 7 (Surface Conflicts) | Add to phases |
| Adopt with adaptation | 2 (Simplicity), 3 (Surgical Changes), 9 (Tests Verify Intent), 11 (Conventions Escalation) | Add clauses to existing sections |
| Rejected | 5 (Model for Judgment), 6 (Token Budgets) | None — not applicable |

## Constraints

- Documentation-only changes. No code, no linter changes.
- Edits are additive — don't rewrite existing sections, inject new clauses.
- Keep the Humbleflow voice (imperative, mechanical, agent-oriented).
- The skill reference files (`skills/humbleflow/references/`) and the project template
  files (`templates/docs/principles.md`) must stay in sync.

## Unknowns & Risks

| # | Unknown / Risk | Impact | Mitigation |
|---|---------------|--------|------------|
| 1 | Adding behavioral instructions may bloat phase docs | Agents load more context than needed | Keep additions short — single sentences or short paragraphs, not new sections |
| 2 | Reference files and template files may drift after edits | Agents in different projects get different instructions | Edit both locations in the same commit |
| 3 | Rule 3 (surgical changes) conflicts with Maintain phase | Agent might stop correcting drift during GC | Add explicit "during implementation" scope and "Maintain phase is exempt" note |

## Success Criteria

- [x] Rule 1 language added to Specify phase (assumption-surfacing, multi-interpretation, push-back)
- [x] Rule 2 anti-speculation clause added to Implement phase
- [x] Rule 3 surgical-scoping added to Implement phase with Maintain-phase exemption
- [x] Rule 7 conflict-resolution instruction added to Implement phase
- [x] Rule 9 intent-encoding clause added to GP7 test guidance
- [x] Rule 11 escalation path added to GP enforcement/evolution section
- [x] All changes mirrored in both `references/` and `templates/docs/`
- [x] No existing instructions were removed or weakened
- [x] Self-review confirms additions are concise and don't bloat docs

## Affected Files

| File | Nature of change |
|------|-----------------|
| `skills/humbleflow/references/phases.md` | Modify: Specify section + Implement section |
| `skills/humbleflow/references/golden-principles.md` | Modify: GP7 + Enforcement/Evolution section |
| `templates/docs/principles.md` | Modify: mirror the same golden-principles changes |
| `plans/2026-05-11-adopt-12-rule-behavioral-guardrails.md` | This plan |

## Approach

### Phase 1: Edit phase instructions (`references/phases.md`)

Three additions to the phases doc:

**1a. Specify phase — add after step 2 (the clarifying-question step):**

Add three new agent instructions:
- State your assumptions explicitly before designing.
- If the prompt is ambiguous in multiple valid ways, present those interpretations and ask the human to choose.
- If a simpler approach exists than what the prompt implies, propose it before implementing.

**1b. Implement phase — add to "What NOT to do" section:**

Add two items:
- Do not implement anything not in the plan. No speculative features, no "while I'm here" improvements.
- Do not refactor adjacent code that isn't touched by the plan — that is the Maintain phase's job.

**1c. Implement phase — add after step 1 (validate current state):**

Add a new step:
- If you encounter two contradictory patterns in the codebase, follow the more recent or more tested one. Leave a `// TODO(drift)` comment on the older pattern. Surface the conflict in the execution plan's decision log.

### Phase 2: Edit golden principles (`references/golden-principles.md` + `templates/docs/principles.md`)

Two additions, mirrored to both files:

**2a. GP7 (Test Coverage) — add to "What Makes a Good Test" section:**

Add a sixth bullet:
- **Intent-encoding.** Test names and assertions should encode *why* the behavior matters, not just *what* it does. `it("applies 8.5% sales tax to comply with CA regulation")` is better than `it("calculates total with tax")`. If the business rule changes, the test name should make it obvious which tests need updating.

**2b. Enforcement section — add escalation path after "How Principles Evolve":**

Add:
- **Agent escalation.** If an agent believes a principle or convention is causing harm (producing worse code than ignoring it), it must NOT silently deviate. Instead: (1) follow the principle, (2) leave a comment explaining the concern, (3) escalate to a human for a principle change. Principles evolve through human judgment, not agent rebellion.

### Phase 3: Review and sync

- [ ] Self-review both modified reference files
- [ ] Verify `templates/docs/principles.md` matches `references/golden-principles.md` for the edited sections
- [ ] Verify no existing instructions were removed
- [ ] Run `make validate-plan` on this plan

## Progress Log

| Date | Status | Notes |
|------|--------|-------|
| 2026-05-11 | planning | Plan created based on analysis of 12-rule template vs Humbleflow. |
| 2026-05-11 | done | All 6 edits applied to 3 files. Self-reviewed. No existing content removed. |

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-11 | Adopt 5 rules, adapt 2, reject 2, skip 4 (already covered) | See analysis report. |
| 2026-05-11 | Use lightweight plan template | Documentation-only change, single domain, no code. |
| 2026-05-11 | Mirror changes to both `references/` and `templates/docs/` | Prevents drift between skill docs and project scaffold docs. |

## Completion Notes

[To be filled after merge.]
