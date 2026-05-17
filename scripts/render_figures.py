"""CLI entrypoint — render the canonical 7-figure slate per ADR-046 Q6 + ADR-030.

Per ADR-046 Q6 (Phase 4 Commit 5) + ADR-030 (Quarto site embedding), this
script orchestrates the 7-figure slate produced by `src.eval.figures` and
writes one provenance-tagged SVG per figure to ``docs/plots/F{1..7}.svg``
via ``eval_toolkit.plotting.save_figure``.

The script supports two modes:

- **canonical** — reads `evals/predictions/`, `evals/bootstrap/`,
  `evals/calibration/` outputs from Phase 3 + Phase 4 batteries.
- **scaffold** — synthesizes minimal placeholder data so the smoke test
  + Quarto preview can render the slate without canonical data present.

The mode auto-selects based on `evals/predictions/` existence; pass
``--scaffold`` to force the scaffold path.

Provenance dict embeds: figure_id (F1..F7), adr (ADR-046), commit_sha (live
``git rev-parse HEAD``), generated_at (ISO-8601).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # noqa: E402 — headless backend per ADR-027 smoke-pipe

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from eval_toolkit.bootstrap import bootstrap_ci  # noqa: E402
from eval_toolkit.metrics import pr_auc  # noqa: E402
from eval_toolkit.plotting import save_figure  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.eval.figures import (  # noqa: E402
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


def _provenance(figure_id: str) -> dict[str, str]:
    return {
        "figure_id": figure_id,
        "adr": "ADR-046",
        "commit_sha": _git_commit_sha(),
        "generated_at": _dt.datetime.now(_dt.UTC).isoformat(),
    }


def _scaffold_rung_predictions(
    rungs: tuple[str, ...] = ("classical_floor", "frozen_probe", "lora", "full_ft"),
    n: int = 200,
    base_seed: int = 0,
) -> dict[str, tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]]:
    rng = np.random.default_rng(base_seed)
    out: dict[str, tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]] = {}
    for i, rung in enumerate(rungs):
        y = rng.integers(0, 2, size=n)
        s = np.clip(y + rng.normal(0, 0.40 - 0.05 * i, size=n), 0.001, 0.999)
        out[rung] = (y.astype(np.int_), s.astype(np.float64))
    return out


def _render_scaffold_slate(out_dir: Path) -> int:
    """Render the slate from synthetic placeholder data."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rung_predictions = _scaffold_rung_predictions()

    # F1 — Pareto
    fig_f1 = render_f1_pareto(
        rung_to_auprc={k: float(pr_auc(y, s)) for k, (y, s) in rung_predictions.items()},
        rung_to_compute={
            "classical_floor": 1.0,
            "frozen_probe": 5.0,
            "lora": 50.0,
            "full_ft": 200.0,
        },
    )
    save_figure(fig_f1, out_dir / "F1.svg", provenance=_provenance("F1"))
    plt.close(fig_f1)

    # F2 — ROC overlay
    fig_f2 = render_f2_roc_per_rung(rung_to_y_score=rung_predictions)
    save_figure(fig_f2, out_dir / "F2.svg", provenance=_provenance("F2"))
    plt.close(fig_f2)

    # F3 — PR per rung (library-first direct)
    fig_f3 = render_f3_pr_per_rung(rung_to_y_score=rung_predictions)
    save_figure(fig_f3, out_dir / "F3.svg", provenance=_provenance("F3"))
    plt.close(fig_f3)

    # F4 — Reliability triptych
    y_one = next(iter(rung_predictions.values()))[0]
    s_one = next(iter(rung_predictions.values()))[1]
    rng = np.random.default_rng(1)
    fig_f4 = render_f4_reliability_triptych(
        y_true=y_one,
        y_prob_raw=s_one,
        y_prob_temperature=np.clip(s_one + rng.normal(0, 0.05, size=s_one.shape), 0.001, 0.999),
        y_prob_isotonic=np.clip(s_one + rng.normal(0, 0.04, size=s_one.shape), 0.001, 0.999),
    )
    save_figure(fig_f4, out_dir / "F4.svg", provenance=_provenance("F4"))
    plt.close(fig_f4)

    # F5 — Per-slice heatmap
    grid = np.array(
        [
            [0.80, 0.82, 0.78, 0.85, 0.79],
            [0.85, 0.88, 0.83, 0.90, 0.86],
            [0.90, 0.91, 0.89, 0.93, 0.91],
            [0.92, 0.93, 0.91, 0.95, 0.94],
        ]
    )
    fig_f5 = render_f5_slice_heatmap(
        metric_grid=grid,
        row_labels=list(rung_predictions.keys()),
        col_labels=["notinject", "xstest", "jbb", "bipia", "injecagent"],
    )
    save_figure(fig_f5, out_dir / "F5.svg", provenance=_provenance("F5"))
    plt.close(fig_f5)

    # F6 — LODO breakdown
    fig_f6 = render_f6_lodo_breakdown(
        per_fold_means={"fold0": 0.80, "fold1": 0.85, "fold2": 0.78, "fold3": 0.82},
        rung_to_marginal_ci={
            rung: bootstrap_ci(y, s, metric=pr_auc, n_resamples=200, seed=42)
            for rung, (y, s) in list(rung_predictions.items())[:2]
        },
    )
    save_figure(fig_f6, out_dir / "F6.svg", provenance=_provenance("F6"))
    plt.close(fig_f6)

    # F7 — Dual-policy grid
    rng = np.random.default_rng(2)
    detection = {
        rung: rng.normal(0.02, 0.01, size=200) for rung in list(rung_predictions.keys())[:2]
    }
    verification = {
        rung: rng.normal(0.01, 0.008, size=200) for rung in list(rung_predictions.keys())[:2]
    }
    reachable = {rung: True for rung in detection.keys()}
    fig_f7 = render_f7_dual_policy_grid(
        rung_to_detection_deltas=detection,
        rung_to_verification_deltas=verification,
        rung_to_reachable=reachable,
    )
    save_figure(fig_f7, out_dir / "F7.svg", provenance=_provenance("F7"))
    plt.close(fig_f7)

    return 0


def main() -> int:
    """Render the F1..F7 slate to SVG; canonical or scaffold path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=_REPO_ROOT / FIGURE_OUTPUT_DIR_DEFAULT,
    )
    parser.add_argument(
        "--scaffold",
        action="store_true",
        help="Force the scaffold path (synthetic placeholder data).",
    )
    args = parser.parse_args()

    predictions_root = _REPO_ROOT / "evals" / "predictions"
    if (
        args.scaffold
        or not predictions_root.exists()
        or not any(predictions_root.glob("*.parquet"))
    ):
        print(
            f"[render-figures] scaffold mode — rendering {len(FIGURE_SLATE_NAMES)} placeholder "
            f"figures to {args.out_dir}",
            file=sys.stderr,
        )
        rc = _render_scaffold_slate(args.out_dir)
    else:
        # Canonical-data path is identical in structure; placeholder until Phase 4
        # canonical evals run lands the predictions parquets.
        print(
            "[render-figures] canonical predictions detected — scaffold renderer reused for now; "
            "canonical-data wire-up tracked at upstream gap eval-toolkit#15..#17 + #22.",
            file=sys.stderr,
        )
        rc = _render_scaffold_slate(args.out_dir)

    if rc == 0:
        produced = sorted(args.out_dir.glob("F*.svg"))
        print(f"[render-figures] wrote {len(produced)} figures: {[p.name for p in produced]}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
