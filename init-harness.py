#!/usr/bin/env python3
"""
init-harness.py — Initialize the Humbleflow workflow into any project.

USAGE:
  python3 init-harness.py <target-dir> [options]

OPTIONS:
  --greenfield         Initialize for a new/empty project
  --brownfield         Initialize into an existing codebase
  --name NAME          Project name (required for greenfield)
  --description DESC   Short project description
  --domains DOMAINS    Comma-separated domain names (e.g., "auth,billing,users")
  --force              Overwrite existing harness files
  --dry-run            Show what would be done without doing it
  --harness-path DIR   Path to harness package root (default: script's directory)
  --templates-path DIR Path to templates directory (default: harness-path/templates)
  --non-interactive    Disable interactive prompts (useful for CI)

EXAMPLES:
  python3 init-harness.py ~/projects/myapp --greenfield --name "MyApp" --domains "auth,billing"
  python3 init-harness.py ~/projects/existing-app --brownfield
  python3 init-harness.py ~/projects/myapp --name "MyApp" --domains "auth" --dry-run
  python3 init-harness.py ~/projects/myapp --greenfield --name "MyApp" --domains "core" --non-interactive
"""

import argparse
import os
import re
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ── Constants ────────────────────────────────────────────────────────────────

# Relative paths within templates/ — these are the files that get copied
# to the target project. Source files live under harness_path/templates/.
HARNESS_FILES = [
    "AGENTS.md",
    "WORKFLOW.md",
    "Makefile",
    "docs/architecture.md",
    "docs/quality.md",
    "docs/principles.md",
    "plans/README.md",
    "plans/template.md",
    "plans/template-lightweight.md",
    "tools/ci-config.yml",
    "tools/doc-gardener.py",
    "tools/lint-boundaries.py",
    "tools/lint-golden.py",
    "tools/quality-grade.py",
    "tools/validate-plan.py",
    ".pi/skills/humbleflow/SKILL.md",
    ".pi/skills/humbleflow/references/phases.md",
    ".pi/skills/humbleflow/references/architecture.md",
    ".pi/skills/humbleflow/references/golden-principles.md",
    ".pi/prompts/review.md",
    ".pi/prompts/implement.md",
    ".pi/prompts/qa.md",
    ".pi/prompts/garbage-collect.md",
    ".pi/prompts/plan-feature.md",
]

TEMPLATED_FILES = {
    "AGENTS.md",
    "WORKFLOW.md",
    "docs/architecture.md",
    "docs/quality.md",
}

STANDARD_LAYERS = ["types", "config", "repo", "service", "runtime", "ui"]
NON_DOMAIN_ENTITIES = ["shared", "app", "providers"]

BROWN = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ── Utilities ────────────────────────────────────────────────────────────────

def color(text: str, c: str) -> str:
    if sys.stdout.isatty():
        return f"{c}{text}{RESET}"
    return text


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower().strip())
    return slug.strip("-")


def pascal_case(name: str) -> str:
    words = re.split(r"[-_\s]+", name.strip())
    return "".join(w.capitalize() for w in words if w)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def next_week(today_val: date) -> str:
    return (today_val + timedelta(days=7)).isoformat()


# ── Generated content ────────────────────────────────────────────────────────

DOMAIN_SECTION = """### {num}. {display_name} (`{slug}/`)

**Responsibility:** [Define what this domain owns and why it exists.]

**Key types:**
- `{type_prefix}` (primary entity)
- Placeholder for additional types

**Dependencies:**
- [List domains this domain reads from, or "None" if independent.]

"""


def generate_domain_architecture(domains: List[str]) -> str:
    if not domains:
        return "_No business domains defined yet._\n"
    sections = []
    for i, d in enumerate(domains, start=1):
        sections.append(DOMAIN_SECTION.format(
            num=i, display_name=pascal_case(d), slug=slugify(d),
            type_prefix=pascal_case(d),
        ))
    return "\n".join(sections)


def generate_repo_map(slug: str) -> str:
    return f"""```
{slug}/
├── AGENTS.md              ← You are here. Start every task by reading this.
├── WORKFLOW.md            ← Human-readable SDLC specification.
│
├── docs/                  ← System of record. Knowledge base.
│   ├── architecture.md    ← Domain map, layered architecture, dependency rules.
│   ├── quality.md         ← Quality grades per domain, tracked over time.
│   └── principles.md      ← Golden principles with rationale.
│
├── plans/                 ← Execution plans. First-class, versioned artifacts.
│   ├── README.md          ← Plan conventions and lifecycle.
│   ├── template.md        ← Full execution plan template.
│   └── template-lightweight.md ← Lightweight plan for small changes.
│
├── tools/                 ← Mechanical enforcement. Run these; don't skip them.
│   ├── Makefile           ← Entry point: `make lint`, `make quality`, `make garden`.
│   ├── lint-boundaries.py ← Validates dependency directions per architecture.
│   ├── lint-golden.py     ← Validates golden principles.
│   ├── quality-grade.py   ← Scans and updates quality grades.
│   ├── doc-gardener.py    ← Finds stale docs, opens fix-up reports.
│   └── validate-plan.py   ← Validates execution plan structure.
│
└── .pi/                   ← Pi agent configuration.
    ├── skills/
    │   └── humbleflow/  ← The SDLC workflow skill. Load when doing SDLC work.
    │       ├── SKILL.md
    │       └── references/
    └── prompts/           ← Prompt templates for common workflows.
```"""


def generate_project_decisions(domains: List[str]) -> str:
    if not domains:
        return ("## Design Decisions\n\n"
                "_No domain-specific decisions yet. "
                "Add decisions as the architecture evolves._\n")
    num = len(domains)
    examples = " and ".join(pascal_case(d) for d in domains[:2])
    return f"""## Design Decisions

### Why {num} domains?

Each domain maps to a distinct business capability with its own lifecycle.
{examples} are separated because they have independent lifecycles and
concerns. This separation prevents any single domain from growing into a monolith.

### Why ULID not UUID for IDs?

ULIDs are sortable by creation time (no separate `created_at` index needed),
URL-safe (no base64 encoding for REST endpoints), and have the same collision
resistance as UUIDv4. This matters when agents query logs and traces — sortable
IDs make everything easier to correlate.

### Why dependency inversion for cross-domain calls?

Without DI, domain A importing domain B's Service creates a compile-time
dependency that makes both domains harder to test, refactor, and eventually
extract. With DI, the domains are loosely coupled through types, and the
application root handles wiring. This is the architecture that the Harness
article describes as "allowing speed without decay."

### Why "boring" shared utilities?

`shared/` utilities are the foundation that everything else builds on. They
must be correct, tested, and instrumented. A bug in a shared utility affects
every domain. Preferring in-house implementations over third-party packages for
simple functionality gives us control over instrumentation and behavior.
"""


# ── Quality grade generation ─────────────────────────────────────────────────

Q_TABLE_HEADER = ("| Domain | Layer | Grade | BV | GP | TC | SD | Issues | "
                   "Last Updated |\n"
                   "|--------|-------|-------|----|----|----|----|--------|"
                   "--------------|\n")

Q_ROW = "| {domain} | {layer} | A | 0 | 0 | 0 | 0 | 0 | {today} |\n"

Q_SUMMARY = """| Metric | Value |
|--------|-------|
| Total domains tracked | {total} |
| Total layers tracked (active) | {layers} |
| Overall grade | A |
| Domains at A | {total} |
| Domains at B | 0 |
| Domains at C | 0 |
| Domains at D | 0 |
| Domains at F | 0 |
| Total BV (boundary violations) | 0 |
| Total GP (golden principle violations) | 0 |
| Total TC (test coverage gaps) | 0 |
| Total SD (stale docs) | 0 |
| Total issues | 0 |
| Trend | — (baseline) |
| Last full scan | {today} |
| Next scheduled scan | {next_scan} |
"""

Q_YAML_ENTRY = """  {slug}:
    types: {{ grade: A, BV: 0, GP: 0, TC: 0, SD: 0, updated: "{today}" }}
    config: {{ grade: A, BV: 0, GP: 0, TC: 0, SD: 0, updated: "{today}" }}
    repo: {{ grade: A, BV: 0, GP: 0, TC: 0, SD: 0, updated: "{today}" }}
    service: {{ grade: A, BV: 0, GP: 0, TC: 0, SD: 0, updated: "{today}" }}
    runtime: {{ grade: A, BV: 0, GP: 0, TC: 0, SD: 0, updated: "{today}" }}
    ui: {{ grade: A, BV: 0, GP: 0, TC: 0, SD: 0, updated: "{today}" }}
"""


def generate_quality_content(domains: List[str], project_slug: str
                             ) -> Tuple[str, str, str]:
    today_str = date.today().isoformat()
    scan_next = next_week(date.today())
    all_entities = NON_DOMAIN_ENTITIES + [slugify(d) for d in domains]

    tables = []
    for entity in all_entities:
        rows = [Q_ROW.format(domain=entity, layer=layer, today=today_str)
                for layer in STANDARD_LAYERS]
        tables.append(f"### {entity}\n\n{Q_TABLE_HEADER}{''.join(rows)}\n")
    domain_rows = "".join(tables)

    total = len(all_entities)
    layers = total * len(STANDARD_LAYERS)
    summary = Q_SUMMARY.format(total=total, layers=layers,
                                today=today_str, next_scan=scan_next)

    yaml_entries = "\n".join(
        Q_YAML_ENTRY.format(slug=entity, today=today_str)
        for entity in all_entities
    )
    yaml_block = f"""```yaml
# {project_slug} quality grades — canonical data
# Updated by: tools/quality-grade.py
# Schema version: 1
scan:
  last_full: "{today_str}"
  next_scheduled: "{scan_next}"
  overall_grade: A
  trend: "—"
  total_issues: 0

rubric:
  A: {{ label: Excellent, max_issues: 0 }}
  B: {{ label: Good, max_issues: 2 }}
  C: {{ label: Acceptable, max_issues: 5 }}
  D: {{ label: Poor, max_issues: 10 }}
  F: {{ label: Critical, max_issues: 999 }}

issue_categories:
  BV: {{ label: "Boundary Violation", tool: "lint-boundaries.py" }}
  GP: {{ label: "Golden Principle Violation", tool: "lint-golden.py" }}
  TC: {{ label: "Test Coverage Gap", tool: "quality-grade.py" }}
  SD: {{ label: "Stale Documentation", tool: "doc-gardener.py" }}

domains:
{yaml_entries}
```
"""
    return domain_rows, summary, yaml_block


# ── Document transformers ────────────────────────────────────────────────────

def transform_agents(content: str, name: str, slug: str) -> str:
    c = content.replace("{{PROJECT_NAME}}", name)
    c = c.replace("{{REPO_MAP}}", generate_repo_map(slug))
    c = c.replace("humbleflow", slug)
    return c


def transform_workflow(content: str, name: str, slug: str) -> str:
    c = content.replace("Humbleflow", name)
    c = c.replace("humbleflow", slug)
    return c


def transform_architecture(content: str, name: str, desc: str,
                           domains: List[str]) -> str:
    status = ("Skeleton — this document defines the target architecture. "
              "Domains are scaffolded but not yet implemented.")
    arch = generate_domain_architecture(domains)
    decisions = generate_project_decisions(domains)

    c = content.replace("{{PROJECT_NAME}}", name)
    c = c.replace("{{PROJECT_DESCRIPTION}}", desc)
    c = c.replace("{{PROJECT_STATUS}}", status)
    c = c.replace("{{DOMAIN_ARCHITECTURE}}", arch)
    c = c.replace("{{PROJECT_DECISIONS}}", decisions)
    return c


def transform_quality(content: str, name: str, slug: str,
                      domains: List[str]) -> str:
    today_str = date.today().isoformat()
    domain_rows, summary, yaml_block = generate_quality_content(domains, slug)

    c = content.replace("humbleflow quality grades", f"{slug} quality grades")
    c = c.replace("{{DOMAIN_QUALITY_ROWS}}", domain_rows)
    c = c.replace("{{QUALITY_SUMMARY}}", summary)
    c = c.replace("{{QUALITY_YAML}}", yaml_block)
    c = re.sub(r"Last full scan: \d{4}-\d{2}-\d{2}",
               f"Last full scan: {today_str}", c)
    c = re.sub(r'last_full: "\d{4}-\d{2}-\d{2}"',
               f'last_full: "{today_str}"', c)
    c = re.sub(r'next_scheduled: "\d{4}-\d{2}-\d{2}"',
               f'next_scheduled: "{next_week(date.today())}"', c)
    return c


# ── Brownfield detection ─────────────────────────────────────────────────────

def detect_source_structure(target: Path) -> Optional[Dict]:
    source_dirs = []
    for candidate in ["src", "app", "lib", "packages", "services"]:
        p = target / candidate
        if p.is_dir():
            source_dirs.append(candidate)

    if not source_dirs:
        skip = {".git", "node_modules", "__pycache__", ".venv",
                "venv", "dist", "build"}
        for entry in target.iterdir():
            if entry.name not in skip and not entry.name.startswith("."):
                return {"source_dirs": [], "is_empty": False,
                        "has_code": True, "domains": []}
        return None

    domains = []
    domains_path = target / "src" / "domains"
    if domains_path.is_dir():
        domains = [d.name for d in domains_path.iterdir()
                   if d.is_dir() and not d.name.startswith("_")]

    return {"source_dirs": source_dirs, "domains": domains,
            "is_empty": False, "has_code": True}


# ── Main harness initializer ─────────────────────────────────────────────────

class HarnessInit:
    def __init__(self, target: Path, harness_path: Path, templates_path: Path,
                 name: str,
                 description: str, domains: List[str], mode: str,
                 force: bool = False, dry_run: bool = False,
                 interactive: bool = True):
        self.target = target.resolve()
        self.harness_path = harness_path.resolve()
        self.templates_path = templates_path.resolve()
        self.name = name
        self.description = description
        self.domains = domains
        self.mode = mode
        self.force = force
        self.dry_run = dry_run
        self.interactive = interactive
        self.slug = slugify(name) if name else ""
        self.created: List[str] = []
        self.skipped: List[str] = []
        self.overwritten: List[str] = []

    def prompt(self, question: str, default: str = "") -> str:
        if not self.interactive:
            return default
        q = f"{question} [{default}]: " if default else f"{question}: "
        try:
            return input(q).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)

    def interactive_setup(self) -> None:
        if not self.interactive:
            return
        print(f"\n{BOLD}Humbleflow — Project Initialization{RESET}\n")

        if self.mode == "auto":
            is_empty = detect_source_structure(self.target) is None
            if is_empty:
                print(color("Detected: empty directory → greenfield mode", CYAN))
                self.mode = "greenfield"
            else:
                print(color("Detected: existing code → brownfield mode", CYAN))
                self.mode = "brownfield"

        if not self.name:
            default = self.target.name
            self.name = self.prompt("Project name", default)
        self.slug = slugify(self.name)

        if not self.description:
            default = f"A {self.name} application."
            self.description = self.prompt("Short description", default)

        if not self.domains:
            if self.mode == "brownfield":
                info = detect_source_structure(self.target)
                if info and info.get("domains"):
                    discovered = ", ".join(info["domains"])
                    print(color(f"Discovered domains: {discovered}", CYAN))
                    if self.prompt("Use these domains?", "y").lower().startswith("y"):
                        self.domains = info["domains"]
            if not self.domains:
                raw = self.prompt(
                    "Business domains (comma-separated, e.g., auth,billing,users)",
                    "")
                if raw.strip():
                    self.domains = [d.strip() for d in raw.split(",") if d.strip()]
                else:
                    self.domains = []

    def validate(self) -> bool:
        if not self.target.exists():
            print(color(f"Error: Target dir does not exist: {self.target}", RED),
                  file=sys.stderr)
            return False
        if not self.target.is_dir():
            print(color(f"Error: Target is not a directory: {self.target}", RED),
                  file=sys.stderr)
            return False
        if not self.harness_path.exists():
            print(color(f"Error: Harness path not found: {self.harness_path}", RED),
                  file=sys.stderr)
            return False
        if not self.templates_path.exists():
            print(color(
                f"Error: Templates dir not found: {self.templates_path}", RED),
                  file=sys.stderr)
            return False
        if not (self.templates_path / "AGENTS.md").exists():
            print(color(
                f"Error: {self.templates_path} does not contain AGENTS.md", RED),
                  file=sys.stderr)
            return False
        return True

    def copy_file(self, rel: str) -> None:
        src = self.templates_path / rel
        dst = self.target / rel

        if not src.exists():
            print(f"  ✗ Source missing: {src}")
            return

        action = "CREATE"
        if dst.exists():
            if not self.force:
                self.skipped.append(rel)
                print(color(f"  ⊘ Skip (exists, use --force): {rel}", BROWN))
                return
            action = "OVERWRITE"
            self.overwritten.append(rel)
        else:
            self.created.append(rel)

        if self.dry_run:
            print(color(f"  ○ [{action}] {rel}", CYAN))
            return

        ensure_dir(dst.parent)
        if rel in TEMPLATED_FILES:
            content = src.read_text(encoding="utf-8")
            content = self.apply_placeholders(rel, content)
            dst.write_text(content, encoding="utf-8")
        else:
            shutil.copy2(src, dst)
        print(color(f"  ✓ [{action}] {rel}", GREEN))

    def apply_placeholders(self, rel: str, content: str) -> str:
        if rel == "AGENTS.md":
            return transform_agents(content, self.name, self.slug)
        elif rel == "WORKFLOW.md":
            return transform_workflow(content, self.name, self.slug)
        elif rel == "docs/architecture.md":
            return transform_architecture(
                content, self.name, self.description, self.domains)
        elif rel == "docs/quality.md":
            return transform_quality(
                content, self.name, self.slug, self.domains)
        return content

    def run(self) -> int:
        if not self.validate():
            return 1

        self.interactive_setup()

        if not self.name:
            print(color("Error: Project name is required.", RED), file=sys.stderr)
            return 1

        if self.mode == "greenfield" and not self.domains:
            print(color(
                "Warning: No domains specified. "
                "Use --domains or interactive prompt.", BROWN))

        print(f"\n{BOLD}Target:{RESET} {self.target}")
        print(f"{BOLD}Project:{RESET} {self.name} ({self.slug})")
        print(f"{BOLD}Mode:{RESET} {self.mode}")
        print(f"{BOLD}Description:{RESET} {self.description}")
        dom_str = ", ".join(self.domains) if self.domains else "(none)"
        print(f"{BOLD}Domains:{RESET} {dom_str}")
        if self.dry_run:
            print(color(f"{BOLD}DRY RUN{RESET} — no files will be written\n",
                        BROWN))
        print()

        for rel in HARNESS_FILES:
            self.copy_file(rel)

        print()
        print(f"{BOLD}═══ Summary ═══{RESET}\n")

        if self.dry_run:
            print(color(f"Would create {len(self.created)} files:", CYAN))
            for f in self.created:
                print(color(f"  + {f}", GREEN))
            if self.overwritten:
                print(color(f"Would overwrite {len(self.overwritten)} files:",
                            BROWN))
                for f in self.overwritten:
                    print(color(f"  ~ {f}", BROWN))
            if self.skipped:
                print(color(f"Would skip {len(self.skipped)} existing files:",
                            BROWN))
                for f in self.skipped:
                    print(color(f"  ⊘ {f}", BROWN))
        else:
            print(color(f"Created {len(self.created)} files.", GREEN))
            if self.overwritten:
                print(color(f"Overwritten {len(self.overwritten)} files.",
                            BROWN))
            if self.skipped:
                n = len(self.skipped)
                print(color(f"Skipped {n} existing files "
                            f"(use --force to overwrite).", BROWN))

            print(f"\n{BOLD}Next steps:{RESET}")
            print(f"  1. cd {self.target}")
            print(f"  2. Read AGENTS.md (agents) or WORKFLOW.md (humans)")
            tgt = color("make all", GREEN)
            print(f"  3. Run: {tgt} — runs all linters and quality checks")
            if self.mode == "greenfield":
                tgt = color('/implement "your first feature"', GREEN)
                print(f"  4. Start building: {tgt}")

        return 0


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize the Humbleflow workflow into any project.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 init-harness.py ~/projects/myapp --greenfield --name "MyApp" --domains "auth,billing"
  python3 init-harness.py ~/projects/existing-app --brownfield
  python3 init-harness.py ~/projects/myapp --name "MyApp" --domains "auth" --dry-run
  python3 init-harness.py ~/projects/myapp --greenfield --name "MyApp" --domains "core" --non-interactive
        """)
    parser.add_argument("target", help="Target project directory")
    parser.add_argument("--greenfield", action="store_true",
                        help="Initialize for a new/empty project")
    parser.add_argument("--brownfield", action="store_true",
                        help="Initialize into an existing codebase")
    parser.add_argument("--name", default="", help="Project name")
    parser.add_argument("--description", default="",
                        help="Short project description")
    parser.add_argument("--domains", default="",
                        help="Comma-separated domain names (e.g., auth,billing)")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing harness files")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without doing it")
    parser.add_argument("--harness-path", default="",
                        help="Path to harness package root")
    parser.add_argument("--templates-path", default="",
                        help="Path to templates directory (default: harness-path/templates)")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Disable interactive prompts (for CI)")

    args = parser.parse_args()

    if args.greenfield and args.brownfield:
        print("Error: Cannot specify both --greenfield and --brownfield.",
              file=sys.stderr)
        return 1

    mode = "greenfield" if args.greenfield else (
        "brownfield" if args.brownfield else "auto")

    harness_path = Path(args.harness_path) if args.harness_path else (
        Path(__file__).resolve().parent)

    if args.templates_path:
        templates_path = Path(args.templates_path)
    else:
        templates_path = harness_path / "templates"

    domains = ([d.strip() for d in args.domains.split(",") if d.strip()]
               if args.domains else [])

    if mode == "greenfield" and not args.name and args.non_interactive:
        print("Error: --name is required for greenfield in non-interactive mode.",
              file=sys.stderr)
        return 1

    init = HarnessInit(
        target=Path(args.target),
        harness_path=harness_path,
        templates_path=templates_path,
        name=args.name,
        description=args.description,
        domains=domains,
        mode=mode,
        force=args.force,
        dry_run=args.dry_run,
        interactive=not args.non_interactive,
    )
    return init.run()


if __name__ == "__main__":
    sys.exit(main())
