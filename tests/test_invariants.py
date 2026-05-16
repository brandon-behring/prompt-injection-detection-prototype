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
    """Trained rung slate contains exactly ModernBERT-base across three conditions.

    Per ADR-015 (rung architecture refinement, supersedes ADR-007), the trained
    slate is locked to ModernBERT-base x {frozen-probe, LoRA, full-FT}. A silent
    fallback to DeBERTa-v3-base is prohibited; any backbone swap requires a
    superseding ADR. This invariant asserts that the trained-rung config
    enumeration matches the locked slate.
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
