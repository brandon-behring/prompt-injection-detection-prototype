---
title: "Results: tables, figures, and source artifacts"
description: "Canonical results page for the prompt-injection classifier evaluation."
---

# Results

This page is the evidence layer behind the landing page. It gives exact values,
five canonical figures, and pointers to the raw artifacts that produced them.

> *How to read this page*: scan the **Metric Primer** (§Metric Primer below) if AUPRC or confidence intervals are new. Then **§1 Primary Table** is the headline number; **§1B** answers the natural follow-up question (does a bigger backbone fix the OOD gap?); **§2–§5** drill into the specific findings (frozen-probe vs LoRA delta; per-slice view; threshold transfer; calibration). **§6 AUROC** is reported for comparison with prior work. **§7 Raw Artifacts** is for readers who want to verify or extend the analysis.

## Metric Primer

- **AUPRC** is the primary metric. It measures whether positives are ranked
  ahead of negatives. On imbalanced data, a random ranking scores the positive
  rate. For the pooled out-of-distribution (OOD) slice, `pooled_ood`, that
  floor is **412 / 1101 = 0.374**.
- **AUROC** is secondary. Its random floor is always 0.5, but it can make
  imbalanced tasks look better than they are.
- **Recall at FPR <= 1%** asks: if we allow at most 1 false alarm per 100 benign
  examples, how many attacks are caught?
- **95% CI** shows uncertainty. A narrow interval supports a sharper claim; an
  interval crossing an important baseline means the claim is weak.
- **ECE and Brier** are calibration errors. Lower is better.

## 1. Primary Table: AUPRC

Source: `evals/bootstrap/marginal_cells.parquet`, seed=1, BCa bootstrap with
10000 resamples. Single-class slices are marked `N/A` because AUPRC requires
both positives and negatives.

> *Reading this table*: the headline column is **Pooled OOD AUPRC** (the rightmost binary-class column with both positives and negatives). A random ranking on Pooled OOD scores ≈ **0.374** — any detector at or below that floor is not clearly better than guessing. Per-slice columns (JBB, XSTest) refine the picture: a detector might be strong on one OOD family and weak on another. **What to look at**: (1) the magnitude of pooled OOD AUPRC vs the random floor; (2) the width of the 95% CI (a wide CI means low statistical confidence in the point estimate); (3) the cross-detector ordering on pooled OOD.

| Detector \ Slice | JBB (100p/100n) | XSTest (200p/250n) | Pooled OOD (412p/689n) | BIPIA | InjecAgent | NotInject |
|---|---:|---:|---:|---:|---:|---:|
| ModernBERT frozen probe | 0.552 [0.520, 0.580] | 0.468 [0.448, 0.486] | **0.364 [0.354, 0.375]** | N/A | N/A | N/A |
| ProtectAI v1 | 0.519 [0.437, 0.597] | 0.469 [0.415, 0.523] | 0.361 [0.330, 0.391] | N/A | N/A | N/A |
| ProtectAI v2 | 0.556 [0.453, 0.648] | 0.382 [0.333, 0.429] | 0.314 [0.283, 0.345] | N/A | N/A | N/A |
| ModernBERT LoRA | 0.535 [0.504, 0.563] | 0.467 [0.447, 0.486] | 0.293 [0.286, 0.301] | N/A | N/A | N/A |
| TF-IDF + LR | 0.470 [0.443, 0.496] | 0.395 [0.379, 0.410] | 0.291 [0.283, 0.298] | N/A | N/A | N/A |
| Random floor | 0.500 | 0.444 | 0.374 | undefined | undefined | undefined |

**Takeaway:** the best pooled OOD AUPRC is the frozen probe at 0.364, but the
random floor is 0.374. The honest reading is that none of these detectors clearly
learned the cross-family OOD ranking problem.

![F1: Pooled OOD AUPRC vs random floor](docs/plots/F1.svg)

**What F1 shows:** exact pooled OOD AUPRC values with 95% CIs and the random
floor.

**What F1 does not show:** deployment readiness, per-slice behavior, or whether
single-class slices were caught at a fixed threshold.

## 2. Frozen Probe vs LoRA

The frozen probe uses the pretrained ModernBERT backbone without task-specific
weight movement. LoRA fine-tunes a small adapter on the direct-injection
training pool. If fine-tuning helped OOD, LoRA should beat the frozen probe.
It does not.

| Comparison | Slice | Metric | LoRA - frozen probe | 95% CI | Read |
|---|---|---|---:|---:|---|
| LoRA vs frozen probe | JBB | AUPRC | -0.016 | [-0.024, -0.009] | LoRA worse |
| LoRA vs frozen probe | XSTest | AUPRC | -0.001 | [-0.006, 0.004] | indistinguishable |
| LoRA vs frozen probe | Pooled OOD | AUPRC | -0.071 | see marginal table | LoRA much worse |

![F2: Frozen probe vs LoRA paired deltas](docs/plots/F2.svg)

**What F2 shows:** paired-bootstrap AUPRC differences for the comparable
both-class slices available in `evals/bootstrap/paired_cells.parquet`.

**What F2 does not show:** a paired pooled OOD CI, because the persisted paired
artifact does not include that pooled comparison; the pooled delta above is the
difference between marginal point estimates.

## 3. Per-Slice View

The OOD slate is deliberately not one homogeneous test set:

- **JBB**: jailbreak-style harmful elicitation, both classes.
- **XSTest**: jailbreak-as-question style, both classes.
- **BIPIA**: indirect injection, all positive.
- **InjecAgent**: agentic-flow injection, all positive.
- **NotInject**: benign text that looks injection-shaped, all negative.

![F3: Per-slice AUPRC grid](docs/plots/F3.svg)

**What F3 shows:** where AUPRC is defined, the detectors cluster near the random
floor on pooled OOD.

**What F3 does not show:** AUPRC/AUROC for all-positive or all-negative slices;
those metrics are mathematically undefined there. Raw predictions still exist
for alternative analyses.

## 4. Threshold Transfer

The detection policy tunes a threshold on validation to target **FPR <= 1%**.
That target does not reliably transfer to held-out test sources.

| Detector | Mean threshold | Test recall | Test FPR | Read |
|---|---:|---:|---:|---|
| ModernBERT frozen probe | 0.829 | 0.063 | 0.010 | holds FPR, catches very little |
| ModernBERT LoRA | 0.795 | 0.424 | 0.115 | catches more, but far exceeds FPR target |
| TF-IDF + LR | 0.657 | 0.333 | 0.067 | exceeds FPR target |

![F4: Detection-threshold transfer](docs/plots/F4.svg)

**What F4 shows:** the validation-tuned 1% FPR policy does not become a robust
test-time operating point under source shift.

**What F4 does not show:** a recommended production threshold. Deployment is out
of scope.

## 5. Calibration

Calibration asks whether scores behave like probabilities. A model that gives
0.90 scores should be correct about 90% of the time in that score region.

| Detector | Mean ECE | Mean Brier | Read |
|---|---:|---:|---|
| ModernBERT frozen probe | **0.144** | **0.265** | best calibrated |
| TF-IDF + LR | 0.350 | 0.376 | weaker but better than LoRA |
| ModernBERT LoRA | 0.444 | 0.451 | fine-tuning worsens calibration |
| ProtectAI v1 | 0.452 | 0.470 | poorly calibrated on this slate |
| ProtectAI v2 | 0.460 | 0.471 | poorly calibrated on this slate |

![F5: Calibration comparison](docs/plots/F5.svg)

**What F5 shows:** frozen probe has the lowest calibration error; LoRA's scores
are much less probability-like on this OOD evaluation.

**What F5 does not show:** whether post-hoc calibration would fix the
cross-family ranking failure.

## 6. Secondary Table: AUROC

AUROC is reported for comparison with other work, but AUPRC is the headline
metric because this task is imbalanced.

| Detector \ Slice | JBB | XSTest | Pooled OOD | BIPIA | InjecAgent | NotInject |
|---|---:|---:|---:|---:|---:|---:|
| ModernBERT frozen probe | 0.542 [0.520, 0.565] | 0.537 [0.522, 0.552] | **0.515 [0.505, 0.525]** | N/A | N/A | N/A |
| ModernBERT LoRA | 0.528 [0.505, 0.552] | 0.530 [0.515, 0.546] | 0.383 [0.374, 0.392] | N/A | N/A | N/A |
| TF-IDF + LR | 0.445 [0.422, 0.469] | 0.451 [0.436, 0.466] | 0.371 [0.362, 0.381] | N/A | N/A | N/A |
| ProtectAI v1 | 0.533 [0.464, 0.602] | 0.544 [0.497, 0.589] | 0.440 [0.409, 0.469] | N/A | N/A | N/A |
| ProtectAI v2 | 0.594 [0.512, 0.671] | 0.391 [0.341, 0.442] | 0.402 [0.369, 0.437] | N/A | N/A | N/A |
| Random floor | 0.500 | 0.500 | 0.500 | undefined | undefined | undefined |

## 7. Raw Artifacts

If you want to verify the numbers above or do your own slice / threshold / calibration analysis, the raw evaluation artifacts are committed under `evals/`. You do not need these to understand the results — the tables and figures above are sufficient — but they are here if you want to audit the math, re-render the figures, or extend the analysis. All five figures (F1–F5) record their source-artifact paths in the per-figure `.meta.json` sidecars next to the SVGs in `docs/plots/`.

| Artifact | Role |
|---|---|
| `evals/bootstrap/marginal_cells.parquet` | AUPRC/AUROC point estimates and marginal CIs |
| `evals/bootstrap/paired_cells.parquet` | paired-bootstrap detector-vs-detector differences |
| `evals/metrics/per_cell.parquet` | per-detector, per-fold, per-seed metrics including ECE and Brier |
| `evals/operating_points/dual_policy.parquet` | validation-fitted detection and verification thresholds |
| `evals/predictions/` | per-row predictions used by downstream analyses |

Each figure sidecar under `docs/plots/F*.meta.json` records `data_mode:
canonical`, ADR-062, the source artifact path, commit SHA, and generation time.

## Cross-References

- [Executive summary](EXECUTIVE_SUMMARY.md): one-page version.
- [Writeup](WRITEUP.md): methodology narrative.
- [Evaluation design](WRITEUP/eval-design.md): detailed metric rationale.
- [Threshold policy](WRITEUP/threshold-policy.md): detection and verification
  operating-point methodology.
- [Reference-scorer audit](WRITEUP/reference-scorer-audit.md): ProtectAI
  contamination caveats.
