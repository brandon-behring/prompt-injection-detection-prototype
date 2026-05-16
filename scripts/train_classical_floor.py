"""CLI entrypoint — train all 12 (fold, seed) cells of the classical floor.

Per ADR-044 Q6, the classical floor (sklearn) runs locally on CPU; 12 cells
in approximately 5 minutes wall-clock; near-zero cost. Per ADR-017, the
classical floor is the only ``verified_disjoint`` anchor in the rung slate.

Usage
-----
.. code-block:: bash

    uv run python scripts/train_classical_floor.py
    uv run python scripts/train_classical_floor.py --fold-only 0 --seed-only 42

Defaults read ``configs/rungs/classical_floor.yaml``, source data from
``data/processed/`` (from ``make data-prepare``), and write predictions
to ``evals/predictions/``.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.training.train_classical import load_config, train_one_cell  # noqa: E402


def main() -> int:
    """Sweep the (fold, seed) grid; train each cell; print per-cell progress."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=_REPO_ROOT / "configs" / "rungs" / "classical_floor.yaml",
        help="Path to classical-floor rung YAML config",
    )
    parser.add_argument(
        "--processed-root",
        type=Path,
        default=_REPO_ROOT / "data" / "processed",
        help="Path to data/processed/ (Phase 1 materialized splits)",
    )
    parser.add_argument(
        "--predictions-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions",
        help="Path to evals/predictions/ output dir",
    )
    parser.add_argument(
        "--fold-only",
        type=int,
        default=None,
        help="Train only this fold (default: all 4)",
    )
    parser.add_argument(
        "--seed-only",
        type=int,
        default=None,
        help="Train only this seed (default: all 3 from config)",
    )
    args = parser.parse_args()

    if not args.config.exists():
        print(f"[train_classical_floor] ERROR: config not found at {args.config}")
        return 1
    if not args.processed_root.exists():
        print(f"[train_classical_floor] ERROR: data/processed not found at {args.processed_root}")
        print("[train_classical_floor] Run `make data-prepare` first.")
        return 1

    cfg = load_config(args.config)
    folds = [args.fold_only] if args.fold_only is not None else list(range(4))
    seeds = [args.seed_only] if args.seed_only is not None else list(cfg["seeds"])

    n_cells = len(folds) * len(seeds)
    print(
        f"[train_classical_floor] Training {len(folds)} folds x {len(seeds)} seeds "
        f"= {n_cells} cells (rung=tfidf-lr per ADR-017)"
    )

    t_start = time.monotonic()
    n_written = 0
    for fold in folds:
        for seed in seeds:
            t_cell = time.monotonic()
            print(f"[train_classical_floor] fold={fold} seed={seed} ... ", end="", flush=True)
            out_path = train_one_cell(
                config_path=args.config,
                fold=fold,
                seed=seed,
                processed_root=args.processed_root,
                predictions_root=args.predictions_root,
            )
            n_written += 1
            elapsed = time.monotonic() - t_cell
            print(
                f"-> {out_path.relative_to(_REPO_ROOT)} ({elapsed:.1f}s)",
                flush=True,
            )

    total_elapsed = time.monotonic() - t_start
    print(
        f"[train_classical_floor] Wrote {n_written} prediction parquets to "
        f"{args.predictions_root} (total {total_elapsed:.1f}s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
