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

Training on direct prompt-injection examples did **not** produce a detector that
generalized to different attack families. On the pooled OOD slice, no evaluated
detector clearly beat the AUPRC random floor of **0.374**.

| Detector | Pooled OOD AUPRC | Interpretation |
|---|---:|---|
| ModernBERT frozen probe | 0.364 [0.354, 0.375] | Best in-house score, but still at the random floor |
| ProtectAI v1 | 0.361 [0.330, 0.391] | Similar result; diagnostic only because of contamination caveats |
| ProtectAI v2 | 0.314 [0.283, 0.345] | Does not dominate v1 on this evaluation |
| ModernBERT LoRA | 0.293 [0.286, 0.301] | Fine-tuning hurt OOD performance |
| TF-IDF + LR | 0.291 [0.283, 0.298] | Classical baseline, roughly tied with LoRA |

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

1. **The OOD wall is cross-family.** The training pool is direct-injection
   heavy, while the OOD slate includes attack families absent from training.
2. **Fine-tuning hurt.** LoRA scored 0.293 on pooled OOD, below the frozen
   probe's 0.364 and roughly tied with TF-IDF + LR.
3. **Reference detectors are not monotone by version.** ProtectAI v2 improves
   one slice but regresses on another, so "newer" does not mean universally
   better.
4. **Thresholds are fragile.** Validation thresholds understate how many false
   positives appear on held-out sources.

## What This Does Not Claim

The numbers do not cover multilingual attacks, encoded payloads, paraphrase
robustness, adversarial perturbations, or full multi-turn system behavior. The
result is a capability characterization and methodology artifact, not a
deployment recommendation.

## Where To Go Next

- [Results](RESULTS.md): exact grids, canonical figures, and artifact links.
- [Writeup](WRITEUP.md): methodology narrative.
- [Evidence](EVIDENCE.md): external-evidence and reference-scorer audit trail.
- [Decisions](decisions/README.md): ADR trail, now including ADR-062 for this
  clarity and canonical-figures patch.
