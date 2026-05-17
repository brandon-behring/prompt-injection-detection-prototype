"""Phase 3 dual-policy operating-point fitting per ADR-025 + ADR-045 Commit 4.

ADR-025 locks two policies at symmetric 1% cost weights:
- Detection — FPR ≤ 1% on validation via `TargetFPRSelector(0.01)` → max recall feasible
- Verification — recall ≥ 99% on validation via `TargetRecallSelector(0.99)` → min FPR feasible

Both fit per-(rung, fold, seed) on validation only per ADR-011 Guarantee 6.
Apply the fitted threshold on test and emit `OperatingPointModel` rows.
Verification-target reachability is audited per A-009 — if the val recall
target is unreachable, `target_reachable=False` and the audit JSON carries
fallback values for honest reporting.

Detection-policy fitting on reference rungs is excluded per SPEC §4 dual-
policy applicability lock — only trained rungs receive operating points.
Caller is responsible for filtering by `contamination_state` before
invoking these functions on reference-scorer predictions.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd
from eval_toolkit.metrics import metrics_at_threshold
from eval_toolkit.thresholds import TargetFPRSelector, TargetRecallSelector
from numpy.typing import NDArray

from src.eval.schemas import OperatingPointModel, PolicyName, ReachabilityAuditModel

# Locked target values per ADR-025 Q1 — symmetric 1%.
DETECTION_TARGET_FPR: Final[float] = 0.01
VERIFICATION_TARGET_RECALL: Final[float] = 0.99

# Fallback thresholds when selector raises RuntimeError on unreachable target.
# Detection fallback = 1.0 (catch nothing → FPR=0 ≤ target trivially); but
# this loses all recall — caller should re-examine.
# Verification fallback = 0.0 (catch everything → recall=1.0 ≥ target
# trivially); but this floods FPR — A-009 audit captures this.
_DETECTION_FALLBACK_THRESHOLD: Final[float] = 1.0
_VERIFICATION_FALLBACK_THRESHOLD: Final[float] = 0.0


def fit_operating_point(
    *,
    rung: str,
    fold: int,
    seed: int,
    policy: PolicyName,
    target_value: float,
    y_val: NDArray[np.int_],
    s_val: NDArray[np.float64],
    y_test: NDArray[np.int_],
    s_test: NDArray[np.float64],
) -> OperatingPointModel:
    """Fit one operating point on val; apply on test; return validated record.

    Parameters
    ----------
    rung : str
        Rung identifier (trained rungs only per ADR-025; reference rungs raise).
    fold : int
        LODO fold 0..3.
    seed : int
        Training seed.
    policy : {"detection", "verification"}
        Which policy to fit.
    target_value : float
        Target FPR for detection or target recall for verification.
    y_val, s_val : numpy.ndarray
        Validation labels + scores; selector fits on these.
    y_test, s_test : numpy.ndarray
        Test labels + scores; fitted threshold applied here for reporting.

    Returns
    -------
    OperatingPointModel
        Validated record with threshold + target_reachable + achieved metrics.
    """
    if policy == "detection":
        selector_callable = TargetFPRSelector(target_value).select
        fallback_threshold = _DETECTION_FALLBACK_THRESHOLD
        achieved_metric_key = "fpr"
    else:
        selector_callable = TargetRecallSelector(target_value).select
        fallback_threshold = _VERIFICATION_FALLBACK_THRESHOLD
        achieved_metric_key = "recall"

    try:
        result = selector_callable(y_val, s_val)
        target_reachable = True
        threshold = float(result.threshold)
    except RuntimeError:
        target_reachable = False
        threshold = fallback_threshold

    val_metrics = metrics_at_threshold(y_val, s_val, threshold=threshold)
    test_metrics = metrics_at_threshold(y_test, s_test, threshold=threshold)
    achieved_val_metric = float(val_metrics[achieved_metric_key])

    return OperatingPointModel(
        rung=rung,
        fold=fold,
        seed=seed,
        policy=policy,
        target_value=target_value,
        threshold=threshold,
        target_reachable=target_reachable,
        achieved_val_metric=achieved_val_metric,
        achieved_test_recall=float(test_metrics["recall"]),
        achieved_test_fpr=float(test_metrics["fpr"]),
        achieved_test_precision=float(test_metrics["precision"]),
    )


def fit_dual_policy_for_cell(
    *,
    rung: str,
    fold: int,
    seed: int,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> list[OperatingPointModel]:
    """Fit both detection + verification policies for one (rung, fold, seed) cell.

    Parameters
    ----------
    rung : str
        Trained rung identifier (e.g. "lora").
    fold : int
        LODO fold 0..3.
    seed : int
        Training seed.
    val_df : pandas.DataFrame
        Validation predictions parquet rows (must carry "label" + "predicted_proba_class1").
    test_df : pandas.DataFrame
        Test predictions parquet rows (same schema).

    Returns
    -------
    list of OperatingPointModel
        Length 2: detection record + verification record.
    """
    if val_df.empty or test_df.empty:
        raise ValueError("fit_dual_policy_for_cell requires non-empty val_df + test_df")

    y_val = val_df["label"].to_numpy(dtype=np.int_)
    s_val = val_df["predicted_proba_class1"].to_numpy(dtype=np.float64)
    y_test = test_df["label"].to_numpy(dtype=np.int_)
    s_test = test_df["predicted_proba_class1"].to_numpy(dtype=np.float64)

    detection = fit_operating_point(
        rung=rung,
        fold=fold,
        seed=seed,
        policy="detection",
        target_value=DETECTION_TARGET_FPR,
        y_val=y_val,
        s_val=s_val,
        y_test=y_test,
        s_test=s_test,
    )
    verification = fit_operating_point(
        rung=rung,
        fold=fold,
        seed=seed,
        policy="verification",
        target_value=VERIFICATION_TARGET_RECALL,
        y_val=y_val,
        s_val=s_val,
        y_test=y_test,
        s_test=s_test,
    )
    return [detection, verification]


def compute_reachability_audit(
    *,
    rung: str,
    fold: int,
    seed: int,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> ReachabilityAuditModel:
    """Compute verification-target reachability audit per A-009 + ADR-025 Q4.

    Emits one ReachabilityAuditModel per (rung, fold, seed) tuple. Caller
    aggregates these into `evals/audit/verification_reachability.json`.
    """
    if val_df.empty or test_df.empty:
        raise ValueError("compute_reachability_audit requires non-empty val_df + test_df")

    y_val = val_df["label"].to_numpy(dtype=np.int_)
    s_val = val_df["predicted_proba_class1"].to_numpy(dtype=np.float64)
    y_test = test_df["label"].to_numpy(dtype=np.int_)
    s_test = test_df["predicted_proba_class1"].to_numpy(dtype=np.float64)

    verification = fit_operating_point(
        rung=rung,
        fold=fold,
        seed=seed,
        policy="verification",
        target_value=VERIFICATION_TARGET_RECALL,
        y_val=y_val,
        s_val=s_val,
        y_test=y_test,
        s_test=s_test,
    )

    # achieved_val_metric for verification is the achieved val recall — directly
    # reusable for the audit record.
    return ReachabilityAuditModel(
        rung=rung,
        fold=fold,
        seed=seed,
        target_reachable=verification.target_reachable,
        achieved_val_recall=verification.achieved_val_metric,
        fallback_threshold=verification.threshold,
        fallback_test_fpr=verification.achieved_test_fpr,
    )
