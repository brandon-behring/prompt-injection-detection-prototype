"""Invariant tests — skip-marked stubs at seed time.

Each invariant corresponds to a [LOCKED] rule in SPEC_GREENFIELD.md §5
(Tests-as-invariants). Stubs fail with NotImplementedError so that
Phase 1 must explicitly unskip + implement before the test can pass.

Per SPEC_GREENFIELD Phase 0 done criterion (d), these stubs must
exist at seed time and remain in `pytest -m unit` collection.
"""

import pytest


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_class_balance_per_fold() -> None:
    """Per-fold negative:positive ratio is within tolerance."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_source_disjoint_train_test() -> None:
    """Each test slice's source is not present in the train sources."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_hyperparameter_immutability() -> None:
    """Config hash matches the committed value (no silent hyperparameter mutation)."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_calibration_honesty_val_only() -> None:
    """Temperature scaling fits only on validation, not test."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_reporting_completeness_assumptions_in_caveats() -> None:
    """Every assumption with severity >= medium in assumptions.md appears in the WRITEUP caveats block."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_no_emoji_in_repo() -> None:
    """No emoji code points in source / docs (per SPEC_GREENFIELD §5)."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_config_result_classes_frozen_slotted() -> None:
    """Classes whose name ends in Config or Result are frozen + slotted dataclasses."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_trained_backbone_modernbert_only_invariant() -> None:
    """Trained transformer rungs contain exactly ModernBERT-base across three conditions.

    Per ADR-015 (rung architecture refinement, supersedes ADR-007), the trained
    transformer slate is locked to ModernBERT-base x {frozen-probe, LoRA, full-FT}.
    A silent fallback to DeBERTa-v3-base is prohibited; any backbone swap requires a
    superseding ADR. Per ADR-017 (rung-slate expansion), the trained slate also
    includes a TF-IDF+LR classical floor rung — this invariant asserts the transformer
    portion of the trained slate (not all trained rungs) matches the locked
    ModernBERT-base × 3-conditions enumeration; the classical-floor rung is carved out
    and asserted separately by `test_classical_floor_rung_present`.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_truncation_policy_adaptive_chunked_max_pool() -> None:
    """Eval-path truncation policy is adaptive chunked scoring with max-pool aggregation.

    Per ADR-014 (threat-model bundle, Q4 lock), evaluation-time inputs that
    exceed the length cap are split into overlapping chunks of size cap with
    stride cap // 2; each chunk is scored independently; per-sample score is
    the max over chunk scores. Training-time uses head-truncation (HF default).
    This invariant asserts that the eval pipeline's truncation handler matches
    the locked policy and that aggregator equals max-pool.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_source_manifest_schema_valid() -> None:
    """data/source_manifest.yaml parses, contains all 11 sources, each has SHA + license + role.

    Per ADR-016 (Q3 lock), HF revisions and GitHub commit SHAs are pinned at
    Phase 1 entry in unified data/source_manifest.yaml. This invariant asserts
    the manifest parses as valid YAML, contains all 11 expected sources
    (4 train positives + 2 train benigns + 5 OOD slices), and each source
    record carries the required fields (type, revision/commit_sha, license,
    role). Schema version equals 1.0; bump_history is a list.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_dedup_calibration_persisted() -> None:
    """evals/dedup_calibration.json exists with FPR+FNR at threshold 0.80 plus cosine histograms.

    Per ADR-016 (Q4 lock), the dedup encoder is all-MiniLM-L6-v2 cosine at
    threshold 0.80 with simplified calibration evidence. This invariant
    asserts the calibration JSON exists, contains FPR + FNR measured against
    a 50-pair labeled holdout at threshold 0.80, includes dedup counts at
    sensitivity thresholds {0.75, 0.80, 0.85}, and contains per-source cosine
    distribution histograms (anisotropy sanity check per Ethayarajh 2019).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_benign_contamination_scan_clean() -> None:
    """Benign sources (LMSYS + UltraChat) have <=2% contamination per A-005.

    Per ADR-016 Phase 1 revisit triggers (assumption A-005), the contamination
    scan flags any benign sample with MiniLM cosine >= 0.85 to a known
    injection template. This invariant asserts contamination rate stays at
    or below 2% in both LMSYS-Chat-1M (post English-only filter and
    post-subsample) and UltraChat (post-subsample). If invariant fails,
    A-005 fires and a superseding ADR adjusts source mix or filter threshold.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_classical_floor_rung_present() -> None:
    """TF-IDF + LR classical floor rung is in the trained-rung config enumeration.

    Per ADR-017 (trained-rung-slate expansion), the trained slate is expanded
    from 3 ModernBERT-base conditions to 4 rungs by prepending a TF-IDF + LR
    classical floor rung. This invariant asserts the trained-rung config
    enumeration contains exactly one classical-floor rung with the locked recipe —
    sklearn TfidfVectorizer combining word 1-2-grams (max_features=15000,
    sublinear_tf=True) + char 3-5-grams (max_features=15000) plus sklearn
    LogisticRegression with solver=liblinear + C=1.0 + class_weight=balanced +
    max_iter=1000. Restores the SPEC §2 line 121 common-pattern default.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_per_epoch_predictions_present() -> None:
    """Per-epoch parquet predictions exist for every transformer (rung, seed, fold).

    Per ADR-019 (LoRA + transformer training recipe), epoch-2 predictions are
    the headline numbers and epoch-1 predictions are reported as a diagnostic
    ablation. This invariant asserts the prediction directory contains exactly
    72 transformer-rung parquet files for the 3 transformer rungs × 3 seeds ×
    4 LODO folds × 2 epochs enumeration, with file paths matching the convention
    evals/predictions/<rung>__fold<F>__seed<S>__epoch<N>.parquet. TF-IDF + LR
    rung predictions (no epoch dimension; 12 files) and reference-rung
    predictions (16 files) are asserted separately.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_flash_attn_fallback_present() -> None:
    """ModernBERT loader has try/except fallback from flash_attention_2 to SDPA.

    Per ADR-020 (compute infrastructure and cost discipline), the GPU-failover
    ladder may land us on smaller GPU classes without flash_attention_2 support.
    Per the runpod-deploy flash-attention-fallback recipe, the model loader must
    wrap AutoModelForSequenceClassification.from_pretrained with attn_implementation
    equals flash_attention_2 in a try/except catching (ValueError, ImportError) plus
    fall through to a second load without attn_implementation set (stock SDPA). The
    fallback path must log a flash_attn_fallback event so the audit trail captures
    which physical config produced each per-row prediction. This invariant asserts
    the production model-load function has the try/except structure with the
    correct exception types caught and an event log call in the fallback branch.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_effective_batch_constant_across_gpu_classes() -> None:
    """BATCH_TABLE preserves effective batch = 32 across all GPU classes.

    Per ADR-020 (compute infrastructure), the per-GPU-class BATCH_TABLE
    scales per_device_train_batch_size and gradient_accumulation_steps
    together such that their product equals 32 for every GPU class in the
    pod.gpu_order failover ladder. This invariant asserts the table covers
    H100 + H200 + A100-80G + A100-40G + L40S + L40 (and any subsequent additions)
    with per_device times grad_accum equals 32 for each entry. The effective batch
    is the actual gradient-computation hyperparameter; per_device and grad_accum
    are throughput knobs that do not change the gradient computation. Preserves
    SPEC §2 hyperparameter-immutability invariant under GPU substitution.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_ood_aggregation_layout() -> None:
    """OOD slate reports pooled-headline plus per-slice-spoke aggregation views.

    Per ADR-021 (eval slate aggregation), the 5 OOD slices locked by ADR-016
    (NotInject + XSTest + JBB-Behaviors + BIPIA + InjecAgent) are reported in
    two complementary aggregation views. This invariant asserts: (1) the headline
    emit (evals/results.json) contains a pooled-OOD column per rung concatenating
    rows across the 5 slices yielding a single AUPRC + AUROC + recall@FPR + ECE +
    Brier per rung; (2) the spoke artifact (evals/ood_per_slice.parquet) contains
    a 5-by-rung grid with per-slice bootstrap CIs; (3) all 5 OOD slices appear in
    the spoke artifact exactly once per rung.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_recall_at_fpr_pinpoint_volatility() -> None:
    """Recall@FPR=0.1% pinpoint reports volatility surfaces at pooled level.

    Per ADR-021 (recall@FPR pinpoint feasibility), the 0.1% pinpoint is computed
    only at the pooled aggregation level and reports four volatility surfaces.
    This invariant asserts: (1) per-rung headline emit contains half-width column
    alongside point estimate for the 0.1% pinpoint; (2) evals/audit/per_rung_audit.json
    contains a resample-degeneracy fraction (fraction of bootstrap resamples where
    the FPR=0.001 threshold pinned at less than 1 false-positive count); (3)
    evals/audit/pinpoint_threshold_drift.json contains the distribution of
    *thresholds* across resamples for the 0.1% pinpoint; (4) per-slice and
    per-LODO-fold aggregations report the 0.1% pinpoint cell as "not computable
    at this aggregation level (n_neg too small)" rather than a numerical value.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_bootstrap_n_and_stability_check() -> None:
    """Bootstrap apparatus runs 10K @ seed=1 headline + 10K @ seed=2 stability check.

    Per ADR-022 (statistical inference apparatus), the bootstrap protocol for every
    headline CI is: 10K iterations via eval_toolkit.bootstrap_ci (BCa for marginals)
    at seed=1 as headline; 10K iterations at seed=2 as stability check; flag in
    audit JSON when stability-check CI half-width differs from headline CI half-width
    by more than 5 percent (signals resampling instability). This invariant asserts
    the bootstrap orchestrator (scripts/run_bootstrap_battery.py) emits both the
    seed=1 headline CI and the seed=2 stability-check CI to
    evals/audit/bootstrap_stability_check.parquet, with a half-width-diff-percent
    column and a flag column (boolean: True when diff > 5 percent).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_paired_across_rungs_pairing() -> None:
    """Multi-seed pairing structure follows ADR-022 gap-honest defaults.

    Per ADR-022 (multi-seed protocol details), trained-vs-trained rung comparisons
    use row-level pairing via eval_toolkit.paired_bootstrap_diff; trained-vs-reference
    rung comparisons use per-row replication of reference scores across the 12 trained
    seeds (reference-side variance is correctly fold-only). This invariant asserts:
    (1) for any trained-vs-trained comparison, the input to paired_bootstrap_diff
    is a 1-D array of row-level predictions with shape matching the pooled test set;
    (2) for any trained-vs-reference comparison, the reference rung's score for a
    given row is identical across the 12 (fold, seed) slots of the trained rung
    (replication invariant); (3) the per-(rung, fold, seed) observation parquet
    (evals/audit/per_seed_observations.parquet) contains 12 rows per trained rung
    and 4 rows per reference rung.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_calibration_battery_composition() -> None:
    """Calibration battery emits raw plus temperature plus isotonic intervention states.

    Per ADR-023 (calibration battery composition), the headline emit contains
    ECE-equal-mass(n_bins=15, quantile binning) plus Brier per rung on raw scores
    only. The spoke artifact contains all 4 ECE variants (L1/L2 plug-in/debiased)
    plus Brier decomposition plus reliability diagrams plus temperature-applied and
    isotonic-applied ECE/Brier deltas. This invariant asserts: (1) headline
    evals/results.json contains exactly 2 calibration columns per rung
    (ECE-equal-mass-raw, Brier-raw); (2) spoke evals/calibration_spoke.parquet
    contains 4 ECE variants plus Brier plus temperature-applied and
    isotonic-applied versions of each; (3) the calibrator-fit input rows are
    drawn from the validation split only (no test rows; per ADR-011 Guarantee 6);
    (4) per-(rung, fold, seed) calibrator artifacts exist at
    evals/calibration/<rung>__fold<F>__seed<S>__intervention<temperature|isotonic|raw>.json.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_monotonic_intervention_preserves_ranks() -> None:
    """Calibration interventions are monotonic and therefore preserve rank-based metrics.

    Per ADR-023 (calibration battery), calibration interventions (temperature
    scaling and isotonic regression) are monotonic by construction; rank-based
    headline metrics (PR-AUC, ROC-AUC, recall@FPR) are unchanged by intervention.
    This sanity-check invariant asserts that for any (rung, fold, seed) tuple,
    PR-AUC and ROC-AUC after temperature scaling equal PR-AUC and ROC-AUC before
    temperature scaling within numerical tolerance (1e-9); same for isotonic.
    If false, the calibrator implementation is producing non-monotonic outputs —
    a bug in the calibrator-fit chain.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_cross_fold_ci_methodology() -> None:
    """Cross-fold CI machinery runs cv_clt_ci headline plus block-bootstrap-on-folds spoke.

    Per ADR-024 (cross-fold CI methodology), the headline cross-fold CI uses
    eval_toolkit.bootstrap.cv_clt_ci (Bayle 2020 Theorem 3.1) on the 12 per-(fold, seed)
    metric values per rung; the spoke ablation uses block-bootstrap-on-folds
    (resample 4 folds with replacement; per-resample compute mean-of-fold-metrics;
    10K resamples; percentile CI); the sensitivity-check flag fires when
    block_bootstrap_CI_halfwidth / cv_clt_CI_halfwidth > 1.5. This invariant asserts:
    (1) cv_clt_ci primitive is invoked on 12 per-(fold, seed) values per rung;
    (2) block-bootstrap-on-folds orchestrator produces percentile CI on 10K resamples;
    (3) sensitivity-check flag column emits in evals/audit/cross_fold_ci_audit.parquet;
    (4) when sensitivity flag fires, the methodology spoke contains the named
    "LODO non-exchangeability" paragraph. The conditional stratified-k-fold-within-LODO
    escalation is gated on evals/cost_ledger.csv state at Phase 4 entry — not asserted
    by this invariant (deferred to manual Phase 4 audit).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_dual_policy_threshold_pairing() -> None:
    """Dual-policy thresholds fit per-(rung, fold, seed) on val with paired CI propagation.

    Per ADR-025 (dual-policy threshold characterization at symmetric 1% cost weights),
    the Detection policy fits eval_toolkit.thresholds.TargetFPRSelector(0.01) on
    validation per-(rung, fold, seed) and the Verification policy fits
    eval_toolkit.thresholds.TargetRecallSelector(0.99) on validation per-(rung, fold, seed);
    24 thresholds per trained rung × 4 trained rungs equals 96 threshold-pair
    instances total; CI propagation uses eval_toolkit.bootstrap.paired_bootstrap_op_point_diff
    (two-level bootstrap — refit threshold per val resample, apply on test resample,
    compute paired diff) consistent with ADR-022's per-(seed) threshold protocol.
    This invariant asserts: (1) the dual-policy threshold orchestrator
    (scripts/fit_dual_policy_thresholds.py) calls TargetFPRSelector(0.01).select(y_val, s_val)
    and TargetRecallSelector(0.99).select(y_val, s_val) for every (trained_rung, fold, seed)
    tuple; (2) reference rungs (4 untrained rungs per ADR-018) are excluded from
    dual-policy fitting (only recall@FPR pinpoints applied per SPEC §4 dual-policy
    applicability lock); (3) the bootstrap battery (scripts/run_bootstrap_battery.py)
    invokes paired_bootstrap_op_point_diff for trained-vs-trained dual-policy comparisons;
    (4) the headline emit (evals/results.json) carries an "FPR @ recall ≥ 99%" column
    on trained rungs and a footnote on the existing recall@FPR=1% column tagging it as
    the detection-policy operating point.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_verification_reachability_audit() -> None:
    """Verification-target reachability audit JSON is emitted per-(rung, fold, seed).

    Per ADR-025 Q4 (infeasibility handling) and assumption A-009, when
    TargetRecallSelector(0.99) cannot satisfy the recall ≥ 99% constraint on a
    (rung, fold, seed) val slice, the reporting protocol emits per-(rung, fold, seed)
    reachability evidence to evals/audit/verification_reachability.json and the
    headline cell carries an asterisk flag. This invariant asserts:
    (1) evals/audit/verification_reachability.json exists with the locked schema
    (top-level dict keyed by rung_id, then fold_id, then seed; each leaf entry contains
    target_reachable bool, target_recall=0.99, achieved_val_recall float, fallback_threshold
    float, fallback_test_fpr float); (2) every (trained_rung, fold, seed) tuple has an
    entry (96 entries total = 4 trained rungs × 4 folds × 3 seeds × 2 — but only the 96
    verification-side entries appear; detection-side reachability is trivially 100% so
    no audit needed); (3) any entry with target_reachable equals false has a corresponding
    asterisk flag in the headline emit (evals/results.json) cell for that rung's
    "FPR @ recall ≥ 99%" column at the matching aggregation level; (4) the spoke
    (WRITEUP/threshold-policy.md) "Verification-target reachability across trained rungs"
    subsection enumerates per-rung reachability rate (count of reachable cells / total
    cells per rung) as a cross-rung comparison artifact.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")
