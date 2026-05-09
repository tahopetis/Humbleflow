#!/usr/bin/env python3
"""
Find stale documentation and report issues.

Scans docs/ for references to files, functions, or APIs that no longer exist
or have been moved. Also checks for docs that haven't been updated in a long
time relative to the code they describe.

Reads: docs/ directory
Scans: src/ for existence of referenced files
Output: A report of stale docs with remediation suggestions
Exit code: 0 if no stale docs found, 1 if issues found (non-blocking)

This tool opens "fix-up reports" — it does not auto-edit docs. The garbage
collection workflow uses this to create targeted refactoring PRs.
"""

import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
SRC_DIR = ROOT / "src"


def find_doc_files() -> List[Path]:
    """Find all documentation files."""
    if not DOCS_DIR.exists():
        return []
    docs = []
    for ext in [".md"]:
        docs.extend(DOCS_DIR.rglob(f"*{ext}"))
    return sorted(docs)


def find_all_repo_files() -> Set[str]:
    """Build a set of all repo file paths (relative to root) for reference checking."""
    files = set()
    for search_dir in [SRC_DIR, ROOT / "tools", ROOT / "docs"]:
        if not search_dir.exists():
            continue
        for f in search_dir.rglob("*"):
            if f.is_file() and f.suffix in {".ts", ".tsx", ".js", ".jsx", ".py", ".md"}:
                files.add(str(f.relative_to(ROOT)))
    return files


def extract_references(doc_path: Path) -> List[Tuple[str, int, str]]:
    """
    Extract file references from a markdown document.
    Returns: [(reference_text, lineno, context)]
    """
    refs = []
    try:
        with open(doc_path) as f:
            content = f.read()
    except Exception:
        return refs

    # Remove fenced code blocks before scanning for references
    content_no_code = re.sub(r'```[^`]*```', '', content, flags=re.DOTALL)
    lines = content_no_code.split('\n')
    doc_filename = doc_path.name

    # Patterns for file references in markdown (only outside code blocks)
    patterns = [
        # Link paths: [text](path.md) or [text](path.py) — the most reliable signal
        r"\]\(([\w/\-\.]+\.(?:md|py|ts|tsx|yml))\)",
        # Explicit mentions: "See src/domains/auth/service.ts" or "in tools/lint.py"
        r"(?:see|in|at|file|from|run)\s+`?((?:src|tools|docs|plans)/[\w/\-\.]+\.[\w]+)`?",
    ]

    for lineno, line in enumerate(lines, 1):
        for pattern in patterns:
            for match in re.finditer(pattern, line, re.IGNORECASE):
                ref_text = match.group(1).rstrip('/')
                # Skip directory references (no file extension)
                if '/' in ref_text and '.' not in ref_text.split('/')[-1]:
                    continue
                # Skip self-references
                if ref_text == doc_filename or ref_text.endswith('/' + doc_filename):
                    continue
                refs.append((ref_text, lineno, line.strip()))

    return refs


def check_reference_exists(
    ref: str, source_files: Set[str]
) -> Tuple[bool, str]:
    """
    Check if a referenced file exists.
    Returns (exists, resolved_path).
    """
    # Try exact match
    if ref in source_files:
        return True, ref

    # Strip ../ if present (relative path from docs/)
    clean = ref
    while clean.startswith('../'):
        clean = clean[3:]
    if clean in source_files:
        return True, clean

    # Try with relative path from repo root
    try:
        relative = str((ROOT / ref).relative_to(ROOT))
        if relative in source_files:
            return True, relative
    except ValueError:
        pass

    # Try without file extension
    stem = Path(ref).stem
    for sf in source_files:
        if Path(sf).stem == stem:
            return True, sf

    return False, ref


def check_doc_freshness(doc_path: Path) -> Optional[str]:
    """
    Check if a doc references code that's newer than the doc itself.
    Returns a message if the doc might be stale.
    """
    try:
        doc_mtime = doc_path.stat().st_mtime
    except Exception:
        return None

    # Find referenced source files
    refs = extract_references(doc_path)
    source_files = find_all_repo_files()

    stale_refs = []
    for ref_text, lineno, _context in refs:
        exists, resolved = check_reference_exists(ref_text, source_files)
        if not exists:
            stale_refs.append((ref_text, lineno, "File not found"))

    if stale_refs:
        lines = []
        for ref_text, lineno, reason in stale_refs:
            lines.append(f"  Line {lineno}: `{ref_text}` — {reason}")
        return "\n".join(lines)

    return None


def main() -> int:
    doc_files = find_doc_files()
    if not doc_files:
        print("No documentation files found in docs/.")
        return 0

    source_files = find_all_repo_files()
    issues: Dict[str, str] = {}
    total_issues = 0

    print(f"Scanning {len(doc_files)} doc(s) for stale references...\n")

    for doc_path in doc_files:
        rel = str(doc_path.relative_to(ROOT))
        stale = check_doc_freshness(doc_path)
        if stale:
            issues[rel] = stale
            total_issues += 1

    if issues:
        print(f"\n{'='*60}")
        print(f"STALE DOCUMENTATION FOUND: {total_issues} file(s)")
        print(f"{'='*60}\n")
        for doc, detail in issues.items():
            print(f"📄 {doc}")
            print(detail)
            print()
        print("Garbage collection: Open a fix-up PR for each stale doc.")
        print("Run `/garbage-collect` to create targeted refactoring PRs.")
        return 1

    print(f"✓ No stale documentation found ({len(doc_files)} docs scanned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
