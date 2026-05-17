"""Smoke tests for src/eval/cross_fold_ci.py (Phase 4 Commit 2 per ADR-046 Q3 headline)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import pytest

from src.eval.cross_fold_ci import (
    A_008_RATIO_THRESHOLD,
    BLOCK_BOOTSTRAP_N_RESAMPLES,
    CROSS_FOLD_METRIC_REGISTRY,
    compute_a_008_flag,
    compute_block_bootstrap_on_folds,
    compute_cross_fold_ci_cell,
    compute_per_fold_metric_vector,
)
from src.eval.schemas import CrossFoldCIModel


def _synth_multi_fold_predictions(
    k_folds: int = 4,
    seeds: tuple[int, ...] = (42, 43, 44),
    n_per_cell: int = 80,
    rung: str = "frozen_probe",
    slice_name: str = "iid",
    base_seed: int = 0,
) -> pd.DataFrame:
    """Synthesize predictions with K folds x S seeds per fold for cv_clt_ci input."""
    rng = np.random.default_rng(base_seed)
    rows: list[dict[str, Any]] = []
    for fold in range(k_folds):
        for seed in seeds:
            y = rng.integers(0, 2, size=n_per_cell)
            s = np.clip(y + rng.normal(0, 0.3, size=n_per_cell), 0.001, 0.999)
            for i in range(n_per_cell):
                rows.append(
                    {
                        "rung": rung,
                        "fold": fold,
                        "seed": seed,
                        "slice_name": slice_name,
                        "row_idx_in_source": i,
                        "source": f"synth_fold{fold}",
                        "label": int(y[i]),
                        "predicted_proba_class1": float(s[i]),
                    }
                )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# compute_per_fold_metric_vector
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_per_fold_metric_vector_length_matches_n_folds() -> None:
    """Vector length equals number of folds when each fold has data."""
    df = _synth_multi_fold_predictions(k_folds=4)
    v = compute_per_fold_metric_vector(
        df, rung="frozen_probe", slice_name="iid", metric_name="auprc"
    )
    assert v.shape == (4,)
    assert np.all(np.isfinite(v))
    assert np.all((v >= 0.0) & (v <= 1.0))


@pytest.mark.smoke
def test_per_fold_metric_vector_unknown_metric_raises() -> None:
    df = _synth_multi_fold_predictions(k_folds=3)
    with pytest.raises(ValueError, match="Unknown metric_name"):
        compute_per_fold_metric_vector(
            df, rung="frozen_probe", slice_name="iid", metric_name="bogus"
        )


@pytest.mark.smoke
def test_per_fold_metric_vector_single_fold_raises() -> None:
    """cv_clt_ci needs >= 2 folds; a single-fold filter must raise."""
    df = _synth_multi_fold_predictions(k_folds=1)
    with pytest.raises(ValueError, match=">= 2 folds"):
        compute_per_fold_metric_vector(
            df, rung="frozen_probe", slice_name="iid", metric_name="auprc"
        )


# --------------------------------------------------------------------------- #
# compute_cross_fold_ci_cell — Commit 2 headline cv_clt
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_cross_fold_ci_cell_schema_valid() -> None:
    """Cell roundtrips through CrossFoldCIModel with both headline and spoke filled."""
    df = _synth_multi_fold_predictions(k_folds=4)
    cell = compute_cross_fold_ci_cell(
        df,
        rung="frozen_probe",
        slice_name="iid",
        metric_name="auroc",
        block_bootstrap_n_resamples=500,
    )
    assert isinstance(cell, CrossFoldCIModel)
    assert cell.k_folds == 4
    assert cell.n_seeds_per_fold == 3
    assert 0.0 <= cell.cv_clt_ci_lo <= cell.cv_clt_ci_hi <= 1.0
    assert cell.cv_clt_ci_halfwidth > 0.0


@pytest.mark.smoke
def test_cross_fold_ci_cell_block_fields_populated_at_commit_3() -> None:
    """Commit 3 always emits the block-bootstrap spoke + a_008_flag_fired."""
    df = _synth_multi_fold_predictions(k_folds=4)
    cell = compute_cross_fold_ci_cell(
        df,
        rung="frozen_probe",
        slice_name="iid",
        metric_name="auprc",
        block_bootstrap_n_resamples=500,
    )
    assert cell.block_bootstrap_ci_lo is not None
    assert cell.block_bootstrap_ci_hi is not None
    assert cell.block_bootstrap_ci_halfwidth is not None
    assert cell.block_bootstrap_ci_halfwidth >= 0.0
    assert cell.block_bootstrap_n_resamples == 500
    assert cell.a_008_flag_fired is not None
    assert isinstance(cell.a_008_flag_fired, bool)


@pytest.mark.smoke
def test_cross_fold_metric_registry_covers_phase4_headlines() -> None:
    assert "auprc" in CROSS_FOLD_METRIC_REGISTRY
    assert "auroc" in CROSS_FOLD_METRIC_REGISTRY


# --------------------------------------------------------------------------- #
# compute_block_bootstrap_on_folds — Commit 3 spoke (inline impl per upstream #21)
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_block_bootstrap_returns_ordered_interval() -> None:
    """ci_lo <= ci_hi for any K-fold input."""
    per_fold = np.array([0.80, 0.85, 0.78, 0.82], dtype=np.float64)
    ci_lo, ci_hi = compute_block_bootstrap_on_folds(per_fold, n_resamples=500, seed=42)
    assert ci_lo <= ci_hi


@pytest.mark.smoke
def test_block_bootstrap_interval_contains_mean_for_modest_resamples() -> None:
    """Empirical CI from K=4 folds contains the fold mean."""
    per_fold = np.array([0.80, 0.85, 0.78, 0.82], dtype=np.float64)
    mean = per_fold.mean()
    ci_lo, ci_hi = compute_block_bootstrap_on_folds(per_fold, n_resamples=2000, seed=42)
    assert ci_lo <= mean <= ci_hi


@pytest.mark.smoke
def test_block_bootstrap_seed_determinism() -> None:
    """Same seed -> identical interval."""
    per_fold = np.array([0.80, 0.85, 0.78, 0.82], dtype=np.float64)
    a = compute_block_bootstrap_on_folds(per_fold, n_resamples=500, seed=7)
    b = compute_block_bootstrap_on_folds(per_fold, n_resamples=500, seed=7)
    assert a == b


@pytest.mark.smoke
def test_block_bootstrap_rejects_single_fold() -> None:
    # Upstream eval-toolkit v0.34.0 message uses unicode ≥; match loosely.
    with pytest.raises(ValueError, match=r"K\s*[≥>=]+\s*2"):
        compute_block_bootstrap_on_folds(np.array([0.5], dtype=np.float64), n_resamples=10)


@pytest.mark.smoke
def test_block_bootstrap_rejects_invalid_confidence() -> None:
    per_fold = np.array([0.80, 0.85], dtype=np.float64)
    with pytest.raises(ValueError, match="confidence"):
        compute_block_bootstrap_on_folds(per_fold, n_resamples=10, confidence=1.5)


@pytest.mark.smoke
def test_block_bootstrap_default_n_resamples_matches_adr_022() -> None:
    """Default n_resamples mirrors the ADR-022 marginal/paired budget."""
    assert BLOCK_BOOTSTRAP_N_RESAMPLES == 10_000


# --------------------------------------------------------------------------- #
# compute_a_008_flag — A-008 sensitivity check
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_a_008_flag_fires_when_ratio_exceeds_threshold() -> None:
    """ratio > 1.5 -> True."""
    assert compute_a_008_flag(cv_clt_halfwidth=0.02, block_bootstrap_halfwidth=0.04) is True


@pytest.mark.smoke
def test_a_008_flag_does_not_fire_when_ratio_below_threshold() -> None:
    """ratio == 1.5 (the threshold) -> False (strict inequality)."""
    assert compute_a_008_flag(cv_clt_halfwidth=0.02, block_bootstrap_halfwidth=0.03) is False


@pytest.mark.smoke
def test_a_008_flag_threshold_constant() -> None:
    """A-008 threshold matches ADR-024 + A-008 specification at 1.5."""
    assert A_008_RATIO_THRESHOLD == 1.5


@pytest.mark.smoke
def test_a_008_flag_handles_degenerate_cv_clt() -> None:
    """Zero cv_clt halfwidth (all folds identical) yields True iff block halfwidth > 0."""
    assert compute_a_008_flag(cv_clt_halfwidth=0.0, block_bootstrap_halfwidth=0.01) is True
    assert compute_a_008_flag(cv_clt_halfwidth=0.0, block_bootstrap_halfwidth=0.0) is False
