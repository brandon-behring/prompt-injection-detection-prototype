---
title: "Model details"
description: "Detector ladder and reference scorer details for the prompt-injection evaluation."
---

# Model Details

*Part of the [WRITEUP methodology](../WRITEUP.md); see the hub for the cover narrative and reading guide.*

> **How to read this spoke**: For a hiring-manager-level skim, focus on the bolded **Result** subsections + the final §Summary if present. For a full audit, read the methodology paragraphs + the ADR references in headers. Note: the filename retains "rungs" as an architectural artifact (older ADRs use that term); reader-facing prose elsewhere calls these "detectors" — same thing.

:::{.callout-note}
## Summary

- **TF-IDF + LR floor**: `pooled_ood` AUPRC 0.291 [0.283, 0.298] — below the random-predictor baseline of 0.374; this is the floor every other detector is measured against.
- **Frozen probe (ModernBERT)**: `pooled_ood` AUPRC 0.364 [0.354, 0.375] — best in the slate (+0.073 lift over the floor) but still ~0.01 below the prevalence baseline. The pretrained ModernBERT embeddings carry what little OOD generalization budget exists.
- **LoRA fine-tune**: `pooled_ood` AUPRC 0.293 [0.286, 0.301] — drops -0.071 below frozen-probe; ties the classical floor. Fine-tuning on the LODO direct-injection pool *hurts* OOD generalization (negative result).
- **ProtectAI v1 reference**: `pooled_ood` AUPRC 0.361 [0.330, 0.391] — essentially at parity with frozen-probe; `suspected_contamination` tier per ADR-005.
- **ProtectAI v2 reference**: `pooled_ood` AUPRC 0.314 [0.283, 0.345] — worse than v1 on `xstest` (-0.15 AUROC clear regression); broader-scope training did NOT monotonically improve across the OOD slate.
:::

This spoke covers section 4 of the methodology narrative: the detector ladder.
The evaluated detectors are the classical floor, three trained transformer
variants, and two published reference scorers per ADR-015, ADR-017, ADR-018,
and ADR-050. Older ADRs call these "rungs"; in the reader-facing writeup,
"detector" means one evaluated scoring approach.
Hyperparameters are locked before training begins; no val-set
gridsearch. For the locked recipe in tabular form see
[`../docs/HYPERPARAMETER_DISCLOSURE.md`](../docs/HYPERPARAMETER_DISCLOSURE.md);
for headline results using these detectors see
[`../WRITEUP.md`](../WRITEUP.md) §Results.

Training compute target locked at A100-SXM4-80GB across 12 cells and 2 epochs
per ADR-019 + ADR-049 (per-pod cap $40/$60/$100 per ADR-020).

## 4.1 Detector 1: *the linear floor*

TF-IDF (word ngrams 1-2 + char ngrams 3-5; max_features=15000 each;
sublinear TF; lowercase + strip_accents=unicode) + logistic regression
(`solver=liblinear`, `C=1.0`, `class_weight=balanced`, `max_iter=1000`).
Deterministic; one fit per fold × seed. Per ADR-017 + ADR-044.
Contamination tier: `verified_disjoint` per ADR-005.

*Why this detector exists*: a linear model is the minimum-viable
classifier for the task; everything above it has to earn its
complexity.

**Result**: tfidf-lr's `pooled_ood` AUPRC is 0.291 [0.283, 0.298] —
substantially below the `pooled_ood` positive-class prevalence
baseline of 0.374 (random-predictor AUPRC equals positive prevalence
on the slice). On the IID-shaped slices it lands at 0.470 [0.443,
0.496] (jbb_behaviors) and 0.395 [0.379, 0.410] (xstest). This is
the floor every other detector is measured against. *Result*: only
`frozen-probe` lifts above this floor on `pooled_ood` with margin
(delta +0.073 AUPRC). By AUROC (cross-paper comparable; chance
baseline 0.5), tfidf-lr lands at 0.371 [0.362, 0.381] — below chance
under AUROC's prior-independent framing.

## 4.2 Detector 2: *what the backbone already encodes*

ModernBERT-base (`answerdotai/ModernBERT-base`, revision pinned at SHA
`8949b909ec900327062f0ebf497f51aef5e6f0c8`) with all backbone weights
FROZEN; only the 2-class classification head is trained per ADR-015 +
ADR-019. 2 epochs × class-balanced loss × bf16 × 12 cells (4 folds × 3
seeds). Contamination tier: `backbone-partial-disjoint` per ADR-005.

*Why this detector exists*: separates *pretraining alone* from
*fine-tuning*. If the frozen probe matches or beats the linear floor but the
fine-tuned detector does not lift further, fine-tuning is not adding
capability — it's overfitting.

**Result**: frozen-probe's `pooled_ood` AUPRC is 0.364 [0.354, 0.375]
— the best `pooled_ood` AUPRC in the slate, but still ~0.01 *below*
the `pooled_ood` positive-class prevalence baseline of 0.374. Net
OOD lift over tfidf-lr is +0.073 AUPRC. The pretrained ModernBERT
embeddings carry what little OOD generalization budget exists — but
the absolute number does not clear the prevalence baseline. By
AUROC (chance baseline 0.5), frozen-probe lands at 0.515 [0.505,
0.525] — *the only detector whose AUROC CI clears 0.50 with margin*.
This is the headline finding of WRITEUP §Results.

## 4.3 Detector 3: *the fine-tuning ceiling at the project's compute budget*

ModernBERT-base with LoRA adapters per ADR-015 + ADR-019:
- `r = 8`, `alpha = 16`, `dropout = 0.1`
- `target_modules = [Wqkv, attn.Wo, mlp.Wo, mlp.Wi]` (ModernBERT
  attention + MLP linear modules)
- `modules_to_save = [classifier]`, `task_type = SEQ_CLS`, `bias = none`

2 epochs × class-balanced loss × bf16 × 12 cells. Approximately 0.5 %
to 1 % of parameters trainable. Contamination tier:
`backbone-partial-disjoint` per ADR-005.

*Why this detector exists*: it is the maximally-adapted model in the
project compute budget. If anything above the frozen probe is worth
doing, this detector is where it shows.

**Result**: LoRA's `pooled_ood` AUPRC is 0.293 [0.286, 0.301] —
below the frozen-probe baseline by -0.071 AUPRC using marginal point
estimates, and essentially tied with the classical floor (0.291). The
persisted paired-bootstrap artifact covers JBB and XSTest, but not the pooled
comparison. The adapter weights specialise to the training distribution; on
the OOD slate they degrade generalization vs the bare backbone embeddings.
LoRA fine-tuning on this task at this compute budget is a negative result: it
is close to frozen-probe on XSTest, worse on JBB, and worse on the pooled OOD
slice. By AUROC, LoRA lands at 0.383 [0.374, 0.392], -0.132 below
frozen-probe. See WRITEUP §Results §Frozen probe vs adapter fine-tuned for the
paired-bootstrap detail.

**Note on full-FT**: full-FT was the planned full-backbone detector (full backbone
trainable) per ADR-019 and was trained for LODO at Phase 2 (24
prediction parquets retained); OOD inference was dropped at Phase 5
X11 per ADR-052 (narrow supersession of ADR-050 R2). Load-bearing
reason: LoRA's pooled-OOD point estimate vs frozen-probe already
showed fine-tuning on the LODO direct-injection pool was HURTING
OOD generalization; full-FT is a larger version of the
same mechanism (~149M params vs LoRA's ~1.5M trainable), so the
expected marginal benefit on OOD was low. The FUSE EIO crash on
/workspace MooseFS storage was the operational trigger that exposed
the decision. OOD comparison ships 2 trained detectors (frozen-probe +
LoRA); LODO 3-detector ladder narrative survives via the 24 Phase 2
LODO predictions. See ADR-052 + [`limitations-and-future-work.md`](./limitations-and-future-work.md)
§8.1 for the full methodological + retrospective framing.

## 4.4 Detector 4: *narrow-scope reference scorer*

ProtectAI `deberta-v3-base-prompt-injection` v1
(`suspected_contamination` per ADR-005). Stated training scope: direct
prompt injection (English). Inference-only via
`transformers.AutoModelForSequenceClassification` per ADR-018. *Why
this detector exists*: a publicly-trained narrow-scope detector is the
"is this better than something already on the shelf for this attack
class" bar.

*Caveat*: reference scorers carry training-overlap audit obligations
per [`../EVIDENCE.md`](../EVIDENCE.md) §1. Reported as diagnostic
reference, not as a clean baseline.

**Result**: ProtectAI v1's `pooled_ood` AUPRC is 0.361 [0.330, 0.391]
— essentially at parity with frozen-probe (0.364) and well above
tfidf-lr (+0.070 AUPRC over the classical floor). Like frozen-probe,
it lands just below the `pooled_ood` prevalence baseline (0.374).
The off-the-shelf narrow-scope detector beats a linear floor and
matches the frozen pretrained backbone on this slate within CI
overlap — but the suspected-contamination caveat retained means
this read is diagnostic, not a clean baseline. By AUROC, ProtectAI
v1 lands at 0.440 [0.409, 0.469] (-0.075 below frozen-probe's
AUROC).

## 4.5 Detector 5: *broad-scope reference scorer*

ProtectAI `deberta-v3-base-prompt-injection-v2`
(`suspected_contamination`). v2 adds broader-scope training data per
the published model card update per ADR-018. *Why this detector exists*:
a broader-scope reference completes the reference picture. Caveat:
training-data disclosure is at category level only; contamination
cannot be verified; audit shifts to fold-pattern + scope-mismatch
analysis per [`../EVIDENCE.md`](../EVIDENCE.md) §2.

**Result**: ProtectAI v2's `pooled_ood` AUPRC is 0.314 [0.283, 0.345]
— substantially worse than v1 (-0.047 AUPRC on pooled). v2 BEATS
v1 on jbb_behaviors (+0.037 AUPRC) but LOSES on xstest (-0.087
AUPRC; CIs overlap but with separation). The lesson: off-the-shelf
detector updates do not monotonically improve across distributions;
consumers cannot assume v2 dominates v1. By AUROC, v2 lands at
0.402 [0.369, 0.437] (-0.04 below v1) — same direction as AUPRC.

## Note on dropped reference detectors

**LLM-judge detectors** (gpt-4o-2024-08-06 + claude-sonnet-4-6) were
locked at Phase 0-03 per ADR-018 and DROPPED at Phase 4 cost
re-estimation per ADR-050 (16× envelope overrun against the original
$14 estimate driven by per-row LLM-judge inference being charged at
the full input-prompt token count — long injection examples hit 1k-3k
tokens routinely). The `vendor_black_box` contamination tier therefore
has 0 detectors in this submission; the contamination-stratification
gradient compresses from 4 tiers to 3.

## Cross-references

- **Hyperparameter disclosure (locked recipe + axes-not-searched)** → [`../docs/HYPERPARAMETER_DISCLOSURE.md`](../docs/HYPERPARAMETER_DISCLOSURE.md)
- **Headline results using the detector ladder** → [`../WRITEUP.md`](../WRITEUP.md) §Results
- **Reference-scorer contamination audit detail** → [`reference-scorer-audit.md`](./reference-scorer-audit.md)

**Linked ADRs**: ADR-015 (single-backbone slate), ADR-017 (classical
floor + trained-rung slate), ADR-018 (reference slate), ADR-019
(transformer training recipe), ADR-044 (Phase 2 implementation),
ADR-049 (GPU order priority refresh), ADR-050 (rung-slate narrowing).
