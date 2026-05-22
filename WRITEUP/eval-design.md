---
title: "Evaluation design"
description: "Statistical apparatus, OOD slate composition, single-class slice handling, and headline metric battery for the prompt-injection evaluation."
---

*Deep-dive reference for the methodology in [WRITEUP_PAPER.md](../WRITEUP_PAPER.md) (academic) and [WRITEUP_NARRATIVE.md](../WRITEUP_NARRATIVE.md) (narrative). Pick a guide for the cover narrative; this spoke goes deeper.*

> **How to read this spoke**: For a fast skim, focus on the bolded **Result** subsections + the final §Summary if present. For a full audit, read the methodology paragraphs + the ADR references in headers.

:::{.callout-note}
## Summary

- **Headline metric battery**: PR-AUC (primary; canonical for class-imbalanced ranking) + ROC-AUC (secondary; cross-paper) + recall@FPR at 0.1 %, 1 %, 5 % (1 % is canonical per PromptShield 2025) + ECE + Brier. BCa bootstrap CIs throughout.
- **Statistical stance**: report effect sizes and CIs. Do not rely on p-values. Modern preference in applied ML evaluation; aligned with [eval-toolkit](https://github.com/brandon-behring/eval-toolkit)'s primitive design.
- **Paired-bootstrap**: rung-vs-rung Δ-CIs preserve per-row pairing correlation without parametric assumptions (DeLong's, McNemar's). MDE reported alongside any CI that includes zero.
- **Per-source breakdowns**: mandatory for any OOD claim. The 5-slice OOD slate (`notinject` / `xstest` / `jbb_behaviors` / `bipia` / `injecagent`) probes false-positive robustness + cross-distribution + adversarial-elicitation + indirect injection + agentic-flow generalization.
- **Single-class slice convention**: BIPIA + InjecAgent are all-positive; NotInject is all-negative. AUROC + AUPRC are mathematically undefined on single-class slices; the metrics pipeline filters these out at source per ADR-006.
:::

This spoke covers §5.1, §5.2, §5.4, §5.5 — the evaluation framework,
statistical apparatus, per-source breakdown discipline, and OOD slate
composition. Threshold policy (§5.3) is its own spoke
([`threshold-policy.md`](./threshold-policy.md)); adversarial
robustness scope (§5.6) lives in the reference-scorer audit spoke
([`reference-scorer-audit.md`](./reference-scorer-audit.md)) since it
co-locates with the threat-model narrative.

This section is the heart of the writeup. Every test below is reported
with effect sizes and CIs — never p-values. The choice is
methodological: in finite-sample settings, *what is the effect and how
confident is the estimate* is the answerable question; *is this nonzero
at α=0.05* is a question whose answer depends on the sample size more
than the phenomenon.

## 5.1 Headline descriptive metrics

The headline metric battery reports with BCa bootstrap CIs:

- **PR-AUC** — the most relevant ranking metric for class-imbalanced
  tasks where precision and recall both matter. F1 alone is misleading
  at any chosen threshold; PR-AUC integrates over thresholds.
- **ROC-AUC** — reported alongside for class-prior-independent
  ranking. Less useful than PR-AUC under this task's class priors but
  standard for cross-paper comparison.
- **recall@FPR ∈ {0.1 %, 1 %, 5 %}** — operational pinpoints. The
  1 % point is the canonical reporting threshold (PromptShield 2025).
  The 0.1 % point is included in `evals/metrics/per_cell.parquet`
  per ADR-021 + ADR-023 volatility-surface protocol but is noisy at
  this project's sample sizes and not surfaced in headlines.
- **ECE (equal-mass + Kumar-2019 debiased) + Brier** — calibration;
  see §5.2 calibration battery below.

See eval-toolkit `comparison` methodology (see [README](https://github.com/brandon-behring/eval-toolkit#readme))
for why each metric is preferred over plain F1.

## 5.2 Statistical tests

**Result (Stance)**: report effect sizes and CIs. Do not rely on
p-values. This is the modern preference in applied ML evaluation and
is aligned with
[eval-toolkit](https://github.com/brandon-behring/eval-toolkit)'s
primitive design.

### Per-metric bootstrap CIs — `bootstrap_ci`

*Why*: a point estimate of PR-AUC hides finite-sample variance.
Without a CI, claiming rung A beats rung B is irresponsible — the gap
may be smaller than the sampling noise. Per-row resampling preserves
label distribution and avoids parametric assumptions.

Method: BCa bootstrap (Efron 1987 / Efron & Tibshirani 1993 §14);
resample budget per eval-toolkit guidance: n=200 sanity / n=1000
default / n=5000 publication-grade / n=10K+ only for expensive
metrics. Pinned seed; stability check at a second seed flags
instability if per-fold CI shifts > 0.01. **Report the point estimate,
not the resample mean** — `BootstrapCI.point_estimate` is the metric
on the *original* data. See
eval-toolkit `bootstrap` methodology (see [README](https://github.com/brandon-behring/eval-toolkit#readme)).

### Paired-bootstrap differences for rung-vs-rung — `paired_bootstrap_diff`

*Why*: when two rungs are evaluated on the same test set, their
per-row errors are correlated. Paired bootstrap accounts for that
correlation without requiring parametric assumptions like DeLong's.
One primitive covers AUC differences, recall@FPR differences, and
threshold-based differences uniformly — no need to mix DeLong +
McNemar + permutation tests. Non-overlapping CIs imply significance;
overlap does NOT imply non-significance — always compute the
difference CI.

Method: per-row pairing; matched resamples; CI on the paired Δ.
Reported wherever a comparative claim is made. Specialised variants
`paired_bootstrap_ece_diff` (ECE comparisons) and
`paired_bootstrap_op_point_diff` (two-level bootstrap for threshold
refitting) handle non-AUC paired metrics. `delong_roc_variance` is
available for sanity-check parametric ROC-AUC CIs (DeLong et al.
1988).

### MDE — `mde_from_ci`

*Why*: a wide CI that excludes "no difference" is still informative;
a wide CI that *includes* "no difference" can mean either "the rungs
are equivalent" or "the test lacks power to tell". MDE distinguishes
these. A claim of equivalence requires MDE small enough to rule out
the smallest meaningful difference.

Method: derive MDE from CI width at α=0.05, power=0.80. Report
alongside every CI that includes zero.

### Calibration battery

`reliability_curve` + `fit_temperature` + `fit_isotonic_calibrator`
+ `fit_platt_calibrator` + `fit_beta_calibrator` + ECE variants
+ Brier.

*Why*: even without a deployment goal, calibration tells you whether
the scores mean what they claim. A score of 0.9 should fire injections
~90 % of the time. ECE quantifies the gap; Brier is a proper scoring
rule that decomposes as `BS = REL − RES + UNC` (Murphy 1973), so two
models with same Brier may have very different operational profiles.
Reliability curves diagnose *where* miscalibration concentrates
(over-confident on the cleanest? under-confident on the most
ambiguous?). Temperature (Guo et al. 2017 ICML; single-parameter
logit scaling; argmax-invariant), isotonic, Platt (1999), and Beta
scaling are the standard post-hoc repairs, fit on validation only.

**ECE choice matters**: prefer L2-debiased ECE (Kumar et al. 2019,
arXiv:1909.10155) for headline reporting — preserves rank ordering
and removes small-sample inflation
(`expected_calibration_error_l2_debiased`). Equal-mass ECE
(`expected_calibration_error_equal_mass`) is more robust under class
imbalance via quantile binning (Naeini et al. 2015,
arXiv:1411.0760). **Pin `n_bins` across comparisons** — ECE is a
binned estimator; small bin counts understate, large bin counts
overstate.

See
eval-toolkit `calibration` methodology (see [README](https://github.com/brandon-behring/eval-toolkit#readme)).

### CV-CLT CI for cross-fold variance — `cv_clt_ci`

*Why*: when source-disjoint k-fold is run as a supplement, per-fold
metrics are not independent — train sets overlap across folds. A naive
standard-error treatment overstates confidence. CLT-based CI with
Bayle 2020 (Annals of Statistics) Theorem 3.1 correction handles the
dependence properly. See
eval-toolkit `splits` methodology (see [README](https://github.com/brandon-behring/eval-toolkit#readme)).

LODO non-exchangeability is a real assumption violation per
assumption A-008 — the `cv_clt_ci` primitive was derived for
exchangeable k-fold. Reporting consequence:
`evals/audit/cross_fold_ci_audit.parquet` reports both `cv_clt_ci`
CI and block-bootstrap-on-folds CI per rung; if the ratio
`block_bootstrap_CI_halfwidth / cv_clt_CI_halfwidth > 1.5`, the
spoke flags "LODO non-exchangeability dominates within-fold
variance" — turning the assumption violation into a named
methodology finding.

### Multi-comparison correction — `bh_fdr_correct`

*Why*: when comparing many rung-pairs simultaneously, family-wise
error inflates. Benjamini-Hochberg FDR (BH 1995) is preferred over
Bonferroni for power reasons in correlated-test families.

### Evidence gates — release-time go/no-go

*Why*: claims at submission need machine-checkable gates, not
implicit confidence. eval-toolkit's `claims.md` provides composable
gates: `metric_threshold_gate`, `low_fpr_feasibility_gate`,
`paired_diff_present_gate`, `no_leakage_errors_gate`, etc. The
`ClaimSpec` → `GateResult` → `ClaimReport` pipeline (v0.9+) gives a
release-gate manifest a reviewer can audit.

*§5.3 (Threshold policy — dual detection + verification) lives in its
own spoke at [`threshold-policy.md`](./threshold-policy.md) per the
locked sub-spoke structure in ADR-025.*

## 5.4 Per-source / per-style breakdown

*Why*: aggregate metrics hide heterogeneity. A 0.95 average PR-AUC
can mask a 0.6 PR-AUC on one source that is in fact the source you
care about. Per-source breakdowns are mandatory for any OOD claim
because OOD is defined by *which source* the test rows came from.

The project also ships a per-attack-style heuristic tagger
(regex-based; conservative). Tagger coverage on the LODO training
pool is **not exhaustively measured** in this submission — the
tagger is used at data-audit time per ADR-041 to spot-check coverage
of the four attack-source slates; per-row tag → per-cell coverage
rates ARE in `evals/data_audit.json` per-source breakdowns. See
[`../EVIDENCE.md`](../EVIDENCE.md) §3.

LLM-as-rater rubric audit was originally locked at Phase 0 per
ADR-018; DROPPED at Phase 4 cost re-estimation per ADR-050. The
50-pair LLM-pre-labelled dedup-calibration holdout
(`data/dedup_holdout.jsonl`) is the partial LLM-judge audit that
survived.

## 5.5 OOD slate

The 5-slice OOD slate per ADR-021 + ADR-016, populated at Phase 0-04
from `docs/research/benchmarks/` candidate set:

| Slice | Source | Class composition | Probe target | Why chosen |
|---|---|---|---|---|
| `notinject` | HF Hub `wikd/NotInject` (SHA pinned per source_manifest.yaml) | All-negative (benign-but-injection-like) | False-positive robustness on injection-shaped benign | Tests whether classifier discriminates *intent* from *form* |
| `xstest` | HF Hub `paul-rottger/xstest-v2-copy` | Both classes (safe/unsafe instructions) | Cross-distribution shift to jailbreak-as-question | Tests against an actively-different distribution from training |
| `jbb_behaviors` | HF Hub `JailbreakBench/JBB-Behaviors` | Both classes (harmful behavior elicitations + benign refusal) | Adversarial-elicitation generalization | Canonical jailbreak benchmark; community-recognized |
| `bipia` | Local git repo (release-pinned SHA in source_manifest.yaml) | All-positive (indirect prompt injection via email body) | Indirect injection generalization | Tests indirect-injection (BIPIA paper benchmark) |
| `injecagent` | Local git repo (release-pinned SHA in source_manifest.yaml) | All-positive (multi-turn agentic injection) | Agentic-flow generalization | Tests agentic-flow injection |

See
eval-toolkit `splits` methodology (see [README](https://github.com/brandon-behring/eval-toolkit#readme))
for the source-disjoint discipline this project applies.

**Result (Single-class slice convention)**: BIPIA + InjecAgent are
all-positive; NotInject is all-negative. AUROC and AUPRC are
mathematically undefined on single-class slices. The metrics pipeline
filters these slices out of AUROC / AUPRC artifacts at source
(per Item 4 of the v1.0.0 closure sweep — see
[WRITEUP_PAPER §6.2 Reference scorer contamination](../WRITEUP_PAPER.md#reference-scorer-contamination)
and [WRITEUP/limitations-and-future-work §8.2](./limitations-and-future-work.md#methodology-caveats));
per-slice recall-at-threshold is reported on single-class slices instead.

## Cross-references

- **Threshold policy (§5.3 dual-policy detection + verification)** → [`threshold-policy.md`](./threshold-policy.md)
- **Reference-scorer contamination audit + adversarial robustness scope** → [`reference-scorer-audit.md`](./reference-scorer-audit.md)
- **Data splits + LODO + leakage discipline** → [`data-decisions.md`](./data-decisions.md)
- **Methodology guarantees + library tooling** → [`methodology-guarantees.md`](./methodology-guarantees.md)
- **Headline results (interpretation)**: [WRITEUP_PAPER §4](../WRITEUP_PAPER.md#results) (academic) or [WRITEUP_NARRATIVE Act 3](../WRITEUP_NARRATIVE.md#act-3-revelation) (narrative)
- **Headline tables (data)**: [RESULTS §1](../RESULTS.md#cross-family-ood-table-auprc)

**Linked ADRs**: ADR-006 (headline metrics + statistical apparatus),
ADR-021 (slice aggregation + recall@FPR pinpoints), ADR-022 (paired-
bootstrap protocol), ADR-023 (calibration battery), ADR-024 (cross-
fold CI methodology), ADR-046 (Phase 4 analysis bundle).
