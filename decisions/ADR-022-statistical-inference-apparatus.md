---
adr_id: 022
slug: statistical-inference-apparatus
title: Statistical inference apparatus — bootstrap N + stability check, multi-comparison stance, multi-seed protocol, paired-test method
date: 2026-05-15
status: Accepted
claim_id: CLAIM-022
claim: Phase 0-04 formalizes the statistical inference apparatus at the ledger-row level by ratifying and extending ADR-006's brief-level pre-locks across four §3 Eval rows. (1) Bootstrap N plus stability check (row 340) — 10K iterations at seed=1 (BCa for marginals via eval_toolkit.bootstrap_ci, percentile for paired-Delta-CIs via eval_toolkit.paired_bootstrap_diff) as headline; 10K iterations at seed=2 as stability check; flag in audit JSON when the stability-check CI half-width differs from the headline CI half-width by more than 5 percent (signals resampling instability requiring escalation to 100K iterations or honest reporting of wider CI); parallelize across independent CI computations via joblib.Parallel(n_jobs=-1) at the orchestrator layer (library-first discipline preserved — primitive itself stays as eval-toolkit shipped) on the 64-core Threadripper CPU (approximately 10000 independent CIs across 84 trained plus 16 reference prediction parquets times 4 headline metrics times 3 recall@FPR pinpoints times 6 slice aggregations times approximately 28 rung-vs-rung pairs); upstream issue filed against eval-toolkit proposing optional n_jobs parameter on paired_bootstrap_diff for internal resample-loop parallelization. (2) Multi-comparison correction (row 341) — no formal correction applied per ADR-006 estimation-over-testing stance ratified; methodology spoke at WRITEUP/methodology.md gains an explicit "family of comparisons" acknowledgment paragraph citing Gelman and Loken 2014 garden-of-forking-paths plus ASA 2016 statement on p-values; pre-empts A2 reviewer concern about ~28 paired comparisons without re-importing significance-testing apparatus. (3) Multi-seed protocol details (row 344) — 3 seeds {42, 1337, 2025} per ADR-006 ratified; trained rungs have 12 (fold, seed) observations per rung (4 LODO folds times 3 seeds) per ADR-016; reference rungs have 4 (fold) observations per rung (no seed dimension, inference-only); paired-across-rungs implementation uses (a) row-level pairing for trained-vs-trained comparisons via eval-toolkit paired_bootstrap_diff, (b) per-row replication of reference scores across the 12 trained seeds for trained-vs-reference comparisons (reference-side variance correctly fold-only); rank-based metrics aggregate per-(fold, seed)-then-mean (12 values per rung yielding cross-fold CI per ADR-024); per-row metrics (ECE plus Brier) pool rows across (fold, seed) and compute once per rung; recall@FPR thresholds computed per-(seed) from val per-(rung, fold) and applied to test (12 thresholds per rung yielding 12 recall values per rung); calibration interventions fit per-(rung, fold, seed) yielding 12 calibrators per rung times 2 interventions per ADR-023; per-(rung, fold, seed) observations dumped to evals/audit/per_seed_observations.parquet per ADR-011 Guarantee 5; methodology spoke gains variance-attribution subsection decomposing per-rung variance into fold-to-fold plus seed-to-seed plus within-(fold, seed)-bootstrap noise. (4) Paired-test method (row 345) — eval-toolkit paired_bootstrap_diff (Efron-Tibshirani 1993 §10.3 row-level pairing) ratified; DeLong 1988 plus McNemar plus Cochran-Q rejected at the row level with multi-source-LODO-specific rationale (DeLong's asymptotic Gaussian assumption breaks at our per-fold scale of approximately 4000 to 5000 benigns; designed for AUROC only not AUPRC or ECE; produces p-value contradicting estimation-over-testing; McNemar requires fixed-threshold commitment contradicting ADR-006 scenario-based threshold framing; Cochran-Q designed for fixed-classifier-vs-many-datasets — inverse of our setting). LLM-judge non-determinism at temperature=0 surfaced as new assumption A-007 (reference-rung scores cached at first call; re-run only on cache miss; inter-call variance not measured).
source: SPEC_GREENFIELD.md §3 Eval ledger rows 340 + 341 + 344 + 345 + Phase 0-04 walk Q2 + Q3 + Q6 + Q7
acceptance_criterion: SPEC_GREENFIELD ledger row 340 carries locked-to-10K-bootstrap-with-second-seed-stability-check status; ledger row 341 carries locked-to-no-formal-correction-with-Gelman-Loken-acknowledgment-paragraph status; ledger row 344 carries locked-to-3-seeds-paired-across-rungs-with-gap-honest-defaults status; ledger row 345 carries locked-to-paired-bootstrap-diff-with-multi-source-LODO-rejection-rationale status; SPEC_SHEET §5.2 statistical tests expanded with explicit listing of headline-bootstrap-iteration-counts plus stability-check-protocol plus multi-comparison-acknowledgment plus paired-across-rungs-implementation-details; assumptions.md gains A-007 documenting LLM-judge non-determinism reference treatment; decisions/library_imports.md eval-toolkit section populated with bootstrap_ci + paired_bootstrap_diff + paired_bootstrap_ece_diff + cross_validate_metric primitives; decisions/upstream_issues.md gains entry for paired_bootstrap_diff parallelization proposal; tests/test_invariants.py contains skip-marked stub test_bootstrap_n_and_stability_check asserting 10K-plus-10K-at-second-seed pipeline plus 5pct-half-width-flag emission; tests/test_invariants.py contains skip-marked stub test_paired_across_rungs_pairing asserting (a) trained-vs-trained row-level pairing plus (b) trained-vs-reference per-row replication pattern.
closing_commit: b750d1d
references:
  - https://projecteuclid.org/journals/annals-of-statistics/volume-7/issue-1/Bootstrap-Methods-Another-Look-at-the-Jackknife/10.1214/aos/1176344552.full
  - https://projecteuclid.org/journals/statistical-science/volume-11/issue-3/Bootstrap-confidence-intervals/10.1214/ss/1032280214.full
  - http://www.stat.columbia.edu/~gelman/research/published/ForkingPaths.pdf
  - https://www.tandfonline.com/doi/full/10.1080/00031305.2016.1154108
  - https://www.tandfonline.com/doi/abs/10.1198/000313006X152649
  - https://www.jstor.org/stable/2531595
  - https://www.aaai.org/Library/ICML/2003/icml03-013.php
  - https://www.jmlr.org/papers/v7/demsar06a.html
  - decisions/ADR-006-headline-metrics-and-statistical-apparatus.md
  - decisions/ADR-011-methodology-guarantees.md
  - decisions/ADR-016-data-design-bundle.md
  - decisions/ADR-018-reference-scorer-slate-and-contamination-stratification.md
transcript: transcripts/2026-05-15__phase-0-04__eval-framework.md
---

# ADR-022: Statistical inference apparatus — bootstrap N + stability check, multi-comparison stance, multi-seed protocol, paired-test method

## Status

Accepted (2026-05-15). Formalizes ADR-006 brief-level pre-locks at the §3 Eval ledger-row level + adds row-specific operational details.

## Context

ADR-006 (Phase 0-00 brief alignment) pre-locked the brief-level inferential stance: 10K bootstrap iterations, BCa marginals plus paired Delta-CIs, estimation-over-testing, 3 seeds paired-across-rungs, no formal p-tests. The §3 Eval ledger rows 340 / 341 / 344 / 345 require formalization at the row level with the operational details ADR-006 left implicit:

- Row 340 (bootstrap N): the SPEC-text "pinned seed with stability check at a second seed" was not operationalized
- Row 341 (multi-comparison correction): ADR-006 stated "not applicable" but did not specify whether to surface the acknowledgment in the writeup
- Row 344 (multi-seed protocol): the "paired-across-rungs" semantics — what is paired and how heterogeneous rung observation counts (12 trained vs 4 reference) reconcile — were ambiguous
- Row 345 (paired-test method): DeLong / McNemar rejection rationale was stated at the brief level but lacked the LODO-specific operational reasoning

Phase 0-04 walks Q2 / Q3 / Q6 / Q7 surfaced 6 gaps in the original pre-lock — reference-rung observation-count asymmetry; aggregation order for rank-based vs per-row metrics; (fold, seed) blocking violating iid; LLM-judge non-determinism at T=0; recall@FPR threshold drift across seeds; per-(rung, fold, seed) calibrator fitting. This ADR resolves each gap with a methodology-honest default.

## Decision

### Bootstrap N plus stability check (row 340)

| Layer | Decision |
|---|---|
| Headline iterations | 10K via eval_toolkit.bootstrap_ci (BCa for marginals); 10K via eval_toolkit.paired_bootstrap_diff (percentile for paired Delta-CIs) |
| Stability check | 10K at a second resampling seed (seed=2); flag when stability-check half-width differs from headline half-width by more than 5 percent |
| Parallelization | joblib.Parallel(n_jobs=-1) at the orchestrator layer in scripts/run_bootstrap_battery.py; library primitive itself stays single-threaded as shipped (library-first discipline); 64-core Threadripper expected to compress approximately 10000 independent CIs from hours of serial walltime to minutes |
| Upstream issue | Filed against eval-toolkit proposing optional n_jobs parameter on paired_bootstrap_diff for internal resample-loop parallelization |

### Multi-comparison correction (row 341)

**No formal correction applied** per ADR-006 estimation-over-testing stance. The methodology spoke at WRITEUP/methodology.md gains an explicit "Family of comparisons" acknowledgment paragraph that:

- Names the comparison family size (~28 paired rung-vs-rung comparisons across 8 rungs choose 2)
- Cites Gelman and Loken 2014 "garden of forking paths" framing
- Cites the ASA 2016 statement on p-values supporting effect-size-with-CI over null-hypothesis testing
- States explicitly that paired-bootstrap Delta-CIs are not Bonferroni-corrected and explains the rationale (correction applies to significance-testing; we report effect sizes)

### Multi-seed protocol details (row 344)

**3 seeds {42, 1337, 2025}** per ADR-006 ratified plus the following gap-honest implementation defaults:

| Sub-decision | Locked policy |
|---|---|
| Trained-rung observations per rung | 12 = 4 LODO folds × 3 seeds per ADR-016 |
| Reference-rung observations per rung | 4 = 4 LODO folds × 1 (no seed dimension; inference-only at T=0) |
| Trained-vs-trained pairing | Row-level pairing via eval-toolkit paired_bootstrap_diff (same y_true rows across both rungs) |
| Trained-vs-reference pairing | Per-row replication of reference scores across the 12 trained seeds; reference-side variance is fold-only (correctly so — reference has no seed dimension) |
| Rank-based metric aggregation (PR-AUC, ROC-AUC, recall@FPR) | Compute per-(fold, seed) → 12 values per rung → mean → cross-fold CI per ADR-024; pool-then-compute reported in spoke as sensitivity-check ablation |
| Per-row metric aggregation (ECE, Brier) | Pool rows across (fold, seed) and compute once per rung (within-block iid violation is small for per-row scoring rules) |
| Recall@FPR threshold computation | Per-(seed) thresholds computed from val per-(rung, fold); applied to test; 12 thresholds per (rung, fold) yielding 12 recall values per rung; averaged |
| Calibration intervention fit | Per-(rung, fold, seed) → 12 calibrators per rung × 2 interventions (temperature + isotonic) per ADR-023 |
| Per-seed transparency | Per-(rung, fold, seed) values dumped to evals/audit/per_seed_observations.parquet per ADR-011 Guarantee 5 |
| Variance attribution spoke | Per-rung decomposition: fold-to-fold vs seed-to-seed vs within-(fold, seed) bootstrap noise |
| LLM-judge non-determinism | Reference scores cached at first call; re-run only on cache miss; inter-call variance not measured (A-007) |

### Paired-test method (row 345)

**eval-toolkit paired_bootstrap_diff** (Efron-Tibshirani 1993 §10.3 row-level pairing) ratified. Rejection rationale for the field-standard alternatives at the row level:

| Method | Why rejected (multi-source-LODO-specific) |
|---|---|
| DeLong 1988 | Asymptotic Gaussian assumption breaks at per-fold n ≈ 4-5K benigns; designed for AUROC only — doesn't extend to AUPRC or ECE; produces p-value contradicting estimation-over-testing; LODO fold-blocking violates the iid assumption underlying the DeLong variance estimate |
| McNemar | Threshold-dependent; would require committing to a single deployment operating point we explicitly refuse to commit to (ADR-006 + scenario-based framing); doesn't handle the dual-policy framing |
| Cochran's Q / Friedman | Designed for fixed-classifier-vs-many-datasets — inverse of our setting (many rungs vs few LODO folds); produces p-value |
| Permutation test on Delta | Equivalent to bootstrap on the null hypothesis; would require explicit p-value reporting; contradicts ADR-006 stance; more compute |

## Consequences

### Positive

- All four rows formalized at the ledger-row level with operational details ADR-006 left implicit; A2 reviewer can read exact apparatus without inferring from brief-level claims
- Parallelization-via-glue plan preserves library-first discipline while leveraging 64-core hardware — upstream issue captures the future improvement path
- Gap-honest multi-seed defaults eliminate the silent-aggregation-choice failure mode (the choice of "pool-rows-and-compute-once" vs "compute-per-(fold,seed)-and-aggregate" is itself a methodology decision; both are now explicit)
- Multi-comparison acknowledgment paragraph pre-empts A2 reviewer concern; cheap (~1 paragraph)
- DeLong / McNemar rejection rationale at the row level satisfies ADR-011 Guarantee 8 (no untracked methodology components)

### Negative

- Per-(rung, fold, seed) audit JSON pipeline + per-seed observations parquet add Phase 3 deliverables
- Variance-attribution spoke subsection requires Phase 4 analysis work (per-rung ANOVA-style decomposition)
- LLM-judge response caching infrastructure (Phase 1 deliverable) adds a small persistence concern

### Neutral

- Rank-based-metric-aggregation choice (compute-per-(fold, seed)-then-mean) pushes weight onto ADR-024's cross-fold CI machinery; the two ADRs are intentionally coupled

## Alternatives considered

For each row's alternatives, see ADR-006's Alternatives Considered section. The ADR-022-specific additions:

- **No stability check (Option A of Q2)**: rejected because cannot distinguish narrow-CI from narrow-but-lucky-CI; cheap to add second-seed run
- **100K-iteration headline plus 10K second-seed ablation (Option C of Q2)**: rejected because 100K walltime ~10x of 10K at scale of ~10000 independent CIs; marginal gain over 10K+10K is small per Efron-Tibshirani 1993 iteration-count guidance
- **Silent multi-comparison treatment (Option A of Q3)**: rejected because A2 reviewer may infer cherry-picking from many-comparisons surface
- **BH-FDR post-hoc on the comparison family as ablation (Option C of Q3)**: rejected because adds inferential apparatus contradicting estimation-over-testing stance; muddles narrative
- **Pre-registration of primary-vs-exploratory comparisons (Option D of Q3)**: rejected because adds bureaucracy; some comparisons are genuinely planned-vs-incidental and the line is hard to draw cleanly
- **Seed-only pairing across folds (alternative to (fold, seed)-tuple pairing in Q6)**: rejected because loses fold-level pairing
- **Trained-vs-reference per-rung-seed-aggregation (Option (b) of Q6 Gap 1)**: rejected because drops trained-side seed variance from the Delta-CI making it tighter than honest

## Phase 1 deliverables

- scripts/run_bootstrap_battery.py with joblib parallelization scaffolding
- evals/audit/per_seed_observations.parquet schema documented in evals/audit/README.md
- evals/audit/llm_judge_cache/ directory layout documented (per-row response cache for gpt-4o + claude-sonnet)
- decisions/upstream_issues.md gains entry for paired_bootstrap_diff parallelization proposal

## References

See frontmatter references list. Primary anchors — Efron 1979 plus Efron-Tibshirani 1993 §10.3 (bootstrap apparatus); DiCiccio-Efron 1996 (BCa derivation); Gelman-Loken 2014 (forking paths); ASA 2016 statement on p-values; Gelman-Stern 2006 (significance vs not-significance distinction); DeLong 1988 (the test we are not using); Bouckaert 2003 (multi-seed paired-across-rungs precedent); Demsar 2006 (per-dataset reporting in multi-dataset settings); ADR-006 (brief-level pre-lock); ADR-011 Guarantee 5 (no cherry-picking seeds); ADR-016 (LODO + 12-obs-per-rung); ADR-018 (reference rung slate + contamination taxonomy).

## Transcript

See `transcripts/2026-05-15__phase-0-04__eval-framework.md` for the conversation that led to this decision.
