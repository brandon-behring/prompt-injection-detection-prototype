# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 03 — Calibration battery
#
# Per ADR-023, the calibration audit reports:
# - **ECE equal-mass** (10 bins; per-cell)
# - **Brier score** (per-cell)
# - **Reliability curve** (rendered as F4 reliability triptych in `docs/plots/F4.svg`; see RESULTS §4)
# - **Temperature + isotonic fitting** (validation-only per ADR-023)
#
# Platt + Beta calibrators were deferred per ADR-023 original
# scope. v1.0.6 filed eval-toolkit#43 (library-first); v1.0.8 will
# consume upstream when shipped. See NEXT_STEPS §1.4.
#
# This notebook aggregates the per-cell ECE + Brier from
# `evals/metrics/per_cell.parquet` and surfaces the per-rung
# calibration story.

# %%
from pathlib import Path

import pandas as pd

REPO_ROOT = Path.cwd().resolve()
while not (REPO_ROOT / "pyproject.toml").exists() and REPO_ROOT != REPO_ROOT.parent:
    REPO_ROOT = REPO_ROOT.parent

PER_CELL_PARQUET = REPO_ROOT / "evals" / "metrics" / "per_cell.parquet"
F4_FIGURE = REPO_ROOT / "docs" / "plots" / "F4.svg"

per_cell = pd.read_parquet(PER_CELL_PARQUET)
print(f"per_cell.parquet: {per_cell.shape}")
print(f"calibration columns: {[c for c in per_cell.columns if 'ece' in c or 'brier' in c]}")

# %% [markdown]
# ## Per-rung × per-slice mean ECE + Brier (across folds × seeds)

# %%
RUNG_ORDER = ["frozen_probe", "lora", "tfidf-lr", "protectai-v1", "protectai-v2"]
SLICE_ORDER = ["jbb_behaviors", "xstest", "pooled_ood"]

calib_agg = (
    per_cell.groupby(["rung", "slice_name"])
    .agg(
        ece_mean=("ece_equal_mass", "mean"),
        ece_std=("ece_equal_mass", "std"),
        brier_mean=("brier", "mean"),
        brier_std=("brier", "std"),
        n_cells=("ece_equal_mass", "count"),
    )
    .reset_index()
)

print(
    "ECE equal-mass per (rung, slice) — mean ± std across 12 cells (4 folds × 3 seeds; protectai ungrid):"
)
ece_table = (
    calib_agg.pivot(index="rung", columns="slice_name", values="ece_mean")
    .reindex(index=RUNG_ORDER, columns=SLICE_ORDER)
    .round(4)
)
print(ece_table.to_string())

# %%
print()
print("Brier score per (rung, slice) — mean across cells:")
brier_table = (
    calib_agg.pivot(index="rung", columns="slice_name", values="brier_mean")
    .reindex(index=RUNG_ORDER, columns=SLICE_ORDER)
    .round(4)
)
print(brier_table.to_string())

# %% [markdown]
# ## Calibration narrative
#
# Per WRITEUP/eval-design.md §5.1 + WRITEUP/methodology-guarantees.md:
#
# - **ECE equal-mass** is the headline calibration metric (10
#   equal-mass bins per ADR-023; debiased variants surfaced in
#   calibration_battery.py but only equal-mass exported to
#   per_cell.parquet).
# - **Brier** is reported as a strictly-proper-scoring-rule
#   sanity check; lower is better.
# - **Reliability curves** rendered per rung in F4 (triptych):
#   raw + temperature-scaled + isotonic-fitted reliability
#   diagrams. See `docs/plots/F4.svg` + RESULTS §4.
#
# **Calibration trend by rung**:

# %%
print("Per-rung mean calibration (averaged across multi-class slices):")
rung_means = (
    calib_agg.groupby("rung")
    .agg(
        mean_ece=("ece_mean", "mean"),
        mean_brier=("brier_mean", "mean"),
    )
    .reindex(RUNG_ORDER)
    .round(4)
)
print(rung_means.to_string())

# %%
print()
print(
    "Verification: lower-is-better; protectai rungs have higher ECE/Brier in cells with sample sizes ≥1, since they emit non-calibrated logits without per-fold val tuning."
)

# %% [markdown]
# ## F4 figure reference

# %%
print(f"F4 reliability triptych SVG: {F4_FIGURE}")
print(f"  Exists: {F4_FIGURE.exists()}")
print(f"  Size:   {F4_FIGURE.stat().st_size if F4_FIGURE.exists() else '-'} bytes")
print(
    "  See RESULTS.md §4 for the embedded version + WRITEUP/eval-design.md §5.1 for the methodology."
)

# %% [markdown]
# ## Reference: see also
#
# - **`01_canonical_results.ipynb`** — headline AUPRC + AUROC grids.
# - **`02_frozen_vs_lora.ipynb`** — paired-bootstrap rung-comparison + DeLong + BH-FDR.
# - **`04_ood_slate.ipynb`** — per-slice IID-vs-OOD gap visualization.
# - **ADR-023** — calibration battery design + scope deferrals (Platt/Beta).
# - **eval-toolkit#43** — Platt + Beta calibrator request (filed v1.0.6; v1.0.8 conditional consume).
# - **RESULTS.md §4** — F4 reliability triptych embedded.
