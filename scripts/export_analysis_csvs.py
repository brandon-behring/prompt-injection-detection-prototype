"""Export analysis CSVs to `analysis/v1.0.7_canonical/` per NEXT_STEPS §1.2.

Generates 3 CSVs:

1. **`paired_tests.csv`** — 1:1 mirror of `evals/bootstrap/paired_cells.parquet`
   (40 rows × 12 columns). Round-trip via
   `pd.read_parquet(P).equals(pd.read_csv(C))` after appropriate type coercion.

2. **`ece_per_cell.csv`** — 1:1 mirror of `evals/metrics/per_cell.parquet`
   (114 rows × 14 columns including ECE + Brier).

3. **`per_source_rates.csv`** — NEW label-audit aggregation. For each
   (source, fold, seed) cell, reports positive_prevalence + n_rows +
   mean_predicted_proba per rung. Aggregates from
   `evals/predictions/*.parquet` (282 files).

Per /exploring-options batch 9 Q3 lock (1:1 parquet mirror + per_source_rates supplement).

Landed at v1.0.7 per Path 3 close of NEXT_STEPS §1.2.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def _find_repo_root(start: Path) -> Path:
    """Walk up from `start` until we find a `pyproject.toml`.

    Parameters
    ----------
    start : Path
        Starting directory.

    Returns
    -------
    Path
        The repo root containing `pyproject.toml`.

    Raises
    ------
    RuntimeError
        If no `pyproject.toml` is found in any ancestor.
    """
    cur = start.resolve()
    while cur != cur.parent:
        if (cur / "pyproject.toml").exists():
            return cur
        cur = cur.parent
    raise RuntimeError(f"no pyproject.toml found in any ancestor of {start}")


def export_paired_tests(repo_root: Path, out_dir: Path) -> int:
    """Export paired_cells.parquet → paired_tests.csv (1:1 mirror).

    Returns
    -------
    int
        Number of rows written.
    """
    src = repo_root / "evals" / "bootstrap" / "paired_cells.parquet"
    if not src.exists():
        raise FileNotFoundError(f"missing {src}")
    df = pd.read_parquet(src)
    dst = out_dir / "paired_tests.csv"
    df.to_csv(dst, index=False)
    print(f"  wrote {dst.relative_to(repo_root)} ({len(df)} rows × {df.shape[1]} cols)")
    return len(df)


def export_ece_per_cell(repo_root: Path, out_dir: Path) -> int:
    """Export per_cell.parquet → ece_per_cell.csv (1:1 mirror).

    Returns
    -------
    int
        Number of rows written.
    """
    src = repo_root / "evals" / "metrics" / "per_cell.parquet"
    if not src.exists():
        raise FileNotFoundError(f"missing {src}")
    df = pd.read_parquet(src)
    dst = out_dir / "ece_per_cell.csv"
    df.to_csv(dst, index=False)
    print(f"  wrote {dst.relative_to(repo_root)} ({len(df)} rows × {df.shape[1]} cols)")
    return len(df)


def export_per_source_rates(repo_root: Path, out_dir: Path) -> int:
    """Build + export per_source_rates.csv from predictions parquets.

    Aggregates from `evals/predictions/*.parquet` (282 files; canonical
    fold0/seed42 LODO test slate). Each row reports (rung, source,
    fold, seed) with positive_prevalence + n_rows + mean predicted proba.

    Returns
    -------
    int
        Number of rows written.
    """
    pred_dir = repo_root / "evals" / "predictions"
    if not pred_dir.exists():
        raise FileNotFoundError(f"missing {pred_dir}")

    rows: list[dict[str, object]] = []
    pred_files = sorted(pred_dir.glob("*.parquet"))
    for pred_path in pred_files:
        try:
            df = pd.read_parquet(pred_path)
        except Exception as exc:
            print(f"  warning: failed to read {pred_path}: {exc}", file=sys.stderr)
            continue
        # File schema includes: rung, fold, seed, source, label, predicted_proba_class1
        for (rung, fold, seed, source), grp in df.groupby(
            ["rung", "fold", "seed", "source"], dropna=False
        ):
            rows.append(
                {
                    "rung": rung,
                    "fold": fold,
                    "seed": seed,
                    "source": source,
                    "n_rows": len(grp),
                    "n_positive": int(grp["label"].sum()),
                    "positive_prevalence": float(grp["label"].mean()),
                    "mean_predicted_proba": float(grp["predicted_proba_class1"].mean()),
                    "std_predicted_proba": float(grp["predicted_proba_class1"].std(ddof=0)),
                }
            )
    out_df = (
        pd.DataFrame(rows).sort_values(["rung", "fold", "seed", "source"]).reset_index(drop=True)
    )
    dst = out_dir / "per_source_rates.csv"
    out_df.to_csv(dst, index=False)
    print(f"  wrote {dst.relative_to(repo_root)} ({len(out_df)} rows × {out_df.shape[1]} cols)")
    return len(out_df)


def main(argv: list[str] | None = None) -> int:
    """Export analysis CSVs; return 0 on success.

    Parameters
    ----------
    argv : list[str] | None
        Argv list (for testing); defaults to sys.argv[1:].

    Returns
    -------
    int
        0 on success; 1 if any export failed.
    """
    parser = argparse.ArgumentParser(description="Export analysis CSVs per NEXT_STEPS §1.2")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: <repo_root>/analysis/v1.0.7_canonical/)",
    )
    args = parser.parse_args(argv)

    repo_root = _find_repo_root(Path.cwd())
    out_dir = args.out_dir or (repo_root / "analysis" / "v1.0.7_canonical")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Repo root: {repo_root}")
    print(f"Out dir:   {out_dir}")
    print()

    try:
        export_paired_tests(repo_root, out_dir)
        export_ece_per_cell(repo_root, out_dir)
        export_per_source_rates(repo_root, out_dir)
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print()
    print(f"OK: 3 CSVs written to {out_dir.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
