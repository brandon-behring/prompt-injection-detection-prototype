# Next steps

Forward-looking work organized in two tiers: **tactical** (incremental items that fit on top of the project's infrastructure) and **aspirational** (clean-slate directions that would require rethinking the design). Each entry leads with a *why*; without one, the entry is decoration.

---

## 1. Tactical next steps

Concrete items already scoped from the seed; populated incrementally during Phases 1-5.

### 1.1 Demo notebooks (Phase 2+)

*Why*: paper-figure notebooks are reviewer-facing deliverables; paired `.ipynb` + `.py` (via `jupytext`) lets reviewers diff notebook logic, not just outputs.
*Scope*: `notebooks/01_canonical_results.ipynb` (headline table population); `02_frozen_vs_lora.ipynb` (paired-bootstrap rung-comparison); `03_calibration.ipynb` (reliability curves + ECE per rung); `04_ood_slate.ipynb` (per-slice IID-vs-OOD gap viz).
*Effort*: ~1 hour per notebook once Phase 4 analysis outputs exist. Library-first: use `eval_toolkit.bootstrap_ci` / `plot_pr_curve` / `plot_reliability_diagram`.
*Status (v1.0.6)*: carryforward to v1.0.7. Jupytext config + `notebooks/README.md` scaffolded at Phase 2; 4 notebooks themselves deferred to v1.0.7 (Path 3 close per /exploring-options batches 7-9).
*Status (v1.0.7)*: **closed**. 4 jupytext-paired notebooks (`01_canonical_results` + `02_frozen_vs_lora` + `03_calibration` + `04_ood_slate`) landed with frozen output cells per batch 9 Q2 lock. Rendered via Quarto + linked from new "Notebooks" sidebar section + navbar menu. `make notebooks` target available for operator re-render.

### 1.2 Analysis output templating

*Why*: reproducibility benefits when each analysis run lives in a versioned directory with consistent CSV/Parquet outputs.
*Scope*: establish `analysis/v<version>_<name>/` directory structure with metadata header (analyzer version, date, config hash). Outputs: `paired_tests.csv` (fold × seed × delta_prauc + CI bounds + DeLong + BH-FDR), `ece_per_cell.csv` (calibration per scorer/fold/method), `per_source_rates.csv` (label audit).
*Effort*: ~30 min scaffolding + per-analysis ~15 min.
*Status (v1.0.6)*: outputs partially landed at `evals/` flat structure (parquet not CSV; `paired_cells.parquet` + `per_cell.parquet` exist); CSV mirror + `per_source_rates.csv` + `analysis/v1.0.7_canonical/` versioned dir deferred to v1.0.7 (Path 3; 1:1 parquet mirror per /exploring-options batch 9 Q3).
*Status (v1.0.7)*: **closed**. `scripts/export_analysis_csvs.py` generates `analysis/v1.0.7_canonical/` with `paired_tests.csv` (40 rows; 1:1 mirror) + `ece_per_cell.csv` (114 rows; 1:1 mirror) + `per_source_rates.csv` (282 rows; NEW label-audit aggregation from prediction parquets). `make export-analysis-csvs` target available for regen.

### 1.3 Paired bootstrap + DeLong infrastructure (Phase 4+)

*Why*: paired comparisons across rungs need paired-error correlation handling; DeLong gives parametric AUC-difference CI for sanity-check; BH-FDR corrects multi-comparison.
*Scope*: use `eval_toolkit.paired_bootstrap_diff` + DeLong primitive. Wire into `notebooks/02_frozen_vs_lora.ipynb`.
*Effort*: ~2 hours including the BH-FDR wrapper.
*Status (v1.0.6)*: `paired_bootstrap_diff` landed at v0.9.0-rc series via `scripts/run_bootstrap_battery.py:46` (40 cells × 2 seeds persisted). BH-FDR is now trivially library-first via `eval_toolkit.bootstrap.fdr_bh_correct` (eval-toolkit v0.32.0+; just unused locally). DeLong (`eval_toolkit.bootstrap.delong_roc_variance`) also available upstream + unused. Both wired in v1.0.7 `notebooks/02_frozen_vs_lora` (Path 3 close).
*Status (v1.0.7)*: **closed**. `notebooks/02_frozen_vs_lora.ipynb` wires DeLong `delong_roc_variance` + BH-FDR `fdr_bh_correct` + paired-bootstrap deltas in a 3-method cross-check on the LoRA -0.071 vs frozen-probe headline finding. All 3 methods agree.

### 1.4 Calibration audit suite (Phase 3-4)

*Why*: deployment-policy claims require calibrated probabilities; ECE alone is incomplete — reliability curves + Brier + temperature/Platt/isotonic fits round out the audit.
*Scope*: `eval_toolkit.calibration` (Platt + Beta + Isotonic + ECE equal-mass + ECE debiased + Brier + reliability_curve). Render in `03_calibration.ipynb`.
*Effort*: ~3 hours including notebook narrative.
*Status (v1.0.6)*: 6 of 7 components landed (ECE equal-mass + Brier + reliability curves + temperature + isotonic + four-ECE-variant matrix). Platt + Beta NOT in eval-toolkit v0.39.0; **upstream issue [#43](https://github.com/brandon-behring/eval-toolkit/issues/43) filed at v1.0.6** per /exploring-options batch 8 Q1 lock (library-first invariant). v1.0.8 will consume upstream when shipped; otherwise §1.4 close deferred to v1.1.x. Notebook deferred to v1.0.7 `notebooks/03_calibration`.
*Status (v1.0.8)*: **closed**. Upstream #43 closed in v0.40.0 (~17 min after filing — fastest turnaround of v1.0.x series). v1.0.8 lands the full 4-calibrator binary battery (temperature + isotonic + Platt + Beta) uniformly on the eval-toolkit `_binary` API per ADR-056. Code surface shrunk ~60 lines (`proba_to_logprobs` + `apply_temperature` helpers deleted). Local `fit_isotonic_binary_local` adapter pending upstream [#44](https://github.com/brandon-behring/eval-toolkit/issues/44) (filed v1.0.8; remove when ships).

### 1.5 Leakage audit framework (Phase 1-4)

*Why*: SHA-256 disjoint check + TF-IDF cross-split check catches train↔test contamination; both invariants currently land in `manifest.json` guardrails.
*Scope*: integrate `eval_toolkit.leakage` primitives into the data-loading + eval pipelines; fail-loud if any guardrail asserts.
*Effort*: ~2 hours.
*Status (v1.0.6)*: **closed**. SHA-256 + TF-IDF cosine ≥ 0.85 checks landed via `src/data/audit.py` (eval_toolkit.leakage primitives); `evals/leakage_report.json` carries clean flag. v1.0.6 adds the missing enforcement layer: CI hard-gate at `.github/workflows/ci.yml::leakage` + `tests/test_invariants.py::test_leakage_report_clean` + standalone `scripts/audit_leakage.py` + `make audit-leakage` target. ADR-039 gate 3 intent now met for the leakage axis.

### 1.6 HYPERPARAMETER_DISCLOSURE depth (Phase 5)

*Why*: reviewers may suspect cherry-picking; disclosing what was explored vs deliberately not explored is the anti-cherry-pick defense.
*Scope*: expand `docs/HYPERPARAMETER_DISCLOSURE.md` to four sections: §1 seed recipe (locked values), §2 exploration trajectory (what was actually swept), §3 axes held constant (why deferred), §4 caveats (budget-dependence, etc.).
*Effort*: ~1 hour once Phase 4 controls have run.
*Status (v1.0.0)*: **closed**. All 4 prescribed sections present at `docs/HYPERPARAMETER_DISCLOSURE.md` (196 lines).

### 1.7 EXECUTIVE_SUMMARY (Phase 5, written LAST)

*Why*: 1-page decision-maker-facing layer above the full WRITEUP. Reviewer who skims first reads this; deep-readers continue to WRITEUP.
*Scope*: `EXECUTIVE_SUMMARY.md` at repo root — headline characterization claims (max 4), what's locked vs deferred, recommended-reading-order pointer.
*Effort*: ~1 hour; written **after** Phase 5 WRITEUP narrative stabilizes.
*Status (v1.0.3+)*: Landed at v1.0.3 (`EXECUTIVE_SUMMARY.md` at repo root, not under `docs/`). Role retroactively anchored at v1.0.4 via [ADR-053](decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md) — `EXECUTIVE_SUMMARY` is one of the two governed entry artifacts (decision-maker layer); `index.qmd` is the parallel reviewer-landing reading guide with interpretation pedagogy.

### 1.8 Generic citation auditor (Phase 3-5)

*Why*: WRITEUP / EVIDENCE will accumulate citations to `docs/research/<topic>/<file>.md:<line>` and external URLs. A machine-enforced auditor (CI hard-gate) prevents broken citations as the writeup grows.
*Scope*: `scripts/audit_citations.py` — scans `.md` files for citation patterns (`docs/research/<path>` + `<file>:<line>` + external URLs); verifies cited files exist + lines exist + URLs respond. Add as CI hard-gate alongside `regenerate_audit.py`.
*Effort*: ~3 hours.
*Status (v1.0.6)*: **closed as not-adopted** per /exploring-options batch 8 Q2 lock. WRITEUP + spokes use standard markdown link syntax (`[text](path)`) + EVIDENCE.md as the external-citation audit surface; the `<file>:<line>` citation pattern was never load-bearing for the project's documentation discipline. No auditor needed; CI gate not added.

### 1.9 Manifest backfill pipeline (Phase 4+)

*Why*: post-eval-run manifest fixups (injecting `git_sha` + `config_hash` + `contamination_flags` if the eval-toolkit version doesn't emit them automatically).
*Scope*: `scripts/backfill_provenance.py` — reads `evals/<run>/predictions.parquet` + `config.yaml` + `git log`; emits `manifest.json` per the upstream schema.
*Effort*: ~2 hours.
*Status (v1.0.6)*: carryforward to v1.0.8. Provenance currently distributed across `evals/{data_audit,results,leakage_report,contamination_scan,dedup_calibration}.json`; prediction parquets lack `git_sha` / `config_hash` / `contamination_flags` columns. v1.0.8 lands `scripts/backfill_provenance.py` + new ADR-055 (Manifest schema v3 backfill conventions) per Path 3 close.
*Status (v1.0.8)*: **closed**. `scripts/backfill_provenance.py` emits 282 per-prediction manifest JSON files at `evals/manifests/<rung>__<fold>__<seed>__<slice>.json` per ADR-057 (manifest schema v3). Each manifest carries git_sha + config_hash + contamination_flag (ADR-005 3-tier taxonomy) + rung/fold/seed/slice/n_rows + predictions_relpath. 3 filename patterns supported (trained-with-tail + trained-no-tail + reference). `make backfill-provenance` target + `--check` mode for CI integration. Per-prediction (not column injection) — non-destructive to source-of-truth parquets per /exploring-options batch 11 Q1 lock.

### 1.10 DeBERTa-v3-base long-context ablation (v1.1.x)

*Why*: indirect injection (BIPIA email-body) is the dominant cross-family OOD gap surfaced in v1.0.x. A long-context comparator (ModernBERT-base 8192 native) vs short-context (DeBERTa-v3-base 512 with explicit truncation handling) ablation would isolate context-length effect from architecture effect on BIPIA-style indirect injection.

Prior v4/v5 iterations of this project did partial DeBERTa-v3 tests but had to manage truncation differently across the two backbones; in this submission DeBERTa was deliberately dropped at Phase 0 per ADR-015 to avoid the truncation × architecture confound on the headline rung-vs-rung comparison (`WRITEUP/limitations-and-future-work.md` §9.2 documents the drop reasoning).

*Scope*: v1.1.x iteration adds DeBERTa-v3-base as a separately-evaluated rung with a controlled truncation strategy (e.g., chunk-and-average over 512-token windows vs head-truncation) so the truncation handling is methodologically addressable rather than load-bearing for the architecture comparison. Lands as an ablation appendix, not a co-equal rung in the headline ladder.

*Effort*: ~3-4 hours wallclock if the truncation-handling design lands quickly; longer if the chunk-and-average baseline needs validation against the source-disjoint LODO protocol.
*Status (v1.0.6)*: carryforward to v1.1.0 — same-session per Path 3 batch 8 Q3 lock. Medium-ablation scope locked (2 truncation strategies × full 5-slice OOD slate; ablation-appendix framing in RESULTS §1B; NOT integrated as 6th rung; ~$8-10 GPU; new ADR-057 for truncation methodology).

*Status (v1.1.0)*: **methodology landed (ADR-060); execution deferred to v1.1.1**. /exploring-options 2026-05-19 surfaced a scope-mismatch — the existing training pipeline (`src/training/train_modernbert.py` + `src/training/load_modernbert.py`) is ModernBERT-specific by construction; adding DeBERTa requires loader refactor + windowed-inference module + eval-pipeline integration (~4-6h infrastructure work BEFORE any GPU fire). User picked **Path B**: land the methodology lock + scaffolds (ADR-060 + `configs/rungs/deberta_v3_base.yaml` + `configs/runpod/headline-deberta.yaml` + Makefile target stubs + RESULTS §1B placeholder) at v1.1.0; defer execution to v1.1.1. v1.1.0 = $0 GPU. v1.1.1 = ~$5-7 GPU + ~4-6h infrastructure. The methodology lock (single fold/seed, 2 truncation strategies, 5-slice OOD eval, ablation-appendix framing) is binding regardless of when execution lands.

*Status (v1.2.0)*: **clarity pass landed** — the v1.1.2 execution result (chunk_and_average vs head_truncation pooled OOD AUPRC ~0.29) is now narrated in RESULTS §1B with the backbone-dominant interpretation, cross-referenced from WRITEUP/limitations-and-future-work.md §9.2, and surfaced on the dedicated hiring-manager landing page at `docs/for-hiring-managers.md`. ADR-064 (writeup hiring-manager clarity + documentation-wide consistency pass) records the polish layer + 9-broken-slug-ref flag in immutable ADRs + canonical terminology table. CI markdown-link-checker (lychee) introduced at v1.1.4 prevents recurrence.

*Status (v1.1.2)*: **execution landed**. Slot-shift from the ADR-060 body's "v1.1.1" wording: that slot was consumed by ADR-061 (Quarto navigation restructure) so DeBERTa execution carried forward to v1.1.2 (ADR-060 stays immutable; commit messages document the slot shift). Phase A refactored `load_modernbert` → `load_backbone(*, hf_id, revision, ...)`; Phase B added `src/inference/windowed.py` (chunk-and-average + head-truncation strategies); Phase C wired training dispatch + Makefile targets; Phase D fired both strategies on A100-SXM4-80GB (US-MD-1) sharing a warm pod via `lifecycle.on_success: recycle`. **Headline result** (`evals/metrics/per_cell_deberta.parquet`, pooled OOD AUPRC, epoch-2): `chunk_and_average` = 0.2912; `head_truncation` = 0.2895. The 2 truncation strategies produce **essentially identical** per-slice metrics across the 5-slice OOD slate — publishable null result. By the ADR-060 confound-control interpretation, this indicates the ModernBERT advantage on the headline ladder is **backbone-dominant**, not context-window-dominant. Actual GPU spend: **$1.34** (well under the $5-7 envelope; 9 pod manifests across 7 short failures + 2 successful fires; see `evals/cost_ledger.csv`). Fix-cycle of 7 commits (sentencepiece + protobuf deps + FUSE workaround moving project to /root + fp32 numerical stability + YAML-driven training overrides + checkpoint path doubling + drop staging bounce) before the 8th commit (the load-bearing fp32 fix) cleared all training-time errors.

*Cumulative project compute spend (canonical figure)*: **$17.08** (full precision $17.0807; sum of `actual_cost_usd` across all 17 GPU-pod rows in `evals/cost_ledger.csv` as of v1.2.0 close, commit `3212cc5`, 2026-05-19). Within ADR-020's $200 hard cap. See [ADR-065](decisions/ADR-065-writeup-accuracy-narrative-and-callout-conventions.md) §E for provenance; supersedes ADR-063's stale $9.92 (flagged in ADR-064 §D; computed at v1.2.1).

---

## 2. Aspirational future directions

Things that would require rethinking the project's design rather than extending it. These are not commitments; they are the contour of where the next iteration might go.

### 2.1 Multi-seed × multi-fold canonical evidence (GPU-intensive)

*Why*: at submission scope, single-seed evaluation suffices for honest characterization. A future iteration with broader compute budget could run 3 seeds × 3 folds × N scorers for tighter CIs + cross-seed variance reporting.
*What the project was missing*: GPU budget for multi-seed sweeps; deferred to a future iteration with explicit `[OPEN: multi-seed protocol]` lock.

### 2.2 Full reference-detector appendix

*Why*: the seed scopes reference scorers minimally; a future iteration could run multiple off-the-shelf detectors with full training-overlap audit per the three-state taxonomy.
*What the project was missing*: reviewer-explicit demand for off-the-shelf comparisons; deferred to a separate appendix track.

### 2.3 Multi-source LODO with full semantic-dedup pipeline

*Why*: source-disjoint k=3 LODO with calibrated MiniLM-style semantic dedup + TF-IDF same-label hard gate + cross-label warn gate is the gold-standard data discipline. The seed locks the discipline; full pipeline + per-fold leakage audit could land at Phase 1+.
*What the project was missing*: time to set up the full dedup-calibration loop + leakage-audit pipeline within scope.

### 2.4 Refactor F1/F2/F5 figures to use upstream eval-toolkit plot_* primitives (v1.2.0+)

*Why*: library-first invariant. eval-toolkit v0.36+ shipped `plot_roc_curve` (#14; F2 source), `plot_pareto_frontier` (#15; F1 source), `plot_slice_metric_heatmap` (#16; F5 source) — exactly the figure types our hand-rolled implementations cover at `src/eval/figures.py::render_f1_pareto` / `render_f2_roc_overlay` / `render_f5_per_slice_heatmap`. Deferred from v1.0.7 to avoid scope creep on the notebook patch.
*Scope*: replace 3 hand-rolled rendering functions with upstream primitive calls; delete the local implementations (no-orphaned-code invariant); re-render F1/F2/F5 to verify visual parity. ~2 hours.
*Trigger*: next figure regen need (e.g., post-DeBERTa-ablation re-render that pulls F5 per-slice heatmap with the 6th rung in scope) OR v1.2.0+ polish patch (whichever lands first). Note: v1.1.1 was consumed by ADR-061 (Quarto navigation restructure) so the original "v1.1.1 polish patch" plan shifted; the canonical-figures rewrite at v1.1.3 (ADR-062) already adopted several library primitives, narrowing this future-work item.
*Status (v1.0.6)*: deferred per /exploring-options batch 8 Q4 lock.

---

## 3. Open questions raised during the project

Open questions surfaced during Phase 0-5; not yet answered. Each is a
genuine candidate for a future iteration's research-plan slot.

- **Does the contamination-tier ordering hold under harder OOD slates?**
  ADR-005's three-state taxonomy (`verified_disjoint` <
  `backbone-partial-disjoint` < `suspected_contamination`) was inferred
  from a single OOD slate composition (BIPIA + InjecAgent + JBB + XSTest +
  NotInject). A harder slate — adversarial-style attacks not in the
  training corpus — might re-order the rungs or compress the gap. The
  invariant test ordering (frozen-probe < LoRA < full-FT on LODO) may not
  generalize.
- **Does the LoRA → full-FT gap survive higher seed counts?** Phase 4
  ran 3 seeds × 4 folds; the LoRA-vs-full-FT gap on LODO sits within
  the paired-bootstrap CI. A 5-seed or 10-seed run would either widen
  the gap into significance or confirm that the marginal capacity from
  full-FT doesn't pay for itself on this data scale.
- **Does the single-class-slice convention generalize beyond AUPRC /
  AUROC?** The skip-filter rule (locked at Phase 5 — see WRITEUP §5 and
  the SUBMISSION_AUDIT regen at ADR-050) drops single-class rows from
  AUPRC/AUROC artifacts but leaves them in calibration metrics (ECE,
  Brier, reliability curves). ECE on an all-positive slice is still
  defined but may carry similar pathologies; a future iteration could
  surface a unified "metric-defined-for-this-slice-composition" type
  primitive in `eval-toolkit`.

---

## 4. What the project deliberately doesn't do

Pointer rather than restatement. See [`WRITEUP.md` §8](./WRITEUP.md) for the consolidated deferred list and [`WRITEUP.md` §9](./WRITEUP.md) for architectures and approaches that were tried and abandoned. The distinction matters: §8 = scope; §9 = experimental dead-ends.

---

## 5. Upstream contributions

When Phase 1+ work discovers gaps in `eval-toolkit` / `runpod-deploy` / `research_toolkit`, the gaps become upstream issues per the anti-hand-rolling discipline. See `decisions/upstream_issues.md` for the live ledger.
