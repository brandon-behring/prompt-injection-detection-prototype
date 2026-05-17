"""CLI entrypoint — sweep cross-fold CI cells per ADR-024 + ADR-046 Q3.

Per ADR-046 Q3 (Phase 4 Commit 5), this script sweeps cross-fold CIs across
the (rung x slice x metric) grid via
`src.eval.cross_fold_ci.compute_cross_fold_ci_cell`. Each cell carries both
the cv_clt headline (Bayle 2020) and the block-bootstrap-on-folds spoke
(inline impl per upstream issue #21) plus the a_008_flag_fired boolean.
Persisted to `evals/audit/cross_fold_ci_audit.parquet` per ADR-013.

Inputs
------
``--predictions-root`` — directory of per-cell predictions parquets.
``--metrics`` — comma-separated metric names (default ``auprc,auroc``).
``--block-n-resamples`` — block-bootstrap iterations per cell
(default 10000 per ADR-022).

Outputs
-------
``--audit-out`` (default ``evals/audit/cross_fold_ci_audit.parquet``) —
concatenated `CrossFoldCIModel` rows.

Usage
-----
.. code-block:: bash

    uv run python scripts/run_cv_clt_ci.py
    uv run python scripts/run_cv_clt_ci.py --block-n-resamples 1000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.eval.cross_fold_ci import (  # noqa: E402
    BLOCK_BOOTSTRAP_N_RESAMPLES,
    CROSS_FOLD_METRIC_REGISTRY,
    compute_cross_fold_ci_cell,
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
    """Sweep cross-fold CIs; persist CrossFoldCIModel rows to parquet."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predictions-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions",
    )
    parser.add_argument("--metrics", default="auprc,auroc")
    parser.add_argument("--block-n-resamples", type=int, default=BLOCK_BOOTSTRAP_N_RESAMPLES)
    parser.add_argument(
        "--audit-out",
        type=Path,
        default=_REPO_ROOT / "evals" / "audit" / "cross_fold_ci_audit.parquet",
    )
    args = parser.parse_args()

    metric_names = [m.strip() for m in args.metrics.split(",") if m.strip()]
    for name in metric_names:
        if name not in CROSS_FOLD_METRIC_REGISTRY:
            print(
                f"[cv-clt] unknown metric {name!r}; valid: {sorted(CROSS_FOLD_METRIC_REGISTRY)}",
                file=sys.stderr,
            )
            return 1

    paths = sorted(args.predictions_root.glob("*.parquet"))
    if not paths:
        print(f"[cv-clt] no parquets at {args.predictions_root}", file=sys.stderr)
        return 1

    df = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)
    df["slice_name"] = df["source"].map(_classify_slice)

    pooled_rows = df[df["slice_name"].isin(OOD_SLICE_NAMES)].copy()
    pooled_rows["slice_name"] = POOLED_OOD_SLICE_NAME
    df = pd.concat([df, pooled_rows], ignore_index=True)

    rungs = sorted(df["rung"].unique())
    slice_names = sorted(set(df["slice_name"].unique()))

    cells = []
    n_flagged = 0
    for rung in rungs:
        for slice_name in slice_names:
            for metric_name in metric_names:
                try:
                    cell = compute_cross_fold_ci_cell(
                        df,
                        rung=str(rung),
                        slice_name=str(slice_name),
                        metric_name=metric_name,
                        block_bootstrap_n_resamples=args.block_n_resamples,
                    )
                except ValueError as err:
                    print(
                        f"[cv-clt] skip {rung}/{slice_name}/{metric_name}: {err}",
                        file=sys.stderr,
                    )
                    continue
                cells.append(cell)
                if cell.a_008_flag_fired:
                    n_flagged += 1

    if not cells:
        print("[cv-clt] no cells produced", file=sys.stderr)
        return 1

    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame([c.model_dump() for c in cells])
    out_df.to_parquet(args.audit_out, index=False)
    print(
        f"[cv-clt] wrote {len(cells)} cells to {args.audit_out} "
        f"({n_flagged} a_008_flag_fired per ADR-024 + A-008 sensitivity check)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
