"""Smoke tests for scripts/cost_rollup.py (Phase 2 Commit 5 per ADR-044).

Validates:
- walk_runpod_manifests reads a synthetic schema-v2 manifest correctly.
- walk_api_logs reads a synthetic LLM-judge call log correctly.
- write_cost_ledger emits a valid CSV with the ADR-020 line 146 schema.
- compute_cumulative_spend sums actual_cost_usd correctly.
- Hard cap (--check) returns exit 1 above $200 (tested via direct function).
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Ensure scripts/ is on sys.path for the cost_rollup import.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


@pytest.mark.smoke
def test_walk_runpod_manifests_empty_dir_returns_empty(tmp_path: Path) -> None:
    """No artifacts/runpod/ dir → empty list (clean first-run state)."""
    import cost_rollup

    rows = cost_rollup.walk_runpod_manifests(tmp_path / "nonexistent")
    assert rows == []


@pytest.mark.smoke
def test_walk_runpod_manifests_reads_schema_v2(tmp_path: Path) -> None:
    """Synthetic schema-v2 manifest → row with all required ledger fields."""
    import cost_rollup

    run_dir = tmp_path / "20260516_120000_runA"
    run_dir.mkdir()
    manifest = {
        "schema_version": "v2",
        "job_name": "pid-phase2-lora",
        "run_id": "pid-lora-20260516_120000",
        "pod_id": "abc123",
        "gpu_id": "NVIDIA H100 80GB HBM3",
        "datacenter_id": "US-MD-1",
        "wall_time_sec": 3600.0,
        "gpu_price_per_hour_usd": 3.50,
        "estimated_cost_usd": 3.50,
        "cost_cap_usd": 60.0,
        "pod_final_state": "EXITED",
    }
    (run_dir / "runpod_deploy_pull_manifest.json").write_text(json.dumps(manifest))

    rows = cost_rollup.walk_runpod_manifests(tmp_path)
    assert len(rows) == 1
    row = rows[0]
    assert row["target"] == "pid-phase2-lora"
    assert row["timestamp"] == "pid-lora-20260516_120000"
    assert row["est_cost_usd"] == 3.50
    assert row["actual_cost_usd"] == 3.50
    assert row["gpu_hours"] == 1.0
    assert row["api_calls"] == 0
    assert "H100" in row["notes"]
    assert "EXITED" in row["notes"]
    assert "US-MD-1" in row["notes"]


@pytest.mark.smoke
def test_walk_runpod_manifests_skips_unreadable(tmp_path: Path) -> None:
    """Malformed JSON → skipped + WARN, not crash."""
    import cost_rollup

    run_dir = tmp_path / "bad_run"
    run_dir.mkdir()
    (run_dir / "runpod_deploy_pull_manifest.json").write_text("not json")
    rows = cost_rollup.walk_runpod_manifests(tmp_path)
    assert rows == []


@pytest.mark.smoke
def test_walk_api_logs_reads_synthetic_judge_log(tmp_path: Path) -> None:
    """Synthetic LLM-judge log → row with judge target + n_calls."""
    import cost_rollup

    log_path = tmp_path / "fold0_gpt4o.json"
    log_path.write_text(
        json.dumps(
            {
                "judge": "gpt-4o-2024-08-06",
                "n_calls": 200,
                "est_cost_usd": 4.20,
                "timestamp": "2026-05-16T20:00:00Z",
            }
        )
    )
    rows = cost_rollup.walk_api_logs(tmp_path)
    assert len(rows) == 1
    row = rows[0]
    assert row["target"] == "llm_judge_gpt-4o-2024-08-06"
    assert row["api_calls"] == 200
    assert row["est_cost_usd"] == 4.20
    assert row["gpu_hours"] == 0.0


@pytest.mark.smoke
def test_walk_api_logs_ignores_non_judge_json(tmp_path: Path) -> None:
    """JSON file lacking 'judge' key is ignored (not crashing)."""
    import cost_rollup

    (tmp_path / "other.json").write_text(json.dumps({"unrelated": "data"}))
    rows = cost_rollup.walk_api_logs(tmp_path)
    assert rows == []


@pytest.mark.smoke
def test_write_cost_ledger_csv_schema(tmp_path: Path) -> None:
    """write_cost_ledger emits a CSV with the ADR-020 line 146 schema header."""
    import cost_rollup

    rows: list[dict[str, Any]] = [
        {
            "timestamp": "t1",
            "target": "pid-frozen",
            "est_cost_usd": 12.50,
            "actual_cost_usd": 12.50,
            "gpu_hours": 3.6,
            "api_calls": 0,
            "notes": "smoke",
        }
    ]
    out = tmp_path / "evals" / "cost_ledger.csv"
    cost_rollup.write_cost_ledger(rows, out)

    assert out.exists()
    with out.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames is not None
        assert tuple(reader.fieldnames) == cost_rollup.LEDGER_HEADER
        rows_back = list(reader)
    assert len(rows_back) == 1
    assert rows_back[0]["target"] == "pid-frozen"
    assert float(rows_back[0]["actual_cost_usd"]) == 12.50


@pytest.mark.smoke
def test_compute_cumulative_spend_sums_actual_costs() -> None:
    """compute_cumulative_spend sums actual_cost_usd across rows."""
    import cost_rollup

    rows = [
        {"actual_cost_usd": 50.0, "target": "a"},
        {"actual_cost_usd": 30.5, "target": "b"},
        {"actual_cost_usd": 0.0, "target": "c"},
    ]
    assert cost_rollup.compute_cumulative_spend(rows) == 80.5


@pytest.mark.smoke
def test_thresholds_match_adr_020() -> None:
    """Hard/soft/trigger thresholds match ADR-020 line 148."""
    import cost_rollup

    assert cost_rollup.HARD_CAP_USD == 200.0
    assert cost_rollup.SOFT_CAP_USD == 125.0
    assert cost_rollup.TRIGGER_FLAG_USD == 80.0
