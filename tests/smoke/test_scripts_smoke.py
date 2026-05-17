"""Smoke tests for Phase 3 Commit 5 orchestration scripts.

Tests each CLI entrypoint as a subprocess (matching how `make eval-*`
targets will invoke them) against synthetic fixture predictions.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _make_predictions_parquet(
    out_path: Path,
    *,
    rung: str,
    fold: int,
    seed: int,
    epoch: int | None,
    contamination_state: str,
    n_iid_per_class: int = 80,
    n_per_ood_slice: int = 60,
    sources_iid: tuple[str, ...] = ("ultrachat_200k", "lmsys_chat_1m", "deepset_prompt_injections"),
    sources_ood: tuple[str, ...] = ("notinject", "xstest", "jbb_behaviors", "bipia", "injecagent"),
    random_seed: int = 42,
) -> None:
    """Write a synthetic predictions parquet matching PredictionsRowModel."""
    rng = np.random.default_rng(random_seed)
    rows: list[dict[str, object]] = []
    row_counter = 0
    for src in sources_iid:
        for _ in range(n_iid_per_class):
            label = int(rng.integers(0, 2))
            score = float(rng.uniform(0.6, 0.99) if label == 1 else rng.uniform(0.01, 0.4))
            rows.append(
                {
                    "rung": rung,
                    "fold": fold,
                    "seed": seed,
                    "epoch": epoch,
                    "row_idx_in_source": row_counter,
                    "source": src,
                    "text": f"iid-{src}-{row_counter}",
                    "label": label,
                    "predicted_proba_class1": score,
                    "contamination_state": contamination_state,
                }
            )
            row_counter += 1
    for src in sources_ood:
        for i in range(n_per_ood_slice):
            label = int(rng.integers(0, 2))
            score = float(rng.uniform(0.55, 0.95) if label == 1 else rng.uniform(0.05, 0.45))
            rows.append(
                {
                    "rung": rung,
                    "fold": fold,
                    "seed": seed,
                    "epoch": epoch,
                    "row_idx_in_source": i,
                    "source": src,
                    "text": f"ood-{src}-{i}",
                    "label": label,
                    "predicted_proba_class1": score,
                    "contamination_state": contamination_state,
                }
            )
    df = pd.DataFrame(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)


def _run_script(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a Phase 3 script via subprocess; return CompletedProcess."""
    cmd = [sys.executable, str(_REPO_ROOT / "scripts" / script), *args]
    return subprocess.run(  # noqa: S603 — controlled args
        cmd,
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )


# --------------------------------------------------------------------------- #
# run_metrics_battery.py
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_run_metrics_battery_end_to_end(tmp_path: Path) -> None:
    """run_metrics_battery emits per-(rung, fold, seed, slice) records + pooled-OOD."""
    pred_dir = tmp_path / "predictions"
    for fold in (0, 1):
        _make_predictions_parquet(
            pred_dir / f"lora__fold{fold}__seed42.parquet",
            rung="lora",
            fold=fold,
            seed=42,
            epoch=2,
            contamination_state="backbone-partial-disjoint",
            random_seed=42 + fold,
        )

    metrics_out = tmp_path / "metrics" / "per_cell.parquet"
    result = _run_script(
        "run_metrics_battery.py",
        "--predictions-root",
        str(pred_dir),
        "--metrics-out",
        str(metrics_out),
    )
    assert result.returncode == 0, f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    assert metrics_out.exists()

    df = pd.read_parquet(metrics_out)
    assert len(df) > 0
    # Expect 2 (folds) × 1 (rung) × (1 iid + 5 per-slice + 1 pooled_ood) = 14 rows
    slice_names = set(df["slice_name"].unique())
    assert "iid" in slice_names
    assert "pooled_ood" in slice_names
    assert "bipia" in slice_names


# --------------------------------------------------------------------------- #
# fit_dual_policy_thresholds.py
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_fit_dual_policy_thresholds_end_to_end(tmp_path: Path) -> None:
    """fit_dual_policy_thresholds emits operating points + reachability audit."""
    val_dir = tmp_path / "predictions_val"
    test_dir = tmp_path / "predictions"
    for fold in (0, 1):
        _make_predictions_parquet(
            val_dir / f"lora__fold{fold}__seed42.parquet",
            rung="lora",
            fold=fold,
            seed=42,
            epoch=2,
            contamination_state="backbone-partial-disjoint",
            random_seed=100 + fold,
        )
        _make_predictions_parquet(
            test_dir / f"lora__fold{fold}__seed42.parquet",
            rung="lora",
            fold=fold,
            seed=42,
            epoch=2,
            contamination_state="backbone-partial-disjoint",
            random_seed=200 + fold,
        )

    ops_out = tmp_path / "operating_points" / "dual_policy.parquet"
    audit_out = tmp_path / "audit" / "verification_reachability.json"
    result = _run_script(
        "fit_dual_policy_thresholds.py",
        "--val-root",
        str(val_dir),
        "--test-root",
        str(test_dir),
        "--operating-points-out",
        str(ops_out),
        "--reachability-audit-out",
        str(audit_out),
    )
    assert result.returncode == 0, f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    assert ops_out.exists()
    assert audit_out.exists()

    op_df = pd.read_parquet(ops_out)
    # 2 folds × 1 seed × 2 policies = 4 rows
    assert len(op_df) == 4
    assert set(op_df["policy"].unique()) == {"detection", "verification"}

    with audit_out.open() as fh:
        audit = json.load(fh)
    assert "lora" in audit


@pytest.mark.smoke
def test_fit_dual_policy_excludes_reference_rungs(tmp_path: Path) -> None:
    """Reference scorers (suspected_contamination + vendor_black_box) skipped per SPEC §4."""
    val_dir = tmp_path / "predictions_val"
    test_dir = tmp_path / "predictions"
    _make_predictions_parquet(
        val_dir / "lora__fold0__seed42.parquet",
        rung="lora",
        fold=0,
        seed=42,
        epoch=2,
        contamination_state="backbone-partial-disjoint",
        random_seed=10,
    )
    _make_predictions_parquet(
        val_dir / "protectai-v1__fold-1__seed-1.parquet",
        rung="protectai-v1",
        fold=-1,
        seed=-1,
        epoch=None,
        contamination_state="suspected_contamination",
        random_seed=11,
    )
    _make_predictions_parquet(
        test_dir / "lora__fold0__seed42.parquet",
        rung="lora",
        fold=0,
        seed=42,
        epoch=2,
        contamination_state="backbone-partial-disjoint",
        random_seed=12,
    )
    _make_predictions_parquet(
        test_dir / "protectai-v1__fold-1__seed-1.parquet",
        rung="protectai-v1",
        fold=-1,
        seed=-1,
        epoch=None,
        contamination_state="suspected_contamination",
        random_seed=13,
    )

    ops_out = tmp_path / "operating_points" / "dual_policy.parquet"
    audit_out = tmp_path / "audit" / "verification_reachability.json"
    result = _run_script(
        "fit_dual_policy_thresholds.py",
        "--val-root",
        str(val_dir),
        "--test-root",
        str(test_dir),
        "--operating-points-out",
        str(ops_out),
        "--reachability-audit-out",
        str(audit_out),
    )
    assert result.returncode == 0
    op_df = pd.read_parquet(ops_out)
    # Only LoRA × 1 fold × 1 seed × 2 policies = 2 rows; protectai-v1 must be skipped.
    assert (op_df["rung"] == "lora").all()


# --------------------------------------------------------------------------- #
# run_bootstrap_battery.py
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_run_bootstrap_battery_persists_full_pairwise(tmp_path: Path) -> None:
    """Bootstrap battery emits paired-bootstrap CIs for every rung × rung × slice cell.

    Per ADR-045 Q6 user refinement, persistence is full-pairwise (NOT only the
    3 headline comparisons); the WRITEUP narrative subsets at report time.
    """
    pred_dir = tmp_path / "predictions"
    for rung in ("frozen-probe", "lora", "full-ft"):
        _make_predictions_parquet(
            pred_dir / f"{rung}__fold0__seed42.parquet",
            rung=rung,
            fold=0,
            seed=42,
            epoch=2,
            contamination_state="backbone-partial-disjoint",
            random_seed=hash(rung) % 1000,
        )

    out_path = tmp_path / "bootstrap" / "paired_cells.parquet"
    result = _run_script(
        "run_bootstrap_battery.py",
        "--predictions-root",
        str(pred_dir),
        "--metrics",
        "auprc,auroc",
        "--n-resamples",
        "100",
        "--seed",
        "1",
        "--bootstrap-out",
        str(out_path),
    )
    assert result.returncode == 0, f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    assert out_path.exists()

    df = pd.read_parquet(out_path)
    # 3 rungs → C(3, 2) = 3 pairwise × N slices × 2 metrics ≥ 6 cells.
    assert len(df) >= 6
    # Headline-pair comparison present.
    pairs = {(r["rung_a"], r["rung_b"]) for _, r in df.iterrows()}
    assert ("frozen-probe", "lora") in pairs or ("lora", "frozen-probe") in pairs


# --------------------------------------------------------------------------- #
# eval_from_hub.py — T0 dry-run
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_eval_from_hub_dry_run() -> None:
    """eval_from_hub --dry-run resolves repo_id without HF download (T0 stub gate)."""
    result = _run_script(
        "eval_from_hub.py",
        "--rung",
        "lora",
        "--dry-run",
    )
    assert result.returncode == 0
    assert "BBehring/prompt-injection-lora" in result.stdout
