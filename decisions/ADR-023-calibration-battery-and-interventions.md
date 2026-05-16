---
adr_id: 023
slug: calibration-battery-and-interventions
title: Calibration battery composition — raw plus temperature plus isotonic interventions
date: 2026-05-15
status: Accepted
claim_id: CLAIM-023
claim: Phase 0-04 locks the calibration battery composition at row 343 as Option C revised — raw scores reported plus two validation-fit calibration interventions (temperature scaling and isotonic regression). The PDF executive headline table carries two calibration columns per rung — ECE-equal-mass (n_bins=15, quantile binning) and Brier score — both computed on the raw model outputs (no intervention applied). The methodology spoke at WRITEUP/calibration.md (new) carries the full battery — all four ECE variants from eval-toolkit (L1 plug-in via expected_calibration_error, L1 debiased via expected_calibration_error_debiased, L2 plug-in via expected_calibration_error_l2, L2 debiased via expected_calibration_error_l2_debiased), Brier score plus Brier decomposition into refinement-reliability-uncertainty components, reliability diagrams (equal-mass quantile binning per eval-toolkit recommendation under class imbalance), and intervention-delta tables showing how much miscalibration is correctable by (a) Guo 2017 1-parameter temperature scaling and (b) sklearn IsotonicRegression-wrapped fit_isotonic_calibrator non-parametric monotonic remapping. Both calibrators fit on the validation split per-(rung, fold, seed) yielding 12 calibrators per trained rung times 2 interventions; applied to the test split; ECE plus Brier re-computed on the calibrated scores. Per ADR-011 Guarantee 6, calibration fitting occurs on validation only — no test-set leakage. Per ADR-022's multi-seed protocol, calibration interventions on the 4 reference rungs (LLM judges and ProtectAI v1/v2) fit per-(rung, fold) yielding 4 calibrators per reference rung times 2 interventions (reference rungs have no seed dimension). Calibration interventions are explicitly methodology-axis not deployment-axis — the temperature-vs-isotonic gap is the methodology-informative quantity (small gap means simple scaling captures most miscalibration; large gap means miscalibration has non-temperature-monotone structure recoverable only by non-parametric remapping). Calibration interventions are monotonic by construction and therefore do NOT change rank-based headline metrics (PR-AUC, ROC-AUC, recall@FPR) — this methodology subtlety is noted in the spoke. Platt scaling plus beta calibration deferred to afterword; maximum-calibration-error (worst-bin) computed and dumped to audit JSON but not reported in headline or spoke; per-slice calibration after intervention deferred unless reviewer asks (per-slice n too small for stable temperature fits).
source: SPEC_GREENFIELD.md §3 Eval ledger row 343 + Phase 0-04 walk Q5
acceptance_criterion: SPEC_GREENFIELD ledger row 343 carries locked-to-raw-plus-temperature-plus-isotonic-with-ECE-equal-mass-and-Brier-headline-plus-full-spoke-battery status; SPEC_SHEET §5.1 primary descriptive metrics replaces [OPEN] on calibration battery with [LOCKED — ECE-equal-mass(n_bins=15, quantile) plus Brier headline; full 4-ECE plus Brier-decomp plus reliability diagrams plus temperature plus isotonic intervention deltas in WRITEUP/calibration.md spoke per ADR-023]; WRITEUP/calibration.md spoke filename pre-committed; decisions/library_imports.md eval-toolkit section populated with all 4 ECE variants plus brier_score plus brier_decomposition plus reliability_curve plus fit_temperature plus fit_isotonic_calibrator primitives; tests/test_invariants.py contains skip-marked stub test_calibration_battery_composition asserting (1) headline emit contains ECE-equal-mass plus Brier per rung on raw scores; (2) spoke artifact contains all 4 ECE variants plus temperature-applied plus isotonic-applied deltas; (3) calibrator fits use only validation data per ADR-011 Guarantee 6 (no test-set rows in calibrator-fit input); tests/test_invariants.py contains skip-marked stub test_monotonic_intervention_preserves_ranks asserting PR-AUC after temperature equals PR-AUC before temperature within numerical tolerance (sanity check that the intervention machinery is monotonic).
closing_commit: b750d1d
references:
  - https://arxiv.org/abs/1909.10155
  - https://arxiv.org/abs/1706.04599
  - https://ojs.aaai.org/index.php/AAAI/article/view/9602
  - https://www.cs.cmu.edu/~aarti/Class/10704_Spring15/Niculescu-Mizil_Caruana.pdf
  - https://www.jmlr.org/papers/v18/14-188.html
  - decisions/ADR-006-headline-metrics-and-statistical-apparatus.md
  - decisions/ADR-011-methodology-guarantees.md
  - decisions/ADR-022-statistical-inference-apparatus.md
transcript: transcripts/2026-05-15__phase-0-04__eval-framework.md
---

# ADR-023: Calibration battery composition — raw plus temperature plus isotonic interventions

## Status

Accepted (2026-05-15). New lock at the §3 Eval ledger row 343 level; not pre-locked by ADR-006 (which named the calibration-battery row but deferred composition).

## Context

A classifier is *calibrated* if its predicted probabilities match observed frequencies — among rows where the model says "70 percent positive", roughly 70 percent are positive (Guo et al. 2017). Modern transformer fine-tuning routinely produces miscalibrated outputs; sklearn LogisticRegression with class_weight='balanced' produces a different miscalibration profile (typically under-confident on the positive class); LLM-judges at temperature=0 produce near-categorical softmax outputs with high concentration at the extremes; ProtectAI v1/v2 produce softmax outputs with unknown calibration character.

SPEC §3 Eval pre-named the calibration battery as ECE plus Brier plus reliability curve but did not specify (a) which ECE variant for headline; (b) bin count; (c) whether interventions are applied; (d) per-(rung, fold, seed) vs aggregate fitting.

Phase 0-04 walk Q5 surfaced that eval-toolkit ships a complete calibration battery — all 4 ECE variants (L1/L2 × plug-in/debiased), Brier plus Brier decomposition, reliability curves, and four calibrators (temperature, Platt, isotonic, beta). The choice question is therefore about reporting depth, not primitive availability. Brandon's follow-up question — "are we also considering isotonic regression to calibrate the models?" — surfaced the lift-delta-chain framing: the before-after-temperature delta tells you "how much miscalibration is monotone-rescaling fixable" (Guo 2017 1-parameter fix); the before-after-isotonic delta tells you "how much miscalibration is arbitrary-monotone-remapping fixable" (high-capacity non-parametric fix). The temperature-to-isotonic gap is the methodology-informative quantity.

ADR-011 Guarantee 6 explicitly anticipates calibration interventions ("calibration-fit (temperature/isotonic) done on validation only") so the intervention is spec-aligned.

## Decision

### Headline composition (PDF executive table)

| Column | Primitive | Notes |
|---|---|---|
| ECE-equal-mass | eval_toolkit.expected_calibration_error_equal_mass(n_bins=15, strategy='quantile') | L1 plug-in equal-mass binning; Guo 2017 n_bins=15 standard; equal-mass binning preferred under class imbalance per eval-toolkit methodology/calibration.md guidance |
| Brier | eval_toolkit.brier_score | Proper scoring rule; no binning required |

Both computed on raw model outputs (no intervention applied). Per ADR-022 per-row-metric aggregation rule: pool rows across (fold, seed) per rung; compute once per rung; bootstrap CI per ADR-024 cross-fold methodology.

### Spoke composition (WRITEUP/calibration.md)

Full 4-ECE matrix per rung — plug-in vs debiased (L1 and L2). The plug-in-vs-debiased delta surfaces how much binning bias affects the headline ECE; Kumar 2019 argues plug-in ECE systematically underestimates calibration error.

Brier decomposition per rung — refinement + reliability + uncertainty components via eval_toolkit.brier_decomposition. The reliability component is the "miscalibration" content of Brier; refinement is the "discrimination" content; the decomposition surfaces which component dominates per rung.

Reliability diagrams per rung — equal-mass quantile binning (eval_toolkit.reliability_curve(strategy='quantile')); visual canonical of the ECE story.

Intervention deltas per rung — three calibration states reported in a small table:

| State | Calibrator | ECE-equal-mass | Brier |
|---|---|---|---|
| Raw | (none) | value | value |
| Temperature-scaled | eval_toolkit.fit_temperature on val per-(rung, fold, seed) | value | value |
| Isotonic-regressed | eval_toolkit.fit_isotonic_calibrator on val per-(rung, fold, seed) | value | value |

### Interventions — fitting protocol

| Sub-decision | Locked policy |
|---|---|
| Calibrators applied | Temperature (Guo 2017 1-parameter logit-scaling) + Isotonic (sklearn IsotonicRegression-wrapped, non-parametric monotonic remapping) |
| Calibrators NOT applied | Platt (deferred to afterword — legacy SVM-margin convention; minor lift over temperature on transformer outputs); beta (deferred to afterword — boundary-niche; useful when scores cluster at 0/1) |
| Fitting data | Validation split per ADR-016's per-LODO-fold val (per ADR-011 Guarantee 6 — no test-set leakage) |
| Per-rung fitting granularity | Per-(rung, fold, seed) yielding 12 trained calibrators per rung × 2 interventions; per-(rung, fold) yielding 4 reference calibrators per reference rung × 2 interventions |
| Test-set application | Calibrated scores computed by applying the val-fit calibrator to test rows; ECE plus Brier re-computed |
| Rank-based metric preservation | Calibration interventions are monotonic by construction → PR-AUC, ROC-AUC, and recall@FPR are unchanged by intervention; this methodology subtlety noted in the spoke |
| Per-slice calibration after intervention | Deferred unless reviewer asks (per-slice n too small for stable temperature fits) |
| Maximum-calibration-error (worst-bin) | Computed via eval_toolkit.maximum_calibration_error; dumped to evals/calibration/per_obs_audit.parquet; not headline or spoke (audit-only) |

### Phase 1 deliverables

- src/eval/calibration_battery.py — orchestrates raw-plus-temperature-plus-isotonic computation per rung
- evals/calibration/<rung>__fold<F>__seed<S>__intervention<temperature|isotonic|raw>.json — per-(rung, fold, seed, intervention) ECE plus Brier values
- evals/calibration/per_obs_audit.parquet — per-(rung, fold, seed) audit rows including maximum-calibration-error
- WRITEUP/calibration.md spoke filename pre-committed
- WRITEUP/methodology.md gains a one-paragraph subsection "Calibration interventions are monotonic and therefore don't change rank-based metrics"

## Consequences

### Positive

- Headline carries Guo 2017-standard ECE (PromptShield-comparable for cross-paper comparison) plus Brier (proper-scoring-rule baseline that doesn't require binning) — 2 columns per rung
- Spoke surfaces methodology depth — 4 ECE variants reveals plug-in-vs-debiased bias; Brier decomposition reveals refinement-vs-reliability split; intervention deltas reveal temperature-vs-isotonic gap
- Library-first — all primitives from eval-toolkit; no hand-rolling
- Compute essentially free — calibrator fits are CPU-seconds per (rung, fold, seed)
- Aligns with ADR-011 Guarantee 6 (validation-only fitting) — calibrator-fit-on-val-applied-to-test is exactly the locked pattern
- Aligns with ADR-005 Principle 2 (honest evaluation preferred) — surfaces miscalibration honestly rather than reporting only post-intervention numbers

### Negative

- WRITEUP/calibration.md is a new spoke; one more Phase 5 deliverable
- Per-(rung, fold, seed) calibrator artifacts (96 trained calibrators + 32 reference = 128 JSON files); modest persistence overhead
- Methodology subtlety about "monotonic intervention preserves ranks" needs a clear paragraph for A2 reviewer (otherwise reviewer may wonder why PR-AUC isn't reported after intervention)

### Neutral

- Maximum-calibration-error computed alongside but not surfaced — reviewer can still see worst-bin behavior in audit parquet if curious; aligns with audit-trail discipline

## Alternatives considered

- **Option A (Raw only, no interventions)**: simplest; rejected because doesn't surface how much miscalibration is correctable by simple post-hoc fix — methodology contribution lost
- **Option B (Raw plus temperature only)**: Guo 2017 standard; rejected because no high-capacity comparison point; temperature-vs-isotonic gap is the methodology-informative quantity
- **Option D (Full 4-calibrator battery — temperature, Platt, isotonic, beta)**: most rigorous; rejected because Platt and beta calibrators show similar behavior to temperature and isotonic respectively in preliminary characterization; deferred to afterword if reviewer asks
- **Per-rung pooled (rather than per-fold-seed) calibrator fitting**: simpler; rejected because breaks the per-(fold, seed)-paired-across-rungs structure locked by ADR-022; would also leak val rows from one fold into another fold's calibrator
- **Per-slice calibration after intervention**: most granular; rejected because per-slice n less than or equal to 1054 is too small for stable temperature fits; deferred unless reviewer asks

## References

See frontmatter references list. Primary anchors — Kumar, Liang and Ma 2019 (debiased ECE estimators, arXiv:1909.10155); Guo et al. 2017 (transformer calibration plus temperature scaling, arXiv:1706.04599); Naeini, Cooper and Hauskrecht 2015 (Bayesian binning and ECE history, AAAI); Niculescu-Mizil and Caruana 2005 (calibrator comparison — Platt vs isotonic); Kull, Silva Filho and Flach 2017 (beta calibration, JMLR); eval-toolkit methodology/calibration.md (local — equal-mass binning recommendation under class imbalance); ADR-006 (calibration-battery row pre-named); ADR-011 Guarantee 6 (validation-only fitting); ADR-022 (multi-seed protocol details — per-(rung, fold, seed) calibrator fitting consistency).

## Transcript

See `transcripts/2026-05-15__phase-0-04__eval-framework.md` for the conversation that led to this decision.
