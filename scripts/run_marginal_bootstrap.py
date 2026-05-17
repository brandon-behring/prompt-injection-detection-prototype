"""CLI entrypoint — sweep marginal-bootstrap CI cells per ADR-022 + ADR-046 Q1.

Per ADR-046 Q1 (Phase 4 Commit 5), this script sweeps marginal CIs across
the (rung x slice x metric x seed) grid via
`src.eval.marginal_bootstrap.compute_marginal_battery` and persists each
cell to `evals/bootstrap/marginal_cells.parquet` as `MarginalBootstrapCellModel`
records. Per ADR-022 the seed dimension covers both the seed=1 headline and
the seed=2 stability check so the half-width-diff flag is queryable from disk.

Inputs
------
``--predictions-root`` — directory of per-cell predictions parquets.
``--metrics`` — comma-separated list of metric names (default ``auprc,auroc``).
``--n-resamples`` — bootstrap iterations per cell (default 10000 per ADR-022).
``--seeds`` — comma-separated seeds (default ``1,2`` per ADR-022 multi-seed).

Outputs
-------
``--marginal-out`` (default ``evals/bootstrap/marginal_cells.parquet``) —
concatenated `MarginalBootstrapCellModel` rows.

Usage
-----
.. code-block:: bash

    uv run python scripts/run_marginal_bootstrap.py
    uv run python scripts/run_marginal_bootstrap.py --n-resamples 1000 --seeds 1,2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.eval.marginal_bootstrap import (  # noqa: E402
    HEADLINE_N_RESAMPLES,
    HEADLINE_SEED,
    MARGINAL_METRIC_REGISTRY,
    STABILITY_CHECK_SEED,
    compute_marginal_battery,
)
from src.eval.slice_analysis import (  # noqa: E402
    IID_SLICE_NAME,
    OOD_SLICE_NAMES,
    POOLED_OOD_SLICE_NAME,
)


def _classify_slice(source: str) -> str:
    if source in OOD_SLICE_NAMES:
        return source
    return IID_SLICE_NAME


def main() -> int:
    """Sweep marginal CIs; persist MarginalBootstrapCellModel rows to parquet."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predictions-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions",
    )
    parser.add_argument("--metrics", default="auprc,auroc")
    parser.add_argument("--n-resamples", type=int, default=HEADLINE_N_RESAMPLES)
    parser.add_argument(
        "--seeds",
        default=f"{HEADLINE_SEED},{STABILITY_CHECK_SEED}",
        help="Comma-separated bootstrap seeds (default headline + stability per ADR-022)",
    )
    parser.add_argument(
        "--marginal-out",
        type=Path,
        default=_REPO_ROOT / "evals" / "bootstrap" / "marginal_cells.parquet",
    )
    args = parser.parse_args()

    metric_names = [m.strip() for m in args.metrics.split(",") if m.strip()]
    for name in metric_names:
        if name not in MARGINAL_METRIC_REGISTRY:
            print(
                f"[marginal-bootstrap] unknown metric {name!r}; "
                f"valid: {sorted(MARGINAL_METRIC_REGISTRY)}",
                file=sys.stderr,
            )
            return 1

    try:
        seeds = tuple(int(s.strip()) for s in args.seeds.split(",") if s.strip())
    except ValueError:
        print(f"[marginal-bootstrap] invalid --seeds {args.seeds!r}", file=sys.stderr)
        return 1

    paths = sorted(args.predictions_root.glob("*.parquet"))
    if not paths:
        print(f"[marginal-bootstrap] no parquets at {args.predictions_root}", file=sys.stderr)
        return 1

    df = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)
    df["slice_name"] = df["source"].map(_classify_slice)

    rungs = sorted(df["rung"].unique())
    slice_names = sorted(set(df["slice_name"].unique()) | {POOLED_OOD_SLICE_NAME})

    # Pooled-OOD virtual slice — concatenate per-OOD rows once for marginal sweep.
    pooled_rows = df[df["slice_name"].isin(OOD_SLICE_NAMES)].copy()
    pooled_rows["slice_name"] = POOLED_OOD_SLICE_NAME
    df = pd.concat([df, pooled_rows], ignore_index=True)

    cells = compute_marginal_battery(
        df,
        rungs=rungs,
        slice_names=slice_names,
        metric_names=metric_names,
        n_resamples=args.n_resamples,
        seeds=seeds,
    )
    if not cells:
        print("[marginal-bootstrap] no cells produced", file=sys.stderr)
        return 1

    args.marginal_out.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame([c.model_dump() for c in cells])
    out_df.to_parquet(args.marginal_out, index=False)
    print(
        f"[marginal-bootstrap] wrote {len(cells)} cells "
        f"({len(rungs)} rungs x {len(slice_names)} slices x {len(metric_names)} metrics x "
        f"{len(seeds)} seeds, after empty-cell skips) to {args.marginal_out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
