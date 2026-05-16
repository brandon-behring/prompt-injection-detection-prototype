"""HackAPrompt template extraction for contamination corpus (per ADR-041 Q6).

Public API
----------
- `extract_hackaprompt_templates(spec, target_count=200, sample_seed=1337)` -> pd.DataFrame

Returns a DataFrame normalized to `(text, label, source, row_idx_in_source, level)`
schema (compatible with `src.data.loaders.OUTPUT_COLUMNS` plus an extra `level`
column for diagnostics). Templates are sampled from `correct == True` rows
(successful injections), balanced across HackAPrompt difficulty levels.

ADR-041 Q6 conceptual basis: Schulhoff 2023 catalogues ~29 attack techniques;
ideal extraction would be ~7 templates per technique. Practical simplification:
HackAPrompt rows are NOT directly labeled by Schulhoff's taxonomy, so this
implementation samples balanced-across-levels successful injections (~200 / 10
levels = ~20/level). The templates capture the canonical successful-exploit
pattern surface; full taxonomy-aware extraction is a future-work axis.

Sampling is seed-deterministic. Sampled templates are DISJOINT from the slate's
HackAPrompt sample (slate uses selection_seed=42 per ADR-016 Q6; templates use
sample_seed=1337 here).
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from datasets import Dataset, load_dataset

DEFAULT_TARGET_COUNT: int = 200
DEFAULT_SAMPLE_SEED: int = 1337


def extract_hackaprompt_templates(
    spec: dict[str, Any],
    *,
    target_count: int = DEFAULT_TARGET_COUNT,
    sample_seed: int = DEFAULT_SAMPLE_SEED,
) -> pd.DataFrame:
    """Extract approximately target_count successful-injection templates from HackAPrompt.

    Parameters
    ----------
    spec : dict
        HackAPrompt source spec from configs/data/source_manifest.yaml (carries
        hf_id + revision_sha).
    target_count : int, optional
        Approximate number of templates to extract (default 200 per ADR-041 Q6).
    sample_seed : int, optional
        Random seed for the per-level sampling step (default 1337; disjoint
        from slate's 42 per ADR-016 Q6).

    Returns
    -------
    pandas.DataFrame
        Columns `(text, label=1, source="hackaprompt_templates", row_idx_in_source, level)`.

    Raises
    ------
    RuntimeError
        If the HackAPrompt corpus contains no `correct == True` rows.
    """
    ds = load_dataset(
        "hackaprompt/hackaprompt-dataset",
        split="train",
        revision=spec["revision_sha"],
    )
    if not isinstance(ds, Dataset):
        raise RuntimeError(f"Expected Dataset, got {type(ds).__name__}")
    df = ds.to_pandas()

    # Filter to successful injections only; non-null user_input.
    df = df[df["correct"] == True]  # noqa: E712 — pandas-idiomatic comparison to True
    df = df[df["user_input"].notna() & (df["user_input"].astype(str).str.len() > 0)]
    if len(df) == 0:
        raise RuntimeError("No correct=True rows in HackAPrompt; cannot extract templates")

    # Random shuffle (seeded).
    df = df.sample(frac=1, random_state=sample_seed).reset_index(drop=True)

    # Balanced sample across levels (if level column present).
    if "level" in df.columns:
        n_levels = df["level"].nunique()
        per_level = max(target_count // n_levels, 1)
        sampled = df.groupby("level", group_keys=False, sort=False).head(per_level)
    else:
        sampled = df.head(target_count)
    sampled = sampled.head(target_count).reset_index(drop=True)

    return pd.DataFrame(
        {
            "text": sampled["user_input"].astype(str),
            "label": 1,
            "source": "hackaprompt_templates",
            "row_idx_in_source": list(range(len(sampled))),
            "level": (sampled["level"].astype(int) if "level" in sampled.columns else 0),
        }
    )
