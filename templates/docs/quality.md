# Quality Grades

> **Mechanically maintained by `tools/quality-grade.py`.**
> Tracked per business domain and architectural layer.
> Criteria defined in [`principles.md`](principles.md).
>
> Last full scan: 2026-05-09
> Overall grade: **A** — Trend: **—** (baseline)

---

## Grading Rubric

| Grade | Label | Threshold | Description |
|-------|-------|-----------|-------------|
| **A** | Excellent | 0 issues | No violations. Full test coverage. Docs current. Code exemplary. |
| **B** | Good | 1-2 issues | Minor issues. One or two golden-principle violations. Coverage ≥ 80%. |
| **C** | Acceptable | 3-5 issues | Noticeable drift. Several violations or coverage gaps. Needs attention soon. |
| **D** | Poor | 6-10 issues | Significant debt. Multiple violations across layers. Refactoring needed. |
| **F** | Critical | 11+ issues | Systemic problems. Architectural violations, widespread drift, coverage < 50%. Requires immediate rework. |

### Issue Categories

| Code | Category | Detected by | Description |
|------|----------|-------------|-------------|
| **BV** | Boundary Violation | `lint-boundaries.py` | Wrong-direction import or cross-domain import. |
| **GP** | Golden Principle Violation | `lint-golden.py` | YOLO probing, hand-rolled shared util, unstructured logging, naming convention, file size limit. |
| **TC** | Test Coverage Gap | `quality-grade.py` | Coverage below minimum threshold for the layer. |
| **SD** | Stale Documentation | `doc-gardener.py` | Docs reference deleted/moved code or are outdated. |

---

## Domain Quality

<!-- HARNESS-TEMPLATE: Domain tables use {{PLACEHOLDER}} syntax -->

<!-- quality-grade.py reads and writes the tables below.
     Format: | Domain | Layer | Grade | BV | GP | TC | SD | Issues | Last Updated |
     The "Issues" column is computed as BV+GP+TC+SD.
     Do not change column order or header text. -->

{{DOMAIN_QUALITY_ROWS}}

<!-- New domains are appended above. Layers marked "—" are not applicable
     (e.g., shared has no runtime layer, providers have no UI layer by default).
     quality-grade.py skips rows with Grade = "—". -->

---

## Summary

<!-- quality-grade.py reads and writes the rows below.
     Format: | Metric | Value |
     The "Value" column is computed from the domain tables above. -->

| Metric | Value |
|--------|-------|
{{QUALITY_SUMMARY}}

---

## Machine-Readable Block

<!-- quality-grade.py reads and writes the YAML block below.
     This is the canonical data store. The markdown tables above are
     the human-readable rendering. -->

```yaml
# humbleflow quality grades — canonical data
# Updated by: tools/quality-grade.py
# Schema version: 1
scan:
  last_full: "2026-05-09"
  next_scheduled: "2026-05-16"
  overall_grade: A
  trend: "—"
  total_issues: 0

rubric:
  A: { label: Excellent, max_issues: 0 }
  B: { label: Good, max_issues: 2 }
  C: { label: Acceptable, max_issues: 5 }
  D: { label: Poor, max_issues: 10 }
  F: { label: Critical, max_issues: 999 }

issue_categories:
  BV: { label: "Boundary Violation", tool: "lint-boundaries.py" }
  GP: { label: "Golden Principle Violation", tool: "lint-golden.py" }
  TC: { label: "Test Coverage Gap", tool: "quality-grade.py" }
  SD: { label: "Stale Documentation", tool: "doc-gardener.py" }

domains:
  {{QUALITY_YAML}}
```
