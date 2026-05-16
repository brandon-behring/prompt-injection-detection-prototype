"""Compute dedup FPR + FNR from hand-labeled holdout (per ADR-041 Q5 + ADR-016 Q4).

Reads `data/dedup_holdout.jsonl` (50 pairs, each hand-labeled with
`true_duplicate: bool`) and writes `evals/dedup_calibration.json` containing:

- FPR + FNR at the locked threshold 0.80 (per ADR-016 Q4).
- Sensitivity table at thresholds {0.75, 0.80, 0.85}.
- Per-band counts (banded-sample diagnostics).
- Holdout SHA-256 + encoder revision (provenance).

Errors out (exit 2) if any holdout row has `true_duplicate: null` — labeling
is the human-in-the-loop step that cannot be skipped.

Usage:
    uv run python scripts/calibrate_dedup.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.dedup import MINI_LM_MODEL, THRESHOLD  # noqa: E402

SENSITIVITY_THRESHOLDS: tuple[float, ...] = (0.75, 0.80, 0.85)


class HoldoutNotLabeledError(RuntimeError):
    """Raised when holdout JSONL contains any null `true_duplicate` field."""


def _read_holdout(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Read JSONL holdout — first line is metadata; rest are labeled pairs."""
    if not path.exists():
        raise FileNotFoundError(
            f"Holdout not found at {path}. Run scripts/build_dedup_holdout.py first."
        )
    metadata: dict[str, Any] = {}
    pairs: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            record = json.loads(line)
            if record.get("_metadata"):
                metadata = record
            else:
                pairs.append(record)

    unlabeled = [p["pair_id"] for p in pairs if p.get("true_duplicate") is None]
    if unlabeled:
        raise HoldoutNotLabeledError(
            f"{len(unlabeled)} holdout pairs are unlabeled (null true_duplicate). "
            f"Hand-label each row in {path} before running calibration. "
            f"Unlabeled pair_ids: {unlabeled[:10]}{'...' if len(unlabeled) > 10 else ''}"
        )
    return metadata, pairs


def _confusion_at_threshold(
    pairs: list[dict[str, Any]], threshold: float
) -> dict[str, int | float]:
    """Compute TP/FP/TN/FN + FPR/FNR at a given cosine threshold."""
    tp = fp = tn = fn = 0
    for p in pairs:
        predicted = float(p["cosine"]) >= threshold
        actual = bool(p["true_duplicate"])
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and not actual:
            tn += 1
        else:
            fn += 1
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    return {
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "fpr": fpr,
        "fnr": fnr,
        "n_pairs": len(pairs),
    }


def _per_band_counts(pairs: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Return {band_str: {n_total, n_true_duplicate}} for banded-sample diagnostics."""
    out: dict[str, dict[str, int]] = {}
    for p in pairs:
        band = p.get("band")
        key = "random" if band is None else f"[{band[0]:.2f}, {band[1]:.2f})"
        bucket = out.setdefault(key, {"n_total": 0, "n_true_duplicate": 0})
        bucket["n_total"] += 1
        if bool(p["true_duplicate"]):
            bucket["n_true_duplicate"] += 1
    return out


def _holdout_sha256(path: Path) -> str:
    """Return SHA-256 digest of the holdout JSONL bytes (provenance pin)."""
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    """Entry — read holdout, compute confusion at locked threshold + sensitivity table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--holdout",
        type=Path,
        default=_REPO_ROOT / "data" / "dedup_holdout.jsonl",
        help="Holdout JSONL path (default data/dedup_holdout.jsonl)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_REPO_ROOT / "evals" / "dedup_calibration.json",
        help="Calibration JSON output path (default evals/dedup_calibration.json)",
    )
    args = parser.parse_args()

    try:
        metadata, pairs = _read_holdout(args.holdout)
    except HoldoutNotLabeledError as err:
        print(f"[calibrate_dedup] ERROR: {err}")
        return 2

    print(f"[calibrate_dedup] Loaded {len(pairs)} labeled pairs from {args.holdout}")

    locked = _confusion_at_threshold(pairs, THRESHOLD)
    print(f"[calibrate_dedup] At locked threshold {THRESHOLD}:")
    print(f"    TP={locked['tp']}  FP={locked['fp']}  TN={locked['tn']}  FN={locked['fn']}")
    print(f"    FPR={locked['fpr']:.4f}  FNR={locked['fnr']:.4f}")

    sensitivity = {f"{t:.2f}": _confusion_at_threshold(pairs, t) for t in SENSITIVITY_THRESHOLDS}

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "adr_ref": "ADR-016 Q4 + ADR-041 Q5",
        "threshold_locked": THRESHOLD,
        "encoder": MINI_LM_MODEL,
        "encoder_revision": metadata.get("encoder_revision", "unknown"),
        "holdout_path": str(args.holdout.relative_to(_REPO_ROOT)),
        "holdout_sha256": _holdout_sha256(args.holdout),
        "holdout_size": len(pairs),
        "holdout_n_banded": metadata.get("n_banded"),
        "holdout_n_random": metadata.get("n_random"),
        "at_locked_threshold": locked,
        "sensitivity_table": sensitivity,
        "per_band_counts": _per_band_counts(pairs),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"[calibrate_dedup] Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
