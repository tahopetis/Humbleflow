#!/usr/bin/env python3
"""
Scan domains, evaluate against quality rubric, and update docs/quality.md.

Reads:  docs/quality.md (the current grades and YAML block)
Runs:   lint-boundaries.py and lint-golden.py to collect violation counts
        Checks test coverage (heuristic: co-located test file presence)
        Checks for stale docs
Updates: docs/quality.md with new grades and issue counts

Exit code: 0 always (updates grades, does not fail)
"""

import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("Warning: PyYAML not installed. Install with: pip install pyyaml")
    print("Falling back to text-based parsing of quality.md")
    yaml = None


ROOT = Path(__file__).resolve().parent.parent
QUALITY_FILE = ROOT / "docs" / "quality.md"

# Grading rubric
RUBRIC = {
    "A": (0, "Excellent"),
    "B": (2, "Good"),
    "C": (5, "Acceptable"),
    "D": (10, "Poor"),
    "F": (999, "Critical"),
}


def compute_grade(total_issues: int) -> str:
    """Determine grade from total issue count."""
    for grade, (threshold, _label) in sorted(RUBRIC.items()):
        if total_issues <= threshold:
            return grade
    return "F"


def run_boundary_lint() -> int:
    """Run lint-boundaries.py and return violation count."""
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "lint-boundaries.py")],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        # Parse violation count from output
        match = re.search(r"BOUNDARY VIOLATIONS FOUND: (\d+)", result.stdout)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return 0


def run_golden_lint() -> int:
    """Run lint-golden.py and return violation count."""
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "lint-golden.py")],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        match = re.search(
            r"GOLDEN PRINCIPLE VIOLATIONS FOUND: (\d+)", result.stdout
        )
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return 0


def count_test_gaps(domain: str) -> int:
    """
    Count source files without co-located tests in a domain.
    """
    domain_dir = ROOT / "src" / "domains" / domain
    if not domain_dir.exists():
        return 0

    gaps = 0
    for f in domain_dir.rglob("*.ts"):
        if f.name.endswith(".test.ts") or f.name.endswith(".spec.ts"):
            continue
        # Skip type-only and config files
        if f.parent.name == "types" or "config" in f.name.lower():
            continue

        stem = f.stem
        test_file = f.with_name(f"{stem}.test.ts")
        spec_file = f.with_name(f"{stem}.spec.ts")
        if not test_file.exists() and not spec_file.exists():
            gaps += 1

    return gaps


def count_stale_docs(domain: str) -> int:
    """
    Check for documentation referencing files that don't exist.
    This is a stub — the full implementation is in doc-gardener.py.
    """
    return 0


def scan_domains() -> Dict[str, Dict[str, Dict[str, int]]]:
    """
    Scan all domains and compute issue counts per domain per layer.
    Returns: {domain: {layer: {BV: n, GP: n, TC: n, SD: n}}}
    """
    domains = {}

    # Discover domains
    domains_dir = ROOT / "src" / "domains"
    if domains_dir.exists():
        for d in sorted(domains_dir.iterdir()):
            if d.is_dir():
                domains[d.name] = {}
                for layer in ["types", "config", "repo", "service", "runtime", "ui"]:
                    domains[d.name][layer] = {"BV": 0, "GP": 0, "TC": 0, "SD": 0}

    # Also track shared and providers
    for special in ["shared", "providers"]:
        special_dir = ROOT / "src" / special
        if special_dir.exists():
            domains[special] = {}
            for layer in ["types", "config", "repo", "service", "runtime", "ui"]:
                layer_dir = special_dir / layer
                if layer_dir.exists():
                    domains[special][layer] = {"BV": 0, "GP": 0, "TC": 0, "SD": 0}

    # Populate violations (BV and GP distributed by domain)
    # For now, run linters globally and distribute evenly
    bv_count = run_boundary_lint()
    gp_count = run_golden_lint()

    # Distribute BV and GP across domains
    active_domain_count = len(domains)
    if active_domain_count > 0:
        bv_per_domain = bv_count // active_domain_count
        bv_remainder = bv_count % active_domain_count
        gp_per_domain = gp_count // active_domain_count
        gp_remainder = gp_count % active_domain_count

        for i, domain in enumerate(sorted(domains.keys())):
            extra_bv = 1 if i < bv_remainder else 0
            extra_gp = 1 if i < gp_remainder else 0
            # Assign to the types layer by default (most violations live there)
            if "types" in domains[domain]:
                domains[domain]["types"]["BV"] = bv_per_domain + extra_bv
                domains[domain]["types"]["GP"] = gp_per_domain + extra_gp

    # Populate TC (test coverage gaps)
    for domain in domains:
        if domain not in ("shared", "providers"):
            tc = count_test_gaps(domain)
            if "service" in domains[domain]:
                domains[domain]["service"]["TC"] = tc

    # Populate SD (stale docs)
    for domain in domains:
        sd = count_stale_docs(domain)
        if sd > 0 and "types" in domains[domain]:
            domains[domain]["types"]["SD"] = sd

    return domains


def update_quality_file(domains: Dict[str, Dict[str, Dict[str, int]]]):
    """Update docs/quality.md with new grades."""
    if not QUALITY_FILE.exists():
        print(f"Error: {QUALITY_FILE} not found. Cannot update grades.")
        return

    with open(QUALITY_FILE) as f:
        content = f.read()

    today = date.today().isoformat()

    # Update the YAML block
    yaml_start = content.find("```yaml")
    yaml_end = content.find("```", yaml_start + 7)

    if yaml_start >= 0 and yaml_end >= 0:
        # Build new YAML
        new_yaml_lines = []
        for domain, layers in sorted(domains.items()):
            new_yaml_lines.append(f"  {domain}:")
            for layer, issues in sorted(layers.items()):
                total = sum(issues.values())
                grade = compute_grade(total)
                new_yaml_lines.append(
                    f"    {layer}: "
                    f"{{ grade: {grade}, BV: {issues['BV']}, GP: {issues['GP']}, "
                    f"TC: {issues['TC']}, SD: {issues['SD']}, updated: \"{today}\" }}"
                )

        # Find and replace the domains section in YAML
        old_yaml = content[yaml_start:yaml_end]
        new_yaml = old_yaml[: old_yaml.find("  shared:")] + "\n".join(
            new_yaml_lines
        )

        content = content[:yaml_start] + new_yaml + content[yaml_end:]

    # Update the summary table
    total_bv = sum(
        issues["BV"]
        for d in domains.values()
        for issues in d.values()
    )
    total_gp = sum(
        issues["GP"]
        for d in domains.values()
        for issues in d.values()
    )
    total_tc = sum(
        issues["TC"]
        for d in domains.values()
        for issues in d.values()
    )
    total_sd = sum(
        issues["SD"]
        for d in domains.values()
        for issues in d.values()
    )
    total_issues = total_bv + total_gp + total_tc + total_sd
    overall_grade = compute_grade(total_issues)

    # Count domains at each grade
    domain_grades = {}
    for domain, layers in domains.items():
        domain_total = sum(sum(issues.values()) for issues in layers.values())
        domain_grades[domain] = compute_grade(domain_total)

    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for g in domain_grades.values():
        grade_counts[g] += 1

    # Replace summary metric values
    replacements = {
        r"\| Total domains tracked \| \d+ \|": f"| Total domains tracked | {len(domains)} |",
        r"\| Overall grade \| \w \|": f"| Overall grade | {overall_grade} |",
        r"\| Domains at A \| \d+ \|": f"| Domains at A | {grade_counts['A']} |",
        r"\| Domains at B \| \d+ \|": f"| Domains at B | {grade_counts['B']} |",
        r"\| Domains at C \| \d+ \|": f"| Domains at C | {grade_counts['C']} |",
        r"\| Domains at D \| \d+ \|": f"| Domains at D | {grade_counts['D']} |",
        r"\| Domains at F \| \d+ \|": f"| Domains at F | {grade_counts['F']} |",
        r"\| Total BV \(boundary violations\) \| \d+ \|": f"| Total BV (boundary violations) | {total_bv} |",
        r"\| Total GP \(golden principle violations\) \| \d+ \|": f"| Total GP (golden principle violations) | {total_gp} |",
        r"\| Total TC \(test coverage gaps\) \| \d+ \|": f"| Total TC (test coverage gaps) | {total_tc} |",
        r"\| Total SD \(stale docs\) \| \d+ \|": f"| Total SD (stale docs) | {total_sd} |",
        r"\| Total issues \| \d+ \|": f"| Total issues | {total_issues} |",
        r"\| Last full scan \| [\d-]+ \|": f"| Last full scan | {today} |",
    }

    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)

    # Update header line
    content = re.sub(
        r"Overall grade: \*\*\w\*\*",
        f"Overall grade: **{overall_grade}**",
        content,
    )
    content = re.sub(
        r"Last full scan: [\d-]+",
        f"Last full scan: {today}",
        content,
    )

    with open(QUALITY_FILE, "w") as f:
        f.write(content)

    print(f"\n{'='*60}")
    print(f"QUALITY GRADES UPDATED")
    print(f"{'='*60}")
    print(f"  Overall: {overall_grade}")
    print(f"  Domains tracked: {len(domains)}")
    print(f"  A: {grade_counts['A']}  B: {grade_counts['B']}  C: {grade_counts['C']}  D: {grade_counts['D']}  F: {grade_counts['F']}")
    print(f"  Total issues: {total_issues} (BV={total_bv}, GP={total_gp}, TC={total_tc}, SD={total_sd})")
    print(f"  Updated: {today}")
    print(f"  File: {QUALITY_FILE}")


def main() -> int:
    domains = scan_domains()
    if not domains:
        print("No domains found in src/domains/. Skipping quality update.")
        return 0
    update_quality_file(domains)
    return 0


if __name__ == "__main__":
    sys.exit(main())
