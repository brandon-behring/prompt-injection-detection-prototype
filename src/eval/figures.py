"""Phase 4 figures library-first hybrid 7-figure slate per ADR-046 Q6 + ADR-030.

The Phase 4 figures slate ships 7 SVG plots embedded by the Quarto site at
`docs/plots/F{1..7}.svg`. Per the project-wide library-first invariant
(memory entry `library-first-is-project-wide-invariant` 2026-05-16),
`eval_toolkit.plotting` is the first port of call for each figure. The
upstream gaps surfaced by F1 + F2 + F5 are filed at eval-toolkit issues
#14 + #15 + #16 with project-glue fallbacks below pending upstream landing.

| Figure | Subject | Render path |
|---|---|---|
| F1 | Pareto frontier — AUPRC vs compute | project glue (issue #15) |
| F2 | ROC per rung | project glue (issue #14 + PR candidate) |
| F3 | Precision-recall per rung | `eval_toolkit.plotting.plot_pr_curve` |
| F4 | Reliability triptych — raw + temperature + isotonic | `plot_reliability_diagram` x3 |
| F5 | Per-slice OOD heatmap | project glue (issue #16) |
| F6 | LODO fold variance breakdown | `plot_metric_bars` + `plot_lift_ci` |
| F7 | Dual-policy operating-point grid w/ reachability flags | project glue + `plot_bootstrap_distribution` |

All renderers consume `set_plot_style` + `PALETTE` + `save_figure` so the
output carries the upstream provenance metadata chunks per ADR-030. Output
format defaults to SVG (per ADR-030 Quarto embedding); `save_figure` accepts
`.svg | .png | .pdf` via its `permitted_suffixes` argument.

The renderers below all return a `matplotlib.figure.Figure` so the caller
(typically `scripts/render_figures.py` in Commit 5) can decide where to
write each figure. The `save_figure` step is decoupled to keep this module
plot-only — callers pass the result to `eval_toolkit.plotting.save_figure`
with the desired output path + provenance dict.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final

import matplotlib.pyplot as plt
import numpy as np
from eval_toolkit.bootstrap import BootstrapCI
from eval_toolkit.plotting import (
    PALETTE,
    plot_bootstrap_distribution,
    plot_lift_ci,
    plot_pr_curve,
    plot_reliability_diagram,
    set_plot_style,
)
from matplotlib.figure import Figure
from numpy.typing import NDArray

# Output destination convention per ADR-030 Quarto site embedding.
FIGURE_OUTPUT_DIR_DEFAULT: Final[str] = "docs/plots"
FIGURE_SLATE_NAMES: Final[tuple[str, ...]] = ("F1", "F2", "F3", "F4", "F5", "F6", "F7")


# --------------------------------------------------------------------------- #
# F1 — Pareto frontier (AUPRC vs compute)
# Project glue per ADR-046 Q6; pending upstream eval-toolkit issue #15
# (`plot_pareto_frontier` for cost-vs-performance scatter with frontier overlay).
# --------------------------------------------------------------------------- #


def render_f1_pareto(
    *,
    rung_to_auprc: Mapping[str, float],
    rung_to_compute: Mapping[str, float],
    title: str = "Pareto frontier — AUPRC vs compute",
    figsize: tuple[float, float] = (7.0, 5.0),
) -> Figure:
    """Scatter rungs in (compute, AUPRC) space; overlay Pareto frontier.

    Project glue per ADR-046 Q6: domain inputs (per-rung dicts) → key
    intersection → numpy arrays → upstream `plot_pareto_frontier`.
    eval-toolkit v0.34.0 (closes #15) ships the primitive — this body
    is now just the dict → array adapter + axis label setup.
    """
    from eval_toolkit import plot_pareto_frontier

    set_plot_style()

    keys = sorted(set(rung_to_auprc) & set(rung_to_compute))
    if not keys:
        raise ValueError("No rung keys appear in both rung_to_auprc and rung_to_compute.")

    xs = np.array([rung_to_compute[k] for k in keys], dtype=np.float64)
    ys = np.array([rung_to_auprc[k] for k in keys], dtype=np.float64)

    fig = plot_pareto_frontier(
        cost=xs,
        metric=ys,
        point_labels=keys,
        higher_metric_is_better=True,  # AUPRC higher = better
        title=title,
        figsize=figsize,
    )
    # Domain-specific axis labels (upstream is metric-agnostic).
    ax = fig.axes[0]
    ax.set_xlabel("Compute (training cost proxy)")
    ax.set_ylabel("AUPRC")
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# F2 — ROC per rung
# Project glue per ADR-046 Q6; pending upstream eval-toolkit issue #14
# (`plot_roc_curve` sibling to `plot_pr_curve`).
# --------------------------------------------------------------------------- #


def render_f2_roc_per_rung(
    *,
    rung_to_y_score: Mapping[str, tuple[NDArray[np.int_], NDArray[np.float64]]],
    title: str = "ROC per rung",
    figsize: tuple[float, float] = (7.0, 5.5),
) -> Figure:
    """One-axes ROC overlay for all rungs via `eval_toolkit.plot_roc_curve`.

    Library-first direct dispatch (mirrors F3's `plot_pr_curve` loop) —
    looped over rungs onto a shared axes via the `ax` kwarg per the
    upstream API. eval-toolkit v0.33.0 (closes #14) ships
    `plot_roc_curve` as the sibling primitive; no project glue beyond
    the loop + axis title.
    """
    from eval_toolkit import plot_roc_curve

    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    fig_returned: Figure | None = None
    for rung, (y_true, y_score) in rung_to_y_score.items():
        fig_returned = plot_roc_curve(y_true, y_score, label=rung, ax=ax)
    ax.set_title(title)
    fig.tight_layout()
    return fig_returned if fig_returned is not None else fig


# --------------------------------------------------------------------------- #
# F3 — PR per rung (library-first direct dispatch)
# --------------------------------------------------------------------------- #


def render_f3_pr_per_rung(
    *,
    rung_to_y_score: Mapping[str, tuple[NDArray[np.int_], NDArray[np.float64]]],
    threshold: float | None = None,
    prevalence: float | None = None,
    title: str = "Precision-recall per rung",
    figsize: tuple[float, float] = (7.0, 5.5),
) -> Figure:
    """Overlay PR curves for each rung via `eval_toolkit.plotting.plot_pr_curve`.

    Library-first direct dispatch — looped over rungs onto a shared axes via
    the `ax` kwarg per the upstream API. No project glue beyond the loop.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    fig_returned: Figure | None = None
    for rung, (y_true, y_score) in rung_to_y_score.items():
        fig_returned = plot_pr_curve(
            y_true,
            y_score,
            label=rung,
            threshold=threshold,
            prevalence=prevalence,
            ax=ax,
        )
    if fig_returned is None:
        raise ValueError("No rungs supplied to render_f3_pr_per_rung.")
    ax.set_title(title)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# F4 — Reliability triptych (raw + temperature + isotonic) — library-first
# --------------------------------------------------------------------------- #


def render_f4_reliability_triptych(
    *,
    y_true: NDArray[np.int_],
    y_prob_raw: NDArray[np.float64],
    y_prob_temperature: NDArray[np.float64],
    y_prob_isotonic: NDArray[np.float64],
    n_bins: int = 15,
    title: str = "Reliability — raw vs temperature vs isotonic",
    figsize: tuple[float, float] = (12.0, 4.5),
) -> Figure:
    """Three-panel reliability diagram via `plot_reliability_diagram` per intervention.

    Library-first per ADR-046 Q6 — upstream `plot_reliability_diagram` invoked
    once per intervention onto a shared 1x3 subplot grid.
    """
    set_plot_style()
    fig, axes = plt.subplots(1, 3, figsize=figsize, sharey=True)

    panels = (
        ("raw", y_prob_raw),
        ("temperature", y_prob_temperature),
        ("isotonic", y_prob_isotonic),
    )
    for ax, (intervention, y_prob) in zip(axes, panels):
        plot_reliability_diagram(
            y_true,
            y_prob,
            n_bins=n_bins,
            title=f"{intervention}",
            ax=ax,
        )

    fig.suptitle(title)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# F5 — Per-slice OOD heatmap
# Project glue per ADR-046 Q6; pending upstream eval-toolkit issue #16
# (`plot_slice_metric_heatmap` for `(group_x x group_y x metric)` grids).
# --------------------------------------------------------------------------- #


def render_f5_slice_heatmap(
    *,
    metric_grid: NDArray[np.float64],
    row_labels: list[str],
    col_labels: list[str],
    title: str = "Per-slice OOD metric heatmap",
    cmap: str = "viridis",
    figsize: tuple[float, float] = (8.0, 5.5),
) -> Figure:
    """Heatmap of (rung x slice x metric) cell values.

    Library-first dispatch to `eval_toolkit.plot_slice_metric_heatmap`
    (closes upstream issue #16; shipped in v0.33.0). Project glue beyond
    the upstream primitive: domain-specific colorbar label ("metric") +
    annotation formatting + figsize defaults.
    """
    from eval_toolkit import plot_slice_metric_heatmap

    set_plot_style()
    return plot_slice_metric_heatmap(
        grid=metric_grid,
        row_labels=row_labels,
        col_labels=col_labels,
        metric_name="metric",
        cmap=cmap,
        annotate=True,
        annot_fmt="{:.3f}",
        title=title,
        figsize=figsize,
    )


# --------------------------------------------------------------------------- #
# F6 — LODO fold variance breakdown — uses plot_metric_bars + plot_lift_ci
# --------------------------------------------------------------------------- #


def render_f6_lodo_breakdown(
    *,
    per_fold_means: Mapping[str, float],
    rung_to_marginal_ci: Mapping[str, BootstrapCI],
    title: str = "LODO fold variance + marginal CI per rung",
    figsize: tuple[float, float] = (12.0, 5.0),
) -> Figure:
    """Two-panel LODO breakdown: per-fold bar chart + per-rung marginal CI.

    Library-first hybrid per ADR-046 Q6 — right panel via `plot_lift_ci(ax=...)`
    which expects `BootstrapCI` (point_estimate + ci_low + ci_high) inputs;
    left panel uses bare matplotlib bars because `plot_metric_bars` does not
    accept an ``ax`` kwarg in eval-toolkit v0.31.0 (upstream gap filed as
    issue #22; remove the local bars + dispatch to the primitive when upstream
    lands). PALETTE colors keep the styling identical across panels.

    Note: `plot_lift_ci` accepts marginal `BootstrapCI` (from
    `eval_toolkit.bootstrap.bootstrap_ci`); the per-rung CIs visualize each
    rung's metric uncertainty in the same axis layout. Paired-Δ visualization
    lives in F7's dual-policy grid.
    """
    set_plot_style()
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=figsize)

    # Left panel — per-fold bars (project glue; upstream gap #22 pending).
    fold_labels = list(per_fold_means.keys())
    fold_values = [per_fold_means[k] for k in fold_labels]
    ax_left.bar(fold_labels, fold_values, color=PALETTE["negative"])
    ax_left.set_xticks(range(len(fold_labels)))
    ax_left.set_xticklabels(fold_labels, rotation=30, ha="right")
    ax_left.set_ylabel("Metric (per fold)")
    ax_left.set_title("Per-fold means")

    # Right panel — per-rung marginal-bootstrap CIs via library-first primitive.
    plot_lift_ci(
        dict(rung_to_marginal_ci),
        zero_line=False,
        xlabel="Metric (with 95% CI)",
        title="Per-rung marginal CI",
        ax=ax_right,
    )

    fig.suptitle(title)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# F7 — Dual-policy operating-point grid (+ reachability flags) — hybrid
# --------------------------------------------------------------------------- #


def render_f7_dual_policy_grid(
    *,
    rung_to_detection_deltas: Mapping[str, NDArray[np.float64]],
    rung_to_verification_deltas: Mapping[str, NDArray[np.float64]],
    rung_to_reachable: Mapping[str, bool],
    title: str = "Dual-policy operating-point bootstrap Δ-distributions",
    figsize: tuple[float, float] = (12.0, 6.0),
) -> Figure:
    """Grid of bootstrap-Δ sub-panels: detection (top row) + verification (bottom row).

    Library-first per ADR-046 Q6 — each sub-panel invokes
    `plot_bootstrap_distribution`. Project glue is the n_rungs x 2 grid layout
    + reachability-flag annotations (asterisks on unreachable verification cells
    per ADR-025 + A-009).
    """
    set_plot_style()
    rungs = list(rung_to_detection_deltas.keys())
    n_rungs = len(rungs)
    if n_rungs == 0:
        raise ValueError("No rungs supplied to render_f7_dual_policy_grid.")

    fig, axes = plt.subplots(2, n_rungs, figsize=figsize, sharex=False, sharey=False)
    if n_rungs == 1:
        axes = np.array([[axes[0]], [axes[1]]])

    for col, rung in enumerate(rungs):
        plot_bootstrap_distribution(
            rung_to_detection_deltas[rung],
            title=f"{rung} — Detection (FPR=1%)",
            ax=axes[0, col],
        )
        v_title = f"{rung} — Verification (Recall>=99%)"
        if not rung_to_reachable.get(rung, True):
            v_title += " *"  # A-009 unreachable-target asterisk per ADR-025.
        plot_bootstrap_distribution(
            rung_to_verification_deltas[rung],
            title=v_title,
            ax=axes[1, col],
        )

    fig.suptitle(title)
    fig.tight_layout()
    return fig
