"""Phase 4 cross-fold CI primitives per ADR-024 + ADR-046 Q3.

Commit 2 shipped the **headline cv_clt CI** via `eval_toolkit.bootstrap.cv_clt_ci`
(Bayle 2020 Annals of Statistics Theorem 3.1). Commit 3 (this update) adds the
always-emit **block-bootstrap-on-folds spoke** + the `a_008_flag_fired` boolean
per the A-008 sensitivity check (LODO non-exchangeability dominates within-fold
variance when `block_bootstrap_halfwidth / cv_clt_halfwidth > 1.5`).

The headline takes per-(fold, seed) metric values (K folds x S seeds-per-fold)
and reduces them to per-fold means before feeding `cv_clt_ci`. Per ADR-022 the
seed-within-fold replications average together to yield a single point per fold,
which is the regime Bayle 2020's CV-CLT assumes (K independent fold estimates).

The block-bootstrap spoke resamples K folds with replacement from the same
per-fold vector and computes a percentile CI on the resulting empirical
distribution of fold-mean draws. This is robust to LODO non-exchangeability
(folds carry different sources with different size + attack-style character;
they are not exchangeable in the CV-CLT sense) so a wider block-bootstrap CI
than the cv_clt headline indicates LODO variance dominates within-fold variance
— surfaced via `a_008_flag_fired` per A-008.

Library-first
-------------
- `eval_toolkit.bootstrap.cv_clt_ci` does the Bayle 2020 CI math (headline).
- `eval_toolkit.metrics.{pr_auc, roc_auc}` are the per-fold metric callbacks.

Project glue is per-(fold, seed) grouping + within-fold mean aggregation +
`CrossFoldCIModel` schema validator. Both the cv_clt headline AND the
block-bootstrap spoke math are now upstream — closed in eval-toolkit
v0.34.0 (#21).

Upstream
--------
Block-bootstrap-on-folds (CV-aware block bootstrap; complement to `cv_clt_ci`)
is now `eval_toolkit.block_bootstrap_on_folds` per eval-toolkit v0.34.0.
The wrapper below adapts the BootstrapCI return to this project's
`(ci_lo, ci_hi)` tuple shape; the actual algorithm lives upstream.
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

# Block-bootstrap-on-folds default budget (per ADR-022 statistical-inference
# apparatus + ADR-046 Q3). 10K resamples mirror the marginal/paired bootstrap
# budget; the resampling unit here is a complete fold (K-element draw with
# replacement), not a row, so 10K runs in O(seconds) per cell.
BLOCK_BOOTSTRAP_N_RESAMPLES: Final[int] = 10_000
BLOCK_BOOTSTRAP_SEED: Final[int] = 1

# A-008 sensitivity-check threshold. When the block-bootstrap CI half-width
# exceeds 1.5x the cv_clt CI half-width, the methodology spoke names "LODO
# non-exchangeability dominates within-fold variance" per ADR-024.
A_008_RATIO_THRESHOLD: Final[float] = 1.5


def compute_block_bootstrap_on_folds(
    per_fold_metrics: NDArray[np.float64],
    *,
    n_resamples: int = BLOCK_BOOTSTRAP_N_RESAMPLES,
    confidence: float = 0.95,
    seed: int = BLOCK_BOOTSTRAP_SEED,
) -> tuple[float, float]:
    """Block-bootstrap-on-folds: thin wrapper over `eval_toolkit.block_bootstrap_on_folds`.

    Adapts the upstream `BootstrapCI` return to this project's
    `(ci_lo, ci_hi)` tuple shape. The algorithm + validation live upstream
    in eval-toolkit v0.34.0+ (closes upstream #21):

        1. Draw n_resamples K-element samples with replacement from
           per_fold_metrics (each draw represents a hypothetical alternative
           cross-validation outcome under fold-exchangeability).
        2. Compute the mean of each resample.
        3. Return the [alpha/2, 1 - alpha/2] percentile CI on the empirical
           distribution of resample means.

    Wider CI than `cv_clt_ci` on the same per-fold vector indicates LODO
    non-exchangeability dominates within-fold variance per A-008.

    Parameters
    ----------
    per_fold_metrics : np.ndarray, shape (K,)
        K per-fold metric estimates. Need K >= 2.
    n_resamples : int, optional
        Number of bootstrap resamples (default 10000 per ADR-022).
    confidence : float, optional
        Two-sided confidence level (default 0.95).
    seed : int, optional
        RNG seed for reproducibility.

    Returns
    -------
    (ci_lo, ci_hi) : tuple[float, float]
    """
    from eval_toolkit import block_bootstrap_on_folds

    ci = block_bootstrap_on_folds(
        per_fold_metrics,
        n_resamples=n_resamples,
        confidence=confidence,
        rng=seed,
    )
    return float(ci.ci_low), float(ci.ci_high)


def compute_a_008_flag(*, cv_clt_halfwidth: float, block_bootstrap_halfwidth: float) -> bool:
    """Return True iff block_bootstrap_halfwidth / cv_clt_halfwidth > A_008_RATIO_THRESHOLD."""
    if cv_clt_halfwidth <= 0.0:
        # Degenerate cv_clt halfwidth (all-folds-identical) — A-008 trivially fires
        # if any block-bootstrap variance is present.
        return block_bootstrap_halfwidth > 0.0
    return (block_bootstrap_halfwidth / cv_clt_halfwidth) > A_008_RATIO_THRESHOLD


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
    block_bootstrap_n_resamples: int = BLOCK_BOOTSTRAP_N_RESAMPLES,
    block_bootstrap_seed: int = BLOCK_BOOTSTRAP_SEED,
) -> CrossFoldCIModel:
    """Compute the full cross-fold CI cell — cv_clt headline + block-bootstrap spoke.

    Per ADR-046 Q3, this function always emits both the cv_clt headline and the
    block-bootstrap-on-folds spoke; the `a_008_flag_fired` boolean is filled
    deterministically from the two half-widths per A-008 + ADR-024.
    """
    per_fold = compute_per_fold_metric_vector(
        df, rung=rung, slice_name=slice_name, metric_name=metric_name
    )
    n_seeds_per_fold = _infer_seeds_per_fold(df=df, rung=rung, slice_name=slice_name)

    # Headline cv_clt CI (Bayle 2020 Theorem 3.1) via eval-toolkit.
    cv_clt = cv_clt_ci(per_fold, confidence=0.95)
    cv_clt_halfwidth = (float(cv_clt.ci_high) - float(cv_clt.ci_low)) / 2.0

    # Block-bootstrap-on-folds spoke per A-008 — library-first via `eval_toolkit.block_bootstrap_on_folds`
    # (eval-toolkit #21 closed; consumed at v1.0.x; ADR-066 §B6 records the carryforward).
    block_ci_lo, block_ci_hi = compute_block_bootstrap_on_folds(
        per_fold,
        n_resamples=block_bootstrap_n_resamples,
        confidence=0.95,
        seed=block_bootstrap_seed,
    )
    block_halfwidth = (block_ci_hi - block_ci_lo) / 2.0

    a_008_flag = compute_a_008_flag(
        cv_clt_halfwidth=cv_clt_halfwidth, block_bootstrap_halfwidth=block_halfwidth
    )

    return CrossFoldCIModel(
        rung=rung,
        slice_name=slice_name,
        metric=metric_name,
        k_folds=int(per_fold.shape[0]),
        n_seeds_per_fold=n_seeds_per_fold,
        cv_clt_point_estimate=float(cv_clt.point_estimate),
        cv_clt_ci_lo=float(cv_clt.ci_low),
        cv_clt_ci_hi=float(cv_clt.ci_high),
        cv_clt_ci_halfwidth=cv_clt_halfwidth,
        block_bootstrap_ci_lo=block_ci_lo,
        block_bootstrap_ci_hi=block_ci_hi,
        block_bootstrap_ci_halfwidth=block_halfwidth,
        block_bootstrap_n_resamples=block_bootstrap_n_resamples,
        a_008_flag_fired=a_008_flag,
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
