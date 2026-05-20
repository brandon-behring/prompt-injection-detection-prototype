---
title: "Reading guide"
description: "How to read the prompt-injection classifier evaluation at different depths."
---

# Reading Guide

The site is organized from least to most technical. Start with the result, then
drill into evidence and methodology only as needed.

## Path A: Hiring Manager, 10-15 Minutes

Goal: understand the problem, the result, and what the project demonstrates.

1. [Landing page](index.qmd): problem, setup, headline result, limits.
2. [For hiring managers in a hurry](docs/for-hiring-managers.md): 60-second
   version of the problem, finding, trust basis, and candidate signal.
3. [Results](RESULTS.md): skim Direct Prompt-Injection Performance and the
   Cross-Family OOD table together.
4. [Executive summary](EXECUTIVE_SUMMARY.md): one-page version if you want a
   slightly fuller decision-maker view.

What to take away: this is an honest two-sided result. Direct prompt-injection
detection works on balanced validation, but that learned signal does not
clearly transfer to different attack families.

## Path B: Technical Reviewer, 45-60 Minutes

Goal: decide whether the result is methodologically credible.

1. [Results](RESULTS.md): exact tables and canonical figures.
2. [Writeup](WRITEUP.md): methodology hub.
3. [Evaluation design](WRITEUP/eval-design.md): metric and CI rationale.
4. [Data decisions](WRITEUP/data-decisions.md): source slate, dedup, leakage.
5. [Reference-scorer audit](WRITEUP/reference-scorer-audit.md): ProtectAI
   contamination caveats.
6. [Decisions](decisions/README.md): ADR trail, especially ADR-016, ADR-022,
   ADR-050, ADR-052, and ADR-062.

## Path C: Reproduce, 30+ Minutes

Goal: check that the numbers can be regenerated.

```bash
make install
make test-smoke
make eval-from-hub RUNG=frozen-probe
make eval-from-hub RUNG=lora
make site
```

For the full cloud path, see [reproducibility](WRITEUP/reproducibility.md).

## Path D: Static Analysis Appendices, 20-30 Minutes

Goal: inspect the rendered per-cell results, calibration, and OOD slice breakdowns.

Four Jupytext-paired notebooks ship as static rendered HTML appendices with frozen output cells (per ADR-053 reading-guide governance + v1.0.7). Each is reachable from the sidebar **Notebooks** section on the rendered Quarto site:

1. [`01_canonical_results`](notebooks/01_canonical_results.ipynb) — headline AUPRC + AUROC per trained detector, with bootstrap CIs and the random-floor reference line.
2. [`02_frozen_vs_lora`](notebooks/02_frozen_vs_lora.ipynb) — 3-method cross-check (paired bootstrap deltas + DeLong + BH-FDR) on the frozen-probe vs LoRA gap.
3. [`03_calibration`](notebooks/03_calibration.ipynb) — temperature + isotonic + Platt + Beta calibration on per-detector scores; reliability diagrams.
4. [`04_ood_slate`](notebooks/04_ood_slate.ipynb) — per-OOD-slice AUPRC breakdown; identifies which sources drive the pooled-OOD gap.

The notebooks render to static HTML on the Quarto site without re-execution.
Operators regenerate the frozen outputs via `make notebooks` after pulling new
evaluation parquets.

## How To Read The Headline Numbers

**AUPRC is not measured against 0.5.** For the pooled out-of-distribution slice
(`pooled_ood`), random AUPRC is the positive rate: 412 positives / 1101 rows =
0.374. The frozen probe scores 0.364, so it is at the random floor, not clearly
above it.

**Out-of-distribution (OOD) means cross-family here.** The training data is
direct-injection-heavy. The OOD slate includes indirect injection,
agentic-flow injection, jailbreak-style questions, and benign text that
resembles attacks.

**LoRA getting worse matters.** Fine-tuning on the direct-injection training
pool reduced pooled OOD AUPRC from 0.364 to 0.293. That suggests the pretrained
backbone carried the useful OOD signal and the adapter specialized away from it.

**Reference scorers are diagnostic.** ProtectAI v1/v2 are useful comparison
points, but their training-data disclosure creates contamination caveats.

**Thresholds are not deployment recommendations.** The threshold analysis shows
how scores behave under two cost regimes. It does not select a production
policy.

## Repo Map

| Path | Contents |
|---|---|
| `index.qmd` | first-reader landing page |
| `EXECUTIVE_SUMMARY.md` | one-page summary |
| `RESULTS.md` | exact tables, figures, artifacts |
| `NEXT_STEPS.md` | completed carryforward log plus live future-work questions |
| `WRITEUP.md` | methodology hub |
| `WRITEUP/` | detailed methodology spokes |
| `docs/plots/` | canonical F1-F5 figures with metadata sidecars |
| `evals/` | metrics, bootstrap, operating points, predictions |
| `decisions/` | ADRs and decision provenance |
| `src/`, `scripts/`, `tests/` | implementation and tests |

## Submission Anchors

- Canonical source pin:
  [`tree/v1.0.0`](https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.0.0)
- Live rendered site:
  <https://brandon-behring.github.io/prompt-injection-detection-prototype/>
- HF Hub checkpoints:
  [frozen probe](https://huggingface.co/BBehring/prompt-injection-frozen-probe)
  and [LoRA](https://huggingface.co/BBehring/prompt-injection-lora)
