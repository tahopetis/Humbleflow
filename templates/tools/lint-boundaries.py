#!/usr/bin/env python3
"""
Validate dependency directions per the Humbleflow layered architecture.

Architecture rule: Types → Config → Repo → Service → Runtime → UI
Code may only depend "forward" (downward) through the layers.
Backward imports and cross-domain imports are violations.

Reads: docs/architecture.md for domain map
Scans: src/domains/ for import statements
Output: violation list with remediation instructions for agent context
Exit code: 0 if clean, 1 if violations found
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Layer ordering (lower index = lower layer, imports go upward in index)
LAYERS = ["types", "config", "repo", "service", "runtime", "ui"]
LAYER_INDEX = {layer: i for i, layer in enumerate(LAYERS)}

# Directories to skip
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pi", "plans", "docs", "tools"}


def find_source_files(root: Path) -> List[Path]:
    """Find all TypeScript/JavaScript source files."""
    source_dirs = []
    for d in ["src", "app", "lib"]:
        p = root / d
        if p.exists():
            source_dirs.append(p)

    if not source_dirs:
        return []

    files = []
    for sd in source_dirs:
        for ext in [".ts", ".tsx", ".js", ".jsx"]:
            files.extend(sd.rglob(f"*{ext}"))

    return sorted(files)


def extract_imports(filepath: Path) -> List[Tuple[str, str, int]]:
    """
    Extract import paths from a TypeScript/JavaScript file.
    Returns list of (import_path, type, lineno).
    """
    imports = []
    try:
        with open(filepath) as f:
            content = f.read()
    except Exception:
        return imports

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, "import", node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append((node.module, "import_from", node.lineno))

    return imports


def infer_domain_and_layer(filepath: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Infer the domain and layer from a file's path.
    Expected structure: src/domains/<domain>/<layer>/...
                       or src/shared/...
                       or src/providers/...
    """
    parts = filepath.parts
    try:
        if "domains" in parts:
            idx = parts.index("domains")
            domain = parts[idx + 1]
            layer = parts[idx + 2] if len(parts) > idx + 2 else None
            return domain, layer
        elif "shared" in parts:
            idx = parts.index("shared")
            layer = parts[idx + 1] if len(parts) > idx + 1 else None
            return "shared", layer
        elif "providers" in parts:
            idx = parts.index("providers")
            layer = parts[idx + 1] if len(parts) > idx + 1 else None
            return "providers", layer
    except IndexError:
        pass
    return None, None


def resolve_import_target(
    import_path: str, source_file: Path, root: Path
) -> Tuple[Optional[str], Optional[str]]:
    """
    Resolve an import path to its domain and layer.
    Handle relative imports, aliases, and absolute imports.
    """
    # Relative imports
    if import_path.startswith("."):
        resolved = (source_file.parent / import_path).resolve()
        try:
            rel = resolved.relative_to(root)
            return infer_domain_and_layer(rel)
        except ValueError:
            return None, None

    # Alias imports (@/ or ~/)
    if import_path.startswith("@/") or import_path.startswith("~/"):
        stripped = import_path[2:]
        parts = Path(stripped).parts
        if parts[0] == "domains":
            domain = parts[1] if len(parts) > 1 else None
            layer = parts[2] if len(parts) > 2 else None
            return domain, layer
        elif parts[0] == "shared":
            layer = parts[1] if len(parts) > 1 else None
            return "shared", layer
        elif parts[0] == "providers":
            layer = parts[1] if len(parts) > 1 else None
            return "providers", layer

    # Absolute imports (e.g., from a package)
    # Check if it resolves to something in src/
    possible = root / "src" / import_path.replace(".", "/")
    if possible.exists() or possible.with_suffix(".ts").exists():
        return infer_domain_and_layer(Path("src") / import_path.replace(".", "/"))

    # External import — not a violation
    return None, None


def check_violation(
    source_domain: Optional[str],
    source_layer: Optional[str],
    target_domain: Optional[str],
    target_layer: Optional[str],
    import_path: str,
    filepath: Path,
    lineno: int,
) -> Optional[str]:
    """Check if an import violates boundary rules. Returns violation message or None."""

    # External or unresolvable imports are not violations
    if target_domain is None or target_layer is None:
        return None
    if source_domain is None or source_layer is None:
        return None

    # Same domain: check layer ordering
    if source_domain == target_domain:
        source_idx = LAYER_INDEX.get(source_layer)
        target_idx = LAYER_INDEX.get(target_layer)
        if source_idx is not None and target_idx is not None:
            if source_idx > target_idx:
                return (
                    f"Backward import: {source_domain}/{source_layer} → "
                    f"{target_domain}/{target_layer}\n"
                    f"  Import: '{import_path}' at line {lineno}\n"
                    f"  Rule: {source_layer} (layer {source_idx}) cannot import "
                    f"from {target_layer} (layer {target_idx})\n"
                    f"  Fix: Move the shared logic to a lower layer, or use "
                    f"dependency inversion (define an interface in {target_layer} "
                    f"and implement in {source_layer})"
                )

    # Cross-domain imports: only shared types allowed
    if source_domain != target_domain:
        # Allow importing from shared (cross-domain utility)
        if target_domain == "shared":
            return None
        # Allow importing types from another domain (dependency inversion)
        if target_layer == "types":
            return None
        # Allow providers import (cross-cutting concern)
        if target_domain == "providers":
            return None

        return (
            f"Cross-domain import: {source_domain}/{source_layer} → "
            f"{target_domain}/{target_layer}\n"
            f"  Import: '{import_path}' at line {lineno}\n"
            f"  Rule: Domain {source_domain} cannot import from domain "
            f"{target_domain} layer {target_layer}\n"
            f"  Fix: Move shared types to {target_domain}/types or shared/, "
            f"or use Providers for cross-cutting concerns"
        )

    return None


def main() -> int:
    root = Path.cwd()
    violations: List[str] = []

    source_files = find_source_files(root)
    if not source_files:
        print("No source files found. Skipping boundary lint.")
        return 0

    for filepath in source_files:
        source_domain, source_layer = infer_domain_and_layer(filepath)
        imports = extract_imports(filepath)

        for import_path, _import_type, lineno in imports:
            target_domain, target_layer = resolve_import_target(
                import_path, filepath, root
            )
            violation = check_violation(
                source_domain,
                source_layer,
                target_domain,
                target_layer,
                import_path,
                filepath,
                lineno,
            )
            if violation:
                violations.append(f"{filepath}: {violation}")

    if violations:
        print(f"\n{'='*60}")
        print(f"BOUNDARY VIOLATIONS FOUND: {len(violations)}")
        print(f"{'='*60}\n")
        for v in violations:
            print(v)
            print()
        print(f"See docs/architecture.md for the layered architecture rules.")
        print(
            f"See .pi/skills/humbleflow/references/architecture.md "
            f"for detailed guidance."
        )
        return 1

    print(f"✓ No boundary violations found ({len(source_files)} files scanned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
