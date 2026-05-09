---
description: Create an execution plan from acceptance criteria, identifying unknowns and risks.
argument-hint: "<feature-description>"
---
Create an execution plan for the following feature following the Humbleflow planning phase.

## Feature
$ARGUMENTS

## Process

### 1. Clarify
Ask ONE clarifying question if anything is ambiguous. Pick the single most important unknown. Do not ask multiple questions — resolve one at a time.

### 2. Research
- Read `docs/architecture.md` to identify affected domains
- Read `docs/quality.md` to understand current grades in those domains
- Check `plans/` for related or conflicting plans

### 3. Plan
Create a new plan file at `plans/YYYY-MM-DD-<slug>.md` using the template from `plans/template.md`.

Fill in every section:

#### Goal
One sentence describing what this plan achieves.

#### Constraints
What must NOT change. Performance requirements. Backwards compatibility. Security constraints.

#### Unknowns
Surface what you don't know. Be honest. Unknowns are not failures — they're what you need to resolve before or during implementation.

#### Success Criteria
Concrete, verifiable outcomes. "The user can..." or "The system no longer..." Use specific metrics where applicable.

#### Approach
The step-by-step strategy. What files/components are affected. What order to build in (depth-first: types → config → repo → service → runtime → UI). What new dependencies are needed. Risk mitigation for each step.

#### Progress Log
Start with the plan creation entry.

#### Decision Log
Start empty. Decisions are captured during implementation.

### 4. Validate
```bash
make validate-plan plans/<your-plan>.md
```

### 5. Present
Present the plan to the human. Highlight:
- The approach in 2-3 sentences
- Unknowns that need human input
- Risks and mitigations
- Affected domains and their current quality grades

Wait for human approval before implementation (full plans). Lightweight plans can proceed without explicit approval.

## Template Reference
See `plans/template.md` for the full template with all sections.
