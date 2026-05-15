---
adr_id: 006
slug: headline-metrics-and-statistical-apparatus
title: Headline metrics, operating-point pinpoints, and statistical apparatus
date: 2026-05-15
status: Accepted
claim_id: CLAIM-006
claim: The submission reports four headline metrics (AUPRC, AUROC, Recall@FPR=1%, ECE) at three operating-point pinpoints {0.1%, 1%, 5%} per rung; statistical inference is via 95% bootstrap CIs (10K iters, BCa for marginals, paired for rung-vs-rung differences) with MDE on every reported CI; multi-seed protocol is 3 seeds paired across rungs (adaptive escalation to 5 if budget permits per ADR-001 fallback ladder); no formal p-tests (estimation-over-testing, per ADR-005 Principle 2); cost-weighted thresholding is rejected as false precision and replaced by qualitative scenario discussion in WRITEUP/threshold-policy.md.
source: SPEC_GREENFIELD.md §Brief row 308 (Brief-mandated metrics / constraints) + §3 Eval rows 340-347
acceptance_criterion: All headline rung-tables show the four metrics with three Recall@FPR pinpoints; every reported metric has a bootstrap CI; rung-vs-rung comparisons are reported as Δ-CIs (paired bootstrap), not p-values; MDE is computed for every CI; cost-weighted thresholding is absent from the writeup and replaced by ≥3 deployment scenarios in the threshold-policy spoke.
closing_commit:
references:
  - https://journals.sagepub.com/doi/10.1177/0956797613504966
  - https://www.tandfonline.com/doi/full/10.1080/00031305.2016.1154108
  - https://arxiv.org/abs/1909.10155
  - https://projecteuclid.org/journals/annals-of-statistics/volume-7/issue-1/Bootstrap-Methods-Another-Look-at-the-Jackknife/10.1214/aos/1176344552.full
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-006: Headline metrics, operating-point pinpoints, and statistical apparatus

## Status

Accepted (2026-05-15)

## Context

ADR-005 Principle 2 (honest evaluation preferred) and the estimation-over-testing stance surfaced during Q5-C1 require concrete commitments about *which metrics get reported as headline*, *at which operating points*, *with what uncertainty quantification*, and *with what inferential framing for rung-vs-rung comparisons*. These four sub-decisions are deeply intertwined — the metric set determines the calibration story, the pinpoint set determines the operational story, the inference protocol determines whether comparisons are reported as effect sizes or as significance verdicts, and the threshold-handling stance determines whether cost-weighting is feigned or honestly deferred.

The choice cluster has substantial literature behind it. Microsoft PromptShield 2024-2025 uses Recall@FPR low-pinpoints as its canonical metric. Kumar 2019 (arXiv:1909.10155) argues for debiased ECE estimation over naive binning. Efron 1979 founds the bootstrap; BCa is the standard small-sample variant. Cumming 2014 ("The New Statistics") and the ASA's 2016 statement on p-values argue for effect-size-with-CI reporting over null-hypothesis significance testing.

## Decision

**Headline metric set** (4 metrics): AUPRC, AUROC, Recall@FPR=1%, ECE. PDF exec-summary headline table per rung carries these four columns.

**Operating-point pinpoints** (3 levels): {0.1%, 1%, 5%}. PDF headline table widens to show Recall at each FPR pinpoint per rung (six columns total: AUPRC, AUROC, Recall@FPR=0.1%, Recall@FPR=1%, Recall@FPR=5%, ECE).

**Statistical apparatus**:
- 95% confidence intervals (field-standard).
- 10K bootstrap iterations as default; can escalate to 100K locally for any analysis where it tightens the headline narrative without budget impact (local CPU work; embarrassingly parallel; cost ≈ minutes).
- BCa (bias-corrected accelerated) for marginal-metric CIs; paired bootstrap for rung-vs-rung differences (Δ-CIs).
- MDE (minimum detectable effect) computed for every reported CI.
- Multi-seed protocol: 3 seeds paired across rungs as floor; adaptive escalation to 5 seeds if budget permits per ADR-001 fallback ladder.

**Inferential framing**: estimation-over-testing. No formal p-tests, no McNemar, no DeLong. Rung-vs-rung comparisons are reported as paired-bootstrap Δ-CIs interpreted via magnitude, location, and overlap. CIs straddling zero are reported honestly. Multi-comparison correction is therefore not applicable.

**Threshold-handling stance**: cost-weighted thresholding is **rejected as false precision**. The project does not have a deployment-cost ratio and refuses to fabricate one. Replaced by qualitative scenario discussion in `WRITEUP/threshold-policy.md` spoke covering ≥3 deployment scenarios (e.g., agentic tool-use with catastrophic miss cost; user-facing chat with friction-dominant cost; throughput-dominant logging/triage). The deployer picks the operating point given their scenario.

**Compute placement**: training runs on RunPod GPU; per-row predictions persisted to durable storage before pod teardown (per ADR-013); all bootstrap analysis, MDE computation, paired-Δ-CI computation, and Cohen's kappa analysis (per ADR-007) runs on local CPU.

## Consequences

**Positive:**

- Estimation-over-testing aligns the inferential framing with ADR-005 Principle 2 (honest evaluation preferred). CIs that straddle zero are not embarrassments; they are honest descriptions of the comparison's resolution.
- Multi-comparison correction is pre-resolved as not-applicable, removing a Phase 0-04 sub-decision.
- Scenario-based threshold deferral lets the writeup serve A1+A2 dual audience (ADR-004) without fabricating cost ratios — the deployer maps their context to one of the surfaced scenarios.
- Local-CPU bootstrap workflow keeps GPU rental cost bounded; analysis re-runs are essentially free.
- MDE reporting on every CI distinguishes this submission from typical published work where MDE is silently omitted.

**Negative / cost:**

- Six-column headline table per rung is wide; requires careful PDF layout (likely landscape orientation for the headline table or a two-row header).
- Multi-seed protocol at 3 seeds × 6 trained rungs × ~2 backbones = 18 training runs (or 36 if 5 seeds). Risks Q1 fallback-ladder activation if RunPod queue/throughput surprises emerge.
- Scenario-based threshold discussion is harder to write than a single-cost-ratio analysis; requires articulating ≥3 deployment scenarios with their tolerance shapes.

**Neutral:**

- Phase 0-04 still walks §3 Eval rows 343 (calibration battery composition — full ECE+Brier+reliability), 344 (multi-seed protocol details), 346 (cross-fold CI methodology — bootstrap-per-fold vs CV-CLT vs Nadeau-Bengio). This ADR fixes the headline metric set + pinpoints + estimation-over-testing stance; the full battery and the cross-fold aggregation are still open.

## Alternatives Considered

- **3-metric headline (AUROC + Recall@FPR + ECE)**: One fewer column. *Rejected because* AUPRC explicitly carries the class-imbalance story; benign vastly outnumbers injection in deployment and AUROC alone is misleading.
- **Single Recall@FPR=1% pinpoint**: Cleaner exec summary. *Rejected because* 0.1% reveals where over-defense bites hardest (InjecGuard 2024 over-defense finding); 5% reveals where lenient deployment regimes sit; three-pinpoint coverage tells the operational story honestly.
- **Formal McNemar / DeLong tests for rung-vs-rung comparison**: Field-common. *Rejected because* dichotomous test outcomes mislead readers (Gelman & Stern 2006); paired-bootstrap Δ-CIs carry strictly more information.
- **BH-FDR multi-comparison correction**: Would apply if formal tests were used. *Rejected because* no formal tests are being run (estimation-over-testing).
- **Single cost-weighted operating point (e.g., $C_{FP}/C_{FN} = 10$)**: Concrete deployment story. *Rejected because* the project has no real cost ratio; fabricating one is false precision. Scenario-discussion is the principled replacement.
- **Bootstrap on RunPod GPU**: Co-locates training and analysis. *Rejected because* bootstrap is CPU-bound; GPU adds nothing; local-CPU workflow is strictly cheaper.

## References

- Cumming 2014 — "The New Statistics: Why and How" — https://journals.sagepub.com/doi/10.1177/0956797613504966
- Wasserstein & Lazar 2016 — ASA Statement on p-values — https://www.tandfonline.com/doi/full/10.1080/00031305.2016.1154108
- Gelman & Stern 2006 — Difference Between Significant and Not Significant — https://www.tandfonline.com/doi/abs/10.1198/000313006X152649
- Kumar 2019 — Debiased calibration estimators — https://arxiv.org/abs/1909.10155
- Efron 1979 — Bootstrap — https://projecteuclid.org/journals/annals-of-statistics/volume-7/issue-1/Bootstrap-Methods-Another-Look-at-the-Jackknife/10.1214/aos/1176344552.full
- PromptShield (Microsoft 2024) — provisional https://arxiv.org/abs/2405.14478
- Elkan 2001 — Cost-sensitive learning — https://cseweb.ucsd.edu/~elkan/rescale.pdf
- InjecGuard / NotInject (Li & Liu 2024) — https://arxiv.org/abs/2410.22770
- `docs/research/benchmarks/01_benchmark_direct.md` — JailbreakBench / HarmBench framing
- ADR-005 (Principle 2 — honest evaluation preferred; estimation-over-testing rationale)
- ADR-001 (multi-seed escalation gated by fallback ladder)
- ADR-013 (per-row prediction persistence pre-teardown)
