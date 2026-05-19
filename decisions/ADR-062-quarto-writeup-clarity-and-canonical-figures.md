---
adr_id: "062"
slug: quarto-writeup-clarity-and-canonical-figures
title: Quarto writeup clarity rewrite and canonical reviewer figure slate
date: 2026-05-19
status: Accepted
claim_id: CLAIM-062
claim: >-
  User feedback after the v1.1.1 navigation pass found that the Quarto/writeup
  was still too jargon-heavy and dense for a first-time hiring-manager reader:
  the problem setup, metric meaning, plot interpretation, and limits were not
  clear enough. This patch rewrites the first reading path problem-first,
  pushes ADR/process detail below the core story, and replaces the scaffolded
  seven-figure slate with five reviewer-facing figures rendered only from
  canonical eval artifacts. Synthetic scaffold plots remain available only for
  smoke tests outside docs/plots.
source: user request 2026-05-19; implementation plan "Quarto Writeup Clarity Rewrite"
acceptance_criterion: >-
  `index.qmd`, `EXECUTIVE_SUMMARY.md`, `WRITEUP.md`, `RESULTS.md`, README,
  READING_GUIDE, and GLOSSARY explain the problem, metrics, headline result,
  plots, and limitations in plain language before deep methodology detail.
  `scripts/render_figures.py --out-dir docs/plots` renders exactly F1-F5 from
  committed canonical artifacts under evals/; each sidecar records
  `data_mode: canonical`, ADR-062, commit SHA, generation time, and source
  artifact paths. `--scaffold` refuses to write to docs/plots and is test-only.
  F6/F7 scaffold figures are removed from the reviewer-facing path. Quarto site
  renders cleanly and smoke tests pass.
closing_commit: pending implementation commit
supersedes: [ADR-046, ADR-054, ADR-061]
superseded_by: []
references:
  - decisions/ADR-046-phase-4-analysis-implementation-bundle.md
  - decisions/ADR-054-results-page-as-third-entry-artifact-extending-adr-053.md
  - decisions/ADR-061-quarto-site-navigation-restructure.md
  - evals/bootstrap/marginal_cells.parquet
  - evals/bootstrap/paired_cells.parquet
  - evals/metrics/per_cell.parquet
  - evals/operating_points/dual_policy.parquet
transcript: transcripts/2026-05-19__quarto-writeup-clarity-rewrite.md
---

# ADR-062: Quarto Writeup Clarity and Canonical Figures

## Status

Accepted (2026-05-19; implementation patch for the live Quarto site).

## Context

ADR-061 fixed navigation, but the first reading path still assumed too much
ML/evaluation vocabulary. A first-time reviewer needed to infer why prompt
injection matters, what the classifier was asked to do, what AUPRC/AUROC/FPR
mean, and how to read the plots.

Inspection also found that `docs/plots/F1-F7.svg` had been generated through
the scaffold path in `scripts/render_figures.py`. Those plots were useful for
testing the rendering pipeline, but they were not safe as reviewer-facing
evidence because their numbers did not come from the canonical `evals/`
artifacts.

## Decision

Rebuild the reviewer path around plain-language interpretation:

- Problem first: prompt injection is untrusted text trying to override an LLM
  system's instructions.
- Result second: no evaluated rung clearly beats the random AUPRC floor on the
  pooled cross-family OOD slice.
- Evidence third: exact tables plus a small canonical plot slate.
- Methodology/process detail remains available, but below the first-path story.

The reviewer-facing plot slate becomes five figures:

1. Pooled OOD AUPRC by rung vs the prevalence baseline.
2. Frozen-probe vs LoRA paired AUPRC deltas on comparable both-class slices.
3. Per-slice AUPRC grid, with single-class slices explicitly marked `N/A`.
4. Detection-threshold transfer against the 1% FPR target.
5. Calibration comparison using ECE and Brier.

`scripts/render_figures.py` must read canonical artifacts by default. The
`--scaffold` mode is retained for smoke tests only and refuses to write to
`docs/plots`.

## Consequences

- The live site becomes clearer for the intended hiring-manager audience.
- The main figures now align with the numerical tables and provenance sidecars.
- F6/F7 remain historical Phase 4 concepts, but they are no longer embedded in
  the main reviewer path unless regenerated from canonical artifacts in a
  future ADR.
- The figure renderer still uses eval-toolkit primitives where available:
  `set_plot_style`, `PALETTE`, `plot_lift_ci`, `plot_slice_metric_heatmap`, and
  `save_figure`. Remaining matplotlib code is project-specific composition.

## Alternatives Considered

- **Caption-only fix**: rejected because scaffold-derived plots should not stay
  in the reviewer path with stronger prose.
- **Tables-only results page**: rejected because the hiring-manager path needs
  visual support, but exact values still belong in tables.
- **Keep ADR/process detail prominent**: rejected for the first reading path;
  methodology rigor remains linked and auditable, just not front-loaded.
