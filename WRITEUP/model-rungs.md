# Model rungs

This spoke covers §4 of the methodology narrative — the rung ladder
(5 rungs: classical floor + 3 trained transformer rungs + 2 reference
scorers) per ADR-015 + ADR-017 + ADR-018 + ADR-050. Each rung answers
*what does this capability layer add over the rung below?*
Hyperparameters are locked before training begins; no val-set
gridsearch. For the locked recipe in tabular form see
[`../docs/HYPERPARAMETER_DISCLOSURE.md`](../docs/HYPERPARAMETER_DISCLOSURE.md);
for headline results consuming these rungs see
[`../WRITEUP.md`](../WRITEUP.md) §Results.

Training compute target locked at A100-SXM4-80GB × 12 cells × 2 epochs
per ADR-019 + ADR-049 (per-pod cap $40/$60/$100 per ADR-020).

## 4.1 Rung 1 — *the linear floor*

TF-IDF (word ngrams 1-2 + char ngrams 3-5; max_features=15000 each;
sublinear TF; lowercase + strip_accents=unicode) + logistic regression
(`solver=liblinear`, `C=1.0`, `class_weight=balanced`, `max_iter=1000`).
Deterministic; one fit per fold × seed. Per ADR-017 + ADR-044.
Contamination tier: `verified_disjoint` per ADR-005.

*Why this rung exists*: a linear model is the minimum-viable
classifier for the task; everything above it has to earn its
complexity.

**Result**: tfidf-lr's `pooled_ood` AUROC is 0.371 [0.362, 0.381] —
slightly below chance, but with a tight CI that does NOT cross 0.50
(CI upper bound 0.381). On the IID-shaped slices it lands at 0.445
[0.422, 0.469] (jbb_behaviors) and 0.451 [0.436, 0.466] (xstest).
This is the floor everything else has to beat to earn its complexity.
*Result*: only `frozen_probe` clears this floor on `pooled_ood` with
margin (delta +0.144 AUROC).

## 4.2 Rung 2 — *what the backbone already encodes*

ModernBERT-base (`answerdotai/ModernBERT-base`, revision pinned at SHA
`8949b909ec900327062f0ebf497f51aef5e6f0c8`) with all backbone weights
FROZEN; only the 2-class classification head is trained per ADR-015 +
ADR-019. 2 epochs × class-balanced loss × bf16 × 12 cells (4 folds × 3
seeds). Contamination tier: `backbone-partial-disjoint` per ADR-005.

*Why this rung exists*: separates *pretraining alone* from
*fine-tuning*. If the frozen probe matches or beats Rung 1 but the
fine-tuned rung doesn't lift further, fine-tuning isn't adding
capability — it's overfitting.

**Result**: frozen-probe's `pooled_ood` AUROC is 0.515 [0.505, 0.525]
— *the only rung whose CI clears 0.50 with margin*. Net OOD lift over
tfidf-lr is +0.144 AUROC. The pretrained ModernBERT embeddings carry
significant generalization budget; the classifier head needs ONLY
linear access to those embeddings to land above chance on the OOD
slate. This is the headline finding of WRITEUP §Results §7.

## 4.3 Rung 3 — *the fine-tuning ceiling at the project's compute budget*

ModernBERT-base with LoRA adapters per ADR-015 + ADR-019:
- `r = 8`, `alpha = 16`, `dropout = 0.1`
- `target_modules = [Wqkv, attn.Wo, mlp.Wo, mlp.Wi]` (ModernBERT
  attention + MLP linear modules)
- `modules_to_save = [classifier]`, `task_type = SEQ_CLS`, `bias = none`

2 epochs × class-balanced loss × bf16 × 12 cells. Approximately 0.5 %
to 1 % of parameters trainable. Contamination tier:
`backbone-partial-disjoint` per ADR-005.

*Why this rung exists*: it's the maximally-adapted model in the
project compute budget. If anything above the frozen probe is worth
doing, this rung is where it shows.

**Result**: LoRA's `pooled_ood` AUROC is 0.383 [0.374, 0.392] —
*below* the frozen-probe baseline (-0.132 AUROC; paired-bootstrap CI
excludes zero). The adapter weights specialise to the training
distribution; on the OOD slate they degrade generalization vs the bare
backbone embeddings. LoRA fine-tuning on this task at this compute
budget is a NEGATIVE result — it works on jbb_behaviors / xstest
(in-distribution-shaped slices) and overfits relative to the frozen
probe on genuinely OOD distributions. See WRITEUP §Results §7.7 for
the paired-bootstrap detail.

**Note on full-FT**: full-FT was the planned Rung 3.5 (full backbone
trainable) per ADR-019; per ADR-050 it was DROPPED from OOD comparison
due to a Phase 5 FUSE EIO crash on /workspace MooseFS storage. full-FT
remains in the LODO comparison (3-rung ladder narrative survives via
the 24 surviving LODO predictions from Phase 2); OOD comparison ships
2 trained rungs (frozen-probe + LoRA). See
[`limitations-and-future-work.md`](./limitations-and-future-work.md) §8.1.

## 4.4 Rung 4 — *narrow-scope reference scorer*

ProtectAI `deberta-v3-base-prompt-injection` v1
(`suspected_contamination` per ADR-005). Stated training scope: direct
prompt injection (English). Inference-only via
`transformers.AutoModelForSequenceClassification` per ADR-018. *Why
this rung exists*: a publicly-trained narrow-scope detector is the
"is this better than something already on the shelf for this attack
class" bar.

*Caveat*: reference scorers carry training-overlap audit obligations
per [`../EVIDENCE.md`](../EVIDENCE.md) §1. Reported as diagnostic
reference, not as a clean baseline.

**Result**: ProtectAI v1's `pooled_ood` AUROC is 0.440 [0.409, 0.469].
Slightly above tfidf-lr (+0.069); well below frozen-probe (-0.075).
The off-the-shelf narrow-scope detector beats a linear floor but does
not match a frozen pretrained backbone on this slate. Suspected-
contamination caveat retained.

## 4.5 Rung 5 — *broad-scope reference scorer*

ProtectAI `deberta-v3-base-prompt-injection-v2`
(`suspected_contamination`). v2 adds broader-scope training data per
the published model card update per ADR-018. *Why this rung exists*:
a broader-scope reference completes the reference picture. Caveat:
training-data disclosure is at category level only; contamination
cannot be verified; audit shifts to fold-pattern + scope-mismatch
analysis per [`../EVIDENCE.md`](../EVIDENCE.md) §2.

**Result**: ProtectAI v2's `pooled_ood` AUROC is 0.402 [0.369, 0.437]
— slightly worse than v1 (-0.04 on pooled). v2 BEATS v1 on
jbb_behaviors (+0.06 AUROC) but LOSES on xstest (-0.15 AUROC; CIs do
not overlap — a clear regression). The lesson: off-the-shelf detector
updates do not monotonically improve across distributions; consumers
cannot assume v2 dominates v1.

## Note on dropped reference rungs

**LLM-judge rungs** (gpt-4o-2024-08-06 + claude-sonnet-4-6) were
locked at Phase 0-03 per ADR-018 and DROPPED at Phase 4 cost
re-estimation per ADR-050 (16× envelope overrun against the original
$14 estimate driven by per-row LLM-judge inference being charged at
the full input-prompt token count — long injection examples hit 1k-3k
tokens routinely). The `vendor_black_box` contamination tier therefore
has 0 rungs in this submission; the contamination-stratification
gradient compresses from 4 tiers to 3.

## Cross-references

- **Hyperparameter disclosure (locked recipe + axes-not-searched)** → [`../docs/HYPERPARAMETER_DISCLOSURE.md`](../docs/HYPERPARAMETER_DISCLOSURE.md)
- **Headline results consuming the rung ladder** → [`../WRITEUP.md`](../WRITEUP.md) §Results
- **Reference-scorer contamination audit detail** → [`reference-scorer-audit.md`](./reference-scorer-audit.md)

**Linked ADRs**: ADR-015 (single-backbone slate), ADR-017 (classical
floor + trained-rung slate), ADR-018 (reference slate), ADR-019
(transformer training recipe), ADR-044 (Phase 2 implementation),
ADR-049 (GPU order priority refresh), ADR-050 (rung-slate narrowing).
