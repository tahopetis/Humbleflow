# Execution Plans — Conventions

## What Are Execution Plans?

Execution plans are **first-class, versioned artifacts** checked into the repository.
They are the bridge between human intent ("build feature X") and agent execution
("here's exactly what to do"). Every non-trivial change in Humbleflow starts with a
plan.

A plan captures:

- **What** we're building (goal, acceptance criteria)
- **Why** we're building it (motivation, constraints)
- **How** we'll build it (approach, affected domains, files)
- **What we don't know** (unknowns, risks, open questions)
- **What happened** (progress log, decisions made, completion notes)

Plans are written by agents and reviewed by humans (for full plans) or by peer agents
(for lightweight plans). They live in the repo alongside the code they describe. This
means a future agent can read a plan and understand the full arc of a feature — from
initial intent to shipped outcome — without accessing any external context.

## Why Plans Exist

In an agent-driven SDLC:

1. **Context persistence.** Agent sessions are ephemeral. A plan survives across
   sessions, agent restarts, and even across different agents. The plan is the thread
   that connects multiple implementation sessions.

2. **Progressive disclosure.** AGENTS.md tells you *how* to work. The skill tells you
   *what phases* to follow. The plan tells you *what to do right now* on this specific
   task. An agent loading a plan knows exactly where it left off.

3. **Decision capture.** When an agent makes a tradeoff, it goes in the decision log.
   Months later, another agent can understand why a choice was made without guessing
   or re-litigating.

4. **Mechanical validation.** Plans are validated by `tools/validate-plan.py`. If a
   plan is missing required sections or has a stale progress log, the tool catches it.

5. **Human visibility.** Humans don't read every line of code. They read plans.
   A human scanning `plans/` can see what's in flight, what's complete, and what
   decisions were made — at a glance.

## Lifecycle

Every plan moves through four states:

```
draft → active → completed → archived
```

### draft

The plan is being written. It has frontmatter but sections may be incomplete.
No work has started. A draft plan should not be assigned to an agent.

**Frontmatter:**
```yaml
---
created: 2026-05-09
status: draft
supersededBy: null
---
```

### active

Work is in progress. The plan has all required sections filled. An agent has
checked it out and is executing against it. The progress log is updated with
each implementation session.

**Frontmatter:**
```yaml
---
created: 2026-05-09
status: active
supersededBy: null
---
```

### completed

All work is done. All acceptance criteria are met. The PRs are merged. The
completion notes and final decision log are written.

**Frontmatter:**
```yaml
---
created: 2026-05-09
status: completed
supersededBy: null
---
```

### archived

The plan is no longer active and the work is long done. Archived plans move to
`plans/archived/` (if the convention exists) or remain in `plans/` with
`status: archived`. Archived plans are kept for historical reference — they
are never deleted.

**Frontmatter:**
```yaml
---
created: 2026-05-09
status: archived
supersededBy: 2026-06-15-rewrite-auth.md
---
```

The `supersededBy` field points to a newer plan that replaced this one. Only
set this when a plan was deliberately abandoned in favor of a new approach —
not when it was simply completed.

## Naming Convention

```
plans/YYYY-MM-DD-<slug>.md
```

- **YYYY-MM-DD** — The date the plan was created (not the due date).
- **slug** — A short, descriptive, kebab-case identifier.

Examples:
```
plans/2026-05-09-humbleflow-workflow.md
plans/2026-05-10-add-user-authentication.md
plans/2026-05-11-fix-payment-timeout-bug.md
```

Do not include status, assignee, or priority in the filename. Those belong in
the frontmatter.

## Full Plan vs Lightweight Plan

### Full Plan (`template.md`)

Use for:
- Multi-day features
- Architectural changes
- Cross-domain work
- Work with external dependencies
- Anything with significant unknowns or risks

A full plan has all sections: goals, constraints, unknowns, success criteria,
approach, progress log, decision log, risks, and completion notes. It is
reviewed by a human before work begins.

### Lightweight Plan (`template-lightweight.md`)

Use for:
- Single-domain changes
- Work estimable at < 1 day of agent time
- Bug fixes with clear reproduction steps
- Small refactors, dependency updates, doc changes
- Tasks where the approach is obvious

A lightweight plan has a minimal structure: goal, approach, acceptance criteria,
and a brief progress log. It does not require human review before work begins
(though a human may request review).

**Rule of thumb:** If you need to think about architecture, use a full plan.
If you know exactly which 2-3 files you'll touch, use a lightweight plan.
When in doubt, use a full plan — it's cheaper to skip sections of a full plan
than to discover you needed them halfway through.

### Template Files

- **Full plan template:** [`template.md`](template.md)
- **Lightweight plan template:** [`template-lightweight.md`](template-lightweight.md)

Both templates live in this directory. When creating a new plan, copy the
appropriate template, rename it following the naming convention, and fill it in.

## Linking to PRs and Issues

Plans are the canonical source of truth. PRs and issues reference the plan,
not the other way around.

### In the plan

Link relevant PRs and issues in the progress log:

```markdown
## Progress Log

### 2026-05-09 14:30 — Session 1
- Created domain types for `app-settings`.
- Opened PR #42: `feat(app-settings): add domain types`

### 2026-05-10 09:15 — Session 2
- Implemented `app-settings` service layer.
- PR #42 updated.
- Addressed review feedback from agent-reviewer on #42.

### 2026-05-10 16:00 — Session 3
- PR #42 merged.
- Opened PR #43: `feat(app-settings): add UI components`.
```

### In the PR

Reference the plan in the PR description:

```
## Plan
[plans/2026-05-09-app-settings.md](./plans/2026-05-09-app-settings.md)

## What
Implements the `app-settings` domain types as specified in the plan. This is the first of several PRs.

## Acceptance Criteria
- [x] `AppSettings` schema defined
- [x] `AppSettingsConfig` type defined
- [x] Tests pass
```

## Progress Log

The progress log is the **running timeline** of the plan's execution. It is the
most important section of an active plan. Update it after every implementation
session — even if the session was short or yielded no code changes.

**What to log:**
- Files created, modified, or deleted
- PRs opened, updated, or merged
- Review feedback received and addressed
- Build/test failures encountered and resolved
- Blockers hit and how they were resolved (or escalated)
- QA results (bug reproduced, fix validated)

**Format:**
```markdown
## Progress Log

### YYYY-MM-DD HH:MM — Brief session summary
- What was done.
- What was decided.
- What's next.
```

Keep entries concise. One entry per session. If a single issue spans 10 sessions,
the progress log has 10 entries. This makes it trivially auditable by humans and
agents alike.

## Decision Log

The decision log captures **tradeoffs and choices** that future agents need to
understand. Not every implementation detail goes here — only decisions that
someone would reasonably question or need context for later.

**What to log:**
- Technology choices (library X over Y, and why)
- Architectural tradeoffs (denormalized for performance, coupling accepted for now)
- Constraint acceptances (known limitation we're shipping with)
- Rejected alternatives (considered approach A but chose B because...)
- Escalation outcomes (human decided X, so we did Y)

**Format:**
```markdown
## Decision Log

### 2026-05-09 — Use Zod over TypeBox
**Context:** Needed schema validation for API boundaries.
**Decision:** Use Zod.
**Rationale:** The model is already familiar with Zod. TypeBox would require additional
training context. Zod's `.parse()` pattern matches our "parse, don't validate" principle
more naturally.
**Alternatives considered:** TypeBox (rejected: steeper learning curve for agents), Joi
(rejected: not type-safe).

### 2026-05-10 — Accept 800ms cold start for v1
**Context:** Service startup time measured at 800ms on cold start. Target was 500ms.
**Decision:** Ship as-is. Address in v2.
**Rationale:** Human reviewer approved. Optimization would require architectural rework
disproportionate to the 300ms gap. Graceful degradation path exists.
```

## Agent-Readable and Machine-Validatable

Plans are designed to be consumed by two audiences: **agents** (who read and
execute them) and **tools** (who validate their structure).

### Agent readability

- Plans use a consistent structure. An agent loading any plan in the repo knows
  exactly where to find the goal, progress, and decisions.
- Plans are markdown — no custom formats, no YAML beyond frontmatter.
- Plans are self-contained. An agent can load a plan file and have everything
  it needs: what to do, what's been done, what was decided.
- Plans reference other repo artifacts (`docs/`, other plans) by relative path.
  No external URLs that might rot.

### Machine validation

Run `tools/validate-plan.py` against any plan:

```bash
make validate-plan plans/2026-05-09-humbleflow-workflow.md
```

The validator checks:
- Frontmatter is present and valid (created date, status, supersededBy).
- Required sections exist (depends on template type).
- Progress log is not empty for `active` plans.
- Decision log is not empty for `completed` plans.
- No stale references (files linked in the plan still exist).
- PR links are valid (if the tool has access to the PR API).

Validation is informational for `draft` plans and warning-level for `active`
plans. A `completed` plan with missing sections is a hard failure — it means
the plan was never properly finished.

## Directory Organization

```
plans/
├── README.md                          ← You are here.
├── template.md                        ← Full execution plan template.
├── template-lightweight.md            ← Lightweight plan template.
├── 2026-05-09-humbleflow-workflow.md  ← Active/completed plans live here.
├── 2026-05-10-some-feature.md
└── archived/                          ← Optional: archived plans.
    └── 2026-01-15-old-feature.md
```

Active and completed plans stay in the root of `plans/`. Archived plans may
move to `plans/archived/` to keep the root directory focused on current work.
Whether to use an `archived/` subdirectory is a project convention — either
approach is valid as long as it's consistent.
