# humbleflow · [![pi-package](https://img.shields.io/badge/pi-package-blue)](https://pi.dev/packages) [![claude-code-plugin](https://img.shields.io/badge/claude--code-plugin-green)](https://code.claude.com/docs/en/plugins)

A multi-platform, agent-first SDLC — based on [OpenAI's Harness Engineering principles](https://openai.com/index/harness-engineering/). **Humans steer. Agents execute.** Supports Pi and Claude Code.

---

## Install

### One command (auto-detect)
```bash
curl -fsSL https://raw.githubusercontent.com/tahopetis/Humbleflow/master/install.sh | bash
```
Detects Pi and/or Claude Code and installs for whichever are available.
For Claude Code, restart after install. Commands appear as `/humbleflow-init`, `/humbleflow-implement`, etc.Falls back to CLI-only if neither is found.

### From npm (if published)
```bash
npx humbleflow install
```

### Install from local clone
```bash
./install.sh
# or:
python3 humbleflow install
```

**Pi**
```bash
pi install git:github.com/tahopetis/humbleflow
```

**Claude Code**
```bash
# After running install.sh, restart Claude Code.
# Commands appear as:
#   /humbleflow-init, /humbleflow-implement, /humbleflow-review,
#   /humbleflow-qa, /humbleflow-garbage-collect, /humbleflow-plan-feature

# Or use plugin mode (namespaced as /humbleflow:*):
claude --plugin-dir ~/.humbleflow
```

**CLI only**
```bash
npm install -g humbleflow
```

---

## What You Get

| Component | What it does |
|-----------|-------------|
| **`humbleflow` skill** | Loaded automatically by agents for any SDLC work. Covers all 7 phases: specify → plan → implement → review → QA → merge → maintain. |
| **6 workflows** | Init, implement, review, QA, garbage-collect, plan-feature — one-shot workflows for common tasks. Works in Pi (`/humbleflow-*`) and Claude Code (`/humbleflow:*`). |
| **`humbleflow` CLI** | One-command project initialization (`humbleflow init`). Greenfield or brownfield. Generates SPEC.md, BACKLOG.md, architecture docs, quality tables, and `AGENTS.md` customized to your project. |
| **7 enforcement tools** | Python linters for boundary validation, golden-principle checks, quality grading, doc gardening, plan validation — plus a `Makefile` that ties them together. |
| **SPEC.md + BACKLOG.md** | Project vision + prioritized backlog. Agents auto-update SPEC.md on merge and check BACKLOG.md for next work. |

---

## Quick Start

### Guided discovery (agent-driven — recommended)

```bash
mkdir myapp && cd myapp
# Pi:
pi
# Type: /humbleflow-init

# Claude Code:
claude
# Type: /humbleflow:init
```

The agent asks 6 questions one at a time:
project name, problem, users, MVP anchor, domains, constraints.
Then generates `SPEC.md` + `BACKLOG.md` and scaffolds everything.
You're immediately ready to build:

```
# Pi:          /humbleflow-implement "Build the MVP"
# Claude Code: /humbleflow:implement "Build the MVP"
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
├── skills/humbleflow/         ← SDLC skill (auto-loaded by agents)
│   ├── SKILL.md
│   └── references/
│       ├── phases.md            ← Phase-by-phase agent instructions
│       ├── architecture.md      ← Layered architecture rules
│       └── golden-principles.md ← Taste invariants
│
├── commands/                   ← Claude Code workflows
│   ├── init.md                  ← /humbleflow:init: guided discovery
│   ├── implement.md             ← /humbleflow:implement: full implementation
│   ├── review.md                ← /humbleflow:review: adversarial review
│   ├── qa.md                    ← /humbleflow:qa: bug repro → fix
│   ├── garbage-collect.md       ← /humbleflow:garbage-collect: drift scan
│   └── plan-feature.md          ← /humbleflow:plan-feature: spec → plan
│
├── agents/                     ← Claude Code review subagents
│   ├── humbleflow-review-correctness.md
│   ├── humbleflow-review-tests.md
│   └── humbleflow-review-simplicity.md
│
├── hooks/                      ← Claude Code hooks (post-merge reminders)
│   └── hooks.json
│
├── .claude-plugin/             ← Claude Code plugin manifest
│   └── plugin.json
│
├── prompts/                     ← Pi prompt templates
│   ├── humbleflow-init.md       ← /humbleflow-init: guided discovery
│   ├── implement.md             ← /humbleflow-implement: full implementation flow
│   ├── review.md                ← /humbleflow-review: parallel adversarial review
│   ├── qa.md                    ← /humbleflow-qa: bug repro → fix → validate
│   ├── garbage-collect.md       ← /humbleflow-garbage-collect: drift scan → refactor
│   └── plan-feature.md          ← /humbleflow-plan-feature: spec → execution plan
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
| **Entropy control** | `/humbleflow-garbage-collect` + `doc-gardener.py` scan for drift, open refactoring PRs, update quality grades. |

### The full loop

```
Init  →  discover (6 questions) → SPEC.md + BACKLOG.md + scaffold
Implement  →  build → merge
          →  auto-update SPEC.md (capabilities)
          →  auto-check BACKLOG.md (report next item)
Garbage-collect  →  scan drift → refactor → update quality grades

Repeat: implement → merge → check backlog → next
```

[Read the full article →](https://openai.com/index/harness-engineering/)

---

## Requirements

- **Python 3.9+** (for enforcement tools and init script)
- **Pi** or **Claude Code** (for skill and workflow loading)
- That's it. No npm dependencies, no external services.

---

## License

MIT
