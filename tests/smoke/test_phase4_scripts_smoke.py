"""Smoke tests for Phase 4 Commit 5 orchestration scripts (per ADR-046).

Each CLI entrypoint runs as a subprocess against synthetic fixture predictions.
Matches the pattern in `tests/smoke/test_scripts_smoke.py` for Phase 3.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from tests.smoke.test_scripts_smoke import _make_predictions_parquet, _run_script

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# --------------------------------------------------------------------------- #
# run_marginal_bootstrap.py
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_run_marginal_bootstrap_end_to_end(tmp_path: Path) -> None:
    """Sweeps marginal CIs across (rung x slice x metric x seed)."""
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

    marginal_out = tmp_path / "bootstrap" / "marginal_cells.parquet"
    result = _run_script(
        "run_marginal_bootstrap.py",
        "--predictions-root",
        str(pred_dir),
        "--n-resamples",
        "200",
        "--seeds",
        "1,2",
        "--marginal-out",
        str(marginal_out),
    )
    assert result.returncode == 0, f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    assert marginal_out.exists()

    df = pd.read_parquet(marginal_out)
    assert len(df) > 0
    assert {"rung", "slice_name", "metric", "seed", "ci_lo", "ci_hi", "n_obs"}.issubset(df.columns)
    seeds_present = sorted(df["seed"].unique().tolist())
    assert seeds_present == [1, 2]


# --------------------------------------------------------------------------- #
# run_cv_clt_ci.py
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_run_cv_clt_ci_end_to_end(tmp_path: Path) -> None:
    """Sweeps cross-fold CIs; always emits cv_clt headline + block-bootstrap spoke."""
    pred_dir = tmp_path / "predictions"
    # Need >= 2 folds for cv_clt_ci.
    for fold in (0, 1, 2):
        _make_predictions_parquet(
            pred_dir / f"lora__fold{fold}__seed42.parquet",
            rung="lora",
            fold=fold,
            seed=42,
            epoch=2,
            contamination_state="backbone-partial-disjoint",
            random_seed=42 + fold,
        )

    audit_out = tmp_path / "audit" / "cross_fold_ci_audit.parquet"
    result = _run_script(
        "run_cv_clt_ci.py",
        "--predictions-root",
        str(pred_dir),
        "--block-n-resamples",
        "500",
        "--audit-out",
        str(audit_out),
    )
    assert result.returncode == 0, f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    assert audit_out.exists()

    df = pd.read_parquet(audit_out)
    assert len(df) > 0
    # Commit 3 contract — both cv_clt + block fields must be populated.
    assert df["cv_clt_ci_lo"].notna().all()
    assert df["cv_clt_ci_hi"].notna().all()
    assert df["block_bootstrap_ci_lo"].notna().all()
    assert df["block_bootstrap_ci_hi"].notna().all()
    assert df["a_008_flag_fired"].notna().all()


# --------------------------------------------------------------------------- #
# run_mde.py
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_run_mde_end_to_end(tmp_path: Path) -> None:
    """Aggregates MDE cells from marginal + cross-fold parquets to evals/audit/."""
    # Build a tiny marginal_cells.parquet by hand (avoid running run_marginal_bootstrap).
    marginal_path = tmp_path / "bootstrap" / "marginal_cells.parquet"
    marginal_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "rung": "lora",
                "slice_name": "iid",
                "metric": "auprc",
                "n_resamples": 1000,
                "seed": 1,
                "point_estimate": 0.85,
                "ci_lo": 0.80,
                "ci_hi": 0.90,
                "ci_method": "bca",
                "n_obs": 400,
            },
            {
                "rung": "frozen_probe",
                "slice_name": "iid",
                "metric": "auprc",
                "n_resamples": 1000,
                "seed": 1,
                "point_estimate": 0.75,
                "ci_lo": 0.70,
                "ci_hi": 0.80,
                "ci_method": "bca",
                "n_obs": 400,
            },
        ]
    ).to_parquet(marginal_path, index=False)

    # Build a tiny cross_fold_ci_audit.parquet by hand.
    cf_path = tmp_path / "audit" / "cross_fold_ci_audit.parquet"
    cf_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "rung": "lora",
                "slice_name": "iid",
                "metric": "auprc",
                "k_folds": 4,
                "n_seeds_per_fold": 3,
                "cv_clt_point_estimate": 0.85,
                "cv_clt_ci_lo": 0.80,
                "cv_clt_ci_hi": 0.90,
                "cv_clt_ci_halfwidth": 0.05,
                "block_bootstrap_ci_lo": 0.78,
                "block_bootstrap_ci_hi": 0.92,
                "block_bootstrap_ci_halfwidth": 0.07,
                "block_bootstrap_n_resamples": 1000,
                "a_008_flag_fired": False,
            }
        ]
    ).to_parquet(cf_path, index=False)

    mde_out = tmp_path / "audit" / "mde_per_cell.parquet"
    paired_path = tmp_path / "bootstrap" / "paired_cells_missing.parquet"  # absent on purpose
    result = _run_script(
        "run_mde.py",
        "--paired-parquet",
        str(paired_path),
        "--marginal-parquet",
        str(marginal_path),
        "--cross-fold-parquet",
        str(cf_path),
        "--mde-out",
        str(mde_out),
    )
    assert result.returncode == 0, f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    assert mde_out.exists()

    df = pd.read_parquet(mde_out)
    # Expect 2 marginal + 2 cross-fold (cv_clt + block) = 4 cells minimum.
    assert len(df) >= 4
    kinds = set(df["source_ci_kind"].unique())
    assert "marginal_bootstrap" in kinds
    assert "cv_clt" in kinds
    assert "block_bootstrap" in kinds


# --------------------------------------------------------------------------- #
# render_figures.py
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_render_figures_scaffold_writes_7_svgs(tmp_path: Path) -> None:
    """Scaffold path writes docs/plots/F{1..7}.svg + per-figure .meta.json sidecars."""
    out_dir = tmp_path / "docs_plots"
    result = _run_script(
        "render_figures.py",
        "--scaffold",
        "--out-dir",
        str(out_dir),
    )
    assert result.returncode == 0, f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"

    svgs = sorted(out_dir.glob("F*.svg"))
    assert len(svgs) == 7
    names = sorted(p.name for p in svgs)
    assert names == ["F1.svg", "F2.svg", "F3.svg", "F4.svg", "F5.svg", "F6.svg", "F7.svg"]

    # Every SVG has a .meta.json sidecar carrying provenance per ADR-030.
    for svg in svgs:
        sidecar = svg.parent / f"{svg.stem}.meta.json"
        assert sidecar.exists(), f"missing sidecar: {sidecar}"
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
        assert meta["figure_id"] == svg.stem
        assert meta["adr"] == "ADR-046"
        assert "commit_sha" in meta
        assert "generated_at" in meta


# --------------------------------------------------------------------------- #
# audit_reference_scorers.py — dry-run only (live judge calls cost-gated)
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_audit_reference_scorers_dry_run_smoke(tmp_path: Path) -> None:
    """--dry-run prints cost preview + exits without LLM calls."""
    pred_dir = tmp_path / "predictions"
    # Need both reference + trained rungs for disagreement sampling.
    for fold in (0,):
        _make_predictions_parquet(
            pred_dir / f"R-LLM-OpenAI__fold{fold}__seed42.parquet",
            rung="R-LLM-OpenAI",
            fold=fold,
            seed=42,
            epoch=None,
            contamination_state="vendor_black_box",
            random_seed=11 + fold,
        )
        _make_predictions_parquet(
            pred_dir / f"lora__fold{fold}__seed42.parquet",
            rung="lora",
            fold=fold,
            seed=42,
            epoch=2,
            contamination_state="backbone-partial-disjoint",
            random_seed=22 + fold,
        )

    audit_out = tmp_path / "audit" / "reference_scorer_rater_audit.json"
    result = _run_script(
        "audit_reference_scorers.py",
        "--predictions-root",
        str(pred_dir),
        "--reference-rungs",
        "R-LLM-OpenAI",
        "--trained-rung-for-disagreement",
        "lora",
        "--n-pairs-per-rung",
        "5",
        "--audit-out",
        str(audit_out),
        "--dry-run",
    )
    assert result.returncode == 0, f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    # Dry run -> no audit JSON written.
    assert not audit_out.exists()
    assert "DRY RUN" in result.stderr
