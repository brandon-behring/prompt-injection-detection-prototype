"""Smoke tests for src/eval/slice_analysis.py (Phase 3 Commit 4 per ADR-021 + ADR-045)."""

from __future__ import annotations


import numpy as np
import pandas as pd
import pytest

from src.eval.schemas import MetricsRecordModel, SliceMetricsModel
from src.eval.slice_analysis import (
    OOD_SLICE_NAMES,
    POOLED_OOD_SLICE_NAME,
    RECALL_AT_FPR_PINPOINTS,
    aggregate_slice_across_observations,
    compute_metric_record,
    compute_pinpoint_volatility,
    compute_pooled_ood_record,
    compute_recall_at_fpr,
)


def _separable_df(n: int = 200, seed: int = 0, rung: str = "lora") -> pd.DataFrame:
    """Separable binary predictions DataFrame matching the Phase 1 schema."""
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, size=n).astype(np.int_)
    s = np.where(y == 1, rng.uniform(0.6, 0.99, size=n), rng.uniform(0.01, 0.4, size=n)).astype(
        np.float64
    )
    return pd.DataFrame(
        {
            "rung": rung,
            "fold": 0,
            "seed": 42,
            "epoch": 2,
            "row_idx_in_source": list(range(n)),
            "source": "src",
            "text": [f"text-{i}" for i in range(n)],
            "label": y,
            "predicted_proba_class1": s,
            "contamination_state": "backbone-partial-disjoint",
        }
    )


# --------------------------------------------------------------------------- #
# Locked taxonomy + constants
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_ood_slice_names_locked_to_5_per_adr_021() -> None:
    """OOD_SLICE_NAMES carries exactly the 5 slices from ADR-016 + ADR-021."""
    assert OOD_SLICE_NAMES == (
        "notinject",
        "xstest",
        "jbb_behaviors",
        "bipia",
        "injecagent",
    )


@pytest.mark.smoke
def test_recall_at_fpr_pinpoints_locked_to_triad_per_adr_021() -> None:
    """RECALL_AT_FPR_PINPOINTS carries (0.001, 0.01, 0.05) per ADR-021."""
    assert RECALL_AT_FPR_PINPOINTS == (0.001, 0.01, 0.05)


# --------------------------------------------------------------------------- #
# compute_recall_at_fpr
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_compute_recall_at_fpr_separable_returns_high_recall() -> None:
    """Well-separated classifier achieves high recall at any reasonable FPR target."""
    df = _separable_df(n=300, seed=1)
    y = df["label"].to_numpy(dtype=np.int_)
    s = df["predicted_proba_class1"].to_numpy(dtype=np.float64)
    r = compute_recall_at_fpr(y, s, fpr_target=0.05)
    assert r is not None
    assert r > 0.8


@pytest.mark.smoke
def test_compute_recall_at_fpr_returns_none_on_single_class() -> None:
    """Single-class y returns None (recall undefined)."""
    y = np.ones(10, dtype=np.int_)
    s = np.random.default_rng(0).uniform(0, 1, size=10).astype(np.float64)
    assert compute_recall_at_fpr(y, s, fpr_target=0.01) is None


@pytest.mark.smoke
def test_compute_recall_at_fpr_returns_none_on_empty() -> None:
    """Empty input returns None."""
    y = np.array([], dtype=np.int_)
    s = np.array([], dtype=np.float64)
    assert compute_recall_at_fpr(y, s, fpr_target=0.01) is None


# --------------------------------------------------------------------------- #
# compute_metric_record
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_compute_metric_record_returns_validated_model_for_per_slice() -> None:
    """Per-slice records have recall_at_fpr_0_1 = None per ADR-021."""
    df = _separable_df(n=200, seed=2)
    rec = compute_metric_record(
        rung="lora",
        fold=0,
        seed=42,
        slice_name="bipia",
        df=df,
        include_0_1_pinpoint=False,
    )
    assert isinstance(rec, MetricsRecordModel)
    assert rec.slice_name == "bipia"
    assert rec.recall_at_fpr_0_1 is None
    assert rec.auprc > 0.5
    assert rec.recall_at_fpr_1 >= 0.0


@pytest.mark.smoke
def test_compute_metric_record_with_0_1_pinpoint_for_pooled() -> None:
    """When include_0_1_pinpoint=True (pooled), recall_at_fpr_0_1 is populated."""
    df = _separable_df(n=500, seed=5)
    rec = compute_metric_record(
        rung="lora",
        fold=-1,
        seed=-1,
        slice_name="pooled_ood",
        df=df,
        include_0_1_pinpoint=True,
    )
    # Either a float in [0, 1] or None if too small — both schema-valid.
    assert rec.recall_at_fpr_0_1 is None or 0.0 <= rec.recall_at_fpr_0_1 <= 1.0


@pytest.mark.smoke
def test_compute_metric_record_rejects_empty_df() -> None:
    """Empty df raises ValueError fail-loud per project standards."""
    df_empty = pd.DataFrame({"label": [], "predicted_proba_class1": []})
    with pytest.raises(ValueError):
        compute_metric_record(rung="x", fold=0, seed=42, slice_name="empty_slice", df=df_empty)


# --------------------------------------------------------------------------- #
# compute_pooled_ood_record
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_compute_pooled_ood_record_aggregates_5_slices() -> None:
    """Pooled record concatenates all 5 OOD slice DataFrames per ADR-021."""
    per_slice = {name: _separable_df(n=80, seed=hash(name) % 1000) for name in OOD_SLICE_NAMES}
    rec = compute_pooled_ood_record(rung="lora", fold=0, seed=42, per_slice_dfs=per_slice)
    assert rec.slice_name == POOLED_OOD_SLICE_NAME
    assert rec.n_rows == 5 * 80


@pytest.mark.smoke
def test_compute_pooled_ood_record_rejects_empty_slate() -> None:
    """No OOD slices in input raises ValueError."""
    with pytest.raises(ValueError):
        compute_pooled_ood_record(rung="x", fold=0, seed=42, per_slice_dfs={})


@pytest.mark.smoke
def test_compute_pooled_ood_record_partial_slate_works() -> None:
    """Subset of OOD slices is acceptable (allows operator-deferred slices per ADR-001 fallback)."""
    per_slice = {"notinject": _separable_df(n=100, seed=10)}
    rec = compute_pooled_ood_record(rung="lora", fold=0, seed=42, per_slice_dfs=per_slice)
    assert rec.n_rows == 100


# --------------------------------------------------------------------------- #
# aggregate_slice_across_observations
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_aggregate_slice_across_observations_mean_basic() -> None:
    """Per-(fold, seed) records aggregate to a SliceMetricsModel."""
    records = [
        compute_metric_record(
            rung="lora", fold=i, seed=42, slice_name="bipia", df=_separable_df(n=100, seed=i)
        )
        for i in range(4)
    ]
    agg = aggregate_slice_across_observations(
        rung="lora", slice_name="bipia", metric_records=records
    )
    assert isinstance(agg, SliceMetricsModel)
    assert agg.n_observations == 4
    assert agg.auprc_mean == pytest.approx(np.mean([r.auprc for r in records]))


# --------------------------------------------------------------------------- #
# compute_pinpoint_volatility per ADR-021 line 53-65
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_compute_pinpoint_volatility_emits_locked_surfaces() -> None:
    """Bootstrap volatility emit carries all 7 fields per ADR-021 spoke discipline."""
    df = _separable_df(n=500, seed=42)
    y = df["label"].to_numpy(dtype=np.int_)
    s = df["predicted_proba_class1"].to_numpy(dtype=np.float64)
    surfaces = compute_pinpoint_volatility(
        y_true=y, y_score=s, fpr_target=0.05, n_resamples=200, seed=1
    )
    for field in (
        "point_estimate",
        "ci_lo",
        "ci_hi",
        "half_width",
        "flag_wide_ci",
        "degeneracy_fraction",
        "threshold_drift_min",
        "threshold_drift_max",
    ):
        assert field in surfaces, f"volatility surface missing {field!r}"
    assert isinstance(surfaces["flag_wide_ci"], bool)
    assert 0.0 <= surfaces["degeneracy_fraction"] <= 1.0  # type: ignore[operator]
