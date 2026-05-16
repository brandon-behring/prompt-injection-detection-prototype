"""Smoke tests for src/data/splits.py — synthetic 4-positive + 2-benign verification.

Tests LODO + stratified-80/20 logic with hand-crafted positives + benigns;
no source download required, no encoder load. Pure dataframe + sklearn split
exercise.

Run via: `pytest tests/smoke/test_splits_smoke.py -v` or `make smoke`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.data.splits import (
    SEEDS,
    TRAIN_POSITIVE_SOURCES,
    VAL_FRACTION,
    SplitsConfigError,
    class_balance_per_split,
    make_splits,
    materialize_index_masks,
    materialize_splits,
)


def _synthetic_positives(rows_per_source: int = 30) -> pd.DataFrame:
    """Build a synthetic positives DataFrame with rows_per_source rows per ADR-016 source."""
    frames = []
    for src in TRAIN_POSITIVE_SOURCES:
        frames.append(
            pd.DataFrame(
                {
                    "text": [f"{src}_attack_{i}" for i in range(rows_per_source)],
                    "label": 1,
                    "source": src,
                    "row_idx_in_source": list(range(rows_per_source)),
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


def _synthetic_benigns(rows_per_source: int = 100) -> pd.DataFrame:
    """Build a synthetic benigns DataFrame with rows_per_source for lmsys + ultrachat."""
    frames = []
    for src in ("lmsys_chat_1m", "ultrachat_200k"):
        frames.append(
            pd.DataFrame(
                {
                    "text": [f"{src}_benign_{i}" for i in range(rows_per_source)],
                    "label": 0,
                    "source": src,
                    "row_idx_in_source": list(range(rows_per_source)),
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


@pytest.mark.smoke
def test_make_splits_produces_12_splits() -> None:
    """make_splits produces exactly 4 folds x 3 seeds = 12 (fold, seed) splits."""
    splits = make_splits(_synthetic_positives(), _synthetic_benigns())
    assert len(splits) == len(TRAIN_POSITIVE_SOURCES) * len(SEEDS) == 12
    # Each (fold_id, seed) pair appears exactly once.
    pairs = {(s.fold_id, s.seed) for s in splits}
    assert len(pairs) == 12


@pytest.mark.smoke
def test_make_splits_test_set_source_disjoint() -> None:
    """For each fold, the held-out source is NOT present in train or val."""
    splits = make_splits(_synthetic_positives(), _synthetic_benigns())
    for split in splits:
        train_sources = set(split.train["source"].unique())
        val_sources = set(split.val["source"].unique())
        assert (
            split.held_out_source not in train_sources
        ), f"fold {split.fold_id} test source {split.held_out_source} leaked into train"
        assert (
            split.held_out_source not in val_sources
        ), f"fold {split.fold_id} test source {split.held_out_source} leaked into val"
        # Test set contains ONLY the held-out source.
        test_sources = set(split.test["source"].unique())
        assert test_sources == {split.held_out_source}


@pytest.mark.smoke
def test_make_splits_stratified_class_balance() -> None:
    """Within each (fold, seed), train + val preserve the train-pool class ratio."""
    positives = _synthetic_positives(rows_per_source=30)  # 4 x 30 = 120 positives total
    benigns = _synthetic_benigns(rows_per_source=100)  # 2 x 100 = 200 benigns total
    splits = make_splits(positives, benigns)
    for split in splits:
        train_pool_size = len(split.train) + len(split.val)
        val_size = len(split.val)
        # 80/20 +/- 1 row for rounding.
        assert (
            abs(val_size / train_pool_size - VAL_FRACTION) < 0.02
        ), f"val fraction {val_size / train_pool_size:.3f} far from {VAL_FRACTION}"
        # Stratification — train pool minus held-out source has 90 positives + 200 benigns
        # = 290; class ratio ~ 0.31 pos. train + val each should match.
        train_pos_ratio = (split.train["label"] == 1).mean()
        val_pos_ratio = (split.val["label"] == 1).mean()
        assert abs(train_pos_ratio - val_pos_ratio) < 0.05, (
            f"train/val class ratios diverged: train={train_pos_ratio:.3f} "
            f"val={val_pos_ratio:.3f}"
        )


@pytest.mark.smoke
def test_make_splits_different_seeds_yield_different_partitions() -> None:
    """3 seeds produce distinct train/val partitions (not deterministic-same)."""
    splits = make_splits(_synthetic_positives(), _synthetic_benigns())
    # Group by fold_id and check the 3 seeds produce distinct train indices.
    by_fold: dict[int, list[set[str]]] = {}
    for split in splits:
        by_fold.setdefault(split.fold_id, []).append(set(split.train["text"]))
    for fold_id, train_sets in by_fold.items():
        assert len(train_sets) == 3
        # Pairwise comparison — at least one differs from another.
        differs = any(train_sets[i] != train_sets[j] for i in range(3) for j in range(i + 1, 3))
        assert differs, f"fold {fold_id}: 3 seeds produced identical train partitions"


@pytest.mark.smoke
def test_materialize_splits_writes_36_parquets(tmp_path: Path) -> None:
    """materialize_splits writes 36 parquet files in the locked layout."""
    splits = make_splits(_synthetic_positives(), _synthetic_benigns())
    written = materialize_splits(splits, tmp_path)
    assert len(written) == 36, f"expected 36 parquet files, got {len(written)}"
    # Locked layout: data/processed/fold-N/seed-S/{train,val,test}.parquet
    for split in splits:
        for role in ("train", "val", "test"):
            expected = tmp_path / f"fold-{split.fold_id}" / f"seed-{split.seed}" / f"{role}.parquet"
            assert expected.exists(), f"missing parquet: {expected}"
            # Round-trip: read back + verify columns.
            df = pd.read_parquet(expected)
            assert list(df.columns) == ["text", "label", "source", "row_idx_in_source"]


@pytest.mark.smoke
def test_materialize_index_masks_writes_36_npy_files(tmp_path: Path) -> None:
    """materialize_index_masks writes 36 .npy files (one per role per split)."""
    splits = make_splits(_synthetic_positives(), _synthetic_benigns())
    written = materialize_index_masks(splits, tmp_path)
    assert len(written) == 36
    for path in written:
        mask = np.load(path)
        assert mask.dtype == np.int64
        assert mask.ndim == 2
        assert mask.shape[1] == 2, f"index mask {path} should be (n, 2); got {mask.shape}"


@pytest.mark.smoke
def test_class_balance_per_split_aggregates_correctly() -> None:
    """class_balance_per_split returns dict with train/val/test totals matching split sizes."""
    splits = make_splits(_synthetic_positives(), _synthetic_benigns())
    sample = splits[0]
    balance = class_balance_per_split(sample)
    assert balance["train"]["total"] == len(sample.train)
    assert balance["val"]["total"] == len(sample.val)
    assert balance["test"]["total"] == len(sample.test)
    for role in ("train", "val", "test"):
        assert balance[role]["n_pos"] + balance[role]["n_neg"] == balance[role]["total"]


@pytest.mark.unit
def test_make_splits_rejects_missing_positive_source() -> None:
    """make_splits raises if positives_df is missing one of the locked sources."""
    positives = _synthetic_positives()
    # Drop hackaprompt.
    positives = positives[positives["source"] != "hackaprompt"]
    with pytest.raises(SplitsConfigError) as excinfo:
        make_splits(positives, _synthetic_benigns())
    assert "hackaprompt" in str(excinfo.value)


@pytest.mark.unit
def test_make_splits_rejects_mislabeled_positives() -> None:
    """make_splits raises if positives_df contains any label != 1."""
    positives = _synthetic_positives()
    positives.loc[0, "label"] = 0
    with pytest.raises(SplitsConfigError):
        make_splits(positives, _synthetic_benigns())
