"""Render the reviewer-facing canonical figure slate.

The main Quarto site uses five figures, all derived from committed canonical
artifacts under ``evals/``. Synthetic scaffold figures are still useful for
smoke tests, but ``--scaffold`` is forbidden from writing to ``docs/plots`` so
placeholder plots cannot accidentally become reviewer-facing artifacts.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # noqa: E402 - headless backend for CI / smoke runs

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from eval_toolkit.bootstrap import BootstrapCI  # noqa: E402
from eval_toolkit.plotting import (  # noqa: E402
    PALETTE,
    plot_lift_ci,
    plot_slice_metric_heatmap,
    save_figure,
    set_plot_style,
)
from matplotlib.figure import Figure  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.eval.figures import FIGURE_OUTPUT_DIR_DEFAULT, FIGURE_SLATE_NAMES  # noqa: E402

RUNG_ORDER: tuple[str, ...] = (
    "frozen_probe",
    "protectai-v1",
    "protectai-v2",
    "lora",
    "tfidf-lr",
)
TRAINED_RUNG_ORDER: tuple[str, ...] = ("frozen_probe", "lora", "tfidf-lr")
RUNG_LABELS: dict[str, str] = {
    "frozen_probe": "Frozen probe",
    "lora": "LoRA",
    "tfidf-lr": "TF-IDF + LR",
    "protectai-v1": "ProtectAI v1",
    "protectai-v2": "ProtectAI v2",
}
SLICE_ORDER: tuple[str, ...] = (
    "jbb_behaviors",
    "xstest",
    "pooled_ood",
    "bipia",
    "injecagent",
    "notinject",
)
SLICE_LABELS: dict[str, str] = {
    "jbb_behaviors": "JBB",
    "xstest": "XSTest",
    "pooled_ood": "Pooled OOD",
    "bipia": "BIPIA",
    "injecagent": "InjecAgent",
    "notinject": "NotInject",
}
POOLED_OOD_PREVALENCE = 412 / 1101

CANONICAL_ARTIFACTS: dict[str, Path] = {
    "metrics": _REPO_ROOT / "evals" / "metrics" / "per_cell.parquet",
    "marginal": _REPO_ROOT / "evals" / "bootstrap" / "marginal_cells.parquet",
    "paired": _REPO_ROOT / "evals" / "bootstrap" / "paired_cells.parquet",
    "operating_points": _REPO_ROOT / "evals" / "operating_points" / "dual_policy.parquet",
}


def _git_commit_sha() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=_REPO_ROOT, stderr=subprocess.DEVNULL
            )
            .decode("utf-8")
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _source_artifacts(paths: list[Path]) -> str:
    return ", ".join(str(path.relative_to(_REPO_ROOT)) for path in paths)


def _provenance(figure_id: str, *, data_mode: str, source_artifacts: list[Path]) -> dict[str, str]:
    return {
        "figure_id": figure_id,
        "adr": "ADR-062",
        "data_mode": data_mode,
        "source_artifacts": _source_artifacts(source_artifacts),
        "commit_sha": _git_commit_sha(),
        "generated_at": _dt.datetime.now(_dt.UTC).isoformat(),
    }


def _require_artifacts() -> None:
    missing = [
        str(path.relative_to(_REPO_ROOT))
        for path in CANONICAL_ARTIFACTS.values()
        if not path.exists()
    ]
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(f"canonical figure artifacts are missing: {joined}")


def _read_canonical() -> dict[str, pd.DataFrame]:
    _require_artifacts()
    return {name: pd.read_parquet(path) for name, path in CANONICAL_ARTIFACTS.items()}


def _style_axes(ax: plt.Axes) -> None:
    ax.grid(True, axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _seed1_auprc(marginal: pd.DataFrame) -> pd.DataFrame:
    return marginal[
        (marginal["seed"] == 1)
        & (marginal["metric"] == "auprc")
        & (marginal["slice_name"].isin(("jbb_behaviors", "xstest", "pooled_ood")))
    ].copy()


def render_f1_pooled_ood_auprc(marginal: pd.DataFrame) -> Figure:
    set_plot_style()
    data = _seed1_auprc(marginal)
    data = data[data["slice_name"] == "pooled_ood"].set_index("rung").loc[list(RUNG_ORDER)]

    labels = [RUNG_LABELS[rung] for rung in data.index]
    values = data["point_estimate"].to_numpy()
    lower = values - data["ci_lo"].to_numpy()
    upper = data["ci_hi"].to_numpy() - values

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    colors = [
        PALETTE["positive"] if rung == "frozen_probe" else PALETTE["baseline"]
        for rung in data.index
    ]
    ax.bar(labels, values, color=colors, alpha=0.85)
    ax.errorbar(labels, values, yerr=[lower, upper], fmt="none", ecolor="#111827", capsize=4, lw=1)
    ax.axhline(
        POOLED_OOD_PREVALENCE,
        color=PALETTE["baseline"],
        linestyle="--",
        linewidth=1.5,
        label=f"Random floor ({POOLED_OOD_PREVALENCE:.3f} = 412 / 1101 prevalence)",
    )
    for i, value in enumerate(values):
        ax.text(i, value + 0.006, f"{value:.3f}", ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0.25, 0.41)
    ax.set_ylabel("AUPRC (higher is better)")
    ax.set_title("Pooled OOD AUPRC: no rung clearly beats the random floor")
    ax.legend(loc="upper right")
    _style_axes(ax)
    fig.autofmt_xdate(rotation=20, ha="right")
    fig.tight_layout()
    return fig


def render_f2_frozen_vs_lora_paired_delta(paired: pd.DataFrame) -> Figure:
    set_plot_style()
    data = paired[
        (paired["rung_a"] == "frozen_probe")
        & (paired["rung_b"] == "lora")
        & (paired["metric"] == "auprc")
        & (paired["slice_name"].isin(("jbb_behaviors", "xstest")))
    ].copy()
    data["slice_order"] = data["slice_name"].map({"jbb_behaviors": 0, "xstest": 1})
    data = data.sort_values("slice_order")

    estimates = {
        SLICE_LABELS[row["slice_name"]]: BootstrapCI(
            point_estimate=float(row["point_estimate_diff"]),
            ci_low=float(row["ci_lo"]),
            ci_high=float(row["ci_hi"]),
            confidence=0.95,
            n_resamples=int(row["n_resamples"]),
            method=str(row["ci_method"]),
        )
        for _, row in data.iterrows()
    }
    fig = plot_lift_ci(
        estimates,
        zero_line=True,
        xlabel="LoRA AUPRC minus frozen-probe AUPRC (95% CI; whiskers crossing 0 = indistinguishable)",
        title="Paired comparison: LoRA does not improve the comparable slices",
        figsize=(7.2, 3.8),
    )
    fig.tight_layout()
    return fig


def render_f3_slice_grid(marginal: pd.DataFrame) -> Figure:
    set_plot_style()
    data = _seed1_auprc(marginal)
    lookup = {(row["rung"], row["slice_name"]): row["point_estimate"] for _, row in data.iterrows()}
    grid = np.full((len(RUNG_ORDER), len(SLICE_ORDER)), np.nan, dtype=float)
    for r_i, rung in enumerate(RUNG_ORDER):
        for s_i, slice_name in enumerate(SLICE_ORDER):
            if (rung, slice_name) in lookup:
                grid[r_i, s_i] = float(lookup[(rung, slice_name)])

    fig = plot_slice_metric_heatmap(
        grid,
        row_labels=[RUNG_LABELS[r] for r in RUNG_ORDER],
        col_labels=[SLICE_LABELS[s] for s in SLICE_ORDER],
        metric_name="AUPRC",
        annotate=False,
        title="AUPRC by slice; single-class slices are not defined",
        figsize=(9.0, 4.8),
    )
    ax = fig.axes[0]
    for r_i in range(grid.shape[0]):
        for s_i in range(grid.shape[1]):
            value = grid[r_i, s_i]
            label = "N/A" if np.isnan(value) else f"{value:.3f}"
            ax.text(s_i, r_i, label, ha="center", va="center", color="#111827", fontsize=9)
    fig.tight_layout()
    return fig


def render_f4_detection_threshold_transfer(operating_points: pd.DataFrame) -> Figure:
    set_plot_style()
    data = operating_points[operating_points["policy"] == "detection"]
    grouped = data.groupby("rung", as_index=True)[
        ["achieved_test_fpr", "achieved_test_recall"]
    ].mean()
    grouped = grouped.loc[list(TRAINED_RUNG_ORDER)]
    labels = [RUNG_LABELS[rung] for rung in grouped.index]

    fig, (ax_fpr, ax_recall) = plt.subplots(1, 2, figsize=(9.0, 4.0))
    ax_fpr.bar(labels, grouped["achieved_test_fpr"], color=PALETTE["positive"], alpha=0.85)
    ax_fpr.axhline(
        0.01, color=PALETTE["baseline"], linestyle="--", linewidth=1.5, label="1% target"
    )
    ax_fpr.set_title("False-positive rate on test")
    ax_fpr.set_ylabel("FPR")
    ax_fpr.legend(loc="upper left")
    _style_axes(ax_fpr)

    ax_recall.bar(labels, grouped["achieved_test_recall"], color=PALETTE["accent"], alpha=0.85)
    ax_recall.set_title("Recall on test")
    ax_recall.set_ylabel("Recall")
    _style_axes(ax_recall)

    for ax in (ax_fpr, ax_recall):
        ax.tick_params(axis="x", rotation=20)
    fig.suptitle("Validation thresholds do not transfer cleanly to held-out sources")
    fig.tight_layout()
    return fig


def render_f5_calibration(metrics: pd.DataFrame) -> Figure:
    set_plot_style()
    grouped = (
        metrics.groupby("rung", as_index=True)[["ece_equal_mass", "brier"]]
        .mean()
        .loc[list(RUNG_ORDER)]
    )
    labels = [RUNG_LABELS[rung] for rung in grouped.index]
    x = np.arange(len(grouped))
    width = 0.36

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.bar(
        x - width / 2,
        grouped["ece_equal_mass"],
        width,
        label="ECE",
        color=PALETTE["positive"],
        alpha=0.85,
    )
    ax.bar(
        x + width / 2, grouped["brier"], width, label="Brier", color=PALETTE["accent"], alpha=0.85
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel(
        "Error (lower is better; ECE = expected calibration error, Brier = mean squared error)"
    )
    ax.set_title("Calibration: frozen probe is much better calibrated than LoRA")
    ax.legend()
    _style_axes(ax)
    fig.tight_layout()
    return fig


def _save(
    fig: Figure, out_dir: Path, figure_id: str, *, data_mode: str, source_artifacts: list[Path]
) -> None:
    save_figure(
        fig,
        out_dir / f"{figure_id}.svg",
        provenance=_provenance(figure_id, data_mode=data_mode, source_artifacts=source_artifacts),
    )
    plt.close(fig)


def _render_canonical_slate(out_dir: Path) -> int:
    frames = _read_canonical()
    out_dir.mkdir(parents=True, exist_ok=True)

    _save(
        render_f1_pooled_ood_auprc(frames["marginal"]),
        out_dir,
        "F1",
        data_mode="canonical",
        source_artifacts=[CANONICAL_ARTIFACTS["marginal"]],
    )
    _save(
        render_f2_frozen_vs_lora_paired_delta(frames["paired"]),
        out_dir,
        "F2",
        data_mode="canonical",
        source_artifacts=[CANONICAL_ARTIFACTS["paired"]],
    )
    _save(
        render_f3_slice_grid(frames["marginal"]),
        out_dir,
        "F3",
        data_mode="canonical",
        source_artifacts=[CANONICAL_ARTIFACTS["marginal"]],
    )
    _save(
        render_f4_detection_threshold_transfer(frames["operating_points"]),
        out_dir,
        "F4",
        data_mode="canonical",
        source_artifacts=[CANONICAL_ARTIFACTS["operating_points"]],
    )
    _save(
        render_f5_calibration(frames["metrics"]),
        out_dir,
        "F5",
        data_mode="canonical",
        source_artifacts=[CANONICAL_ARTIFACTS["metrics"]],
    )
    return 0


def _synthetic_frames() -> dict[str, pd.DataFrame]:
    marginal_rows: list[dict[str, Any]] = []
    for rung_i, rung in enumerate(RUNG_ORDER):
        for slice_i, slice_name in enumerate(("jbb_behaviors", "xstest", "pooled_ood")):
            value = 0.32 + 0.02 * rung_i + 0.01 * slice_i
            marginal_rows.append(
                {
                    "rung": rung,
                    "slice_name": slice_name,
                    "metric": "auprc",
                    "seed": 1,
                    "point_estimate": value,
                    "ci_lo": value - 0.01,
                    "ci_hi": value + 0.01,
                }
            )
    paired = pd.DataFrame(
        {
            "rung_a": ["frozen_probe", "frozen_probe"],
            "rung_b": ["lora", "lora"],
            "slice_name": ["jbb_behaviors", "xstest"],
            "metric": ["auprc", "auprc"],
            "point_estimate_diff": [-0.02, -0.01],
            "ci_lo": [-0.03, -0.02],
            "ci_hi": [-0.01, 0.005],
            "n_resamples": [200, 200],
            "ci_method": ["percentile", "percentile"],
        }
    )
    operating = pd.DataFrame(
        {
            "rung": ["frozen_probe", "lora", "tfidf-lr"],
            "policy": ["detection", "detection", "detection"],
            "achieved_test_fpr": [0.01, 0.11, 0.06],
            "achieved_test_recall": [0.06, 0.42, 0.33],
        }
    )
    metric_rows: list[dict[str, Any]] = []
    for rung_i, rung in enumerate(RUNG_ORDER):
        metric_rows.append(
            {
                "rung": rung,
                "ece_equal_mass": 0.12 + 0.05 * rung_i,
                "brier": 0.25 + 0.04 * rung_i,
            }
        )
    return {
        "marginal": pd.DataFrame(marginal_rows),
        "paired": paired,
        "operating_points": operating,
        "metrics": pd.DataFrame(metric_rows),
    }


def _render_synthetic_slate(out_dir: Path) -> int:
    frames = _synthetic_frames()
    out_dir.mkdir(parents=True, exist_ok=True)
    synthetic_source = [_REPO_ROOT / "scripts" / "render_figures.py"]
    _save(
        render_f1_pooled_ood_auprc(frames["marginal"]),
        out_dir,
        "F1",
        data_mode="synthetic_fixture",
        source_artifacts=synthetic_source,
    )
    _save(
        render_f2_frozen_vs_lora_paired_delta(frames["paired"]),
        out_dir,
        "F2",
        data_mode="synthetic_fixture",
        source_artifacts=synthetic_source,
    )
    _save(
        render_f3_slice_grid(frames["marginal"]),
        out_dir,
        "F3",
        data_mode="synthetic_fixture",
        source_artifacts=synthetic_source,
    )
    _save(
        render_f4_detection_threshold_transfer(frames["operating_points"]),
        out_dir,
        "F4",
        data_mode="synthetic_fixture",
        source_artifacts=synthetic_source,
    )
    _save(
        render_f5_calibration(frames["metrics"]),
        out_dir,
        "F5",
        data_mode="synthetic_fixture",
        source_artifacts=synthetic_source,
    )
    return 0


def _default_docs_plots_dir() -> Path:
    return (_REPO_ROOT / FIGURE_OUTPUT_DIR_DEFAULT).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=_REPO_ROOT / FIGURE_OUTPUT_DIR_DEFAULT,
    )
    parser.add_argument(
        "--scaffold",
        action="store_true",
        help="Render synthetic fixture plots. Forbidden for docs/plots output.",
    )
    args = parser.parse_args()
    out_dir = args.out_dir.resolve()

    try:
        if args.scaffold:
            if out_dir == _default_docs_plots_dir():
                print(
                    "[render-figures] refusing to write synthetic figures to docs/plots; "
                    "pass --out-dir tests/fixtures/plots or another non-reviewer path",
                    file=sys.stderr,
                )
                return 2
            rc = _render_synthetic_slate(out_dir)
            mode = "synthetic fixture"
        else:
            rc = _render_canonical_slate(out_dir)
            mode = "canonical"
    except Exception as exc:
        print(f"[render-figures] error: {exc}", file=sys.stderr)
        return 1

    if rc == 0:
        produced = sorted(path.name for path in out_dir.glob("F*.svg"))
        expected = [f"{name}.svg" for name in FIGURE_SLATE_NAMES]
        print(f"[render-figures] wrote {len(produced)} {mode} figures: {produced}")
        if produced != expected:
            print(f"[render-figures] expected {expected}", file=sys.stderr)
            return 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
