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


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_module_layout_taxonomy() -> None:
    """src/ + scripts/ + configs/ + tests/ taxonomy matches ADR-026 contract.

    Per ADR-026 (module layout — concern-grouped sub-packages under src/), the locked
    layout is src/{data, training, scoring, eval, utils}/ with each sub-package being
    a Python package (contains __init__.py); scripts/ contains entrypoint files only
    (no library code; not importable as a package); configs/{runpod, rungs, profiles,
    data}/ each contain at least one YAML file at Phase 1 entry; tests/{conftest.py,
    test_invariants.py, fixtures/, unit/, smoke/, integration/} structure preserved.
    This invariant asserts: (1) each of src/{data, training, scoring, eval, utils}
    exists as a directory with an __init__.py; (2) scripts/ exists and contains no
    __init__.py (entrypoints are scripts, not a package); (3) configs/{runpod, rungs,
    profiles, data} exist as directories at Phase 1 entry; (4) tests/{fixtures, unit,
    smoke, integration} exist as directories at Phase 1 entry; (5) the no-emoji
    invariant scan globs already operate over src/ scripts/ configs/ tests/ docs/ so
    the layout lock does not change scan-target enumeration. Adding or moving a
    top-level src/ sub-package post-lock requires a superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_makefile_execution_context_stratification() -> None:
    """Makefile carries the three-target execution-context stratification per ADR-027.

    Per ADR-027 (smoke vs canonical separation — three Makefile targets stratified by
    execution context), the Makefile must declare: (1) make smoke target — runs
    pytest -m smoke + a fixture-data E2E pass through scripts/run_metrics_battery.py
    with configs/profiles/fixtures.yaml; constraints — laptop only, no GPU calls, no
    network calls, total wall-clock under 10 minutes; (2) make test-integration
    target — runs pytest -m integration; integration tests use pytest.importorskip
    plus pytest.mark.skipif idiom for GPU-conditional skipping (verified via grep of
    @pytest.mark.integration tests in tests/integration/); same target invocation
    works on laptop (skips GPU tests) and on cloud pod (runs them as pre-flight);
    (3) make headline-cloud target — wraps runpod-deploy validate --all + run
    --dry-run + run --config configs/runpod/headline.yaml; cost-cap-gated 125 USD
    per job per ADR-020 + A-002; NOT a test target. (4) make headline-dry-run target
    exposes runpod-deploy run --dry-run standalone for cost preview without
    provisioning. This invariant asserts all 4 targets exist as Makefile rules and
    that test-integration tests use the importorskip+skipif idiom rather than failing
    on no-GPU laptops. The honest debugging-grade-here-rigorous-upstream framing
    paragraph is required in WRITEUP/methodology.md (separately enforced by the
    reporting-completeness invariant).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_coverage_floor_70pct_enforced() -> None:
    """Makefile coverage target enforces 70% flat coverage floor per ADR-028.

    Per ADR-028 (test coverage floor — 70% flat with upstream-issue-filing
    discipline), the Makefile coverage target must invoke pytest with
    --cov-fail-under=70 (replacing the prior ungated --cov=. --cov-report=term-missing
    form). The CI command is uv run pytest --cov --cov-fail-under=70
    --cov-report=term-missing. This invariant asserts: (1) the Makefile coverage
    target string contains --cov-fail-under=70 (verified via subprocess grep on
    Makefile); (2) the co-locked process commitment is documented in
    decisions/upstream_issues.md "How to use this ledger" section under a
    "Test-coverage-gap entries" subsection covering the [test-coverage-gap] +
    [not-applicable] tag conventions; (3) STYLE.md project-deltas first bullet
    references the locked 70% floor (no longer the [OPEN: ...] placeholder).
    Behavioral verification — when synthetic coverage drops below 70%, the make
    coverage exit code is non-zero — is deferred to a Phase 1 integration test that
    constructs a temp-dir minimal repo to exercise the gate without polluting the
    real coverage report.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_pytest_markers_registered_and_in_sync() -> None:
    """Exactly 4 pytest markers registered + pyproject.toml + conftest.py in sync per ADR-029.

    Per ADR-029 (test marker strategy — 4-marker ratification), the locked taxonomy is
    exactly {unit, smoke, integration, network} — no property, no golden, no slow, no
    gpu. Markers are registered in BOTH pyproject.toml [tool.pytest.ini_options]
    markers list AND tests/conftest.py via pytest_configure addinivalue_line calls;
    --strict-markers is enabled in pyproject addopts so unknown markers fail loudly.
    This invariant asserts: (1) pyproject.toml [tool.pytest.ini_options] markers list
    is exactly the set {unit, smoke, integration, network} — set-equality check (no
    extras, no missing); (2) tests/conftest.py pytest_configure registers exactly the
    same 4 markers via addinivalue_line; (3) --strict-markers appears in pyproject
    addopts; (4) no test file in tests/ uses an unregistered marker (verified via
    grep of @pytest.mark.<name> patterns in tests/ + comparison against the
    registered set; pytest-builtin markers like skip, parametrize, skipif, xfail are
    excluded from the comparison); (5) no marker file appears in eval-toolkit-only
    set {property, golden} since math rigor lives upstream per ADR-027. Marker-add or
    marker-remove post-lock requires a superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_quarto_site_config_present() -> None:
    """_quarto.yml + .github/workflows/publish.yml + index.qmd present per ADR-030.

    Per ADR-030 (deliverable format — repo-only with Quarto-rendered HTML site via
    GH Actions; supersedes ADR-002), the repo must declare a Quarto website config
    plus a GH Actions workflow that publishes the site to GH Pages. This invariant
    asserts: (1) _quarto.yml exists at repo root; (2) _quarto.yml parses as valid
    YAML and declares project.type=website; (3) _quarto.yml declares format.html
    (HTML output target only — no PDF auxiliary per ADR-030 Q1.b lock); (4) the
    sidebar block under website includes contents referencing all 8 spokes
    (eval-design plus methodology-guarantees plus limitations-and-future-work plus
    data-decisions plus model-rungs plus threshold-policy plus reference-scorer-audit
    plus reproducibility) plus an auto: decisions/ADR-*.md glob for the ADRs
    section; (5) .github/workflows/publish.yml exists and references both
    quarto-actions/setup@v2 and quarto-actions/publish@v2 steps; (6) the workflow
    triggers on push to main and on tag push v*; (7) the workflow declares
    permissions block with contents=write plus pages=write plus id-token=write.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_index_qmd_reading_paths_present() -> None:
    """index.qmd contains three reviewer reading paths per ADR-031.

    Per ADR-031 (reviewer reading paths via index.qmd; supersedes ADR-004 PDF-as-hub
    framing), index.qmd at repo root carries the entry-point reading-path guide
    that replaces the PDF cover sheet role. This invariant asserts: (1) index.qmd
    exists at repo root; (2) index.qmd contains a Quick-skim path section header
    (A1 hiring manager 15-min path); (3) index.qmd contains an Audit path section
    header (A2 ML researcher 60-min path); (4) index.qmd contains a Deep-dive
    section header (reproduce-numbers path with T0 plus T1 plus T3 references per
    ADR-034); (5) index.qmd contains a Repo map section enumerating src plus
    scripts plus configs plus decisions plus results plus tests plus WRITEUP plus
    WRITEUP/; (6) index.qmd contains a Submission anchors section listing the
    three reviewer URLs (source pin at submission tag plus live Quarto site plus GH
    release page) per ADR-033 reviewer-email URL plan; (7) WRITEUP/reproducibility.md
    spoke exists (slotted by ADR-031 for ADR-034 content). Adding a new spoke or
    reading-path section is allowed without superseding ADR; spoke removal requires
    superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_hf_hub_publication_naming_convention() -> None:
    """Published HF Hub model repos follow BBehring/prompt-injection-<rung> per ADR-032.

    Per ADR-032 (HF Hub publication — primary headline rungs only with model card
    discipline), every published rung must follow the BBehring/prompt-injection-
    <rung-name> naming convention plus carry a model card with the locked
    frontmatter schema. This invariant asserts at Phase 5 close: (1) for each
    rung in the headline-publication set (frozen-probe plus LoRA plus
    conditionally full-FT plus conditionally TF-IDF+LR per ADR-019 plus ADR-017
    final composition), a public HF Hub repo exists at BBehring/prompt-injection-
    <rung-name> (verified via huggingface_hub.HfApi().list_repos with author
    BBehring filter); (2) each repo's README YAML frontmatter contains the
    required keys — license (apache-2.0 inherited from ModernBERT-base) plus tags
    (text-classification plus prompt-injection plus safety) plus datasets (HF
    dataset IDs at the pinned SHAs per ADR-016) plus model-index.results
    (per-rung headline metrics from results.json with the pooled-OOD column per
    ADR-021) plus intended use plus limitations plus citation; (3) reference
    scorers per ADR-018 are NOT present under BBehring/ namespace (they remain
    at their canonical authors). Publication-set composition is provisional —
    final list revisitable at Phase 5 per ADR-032 extension condition without
    superseding this invariant.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_submission_tag_changelog_present() -> None:
    """CHANGELOG.md follows Keep-a-Changelog 1.1.0 + has v1.0.0 section at submission per ADR-033.

    Per ADR-033 (GitHub release strategy — rehearsal plus submission plus
    patches), CHANGELOG.md is committed at repo root in Keep-a-Changelog 1.1.0
    format with entries written in human language not git-shortlog dumps. This
    invariant asserts: (1) CHANGELOG.md exists at repo root; (2) the file
    references keepachangelog.com and semver.org in its preamble (format
    declaration); (3) at v1.0.0 submission tag time, a [v1.0.0] section exists
    with at minimum a Submission subsection naming the 4 publication artefacts
    (Quarto site published to GH Pages plus HF Hub model repos published plus
    methodology writeup plus reviewer URLs); (4) at v1.0.0 submission tag time,
    a [v0.9.0-rc1] section exists naming the rehearsal tag's purpose; (5)
    Keep-a-Changelog section structure is followed (Added plus Changed plus
    Deprecated plus Removed plus Fixed plus Security as applicable); (6) version
    links at file bottom match the SemVer tag format. Patch tags v1.0.x add
    sections without changing existing ones (audit-trail discipline).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 1")
def test_reproducibility_tier_documented() -> None:
    """WRITEUP/reproducibility.md documents T0+T1+T3 tier ladder per ADR-034.

    Per ADR-034 (reproducibility tier — full ladder T0 eval-from-hub plus T1
    smoke plus T3 headline-cloud), the WRITEUP/reproducibility.md spoke
    documents the tier ladder with verbatim commands plus cost plus time plus
    what-each-tier-verifies plus what-each-tier-does-NOT-verify. This invariant
    asserts: (1) WRITEUP/reproducibility.md exists; (2) the spoke contains all
    three tier names T0 plus T1 plus T3 in section headers; (3) each tier has a
    verbatim command in a code block — make smoke plus make eval-from-hub plus
    make headline-cloud; (4) the Makefile contains all three target names
    (smoke plus eval-from-hub plus headline-cloud) as rules; (5) the spoke
    contains the tier-coverage matrix with cost plus time plus verifies plus
    does-not-verify columns for each tier; (6) the spoke explicitly carves out
    T2 (test-integration) as a developer-tool tier with rationale (not promoted
    to reviewer-facing per ADR-034 Q4 walk); (7) the spoke includes the ACM
    artifact-badging mapping subsection (T0+T1 supply Functional+Reusable; T3
    supplies Reproducible). Adding a new tier requires superseding ADR; tier
    removal requires superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")
