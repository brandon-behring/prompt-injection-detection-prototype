"""Build the 50-pair dedup calibration holdout (per ADR-041 Q5).

Generates `data/dedup_holdout.jsonl` with 50 candidate pairs sampled via the
stratified-cosine-band strategy:

- 25 pairs banded: 5 cosine bands {[0.55-0.65), [0.65-0.75), [0.75-0.85),
  [0.85-0.95), [0.95-1.00)} times 5 pairs/band, cycling through the 4
  train-positive sources for source-diversity coverage.
- 25 pairs uniform random across the same source pools (across the full
  cosine range).

Each output row carries `true_duplicate: null` — Brandon hand-labels each pair
post-generation (per ADR-041 Q5 human-in-the-loop step). After labeling,
`scripts/calibrate_dedup.py` reads the labeled JSONL and writes
`evals/dedup_calibration.json` with FPR + FNR at the locked 0.80 threshold +
sensitivity table at {0.75, 0.80, 0.85}.

Usage:
    uv run python scripts/build_dedup_holdout.py [--seed 42]

The script is idempotent under fixed seed — re-running produces the same
candidate pairs (provided source SHAs are unchanged per the manifest).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.dedup import (  # noqa: E402
    MINI_LM_MODEL,
    compute_embeddings,
    encoder_revision_sha,
    pairwise_cosines,
)
from src.data.loaders import load_source  # noqa: E402

# Locked per ADR-041 Q5 — 5 bands, 5 pairs each.
COSINE_BANDS: list[tuple[float, float]] = [
    (0.55, 0.65),
    (0.65, 0.75),
    (0.75, 0.85),
    (0.85, 0.95),
    (0.95, 1.00),
]
PAIRS_PER_BAND: int = 5
RANDOM_PAIR_COUNT: int = 25
TRAIN_POSITIVE_SOURCES: list[str] = [
    "deepset_prompt_injections",
    "lakera_gandalf_ignore_instructions",
    "lakera_mosscap_prompt_injection",
    "hackaprompt",
]


def _sample_banded_pairs(
    rng: np.random.Generator,
    source_pairs_by_band: dict[tuple[float, float], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Sample PAIRS_PER_BAND pairs from each band, cycling through sources for diversity."""
    sampled: list[dict[str, Any]] = []
    for band, candidates in source_pairs_by_band.items():
        if len(candidates) < PAIRS_PER_BAND:
            print(
                f"[build_dedup_holdout] WARNING band {band} has only {len(candidates)} candidates "
                f"(need {PAIRS_PER_BAND}); taking all."
            )
            sampled.extend(candidates)
            continue
        # Bucket by source so we cycle.
        by_source: dict[str, list[dict[str, Any]]] = {}
        for c in candidates:
            by_source.setdefault(c["source_a"], []).append(c)
        # Round-robin pick.
        picked_in_band: list[dict[str, Any]] = []
        round_idx = 0
        while len(picked_in_band) < PAIRS_PER_BAND:
            available_sources = [s for s, lst in by_source.items() if lst]
            if not available_sources:
                break
            src = available_sources[round_idx % len(available_sources)]
            idx = rng.integers(0, len(by_source[src]))
            picked_in_band.append(by_source[src].pop(int(idx)))
            round_idx += 1
        sampled.extend(picked_in_band)
    return sampled


def _enumerate_within_source_pairs(source: str, df_texts: list[str]) -> list[dict[str, Any]]:
    """Enumerate all within-source pairs with cosine in any band; tag with band."""
    if len(df_texts) < 2:
        return []
    emb = compute_embeddings(df_texts)
    cos = pairwise_cosines(emb, emb)
    n = len(df_texts)
    out: list[dict[str, Any]] = []
    for i in range(n):
        for j in range(i + 1, n):
            c = float(cos[i, j])
            band = next((b for b in COSINE_BANDS if b[0] <= c < b[1]), None)
            if band is None:
                continue
            out.append(
                {
                    "source_a": source,
                    "source_b": source,
                    "idx_a": i,
                    "idx_b": j,
                    "text_a": df_texts[i],
                    "text_b": df_texts[j],
                    "cosine": c,
                    "band": list(band),
                }
            )
    return out


def main() -> int:
    """Entry point — load 4 train-positive sources, enumerate banded pairs, sample 50."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default 42)")
    parser.add_argument(
        "--output",
        type=Path,
        default=_REPO_ROOT / "data" / "dedup_holdout.jsonl",
        help="Output JSONL path (default data/dedup_holdout.jsonl)",
    )
    args = parser.parse_args()
    rng = np.random.default_rng(args.seed)

    print(f"[build_dedup_holdout] Loading + embedding {len(TRAIN_POSITIVE_SOURCES)} sources...")
    all_banded: list[dict[str, Any]] = []
    per_source_texts: dict[str, list[str]] = {}
    failed_sources: list[tuple[str, str]] = []
    for src in TRAIN_POSITIVE_SOURCES:
        try:
            df = load_source(src)
        except Exception as exc:  # noqa: BLE001
            failed_sources.append((src, str(exc)[:200]))
            print(f"  {src:>36s}  FAILED: {type(exc).__name__} — skipping")
            print(f"    {str(exc)[:200]}")
            continue
        texts = df["text"].astype(str).tolist()
        per_source_texts[src] = texts
        print(f"  {src:>36s}  n={len(texts)}  enumerating pairs...")
        banded = _enumerate_within_source_pairs(src, texts)
        print(f"    {len(banded)} pairs in any band [0.55, 1.00)")
        all_banded.extend(banded)

    if not per_source_texts:
        raise RuntimeError("All sources failed to load — cannot build holdout.")
    if failed_sources:
        print(
            f"[build_dedup_holdout] WARNING {len(failed_sources)} source(s) failed; "
            f"proceeding with {len(per_source_texts)} of {len(TRAIN_POSITIVE_SOURCES)} sources."
        )
        print(
            "[build_dedup_holdout] Methodology note: ADR-041 Q5 names all 4 train-positive sources; "
            "re-run after access granted for full coverage."
        )

    print(f"[build_dedup_holdout] Total banded candidates: {len(all_banded)}")

    by_band: dict[tuple[float, float], list[dict[str, Any]]] = {b: [] for b in COSINE_BANDS}
    for p in all_banded:
        band_key = (float(p["band"][0]), float(p["band"][1]))
        by_band[band_key].append(p)
    print("[build_dedup_holdout] Per-band candidate counts:")
    for b, lst in by_band.items():
        print(f"    {b}  n={len(lst)}")

    banded_sample = _sample_banded_pairs(rng, by_band)
    print(f"[build_dedup_holdout] Sampled {len(banded_sample)} banded pairs.")

    # Random pairs: enumerate all pairs across the source pools (any cosine).
    print(f"[build_dedup_holdout] Sampling {RANDOM_PAIR_COUNT} random pairs (any cosine)...")
    random_pairs: list[dict[str, Any]] = []
    available_sources = list(per_source_texts.keys())
    src_choices = rng.choice(available_sources, size=RANDOM_PAIR_COUNT, replace=True)
    for src in src_choices:
        texts = per_source_texts[str(src)]
        if len(texts) < 2:
            continue
        i, j = sorted(rng.choice(len(texts), size=2, replace=False).tolist())
        emb = compute_embeddings([texts[i], texts[j]])
        cos = float(emb[0] @ emb[1].T)
        random_pairs.append(
            {
                "source_a": str(src),
                "source_b": str(src),
                "idx_a": int(i),
                "idx_b": int(j),
                "text_a": texts[i],
                "text_b": texts[j],
                "cosine": cos,
                "band": None,
            }
        )

    print(f"[build_dedup_holdout] Sampled {len(random_pairs)} random pairs.")

    all_pairs = banded_sample + random_pairs
    args.output.parent.mkdir(parents=True, exist_ok=True)

    metadata = {
        "_metadata": True,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seed": args.seed,
        "encoder": MINI_LM_MODEL,
        "encoder_revision": encoder_revision_sha(),
        "n_pairs": len(all_pairs),
        "n_banded": len(banded_sample),
        "n_random": len(random_pairs),
        "adr_ref": "ADR-041 Q5",
    }

    with args.output.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(metadata) + "\n")
        for pair_id, pair in enumerate(all_pairs):
            pair["pair_id"] = pair_id
            pair["true_duplicate"] = None  # TBD — hand-labeled by Brandon
            fh.write(json.dumps(pair, ensure_ascii=False) + "\n")

    print(f"[build_dedup_holdout] Wrote {len(all_pairs)} pairs to {args.output}")
    print("[build_dedup_holdout] Next step: hand-label `true_duplicate` field in each row.")
    print("[build_dedup_holdout] Then run: uv run python scripts/calibrate_dedup.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
