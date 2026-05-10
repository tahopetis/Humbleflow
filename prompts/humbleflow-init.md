---
description: Initialize a new humbleflow project. Guided discovery → SPEC.md → scaffold → ready to build.
---
You are initializing a new Humbleflow project in the current directory. Guide the human through discovery, then scaffold everything.

## Phase 1: Discovery

Ask these questions one at a time. Do NOT ask them all at once. Wait for each answer before asking the next.

1. **"What's the name of this project?"** (default: current directory name)

2. **"What problem does it solve? Describe it in one or two sentences."**

3. **"Who are the primary users?"** (e.g., developers, designers, end consumers, internal team)

4. **"What's the single most important thing it must do?** — the MVP anchor. If nothing else works, this must."

5. **"What are the business domains?"** Suggest 2-4 based on the description. Let the human confirm or revise.
   Example: For a SaaS billing app → "auth, billing, subscriptions, analytics"
   Format: comma-separated, lowercase, one word each.

6. **"Any constraints?"** (performance, security, compliance, platform, deployment). If none, note "no specific constraints."

## Phase 2: Generate SPEC.md

Create `SPEC.md` from the answers. Use this exact format:

```markdown
# {{PROJECT_NAME}} — Specification

## Vision
{{Two-sentence description from Q2}}

## Users
{{Answer from Q3}}

## MVP
{{Answer from Q4}}

## Capabilities
### Built
<!-- Completed features appear here after merge -->

### In Progress
- [ ] MVP: {{MVP anchor}} (see plans/YYYY-MM-DD-initial-build.md)

## Domains
{{Domains from Q5, one per line with brief descriptions}}

## Constraints
{{Answer from Q6}}

## Status
**Phase:** planning
**Last updated:** {{today}}
```

## Phase 3: Generate BACKLOG.md

Create `BACKLOG.md` with this format:

```markdown
# Backlog — {{PROJECT_NAME}}

> Items are added during development or via discovery.
> Mark completed with `[x]` and add a completion date.
> Prioritization: Now → Next → Later.

## Now (current)
- [ ] MVP: {{MVP anchor}} — see `plans/YYYY-MM-DD-initial-build.md`

## Next (upcoming)
<!-- Add items here as requirements come in -->

## Later (future)
<!-- Park ideas here for later consideration -->

## Done
<!-- Completed items move here with completion dates -->
```

## Phase 4: Scaffold project

Find the humbleflow package templates. Check these locations in order:
- `~/.pi/agent/git/github.com/tahopetis/humbleflow/templates/`
- `./templates/` (if already in a humbleflow project)
- `~/.pi/agent/npm/node_modules/humbleflow/templates/`

If the templates directory is not found, tell the human to first run:
```bash
pi install git:github.com/tahopetis/humbleflow
```

Copy and customize these files from the templates directory to the current directory:

| Source (in templates/) | Destination | Customization |
|------------------------|-------------|---------------|
| `AGENTS.md` | `./AGENTS.md` | Replace `{{PROJECT_NAME}}` with project name. Replace `{{REPO_MAP}}` with generated tree using project slug. |
| `WORKFLOW.md` | `./WORKFLOW.md` | Replace `Humbleflow` with project name. Replace `humbleflow` with project slug. |
| `Makefile` | `./Makefile` | No changes (generic). |
| `SPEC.md` | `./SPEC.md` | Replace `{{PROJECT_NAME}}`, `{{PROJECT_DESCRIPTION}}`, `{{CREATED_DATE}}` with today. Then append the rich content generated in Phase 2 (vision, users, MVP, domains, constraints). |
| `docs/architecture.md` | `./docs/architecture.md` | Replace `{{PROJECT_NAME}}`, `{{PROJECT_DESCRIPTION}}`, `{{PROJECT_STATUS}}`, `{{DOMAIN_ARCHITECTURE}}`, `{{PROJECT_DECISIONS}}`. |
| `docs/quality.md` | `./docs/quality.md` | Replace `{{DOMAIN_QUALITY_ROWS}}`, `{{QUALITY_SUMMARY}}`, `{{QUALITY_YAML}}`. |
| `docs/principles.md` | `./docs/principles.md` | No changes (generic). |
| `plans/README.md` | `./plans/README.md` | No changes (generic). |
| `plans/template.md` | `./plans/template.md` | No changes (generic). |
| `plans/template-lightweight.md` | `./plans/template-lightweight.md` | No changes (generic). |
| `BACKLOG.md` | `./BACKLOG.md` | No changes — leave as template. |
| `tools/*` (all files) | `./tools/` | No changes (generic). |

Then copy Pi resources from the PACKAGE ROOT (not templates/):

| Source (package root) | Destination |
|----------------------|-------------|
| `skills/humbleflow/*` (all files) | `./.pi/skills/humbleflow/` |
| `prompts/implement.md` | `./.pi/prompts/implement.md` |
| `prompts/review.md` | `./.pi/prompts/review.md` |
| `prompts/qa.md` | `./.pi/prompts/qa.md` |
| `prompts/garbage-collect.md` | `./.pi/prompts/garbage-collect.md` |
| `prompts/plan-feature.md` | `./.pi/prompts/plan-feature.md` |

**Important:** Only copy files that don't already exist. If a file exists, skip it and tell the human. Do NOT copy `prompts/humbleflow-init.md` — it's only needed for initialization, not in the project.

**Important:** Only copy files that don't already exist. If a file exists, skip it and tell the human.

For the templated files (AGENTS.md, WORKFLOW.md, docs/architecture.md, docs/quality.md), read the source, apply the customizations, then write to the destination.

### Domain section generation (for architecture.md)

For each domain, generate a section like:

```markdown
### {N}. {PascalCase name} (`{slug}/`)

**Responsibility:** [One sentence from the domain description.]

**Key types:**
- `{TypeName}` (primary entity)
- Additional types TBD

**Dependencies:**
- None (independent domain)
```

### Quality table generation (for quality.md)

Generate A-grade rows for every domain + shared, app, providers. Each gets rows for all 6 layers (types, config, repo, service, runtime, ui). Use today's date.

### AGENTS.md customization

Replace `{{PROJECT_NAME}}` with the project name. Generate the repository map tree using the project slug (lowercase, hyphens).

## Phase 5: Initial execution plan

Create `plans/YYYY-MM-DD-initial-build.md` (use today's date) with:

```markdown
---
created: {{today}}
status: active
assignedTo: agent
blockedBy: null
supersededBy: null
---

# Plan: Initial Build — {{PROJECT_NAME}}

## Goal
Build the MVP: {{MVP description from Q4}}

## Constraints
{{Constraints from Q6}}

## Unknowns & Risks
| # | Unknown / Risk | Impact | Mitigation |
|---|---------------|--------|------------|
| 1 | Exact technical stack not specified | Could pick wrong framework | Use boring, well-known defaults; confirm with human |
| 2 | Scope may expand during implementation | Timeline/quality risk | Strict MVP gate: only the anchor capability |

## Success Criteria
- [ ] {{MVP anchor from Q4}} is implemented and testable
- [ ] All domains have type definitions
- [ ] Core user flow works end-to-end
- [ ] `make lint` passes
- [ ] Test coverage meets thresholds

## Affected Domains
{{Table: domain → layers → nature of change}}

## Approach
### Phase 1: Type definitions
- Define schemas and types for all domains
- Establish shared utilities

### Phase 2: Core implementation
- Build the MVP anchor capability
- Implement depth-first per domain

### Phase 3: Integration
- Wire domains together
- End-to-end flow validation

## Progress Log
| Date | Status | Notes |
|------|--------|-------|
| {{today}} | active | Project initialized. SPEC.md created. Ready for implementation. |
```

## Phase 6: Summary

Print a summary:

```
✅ Humbleflow initialized: {{PROJECT_NAME}}

Created:
  • SPEC.md — project vision, users, MVP, domains, constraints
  • BACKLOG.md — prioritized feature backlog (Now/Next/Later)
  • AGENTS.md — agent entry point
  • WORKFLOW.md — human SDLC guide
  • docs/ — architecture, quality grades, golden principles
  • plans/ — execution plan templates + initial build plan
  • tools/ — mechanical enforcement (lint, quality, garden)
  • .pi/ — skill + prompt templates

Next steps:
  1. Read SPEC.md to confirm the vision is correct
  2. Read plans/{{today}}-initial-build.md to review the plan
  3. Start building: /implement "Build the {{MVP anchor}}"
```
