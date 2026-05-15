# Assumptions registry

Unverified assumptions made during the project. Severity tags drive whether the assumption appears in WRITEUP caveats and whether an ADR is required when it's invalidated.

## Severity

- **low** — assumption is a stylistic choice with minimal evidential impact
- **medium** — assumption affects interpretation but doesn't invalidate conclusions
- **high** — assumption is load-bearing; if false, conclusions need revisiting
- **critical** — assumption is foundational; if false, the project's framing changes

## Discipline

- Every severity ≥ medium assumption appears in WRITEUP's caveats block (invariant test: `test_reporting_completeness_assumptions_in_caveats`).
- When an assumption is invalidated mid-implementation, update this file and write a corrective ADR. Do not silently revise.

## Registry

| ID | Description | Severity | Verification status | Linked to (ADR / EVIDENCE.md §) | Notes |
|---|---|---|---|---|---|
| A-001 | `[TBD: populated at Phase 0 from brief alignment]` | — | unverified | | |

`[TBD: populated incrementally from Phase 0 onward]`
