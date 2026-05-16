"""Classical-floor (TF-IDF + LR) trainer per ADR-017 + ADR-044 Q5.

Trainer for the sklearn-stack classical floor rung. Reads YAML config, fits
the locked pipeline per (fold, seed), persists per-row predictions to
``evals/predictions/tfidf-lr__fold<F>__seed<S>.parquet``. Per ADR-017 line 60,
no epoch suffix since classical floor has no epoch concept.

Public API
----------
- ``load_config(config_path)`` -> dict — parses + validates a rung YAML.
- ``train_one_cell(config_path, fold, seed, processed_root, predictions_root)``
  -> Path — trains one (fold, seed) cell; returns the written parquet path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pandas as pd
import yaml

from src.training.tfidf_lr import build_tfidf_lr_pipeline

PREDICTIONS_SCHEMA: tuple[str, ...] = (
    "rung",
    "fold",
    "seed",
    "row_idx_in_source",
    "source",
    "text",
    "label",
    "predicted_proba_class1",
)


def load_config(config_path: Path) -> dict[str, Any]:
    """Load and validate a rung YAML config for the classical floor.

    Parameters
    ----------
    config_path : Path
        Path to ``configs/rungs/classical_floor.yaml`` (or test fixture).

    Returns
    -------
    dict
        Parsed YAML.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    ValueError
        If ``classifier_type != "classical"`` (wrong YAML for this trainer).
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Rung config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    if cfg.get("classifier_type") != "classical":
        raise ValueError(
            f"{config_path}: classifier_type must be 'classical' for classical-floor "
            f"trainer; got {cfg.get('classifier_type')!r}"
        )
    return cast(dict[str, Any], cfg)


def train_one_cell(
    *,
    config_path: Path,
    fold: int,
    seed: int,
    processed_root: Path,
    predictions_root: Path,
) -> Path:
    """Train one (fold, seed) cell of the classical floor; write predictions parquet.

    Parameters
    ----------
    config_path : Path
        Path to ``configs/rungs/classical_floor.yaml``.
    fold : int
        LODO fold index (0-3 per ADR-016).
    seed : int
        One of ``(42, 43, 44)`` per ADR-044 Q1.
    processed_root : Path
        Path to ``data/processed/`` (contains
        ``fold-<F>/seed-<S>/{train,val,test}.parquet`` from Phase 1).
    predictions_root : Path
        Path to ``evals/predictions/`` (parquet files written here).

    Returns
    -------
    Path
        Absolute path to the written predictions parquet.

    Raises
    ------
    FileNotFoundError
        If the fold/seed parquets do not exist.
    """
    cfg = load_config(config_path)
    seed_dir = processed_root / f"fold-{fold}" / f"seed-{seed}"
    train_path = seed_dir / "train.parquet"
    test_path = seed_dir / "test.parquet"
    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError(f"Phase 1 splits missing for fold={fold} seed={seed} at {seed_dir}")

    train_df = pd.read_parquet(train_path)
    test_df = pd.read_parquet(test_path)

    pipeline = build_tfidf_lr_pipeline(
        seed=seed,
        tfidf_cfg=cfg["tfidf"],
        lr_cfg=cfg["logistic_regression"],
    )
    pipeline.fit(train_df["text"], train_df["label"])
    probs = pipeline.predict_proba(test_df["text"])

    predictions = pd.DataFrame(
        {
            "rung": "tfidf-lr",
            "fold": fold,
            "seed": seed,
            "row_idx_in_source": test_df["row_idx_in_source"].to_numpy(),
            "source": test_df["source"].to_numpy(),
            "text": test_df["text"].to_numpy(),
            "label": test_df["label"].to_numpy(),
            "predicted_proba_class1": probs[:, 1],
        }
    )

    predictions_root.mkdir(parents=True, exist_ok=True)
    file_template: str = cfg["predictions_file_template"]
    out_path = predictions_root / file_template.format(fold=fold, seed=seed)
    predictions.to_parquet(out_path, index=False)
    return out_path
