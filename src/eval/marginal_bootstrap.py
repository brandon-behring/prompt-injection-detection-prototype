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
- `eval_toolkit._parallel.parallel_map` parallelises the per-cell sweep
  (each cell is independent; n_jobs=-1 uses all cores).

Project glue is row-level slice filtering + (rung, slice, metric) iteration + the
`MarginalBootstrapCellModel` schema validator. No re-implementation of CI math.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

import numpy as np
import pandas as pd
from eval_toolkit._parallel import parallel_map
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


def _compute_one_cell_or_none(
    spec: tuple[pd.DataFrame, str, str, str, int, int],
) -> MarginalBootstrapCellModel | None:
    """Worker for parallel_map; returns None for empty-filter cells.

    Top-level def + tuple-spec signature is required: joblib's loky backend
    can only pickle named functions, not closures.
    """
    df, rung, slice_name, metric_name, n_resamples, seed = spec
    try:
        return compute_marginal_bootstrap_cell(
            df,
            rung=rung,
            slice_name=slice_name,
            metric_name=metric_name,
            n_resamples=n_resamples,
            seed=seed,
        )
    except ValueError:
        return None


def compute_marginal_battery(
    df: pd.DataFrame,
    *,
    rungs: list[str],
    slice_names: list[str],
    metric_names: list[str],
    n_resamples: int = HEADLINE_N_RESAMPLES,
    seeds: tuple[int, ...] = (HEADLINE_SEED, STABILITY_CHECK_SEED),
    n_jobs: int = 1,
) -> list[MarginalBootstrapCellModel]:
    """Sweep marginal CIs across (rung x slice x metric x seed).

    Optional parallelism via ``eval_toolkit._parallel.parallel_map`` —
    each cell is independent. **Default is ``n_jobs=1`` (sequential)** —
    parallel mode (``n_jobs > 1`` or ``-1`` for all cores) is opt-in
    because each loky worker copies the DataFrame and the BCa
    intermediate state (~hundreds of MB per cell), so unbounded
    parallelism can OOM on a many-core machine. Recommended ceiling:
    ``min(8, available_RAM_GB / 4)`` — at 10K resamples each worker
    uses ~3-4 GB peak for the typical OOD-pool cell size.

    Skips cells where the rung/slice filter is empty (e.g., reference scorer
    on a transformer-only slice) rather than raising. Also applies the Q9
    source-level filter to drop AUROC/AUPRC × single-class-slice cells.
    Return value lists only the cells that produced output.
    """
    # Local import — avoid a circular import via slice_analysis ←→ marginal_bootstrap.
    from src.eval.slice_analysis import is_metric_defined_for_slice

    # Materialise the cell spec list (filtered + (rung x slice x metric x seed)).
    specs: list[tuple[pd.DataFrame, str, str, str, int, int]] = []
    for rung in rungs:
        for slice_name in slice_names:
            for metric_name in metric_names:
                # Source-level filter (Q9 lock): AUROC/AUPRC undefined on
                # single-class slices (bipia/injecagent/notinject); skip
                # rather than emit degenerate 1.0/0.0 values.
                if not is_metric_defined_for_slice(slice_name, metric_name):
                    continue
                for seed in seeds:
                    specs.append((df, rung, slice_name, metric_name, n_resamples, seed))

    results = parallel_map(
        _compute_one_cell_or_none,
        specs,
        n_jobs=n_jobs,
        description="marginal_bootstrap_cells",
    )
    return [cell for cell in results if cell is not None]
