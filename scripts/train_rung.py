"""CLI entrypoint — train all 12 (fold, seed) cells of one transformer rung.

Per ADR-044 Q6, per-rung orchestration is the canonical Phase 2 cadence:
3 GPU jobs (one per transformer rung) + 1 local CPU job (the classical floor
via ``scripts/train_classical_floor.py``). Each invocation sweeps 12 cells
(3 seeds × 4 LODO folds) for one rung; failure-isolation lets us re-run a
single rung mid-Phase-2 without losing progress on other rungs.

Usage
-----
.. code-block:: bash

    # Full sweep (12 cells per rung; meant for cloud runs via runpod-deploy)
    uv run python scripts/train_rung.py --rung frozen_probe
    uv run python scripts/train_rung.py --rung lora
    uv run python scripts/train_rung.py --rung full_ft

    # Partial sweep (debugging or smoke)
    uv run python scripts/train_rung.py --rung lora --fold-only 0 --seed-only 42

The defaults read ``configs/rungs/<rung>.yaml``, source data from
``data/processed/`` (produced by ``make data-prepare`` at Phase 1), and write
per-epoch predictions to ``evals/predictions/``.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.training.train_modernbert import VALID_CLASSIFIER_TYPES, load_config, train_one_cell  # noqa: E402


def main() -> int:
    """Parse args, sweep the (fold, seed) grid, write per-epoch parquets."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rung",
        required=True,
        choices=sorted(VALID_CLASSIFIER_TYPES),
        help="Which transformer rung to train (per ADR-044 Q6)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to rung YAML config (default: configs/rungs/<rung>.yaml)",
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
        help="Path to evals/predictions/ output",
    )
    parser.add_argument(
        "--checkpoint-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "checkpoints",
        help="Path to evals/checkpoints/ for the final-epoch checkpoint dir per cell.",
    )
    parser.add_argument(
        "--checkpoint-staging-root",
        type=Path,
        default=None,
        help=(
            "Optional: if set, HF Trainer writes per-step checkpoints here during training, "
            "then the final-epoch dir is copied to --checkpoint-root after training completes. "
            "Workaround for FUSE F_SETLKW hangs on /workspace (HF Trainer atomic-save protocol "
            "stalls on MooseFS-backed paths; see memory entry "
            "fuse-workspace-needs-uv-link-mode-copy.md). On RunPod pods, set this to "
            "/root/training_staging (container overlay disk; POSIX locks work normally). "
            "Default: None (Trainer writes directly to --checkpoint-root; safe locally but hangs on FUSE)."
        ),
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

    config_path: Path = args.config or (_REPO_ROOT / "configs" / "rungs" / f"{args.rung}.yaml")
    if not config_path.exists():
        print(f"[train_rung] ERROR: config not found at {config_path}")
        return 1
    if not args.processed_root.exists():
        print(f"[train_rung] ERROR: data/processed not found at {args.processed_root}")
        print("[train_rung] Run `make data-prepare` first (Phase 1).")
        return 1

    cfg = load_config(config_path)
    folds: list[int] = [args.fold_only] if args.fold_only is not None else list(range(4))
    seeds: list[int] = [args.seed_only] if args.seed_only is not None else list(cfg["seeds"])

    n_cells = len(folds) * len(seeds)
    print(
        f"[train_rung] START rung={args.rung} {len(folds)} folds x {len(seeds)} seeds "
        f"= {n_cells} cells (backbone={cfg['backbone']['hf_id']}@{cfg['backbone']['revision'][:8]})"
    )

    t_start = time.monotonic()
    n_cells_done = 0
    n_files_written = 0
    for fold in folds:
        for seed in seeds:
            t_cell = time.monotonic()
            print(
                f"[train_rung] rung={args.rung} fold={fold} seed={seed} ...",
                flush=True,
            )
            written = train_one_cell(
                config_path=config_path,
                fold=fold,
                seed=seed,
                processed_root=args.processed_root,
                predictions_root=args.predictions_root,
                checkpoint_root=args.checkpoint_root,
                checkpoint_staging_root=args.checkpoint_staging_root,
            )
            n_cells_done += 1
            n_files_written += len(written)
            elapsed = time.monotonic() - t_cell
            print(
                f"[train_rung]   -> wrote {len(written)} per-epoch parquets ({elapsed:.1f}s)",
                flush=True,
            )
            for p in written:
                try:
                    display_p: Path | str = p.relative_to(_REPO_ROOT)
                except ValueError:
                    display_p = p
                print(f"[train_rung]      {display_p}")

    total_elapsed = time.monotonic() - t_start
    # The success_marker in configs/runpod/headline-<rung>.yaml matches this line.
    print(
        f"[train_rung] DONE rung={args.rung} {n_cells_done} cells / "
        f"{n_files_written} parquets in {total_elapsed:.1f}s"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
