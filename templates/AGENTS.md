<!-- HARNESS-TEMPLATE: Replace {{PROJECT_NAME}} during init -->
# {{PROJECT_NAME}} — Agent Map

> You are an agent working in the `humbleflow` repository. This document is your map.
> It tells you what exists, where to find it, and how we operate. Read it once at the
> start of every task. Load deeper docs when you need them — don't try to hold
> everything in context at once.

## Core Beliefs

1. **Humans steer. Agents execute.** Human time is the scarce resource. Humans write
   prompts and acceptance criteria, validate outcomes, and encode taste as mechanical
   rules. Agents do everything else.

2. **The repository is the system of record.** If it's not in the repo, it doesn't
   exist. No Google Docs, no Slack threads, no tribal knowledge. Write it down here.

3. **Parse, don't validate.** Data shapes are validated at boundaries using typed
   schemas. Never probe data "YOLO-style" — if you're guessing shapes, something is
   wrong.

4. **Corrections are cheap, waiting is expensive.** Ship fast, fix fast. Merge gates
   are minimal. Test flakes get follow-up runs, not indefinite blocks.

5. **Taste is code.** When a human teaches you a preference, it gets encoded into a
   linter or structural test. Documentation alone is not enough — it must be enforced
   mechanically.

## Repository Map

```
{{PROJECT_NAME}}/
├── AGENTS.md              ← You are here. Start every task by reading this.
├── SPEC.md                ← Project vision, users, MVP, capabilities, constraints.
├── BACKLOG.md             ← Prioritized work queue (Now → Next → Later → Done).
├── WORKFLOW.md            ← Human-readable SDLC specification.
│
├── docs/                  ← System of record. Knowledge base.
│   ├── architecture.md    ← Domain map, layered architecture, dependency rules.
│   ├── quality.md         ← Quality grades per domain, tracked over time.
│   └── principles.md      ← Golden principles with rationale.
│
├── plans/                 ← Execution plans. First-class, versioned artifacts.
│   ├── README.md          ← Plan conventions and lifecycle.
│   ├── template.md        ← Full execution plan template.
│   ├── template-lightweight.md ← Lightweight plan for small changes.
│   └── YYYY-MM-DD-*.md    ← Active and completed plans.
│
├── tools/                 ← Mechanical enforcement. Run these; don't skip them.
│   ├── Makefile           ← Entry point: `make lint`, `make quality`, `make garden`.
│   ├── lint-boundaries.py ← Validates dependency directions per architecture.
│   ├── lint-golden.py     ← Validates golden principles.
│   ├── quality-grade.py   ← Scans and updates quality grades.
│   ├── doc-gardener.py    ← Finds stale docs, opens fix-up reports.
│   └── validate-plan.py   ← Validates execution plan structure.
│
└── .pi/                   ← Pi agent configuration.
    ├── skills/
    │   └── humbleflow/    ← The SDLC workflow skill. Load when doing SDLC work.
    │       ├── SKILL.md
    │       └── references/
    └── prompts/           ← Prompt templates for common workflows.
```

## How to Work

### Starting a new task

0. **Check what's been built:** Read `SPEC.md` for project vision and completed capabilities. Read `BACKLOG.md` for upcoming and pending work.
1. **Read this map** (you're doing it now).
2. **Determine the task type:**
   - **Bug fix?** → Read `docs/architecture.md` for the affected domain, then follow `/qa`.
   - **New feature?** → Read `docs/architecture.md`, check `docs/quality.md` for domain grades, create an execution plan in `plans/`, then follow `/implement`.
   - **Refactoring / cleanup?** → Check `docs/quality.md` for low-grade domains. Follow `/garbage-collect` conventions.
   - **Documentation?** → Update `docs/` directly. Run `make garden` after.
3. **Load the `humbleflow` skill** for detailed phase instructions.
4. **Create an execution plan** in `plans/` for anything that takes more than a trivial change.
5. **If this is a new requirement:** add it to `BACKLOG.md` under the appropriate priority (Now/Next/Later), then ask the human to confirm priority before starting.

### Before opening a PR

1. **Run `make lint`** — boundary and golden-principle checks must pass.
2. **Self-review locally:** read the diff, check for violations of `docs/principles.md`.
3. **Request agent review:** use `/review` for adversarial review from fresh-context agents.
4. **Respond to all feedback** (agent and human). Iterate until all reviewers are satisfied.
5. **QA validation** for anything user-facing: reproduce the bug, validate the fix, capture evidence.

### After merge

1. **Update the execution plan** with completion notes and decision log.
2. **Update SPEC.md:** Append the completed feature to `## Capabilities` with a checkmark. Format: `- [x] Feature name — brief outcome`.
3. **Update BACKLOG.md:** Move the completed item from Now to Done with a completion date. Report the next pending item to the human: "Done. Next in backlog: [item]. Want to start it?"
4. **Run `make quality`** to update domain quality grades.
5. **Delete ephemeral worktrees** if applicable.

## Key Rules (enforced mechanically by `tools/`)

| Rule | Enforced by | What happens on violation |
|------|------------|--------------------------|
| Dependency direction: Types→Config→Repo→Service→Runtime→UI | `lint-boundaries.py` | PR blocked |
| No backward or cross-domain imports | `lint-boundaries.py` | PR blocked |
| Data validated at boundaries (typed schemas) | `lint-golden.py` | Warning + remediation hint |
| Structured logging required | `lint-golden.py` | Warning + remediation hint |
| File size limits | `lint-golden.py` | Warning |
| Naming conventions for schemas/types | `lint-golden.py` | Warning |
| Docs freshness (no stale references) | `doc-gardener.py` | Auto-fix PR opened |
| Execution plan completeness | `validate-plan.py` | Warning |

## When to Escalate to a Human

- **Judgment calls:** architectural tradeoffs, technology choices, user-facing design decisions.
- **Blocked by missing capability:** you need a tool, API access, or infrastructure that doesn't exist. Do NOT work around it — report what's missing.
- **Ambiguous acceptance criteria:** the prompt can be interpreted multiple ways and the right choice matters.
- **Security-sensitive changes:** auth, permissions, data handling, secrets.
- **You've been stuck for > 3 iterations** on the same problem. Step back and ask what capability is missing.
