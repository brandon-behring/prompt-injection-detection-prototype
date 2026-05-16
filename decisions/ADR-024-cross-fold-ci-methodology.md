---
adr_id: 024
slug: cross-fold-ci-methodology
title: Cross-fold CI methodology — cv_clt_ci (Bayle 2020) headline plus block-bootstrap-on-folds spoke
date: 2026-05-15
status: Accepted
claim_id: CLAIM-024
claim: Phase 0-04 locks the cross-fold confidence-interval methodology at row 346 as Option F — hybrid library-first headline plus methodology-honest spoke ablation plus a conditional escalation path. (1) Headline CI machinery — eval_toolkit.cv_clt_ci (Bayle, Bayle, Janson and Mackey 2020 Annals of Statistics Theorem 3.1 implementation in eval-toolkit at src/eval_toolkit/bootstrap.py:963) on the 12 (fold, seed) per-rung metric values from ADR-022's compute-per-(fold, seed)-then-aggregate rule. The cv_clt_ci primitive computes normal-approximation CI with sample variance (K-1)-denominator estimator at K=12 entries (4 folds times 3 seeds); BCa-replaced-by-normal-approx is appropriate at this K. (2) Spoke ablation — block bootstrap on (fold) blocks — resample 4 folds with replacement (with seeds inside each block as units); per-resample compute mean-of-fold-metrics; 10K resamples; percentile CI on the resampled fold-mean. Computed via custom orchestrator on top of eval_toolkit.bootstrap_ci primitive (resample-indices construction is project-specific glue; primitive is library-shipped — library-first discipline preserved). The block-bootstrap CI is reported alongside the cv_clt_ci CI in WRITEUP/methodology.md spoke as a sensitivity check addressing the LODO non-exchangeability concern (LODO folds are explicitly not exchangeable per ADR-016 design — each fold holds out a different positive source with different size and attack-style character; cv_clt_ci was derived for exchangeable k-fold). (3) Sensitivity-check threshold — if block_bootstrap_CI_halfwidth / cv_clt_CI_halfwidth exceeds 1.5 for any headline rung, flag in the spoke as "LODO non-exchangeability dominates within-fold variance; headline CI may understate uncertainty" — this becomes a named methodology finding rather than a hidden numerical caveat. (4) Conditional escalation — stratified-k-fold-within-LODO (Fomin 2025 + Nadeau-Bengio 2003 variance decomposition; approximately 5x compute relative to plain LODO) is pre-committed as a conditional escalation IF the project's cost ledger at Phase 4 entry shows cumulative spend well below the ADR-020 per-job soft cap of 125 USD (rough threshold — under 75 USD cumulative); ELSE deferred to afterword. (5) Bates 2024 JASA nested-CV and Nadeau-Bengio 2003 standalone correction factor explicitly deferred to afterword — both require custom implementations not in eval-toolkit; their theoretical advantages do not outweigh the library-first plus 2.5-day-timeline cost.
source: SPEC_GREENFIELD.md §3 Eval ledger row 346 + Phase 0-04 walk Q8
acceptance_criterion: SPEC_GREENFIELD ledger row 346 carries locked-to-cv_clt_ci-headline-plus-block-bootstrap-on-folds-spoke-plus-conditional-stratified-k-fold status; SPEC_SHEET §5.2 cross-fold CI methodology replaces [OPEN] with [LOCKED — cv_clt_ci (Bayle 2020) headline plus block-bootstrap-on-folds spoke ablation plus conditional stratified-k-fold-within-LODO escalation if Phase 4 compute budget permits per ADR-024]; decisions/library_imports.md eval-toolkit section gains cv_clt_ci primitive entry; WRITEUP/methodology.md gains a "Cross-fold CI methodology and LODO non-exchangeability" subsection containing both CI values per rung plus the sensitivity-check flag; tests/test_invariants.py contains skip-marked stub test_cross_fold_ci_methodology asserting (1) cv_clt_ci primitive invoked on 12 per-(fold, seed) values per rung; (2) block-bootstrap-on-folds orchestrator produces percentile CI on 10K resamples of (fold) blocks; (3) sensitivity-check flag emits when block_bootstrap_halfwidth / cv_clt_halfwidth exceeds 1.5; (4) conditional-stratified-k-fold-within-LODO escalation gated on cost-ledger evals/cost_ledger.csv state at Phase 4 entry; assumptions.md A-008 added (severity medium) documenting LODO-non-exchangeability concern as load-bearing on cross-fold CI validity.
closing_commit: b750d1d
references:
  - https://www.jstor.org/stable/27033529
  - https://www.tandfonline.com/doi/full/10.1080/01621459.2023.2197686
  - https://link.springer.com/article/10.1023/A:1024068626366
  - https://www.jstor.org/stable/2290993
  - https://arxiv.org/abs/2007.02780
  - decisions/ADR-016-data-design-bundle.md
  - decisions/ADR-022-statistical-inference-apparatus.md
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md
transcript: transcripts/2026-05-15__phase-0-04__eval-framework.md
---

# ADR-024: Cross-fold CI methodology — cv_clt_ci (Bayle 2020) headline plus block-bootstrap-on-folds spoke

## Status

Accepted (2026-05-15). New lock at the §3 Eval ledger row 346 level; methodology-load-bearing for headline rung-vs-rung Delta-CI honesty.

## Context

Per ADR-022's compute-per-(fold, seed)-then-aggregate rule for rank-based metrics, each rung produces 12 metric values (4 LODO folds times 3 seeds). The naive CI approach (sample standard-deviation divided by square-root of K) is anti-conservative because the 12 observations share training data — folds are not independent. The CI choice determines whether the headline rung-vs-rung Delta-CIs are honest or artificially tight.

Phase 0-04 walk Q8 surfaced two LODO-specific concerns:

1. **eval-toolkit ships cv_clt_ci implementing Bayle, Bayle, Janson and Mackey 2020 Annals of Statistics** Theorem 3.1 at src/eval_toolkit/bootstrap.py:963 — NOT Bates 2024 JASA as the SPEC ledger row 346 originally framed. Bayle 2020 is a CV-CLT precursor result with the same end-purpose (cross-validation-mean CI with correct coverage). Library-first discipline points to cv_clt_ci as the headline machinery.

2. **LODO folds are explicitly not exchangeable** per ADR-016 design — each fold holds out a different positive source (deepset / Lakera-gandalf / Lakera-mosscap / hackaprompt) with different size and attack-style character. The 4 sources differ in 1.5x to 6x sample size and in attack style (classical vs CTF vs competition vs Gandalf-CTF). A rung's per-fold metric will systematically differ across folds NOT because of sampling variance but because of source-character variance. This is exactly the OOD generalization signal we WANT to measure — but for CI purposes it inflates between-fold variance beyond what within-fold (iid) sampling implies. cv_clt_ci was derived for exchangeable k-fold; the LODO non-exchangeability is a real assumption violation.

The walk weighed five options — cv_clt_ci alone, Nadeau-Bengio 2003 corrected variance, Bates 2024 JASA nested-CV, block bootstrap on (fold) blocks, and bootstrap-per-fold-only. Brandon locked the hybrid Option F with a conditional escalation path for stratified-k-fold-within-LODO.

## Decision

### Headline CI machinery (row 346 primary lock)

**eval-toolkit cv_clt_ci** (Bayle 2020 implementation at src/eval_toolkit/bootstrap.py:963) on the 12 (fold, seed) per-rung metric values. Operationally:

```python
fold_seed_metrics = np.array([
    compute_metric(rung_predictions[fold, seed])
    for fold in range(4) for seed in [42, 1337, 2025]
])  # shape (12,)
ci = cv_clt_ci(fold_seed_metrics, confidence=0.95)
```

For rung-vs-rung Delta-CIs, the same primitive applied to the 12 per-(fold, seed) Delta values:

```python
delta_fold_seed = np.array([
    compute_metric(rung_B_preds[fold, seed]) - compute_metric(rung_A_preds[fold, seed])
    for fold in range(4) for seed in [42, 1337, 2025]
])  # shape (12,)
delta_ci = cv_clt_ci(delta_fold_seed, confidence=0.95)
```

K=12 is comfortable for the normal approximation underlying cv_clt_ci; sample variance with (K-1)=11 denominator is well-defined; z-quantile CI is appropriate.

### Spoke ablation (row 346 sensitivity check)

**Block bootstrap on (fold) blocks** — resample 4 folds with replacement (treating each fold as a block of 3 seed observations); per-resample compute mean-of-fold-metrics; 10K resamples; percentile CI on the resampled fold-mean.

```python
def block_bootstrap_on_folds(fold_seed_metrics_2d, n_resamples=10_000, seed=1):
    """fold_seed_metrics_2d: shape (n_folds=4, n_seeds=3)."""
    rng = np.random.default_rng(seed)
    fold_means = []
    n_folds = fold_seed_metrics_2d.shape[0]
    for _ in range(n_resamples):
        idx = rng.integers(0, n_folds, size=n_folds)
        resampled = fold_seed_metrics_2d[idx]
        fold_means.append(resampled.mean())
    return np.quantile(fold_means, [0.025, 0.975])
```

Block-bootstrap orchestrator is project-specific glue on top of eval_toolkit.bootstrap_ci primitive; library-first discipline preserved (the primitive itself stays as eval-toolkit shipped).

### Sensitivity-check flag

For each headline rung, the spoke reports both cv_clt_ci CI and block-bootstrap CI alongside; if the ratio exceeds 1.5:

```
block_bootstrap_CI_halfwidth / cv_clt_CI_halfwidth > 1.5
```

then the methodology spoke flags the rung as "LODO non-exchangeability dominates within-fold variance; headline CI may understate uncertainty." This converts the assumption violation into a named methodology finding rather than a hidden numerical caveat per ADR-005 Principle 2.

### Conditional escalation path

**Stratified-k-fold-within-LODO** (Fomin 2025 plus Nadeau-Bengio 2003 variance decomposition; approximately 5x compute relative to plain LODO) is pre-committed as a conditional escalation IF the cost ledger at Phase 4 entry shows cumulative spend well below ADR-020's per-job soft cap of 125 USD (rough threshold — under 75 USD cumulative). The escalation would replace the LODO 4-fold structure with stratified-k-fold-within-LODO 5-fold-within-LODO yielding 4 LODO splits times 5 inner folds times 3 seeds = 60 observations per rung (rather than 12), enabling Nadeau-Bengio 2003-style variance decomposition into (LODO-source-character variance) + (within-LODO-source sampling variance). If cost ledger does not permit, this escalation is deferred to afterword.

### Bates 2024 plus Nadeau-Bengio 2003 — explicit deferral

Both deferred to afterword:

- **Nadeau-Bengio 2003 standalone correction factor** — would need hand-rolling (not in eval-toolkit); correction factor calibrated for random k-fold not LODO; theoretical advantage doesn't outweigh implementation cost
- **Bates 2024 JASA nested-CV** — would need hand-rolling plus approximately 5x compute relative to plain LODO; provides provable finite-sample coverage but the asymptotic Bayle 2020 baseline is adequate at K=12

## Consequences

### Positive

- Library-first headline machinery via eval-toolkit cv_clt_ci — reviewer can re-run with the same toolkit version
- Block-bootstrap-on-folds spoke ablation directly addresses LODO non-exchangeability without adding a custom CI machinery — methodology-honest
- Sensitivity-check flag converts assumption violation into named methodology finding per ADR-005 Principle 2
- K=12 (4 folds times 3 seeds) is generous for cv_clt_ci normal approximation
- Conditional-escalation path keeps stratified-k-fold-within-LODO available without committing 5x compute upfront

### Negative

- Custom block-bootstrap orchestrator (~30-50 lines) added to scripts/run_bootstrap_battery.py — modest implementation cost
- Bates 2024 plus Nadeau-Bengio deferred — reviewer might prefer the newest methodology; mitigated by the spoke documenting why those are afterword
- LODO non-exchangeability remains a real concern even after the sensitivity check — if sensitivity-check fires for many rungs, the methodology spoke must own that signal

### Neutral

- Stratified-k-fold-within-LODO is pre-committed as conditional but is unlikely to fire in our 2.5-day budget (per Brandon's "likely not" framing); afterword-deferral path is the expected outcome

## Alternatives considered

- **Option A (cv_clt_ci alone, no ablation)**: simplest library-first; rejected because LODO non-exchangeability is a real concern that needs the sensitivity check
- **Option B (Nadeau-Bengio 2003 corrected variance only)**: historical standard; rejected because not in eval-toolkit; correction factor calibrated for random k-fold not LODO
- **Option C (Bates 2024 JASA nested-CV)**: best theoretical guarantees; rejected because requires nested CV with 5x more compute and mismatches LODO design
- **Option D (Block bootstrap on folds alone, no cv_clt_ci)**: methodology-honest for non-exchangeability but K=4 folds is small for block-bootstrap variance estimation; rejected as headline machinery (preserved as spoke ablation)
- **Option E (Bootstrap-per-fold only, no cross-fold aggregation)**: preserves per-fold honesty; rejected because no headline summary number — reviewer must scan 4 cells per rung
- **Naive row-level pooled bootstrap (Option F-equivalent in Q6)**: explicitly excluded by ADR-022's compute-per-(fold, seed)-then-aggregate rule for rank-based metrics

## Phase 1 deliverables

- scripts/run_bootstrap_battery.py — orchestrates cv_clt_ci headline + block-bootstrap-on-folds spoke ablation via joblib.Parallel(n_jobs=-1)
- evals/audit/cross_fold_ci_audit.parquet — per-rung headline-CI plus spoke-ablation-CI plus sensitivity-flag
- WRITEUP/methodology.md gains "Cross-fold CI methodology and LODO non-exchangeability" subsection
- assumptions.md A-008 added (severity medium) documenting LODO non-exchangeability concern

## References

See frontmatter references list. Primary anchors — Bayle, Bayle, Janson and Mackey 2020 Annals of Statistics (cv_clt_ci primitive); Bates, Hastie and Tibshirani 2024 JASA (nested-CV alternative deferred to afterword); Nadeau and Bengio 2003 Machine Learning journal (corrected-variance t-CI deferred to afterword); Politis and Romano 1994 (block bootstrap foundation for spoke ablation); Fomin 2025 (LODO methodology; stratified-k-fold-within-LODO conditional escalation reference); ADR-016 (LODO 4-fold design plus 3-seed protocol); ADR-022 (compute-per-(fold, seed)-then-aggregate rule for rank-based metrics; the 12 per-rung values that feed cv_clt_ci); ADR-020 (cost-cap dual-layer plus cost-ledger conditional-escalation gating).

## Transcript

See `transcripts/2026-05-15__phase-0-04__eval-framework.md` for the conversation that led to this decision.
