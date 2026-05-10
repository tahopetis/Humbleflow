#!/usr/bin/env bash
set -euo pipefail

# humbleflow — one-shot installer
# Detects Pi and/or Claude Code and installs humbleflow for whichever are available.
# Falls back to CLI-only if neither agent platform is detected.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/tahopetis/Humbleflow/master/install.sh | bash
#   ./install.sh                          # from a local clone

REPO_URL="https://github.com/tahopetis/Humbleflow.git"
INSTALL_DIR="${HOME}/.humbleflow"

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

if [ -f "./humbleflow" ] && [ -d "./skills" ]; then
    SCRIPT_DIR="$(pwd)"
    ok "Using local clone: ${SCRIPT_DIR}"
else
    if [ -d "${INSTALL_DIR}" ]; then
        info "Updating ${INSTALL_DIR}..."
        (cd "${INSTALL_DIR}" && git pull --ff-only 2>/dev/null) || true
    else
        info "Cloning to ${INSTALL_DIR}..."
        git clone --depth 1 "${REPO_URL}" "${INSTALL_DIR}" 2>/dev/null || {
            err "Failed to clone ${REPO_URL}"
            say "  Try: git clone ${REPO_URL} && cd Humbleflow && ./install.sh"
            exit 1
        }
    fi
    SCRIPT_DIR="${INSTALL_DIR}"
    ok "Ready: ${SCRIPT_DIR}"
fi

# ── Detect platforms ─────────────────────────────────────────────────────────

if command -v pi &>/dev/null; then
    PI_AVAILABLE=true
    ok "Pi detected"
else
    warn "Pi not found — skipping"
fi

if command -v claude &>/dev/null; then
    CLAUDE_AVAILABLE=true
    ok "Claude Code detected"
else
    warn "Claude Code not found — skipping"
fi

# ── Pi install ───────────────────────────────────────────────────────────────

if $PI_AVAILABLE; then
    say ""
    say "${BOLD}── Pi ──${RESET}"

    if pi list 2>/dev/null | grep -q "humbleflow"; then
        ok "Already installed for Pi"
    else
        info "Installing..."
        if pi install "git:file://${SCRIPT_DIR}" 2>/dev/null; then
            ok "Installed"
        elif pi install git:github.com/tahopetis/Humbleflow 2>/dev/null; then
            ok "Installed (from GitHub)"
        else
            warn "pi install failed, manual setup..."
            PI_SKILLS="${HOME}/.pi/agent/skills/humbleflow"
            PI_PROMPTS="${HOME}/.pi/agent/prompts"
            mkdir -p "${PI_SKILLS}" "${PI_PROMPTS}"
            cp -r "${SCRIPT_DIR}/skills/humbleflow/"* "${PI_SKILLS}/"
            cp "${SCRIPT_DIR}/prompts/"*.md "${PI_PROMPTS}/"
            ok "Skills → ${PI_SKILLS}"
            ok "Prompts → ${PI_PROMPTS}"
        fi
    fi
fi

# ── Claude Code install ──────────────────────────────────────────────────────

if $CLAUDE_AVAILABLE; then
    say ""
    say "${BOLD}── Claude Code ──${RESET}"

    # Claude Code loads plugins via --plugin-dir (session) or marketplace.
    # The repo at SCRIPT_DIR is the plugin. Add a shell alias for convenience.
    CC_ALIAS_FILE="${HOME}/.claude/.humbleflow-alias"
    ALIAS_LINE="alias claude='claude --plugin-dir ${SCRIPT_DIR}'"

    if [ -f "${CC_ALIAS_FILE}" ]; then
        ok "Plugin dir already configured"
    else
        mkdir -p "${HOME}/.claude"
        echo "${ALIAS_LINE}" > "${CC_ALIAS_FILE}"
        ok "Wrote alias → ${CC_ALIAS_FILE}"
    fi

    say ""
    say "  Add this to your shell rc file (~/.bashrc, ~/.zshrc):"
    say "    ${CYAN}source ~/.claude/.humbleflow-alias${RESET}"
    say ""
    say "  Or start Claude Code with the flag directly:"
    say "    ${CYAN}claude --plugin-dir ${SCRIPT_DIR}${RESET}"
fi

# ── CLI install ──────────────────────────────────────────────────────────────

say ""
say "${BOLD}── CLI ──${RESET}"

if command -v humbleflow &>/dev/null; then
    ok "CLI already on PATH"
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
        say "  ${CYAN}${SCRIPT_DIR}/humbleflow${RESET} init . --name \"MyApp\" --domains \"auth\""
    fi
fi

# ── Summary ──────────────────────────────────────────────────────────────────

say ""
say "${BOLD}═══ Done ═══${RESET}"

if $PI_AVAILABLE; then
    say "  Pi:           ${GREEN}✓${RESET}  /humbleflow-init, /humbleflow-implement, ..."
fi
if $CLAUDE_AVAILABLE; then
    say "  Claude Code:  ${GREEN}✓${RESET}  source ~/.claude/.humbleflow-alias"
    say "                then: /humbleflow:init, /humbleflow:implement, ..."
else
    say "  Claude Code:  —   (claude --plugin-dir ${SCRIPT_DIR})"
fi
say "  CLI:          ${GREEN}✓${RESET}  humbleflow init"
say ""
say "Start building:"
say "  ${CYAN}humbleflow init . --name \"MyApp\" --domains \"auth,billing\"${RESET}"
say ""
