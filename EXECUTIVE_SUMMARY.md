---
title: "Executive summary — 1-page decision-maker layer over WRITEUP"
description: "1-page summary of the prompt-injection classifier methodology submission. Read this first; deep-readers continue to WRITEUP."
---

# Executive summary

**Project**: methodology + capability characterisation of a 5-rung
prompt-injection classifier ladder, evaluated under an honest OOD
slate. Spec-first SDD submission with 52 immutable ADRs (Michael
Nygard format). Reviewer URL pin:
[`tree/v1.0.0`](https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.0.0).
Live Quarto site:
[brandon-behring.github.io/prompt-injection-detection-prototype/](https://brandon-behring.github.io/prompt-injection-detection-prototype/).

## Thesis

Most prompt-injection detectors are evaluated on data that leaks
into training, so their reported OOD numbers don't tell you much.
A classifier that cross-validates on a single direct-prompt-
injection dataset is trivial to build, but it gives a poor read on
OOD performance and raises real leakage concerns. **The submission
is an attempt to build a fairer evaluation harness around that —
not to find the best model, but to lay the groundwork for fairer
evaluation** and to identify the weaknesses of both the trained
rungs and the published reference scorers.

## Headline claims

1. **The OOD wall is cross-family, not cross-source.** Training
   pool is 4 direct-injection sources (deepset/prompt-injections,
   Lakera/gandalf_ignore_instructions, Lakera/mosscap_prompt_injection,
   hackaprompt). The 5-slice OOD slate probes attack families
   *absent* from training: indirect injection via email-body context
   (BIPIA), multi-turn agentic-flow (InjecAgent), jailbreaks
   (JBB-Behaviors), and benign-but-injection-shaped texts
   (NotInject, XSTest). Direct-injection training performance does
   not translate.
2. **None of the rungs clears the `pooled_ood` positive-class
   prevalence baseline (0.374) under AUPRC** (range 0.291–0.364;
   frozen-probe best at 0.364). Random-predictor AUPRC equals the
   positive prevalence; the best trained rung still lands ~0.01
   *below* that baseline.
3. **Fine-tuning HURTS OOD generalization relative to the frozen
   probe.** LoRA's `pooled_ood` AUPRC delta vs frozen-probe is
   **-0.071** (paired-bootstrap CI clears zero); fine-tuning the
   head onto the LODO direct-injection pool actively degrades the
   pretrained ModernBERT-base embeddings on OOD. The pretrained
   backbone — not the LODO training pool — carries what little OOD
   generalization budget exists.
4. **ProtectAI v1 → v2 is not a monotone improvement** across the
   OOD slate: v2 beats v1 on jbb_behaviors (+0.037 AUPRC) and loses
   on xstest (-0.087 AUPRC). Off-the-shelf detector updates can
   regress on specific OOD distributions; downstream consumers
   should not assume v2 dominates v1 universally.

## What was characterised

5-rung ladder: TF-IDF + LR classical floor (`verified_disjoint`)
→ ModernBERT-base frozen-probe → ModernBERT-base LoRA (~1 %
trainable params) → ModernBERT-base full-FT (LODO only; OOD dropped
per ADR-052) → 2 reference scorers (ProtectAI v1 + v2;
`suspected_contamination`). Evaluated under: source-disjoint LODO
(4 folds × 3 seeds = 12 cells per rung), calibrated semantic dedup
(threshold 0.80; 50-pair golden holdout), post-split leakage scrub
(exact-hash + cosine ≥ 0.85), contamination-taxonomy audit per
Kapoor & Narayanan 2023 against the published reference scorers,
paired-bootstrap MDE on every reported CI (10K resamples × 2
seeds; 0/40 stability flags), dual-policy threshold characterisation
(detection FPR ≤ 1 %, verification recall ≥ 99 %; both with
reachability audit).

## What is deferred (out of scope per ADR-014)

Multi-turn agentic flows (named in test slate via InjecAgent to
quantify the gap; not detected by single-turn classifier scope),
encoded payloads (base64 / leetspeak / hex / Unicode confusables),
paraphrase attacks (semantic equivalents), adversarial perturbations
(gradient-guided / search-based evasion), cross-language coverage.
Full-FT OOD inference dropped per ADR-052 (methodological: LoRA
evidence + FUSE-EIO operational trigger); details in
[WRITEUP/limitations-and-future-work.md §8.1](./WRITEUP/limitations-and-future-work.md).

## Reading-path pointer (the 30-minute reviewer)

1. This summary.
2. [WRITEUP §1 Motivation + §1.5 Attack-type taxonomy + train/test composition](https://brandon-behring.github.io/prompt-injection-detection-prototype/WRITEUP.html).
3. [WRITEUP §Results headline characterisation](https://brandon-behring.github.io/prompt-injection-detection-prototype/WRITEUP.html#results) (cross-family framing + 4 claims).
4. [EVIDENCE.md](https://brandon-behring.github.io/prompt-injection-detection-prototype/EVIDENCE.html) — external-evidence audit trail (ProtectAI v1/v2 contamination findings).
5. [decisions/](https://brandon-behring.github.io/prompt-injection-detection-prototype/decisions/README.html) — 52-ADR governance trail (the deep cut; ADR-005, ADR-015–022, ADR-050, ADR-052 are the headline locks).

## Honest reading

This is a methodology + capability *characterisation*, not a
leaderboard claim. The headline finding — that the OOD wall is
cross-family and that fine-tuning consumes the OOD generalization
budget the pretrained backbone provides — is methodologically
richer than a "great classifier" framing would have allowed. A
deployment context that includes attack classes outside the
training pool (multi-turn agentic flows, encoded payloads,
paraphrase attacks, adversarial perturbations) cannot rely on
these numbers; the methodology spoke names what would need to
land to extend coverage.
