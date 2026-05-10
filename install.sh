#!/usr/bin/env bash
set -euo pipefail

# humbleflow — one-shot installer
# Detects Pi and/or Claude Code and installs humbleflow for whichever are available.
# Falls back to CLI-only if neither agent platform is detected.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/tahopetis/humbleflow/master/install.sh | bash
#   ./install.sh                          # from a local clone

REPO_URL="https://github.com/tahopetis/humbleflow.git"
REPO_DIR="${HOME}/.humbleflow"

BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

say()  { echo -e "$@"; }
ok()   { say "  ${GREEN}✓${RESET} $1"; }
warn() { say "  ${YELLOW}⚠${RESET}  $1"; }
err()  { say "  ${RED}✗${RESET} $1"; }
info() { say "  ${CYAN}→${RESET} $1"; }

PI_AVAILABLE=false
CLAUDE_AVAILABLE=false

# ── Resolve the humbleflow source ────────────────────────────────────────────

say ""
say "${BOLD}humbleflow installer${RESET}"
say ""

# Are we running from inside a humbleflow clone?
if [ -f "./humbleflow" ] && [ -d "./skills" ]; then
    SCRIPT_DIR="$(pwd)"
    ok "Using local clone: ${SCRIPT_DIR}"
else
    # Running from curl pipe — clone the repo
    info "Cloning humbleflow..."
    if [ -d "${REPO_DIR}" ]; then
        info "Updating existing clone at ${REPO_DIR}..."
        (cd "${REPO_DIR}" && git pull --ff-only 2>/dev/null) || true
    else
        git clone --depth 1 "${REPO_URL}" "${REPO_DIR}" 2>/dev/null || {
            err "Failed to clone ${REPO_URL}"
            say "  Try manually: git clone ${REPO_URL} && cd humbleflow && ./install.sh"
            exit 1
        }
    fi
    SCRIPT_DIR="${REPO_DIR}"
    ok "Ready: ${SCRIPT_DIR}"
fi

# ── Detect platforms ─────────────────────────────────────────────────────────

# Pi detection
if command -v pi &>/dev/null; then
    PI_AVAILABLE=true
    ok "Pi detected ($(pi --version 2>/dev/null || echo 'unknown version'))"
else
    warn "Pi not found — skipping Pi install"
fi

# Claude Code detection
if command -v claude &>/dev/null; then
    CLAUDE_AVAILABLE=true
    ok "Claude Code detected ($(claude --version 2>/dev/null || echo 'unknown version'))"
else
    warn "Claude Code not found — skipping Claude Code install"
fi

# ── Pi install ───────────────────────────────────────────────────────────────

if $PI_AVAILABLE; then
    say ""
    say "${BOLD}── Pi ──${RESET}"

    if pi list 2>/dev/null | grep -q "humbleflow"; then
        ok "humbleflow already installed for Pi"
    else
        info "Installing for Pi..."
        if pi install "git:file://${SCRIPT_DIR}" 2>/dev/null; then
            ok "Installed via pi"
        else
            info "Trying GitHub fallback..."
            if pi install git:github.com/tahopetis/humbleflow 2>/dev/null; then
                ok "Installed via pi (from GitHub)"
            else
                warn "pi install failed, manual setup..."
                PI_SKILLS="${HOME}/.pi/agent/skills/humbleflow"
                PI_PROMPTS="${HOME}/.pi/agent/prompts"
                mkdir -p "${PI_SKILLS}" "${PI_PROMPTS}"
                cp -r "${SCRIPT_DIR}/skills/humbleflow/"* "${PI_SKILLS}/"
                cp "${SCRIPT_DIR}/prompts/"*.md "${PI_PROMPTS}/"
                ok "Skills → ${PI_SKILLS}"
                ok "Prompts → ${PI_PROMPTS}"
                warn "Restart Pi to load the skill"
            fi
        fi
    fi
fi

# ── Claude Code install ──────────────────────────────────────────────────────

if $CLAUDE_AVAILABLE; then
    say ""
    say "${BOLD}── Claude Code ──${RESET}"

    CC_PLUGIN="${HOME}/.claude/plugins/humbleflow"

    if [ -L "${CC_PLUGIN}" ] || [ -d "${CC_PLUGIN}" ]; then
        ok "humbleflow already linked for Claude Code"
    else
        mkdir -p "$(dirname "${CC_PLUGIN}")"
        ln -sfn "${SCRIPT_DIR}" "${CC_PLUGIN}"
        ok "Linked → ${CC_PLUGIN}"
        ok "Run /reload-plugins in Claude Code to activate"
    fi

    say ""
    say "  Or test directly:"
    say "    ${CYAN}claude --plugin-dir ${SCRIPT_DIR}${RESET}"
fi

# ── CLI install ──────────────────────────────────────────────────────────────

say ""
say "${BOLD}── CLI ──${RESET}"

if command -v humbleflow &>/dev/null; then
    ok "humbleflow CLI already on PATH"
else
    if command -v npm &>/dev/null; then
        info "npm linking..."
        (cd "${SCRIPT_DIR}" && npm link --silent 2>/dev/null) && {
            ok "CLI linked — 'humbleflow' is now on PATH"
        } || {
            warn "npm link failed. Run directly:"
            say "    ${CYAN}${SCRIPT_DIR}/humbleflow${RESET} init . --name \"MyApp\" --domains \"auth\""
        }
    else
        warn "npm not found. Run directly:"
        say "  ${CYAN}${SCRIPT_DIR}/humbleflow${RESET} init . --name \"MyApp\" --domains \"auth,billing\""
    fi
fi

# ── Summary ──────────────────────────────────────────────────────────────────

say ""
say "${BOLD}═══ Done ═══${RESET}"

if $PI_AVAILABLE; then
    say "  Pi:           ${GREEN}✓${RESET}  /humbleflow-init, /humbleflow-implement, ..."
else
    say "  Pi:           —   (pi install git:github.com/tahopetis/humbleflow)"
fi

if $CLAUDE_AVAILABLE; then
    say "  Claude Code:  ${GREEN}✓${RESET}  /humbleflow:init, /humbleflow:implement, ..."
else
    say "  Claude Code:  —   (claude --plugin-dir ${SCRIPT_DIR})"
fi

say "  CLI:          ${GREEN}✓${RESET}  humbleflow init"
say ""
say "Start building:"
say "  ${CYAN}humbleflow init . --name \"MyApp\" --domains \"auth,billing\"${RESET}"
say ""
