# humbleflow · [![pi-package](https://img.shields.io/badge/pi-package-blue)](https://pi.dev/packages)

A Pi package for agent-first SDLC — based on [OpenAI's Harness Engineering principles](https://openai.com/index/harness-engineering/). **Humans steer. Agents execute.**

---

## Quick Install

```bash
pi install git:github.com/user/humbleflow

# Then in your project:
python3 ~/.pi/agent/git/github.com/user/humbleflow/init-harness.py . --greenfield --name "MyApp"
```

---

## What You Get

| Component | What it does |
|-----------|-------------|
| **`humbleflow` skill** | Loaded automatically by agents for any SDLC work. Covers all 7 phases: specify → plan → implement → review → QA → merge → maintain. |
| **5 prompt templates** | `/implement`, `/review`, `/qa`, `/garbage-collect`, `/plan-feature` — one-shot workflows for common tasks. |
| **`init-harness.py`** | One-command project initialization. Greenfield or brownfield. Generates architecture docs, quality tables, and `AGENTS.md` customized to your project. |
| **7 enforcement tools** | Python linters for boundary validation, golden-principle checks, quality grading, doc gardening, plan validation — plus a `Makefile` that ties them together. |

---

## Quick Start

### Greenfield (new project)

```bash
init-harness.py ~/projects/myapp --greenfield --name "MyApp" --domains "auth,billing,users"
cd ~/projects/myapp
# Agents now auto-load the humbleflow skill. Just prompt:
#   "Add two-factor authentication to the login flow"
```

### Brownfield (existing codebase)

```bash
init-harness.py ~/projects/existing-app --brownfield
# Auto-discovers domains from src/domains/*, grades existing code, warns on overwrites
cd ~/projects/existing-app
make all   # Run linters and quality checks on existing code
```

### Interactive mode

```bash
init-harness.py ~/projects/myapp
# Prompts for project name, description, domains, and mode
```

---

## What's in the Box

```
humbleflow/
├── init-harness.py              ← Project initialization
├── AGENTS.md                    ← Agent entry point (TOC ~100 lines)
├── WORKFLOW.md                  ← Human-readable SDLC guide
├── Makefile                     ← make lint / make quality / make garden
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
├── docs/                        ← System of record (templates)
│   ├── architecture.md          ← Domain map + layered model
│   ├── quality.md               ← A→F grading per domain
│   └── principles.md            ← 7 golden principles with examples
│
├── plans/                       ← Execution plan infrastructure
│   ├── template.md              ← Full plan (multi-day, cross-domain)
│   └── template-lightweight.md  ← Lightweight plan (< 1 day)
│
└── tools/                       ← Mechanical enforcement
    ├── lint-boundaries.py       ← Dependency direction validator
    ├── lint-golden.py           ← Golden principle validator
    ├── quality-grade.py         ← Domain quality scanner
    ├── doc-gardener.py          ← Stale documentation finder
    ├── validate-plan.py         ← Plan structure validator
    ├── ci-config.yml            ← CI pipeline configuration
    └── Makefile                 ← One-command orchestrator
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
