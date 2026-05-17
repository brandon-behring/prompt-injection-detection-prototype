"""CLI entrypoint — run the full-pairwise paired-bootstrap battery per ADR-022 + ADR-045 Q6.

Per ADR-045 Q6 user refinement, ALL pairwise comparisons are computed and
persisted (~30 cells: C(4 trained rungs, 2) = 6 pairwise × 5 OOD slices),
even though the WRITEUP narrative features only the 3 headline comparisons
(classical-floor vs frozen-probe; frozen-probe vs LoRA; LoRA vs full-FT).

Persistence preserves the methodology contract per ADR-013 — post-hoc
questions ("what about classical-floor vs LoRA?") are answered from disk
without re-running the bootstrap battery.

Inputs
------
``--predictions-root`` — directory of per-cell prediction parquets.
``--metrics`` — comma-separated list of metric names (default ``auprc,auroc``).
``--n-resamples`` — bootstrap iterations per cell (default 10000 per ADR-022).
``--seed`` — bootstrap seed (1 = headline, 2 = stability check per ADR-022).

Outputs
-------
``--bootstrap-out`` (default ``evals/bootstrap/paired_cells.parquet``) —
concatenated BootstrapCellModel rows.

Usage
-----
.. code-block:: bash

    uv run python scripts/run_bootstrap_battery.py
    uv run python scripts/run_bootstrap_battery.py --n-resamples 1000 --seed 1
"""

from __future__ import annotations

import argparse
import itertools
import sys
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd
from eval_toolkit.bootstrap import paired_bootstrap_diff
from eval_toolkit.metrics import pr_auc, roc_auc
from numpy.typing import NDArray

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.eval.schemas import BootstrapCellModel  # noqa: E402
from src.eval.slice_analysis import IID_SLICE_NAME, OOD_SLICE_NAMES  # noqa: E402

# Metric registry — map metric names to eval-toolkit primitives.
METRIC_REGISTRY: dict[str, Callable[..., float]] = {
    "auprc": pr_auc,
    "auroc": roc_auc,
}


def _classify_slice(source: str) -> str:
    if source in OOD_SLICE_NAMES:
        return source
    return IID_SLICE_NAME


def _build_pair_table(
    df: pd.DataFrame, rung_a: str, rung_b: str, slice_name: str
) -> tuple[NDArray[np.int_], NDArray[np.float64], NDArray[np.float64]] | None:
    """Join rung_a + rung_b on (source, row_idx_in_source) within a slice.

    Returns (y_true, score_a, score_b) aligned arrays, or None if no overlap.
    """
    slice_filter = df["slice_name"] == slice_name
    a = df[slice_filter & (df["rung"] == rung_a)][
        ["source", "row_idx_in_source", "label", "predicted_proba_class1"]
    ].rename(columns={"predicted_proba_class1": "score_a"})
    b = df[slice_filter & (df["rung"] == rung_b)][
        ["source", "row_idx_in_source", "predicted_proba_class1"]
    ].rename(columns={"predicted_proba_class1": "score_b"})
    if a.empty or b.empty:
        return None
    joined = a.merge(b, on=["source", "row_idx_in_source"], how="inner")
    if joined.empty:
        return None
    return (
        joined["label"].to_numpy(dtype=np.int_),
        joined["score_a"].to_numpy(dtype=np.float64),
        joined["score_b"].to_numpy(dtype=np.float64),
    )


def main() -> int:
    """Sweep all pairwise rung × slice × metric cells; persist paired-bootstrap CIs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predictions-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions",
    )
    parser.add_argument("--metrics", default="auprc,auroc")
    parser.add_argument("--n-resamples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument(
        "--bootstrap-out",
        type=Path,
        default=_REPO_ROOT / "evals" / "bootstrap" / "paired_cells.parquet",
    )
    args = parser.parse_args()

    metric_names = [m.strip() for m in args.metrics.split(",") if m.strip()]
    for name in metric_names:
        if name not in METRIC_REGISTRY:
            print(
                f"[bootstrap] unknown metric {name!r}; valid: {list(METRIC_REGISTRY)}",
                file=sys.stderr,
            )
            return 1

    paths = sorted(args.predictions_root.glob("*.parquet"))
    if not paths:
        print(f"[bootstrap] no parquets at {args.predictions_root}", file=sys.stderr)
        return 1

    df = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)
    df["slice_name"] = df["source"].map(_classify_slice)

    rungs = sorted(df["rung"].unique())
    slices = sorted(set(df["slice_name"].unique()))

    cells: list[BootstrapCellModel] = []
    for rung_a, rung_b in itertools.combinations(rungs, 2):
        for slice_name in slices:
            pair = _build_pair_table(df, rung_a, rung_b, slice_name)
            if pair is None:
                continue
            y, score_a, score_b = pair
            if y.sum() == 0 or y.sum() == len(y):
                continue  # single-class slice — metric undefined
            for metric_name in metric_names:
                metric_fn = METRIC_REGISTRY[metric_name]
                try:
                    result = paired_bootstrap_diff(
                        y,
                        score_a,
                        score_b,
                        metric_fn,
                        n_resamples=args.n_resamples,
                        seed=args.seed,
                    )
                except (RuntimeError, ValueError) as err:
                    print(
                        f"[bootstrap] skip {rung_a} vs {rung_b} / {slice_name} / {metric_name}: {err}",
                        file=sys.stderr,
                    )
                    continue

                point_a = float(np.clip(metric_fn(y, score_a), 0.0, 1.0))
                point_b = float(np.clip(metric_fn(y, score_b), 0.0, 1.0))
                cell = BootstrapCellModel(
                    rung_a=rung_a,
                    rung_b=rung_b,
                    slice_name=str(slice_name),
                    metric=metric_name,
                    n_resamples=args.n_resamples,
                    seed=args.seed,
                    point_estimate_a=point_a,
                    point_estimate_b=point_b,
                    point_estimate_diff=float(getattr(result, "diff", point_b - point_a)),
                    ci_lo=float(getattr(result, "ci_lo", getattr(result, "lo", 0.0))),
                    ci_hi=float(getattr(result, "ci_hi", getattr(result, "hi", 0.0))),
                    ci_method="percentile",
                )
                cells.append(cell)

    if not cells:
        print("[bootstrap] no bootstrap cells produced", file=sys.stderr)
        return 1

    args.bootstrap_out.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame([c.model_dump() for c in cells])
    out_df.to_parquet(args.bootstrap_out, index=False)
    print(
        f"[bootstrap] wrote {len(cells)} paired-bootstrap cells "
        f"({len(rungs)} rungs × {len(slices)} slices × {len(metric_names)} metrics) "
        f"to {args.bootstrap_out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
