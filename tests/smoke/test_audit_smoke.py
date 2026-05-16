"""Smoke tests for src/data/audit.py — synthetic source verification.

Tests audit + leakage + contamination math with hand-crafted DataFrames; no
HF download. Encoder load (~80MB MiniLM) is the only network call.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.data.audit import (
    BENIGN_CONTAMINATION_THRESHOLD_PCT,
    compute_contamination_scan,
    compute_data_audit,
    compute_leakage_report,
)
from src.data.splits import TRAIN_POSITIVE_SOURCES, make_splits


def _synthetic_positives(per_source: int = 30) -> pd.DataFrame:
    """Build synthetic positives DataFrame across the 4 ADR-016 sources."""
    frames = []
    for src in TRAIN_POSITIVE_SOURCES:
        frames.append(
            pd.DataFrame(
                {
                    "text": [f"{src}_inject_{i}" for i in range(per_source)],
                    "label": 1,
                    "source": src,
                    "row_idx_in_source": list(range(per_source)),
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


def _synthetic_benigns(per_source: int = 100) -> pd.DataFrame:
    """Build synthetic benigns DataFrame for lmsys + ultrachat."""
    frames = []
    for src in ("lmsys_chat_1m", "ultrachat_200k"):
        frames.append(
            pd.DataFrame(
                {
                    "text": [f"{src}_benign_{i}" for i in range(per_source)],
                    "label": 0,
                    "source": src,
                    "row_idx_in_source": list(range(per_source)),
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


@pytest.mark.smoke
def test_compute_data_audit_yields_per_source_counts() -> None:
    """compute_data_audit returns per-source counts + per-fold class balance."""
    positives = _synthetic_positives()
    benigns = _synthetic_benigns()
    splits = make_splits(positives, benigns)
    audit = compute_data_audit(
        positives_raw_per_source={
            src: positives[positives["source"] == src] for src in TRAIN_POSITIVE_SOURCES
        },
        positives_dedup=positives,
        benigns_raw_per_source={
            src: benigns[benigns["source"] == src] for src in ("lmsys_chat_1m", "ultrachat_200k")
        },
        benigns_dedup=benigns,
        splits=splits,
    )
    assert audit["schema_version"] == "1.0"
    assert set(audit["per_source_counts_and_length"].keys()) == set(TRAIN_POSITIVE_SOURCES) | {
        "lmsys_chat_1m",
        "ultrachat_200k",
    }
    for src in TRAIN_POSITIVE_SOURCES:
        rec = audit["per_source_counts_and_length"][src]
        assert rec["role"] == "train_positive"
        assert rec["raw_n"] == 30
        assert rec["post_dedup_n"] == 30
        assert "length_distribution" in rec
    assert len(audit["per_fold_class_balance"]) == 12  # 4 folds x 3 seeds


@pytest.mark.smoke
@pytest.mark.network
def test_compute_leakage_report_zero_overlaps_on_disjoint_splits() -> None:
    """Synthetic splits with text-distinct per source -> zero leakage expected."""
    positives = _synthetic_positives()
    benigns = _synthetic_benigns()
    splits = make_splits(positives, benigns)
    leakage = compute_leakage_report(splits)
    assert leakage["schema_version"] == "1.0"
    assert leakage["total_exact_hash_overlaps"] == 0
    assert leakage["total_cosine_overlaps"] == 0
    assert leakage["leakage_clean"] is True
    assert len(leakage["per_fold_seed"]) == 12


@pytest.mark.smoke
@pytest.mark.network
def test_compute_contamination_scan_unrelated_benigns_clean() -> None:
    """Synthetic benigns with text completely unrelated to slate -> zero contamination."""
    positives = _synthetic_positives()
    benigns = _synthetic_benigns()
    templates_df = pd.DataFrame(
        {
            "text": ["malicious_template_pattern_one", "malicious_template_pattern_two"],
            "label": 1,
            "source": "hackaprompt_templates",
            "row_idx_in_source": [0, 1],
        }
    )
    ood_dfs = {
        "synthetic_ood": pd.DataFrame(
            {
                "text": ["benign_ood_query"],
                "label": 0,
                "source": "synthetic_ood",
                "row_idx_in_source": [0],
            }
        )
    }
    scan = compute_contamination_scan(
        benigns_df=benigns,
        ood_dfs=ood_dfs,
        slate_df=positives,
        templates_df=templates_df,
    )
    assert scan["schema_version"] == "1.0"
    assert scan["cosine_threshold"] == 0.85
    # Unrelated synthetic text shouldn't hit 0.85 cosine.
    for src_stats in scan["per_benign_source"].values():
        assert src_stats["contamination_pct"] <= BENIGN_CONTAMINATION_THRESHOLD_PCT
    assert scan["a_005_benign_contamination_clean"] is True
