# Prompt-Injection Classification: Methodology and Capability Characterization

**Author**: Brandon Behring | **Date**: 2026-05-19 | **Status**: live-site
clarity patch per ADR-062; canonical submission source pin remains
`tree/v1.0.0`.

This is the methodology hub. It explains the problem, the evaluation setup, the
headline result, and the limits in one place. The detailed spokes remain linked
below for readers who want the full audit trail.

| Spoke | What It Covers |
|---|---|
| [Data decisions](./WRITEUP/data-decisions.md) | source slate, deduplication, leakage handling, leave-one-dataset-out (LODO) splits |
| [Model details](./WRITEUP/model-rungs.md) | TF-IDF + LR, frozen-probe, LoRA, full-FT status, ProtectAI references (older decision records call these "rungs"; reader-facing prose uses "detector"; see the [glossary](./docs/GLOSSARY.md#rung--detector-clarifier)) |
| [Evaluation design](./WRITEUP/eval-design.md) | AUPRC/AUROC, confidence intervals, calibration, out-of-distribution (OOD) slate |
| [Threshold policy](./WRITEUP/threshold-policy.md) | detection and verification thresholds |
| [Reference-scorer audit](./WRITEUP/reference-scorer-audit.md) | contamination caveats for published detectors |
| [Methodology guarantees](./WRITEUP/methodology-guarantees.md) | library-first evaluation stack and reproducibility discipline |
| [Limitations and future work](./WRITEUP/limitations-and-future-work.md) | what is out of scope and what should be tried next |
| [Reproducibility](./WRITEUP/reproducibility.md) | local, hub, and cloud reproduction paths |

## 1. Problem

Prompt injection is untrusted text that tries to override the instructions an
LLM system is supposed to follow. A detector for this problem sounds simple:
score a piece of text as "injection" or "benign." The hard part is knowing
whether the detector learned the attack class or only memorized the style of
the training examples.

This project evaluates that question directly. The goal is not to produce a
deployment-ready detector. The goal is to build a fair evaluation harness and
show what several detector designs can and cannot do under distribution shift.

## 2. Scope

The classifier is a **single-turn English text classifier**. It receives one
text span and returns a score.

In scope:

- direct prompt-injection text,
- held-out OOD slices that probe related but different attack families,
- model comparison through a detector ladder of increasing complexity,
- uncertainty reporting on headline claims.

Out of scope:

- multilingual attacks,
- encoded payloads such as base64, leetspeak, or Unicode confusables,
- paraphrase robustness,
- adversarial perturbations,
- full multi-turn system behavior,
- deployment threshold recommendations.

InjecAgent appears in the OOD slate to quantify the gap for agentic-flow
attacks. It does not mean the single-turn classifier is expected to solve that
problem.

## 3. Evaluation Setup

The training pool is direct-injection-heavy. The OOD test slate intentionally
changes the attack family.

| Attack Type | Training Pool | OOD Test Slices |
|---|---|---|
| Direct injection | deepset, Lakera Gandalf, Lakera Mosscap, HackAPrompt | partial coverage in JBB/XSTest |
| Indirect injection | absent | BIPIA |
| Agentic-flow injection | absent | InjecAgent |
| Jailbreak-as-question | partial HackAPrompt coverage | JBB, XSTest |
| Benign but injection-shaped | absent | NotInject |

That mismatch is the main story. The OOD wall is **cross-family**, not merely a
new source name.

## 4. Models Evaluated

The detector ladder was chosen to answer "what does each added capability buy?"

| Detector | Purpose |
|---|---|
| TF-IDF + logistic regression | classical floor; cheap lexical baseline |
| ModernBERT frozen probe | tests what the pretrained backbone already encodes |
| ModernBERT LoRA | tests whether adapter fine-tuning helps or overfits |
| ProtectAI v1/v2 | diagnostic published references, with contamination caveats |

Full fine-tuning was trained for the LODO path, but OOD inference was dropped
after LoRA already showed that fine-tuning on this direct-injection pool hurt
OOD generalization. See [model details](./WRITEUP/model-rungs.md) and
[limitations](./WRITEUP/limitations-and-future-work.md) for the detailed
status.

## 5. How To Read The Metrics

- **AUPRC** is the primary metric. It asks whether positives are ranked ahead
  of negatives. On imbalanced data, random AUPRC equals the positive rate. For
  `pooled_ood`, that is **412 / 1101 = 0.374**.
- **AUROC** is secondary. It has a 0.5 random floor and is useful for comparing
  with other work, but it is less informative under class imbalance.
- **95% confidence intervals** show uncertainty around the number.
- **Recall at FPR <= 1%** asks how many attacks are caught when false alarms are
  tightly limited.
- **ECE and Brier** are calibration errors. Lower is better.

The project reports effect sizes and confidence intervals, not p-values.

## 6. Headline Result

No evaluated detector clearly beats the pooled OOD random floor under AUPRC.

| Detector | Pooled OOD AUPRC | 95% CI | Read |
|---|---:|---:|---|
| ModernBERT frozen probe | **0.364** | [0.354, 0.375] | best in-house score, but at the random floor |
| ProtectAI v1 | 0.361 | [0.330, 0.391] | similar, but diagnostic only |
| ProtectAI v2 | 0.314 | [0.283, 0.345] | does not dominate v1 |
| ModernBERT LoRA | 0.293 | [0.286, 0.301] | fine-tuning hurt OOD ranking |
| TF-IDF + LR | 0.291 | [0.283, 0.298] | classical floor, roughly tied with LoRA |

The negative result is the point. A detector can look reasonable on
direct-injection-style examples and still fail when the attack family changes.

For exact grids, figures, and artifact links, see [Results](RESULTS.md).

## 7. Main Findings

### Finding 1: The OOD wall is cross-family

The OOD slices are not just new copies of the training data. They include
indirect injection, agentic-flow attacks, jailbreak-style questions, and benign
text that resembles injection text. Direct-injection training does not transfer
cleanly to those families.

### Finding 2: Fine-tuning hurt OOD generalization

LoRA scored **0.293** on pooled OOD, compared with **0.364** for the frozen
probe and **0.291** for TF-IDF + LR. The frozen probe keeps the pretrained
backbone signal; LoRA specializes to the direct-injection training pool and
loses much of that signal.

### Finding 3: Published detector versions are slice-dependent

ProtectAI v2 improves over v1 on JBB but regresses on XSTest and pooled OOD.
The practical lesson is not "v1 is better"; it is that detector updates should
be evaluated against the actual slice mix that matters.

### Finding 4: Validation thresholds are fragile

The detection policy tunes a threshold on validation to target FPR <= 1%. On
held-out test sources, TF-IDF + LR averages 6.7% FPR and LoRA averages 11.5%
FPR. The frozen probe holds the FPR target but catches only about 6% of
positives. That is characterization, not a deployable operating point.

## 8. What The Plots Say

The reviewer-facing plot slate in [Results](RESULTS.md) is now generated only
from canonical artifacts:

- F1 shows pooled OOD AUPRC against the random floor.
- F2 shows paired frozen-probe vs LoRA deltas on comparable both-class slices.
- F3 shows which slices have defined AUPRC and which are single-class `N/A`.
- F4 shows validation-threshold transfer failure.
- F5 shows calibration error by detector.

Each `docs/plots/F*.meta.json` sidecar records `data_mode: canonical`, the
source artifact, ADR-062, commit SHA, and generation time.

## 9. Methodology In One Paragraph

The evaluation uses source-disjoint splits, deduplication, leakage checks,
per-row prediction persistence, bootstrap confidence intervals, paired
comparisons, calibration metrics, and validation-only threshold selection. The
generic evaluation primitives come from
[eval-toolkit](https://github.com/brandon-behring/eval-toolkit); this repo
contains project-specific data, training, scoring, and writeup glue.

## 10. Limits And Next Steps

These results should not be read as a complete safety claim. A deployment
context involving multilingual attacks, encoded payloads, paraphrases,
adversarial perturbations, or multi-turn tool-use needs additional data and
evaluation. The most useful next steps are OOD-aware training data, stronger
backbone comparisons, and OOD-aware threshold selection.

See [limitations and future work](./WRITEUP/limitations-and-future-work.md) for
the full version.
