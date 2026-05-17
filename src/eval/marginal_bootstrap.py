"""Phase 4 marginal-bootstrap primitives per ADR-022 + ADR-046 Q1 (Commit 2).

Per-rung marginal CIs (no pairing) for the headline + spoke metrics. Each cell wraps
`eval_toolkit.bootstrap.bootstrap_ci` (BCa default per ADR-022); the headline protocol
fires seed=1 + seed=2 stability check and persists both cells so the half-width
comparison is queryable from disk per ADR-013 persist-everything-report-selectively
pattern.

Inputs are the same `PredictionsRowModel`-shaped DataFrames consumed by the Phase 3
metrics + bootstrap batteries. Outputs are `MarginalBootstrapCellModel` records.

Library-first
-------------
- `eval_toolkit.bootstrap.bootstrap_ci` does the BCa CI (single-rung marginal).
- `eval_toolkit.metrics.{pr_auc, roc_auc}` are the metric callbacks.

Project glue is row-level slice filtering + (rung, slice, metric) iteration + the
`MarginalBootstrapCellModel` schema validator. No re-implementation of CI math.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

import numpy as np
import pandas as pd
from eval_toolkit.bootstrap import bootstrap_ci
from eval_toolkit.metrics import pr_auc, roc_auc
from numpy.typing import NDArray

from src.eval.schemas import MarginalBootstrapCellModel

# Metric registry mirrors scripts/run_bootstrap_battery.py to keep the metric
# names + callable wiring in one place across Phase 3 + Phase 4.
MARGINAL_METRIC_REGISTRY: Final[
    dict[str, Callable[[NDArray[np.int_], NDArray[np.float64]], float]]
] = {
    "auprc": pr_auc,
    "auroc": roc_auc,
}

# ADR-022 protocol — 10K iterations for the headline CI + 10K @ a second seed for
# the stability-check sister cell.
HEADLINE_N_RESAMPLES: Final[int] = 10_000
HEADLINE_SEED: Final[int] = 1
STABILITY_CHECK_SEED: Final[int] = 2


def _filter_rung_slice(
    df: pd.DataFrame, rung: str, slice_name: str
) -> tuple[NDArray[np.int_], NDArray[np.float64]]:
    """Extract (y, s) for a single (rung, slice_name) cell."""
    mask = (df["rung"] == rung) & (df["slice_name"] == slice_name)
    sub = df.loc[mask, ["label", "predicted_proba_class1"]]
    if sub.empty:
        raise ValueError(
            f"No predictions for rung={rung!r} slice={slice_name!r} — check pipeline upstream."
        )
    y = sub["label"].to_numpy(dtype=np.int_)
    s = sub["predicted_proba_class1"].to_numpy(dtype=np.float64)
    return y, s


def compute_marginal_bootstrap_cell(
    df: pd.DataFrame,
    *,
    rung: str,
    slice_name: str,
    metric_name: str,
    n_resamples: int = HEADLINE_N_RESAMPLES,
    seed: int = HEADLINE_SEED,
) -> MarginalBootstrapCellModel:
    """Compute one marginal-bootstrap CI cell for (rung, slice, metric).

    Parameters
    ----------
    df : pd.DataFrame
        Predictions table with at least columns ``rung``, ``slice_name``,
        ``label``, ``predicted_proba_class1`` per ADR-045 Q3 schema contract.
    rung : str
        Rung name (e.g. ``"frozen_probe"``).
    slice_name : str
        Slice name (e.g. ``"pooled_ood"``, ``"iid"``, one of OOD_SLICE_NAMES).
    metric_name : str
        Key into ``MARGINAL_METRIC_REGISTRY``.
    n_resamples, seed : int
        Bootstrap budget + seed (see ADR-022 multi-seed protocol).

    Returns
    -------
    MarginalBootstrapCellModel

    Raises
    ------
    ValueError
        If metric_name unknown or the rung/slice filter yields zero rows.
    """
    if metric_name not in MARGINAL_METRIC_REGISTRY:
        raise ValueError(
            f"Unknown metric_name={metric_name!r}; supported: "
            f"{sorted(MARGINAL_METRIC_REGISTRY.keys())}"
        )
    metric_fn = MARGINAL_METRIC_REGISTRY[metric_name]
    y, s = _filter_rung_slice(df, rung=rung, slice_name=slice_name)
    point_estimate = float(metric_fn(y, s))
    ci = bootstrap_ci(
        y, s, metric=metric_fn, n_resamples=n_resamples, confidence=0.95, method="BCa", seed=seed
    )
    return MarginalBootstrapCellModel(
        rung=rung,
        slice_name=slice_name,
        metric=metric_name,
        n_resamples=n_resamples,
        seed=seed,
        point_estimate=point_estimate,
        ci_lo=float(ci.ci_low),
        ci_hi=float(ci.ci_high),
        ci_method="bca",
        n_obs=int(y.shape[0]),
    )


def compute_marginal_battery(
    df: pd.DataFrame,
    *,
    rungs: list[str],
    slice_names: list[str],
    metric_names: list[str],
    n_resamples: int = HEADLINE_N_RESAMPLES,
    seeds: tuple[int, ...] = (HEADLINE_SEED, STABILITY_CHECK_SEED),
) -> list[MarginalBootstrapCellModel]:
    """Sweep marginal CIs across (rung x slice x metric x seed).

    Skips cells where the rung/slice filter is empty (e.g., reference scorer on a
    transformer-only slice) rather than raising — return value lists only the cells
    that produced output. Caller persists the resulting list to parquet.
    """
    cells: list[MarginalBootstrapCellModel] = []
    for rung in rungs:
        for slice_name in slice_names:
            for metric_name in metric_names:
                for seed in seeds:
                    try:
                        cell = compute_marginal_bootstrap_cell(
                            df,
                            rung=rung,
                            slice_name=slice_name,
                            metric_name=metric_name,
                            n_resamples=n_resamples,
                            seed=seed,
                        )
                    except ValueError:
                        # Empty filter — skip cell (caller can grep for missing rows).
                        continue
                    cells.append(cell)
    return cells
