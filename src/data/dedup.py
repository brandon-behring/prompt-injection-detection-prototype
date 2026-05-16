"""MiniLM-L6-v2 cosine dedup at threshold 0.80 (per ADR-016 Q4 + ADR-041 Q5).

Public API
----------
- `compute_embeddings(texts) -> np.ndarray` — encode + L2-normalize via MiniLM-L6-v2.
- `pairwise_cosines(a, b, block_size) -> np.ndarray` — block-wise cosine for memory safety.
- `dedup_within_source(df, threshold) -> (kept_df, dropped_pairs)` — label-aware
  per-(source, label) cell; deterministic first-occurrence retention.
- `dedup_cross_source_benigns(dfs, priority_source, threshold)
  -> (kept_df, dropped_pair_records)` — cross-source benign pass with LMSYS-priority
  tiebreak per ADR-016 Q5.
- `encoder_revision_sha() -> str` — HF SHA of the loaded encoder; persisted to
  `evals/dedup_calibration.json` for provenance.

Threshold + encoder are module constants — not configurable (per ADR-016 Q4 lock).
Bumping either requires a superseding ADR (per ADR-036 bump-trigger policy).

The dedup pipeline is greedy + first-occurrence by row index; matches the
SPEC_GREENFIELD deterministic-ordering lock. Memory profile: block-wise cosine
keeps peak RAM under approximately block_size x N x 4 bytes (default block_size
1024 gives <100MB peak for the 20K-row LMSYS plus UltraChat cross-source pass).
"""

from __future__ import annotations

from typing import Any, Final

import numpy as np
import pandas as pd
from huggingface_hub import HfApi
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

# Locked constants per ADR-016 Q4.
MINI_LM_MODEL: Final[str] = "sentence-transformers/all-MiniLM-L6-v2"
THRESHOLD: Final[float] = 0.80
LMSYS_PRIORITY_SOURCE: Final[str] = "lmsys_chat_1m"

# Cross-source contamination scan threshold (per ADR-016 audit trigger A-005;
# cosine >=0.85 flagged as injection-template-match in contamination_scan.json).
CONTAMINATION_THRESHOLD: Final[float] = 0.85

# Module-level encoder cache — single load per process.
_encoder: SentenceTransformer | None = None
_encoder_sha: str | None = None


class DedupConfigError(ValueError):
    """Raised when dedup input violates the locked-config contract."""


def get_encoder() -> SentenceTransformer:
    """Return the singleton SentenceTransformer instance (load-once-per-process)."""
    global _encoder
    if _encoder is None:
        _encoder = SentenceTransformer(MINI_LM_MODEL)
    return _encoder


def encoder_revision_sha() -> str:
    """Return the HF revision SHA of the loaded MiniLM-L6-v2 model.

    Persisted to `evals/dedup_calibration.json` for provenance. Falls back to
    the model card path when HfApi access fails (e.g., offline).
    """
    global _encoder_sha
    if _encoder_sha is not None:
        return _encoder_sha
    try:
        api = HfApi()
        info = api.model_info(repo_id=MINI_LM_MODEL)
        sha = info.sha
        if isinstance(sha, str):
            _encoder_sha = sha
            return _encoder_sha
    except Exception:  # noqa: BLE001
        pass
    _encoder_sha = "unknown-offline"
    return _encoder_sha


def compute_embeddings(texts: list[str], *, batch_size: int = 64) -> NDArray[np.float32]:
    """Encode `texts` and L2-normalize each row vector.

    Parameters
    ----------
    texts : list[str]
        Texts to embed; length N.
    batch_size : int, optional
        Encoder batch size (default 64).

    Returns
    -------
    numpy.ndarray
        Shape (N, 384) float32 array; each row L2-normalized.
    """
    if not texts:
        return np.empty((0, 384), dtype=np.float32)
    enc = get_encoder()
    arr = enc.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    return np.asarray(arr, dtype=np.float32)


def pairwise_cosines(
    a: NDArray[np.float32], b: NDArray[np.float32], *, block_size: int = 1024
) -> NDArray[np.float32]:
    """Block-wise cosine matrix between L2-normalized embedding arrays.

    Assumes inputs are L2-normalized (output is the dot product).

    Parameters
    ----------
    a : numpy.ndarray
        Shape (n_a, d) L2-normalized.
    b : numpy.ndarray
        Shape (n_b, d) L2-normalized.
    block_size : int, optional
        Row-block size for memory-bounded compute (default 1024).

    Returns
    -------
    numpy.ndarray
        Shape (n_a, n_b) float32; symmetric when a == b.
    """
    n_a, n_b = a.shape[0], b.shape[0]
    out = np.empty((n_a, n_b), dtype=np.float32)
    for i in range(0, n_a, block_size):
        out[i : i + block_size] = a[i : i + block_size] @ b.T
    return out


def _greedy_first_occurrence_mask(
    emb: NDArray[np.float32], *, threshold: float, block_size: int = 1024
) -> tuple[NDArray[Any], list[tuple[int, int]]]:
    """Return boolean keep-mask + dropped-pair list via greedy first-occurrence dedup.

    For each row i (in order), drop any row j > i with cos(i, j) >= threshold.
    Block-wise scan keeps memory bounded; runtime is O(N^2) in N.

    Returns
    -------
    keep : numpy.ndarray
        Boolean array of shape (N,); True means row is kept.
    dropped : list[tuple[int, int]]
        List of (kept_idx, dropped_idx) tuples for audit trail.
    """
    n = emb.shape[0]
    keep = np.ones(n, dtype=bool)
    dropped: list[tuple[int, int]] = []
    for i in range(n):
        if not keep[i]:
            continue
        j_start = i + 1
        if j_start >= n:
            break
        for bstart in range(j_start, n, block_size):
            bend = min(bstart + block_size, n)
            sims = emb[i] @ emb[bstart:bend].T
            for offset, sim in enumerate(sims):
                j = bstart + offset
                if not keep[j]:
                    continue
                if sim >= threshold:
                    keep[j] = False
                    dropped.append((i, j))
    return keep, dropped


def dedup_within_source(
    df: pd.DataFrame, *, threshold: float = THRESHOLD
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Label-aware within-(source, label) dedup with deterministic first-occurrence.

    Per ADR-016 Q4 — dedup is performed within each (source, label) cell so that
    a benign-positive minimal pair (semantically near, label-disjoint) is never
    collapsed. Within a cell, greedy first-occurrence retention (lower row-idx wins).

    Parameters
    ----------
    df : pandas.DataFrame
        Input rows with at least columns `text`, `source`, `label`.
    threshold : float, optional
        Cosine threshold (default 0.80 = ADR-016 Q4 lock).

    Returns
    -------
    kept_df : pandas.DataFrame
        Deduped rows; index reset.
    dropped_records : list[dict]
        One record per dropped pair: `{cell_source, cell_label, kept_row, dropped_row}`.
    """
    if {"text", "source", "label"} - set(df.columns):
        raise DedupConfigError(
            f"dedup_within_source requires columns text+source+label; got {list(df.columns)}"
        )
    embeddings = compute_embeddings(df["text"].astype(str).tolist())

    keep_global = np.ones(len(df), dtype=bool)
    dropped_records: list[dict[str, Any]] = []
    grouped = df.groupby(["source", "label"], sort=False)
    for group_key, cell_df in grouped:
        src, label = group_key
        cell_idx = cell_df.index.to_numpy()
        if len(cell_idx) < 2:
            continue
        cell_emb = embeddings[cell_idx]
        keep_cell, cell_pairs = _greedy_first_occurrence_mask(cell_emb, threshold=threshold)
        for kept_i, dropped_j in cell_pairs:
            keep_global[cell_idx[dropped_j]] = False
            dropped_records.append(
                {
                    "cell_source": str(src),
                    "cell_label": int(label),  # type: ignore[call-overload]
                    "kept_row": int(cell_idx[kept_i]),
                    "dropped_row": int(cell_idx[dropped_j]),
                }
            )
        # Propagate keep_cell into global mask too (redundant safety).
        keep_global[cell_idx] &= keep_cell

    kept_df = df[keep_global].reset_index(drop=True)
    return kept_df, dropped_records


def drop_train_test_leakage(
    train_val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    *,
    threshold: float = 0.85,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Drop train+val rows that exact-match or cosine-near-match any test row.

    Per ADR-016 Q3 hard-locked leakage invariant — no exact-hash and no high-cosine
    train-test overlap. ADR-016 Q5 specified cross-source dedup for benigns only;
    cross-source positive near-paraphrases leak across LODO folds (a near-paraphrase
    of a held-out-source row in another source's train data effectively gives the
    model a "seen it before" advantage). This function operates post-split: for
    each (fold, seed) split, scan train+val vs test; drop the TRAIN-SIDE row of any
    overlapping pair. Test set stays intact (it's the held-out source's full pool).

    Per ADR-043 — this is the canonical leakage cleanup applied after make_splits +
    before materialize_splits. The threshold (0.85) matches the leakage scan threshold
    in compute_leakage_report.

    Parameters
    ----------
    train_val_df : pandas.DataFrame
        Combined train + val pool for one (fold, seed) split.
    test_df : pandas.DataFrame
        Test set for the same fold (seed-independent).
    threshold : float, optional
        Cosine threshold for near-paraphrase leakage (default 0.85 per ADR-016 Q3).

    Returns
    -------
    cleaned_train_val : pandas.DataFrame
        train_val_df with leaked rows dropped; index reset.
    dropped_records : list[dict]
        Per-pair drop record `{train_idx, train_text, test_idx, test_text, cosine, reason}`.
    """
    if {"text"} - set(train_val_df.columns) or {"text"} - set(test_df.columns):
        raise DedupConfigError(
            f"drop_train_test_leakage requires text column; "
            f"train_val cols={list(train_val_df.columns)} test cols={list(test_df.columns)}"
        )
    if len(train_val_df) == 0 or len(test_df) == 0:
        return train_val_df.reset_index(drop=True), []

    # Exact-hash overlaps.
    test_text_set = set(test_df["text"].astype(str))
    train_val_texts = train_val_df["text"].astype(str)
    exact_overlap_mask = train_val_texts.isin(test_text_set)
    dropped: list[dict[str, Any]] = []
    for idx in train_val_df.index[exact_overlap_mask]:
        dropped.append(
            {
                "train_idx": int(idx),
                "train_text": str(train_val_texts.loc[idx])[:120],
                "test_idx": -1,
                "test_text": "(exact-hash overlap; one of multiple test rows)",
                "cosine": 1.0,
                "reason": "exact-hash-leak",
            }
        )

    # Cosine overlaps (excluding rows already flagged exact).
    keep_mask = ~exact_overlap_mask
    candidate_train_val = train_val_df[keep_mask]
    if len(candidate_train_val) > 0:
        train_val_emb = compute_embeddings(candidate_train_val["text"].astype(str).tolist())
        test_emb = compute_embeddings(test_df["text"].astype(str).tolist())
        # For each candidate train_val row, find max cosine to ANY test row.
        BLOCK = 256
        cosine_drop_indices: list[int] = []
        for bstart in range(0, len(candidate_train_val), BLOCK):
            block_emb = train_val_emb[bstart : bstart + BLOCK]
            sims = block_emb @ test_emb.T  # shape (block_len, n_test)
            max_per_row = sims.max(axis=1)
            argmax_test = sims.argmax(axis=1)
            for row_offset, (max_sim, test_argmax) in enumerate(zip(max_per_row, argmax_test)):
                if max_sim >= threshold:
                    abs_idx = candidate_train_val.index[bstart + row_offset]
                    cosine_drop_indices.append(int(abs_idx))
                    dropped.append(
                        {
                            "train_idx": int(abs_idx),
                            "train_text": str(train_val_texts.loc[abs_idx])[:120],
                            "test_idx": int(test_df.index[int(test_argmax)]),
                            "test_text": str(test_df["text"].iloc[int(test_argmax)])[:120],
                            "cosine": float(max_sim),
                            "reason": "cosine-leak",
                        }
                    )
        keep_mask.loc[cosine_drop_indices] = False

    cleaned = train_val_df[keep_mask].reset_index(drop=True)
    return cleaned, dropped


def dedup_cross_source_benigns(
    dfs: dict[str, pd.DataFrame],
    *,
    threshold: float = THRESHOLD,
    priority_source: str = LMSYS_PRIORITY_SOURCE,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Cross-source benign dedup with priority-source tiebreak.

    Per ADR-016 Q5 — after within-source dedup, LMSYS-Chat-1M (real-user) and
    UltraChat (synthetic) are concatenated and cross-source-deduped. When a
    near-duplicate pair crosses sources, the row from `priority_source` wins
    (real-data signal preserved over synthetic). Within same-source pairs that
    survived within-source dedup pass (none should), first-occurrence applies.

    Parameters
    ----------
    dfs : dict[str, pandas.DataFrame]
        Per-source benign DataFrames keyed by source name.
    threshold : float, optional
        Cosine threshold (default 0.80).
    priority_source : str, optional
        Source name whose rows win cross-source tiebreaks (default "lmsys_chat_1m").

    Returns
    -------
    kept_df : pandas.DataFrame
        Concatenated + deduped benigns; index reset.
    dropped_records : list[dict]
        Per-pair audit: `{kept_source, kept_row, dropped_source, dropped_row, cosine, reason}`.
    """
    if not dfs:
        raise DedupConfigError("dedup_cross_source_benigns called with empty dfs")
    if priority_source not in dfs:
        raise DedupConfigError(
            f"priority_source {priority_source!r} not in dfs keys {sorted(dfs.keys())}"
        )

    # Place priority-source rows FIRST so first-occurrence tiebreak naturally favors them.
    ordered_keys = [priority_source] + [k for k in dfs.keys() if k != priority_source]
    concat = pd.concat([dfs[k] for k in ordered_keys], ignore_index=True)

    embeddings = compute_embeddings(concat["text"].astype(str).tolist())
    n = len(concat)
    keep = np.ones(n, dtype=bool)
    dropped_records: list[dict[str, Any]] = []

    BLOCK = 1024
    sources = concat["source"].to_numpy()
    for i in range(n):
        if not keep[i]:
            continue
        for bstart in range(i + 1, n, BLOCK):
            bend = min(bstart + BLOCK, n)
            sims = embeddings[i] @ embeddings[bstart:bend].T
            for offset, sim in enumerate(sims):
                j = bstart + offset
                if not keep[j] or sim < threshold:
                    continue
                # i appears first in concat (because priority sources are first);
                # under the priority-first ordering, dropping j naturally implements
                # the LMSYS-priority rule.
                keep[j] = False
                src_i = sources[i]
                src_j = sources[j]
                if src_i == priority_source and src_j != priority_source:
                    reason = f"priority-source-{priority_source}"
                elif src_i == src_j:
                    reason = "same-source-first-occurrence"
                else:
                    reason = "first-occurrence-tiebreak"
                dropped_records.append(
                    {
                        "kept_source": str(src_i),
                        "kept_row": int(i),
                        "dropped_source": str(src_j),
                        "dropped_row": int(j),
                        "cosine": float(sim),
                        "reason": reason,
                    }
                )

    kept_df = concat[keep].reset_index(drop=True)
    return kept_df, dropped_records
