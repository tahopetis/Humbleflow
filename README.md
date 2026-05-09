# humbleflow · [![pi-package](https://img.shields.io/badge/pi-package-blue)](https://pi.dev/packages)

A Pi package for agent-first SDLC — based on [OpenAI's Harness Engineering principles](https://openai.com/index/harness-engineering/). **Humans steer. Agents execute.**

---

## Quick Install

```bash
# Option A: npm (CLI on PATH + Pi resources)
npm install -g humbleflow

# Option B: Pi package (skill + prompts, CLI via full path)
pi install git:github.com/tahopetis/humbleflow
```

Then initialize your project:

```bash
# Option A users: just run the command
humbleflow init . --greenfield --name "MyApp" --domains "auth,billing"

# Option B users: use the full path
~/.pi/agent/git/github.com/tahopetis/humbleflow/humbleflow init . --greenfield --name "MyApp"
```

---

## What You Get

| Component | What it does |
|-----------|-------------|
| **`humbleflow` skill** | Loaded automatically by agents for any SDLC work. Covers all 7 phases: specify → plan → implement → review → QA → merge → maintain. |
| **5 prompt templates** | `/implement`, `/review`, `/qa`, `/garbage-collect`, `/plan-feature` — one-shot workflows for common tasks. |
| **`humbleflow` CLI** | One-command project initialization (`humbleflow init`). Greenfield or brownfield. Generates architecture docs, quality tables, and `AGENTS.md` customized to your project. |
| **7 enforcement tools** | Python linters for boundary validation, golden-principle checks, quality grading, doc gardening, plan validation — plus a `Makefile` that ties them together. |

---

## Quick Start

### Greenfield (new project)

```bash
humbleflow init ~/projects/myapp --greenfield --name "MyApp" --domains "auth,billing,users"
cd ~/projects/myapp
# Agents now auto-load the humbleflow skill. Just prompt:
#   "Add two-factor authentication to the login flow"
```

### Brownfield (existing codebase)

```bash
humbleflow init ~/projects/existing-app --brownfield
# Auto-discovers domains from src/domains/*, grades existing code, warns on overwrites
cd ~/projects/existing-app
make all   # Run linters and quality checks on existing code
```

### Interactive mode

```bash
humbleflow init ~/projects/myapp
# Prompts for project name, description, domains, and mode
```

### Dry run

```bash
humbleflow init ~/projects/myapp --greenfield --name "MyApp" --dry-run
# Shows what would be created without writing anything
```

---

## What's in the Box

```
humbleflow/
├── humbleflow                   ← CLI: humbleflow init / humbleflow version
├── AGENTS.md                    ← Agent entry point (TOC ~100 lines)
├── WORKFLOW.md                  ← Human-readable SDLC guide
│
├── skills/humbleflow/         ← Pi skill (loaded on-demand by agents)
│   ├── SKILL.md
│   └── references/
│       ├── phases.md            ← Phase-by-phase agent instructions
│       ├── architecture.md      ← Layered architecture rules
│       └── golden-principles.md ← Taste invariants
│
├── prompts/                     ← Pi prompt templates
│   ├── implement.md             ← /implement: full implementation flow
│   ├── review.md                ← /review: parallel adversarial review
│   ├── qa.md                    ← /qa: bug repro → fix → validate
│   ├── garbage-collect.md       ← /garbage-collect: drift scan → refactor
│   └── plan-feature.md          ← /plan-feature: spec → execution plan
│
└── templates/                   ← Project scaffolding (copied by humbleflow init)
    ├── AGENTS.md, WORKFLOW.md, Makefile
    ├── docs/                    ← System of record templates
    ├── plans/                   ← Execution plan infrastructure
    └── tools/                   ← Mechanical enforcement
```

---

## Architecture

Inspired by OpenAI's internal experiment: building a product with **0 lines of manually-written code**. The key insight — "give Codex a map, not a 1,000-page manual" — shapes every design decision.

| Principle | How humbleflow enforces it |
|-----------|------------------------------|
| **Progressive disclosure** | `AGENTS.md` is ~100 lines. Agents load deeper docs on-demand. |
| **Architecture as code** | `lint-boundaries.py` validates Types→Config→Repo→Service→Runtime→UI dependency directions. |
| **Taste as code** | `lint-golden.py` checks parse-don't-validate, no YOLO probing, structured logging, naming conventions. |
| **Corrections over waiting** | Minimal merge gates. Test flakes → re-run. Linter violations → fix, don't block. |
| **Entropy control** | `/garbage-collect` + `doc-gardener.py` scan for drift, open refactoring PRs, update quality grades. |

[Read the full article →](https://openai.com/index/harness-engineering/)

---

## Requirements

- **Python 3.9+** (for enforcement tools and init script)
- **Pi** (for skill and prompt template loading)
- That's it. No npm dependencies, no external services.

---

## License

MIT
