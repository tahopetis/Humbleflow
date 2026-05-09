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

{{REPO_MAP}}

## How to Work

### Starting a new task

1. **Read this map** (you're doing it now).
2. **Determine the task type:**
   - **Bug fix?** → Read `docs/architecture.md` for the affected domain, then follow `/qa`.
   - **New feature?** → Read `docs/architecture.md`, check `docs/quality.md` for domain grades, create an execution plan in `plans/`, then follow `/implement`.
   - **Refactoring / cleanup?** → Check `docs/quality.md` for low-grade domains. Follow `/garbage-collect` conventions.
   - **Documentation?** → Update `docs/` directly. Run `make garden` after.
3. **Load the `humbleflow` skill** for detailed phase instructions.
4. **Create an execution plan** in `plans/` for anything that takes more than a trivial change.

### Before opening a PR

1. **Run `make lint`** — boundary and golden-principle checks must pass.
2. **Self-review locally:** read the diff, check for violations of `docs/principles.md`.
3. **Request agent review:** use `/review` for adversarial review from fresh-context agents.
4. **Respond to all feedback** (agent and human). Iterate until all reviewers are satisfied.
5. **QA validation** for anything user-facing: reproduce the bug, validate the fix, capture evidence.

### After merge

1. **Update the execution plan** with completion notes and decision log.
2. **Run `make quality`** to update domain quality grades.
3. **Delete ephemeral worktrees** if applicable.

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
