# Hyperparameter disclosure

Reviewers may suspect cherry-picking. This document is the anti-cherry-pick
defense: every hyperparameter value is **locked before training begins**
(per `SPEC_GREENFIELD.md` §2 locked-process rule + ADR-019), and every
non-default choice carries either a locking ADR or a literature-inheritance
source. No val-set gridsearch ran during this submission.

The four sections below cover: the locked recipe (§1), what was *actually*
swept (§2), what was deliberately *not* swept (§3), and budget-dependence
caveats (§4).

## 1. Seed recipe (locked values)

All values are read at runtime from `configs/rungs/*.yaml`; mismatches
between code defaults and YAML fail loud per ADR-026.

### 1.1 Cross-rung training recipe (shared by frozen-probe + LoRA + full-FT)

Per ADR-019 — uniform across the 3 transformer rungs so that rung-vs-rung
comparisons isolate capacity, not optimisation.

| Knob | Setting | Source / Rationale | ADR |
|---|---|---|---|
| Backbone | `answerdotai/ModernBERT-base` rev `8949b909ec900327062f0ebf497f51aef5e6f0c8` | Single-backbone lock; SHA pinned per SDD reproducibility | ADR-015 |
| Learning rate | `1.0e-4` | Literature default for ModernBERT classification fine-tuning | ADR-019 |
| LR scheduler | `cosine` | Smooth decay; literature default | ADR-019 |
| Warmup ratio | `0.10` | 10 % linear warmup; literature default | ADR-019 |
| Epochs | `2` | Locked at minimum-budget within ADR-020 cost envelope | ADR-019 |
| Precision | `bf16` | A100/H100-friendly; matches ModernBERT training | ADR-019 |
| Max grad norm | `1.0` | Standard gradient clipping | ADR-019 |
| Weight decay | `0.01` | AdamW default | ADR-019 |
| Effective batch | `32` (per_device × grad_accum) | Cost-bounded; held constant across rungs | ADR-020 BATCH_TABLE |
| Class weighting | `balanced` (sklearn) | Per-fold recomputed to neutralise LODO imbalance | ADR-019 |
| Save strategy | `epoch` | Per-epoch checkpoint for prediction audit | ADR-019 |
| Eval strategy during training | `no` | Eval is downstream of train per ADR-013 | ADR-013 |
| Tokenizer max_length | `8192` | ModernBERT native context; head-truncation when exceeded | ADR-014 Q3+Q4 |
| Tokenizer pad_to_multiple_of | `8` | Tensor-core alignment | ADR-014 Q4 |
| Seeds | `[42, 43, 44]` | 3-seed slate per ADR-044 Q1 partial supersession of ADR-019 line 99 | ADR-044 |

### 1.2 Frozen-probe specifics

Frozen backbone + trainable linear head over the `[CLS]` token. No
rung-specific hyperparameters beyond the shared training recipe.

| Knob | Setting | Source / Rationale | ADR |
|---|---|---|---|
| Classifier head | linear (`hidden_size → 2`) | sklearn-equivalent; locked architecture | ADR-017 |
| Backbone gradient | frozen | Defines the "frozen-probe" rung | ADR-017 |

### 1.3 LoRA specifics

LoRA adapters on the 4 ModernBERT attention/MLP linear modules per
encoder layer × 22 encoder layers = 88 adapter modules. Trainable
parameter ratio approximately 0.5 % to 1 % of total per ADR-019.

| Knob | Setting | Source / Rationale | ADR |
|---|---|---|---|
| `r` (LoRA rank) | `8` | Literature default for BERT-class models; not searched | ADR-019 |
| `alpha` | `16` | Standard `2 × r` convention | ADR-019 |
| `dropout` | `0.1` | LoRA paper default | ADR-019 |
| `target_modules` | `[Wqkv, attn.Wo, mlp.Wo, mlp.Wi]` | ModernBERT attention/MLP linear modules | ADR-019 |
| `modules_to_save` | `[classifier]` | Head trained alongside adapters | ADR-019 |
| `task_type` | `SEQ_CLS` | PEFT sequence-classification task spec | ADR-019 |
| `bias` | `none` | LoRA paper default | ADR-019 |

### 1.4 Full-FT specifics

All ModernBERT parameters trainable. No rung-specific hyperparameters
beyond the shared training recipe + one storage-discipline relaxation.

| Knob | Setting | Source / Rationale | ADR |
|---|---|---|---|
| `cleanup_intermediate_checkpoints` | `false` (relaxed at X11 2026-05-17) | Phase 5 X11 re-fire needs persisted checkpoints for OOD inference; relaxation is storage-not-methodology | not a methodology lock |

### 1.5 Classical floor (`tfidf-lr`)

| Knob | Setting | Source / Rationale | ADR |
|---|---|---|---|
| Word n-gram | `1..2` | Standard bigram TF-IDF | ADR-017 |
| Word max features | `15000` | Bounded vocab | ADR-017 |
| Char n-gram | `3..5` | Subword robustness against tokenisation artifacts | ADR-017 |
| Char max features | `15000` | Bounded vocab | ADR-017 |
| `sublinear_tf` | `true` | Log-scaled term frequency | ADR-017 |
| LR solver | `liblinear` | sklearn small-dataset default | ADR-017 |
| LR `C` | `1.0` | sklearn default; not searched | ADR-017 |
| LR `class_weight` | `balanced` | Cross-rung uniform per ADR-019 | ADR-017 + ADR-019 |
| LR `max_iter` | `1000` | Fit-to-convergence; no epoch concept | ADR-017 |

## 2. Exploration trajectory — what was actually swept

**Hyperparameter sweep ran during this submission**: **none**.

Per the locked-process rule, hyperparameters were finalised at ADR-019
(Phase 0-04 close, 2026-05-15) before any training began. The values
above were inherited from the ModernBERT classification literature +
sklearn defaults; no val-set gridsearch executed.

**What *was* swept** (operating-point sweeps and stability checks, not
hyperparameter tuning):

- **Recall@FPR pinpoints** at FPR ∈ {0.1 %, 1 %, 5 %} per ADR-046. Reported
  per-cell in `evals/metrics/per_cell.parquet`. This is a *reporting*
  sweep, not a tuning sweep — same trained model, multiple thresholds.
- **Dual-policy threshold characterisation** (Detection FPR ≤ 1 %;
  Verification recall ≥ 99 %) per ADR-025 — also a reporting sweep over
  val-fit thresholds, not a training sweep.
- **Bootstrap seed stability check** at `seed=2` (Phase 7 commit `26776dc`)
  — 0 of 40 cells flagged at 5 % CI-halfwidth threshold. Captured at
  `evals/bootstrap/paired_cells_seed2.parquet`. This is a bootstrap-stability
  check, not a model retraining sweep.
- **Per-fold variance characterisation** — 4 LODO folds × 3 training
  seeds (42, 43, 44) = 12 cells per (rung, slice, metric) per ADR-019.
  Variance is reported, not tuned against.

## 3. Axes held constant (intentional)

What was *deliberately* not searched, with rationale:

- **Backbone choice** — single-backbone lock at `answerdotai/ModernBERT-base`
  per ADR-015. Rationale: the rung-vs-rung comparison isolates *capability
  level* (frozen-probe vs LoRA vs full-FT) over a fixed backbone, not
  backbone choice itself. Multi-backbone comparison is out of scope per
  ADR-015 + WRITEUP §8.
- **Learning rate** — `1.0e-4` literature default for BERT-class
  classification, held constant cross-rung. Rationale: per-rung LR
  tuning would change the rung-vs-rung interpretation from "what does
  this capacity layer add" to "what does this capacity layer + its
  optimal LR add"; the latter is a different methodological contract.
- **LR schedule + warmup ratio** — cosine + 0.10 warmup; literature default.
  Same rationale as LR.
- **Epoch count** — 2 epochs. Bounded by ADR-020 cost envelope; per ADR-019
  the choice is "minimum-budget epoch count that achieves stable
  per-epoch parquet emission". Higher-epoch sensitivity deferred to
  NEXT_STEPS §1.3.
- **Effective batch size** — 32. Bounded by single A100 80GB capacity
  for the longest tokenisation window (8192 tokens) under bf16.
- **LoRA `r` and `alpha`** — `r=8`, `alpha=16` literature defaults; not
  searched. Rationale: `r` search would multiply LoRA-rung training cost
  by 3-5× (small / medium / large rank) without a methodology contract
  reason — the rung label is "LoRA at literature-default rank", not
  "LoRA at its capacity-optimal rank".
- **LoRA `target_modules`** — locked at `[Wqkv, attn.Wo, mlp.Wo, mlp.Wi]`
  per the ModernBERT-base attention + MLP linear-module set. Rationale:
  alternate target sets (`Wqkv` only; `mlp.*` only; etc.) would tilt
  the rung-vs-rung gap by changing what's adapted; literature default
  is "all linear modules in attention and MLP".
- **Tokenizer max_length** — 8192 (ModernBERT native context). Truncating
  to a shorter window would distort row-level signal for the long-context
  prompt-injection corpus per ADR-014 Q4.
- **TF-IDF `C`** — sklearn default 1.0 for the classical floor. Rationale:
  classical floor is a *diagnostic anchor* (per ADR-017 dual role), not
  a tuned-baseline; tuning would shift its interpretation.
- **Optimizer** — AdamW (HF Trainer default) cross-rung. Not searched.

## 4. Caveats

- **Budget dependence**: the 3-seed × 4-fold = 12-cell-per-rung sample size
  is the minimum justifiable for the Bayle 2020 `cv_clt_ci` headline CI
  machinery per ADR-024. Higher seed counts (e.g., 5-seed or 10-seed)
  would narrow CIs and could move some LoRA-vs-full-FT gap claims from
  "CI clears zero" to "CI does not clear zero" or vice versa. The
  bootstrap-seed stability check at `seed=2` (§2) tests this within the
  bootstrap layer; it does *not* test cross-seed variance at the training
  layer.
- **Hyperparameter inheritance vs project-locked**: the recipe is inherited
  from ModernBERT literature + sklearn defaults, *not* tuned for this
  injection-detection task. A future iteration could justify a small
  per-rung LR sweep at a higher compute budget if the case-study
  contract is replaced by a deployment-orientated contract.
- **Storage-discipline relaxation at X11**: full-FT
  `cleanup_intermediate_checkpoints` flipped from `true` to `false` mid-
  Phase-5 to enable OOD inference from persisted weights. This is *not*
  a methodology lock per the inline comment in `configs/rungs/full_ft.yaml`
  — the cleanup was a storage convenience, not an audit-relevant
  artifact. Relaxing it does not change any prediction parquet or
  metric value.
- **No val-set gridsearch**: this submission deliberately *cannot* point
  to a tuning sweep that justifies a specific hyperparameter value as
  "optimal for this task". The audit story is "locked from literature
  before training; no tuning happened" — which is the anti-cherry-pick
  position by design.

## Audit hook

Every claim in `WRITEUP.md` that depends on a hyperparameter choice
cross-references this file. The pairing makes the anti-cherry-pick story
auditable: a reviewer can match each result row to its disclosed setting
+ verify against `configs/rungs/<rung>.yaml` at commit `v1.0.0`.

**Linked ADRs**: ADR-013 (eval downstream of train), ADR-014 (tokenizer
locks), ADR-015 (single-backbone lock), ADR-017 (rung-slate + classical-
floor), ADR-019 (transformer training recipe), ADR-020 (cost envelope +
batch table), ADR-024 (cross-fold CI machinery), ADR-026 (config-hash
discipline), ADR-044 (seed-slate partial supersession of ADR-019).
