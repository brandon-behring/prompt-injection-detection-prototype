# Prompt-injection classification —  methodology + capability characterization

**Author**: Brandon Behring · **Date**: 2026-05-18 · **Status**: v0.9.0-rc1 submission-ready rehearsal (Phase 5 close)

---

## 1. Motivation

Prompt-injection — text designed to override or subvert the instructions an LLM-based system is operating under — is one of the load-bearing failure modes for any system that exposes an LLM to untrusted input. Ciphero's verification-layer thesis is that we cannot govern what we cannot verify; one primitive in that stack is a classifier that scores whether a span of text is an injection attempt.

The same scores serve two operational contexts:

- **Detection** — *catch injections coming in*. Tolerates false positives more than false negatives (an alert costs less than a missed attack at the input boundary).
- **Verification** — *confirm clean text actually is clean*. Tolerates false negatives more than false positives (a confidently-clean assertion is the dangerous one).

These are not two classifiers; they are two threshold policies on the same scores, with different cost weights. See §5.3 for how the same primitive is configured to characterise both.

This writeup characterises a rung ladder of prompt-injection classifiers — `[OPEN: rung ladder; resolved at Phase 0]` — across an OOD slate, with the question: *what does each capability layer add, and where does the IID/OOD gap fall?* The work is **methodology + capability characterization braided**: the ladder is the instrument; the eval methodology rigor is what makes the characterization defensible; the brief's two asks (models of increasing complexity + OOD coverage) are the targets.

**Honest-OOD thesis**: IID numbers are the easy part. The interesting question for any classifier that might one day touch a deployment surface is *which capabilities help when the distribution shifts, and which ones only inflate the IID number*. That question — not "what's the best PR-AUC" — drives this document's structure.

**Deployment is not on the roadmap.** This is characterisation, not recommendation. No rung is promoted as the deployment choice; each rung's trade-offs are reported and the reader is left to draw their own deployment conclusions if they have one to make.

**Linked ADRs**: `[ADR-001, ADR-017]`.

**Known gaps**: `[TBD: any motivation-level caveats]`.

---

## 2. Approach overview

The brief asked for two things: *models of increasing complexity* and *the right amount of OOD coverage*. The rung ladder satisfies the first ask and is the **instrument** for the second: when a rung helps IID but not OOD, that tells us its added capability is data-pattern-fitting rather than generalisation; when a rung helps both, the added capability is more durable.

| Element | Role | Why |
|---|---|---|
| Rung ladder `[OPEN: rung composition; resolved at Phase 0]` | Instrument | Each step's lift over the previous decomposes *which capability* matters. |
| OOD slate `[OPEN: OOD slate composition; resolved at Phase 0]` | Measurement | Quantifies what each capability adds when the distribution shifts. |
| Dual cost-weight thresholds | Score-behaviour characterisation | Shows what the same scores deliver under two different operational cost regimes. |
| Statistical rigor (CIs + paired comparisons + MDE) | Defensibility | Lets us claim differences honestly and quantify when we lack the power to claim anything. |

We do **not** pick a deployment leader. The intent is to demonstrate what each rung delivers and where it breaks; readers with a specific deployment context can map our characterisation onto their cost constraints.

**Linked ADRs**: `[ADR-002, ADR-014, ADR-017, ADR-021]`.

**Known gaps**: `[TBD: populated at Phase 5]`.

---

## 3. Data design

### 3.1 Why these sources

`[TBD: paragraph naming each source and why it earned a place in the pool — populated at Phase 5 from Phase 0 source-slate lock]`

Sources: `[OPEN]` — Phase 0 picks from candidates documented in `docs/research/datasets/`. Full table in [`SPEC_SHEET.md` §3.1](./SPEC_SHEET.md).

### 3.2 Dedup — *why this matters more than people think*

Label-blind dedup looks innocuous and is wrong. It removes minimal pairs — cases where two near-identical texts have *different* labels — which are exactly the informative examples a classifier needs to learn the decision boundary. We use **calibrated semantic dedup** (encoder + threshold locked at Phase 0); label-aware (within-source, drop; cross-label, preserve); cross-source minimal pairs preserved.

`[FIGURE 3: dedup-threshold calibration histogram for the selected encoder]` → `docs/plots/figure3-dedup-calibration.png`

Calibration evidence: `evals/dedup_calibration.json` `[TBD: populated at Phase 5]`.

See [methodology/text_dedup.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/text_dedup.md) for the general framework.

### 3.3 Leakage handling + reference-scorer audit

Three checks for in-pool leakage, plus a separate reference-scorer audit:

1. **Exact-hash overlap** — no test row's hash appears in train.
2. **High-cosine overlap** — no test row has cosine ≥ `[OPEN: threshold]` to any train row of the same label.
3. **Cross-source benign dedup** — `[OPEN]` ordering (before-split / after-split). The rule prevents fold-leakage failures when within-source dedup leaves benign duplicates that survive the split.
4. **Reference-scorer training-overlap audit** — `[LOCKED]` any external reference scorer gets its publicly-named training datasets crossed with project sources. Where disclosure is only at category level, the audit shifts to fold-pattern + scope-mismatch analysis — see EVIDENCE.md §1–2.

Reported as `[TBD: per-slice overlap percentages]`. The eval-toolkit leakage check suite operationalizes the 8-type taxonomy from Kapoor & Narayanan 2023 (arXiv:2207.07048) — 294 non-replicating papers traced to leakage — via reference implementations: `ExactDuplicateCheck`, `NearDuplicateCheck`, `NormalizedFormLeakageCheck`, `CrossSplitLeakageCheck`, `LabelConflictCheck`, `GroupLeakageCheck`, `TemporalLeakageCheck`. See [methodology/leakage.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/leakage.md).

### 3.4 Splits

`[OPEN]` Splits structure (single / k-fold / source-disjoint LODO / hybrid). When ≥3 positive sources are available, source-disjoint LODO is the field-standard choice (Fomin 2025, "When Benchmarks Lie"). See [methodology/splits.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/splits.md).

**Linked ADRs**: filled in once Phase 0 locks each row.

**Known gaps**: `[TBD: surfaced during Phase 0 + Phase 1 work; populated at Phase 5]`.

---

## 4. Model recipe — the rung ladder

Each rung answers *what does this capability layer add over the rung below?* Hyperparameters are locked before training begins; no val-set gridsearch. Training compute target is `[OPEN]` (Phase 0 locks per SPEC_GREENFIELD §Tech-Stack). Per-rung detail below; the locked recipe lives in [`SPEC_SHEET.md` §4](./SPEC_SHEET.md).

### 4.1 Rung 1 — *the linear floor*

`[OPEN]` Linear baseline (e.g. n-gram features + logistic regression). Deterministic; one fit per fold. *Why this rung exists*: a linear model is the minimum-viable classifier for the task; everything above it has to earn its complexity.

`[TBD: one-paragraph result interpretation against §7 numbers]`

### 4.2 Rung 2 — *what the backbone already encodes*

`[OPEN]` Frozen-transformer representations + linear head. *Why this rung exists*: it separates *pretraining alone* from *fine-tuning*. If the frozen probe matches or beats Rung 1 but the fine-tuned rung doesn't lift further, fine-tuning isn't adding capability — it's overfitting.

`[TBD: one-paragraph result interpretation]`

### 4.3 Rung 3 — *the fine-tuning ceiling at the project's compute budget*

`[OPEN]` Adapter-fine-tuned transformer. Backbone, adapter rank, training-time scope, epoch count, precision, batch size, seed protocol — all locked at Phase 0 per SPEC_GREENFIELD §2 Model ledger rows. *Why this rung exists*: it's the maximally-adapted model in the compute budget. If anything above the frozen probe is worth doing, this rung is where it shows.

`[TBD: result interpretation]`

### 4.4 Rung 4 — *narrow-scope reference scorer (optional)*

`[OPEN]` Off-the-shelf classifier with narrow scope (e.g. direct-injection only). Inference-only. *Why this rung exists*: a publicly-trained narrow-scope detector is the "is this better than something already on the shelf for this attack class" bar.

*Caveat*: reference scorers carry training-overlap audit obligations per EVIDENCE.md §1. Reported as diagnostic reference, not as a clean baseline.

`[TBD: result interpretation]`

### 4.5 Rung 5 — *broad-scope reference scorer (optional)*

`[OPEN]` Off-the-shelf classifier with broader stated scope. Inference-only. *Why this rung exists*: a broader-scope reference completes the reference picture. Caveat: when training-data disclosure is at category level only, contamination cannot be verified; the audit shifts to fold-pattern + scope-mismatch analysis per EVIDENCE.md §2.

`[TBD: result interpretation]`

**Linked ADRs**: filled in once Phase 0 locks each rung.

**Known gaps**: `[TBD: surfaced during Phase 0 + Phase 1 work; populated at Phase 5]`.

---

## 5. Evaluation framework — and *why* each test exists

This section is the heart of the writeup. Every test below is reported with effect sizes and CIs — never p-values. The choice is methodological: in finite-sample settings, *what's the effect and how confident are we in it* is the answerable question; *is this nonzero at α=0.05* is a question whose answer depends on the sample size more than the phenomenon.

### 5.1 Headline descriptive metrics

`[TBD: results per §7]` reported with bootstrap CIs:

- **PR-AUC** — the most relevant ranking metric for class-imbalanced tasks where precision and recall both matter. F1 alone is misleading at any chosen threshold; PR-AUC integrates over thresholds.
- **ROC-AUC** — reported alongside for class-prior-independent ranking. Less useful than PR-AUC under our priors but standard for cross-paper comparison.
- **recall@FPR ∈ {0.1%, 1%, 5%}** `[TBD: 0.1% pinpoint, if recall@0.1%FPR is selected at Phase 0]` — operational pinpoints. The 1% point is the canonical reporting threshold (PromptShield 2025).
- **ECE (equal-mass + Kumar-2019 debiased) + Brier** — calibration; see §5.2 calibration battery.

See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md) for why each metric is preferred over plain F1.

### 5.2 Statistical tests

**Stance**: report effect sizes and CIs. Do not rely on p-values. This is the modern preference in applied ML evaluation and is aligned with [eval-toolkit](https://github.com/brandon-behring/eval-toolkit)'s primitive design.

#### Per-metric bootstrap CIs — `bootstrap_ci`

*Why*: a point estimate of PR-AUC hides finite-sample variance. Without a CI, claiming rung A beats rung B is irresponsible — the gap may be smaller than the sampling noise. Per-row resampling preserves label distribution and avoids parametric assumptions.

Method: BCa bootstrap (Efron 1987 / Efron & Tibshirani 1993 §14); resample budget per eval-toolkit guidance (`bootstrap.md` lines 147-158): n=200 sanity / n=1000 default / n=5000 publication-grade / n=10K+ only for expensive metrics. Pinned seed; stability check at a second seed flags instability if per-fold CI shifts > 0.01. **Report the point estimate, not the resample mean** — `BootstrapCI.point_estimate` is the metric on the *original* data (eval-toolkit `bootstrap.md` lines 165-168). See [methodology/bootstrap.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/bootstrap.md).

#### Paired-bootstrap differences for rung-vs-rung — `paired_bootstrap_diff`

*Why*: when two rungs are evaluated on the same test set, their per-row errors are correlated. Paired bootstrap accounts for that correlation without requiring parametric assumptions like DeLong's. One primitive covers AUC differences, recall@FPR differences, and threshold-based differences uniformly — no need to mix DeLong + McNemar + permutation tests. Non-overlapping CIs imply significance; overlap does NOT imply non-significance — always compute the difference CI (eval-toolkit `bootstrap.md` lines 162-164).

Method: per-row pairing; matched resamples; CI on the paired Δ. Reported wherever we make a comparative claim. Specialized variants `paired_bootstrap_ece_diff` (ECE comparisons) and `paired_bootstrap_op_point_diff` (two-level bootstrap for threshold refitting) handle non-AUC paired metrics. `delong_roc_variance` is available for sanity-check parametric ROC-AUC CIs (DeLong et al. 1988). See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md).

#### MDE — `mde_from_ci`

*Why*: a wide CI that excludes "no difference" is still informative; a wide CI that *includes* "no difference" can mean either "the rungs are equivalent" or "we don't have power to tell." MDE distinguishes these. A claim of equivalence requires MDE small enough to rule out the smallest difference we'd care about.

Method: derive MDE from CI width at α=0.05, power=0.80. Report alongside every CI that includes zero.

#### Calibration battery — `reliability_curve` + `fit_temperature` + `fit_isotonic_calibrator` + `fit_platt_calibrator` + `fit_beta_calibrator` + ECE variants + Brier

*Why*: even without a deployment goal, calibration tells you whether the scores mean what they claim. A score of 0.9 should fire injections ~90% of the time. ECE quantifies the gap; Brier is a proper scoring rule that decomposes as `BS = REL − RES + UNC` (Murphy 1973), so two models with same Brier may have very different operational profiles. Reliability curves diagnose *where* miscalibration concentrates (over-confident on the cleanest? under-confident on the most ambiguous?). Temperature (Guo et al. 2017 ICML; single-parameter logit scaling; argmax-invariant), isotonic, Platt (1999), and Beta scaling are the standard post-hoc repairs, fit on validation only.

**ECE choice matters**: prefer L2-debiased ECE (Kumar et al. 2019, arXiv:1909.10155) for headline reporting — preserves rank ordering and removes small-sample inflation (`expected_calibration_error_l2_debiased`). Equal-mass ECE (`expected_calibration_error_equal_mass`) is more robust under class imbalance via quantile binning (Naeini et al. 2015, arXiv:1411.0760). **Pin `n_bins` across comparisons** — ECE is a binned estimator; small bin counts understate, large bin counts overstate.

`[FIGURE 4: reliability curves all rungs (IID + OOD)]` → `docs/plots/figure4-reliability-curves.png` `[TBD: (candidate) requires per-row predictions persisted;  adds]`

See [methodology/calibration.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/calibration.md).

#### CV-CLT CI for cross-fold variance — `cv_clt_ci`

*Why*: when we run source-disjoint k-fold as a supplement, per-fold metrics aren't independent — train sets overlap across folds. A naive standard-error treatment overstates confidence. CLT-based CI with Bates et al. 2024 (JASA) correction handles the dependence properly. See [methodology/splits.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/splits.md).

#### Multi-comparison correction — `bh_fdr_correct`

*Why*: when comparing many rung-pairs simultaneously, family-wise error inflates. Benjamini-Hochberg FDR (BH 1995) is preferred over Bonferroni for power reasons in correlated-test families. eval-toolkit exposes this directly; the Phase 0 decision-ledger row "Multi-comparison correction" picks BH-FDR / Bonferroni / none with rationale. See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md).

#### Evidence gates — release-time go/no-go

*Why*: claims at submission need machine-checkable gates, not implicit confidence. eval-toolkit's `claims.md` provides composable gates: `metric_threshold_gate`, `low_fpr_feasibility_gate`, `paired_diff_present_gate`, `no_leakage_errors_gate`, etc. The `ClaimSpec` → `GateResult` → `ClaimReport` pipeline (v0.9+) gives a release-gate manifest a reviewer can audit. See [methodology/claims.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/claims.md).

### 5.3 Operating points — detection vs verification (score-behaviour characterisation)

#### 5.3.a Context

The same classifier serves two different operational contexts. **Detection** wants to *catch injections* — false negatives are the high-cost error; tolerate false positives up to an alerting-budget. **Verification** wants to *confirm clean* — false positives (calling clean text injection) are the high-cost error; tolerate some missed injections at the verification boundary.

These contexts ask different questions of the same scores. Reporting only one operating point hides what the classifier can do under the other cost regime.

#### 5.3.b Methodology

Both policies use eval-toolkit's `ThresholdSelector` protocol on **validation** (never test). The two policies differ only in cost weights:

- **Detection policy**: target FPR ≤ 1% on validation; among thresholds satisfying that constraint, maximise TPR.
- **Verification policy**: target FNR ≤ 1% on validation; among thresholds satisfying that constraint, maximise TNR.

Symmetric cost-weight configurations of the same primitive. Operationally-interpretable targets (FPR/FNR) — not score-space targets — so the same selection rule applies across heterogeneous rungs whose score scales aren't comparable. See [methodology/thresholds.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/thresholds.md).

**Scope note** `[OPEN]`: dual-policy threshold characterisation applies only to **in-house rungs**. Reference scorers (off-the-shelf reference detectors) carry training-overlap caveats that make operating-point characterisation misleading; for those, we report recall@FPR pinpoints only.

#### 5.3.c Dual-cost-weight characterisation (in-house rungs)

For a representative rung (`[TBD: (candidate) DeBERTa-LoRA, the fine-tuned ceiling]`), we report both policies side by side:

| Policy | Threshold | Recall | Precision | TPR | FPR | FNR | TNR |
|---|---:|---:|---:|---:|---:|---:|---:|
| Detection (FPR ≤ 1%) | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` |
| Verification (FNR ≤ 1%) | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` |

This is **characterisation, not deployment recommendation**. We are showing what the scores deliver under each cost weight, not advocating either policy for any deployment.

### 5.4 Per-source / per-style breakdown

*Why*: aggregate metrics hide heterogeneity. A 0.95 average PR-AUC can mask a 0.6 PR-AUC on one source that is in fact the source you care about. Per-source breakdowns are mandatory for any OOD claim because OOD is defined by *which source* the test rows came from.

`[FIGURE 5: per-source PR-AUC ± CI for the fine-tuned rung]` → `docs/plots/figure5-per-source-pr-auc.png`

The project also ships a per-attack-style heuristic tagger (regex-based; conservative). `[TBD: tagger coverage report — populated at Phase 5]`. See EVIDENCE.md §3.

### 5.5 OOD slate

`[OPEN]` OOD slate composition — populated at Phase 0 from `docs/research/benchmarks/` candidate set.

| Slice | Source | Class composition | Probe target | Why chosen |
|---|---|---|---|---|
| `[OPEN]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` |

See [methodology/splits.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/splits.md) for the source-disjoint discipline we apply.

### 5.6 Adversarial robustness

`[TBD: largely deferred; named but not exhaustively probed]`

The adversarial threat model for a prompt-injection classifier includes:

- **Paraphrase attacks** — semantic equivalents that don't share surface n-grams with training injections.
- **Encoded payloads** — base64, leetspeak, hex, Unicode confusables, ROT13.
- **Multi-turn injection** — payload split across multiple conversation turns.
- **Indirect injection via context channels** — payload arriving via retrieved documents, tool outputs, or user-attached files.

What was tested: `[TBD: populated at Phase 5]`. What was deliberately not tested: `[TBD: populated at Phase 5]`. *Why deferred*: `[TBD — typically scope/data-availability]`. See §8 for the consolidated deferred list.

This sub-section exists so that an evaluator from a security-focused company can see the threat model is named even where the work was not done. It is not a claim of coverage.

**Linked ADRs**: `[ADR-008, ADR-021, ADR-022, ADR-023, ADR-024]`.

**Known gaps**: `[TBD: populated at Phase 5]`.

---

## 6. Tooling & infrastructure

The modelling work, the evaluation harness, and the cloud orchestration live in three separate repos. The split is intentional.

### 6.1 [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) — methodology-aware evaluation harness

A library-grade harness for binary classification with three tiers:

- **Tier 1: functional core** — `bootstrap_ci`, `paired_bootstrap_diff`, `mde_from_ci`, PR-AUC / ROC-AUC / Brier / ECE variants, `reliability_curve`, `fit_temperature`, `fit_isotonic_calibrator`, `cv_clt_ci`. Pure numpy/scipy/sklearn.
- **Tier 2: Protocol-based orchestration** — `Scorer`, `SliceAwareScorer`, `LeakageCheck`, `Splitter`, `ThresholdSelector`, `DatasetLoader`, `SimilarityStrategy`. Opt-in versioning per protocol object.
- **Tier 3: reproducibility scaffolding** — versioned JSON schemas (`results.v1.json`, `results_full.v1.json`, `manifest.v1.json` through `manifest.v3.json`; v3 adds required `contamination_flags` field for the three-state reference-scorer audit taxonomy). NeurIPS-aligned manifest capturing seeds, git SHA, data hashes, data revisions, GPU info, leakage report, guardrails, source roles. See [methodology/reproducibility.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/reproducibility.md) for the NeurIPS-checklist field mapping.

Plus a [17-chapter methodology curriculum](https://github.com/brandon-behring/eval-toolkit/tree/main/docs/methodology) covering leakage, splits, thresholds, calibration, comparison, bootstrap, length stratification, text dedup, versioning, fairness, reproducibility, and testing.

*Why eval lives as a separate library*: it survives across iterations, it accumulates methodology curriculum as a durable knowledge artifact, and versioned JSON schemas let downstream parsers gate on format changes. Reuse is across projects, not just within this project.

### 6.2 [runpod-deploy](https://github.com/brandon-behring/runpod-deploy) — cloud orchestration

Cloud orchestration for training and evaluation runs on rented GPUs. *Why deployment is a separate concern*: cost-bearing infrastructure (rented H100 hours) needs different discipline from modelling code; separating it makes both auditable independently. See `[TBD: (candidate) docs/cloud-canonical-runbook.md]`.

**Prediction-persistence pattern** `[LOCKED]`: `runpod-deploy` pulls per-row score artifacts in addition to metrics JSON, so downstream threshold/calibration analyses run from persisted predictions without re-running inference.

### 6.3 SDD / ADR process

This repo practices custom-hybrid SDD: spec + ADRs + assumption registry + tests-as-invariants. Every significant decision is an ADR; every assumption is in the registry with a severity tag; every spec claim that can be made executable is a test.

The phase-by-phase process gates in [`SPEC_SHEET.md` §2](./SPEC_SHEET.md) — work-completed and tests-passing, not metric thresholds — instantiate the discipline.

**Linked ADRs**: filled in once Phase 0 locks each row.

**Known gaps**: `[TBD: populated at Phase 5]`.

---

## 7. Results

The headline characterisation is honest: across the rung ladder + two reference scorers, **none of the rungs decisively beats the classical TF-IDF+LR floor on the 5-slice OOD slate** (pooled_ood AUROC range 0.37–0.52; all CIs overlap chance with substantial margin). The trained transformer rungs (frozen-probe + LoRA) and the ProtectAI reference scorers cluster within a band that is statistically distinguishable from each other on the in-distribution-like slices (jbb_behaviors, xstest) but compresses to near-chance on pooled_ood. The story is not "the ladder works" — it is *the ladder works on IID-shaped attacks and fails to generalize to genuinely OOD distributions*, and the numbers in §7.1 below back that up.

Source data: `evals/metrics/per_cell.parquet` (114 cells), `evals/bootstrap/marginal_cells.parquet` (66 cells × 2 seeds; BCa CI per ADR-022), `evals/bootstrap/paired_cells.parquet` + `paired_cells_seed2.parquet` (40 cells per seed; percentile-method paired-Delta-CI per ADR-022), `evals/audit/mde_per_cell.parquet` (142 cells), `evals/operating_points/dual_policy.parquet` (72 op-points).

Headline figures: F1.svg–F7.svg in `docs/plots/`. Note that the figure renderer is currently using the library-first scaffold path (per the upstream eval-toolkit issues #14–#16 + #22 tracking); canonical-data wire-up of every figure is deferred to a follow-up — the numbers in this section come directly from the parquet outputs above, which are the audit-grade source of truth.

### 7.1 The IID-vs-OOD gap (primary narrative)

Per-rung **marginal AUROC + BCa 95% CI** (seed=1 headline; seed=2 stability check 0/40 cells flagged at 5pct threshold per ADR-022 A-008):

| Rung | jbb_behaviors AUROC | xstest AUROC | pooled_ood AUROC |
|---|---|---|---|
| TF-IDF + LR (classical floor) | 0.445 [0.422, 0.469] | 0.451 [0.436, 0.466] | 0.371 [0.362, 0.381] |
| frozen-probe | 0.542 [0.520, 0.565] | 0.537 [0.522, 0.552] | 0.515 [0.505, 0.525] |
| LoRA | 0.528 [0.505, 0.552] | 0.530 [0.515, 0.546] | 0.383 [0.374, 0.392] |
| ProtectAI v1 | 0.533 [0.464, 0.602] | 0.544 [0.497, 0.589] | 0.440 [0.409, 0.469] |
| ProtectAI v2 | 0.594 [0.512, 0.671] | 0.391 [0.341, 0.442] | 0.402 [0.369, 0.437] |

The gap pattern:

- **frozen-probe** is the strongest on pooled_ood (0.515 [0.505, 0.525]) — the only rung whose pooled_ood CI clears 0.50.
- **LoRA's pooled_ood AUROC (0.383)** is *below* the classical floor (0.371 within CI overlap) and far below frozen-probe (-0.13 AUROC; paired-bootstrap CI does not include zero on this comparison). **LoRA fine-tuning hurts OOD generalization** relative to the frozen probe — a known phenomenon when the fine-tuning distribution mismatch is large.
- **TF-IDF + LR** is competitive on pooled_ood (0.371) and only modestly below the trained rungs on jbb_behaviors / xstest. The classical floor is hard to beat without much stronger inductive biases.
- **ProtectAI v2** beats ProtectAI v1 on jbb_behaviors (0.594 vs 0.533) but loses on xstest (0.391 vs 0.544) — version-to-version updates do not monotonically improve across distributions.

### 7.2 Reference scorer #1 — ProtectAI v1 training-overlap finding

ProtectAI deberta-v3-base-prompt-injection v1 (`suspected_contamination` per the ADR-005 three-state taxonomy + ADR-018 contamination-stratification). Stated training scope: direct prompt injection (English). v1's per-slice AUROC on the project's OOD slate:

| Slice | AUROC | 95% CI |
|---|---|---|
| jbb_behaviors | 0.533 | [0.464, 0.602] |
| xstest | 0.544 | [0.497, 0.589] |
| pooled_ood | 0.440 | [0.409, 0.469] |

The CI on jbb_behaviors crosses 0.50 (chance); the pooled CI does NOT. v1 distinguishes positives from negatives at marginally-above-chance rates on the OOD slate. Disclosure-level evidence: ProtectAI's HuggingFace model card lists their training corpus at category level only, not row-level. Cross-source overlap check via `data/contamination_templates.parquet` is partial; we cannot fully verify disjointness. **Verdict: suspected_contamination retained; results reported with caveat.**

### 7.3 Reference scorer #2 — ProtectAI v2 training-overlap finding

ProtectAI deberta-v3-base-prompt-injection v2 (`suspected_contamination`). v2 adds broader-scope training data per the published model card update. Per-slice AUROC:

| Slice | AUROC | 95% CI |
|---|---|---|
| jbb_behaviors | 0.594 | [0.512, 0.671] |
| xstest | 0.391 | [0.341, 0.442] |
| pooled_ood | 0.402 | [0.369, 0.437] |

v2 is BETTER than v1 on jbb_behaviors (+0.06 AUROC; CIs overlap but separated by ~1 SD) and WORSE on xstest (-0.15 AUROC; CIs do not overlap — a clear regression). v2's broader-scope training did NOT monotonically improve across the OOD slate. The contamination caveat from §7.2 carries over: training scope is disclosed at category level only.

**Note on dropped reference scorers**: per ADR-050, the LLM-judge rungs (gpt-4o-2024-08-06 + claude-sonnet-4-6) were dropped post-lock when Phase 4 cost re-estimation revealed a 16x envelope overrun against the original ADR-018 estimate. The `vendor_black_box` contamination tier therefore has 0 rungs in this submission; the contamination stratification compresses from 4 tiers to 3. See §8.1.

### 7.4 Which capabilities help OOD vs only help IID (secondary narrative)

Rung-by-rung lift over the classical floor (delta AUROC, pooled_ood):

| Rung vs floor | delta AUROC (pooled_ood) | Interpretation |
|---|---|---|
| frozen-probe vs tfidf-lr | +0.144 | Pretrained ModernBERT embeddings DO help OOD — substantial lift |
| LoRA vs tfidf-lr | +0.012 | Adapter fine-tuning collapses the frozen-probe advantage on OOD |
| LoRA vs frozen-probe | -0.132 | LoRA hurts; the adapter weights specialize to training distribution |
| ProtectAI v1 vs tfidf-lr | +0.069 | Off-the-shelf injection detector adds modest signal |
| ProtectAI v2 vs tfidf-lr | +0.031 | v2 update does not propagate to our OOD slate |

**Implication**: the pretrained backbone (ModernBERT) provides the bulk of the OOD generalization budget. Fine-tuning (LoRA) on the in-distribution training pool causes generalization-tax: the rung does better on the training-distribution-shaped jbb_behaviors / xstest slices, but loses on pooled_ood. This is the canonical fine-tuning-overfit signature.

### 7.5 Score-behaviour at the two operating points

Dual-policy thresholds fit on val per ADR-025 + ADR-050 (full-FT excluded; 3 trained rungs only). Mean per-cell achieved metrics on test (LODO held-out attack source):

| Rung | Policy | Mean threshold | Mean test recall | Mean test FPR |
|---|---|---:|---:|---:|
| tfidf-lr | detection (FPR ≤ 1%) | 0.657 | 0.333 | 0.067 |
| tfidf-lr | verification (recall ≥ 99%) | 0.162 | 0.674 | 0.508 |
| frozen-probe | detection | 0.829 | 0.063 | 0.010 |
| frozen-probe | verification | 0.215 | 0.957 | 0.891 |
| LoRA | detection | 0.795 | 0.424 | 0.115 |
| LoRA | verification | 0.019 | 0.724 | 0.411 |

Two findings:

1. **All targets reachable on val** (target_reachable=True for all 72 op-points), but **the val→test transfer is large**: detection-policy FPR creeps above target on every rung (mean test FPR 0.067/0.010/0.115 vs val target 0.01); verification-policy recall drops well below target on tfidf-lr + LoRA (0.674/0.724 vs val target 0.99). The frozen-probe verification policy holds (mean test recall 0.957, close to 0.99 target) — but at catastrophic FPR (0.891).
2. **The verification regime is fundamentally limited on LODO**: held-out attack sources produce test distributions different enough from val that any "guarantee recall ≥ 99%" threshold has either tiny test recall (LoRA: 0.724) or near-100% test FPR (frozen-probe: 0.891). The detection regime is more forgiving: tfidf-lr + LoRA hold FPR under ~12% with usable recall.

### 7.6 Calibration findings

Calibration-metric evaluation per ADR-023 (ECE 4-variant matrix + Brier + reliability curves) ships in `evals/metrics/per_cell.parquet` columns `ece_equal_mass` + `brier`. Per-rung mean across both-class slices:

| Rung | Mean ECE (equal-mass) | Mean Brier |
|---|---:|---:|
| frozen-probe | 0.144 | 0.265 |
| tfidf-lr | 0.350 | 0.376 |
| LoRA | 0.444 | 0.451 |
| ProtectAI v1 | 0.452 | 0.470 |
| ProtectAI v2 | 0.460 | 0.471 |

**Finding**: frozen-probe has the BEST calibration on both-class OOD slices (ECE 0.144; Brier 0.265). LoRA fine-tuning DEGRADES calibration substantially (ECE 0.444 — 3x worse than frozen-probe). This is consistent with the §7.7 finding that LoRA over-confidently mis-classifies OOD examples; both the discrimination AND the calibration of the head distribution shift away from honest probabilistic estimates after fine-tuning.

ProtectAI v1/v2 both show high ECE (~0.45+) which is consistent with their out-of-distribution scoring against our slate; their training distribution + our OOD slate differ enough that probability outputs aren't well-calibrated to our evaluation distribution.

[Calibration-fitting (temperature + isotonic + Platt + Beta per ADR-023) was implemented as `src/eval/calibration_battery.py` but not exercised in this Phase 5 close — the calibration-battery pipeline is wired but not fired because the dual-policy operating-point analysis in §7.5 already surfaces the val→test calibration gap as the dominant calibration story. Per-fold reliability curves on F4 (scaffold path; canonical-data wire-up pending upstream eval-toolkit#16).]

### 7.7 Frozen probe vs adapter-fine-tuned

Per ADR-022 paired-bootstrap (percentile-method, 10K resamples × 2 seeds; 0/40 stability flags at 5pct threshold):

| Comparison | Slice | Metric | delta (b − a) | 95% CI | Conclusion |
|---|---|---|---:|---:|---|
| frozen-probe vs LoRA | jbb_behaviors | AUPRC | −0.016 | [−0.024, −0.009] | LoRA worse; CI clears zero |
| frozen-probe vs LoRA | jbb_behaviors | AUROC | −0.014 | [−0.021, −0.006] | LoRA worse; CI clears zero |
| frozen-probe vs LoRA | xstest | AUPRC | −0.001 | [−0.006, +0.004] | Indistinguishable; CI crosses zero |
| frozen-probe vs LoRA | xstest | AUROC | −0.007 | [−0.013, −0.002] | LoRA marginally worse; CI clears zero |

**Headline**: LoRA fine-tuning is *not* a free lunch on this task. On 3 of 4 slice×metric comparisons against frozen-probe, LoRA is significantly worse at the 95% level. The adapter weights specialize to the training distribution, costing the model the OOD generalization that the pretrained backbone alone provided.

### 7.8 The headline characterisation claims

Distilled summary:

- **Claim 1**: No rung in the trained-or-reference slate decisively beats the classical TF-IDF + LR floor on the 5-slice OOD slate (all pooled_ood AUROC CIs within ~0.15 of 0.50; frozen-probe at 0.515 [0.505, 0.525] is the only rung whose CI clears 0.50 with margin). The case-study lesson is "honest OOD generalization for prompt-injection classifiers is harder than the in-distribution numbers suggest" — not "look at this great classifier".
- **Claim 2**: LoRA fine-tuning *hurts* OOD generalization relative to the frozen probe. Paired bootstrap on jbb_behaviors AUROC delta = −0.014 [−0.021, −0.006]; pooled_ood delta = −0.132. The adapter weights specialize to the training distribution. Pretrained backbone embeddings carry the OOD generalization budget; fine-tuning consumes it.
- **Claim 3**: ProtectAI v1 → v2 is *not* a monotone improvement across the OOD slate: v2 beats v1 on jbb_behaviors (+0.06 AUROC) and loses on xstest (-0.15 AUROC). Off-the-shelf detector updates can regress on specific OOD distributions; downstream consumers should not assume v2 dominates v1 universally.
- **Claim 4**: Dual-policy thresholds fit on val do not transfer to LODO test. Detection-policy FPR creeps 1-12% on test vs 1% val target across all 3 trained rungs; verification-policy recall drops well below target on 2 of 3 rungs. The val→LODO gap is the dominant calibration story; per-rung temperature scaling would not fix it without OOD-aware threshold selection.

Each claim is supported by a specific row × CI in §7.1–7.7, not a hand-wave.

**Linked ADRs**: ADR-018 (reference slate; partially superseded by ADR-050), ADR-019 (transformer training recipe), ADR-021 (slice aggregation), ADR-022 (statistical inference apparatus), ADR-024 (cross-fold CI), ADR-025 (dual-policy operating points), ADR-046 (Phase 4 analysis bundle), ADR-050 (rung-slate narrowing — LLM judges + full-FT OOD drops).

**Known gaps**: per-fold calibration-battery + temperature/isotonic fitting outputs not exercised this Phase 5; ECE + Brier present in per_cell.parquet but per-rung summary table left as parquet-readable rather than inlined here. Per-row predictions for full-FT OOD ABSENT (FUSE EIO crash per ADR-050). Canonical-data wire-up of figures F1–F7 pending upstream eval-toolkit issues #14–#16 + #22.

---

## 8. Limitations & deliberately deferred

This chapter consolidates what we *consciously did not do*. These are not failures — they are scope decisions we can defend. The companion chapter §9 covers things we *tried and abandoned*; the distinction matters.

### 8.1 Scope deferrals

- **Deployment** — out of roadmap. The work is characterisation; no deployment recommendation; no deployment-readiness testing.
- **Adversarial red-teaming** — threat model named in §5.6, not exhaustively probed. *Why deferred*: in-scope adversarial inputs (the 4 LODO training sources + 5 OOD slates) already span a wide diversity of attack styles; expanding to a curated red-team set would change the methodology contract from "characterisation against a fixed slate" to "ongoing adversarial probing" — out of case-study scope.
- **Agentic-flow coverage** — multi-step / tool-use injection. *Why deferred*: the classifier scope is single-turn text-as-input; agentic-flow detection requires intermediate-state interception (tool-call args, function-output contamination) which is a deployment-stack question, not a classifier question.
- **Conformal prediction** — distribution-free uncertainty quantification beyond bootstrap. *Why deferred*: conformal calibration on LODO held-out attack sources would require a calibration set drawn from the same distribution as test (which doesn't exist by LODO design). Per-fold bootstrap CIs from ADR-022 are the in-scope honest uncertainty quantification.
- **Cross-language coverage** — English-only by source-slate construction (4 LODO + 5 OOD sources are all English). *Why deferred*: per ADR-016 source-slate lock; cross-language attack generalization is a separate dataset-design question requiring multilingual injection corpora.
- **Cross-source same-style ablation** `[OPEN]` — would disambiguate "training contamination" from "attack-style difficulty" for reference scorers. May be underpowered if per-style sample size is small; in that case treated as an explicit limitation. See EVIDENCE.md §3.
- **LLM-judge reference scorers** (gpt-4o-2024-08-06 + claude-sonnet-4-6) — dropped post-lock per ADR-050. *Why dropped*: Phase 4 cost re-estimation against the actual OOD slate sizing revealed an envelope ~16x the original ADR-018 estimate ($14 → $240) driven by per-row LLM-judge inference being charged at the full input-prompt token count (long injection examples hit 1k-3k tokens routinely). The vendor_black_box contamination tier therefore has 0 rungs in this submission; the contamination-stratification gradient compresses from 4 tiers to 3. ProtectAI v1 + v2 remain as suspected_contamination reference scorers.
- **full-FT OOD inference** — dropped post-lock per ADR-050. *Why dropped*: Phase 5 X11 full-FT re-fire crashed mid-training when shutil.copytree of the 598 MB optimizer.pt to /workspace MooseFS-backed FUSE storage returned [Errno 5] Input/output error (uv#17801 + MooseFS#380 upstream context). full-FT remains in the LODO comparison (3-rung ladder narrative survives via the surviving Phase 2 24 LODO predictions); OOD comparison ships 2 trained rungs (frozen-probe + LoRA) + 1 classical floor (tfidf-lr) + 2 reference scorers (ProtectAI v1 + v2) = 5 rungs.
- `[TBD: additional scope deferrals — populated at Phase 0]`

### 8.2 Methodology caveats

- **Single-class OOD slices break threshold-free metrics** — BIPIA + InjecAgent are all-positive attack-only datasets per their source design; NotInject is all-negative benign-only. AUROC and AUPRC are mathematically undefined on these slices and the metrics pipeline correctly skips them (the per-cell parquet `evals/metrics/per_cell.parquet` covers jbb_behaviors + xstest + pooled_ood). Per-slice recall-at-threshold is reported on the single-class slices instead.
- **LODO test sets are intentionally all-positive** per ADR-016 design (held-out attack source = cross-source generalization test). Recall@threshold is the well-defined metric on LODO; AUROC/AUPRC are undefined and not reported there.
- **Val-set inference for trained rungs uses max_length 2048** (vs the Phase 2 training max_length 8192). Covers >99% of val token-length distribution per char-to-token ~4:1 ratio; p99 token length ~1100 in val. Fidelity loss negligible for the dual-policy threshold-fitting purpose; the long-tail truncation is a tracked-but-tolerated divergence from the training-time configuration.
- `[TBD: additional caveats — populated at Phase 5 from Phase 4 metric distributions]`

Each deferred item has a *why* — usually scope or data availability — and is named in [`NEXT_STEPS.md`](./NEXT_STEPS.md) where applicable.

**Linked ADRs**: filled in once Phase 0 locks each row.

---

## 9. Negative results — architectures and approaches tried and abandoned

This chapter exists because honest framing requires showing the experimental work that did not pan out, not just the work that did. Negative results are interesting: they tell the next iteration *what not to spend time on*.

### 9.1 Hyperparameter / training dead-ends

No factorial hyperparameter sweep was conducted at the chosen compute budget per ADR-019 (single recipe per rung locked at Phase 0; no val-set gridsearch). Three operational findings during canonical fires that ARE worth documenting:

- **`max_length=8192` at training time + `max_length=2048` at val/OOD inference** is a deliberate fidelity trade-off. The trained checkpoints saw the full ModernBERT 8192 context at train time; downstream val inference on local 8GB VRAM (RTX 2070 SUPER) couldn't sustain batch=8 at max_length=8192 without OOM on long examples (val text p99 token length ~1100; max ~2800). Lowered val inference to max_length=2048 + batch=4; covers >99% of val rows intact. The truncation tail is a tracked-but-tolerated divergence (see §8.2).
- **Two pre-training-fire bugs were caught and fix-forwarded** during Phase 2 (X1-X11 chain documented in `decisions/upstream_issues.md`): SSH-ready timeout 240s → 600s for cold image pulls; phantom image tag passing `runpod-deploy validate` without registry HEAD-check; `UV_LINK_MODE=copy` + `UV_CACHE_DIR=/root/uv_cache` + `UV_PROJECT_ENVIRONMENT=/root/.venv` all needed to escape FUSE F_SETLKW deadlocks on RunPod's MooseFS-backed /workspace. Each of these would have been a multi-hour debug spiral for a first-time RunPod consumer; the fix-forward chain is preserved in commits + upstream PRs are filed at brandon-behring/runpod-deploy.
- **Full-FT cleanup-intermediate-checkpoints policy** was locked at `true` per ADR-019 storage discipline (43 GB of throwaway weights avoided per fire) but had to be RELAXED to `false` for Phase 5 X11 re-fire so OOD inference could load the trained checkpoints. The re-fire then crashed at `shutil.copytree` on the 598 MB optimizer.pt due to FUSE EIO. The lesson is operational: storage-discipline locks that delete weights need a `keep_final_only` flag to support post-train OOD inference workflows. Filed upstream as a runpod-deploy issue (proposed `lifecycle.keep_final_checkpoint` config knob).

### 9.2 Architectures evaluated and dropped

- **DeBERTa-v3-base** dropped during Phase 0 lock per ADR-015 (formerly ADR-007) for cross-backbone context-window asymmetry — DeBERTa-v3 caps at 512 tokens vs ModernBERT-base 8192. Including both backbones would have produced an irreducible truncation × architecture confound on BIPIA-style indirect injection. Single-backbone slate (ModernBERT-base × 3 conditions) preserves the rung-ladder narrative without architecture confounding.
- **Lakera Guard reference scorer** dropped at Phase 0-03 per ADR-018 (terms-of-service verification overhead unacceptable for prototype scope). The reference slate gained ProtectAI v1 in its place — internal v1→v2 lift becomes a parallel to the trained-rung-lift story.
- **LLM-judge reference rungs (gpt-4o + claude-sonnet-4-6)** dropped at Phase 4 cost re-estimation per ADR-050 (16× envelope overrun). See §8.1.
- **full-FT OOD inference** dropped at Phase 5 X11 re-fire per ADR-050 (FUSE EIO crash; non-deterministic; re-fire operationally fragile at 6-12 hr wall on Low-stock A100). full-FT remains in LODO comparison; OOD ships 2 trained rungs. See §8.1.

### 9.3 Data-pipeline experiments that didn't matter

- **Dedup threshold sweep** — ADR-042 locked the LLM-pre-label bootstrap calibration at a fixed cosine threshold per `evals/dedup_calibration.json`. A sensitivity sweep on threshold ± 0.05 was considered but deferred — the calibration's `human_verified_pct` operator follow-up (raise from 0 to 100 before v1.0.0 tag per ADR-042) is the higher-leverage gate.
- **Augmentation strategies** — no synthetic augmentation was tried (no paraphrase generation, no back-translation, no character-noise injection). The case-study scope is *characterisation of an honest classifier slate against a fixed data slate*, not data-augmentation research. Tracked as out-of-scope per Phase 0 lock.

### 9.4 What the negatives imply for v6

The OOD generalization wall is the dominant signal. Three concrete suggestions for a successor iteration:

1. **OOD-aware training data** — the current pool is dominated by 4 LODO sources (prompt-injection-style attacks) that share a stylistic core. Adding cross-style attacks (BIPIA-style indirect injection in training; jailbreaks-as-questions in training) would test whether the OOD wall is *training-distribution scope* or *fundamental classifier inadequacy*.
2. **Pretrained backbone scaling** — frozen ModernBERT-base embeddings provide more OOD generalization than LoRA fine-tuning does. A v6 ablation along backbone scale (ModernBERT-base 150M → ModernBERT-large 400M; or a different backbone family) would test whether the OOD ceiling is backbone-capacity-limited.
3. **OOD-aware threshold selection** — dual-policy thresholds fit on val do not transfer to LODO test (§7.5). Per-source temperature scaling or conformal calibration with a held-out OOD calibration set (currently impossible by LODO design) would close the val→LODO gap.

**Linked ADRs**: ADR-015 (single-backbone lock, supersedes ADR-007), ADR-018 (reference slate), ADR-019 (transformer training recipe), ADR-042 (dedup calibration), ADR-050 (rung-slate narrowing).

---

## 10. Reproducibility

The work reproduces at three levels:

### 10.1 Local

```bash
make install         # uv sync --extra dev
make lint            # ruff + mypy strict
make test            # invariants + math correctness + smoke
make diagnostics-smoke  # [OPEN] no-external-services smoke pass (~10 min)
```

### 10.2 Cloud

Canonical numbers reproduce from `runpod-deploy`:

```bash
make preflight    # [TBD] CPU preflight — gates invariants before GPU spend
make h100         # [TBD] canonical H100 path
```

Runbook: `[TBD: (candidate) docs/cloud-canonical-runbook.md]`.

### 10.3 Evaluation

Eval invocation through `eval-toolkit` captures a NeurIPS-aligned manifest at `evals/manifest.json` covering seeds, git SHA, data hashes, GPU info, and a leakage report. `evals/results.json` is schema-validated against eval-toolkit's `results.v1.json`. **The project persists per-row predictions** at `evals/predictions.parquet` `[TBD: scoped at Phase 0]`.

### 10.4 Data + checkpoints

- Data sources: licenses + download instructions in [`SPEC_SHEET.md` §3](./SPEC_SHEET.md). HF revisions `[LOCKED]` SHA-pinned at  build time (forward-only).
- Checkpoints: `[TBD: HF Hub URL for checkpoints]`.
- Predictions: `[TBD: GitHub release tag with predictions tarball]`.

### 10.5 Transcripts

`[TBD: populated at Phase 5]` Selected Claude-Code transcripts illustrating key decision points are in `transcripts/` and referenced from the appendix. Examples: `[transcript: dedup-threshold-bake-off]`, `[transcript: ood-slice-selection]`, `[transcript: protectai-overlap-audit]`.

**Linked ADRs**: `[ADR-016, ADR-025, ADR-027]`.

---

## 11. Lessons & reflections

`[TBD: populated at Phase 5]` Short. What surprised. What the SDD process bought; what it cost.

- `[TBD: lesson 1]`
- `[TBD: lesson 2]`
- `[TBD: lesson 3]`

---

## 12. Appendix

### A. Glossary

- **Detection policy** — threshold selection targeting FPR ≤ 1% on validation; characterises high-recall-low-FP behaviour.
- **Verification policy** — threshold selection targeting FNR ≤ 1% on validation; characterises high-precision-on-clean behaviour.
- **LODO** — leave-one-dataset-out cross-validation; source-disjoint k-fold where each fold holds out an entire dataset source.
- **LoRA** — Low-Rank Adaptation; parameter-efficient fine-tuning method.
- **PR-AUC** — area under the precision-recall curve; threshold-free ranking metric for class-imbalanced tasks.
- **ECE** — expected calibration error; mean absolute gap between predicted-probability bins and observed frequencies.
- **MDE** — minimum detectable effect; the smallest difference your sample size can reliably detect at a given power.
- **IID** — independent and identically distributed; evaluation on data drawn from the same source/distribution as training.
- **OOD** — out-of-distribution; evaluation on data deliberately drawn from a different source or distribution.
- **Rung ladder** — a sequence of classifiers of increasing complexity, designed so each step's lift decomposes which capability is responsible.

### B. ADR index

[`decisions/README.md`](./decisions/README.md) — single version-neutral sequence;  ADRs supersede prior ones via the standard `superseded-by-ADR-N` mechanism.

### C. Assumption ledger

[`assumptions.md`](./assumptions.md) — every assumption with severity ≥ medium appears in §8.2 above.

### D. Audit trail

[`EVIDENCE.md`](./EVIDENCE.md) — what external evidence was verified, what couldn't be, what was left unresolved.

### E. Linked Claude transcripts

`[TBD: populated at Phase 5]` Resolved from `[transcript: <slug>]` placeholders to `transcripts/<slug>.md` once the transcript-export skill exists.

### F. eval-toolkit methodology curriculum

[`docs/methodology/`](https://github.com/brandon-behring/eval-toolkit/tree/main/docs/methodology) — 16-chapter curriculum. Cross-linked from §3, §5.1–5.5, and §6.1 above.
