# Next steps

Forward-looking work organized in two tiers: **tactical** (incremental items that fit on top of the project's infrastructure) and **aspirational** (clean-slate directions that would require rethinking the design). Each entry leads with a *why*; without one, the entry is decoration.

---

## 1. Tactical next steps

Concrete items already scoped from the seed; populated incrementally during Phases 1-5.

### 1.1 Demo notebooks (Phase 2+)

*Why*: paper-figure notebooks are reviewer-facing deliverables; paired `.ipynb` + `.py` (via `jupytext`) lets reviewers diff notebook logic, not just outputs.
*Scope*: `notebooks/01_canonical_results.ipynb` (headline table population); `02_frozen_vs_lora.ipynb` (paired-bootstrap rung-comparison); `03_calibration.ipynb` (reliability curves + ECE per rung); `04_ood_slate.ipynb` (per-slice IID-vs-OOD gap viz).
*Effort*: ~1 hour per notebook once Phase 4 analysis outputs exist. Library-first: use `eval_toolkit.bootstrap_ci` / `plot_pr_curve` / `plot_reliability_diagram`.

### 1.2 Analysis output templating

*Why*: reproducibility benefits when each analysis run lives in a versioned directory with consistent CSV/Parquet outputs.
*Scope*: establish `analysis/v<version>_<name>/` directory structure with metadata header (analyzer version, date, config hash). Outputs: `paired_tests.csv` (fold × seed × delta_prauc + CI bounds + DeLong + BH-FDR), `ece_per_cell.csv` (calibration per scorer/fold/method), `per_source_rates.csv` (label audit).
*Effort*: ~30 min scaffolding + per-analysis ~15 min.

### 1.3 Paired bootstrap + DeLong infrastructure (Phase 4+)

*Why*: paired comparisons across rungs need paired-error correlation handling; DeLong gives parametric AUC-difference CI for sanity-check; BH-FDR corrects multi-comparison.
*Scope*: use `eval_toolkit.paired_bootstrap_diff` + DeLong primitive. Wire into `notebooks/02_frozen_vs_lora.ipynb`.
*Effort*: ~2 hours including the BH-FDR wrapper.

### 1.4 Calibration audit suite (Phase 3-4)

*Why*: deployment-policy claims require calibrated probabilities; ECE alone is incomplete — reliability curves + Brier + temperature/Platt/isotonic fits round out the audit.
*Scope*: `eval_toolkit.calibration` (Platt + Beta + Isotonic + ECE equal-mass + ECE debiased + Brier + reliability_curve). Render in `03_calibration.ipynb`.
*Effort*: ~3 hours including notebook narrative.

### 1.5 Leakage audit framework (Phase 1-4)

*Why*: SHA-256 disjoint check + TF-IDF cross-split check catches train↔test contamination; both invariants currently land in `manifest.json` guardrails.
*Scope*: integrate `eval_toolkit.leakage` primitives into the data-loading + eval pipelines; fail-loud if any guardrail asserts.
*Effort*: ~2 hours.

### 1.6 HYPERPARAMETER_DISCLOSURE depth (Phase 5)

*Why*: reviewers may suspect cherry-picking; disclosing what was explored vs deliberately not explored is the anti-cherry-pick defense.
*Scope*: expand `docs/HYPERPARAMETER_DISCLOSURE.md` to four sections: §1 seed recipe (locked values), §2 exploration trajectory (what was actually swept), §3 axes held constant (why deferred), §4 caveats (budget-dependence, etc.).
*Effort*: ~1 hour once Phase 4 controls have run.

### 1.7 EXECUTIVE_SUMMARY (Phase 5, written LAST)

*Why*: 1-page decision-maker-facing layer above the full WRITEUP. Reviewer who skims first reads this; deep-readers continue to WRITEUP.
*Scope*: `docs/EXECUTIVE_SUMMARY.md` — headline characterization claims (max 4), what's locked vs deferred, recommended-reading-order pointer.
*Effort*: ~1 hour; written **after** Phase 5 WRITEUP narrative stabilizes.

### 1.8 Generic citation auditor (Phase 3-5)

*Why*: WRITEUP / EVIDENCE will accumulate citations to `docs/research/<topic>/<file>.md:<line>` and external URLs. A machine-enforced auditor (CI hard-gate) prevents broken citations as the writeup grows.
*Scope*: `scripts/audit_citations.py` — scans `.md` files for citation patterns (`docs/research/<path>` + `<file>:<line>` + external URLs); verifies cited files exist + lines exist + URLs respond. Add as CI hard-gate alongside `regenerate_audit.py`.
*Effort*: ~3 hours.

### 1.9 Manifest backfill pipeline (Phase 4+)

*Why*: post-eval-run manifest fixups (injecting `git_sha` + `config_hash` + `contamination_flags` if the eval-toolkit version doesn't emit them automatically).
*Scope*: `scripts/backfill_provenance.py` — reads `evals/<run>/predictions.parquet` + `config.yaml` + `git log`; emits `manifest.json` per the upstream schema.
*Effort*: ~2 hours.

### 1.10 DeBERTa-v3-base long-context ablation (v1.1.x)

*Why*: indirect injection (BIPIA email-body) is the dominant cross-family OOD gap surfaced in v1.0.x. A long-context comparator (ModernBERT-base 8192 native) vs short-context (DeBERTa-v3-base 512 with explicit truncation handling) ablation would isolate context-length effect from architecture effect on BIPIA-style indirect injection.

Prior v4/v5 iterations of this project did partial DeBERTa-v3 tests but had to manage truncation differently across the two backbones; in this submission DeBERTa was deliberately dropped at Phase 0 per ADR-015 to avoid the truncation × architecture confound on the headline rung-vs-rung comparison (`WRITEUP/limitations-and-future-work.md` §9.2 documents the drop reasoning).

*Scope*: v1.1.x iteration adds DeBERTa-v3-base as a separately-evaluated rung with a controlled truncation strategy (e.g., chunk-and-average over 512-token windows vs head-truncation) so the truncation handling is methodologically addressable rather than load-bearing for the architecture comparison. Lands as an ablation appendix, not a co-equal rung in the headline ladder.

*Effort*: ~3-4 hours wallclock if the truncation-handling design lands quickly; longer if the chunk-and-average baseline needs validation against the source-disjoint LODO protocol.

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
