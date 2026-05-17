"""CLI entrypoint — sweep MDE on every emitted CI per ADR-006 + ADR-046 Q4.

Per ADR-046 Q4 (Phase 4 Commit 5) + ADR-006 mandate, this script wraps every
CI half-width persisted by the Phase 3 + Phase 4 batteries into an MDE cell.
Total persistence is approximately 100 cells per ADR-006 — the Phase 5 WRITEUP
narrative draws its reporting subset from the full matrix.

Source CI parquets consumed
---------------------------
- ``evals/bootstrap/paired_cells.parquet`` — Phase 3 Commit 5
  (`BootstrapCellModel` per paired comparison)
- ``evals/bootstrap/marginal_cells.parquet`` — Phase 4 Commit 5
  (`MarginalBootstrapCellModel` per marginal CI)
- ``evals/audit/cross_fold_ci_audit.parquet`` — Phase 4 Commit 5
  (`CrossFoldCIModel` carrying both cv_clt + block-bootstrap halfwidths)

Outputs
-------
``--mde-out`` (default ``evals/audit/mde_per_cell.parquet``) — concatenated
`MDECellModel` rows. ``source_ci_kind`` discriminates provenance.

Usage
-----
.. code-block:: bash

    uv run python scripts/run_mde.py
    uv run python scripts/run_mde.py --power 0.9
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.eval.mde import (  # noqa: E402
    mde_from_marginal_ci_record,
)
from src.eval.schemas import MDECellModel  # noqa: E402


def _mde_cells_from_paired(parquet: Path, *, alpha: float, power: float) -> list[MDECellModel]:
    """Wrap every paired-bootstrap cell into an MDE cell via the closed-form path.

    Per ADR-046 Q4 paired cells go through the same closed-form formula as the
    marginal path (mde_from_paired_ci_record requires a live PairedBootstrapCI
    object which is not persisted in the parquet — only its CI bounds + diff).
    Numerically identical to mde_from_ci's inner formula per upstream issue #20.
    """
    if not parquet.exists():
        return []
    df = pd.read_parquet(parquet)
    cells: list[MDECellModel] = []
    for _, row in df.iterrows():
        ci_lo = float(row["ci_lo"])
        ci_hi = float(row["ci_hi"])
        if ci_hi <= ci_lo:
            continue
        cells.append(
            MDECellModel(
                rung_a=str(row["rung_a"]),
                rung_b=str(row["rung_b"]),
                slice_name=str(row["slice_name"]),
                metric=str(row["metric"]),
                source_ci_kind="paired_bootstrap",
                ci_halfwidth=(ci_hi - ci_lo) / 2.0,
                alpha=alpha,
                power=power,
                mde=mde_from_marginal_ci_record(
                    rung=f"{row['rung_a']}_vs_{row['rung_b']}",
                    slice_name=str(row["slice_name"]),
                    metric=str(row["metric"]),
                    ci_lo=ci_lo,
                    ci_hi=ci_hi,
                    n=-1,
                    alpha=alpha,
                    power=power,
                ).mde,
                n=-1,
            )
        )
    return cells


def _mde_cells_from_marginal(parquet: Path, *, alpha: float, power: float) -> list[MDECellModel]:
    if not parquet.exists():
        return []
    df = pd.read_parquet(parquet)
    cells: list[MDECellModel] = []
    for _, row in df.iterrows():
        ci_lo = float(row["ci_lo"])
        ci_hi = float(row["ci_hi"])
        if ci_hi <= ci_lo:
            continue
        cells.append(
            mde_from_marginal_ci_record(
                rung=str(row["rung"]),
                slice_name=str(row["slice_name"]),
                metric=str(row["metric"]),
                ci_lo=ci_lo,
                ci_hi=ci_hi,
                n=int(row["n_obs"]),
                source_ci_kind="marginal_bootstrap",
                alpha=alpha,
                power=power,
            )
        )
    return cells


def _mde_cells_from_cross_fold(parquet: Path, *, alpha: float, power: float) -> list[MDECellModel]:
    if not parquet.exists():
        return []
    df = pd.read_parquet(parquet)
    cells: list[MDECellModel] = []
    for _, row in df.iterrows():
        # cv_clt headline cell
        cv_lo = float(row["cv_clt_ci_lo"])
        cv_hi = float(row["cv_clt_ci_hi"])
        k_folds = int(row["k_folds"])
        n_seeds_per_fold = int(row["n_seeds_per_fold"])
        if cv_hi > cv_lo:
            cells.append(
                mde_from_marginal_ci_record(
                    rung=str(row["rung"]),
                    slice_name=str(row["slice_name"]),
                    metric=str(row["metric"]),
                    ci_lo=cv_lo,
                    ci_hi=cv_hi,
                    n=k_folds * n_seeds_per_fold,
                    source_ci_kind="cv_clt",
                    alpha=alpha,
                    power=power,
                )
            )
        # block-bootstrap spoke cell — emitted iff Commit 3 populated it.
        bb_lo_raw = row["block_bootstrap_ci_lo"]
        bb_hi_raw = row["block_bootstrap_ci_hi"]
        if bb_lo_raw is None or bb_hi_raw is None:
            continue
        bb_lo = float(bb_lo_raw)
        bb_hi = float(bb_hi_raw)
        if bb_hi > bb_lo:
            cells.append(
                mde_from_marginal_ci_record(
                    rung=str(row["rung"]),
                    slice_name=str(row["slice_name"]),
                    metric=str(row["metric"]),
                    ci_lo=bb_lo,
                    ci_hi=bb_hi,
                    n=k_folds,
                    source_ci_kind="block_bootstrap",
                    alpha=alpha,
                    power=power,
                )
            )
    return cells


def main() -> int:
    """Aggregate MDE cells from every source CI parquet; persist matrix to disk."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--paired-parquet",
        type=Path,
        default=_REPO_ROOT / "evals" / "bootstrap" / "paired_cells.parquet",
    )
    parser.add_argument(
        "--marginal-parquet",
        type=Path,
        default=_REPO_ROOT / "evals" / "bootstrap" / "marginal_cells.parquet",
    )
    parser.add_argument(
        "--cross-fold-parquet",
        type=Path,
        default=_REPO_ROOT / "evals" / "audit" / "cross_fold_ci_audit.parquet",
    )
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--power", type=float, default=0.8)
    parser.add_argument(
        "--mde-out",
        type=Path,
        default=_REPO_ROOT / "evals" / "audit" / "mde_per_cell.parquet",
    )
    args = parser.parse_args()

    all_cells: list[MDECellModel] = []
    all_cells.extend(
        _mde_cells_from_paired(args.paired_parquet, alpha=args.alpha, power=args.power)
    )
    all_cells.extend(
        _mde_cells_from_marginal(args.marginal_parquet, alpha=args.alpha, power=args.power)
    )
    all_cells.extend(
        _mde_cells_from_cross_fold(args.cross_fold_parquet, alpha=args.alpha, power=args.power)
    )

    if not all_cells:
        print(
            "[mde] no source CI parquets found — run the bootstrap + cv_clt batteries first",
            file=sys.stderr,
        )
        return 1

    args.mde_out.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame([c.model_dump() for c in all_cells])
    out_df.to_parquet(args.mde_out, index=False)
    print(
        f"[mde] wrote {len(all_cells)} MDE cells to {args.mde_out} "
        f"(alpha={args.alpha}, power={args.power}; per ADR-006 mandate)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
