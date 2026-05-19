---
adr_id: "063"
slug: deberta-ablation-v1-1-2-execution-and-slot-shift
title: DeBERTa-v3-base medium ablation execution (v1.1.2 carryforward; narrow renaming-only supersession of ADR-060 "v1.1.1" body references) — null result, backbone-dominant interpretation
date: 2026-05-19
status: Accepted
claim_id: CLAIM-063
claim: >-
  ADR-060 (2026-05-19) landed the DeBERTa-v3-base medium ablation
  methodology lock at v1.1.0 with body text *"execution deferred to
  v1.1.1"*. That naming did not survive the same calendar day — the
  v1.1.1 slot was consumed by ADR-061 (Quarto site navigation
  restructure; user-feedback discoverability fix) before the DeBERTa
  execution could begin. DeBERTa execution carried forward to v1.1.2
  per the v1.1.2-handoff doc, with the ADR-060 body text left
  immutable per the project's `no-amend / no-squash` ADR-discipline.
  This ADR codifies the carryforward as a narrow renaming-only
  supersession of ADR-060's "v1.1.1" body references; the
  methodology lock itself (single fold/seed, 2 truncation strategies,
  5-slice OOD eval, ablation-appendix framing, ~$5-7 GPU envelope)
  is unchanged.
  v1.1.2 execution shipped both training fires on a single warm
  A100-SXM4-80GB pod via `lifecycle.on_success: recycle`
  (chunk_and_average -> recycle -> head_truncation -> explicit
  `runpod-deploy stop`). The 2-strategy ablation produced essentially
  identical per-slice metrics (pooled OOD AUPRC 0.2912 vs 0.2895;
  jbb_behaviors AUPRC 0.4855 vs 0.4890; xstest AUPRC 0.3966 vs
  0.3912) — a publishable null result. By the ADR-060 confound-
  control interpretation, this indicates the ModernBERT advantage
  on the headline ladder is BACKBONE-DOMINANT, not context-window-
  dominant. Actual GPU spend: $1.34 (well under the $5-7 expected
  envelope; well under the ADR-020 $125 per-job soft cap and $200
  cumulative hard cap).
source: transcripts/2026-05-19__v1-1-2-deberta-execution.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.1.2 close: `evals/metrics/per_cell_deberta.parquet` exists
  with at least the 6 binary-class slice rows (2 strategies x
  {jbb_behaviors, xstest, pooled_ood}; single-class slices bipia +
  injecagent + notinject + iid correctly skipped per ADR-006
  single-class-slice handling). `evals/cost_ledger.csv` carries the
  9 `pid-deberta-2026051*` rows totaling $1.34. `NEXT_STEPS.md`
  §1.10 has a Status (v1.1.2) paragraph capturing the headline +
  null-result interpretation. `CHANGELOG.md` [1.1.2] block exists
  with the headline-result table. `src/inference/windowed.py` +
  `src/training/load_backbone.py` + `scripts/run_deberta_ood_inference.py`
  all committed. `configs/rungs/deberta_v3_base.yaml` carries the
  pinned `revision: 8ccc9b6f36199bec6961081d44eb72fb3f7353f3` +
  `bf16: false` (DeBERTa numerical-stability fix). RESULTS §1B +
  WRITEUP §9.2 + library_imports.md inventory updates defer to a
  follow-up patch after the in-flight ADR-062 doc-rewrite commit
  stabilises (audit-clean separation per project no-conflated-
  scopes discipline). SUBMISSION_AUDIT.md regenerates with at
  least 63 CLAIM rows (ADRs 001 through 063).
closing_commit: v1.1.2
supersedes: []  # narrow renaming-only; see ADR-060 superseded_by
superseded_by: []
references:
  - decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md
  - decisions/ADR-061-quarto-site-navigation-restructure.md
  - decisions/ADR-006-single-seed-protocol-for-comparative-claims.md
  - decisions/ADR-019-modernbert-training-recipe.md
  - decisions/ADR-020-runpod-orchestration-and-cost-discipline.md
  - decisions/ADR-059-runpod-deploy-pypi-install-narrow-supersession-of-adr-036.md
  - NEXT_STEPS.md  # §1.10 Status (v1.1.2)
  - CHANGELOG.md  # [1.1.2]
  - evals/metrics/per_cell_deberta.parquet
  - evals/cost_ledger.csv
transcript: transcripts/2026-05-19__v1-1-2-deberta-execution.md
---

# ADR-063 — DeBERTa-v3-base ablation v1.1.2 execution + slot-shift

## Status

Accepted (2026-05-19; narrow renaming-only carryforward of ADR-060
v1.1.1 -> v1.1.2 + capture of the executed ablation result).

## Context

[ADR-060](./ADR-060-deberta-v3-base-long-context-ablation-methodology.md)
landed the DeBERTa-v3-base medium ablation methodology lock at v1.1.0
with body text "execution deferred to v1.1.1". The execution did not
happen at v1.1.1 because that release-tag slot was consumed by
[ADR-061](./ADR-061-quarto-site-navigation-restructure.md) (a
user-feedback-driven Quarto site navigation restructure that took
priority on calendar-day 2026-05-19).

The v1.1.2 handoff doc at
`/home/brandon_behring/.claude/plans/v1-1-2-deberta-execution-handoff.md`
sequenced the execution as Phase A (generic loader refactor) -> Phase B
(windowed-inference module) -> Phase C (training dispatch + Makefile)
-> Phase D (GPU fires) -> Phase E (governance close) -> Phase F
(transcript). The full v1.1.2 session executed Phases A-D end-to-end
on 2026-05-19 and partial Phase E (this ADR + NEXT_STEPS + CHANGELOG;
the wider RESULTS/WRITEUP/library_imports updates defer per the
no-conflated-scopes discipline because the in-flight doc agent
working on ADR-062 holds unstaged edits on those same files).

## Decision

### Narrow renaming-only supersession of ADR-060 body references

ADR-060 is immutable per project ADR-discipline. The body's "v1.1.1
execution" wording is treated as a placeholder that was assigned
without knowing the v1.1.1 slot would be needed for ADR-061. The
DeBERTa execution carries forward to v1.1.2; commit messages document
the shift. ADR-060's methodology lock (single fold/seed; 2 truncation
strategies; 5-slice OOD eval; ablation-appendix framing; ~$5-7 GPU
envelope) is BINDING regardless of release-slot. No methodology
content is changed by this carryforward.

### v1.1.2 Phase A–D execution outcome

**Phase A** (commit `a34128b`): refactored
`src/training/load_modernbert.py` to `src/training/load_backbone.py`
with a generic `hf_id` kwarg so the same flash-attn-fallback recipe
(per ADR-020) serves both ModernBERT (ADR-019) and DeBERTa-v3-base
(ADR-060). Per the no-orphans invariant, the old loader was deleted
in the same commit; 6 call sites + 3 test files updated.

**Phase B** (commit `9ecf0e3`): added `src/inference/windowed.py`
implementing chunk-and-average + head-truncation truncation
strategies via HF tokenizer's native sliding-window protocol
(`return_overflowing_tokens=True` + `stride`); 15 mocked-only smoke
tests at `tests/smoke/test_windowed_inference_smoke.py`. Reuses
`src.training.softmax_cast.softmax_fp32` for ADR-019 numerical
stability.

**Phase C** (commit `2ed8e04`): pinned DeBERTa-v3-base revision SHA
`8ccc9b6f36199bec6961081d44eb72fb3f7353f3` via
`huggingface_hub.HfApi.model_info`; wired training_strategy dispatch
into `train_modernbert.py` (prepare_model + _write_predictions_parquet
+ PerEpochPredictionsCallback + train_one_cell); added
`VALID_RUNG_NAMES` + `VALID_TRUNCATION_STRATEGIES` constants; extended
`train_rung.py` with `--truncation-strategy` CLI override + DeBERTa
rung dispatch; added `--epoch-filter` to `run_metrics_battery.py`;
wired 3 Makefile targets (`train-deberta-v3` / `eval-deberta-v3` /
`deberta-ablation`).

**Phase D** (commits `3791c1a` through `898fae5`; 8 commits total
across the fix-cycle + the closing feat commit): fired both
strategies on a single warm A100-SXM4-80GB pod (US-MD-1) via
`lifecycle.on_success: recycle`. Pre-flight surfaced 7 distinct
infrastructure errors before the training succeeded end-to-end:

1. `83fd348` — added `sentencepiece` Python dep (DeBERTa-v3 tokenizer
   needs the SentencePiece backend).
2. `99501ba` — narrowed `headline-deberta.yaml` staging excludes
   (later subsumed by `33387b5`; kept for audit-trail completeness).
3. `33387b5` — **load-bearing FUSE fix** — moved `/workspace`
   (FUSE/MooseFS) -> `/root` (container overlay disk; POSIX
   semantics work) for project code + HF cache + secrets + run
   scripts + logs. Re-extends the X8 venv-on-/root workaround
   (per `fuse-workspace-needs-uv-link-mode-copy` memory) to all
   writable paths; without this the rsync push fails with
   `Input/output error (5)` on `/workspace`.
4. `f660f76` — added `protobuf` Python dep (transformers'
   `SentencePieceExtractor.__init__` calls
   `requires_backends(self, "protobuf")` independently from the
   sentencepiece package).
5. `60fdc53` — bound `truncation_strategy` in
   `checkpoint_dir_template.format()` (the Phase C2 dispatch wiring
   missed this specific format site).
6. `aa91067` — **load-bearing numerical-stability fix** — DeBERTa-v3
   + bf16 produces `loss=0` + `grad_norm=NaN` from training step 1
   (disentangled attention overflows bf16 mantissa). Made
   `build_training_args` + `load_backbone` accept YAML-driven
   `bf16`/`fp16`/`learning_rate`/`num_train_epochs` overrides;
   switched DeBERTa to fp32. Locally validated forward+backward
   before re-firing (`loss=0.7268` + 202/202 finite gradients on
   fp32 vs `loss=NaN` + 0/202 finite on bf16).
7. `67679a5` — fixed checkpoint path doubling (deberta_v3_base.yaml
   `checkpoint_dir_template` prefix conflicted with
   `train_rung.py --checkpoint-root` default); dropped the FUSE
   staging-bounce (`--checkpoint-staging-root /root/training_staging`
   is unnecessary since we're already on /root overlay disk).

The 8th commit (`898fae5`) closed Phase D with both training fires
complete, 4 training-time predictions parquets, 10 OOD-inference
predictions parquets (via the new
`scripts/run_deberta_ood_inference.py` standalone OOD orchestrator,
designed as a narrow companion to `scripts/run_inference_battery.py`
since the DeBERTa checkpoint path has an extra strategy-nesting
level), and the 6-row `evals/metrics/per_cell_deberta.parquet`.

### Headline result (publishable null)

| strategy | jbb_behaviors AUPRC | xstest AUPRC | pooled_ood AUPRC |
|---|---:|---:|---:|
| `chunk_and_average` | 0.4855 | 0.3966 | 0.2912 |
| `head_truncation`   | 0.4890 | 0.3912 | 0.2895 |

Single-class slices (bipia, injecagent, notinject all-positive; iid
all-negative for the LODO held-out source) correctly skip per ADR-006
single-class-slice handling (AUROC undefined -> pydantic validation
nan-guard).

The 2 truncation strategies produce essentially identical per-slice
metrics. By the ADR-060 confound-control interpretation: **the
ModernBERT advantage on the headline ladder is BACKBONE-DOMINANT,
not context-window-dominant**. Long-context (chunk-and-average)
provides no measurable benefit over head-truncation on this 5-slice
OOD slate. The interpretive caveat goes in the RESULTS §1B +
WRITEUP/limitations-and-future-work.md §9.2 follow-up patch.

### Cost reconciliation

Actual GPU spend across the 9 Phase D pod manifests (7 short
failures averaging ~$0.05-0.20 each + 2 successful ~6-min training
fires at ~$0.18 each): **$1.34**, well under the ADR-060 $5-7
expected envelope. Cumulative project spend: $9.92 / ADR-020 $200
hard cap.

## Consequences

- **ADR-060 immutability preserved**: this narrow renaming-only
  supersession captures the release-slot shift without rewriting
  ADR-060's body text. Future readers cross-reference
  ADR-060 -> ADR-063 to understand why "v1.1.1 execution" actually
  landed at v1.1.2.

- **Methodology lock honored**: the executed ablation matches every
  ADR-060 constraint (microsoft/deberta-v3-base; fold 0; seed 42; 2
  epochs; 2 truncation strategies; full 5-slice OOD; ablation
  appendix; not a 6th rung). No methodology drift.

- **Publishable null result**: the per-strategy headline directly
  resolves the long-context-vs-backbone-dominance question that
  motivated NEXT_STEPS §1.10 and the v1.1.x carryforward. The
  ModernBERT-vs-DeBERTa headline-ladder gap (per RESULTS §1) is
  attributed to backbone architecture, not context window. The
  reviewer can now read the ablation appendix in RESULTS §1B and
  conclude: "ModernBERT's 8192-token window did not help on this
  slate; the win is backbone-architectural."

- **Deferred Phase E artifacts**: RESULTS §1B + WRITEUP §9.2 +
  library_imports.md inventory entries + SUBMISSION_AUDIT
  regeneration defer to a follow-up patch after the in-flight
  doc agent's ADR-062 commit stabilises. The deferral is documented
  here + in `898fae5` + `61a09c9` commit messages so the audit trail
  is complete even before the doc artifacts land.

- **Library-first preserved**: `src/inference/windowed.py` uses HF
  tokenizer's native sliding-window protocol; no hand-rolled
  window-stride arithmetic. Reuses `softmax_cast.softmax_fp32`
  (ADR-019 numerical stability). The chunk-and-average pattern is
  project-internal infrastructure (specific to the
  ModernBERT-vs-DeBERTa-v3 confound control), not a generic
  eval-toolkit primitive; no upstream MR filed.

- **No methodology drift**: the bf16 -> fp32 switch was a numerical-
  stability fix (DeBERTa-v3 + bf16 produces NaN gradients), not a
  methodology change. ADR-060 did not constrain the precision; the
  fp32 choice was made via the YAML's `training.bf16: false` flag,
  with `build_training_args` honoring the override per a backward-
  compatible plumbing change that preserves ADR-019 ModernBERT bf16
  default.

## Linked ADRs

- **Referenced**:
  - [ADR-060](./ADR-060-deberta-v3-base-long-context-ablation-methodology.md)
    — methodology lock; this ADR carries forward its execution
    landing condition to v1.1.2 (narrow renaming-only).
  - [ADR-061](./ADR-061-quarto-site-navigation-restructure.md) —
    consumed the v1.1.1 slot that ADR-060 had body-text-named for
    DeBERTa execution.
  - [ADR-006](./ADR-006-single-seed-protocol-for-comparative-claims.md)
    — single-class slice handling (AUROC nan-guard).
  - [ADR-019](./ADR-019-modernbert-training-recipe.md) — bf16 +
    lr=1e-4 default; this ADR's `build_training_args` plumbing
    change preserves ADR-019 ModernBERT defaults while allowing
    DeBERTa fp32 overrides via YAML.
  - [ADR-020](./ADR-020-runpod-orchestration-and-cost-discipline.md)
    — cost envelope ($25 per-job soft cap honored; $1.34 actual).
  - [ADR-059](./ADR-059-runpod-deploy-pypi-install-narrow-supersession-of-adr-036.md)
    — runpod-deploy v0.8.4 lifecycle.on_success: recycle (the
    warm-pod 2-fire shape this ADR consumed).

- **Source**: v1.1.2 execution session per
  `transcripts/2026-05-19__v1-1-2-deberta-execution.md` (private;
  emailed at submission).

## Transcript

`transcripts/2026-05-19__v1-1-2-deberta-execution.md` — captures the
full A-D sub-phase walkthrough including the 7-commit fix-cycle
diagnosis + the load-bearing FUSE + fp32 fixes.
