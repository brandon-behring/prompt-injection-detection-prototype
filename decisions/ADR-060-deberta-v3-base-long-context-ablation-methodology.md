---
adr_id: "060"
slug: deberta-v3-base-long-context-ablation-methodology
title: DeBERTa-v3-base medium ablation methodology — chunk-and-average vs head-truncation × 5-slice OOD; infrastructure-only at v1.1.0; execution deferred to v1.1.1
date: 2026-05-19
status: Accepted (methodology lock — infrastructure landed; execution deferred to v1.1.1 per /exploring-options 2026-05-19 Path B lock)
claim_id: CLAIM-060
claim: >-
  NEXT_STEPS §1.10 (DeBERTa-v3-base long-context ablation) was explicitly
  tagged v1.1.x at submission. /exploring-options 2026-05-19 batch 9 Q1
  locked the **medium ablation** scope: train DeBERTa-v3-base once
  (1 fold + 1 seed; LODO not full grid); apply 2 truncation strategies
  (chunk-and-average over 512-token windows + head-truncation); evaluate
  on the full 5-slice OOD slate (BIPIA + InjecAgent + JBB-Behaviors +
  XSTest + NotInject); ablation-appendix framing in RESULTS §1B (NOT
  integrated as 6th rung in the headline ladder, per §1.10 literal).
  Approximate compute envelope: 1×L4 or 1×A100; ~30 min wall per
  training fire; ~$8-10 GPU. /exploring-options 2026-05-19 Q2 lock
  chose sequential single-pod 2-fire via `lifecycle.on_success: recycle`
  (#90 closure consumption; saves ~$1-2 + ~3-5 min per fire vs full
  teardown between truncation strategies).
  **Scope-mismatch discovery (2026-05-19 mid-execution)**: the existing
  training pipeline (`src/training/train_modernbert.py` +
  `src/training/load_modernbert.py`) is ModernBERT-specific by
  construction; the `MODERNBERT_BASE_HF_ID` constant is hard-coded in
  the loader. Adding DeBERTa requires loader-refactor +
  trainer-extension + chunk-and-average windowed-inference code +
  eval-pipeline integration — ~4-6h infrastructure work BEFORE any
  GPU fire. The v1.1.0 plan estimated B5 at ~2.5h on the assumption
  the trainer was generic; it isn't. Per /exploring-options 2026-05-19
  Path B lock, v1.1.0 lands the **methodology + infrastructure
  scaffold** (this ADR + `configs/rungs/deberta_v3_base.yaml` +
  `configs/runpod/headline-deberta.yaml` + Makefile target stubs +
  RESULTS §1B placeholder); execution defers to v1.1.1. The
  methodology lock is binding regardless of when execution lands.
source: transcripts/2026-05-19__v1-1-0-runpod-deploy-and-deberta.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.1.0 close, this ADR exists with status "Accepted (methodology
  lock — infrastructure landed; execution deferred to v1.1.1)".
  `configs/rungs/deberta_v3_base.yaml` exists with hyperparameter recipe
  (backbone, fold/seed scope, truncation strategy switch, batch sizes,
  epoch count). `configs/runpod/headline-deberta.yaml` exists with
  `lifecycle.on_success: recycle` + `budget.ssh_ready_timeout_sec: 600`
  + image pin + cost cap per ADR-020 soft $125 per-job. Makefile
  targets `train-deberta-v3`, `eval-deberta-v3`, `deberta-ablation`
  exist as stubs that exit 2 with a "v1.1.1 execution carryforward"
  message + pointer to this ADR. `RESULTS.md` gains a §1B placeholder
  section with the methodology lock + planned scope + "Results pending
  v1.1.1 GPU fire" line. `WRITEUP/limitations-and-future-work.md` §9.2
  documents the deferred execution. `NEXT_STEPS.md` §1.10 status →
  "methodology landed at v1.1.0 (ADR-060); execution v1.1.1".
  `decisions/upstream_issues.md` references ADR-060 in the #90 row
  (the deferred consumer-site for `lifecycle.on_success: recycle`).
  SUBMISSION_AUDIT.md regenerates clean with 60 CLAIM rows. v1.1.1
  landing condition: `make deberta-ablation` exits 0 with per-truncation
  AUPRC/AUROC entries in `evals/metrics/per_cell_deberta.parquet`;
  RESULTS §1B placeholder replaced with real numbers; ~$5-7 GPU spend
  recorded in `evals/cost_ledger.csv` (within ADR-020 envelope).
closing_commit: v1.1.0 (methodology); v1.1.1 (execution carryforward)
supersedes: []
superseded_by: []
references:
  - decisions/ADR-015-backbone-selection-modernbert-base.md
  - decisions/ADR-020-runpod-orchestration-and-cost-discipline.md
  - decisions/ADR-050-rung-slate-narrowing-llm-judges-and-full-ft-ood-dropped.md
  - decisions/ADR-051-v1.0.x-carryforward-of-t0-and-invariant-scaffolds.md
  - decisions/ADR-059-runpod-deploy-pypi-install-narrow-supersession-of-adr-036.md
  - NEXT_STEPS.md  # §1.10
  - https://huggingface.co/microsoft/deberta-v3-base
transcript: transcripts/2026-05-19__v1-1-0-runpod-deploy-and-deberta.md
---

# ADR-060 — DeBERTa-v3-base long-context ablation methodology (v1.1.0 infrastructure; v1.1.1 execution)

## Status

Accepted (2026-05-19; methodology lock — infrastructure scaffolds
land at v1.1.0; GPU execution deferred to v1.1.1 per Path B of the
/exploring-options scope-mismatch resolution).

## Context

[NEXT_STEPS.md](../NEXT_STEPS.md) §1.10 was tagged v1.1.x at the
v1.0.0 submission close — the only scope item explicitly identified
as v1.1.x rather than v1.0.x in the §1 ladder. The motivation, per
the §1.10 entry:

> "DeBERTa-v3-base is the only widely-cited classical-transformer
> baseline left untested. ModernBERT's 8192-token native attention
> window dominates DeBERTa-v3's 512 cap on the IID slate, but the
> OOD slate skews toward shorter prompts in 3 of 5 slices — a tight
> medium-ablation could clarify whether the ModernBERT win is
> backbone-dominant or context-window-dominant. Two truncation
> strategies (chunk-and-average + head-truncation) are confound
> controls; neither claimed canonical."

The /exploring-options 2026-05-19 6-batch sub-session 9 Q1 locked
the **medium ablation** scope (Option 2 — single fold/seed
training × 2 truncation strategies × full 5-slice OOD eval).
ADR-060 codifies that lock.

**Mid-execution scope-mismatch discovery**: at v1.1.0 Commit 3
prep, the existing training pipeline turned out to be
ModernBERT-specific. `src/training/load_modernbert.py` hardcodes
`MODERNBERT_BASE_HF_ID = "answerdotai/ModernBERT-base"` and is
called directly from `train_modernbert.py`. Generic backbone
support never landed because the project trained on a single
backbone — generic-loader infrastructure was YAGNI until DeBERTa.

The v1.1.0 plan estimated B5 (DeBERTa configs + training fires +
results) at ~2.5h on the assumption that adding a new backbone
was a config-only change. The realistic estimate is ~4-6h
infrastructure + ~$5-7 GPU. The user (2026-05-19 AskUserQuestion)
chose **Path B**: land the methodology + infrastructure scaffold
at v1.1.0; defer execution to v1.1.1.

## Decision

### Methodology lock (binding at v1.1.0; survives the v1.1.1 execution carryforward)

The DeBERTa-v3-base medium ablation locked scope:

- **Backbone**: `microsoft/deberta-v3-base`; pin SHA at v1.1.1
  execution time (loaded via `huggingface_hub.snapshot_download`
  for reproducibility).
- **Training scope**: 1 fold (fold 0), 1 seed (seed 42), 2 epochs
  (matches the ModernBERT recipes per ADR-019). NOT a full LODO
  grid; ablation appendix only.
- **Truncation strategies** (2 reported side-by-side as confound
  controls; neither claimed canonical):
  - **Chunk-and-average**: tokenize the full text; emit 512-token
    windows with stride 256 (50% overlap); per-window forward pass;
    average per-window probabilities to obtain final
    `predicted_proba_class1`. Captures long-context signal at the
    cost of window-edge artifacts.
  - **Head-truncation**: tokenize the full text; take the first
    512 tokens (matches DeBERTa-v3 native window); standard
    forward pass; emit `predicted_proba_class1` directly. Strict
    DeBERTa-v3 native behavior; loses information past token 512.
- **Eval slate**: full 5-slice OOD (BIPIA + InjecAgent +
  JBB-Behaviors + XSTest + NotInject); matches the v1.0.0
  headline OOD slate per ADR-021.
- **Framing**: ablation appendix in `RESULTS.md` §1B; **NOT**
  integrated as a 6th rung in the headline ladder (per §1.10
  literal language).
- **Compute envelope**: 1×L4 or 1×A100; ~30 min wall per training
  fire; ~$5-7 GPU total for the sequential-single-pod 2-fire
  shape (per Q2 lock; budgeted under ADR-020 $125 per-job soft
  cap; current cumulative spend $8.58 → ~$13.58 after v1.1.1).

### Infrastructure (lands at v1.1.0)

- `configs/rungs/deberta_v3_base.yaml` — full hyperparameter recipe.
  Mirrors the ModernBERT rung yamls; adds a `truncation_strategy:`
  field (one of `chunk_and_average` or `head_truncation`).
- `configs/runpod/headline-deberta.yaml` — RunPod orchestration
  config. `lifecycle.on_success: recycle` per Q2 lock (#90
  consumption); `budget.ssh_ready_timeout_sec: 600` per #88
  consumption; image pin matches ModernBERT configs;
  `budget.cost_cap_usd: 25.0` (well under ADR-020 $125 soft cap;
  generous for 2 training fires).
- `Makefile` targets `train-deberta-v3`, `eval-deberta-v3`,
  `deberta-ablation` exist as stubs that exit 2 with a
  "v1.1.1 execution carryforward; see ADR-060" message + pointer
  to this ADR.
- `RESULTS.md` §1B placeholder section with the methodology lock +
  planned scope + "Results pending v1.1.1 GPU fire".
- `WRITEUP/limitations-and-future-work.md` §9.2 documents the
  deferred execution.
- `NEXT_STEPS.md` §1.10 status → "methodology landed at v1.1.0
  (ADR-060); execution v1.1.1".

### v1.1.1 landing condition (when execution lands)

- Loader refactor: `src/training/load_modernbert.py` →
  `src/training/load_backbone.py` (generic; accepts `hf_id` +
  `revision` parameters) OR add parallel
  `src/training/load_deberta.py`. Library-first invariant +
  no-orphaned-code invariant apply.
- Trainer dispatch: `train_modernbert.py` extends to route per
  backbone (rename + refactor if generic-loader path chosen).
- Chunk-and-average inference loop: new module
  `src/inference/windowed.py` implementing the 512-token-window
  stride-256 forward-pass + score-averaging logic.
- Eval pipeline integration: `scripts/run_inference_battery.py` +
  `src/eval/slice_analysis.py` pickup DeBERTa rung outputs.
- 2 RunPod fires via `make deberta-ablation` (sequential
  single-pod 2-fire per Q2 lock); cost preview via
  `make headline-dry-run` BEFORE billing; `validate
  --check-image-registry` (#97 consumption) is default.
- Results land in
  `evals/predictions/deberta_v3_base_{chunk_avg,head_trunc}__fold0__seed42__*.parquet`
  + aggregated `evals/metrics/per_cell_deberta.parquet`.
- `RESULTS.md` §1B placeholder replaced with real numbers
  (chunk-and-average AUPRC/AUROC × 5 slices + head-truncation
  AUPRC/AUROC × 5 slices, side-by-side comparison table).
- `WRITEUP/limitations-and-future-work.md` §9.2 updated with the
  ablation result; long-context-vs-backbone-dominance verdict.
- `evals/cost_ledger.csv` records the 2 fire costs (within
  ADR-020 envelope).
- v1.1.1 tag + GH release + reviewer URL verification.

## Consequences

- **Reviewer experience**: the methodology lock is reviewable
  immediately at v1.1.0 via this ADR + the placeholder RESULTS
  §1B section. A reviewer auditing the §1.10 carryforward sees
  the lock; the deferred execution is honest accounting.
- **No methodology drift**: future v1.1.1 (or later) execution
  must hew to the locked scope. Any deviation requires a new ADR
  (per project anti-pattern: "Mutating a locked decision without
  writing a superseding ADR").
- **Cost certainty**: methodology lock has zero GPU cost; v1.1.0
  is a $0 release. Execution cost is bounded by ADR-020 envelope.
- **SDD discipline preserved**: the spec (this ADR) lands BEFORE
  the implementation (v1.1.1). The implementation is bound to
  the spec, not vice versa. Common SDD anti-pattern (write
  implementation; back-fill ADR) is avoided.
- **Library-first preserved**: the v1.1.1 infrastructure work
  (loader refactor + windowed-inference module) follows the
  library-first invariant. If a primitive belongs upstream
  (`eval_toolkit` or similar), file an upstream issue before
  any local hand-roll.

## Linked ADRs

- **Referenced**: ADR-015 (backbone selection — the original
  ModernBERT-vs-DeBERTa decision); ADR-020 (RunPod cost
  discipline); ADR-050 (rung slate narrowing — full-FT OOD
  dropped; DeBERTa carryforward to v1.1.x); ADR-051 (v1.0.x
  carryforward governance — same Phase-0-to-v1.x carryforward
  pattern); ADR-059 (runpod-deploy v0.8.4 bump that enables
  `lifecycle.on_success: recycle` consumption per Q2 lock).
- **Source**: /exploring-options 2026-05-19 batch 9 Q1
  (methodology lock); /exploring-options 2026-05-19 Q2 lock
  (sequential single-pod execution shape); /exploring-options
  2026-05-19 AskUserQuestion Path B lock (infrastructure-only
  v1.1.0 + execution deferred to v1.1.1).

## Transcript

Decisions surfaced during the 2026-05-19 v1.1.0 planning session
(`/exploring-options` 6-question execution-lock + Path B
scope-mismatch resolution; transcript at
`transcripts/2026-05-19__v1-1-0-runpod-deploy-and-deberta.md`).
