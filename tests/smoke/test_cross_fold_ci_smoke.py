"""Smoke tests for src/eval/cross_fold_ci.py (Phase 4 Commit 2 per ADR-046 Q3 headline)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import pytest

from src.eval.cross_fold_ci import (
    CROSS_FOLD_METRIC_REGISTRY,
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
    """Headline cell roundtrips through CrossFoldCIModel without error."""
    df = _synth_multi_fold_predictions(k_folds=4)
    cell = compute_cross_fold_ci_cell(
        df, rung="frozen_probe", slice_name="iid", metric_name="auroc"
    )
    assert isinstance(cell, CrossFoldCIModel)
    assert cell.k_folds == 4
    assert cell.n_seeds_per_fold == 3
    assert 0.0 <= cell.cv_clt_ci_lo <= cell.cv_clt_ci_hi <= 1.0
    assert cell.cv_clt_ci_halfwidth > 0.0


@pytest.mark.smoke
def test_cross_fold_ci_cell_block_fields_none_at_commit_2() -> None:
    """Commit 2 leaves all block-bootstrap spoke fields as None; Commit 3 fills them."""
    df = _synth_multi_fold_predictions(k_folds=3)
    cell = compute_cross_fold_ci_cell(
        df, rung="frozen_probe", slice_name="iid", metric_name="auprc"
    )
    assert cell.block_bootstrap_ci_lo is None
    assert cell.block_bootstrap_ci_hi is None
    assert cell.block_bootstrap_ci_halfwidth is None
    assert cell.block_bootstrap_n_resamples is None
    assert cell.a_008_flag_fired is None


@pytest.mark.smoke
def test_cross_fold_metric_registry_covers_phase4_headlines() -> None:
    assert "auprc" in CROSS_FOLD_METRIC_REGISTRY
    assert "auroc" in CROSS_FOLD_METRIC_REGISTRY
