"""Phase 1 audit + leakage + contamination scans.

Per ADR-016 §A-005 + ADR-041 Q6 (methodology) + ADR-047 (library-first refactor —
leakage detection delegated to `eval_toolkit.leakage.run_leakage_checks` with
`CrossSplitLeakageCheck`; per-row max-cosine contamination scan delegated to
`eval_toolkit.text_dedup.EmbeddingCosineStrategy.pairs_across`; project glue
preserves the per-fold-seed iteration + project-dict output schemas).

Public API
----------
- `compute_data_audit(positives_raw, positives_dedup, benigns_dedup, splits)` -> dict
- `compute_leakage_report(splits)` -> dict — exact-hash + cosine >=0.85 train/val vs test overlap
- `compute_contamination_scan(benigns, ood_dfs, slate_df, templates_df)` -> dict — per-row max
  cosine to (slate + templates) reference corpus per ADR-041 Q6 + A-006

Outputs are JSON-serializable dicts; orchestration script writes to:
- evals/data_audit.json
- evals/leakage_report.json
- evals/contamination_scan.json

Thresholds:
- Contamination flag — cosine >= 0.85 per ADR-016 §A-005 audit trigger 1.
- Leakage cosine flag — cosine >= 0.85 per ADR-016 §Q3 hard-locked leakage invariant.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from eval_toolkit.harness import EvalSlice
from eval_toolkit.leakage import CrossSplitLeakageCheck, run_leakage_checks
from eval_toolkit.text_dedup import EmbeddingCosineStrategy
from numpy.typing import NDArray

from src.data.dedup import (
    CONTAMINATION_THRESHOLD,
    compute_embeddings,
)
from src.data.splits import FoldSeedSplit, class_balance_per_split

# Per ADR-016 §A-005 audit trigger 2: per-LODO-fold positive:negative ratio must fall
# in [1:10, 1:3]; outside this range a superseding ADR adjusts subsample ceilings.
CLASS_BALANCE_MIN_NEG_PER_POS = 3
CLASS_BALANCE_MAX_NEG_PER_POS = 10

# Per ADR-016 §A-005 audit trigger 1: ≤2 percent of either LMSYS or UltraChat may be
# flagged as injection-template-match (MiniLM cosine >= 0.85). Above 2 percent fires
# the superseding ADR requirement.
BENIGN_CONTAMINATION_THRESHOLD_PCT = 2.0


def _length_distribution(texts: "pd.Series[Any]") -> dict[str, int | float]:
    """Return per-text-length distribution stats (chars + word count).

    Returns all-zero stats if texts is empty (guards against the empty-source
    edge case where a normalizer returned 0 rows; downstream audit still emits
    a row for the source so the empty-source signal is visible in the JSON).
    """
    if len(texts) == 0:
        return {
            "char_p50": 0,
            "char_p95": 0,
            "char_max": 0,
            "word_p50": 0,
            "word_p95": 0,
            "word_max": 0,
        }
    char_lens = texts.astype(str).str.len()
    word_counts = texts.astype(str).str.split().str.len()
    return {
        "char_p50": int(char_lens.quantile(0.50)),
        "char_p95": int(char_lens.quantile(0.95)),
        "char_max": int(char_lens.max()),
        "word_p50": int(word_counts.quantile(0.50)),
        "word_p95": int(word_counts.quantile(0.95)),
        "word_max": int(word_counts.max()),
    }


def compute_data_audit(
    positives_raw_per_source: dict[str, pd.DataFrame],
    positives_dedup: pd.DataFrame,
    benigns_raw_per_source: dict[str, pd.DataFrame],
    benigns_dedup: pd.DataFrame,
    splits: list[FoldSeedSplit],
) -> dict[str, Any]:
    """Per-source counts + per-fold class balance + per-source length stats.

    Operationalizes ADR-016 §A-005 audit trigger 2 (class-balance) + trigger 4
    (length-distribution) at Phase 1 entry.
    """
    per_source: dict[str, dict[str, Any]] = {}
    for src, raw_df in positives_raw_per_source.items():
        dedup_df = positives_dedup[positives_dedup["source"] == src]
        per_source[src] = {
            "role": "train_positive",
            "raw_n": int(len(raw_df)),
            "post_dedup_n": int(len(dedup_df)),
            "n_dropped_dedup": int(len(raw_df) - len(dedup_df)),
            "length_distribution": _length_distribution(dedup_df["text"]),
        }
    for src, raw_df in benigns_raw_per_source.items():
        dedup_df = benigns_dedup[benigns_dedup["source"] == src]
        per_source[src] = {
            "role": "train_benign",
            "raw_n": int(len(raw_df)),
            "post_dedup_n": int(len(dedup_df)),
            "n_dropped_dedup": int(len(raw_df) - len(dedup_df)),
            "length_distribution": _length_distribution(dedup_df["text"]),
        }

    per_fold_class_balance: list[dict[str, Any]] = []
    triggers_fired: list[dict[str, Any]] = []
    for split in splits:
        bal = class_balance_per_split(split)
        # Class balance per training pool (train + val).
        train_pool_pos = bal["train"]["n_pos"] + bal["val"]["n_pos"]
        train_pool_neg = bal["train"]["n_neg"] + bal["val"]["n_neg"]
        neg_per_pos = train_pool_neg / max(train_pool_pos, 1)
        in_range = CLASS_BALANCE_MIN_NEG_PER_POS <= neg_per_pos <= CLASS_BALANCE_MAX_NEG_PER_POS
        record = {
            "fold_id": split.fold_id,
            "seed": split.seed,
            "held_out_source": split.held_out_source,
            "train_pool_n_pos": train_pool_pos,
            "train_pool_n_neg": train_pool_neg,
            "neg_per_pos": round(neg_per_pos, 3),
            "in_adr_016_range": bool(in_range),
            "test_n_pos": bal["test"]["n_pos"],
            "test_n_neg": bal["test"]["n_neg"],
        }
        per_fold_class_balance.append(record)
        if not in_range:
            triggers_fired.append(
                {
                    "trigger": "A-005 trigger 2 (class-balance)",
                    "fold_id": split.fold_id,
                    "seed": split.seed,
                    "neg_per_pos": neg_per_pos,
                    "expected_range_inclusive": [
                        CLASS_BALANCE_MIN_NEG_PER_POS,
                        CLASS_BALANCE_MAX_NEG_PER_POS,
                    ],
                }
            )

    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "adr_ref": "ADR-016 + ADR-041 + A-005 audit triggers 2 + 4",
        "per_source_counts_and_length": per_source,
        "per_fold_class_balance": per_fold_class_balance,
        "a_005_triggers_fired": triggers_fired,
        "a_005_class_balance_clean": len(triggers_fired) == 0,
    }


def _embedding_strategy() -> EmbeddingCosineStrategy:
    """Build EmbeddingCosineStrategy bound to the project-owned embedder per ADR-047."""
    return EmbeddingCosineStrategy(embedder=compute_embeddings)


def compute_leakage_report(splits: list[FoldSeedSplit]) -> dict[str, Any]:
    """Exact-hash + cosine >=0.85 train+val vs test overlap per (fold, seed).

    Per ADR-016 §Q3 hard-locked leakage invariant — zero overlap expected.

    Per ADR-047 Commit 4 — cosine layer delegated to
    `eval_toolkit.leakage.CrossSplitLeakageCheck` (via `run_leakage_checks`),
    which wraps `eval_toolkit.text_dedup.cross_dedup` at the project-owned
    embedder strategy. Exact-hash layer preserved as project-specific
    set-intersection (per ADR-016 §Q3 the layers are conceptually distinct
    and the project-dict output schema separates their counts).

    Note: ADR-047 acceptance criterion specified
    `run_leakage_checks([ExactDuplicateCheck, NearDuplicateCheck,
    CrossSplitLeakageCheck], splits)`. Implementation uses only
    `CrossSplitLeakageCheck` since ExactDuplicateCheck + NearDuplicateCheck
    operate within-split and would always report zero findings post-
    `dedup_within_source` (which runs upstream in the data pipeline per ADR-041
    Q7). The ADR's library-first intent is preserved.
    """
    strategy = _embedding_strategy()
    leakage_check = CrossSplitLeakageCheck(
        train_split="train_val",
        eval_splits=["test"],
        threshold=0.85,
        strategy=strategy,
    )

    per_fold: list[dict[str, Any]] = []
    total_exact = 0
    total_cosine = 0
    for split in splits:
        train_val_texts = pd.concat([split.train["text"], split.val["text"]], ignore_index=True)
        test_texts = split.test["text"]

        # Exact-hash layer — project-specific set intersection per ADR-016 §Q3.
        train_val_set = set(train_val_texts.astype(str))
        test_set = set(test_texts.astype(str))
        exact_overlaps = train_val_set & test_set

        # Cosine layer — upstream CrossSplitLeakageCheck (project glue assembles
        # the per-fold splits dict + extracts the test-side drop count from
        # the LeakageFinding).
        cosine_overlaps = 0
        if len(test_texts) > 0 and len(train_val_texts) > 0:
            train_val_slice = EvalSlice(
                name="train_val",
                df=pd.DataFrame(
                    {"text": train_val_texts.astype(str), "label": [0] * len(train_val_texts)}
                ),
            )
            test_slice = EvalSlice(
                name="test",
                df=pd.DataFrame({"text": test_texts.astype(str), "label": [0] * len(test_texts)}),
            )
            # Per v1.0.6 eval-toolkit bump v0.34→v0.39: cast() workaround
            # removed. Upstream eval-toolkit#40 (resolved 2026-05-18) relaxed
            # LeakageCheck.name from settable-attr to @property; frozen-
            # dataclass CrossSplitLeakageCheck is now mypy-strict-compatible
            # via structural match (@runtime_checkable Protocol).
            report = run_leakage_checks(
                [leakage_check],
                {"train_val": train_val_slice, "test": test_slice},
            )
            test_drop_indices = (report.findings[0].drop_indices or {}).get("test", [])
            cosine_overlaps = len(test_drop_indices)

        per_fold.append(
            {
                "fold_id": split.fold_id,
                "seed": split.seed,
                "held_out_source": split.held_out_source,
                "n_train_val": int(len(train_val_texts)),
                "n_test": int(len(test_texts)),
                "exact_hash_overlaps": len(exact_overlaps),
                "cosine_ge_085_overlaps": cosine_overlaps,
            }
        )
        total_exact += len(exact_overlaps)
        total_cosine += cosine_overlaps

    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "adr_ref": "ADR-016 Q3 hard-locked leakage invariant",
        "cosine_threshold": 0.85,
        "per_fold_seed": per_fold,
        "total_exact_hash_overlaps": total_exact,
        "total_cosine_overlaps": total_cosine,
        "leakage_clean": total_exact == 0 and total_cosine == 0,
    }


def compute_contamination_scan(
    benigns_df: pd.DataFrame,
    ood_dfs: dict[str, pd.DataFrame],
    slate_df: pd.DataFrame,
    templates_df: pd.DataFrame,
) -> dict[str, Any]:
    """Per-row max cosine to (slate + templates) reference corpus per ADR-041 Q6.

    For each benign + OOD row, compute the max cosine to ANY row in the reference
    corpus. Flag rows with max cosine >= CONTAMINATION_THRESHOLD (0.85). Operationalizes
    ADR-016 §A-005 audit trigger 1 (benign contamination) + assumption A-006
    (eval-data contamination with public training-data mirrors; per ADR-041 Q6
    interpreted operationally as slate + ~200 extracted HackAPrompt templates).

    Per ADR-047 Commit 4 — max-cosine machinery delegated to
    `eval_toolkit.text_dedup.EmbeddingCosineStrategy.pairs_across(k=1)`; project
    glue handles per-source aggregation + percentile stats + A-005 trigger
    evaluation + output dict schema.
    """
    strategy = _embedding_strategy()
    ref_texts = (
        pd.concat([slate_df["text"], templates_df["text"]], ignore_index=True).astype(str).tolist()
    )
    print(f"[contamination_scan] embedding {len(ref_texts)} reference rows...")

    def _scan_one(source_texts: list[str]) -> NDArray[np.float32]:
        """Per-row top-1 cosine to reference corpus via upstream pairs_across."""
        sims, _idx = strategy.pairs_across(
            query_texts=source_texts,
            reference_texts=ref_texts,
            k=1,
        )
        max_cos: NDArray[np.float32] = sims[:, 0].astype(np.float32)
        return max_cos

    per_benign: dict[str, dict[str, Any]] = {}
    triggers_fired: list[dict[str, Any]] = []
    for src in benigns_df["source"].unique():
        sub = benigns_df[benigns_df["source"] == src]
        if len(sub) == 0:
            per_benign[src] = {"n_total": 0, "n_flagged": 0, "contamination_pct": 0.0}
            continue
        print(f"[contamination_scan] scanning {src} n={len(sub)}...")
        max_cos = _scan_one(sub["text"].astype(str).tolist())
        flagged = max_cos >= CONTAMINATION_THRESHOLD
        pct = float(flagged.mean() * 100.0)
        per_benign[str(src)] = {
            "n_total": int(len(sub)),
            "n_flagged": int(flagged.sum()),
            "contamination_pct": round(pct, 3),
            "max_cosine_p95": float(np.percentile(max_cos, 95)),
            "max_cosine_p99": float(np.percentile(max_cos, 99)),
        }
        if pct > BENIGN_CONTAMINATION_THRESHOLD_PCT:
            triggers_fired.append(
                {
                    "trigger": "A-005 trigger 1 (benign contamination)",
                    "source": str(src),
                    "contamination_pct": pct,
                    "expected_max": BENIGN_CONTAMINATION_THRESHOLD_PCT,
                }
            )

    per_ood: dict[str, dict[str, Any]] = {}
    for src, df in ood_dfs.items():
        if len(df) == 0:
            per_ood[src] = {"n_total": 0, "n_flagged": 0, "contamination_pct": 0.0}
            continue
        print(f"[contamination_scan] scanning OOD {src} n={len(df)}...")
        max_cos = _scan_one(df["text"].astype(str).tolist())
        flagged = max_cos >= CONTAMINATION_THRESHOLD
        per_ood[src] = {
            "n_total": int(len(df)),
            "n_flagged": int(flagged.sum()),
            "contamination_pct": round(float(flagged.mean() * 100.0), 3),
            "max_cosine_p95": float(np.percentile(max_cos, 95)),
            "max_cosine_p99": float(np.percentile(max_cos, 99)),
        }

    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "adr_ref": "ADR-016 A-005 trigger 1 + A-006 + ADR-041 Q6",
        "cosine_threshold": CONTAMINATION_THRESHOLD,
        "reference_corpus": {
            "slate_n_rows": int(len(slate_df)),
            "templates_n_rows": int(len(templates_df)),
            "total_ref_rows": len(ref_texts),
        },
        "per_benign_source": per_benign,
        "per_ood_source": per_ood,
        "a_005_triggers_fired": triggers_fired,
        "a_005_benign_contamination_clean": len(triggers_fired) == 0,
    }
