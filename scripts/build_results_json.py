"""Build evals/results.json from per_cell + marginal_cells parquets.

Per ADR-032 + ADR-034, the model-card schema needs headline metrics
(AUPRC + AUROC + recall@FPR1%) per (rung, slice) with 95% CI. This
script aggregates the existing per_cell.parquet + marginal_cells.parquet
into a single JSON suitable for the HF Hub model-card YAML
`model-index.results` field + the score-match contract.

Per Q10 lock: published rungs are frozen-probe + LoRA only (full-FT
weights missing locally per ADR-050).

Output schema
-------------
.. code-block:: json

    {
      "schema_version": "1.0",
      "generated_at_utc": "...",
      "git_sha": "...",
      "published_rungs": ["frozen-probe", "lora"],
      "score_match_tolerance": 1e-4,
      "per_rung": {
        "frozen-probe": {
          "contamination_tier": "backbone-partial-disjoint",
          "canonical_checkpoint": "fold0/seed42",
          "metrics": {
            "pooled_ood/auprc": {"point": 0.364, "ci_lo": 0.353, "ci_hi": 0.375},
            ...
          }
        },
        "lora": { ... }
      }
    }
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

PUBLISHED_RUNGS = ["frozen-probe", "lora"]
# per_cell.parquet + marginal_cells.parquet use the underscore form.
PUBLISHED_RUNG_KEYS = {"frozen-probe": "frozen_probe", "lora": "lora"}
CONTAMINATION_TIER = {
    "frozen-probe": "backbone-partial-disjoint",
    "lora": "backbone-partial-disjoint",
}
HEADLINE_SLICES = ["jbb_behaviors", "xstest", "pooled_ood"]
HEADLINE_METRICS = ["auprc", "auroc"]


def _git_sha() -> str:
    """Return current git HEAD short SHA, or 'unknown' if unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=_REPO_ROOT,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def main() -> int:
    """Aggregate per_cell + marginal_cells into evals/results.json."""
    per_cell = pd.read_parquet(_REPO_ROOT / "evals" / "metrics" / "per_cell.parquet")
    marginal = pd.read_parquet(_REPO_ROOT / "evals" / "bootstrap" / "marginal_cells.parquet")

    out: dict[str, object] = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": _git_sha(),
        "adr_ref": "ADR-032 + ADR-034 + ADR-050",
        "published_rungs": PUBLISHED_RUNGS,
        "score_match_tolerance": 1e-4,
        "per_rung": {},
    }

    per_rung_out: dict[str, dict[str, object]] = {}
    out["per_rung"] = per_rung_out
    for rung in PUBLISHED_RUNGS:
        rung_key = PUBLISHED_RUNG_KEYS[rung]
        rung_block: dict[str, object] = {
            "contamination_tier": CONTAMINATION_TIER[rung],
            "canonical_checkpoint": "fold0/seed42",
            "metrics": {},
        }

        metrics_block: dict[str, object] = {}
        rung_block["metrics"] = metrics_block
        # Per-(slice, metric) headline values from marginal_cells (CI-bearing)
        # at seed=1 (HEADLINE_SEED per ADR-022).
        for slice_name in HEADLINE_SLICES:
            for metric_name in HEADLINE_METRICS:
                mask = (
                    (marginal["rung"] == rung_key)
                    & (marginal["slice_name"] == slice_name)
                    & (marginal["metric"] == metric_name)
                    & (marginal["seed"] == 1)
                )
                rows = marginal[mask]
                if rows.empty:
                    continue
                row = rows.iloc[0]
                key = f"{slice_name}/{metric_name}"
                metrics_block[key] = {
                    "point": float(row["point_estimate"]),
                    "ci_lo": float(row["ci_lo"]),
                    "ci_hi": float(row["ci_hi"]),
                    "ci_method": str(row["ci_method"]),
                    "n_obs": int(row["n_obs"]),
                }

        # Per-rung mean recall@FPR1% (from per_cell aggregated across folds × seeds).
        pc_mask = (per_cell["rung"] == rung_key) & (per_cell["slice_name"].isin(HEADLINE_SLICES))
        pc_rows = per_cell[pc_mask]
        for slice_name in HEADLINE_SLICES:
            slice_rows = pc_rows[pc_rows["slice_name"] == slice_name]
            if slice_rows.empty:
                continue
            metrics_block[f"{slice_name}/recall_at_fpr_1_mean"] = float(
                slice_rows["recall_at_fpr_1"].mean()
            )
            metrics_block[f"{slice_name}/ece_equal_mass_mean"] = float(
                slice_rows["ece_equal_mass"].mean()
            )
            metrics_block[f"{slice_name}/brier_mean"] = float(slice_rows["brier"].mean())

        per_rung_out[rung] = rung_block

    out_path = _REPO_ROOT / "evals" / "results.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"[build-results-json] wrote {out_path}")
    print(f"  published rungs: {PUBLISHED_RUNGS}")
    fp_metrics = per_rung_out["frozen-probe"]["metrics"]
    assert isinstance(fp_metrics, dict)
    print(f"  per_rung[frozen-probe].metrics keys: {len(fp_metrics)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
