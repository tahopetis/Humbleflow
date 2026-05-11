---
created: 2026-05-11
status: in-progress
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
- [ ] Self-reviewed, committed, pushed

## Affected Files

| File | Nature of change |
|------|-----------------|
| `skills/humbleflow/references/phases.md` | Modify: Specify section + Implement section |
| `skills/humbleflow/references/golden-principles.md` | Modify: GP7 + Enforcement section |
| `templates/docs/principles.md` | Modify: mirror the same golden-principles changes |
| `plans/2026-05-11-adopt-12-rule-behavioral-guardrails.md` | This plan |

## Progress Log

| Date | Status | Notes |
|------|--------|-------|
| 2026-05-11 | planning | Plan created based on analysis of 12-rule template vs Humbleflow. |
| 2026-05-11 | in-progress | Edits applied in /code/humbleflow. Ready for commit. |

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-11 | Adopt 5 rules, adapt 2, reject 2, skip 4 (already covered) | See analysis report. |
| 2026-05-11 | Use lightweight plan template | Documentation-only change, single domain, no code. |
| 2026-05-11 | Mirror changes to both `references/` and `templates/docs/` | Prevents drift between skill docs and project scaffold docs. |

## Completion Notes

[To be filled after merge.]
