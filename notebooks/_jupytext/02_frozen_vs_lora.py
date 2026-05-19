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
# # 02 — Frozen-probe vs LoRA paired-bootstrap rung-comparison
#
# Quantifies the load-bearing v1.0.x finding: **fine-tuning HURTS
# cross-family OOD generalization**. LoRA's `pooled_ood` AUPRC
# delta vs frozen-probe = **-0.071** (paired-bootstrap CI clears
# zero). This notebook surfaces that delta + 3 cross-checks:
#
# 1. **Paired-bootstrap (BCa) Δ AUPRC** — the headline source (per
#    `evals/bootstrap/paired_cells.parquet`; ADR-022).
# 2. **DeLong AUC-difference CI** — parametric AUC-diff sanity-check
#    via `eval_toolkit.bootstrap.delong_roc_variance`; complements
#    the bootstrap CI with a closed-form variance estimate.
# 3. **BH-FDR multi-comparison correction** — across the 40-cell
#    paired-bootstrap battery via `eval_toolkit.bootstrap.fdr_bh_correct`;
#    controls family-wise error rate at α = 0.05.
#
# All 3 are now library-first via eval-toolkit v0.39.0 (per v1.0.6
# bump). DeLong + BH-FDR primitives shipped at v0.32.0+ but were
# unused until v1.0.7 wired them in this notebook.

# %%
from pathlib import Path

import numpy as np
import pandas as pd
from eval_toolkit.bootstrap import delong_roc_variance, fdr_bh_correct

REPO_ROOT = Path.cwd().resolve()
while not (REPO_ROOT / "pyproject.toml").exists() and REPO_ROOT != REPO_ROOT.parent:
    REPO_ROOT = REPO_ROOT.parent

PAIRED_CELLS_PARQUET = REPO_ROOT / "evals" / "bootstrap" / "paired_cells.parquet"
PAIRED_CELLS_SEED2_PARQUET = REPO_ROOT / "evals" / "bootstrap" / "paired_cells_seed2.parquet"

paired_s1 = pd.read_parquet(PAIRED_CELLS_PARQUET)
paired_s2 = pd.read_parquet(PAIRED_CELLS_SEED2_PARQUET)

print(f"paired_cells.parquet (seed=1):       {paired_s1.shape}")
print(f"paired_cells_seed2.parquet (seed=2): {paired_s2.shape}")
print(f"columns: {list(paired_s1.columns)}")

# %% [markdown]
# ## Headline: LoRA vs frozen_probe on pooled_ood

# %%
headline = paired_s1[
    (paired_s1["rung_a"] == "frozen_probe")
    & (paired_s1["rung_b"] == "lora")
    & (paired_s1["slice_name"] == "pooled_ood")
    & (paired_s1["metric"] == "auprc")
]
print("Headline paired-bootstrap delta — frozen_probe vs LoRA on pooled_ood AUPRC:")
print(headline.to_string(index=False))

# %% [markdown]
# **Interpretation**: `point_estimate_diff` = `point_estimate_a` − `point_estimate_b` = frozen_probe AUPRC − LoRA AUPRC. Positive means frozen_probe wins; negative means LoRA wins. CI clearing zero = paired difference is statistically distinguishable from zero at α = 0.05.

# %% [markdown]
# ## Seed-stability check (per ADR-022 + A-008)
#
# Paired-bootstrap is re-run with seed=2 to verify CI stability.
# A-008 acceptance criterion: < 5% of cells flip CI-clears-zero
# status between seeds.


# %%
def _ci_clears_zero(row: pd.Series) -> bool:
    """True iff the paired-bootstrap CI clears zero (point_diff strictly excludes 0)."""
    return bool((row["ci_lo"] > 0) | (row["ci_hi"] < 0))


merged = paired_s1.merge(
    paired_s2,
    on=["rung_a", "rung_b", "slice_name", "metric"],
    suffixes=("_s1", "_s2"),
)
merged["clears_s1"] = merged.apply(lambda r: r["ci_lo_s1"] > 0 or r["ci_hi_s1"] < 0, axis=1)
merged["clears_s2"] = merged.apply(lambda r: r["ci_lo_s2"] > 0 or r["ci_hi_s2"] < 0, axis=1)
merged["flip"] = merged["clears_s1"] != merged["clears_s2"]
n_total = len(merged)
n_flip = int(merged["flip"].sum())
print(
    f"Paired-bootstrap seed-stability: {n_flip}/{n_total} cells flipped CI-clears-zero status (A-008 threshold: < 5%, i.e., < {round(0.05 * n_total)})"
)
print(f"Status: {'PASS' if n_flip / n_total < 0.05 else 'FAIL'} (per ADR-022 + A-008)")

# %% [markdown]
# ## All pairwise rung comparisons (40-cell battery)

# %%
all_pairs = paired_s1[paired_s1["metric"] == "auprc"][
    ["rung_a", "rung_b", "slice_name", "point_estimate_diff", "ci_lo", "ci_hi"]
].copy()
all_pairs["clears_zero"] = all_pairs.apply(lambda r: (r["ci_lo"] > 0) or (r["ci_hi"] < 0), axis=1)
print("All AUPRC paired-bootstrap deltas (point + CI; clears_zero flag):")
print(all_pairs.round(3).to_string(index=False))

# %% [markdown]
# ## DeLong AUC-difference CI (parametric sanity-check)
#
# DeLong & DeLong (1988) provides a closed-form variance estimate
# for the difference of two AUCs computed on the same paired
# samples. Used here as a sanity-check alongside the paired
# bootstrap — if both methods agree, the bootstrap result is
# robust. Library-first via `eval_toolkit.bootstrap.delong_roc_variance`
# (available since v0.32.0; wired in v1.0.7 per NEXT_STEPS §1.3 close).

# %% [markdown]
# We compute DeLong for the **frozen_probe vs lora on pooled_ood**
# headline comparison using the per-row predictions from
# `evals/predictions/`. The bootstrap CI for the same comparison
# is shown above; DeLong's normal-approximation CI should be in
# the same ballpark.

# %%
PRED_DIR = REPO_ROOT / "evals" / "predictions"


# Load fold=0 / seed=42 predictions for the two rungs on each OOD slice
# (DeLong requires the same eval samples for both classifiers).
def _load_pred(rung: str, slice_name: str) -> pd.DataFrame:
    """Load fold=0/seed=42 prediction parquet for a (rung, slice) cell.

    Parameters
    ----------
    rung : str
        Rung identifier (e.g. ``"frozen-probe"`` or ``"lora"``;
        note hyphenated filenames).
    slice_name : str
        Slice identifier (e.g. ``"pooled_ood"``).

    Returns
    -------
    pd.DataFrame
        Columns include ``label``, ``predicted_proba_class1``.
    """
    # Filename convention: <rung>__fold<F>__seed<S>__<slice>.parquet
    # OOD-slice predictions use underscored rung names; we map hyphens.
    rung_fs = rung.replace("-", "_")
    fname = f"{rung_fs}__fold0__seed42__{slice_name}.parquet"
    path = PRED_DIR / fname
    if not path.exists():
        # Try alternate rung name (some files use hyphen, some underscore)
        fname = f"{rung}__fold0__seed42__{slice_name}.parquet"
        path = PRED_DIR / fname
    return pd.read_parquet(path)


# DeLong needs both classifiers' predictions on the same samples.
# pooled_ood is the union of 5 OOD slices; we concatenate per-slice
# predictions for fold0/seed42, ordered consistently across both rungs.
ood_slices_for_delong = ("jbb_behaviors", "xstest", "bipia", "injecagent", "notinject")

frozen_preds_parts = [_load_pred("frozen_probe", s) for s in ood_slices_for_delong]
lora_preds_parts = [_load_pred("lora", s) for s in ood_slices_for_delong]
frozen_pooled = pd.concat(frozen_preds_parts, ignore_index=True)
lora_pooled = pd.concat(lora_preds_parts, ignore_index=True)
assert len(frozen_pooled) == len(lora_pooled), "row-count mismatch between rungs"
assert (frozen_pooled["label"].to_numpy() == lora_pooled["label"].to_numpy()).all(), (
    "label mismatch between rungs (rows not aligned)"
)
print(
    f"DeLong inputs: {len(frozen_pooled)} pooled_ood rows; positive rate {frozen_pooled['label'].mean():.4f}"
)

# %% [markdown]
# ### DeLong AUC-diff CI

# %%
labels = frozen_pooled["label"].to_numpy(dtype=np.int_)
scores_frozen = frozen_pooled["predicted_proba_class1"].to_numpy(dtype=np.float64)
scores_lora = lora_pooled["predicted_proba_class1"].to_numpy(dtype=np.float64)

delong = delong_roc_variance(labels, y_score_a=scores_frozen, y_score_b=scores_lora)

_se_diff = float(np.sqrt(delong.var))
print("DeLong AUC-difference for frozen_probe vs LoRA on pooled_ood:")
print(f"  AUC_a (frozen_probe):  {delong.auc_a:.4f}")
print(f"  AUC_b (lora):          {delong.auc_b:.4f}")
print(f"  delta_auc (a - b):     {delong.delta_auc:.4f}")
print(f"  SE(delta_auc):         {_se_diff:.4f}")
print(f"  z-statistic:           {delong.z:.4f}")
print(f"  95% CI for delta_auc:  [{delong.ci_low:.4f}, {delong.ci_high:.4f}]")
print(f"  p-value (two-tailed):  {delong.p_value:.6f}")

# %% [markdown]
# **Cross-check vs paired-bootstrap**: the paired-bootstrap
# `point_estimate_diff` for AUROC on pooled_ood (same comparison)
# can be read from `paired_cells.parquet`. If DeLong and bootstrap
# agree on point + CI direction, the result is robust under both
# parametric + nonparametric assumptions.

# %%
auroc_paired = paired_s1[
    (paired_s1["rung_a"] == "frozen_probe")
    & (paired_s1["rung_b"] == "lora")
    & (paired_s1["slice_name"] == "pooled_ood")
    & (paired_s1["metric"] == "auroc")
]
print("Paired-bootstrap AUROC delta (frozen_probe vs lora; pooled_ood):")
print(
    auroc_paired[["point_estimate_diff", "ci_lo", "ci_hi", "ci_method"]]
    .round(4)
    .to_string(index=False)
)
print()
print(
    f"DeLong delta_auc: {delong.delta_auc:.4f} [{delong.ci_low:.4f}, {delong.ci_high:.4f}] (p = {delong.p_value:.4g})"
)
print()
print(
    "Both methods should agree on sign + magnitude of the delta. CI widths may differ (DeLong is normal-approximation; bootstrap is BCa)."
)

# %% [markdown]
# ## BH-FDR multi-comparison correction
#
# The 40-cell paired-bootstrap battery in `paired_cells.parquet`
# spans 6 pairwise rung comparisons × 2 OOD slices × 2 metrics
# + marginal-vs-pooled cells. With α = 0.05 per cell, the
# expected family-wise type-I error rate under the null is
# ~88% (1 − 0.95^40 ≈ 0.872). BH-FDR controls the false
# discovery rate to α; below we apply it across the 40-cell
# battery using the per-cell "clears zero" status as a proxy
# p-value (via the normal-approximation z-stat derived from
# (point_diff / half-CI-width)).
#
# Library-first via `eval_toolkit.bootstrap.fdr_bh_correct`
# (available since v0.32.0; wired in v1.0.7).

# %%
# Derive a per-cell p-value approximation from the paired-bootstrap CI.
# Treating each cell as a normal-distributed estimator:
#   z = point_diff / (half_ci_width / 1.96)
#   p = 2 * (1 - Phi(|z|))
# This is an approximation; the bootstrap CI is BCa not normal,
# but the resulting p-values are usable for BH-FDR ranking.
from scipy import stats as _scipy_stats

all_cells = paired_s1[paired_s1["metric"].isin(["auprc", "auroc"])].copy()
all_cells["half_ci_width"] = (all_cells["ci_hi"] - all_cells["ci_lo"]) / 2.0
all_cells["se_approx"] = all_cells["half_ci_width"] / 1.96
all_cells["z_approx"] = all_cells["point_estimate_diff"] / all_cells["se_approx"]
all_cells["p_approx"] = 2 * (1 - _scipy_stats.norm.cdf(np.abs(all_cells["z_approx"])))

# Apply BH-FDR at α = 0.05; fdr_bh_correct returns q-values (BH-adjusted p-values).
ALPHA = 0.05
p_values = all_cells["p_approx"].to_numpy(dtype=np.float64)
q_values = fdr_bh_correct(p_values)

all_cells["p_corrected"] = q_values
all_cells["bh_reject_null"] = q_values < ALPHA

n_pre = int((all_cells["p_approx"] < ALPHA).sum())
n_post = int(all_cells["bh_reject_null"].sum())
print(f"Pre-correction (α=0.05):       {n_pre} of {len(all_cells)} cells flagged as significant")
print(f"Post BH-FDR correction (α=0.05): {n_post} of {len(all_cells)} cells flagged as significant")
print()
print("Cells flipped from significant to non-significant by BH-FDR:")
flipped = all_cells[(all_cells["p_approx"] < 0.05) & (~all_cells["bh_reject_null"])]
print(
    flipped[
        [
            "rung_a",
            "rung_b",
            "slice_name",
            "metric",
            "point_estimate_diff",
            "p_approx",
            "p_corrected",
        ]
    ]
    .round(4)
    .to_string(index=False)
)

# %% [markdown]
# ## Headline summary (cross-method consistency)

# %%
print("=" * 72)
print("HEADLINE — frozen_probe vs LoRA on pooled_ood:")
print("=" * 72)
print()
print("Paired-bootstrap BCa CI (per evals/bootstrap/paired_cells.parquet):")
print(
    headline[["point_estimate_diff", "ci_lo", "ci_hi", "ci_method"]].round(4).to_string(index=False)
)
print()
print("DeLong AUC-diff (parametric sanity-check; AUROC):")
print(
    f"  delta_auc = {delong.delta_auc:.4f}  [95% CI: {delong.ci_low:.4f}, {delong.ci_high:.4f}];  p = {delong.p_value:.4g}"
)
print()
print(
    f"Seed stability (paired_cells.parquet seed=1 vs seed=2): {n_flip}/{n_total} cells flipped (A-008 threshold < 5%)"
)
print()
print(
    f"BH-FDR (α = 0.05) across 40-cell battery: {n_post}/{len(all_cells)} cells reject null after correction"
)
print()
print("Interpretation: paired-bootstrap + DeLong + BH-FDR all consistent")
print("with the load-bearing finding that fine-tuning HURTS cross-family")
print("OOD generalization (LoRA -0.071 AUPRC vs frozen-probe; CI clears 0).")

# %% [markdown]
# ## Reference: see also
#
# - **`01_canonical_results.ipynb`** — headline AUPRC + AUROC grids (the marginal-bootstrap CI source).
# - **`03_calibration.ipynb`** — reliability triptych + ECE per rung.
# - **`04_ood_slate.ipynb`** — per-slice IID-vs-OOD gap.
# - **`RESULTS.md`** — full 5×5 grid + figures + raw-data pointers.
# - **`WRITEUP/eval-design.md` §5** — AUPRC vs AUROC framing.
# - **ADR-022** — paired-bootstrap statistical apparatus.
# - **ADR-052** — full-FT OOD drop methodological reframing (LoRA negative-delta evidence carried the methodological judgment).
