"""Smoke tests for src/eval/marginal_bootstrap.py (Phase 4 Commit 2 per ADR-046 Q1)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import pytest

from src.eval.marginal_bootstrap import (
    HEADLINE_SEED,
    MARGINAL_METRIC_REGISTRY,
    STABILITY_CHECK_SEED,
    compute_marginal_battery,
    compute_marginal_bootstrap_cell,
)
from src.eval.schemas import MarginalBootstrapCellModel


def _synth_predictions(
    n_per_rung: int = 200, rungs: tuple[str, ...] = ("rungA", "rungB"), seed: int = 0
) -> pd.DataFrame:
    """Generate a tiny PredictionsRowModel-shaped DataFrame with a slice_name column."""
    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    for rung in rungs:
        y = rng.integers(0, 2, size=n_per_rung)
        s = np.clip(y + rng.normal(0, 0.3, size=n_per_rung), 0.001, 0.999)
        for i in range(n_per_rung):
            rows.append(
                {
                    "rung": rung,
                    "fold": 0,
                    "seed": 42,
                    "slice_name": "iid",
                    "row_idx_in_source": i,
                    "source": "synth",
                    "label": int(y[i]),
                    "predicted_proba_class1": float(s[i]),
                }
            )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# compute_marginal_bootstrap_cell
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_marginal_bootstrap_cell_schema_valid() -> None:
    """One cell roundtrips through MarginalBootstrapCellModel without error."""
    df = _synth_predictions()
    cell = compute_marginal_bootstrap_cell(
        df,
        rung="rungA",
        slice_name="iid",
        metric_name="auprc",
        n_resamples=200,
        seed=HEADLINE_SEED,
    )
    assert isinstance(cell, MarginalBootstrapCellModel)
    assert 0.0 <= cell.ci_lo <= cell.ci_hi <= 1.0
    assert cell.ci_method == "bca"
    assert cell.n_obs == 200


@pytest.mark.smoke
def test_marginal_bootstrap_cell_unknown_metric_raises() -> None:
    """Unknown metric_name raises ValueError with the supported list."""
    df = _synth_predictions(n_per_rung=20)
    with pytest.raises(ValueError, match="Unknown metric_name"):
        compute_marginal_bootstrap_cell(
            df, rung="rungA", slice_name="iid", metric_name="bogus", n_resamples=50
        )


@pytest.mark.smoke
def test_marginal_bootstrap_cell_empty_filter_raises() -> None:
    """Empty (rung, slice) filter raises ValueError per fail-loud discipline."""
    df = _synth_predictions(n_per_rung=20)
    with pytest.raises(ValueError, match="No predictions"):
        compute_marginal_bootstrap_cell(
            df,
            rung="missing_rung",
            slice_name="iid",
            metric_name="auprc",
            n_resamples=50,
        )


@pytest.mark.smoke
def test_marginal_metric_registry_covers_phase4_headlines() -> None:
    """Registry must include the two rank-based headline metrics per ADR-022."""
    assert "auprc" in MARGINAL_METRIC_REGISTRY
    assert "auroc" in MARGINAL_METRIC_REGISTRY


# --------------------------------------------------------------------------- #
# compute_marginal_battery — full sweep
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_marginal_battery_emits_two_seeds_per_cell() -> None:
    """Battery sweep emits seed=1 + seed=2 stability check per ADR-022 protocol."""
    df = _synth_predictions(n_per_rung=200)
    cells = compute_marginal_battery(
        df,
        rungs=["rungA"],
        slice_names=["iid"],
        metric_names=["auprc"],
        n_resamples=100,
        seeds=(HEADLINE_SEED, STABILITY_CHECK_SEED),
    )
    assert len(cells) == 2
    seeds_emitted = sorted(cell.seed for cell in cells)
    assert seeds_emitted == [HEADLINE_SEED, STABILITY_CHECK_SEED]


@pytest.mark.smoke
def test_marginal_battery_skips_empty_cells() -> None:
    """Battery silently skips (rung, slice) cells with zero matching rows."""
    df = _synth_predictions(n_per_rung=200, rungs=("rungA",))
    cells = compute_marginal_battery(
        df,
        rungs=["rungA", "rungB_missing"],
        slice_names=["iid"],
        metric_names=["auprc"],
        n_resamples=100,
        seeds=(HEADLINE_SEED,),
    )
    # Only rungA cells emitted; rungB_missing has no rows.
    assert all(cell.rung == "rungA" for cell in cells)
    assert len(cells) == 1
