"""Phase 4 cross-fold CI primitives per ADR-024 + ADR-046 Q3 (Commit 2 headline).

Commit 2 ships the **headline cv_clt CI** via `eval_toolkit.bootstrap.cv_clt_ci`
(Bayle 2020 Annals of Statistics Theorem 3.1). Commit 3 will extend this module
with the always-emit block-bootstrap-on-folds spoke + the `a_008_flag_fired`
boolean per the A-008 sensitivity check (LODO non-exchangeability dominates
within-fold variance when `block_bootstrap_halfwidth / cv_clt_halfwidth > 1.5`).

The headline takes per-(fold, seed) metric values (K folds x S seeds-per-fold)
and reduces them to per-fold means before feeding `cv_clt_ci`. Per ADR-022 the
seed-within-fold replications average together to yield a single point per fold,
which is the regime Bayle 2020's CV-CLT assumes (K independent fold estimates).

Library-first
-------------
- `eval_toolkit.bootstrap.cv_clt_ci` does the Bayle 2020 CI math.
- `eval_toolkit.metrics.{pr_auc, roc_auc}` are the per-fold metric callbacks.

Project glue is per-(fold, seed) grouping + within-fold mean aggregation + the
`CrossFoldCIModel` schema validator. No re-implementation of CI math.

Upstream gap
------------
Block-bootstrap-on-folds (CV-aware block bootstrap) is filed at eval-toolkit
issue #21. Until that lands, Commit 3 supplies an inline NumPy implementation
that draws K blocks-with-replacement from the per-fold metric vector and feeds
the resulting empirical distribution into a percentile CI per ADR-022.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

import numpy as np
import pandas as pd
from eval_toolkit.bootstrap import cv_clt_ci
from eval_toolkit.metrics import pr_auc, roc_auc
from numpy.typing import NDArray

from src.eval.schemas import CrossFoldCIModel

CROSS_FOLD_METRIC_REGISTRY: Final[
    dict[str, Callable[[NDArray[np.int_], NDArray[np.float64]], float]]
] = {
    "auprc": pr_auc,
    "auroc": roc_auc,
}


def compute_per_fold_metric_vector(
    df: pd.DataFrame,
    *,
    rung: str,
    slice_name: str,
    metric_name: str,
) -> NDArray[np.float64]:
    """Reduce per-(fold, seed) rows to one mean metric value per fold.

    Returns a 1-D array of length K (number of folds present). Empty fold groups
    are skipped (the returned array's length reflects only folds with data).

    Per ADR-022, the multi-seed protocol averages within-fold seed replications
    before feeding the per-fold value into the cross-fold CI machinery.
    """
    if metric_name not in CROSS_FOLD_METRIC_REGISTRY:
        raise ValueError(
            f"Unknown metric_name={metric_name!r}; supported: "
            f"{sorted(CROSS_FOLD_METRIC_REGISTRY.keys())}"
        )
    metric_fn = CROSS_FOLD_METRIC_REGISTRY[metric_name]
    mask = (df["rung"] == rung) & (df["slice_name"] == slice_name)
    sub = df.loc[mask, ["fold", "seed", "label", "predicted_proba_class1"]]
    if sub.empty:
        raise ValueError(
            f"No predictions for rung={rung!r} slice={slice_name!r} — check pipeline upstream."
        )

    fold_means: list[float] = []
    for fold_id, fold_group in sub.groupby("fold"):
        seed_scores: list[float] = []
        for _, seed_group in fold_group.groupby("seed"):
            y = seed_group["label"].to_numpy(dtype=np.int_)
            s = seed_group["predicted_proba_class1"].to_numpy(dtype=np.float64)
            if y.shape[0] < 2:
                continue
            seed_scores.append(float(metric_fn(y, s)))
        if seed_scores:
            fold_means.append(float(np.mean(seed_scores)))
    if len(fold_means) < 2:
        raise ValueError(
            f"Need >= 2 folds with data for cv_clt_ci; got {len(fold_means)} "
            f"for rung={rung!r} slice={slice_name!r} metric={metric_name!r}."
        )
    return np.asarray(fold_means, dtype=np.float64)


def compute_cross_fold_ci_cell(
    df: pd.DataFrame,
    *,
    rung: str,
    slice_name: str,
    metric_name: str,
) -> CrossFoldCIModel:
    """Compute the headline cv_clt cross-fold CI cell for (rung, slice, metric).

    Commit 2 fills the cv_clt fields and leaves block-bootstrap fields as None;
    Commit 3 extends this function to also populate the block-bootstrap spoke
    + `a_008_flag_fired` per the A-008 sensitivity check.
    """
    per_fold = compute_per_fold_metric_vector(
        df, rung=rung, slice_name=slice_name, metric_name=metric_name
    )
    n_seeds_per_fold = _infer_seeds_per_fold(df=df, rung=rung, slice_name=slice_name)
    ci = cv_clt_ci(per_fold, confidence=0.95)
    halfwidth = (float(ci.ci_high) - float(ci.ci_low)) / 2.0
    return CrossFoldCIModel(
        rung=rung,
        slice_name=slice_name,
        metric=metric_name,
        k_folds=int(per_fold.shape[0]),
        n_seeds_per_fold=n_seeds_per_fold,
        cv_clt_point_estimate=float(ci.point_estimate),
        cv_clt_ci_lo=float(ci.ci_low),
        cv_clt_ci_hi=float(ci.ci_high),
        cv_clt_ci_halfwidth=halfwidth,
        # Commit 3 will populate these:
        block_bootstrap_ci_lo=None,
        block_bootstrap_ci_hi=None,
        block_bootstrap_ci_halfwidth=None,
        block_bootstrap_n_resamples=None,
        a_008_flag_fired=None,
    )


def _infer_seeds_per_fold(df: pd.DataFrame, *, rung: str, slice_name: str) -> int:
    """Count distinct seeds present per fold for the (rung, slice) selection.

    Returns the modal seed-count (most folds have S seeds; rare empty cell
    misses are tolerated). Used as audit metadata on the CrossFoldCIModel.
    """
    mask = (df["rung"] == rung) & (df["slice_name"] == slice_name)
    counts = df.loc[mask].groupby("fold")["seed"].nunique()
    if counts.empty:
        return 1
    return int(counts.mode().iloc[0])
