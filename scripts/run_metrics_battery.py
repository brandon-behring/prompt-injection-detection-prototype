"""CLI entrypoint — compute the headline metrics battery per ADR-021 + ADR-023.

Per ADR-021 + ADR-023, this script sweeps a (rung, fold, seed, slice) grid
over the persisted predictions parquets and emits one MetricsRecordModel
per cell plus a pooled-OOD row per (rung, fold, seed).

Inputs
------
``--predictions-root`` (default ``evals/predictions/``) — directory carrying
parquet files matching `src.eval.schemas.PredictionsRowModel`.

``--rung-pattern`` (default ``*``) — glob filter on rung_id (e.g. ``lora`` to
process LoRA-only).

Outputs
-------
``--metrics-out`` (default ``evals/metrics/per_cell.parquet``) — concatenated
per-(rung, fold, seed, slice) MetricsRecordModel rows.

Usage
-----
.. code-block:: bash

    uv run python scripts/run_metrics_battery.py
    uv run python scripts/run_metrics_battery.py --predictions-root tests/fixtures/predictions
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.eval.schemas import MetricsRecordModel  # noqa: E402
from src.eval.slice_analysis import (  # noqa: E402
    IID_SLICE_NAME,
    OOD_SLICE_NAMES,
    compute_metric_record,
    compute_pooled_ood_record,
)


def _load_predictions(predictions_root: Path, rung_pattern: str) -> pd.DataFrame:
    """Load all parquets under predictions_root matching the rung pattern."""
    pattern = f"{rung_pattern}*.parquet"
    paths = sorted(predictions_root.glob(pattern))
    if not paths:
        raise FileNotFoundError(
            f"no predictions parquets at {predictions_root} matching pattern {pattern!r}"
        )
    frames = [pd.read_parquet(p) for p in paths]
    return pd.concat(frames, ignore_index=True)


def _classify_slice(source: str) -> str:
    """Map a source name to a slice name: OOD slice name OR 'iid' for benigns/positives."""
    if source in OOD_SLICE_NAMES:
        return source
    return IID_SLICE_NAME


def main() -> int:
    """Run the metrics battery; persist per-cell + pooled-OOD records."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predictions-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions",
    )
    parser.add_argument("--rung-pattern", default="*")
    parser.add_argument(
        "--metrics-out",
        type=Path,
        default=_REPO_ROOT / "evals" / "metrics" / "per_cell.parquet",
    )
    parser.add_argument(
        "--epoch-filter",
        type=int,
        default=None,
        help=(
            "If set, restrict aggregation to rows with this `epoch` value. "
            "Used by the DeBERTa-v3-base ablation per ADR-060 to report only "
            "the final-epoch headline (epoch=2) per the methodology lock. "
            "Default None preserves the pre-v1.1.2 ModernBERT behaviour "
            "(all available epochs aggregated together)."
        ),
    )
    args = parser.parse_args()

    df = _load_predictions(args.predictions_root, args.rung_pattern)
    if args.epoch_filter is not None:
        n_before = len(df)
        df = df[df["epoch"] == args.epoch_filter].reset_index(drop=True)
        print(
            f"[metrics] --epoch-filter={args.epoch_filter}: "
            f"{n_before} -> {len(df)} rows after filter"
        )
        if df.empty:
            print(
                f"[metrics] ERROR: no rows match epoch={args.epoch_filter}; check training output",
                file=sys.stderr,
            )
            return 1
    df["slice_name"] = df["source"].map(_classify_slice)

    records: list[MetricsRecordModel] = []
    grouped = df.groupby(["rung", "fold", "seed"])
    for key, cell_df in grouped:
        rung, fold_val, seed_val = key
        fold = cast(int, fold_val)
        seed = cast(int, seed_val)
        # Per-slice records.
        for slice_name, slice_df in cell_df.groupby("slice_name"):
            if slice_df.empty:
                continue
            try:
                rec = compute_metric_record(
                    rung=str(rung),
                    fold=fold,
                    seed=seed,
                    slice_name=str(slice_name),
                    df=slice_df,
                    include_0_1_pinpoint=False,
                )
                records.append(rec)
            except ValueError as err:
                print(f"[metrics] skip {rung}/{fold}/{seed}/{slice_name}: {err}", file=sys.stderr)

        # Pooled OOD record per (rung, fold, seed).
        per_slice_dfs = {
            name: cell_df[cell_df["slice_name"] == name]
            for name in OOD_SLICE_NAMES
            if not cell_df[cell_df["slice_name"] == name].empty
        }
        if per_slice_dfs:
            try:
                pooled = compute_pooled_ood_record(
                    rung=str(rung),
                    fold=fold,
                    seed=seed,
                    per_slice_dfs=per_slice_dfs,
                )
                records.append(pooled)
            except ValueError as err:
                print(f"[metrics] skip pooled-OOD {rung}/{fold}/{seed}: {err}", file=sys.stderr)

    if not records:
        print("[metrics] no metric records produced", file=sys.stderr)
        return 1

    args.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame([r.model_dump() for r in records])
    out_df.to_parquet(args.metrics_out, index=False)
    print(f"[metrics] wrote {len(records)} records to {args.metrics_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
