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
| A-001 | runpod-deploy + eval-toolkit infrastructure can compress a 1×3-trained-rung-slate + 3-seed multi-seed + 5-fold LODO + 45-run workload + full OOD slate + paired-bootstrap into ~2.5 working days. Originally framed as 2×3 (six trained rungs) per ADR-007; refined to 1×3 (three trained rungs) per ADR-015 supersedes ADR-007. If false, the updated fallback ladder (1×3 → 1×2 → 1×1) activates and the writeup honestly reports what was achieved, not what was attempted. | high | unverified | ADR-001 + ADR-015 | Mid-Phase-2 checkpoint triggers fallback evaluation. |
| A-002 | Total project budget for LLM-judge reference rungs (one OpenAI model + one Anthropic model, both at temperature=0, one call per eval row) plus GPU training compute (3 trained rungs × 3 seeds × 5 LODO folds = 45 runs on H100 spot ~$3/hr) lands in the **$25-$125 range** for an eval slate of ~5K prompts. Original ADR-007 framing was $50-$200 for 6 trained rungs × multi-seed; ADR-015's single-backbone refinement halves the training compute, narrowing the envelope. If actual cost exceeds budget, narrow the eval slate or drop one judge. | medium | unverified | ADR-007 (revised by ADR-015) | Verification at end of Phase 3 against cumulative API + GPU cost. |
| A-003 | Pre-teardown persistence checklist is enforced for every RunPod pod before destruction (per-row predictions + manifests + checkpoints + logs + results.json). If false, a mid-run pod loss reverts the affected rung and the fallback ladder may activate to recover. | medium | unverified | ADR-013 | Phase 2 entry creates `scripts/pre_teardown_check.sh` (or equivalent) and verifies runpod-deploy's incremental persistence support. |
| A-004 | BIPIA samples with token-length above 8192 (ModernBERT-base native context cap) stay at or below 15 percent of the slice under the ModernBERT-base tokenizer. Per dossier characterization the rate is approximately 5 percent (3x tolerance). If false, the adaptive-chunked-scoring policy from ADR-014 becomes load-bearing on the headline indirect-injection slice (not just a conditional safeguard); a future superseding ADR (ADR-017+) adjusts chunk-stride or aggregation policy (e.g., hierarchical encoding, learned aggregator, or tighter stride). Note: ADR-014 body references "ADR-016" as the supersession placeholder; ADR-016 was actually used for Phase 0-02 data design — the truncation-policy supersession path uses the next available ADR number. | medium | unverified | ADR-014 + ADR-015 | Phase 1 length-histogram audit produces `evals/length_histograms.{train,ood}.json` with per-slice quantiles on ModernBERT-base tokenizer. |
| A-005 | The Phase 0-02 data-design locks (ADR-016) depend on the Phase 1 empirical data audit confirming dossier estimates. Specific invalidation triggers — any one of which fires the superseding-ADR requirement: (1) benign contamination scan flags >2% of either LMSYS or UltraChat as injection-template-match (MiniLM cosine >=0.85 to a known injection template); (2) post-dedup per-LODO-fold training-pool class-balance falls outside 1:3 to 1:10 positive:negative range; (3) systematic mislabeling detected in any source via spot-check (~50 random samples per source); (4) actual per-source length distribution diverges materially (5x or more on a percentile) from dossier estimates. | medium | unverified | ADR-016 | Phase 1 deliverables: `evals/data_audit.{contamination,balance,length,labeling}.json` operationalize these triggers. |

`[TBD: populated incrementally from Phase 0 onward — Phase 0-02 (data), 0-03 (model details), 0-04 (eval), 0-05 (threshold), 0-06 (code), 0-07 (submission), 0-08 (tech-stack) will add their own assumptions as load-bearing decisions surface]`
