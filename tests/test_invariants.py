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
