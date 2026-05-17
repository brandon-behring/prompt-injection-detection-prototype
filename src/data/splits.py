"""LODO k=4 x 3 seeds x within-fold stratified 80/20 splits.

Per ADR-016 Q2 + ADR-041 Q7 (methodology) + ADR-047 (library-first refactor —
the LODO source-disjoint partition is delegated to
`eval_toolkit.splits.SourceDisjointKFoldSplitter`; project glue retains the
nested-seed loop + stratified 80/20 train/val + benigns-in-every-train-pool
discipline that is specific to this project's LODO-over-positives-only
protocol).

Public API
----------
- `make_splits(positives_df, benigns_df) -> list[FoldSeedSplit]` — produces 12
  (fold, seed) splits; each split has train + val + test DataFrames.
- `materialize_splits(splits, output_root) -> list[Path]` — writes 36 parquet
  files (4 folds x 3 seeds x 3 roles) under `data/processed/fold-N/seed-S/`.
- `materialize_index_masks(splits, output_root) -> list[Path]` — writes 36
  numpy `.npy` files capturing the source-row-index for each materialized row
  under `data/processed/index_masks/`; used by `evals/leakage_report.json` for
  reverse-trace (per ADR-041 Q7).

Per-fold structure:
- test set = ALL rows from the held-out positive source (label=1; seed-independent).
- train+val pool = 3 other positive sources (label=1) + all deduped benigns
  (label=0); stratified 80/20 random split by label per seed.

Per-rung totals (per ADR-016 Q2):
- 4 LODO folds x 3 seeds = 12 observations per rung.
- 4 trained rungs x 12 = 48 trained runs (per ADR-017).

Note: ADR-041 Q7 comment says "48 parquet files" but the layout is
4 folds x 3 seeds x 3 roles = 36 files; the 48 number conflates trained-run
count with parquet count. Implementation produces 36 files (matching the
layout structure); the math comment in ADR-041 §Q7 is a minor doc bug.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import numpy as np
import pandas as pd
from eval_toolkit.harness import EvalSlice
from eval_toolkit.splits import SourceDisjointKFoldSplitter
from numpy.typing import NDArray
from sklearn.model_selection import train_test_split

# Locked per ADR-016 Q1 — 4 train-positive sources (LODO-rotational).
TRAIN_POSITIVE_SOURCES: Final[tuple[str, ...]] = (
    "deepset_prompt_injections",
    "lakera_gandalf_ignore_instructions",
    "lakera_mosscap_prompt_injection",
    "hackaprompt",
)

# Locked per ADR-006 + ADR-016 Q2 — 3-seed floor.
SEEDS: Final[tuple[int, ...]] = (42, 43, 44)

# Locked per ADR-016 Q2 — single 80/20 train/val random split (NOT nested k-fold).
VAL_FRACTION: Final[float] = 0.20

# Per ADR-047 — fixed seed for the upstream LODO partition step; project glue
# remaps the upstream-shuffled fold order back to TRAIN_POSITIVE_SOURCES tuple
# order so fold_id-to-source mapping stays deterministic across refactors.
_LODO_PARTITION_SEED: Final[int] = 42


class SplitsConfigError(ValueError):
    """Raised when splits input violates ADR-016 contract."""


@dataclass(frozen=True, slots=True)
class FoldSeedSplit:
    """One (fold, seed) split — held-out test source + per-seed train/val partition.

    train + val are stratified 80/20 random splits of (3 train-positive sources
    + all benigns) per ADR-016 Q2; test is the held-out positive source's full
    deduped pool (seed-independent — replicated across seeds for trainer-side
    layout symmetry).
    """

    fold_id: int
    seed: int
    held_out_source: str
    train: pd.DataFrame
    val: pd.DataFrame
    test: pd.DataFrame


def _validate_inputs(positives_df: pd.DataFrame, benigns_df: pd.DataFrame) -> None:
    """Validate that positives + benigns DataFrames satisfy the ADR-016 contract."""
    required_cols = {"text", "label", "source", "row_idx_in_source"}
    for name, df in (("positives_df", positives_df), ("benigns_df", benigns_df)):
        missing = required_cols - set(df.columns)
        if missing:
            raise SplitsConfigError(
                f"{name} missing required columns: {sorted(missing)} "
                f"(per src.data.loaders.OUTPUT_COLUMNS contract)"
            )

    pos_sources = set(positives_df["source"].unique())
    expected_sources = set(TRAIN_POSITIVE_SOURCES)
    missing_sources = expected_sources - pos_sources
    if missing_sources:
        raise SplitsConfigError(
            f"positives_df missing expected ADR-016 sources: {sorted(missing_sources)}; "
            f"present: {sorted(pos_sources)}"
        )
    unexpected_sources = pos_sources - expected_sources
    if unexpected_sources:
        raise SplitsConfigError(
            f"positives_df contains non-positive sources: {sorted(unexpected_sources)}"
        )

    if (positives_df["label"] != 1).any():
        raise SplitsConfigError(
            "positives_df contains rows with label != 1 "
            f"(expected all positives); found labels {set(positives_df['label'].unique())}"
        )
    if (benigns_df["label"] != 0).any():
        raise SplitsConfigError(
            "benigns_df contains rows with label != 0 "
            f"(expected all benigns); found labels {set(benigns_df['label'].unique())}"
        )


def make_splits(positives_df: pd.DataFrame, benigns_df: pd.DataFrame) -> list[FoldSeedSplit]:
    """Build the 12 (fold, seed) LODO + stratified-80/20 splits.

    Source-disjoint LODO partition delegated to
    `eval_toolkit.splits.SourceDisjointKFoldSplitter` per ADR-047; project glue
    orders the resulting folds by `TRAIN_POSITIVE_SOURCES` tuple (preserving
    fold_id-to-source mapping), composes the per-seed stratified 80/20 train/val
    nested split, and applies the benigns-in-every-train-pool discipline that
    is specific to this project's LODO-over-positives-only protocol.

    Parameters
    ----------
    positives_df : pandas.DataFrame
        All deduped train-positive rows; must have `text`, `label=1`, `source`
        (in TRAIN_POSITIVE_SOURCES), `row_idx_in_source`.
    benigns_df : pandas.DataFrame
        All deduped benign rows (post-cross-source LMSYS-priority dedup); must
        have `text`, `label=0`, `source`, `row_idx_in_source`.

    Returns
    -------
    list[FoldSeedSplit]
        12 splits = 4 folds x 3 seeds. Ordering: fold-0/seed-42, fold-0/seed-43,
        fold-0/seed-44, fold-1/seed-42, ...

    Raises
    ------
    SplitsConfigError
        If input DataFrames violate the ADR-016 contract, or if the upstream
        splitter produces a fold whose test set contains other than exactly
        one source (would violate the LODO contract).
    """
    _validate_inputs(positives_df, benigns_df)

    # Delegate LODO source-disjoint partition to upstream per ADR-047.
    positives_slice = EvalSlice(
        name="train_positives_lodo",
        df=positives_df.reset_index(drop=True),
    )
    splitter = SourceDisjointKFoldSplitter(
        source_col="source",
        k=len(TRAIN_POSITIVE_SOURCES),
        seed=_LODO_PARTITION_SEED,
    )

    # Map upstream's shuffled fold order back to TRAIN_POSITIVE_SOURCES tuple
    # order so fold_id-to-source mapping stays deterministic across refactors.
    # Each fold's test set must contain exactly one source per the LODO contract.
    fold_by_source: dict[str, dict[str, EvalSlice]] = {}
    for fold_dict in splitter.iter_folds(positives_slice):
        test_sources = fold_dict["test"].df["source"].unique()
        if len(test_sources) != 1:
            raise SplitsConfigError(
                f"upstream SourceDisjointKFoldSplitter produced fold with "
                f"{len(test_sources)} test sources; expected exactly 1 per "
                f"LODO contract (per ADR-016 Q2). Sources: "
                f"{sorted(test_sources.tolist())}"
            )
        fold_by_source[str(test_sources[0])] = fold_dict

    splits: list[FoldSeedSplit] = []
    for fold_id, held_out in enumerate(TRAIN_POSITIVE_SOURCES):
        fold_dict = fold_by_source[held_out]
        test_df = fold_dict["test"].df.reset_index(drop=True)
        train_pool_pos = fold_dict["train"].df  # 3 other positive sources
        train_pool = pd.concat([train_pool_pos, benigns_df], ignore_index=True)

        for seed in SEEDS:
            train_df, val_df = train_test_split(
                train_pool,
                test_size=VAL_FRACTION,
                stratify=train_pool["label"],
                random_state=seed,
            )
            splits.append(
                FoldSeedSplit(
                    fold_id=fold_id,
                    seed=seed,
                    held_out_source=held_out,
                    train=train_df.reset_index(drop=True),
                    val=val_df.reset_index(drop=True),
                    test=test_df.copy(),
                )
            )
    return splits


def apply_leakage_cleanup(
    splits: list[FoldSeedSplit], *, threshold: float = 0.85
) -> tuple[list[FoldSeedSplit], list[dict[str, Any]]]:
    """Per ADR-043 — drop train+val rows that exact-match or cosine-near-match test.

    Re-builds each FoldSeedSplit with cleaned train + val. Test stays intact.
    Returns the cleaned splits + per-split drop-count records for audit.
    """
    from src.data.dedup import drop_train_test_leakage

    cleaned_splits: list[FoldSeedSplit] = []
    cleanup_records: list[dict[str, Any]] = []
    for split in splits:
        combined = pd.concat([split.train, split.val], ignore_index=False)
        cleaned_combined, dropped = drop_train_test_leakage(
            combined, split.test, threshold=threshold
        )
        # Re-partition train + val from cleaned_combined preserving original 80/20 ratio.
        if len(cleaned_combined) == 0:
            cleaned_train = cleaned_combined
            cleaned_val = cleaned_combined
        else:
            train_target = max(int(len(cleaned_combined) * (1 - VAL_FRACTION)), 1)
            cleaned_train = cleaned_combined.iloc[:train_target].reset_index(drop=True)
            cleaned_val = cleaned_combined.iloc[train_target:].reset_index(drop=True)
        cleaned_splits.append(
            FoldSeedSplit(
                fold_id=split.fold_id,
                seed=split.seed,
                held_out_source=split.held_out_source,
                train=cleaned_train,
                val=cleaned_val,
                test=split.test.copy(),
            )
        )
        cleanup_records.append(
            {
                "fold_id": split.fold_id,
                "seed": split.seed,
                "n_dropped": len(dropped),
                "n_exact_hash_leaks": sum(1 for d in dropped if d["reason"] == "exact-hash-leak"),
                "n_cosine_leaks": sum(1 for d in dropped if d["reason"] == "cosine-leak"),
            }
        )
    return cleaned_splits, cleanup_records


def materialize_splits(splits: list[FoldSeedSplit], output_root: Path) -> list[Path]:
    """Write 36 parquet files (12 splits x 3 roles) under output_root.

    Layout: `output_root/fold-{N}/seed-{S}/{train,val,test}.parquet`.
    Each parquet carries columns `(text, label, source, row_idx_in_source)`.

    Returns the list of written paths in deterministic order.
    """
    written: list[Path] = []
    for split in splits:
        base = output_root / f"fold-{split.fold_id}" / f"seed-{split.seed}"
        base.mkdir(parents=True, exist_ok=True)
        for role, df in (("train", split.train), ("val", split.val), ("test", split.test)):
            path = base / f"{role}.parquet"
            df.to_parquet(path, index=False)
            written.append(path)
    return written


def materialize_index_masks(splits: list[FoldSeedSplit], output_root: Path) -> list[Path]:
    """Write per-(fold, seed, role) index masks under output_root/index_masks/.

    Each .npy file contains a 2-column int64 array of shape (n_rows, 2) — column
    0 = original row index in the (positives_df concat benigns_df) input;
    column 1 = `row_idx_in_source` from the loader output. Used by
    evals/leakage_report.json for reverse-trace to source rows (per ADR-041 Q7).
    """
    mask_dir = output_root / "index_masks"
    mask_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for split in splits:
        for role, df in (("train", split.train), ("val", split.val), ("test", split.test)):
            mask: NDArray[np.int64] = np.column_stack(
                [
                    np.arange(len(df), dtype=np.int64),
                    df["row_idx_in_source"].to_numpy(dtype=np.int64),
                ]
            )
            path = mask_dir / f"fold-{split.fold_id}__seed-{split.seed}__{role}.npy"
            np.save(path, mask)
            written.append(path)
    return written


def class_balance_per_split(split: FoldSeedSplit) -> dict[str, dict[str, int]]:
    """Return per-role class-balance counts for a (fold, seed) split.

    Returns: `{"train": {"n_pos": ..., "n_neg": ..., "total": ...}, "val": {...}, "test": {...}}`.
    Used by `evals/data_audit.json` (Commit 5) and the
    `test_class_balance_per_fold` invariant.
    """
    out: dict[str, dict[str, int]] = {}
    for role, df in (("train", split.train), ("val", split.val), ("test", split.test)):
        n_pos = int((df["label"] == 1).sum())
        n_neg = int((df["label"] == 0).sum())
        out[role] = {"n_pos": n_pos, "n_neg": n_neg, "total": n_pos + n_neg}
    return out
