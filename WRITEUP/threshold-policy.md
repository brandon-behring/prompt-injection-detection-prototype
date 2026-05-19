# Threshold policy

*Part of the [WRITEUP methodology](../WRITEUP.md) — see the hub for the cover narrative + reading guide.*

> **How to read this spoke**: For a hiring-manager-level skim, focus on the bolded **Result** subsections + the final §Summary if present. For a full audit, read the methodology paragraphs + the ADR references in headers.

:::{.callout-note}
## Summary

- **Dual-policy framing**: the same classifier scores are configured at two cost-weight thresholds — **detection** (FPR ≤ 1 %) for low-flag-rate triage, **verification** (recall ≥ 99 %) for must-catch-all-attacks queueing. Both reported side by side per ADR-025.
- **Scope bound**: dual-policy operating-point characterisation applies only to **in-house rungs**. Reference scorers carry training-overlap caveats that make operating-point characterisation misleading; only recall@FPR pinpoints are reported for those.
- **Key val→test transfer finding**: all 72 op-points are reachable on val; transfer to LODO held-out test is partial-to-poor. The val→LODO gap is the dominant calibration story per WRITEUP §Results §7.5.
- **LoRA detection on test**: mean FPR creeps to 0.115 (11.5×) vs 1 % target. Recall trades favorably (0.42) for the higher FPR.
- **Frozen-probe verification on test**: mean recall lands at 0.957 (close to 0.99 target) BUT at mean FPR 0.891 — almost everything is flagged positive. Verification regime over-floods at the cost of selectivity on LODO.
:::

This spoke covers §5.3 — the dual-policy detection / verification
operating-point characterisation per ADR-025. The same classifier
scores are configured to two different cost-weight thresholds; what
those thresholds deliver on validation and how they transfer to LODO
held-out test is the story. For headline metrics + statistical
apparatus see [`eval-design.md`](./eval-design.md); for the §7.5 val-
to-test transfer findings see [`../WRITEUP.md`](../WRITEUP.md) §Results.

## Context

The same classifier serves two different operational contexts.
**Detection** wants to *catch injections* — false negatives are the
high-cost error; tolerate false positives up to an alerting-budget.
**Verification** wants to *confirm clean* — false positives (calling
clean text injection) are the high-cost error; tolerate some missed
injections at the verification boundary.

These contexts ask different questions of the same scores. Reporting
only one operating point hides what the classifier can do under the
other cost regime.

## Methodology

Both policies use eval-toolkit's `ThresholdSelector` protocol on
**validation** (never test). The two policies differ only in cost
weights:

- **Detection policy**: target FPR ≤ 1 % on validation; among
  thresholds satisfying that constraint, maximise TPR. Implemented
  via `eval_toolkit.TargetFPRSelector(0.01)`.
- **Verification policy**: target FNR ≤ 1 % on validation
  (equivalently recall ≥ 99 %); among thresholds satisfying that
  constraint, maximise TNR. Implemented via
  `eval_toolkit.TargetRecallSelector(0.99)`.

Symmetric cost-weight configurations of the same primitive.
Operationally-interpretable targets (FPR / FNR) — not score-space
targets — so the same selection rule applies across heterogeneous
rungs whose score scales aren't comparable. See
[methodology/thresholds.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/thresholds.md).

Per-(rung, fold, seed) fitting on validation only: 24 thresholds per
trained rung × 3 trained rungs (post-ADR-050 narrowing) = 72
threshold-pair instances. `paired_bootstrap_op_point_diff` two-level
bootstrap (refit per resample) for CI propagation. Cost-weighted
thresholding remains rejected per ADR-006 (no `CostSensitiveSelector`
use).

**Scope bound:** dual-policy threshold characterisation applies only
to **in-house rungs**. Reference scorers (off-the-shelf reference
detectors) carry training-overlap caveats that make operating-point
characterisation misleading; for those, only recall@FPR pinpoints
are reported.

## Dual-cost-weight characterisation (in-house rungs)

For the representative rung **LoRA** (the fine-tuned-ceiling-in-
budget on this submission per ADR-019 + ADR-050; full-FT was the
planned representative but is excluded from val-set inference due to
the FUSE EIO crash per §8.1), both policies are reported side by side.
Numbers are *mean across 12 cells* (4 LODO folds × 3 seeds) on LODO
held-out test, with val-fitted thresholds per ADR-025:

| Policy | Mean threshold | Mean test recall | Mean test FPR | Reachable? |
|---|---:|---:|---:|---|
| Detection (FPR ≤ 1 %) | 0.795 | 0.424 | 0.115 | val: 12/12; test: 0/12 within target |
| Verification (recall ≥ 99 %) | 0.019 | 0.724 | 0.411 | val: 12/12; test: 0/12 within target |

For comparison, the **frozen-probe** rung at the same policies:

| Policy | Mean threshold | Mean test recall | Mean test FPR | Reachable? |
|---|---:|---:|---:|---|
| Detection (FPR ≤ 1 %) | 0.829 | 0.063 | 0.010 | val: 12/12; test: 11/12 within target |
| Verification (recall ≥ 99 %) | 0.215 | 0.957 | 0.891 | val: 12/12; test: 5/12 within target |

This is **characterisation, not deployment recommendation**. The
table shows what the scores deliver under each cost weight, not an
advocation of either policy for any deployment.

**Result (key val→test transfer findings)**:

- All 72 op-points are reachable on val (the threshold-fitting set
  by ADR-025); transfer to LODO held-out test is partial-to-poor.
  The val→LODO gap is the dominant calibration story per WRITEUP
  §Results §7.5.
- **LoRA detection on test**: mean FPR creeps to 0.115 (11.5×) vs
  1 % target. Recall trades favorably (0.42) for the higher FPR.
- **frozen-probe detection on test**: mean FPR holds tight (0.010
  ≈ target) but recall collapses to 0.063 (the threshold is too
  conservative for the LODO distribution shift).
- **frozen-probe verification on test**: mean recall lands at
  0.957 (close to 0.99 target) BUT at mean FPR 0.891 — almost
  everything is flagged positive. The verification regime
  over-floods at the cost of selectivity on LODO.

Source: `evals/operating_points/dual_policy.parquet` (72
OperatingPointModel rows) + `evals/audit/verification_reachability.json`
(36 ReachabilityAuditModel records).

## Verification-target reachability (A-009 audit surface)

The verification policy at recall ≥ 99 % is not guaranteed to be
reachable on every (rung, fold, seed) val slice per assumption A-009.
Reachability can fail when:

1. The PR curve at high-recall regime is too noisy on a small val
   slice (per-fold val n ≈ 250-1300 rows; LODO val with positive
   sources held out is the worst case).
2. The model genuinely cannot reach 99 % recall on that fold's
   positives without flagging nearly all benigns (recall plateaus
   < 99 %).
3. Score quantization gaps prevent the achievable recall lattice
   from containing a point at recall ≥ 99 % even when the limit is
   approachable.

`evals/audit/verification_reachability.json` records `target_reachable`
+ `achieved_val_recall` + `fallback_threshold` + `fallback_test_fpr`
per cell.

**Phase 5 mitigation pre-commit** (per ADR-013 + ADR-025 Q4): if
reachability is poor on the headline rungs, the persistence
pre-commit enables a one-commit "Recall-floor sensitivity sweep"
afterword regenerating verification operating points at recall floors
{95 %, 99 %, 99.9 %} from persisted predictions with zero new training
compute.

## Cross-references

- **Headline metrics + statistical apparatus that consume thresholds** → [`eval-design.md`](./eval-design.md)
- **§7.5 val→test transfer findings (full narrative)** → [`../WRITEUP.md`](../WRITEUP.md) §Results
- **Per-row predictions schema (where thresholds are applied)** → [`reproducibility.md`](./reproducibility.md)

**Linked ADRs**: ADR-006 (headline metrics + rejection of cost-
sensitive selectors), ADR-013 (per-row predictions persistence),
ADR-025 (dual-policy threshold characterisation), ADR-050 (rung-slate
narrowing — full-FT OOD dropped). Assumption A-009 (verification
reachability).
