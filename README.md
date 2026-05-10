# humbleflow · [![pi-package](https://img.shields.io/badge/pi-package-blue)](https://pi.dev/packages)

A Pi package for agent-first SDLC — based on [OpenAI's Harness Engineering principles](https://openai.com/index/harness-engineering/). **Humans steer. Agents execute.**

---

## Install

```bash
pi install git:github.com/tahopetis/humbleflow
```

This gives you everything: the `humbleflow` skill (auto-loaded by agents), all 6 prompt templates (`/humbleflow-init`, `/implement`, `/review`, `/qa`, `/garbage-collect`, `/plan-feature`), and the `humbleflow` CLI.

> **CLI-only alternative:** If you don't use Pi, `npm install -g humbleflow` gives you just the CLI on PATH. No skills or prompts.

---

## What You Get

| Component | What it does |
|-----------|-------------|
| **`humbleflow` skill** | Loaded automatically by agents for any SDLC work. Covers all 7 phases: specify → plan → implement → review → QA → merge → maintain. |
| **6 prompt templates** | `/humbleflow-init`, `/implement`, `/review`, `/qa`, `/garbage-collect`, `/plan-feature` — one-shot workflows for common tasks. |
| **`humbleflow` CLI** | One-command project initialization (`humbleflow init`). Greenfield or brownfield. Generates SPEC.md, BACKLOG.md, architecture docs, quality tables, and `AGENTS.md` customized to your project. |
| **7 enforcement tools** | Python linters for boundary validation, golden-principle checks, quality grading, doc gardening, plan validation — plus a `Makefile` that ties them together. |
| **SPEC.md + BACKLOG.md** | Project vision + prioritized backlog. Agents auto-update SPEC.md on merge and check BACKLOG.md for next work. |

---

## Quick Start

### Guided discovery (inside Pi — recommended)

```bash
mkdir myapp && cd myapp && pi
```

Type `/humbleflow-init`. The agent asks 6 questions one at a time:
project name, problem, users, MVP anchor, domains, constraints.
Then generates `SPEC.md` + `BACKLOG.md` and scaffolds everything.
You're immediately ready to build:

```
/implement "Build the MVP"
```

### CLI (terminal, CI, scripting)

```bash
humbleflow init . --greenfield --name "MyApp" --domains "auth,billing"
```

Copies all harness files + SPEC.md and BACKLOG.md templates.
Fill in `SPEC.md` or prompt the agent to do it.

See the full CLI reference: `humbleflow help`

---

## What's in the Box

```
humbleflow/
├── humbleflow                   ← CLI: humbleflow init / humbleflow version
├── SPEC.md                      ← Generated during init: vision, users, MVP, constraints
├── BACKLOG.md                   ← Generated during init: Now → Next → Later → Done
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
│   ├── humbleflow-init.md       ← /humbleflow-init: guided discovery
│   ├── implement.md             ← /implement: full implementation flow
│   ├── review.md                ← /review: parallel adversarial review
│   ├── qa.md                    ← /qa: bug repro → fix → validate
│   ├── garbage-collect.md       ← /garbage-collect: drift scan → refactor
│   └── plan-feature.md          ← /plan-feature: spec → execution plan
│
└── templates/                   ← Project scaffolding (copied by humbleflow init)
    ├── AGENTS.md, WORKFLOW.md, Makefile
    ├── BACKLOG.md               ← Now → Next → Later → Done
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

### The full loop

```
/humbleflow-init  →  discover (6 questions) → SPEC.md + BACKLOG.md + scaffold
/implement        →  build → merge
                  →  auto-update SPEC.md (capabilities)
                  →  auto-check BACKLOG.md (report next item)
/garbage-collect  →  scan drift → refactor → update quality grades

Repeat: /implement → merge → check backlog → next
```

[Read the full article →](https://openai.com/index/harness-engineering/)

---

## Requirements

- **Python 3.9+** (for enforcement tools and init script)
- **Pi** (for skill and prompt template loading)
- That's it. No npm dependencies, no external services.

---

## License

MIT
