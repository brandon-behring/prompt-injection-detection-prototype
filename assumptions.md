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
| A-001 | runpod-deploy + eval-toolkit infrastructure can compress a normally-2-week 2×3-grid + multi-seed + OOD + paired-bootstrap workload into ~2.5 working days. If false, the fallback ladder (2×3 → 2×2 → 1×2 → 1×1) activates and the writeup honestly reports what was achieved, not what was attempted. | high | unverified | ADR-001 | Mid-Phase-2 checkpoint triggers fallback evaluation. |
| A-002 | API budget for LLM-judge reference rungs (one OpenAI model + one Anthropic model, both at temperature=0, one call per eval row) lands in the $50-$200 range for an eval slate of ~5K prompts. If actual cost exceeds budget, narrow the eval slate or drop one judge. | medium | unverified | ADR-007 | Verification at end of Phase 3 against cumulative API cost. |
| A-003 | Pre-teardown persistence checklist is enforced for every RunPod pod before destruction (per-row predictions + manifests + checkpoints + logs + results.json). If false, a mid-run pod loss reverts the affected rung and the fallback ladder may activate to recover. | medium | unverified | ADR-013 | Phase 2 entry creates `scripts/pre_teardown_check.sh` (or equivalent) and verifies runpod-deploy's incremental persistence support. |

`[TBD: populated incrementally from Phase 0 onward — Phase 0-02 (data), 0-03 (model details), 0-04 (eval), 0-05 (threshold), 0-06 (code), 0-07 (submission), 0-08 (tech-stack) will add their own assumptions as load-bearing decisions surface]`
