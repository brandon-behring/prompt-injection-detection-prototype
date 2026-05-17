"""Smoke tests for src/eval/operating_points.py (Phase 3 Commit 4 per ADR-025 + ADR-045)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import pytest

from src.eval.operating_points import (
    DETECTION_TARGET_FPR,
    VERIFICATION_TARGET_RECALL,
    compute_reachability_audit,
    fit_dual_policy_for_cell,
    fit_operating_point,
)
from src.eval.schemas import OperatingPointModel, ReachabilityAuditModel


def _separable_predictions(
    n: int = 200, seed: int = 0
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """y, s — well-separated binary classifier (high AUROC; targets reachable)."""
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, size=n).astype(np.int_)
    s = np.where(y == 1, rng.uniform(0.6, 0.99, size=n), rng.uniform(0.01, 0.4, size=n))
    return y, s.astype(np.float64)


def _degenerate_predictions(
    n: int = 50, seed: int = 0
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """y, s — ties between positive + negative (target unreachable case)."""
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, size=n).astype(np.int_)
    s = np.full(n, 0.5, dtype=np.float64)
    return y, s


# --------------------------------------------------------------------------- #
# Locked target constants per ADR-025
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_locked_target_values_match_adr_025() -> None:
    """DETECTION_TARGET_FPR=0.01 and VERIFICATION_TARGET_RECALL=0.99 per ADR-025 Q1."""
    assert DETECTION_TARGET_FPR == 0.01
    assert VERIFICATION_TARGET_RECALL == 0.99


# --------------------------------------------------------------------------- #
# fit_operating_point — detection + verification on separable data
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_fit_operating_point_detection_reachable() -> None:
    """Detection policy on separable data — target_reachable=True + low FPR."""
    y_val, s_val = _separable_predictions(seed=1)
    y_test, s_test = _separable_predictions(seed=2)
    op = fit_operating_point(
        rung="lora",
        fold=0,
        seed=42,
        policy="detection",
        target_value=0.01,
        y_val=y_val,
        s_val=s_val,
        y_test=y_test,
        s_test=s_test,
    )
    assert isinstance(op, OperatingPointModel)
    assert op.policy == "detection"
    assert op.target_reachable is True
    assert op.target_value == 0.01


@pytest.mark.smoke
def test_fit_operating_point_verification_reachable() -> None:
    """Verification policy on separable data — target_reachable=True + recall ≥ 0.99 on val."""
    y_val, s_val = _separable_predictions(seed=10)
    y_test, s_test = _separable_predictions(seed=11)
    op = fit_operating_point(
        rung="frozen-probe",
        fold=1,
        seed=43,
        policy="verification",
        target_value=0.99,
        y_val=y_val,
        s_val=s_val,
        y_test=y_test,
        s_test=s_test,
    )
    assert op.policy == "verification"
    assert op.target_reachable is True
    assert op.achieved_val_metric >= 0.99 or op.target_reachable is False


@pytest.mark.smoke
def test_fit_operating_point_detection_unreachable_at_strict_fpr() -> None:
    """Strict FPR target unreachable on degenerate data → target_reachable=False + fallback."""
    y_val, s_val = _degenerate_predictions(n=50, seed=0)
    y_test, s_test = _degenerate_predictions(n=50, seed=1)
    op = fit_operating_point(
        rung="full-ft",
        fold=2,
        seed=44,
        policy="detection",
        target_value=0.0001,
        y_val=y_val,
        s_val=s_val,
        y_test=y_test,
        s_test=s_test,
    )
    assert op.target_reachable is False
    # Detection fallback = threshold 1.0 (catch nothing → FPR=0 trivially).
    assert op.threshold == 1.0


# --------------------------------------------------------------------------- #
# fit_dual_policy_for_cell
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_fit_dual_policy_for_cell_returns_two_records() -> None:
    """Battery returns exactly 2 records (detection + verification) per ADR-025."""
    y_val, s_val = _separable_predictions(seed=20)
    y_test, s_test = _separable_predictions(seed=21)
    val_df = pd.DataFrame({"label": y_val, "predicted_proba_class1": s_val})
    test_df = pd.DataFrame({"label": y_test, "predicted_proba_class1": s_test})

    records = fit_dual_policy_for_cell(
        rung="lora",
        fold=0,
        seed=42,
        val_df=val_df,
        test_df=test_df,
    )
    assert len(records) == 2
    policies = {r.policy for r in records}
    assert policies == {"detection", "verification"}


@pytest.mark.smoke
def test_fit_dual_policy_rejects_empty_input() -> None:
    """Empty val or test DataFrame raises ValueError."""
    df_empty = pd.DataFrame({"label": [], "predicted_proba_class1": []})
    df_ok = pd.DataFrame({"label": [0, 1], "predicted_proba_class1": [0.3, 0.7]})
    with pytest.raises(ValueError):
        fit_dual_policy_for_cell(rung="x", fold=0, seed=42, val_df=df_empty, test_df=df_ok)
    with pytest.raises(ValueError):
        fit_dual_policy_for_cell(rung="x", fold=0, seed=42, val_df=df_ok, test_df=df_empty)


# --------------------------------------------------------------------------- #
# compute_reachability_audit per A-009
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_compute_reachability_audit_returns_validated_model() -> None:
    """ReachabilityAuditModel emitted per (rung, fold, seed) per A-009."""
    y_val, s_val = _separable_predictions(seed=30)
    y_test, s_test = _separable_predictions(seed=31)
    val_df = pd.DataFrame({"label": y_val, "predicted_proba_class1": s_val})
    test_df = pd.DataFrame({"label": y_test, "predicted_proba_class1": s_test})

    audit = compute_reachability_audit(
        rung="frozen-probe", fold=1, seed=43, val_df=val_df, test_df=test_df
    )
    assert isinstance(audit, ReachabilityAuditModel)
    assert audit.rung == "frozen-probe"
    assert audit.target_recall == pytest.approx(0.99)
