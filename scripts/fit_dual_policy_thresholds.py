"""CLI entrypoint — fit dual-policy thresholds per ADR-025 + ADR-045 Q5.

Per ADR-025 + ADR-018, dual-policy fitting applies to **trained rungs only**
(classical_floor + frozen-probe + LoRA + full-FT); reference scorers
(ProtectAI v1/v2 + LLM judges) are excluded per SPEC §4 applicability lock.

Inputs
------
``--val-root`` + ``--test-root`` — directories carrying val/test predictions
parquets per fold/seed.

``--rung`` — which trained rung to process (defaults to all).

Outputs
-------
``--operating-points-out`` (default ``evals/operating_points/dual_policy.parquet``)
— OperatingPointModel rows for both policies × trained-rung cells.

``--reachability-audit-out`` (default ``evals/audit/verification_reachability.json``)
— per-(rung, fold, seed) ReachabilityAuditModel records per A-009.

Usage
-----
.. code-block:: bash

    uv run python scripts/fit_dual_policy_thresholds.py
    uv run python scripts/fit_dual_policy_thresholds.py --rung lora
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import cast

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.eval.operating_points import (  # noqa: E402
    compute_reachability_audit,
    fit_dual_policy_for_cell,
)
from src.eval.schemas import OperatingPointModel, ReachabilityAuditModel  # noqa: E402

# Trained-rung allowlist per ADR-025 + SPEC §4 dual-policy applicability lock.
# Rung canonical names per src.eval.schemas.PredictionsRowModel `rung` column —
# transformer rungs persist with underscore form (frozen_probe, full_ft); the
# classical/reference scorers use dash form (tfidf-lr, protectai-v1, protectai-v2).
TRAINED_RUNGS: frozenset[str] = frozenset({"tfidf-lr", "frozen_probe", "lora", "full_ft"})


def _load_predictions(root: Path, rung_filter: str | None) -> pd.DataFrame:
    """Load all predictions parquets under root; optionally filter to one rung_id."""
    paths = sorted(root.glob("*.parquet"))
    if not paths:
        raise FileNotFoundError(f"no parquets at {root}")
    df = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)
    if rung_filter:
        df = df[df["rung"] == rung_filter].reset_index(drop=True)
    return df


def main() -> int:
    """Sweep trained-rung × fold × seed; fit dual policies + emit audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--val-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions_val",
    )
    parser.add_argument(
        "--test-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions",
    )
    parser.add_argument(
        "--rung",
        default=None,
        help="Restrict to one trained rung_id (e.g. 'lora'); default = all trained rungs",
    )
    parser.add_argument(
        "--operating-points-out",
        type=Path,
        default=_REPO_ROOT / "evals" / "operating_points" / "dual_policy.parquet",
    )
    parser.add_argument(
        "--reachability-audit-out",
        type=Path,
        default=_REPO_ROOT / "evals" / "audit" / "verification_reachability.json",
    )
    args = parser.parse_args()

    val_df = _load_predictions(args.val_root, args.rung)
    test_df = _load_predictions(args.test_root, args.rung)

    operating_points: list[OperatingPointModel] = []
    reachability: list[ReachabilityAuditModel] = []

    for key, val_cell in val_df.groupby(["rung", "fold", "seed"]):
        rung, fold_val, seed_val = key
        rung_str = str(rung)
        fold = cast(int, fold_val)
        seed = cast(int, seed_val)
        if rung_str not in TRAINED_RUNGS:
            continue
        test_cell = test_df[
            (test_df["rung"] == rung) & (test_df["fold"] == fold) & (test_df["seed"] == seed)
        ]
        if val_cell.empty or test_cell.empty:
            continue
        try:
            ops = fit_dual_policy_for_cell(
                rung=rung_str,
                fold=fold,
                seed=seed,
                val_df=val_cell,
                test_df=test_cell,
            )
            operating_points.extend(ops)
            audit = compute_reachability_audit(
                rung=rung_str,
                fold=fold,
                seed=seed,
                val_df=val_cell,
                test_df=test_cell,
            )
            reachability.append(audit)
        except (ValueError, RuntimeError) as err:
            print(f"[dual-policy] skip {rung}/{fold}/{seed}: {err}", file=sys.stderr)

    if not operating_points:
        print("[dual-policy] no operating points produced", file=sys.stderr)
        return 1

    args.operating_points_out.parent.mkdir(parents=True, exist_ok=True)
    op_df = pd.DataFrame([op.model_dump() for op in operating_points])
    op_df.to_parquet(args.operating_points_out, index=False)
    print(
        f"[dual-policy] wrote {len(operating_points)} operating points to {args.operating_points_out}"
    )

    args.reachability_audit_out.parent.mkdir(parents=True, exist_ok=True)
    audit_nested: dict[str, dict[str, dict[str, dict[str, object]]]] = {}
    for r in reachability:
        audit_nested.setdefault(r.rung, {}).setdefault(f"fold-{r.fold}", {})[f"seed-{r.seed}"] = {
            "target_reachable": r.target_reachable,
            "target_recall": r.target_recall,
            "achieved_val_recall": r.achieved_val_recall,
            "fallback_threshold": r.fallback_threshold,
            "fallback_test_fpr": r.fallback_test_fpr,
        }
    with args.reachability_audit_out.open("w", encoding="utf-8") as fh:
        json.dump(audit_nested, fh, indent=2)
    print(
        f"[dual-policy] wrote {len(reachability)} reachability records to "
        f"{args.reachability_audit_out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
