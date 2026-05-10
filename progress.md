# Progress

## Timeline

### 2026-05-09 — Phase 1-4: Initial Build ✅

All 24 deliverables from the original plan completed:
- **Phase 1 (Foundation):** AGENTS.md, WORKFLOW.md, humbleflow skill + references, docs/ (architecture, quality, principles), Makefile
- **Phase 2 (Planning):** Plan templates (full + lightweight), plan conventions README
- **Phase 3 (Enforcement):** 6 Python tools (lint-boundaries, lint-golden, quality-grade, doc-gardener, validate-plan, ci-config) + Makefile
- **Phase 4 (Workflows):** 5 prompt templates (/implement, /review, /qa, /garbage-collect, /plan-feature)

### 2026-05-09 — Pi Package Restructuring ✅

Repackaged the project as a proper Pi package:
- Moved `skills/` and `prompts/` to package root (Pi convention for auto-discovery)
- Moved project template files into `templates/` directory (clean separation)
- Added `package.json` with `pi` manifest + `pi-package` keyword for discoverability
- Added `.pi/settings.json` for self-referencing local skills/prompts
- Clean separation: Pi resources vs project templates

### 2026-05-09 — Rename: harness-sdlc → humbleflow ✅

Renamed everything from "harness-sdlc" to "humbleflow":
- `skills/harness-sdlc/` → `skills/humbleflow/`
- SKILL.md name field updated to match directory name
- All text references updated across `.md`, `.py`, `.json` files
- Plan file renamed accordingly

### 2026-05-09 — CLI: humbleflow executable ✅

Replaced `init-harness.py` with a single executable `humbleflow` CLI:
- `humbleflow init <dir>` — project scaffolding (greenfield + brownfield)
- `humbleflow version` — version info
- `humbleflow help` — usage docs
- Supports both npm (`bin` field) and Pi install paths
- Interactive mode: prompts for name, description, domains, mode
- Dry-run mode: shows what would be created without writing

### 2026-05-09 — /humbleflow-init slash command ✅

Added guided project discovery as a Pi prompt template:
- Asks 6 discovery questions one at a time (not all at once)
- Generates `SPEC.md` from answers (vision, users, MVP, domains, constraints)
- Generates `BACKLOG.md` with MVP anchor
- Scaffolds all template files from the humbleflow package
- Creates an initial execution plan (`plans/YYYY-MM-DD-initial-build.md`)
- Updated `/plan-feature` to read `SPEC.md` for project context

### 2026-05-10 — SPEC.md Auto-Update ✅

Agents now auto-update SPEC.md on feature completion:
- Updated skill's Merge phase: append completed features to `SPEC.md` Capabilities
- Updated skill's Maintain phase: check `BACKLOG.md` after merge, report next item
- Post-merge exit criteria now includes SPEC.md update verification

### 2026-05-10 — BACKLOG.md + Milestone Tagging ✅

Added backlog management and milestone tracking:
- New `BACKLOG.md` template with Now → Next → Later → Done sections
- `/humbleflow-init` generates BACKLOG.md pre-populated with MVP anchor
- Added `milestone` field to both plan templates (optional)
- Agents read BACKLOG.md when new requirements arrive, add/prioritize items
- Agents check BACKLOG.md after merge, report next item to human

### 2026-05-10 — Documentation Sweep ✅

Updated all documentation to reflect new features:
- README.md: `/humbleflow-init`, SPEC.md, BACKLOG.md, 6 prompts (was 5)
- templates/AGENTS.md: SPEC.md + BACKLOG.md in repo map, new-requirement flow
- templates/WORKFLOW.md: updated phases, tools, done checklist, repo map
- progress.md: full chronological log (this file)

## Current File Tree

```
humbleflow/
├── AGENTS.md               ← Agent entry point (template, {{PLACEHOLDER}}s)
├── BACKLOG.md              ← Backlog template (Now → Next → Later → Done)
├── humbleflow              ← CLI executable
├── Makefile                ← Enforcement entry point
├── package.json            ← Pi + npm package manifest
├── README.md               ← Package docs
├── WORKFLOW.md             ← Human SDLC guide (template)
│
├── docs/                   ← System of record templates
│   ├── architecture.md     ← {{PLACEHOLDER}} templates
│   ├── principles.md       ← Golden principles (generic)
│   └── quality.md          ← {{PLACEHOLDER}} templates
│
├── plans/                  ← Execution plan infrastructure
│   ├── README.md           ← Plan conventions
│   ├── template.md         ← Full plan template
│   ├── template-lightweight.md  ← Lightweight plan template
│   └── 2026-05-09-humbleflow-sdlc-workflow.md  ← This project's plan
│
├── prompts/                ← Pi prompt templates (6)
│   ├── humbleflow-init.md  ← /humbleflow-init (guided discovery)
│   ├── implement.md        ← /implement
│   ├── review.md           ← /review
│   ├── qa.md               ← /qa
│   ├── garbage-collect.md  ← /garbage-collect
│   └── plan-feature.md     ← /plan-feature
│
├── skills/humbleflow/      ← Pi skill
│   ├── SKILL.md
│   └── references/
│       ├── phases.md       ← 7-phase SDLC instructions
│       ├── architecture.md ← Layered architecture rules
│       └── golden-principles.md ← Taste invariants
│
├── templates/              ← Project scaffolding
│   ├── AGENTS.md, WORKFLOW.md, Makefile, BACKLOG.md
│   ├── docs/ (architecture, quality, principles)
│   ├── plans/ (README, templates)
│   ├── tools/ (6 Python tools + CI config)
│   └── .pi/ (skills + prompts for target projects)
│
└── .pi/
    └── settings.json       ← Self-references ./skills and ./prompts
```

## Open Questions

1. **Worktree isolation** — Documented in skill but not mechanized. Per-plan worktree creation/deletion would enable true parallel execution.
2. **Observability integration** — LogQL/PromQL/CDP access for agents to self-diagnose. Interfaces scaffolded, implementation deferred.
3. **Merge automation** — Thresholds for auto-merge need definition. Currently: all reviews approved, CI green.
4. **Agent capability variance** — Skill written to degrade gracefully. Practical limits unknown until tested across runtimes.
5. **Brownfield domain discovery** — `humbleflow init --brownfield` auto-discovers from `src/domains/*`. Custom directory structures need manual mapping.
