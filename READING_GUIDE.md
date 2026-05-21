---
title: "Reading guide"
description: "How to read the prompt-injection classifier evaluation at different depths."
---

# Reading Guide

The site is organized from least to most technical. Start with the result, then
drill into evidence and methodology only as needed.

## Result Map

Use this map when scanning the project for what was actually accomplished. Each
row points to the deeper table and states why the result matters.

| Finding | Where to read | What the result says | Why it matters or is limited |
|---|---|---|---|
| Direct validation | [Results: Direct Prompt-Injection Performance](RESULTS.md#direct-prompt-injection-performance) | LoRA reaches 0.974 AUPRC / 0.993 AUROC / 0.934 recall@0.5 on balanced direct+benign validation; TF-IDF + LR is similar | confirms the detector stack learned direct prompt-injection patterns |
| Held-out direct-source recall | [Results: Direct Prompt-Injection Performance](RESULTS.md#direct-prompt-injection-performance) | frozen probe recall@0.5 is 0.641, LoRA is 0.625, full fine-tune\*\* is 0.558 | stricter direct-source holdout, but recall-only because the slice is all-positive |
| Pooled OOD failure | [Results: §1 Cross-Family OOD Table](RESULTS.md#1-cross-family-ood-table-auprc) | best pooled OOD AUPRC is 0.364 against a random floor of 0.374 | main scientific finding: direct-trained detectors do not beat guessing under family shift |
| LoRA vs frozen-probe OOD degradation | [Results: §2 Frozen Probe vs LoRA](RESULTS.md#2-frozen-probe-vs-lora) + [§6 AUROC](RESULTS.md#6-secondary-table-auroc) | LoRA pooled OOD AUROC **0.383 below 0.5 floor**; -0.071 AUPRC vs frozen probe | lexical overfitting + slate-induced label-relevance inversion; CIs clear 0.5 on the wrong side |
| DeBERTa context-window null result | [Results: §1B Ablation](RESULTS.md#1b-ablation-does-a-longer-context-backbone-fix-the-ood-gap) | chunk-and-average scores 0.291 pooled OOD AUPRC; head-truncation scores 0.290 | longer context access did not explain the OOD gap; backbone effects remain |
| Threshold transfer failure | [Results: §4 Threshold Transfer](RESULTS.md#4-threshold-transfer) | LoRA catches more positives but jumps to 11.5% test FPR under a 1% validation-FPR policy | validation thresholds are characterization, not deployment recommendations |
| Calibration ranking | [Results: §5 Calibration](RESULTS.md#5-calibration) | frozen probe has the lowest mean ECE (0.144) and Brier (0.265) | score quality and direct-pattern accuracy diverge under OOD shift |
| ProtectAI/reference-detector caveats | [Results: §1 Cross-Family OOD Table](RESULTS.md#1-cross-family-ood-table-auprc) and [reference-scorer audit](WRITEUP/reference-scorer-audit.md) | ProtectAI v1\* is near frozen probe on pooled OOD; v2\* regresses on this slate | useful diagnostic references, but training-overlap disclosure limits clean baseline claims |

\* ProtectAI v1 + v2 were trained on at least 2 of 4 LODO training-pool sources
per [EVIDENCE](EVIDENCE.md) §1-2. Their pooled OOD scores on overlapping slices
are not clean OOD baselines.

\*\* Full-FT shows LODO direct-source data only (24 Phase 2 predictions); the
comparable pooled OOD inference was not run (Phase 5 X11 crash; see
[ADR-075](decisions/ADR-075-full-ft-ood-drop-rationale-unified-narrative.md)).

## Path A: Hiring Manager, 10-15 Minutes

Goal: understand the problem, the result, and what the project demonstrates.

1. [Landing page](index.qmd): problem, setup, headline result, limits.
2. [Project at a glance](docs/for-hiring-managers.md): 60-second
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

**LoRA being below the floor matters.** Fine-tuning on the direct-injection
training pool reduced pooled OOD AUPRC from 0.364 to 0.293. The sharper finding
is under AUROC: LoRA scores 0.383 [0.374, 0.392], below the 0.5 random floor.
TF-IDF + LR shows the same pattern at 0.371. CIs on both clear 0.5 on the
wrong side; only the frozen probe stays above floor at 0.515. The mechanism
is **lexical overfitting + a label-relevance shift** on the OOD slate ---
NotInject (benign text engineered to look like direct injection) inverts the
negative class; indirect/agentic attacks (no direct-injection lexical signal)
invert the positive class. The lexical signal is internally consistent; it
just stops tracking attack class on cross-family slices.

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

- Current state:
  [`tree/v1.2.8`](https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.2.8)
  (2026-05-19) --- live-site source
- Original submission tag:
  [`tree/v1.0.0`](https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.0.0)
  (2026-05-18) --- preserved as historical reviewer pin per ADR-033
- Live rendered site:
  <https://brandon-behring.github.io/prompt-injection-detection-prototype/>
- HF Hub checkpoints:
  [frozen probe](https://huggingface.co/BBehring/prompt-injection-frozen-probe)
  and [LoRA](https://huggingface.co/BBehring/prompt-injection-lora)
