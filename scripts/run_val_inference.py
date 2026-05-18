"""Per-cell val.parquet inference for trained rungs — enables dual-policy threshold fitting.

scripts/fit_dual_policy_thresholds.py reads predictions on val (both-class) per
ADR-025 to fit detection (FPR <= 1%) + verification (recall >= 99%) operating
points. Phase 2 training emitted LODO test predictions only (per ADR-019); val
predictions were a Phase 4 deferred step. This script closes that gap.

Reads ``data/processed/fold-{F}/seed-{S}/val.parquet`` per cell + runs inference
via the same primitives as ``scripts/run_inference_battery.py`` (TF-IDF+LR
re-fit per cell; frozen-probe / LoRA from local checkpoints). Writes per-cell
parquet to ``evals/predictions_val/<rung>__fold<F>__seed<S>__val.parquet``
matching ``src.eval.schemas.PredictionsRowModel``.

full-FT is NOT supported — no checkpoints exist locally (Phase 2 stripped them
via ``cleanup_intermediate_checkpoints: true``; Phase 5 re-fire crashed via
FUSE EIO before checkpoints persisted). Dual-policy for full-FT is deferred
pending an ADR-018 supersession.

Usage
-----

.. code-block:: bash

    # All trained rungs (tfidf-lr + frozen-probe + LoRA)
    uv run python scripts/run_val_inference.py

    # Single rung
    uv run python scripts/run_val_inference.py --rung lora

    # Smoke (200 rows per cell)
    uv run python scripts/run_val_inference.py --rung tfidf-lr --smoke 200
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, cast

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.training.tfidf_lr import build_tfidf_lr_pipeline  # noqa: E402
from src.training.train_classical import load_config as load_classical_config  # noqa: E402

PROCESSED_ROOT = _REPO_ROOT / "data" / "processed"
SEEDS: tuple[int, ...] = (42, 43, 44)
FOLDS: tuple[int, ...] = (0, 1, 2, 3)


def _load_val(fold: int, seed: int, smoke_n: int | None) -> pd.DataFrame | None:
    """Load val.parquet for one cell; cap to smoke_n if set. Returns None if missing."""
    path = PROCESSED_ROOT / f"fold-{fold}" / f"seed-{seed}" / "val.parquet"
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    if smoke_n is not None and len(df) > smoke_n:
        df = df.head(smoke_n).reset_index(drop=True)
    return df


def run_tfidf_val(output_root: Path, smoke_n: int | None) -> tuple[int, list[str]]:
    """TF-IDF+LR: re-fit per cell on train.parquet + score val.parquet.

    Returns (n_success, failures) where failures is a list of error strings.
    """
    config_path = _REPO_ROOT / "configs" / "rungs" / "classical_floor.yaml"
    cfg = load_classical_config(config_path)
    rung_id = "tfidf-lr"
    n_success = 0
    failures: list[str] = []
    for fold in FOLDS:
        for seed in SEEDS:
            try:
                val_df = _load_val(fold, seed, smoke_n)
                if val_df is None:
                    failures.append(f"{rung_id} fold{fold}/seed{seed}: val.parquet missing")
                    continue
                train_path = PROCESSED_ROOT / f"fold-{fold}" / f"seed-{seed}" / "train.parquet"
                train_df = pd.read_parquet(train_path)
                pipeline = build_tfidf_lr_pipeline(
                    seed=seed,
                    tfidf_cfg=cfg["tfidf"],
                    lr_cfg=cfg["logistic_regression"],
                )
                t0 = time.time()
                pipeline.fit(train_df["text"].tolist(), train_df["label"].astype(int).to_numpy())
                probs = pipeline.predict_proba(val_df["text"].tolist())
                out = pd.DataFrame(
                    {
                        "rung": rung_id,
                        "fold": fold,
                        "seed": seed,
                        "epoch": None,
                        "row_idx_in_source": val_df["row_idx_in_source"].to_numpy(),
                        "source": val_df["source"].to_numpy(),
                        "text": val_df["text"].to_numpy(),
                        "label": val_df["label"].to_numpy(),
                        "predicted_proba_class1": probs[:, 1].astype(float),
                        "contamination_state": "verified_disjoint",
                    }
                )
                out_path = output_root / f"{rung_id}__fold{fold}__seed{seed}__val.parquet"
                output_root.mkdir(parents=True, exist_ok=True)
                out.to_parquet(out_path, index=False)
                print(
                    f"[val-inference] wrote {rung_id}/fold{fold}/seed{seed}: "
                    f"{len(out)} rows in {time.time() - t0:.1f}s",
                    flush=True,
                )
                n_success += 1
            except Exception as exc:  # noqa: BLE001 — per-cell error isolation
                msg = f"{rung_id} fold{fold}/seed{seed}: {type(exc).__name__}: {exc}"
                print(f"[val-inference] FAIL {msg}", flush=True)
                failures.append(msg)
    return n_success, failures


def run_trained_val(
    rung: str,
    output_root: Path,
    smoke_n: int | None,
    max_length: int,
    batch_size: int,
    skip_existing: bool,
) -> tuple[int, list[str]]:
    """Trained transformer rung (frozen_probe or lora): load checkpoint + score val.parquet.

    Returns (n_success, failures) where failures is a list of error strings.
    """
    import torch
    from peft import PeftModel
    from torch.nn import Module
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    from src.training.load_modernbert import load_modernbert  # noqa: E402
    from src.training.train_modernbert import _predict_proba  # noqa: E402

    checkpoint_root = _REPO_ROOT / "evals" / "checkpoints" / rung
    if not checkpoint_root.exists():
        return 0, [f"{rung}: no checkpoints at {checkpoint_root}"]

    backbone_id = "answerdotai/ModernBERT-base"
    backbone_revision = "8949b909ec900327062f0ebf497f51aef5e6f0c8"
    tokenizer = AutoTokenizer.from_pretrained(backbone_id, revision=backbone_revision)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    n_success = 0
    failures: list[str] = []
    for fold in FOLDS:
        for seed in SEEDS:
            try:
                out_path = output_root / f"{rung}__fold{fold}__seed{seed}__val.parquet"
                if skip_existing and out_path.exists():
                    print(f"[val-inference] SKIP {rung}/fold{fold}/seed{seed}: exists", flush=True)
                    n_success += 1
                    continue
                val_df = _load_val(fold, seed, smoke_n)
                if val_df is None:
                    failures.append(f"{rung} fold{fold}/seed{seed}: val.parquet missing")
                    continue
                seed_dir = checkpoint_root / f"fold{fold}" / f"seed{seed}"
                ckpts = sorted(
                    seed_dir.glob("checkpoint-*"),
                    key=lambda p: int(p.name.replace("checkpoint-", "")),
                )
                if not ckpts:
                    failures.append(f"{rung} fold{fold}/seed{seed}: no checkpoints in {seed_dir}")
                    continue
                ckpt = ckpts[-1]

                if rung == "lora":
                    base = load_modernbert(revision=backbone_revision, num_labels=2)
                    model: Any = PeftModel.from_pretrained(cast(Module, base), str(ckpt))
                else:
                    model = AutoModelForSequenceClassification.from_pretrained(str(ckpt))
                model = model.to(device).eval()

                t0 = time.time()
                probs = _predict_proba(
                    model=model,
                    tokenizer=tokenizer,
                    test_df=val_df,
                    max_length=max_length,
                    per_device_batch_size=batch_size,
                )
                out = pd.DataFrame(
                    {
                        "rung": rung,
                        "fold": fold,
                        "seed": seed,
                        "epoch": 2,
                        "row_idx_in_source": val_df["row_idx_in_source"].to_numpy(),
                        "source": val_df["source"].to_numpy(),
                        "text": val_df["text"].to_numpy(),
                        "label": val_df["label"].to_numpy(),
                        "predicted_proba_class1": probs[:, 1].astype(float),
                        "contamination_state": "backbone-partial-disjoint",
                    }
                )
                out_path = output_root / f"{rung}__fold{fold}__seed{seed}__val.parquet"
                output_root.mkdir(parents=True, exist_ok=True)
                out.to_parquet(out_path, index=False)
                print(
                    f"[val-inference] wrote {rung}/fold{fold}/seed{seed}: "
                    f"{len(out)} rows in {time.time() - t0:.1f}s",
                    flush=True,
                )
                n_success += 1
                del model
                if device == "cuda":
                    torch.cuda.empty_cache()
            except Exception as exc:  # noqa: BLE001
                msg = f"{rung} fold{fold}/seed{seed}: {type(exc).__name__}: {exc}"
                print(f"[val-inference] FAIL {msg}", flush=True)
                failures.append(msg)
    return n_success, failures


def main() -> int:
    """Parse args, dispatch to selected rungs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rung",
        choices=["tfidf-lr", "frozen_probe", "lora", "all"],
        default="all",
        help="Which rung to score on val (default: all trained rungs we have checkpoints for)",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions_val",
    )
    parser.add_argument(
        "--smoke",
        type=int,
        default=None,
        help="Cap each val.parquet to N rows for fast smoke test (default: full)",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=2048,
        help="Max token length per row for transformer rungs (default 2048; full-train was 8192)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="per_device_batch_size for transformer inference (default 4; tuned for 8GB VRAM)",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip cells whose output parquet already exists (resume from interrupted run)",
    )
    args = parser.parse_args()

    args.output_root.mkdir(parents=True, exist_ok=True)
    print(f"[val-inference] output_root={args.output_root}", flush=True)

    total_success = 0
    all_failures: list[str] = []

    if args.rung in ("tfidf-lr", "all"):
        print("[val-inference] === tfidf-lr (re-fit per cell + score val) ===", flush=True)
        n, fails = run_tfidf_val(args.output_root, args.smoke)
        total_success += n
        all_failures.extend(fails)
    if args.rung in ("frozen_probe", "all"):
        print("[val-inference] === frozen_probe (load checkpoint + score val) ===", flush=True)
        n, fails = run_trained_val(
            "frozen_probe",
            args.output_root,
            args.smoke,
            max_length=args.max_length,
            batch_size=args.batch_size,
            skip_existing=args.skip_existing,
        )
        total_success += n
        all_failures.extend(fails)
    if args.rung in ("lora", "all"):
        print("[val-inference] === lora (load checkpoint + score val) ===", flush=True)
        n, fails = run_trained_val(
            "lora",
            args.output_root,
            args.smoke,
            max_length=args.max_length,
            batch_size=args.batch_size,
            skip_existing=args.skip_existing,
        )
        total_success += n
        all_failures.extend(fails)

    print(f"\n[val-inference] DONE: {total_success} cells succeeded", flush=True)
    if all_failures:
        print(f"[val-inference] {len(all_failures)} failures:", flush=True)
        for f in all_failures:
            print(f"  - {f}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
