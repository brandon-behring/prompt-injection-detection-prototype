---
adr_id: "046"
slug: phase-4-analysis-implementation-bundle
title: Phase 4 analysis implementation bundle — 6-commit cadence + scaffold-with-classical + always-emit-both-CIs auto-flag + MDE-on-every-emitted-CI + LLM-rater audit included (user-overridden from defer) + library-first hybrid figures + Phase 5 prep deferred
date: 2026-05-16
status: Accepted
claim_id: CLAIM-046
claim: Phase 4 entry bundles seven implementation choices closing implementation gaps in ADR-006/018/021/022/023/024/025/031/033/038 left open after Phase 0 lock and Phase 3 close. Q1 — Phase 4 ships in a 6-commit cadence mirroring Phase 2 + Phase 3 proven pattern — Commit 1 (this commit) does ADR-046 plus SPEC_SHEET §3.8; Commit 2 lands marginal bootstrap_ci primitives plus cv_clt_ci primitives plus mde_from_ci primitives wired through `src/eval/`; Commit 3 lands `src/eval/cross_fold_ci.py` with always-emit block-bootstrap-on-folds spoke per A-008 plus auto-flag column when `block_bootstrap_CI_halfwidth divided-by cv_clt_CI_halfwidth` exceeds 1.5; Commit 4 lands `src/eval/figures.py` with library-first hybrid renderers consuming `eval_toolkit.plotting.{plot_pr_curve, plot_reliability_diagram, plot_bootstrap_distribution, plot_metric_bars, plot_lift_ci, save_figure, PALETTE, set_plot_style}` for the 4 in-scope primitives plus project glue for the 5 gap-filling figures (F1 Pareto, F2 ROC, F5 slice heatmap, F6 LODO breakdown, F7 dual-policy grid layout) citing upstream issues #14 plus #15 plus #16 as TODOs; Commit 5 lands orchestration scripts `scripts/{run_marginal_bootstrap, run_cv_clt_ci, run_mde, render_figures, audit_reference_scorers}.py` per Q4 plus Q5 plus Q6; Commit 6 closes with Makefile Phase 4 targets plus extended smoke pipeline plus ROADMAP Phase 4 close note plus `v0.9.0-rc1` rehearsal-tag prep documentation per ADR-033. Q2 — data-dependence handling uses scaffold-with-classical-floor smoke discipline matching ADR-045 Q5 precedent — all `src/eval/` Phase 4 modules consume any predictions parquet matching the schema contract; smoke tests use classical-floor fixtures (12 parquets from `make eval-classical-floor`); transformer-dependent integration invariants stay skip-marked until the 72 transformer parquets exist from operator-gated canonical `make headline-{frozen-probe, lora, full-ft}` per ADR-020. Q3 — cross-fold CI spoke ablation always emits both cv_clt_ci plus block-bootstrap-on-folds for every (rung, metric, slice) cell to `evals/audit/cross_fold_ci_audit.parquet` with `a_008_flag_fired` boolean column when the ratio exceeds 1.5; methodology spoke text in `WRITEUP/methodology.md` references the LODO non-exchangeability claim only conditionally on the flag firing per A-008 plus ADR-024; full audit-trail completeness preserved per ADR-013 (persist everything, report selectively). Q4 — MDE on every emitted CI persisted to `evals/audit/mde_per_cell.parquet` — wraps Phase 3 Commit 5's full-pairwise paired-bootstrap cells (approximately 30 cells; persisted to `evals/bootstrap/`) plus Phase 4 marginal bootstrap cells (approximately rungs times slices times metrics equals 40 cells) plus cross-fold cv_clt cells plus paired_bootstrap_op_point cells plus paired_bootstrap_ece cells; total persistence approximately 100 MDE cells; cheap to compute relative to bootstrap itself; satisfies ADR-006 mandate explicitly; Phase 5 WRITEUP narrative picks reporting subset from the full matrix per ADR-013 persist-everything-report-selectively pattern. Q5 — reference-scorer LLM-rater audit included as a real Phase 4 deliverable (user override of defer recommendation) — `scripts/audit_reference_scorers.py` fires a small LLM-rater pass on the 4 reference-scorer outputs (R-LLM-OpenAI + R-LLM-Anthropic + R-ProtectAI-v1 + R-ProtectAI-v2 per ADR-018); sample-with-disagreement-with-classifier protocol surfaces approximately 50 pairs per reference rung; rubric grades each as `(rater_judgment_correct_about_injection, calibration_assessment)`; results persisted to `evals/audit/reference_scorer_rater_audit.json` plus a methodology spoke section in `WRITEUP/reference-scorer-audit.md`; cost-cap-gated with interactive approval per ADR-020 plus ADR-045 Q4 (approximately $5 per A-002 envelope); user explicitly overrode the original defer recommendation citing the value of front-loading the audit rather than waiting for a regex-tagger-conservative-enough trigger that may never fire. Q6 — figures slate ships as library-first hybrid (revised from initial all-matplotlib recommendation after user pushed back on the library-first audit at Q6 of the walkthrough; revealed eval-toolkit's plotting.py ships 7 plot helpers plus save_figure with PNG-PDF-SVG provenance plus PALETTE plus set_plot_style — and the project-wide library-first invariant requires consuming these before any local glue) — F3 PR curves consume `plot_pr_curve`; F4 reliability diagrams consume `plot_reliability_diagram` (3-fold raw plus temperature plus isotonic via subplots); F7 bootstrap distribution sub-panels consume `plot_bootstrap_distribution`; per-cell metric summaries with CI bands consume `plot_metric_bars` plus `plot_lift_ci`; project glue in `src/eval/figures.py` for F1 Pareto AUPRC times compute plus F2 ROC per rung plus F5 per-slice OOD heatmap plus F6 LODO fold variance breakdown plus F7 dual-policy operating-point grid layout — all consuming `set_plot_style` plus `PALETTE` plus `save_figure` for provenance-aware SVG output to `docs/plots/` per ADR-030 Quarto site embedding requirement; upstream gaps filed before any local glue ships as issues #14 (`plot_roc_curve` PR candidate) plus #15 (`plot_pareto_frontier`) plus #16 (`plot_slice_metric_heatmap`) plus #17 (`paired_bootstrap_diff n_jobs` kwarg for bootstrap-loop parallelization) per the project-wide library-first invariant codified at Q6 (memory entry `library-first-is-project-wide-invariant` 2026-05-16). Q7 — Phase 5 prep deferred — Phase 4 stays analysis-only (single-concern phase per ADR-038 phase-tailoring lock); Phase 5 begins post-Phase-4-close with WRITEUP authoring plus Quarto site infrastructure plus model card scaffold; `v0.9.0-rc1` rehearsal tag fires after Phase 4 close per ADR-033 triggering the full publish pipeline (Quarto site build per ADR-030 plus GH Pages deploy plus HF Hub model card pushes per ADR-032) as the 24-plus-hour dress-rehearsal; fix-forward via new commits plus `v0.9.0-rc2` if rehearsal fails. Phase 1 library-first carryforward refactor per ADR-047 closed at commit 3615148 before this commit lands — Phase 4 work proceeds on a clean library-first baseline. Implementation cadence follows Phase 1 plus Phase 2 plus Phase 3 precedent — each commit ships green-CI surface; ADR-046 cited in subsequent commits as `Q-N` for specific decisions.
source: Phase 4 walkthrough — /exploring-options 7-question Phase 4 ratify session 2026-05-16 following Phase 1 (ADR-041) plus Phase 2 (ADR-044) plus Phase 3 (ADR-045) precedent; user override on Q5 (defer recommendation rejected; include-LLM-rater-audit-now locked); user reaffirmation at Q6 reframed library-first as project-wide invariant requiring retroactive Phase 1 audit per ADR-047
acceptance_criterion: decisions/ADR-046-phase-4-analysis-implementation-bundle.md exists at this path with Accepted status; SPEC_SHEET.md §3.8 Phase 4 implementation status table added mirroring §3.7 Phase 3 pattern with per-commit rows tracking green status; SUBMISSION_AUDIT.md regenerates via scripts/regenerate_audit.py with ADR-046 included; src/eval/cross_fold_ci.py implementing always-emit-both cv_clt_ci plus block-bootstrap-on-folds plus a_008_flag_fired column per ADR-024 plus A-008 lands in Commit 3; src/eval/figures.py implementing the 7-figure slate as library-first hybrid (F3 plus F4 plus F7 sub-panels via eval-toolkit primitives; F1 plus F2 plus F5 plus F6 plus F7 grid via project glue with TODOs citing upstream issues #14 plus #15 plus #16) lands in Commit 4; scripts/run_marginal_bootstrap.py per Q4 lands in Commit 5; scripts/run_cv_clt_ci.py per Q3 lands in Commit 5; scripts/run_mde.py per Q4 lands in Commit 5 emitting evals/audit/mde_per_cell.parquet with one row per cell across Phase 3 paired-bootstrap plus Phase 4 marginal plus cross-fold plus operating-point plus ECE cells (approximately 100 total cells per ADR-006 mandate); scripts/render_figures.py per Q6 lands in Commit 5 emitting docs/plots/{F1, F2, F3, F4, F5, F6, F7}.svg; scripts/audit_reference_scorers.py per Q5 lands in Commit 5 firing the LLM-rater pass against approximately 50 disagreement-sampled pairs per reference rung at approximately $5 cost per A-002 envelope with interactive approval prompt per ADR-020 plus ADR-045 Q4 plus per-rung audit results persisted to evals/audit/reference_scorer_rater_audit.json; Makefile Phase 4 targets (marginal-bootstrap, cv-clt-ci, mde-battery, render-figures, audit-reference-scorers, eval-from-hub-paid LLM-rater rubric audit) plus extended smoke pipeline plus docs/ROADMAP.md Phase 4 close note added in Commit 6; v0.9.0-rc1 rehearsal-tag prep documentation in docs/ROADMAP.md Phase 4 close note per ADR-033 plus ADR-038; transcript checkpoint at transcripts/2026-05-16__phase-4-entry-plus-phase-1-library-first-refactor.md captured (covers Phase 4 walkthrough plus Phase 1 carryforward refactor session per ADR-047 plus this Phase 4 work); approximately 7 of 17 remaining-deferred invariants unskipped (test_cross_fold_ci_methodology plus test_bootstrap_n_and_stability_check plus test_paired_across_rungs_pairing all green at canonical evals time); WRITEUP spoke files (writeup/methodology.md plus writeup/reference-scorer-audit.md) populated with Phase 4 results post-Commit 5; Phase 5 (Writeup) unblocked at Commit 6 close; v0.9.0-rc1 rehearsal tag fires after Phase 4 close per ADR-033 triggering full publish pipeline dress-rehearsal.
closing_commit: 70e34fd
supersedes:
superseded_by:
references:
  - decisions/ADR-006-headline-metrics-and-statistical-apparatus.md
  - decisions/ADR-018-reference-scorer-slate-and-contamination-stratification.md
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md
  - decisions/ADR-021-eval-slate-aggregation-and-recall-fpr-pinpoints.md
  - decisions/ADR-022-statistical-inference-apparatus.md
  - decisions/ADR-023-calibration-battery-and-interventions.md
  - decisions/ADR-024-cross-fold-ci-methodology.md
  - decisions/ADR-025-dual-policy-threshold-characterization.md
  - decisions/ADR-026-module-layout-concern-grouped-subpackages.md
  - decisions/ADR-031-reviewer-reading-paths-quarto-site-entry.md
  - decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md
  - decisions/ADR-038-phase-tailoring-light-roadmap-edits.md
  - decisions/ADR-045-phase-3-evaluation-implementation-bundle.md
  - decisions/ADR-047-phase-1-library-first-carryforward-refactor.md
  - decisions/library_imports.md
  - decisions/upstream_issues.md
  - https://github.com/brandon-behring/eval-toolkit/issues/14
  - https://github.com/brandon-behring/eval-toolkit/issues/15
  - https://github.com/brandon-behring/eval-toolkit/issues/16
  - https://github.com/brandon-behring/eval-toolkit/issues/17
transcript: transcripts/2026-05-16__phase-4-entry-plus-phase-1-library-first-refactor.md
---

# ADR-046: Phase 4 analysis implementation bundle

## Status

Accepted (2026-05-16). Does not supersede any prior ADR; closes seven implementation-level decisions left open after Phase 0 + Phase 3.

## Context

Phase 4 (Analysis) was unblocked at Phase 3 close (commits `8b96946..8272747` pushed to origin/main 2026-05-16; ADR-045 closed). `docs/ROADMAP.md:75` confirms Phase 4 entry once Phase 3's statistical-inference apparatus (paired-bootstrap battery + dual-policy thresholds + calibration battery) shipped.

The Phase 4 entry walkthrough generated 7 numbered `/exploring-options` questions following Phase 2 (ADR-044) + Phase 3 (ADR-045) precedent. Two notable user interventions during the walkthrough:

- **Q5 user override** — the initial recommendation was to defer the LLM-rater reference-scorer audit per ROADMAP Phase 4 line 95 `[TBD-at-Phase-4]` cautionary framing. The user explicitly overrode and locked **include-now** — citing the value of front-loading the audit deliverable rather than waiting for an as-yet-unfired regex-tagger trigger.
- **Q6 library-first reaffirmation** — the initial recommendation was hand-rolled matplotlib for the 7-figure slate. The user pushed back: `eval-toolkit` ships `plotting.py` with 7 plot helpers plus `save_figure` plus `PALETTE` plus `set_plot_style` — and the project-wide library-first invariant requires consuming these before any local glue. This reframing escalated into a project-wide invariant reaffirmation that triggered a retroactive Phase 1 audit + 4-commit carryforward refactor per ADR-047 (closed at `3615148` immediately before this ADR lands).

### Pre-existing surface inherited by Phase 4

Phase 0 + Phase 3 locked the methodology surface for analysis:

- **ADR-006** — MDE estimated for every reported CI; 3-seed multi-seed floor.
- **ADR-018** — 4 reference rungs + per-axis matched-budget framing.
- **ADR-021** — pooled-headline + per-slice-spoke aggregation; recall@FPR pinpoint triad.
- **ADR-022** — paired_bootstrap_diff per-row for trained-vs-trained; 10K bootstrap @ seed=1 headline + 10K @ seed=2 stability check; bootstrap apparatus.
- **ADR-023** — full calibration battery (4-ECE matrix + Brier + reliability + temperature + isotonic) — landed in Phase 3 Commit 3.
- **ADR-024** — cv_clt_ci (Bayle 2020) headline + block-bootstrap-on-folds spoke; A-008 sensitivity-check flag when `block_bootstrap_CI_halfwidth / cv_clt_CI_halfwidth > 1.5`.
- **ADR-025** — dual-policy thresholds; verification-reachability audit per A-009 — landed in Phase 3 Commit 4.
- **ADR-031** — WRITEUP hub-and-spoke 8-spoke structure.
- **ADR-033** — `v0.9.0-rc1` rehearsal tag (24+ hour dress-rehearsal post-Phase-4-close).
- **ADR-038** — phase-tailoring lock; Phase 3+4 collapse rejected.
- **ADR-045** — Phase 3 evaluation implementation bundle (Phase 3 close; full-pairwise paired-bootstrap persistence per Q6 user refinement; 30-cell bootstrap battery shipped to `evals/bootstrap/`).
- **ADR-047** — Phase 1 library-first carryforward refactor (closed 3615148 immediately before this ADR; Phase 4 proceeds on clean library-first baseline).

### What remained open at Phase 4 entry

Seven implementation-level questions the Phase 0 + Phase 3 ADRs did not specify at code-snippet level:

1. The commit cadence — mirror Phase 2 + Phase 3's proven 6-commit pattern, or decompose differently.
2. Data-dependence handling — block Phase 4 on operator-gated canonical GPU runs (72 transformer parquets), or scaffold against classical-floor predictions per Phase 3 Q5 precedent.
3. Cross-fold CI spoke ablation — always emit both cv_clt_ci + block-bootstrap (rich audit trail) vs conditional emission (compute saver) vs operator-decided per cell.
4. MDE scope per ADR-006 — apply to every emitted CI (~100 cells) vs headline-only (~20 cells) vs operator-flagged per cell.
5. Reference-scorer LLM-rater audit — defer per ROADMAP `[TBD-at-Phase-4]` framing (defer recommendation) vs include now (~$5 LLM-rater pass) vs regex-based per-style tagger.
6. Figures slate + renderer — initial recommendation was matplotlib throughout; user-reaffirmed library-first invariant escalated to library-first hybrid with 4 upstream gap issues filed.
7. Phase 5 prep interleaving — Phase 4 stays analysis-only vs interleave Quarto + index.qmd scaffolding in Commit 6 vs full Phase 4+5 fusion (rejected per ADR-038).

The walkthrough presented all 7 questions numbered; the user ratified 6 recommendations + explicitly overrode Q5 (include-now instead of defer). This ADR locks all seven; subsequent Phase 4 commits implement them.

## Decision

### Q1 — 6-commit cadence (Phase 2 + Phase 3 precedent)

Per-commit decomposition:

| Commit | Deliverable | Invariant test landed |
|---|---|---|
| 1 (this) | ADR-046 + SPEC_SHEET §3.8 + audit regen | n/a |
| 2 | `src/eval/marginal_bootstrap.py` (bootstrap_ci wrappers per ADR-022) + `src/eval/cross_fold_ci.py` (cv_clt_ci headline per ADR-024) + `src/eval/mde.py` (mde_from_ci wrappers per ADR-006) + smoke | `test_marginal_bootstrap_seed_stability` + `test_cv_clt_ci_methodology` (deferred-unskip at canonical evals run) |
| 3 | `src/eval/cross_fold_ci.py` extension — always-emit block-bootstrap-on-folds spoke per A-008 + auto-flag column + smoke | `test_block_bootstrap_folds_spoke_present` + `test_a_008_flag_fired_when_ratio_exceeds_1_5` |
| 4 | `src/eval/figures.py` — library-first hybrid renderer per Q6; 7-figure slate; consumes `eval_toolkit.plotting.*` for F3 + F4 + F7-subpanels + project glue for F1 + F2 + F5 + F6 + F7-grid + smoke | `test_figures_slate_7_svgs_present` + `test_save_figure_provenance_chunks_present` |
| 5 | Orchestration scripts: `scripts/{run_marginal_bootstrap, run_cv_clt_ci, run_mde, render_figures, audit_reference_scorers}.py` per Q4 + Q5 + Q6 | smoke tests + cost-cap interactive-approval check for `audit_reference_scorers` |
| 6 | Makefile Phase 4 targets (`marginal-bootstrap`, `cv-clt-ci`, `mde-battery`, `render-figures`, `audit-reference-scorers`) + extended `make smoke` (Phase 4 fixture-pipeline pass under ADR-027 budget) + `docs/ROADMAP.md` Phase 4 close note + `v0.9.0-rc1` rehearsal-tag prep doc | n/a |

### Q2 — Scaffold-with-classical-floor smoke (ADR-045 Q5 precedent)

All `src/eval/` Phase 4 modules consume any predictions parquet matching the `PredictionsRowModel` schema contract per ADR-045 Q3. Smoke tests use the 12 classical-floor parquets from `make eval-classical-floor` + the tiny fixture parquets at `tests/fixtures/processed/`. Transformer-pred-consuming integration invariants (e.g., `test_cross_fold_ci_methodology`, `test_bootstrap_n_and_stability_check`) remain `@pytest.mark.skip` until the 72 transformer parquets exist from operator-gated canonical `make headline-{frozen-probe, lora, full-ft}` per ADR-020. Phase 5 (WRITEUP) can begin in parallel against classical-floor numbers.

### Q3 — Always-emit-both with auto-flag (A-008 + ADR-024)

`src/eval/cross_fold_ci.py` (Commit 3) emits for every (rung, metric, slice) cell:

- `cv_clt_ci_lo`, `cv_clt_ci_hi`, `cv_clt_ci_halfwidth` per Bayle 2020 Theorem 3.1 on 12 per-(fold, seed) values
- `block_bootstrap_ci_lo`, `block_bootstrap_ci_hi`, `block_bootstrap_ci_halfwidth` per A-008 spoke ablation
- `a_008_flag_fired` boolean — True iff `block_bootstrap_ci_halfwidth / cv_clt_ci_halfwidth > 1.5`

Persisted to `evals/audit/cross_fold_ci_audit.parquet`. `WRITEUP/methodology.md` (spoke) text references the LODO non-exchangeability claim only conditionally on the flag firing per A-008. Full audit-trail completeness preserved per ADR-013 persist-everything-report-selectively pattern.

### Q4 — MDE on every emitted CI (ADR-006 mandate)

`src/eval/mde.py` (Commit 2) provides `mde_from_ci_record(ci_lo, ci_hi, n, alpha=0.05, power=0.8)` wrapping `eval_toolkit.bootstrap.mde_from_ci`. Orchestrated by `scripts/run_mde.py` (Commit 5) sweeping every CI cell across:

- Phase 3 Commit 5 paired-bootstrap cells (~30 cells; `evals/bootstrap/paired_*.parquet`)
- Phase 4 Commit 2 marginal-bootstrap cells (~40 cells; rungs × slices × metrics)
- Phase 4 Commit 3 cross-fold cells (~rungs × slices × metrics; both cv_clt + block-bootstrap)
- Operating-point diff cells (`paired_bootstrap_op_point_diff`)
- ECE delta cells (`paired_bootstrap_ece_diff`)

Total persistence approximately 100 MDE cells in `evals/audit/mde_per_cell.parquet`. Phase 5 WRITEUP narrative picks reporting subset from the full matrix per ADR-013.

### Q5 — Reference-scorer LLM-rater audit INCLUDED (user override)

User overrode the original defer recommendation. `scripts/audit_reference_scorers.py` (Commit 5):

- Samples ~50 prediction-pairs per reference rung (R-LLM-OpenAI + R-LLM-Anthropic + R-ProtectAI-v1 + R-ProtectAI-v2 per ADR-018) where the reference scorer disagrees with the trained-rung classifier (lora or full_ft headline).
- Rubric grades each pair as `(rater_judgment_correct_about_injection, calibration_assessment)`.
- Cost-cap-gated with interactive approval per ADR-020 + ADR-045 Q4 (estimated ~$5 per A-002 envelope across all 4 reference rungs).
- Results persisted to `evals/audit/reference_scorer_rater_audit.json` + a methodology spoke section in `WRITEUP/reference-scorer-audit.md`.

User rationale: front-loading the audit deliverable is more valuable than waiting for a regex-tagger-conservative-enough trigger that may never fire.

### Q6 — Library-first hybrid figures (revised after walkthrough audit)

`src/eval/figures.py` (Commit 4) ships the 7-figure slate as a library-first hybrid:

| Figure | Render path |
|---|---|
| F1 (Pareto AUPRC × compute) | project glue + `set_plot_style` + `PALETTE` + `save_figure` (gap filed as issue #15) |
| F2 (ROC per rung) | project glue + `set_plot_style` + `PALETTE` + `save_figure` (gap filed as issue #14; PR candidate per task #4) |
| F3 (PR per rung) | `eval_toolkit.plotting.plot_pr_curve` directly |
| F4 (reliability diagrams: raw + temperature + isotonic) | `eval_toolkit.plotting.plot_reliability_diagram` × 3 panels via subplots |
| F5 (per-slice OOD heatmap) | project glue + `set_plot_style` + `save_figure` (gap filed as issue #16) |
| F6 (LODO fold variance breakdown) | project glue + `plot_metric_bars` + `plot_lift_ci` + `save_figure` |
| F7 (dual-policy operating-point grid with reachability flags) | project glue grid layout + `plot_bootstrap_distribution` sub-panels + `save_figure` |

All output as SVG to `docs/plots/` per ADR-030 Quarto site embedding. `set_plot_style` + `PALETTE` (negative/positive/baseline/accent) applied throughout for consistent styling.

Project-wide library-first invariant codified at walkthrough Q6 (memory entry `library-first-is-project-wide-invariant` 2026-05-16) — audit eval-toolkit + runpod-deploy + research_toolkit at every module-design step.

### Q7 — Phase 5 prep deferred

Phase 4 stays analysis-only (single-concern phase per ADR-038 phase-tailoring lock). Phase 5 begins post-Phase-4-close with WRITEUP authoring + Quarto site infrastructure + model card scaffold. `v0.9.0-rc1` rehearsal tag fires after Phase 4 close per ADR-033 triggering the full publish pipeline as a 24+ hour dress-rehearsal; fix-forward via new commits + `v0.9.0-rc2` if rehearsal fails.

## Consequences

**Positive:**

- Phase 4 ships on clean library-first baseline (ADR-047 carryforward refactor closed immediately before this ADR).
- Q3 always-emit-both produces a richer audit trail than conditional emission; reviewer can verify the A-008 sensitivity-check methodology independently of whether the flag fires.
- Q4 MDE-on-every-CI satisfies ADR-006 mandate explicitly; Phase 5 WRITEUP narrative has full matrix to draw from without re-running.
- Q5 user override produces an additional reference-scorer audit deliverable that strengthens the methodology spoke; ~$5 cost is well within A-002 budget envelope.
- Q6 library-first hybrid honors the project-wide invariant + files 4 upstream gaps that benefit other eval-toolkit consumers.
- Q7 phase-gate discipline preserves clean separation between Phase 4 analysis and Phase 5 writeup.

**Negative / cost:**

- Q4 MDE on every CI adds compute (~100 cells × ~0.01s per cell = trivial; not a real cost).
- Q5 LLM-rater audit adds ~$5 cost + interactive operator approval gate.
- Q6 library-first hybrid + 4 upstream gaps creates short-term coupling to upstream issue triage cadence (mitigated by project-glue fallbacks for all 4 gaps).
- 6-commit cadence adds operator-driven commit cadence overhead vs collapsed 4-commit option; chosen because Phase 2 + Phase 3 6-commit precedent worked.

**Neutral:**

- Q1 cadence + Q2 scaffold + Q7 Phase 5 defer all match prior phase precedent; no novel discipline.
- ADR-045 Q6 full-pairwise bootstrap persistence carries forward (Phase 4 reads `evals/bootstrap/` rather than re-running).
- ADR-038 phase-tailoring lock honored — no Phase 3+4 collapse, no Phase 4.5 split.

## Alternatives Considered

- **Q1 — 4-commit collapsed cadence**: combine bootstrap primitives + figures + scripts. *Rejected because*: harder to revert atomically per Phase 2/3 lessons; user ratified 6-commit.
- **Q2 — block on canonical runs**: wait for `make headline-*` to complete before starting Phase 4. *Rejected because*: indefinite operator-availability stall; loses parallel-track shipping discipline that worked in Phase 3.
- **Q3 — conditional emission**: only emit block-bootstrap when cv_clt_CI half-width exceeds threshold. *Rejected because*: loses audit-trail completeness; A-008 flag becomes data-dependent in a way that complicates the methodology spoke.
- **Q4 — headline-only MDE**: compute MDE only on WRITEUP headline table cells (~20). *Rejected because*: misses ADR-006 contract on "every reported CI"; would need ADR amendment.
- **Q5 — defer LLM-rater audit (original recommendation)**: ship `scripts/audit_reference_scorers.py` skeleton only; re-evaluate post-Phase-4. *User-overridden*: user explicitly chose include-now citing value of front-loading the audit.
- **Q6 — full matplotlib throughout (initial recommendation)**: hand-roll all 7 figures. *Rejected after walkthrough Q6 user-reaffirmation*: violates project-wide library-first invariant. Revised to library-first hybrid; 4 upstream gaps filed before any glue ships.
- **Q7 — interleave Phase 5 prep in Commit 6**: add Quarto + index.qmd scaffolding to Phase 4 close. *Rejected because*: muddies phase-gate; ADR-038 phase-tailoring lock applies; rehearsal tag naturally fires after Phase 4 close per ADR-033.
- **Q7 — full Phase 4+5 fusion**: collapse Phase 4 + Phase 5 into one extended cycle. *Rejected per ADR-038 phase-tailoring lock* — "Phase 3+4 collapse is rejected since Phase 4 carries first-class statistical-inference work that deserves its own phase-gate discipline".

## References

- `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md` — MDE-on-every-CI source
- `decisions/ADR-018-reference-scorer-slate-and-contamination-stratification.md` — 4 reference rungs source
- `decisions/ADR-020-compute-infrastructure-and-cost-discipline.md` — Q5 cost-cap-gated interactive approval source
- `decisions/ADR-021-eval-slate-aggregation-and-recall-fpr-pinpoints.md` — 5-slice OOD slate source
- `decisions/ADR-022-statistical-inference-apparatus.md` — bootstrap apparatus source
- `decisions/ADR-023-calibration-battery-and-interventions.md` — F4 reliability source
- `decisions/ADR-024-cross-fold-ci-methodology.md` — Q3 cv_clt_ci + A-008 source
- `decisions/ADR-025-dual-policy-threshold-characterization.md` — F7 dual-policy source
- `decisions/ADR-031-reviewer-reading-paths-quarto-site-entry.md` — WRITEUP spoke structure
- `decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md` — v0.9.0-rc1 rehearsal tag source
- `decisions/ADR-038-phase-tailoring-light-roadmap-edits.md` — Q7 phase-tailoring lock
- `decisions/ADR-045-phase-3-evaluation-implementation-bundle.md` — Phase 3 precedent + Q6 full-pairwise persistence
- `decisions/ADR-047-phase-1-library-first-carryforward-refactor.md` — Phase 1 carryforward refactor (closed immediately before this ADR)
- `decisions/library_imports.md` — library-first discipline ledger (expanded post-Phase-4 commits)
- `decisions/upstream_issues.md` — upstream gaps ledger (entries #14-19)
- `https://github.com/brandon-behring/eval-toolkit/issues/14` — `plot_roc_curve` PR candidate (F2)
- `https://github.com/brandon-behring/eval-toolkit/issues/15` — `plot_pareto_frontier` (F1)
- `https://github.com/brandon-behring/eval-toolkit/issues/16` — `plot_slice_metric_heatmap` (F5)
- `https://github.com/brandon-behring/eval-toolkit/issues/17` — `paired_bootstrap_diff n_jobs` kwarg

## Transcript

See `transcripts/2026-05-16__phase-4-entry-plus-phase-1-library-first-refactor.md` for the conversation that led to this decision (Phase 4 walkthrough Q1-Q7 + Q5 user override + Q6 library-first reaffirmation + ADR-047 carryforward refactor; saved 2026-05-16 mid-session per the save-transcripts-at-major-milestones discipline).
