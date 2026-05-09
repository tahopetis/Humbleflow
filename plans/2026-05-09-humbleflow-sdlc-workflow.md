---
created: 2026-05-09
status: completed
type: meta
supersededBy: null
---

# Plan: Humbleflow Workflow

Build an agent-first SDLC workflow for the `humbleflow` project, based on OpenAI's Harness Engineering principles. The workflow enables agents (primarily Codex, but framework-agnostic) to drive the full software lifecycle: specify → plan → implement → review → QA → merge → maintain.

## Goals

1. **Agent-legible codebase** — The repository itself is the system of record. Agents can reason about the full business domain directly from files in the repo. No Google Docs, no Slack threads, no tribal knowledge.

2. **Humans steer, agents execute** — Human time is the scarce resource. Humans translate intent into prompts and acceptance criteria, validate outcomes, and encode taste as mechanical rules. Agents do everything else.

3. **Mechanical enforcement of architecture & taste** — Boundaries, invariants, and golden principles are enforced by linters and CI, not by code review. Corrections are automated and continuous.

4. **Progressive disclosure** — Agents start with a small, stable entry point and are taught where to look next. They are never overwhelmed with a 1,000-page manual.

5. **Entropy control via garbage collection** — Recurring background agents scan for drift, update quality grades, and open refactoring PRs. Technical debt is paid down continuously, not in bursts.

## Architecture

### Component Map

```
                    ┌──────────────────────────┐
                    │     humbleflow skill    │  ← Pi skill (agent's "map")
                    │  (SKILL.md + references)  │
                    └──────────┬───────────────┘
                               │ loads & follows
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                     AGENTS.md (TOC)                          │
│  ~100 lines. Points to deeper docs. Injected into context.   │
└──────────────────────────────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌──────────────────┐  ┌───────────────┐  ┌──────────────────┐
│   docs/           │  │  plans/       │  │  tools/          │
│  (system of       │  │  (execution   │  │  (mechanical     │
│   record)         │  │   plans)      │  │   enforcement)   │
│                   │  │               │  │                  │
│ • architecture.md │  │ • templates   │  │ • linters        │
│ • quality.md      │  │ • active      │  │ • scanners       │
│ • principles.md   │  │ • completed   │  │ • validators     │
└──────────────────┘  └───────────────┘  └──────────────────┘
```

### Layers (cross-cutting)

| Layer | Responsibility | Artifacts |
|-------|---------------|-----------|
| **Steering** | Human intent → prompts, acceptance criteria | AGENTS.md, docs/principles.md |
| **Map** | Agent discovers what to do and how | humbleflow skill, AGENTS.md |
| **Knowledge** | System of record for architecture, quality, decisions | docs/ |
| **Planning** | Versioned execution plans with progress/decision logs | plans/ |
| **Enforcement** | Mechanical invariants run by CI and background agents | tools/ |
| **Execution** | Agents implement, review, QA, merge | (agent-driven, not pre-built) |

## Phases & Deliverables

### Phase 1: Foundation — The Map & Knowledge Base

**Goal:** Give agents a navigable repository from day one. The skill, TOC, and knowledge docs are the first thing built.

**Deliverables:**

| # | Deliverable | Description | Depends on |
|---|------------|-------------|------------|
| 1.1 | `AGENTS.md` | Table of contents (~100 lines). Entry point injected into agent context. Points to docs/, plans/, tools/. Includes core beliefs and operating principles. | — |
| 1.2 | `.pi/skills/humbleflow/SKILL.md` | Pi skill file. Describes the full SDLC workflow: phases, tools, conventions. Progressive disclosure — brief phase descriptions with pointers to `references/`. | — |
| 1.3 | `.pi/skills/humbleflow/references/phases.md` | Deep dive on each SDLC phase: entry criteria, agent instructions, exit criteria, tool invocations. | 1.2 |
| 1.4 | `.pi/skills/humbleflow/references/architecture.md` | The layered architecture model (Types→Config→Repo→Service→Runtime→UI). Dependency rules. Provider interfaces. | 1.2 |
| 1.5 | `.pi/skills/humbleflow/references/golden-principles.md` | Taste invariants: parse-don't-validate, shared-utils-over-hand-rolled, no-YOLO-probing, structured logging, naming conventions. | 1.2 |
| 1.6 | `docs/architecture.md` | Top-level map of domains and package layering (matklad-style ARCHITECTURE.md). | 1.1 |
| 1.7 | `docs/quality.md` | Quality grades per product domain and architectural layer. Tracks gaps over time. | 1.1 |
| 1.8 | `docs/principles.md` | Golden principles with rationale. The canonical source that linters enforce. | 1.1 |
| 1.9 | `WORKFLOW.md` | Human-readable SDLC specification. Describes the full flow for humans onboarding to the project. | 1.2, 1.3 |

**Parallelizable:** 1.2+1.3+1.4+1.5 can be written in parallel. 1.6+1.7+1.8 can be written in parallel. 1.1 should come first as it defines the structure. 1.9 depends on the skill being defined.

### Phase 2: Planning Infrastructure

**Goal:** Execution plans are first-class, versioned artifacts with progress/decision logs. Agents can create, follow, and complete plans without external context.

**Deliverables:**

| # | Deliverable | Description | Depends on |
|---|------------|-------------|------------|
| 2.1 | `plans/template.md` | Execution plan template with sections: goal, constraints, unknowns, success criteria, progress log, decision log, completion notes. | 1.1 |
| 2.2 | `plans/template-lightweight.md` | Lightweight plan template for small changes (< 1 day). Minimal structure. | 2.1 |
| 2.3 | `plans/README.md` | Conventions: naming, lifecycle (draft→active→completed→archived), linking to PRs. | 2.1 |

**Parallelizable:** 2.1+2.2+2.3 can be written in parallel.

### Phase 3: Mechanical Enforcement Tools

**Goal:** Architecture, taste, and quality are enforced mechanically, not by human review. Agents receive immediate feedback on violations.

**Deliverables:**

| # | Deliverable | Description | Depends on |
|---|------------|-------------|------------|
| 3.1 | `tools/lint-boundaries.py` | Validates dependency directions per the layered architecture. Parses import graphs, flags violations. Output includes remediation instructions for agent context. | 1.6 |
| 3.2 | `tools/lint-golden.py` | Validates golden principles: structured logging usage, naming conventions, file size limits, no YOLO data probing, schema validation at boundaries. | 1.8 |
| 3.3 | `tools/quality-grade.py` | Scans domains, evaluates against quality rubric, updates `docs/quality.md`. | 1.7 |
| 3.4 | `tools/doc-gardener.py` | Finds stale documentation (docs referencing deleted/moved code), opens fix-up PRs or emits a report. | 1.6, 1.7, 1.8 |
| 3.5 | `tools/validate-plan.py` | Validates execution plan structure: required sections present, progress log updated, decisions captured. | 2.1 |
| 3.6 | `tools/Makefile` | Orchestrates all tools. `make lint`, `make quality`, `make garden`, `make validate-plan`. | 3.1-3.5 |
| 3.7 | `tools/ci-config.yml` | CI configuration that runs enforcement tools on every PR. Blocks merges on boundary violations. | 3.6 |

**Dependencies:** 3.1 → 1.6, 3.2 → 1.8, 3.3 → 1.7, 3.4 → 1.6+1.7+1.8, 3.5 → 2.1, 3.6 → 3.1-3.5, 3.7 → 3.6.

**Parallelizable:** 3.1, 3.2, 3.3, 3.4, 3.5 can all start in parallel (they only depend on docs, not on each other).

### Phase 4: Agent Workflow Templates

**Goal:** Pre-built agent workflows for common SDLC tasks: parallel review, garbage collection, context building, handoff planning. These are Pi chain templates or prompt templates that agents invoke.

**Deliverables:**

| # | Deliverable | Description | Depends on |
|---|------------|-------------|------------|
| 4.1 | `.pi/prompts/review.md` | Parallel adversarial review: launches N fresh-context reviewers with distinct angles, synthesizes findings. | 1.1, 1.2 |
| 4.2 | `.pi/prompts/garbage-collect.md` | Garbage collection pass: scans for drift, opens refactoring PRs, updates quality grades. | 3.3, 3.4 |
| 4.3 | `.pi/prompts/implement.md` | Full implementation flow: validate state → plan → implement → self-review → iterate → PR. | 1.2 |
| 4.4 | `.pi/prompts/qa.md` | QA flow: reproduce bug → record video → implement fix → validate → record fix video → PR. | 1.2 |
| 4.5 | `.pi/prompts/plan-feature.md` | Feature planning: create execution plan from acceptance criteria, identify unknowns, estimate. | 2.1 |

**Parallelizable:** All 4.x can be written in parallel.

## Dependency Graph

```
Phase 1 (Foundation)
├── 1.1 AGENTS.md ─────────────────────────────────────────┐
├── 1.2 SKILL.md ──────────────────────┐                    │
├── 1.3 references/phases.md ─────────┤                    │
├── 1.4 references/architecture.md ───┤                    │
├── 1.5 references/golden-principles.md┤                   │
├── 1.6 docs/architecture.md ──────────┼── after 1.1 ──────┤
├── 1.7 docs/quality.md ───────────────┤                   │
├── 1.8 docs/principles.md ────────────┤                   │
└── 1.9 WORKFLOW.md ───────────────────┼── after 1.2+1.3 ─┘
                                        │
Phase 2 (Planning)                      │
├── 2.1 plans/template.md ─────────────┼── after 1.1
├── 2.2 plans/template-lightweight.md ─┤
└── 2.3 plans/README.md ───────────────┘
                                        │
Phase 3 (Enforcement Tools)             │
├── 3.1 lint-boundaries.py ────────────┼── after 1.6
├── 3.2 lint-golden.py ────────────────┼── after 1.8
├── 3.3 quality-grade.py ──────────────┼── after 1.7
├── 3.4 doc-gardener.py ───────────────┼── after 1.6+1.7+1.8
├── 3.5 validate-plan.py ──────────────┼── after 2.1
├── 3.6 Makefile ──────────────────────┼── after 3.1-3.5
└── 3.7 ci-config.yml ────────────────┘── after 3.6
                                        │
Phase 4 (Agent Workflows)               │
├── 4.1 review.md ─────────────────────┼── after 1.1+1.2
├── 4.2 garbage-collect.md ────────────┼── after 3.3+3.4
├── 4.3 implement.md ──────────────────┼── after 1.2
├── 4.4 qa.md ─────────────────────────┤
└── 4.5 plan-feature.md ───────────────┘── after 2.1
```

## What This Is NOT

- **Not a CI/CD pipeline tool** — We're not building CircleCI or GitHub Actions. We're building the *workflow and enforcement logic* that CI invokes.
- **Not a code generation framework** — Agents write the code. We build the harness that makes them reliable.
- **Not tied to a specific agent** — The workflow works with Codex, Claude, or any agent that can read files and invoke tools. Pi-specific parts (skill, prompts) are additive.
- **Not application code** — This is meta-infrastructure. The `humbleflow` application code lives alongside this, built *by* agents *using* this harness.

## Known Gaps & Open Questions

1. **Agent capability variance** — The article uses Codex with Chrome DevTools Protocol access, worktree isolation, and ephemeral observability stacks. We don't yet know which capabilities the available agents have. The skill should be written to degrade gracefully.

2. **Worktree isolation** — The article's "one worktree per change" model is powerful but requires infra setup. Should we include worktree tooling in this plan, or defer it?

3. **Observability integration** — LogQL, PromQL, CDP access — these are deep integrations. Should we scaffold the interfaces now and implement later?

4. **Merge automation** — How aggressive should auto-merge be? The article says "minimal blocking gates." We should define the thresholds.

5. **Model evolution** — The article acknowledges this is unknown. The workflow should be modular enough to swap out components as models improve.

## Success Criteria

- [ ] A new agent, given only `AGENTS.md` and the skill, can navigate the repo and understand its structure
- [ ] Architecture violations are caught mechanically before merge
- [ ] Execution plans are self-contained artifacts that capture decisions
- [ ] Quality grades are tracked per domain and updated automatically
- [ ] The full SDLC loop (specify→plan→implement→review→QA→merge→maintain) is documented and invocable
- [ ] Human engineers interact primarily through prompts and validation, not code
