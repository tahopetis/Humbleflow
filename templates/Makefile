# Humbleflow — Mechanical Enforcement
# Entry point for all lint, quality, and maintenance tools.
#
# Usage:
#   make lint          Run all linters (boundaries + golden principles)
#   make quality       Scan and update quality grades
#   make garden        Find stale documentation
#   make validate      Validate execution plan structure
#   make all           Run everything

PYTHON := python3
TOOLS_DIR := tools
PLANS_DIR := plans

.PHONY: all lint lint-boundaries lint-golden quality garden validate clean help

all: lint quality garden validate
	@echo ""
	@echo "All checks complete."

# ── Linting ─────────────────────────────────────────────────────────────────

lint: lint-boundaries lint-golden

lint-boundaries:
	@echo "=== Boundary Lint ==="
	@$(PYTHON) $(TOOLS_DIR)/lint-boundaries.py
	@echo ""

lint-golden:
	@echo "=== Golden Principle Lint ==="
	@$(PYTHON) $(TOOLS_DIR)/lint-golden.py
	@echo ""

# ── Quality ─────────────────────────────────────────────────────────────────

quality:
	@echo "=== Quality Grade Update ==="
	@$(PYTHON) $(TOOLS_DIR)/quality-grade.py
	@echo ""

# ── Documentation ───────────────────────────────────────────────────────────

garden:
	@echo "=== Doc Gardening ==="
	@$(PYTHON) $(TOOLS_DIR)/doc-gardener.py
	@echo ""

# ── Plan Validation ─────────────────────────────────────────────────────────

validate:
	@echo "=== Plan Validation ==="
	@$(PYTHON) $(TOOLS_DIR)/validate-plan.py
	@echo ""

# ── Utility ─────────────────────────────────────────────────────────────────

clean:
	@echo "Cleaning up..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Done."

help:
	@echo "Humbleflow — Mechanical Enforcement Tools"
	@echo ""
	@echo "  make lint             Run all linters"
	@echo "  make lint-boundaries   Validate dependency directions"
	@echo "  make lint-golden       Validate golden principles"
	@echo "  make quality           Update quality grades"
	@echo "  make garden            Find stale documentation"
	@echo "  make validate          Validate execution plans"
	@echo "  make all               Run everything"
	@echo "  make clean             Remove Python cache files"
	@echo "  make help              Show this help"
