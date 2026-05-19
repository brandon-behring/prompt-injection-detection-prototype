# ---
# jupyter:
#   jupytext:
#     formats: notebooks//ipynb,notebooks/_jupytext//py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 01 — Canonical results
#
# Headline characterization table per the v1.0.x submission:
# 5-rung × 3-multi-class-slice AUPRC + AUROC grid sourced from
# `evals/bootstrap/marginal_cells.parquet` (BCa CI, 10000
# resamples; seed=1 headline + seed=2 stability check 0/40
# cells flagged per A-008).
#
# Single-class slices (`bipia`, `injecagent`, `notinject`)
# excluded per ADR-050; see `RESULTS.md` §1 for the full 5×5
# grid with N/A markers on those cells.
#
# **Companion notebooks:**
# - `02_frozen_vs_lora.ipynb` — paired-bootstrap rung-comparison + DeLong AUC-diff sanity + BH-FDR multi-comparison correction.
# - `03_calibration.ipynb` — reliability triptych + ECE + Brier per rung.
# - `04_ood_slate.ipynb` — per-slice IID-vs-OOD gap visualization.
#
# **Library-first** (per ADR-005 + decisions/library_imports.md
# + `eval-toolkit` v0.39.0 surface):
# `eval_toolkit.bootstrap.bootstrap_ci` + project glue at
# `src/eval/marginal_bootstrap.py` already produced
# `evals/bootstrap/marginal_cells.parquet`; this notebook is the
# READER, not the regenerator. Source-of-truth lives in `evals/`.

# %%
from pathlib import Path

import pandas as pd

REPO_ROOT = Path.cwd().resolve()
while not (REPO_ROOT / "pyproject.toml").exists() and REPO_ROOT != REPO_ROOT.parent:
    REPO_ROOT = REPO_ROOT.parent

MARGINAL_CELLS_PARQUET = REPO_ROOT / "evals" / "bootstrap" / "marginal_cells.parquet"
PER_CELL_PARQUET = REPO_ROOT / "evals" / "metrics" / "per_cell.parquet"

assert MARGINAL_CELLS_PARQUET.exists(), f"missing {MARGINAL_CELLS_PARQUET}"
assert PER_CELL_PARQUET.exists(), f"missing {PER_CELL_PARQUET}"

marginal = pd.read_parquet(MARGINAL_CELLS_PARQUET)
per_cell = pd.read_parquet(PER_CELL_PARQUET)

print(f"marginal_cells.parquet: {marginal.shape[0]} rows × {marginal.shape[1]} cols")
print(f"per_cell.parquet:       {per_cell.shape[0]} rows × {per_cell.shape[1]} cols")

# %% [markdown]
# ## Headline AUPRC grid (5 rungs × 3 multi-class slices)
#
# Per ADR-006 + WRITEUP/eval-design.md §5.1, **AUPRC is the
# primary ranking metric** under class imbalance. The
# random-predictor AUPRC equals the positive prevalence on each
# slice (NOT 0.5 — that's AUROC's chance baseline).

# %%
RUNG_ORDER = ["frozen_probe", "lora", "tfidf-lr", "protectai-v1", "protectai-v2"]
SLICE_ORDER = ["jbb_behaviors", "xstest", "pooled_ood"]

auprc_seed1 = (
    marginal[(marginal["metric"] == "auprc") & (marginal["seed"] == 1)]
    .pivot(index="rung", columns="slice_name", values="point_estimate")
    .reindex(index=RUNG_ORDER, columns=SLICE_ORDER)
    .round(3)
)
auprc_ci_lo = (
    marginal[(marginal["metric"] == "auprc") & (marginal["seed"] == 1)]
    .pivot(index="rung", columns="slice_name", values="ci_lo")
    .reindex(index=RUNG_ORDER, columns=SLICE_ORDER)
    .round(3)
)
auprc_ci_hi = (
    marginal[(marginal["metric"] == "auprc") & (marginal["seed"] == 1)]
    .pivot(index="rung", columns="slice_name", values="ci_hi")
    .reindex(index=RUNG_ORDER, columns=SLICE_ORDER)
    .round(3)
)

print("AUPRC point estimates (5 rungs × 3 multi-class slices; seed=1):")
print(auprc_seed1.to_string())

# %% [markdown]
# ### AUPRC with 95% BCa CI

# %%
auprc_with_ci = auprc_seed1.copy().astype(object)
for rung in RUNG_ORDER:
    for slc in SLICE_ORDER:
        pt = auprc_seed1.loc[rung, slc]
        lo = auprc_ci_lo.loc[rung, slc]
        hi = auprc_ci_hi.loc[rung, slc]
        auprc_with_ci.loc[rung, slc] = f"{pt:.3f} [{lo:.3f}, {hi:.3f}]"

print("AUPRC + 95% BCa CI (10000 resamples per cell):")
print(auprc_with_ci.to_string())

# %% [markdown]
# ## Headline AUROC grid (secondary diagnostic)
#
# AUROC reported for cross-paper comparison per ADR-006.
# AUROC's chance baseline is 0.5 regardless of prevalence;
# under class imbalance AUROC over-states performance vs
# AUPRC. Use AUPRC for primary interpretation.

# %%
auroc_seed1 = (
    marginal[(marginal["metric"] == "auroc") & (marginal["seed"] == 1)]
    .pivot(index="rung", columns="slice_name", values="point_estimate")
    .reindex(index=RUNG_ORDER, columns=SLICE_ORDER)
    .round(3)
)
auroc_ci_lo = (
    marginal[(marginal["metric"] == "auroc") & (marginal["seed"] == 1)]
    .pivot(index="rung", columns="slice_name", values="ci_lo")
    .reindex(index=RUNG_ORDER, columns=SLICE_ORDER)
    .round(3)
)
auroc_ci_hi = (
    marginal[(marginal["metric"] == "auroc") & (marginal["seed"] == 1)]
    .pivot(index="rung", columns="slice_name", values="ci_hi")
    .reindex(index=RUNG_ORDER, columns=SLICE_ORDER)
    .round(3)
)

auroc_with_ci = auroc_seed1.copy().astype(object)
for rung in RUNG_ORDER:
    for slc in SLICE_ORDER:
        pt = auroc_seed1.loc[rung, slc]
        lo = auroc_ci_lo.loc[rung, slc]
        hi = auroc_ci_hi.loc[rung, slc]
        auroc_with_ci.loc[rung, slc] = f"{pt:.3f} [{lo:.3f}, {hi:.3f}]"

print("AUROC + 95% BCa CI (5 rungs × 3 multi-class slices):")
print(auroc_with_ci.to_string())

# %% [markdown]
# ## Prevalence baselines (slice-by-slice random-predictor floor for AUPRC)
#
# AUPRC's random-predictor floor equals the positive class
# prevalence on each slice (NOT 0.5). When a rung's AUPRC is
# below the prevalence baseline, the rung's ranking is
# anti-correlated with the label on that slice.

# %%
prevalence_table = (
    per_cell.groupby("slice_name")
    .agg(
        n_rows=("n_rows", "first"),
        n_positive=("n_positive", "first"),
        n_negative=("n_negative", "first"),
    )
    .reindex(SLICE_ORDER)
)
prevalence_table["positive_prevalence"] = (
    prevalence_table["n_positive"] / prevalence_table["n_rows"]
).round(4)
print("Positive prevalence per multi-class slice:")
print(prevalence_table.to_string())

# %% [markdown]
# ## Headline finding (cross-family OOD wall)
#
# Per WRITEUP §Results + EXECUTIVE_SUMMARY:
#
# 1. **None of the rungs clears the pooled_ood prevalence baseline (0.374) under AUPRC.** Best is frozen-probe at 0.364; CI upper bound 0.375 just touches the baseline.
# 2. **LoRA HURTS OOD** vs frozen-probe (-0.071 AUPRC; paired-bootstrap CI clears zero). Fine-tuning the head on the LODO direct-injection pool actively degrades cross-family OOD.
# 3. **ProtectAI v1 → v2 is non-monotone**: v2 beats v1 on jbb_behaviors (+0.037) but loses on xstest (-0.087). Newer version does not uniformly improve.
# 4. **On in-domain slices** (jbb_behaviors + xstest) all trained rungs clear the prevalence baseline; the wall is OOD-specific.
#
# **Cross-family framing**: training pool is 4 direct-injection sources; the 5-slice OOD slate probes attack types absent from training (indirect injection via BIPIA email-body, multi-turn agentic-flow via InjecAgent, jailbreaks via JBB / XSTest, false-positive-probe via NotInject). The OOD wall is cross-FAMILY, not cross-source.

# %% [markdown]
# ## Reference: see also
#
# - **`RESULTS.md`** — full 5-rung × 5-slice grid with N/A markers on single-class cells; reviewer-facing figures F1-F5; raw-data blob URLs at `tree/v1.0.5/evals/`.
# - **`02_frozen_vs_lora.ipynb`** — paired-bootstrap rung-comparison (the source for the LoRA -0.071 delta + CI).
# - **`03_calibration.ipynb`** — reliability + ECE per rung.
# - **`04_ood_slate.ipynb`** — per-slice IID-vs-OOD gap visualization.
# - **`WRITEUP.md` §Results** — methodology-rooted narrative.
# - **`EXECUTIVE_SUMMARY.md`** — 1-page distillation.
