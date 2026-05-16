"""End-to-end Phase 1 data pipeline orchestrator.

Runs the canonical Phase 1 pipeline per ADR-016 + ADR-041:

  1. Load 4 train-positive sources + 2 train-benign sources (HF + git).
  2. Within-source dedup each (MiniLM cosine >= 0.80 per ADR-016 Q4).
  3. Cross-source benign dedup with LMSYS-priority tiebreak (per ADR-016 Q5).
  4. Make + materialize 36 per-fold parquets + 36 index masks (per ADR-041 Q7).
  5. Load 5 OOD sources for contamination scan.
  6. Extract ~200 templates from HackAPrompt (per ADR-041 Q6).
  7. Compute data_audit + leakage_report + contamination_scan JSONs.
  8. Write all 3 JSONs to evals/.

Wall-clock estimate (CPU; first-run HF downloads cached after):
  LMSYS + UltraChat downloads: ~5-15 min
  Embed + dedup positives (~7K rows): ~30 s
  Embed + dedup benigns (~20K rows): ~3 min
  Splits + materialize: ~30 s
  OOD load (~2K rows): ~1 min
  Templates extract + scan: ~3 min

Usage:
    source .env.local && uv run python scripts/run_data_pipeline.py [--skip-X ...]

Idempotent — HF cache survives re-runs; data/processed/ overwritten each call.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.audit import (  # noqa: E402
    compute_contamination_scan,
    compute_data_audit,
    compute_leakage_report,
)
from src.data.dedup import dedup_cross_source_benigns, dedup_within_source  # noqa: E402
from src.data.loaders import load_source  # noqa: E402
from src.data.manifest_validation import EXPECTED_SOURCE_NAMES  # noqa: E402
from src.data.splits import (  # noqa: E402
    TRAIN_POSITIVE_SOURCES,
    apply_leakage_cleanup,
    make_splits,
    materialize_index_masks,
    materialize_splits,
)

TRAIN_BENIGN_SOURCES: tuple[str, ...] = ("lmsys_chat_1m", "ultrachat_200k")
OOD_SOURCES: tuple[str, ...] = tuple(
    s for s in EXPECTED_SOURCE_NAMES if s not in TRAIN_POSITIVE_SOURCES + TRAIN_BENIGN_SOURCES
)

PROCESSED_ROOT = _REPO_ROOT / "data" / "processed"
EVALS_ROOT = _REPO_ROOT / "evals"


def _log(stage: str, message: str) -> None:
    """Timestamped pipeline log line."""
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] [{stage:>14s}] {message}", flush=True)


def _load_train_positives() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Load 4 train-positive sources; per-source within-source dedup; return raw + deduped."""
    raw: dict[str, pd.DataFrame] = {}
    deduped_frames: list[pd.DataFrame] = []
    for src in TRAIN_POSITIVE_SOURCES:
        _log("load-positive", f"loading {src}")
        df = load_source(src)
        _log("load-positive", f"  {src} loaded n={len(df)}")
        raw[src] = df
        _log("dedup-within", f"deduping {src} (n={len(df)})")
        dedup_df, dropped = dedup_within_source(df)
        _log("dedup-within", f"  {src} kept {len(dedup_df)} (dropped {len(dropped)})")
        deduped_frames.append(dedup_df)
    deduped = pd.concat(deduped_frames, ignore_index=True)
    _log("load-positive", f"total deduped positives n={len(deduped)}")
    return raw, deduped


def _load_train_benigns() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Load 2 benigns; within-source then cross-source dedup; return raw + final pool."""
    raw: dict[str, pd.DataFrame] = {}
    deduped_per_source: dict[str, pd.DataFrame] = {}
    for src in TRAIN_BENIGN_SOURCES:
        _log("load-benign", f"loading {src} (heavy download on first run)")
        df = load_source(src)
        _log("load-benign", f"  {src} loaded n={len(df)}")
        raw[src] = df
        _log("dedup-within", f"deduping {src} (n={len(df)})")
        dedup_df, dropped = dedup_within_source(df)
        _log("dedup-within", f"  {src} kept {len(dedup_df)} (dropped {len(dropped)})")
        deduped_per_source[src] = dedup_df
    _log(
        "dedup-cross",
        f"cross-source dedup with LMSYS-priority (n_total={sum(len(d) for d in deduped_per_source.values())})",
    )
    pool, dropped = dedup_cross_source_benigns(deduped_per_source)
    _log("dedup-cross", f"  cross-source kept n={len(pool)} (dropped {len(dropped)})")
    return raw, pool


def _load_ood_sources() -> dict[str, pd.DataFrame]:
    """Load 5 OOD eval sources (some are git_repo; may fail per-source)."""
    out: dict[str, pd.DataFrame] = {}
    for src in OOD_SOURCES:
        _log("load-ood", f"loading {src}")
        try:
            df = load_source(src)
            _log("load-ood", f"  {src} loaded n={len(df)}")
            out[src] = df
        except Exception as exc:  # noqa: BLE001
            _log("load-ood", f"  {src} FAILED: {type(exc).__name__} — {str(exc)[:120]}")
    return out


def main() -> int:
    """Run the canonical Phase 1 pipeline; emit 3 JSON deliverables under evals/."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-ood",
        action="store_true",
        help="Skip OOD source loading + contamination scan (faster)",
    )
    parser.add_argument(
        "--skip-templates",
        action="store_true",
        help="Skip template extraction + contamination scan reference corpus",
    )
    args = parser.parse_args()

    EVALS_ROOT.mkdir(parents=True, exist_ok=True)

    _log("start", "Phase 1 pipeline begins")

    # ----------------------------------------------------------------------
    # Stage 1 — train sources: load + within-source dedup
    # ----------------------------------------------------------------------
    raw_positives, deduped_positives = _load_train_positives()
    raw_benigns, deduped_benigns = _load_train_benigns()

    # ----------------------------------------------------------------------
    # Stage 2 — splits + materialization
    # ----------------------------------------------------------------------
    _log("splits", "building 12 (fold, seed) splits")
    splits = make_splits(deduped_positives, deduped_benigns)
    _log("leak-cleanup", "applying post-split train+val vs test leakage cleanup (per ADR-043)")
    splits, cleanup_records = apply_leakage_cleanup(splits, threshold=0.85)
    total_dropped = sum(r["n_dropped"] for r in cleanup_records)
    total_exact = sum(r["n_exact_hash_leaks"] for r in cleanup_records)
    total_cosine = sum(r["n_cosine_leaks"] for r in cleanup_records)
    _log(
        "leak-cleanup",
        f"  dropped {total_dropped} rows (exact={total_exact} + cosine={total_cosine}) across 12 splits",
    )
    _log("splits", f"materializing 36 parquets under {PROCESSED_ROOT}")
    parquet_paths = materialize_splits(splits, PROCESSED_ROOT)
    _log("splits", f"  wrote {len(parquet_paths)} parquet files")
    _log("splits", "materializing 36 index masks")
    mask_paths = materialize_index_masks(splits, PROCESSED_ROOT)
    _log("splits", f"  wrote {len(mask_paths)} .npy files")

    # ----------------------------------------------------------------------
    # Stage 3 — data audit JSON
    # ----------------------------------------------------------------------
    _log("audit", "computing data_audit.json")
    data_audit = compute_data_audit(
        positives_raw_per_source=raw_positives,
        positives_dedup=deduped_positives,
        benigns_raw_per_source=raw_benigns,
        benigns_dedup=deduped_benigns,
        splits=splits,
    )
    audit_path = EVALS_ROOT / "data_audit.json"
    with audit_path.open("w", encoding="utf-8") as fh:
        json.dump(data_audit, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    _log("audit", f"  wrote {audit_path}")
    _log(
        "audit",
        f"  A-005 trigger 2 (class-balance) clean: {data_audit['a_005_class_balance_clean']}",
    )

    # ----------------------------------------------------------------------
    # Stage 4 — leakage report JSON
    # ----------------------------------------------------------------------
    _log("leakage", "computing leakage_report.json (per-fold train+val vs test)")
    leakage = compute_leakage_report(splits)
    leakage_path = EVALS_ROOT / "leakage_report.json"
    with leakage_path.open("w", encoding="utf-8") as fh:
        json.dump(leakage, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    _log("leakage", f"  wrote {leakage_path}")
    _log(
        "leakage",
        f"  total_exact={leakage['total_exact_hash_overlaps']} total_cosine={leakage['total_cosine_overlaps']} clean={leakage['leakage_clean']}",
    )

    # ----------------------------------------------------------------------
    # Stage 5 — OOD + contamination scan JSON
    # ----------------------------------------------------------------------
    if args.skip_ood and args.skip_templates:
        _log("contamination", "skipped (--skip-ood + --skip-templates)")
        return 0

    ood_dfs = {} if args.skip_ood else _load_ood_sources()

    if not args.skip_templates:
        _log("templates", "extracting HackAPrompt templates (~200 successful injections)")
        from src.data.manifest_validation import validate_manifest
        from src.data.templates import extract_hackaprompt_templates

        manifest = validate_manifest(_REPO_ROOT / "data" / "source_manifest.yaml")
        hp_spec = next(row for row in manifest["sources"] if row["name"] == "hackaprompt")
        templates_df = extract_hackaprompt_templates(hp_spec)
        templates_path = _REPO_ROOT / "data" / "contamination_templates.parquet"
        templates_df.to_parquet(templates_path, index=False)
        _log("templates", f"  extracted + wrote {len(templates_df)} templates -> {templates_path}")
    else:
        _log("templates", "skipped (--skip-templates); using empty templates corpus")
        templates_df = pd.DataFrame(columns=["text", "label", "source", "row_idx_in_source"])

    _log("contamination", "computing contamination_scan.json")
    scan = compute_contamination_scan(
        benigns_df=deduped_benigns,
        ood_dfs=ood_dfs,
        slate_df=deduped_positives,
        templates_df=templates_df,
    )
    scan_path = EVALS_ROOT / "contamination_scan.json"
    with scan_path.open("w", encoding="utf-8") as fh:
        json.dump(scan, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    _log("contamination", f"  wrote {scan_path}")
    _log(
        "contamination",
        f"  A-005 trigger 1 (benign contamination) clean: {scan['a_005_benign_contamination_clean']}",
    )

    _log("done", "Phase 1 pipeline complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
