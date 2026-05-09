# Humbleflow SDLC — Human-Readable Specification

> **This document is for humans.** Agents should read `AGENTS.md` and load the
> `humbleflow` skill. This document explains the SDLC from a human's perspective:
> what happens at each phase, what you as a human are responsible for, and what the
> agents handle.

---

## The Model

```
HUMAN                            AGENT
─────                            ─────
Write prompts                    Read AGENTS.md
Define acceptance criteria       Load humbleflow skill
Validate outcomes                Follow SDLC phases
Encode taste as rules            Write code, tests, docs
Escalate when stuck              Run linters & fix violations
                                 Self-review
                                 Request agent reviews
                                 Respond to feedback
                                 Reproduce & validate bugs
                                 Open PRs
                                 Merge (with human oversight)
```

**You don't write code.** You steer. You define what "done" looks like. When the agent gets stuck, you identify what capability is missing and feed it back into the harness — by having the agent write the fix.

---

## The SDLC in One Minute

| Phase | What happens | Your role |
|-------|-------------|-----------|
| **Specify** | Agent reads your prompt, asks ONE clarifying question, writes acceptance criteria | Answer the question. Approve or refine the criteria. |
| **Plan** | Agent creates an execution plan with unknowns surfaced | Approve the plan. Resolve unknowns it can't decide. |
| **Implement** | Agent writes code depth-first, adds tests, self-reviews, runs linters | Watch the PR. You don't need to review every line. |
| **Review** | 2-3 fresh-context agents perform adversarial review | Optional. You can review, but agents review each other primarily. |
| **QA** | Agent reproduces bugs, validates fixes, captures evidence | For user-facing changes: verify the evidence. |
| **Merge** | Agent runs final checks, squashes, merges, updates plan | Approve the merge. Only escalate for architectural concerns. |
| **Maintain** | Background agents scan for drift, open refactoring PRs | Review refactoring PRs in < 1 minute. Auto-merge most. |

---

## Your Tools

### Start work

```
/implement "Add two-factor authentication to the login flow"
/qa "Users report that password reset emails are not being delivered"
/plan-feature "Build a notification center with email, push, and in-app channels"
```

### Review and validate

```
/review           # Adversarial review of current PR
```

### Maintain

```
/garbage-collect  # Scan for drift, open cleanup PRs
make quality      # View current quality grades
make garden       # Check for stale documentation
```

---

## What "Done" Looks Like

A task is done when:

1. [ ] Acceptance criteria are verified (QA evidence exists for user-facing changes).
2. [ ] All agent reviewers have approved.
3. [ ] `make lint` passes (boundary + golden principles).
4. [ ] Execution plan is updated with completion notes and decisions.
5. [ ] Quality grades are updated (`make quality`).
6. [ ] PR is merged.

---

## When to Step In

**You are the escalation path.** Agents will escalate to you when:

- A judgment call is needed (architectural tradeoff, technology choice, user-facing design).
- A capability is missing (tool, API access, infrastructure).
- The acceptance criteria are ambiguous after one clarification.
- A change is security-sensitive (auth, permissions, data handling, secrets).
- The agent has been stuck for more than 3 iterations on the same problem.

When you step in, your job is NOT to write the fix yourself. Your job is to identify **what capability is missing** and describe it so the agent can build it:

```
❌ Bad:  "Just change the auth module to use JWT instead of sessions."
✅ Good: "The agent needs a capability to generate and validate JWTs.
         Add a JWT utility to shared/, write the schema in types/,
         then update the auth service to use it. Acceptance criteria:
         - Tokens expire after 15 minutes
         - Refresh tokens are supported
         - Blacklisting works for logout"
```

---

## Taste as Code

When you notice a pattern you want enforced everywhere:

1. **Document it** in `docs/principles.md`.
2. **Have the agent encode it** into `tools/lint-golden.py`.
3. **Run garbage collection** to flag existing violations.

The next time any agent writes code, the linter enforces your preference. You never have to mention it in review again.

---

## Quality at a Glance

Run `make quality` to see the current state. Read `docs/quality.md` for the full breakdown.

The quality grades are:

- **A** — Excellent. No issues.
- **B** — Good. 1-2 minor issues.
- **C** — Acceptable. Needs attention soon.
- **D** — Poor. Refactoring needed.
- **F** — Critical. Immediate rework required.

---

## Repository Map (for Humans)

```
humbleflow/
├── AGENTS.md              ← Agent's entry point. Read this to understand their view.
├── WORKFLOW.md            ← You are here.
│
├── docs/                  ← System of record. The source of truth.
│   ├── architecture.md    ← How the code is organized and what depends on what.
│   ├── quality.md         ← Quality grades per domain.
│   └── principles.md      ← Encoded taste. What the linters enforce.
│
├── plans/                 ← Execution plans. Active, completed, templates.
│   ├── template.md        ← Use this shape for new plans.
│   └── README.md          ← Plan conventions.
│
├── tools/                 ← Mechanical enforcement. CI runs these.
│   ├── Makefile           ← Entry point.
│   ├── lint-boundaries.py ← Architecture violations.
│   ├── lint-golden.py     ← Principle violations.
│   ├── quality-grade.py   ← Grade updater.
│   ├── doc-gardener.py    ← Stale doc finder.
│   └── validate-plan.py   ← Plan structure checker.
│
└── .pi/                   ← Agent configuration.
    ├── skills/humbleflow/ ← The SDLC workflow skill.
    └── prompts/            ← Prompt templates (/implement, /review, etc.).
```

---

## Getting Started

1. **First task:** Type `/plan-feature "describe your first feature"`. The agent will create an execution plan.
2. **Review the plan:** Check that the acceptance criteria match your intent. Resolve unknowns.
3. **Implement:** Type `/implement`. The agent will follow the plan.
4. **Review:** The agent will request peer reviews. You can add yours if you want.
5. **QA:** The agent validates the change. Review the evidence.
6. **Merge:** Approve. The agent handles the rest.
7. **Maintain:** Periodically run `/garbage-collect` or let the scheduled agent handle it.
