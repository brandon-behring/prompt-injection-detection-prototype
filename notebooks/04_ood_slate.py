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
# # 04 — OOD slate gap visualization
#
# Per-slice breakdown of the OOD wall: each rung's AUPRC on
# each multi-class OOD slice (jbb_behaviors + xstest + pooled_ood)
# compared to the slice's positive-prevalence baseline. Reveals
# the cross-family gap — the trained rungs do well on
# in-distribution-like slices (jbb_behaviors, xstest) but
# collapse on pooled_ood (which dilutes those with the 3
# single-class slices: bipia + injecagent + notinject).

# %%
from pathlib import Path

import pandas as pd

REPO_ROOT = Path.cwd().resolve()
while not (REPO_ROOT / "pyproject.toml").exists() and REPO_ROOT != REPO_ROOT.parent:
    REPO_ROOT = REPO_ROOT.parent

MARGINAL_CELLS_PARQUET = REPO_ROOT / "evals" / "bootstrap" / "marginal_cells.parquet"
PER_CELL_PARQUET = REPO_ROOT / "evals" / "metrics" / "per_cell.parquet"
F5_HEATMAP_SVG = REPO_ROOT / "docs" / "plots" / "F5.svg"

marginal = pd.read_parquet(MARGINAL_CELLS_PARQUET)
per_cell = pd.read_parquet(PER_CELL_PARQUET)

# %% [markdown]
# ## Prevalence baselines per slice

# %%
RUNG_ORDER = ["frozen_probe", "lora", "tfidf-lr", "protectai-v1", "protectai-v2"]
SLICE_ORDER = ["jbb_behaviors", "xstest", "pooled_ood"]

prevalence = per_cell.groupby("slice_name")[["n_positive", "n_rows"]].first().reindex(SLICE_ORDER)
prevalence["positive_prevalence"] = (prevalence["n_positive"] / prevalence["n_rows"]).round(4)
print("Positive prevalence per slice (AUPRC random-predictor floor):")
print(prevalence.to_string())

# %% [markdown]
# ## Per-rung AUPRC vs prevalence baseline

# %%
auprc_seed1 = (
    marginal[(marginal["metric"] == "auprc") & (marginal["seed"] == 1)]
    .pivot(index="rung", columns="slice_name", values="point_estimate")
    .reindex(index=RUNG_ORDER, columns=SLICE_ORDER)
)

# Compute delta vs prevalence
delta_vs_baseline = auprc_seed1.copy()
for slc in SLICE_ORDER:
    baseline = prevalence.loc[slc, "positive_prevalence"]
    delta_vs_baseline[slc] = auprc_seed1[slc] - baseline

print("AUPRC delta vs prevalence baseline (positive = above chance; negative = below chance):")
print(delta_vs_baseline.round(4).to_string())

# %% [markdown]
# ## Per-slice rung-comparison
#
# Each slice's per-rung AUPRC + delta-vs-baseline. The
# cross-family gap is most visible on `pooled_ood` (which
# includes BIPIA + InjecAgent indirect + agentic-flow content
# even though those slices' AUPRC themselves are not reported
# per ADR-050).

# %%
for slc in SLICE_ORDER:
    print(f"\n=== {slc} (prevalence {prevalence.loc[slc, 'positive_prevalence']:.4f}) ===")
    for rung in RUNG_ORDER:
        pt = auprc_seed1.loc[rung, slc]
        delta = pt - prevalence.loc[slc, "positive_prevalence"]
        status = "ABOVE" if delta > 0 else "BELOW"
        print(f"  {rung:20s} AUPRC {pt:.4f}  (Δ {delta:+.4f} {status} baseline)")

# %% [markdown]
# ## IID vs OOD gap (frozen-probe vs LoRA on each slice)

# %%
print("Cross-family OOD finding (per ADR-052 + WRITEUP §Results):")
print()
print("                 frozen_probe AUPRC    LoRA AUPRC    Δ (LoRA - frozen)")
print("-" * 76)
for slc in SLICE_ORDER:
    fp = auprc_seed1.loc["frozen_probe", slc]
    lo = auprc_seed1.loc["lora", slc]
    delta = lo - fp
    print(f"  {slc:20s} {fp:.4f}              {lo:.4f}        {delta:+.4f}")
print()
print("Interpretation:")
print(
    "  * jbb_behaviors + xstest: similar performance (in-distribution-like; trained signals transfer)."
)
print(
    "  * pooled_ood: LoRA underperforms by -0.071 (cross-family OOD wall; fine-tuning specialises on direct-injection structure at the cost of OOD signal)."
)

# %% [markdown]
# ## F5 per-slice heatmap reference

# %%
print(f"F5 per-slice heatmap SVG: {F5_HEATMAP_SVG}")
print(f"  Exists: {F5_HEATMAP_SVG.exists()}")
print(f"  Size:   {F5_HEATMAP_SVG.stat().st_size if F5_HEATMAP_SVG.exists() else '-'} bytes")
print("  See RESULTS.md §4 for the embedded version.")

# %% [markdown]
# ## Reference: see also
#
# - **`01_canonical_results.ipynb`** — full headline AUPRC + AUROC grids.
# - **`02_frozen_vs_lora.ipynb`** — paired-bootstrap delta + DeLong + BH-FDR (the -0.071 source).
# - **`03_calibration.ipynb`** — reliability + ECE per rung.
# - **`RESULTS.md`** — full 5×5 grid + figures + raw-data pointers.
# - **`WRITEUP/eval-design.md` §5** — AUPRC vs AUROC framing + cross-family OOD methodology.
# - **`WRITEUP/limitations-and-future-work.md` §9.2** — DeBERTa drop reasoning (v1.1.0 lands ablation).
# - **ADR-050** — single-class slice convention + rung-slate narrowing.
# - **ADR-052** — full-FT OOD methodological reframing.
