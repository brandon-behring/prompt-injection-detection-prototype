"""Cost ledger rollup — aggregates runpod-deploy manifests + API logs into CSV.

Per ADR-020 §dual-layer cost cap discipline:

- **Layer 1 (per-pod)**: ``budget.cost_cap_usd`` enforced by runpod-deploy
  internally; one bad pod cannot exceed its own cap.
- **Layer 2 (project-wide)**: hard cap $200, enforced by this script via the
  ``--check`` flag (intended for CI).

Walks ``artifacts/runpod/<run>/runpod_deploy_pull_manifest.json`` files
(schema v2; auto-emitted by runpod-deploy per ``runpod-deploy/docs/source/
lifecycle.md`` §8 "Manifest write"); aggregates ``wall_time_sec`` ×
``gpu_price_per_hour_usd`` (already pre-computed as ``estimated_cost_usd``);
separately tracks API spend from LLM-judge call logs (per ADR-018 + A-014).
Emits per-target rows to ``evals/cost_ledger.csv`` per ADR-020 line 146 schema.

CSV schema (per ADR-020 line 146)
---------------------------------
``timestamp, target, est_cost_usd, actual_cost_usd, gpu_hours, api_calls, notes``

Usage
-----
.. code-block:: bash

    uv run python scripts/cost_rollup.py            # writes evals/cost_ledger.csv
    uv run python scripts/cost_rollup.py --check    # also fails exit-1 if > $200
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent

# Per ADR-020 §Cost cap (dual-layer) — line 148 thresholds.
HARD_CAP_USD: float = 200.0
SOFT_CAP_USD: float = 125.0
TRIGGER_FLAG_USD: float = 80.0

LEDGER_HEADER: tuple[str, ...] = (
    "timestamp",
    "target",
    "est_cost_usd",
    "actual_cost_usd",
    "gpu_hours",
    "api_calls",
    "notes",
)


def walk_runpod_manifests(runpod_root: Path) -> list[dict[str, Any]]:
    """Walk ``artifacts/runpod/*/runpod_deploy_pull_manifest.json`` files.

    Parameters
    ----------
    runpod_root : Path
        Root directory containing per-run subdirs with manifest JSONs.

    Returns
    -------
    list of dict
        Each dict is a row matching the LEDGER_HEADER schema. Returns empty
        list if ``runpod_root`` does not exist (clean first-run state).
    """
    rows: list[dict[str, Any]] = []
    if not runpod_root.exists():
        return rows
    for manifest_path in sorted(runpod_root.rglob("runpod_deploy_pull_manifest.json")):
        try:
            with manifest_path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as err:
            print(f"[cost_rollup] WARN: skipping unreadable manifest {manifest_path}: {err}")
            continue
        wall_time_sec = float(data.get("wall_time_sec") or 0.0)
        est_cost = float(data.get("estimated_cost_usd") or 0.0)
        gpu_hours = round(wall_time_sec / 3600.0, 3) if wall_time_sec else 0.0
        rows.append(
            {
                "timestamp": data.get("run_id", manifest_path.parent.name),
                "target": data.get("job_name", "unknown"),
                "est_cost_usd": est_cost,
                # actual_cost_usd from runpod-deploy is the same field; the
                # column name distinction is for forward-compat when API spend
                # is later reconciled against vendor billing.
                "actual_cost_usd": est_cost,
                "gpu_hours": gpu_hours,
                "api_calls": 0,
                "notes": (
                    f"gpu_id={data.get('gpu_id', '?')} "
                    f"state={data.get('pod_final_state', '?')} "
                    f"dc={data.get('datacenter_id', '?')}"
                ),
            }
        )
    return rows


def walk_api_logs(api_logs_root: Path) -> list[dict[str, Any]]:
    """Walk LLM-judge API call logs (per ADR-018 + A-014 cache discipline).

    Parameters
    ----------
    api_logs_root : Path
        Typically ``evals/audit/llm_judge_cache/``. Each ``.json`` file is one
        ``(judge_model, run)`` invocation log with at minimum
        ``{"judge": str, "n_calls": int, "est_cost_usd": float, "timestamp": str}``.
        Per ADR-018 + A-007 the cache infrastructure is populated by Phase 3
        scoring; this walker is forward-compat for Phase 4+ cost reconciliation.

    Returns
    -------
    list of dict
        Rows matching the LEDGER_HEADER schema. Empty if no log files exist.
    """
    rows: list[dict[str, Any]] = []
    if not api_logs_root.exists():
        return rows
    for log_path in sorted(api_logs_root.rglob("*.json")):
        try:
            with log_path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict) or "judge" not in data:
            continue
        est_cost = float(data.get("est_cost_usd") or 0.0)
        rows.append(
            {
                "timestamp": data.get("timestamp", log_path.stem),
                "target": f"llm_judge_{data.get('judge', 'unknown')}",
                "est_cost_usd": est_cost,
                "actual_cost_usd": est_cost,
                "gpu_hours": 0.0,
                "api_calls": int(data.get("n_calls") or 0),
                "notes": str(log_path.name),
            }
        )
    return rows


def write_cost_ledger(rows: list[dict[str, Any]], out_path: Path) -> None:
    """Write all rows to ``out_path`` as CSV (schema per ADR-020 line 146).

    Parameters
    ----------
    rows : list of dict
        Aggregated from ``walk_runpod_manifests`` + ``walk_api_logs``.
    out_path : Path
        Typically ``evals/cost_ledger.csv``. Parent directory created if
        missing.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LEDGER_HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def compute_cumulative_spend(rows: list[dict[str, Any]]) -> float:
    """Sum ``actual_cost_usd`` across all rows."""
    return sum(float(r["actual_cost_usd"]) for r in rows)


def main() -> int:
    """Aggregate manifests + API logs; write CSV; optionally fail on hard cap."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runpod-root",
        type=Path,
        default=_REPO_ROOT / "artifacts" / "runpod",
    )
    parser.add_argument(
        "--api-logs-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "audit" / "llm_judge_cache",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_REPO_ROOT / "evals" / "cost_ledger.csv",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail with exit 1 if cumulative spend > HARD_CAP_USD ($200)",
    )
    args = parser.parse_args()

    runpod_rows = walk_runpod_manifests(args.runpod_root)
    api_rows = walk_api_logs(args.api_logs_root)
    all_rows = runpod_rows + api_rows
    write_cost_ledger(all_rows, args.output)
    cumulative = compute_cumulative_spend(all_rows)

    print(f"[cost_rollup] {len(all_rows)} rows aggregated to {args.output}")
    print(f"[cost_rollup]   {len(runpod_rows)} runpod-deploy manifests")
    print(f"[cost_rollup]   {len(api_rows)} API logs")
    print(f"[cost_rollup] Cumulative spend: ${cumulative:.2f}")
    print(f"[cost_rollup]   Soft-flag at ${TRIGGER_FLAG_USD:.2f}")
    print(f"[cost_rollup]   Soft cap at  ${SOFT_CAP_USD:.2f}")
    print(f"[cost_rollup]   Hard cap at  ${HARD_CAP_USD:.2f}")

    if cumulative > TRIGGER_FLAG_USD:
        print(
            f"[cost_rollup] WARN: cumulative ${cumulative:.2f} > soft-flag "
            f"${TRIGGER_FLAG_USD:.2f}"
        )
    if cumulative > SOFT_CAP_USD:
        print(
            f"[cost_rollup] WARN: cumulative ${cumulative:.2f} > soft cap " f"${SOFT_CAP_USD:.2f}"
        )
        print("[cost_rollup] WARN: ADR-020 line 148 requires evals/cost_decisions.md entry")
    if args.check and cumulative > HARD_CAP_USD:
        print(
            f"[cost_rollup] FAIL: cumulative ${cumulative:.2f} > hard cap " f"${HARD_CAP_USD:.2f}"
        )
        print(
            "[cost_rollup] FAIL: ADR-020 line 148 requires superseding ADR "
            "before further GPU/API spend"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
