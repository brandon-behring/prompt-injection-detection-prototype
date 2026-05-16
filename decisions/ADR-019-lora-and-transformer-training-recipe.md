---
adr_id: 019
slug: lora-and-transformer-training-recipe
title: LoRA and transformer-rung training recipe — hyperparameters, epochs, precision, class weighting
date: 2026-05-15
status: Accepted
claim_id: CLAIM-019
claim: Phase 0-03 locks the complete training recipe for the three trained transformer rungs (ModernBERT-base across frozen-probe, LoRA, full-FT) as a single hyperparameter-immutability-compatible bundle. LoRA core hyperparameters use literature defaults from the LoRA paper and modern HF PEFT recipes — r equals 8 plus lora_alpha equals 16 (alpha equals 2r modern convention) plus lora_dropout equals 0.1 plus task_type SEQ_CLS plus bias none — with explicit deterministic target_modules enumeration listing four suffixes (Wqkv, attn.Wo, mlp.Wo, mlp.Wi) covering the fused QKV projection plus attention output projection plus both MLP projections per ModernBERT encoder layer (avoids dependency on PEFT all-linear auto-detection per SDD discipline). LoRA modules_to_save includes the classifier head (randomly-initialized; needs full fine-tuning alongside the LoRA adapters). Optimizer settings shared across the three transformer rungs — learning_rate equals 1e-4 plus warmup_ratio equals 0.10 plus lr_scheduler_type cosine plus per_device_train_batch_size equals 16 plus gradient_accumulation_steps equals 2 (effective batch 32 on H100 plus 80GB-VRAM equivalent classes; per ADR-020 the BATCH_TABLE scales per_device plus grad_accum on smaller GPU classes preserving effective batch 32) plus max_grad_norm equals 1.0 plus weight_decay equals 0.01 plus AdamW optimizer (HF Trainer default) plus DataCollatorWithPadding with max_length equals 8192 plus dynamic padding plus head-truncation when exceeded (per ADR-014 Q4 training-time policy). Epoch policy (ledger row 335) is locked at 2 epochs uniformly across all three transformer rungs (SPEC §2 default sweet spot; cross-rung uniformity eliminates the epoch-count confound when attributing lift between rungs) with per-epoch inference predictions persisted for every (rung, seed, fold) combination (epoch-2 is the headline number; epoch-1 is reported as a diagnostic ablation in the methodology spoke) — this converts SPEC §2 line 132 default suggestion of a 1-epoch-control on at-least-one-fold into a per-fold per-seed 1-epoch diagnostic at near-zero added cost. Intermediate full-FT weight checkpoints are not persisted to disk (approximately 150 megabytes per checkpoint times 12 training runs equals approximately 1.8 gigabytes of throwaway weights) — per-row inference predictions for epoch-1 are saved without persisting the underlying full-FT weights since predictions are the audit-relevant artifact for downstream analyses. LoRA plus frozen-probe intermediate adapter and head checkpoints are persisted (tiny; under 10 megabytes each). Precision policy (ledger row 336) is locked at bf16 for both training and inference with explicit fp32 cast before the final softmax or sigmoid (per SPEC §2 default; matches H100 native tensor-core throughput plus same dynamic range as fp32 avoiding gradient underflow concerns; ModernBERT was pretrained and tested with bf16 per Warner et al. 2024). Class-weight implementation (ledger row 337) is locked at sklearn-style class_weight balanced uniformly across all four trained rungs (TF-IDF+LR per ADR-017 Q1b lock plus the three transformer rungs via a WeightedTrainer subclass that overrides compute_loss with CrossEntropyLoss using a per-fold-recomputed compute_class_weight tensor) — uniform convention across the trained-rung slate enables clean cross-rung lift attribution and aligns with the sklearn convention already established by ADR-017 for the classical-floor rung. TrainingArguments configuration locks save_strategy equals epoch (saves per-epoch checkpoint for LoRA plus frozen-probe; full-FT intermediate checkpoints are deleted post-inference per the storage-management discipline above) plus eval_strategy equals no (no val-set-driven evaluation during training per SPEC §2 hyperparameter-immutability) plus seed slot iterated across the ADR-006 three-seed slate (42, 1337, 2025). Phase 1 verification task — after uv-resolving PEFT plus Transformers pinned versions, instantiate LoraConfig plus AutoModelForSequenceClassification.from_pretrained for answerdotai/ModernBERT-base wrapped with get_peft_model plus dump the resolved trainable parameter enumeration plus target module list to evals/lora_target_modules.json (asserts four LoRA layers per ModernBERT encoder block times 22 layers equals 88 LoRA adapter modules; classifier head is in modules_to_save; trainable parameter ratio approximately 0.5 to 1 percent of total).
source: SPEC_GREENFIELD.md §2 Model ledger rows 335 + 336 + 337 + Phase 0-03 walk Q4 + Q5 + Q6 + Q7
acceptance_criterion: SPEC_GREENFIELD ledger row 335 carries locked-to-2-epochs-uniform-with-per-epoch-prediction-save (see ADR-019) status; ledger row 336 carries locked-to-bf16-training-plus-inference-with-fp32-softmax-cast (see ADR-019) status; ledger row 337 carries locked-to-sklearn-style-class-weight-balanced-uniform-across-trained-rungs (see ADR-019) status; SPEC_SHEET §4.2 through §4.4 transformer-rung subsections are populated with the locked recipe (LoRA core hyperparameters plus epoch policy plus precision plus class-weight); SPEC_SHEET §4 contains a Per-epoch prediction-save discipline subsection noting epoch-2 is headline plus epoch-1 is diagnostic; assumptions.md A-003 (pre-teardown persistence checklist per ADR-013) is extended in spirit to require per-epoch parquet predictions persisting before any pod teardown; tests/test_invariants.py contains skip-marked stub test_per_epoch_predictions_present asserting predictions exist for both epoch=1 and epoch=2 for every transformer (rung, seed, fold) combination per the 96-file enumeration; src/training/lora_config.py contains the locked LoraConfig instantiation matching the recipe; src/training/weighted_trainer.py contains the WeightedTrainer subclass with per-fold compute_class_weight; evals/lora_target_modules.json is the Phase 1 deliverable that captures the actual resolved LoRA target module enumeration plus trainable parameter count from the pinned PEFT and Transformers versions; src/inference/softmax_cast.py contains the fp32-cast-before-softmax helper.
closing_commit:
supersedes:
references:
  - https://arxiv.org/abs/2106.09685
  - https://arxiv.org/abs/2006.04884
  - https://arxiv.org/abs/2412.13663
  - https://arxiv.org/abs/1905.12322
  - https://huggingface.co/docs/peft/main/en/conceptual_guides/lora
  - https://huggingface.co/docs/peft/main/en/developer_guides/lora
  - https://huggingface.co/docs/peft/main/en/task_guides/seq_classification_lora
  - https://github.com/huggingface/peft/blob/main/examples/sequence_classification/LoRA.ipynb
  - https://huggingface.co/docs/transformers/en/perf_train_gpu_one
  - https://huggingface.co/docs/transformers/model_doc/modernbert
  - https://github.com/huggingface/transformers/blob/main/src/transformers/models/modernbert/modeling_modernbert.py
  - https://huggingface.co/answerdotai/ModernBERT-base
  - https://www.philschmid.de/fine-tune-modern-bert-in-2025
  - https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms
  - https://scikit-learn.org/stable/modules/generated/sklearn.utils.class_weight.compute_class_weight.html
  - https://gking.harvard.edu/files/0s.pdf
  - https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
  - https://resources.nvidia.com/en-us-tensor-core/nvidia-tensor-core-gpu-datasheet
  - decisions/ADR-015-rung-architecture-refinement.md
  - decisions/ADR-014-threat-model-bundle.md
  - decisions/ADR-006-statistical-multi-seed-protocol.md
  - decisions/ADR-017-trained-rung-slate-expansion.md
transcript: transcripts/2026-05-15__phase-0-03__model-scope.md
---

# ADR-019: LoRA and transformer-rung training recipe

## Status

Accepted (2026-05-15). Complements ADR-015 (trained-rung architecture) and ADR-017 (rung-slate expansion). Does not supersede any prior ADR; specifies the deferred hyperparameter bundle that ADR-007 line 42 and ADR-015 line 44 both flagged as Phase 0-03 deliverables.

## Context

ADR-007 and ADR-015 both deferred the specific LoRA hyperparameters (r, alpha, dropout, target_modules, lr, epochs, precision, batch, max_len, warmup) to Phase 0-03 with the comment that the discipline rule from SPEC §2 (lock hyperparameters per rung before training; no val-set gridsearch) requires committing to literature defaults rather than tuning.

Phase 0-03 Q4 through Q7 walk fully specified the recipe. The walk surfaced one SDD-discipline refinement that exceeded SPEC §2's documented default — Q4 verification of PEFT plus ModernBERT compatibility surfaced that the modern recipe convention target_modules equals all-linear is an auto-detection convention that creates a silent dependency on PEFT version-specific behavior; the SDD-aligned move is explicit module enumeration listing the four suffixes that match ModernBERT's fused QKV plus attention output plus both MLP projections, removing the auto-detection dependency.

Q5 surfaced an opportunity to upgrade SPEC §2's default 1-epoch-control on at-least-one-fold suggestion into a per-fold per-seed 1-epoch diagnostic at near-zero added cost by saving per-epoch inference predictions throughout the 2-epoch training run. This converts a single-fold sanity check into a slate-wide diagnostic without adding any training compute and without violating hyperparameter-immutability (the headline number remains epoch-2 predictions; epoch-1 predictions are reported as a diagnostic ablation in the methodology spoke).

Q6 confirmed the SPEC §2 default for bf16; no contested ground.

Q7 surfaced a cross-rung-consistency point — the TF-IDF+LR rung from ADR-017 uses sklearn class_weight equals balanced; locking the transformer-rung class-weight implementation to the same sklearn-style formula gives the four trained rungs a uniform weighting convention. This is auditable and aligns with the sklearn convention already established by ADR-017.

Q4 specified per_device_train_batch_size equals 16 and gradient_accumulation_steps equals 2 (effective batch 32) for H100 80GB. The follow-up Q8 walk surfaced that runpod-deploy's GPU-failover ladder may land us on smaller GPU classes (A100 40GB, L40S, L40); ADR-020 addresses this by specifying a per-GPU-class BATCH_TABLE that preserves effective batch 32 by scaling per_device plus grad_accum together. The recipe locked by this ADR is the H100 default; ADR-020 documents the GPU-class-adaptive batch sizing.

## Decision

### Locked LoRA configuration

```python
from peft import LoraConfig

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.1,
    target_modules=["Wqkv", "attn.Wo", "mlp.Wo", "mlp.Wi"],
    modules_to_save=["classifier"],
    task_type="SEQ_CLS",
    bias="none",
)
```

- Explicit target_modules enumeration (not "all-linear" auto-detection) — SDD discipline; deterministic; stable across PEFT version updates
- modules_to_save includes the classifier head for full fine-tuning alongside the LoRA adapters
- Per-encoder-layer count: 4 LoRA modules (Wqkv plus attn.Wo plus mlp.Wi plus mlp.Wo); 22 encoder layers in ModernBERT-base equals 88 LoRA adapter modules total

### Locked TrainingArguments (shared across all three transformer rungs)

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    learning_rate=1e-4,
    warmup_ratio=0.10,
    lr_scheduler_type="cosine",
    per_device_train_batch_size=16,        # H100 80GB default; ADR-020 BATCH_TABLE scales for other classes
    gradient_accumulation_steps=2,         # effective batch 32 across all GPU classes
    num_train_epochs=2,                    # Q5 lock; uniform across the three transformer rungs
    bf16=True,                             # Q6 lock; SPEC §2 default
    fp16=False,
    max_grad_norm=1.0,
    weight_decay=0.01,
    save_strategy="epoch",                 # per-epoch checkpoint (LoRA + frozen-probe only; full-FT intermediates deleted post-inference)
    eval_strategy="no",                    # no val-set evaluation during training per hyperparameter-immutability
    seed=42,                               # iterated across ADR-006 slate (42, 1337, 2025)
    # Other defaults (AdamW optimizer, AdamW eps=1e-8, etc.) inherited from HF Trainer
)
```

### Data collator

```python
from transformers import DataCollatorWithPadding

data_collator = DataCollatorWithPadding(
    tokenizer,
    max_length=8192,                  # per ADR-014 Q3 ModernBERT-base native cap
    pad_to_multiple_of=8,             # tensor-core alignment for bf16 throughput
)
# Dynamic padding to batch-longest; truncation head-first when max_length exceeded per ADR-014 Q4
```

### WeightedTrainer subclass for class-weighted loss

```python
import torch
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from torch.nn import CrossEntropyLoss
from transformers import Trainer


class WeightedTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = CrossEntropyLoss(weight=self.class_weights.to(logits.device))
        loss = loss_fct(logits, labels)
        return (loss, outputs) if return_outputs else loss


# Per-fold computation (different LODO fold = different class balance)
weights = compute_class_weight(
    class_weight="balanced",
    classes=np.array([0, 1]),
    y=train_labels,
)
class_weights = torch.tensor(weights, dtype=torch.float32)
```

### Per-epoch prediction-save discipline

- Save per-row inference predictions for every (transformer rung, seed, fold, epoch) combination — 3 transformer rungs times 3 seeds times 4 folds times 2 epochs equals 72 prediction files
- File path convention — evals/predictions/<rung>__fold<F>__seed<S>__epoch<N>.parquet
- LoRA plus frozen-probe — persist intermediate adapter and head checkpoints (tiny; under 10 MB each)
- Full-FT — do NOT persist intermediate weight checkpoint (approximately 150 MB times 12 runs equals ~1.8 GB of throwaway weights); per-row predictions are the audit-relevant artifact; final epoch checkpoint is persisted
- Discipline rule — epoch-2 predictions are the headline numbers; epoch-1 predictions are reported as a diagnostic ablation in the methodology spoke; the ADR pre-commits this so cherry-picking is precluded
- The methodology spoke includes a per-(rung, seed, fold) epoch-1-to-epoch-2 AUPRC delta plot — surfaces undertraining versus overfitting boundaries; if epoch-1 systematically outperforms epoch-2 on some slice that IS a finding to report honestly

### Fp32 cast before final softmax or sigmoid

```python
# scripts/inference.py (sketch)
import torch

with torch.inference_mode():
    logits = model(**inputs).logits  # bf16
    probs = torch.softmax(logits.float(), dim=-1)  # fp32 cast before softmax
```

Applies to all three trained transformer rungs and to ProtectAI v1 plus v2 inference (preserves numerical-stability discipline uniformly across the bf16-inference rungs).

### Phase 1 verification task

After uv-resolving PEFT plus Transformers pinned versions, instantiate the locked LoraConfig plus AutoModelForSequenceClassification.from_pretrained for answerdotai/ModernBERT-base wrapped with get_peft_model. Dump the resolved trainable parameter enumeration plus target module list to evals/lora_target_modules.json. Assert — exactly 4 LoRA layers per ModernBERT encoder block times 22 layers equals 88 LoRA adapter modules; classifier head is in modules_to_save; trainable parameter ratio approximately 0.5 to 1 percent of total.

## Consequences

### Positive

- Complete training recipe is auditable in a single ADR; no hidden hyperparameters; reproducible without dependence on PEFT auto-detection
- Per-epoch prediction-save converts the SPEC §2 default 1-epoch sanity-check suggestion into a per-fold per-seed diagnostic at near-zero added cost
- Cross-rung sklearn-style class_weight balanced gives all four trained rungs a uniform weighting convention; auditable; aligns with ADR-017 Q1b classical-floor lock
- bf16 training plus inference with fp32-cast-before-softmax matches modern transformer FT best practice on H100; ModernBERT pretrained with bf16
- Explicit target_modules enumeration removes a silent dependency on PEFT version-specific auto-detection; survives PEFT updates
- Storage discipline (no intermediate full-FT weights persisted; per-row predictions persisted instead) controls disk footprint while preserving all audit-relevant artifacts

### Negative

- Per-epoch inference doubles eval-time compute (one extra inference pass per training run); on H100 this is approximately 30 to 60 minutes added across the 36 transformer training runs; well inside the compute envelope locked by ADR-020
- The recipe is a single-point lock — no tuning means if r=8 or lr=1e-4 happens to be suboptimal for this data scale, we report what we get under the locked recipe rather than tuning to improve; this is methodologically intentional per SPEC §2 hyperparameter-immutability
- Storage of 96 per-epoch parquet predictions (32 with epoch dim from transformers plus 12 from TF-IDF+LR plus 16 from reference rungs) requires the pre-teardown checklist (A-003) to cover all of them; spirit of the rule extends to the per-epoch dimension
- The 1-epoch diagnostic is not a true "1-epoch-locked recipe" — the LR schedule (cosine decay over 2 epochs) means at end-of-epoch-1 LR is mid-decay rather than near-zero; the epoch-1 predictions are "partial-training diagnostic" not "what a 1-epoch-locked recipe would achieve"; documented in the spoke

### Phase 1 deliverables

- src/training/lora_config.py — the locked LoraConfig instance
- src/training/weighted_trainer.py — WeightedTrainer subclass
- src/training/training_args.py — locked TrainingArguments factory keyed on seed
- src/inference/softmax_cast.py — fp32-cast-before-softmax helper
- evals/lora_target_modules.json — Phase 1 verification output
- evals/predictions/<rung>__fold<F>__seed<S>__epoch<N>.parquet — per-(rung, seed, fold, epoch) predictions

## Alternatives considered

- **r=16 instead of r=8** — rejected; r=8 is the PEFT default and well-cited; r=16 doubles adapter capacity which may help on larger datasets but introduces overfit risk on our moderate-scale positive class. The hyperparameter-immutability rule prevents tuning so we pick the literature default.
- **target_modules equals all-linear (PEFT auto-detection)** — rejected per SDD discipline; deterministic explicit enumeration is preferred; eliminates dependency on PEFT version-specific auto-detection logic.
- **Higher learning rate (3e-4 or 5e-4)** — rejected; 1e-4 is conservative; preserves backbone-pretrained features; reduces overfit risk on small positive class. The LoRA paper §A.2 uses 5e-4 but on different task scales; modern recipes converge on lr=1e-4 to 3e-4 for BERT-class fine-tuning on moderate-scale data.
- **1 epoch instead of 2** — rejected; SPEC §2 explicitly warns "1-epoch LoRA can dramatically undertrain on small pools (cross-source generalization may collapse)"; our LODO folds have approximately 9K positives, in the moderate-small range where undertraining is likely.
- **3+ epochs** — rejected; deviates from SPEC §2 default without strong justification; Mosbach et al. 2021 argues for ≥3 epochs for BERT full-FT stability but with frozen backbone (LoRA case) stability is much less of a concern.
- **Early-stopping on val** — rejected; violates SPEC §2 hyperparameter-immutability (early-stop is a val-tuned signal); anti-pattern per CLAUDE.md ("tuning on val/test"); requires carving val from train reducing LODO train pool.
- **fp16 instead of bf16** — rejected on H100; bf16 has fp32-equivalent dynamic range (no gradient underflow); fp16 requires GradScaler complexity and softmax fp32 cast for stability; bf16 is the modern default on Ampere+.
- **fp32 throughout** — rejected; 2x memory plus 2x slower; wastes H100 tensor-core throughput; no methodological reason on this hardware.
- **HF-Trainer-style pos_weight via BCEWithLogitsLoss** — rejected for cross-rung consistency with TF-IDF+LR's sklearn-style; both formulations give identical relative weighting (deltas under 0.001 PR-AUC per SPEC §2 line 145); the methodology decision is implementation convention.
- **Uniform class weighting (no weighting)** — rejected; SPEC §2 line 145 warns "uniform may underperform on small positive classes"; at our 1:2.2 LODO-train pool imbalance the impact is small but the sklearn-style move gives free recall improvement on the minority class with negligible added complexity.
- **Save full-FT intermediate weights** — rejected; per-row predictions are the audit-relevant artifact; the model state itself is only needed for resumption (handled by the pre-teardown checklist) or further fine-tuning (out of prototype scope). Storage saved is approximately 1.8 GB across the 12 full-FT runs.
- **Skip per-epoch save entirely** — rejected; per-epoch predictions are near-zero added cost (one extra inference per training run) and provide a per-fold-per-seed 1-epoch diagnostic that strictly improves on SPEC §2's at-least-one-fold suggestion.

## References

See frontmatter references list. Primary anchors — LoRA paper (Hu et al. 2021); Mosbach et al. 2021 BERT FT stability; ModernBERT paper (Warner et al. 2024); Kalamkar et al. 2019 bfloat16 study; HuggingFace PEFT documentation; PEFT sequence-classification LoRA notebook; Sebastian Raschka 2024 practical LoRA tips; Phil Schmid 2025 ModernBERT FT guide; sklearn class_weight documentation; King and Zeng 2001 rare-events logistic regression; PyTorch CrossEntropyLoss reference; NVIDIA H100 tensor-core whitepaper; ModernBERT HF docs and transformers source; ADR-015 single-backbone lock; ADR-014 truncation policy; ADR-006 multi-seed protocol; ADR-017 classical-floor and frozen-probe role.
