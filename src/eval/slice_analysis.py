"""Phase 3 OOD slate slice aggregation per ADR-021 + ADR-045 Commit 4.

Per ADR-021, the 5 OOD slices (NotInject + XSTest + JBB-Behaviors + BIPIA
+ InjecAgent) are reported in two aggregation views:

1. **Pooled headline** — concatenate rows across the 5 slices; compute one
   AUPRC + AUROC + recall@FPR + ECE + Brier per rung. The 0.1% recall@FPR
   pinpoint is computed at this level only (pooled n_neg ≈ 16-20K yields
   meaningful CI). Volatility surfaces (half-width flag, resample
   degeneracy fraction, threshold drift dump) are emitted per ADR-021.

2. **Per-slice spoke** — 5-by-rung grid with per-slice metrics; the 0.1%
   pinpoint is reported as None (n_neg too small per ADR-021).

Reference scorers participate in both views with explicit contamination
caveats per ADR-018.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd
from eval_toolkit import (
    is_metric_defined_for_slice as _et_is_metric_defined_for_slice,
)
from eval_toolkit.metrics import metrics_at_threshold, pr_auc, roc_auc
from eval_toolkit.thresholds import TargetFPRSelector
from numpy.typing import NDArray

from src.eval.calibration_battery import HEADLINE_N_BINS, compute_calibration_record
from src.eval.schemas import MetricsRecordModel, SliceMetricsModel

# ADR-021 + ADR-016 5-slice OOD slate (lowercase; matches manifest source
# names per ADR-041 normalizer convention).
OOD_SLICE_NAMES: Final[tuple[str, ...]] = (
    "notinject",
    "xstest",
    "jbb_behaviors",
    "bipia",
    "injecagent",
)

# Single-class OOD slices per source design (locked per ADR-016 + ADR-021):
# - bipia: all-positive (indirect injection via email body)
# - injecagent: all-positive (multi-turn agentic injection)
# - notinject: all-negative (benign-but-injection-like)
# Per Item 4 of the v1.0.0 closure sweep (Q9 lock), AUROC/AUPRC are
# mathematically undefined on single-class slices and the source-level
# filter excludes them from bootstrap / cross-fold-CI / MDE artifacts
# rather than emitting degenerate 1.0/0.0 values. WRITEUP §Methodology
# caveats documents the convention.
#
# This set is project-specific knowledge (which slice names in this
# OOD slate are single-class by design). The is-metric-degenerate
# decision is delegated to upstream `eval_toolkit.is_metric_defined_for_slice`
# per the library-first invariant (v1.0.6; consuming eval-toolkit#39
# resolved 2026-05-18).
SINGLE_CLASS_SLICES: Final[frozenset[str]] = frozenset({"bipia", "injecagent", "notinject"})


def is_metric_defined_for_slice(slice_name: str, metric_name: str) -> bool:
    """Thin project wrapper around ``eval_toolkit.is_metric_defined_for_slice``.

    Maps the project's slice-name → single-class-class-distribution
    knowledge (``SINGLE_CLASS_SLICES``) onto the upstream primitive's
    ``is_single_class`` boolean kwarg. Returns ``False`` iff the
    (slice, metric) pair is mathematically undefined and should be
    filtered at source rather than emitting degenerate values.

    The actual degenerate-detection logic + the canonical incompatible-
    metrics set (``auroc`` + ``auprc``) lives upstream at
    ``eval_toolkit.SINGLE_CLASS_INCOMPATIBLE_METRICS``. See
    WRITEUP §Methodology caveats for the convention; see
    eval-toolkit#39 (closed 2026-05-18) for the upstream primitive.

    Parameters
    ----------
    slice_name : str
        The slice identifier (e.g., ``"bipia"``, ``"pooled_ood"``).
    metric_name : str
        The metric identifier (e.g., ``"auroc"``, ``"auprc"``,
        ``"recall_at_fpr_1"``, ``"ece_equal_mass"``).

    Returns
    -------
    bool
        ``True`` if the metric is defined on the slice and should be
        computed; ``False`` if the pairing is mathematically undefined.
    """
    return bool(
        _et_is_metric_defined_for_slice(
            metric_name,
            is_single_class=slice_name in SINGLE_CLASS_SLICES,
        )
    )


# Pooled-aggregation special name (not an OOD slice name, sits alongside).
POOLED_OOD_SLICE_NAME: Final[str] = "pooled_ood"
IID_SLICE_NAME: Final[str] = "iid"

# ADR-021 recall@FPR pinpoint triad.
RECALL_AT_FPR_PINPOINTS: Final[tuple[float, ...]] = (0.001, 0.01, 0.05)

# ADR-021 line 53-65 volatility-surface threshold for 0.1% pinpoint.
VOLATILITY_WIDE_CI_RATIO: Final[float] = 0.5  # half_width > 0.5 * point_estimate → flag


def compute_recall_at_fpr(
    y_true: NDArray[np.int_],
    y_score: NDArray[np.float64],
    fpr_target: float,
) -> float | None:
    """Recall at the smallest threshold s.t. FPR ≤ fpr_target on the slice.

    Returns None when fpr_target is unreachable (e.g., slice too small or
    all-positive); caller decides how to encode the cell in the emit.
    """
    if len(y_true) == 0:
        return None
    if y_true.sum() == 0 or y_true.sum() == len(y_true):
        return None
    try:
        result = TargetFPRSelector(fpr_target).select(y_true, y_score)
        return float(result.recall)
    except RuntimeError:
        return None


def compute_metric_record(
    *,
    rung: str,
    fold: int,
    seed: int,
    slice_name: str,
    df: pd.DataFrame,
    include_0_1_pinpoint: bool = False,
) -> MetricsRecordModel:
    """Compute the headline metric record for one (rung, fold, seed, slice) cell.

    Per ADR-021 + ADR-023, returns AUPRC + AUROC + recall@FPR + ECE + Brier.

    Parameters
    ----------
    rung : str
        Rung identifier.
    fold : int
        LODO fold or -1 for reference scorers.
    seed : int
        Training seed or -1 for reference scorers.
    slice_name : str
        Slice identifier — "iid", "pooled_ood", or one of the 5 OOD slice names.
    df : pandas.DataFrame
        Predictions parquet rows for this slice (must carry "label" + "predicted_proba_class1").
    include_0_1_pinpoint : bool
        Whether to compute recall@FPR=0.1% (pooled-only per ADR-021).

    Returns
    -------
    MetricsRecordModel
        Validated record. recall_at_fpr_0_1 is None when include_0_1_pinpoint=False.
    """
    if df.empty:
        raise ValueError(f"compute_metric_record requires non-empty df for slice {slice_name!r}")

    y_true = df["label"].to_numpy(dtype=np.int_)
    y_score = df["predicted_proba_class1"].to_numpy(dtype=np.float64)
    n_positive = int(y_true.sum())
    n_negative = int(len(y_true) - n_positive)

    # eval-toolkit metrics can return values slightly outside [0, 1] due to
    # floating-point arithmetic on perfect-separation cases; clamp to satisfy
    # the pydantic [0, 1] contract without altering meaningful precision.
    auprc = float(np.clip(pr_auc(y_true, y_score), 0.0, 1.0))
    auroc = float(np.clip(roc_auc(y_true, y_score), 0.0, 1.0))

    recall_0_1 = (
        compute_recall_at_fpr(y_true, y_score, fpr_target=0.001) if include_0_1_pinpoint else None
    )
    recall_1 = compute_recall_at_fpr(y_true, y_score, fpr_target=0.01) or 0.0
    recall_5 = compute_recall_at_fpr(y_true, y_score, fpr_target=0.05) or 0.0

    # ECE-equal-mass headline per ADR-023.
    calib = compute_calibration_record(
        rung=rung,
        fold=fold,
        seed=seed,
        calibrator="raw",
        y_true=y_true,
        y_score=y_score,
    )

    return MetricsRecordModel(
        rung=rung,
        fold=fold,
        seed=seed,
        slice_name=slice_name,
        n_rows=len(y_true),
        n_positive=n_positive,
        n_negative=n_negative,
        auprc=auprc,
        auroc=auroc,
        recall_at_fpr_0_1=recall_0_1,
        recall_at_fpr_1=recall_1,
        recall_at_fpr_5=recall_5,
        ece_equal_mass=calib.ece_equal_mass,
        brier=calib.brier,
    )


def compute_pooled_ood_record(
    *,
    rung: str,
    fold: int,
    seed: int,
    per_slice_dfs: dict[str, pd.DataFrame],
) -> MetricsRecordModel:
    """Concatenate the 5 OOD slice DataFrames + compute pooled metrics per ADR-021.

    The 0.1% recall@FPR pinpoint IS computed at this aggregation level
    (pooled n_neg ≈ 16-20K yields meaningful CI per ADR-021 line 51).

    Parameters
    ----------
    rung, fold, seed : metadata propagated to the output record.
    per_slice_dfs : dict mapping slice_name → DataFrame.
        Must contain at least one slice; missing slices are skipped with a warning.

    Returns
    -------
    MetricsRecordModel
        Pooled record with `slice_name="pooled_ood"` and `recall_at_fpr_0_1`
        populated.
    """
    available = [name for name in OOD_SLICE_NAMES if name in per_slice_dfs]
    if not available:
        raise ValueError(
            f"compute_pooled_ood_record requires at least one of {OOD_SLICE_NAMES}; "
            f"got {list(per_slice_dfs.keys())}"
        )
    pooled = pd.concat([per_slice_dfs[name] for name in available], ignore_index=True)
    return compute_metric_record(
        rung=rung,
        fold=fold,
        seed=seed,
        slice_name=POOLED_OOD_SLICE_NAME,
        df=pooled,
        include_0_1_pinpoint=True,
    )


def aggregate_slice_across_observations(
    *,
    rung: str,
    slice_name: str,
    metric_records: list[MetricsRecordModel],
) -> SliceMetricsModel:
    """Aggregate per-(fold, seed) metric records into one per-(rung, slice) summary.

    Used for the ADR-021 spoke `WRITEUP/ood-analysis.md`. Aggregation is
    mean across observations; CIs at this level are computed by the
    Phase 4 bootstrap battery and stitched in via per-rung-per-slice merge.
    """
    if not metric_records:
        raise ValueError(
            f"aggregate_slice_across_observations: empty input for {rung}/{slice_name}"
        )
    auprcs = np.array([r.auprc for r in metric_records], dtype=np.float64)
    aurocs = np.array([r.auroc for r in metric_records], dtype=np.float64)
    recall_1s = np.array([r.recall_at_fpr_1 for r in metric_records], dtype=np.float64)
    recall_5s = np.array([r.recall_at_fpr_5 for r in metric_records], dtype=np.float64)
    eces = np.array([r.ece_equal_mass for r in metric_records], dtype=np.float64)
    briers = np.array([r.brier for r in metric_records], dtype=np.float64)

    auprc_mean = float(auprcs.mean())
    auprc_std = float(auprcs.std(ddof=1)) if len(auprcs) > 1 else 0.0
    # Lightweight ± std bounds as placeholders; rigorous CIs come from
    # Commit 5's bootstrap battery + Phase 4 cv_clt_ci stitching.
    auprc_ci_lo = max(0.0, auprc_mean - auprc_std)
    auprc_ci_hi = min(1.0, auprc_mean + auprc_std)

    return SliceMetricsModel(
        rung=rung,
        slice_name=slice_name,
        n_observations=len(metric_records),
        auprc_mean=auprc_mean,
        auprc_ci_lo=auprc_ci_lo,
        auprc_ci_hi=auprc_ci_hi,
        auroc_mean=float(aurocs.mean()),
        recall_at_fpr_1_mean=float(recall_1s.mean()),
        recall_at_fpr_5_mean=float(recall_5s.mean()),
        ece_equal_mass_mean=float(eces.mean()),
        brier_mean=float(briers.mean()),
    )


def compute_pinpoint_volatility(
    *,
    y_true: NDArray[np.int_],
    y_score: NDArray[np.float64],
    fpr_target: float,
    n_resamples: int = 1000,
    seed: int = 1,
) -> dict[str, float | bool | None]:
    """Bootstrap recall@FPR + emit ADR-021 line 53-65 volatility surfaces.

    Surfaces emitted:
    - point_estimate : float | None
    - ci_lo, ci_hi : float | None (percentile bootstrap)
    - half_width : float | None
    - flag_wide_ci : bool (half_width > 0.5 * point_estimate per ADR-021)
    - degeneracy_fraction : float (fraction of resamples where target unreachable)
    - threshold_drift_min, threshold_drift_max : float | None (range of thresholds)

    Used at pooled aggregation level for the 0.1% pinpoint per ADR-021;
    caller dumps the threshold-drift distribution separately for the audit
    JSON `evals/audit/pinpoint_threshold_drift.json`.
    """
    if len(y_true) == 0:
        return {
            "point_estimate": None,
            "ci_lo": None,
            "ci_hi": None,
            "half_width": None,
            "flag_wide_ci": False,
            "degeneracy_fraction": 1.0,
            "threshold_drift_min": None,
            "threshold_drift_max": None,
        }

    point_estimate = compute_recall_at_fpr(y_true, y_score, fpr_target)

    rng = np.random.default_rng(seed)
    n = len(y_true)
    recalls: list[float] = []
    thresholds: list[float] = []
    n_unreachable = 0

    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        y_b = y_true[idx]
        s_b = y_score[idx]
        if y_b.sum() == 0 or y_b.sum() == len(y_b):
            n_unreachable += 1
            continue
        try:
            result = TargetFPRSelector(fpr_target).select(y_b, s_b)
            recalls.append(float(result.recall))
            thresholds.append(float(result.threshold))
        except RuntimeError:
            n_unreachable += 1

    degeneracy_fraction = float(n_unreachable / n_resamples)

    if not recalls:
        return {
            "point_estimate": point_estimate,
            "ci_lo": None,
            "ci_hi": None,
            "half_width": None,
            "flag_wide_ci": True,
            "degeneracy_fraction": degeneracy_fraction,
            "threshold_drift_min": None,
            "threshold_drift_max": None,
        }

    recalls_arr = np.array(recalls, dtype=np.float64)
    thresholds_arr = np.array(thresholds, dtype=np.float64)
    ci_lo = float(np.percentile(recalls_arr, 2.5))
    ci_hi = float(np.percentile(recalls_arr, 97.5))
    half_width = (ci_hi - ci_lo) / 2.0

    pt_val = point_estimate if point_estimate is not None else 0.0
    flag_wide_ci = (
        bool(half_width > VOLATILITY_WIDE_CI_RATIO * pt_val) if pt_val > 0 else bool(half_width > 0)
    )

    return {
        "point_estimate": point_estimate,
        "ci_lo": ci_lo,
        "ci_hi": ci_hi,
        "half_width": half_width,
        "flag_wide_ci": flag_wide_ci,
        "degeneracy_fraction": degeneracy_fraction,
        "threshold_drift_min": float(thresholds_arr.min()),
        "threshold_drift_max": float(thresholds_arr.max()),
    }


def use_metrics_at_threshold_for_diagnostic(
    y_true: NDArray[np.int_],
    y_score: NDArray[np.float64],
    threshold: float,
) -> dict[str, float | int]:
    """Thin wrapper around eval-toolkit metrics_at_threshold for diagnostic dumps."""
    result: dict[str, float | int] = metrics_at_threshold(y_true, y_score, threshold=threshold)
    return result


# Re-export the headline binning constant for callers + downstream tests.
__all__ = [
    "HEADLINE_N_BINS",
    "IID_SLICE_NAME",
    "OOD_SLICE_NAMES",
    "POOLED_OOD_SLICE_NAME",
    "RECALL_AT_FPR_PINPOINTS",
    "SINGLE_CLASS_SLICES",
    "VOLATILITY_WIDE_CI_RATIO",
    "aggregate_slice_across_observations",
    "compute_metric_record",
    "compute_pinpoint_volatility",
    "compute_pooled_ood_record",
    "compute_recall_at_fpr",
    "is_metric_defined_for_slice",
    "use_metrics_at_threshold_for_diagnostic",
]
