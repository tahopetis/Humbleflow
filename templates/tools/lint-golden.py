#!/usr/bin/env python3
"""
Validate golden principles across the codebase.

Enforces:
  1. Parse, don't validate (no YOLO probing: any, unchecked as casts, deep optional chaining)
  2. Shared utilities over hand-rolled helpers (detects duplicated implementations)
  3. No YOLO data probing (flags any, unchecked as, deep ?. on external data)
  4. Structured logging (flags console.log, console.error, console.warn)
  5. Naming conventions (domain dirs, file patterns)
  6. File size limits
  7. Test coverage expectations (co-located test files)

Reads: docs/principles.md for rule definitions
Scans: src/ for violations
Output: violation list with remediation instructions
Exit code: 0 if clean, 1 if violations found
"""

import ast
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ── Configuration ──────────────────────────────────────────────────────────

# File size limits (from docs/principles.md)
SIZE_LIMITS = {
    "types": 200,
    "schema": 200,
    "config": 150,
    "service": 300,
    "repo": 250,
    "repository": 250,
    "ui": 300,
    "component": 300,
    "test": 500,
    "spec": 500,
    "doc": 400,
    "md": 400,
}

# Naming conventions (from docs/principles.md)
NAMING_RULES = {
    # (pattern, expected, layer_hint)
    r"src/domains/[\w-]+/types/": (r"[A-Z]\w*\.ts$", "PascalCase"),
    r"src/domains/[\w-]+/config/": (r"[a-z]\w*\.ts$", "camelCase"),
    r"src/domains/[\w-]+/service/": (r"[a-z]\w*\.ts$", "camelCase"),
    r"src/domains/[\w-]+/repo/": (r"[a-z]\w*\.ts$", "camelCase"),
    r"src/domains/[\w-]+/runtime/": (r"[a-z]\w*\.ts$", "camelCase"),
    r"src/domains/[\w-]+/ui/": (r"[A-Z]\w*\.tsx?$", "PascalCase"),
}

# Directories to skip
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pi", "plans", "docs", "tools"}

# Disallowed console patterns
CONSOLE_PATTERNS = [
    r"console\.log\(",
    r"console\.error\(",
    r"console\.warn\(",
    r"console\.debug\(",
    r"console\.info\(",
]

# YOLO probing patterns
YOLO_PATTERNS = [
    (r"\bas any\b", "`as any` cast — use a typed schema instead"),
    (r":\s*any\b", "`: any` type annotation — use a proper type or `unknown`"),
    (r"(?:response|data|body|result)\?\.\w+\?\.\w+\?\.", "Deep optional chaining on external data — parse the data with a schema at the boundary"),
]


def find_source_files(root: Path) -> List[Path]:
    """Find all source files to lint."""
    files = []
    for src_dir in ["src", "app", "lib"]:
        p = root / src_dir
        if not p.exists():
            continue
        for ext in [".ts", ".tsx", ".js", ".jsx", ".md"]:
            files.extend(p.rglob(f"*{ext}"))
    return sorted(files)


# ── Check 1: No YOLO Data Probing ─────────────────────────────────────────

def check_yolo_probing(filepath: Path) -> List[str]:
    """Check for `any`, unchecked `as` casts, and deep optional chaining."""
    violations = []
    try:
        with open(filepath) as f:
            lines = f.readlines()
    except Exception:
        return violations

    for lineno, line in enumerate(lines, 1):
        for pattern, description in YOLO_PATTERNS:
            if re.search(pattern, line):
                violations.append(
                    f"  {filepath}:{lineno}: YOLO data probing detected: {description}\n"
                    f"    → {line.strip()}\n"
                    f"    Fix: Parse data with a typed schema at the boundary "
                    f"(see docs/principles.md#3-no-yolo-data-probing)"
                )
    return violations


# ── Check 2: Structured Logging ────────────────────────────────────────────

def check_console_logging(filepath: Path) -> List[str]:
    """Check for console.log/error/warn usage in production code."""
    violations = []
    try:
        with open(filepath) as f:
            lines = f.readlines()
    except Exception:
        return violations

    for lineno, line in enumerate(lines, 1):
        for pattern in CONSOLE_PATTERNS:
            if re.search(pattern, line) and "// allow-console" not in line:
                violations.append(
                    f"  {filepath}:{lineno}: Unstructured logging detected\n"
                    f"    → {line.strip()}\n"
                    f"    Fix: Use the project's structured logger (injected via "
                    f"Providers). Every log entry must include level, message, "
                    f"timestamp, traceId, spanId, domain. "
                    f"(see docs/principles.md#4-structured-logging)"
                )
    return violations


# ── Check 3: File Size Limits ──────────────────────────────────────────────

def check_file_size(filepath: Path) -> List[str]:
    """Check file against size limits."""
    ext = filepath.suffix
    filename = filepath.name.lower()
    parent = filepath.parent.name.lower() if filepath.parent.name else ""

    # Determine file type for limit lookup
    file_type = None
    if ext == ".md":
        file_type = "md"
    elif "test" in filename or "spec" in filename:
        file_type = "test"
    elif parent in SIZE_LIMITS:
        file_type = parent
    elif "schema" in filename:
        file_type = "schema"
    elif "config" in filename:
        file_type = "config"
    elif "service" in filename:
        file_type = "service"
    elif "repo" in filename:
        file_type = "repo"
    elif "component" in filename or ext == ".tsx":
        file_type = "ui"

    limit = SIZE_LIMITS.get(file_type)
    if limit is None:
        return []

    try:
        with open(filepath) as f:
            line_count = sum(1 for _ in f)
    except Exception:
        return []

    if line_count > limit:
        return [
            f"  {filepath}: File size {line_count} lines exceeds limit "
            f"of {limit} lines for {file_type} files\n"
            f"    Fix: Extract focused sub-modules. "
            f"(see docs/principles.md#6-file-size-discipline)"
        ]
    return []


# ── Check 4: Naming Conventions ────────────────────────────────────────────

def check_naming(filepath: Path) -> List[str]:
    """Check file naming conventions."""
    violations = []
    rel = str(filepath)

    for path_pattern, (name_pattern, convention) in NAMING_RULES.items():
        if re.search(path_pattern, rel):
            filename = filepath.name
            if not re.match(name_pattern, filename):
                violations.append(
                    f"  {filepath}: File name '{filename}' does not match "
                    f"{convention} convention for this layer\n"
                    f"    Fix: Rename to follow {convention} convention "
                    f"(see docs/principles.md#5-consistent-naming)"
                )
            break

    return violations


# ── Check 5: Test Co-location ──────────────────────────────────────────────

def check_test_colocation(root: Path) -> List[str]:
    """Check that source files have co-located test files."""
    violations = []
    source_files = []

    for src_dir in ["src"]:
        p = root / src_dir
        if not p.exists():
            continue
        for ext in [".ts", ".tsx"]:
            for f in p.rglob(f"*{ext}"):
                if "test" not in f.name and "spec" not in f.name:
                    # Skip type-only files and simple configs
                    if f.parent.name == "types" and f.suffix == ".ts":
                        continue
                    if "config" in f.name.lower():
                        continue
                    source_files.append(f)

    for sf in source_files:
        # Check for *.test.ts or *.spec.ts next to the file
        stem = sf.stem
        test_patterns = [
            sf.with_name(f"{stem}.test{sf.suffix}"),
            sf.with_name(f"{stem}.spec{sf.suffix}"),
            sf.parent / "__tests__" / f"{stem}.test{sf.suffix}",
            sf.parent / "__tests__" / f"{stem}.spec{sf.suffix}",
        ]
        if not any(tp.exists() for tp in test_patterns):
            violations.append(
                f"  {sf}: No co-located test file found\n"
                f"    Fix: Create {stem}.test.ts with tests for this module "
                f"(see docs/principles.md#7-test-coverage)"
            )

    return violations


# ── Check 6: Hand-rolled Shared Utilities ──────────────────────────────────

def check_duplicated_helpers(root: Path) -> List[str]:
    """
    Detect functions that appear in multiple domains but not in shared/.
    This is a heuristic check — it flags function signatures that appear
    in 2+ domains as potential candidates for extraction.
    """
    function_signatures: Dict[str, List[Path]] = defaultdict(list)
    violations = []

    for src_dir in ["src/domains"]:
        p = root / src_dir
        if not p.exists():
            continue
        for f in p.rglob("*.ts"):
            try:
                with open(f) as fh:
                    content = fh.read()
            except Exception:
                continue

            # Find exported function declarations
            for match in re.finditer(
                r"export\s+(?:async\s+)?function\s+(\w+)", content
            ):
                fn_name = match.group(1)
                function_signatures[fn_name].append(f)

    # Flag functions appearing in 2+ domains
    for fn_name, files in function_signatures.items():
        domains = set()
        for fp in files:
            parts = fp.parts
            if "domains" in parts:
                idx = parts.index("domains")
                if len(parts) > idx + 1:
                    domains.add(parts[idx + 1])

        if len(domains) >= 2:
            # Check if it exists in shared/
            shared_file = root / "src" / "shared" / f"{fn_name}.ts"
            if not shared_file.exists():
                violations.append(
                    f"  Function '{fn_name}' appears in {len(domains)} domains "
                    f"({', '.join(sorted(domains))}) but not in shared/\n"
                    f"    Files: {', '.join(str(f.relative_to(root)) for f in files)}\n"
                    f"    Fix: Extract to shared/{fn_name}.ts with 100% test coverage "
                    f"and OpenTelemetry instrumentation "
                    f"(see docs/principles.md#2-shared-utilities-over-hand-rolled-helpers)"
                )

    return violations


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> int:
    root = Path.cwd()
    files = find_source_files(root)

    if not files:
        print("No source files found. Skipping golden principle lint.")
        return 0

    all_violations: List[str] = []

    print(f"Scanning {len(files)} files for golden principle violations...\n")

    # Run all checks
    for filepath in files:
        all_violations.extend(check_yolo_probing(filepath))
        all_violations.extend(check_console_logging(filepath))
        all_violations.extend(check_file_size(filepath))
        all_violations.extend(check_naming(filepath))

    all_violations.extend(check_test_colocation(root))
    all_violations.extend(check_duplicated_helpers(root))

    if all_violations:
        print(f"\n{'='*60}")
        print(f"GOLDEN PRINCIPLE VIOLATIONS FOUND: {len(all_violations)}")
        print(f"{'='*60}\n")
        for v in all_violations:
            print(v)
            print()
        print(f"See docs/principles.md for all golden principles.")
        print(
            f"See .pi/skills/humbleflow/references/golden-principles.md "
            f"for detailed guidance."
        )
        return 1

    print(f"✓ No golden principle violations found ({len(files)} files scanned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
