---
adr_id: 025
slug: dual-policy-threshold-characterization
title: Dual-policy threshold characterization at symmetric 1% cost weights
date: 2026-05-15
status: Accepted
claim_id: CLAIM-025
claim: Phase 0-05 locks the §4 Threshold ledger row 347 (cost-weight targets) at the per-rung operational level as follows. (1) Numeric cost-weight targets — symmetric 1% on both policy budgets. Detection policy targets FPR ≤ 1% on validation via eval_toolkit.TargetFPRSelector(0.01); Verification policy targets FNR ≤ 1% (equivalently recall ≥ 99%) on validation via eval_toolkit.TargetRecallSelector(0.99). The detection-policy operating point numerically coincides with the recall@FPR=1% headline pinpoint already locked in ADR-021 — the dual-policy framing relabels the existing column with a footnote rather than introducing a new one. (2) Aggregation surface — per-(rung, fold, seed) fitting on the validation split. 4 LODO folds × 3 seeds × 2 policies = 24 thresholds per trained rung; across 4 trained rungs equals 96 threshold-pair instances. Selection variance is propagated via eval_toolkit.paired_bootstrap_op_point_diff (two-level bootstrap — refit threshold on each val resample, apply on test resample, compute paired diff) consistent with ADR-022's per-(seed) threshold protocol. (3) Reporting layout — one new headline column per trained rung — "FPR @ recall ≥ 99%" — for the verification policy; the detection-policy framing is captured by a footnote on the existing recall@FPR=1% column rather than by column duplication; the full dual-policy operating-point grid (4 trained rungs × 2 policies × {pooled-IID + pooled-OOD + 4 per-LODO-fold + 5 per-OOD-slice} aggregation levels — 80 cells per policy) lives in WRITEUP/threshold-policy.md spoke alongside the ≥3 deployment scenarios already mandated by ADR-006. (4) Infeasibility handling — honest reporting plus asterisk flag plus audit JSON. When TargetRecallSelector(0.99) cannot satisfy the recall ≥ 99% constraint on a (rung, fold, seed) val slice, the cell rendering carries an asterisk and the audit emits per-(rung, fold, seed) reachability evidence to evals/audit/verification_reachability.json with target_reachable plus achieved_val_recall plus fallback_threshold plus fallback_test_fpr fields. The methodology spoke gains a "Verification-target reachability across trained rungs" subsection. (5) Persistence pre-commit for post-hoc recall-floor sweeps — ADR-013 per-row val plus test prediction persistence is sufficient for re-fitting at alternative recall floors {95 percent, 99 percent, 99.9 percent} without retraining; pre-bootstrap CIs at the alternative floor regenerate via the existing paired_bootstrap_op_point_diff orchestrator-layer joblib pipeline per ADR-022. The "Recall-floor sensitivity sweep" is a one-commit afterword in WRITEUP/threshold-policy.md if a Phase 5 reviewer requests it. (6) Reference scorers excluded — dual-policy fitting applies only to the 4 trained rungs per SPEC §4 dual-policy applicability lock; the 4 reference rungs report recall@FPR pinpoints only with explicit contamination caveats per ADR-018 plus ADR-006. Cost-weighted thresholding remains rejected per ADR-006 — no CostSensitiveSelector use; the dual-policy framing is two anchor budgets along the ROC curve, not a Bayes-optimal cost-derivation.
source: SPEC_GREENFIELD.md §4 Threshold ledger row 347 + Phase 0-05 walk Q1 + Q2 + Q3 + Q4
acceptance_criterion: SPEC_GREENFIELD ledger row 347 carries locked-to-symmetric-1pct-with-honest-feasibility-reporting status (see ADR-025); SPEC_SHEET §5.3 Operating points subsection replaces the locked-pending-numeric-targets phrasing with explicit detection-FPR ≤ 1% plus verification-FNR ≤ 1% (equivalently recall ≥ 99 percent) plus selector-primitive-name plus aggregation-surface-name; SPEC_SHEET §5.1 primary descriptive metrics adds "FPR @ recall ≥ 99 percent" as the verification-policy column on trained rungs only with footnote on the existing recall@FPR=1% column tagging it as the detection-policy operating point; WRITEUP/threshold-policy.md spoke gains "Dual-policy operating-point grid" subsection (per-(rung, fold, seed) cells with paired_bootstrap_op_point_diff CIs at all aggregation levels) plus "Verification-target reachability across trained rungs" subsection plus optional "Recall-floor sensitivity sweep" afterword; decisions/library_imports.md eval-toolkit section gains TargetFPRSelector plus TargetRecallSelector plus paired_bootstrap_op_point_diff plus metrics_at_threshold entries; assumptions.md A-009 added (severity medium) documenting the verification-target reachability assumption with reachability JSON as load-bearing audit surface; tests/test_invariants.py contains skip-marked stub test_dual_policy_threshold_pairing asserting (a) per-(rung, fold, seed) selector fitting on val + test-application + paired_bootstrap_op_point_diff CI propagation; (b) only trained rungs participate (reference rungs excluded); (c) detection threshold equals TargetFPRSelector(0.01) and verification threshold equals TargetRecallSelector(0.99); tests/test_invariants.py contains skip-marked stub test_verification_reachability_audit asserting evals/audit/verification_reachability.json schema (per-(rung, fold, seed) entries with target_reachable plus achieved_val_recall plus fallback_threshold plus fallback_test_fpr fields) and that unreachable cells carry the asterisk flag in headline emit.
closing_commit: e335739
references:
  - https://github.com/brandon-behring/eval-toolkit#readme  # eval-toolkit README (per ADR-068: original `blob/main/docs/methodology/thresholds.md` ref pointed at aspirational upstream docs that do not exist)
  - https://arxiv.org/abs/1402.1892
  - https://arxiv.org/abs/2405.14478
  - https://arxiv.org/abs/2410.22770
  - https://www.cs.iastate.edu/~honavar/elkan.pdf
  - decisions/ADR-006-headline-metrics-and-statistical-apparatus.md
  - decisions/ADR-013-kit-ratify-bulk-strictness-intake-notebook-persistence.md
  - decisions/ADR-018-reference-scorer-slate-and-contamination-stratification.md
  - decisions/ADR-021-eval-slate-aggregation-and-recall-fpr-pinpoints.md
  - decisions/ADR-022-statistical-inference-apparatus.md
  - decisions/ADR-005-methodology-principles.md
transcript: transcripts/2026-05-15__phase-0-05__threshold-policy.md
---

# ADR-025: Dual-policy threshold characterization at symmetric 1% cost weights

## Status

Accepted (2026-05-15). Closes the last [OPEN] row in SPEC_GREENFIELD §4 Threshold (row 347 — Cost-weight targets). Anchored on pre-locks from ADR-006 (rejection of cost-weighted thresholding plus scenario-based replacement) plus SPEC §4 dual-policy framing plus SPEC §4 dual-policy applicability lock plus ADR-022 per-(seed) threshold protocol plus ADR-021 recall@FPR pinpoint triad.

## Context

ADR-006 pre-locked the threshold-handling stance — cost-weighted thresholding rejected as false precision, replaced by qualitative scenario discussion in `WRITEUP/threshold-policy.md` covering ≥3 deployment scenarios. SPEC §4 then locked the *framing* — same scores serve two operational contexts (Detection — catch injections, FN-expensive; Verification — confirm clean text, FP-expensive) under different cost weights, with selection on validation only via eval-toolkit's `ThresholdSelector` protocol.

What remained genuinely [OPEN] at row 347 was the numeric values for the two policy budgets (FPR target for detection; FNR target for verification), the aggregation surface for selector fitting, the headline-vs-spoke reporting layout, and the protocol for handling per-rung infeasibility when targets are unreachable on a val slice.

eval-toolkit primitives confirmed at decision time (fresh-investigation per CLAUDE.md):

- `TargetFPRSelector(t_fpr).select(y_val, s_val)` — picks smallest threshold s.t. FPR(val) ≤ t_fpr → max recall(val) feasible point ([`eval_toolkit/thresholds.py#L109`](https://github.com/brandon-behring/eval-toolkit/blob/main/src/eval_toolkit/thresholds.py#L109))
- `TargetRecallSelector(r_target).select(y_val, s_val)` — picks highest threshold s.t. recall(val) ≥ r_target → min FPR(val) feasible point — Lipton-Elkan 2014 §3 most-precise convention ([`eval_toolkit/thresholds.py#L71`](https://github.com/brandon-behring/eval-toolkit/blob/main/src/eval_toolkit/thresholds.py#L71))
- `paired_bootstrap_op_point_diff(val_y, val_score_a, val_score_b, test_y, test_score_a, test_score_b, threshold_fn, metric_fn, n_resamples, seed)` — two-level bootstrap (refit threshold per val resample, apply on test resample, compute paired diff) — purpose-built for the per-(seed) refit-per-resample protocol (eval_toolkit `docs/methodology/thresholds.md#L181-L218`; doc-path no longer resolves on upstream main as of v0.43.0 — methodology consolidated into the package's docstrings; see [`paired_bootstrap_op_point_diff` in eval-toolkit](https://github.com/brandon-behring/eval-toolkit/blob/main/src/eval_toolkit/) for current API)
- `CostSensitiveSelector` — explicitly *not* used per ADR-006 cost-weighted-thresholding rejection

## Decision

### Q1 — Numeric cost-weight targets (ledger row 347)

**Symmetric 1% on both policy budgets.**

| Policy | Budget | Selector primitive | Operational reading |
|---|---|---|---|
| **Detection** | FPR ≤ 1% on validation | `TargetFPRSelector(0.01)` | "Catch as many injections as possible while keeping false-alarm rate at or below 1%" |
| **Verification** | FNR ≤ 1% on validation (equivalently recall ≥ 99%) | `TargetRecallSelector(0.99)` | "Flag as little clean text as possible while missing at most 1% of injections" |

Symmetry rationale — (a) the detection-policy operating point coincides numerically with the recall@FPR=1% headline pinpoint locked in ADR-021, so headline integration is free (relabel-in-place footnote, not a new column); (b) symmetric framing keeps the WRITEUP narrative readable as "two budget orientations on a shared 1% cost weight" with no asymmetric-rationale paragraph required; (c) matches eval-toolkit `methodology/thresholds.md` documented default and SPEC §4 default-if-unsure; (d) PromptShield 2024-2025 precedent uses FPR=1% as the canonical operating point on the detection side.

### Q2 — Aggregation surface (per-(rung, fold, seed))

**Per-(rung, fold, seed) selector fitting on the validation split.** 4 LODO folds × 3 seeds × 2 policies = 24 thresholds per trained rung; 96 threshold-pair instances total across 4 trained rungs. Selection variance is propagated via `paired_bootstrap_op_point_diff` two-level bootstrap consistent with ADR-022's per-(seed) threshold protocol for recall@FPR pinpoints.

eval-toolkit `methodology/thresholds.md` §"When to refit threshold per bootstrap resample" justifies the two-level approach when "threshold-selection rule has meaningful variance (small slices, noisy PR curves) AND you're reporting operating-point metrics." Per-fold val n ≈ 250-1300 rows is exactly that regime.

Reference scorers (4 untrained rungs — ProtectAI v1 + v2 + gpt-4o + claude-sonnet-4-6) are excluded from dual-policy fitting per SPEC §4 dual-policy applicability lock; they report recall@FPR pinpoints only with contamination caveats per ADR-018.

### Q3 — Reporting layout (1 new headline column + relabel + spoke grid)

**Headline footprint** per trained rung after Phase 0-05 close:

```
| Rung | AUPRC | AUROC | R@FPR=0.1%* | R@FPR=1%† | R@FPR=5% | FPR@R≥99%† | ECE | Brier |
```

Where:
- `*` (carried over from ADR-021) — volatility-flagged 0.1% pinpoint at pooled aggregation only
- `†` (new in ADR-025) — dual-policy operating points (detection on R@FPR=1%; verification on FPR@R≥99%)

The detection-policy column collapses to the existing recall@FPR=1% pinpoint (no new data, just a footnote labeling it as the detection-policy operating point per ADR-025); the verification-policy column is one *new* column ("FPR @ recall ≥ 99%") per trained rung — total 4 new headline cells (one per trained rung × 1 column). Reference rungs receive blank cells in this column with footnote pointing to the dual-policy applicability lock.

**Spoke** at `WRITEUP/threshold-policy.md` carries:

1. Dual-policy framing explainer (Detection vs Verification budgets; same scores, two anchor operating points along the ROC curve)
2. **Dual-policy operating-point grid** — 4 trained rungs × 2 policies × {pooled-IID + pooled-OOD + 4 per-LODO-fold + 5 per-OOD-slice} aggregation levels = 80 cells per policy, with paired_bootstrap_op_point_diff CIs at every cell
3. **Verification-target reachability across trained rungs** subsection (Q4 surface)
4. ≥3 deployment scenarios per ADR-006 (e.g., agentic tool-use with catastrophic-miss cost; user-facing chat with friction-dominant cost; throughput-dominant triage)
5. Reference-scorer caveat — dual-policy doesn't apply per SPEC §4 lock; reference rungs report recall@FPR pinpoints only
6. **Recall-floor sensitivity sweep** afterword (optional Phase 5 deliverable; pre-committed via Q4 persistence pre-commit; covered in Consequences below)

### Q4 — Infeasibility handling (honest reporting + audit JSON + spoke subsection + persistence pre-commit)

When `TargetRecallSelector(0.99)` cannot satisfy recall ≥ 99% on a (rung, fold, seed) val slice (PR-curve too noisy, plateau below 99%, or score quantization gaps), the reporting protocol pre-commits four surfaces:

| Surface | Implementation |
|---|---|
| Cell rendering | Asterisk (`*`) on cells where target unreachable |
| Footnote | "Cells marked * indicate the verification target (recall ≥ 99%) was unreachable on the val slice; threshold falls back to the lowest available; achieved val-recall is reported in evals/audit/verification_reachability.json" |
| Audit JSON | `evals/audit/verification_reachability.json` with per-(rung, fold, seed) entries containing `target_reachable` (bool), `target_recall` (0.99), `achieved_val_recall` (float), `fallback_threshold` (float), `fallback_test_fpr` (float) |
| Spoke subsection | "Verification-target reachability across trained rungs" — surfaces per-rung reachability rate as a cross-rung comparison artifact |

Audit JSON schema:

```json
{
  "<rung_id>": {
    "<fold_id>": {
      "<seed>": {
        "target_reachable": false,
        "target_recall": 0.99,
        "achieved_val_recall": 0.974,
        "fallback_threshold": 0.412,
        "fallback_test_fpr": 0.083
      }
    }
  }
}
```

**Persistence pre-commit for post-hoc recall-floor sweeps.** ADR-013 already locks per-row val + test prediction persistence per (rung, fold, seed). Switching from recall ≥ 99% to recall ≥ 95% (or any other floor) is a re-run of `TargetRecallSelector(t').select(y_val, s_val)` on the persisted predictions, with no retraining, no re-fitting calibrators, no new GPU time. Pre-bootstrap CIs at the alternative floor regenerate via the existing `paired_bootstrap_op_point_diff` orchestrator-layer joblib pipeline per ADR-022. The "Recall-floor sensitivity sweep" becomes a one-commit afterword in `WRITEUP/threshold-policy.md` if needed during Phase 5 review — pre-committed sweep grid is recall floors {95%, 99%, 99.9%} (mirror of ADR-021's recall@FPR pinpoint triad in FNR space).

## Consequences

### Positive

- Closes the last open ledger row in §4 Threshold; SPEC §4 fully locked at row level
- Aligns with ADR-006 cost-weighted-thresholding rejection (no `CostSensitiveSelector`); dual-policy is two anchor budgets along the ROC curve, not a Bayes-optimal cost derivation
- Detection-policy column reuses the ADR-021 recall@FPR=1% pinpoint — zero new headline data on the detection side; +1 verification column total
- Symmetric 1% targets keep the WRITEUP narrative readable; no asymmetric-rationale paragraph
- Per-(rung, fold, seed) aggregation maintains methodology coherence with ADR-022 (same per-(seed) threshold protocol as recall@FPR pinpoints)
- Honest infeasibility reporting via asterisk + audit JSON mirrors ADR-021's recall@FPR=0.1% volatility-surfacing pattern; treats verification reachability rate as a methodology contribution rather than a hidden caveat
- Persistence pre-commit makes recall-floor sensitivity sweeps a free post-hoc artifact; protects against a Phase 5 reviewer asking "what about 95%?" without requiring rework
- Library-first preserved end-to-end: `TargetFPRSelector` + `TargetRecallSelector` + `paired_bootstrap_op_point_diff` + `metrics_at_threshold` all shipped in eval-toolkit; project-specific glue is the per-(rung, fold, seed) orchestration loop and the audit-JSON emission layer

### Negative

- Headline table widens by one column on trained rungs (+1 column × 4 trained rungs); spoke gains a new `WRITEUP/threshold-policy.md` deliverable with 80 cells × 2 policies plus reachability subsection plus deployment scenarios
- Reference-scorer rows in headline table carry blank cells under the verification column with footnote — slight asymmetry between trained-rung and reference-rung headline rows
- 96 paired_bootstrap_op_point_diff invocations during Phase 4 bootstrap battery (4 trained rungs × 24 threshold pairs); orchestrator-layer joblib parallelization on 64-core Threadripper per ADR-022 absorbs the cost
- Verification-target reachability is rung-dependent and not guaranteed (see assumption A-009); some rungs may carry mostly asterisks under the verification column

### Neutral

- ≥3 deployment scenarios from ADR-006 are co-located in `WRITEUP/threshold-policy.md` with the dual-policy operating-point grid — single spoke artifact
- Cost-weighted thresholding stays rejected; dual-policy framing operates entirely on the FPR / recall axis, not on a fabricated cost ratio
- Detection-policy headline column relabel (footnote on existing recall@FPR=1% cell) is reversible — if a reviewer challenges the relabel, splitting it into a duplicated standalone column is one commit with zero data movement

## Alternatives considered

- **Symmetric 5% targets** — looser detection budget; rejected because 5% FNR verifier is operationally weak (misses 1/20 injections) and 5% FPR detector floods alerts beyond the canonical PromptShield precedent
- **Asymmetric (1% / 0.1%)** — verification stricter to mirror "verification is the precision-biased policy" deployment intuition; rejected because asymmetry needs a justification paragraph and 99.9% recall floor is unreachable on most rungs
- **Symmetric triad (mirror of recall@FPR triad)** — full ROC-curve characterization at 6 pinpoints; rejected because detection-side triad is already locked in ADR-021 (numerical redundancy) and verification-side triad multiplies headline width without proportional methodology gain — kept as an *afterword* sweep via the Q4 persistence pre-commit
- **No new headline column (full dual-policy table only in spoke)** — minimal headline footprint; rejected because the verification-policy column is genuinely new headline information (FPR @ recall ≥ 99% is not in ADR-021's pinpoints) and hiding it from A1 reviewer defeats the dual-policy framing purpose
- **Step-down sequence on infeasibility (try 99% → 95% → max-achievable)** — apparent flexibility; rejected because cell-by-cell tier labels make paired-Δ comparisons across rungs incoherent (same column carries different operating points)
- **Drop the cell on infeasibility** — apparent simplicity; rejected because aggregating only feasible-rung instances introduces selection bias in pooled aggregations
- **Per-rung pooled-validation fitting (8 thresholds total instead of 96)** — simpler; rejected because mismatches ADR-022's per-(seed) protocol and prevents `paired_bootstrap_op_point_diff` two-level CI propagation

## Phase 1 deliverables

- `WRITEUP/threshold-policy.md` spoke filename pre-committed (already on the spoke list per ADR-006); now extended to carry the dual-policy operating-point grid + verification-reachability subsection + recall-floor sensitivity sweep afterword
- `evals/audit/verification_reachability.json` schema documented in `evals/audit/README.md`
- Verify `TargetRecallSelector` source-level unreachable-target behavior at Phase 4 entry (one library check; if the selector raises rather than falls back to lowest threshold, glue wraps in try/except and emits the audit row from the exception path)

## References

See frontmatter references list. Primary anchors — eval-toolkit `methodology/thresholds.md` (selector semantics + two-level bootstrap rationale); Lipton-Elkan-Naryanaswamy 2014 (TargetRecallSelector most-precise convention); PromptShield 2024-2025 (FPR=1% canonical operating point); InjecGuard 2024 (over-defense FPR-floor framing); Elkan 2001 (cost-sensitive learning theory we are *not* applying); ADR-006 cost-weighted-thresholding rejection; ADR-013 per-row prediction persistence; ADR-018 reference-scorer slate plus contamination caveats; ADR-021 recall@FPR pinpoint triad plus volatility-surfacing precedent; ADR-022 per-(seed) threshold protocol plus paired-bootstrap orchestration; ADR-005 Principle 2 (honest evaluation preferred).

## Transcript

See `transcripts/2026-05-15__phase-0-05__threshold-policy.md` for the Phase 0-05 conversation that led to this decision.
