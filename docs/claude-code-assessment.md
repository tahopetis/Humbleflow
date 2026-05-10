# Claude Code Support Assessment

## Summary

Humbleflow is ~85% ready for Claude Code already. The core value — SDLC phases, golden principles, enforcement tools, templates — is entirely platform-agnostic. Adding Claude Code support requires ~11 new files, ~2 edits, and ~2–3 hours of work.

## Current Architecture

Humbleflow has four integration surfaces with Pi:

| Surface | Pi Mechanism | Files |
|---------|-------------|-------|
| **Skill** (SDLC phases) | `skills/` dir discovered via `.pi/settings.json` | `skills/humbleflow/SKILL.md` + 3 references |
| **Prompt templates** (6 `/`-workflows) | `prompts/` dir, invoked as `/humbleflow-init` etc. | 6 `.md` files in `prompts/` |
| **Init CLI** | `humbleflow init` copies Pi skill + prompts into project under `.pi/` | `humbleflow` Python script |
| **Project scaffold** | Templates copied into target dir with `.pi/skills/` and `.pi/prompts/` | `templates/AGENTS.md` references `.pi/` |

## What's Already Compatible (no changes needed)

| Component | Reason |
|-----------|--------|
| **CLI** (`humbleflow init`) | Language-agnostic Python script. Works on any platform. |
| **All templates** (AGENTS.md, WORKFLOW.md, SPEC.md, BACKLOG.md, docs/, plans/, tools/) | Platform-agnostic markdown and Python. |
| **All enforcement tools** (lint-boundaries.py, lint-golden.py, quality-grade.py, doc-gardener.py, validate-plan.py) | Pure Python, no platform coupling. |
| **Makefile** | Platform-agnostic. |
| **SKILL.md structure** | Claude Code uses `skills/<name>/SKILL.md` — identical directory convention. |

## Pi ↔ Claude Code Mechanism Mapping

| Pi feature | Claude Code equivalent |
|---|---|
| `.pi/settings.json` → skills & prompts paths | `.claude-plugin/plugin.json` manifest |
| `skills/humbleflow/SKILL.md` | `skills/humbleflow/SKILL.md` (same format, add Claude frontmatter) |
| `prompts/*.md` (slash commands) | `commands/*.md` or `skills/` |
| Pi `$ARGUMENTS` in prompts | Claude Code `$ARGUMENTS` in skills/commands |
| Pi package install: `pi install git:...` | Plugin marketplace or `--plugin-dir` |
| AGENTS.md template `.pi/` references | Change to `.claude/` references or agnostic |
| Subagent spawning in review | Claude Code built-in subagents + custom agents |

## Changes Needed (ranked by effort)

### 1. TRIVIAL: Add `.claude-plugin/plugin.json` manifest

Create a manifest that declares all components. This is the minimum gate for "being a Claude Code plugin."

**Effort**: 5 minutes. **File**: new `.claude-plugin/plugin.json`.

### 2. SMALL: Update SKILL.md frontmatter for Claude Code

Add `paths` and `when_to_use` fields for better auto-invocation in Claude Code.

**Effort**: 5 minutes. **File**: edit `skills/humbleflow/SKILL.md`.

### 3. SMALL: Convert 6 prompts → Claude Code commands

Place each prompt template as a flat `.md` file in `commands/`. The existing frontmatter already has `description` and `argument-hint` which Claude Code supports.

**Recommendation**: flat `commands/` for init/implement/qa/garbage-collect/plan-feature. The review workflow gets special treatment (see #4).

**Effort**: 20 minutes. **Files**: 6 new files in `commands/`.

### 4. MEDIUM: Convert review workflow to Claude Code subagents

Create 3 custom agents in `agents/` for adversarial review (correctness, tests, simplicity). This is the most valuable Claude Code-specific enhancement — the agents support `isolation: worktree` for true fresh-context execution.

**Effort**: 30-45 minutes. **Files**: 3 new agent `.md` files + 1 updated review command.

### 5. SMALL: Add post-merge hooks

Hooks that remind Claude to update SPEC.md and check BACKLOG.md after merges.

**Effort**: 10 minutes. **File**: new `hooks/hooks.json`.

### 6. MEDIUM: Update AGENTS.md template to be platform-agnostic

Remove Pi-specific `.pi/` directory from the repo map. Mention both Pi and Claude Code as supported platforms in a footnote.

**Effort**: 15 minutes. **File**: edit `templates/AGENTS.md`.

### 7. MEDIUM: Update `humbleflow init` for Claude Code

Add `--platform claude` flag that skips Pi-specific file copies and prints Claude Code install instructions.

**Effort**: 20 minutes. **File**: edit `humbleflow` CLI script.

## New File Map

```
humbleflow/                          (existing repo root)
├── .claude-plugin/                   ← NEW
│   └── plugin.json                   ← NEW: manifest
├── commands/                         ← NEW: prompt→command conversions
│   ├── humbleflow-init.md            ← from prompts/humbleflow-init.md
│   ├── humbleflow-implement.md       ← from prompts/humbleflow-implement.md
│   ├── humbleflow-review.md          ← from prompts/humbleflow-review.md
│   ├── humbleflow-qa.md              ← from prompts/humbleflow-qa.md
│   ├── humbleflow-garbage-collect.md ← from prompts/humbleflow-garbage-collect.md
│   └── humbleflow-plan-feature.md    ← from prompts/humbleflow-plan-feature.md
├── agents/                           ← NEW: Claude Code custom subagents
│   ├── humbleflow-review-correctness.md
│   ├── humbleflow-review-tests.md
│   └── humbleflow-review-simplicity.md
├── hooks/                            ← NEW
│   └── hooks.json                    ← Post-merge reminder hooks
├── skills/                           ← EXISTING (already compatible)
│   └── humbleflow/
│       ├── SKILL.md                  ← MINOR EDIT: Claude frontmatter additions
│       └── references/
│           ├── phases.md
│           ├── architecture.md
│           └── golden-principles.md
├── prompts/                          ← EXISTING (still used by Pi, can eventually be deprecated)
├── templates/                        ← EXISTING (AGENTS.md needs edit)
├── humbleflow                        ← EXISTING (CLI, minor edit)
├── package.json                      ← EXISTING (no change needed, Pi still uses this)
└── .pi/settings.json                 ← EXISTING (no change needed)
```

## Installation UX Comparison

| | Pi | Claude Code |
|---|---|---|
| **Install** | `pi install git:github.com/tahopetis/humbleflow` | `/plugin install humbleflow@<marketplace>` or `claude --plugin-dir ./humbleflow` |
| **Init project** | `/humbleflow-init` (guided) or `humbleflow init` (CLI) | Same CLI: `humbleflow init` |
| **Implement** | `/humbleflow-implement "build auth"` | `/humbleflow:implement "build auth"` |
| **Review** | `/humbleflow-review` (Pi subagents) | `/humbleflow:review` (Claude Code subagents) |
| **QA** | `/humbleflow-qa` | `/humbleflow:qa` |
| **GC** | `/humbleflow-garbage-collect` | `/humbleflow:garbage-collect` |
| **Plan** | `/humbleflow-plan-feature` | `/humbleflow:plan-feature` |
| **Skill auto-load** | Via Pi skill system | Via Claude Code skill auto-discovery |

## Risk & Compatibility

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Pi and Claude Code files coexist in same repo | Confusion about which to use | Both work; Claude Code ignores `.pi/`, Pi ignores `.claude-plugin/` |
| Duplicate prompt vs command content | Drift between `prompts/` and `commands/` | Keep one canonical copy per workflow. Consider symlinks or single source in future |
| AGENTS.md template references wrong platform | Agent confusion | Make it agnostic |
| Review subagent model differences | Pi uses OpenAI, Claude uses Anthropic models | Both support Sonnet-class reasoning; review quality comparable |
| `$ARGUMENTS` syntax | Both Pi and Claude Code support it | No change needed |
| Hooks differ between platforms | Pi doesn't have hooks, Claude Code does | Hooks are additive, no conflict |

## Recommended Implementation Order

1. Add `.claude-plugin/plugin.json` — entry point, makes it a valid plugin
2. Update `SKILL.md` frontmatter — add `paths`, `when_to_use` for better auto-invocation
3. Create `commands/` with 6 workflow conversions — core UX
4. Create `agents/` with 3 review subagents — differentiates from Pi
5. Update `templates/AGENTS.md` — platform-agnostic repo map
6. Add `hooks/hooks.json` — post-merge reminders (nice-to-have)
7. Update `humbleflow init` — add `--platform claude` flag (nice-to-have)

## Conclusion

Humbleflow's architecture is already well-suited for multi-platform support. The core SDLC workflow is platform-agnostic by design. Adding Claude Code support is primarily mechanical: a manifest, command conversions, and agent definitions — with the review subagent system being the single most valuable Claude Code-specific enhancement.
