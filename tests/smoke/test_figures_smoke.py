"""Smoke tests for src/eval/figures.py (Phase 4 Commit 4 per ADR-046 Q6)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # noqa: E402 — headless backend for CI / smoke runs

import matplotlib.pyplot as plt
import numpy as np
import pytest
from eval_toolkit.bootstrap import BootstrapCI, bootstrap_ci
from eval_toolkit.metrics import pr_auc
from eval_toolkit.plotting import save_figure
from matplotlib.figure import Figure

from src.eval.figures import (
    FIGURE_OUTPUT_DIR_DEFAULT,
    FIGURE_SLATE_NAMES,
    render_f1_pareto,
    render_f2_roc_per_rung,
    render_f3_pr_per_rung,
    render_f4_reliability_triptych,
    render_f5_slice_heatmap,
    render_f6_lodo_breakdown,
    render_f7_dual_policy_grid,
)


# --------------------------------------------------------------------------- #
# Synthetic data helpers
# --------------------------------------------------------------------------- #


def _synth_rung_predictions(
    rungs: tuple[str, ...] = ("classical_floor", "frozen_probe", "lora", "full_ft"),
    n: int = 200,
    seed: int = 0,
) -> dict[str, tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]]:
    rng = np.random.default_rng(seed)
    out: dict[str, tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]] = {}
    for i, rung in enumerate(rungs):
        y = rng.integers(0, 2, size=n)
        # Better-performing rungs get tighter noise.
        s = np.clip(y + rng.normal(0, 0.40 - 0.05 * i, size=n), 0.001, 0.999)
        out[rung] = (y.astype(np.int_), s.astype(np.float64))
    return out


def _synth_marginal_ci(seed: int) -> BootstrapCI:
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, size=200).astype(np.int_)
    s = np.clip(y + rng.normal(0, 0.3, size=200), 0.001, 0.999)
    return bootstrap_ci(y, s, metric=pr_auc, n_resamples=200, seed=seed)


# --------------------------------------------------------------------------- #
# Slate constants
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_figure_slate_names_are_f1_through_f5() -> None:
    assert FIGURE_SLATE_NAMES == ("F1", "F2", "F3", "F4", "F5")


@pytest.mark.smoke
def test_figure_output_dir_default_matches_quarto_embedding_path() -> None:
    """ADR-030 Quarto site embeds figures from `docs/plots/`."""
    assert FIGURE_OUTPUT_DIR_DEFAULT == "docs/plots"


# --------------------------------------------------------------------------- #
# F1 — Pareto frontier (project glue)
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_render_f1_pareto_returns_figure() -> None:
    fig = render_f1_pareto(
        rung_to_auprc={"a": 0.70, "b": 0.85, "c": 0.90, "d": 0.92},
        rung_to_compute={"a": 1.0, "b": 5.0, "c": 50.0, "d": 200.0},
    )
    assert isinstance(fig, Figure)
    plt.close(fig)


@pytest.mark.smoke
def test_render_f1_pareto_rejects_disjoint_keys() -> None:
    with pytest.raises(ValueError, match="No rung keys"):
        render_f1_pareto(rung_to_auprc={"a": 0.5}, rung_to_compute={"b": 1.0})


# --------------------------------------------------------------------------- #
# F2 — ROC overlay (project glue)
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_render_f2_roc_per_rung_returns_figure() -> None:
    fig = render_f2_roc_per_rung(rung_to_y_score=_synth_rung_predictions())
    assert isinstance(fig, Figure)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# F3 — PR per rung (library-first direct)
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_render_f3_pr_per_rung_returns_figure() -> None:
    fig = render_f3_pr_per_rung(rung_to_y_score=_synth_rung_predictions())
    assert isinstance(fig, Figure)
    plt.close(fig)


@pytest.mark.smoke
def test_render_f3_pr_per_rung_empty_input_raises() -> None:
    with pytest.raises(ValueError, match="No rungs"):
        render_f3_pr_per_rung(rung_to_y_score={})


# --------------------------------------------------------------------------- #
# F4 — Reliability triptych (library-first 3-panel)
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_render_f4_reliability_triptych_returns_figure() -> None:
    rng = np.random.default_rng(0)
    n = 300
    y = rng.integers(0, 2, size=n).astype(np.int_)
    p_raw = np.clip(y + rng.normal(0, 0.3, size=n), 0.001, 0.999)
    p_temp = np.clip(p_raw + rng.normal(0, 0.05, size=n), 0.001, 0.999)
    p_iso = np.clip(p_raw + rng.normal(0, 0.04, size=n), 0.001, 0.999)
    fig = render_f4_reliability_triptych(
        y_true=y, y_prob_raw=p_raw, y_prob_temperature=p_temp, y_prob_isotonic=p_iso, n_bins=10
    )
    assert isinstance(fig, Figure)
    assert len(fig.get_axes()) >= 3
    plt.close(fig)


# --------------------------------------------------------------------------- #
# F5 — Per-slice heatmap (project glue)
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_render_f5_slice_heatmap_returns_figure() -> None:
    grid = np.array([[0.80, 0.82, 0.78], [0.85, 0.88, 0.83], [0.90, 0.91, 0.89]])
    fig = render_f5_slice_heatmap(
        metric_grid=grid,
        row_labels=["frozen", "lora", "full"],
        col_labels=["iid", "ood", "pooled"],
    )
    assert isinstance(fig, Figure)
    plt.close(fig)


@pytest.mark.smoke
def test_render_f5_slice_heatmap_shape_mismatch_raises() -> None:
    grid = np.zeros((2, 3))
    # Upstream eval-toolkit v0.33.0 plot_slice_metric_heatmap message:
    # "row_labels length 1 != grid.shape[0] 2". Match loosely.
    with pytest.raises(ValueError, match=r"row_labels|does not match|shape"):
        render_f5_slice_heatmap(metric_grid=grid, row_labels=["a"], col_labels=["b", "c", "d"])


# --------------------------------------------------------------------------- #
# F6 — LODO breakdown (diagnostic/historical; #22 consumed at v1.2.2)
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_render_f6_lodo_breakdown_returns_figure() -> None:
    fig = render_f6_lodo_breakdown(
        per_fold_means={"fold0": 0.80, "fold1": 0.85, "fold2": 0.78, "fold3": 0.82},
        rung_to_marginal_ci={
            "frozen_probe": _synth_marginal_ci(1),
            "lora": _synth_marginal_ci(2),
        },
    )
    assert isinstance(fig, Figure)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# F7 — Dual-policy grid (library-first sub-panels + project glue grid)
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_render_f7_dual_policy_grid_returns_figure() -> None:
    rng = np.random.default_rng(0)
    detection = {
        "frozen_probe": rng.normal(0.02, 0.01, size=200),
        "lora": rng.normal(0.03, 0.01, size=200),
    }
    verification = {
        "frozen_probe": rng.normal(0.01, 0.008, size=200),
        "lora": rng.normal(0.02, 0.009, size=200),
    }
    reachable = {"frozen_probe": True, "lora": False}
    fig = render_f7_dual_policy_grid(
        rung_to_detection_deltas=detection,
        rung_to_verification_deltas=verification,
        rung_to_reachable=reachable,
    )
    assert isinstance(fig, Figure)
    plt.close(fig)


@pytest.mark.smoke
def test_render_f7_dual_policy_grid_empty_rungs_raises() -> None:
    with pytest.raises(ValueError, match="No rungs"):
        render_f7_dual_policy_grid(
            rung_to_detection_deltas={},
            rung_to_verification_deltas={},
            rung_to_reachable={},
        )


# --------------------------------------------------------------------------- #
# save_figure provenance + SVG output round-trip
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_save_figure_writes_svg_with_provenance_sidecar(tmp_path: Path) -> None:
    """eval_toolkit.plotting.save_figure writes SVG + provenance sidecar JSON.

    Per upstream save_figure semantics: PNG iTXt chunks for .png, and a
    sibling ``{stem}.meta.json`` sidecar for .svg / .pdf / .png. The sidecar
    contains caller-supplied provenance keys plus auto-fields (timestamp_utc,
    matplotlib_version, figure_dpi).
    """
    import json

    fig = render_f3_pr_per_rung(rung_to_y_score=_synth_rung_predictions())
    out_path = tmp_path / "F3.svg"
    saved = save_figure(
        fig,
        out_path,
        dpi=100,
        provenance={
            "figure_id": "F3",
            "adr": "ADR-046",
            "commit": "phase4-commit4-smoke",
        },
    )
    assert saved.exists()
    sidecar = saved.parent / f"{saved.stem}.meta.json"
    assert sidecar.exists(), f"Expected sidecar at {sidecar}"
    meta = json.loads(sidecar.read_text(encoding="utf-8"))
    assert meta["figure_id"] == "F3"
    assert meta["adr"] == "ADR-046"
    assert "timestamp_utc" in meta
    assert "matplotlib_version" in meta
    plt.close(fig)
