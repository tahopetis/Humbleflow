#!/usr/bin/env python3
"""
Validate execution plan structure.

Checks that plans in plans/ follow the template conventions:
  - Required frontmatter fields present (created, status)
  - Required sections present (Goal, Approach)
  - Progress log is updated when status is not "draft"
  - Decision log captures decisions made during implementation

Reads: plans/*.md
Output: validation report
Exit code: 0 if all valid, 1 if issues found (warning, not blocking)
"""

import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parent.parent
PLANS_DIR = ROOT / "plans"

# Required frontmatter fields
REQUIRED_FRONTMATTER = ["created", "status"]

# Required sections for full plans
REQUIRED_SECTIONS = [
    "Goal",
    "Constraints",
    "Success Criteria",
    "Approach",
    "Progress Log",
    "Decision Log",
]

# Required sections for lightweight plans
LIGHTWEIGHT_SECTIONS = [
    "Goal",
    "Approach",
    "Completed",
]

# Valid statuses
VALID_STATUSES = {"draft", "planning", "active", "completed", "archived", "superseded"}


def find_plan_files() -> List[Path]:
    """Find all plan files, excluding templates and README."""
    if not PLANS_DIR.exists():
        return []
    plans = []
    for f in PLANS_DIR.glob("*.md"):
        name = f.name
        if name in ("README.md", "template.md", "template-lightweight.md"):
            continue
        plans.append(f)
    return sorted(plans)


def parse_frontmatter(content: str) -> Tuple[Dict[str, str], int]:
    """Parse YAML frontmatter block. Returns (fields, end_line)."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, 0

    fields = {}
    end_line = 1
    for i, line in enumerate(lines[1:], 2):
        if line.strip() == "---":
            end_line = i
            break
        match = re.match(r"(\w[\w-]*):\s*(.+)", line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            fields[key] = value

    return fields, end_line


def validate_plan(filepath: Path) -> List[str]:
    """Validate a single plan file. Returns list of issues."""
    issues = []
    rel = str(filepath.relative_to(ROOT))

    try:
        with open(filepath) as f:
            content = f.read()
    except Exception:
        issues.append(f"{rel}: Cannot read file")
        return issues

    # Check frontmatter
    if not content.startswith("---"):
        issues.append(f"{rel}: Missing frontmatter (must start with ---)")
        return issues

    frontmatter, fm_end = parse_frontmatter(content)

    # Check required frontmatter fields
    for field in REQUIRED_FRONTMATTER:
        if field not in frontmatter:
            issues.append(f"{rel}: Missing required frontmatter field: '{field}'")

    # Validate status
    status = frontmatter.get("status", "")
    if status and status not in VALID_STATUSES:
        issues.append(
            f"{rel}: Invalid status '{status}'. Must be one of: "
            f"{', '.join(sorted(VALID_STATUSES))}"
        )

    # Validate created date
    created = frontmatter.get("created", "")
    if created:
        try:
            date.fromisoformat(created)
        except ValueError:
            issues.append(
                f"{rel}: Invalid 'created' date '{created}'. "
                f"Expected YYYY-MM-DD format."
            )

    # Determine plan type
    plan_type = frontmatter.get("type", "full")
    
    # Meta/reference plans are exempt from section validation
    if plan_type in ("meta", "reference"):
        return issues
    
    # Check required sections
    is_lightweight = plan_type == "lightweight"
    required = LIGHTWEIGHT_SECTIONS if is_lightweight else REQUIRED_SECTIONS
    for section in required:
        # Look for markdown headings
        pattern = rf"^#{{1,3}}\s+{re.escape(section)}\s*$"
        if not re.search(pattern, content, re.MULTILINE):
            issues.append(
                f"{rel}: Missing required section: '## {section}'"
            )

    # Check progress log for non-draft plans
    if status and status != "draft":
        progress_match = re.search(
            r"## Progress Log\s*\n(.*?)(?=\n## |\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if progress_match:
            progress_content = progress_match.group(1).strip()
            if not progress_content or progress_content == "_None yet._":
                issues.append(
                    f"{rel}: Plan status is '{status}' but Progress Log is empty. "
                    f"Add entries documenting progress."
                )
        else:
            issues.append(
                f"{rel}: Plan status is '{status}' but no Progress Log section found."
            )

    # Check decision log for completed plans
    if status == "completed":
        decision_match = re.search(
            r"## Decision Log\s*\n(.*?)(?=\n## |\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if decision_match:
            decision_content = decision_match.group(1).strip()
            if not decision_content or decision_content == "_None yet._":
                issues.append(
                    f"{rel}: Plan is completed but Decision Log is empty. "
                    f"Document decisions made during implementation."
                )

    return issues


def main() -> int:
    plan_files = find_plan_files()

    if not plan_files:
        print("No plan files found in plans/. Skipping validation.")
        return 0

    print(f"Validating {len(plan_files)} plan(s)...\n")

    all_issues: List[str] = []
    valid_count = 0

    for plan_file in plan_files:
        issues = validate_plan(plan_file)
        rel = str(plan_file.relative_to(ROOT))
        if issues:
            all_issues.extend(issues)
            print(f"✗ {rel}: {len(issues)} issue(s)")
            for issue in issues:
                print(f"  - {issue}")
        else:
            valid_count += 1
            print(f"✓ {rel}: Valid")

    if all_issues:
        print(f"\n{'='*60}")
        print(f"PLAN VALIDATION ISSUES: {len(all_issues)}")
        print(f"{'='*60}")
        print(f"  {valid_count} valid, {len(plan_files) - valid_count} with issues")
        print(f"\nSee plans/README.md for plan conventions.")
        return 1

    print(f"\n✓ All {valid_count} plan(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
