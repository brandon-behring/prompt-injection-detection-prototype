---
adr_id: "066"
slug: library-first-carryforward-refactor-v1-2-2
title: Library-first carryforward refactor v1.2.2 — consume 7 closed eval-toolkit primitives across 6 sites
date: 2026-05-19
status: Accepted
claim_id: CLAIM-066
claim: >-
  Post-v1.2.1 audit of `decisions/upstream_issues.md` surfaced that ALL 7
  eval-toolkit upstream issues previously documented as "filed; awaiting
  upstream" (#14 `plot_roc_curve`, #15 `plot_pareto_frontier`, #16
  `plot_slice_metric_heatmap`, #17 `n_jobs` for `paired_bootstrap_diff`,
  #20 generalized `mde_from_ci`, #21 `block_bootstrap_on_folds`, #22
  `ax=` kwarg on `plot_metric_bars`) have CLOSED upstream and are exposed
  in the currently-pinned `eval-toolkit==0.42.0` (verified via Python
  attribute check). 6 local workaround sites in `src/eval/`
  (`figures.py::render_f1_pareto` + `render_f2_roc_per_rung` +
  `render_f5_slice_heatmap` + `render_f6_lodo_breakdown`;
  `mde.py::mde_from_marginal_ci_record`;
  `cross_fold_ci.py::compute_cross_fold_ci_cell`) carry TODO comments
  citing these now-closed issues. Per the strengthened library-first
  invariant (memory `library_first_is_project_wide_invariant` 2026-05-18:
  *"NO local workarounds whatsoever. Primitives belong in
  eval-toolkit / runpod-deploy / research_toolkit as PyPI deps; missing
  → upstream MR BLOCKS dependent work"*), this is maintenance debt to
  pay down. v1.2.2 performs the carryforward refactor: each of the 6
  sites consumes the closed upstream primitive; local hand-rolls + unused
  imports are deleted in the SAME commit per the
  `no-orphaned-code-during-refactor` invariant. F1-F6 figures are
  re-rendered via `make render-figures` with visual-parity verification
  per the spirit-of-original threshold (ADR-locked caption discipline
  preserved; cosmetic upstream improvements welcomed). No methodology
  change; refactor only. Pattern after ADR-047 / ADR-056 / ADR-058.
source: transcripts/2026-05-19__v1-2-2-library-first-refactor-and-immutability-clarification.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.2.2 close: 6 local workaround sites in `src/eval/` consume
  upstream primitives (`et.plot_roc_curve` at F2; `et.plot_pareto_frontier`
  at F1; `et.plot_slice_metric_heatmap` at F5;
  `et.plot_metric_bars(ax=...)` at F6 left panel; generalized
  `et.mde_from_ci` at `mde_from_marginal_ci_record`;
  `et.block_bootstrap_on_folds` at `compute_cross_fold_ci_cell`).
  Corresponding `issue #(14|15|16|17|20|21|22)` TODO comments removed
  via `grep -nE "issue #(14|15|16|17|20|21|22)" src/eval/` → 0 hits.
  `decisions/upstream_issues.md` shows status updated to "RESOLVED in
  eval-toolkit v0.42.0; consumed at v1.2.2" for issues #14, #15, #16,
  #17, #20, #21, #22. F1-F6 figures re-rendered cleanly via
  `make render-figures`; ADR-locked caption discipline preserved per
  ADR-062 + ADR-064 §B4. Project glue (`render_*` orchestrator
  wrappers; `MDECellModel` schema; `CrossFoldCICellModel` schema; F5
  N/A overlays; F6 reachability asterisks) stays — only inline numerical
  + plotting impls get replaced. `eval-toolkit` pin unchanged at v0.42.0
  (already exposes all 7 primitives — no pin bump needed). `make smoke`
  + `make site` + lychee + audit-writeup + regenerate-audit-check all
  green on the v1.2.2 push.
closing_commit: v1.2.2
supersedes: []
superseded_by: []
references:
  - decisions/ADR-047-library-first-carryforward-refactor.md  # precedent (Phase 1 src/data/ refactor)
  - decisions/ADR-056-binary-calibrator-family-canonical-upstream-api.md  # precedent (v1.0.8 calibrator consumption)
  - decisions/ADR-058-eval-from-hub-wiring-and-narrow-supersession-of-adr-051-block-a.md  # precedent (v1.0.9 eval_from_hub wiring)
  - decisions/ADR-065-writeup-accuracy-narrative-and-callout-conventions.md  # immediate predecessor (v1.2.1)
  - decisions/upstream_issues.md  # ledger updated as part of v1.2.2 Commit 9
  - decisions/library_imports.md  # eval-toolkit imports section updated at v1.2.2 Commit 9
  - eval-toolkit v0.42.0 (already pinned; no bump)
  - src/eval/figures.py
  - src/eval/mde.py
  - src/eval/cross_fold_ci.py
transcript: transcripts/2026-05-19__v1-2-2-library-first-refactor-and-immutability-clarification.md
---

# ADR-066 — Library-first carryforward refactor v1.2.2

## Status

Accepted (2026-05-19; additive layer on the v1.2.1 polish — no supersession of any prior ADR; this ADR consumes upstream primitives that resolve 7 previously-filed eval-toolkit issues, replacing 6 local workaround sites with library-first calls).

## §A Context

After v1.2.1 close, a survey of deferred work uncovered that **all 7 eval-toolkit upstream issues** previously documented as "filed; awaiting upstream" in `decisions/upstream_issues.md` have CLOSED upstream:

| Upstream issue | Title | Status | Upstream resolution |
|---|---|---|---|
| #14 | Add `plot_roc_curve` (sibling to `plot_pr_curve`) | CLOSED | available in `eval_toolkit.plot_roc_curve` |
| #15 | Add `plot_pareto_frontier` for cost-vs-performance scatter | CLOSED | available in `eval_toolkit.plot_pareto_frontier` |
| #16 | Add `plot_slice_metric_heatmap` for `(group × group × metric)` grids | CLOSED | available in `eval_toolkit.plot_slice_metric_heatmap` |
| #17 | Add `n_jobs` to `paired_bootstrap_diff` | CLOSED | `paired_bootstrap_diff(..., n_jobs=N)` |
| #20 | Generalize `mde_from_ci` to accept `BootstrapCI \| PairedBootstrapCI` | CLOSED | `et.mde_from_ci` accepts both |
| #21 | Add `block_bootstrap_on_folds` (CV-aware block bootstrap) | CLOSED | `et.block_bootstrap_on_folds` |
| #22 | Add `ax=` kwarg to `plot_metric_bars` for shared-axes composition | CLOSED | `plot_metric_bars(..., ax=axes)` |

Verification (via `uv run python -c "import eval_toolkit as et; [hasattr(et, n) for n in ('plot_roc_curve', 'plot_pareto_frontier', 'plot_slice_metric_heatmap', 'plot_metric_bars', 'block_bootstrap_on_folds', 'mde_from_ci', 'paired_bootstrap_diff')]"`): all 7 attributes resolve in the currently-pinned `eval-toolkit==0.42.0`. **No version bump required.**

Per the strengthened library-first invariant (memory `library_first_is_project_wide_invariant`, 2026-05-18: *"NO local workarounds whatsoever. Primitives belong in eval-toolkit / runpod-deploy / research_toolkit as PyPI deps; missing → upstream MR BLOCKS dependent work"*), the 6 local workaround sites that cite these now-closed issues are accumulated maintenance debt. ADR-066 specifies the carryforward refactor pattern + the per-site consumption mapping.

Pattern after [ADR-047](./ADR-047-library-first-carryforward-refactor.md) (Phase 1 `src/data/` carryforward); [ADR-056](./ADR-056-binary-calibrator-family-canonical-upstream-api.md) (v1.0.8 binary-calibrator family consumption); [ADR-058](./ADR-058-eval-from-hub-wiring-and-narrow-supersession-of-adr-051-block-a.md) (v1.0.9 `eval_from_hub.py` wiring).

## §B Decision — per-site refactor mapping

Each of the 6 sites replaces its inline workaround with an upstream-primitive call. Project glue (orchestrator wrappers, schema models, data loaders, project-specific overlay logic) STAYS — only the numerical + plotting impls are replaced.

### B1 — F1 Pareto frontier (`src/eval/figures.py::render_f1_pareto`)

- **Before**: hand-rolled `matplotlib` scatter + frontier polyline (project glue calling `matplotlib.pyplot.scatter` + a custom `_compute_pareto_frontier` helper)
- **After**: `et.plot_pareto_frontier(costs, perfs, ax=axes, ...)` per upstream #15 closure
- **Project glue retained**: `render_f1_pareto` wrapper (data loader from canonical bootstrap parquets; figure_id provenance via `et.save_figure`; ADR-062 caption discipline)
- **Deleted in same commit**: `_compute_pareto_frontier` local helper + unused `numpy` import if no longer used

### B2 — F2 ROC overlay (`src/eval/figures.py::render_f2_roc_per_rung`)

- **Before**: hand-rolled ROC overlay (per-rung `plot` calls with custom AUROC text labels)
- **After**: `et.plot_roc_curve(y_true, y_score, label=..., ax=axes)` per upstream #14 closure; one call per rung onto a shared axes
- **Project glue retained**: per-rung loop + project-specific label formatting + ADR-064 §B4 xlabel discipline
- **Deleted in same commit**: hand-rolled AUROC-text positioning logic if upstream's default placement matches

### B3 — F5 Per-slice heatmap (`src/eval/figures.py::render_f5_slice_heatmap`)

- **Before**: hand-rolled `matplotlib` imshow + tick formatting + cell-value annotation
- **After**: `et.plot_slice_metric_heatmap(values, x_labels, y_labels, ax=axes, ...)` per upstream #16 closure
- **Project glue retained**: N/A overlay on single-class slices per ADR-006 + ADR-062 (single-class slices show `N/A` rather than 0; the overlay is project-shaped since the slice-name → single-class membership mapping is project-specific)
- **Deleted in same commit**: hand-rolled imshow + tick-label formatting

### B4 — F6 LODO breakdown left panel (`src/eval/figures.py::render_f6_lodo_breakdown`)

- **Before**: bare-matplotlib bars (manual `ax.bar(...)` calls) in the left panel because `plot_metric_bars` lacked an `ax=` kwarg
- **After**: `et.plot_metric_bars(metrics, labels, ax=left_ax)` per upstream #22 closure
- **Project glue retained**: right-panel reachability asterisks per ADR-025; A-009 audit-flag overlay; subplot composition (left = bars, right = reachability)
- **Deleted in same commit**: bare-matplotlib bar code in the left panel

### B5 — MDE on marginal CIs (`src/eval/mde.py::mde_from_marginal_ci_record`)

- **Before**: inline closed-form `MDE = z_alpha * (CI_halfwidth / z_beta_minus_one)` workaround (per ADR-006 mandate that EVERY CI gets an MDE; upstream `mde_from_ci` only accepted PairedBootstrapCI)
- **After**: `et.mde_from_ci(bootstrap_ci_record)` per upstream #20 closure (generalized to accept `BootstrapCI | PairedBootstrapCI`)
- **Project glue retained**: `MDECellModel` schema wrapper (cell_id + fold + seed + provenance fields wrapping the numerical MDE value + CI half-width)
- **Deleted in same commit**: inline closed-form computation + fallback note in `src/eval/schemas.py:336`

### B6 — Block-bootstrap on folds (`src/eval/cross_fold_ci.py::compute_cross_fold_ci_cell`)

- **Before**: inline block-bootstrap-on-folds impl (manual block-resampling + percentile CI) used as the "spoke" complement to `cv_clt_ci` per A-008 non-exchangeability auto-flag
- **After**: `et.block_bootstrap_on_folds(per_fold_metrics, n_bootstrap=...)` per upstream #21 closure
- **Project glue retained**: `CrossFoldCICellModel` schema; auto-flag column logic (`block_bootstrap_CI_halfwidth / cv_clt_CI_halfwidth > 1.5` → "LODO non-exchangeability dominates within-fold variance" flag per A-008)
- **Deleted in same commit**: inline block-bootstrap helper function

## §C Decision — figure re-render + visual-parity discipline

After Commits 3-6 land the 6 source-code refactors, Commit 7 re-renders F1-F6 via `make render-figures`. Per Q1 round-8 lock + ADR-062 + ADR-064 §B4:

**Visual-parity threshold**: spirit-of-original; cosmetic upstream improvements welcomed.

- **Required**: ADR-locked caption discipline preserved (random-floor annotation on F1 per ADR-062; F2 xlabel `'LoRA AUPRC minus frozen-probe AUPRC (95% CI; whiskers crossing 0 = indistinguishable)'` per ADR-064 §B4; F3 colorbar `'N/A = single-class slice; AUPRC undefined'`; F4 subpanel suptitle mapping; F5 ECE/Brier ylabel gloss)
- **Required**: semantic content matches v1.2.1 baselines (data points; CI bars; rung order; slice ordering)
- **Acceptable**: cosmetic upstream improvements (palette tones; default tick spacing; legend placement; font sizing)

If an ADR-locked caption-discipline element drops after re-render, the affected figure expands into a focused figure-tuning sub-pass (+15-30 min per affected figure).

GH blob fallback note (per ADR-030): the Quarto site is the canonical reading surface; minor stylistic drift on GH blob is acceptable.

## §D Decision — no-orphaned-code discipline (refactor commit hygiene)

Per the `no-orphaned-code-during-refactor` memory invariant: each refactor commit (3-6) DELETES the local hand-roll + any unused imports in the SAME commit as the upstream-primitive call lands. No transition commits with both paths live.

Specific deletions per commit:
- Commit 3 (F1 + F2): delete `_compute_pareto_frontier` helper; delete unused `numpy.argsort` import if any; delete hand-rolled AUROC-text positioning
- Commit 4 (F5 + F6): delete hand-rolled `imshow` + tick-label code; delete bare-matplotlib `ax.bar` code from F6 left panel
- Commit 5 (mde.py): delete inline closed-form computation; delete fallback note in `src/eval/schemas.py:336`
- Commit 6 (cross_fold_ci.py): delete inline block-bootstrap helper; delete unused `numpy.random` import if any

`ruff` would catch unused imports; manual verification at each commit boundary per the Q2 round-6 self-review directive.

## §E Decision — ledger updates (Commit 9 close)

`decisions/upstream_issues.md` updates: 7 existing rows have Status column updated from "filed; awaiting upstream" → "**RESOLVED in eval-toolkit v0.42.0; consumed at v1.2.2 per ADR-066**". 1 new row appended for the v1.2.2 Commit 8 stretch contribution to eval-toolkit #36 (issue-comment + design-sketch).

`decisions/library_imports.md` updates: existing eval-toolkit imports section gains entries for the 7 newly-consumed primitives (`plot_roc_curve`, `plot_pareto_frontier`, `plot_slice_metric_heatmap`, `plot_metric_bars` with `ax=`, `mde_from_ci` generalized, `block_bootstrap_on_folds`, `paired_bootstrap_diff` with `n_jobs`).

## §F Consequences

### F1 — Library-first invariant honored

The 6 workaround sites that violated the strengthened library-first invariant are paid down. Future contributors writing new eval-toolkit consumer code can dispatch directly into upstream primitives rather than copy-paste-evolve from the deleted local hand-rolls.

### F2 — Audit-trail clarity

The carryforward pattern (consume upstream when it lands; delete local in same commit) is now repeated 4 times (ADR-047 / ADR-056 / ADR-058 / ADR-066). Pattern is durable; future v1.X patches that touch local workarounds can reference this ADR as the canonical pattern.

### F3 — Methodology preserved

No methodology change. Headline AUPRC ladder + ablation results + threshold-policy findings are unchanged. The refactor only replaces inline plotting + numerical impls with upstream-canonical versions; the data they're applied to (canonical bootstrap parquets; per-cell parquets) is unchanged.

### F4 — Figure caption discipline preserved

ADR-062 + ADR-064 §B4 caption discipline is preserved per the spirit-of-original visual-parity threshold (Q1 round-8 lock). Random-floor annotation, CI-crossing-zero cue, N/A single-class label, subpanel mapping, ECE/Brier gloss — all preserved.

### F5 — Cost-trivial

$0 GPU. CPU-only refactor + figure re-render + ADR drafting. Cumulative project compute spend stays $17.08 (within ADR-020 $200 hard cap per ADR-065 §E).

### F6 — Upstream maintainer = consumer-side decision-maker (pattern continued)

Per memory `library-first-pattern-paid-off-twice-v1-0-x`: filing concrete upstream issues with proposed API + workaround resolves quickly when upstream maintainer = consumer-side decision-maker. v1.2.2 confirms the pattern a 3rd time (7 issues filed at Phase 4 / v1.0.6 → resolved in ~weeks → consumed at v1.2.2).

## Linked ADRs

- **References**:
  - [ADR-047](./ADR-047-library-first-carryforward-refactor.md) — Phase 1 `src/data/` carryforward refactor (precedent: 4 hand-rolls retrofitted in single commit)
  - [ADR-056](./ADR-056-binary-calibrator-family-canonical-upstream-api.md) — v1.0.8 binary-calibrator family consumption (precedent: API shape unification after upstream closure)
  - [ADR-058](./ADR-058-eval-from-hub-wiring-and-narrow-supersession-of-adr-051-block-a.md) — v1.0.9 `eval_from_hub.py` wiring (precedent: in-place wiring after upstream resolution)
  - [ADR-065](./ADR-065-writeup-accuracy-narrative-and-callout-conventions.md) — v1.2.1 closing-polish (immediate predecessor)
  - [ADR-062](./ADR-062-quarto-writeup-clarity-and-canonical-figures.md) — figure caption discipline that visual-parity must preserve
  - [ADR-064](./ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md) §B4 — figure caption refinements preserved
  - CLAUDE.md — library-first discipline lives in §"Library-first discipline"
- **Source**: `/exploring-options` rounds 7 + 8 (2026-05-19). Round 7 (6 questions on tier prioritization + ADR structure + pin bump + commit cadence + skip-lines + #36 placement) + Round 8 (4 questions on visual-parity threshold + #36 format + broken-slug-refs approach + ledger format).

## Transcript

`transcripts/2026-05-19__v1-2-2-library-first-refactor-and-immutability-clarification.md` — captures rounds 7 + 8 + the 9-commit execution + per-commit manual-self-review discipline.
