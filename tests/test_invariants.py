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
