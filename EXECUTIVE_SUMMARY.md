---
title: "Executive summary: prompt-injection classifier evaluation"
description: "Plain-language one-page summary of the prompt-injection classifier methodology submission."
---

# Executive Summary

This project evaluates prompt-injection detectors under out-of-distribution
(OOD) shift. Prompt injection means untrusted text trying to override an LLM
system's instructions. The project is not trying to ship a production detector;
it is trying to show what a fairer evaluation says about several detector
designs.

## Bottom Line

Training on direct prompt-injection examples produced real direct-pattern
detection, but it did **not** produce a detector that generalized to different
attack families. The co-headline is:

**Direct detection works better; cross-family generalization fails.**

| Result view | Best in-house result | Interpretation |
|---|---:|---|
| Balanced validation, direct + benign | LoRA AUPRC **0.974**, AUROC **0.993**, recall@0.5 **0.934** | the direct task was learned |
| LODO held-out direct-source test | frozen-probe recall@0.5 **0.641** | held-out direct-source recall |
| Pooled OOD | frozen-probe AUPRC **0.364** vs random floor **0.374** | cross-family ranking did not beat guessing |

On the pooled OOD slice, no evaluated detector clearly beat the AUPRC random
floor of **0.374**. The LODO held-out direct-source test is all-positive, so
false positives, AUPRC, and AUROC are left out of that table.

| Detector | Pooled OOD AUPRC | Interpretation |
|---|---:|---|
| ModernBERT frozen probe | 0.364 [0.354, 0.375] | Best in-house score, but still at the random floor |
| ProtectAI v1\* | 0.361 [0.330, 0.391] | Reference scorer with verified training-pool overlap; not a clean OOD baseline |
| ProtectAI v2\* | 0.314 [0.283, 0.345] | Reference scorer with verified training-pool overlap; does not dominate v1 |
| ModernBERT LoRA | 0.293 [0.286, 0.301] | Fine-tuning was actively harmful --- AUROC 0.383 below 0.5 floor (lexical overfitting + slate-induced label-relevance inversion; see §Mechanism below) |
| TF-IDF + LR | 0.291 [0.283, 0.298] | Classical baseline, roughly tied with LoRA --- AUROC 0.371 also below 0.5 floor (same mechanism as LoRA) |

\* ProtectAI v1 + v2 were trained on at least 2 of 4 LODO training-pool sources
(`deepset/prompt-injections`, `Lakera/gandalf_ignore_instructions`) per
[EVIDENCE](EVIDENCE.md) §1-2. Pooled OOD scores on slices that overlap with
that training pool are not clean OOD baselines.

## Mechanism: lexical overfitting + slate-induced label-relevance inversion

Two detectors land **below** the 0.5 AUROC random floor on pooled OOD with CIs
that clear 0.5 on the wrong side: LoRA at 0.383 [0.374, 0.392] and TF-IDF + LR
at 0.371 [0.362, 0.381]. A score below 0.5 AUROC isn't pure overfitting (which
predicts collapse *toward* random, not past it); it's lexical overfitting
combined with a label-relevance shift on this specific slate:

- LoRA + TF-IDF both learn lexical signatures of direct injection
  ("ignore previous instructions", "you are now", etc.).
- **NotInject** (n=339, all negative): benign text engineered to *look like*
  direct injection. Both detectors score these HIGH (false positives).
- **BIPIA + InjecAgent** (indirect + agentic, n=112): real attacks that *don't*
  use direct-injection lexical patterns. Both detectors score these LOW
  (false negatives).

The lexical signal is real and consistent within itself — it just stops
tracking attack class on cross-family slices where the lexical and semantic
labels diverge. The frozen ModernBERT probe (zero LODO-pool adaptation) stays
at 0.515 AUROC — generic linguistic features are less aligned with the
direct-injection lexical distribution and therefore less inverted on the
cross-family slate.

Generalization gap: in-pool 0.99 AUROC → cross-family 0.38 AUROC, ~0.6 drop
for the trained detectors; frozen probe's gap is 0.91 → 0.515, ~0.4 drop. The
more training adapted to the LODO pool, the harder the cross-family fall.

## Direct Detection Check

The OOD result should not be read as "nothing worked." The direct detection
check shows that the detectors learned the direct prompt-injection task, then
failed to generalize cleanly across attack families.

**Balanced direct+benign validation**

| Detector | AUPRC | AUROC | Recall@0.5 | Interpretation |
|---|---:|---:|---:|---|
| ModernBERT LoRA | **0.974** | **0.993** | **0.934** | strongest direct-pattern detector |
| TF-IDF + LR | 0.971 | 0.992 | 0.930 | lexical direct baseline is also strong |
| ModernBERT frozen probe | 0.653 | 0.907 | 0.849 | weaker ranking, still discriminative |

**Held-out direct-source recall**

| Detector | Recall@0.5 | Interpretation |
|---|---:|---|
| ModernBERT frozen probe | **0.641** | best direct-source holdout recall |
| ModernBERT LoRA | 0.625 | similar recall, despite worse pooled OOD ranking |
| ModernBERT full fine-tune\*\* | 0.558 | lower direct-source recall |

\*\* Full-FT shows LODO direct-source data only (24 Phase 2 predictions
persisted); the comparable pooled OOD inference was **not run** (Phase 5 X11
crash, see [ADR-075](decisions/ADR-075-full-ft-ood-drop-rationale-unified-narrative.md)).
Full-FT is absent from the Pooled OOD table above for that reason.

False positives, AUPRC, and AUROC are omitted from the held-out direct-source
table because that slice is all-positive.

## What Was Tested

- **In scope**: single-turn English text classification.
- **Training pool**: four direct-injection sources.
- **OOD slate**: five held-out slices covering indirect injection, agentic-flow
  injection, jailbreak-style questions, and benign-but-injection-shaped text.
- **Detectors**: TF-IDF + logistic regression, ModernBERT frozen probe,
  ModernBERT LoRA, and ProtectAI v1/v2 reference scorers.

## How To Read The Metrics

- **AUPRC**: the primary ranking metric. On imbalanced data, its random floor is
  the positive rate, not 0.5. Here that floor is 412 / 1101 = 0.374.
- **AUROC**: secondary diagnostic with a 0.5 random floor; useful for
  comparison, but less informative under imbalance.
- **95% CI**: uncertainty around a number. If a model's interval only touches
  the random floor, the result should be read cautiously.
- **FPR**: false-positive rate. In this project, a 1% FPR threshold tuned on
  validation often did not hold on held-out sources.
- **ECE/Brier**: calibration errors. Lower is better; they ask whether model
  scores behave like probabilities.

## Main Findings

1. **Direct detection worked better than OOD.** LoRA reached 0.974 AUPRC on
   balanced direct+benign validation, while the best pooled OOD AUPRC was 0.364.
2. **The OOD wall is cross-family.** The training pool is direct-injection
   heavy, while the OOD slate includes attack families absent from training.
3. **Fine-tuning hurt OOD.** LoRA scored 0.293 on pooled OOD, below the frozen
   probe's 0.364 and roughly tied with TF-IDF + LR.
4. **Reference detectors are not monotone by version.** ProtectAI v2 improves
   one slice but regresses on another, so "newer" does not mean universally
   better.
5. **Thresholds are fragile.** Validation thresholds understate how many false
   positives appear on held-out sources.

## What This Does Not Claim

The numbers do not cover multilingual attacks, encoded payloads, paraphrase
robustness, adversarial perturbations, or full multi-turn system behavior. The
result is a capability characterization and methodology artifact, not a
deployment recommendation.

## Where To Go Next

- [Project at a glance](docs/for-hiring-managers.md): 60-second
  reader path from problem to finding to trust basis.
- [Results](RESULTS.md): exact grids, canonical figures, and artifact links.
- [Writeup](WRITEUP.md): methodology narrative.
- [Evidence](EVIDENCE.md): external-evidence and reference-scorer audit trail.
- [Decisions](decisions/README.md): ADR trail for methodology and governance.
