---
name: humbleflow
description: >
  Agent-first SDLC workflow based on OpenAI's Harness Engineering principles.
  Use when performing any SDLC work: specifying requirements, planning features,
  implementing changes, reviewing code, QA testing, merging, or maintaining
  the codebase. Covers the full lifecycle from prompt to production with
  mechanical enforcement of architecture, taste, and quality. Do NOT use for
  work outside the SDLC — this is the development workflow, not the application domain.
---

# Humbleflow

You are an agent operating inside the Humbleflow SDLC harness. This skill defines
your workflow for every phase of the software development lifecycle. The harness is
designed around one principle: **humans steer, agents execute.**

Your job is to follow the phases below, invoke the right tools, and escalate to a
human only when judgment is required.

## Quick Reference: Phase Selection

| Task type | Phase | Key artifacts |
|-----------|-------|---------------|
| New feature from requirements | Specify → Plan → Implement → Review → QA → Merge | Execution plan, PR, review feedback, QA evidence |
| Bug fix | QA → Implement → Review → Merge | Bug reproduction evidence, fix, validation evidence |
| Refactoring / cleanup | Maintain (garbage collect) | Quality grade update, refactoring PR |
| Architecture / docs | Plan → Implement → Review | Updated `docs/`, execution plan |
| Code review (asked to review) | Review | Review comments on PR |

## The SDLC Phases

For detailed instructions on each phase, load the reference files:

- **[Specify](references/phases.md#1-specify)** — Translate human intent into acceptance criteria and constraints.
- **[Plan](references/phases.md#2-plan)** — Create execution plans with progress/decision logs.
- **[Implement](references/phases.md#3-implement)** — Write code, tests, docs. Self-review. Iterate.
- **[Review](references/phases.md#4-review)** — Agent-to-agent adversarial review. Respond to feedback.
- **[QA](references/phases.md#5-qa)** — Reproduce bugs, validate fixes, capture evidence.
- **[Merge](references/phases.md#6-merge)** — Final checks, squash, merge, cleanup.
- **[Maintain](references/phases.md#7-maintain)** — Garbage collection, quality grading, drift detection.

## Architecture

The codebase follows a strict layered architecture. Before implementing anything,
load **[references/architecture.md](references/architecture.md)** to understand:

- Domain decomposition and package layering
- Dependency direction rules (Types → Config → Repo → Service → Runtime → UI)
- Cross-cutting concern interfaces (Providers)
- What imports are allowed and disallowed

## Golden Principles

These are mechanically enforced. Violating them blocks your PR. Before writing code,
load **[references/golden-principles.md](references/golden-principles.md)** to understand:

- Parse, don't validate (data shapes at boundaries)
- Shared utilities over hand-rolled helpers
- No YOLO data probing
- Structured logging
- Naming conventions
- File size limits

## Tools

Run these before opening a PR. They are in `tools/`:

```bash
make lint      # Run all linters (boundaries + golden principles)
make quality   # Update quality grades
make garden    # Find and report stale docs
make validate-plan plans/<your-plan>.md  # Validate plan structure
```

If a tool fails, read its output carefully — it includes remediation instructions
injected into your context. Fix the violations, then re-run.

## When to Escalate

Escalate to a human when:

1. **Judgment required** — architectural tradeoffs, technology choices, user-facing design.
2. **Missing capability** — you need a tool, API, or infra that doesn't exist. Do NOT work around it.
3. **Ambiguous criteria** — the prompt can be interpreted multiple valid ways.
4. **Security-sensitive** — auth, permissions, data handling, secrets.
5. **Stuck for > 3 iterations** — step back and ask what capability is missing, don't "try harder."

## After Every Task

1. Update the execution plan with progress and decisions.
2. Run `make quality` if the task changed code in a domain.
3. Clean up ephemeral worktrees.
