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
| **Specify** | Agent reads your prompt, surfaces assumptions, presents interpretations if ambiguous, pushes back if a simpler approach exists, asks ONE clarifying question, writes acceptance criteria | Answer the question. Correct assumptions. Choose between interpretations. Approve or refine the criteria. |
| **Plan** | Agent creates an execution plan with unknowns surfaced | Approve the plan. Resolve unknowns it can't decide. |
| **Implement** | Agent writes code depth-first, adds tests, self-reviews, runs linters | Watch the PR. You don't need to review every line. |
| **Review** | 2-3 fresh-context agents perform adversarial review | Optional. You can review, but agents review each other primarily. |
| **QA** | Agent reproduces bugs, validates fixes, captures evidence | For user-facing changes: verify the evidence. |
| **Merge** | Agent runs final checks, squashes, merges, updates plan, updates SPEC.md Capabilities, checks BACKLOG.md for next item | Approve the merge. Only escalate for architectural concerns. |
| **Maintain** | Agent checks BACKLOG.md for pending items, reports next to human. Background agents scan for drift, open refactoring PRs | Respond to the "next item?" prompt. Review refactoring PRs in < 1 minute. |

---

## Your Tools

### Start work

| Workflow | Pi | Claude Code |
|----------|----|-------------|
| Init | `/humbleflow-init` | `/humbleflow:init` or `humbleflow init` CLI |
| Implement | `/humbleflow-implement` | `/humbleflow:implement "feature"` |
| QA | `/humbleflow-qa` | `/humbleflow:qa "bug"` |
| Plan | `/humbleflow-plan-feature` | `/humbleflow:plan-feature "feature"` |

### Review and validate

| Workflow | Pi | Claude Code |
|----------|----|-------------|
| Review | `/humbleflow-review` | `/humbleflow:review` |

### Maintain

| Workflow | Pi | Claude Code |
|----------|----|-------------|
| GC | `/humbleflow-garbage-collect` | `/humbleflow:garbage-collect` |

```
make quality       # View current quality grades
make garden        # Check for stale documentation
```

### Organize

```
# Tell the agent:
"Add [requirement] to the backlog"
"What's next in the backlog?"
"Prioritize the backlog"
```

---

## What "Done" Looks Like

A task is done when:

1. [ ] Acceptance criteria are verified (QA evidence exists for user-facing changes).
2. [ ] All agent reviewers have approved.
3. [ ] `make lint` passes (boundary + golden principles).
4. [ ] Execution plan is updated with completion notes and decisions.
5. [ ] **SPEC.md Capabilities** is updated with the completed feature.
6. [ ] **BACKLOG.md** is checked — completed item moved to Done, next item surfaced.
7. [ ] Quality grades are updated (`make quality`).
8. [ ] PR is merged.

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
my-project/
├── AGENTS.md              ← Agent's entry point. Read this to understand their view.
├── WORKFLOW.md            ← You are here.
├── SPEC.md                ← Project vision, users, MVP, capabilities, constraints.
│                             Auto-updated when features ship.
├── BACKLOG.md             ← Prioritized queue: Now → Next → Later → Done.
│                             Add requirements by telling the agent.
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
└── .pi/                   ← Pi integration (if using Pi).
    ├── skills/humbleflow/ ← The SDLC workflow skill.
    └── prompts/            ← Prompt templates.
```

---

## Getting Started

### New project (greenfield)

1. **Install:** Install humbleflow for your platform:
   - Pi: `pi install git:github.com/tahopetis/humbleflow`
   - Claude Code: `/plugin install humbleflow@<marketplace>` or `claude --plugin-dir <path>`
   - CLI only: `npm install -g humbleflow`
2. **Create directory:** `mkdir myapp && cd myapp`
3. **Initialize:** Type the init command for your platform. The agent will ask 6 discovery questions and scaffold everything.
4. **Review:** Read `SPEC.md` and `BACKLOG.md` to confirm the vision.
5. **Build:** Invoke the implement workflow. The agent reads SPEC.md, creates a plan, and starts building.

### Existing project (brownfield)

1. **Initialize:** Run `humbleflow init . --brownfield` from the CLI.
2. **Map the codebase:** Invoke the plan-feature workflow. The agent discovers existing domains.
3. **Build:** Same as above — the agent creates a plan and implements.

### The daily loop

```
You tell the agent what you need
  → Agent adds to BACKLOG.md, asks to prioritize
    → Agent plans and builds the top item
      → Agent merges, updates SPEC.md, surfaces next backlog item
        → You say "yes" or "add this instead"
```

SPEC.md and BACKLOG.md are YOUR documents. Review them periodically. They're the project's memory — the agent writes them, but you own the vision.

---

## FAQ

### How do I add new requirements after the MVP is built?

Just tell the agent what you need. It adds items to `BACKLOG.md`, asks you to prioritize, then starts on the top item. The loop:

```
tell → backlog → plan → build → merge → SPEC auto-updates → next backlog item
```

Example:
```
You:   "New requirements: recurring invoices, payment reminders, multi-currency"
Agent: Adds all three to BACKLOG.md → "All captured. Which first?"
You:   "Recurring invoices"
Agent: Plans → builds → merges → "Done. Next: payment reminders?"
```

### Can I see what's been built so far?

Yes — read `SPEC.md`. The `## Capabilities` section lists every completed feature with checkmarks. It's auto-updated on every merge.

### How do I group work into releases?

Set a `milestone` field in plan frontmatter: `milestone: v1.0`. All plans with the same milestone are part of that release. When the milestone is done, the agent can archive and tag it.

### When do I write code vs. prompt?

You don't write application code. You write prompts. You define what "done" looks like.

The only files you might edit directly are:
- `SPEC.md` — to refine the vision or update constraints
- `BACKLOG.md` — to reorder priorities or add items yourself
- `docs/principles.md` — to encode new taste rules

Everything else is agent-generated and agent-maintained. If you find yourself wanting to edit code, ask instead: "what capability is missing that made the agent get this wrong?" Then encode it into a tool, linter, or documentation.
