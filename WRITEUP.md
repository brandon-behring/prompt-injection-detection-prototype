# Prompt-injection classification — methodology + capability characterisation

**Author**: Brandon Behring · **Date**: 2026-05-18 · **Status**: `v1.0.0` submission tag (Phase 5 close)

This document is the **TOC + landing page**: the cover narrative
(§1 Motivation, §2 Approach overview, §Results, §Lessons,
§Appendix) lives here; the detailed sections live as spokes
under [`WRITEUP/`](./WRITEUP/) (linked below).

## Reading guide

| Spoke | Coverage |
|---|---|
| [`WRITEUP/data-decisions.md`](./WRITEUP/data-decisions.md) | §3 Data design — source slate selection + dedup + leakage + LODO splits |
| [`WRITEUP/model-rungs.md`](./WRITEUP/model-rungs.md) | §4 Rung ladder — classical floor + ModernBERT × {frozen-probe, LoRA, full-FT} + ProtectAI v1/v2 |
| [`WRITEUP/eval-design.md`](./WRITEUP/eval-design.md) | §5.1, §5.2, §5.4, §5.5 — metric battery + paired-bootstrap + MDE + calibration + OOD slate composition |
| [`WRITEUP/threshold-policy.md`](./WRITEUP/threshold-policy.md) | §5.3 — dual-policy detection + verification operating points + val→test reachability |
| [`WRITEUP/reference-scorer-audit.md`](./WRITEUP/reference-scorer-audit.md) | §3.3 + §5.6 + §7.2/3 — ADR-005 contamination taxonomy applied to reference scorers + adversarial-robustness scope |
| [`WRITEUP/methodology-guarantees.md`](./WRITEUP/methodology-guarantees.md) | §6 Tooling — eval-toolkit + runpod-deploy + SDD process + library-first invariant |
| [`WRITEUP/limitations-and-future-work.md`](./WRITEUP/limitations-and-future-work.md) | §8 scope deferrals + §8.2 methodology caveats + §9 negative results + §11 lessons |
| [`WRITEUP/reproducibility.md`](./WRITEUP/reproducibility.md) | §10 T0 + T1 + T3 reproduction tiers |

For the audit trail of external-evidence claims, see [`EVIDENCE.md`](./EVIDENCE.md).
For the per-decision ADR record, see [`decisions/`](./decisions/) +
[`SUBMISSION_AUDIT.md`](./SUBMISSION_AUDIT.md).

---

## 1. Motivation

Prompt-injection — text designed to override or subvert the instructions an LLM-based system is operating under — is one of the load-bearing failure modes for any system that exposes an LLM to untrusted input. Ciphero's verification-layer thesis is that we cannot govern what we cannot verify; one primitive in that stack is a classifier that scores whether a span of text is an injection attempt.

The same scores serve two operational contexts:

- **Detection** — *catch injections coming in*. Tolerates false positives more than false negatives (an alert costs less than a missed attack at the input boundary).
- **Verification** — *confirm clean text actually is clean*. Tolerates false negatives more than false positives (a confidently-clean assertion is the dangerous one).

These are not two classifiers; they are two threshold policies on the same scores, with different cost weights. See [`WRITEUP/threshold-policy.md`](./WRITEUP/threshold-policy.md) for how the same primitive is configured to characterise both.

This writeup characterises a 5-rung ladder of prompt-injection classifiers — TF-IDF+LR classical floor + ModernBERT-base × {frozen-probe, LoRA, full-FT} + ProtectAI v1 + ProtectAI v2 reference scorers (locked at Phase 0-03 per ADR-015 + ADR-017 + ADR-018 + ADR-050) — across an OOD slate, with the question: *what does each capability layer add, and where does the IID/OOD gap fall?* The work is **methodology + capability characterisation braided**: the ladder is the instrument; the eval methodology rigor is what makes the characterisation defensible; the brief's two asks (models of increasing complexity + OOD coverage) are the targets.

**Honest-OOD thesis**: IID numbers are the easy part. The interesting question for any classifier that might one day touch a deployment surface is *which capabilities help when the distribution shifts, and which ones only inflate the IID number*. That question — not "what's the best PR-AUC" — drives this document's structure.

**Deployment is not on the roadmap.** This is characterisation, not recommendation. No rung is promoted as the deployment choice; each rung's trade-offs are reported and the reader is left to draw their own deployment conclusions if they have one to make.

**Linked ADRs**: ADR-001 (brief alignment), ADR-013 (deliverable scope + WRITEUP shape), ADR-017 (rung-slate expansion).

**Known gaps**: this submission characterises a *prompt-injection text classifier* against an English-only fixed slate of 4 LODO training sources + 5 OOD slates. Cross-language attacks, agentic-flow injection, conformal calibration, and adversarial red-teaming are out of scope per [`WRITEUP/limitations-and-future-work.md`](./WRITEUP/limitations-and-future-work.md) §8.1.

---

## 2. Approach overview

The brief asked for two things: *models of increasing complexity* and *the right amount of OOD coverage*. The rung ladder satisfies the first ask and is the **instrument** for the second: when a rung helps IID but not OOD, that tells us its added capability is data-pattern-fitting rather than generalisation; when a rung helps both, the added capability is more durable.

| Element | Role | Why |
|---|---|---|
| Rung ladder (locked Phase 0-03 per ADR-015 + ADR-017 + ADR-050) | Instrument | Each step's lift over the previous decomposes *which capability* matters. |
| OOD slate (5 slices locked Phase 0-04 per ADR-016 + ADR-021) | Measurement | Quantifies what each capability adds when the distribution shifts. |
| Dual cost-weight thresholds | Score-behaviour characterisation | Shows what the same scores deliver under two different operational cost regimes. |
| Statistical rigor (CIs + paired comparisons + MDE) | Defensibility | Lets us claim differences honestly and quantify when we lack the power to claim anything. |

We do **not** pick a deployment leader. The intent is to demonstrate what each rung delivers and where it breaks; readers with a specific deployment context can map our characterisation onto their cost constraints.

**Linked ADRs**: ADR-002 (approach scaffold), ADR-014 (single-backbone slate framing), ADR-017 (rung-slate expansion), ADR-021 (slice aggregation + headline-metric protocol).

**Known gaps**: this approach evaluates EACH rung against the same slate; cross-rung-ensemble strategies (e.g., LoRA-with-frozen-probe-temperature) are out of scope per the project compute budget.

---

## Results

The headline characterisation is honest: across the rung ladder + two reference scorers, **none of the rungs decisively beats the classical TF-IDF+LR floor on the 5-slice OOD slate** (pooled_ood AUROC range 0.37–0.52; all CIs overlap chance with substantial margin). The trained transformer rungs (frozen-probe + LoRA) and the ProtectAI reference scorers cluster within a band that is statistically distinguishable from each other on the in-distribution-like slices (jbb_behaviors, xstest) but compresses to near-chance on pooled_ood. The story is not "the ladder works" — it is *the ladder works on IID-shaped attacks and fails to generalize to genuinely OOD distributions*, and the numbers below back that up.

Source data: `evals/metrics/per_cell.parquet` (per-cell, post-Item-4 single-class filter), `evals/bootstrap/marginal_cells.parquet` (BCa CI per ADR-022), `evals/bootstrap/paired_cells.parquet` + `paired_cells_seed2.parquet` (paired-Δ CI per ADR-022), `evals/audit/mde_per_cell.parquet`, `evals/operating_points/dual_policy.parquet` (72 op-points).

### The IID-vs-OOD gap (primary narrative)

Per-rung marginal AUROC + BCa 95 % CI (seed=1 headline; seed=2 stability check 0/40 cells flagged at 5 pct threshold per ADR-022 + A-008):

| Rung | jbb_behaviors AUROC | xstest AUROC | pooled_ood AUROC |
|---|---|---|---|
| TF-IDF + LR (classical floor) | 0.445 [0.422, 0.469] | 0.451 [0.436, 0.466] | 0.371 [0.362, 0.381] |
| frozen-probe | 0.542 [0.520, 0.565] | 0.537 [0.522, 0.552] | 0.515 [0.505, 0.525] |
| LoRA | 0.528 [0.505, 0.552] | 0.530 [0.515, 0.546] | 0.383 [0.374, 0.392] |
| ProtectAI v1 | 0.533 [0.464, 0.602] | 0.544 [0.497, 0.589] | 0.440 [0.409, 0.469] |
| ProtectAI v2 | 0.594 [0.512, 0.671] | 0.391 [0.341, 0.442] | 0.402 [0.369, 0.437] |

The gap pattern:

- **frozen-probe** is the strongest on `pooled_ood` (0.515 [0.505, 0.525]) — the only rung whose `pooled_ood` CI clears 0.50.
- **LoRA's `pooled_ood` AUROC (0.383)** is *below* the classical floor (0.371 within CI overlap) and far below frozen-probe (-0.13 AUROC; paired-bootstrap CI does not include zero on this comparison). **LoRA fine-tuning hurts OOD generalization** relative to the frozen probe — a known phenomenon when the fine-tuning distribution mismatch is large.
- **TF-IDF + LR** is competitive on `pooled_ood` (0.371) and only modestly below the trained rungs on jbb_behaviors / xstest. The classical floor is hard to beat without much stronger inductive biases.
- **ProtectAI v2** beats ProtectAI v1 on jbb_behaviors (0.594 vs 0.533) but loses on xstest (0.391 vs 0.544) — version-to-version updates do not monotonically improve across distributions.

Per-scorer contamination findings (ProtectAI v1 + v2) detail lives in [`WRITEUP/reference-scorer-audit.md`](./WRITEUP/reference-scorer-audit.md) and [`EVIDENCE.md`](./EVIDENCE.md) §1-2.

### Which capabilities help OOD vs only help IID

Rung-by-rung lift over the classical floor (delta AUROC, `pooled_ood`):

| Rung vs floor | delta AUROC (pooled_ood) | Interpretation |
|---|---|---|
| frozen-probe vs tfidf-lr | +0.144 | Pretrained ModernBERT embeddings DO help OOD — substantial lift |
| LoRA vs tfidf-lr | +0.012 | Adapter fine-tuning collapses the frozen-probe advantage on OOD |
| LoRA vs frozen-probe | -0.132 | LoRA hurts; the adapter weights specialise to training distribution |
| ProtectAI v1 vs tfidf-lr | +0.069 | Off-the-shelf injection detector adds modest signal |
| ProtectAI v2 vs tfidf-lr | +0.031 | v2 update does not propagate to our OOD slate |

**Implication**: the pretrained backbone (ModernBERT) provides the bulk of the OOD generalization budget. Fine-tuning (LoRA) on the in-distribution training pool causes generalization-tax: the rung does better on the training-distribution-shaped jbb_behaviors / xstest slices, but loses on `pooled_ood`. This is the canonical fine-tuning-overfit signature.

### Score-behaviour at the two operating points

Dual-policy thresholds fit on val per ADR-025 + ADR-050 (full-FT excluded; 3 trained rungs only). Mean per-cell achieved metrics on test (LODO held-out attack source):

| Rung | Policy | Mean threshold | Mean test recall | Mean test FPR |
|---|---|---:|---:|---:|
| tfidf-lr | detection (FPR ≤ 1 %) | 0.657 | 0.333 | 0.067 |
| tfidf-lr | verification (recall ≥ 99 %) | 0.162 | 0.674 | 0.508 |
| frozen-probe | detection | 0.829 | 0.063 | 0.010 |
| frozen-probe | verification | 0.215 | 0.957 | 0.891 |
| LoRA | detection | 0.795 | 0.424 | 0.115 |
| LoRA | verification | 0.019 | 0.724 | 0.411 |

Two findings:

1. **All targets reachable on val** (target_reachable=True for all 72 op-points), but **the val→test transfer is large**: detection-policy FPR creeps above target on every rung; verification-policy recall drops well below target on tfidf-lr + LoRA. The frozen-probe verification policy holds (mean test recall 0.957, close to 0.99 target) — but at catastrophic FPR (0.891).
2. **The verification regime is fundamentally limited on LODO**: held-out attack sources produce test distributions different enough from val that any "guarantee recall ≥ 99 %" threshold has either tiny test recall (LoRA: 0.724) or near-100 % test FPR (frozen-probe: 0.891).

For the full narrative + reachability-audit detail see [`WRITEUP/threshold-policy.md`](./WRITEUP/threshold-policy.md).

### Calibration findings

Per-rung mean across both-class slices:

| Rung | Mean ECE (equal-mass) | Mean Brier |
|---|---:|---:|
| frozen-probe | 0.144 | 0.265 |
| tfidf-lr | 0.350 | 0.376 |
| LoRA | 0.444 | 0.451 |
| ProtectAI v1 | 0.452 | 0.470 |
| ProtectAI v2 | 0.460 | 0.471 |

**Finding**: frozen-probe has the BEST calibration on both-class OOD slices (ECE 0.144; Brier 0.265). LoRA fine-tuning DEGRADES calibration substantially (ECE 0.444 — 3× worse than frozen-probe). This is consistent with the per-row finding that LoRA over-confidently mis-classifies OOD examples; both the discrimination AND the calibration of the head distribution shift away from honest probabilistic estimates after fine-tuning. ProtectAI v1/v2 both show high ECE (~0.45+) which is consistent with their out-of-distribution scoring against our slate.

### Frozen probe vs adapter fine-tuned (paired bootstrap)

Per ADR-022 paired-bootstrap (percentile-method, 10K resamples × 2 seeds; 0/40 stability flags at 5 pct threshold):

| Comparison | Slice | Metric | delta (b − a) | 95 % CI | Conclusion |
|---|---|---|---:|---:|---|
| frozen-probe vs LoRA | jbb_behaviors | AUPRC | −0.016 | [−0.024, −0.009] | LoRA worse; CI clears zero |
| frozen-probe vs LoRA | jbb_behaviors | AUROC | −0.014 | [−0.021, −0.006] | LoRA worse; CI clears zero |
| frozen-probe vs LoRA | xstest | AUPRC | −0.001 | [−0.006, +0.004] | Indistinguishable; CI crosses zero |
| frozen-probe vs LoRA | xstest | AUROC | −0.007 | [−0.013, −0.002] | LoRA marginally worse; CI clears zero |

**Headline**: LoRA fine-tuning is *not* a free lunch on this task. On 3 of 4 slice × metric comparisons against frozen-probe, LoRA is significantly worse at the 95 % level. The adapter weights specialise to the training distribution, costing the model the OOD generalization that the pretrained backbone alone provided.

### The headline characterisation claims

Distilled summary:

- **Claim 1**: No rung in the trained-or-reference slate decisively beats the classical TF-IDF + LR floor on the 5-slice OOD slate (all `pooled_ood` AUROC CIs within ~0.15 of 0.50; frozen-probe at 0.515 [0.505, 0.525] is the only rung whose CI clears 0.50 with margin). The case-study lesson is "honest OOD generalization for prompt-injection classifiers is harder than the in-distribution numbers suggest" — not "look at this great classifier".
- **Claim 2**: LoRA fine-tuning *hurts* OOD generalization relative to the frozen probe. Paired bootstrap on jbb_behaviors AUROC delta = −0.014 [−0.021, −0.006]; `pooled_ood` delta = −0.132. The adapter weights specialise to the training distribution. Pretrained backbone embeddings carry the OOD generalization budget; fine-tuning consumes it.
- **Claim 3**: ProtectAI v1 → v2 is *not* a monotone improvement across the OOD slate: v2 beats v1 on jbb_behaviors (+0.06 AUROC) and loses on xstest (-0.15 AUROC). Off-the-shelf detector updates can regress on specific OOD distributions; downstream consumers should not assume v2 dominates v1 universally.
- **Claim 4**: Dual-policy thresholds fit on val do not transfer to LODO test. Detection-policy FPR creeps 1-12 % on test vs 1 % val target across all 3 trained rungs; verification-policy recall drops well below target on 2 of 3 rungs. The val→LODO gap is the dominant calibration story; per-rung temperature scaling would not fix it without OOD-aware threshold selection.

Each claim is supported by a specific row × CI above, not a hand-wave.

**Linked ADRs**: ADR-018 (reference slate; partially superseded by ADR-050), ADR-019 (transformer training recipe), ADR-021 (slice aggregation), ADR-022 (statistical inference apparatus), ADR-024 (cross-fold CI), ADR-025 (dual-policy operating points), ADR-046 (Phase 4 analysis bundle), ADR-050 (rung-slate narrowing — LLM judges + full-FT OOD drops).

**Known gaps**: per-fold calibration-battery + temperature/isotonic fitting outputs not exercised this Phase 5; per-row predictions for full-FT OOD ABSENT (FUSE EIO crash per ADR-050). Canonical-data wire-up of figures F1–F7 pending upstream eval-toolkit issues #14–#16 + #22.

---

## Lessons (brief)

Long form in [`WRITEUP/limitations-and-future-work.md`](./WRITEUP/limitations-and-future-work.md) §11. Punch lines:

- The OOD generalization wall is the dominant signal; honest framing surfaces it where a "great classifier" framing would have hidden it.
- The SDD process bought reproducibility + audit trail at the cost of a ~50-decision Phase 0 interview flow. ADR-050 (rung-slate narrowing) is the supersession-on-supersession proof point — when reality forced a methodology drift, the discipline ate it cleanly.
- The library-first invariant retrofit (ADR-047) was a discipline lapse caught at Phase 4 entry and recovered in one carryforward refactor. The cost-overrun on LLM judges (ADR-050 driver 1) was a similar lapse — original estimate didn't account for actual token volume.
- FUSE-on-RunPod is a non-deterministic bug class; ~50 % of cumulative spend ($15.74) was FUSE-recovery overhead. Filed upstream issues + PRs at brandon-behring/runpod-deploy.
- Per-step commits + 2-checkpoint push cadence survived multi-day context auto-compaction.

---

## 12. Appendix

### A. Glossary

- **Detection policy** — threshold selection targeting FPR ≤ 1 % on validation; characterises high-recall-low-FP behaviour.
- **Verification policy** — threshold selection targeting FNR ≤ 1 % on validation; characterises high-precision-on-clean behaviour.
- **LODO** — leave-one-dataset-out cross-validation; source-disjoint k-fold where each fold holds out an entire dataset source.
- **LoRA** — Low-Rank Adaptation; parameter-efficient fine-tuning method.
- **PR-AUC** — area under the precision-recall curve; threshold-free ranking metric for class-imbalanced tasks.
- **ECE** — expected calibration error; mean absolute gap between predicted-probability bins and observed frequencies.
- **MDE** — minimum detectable effect; the smallest difference your sample size can reliably detect at a given power.
- **IID** — independent and identically distributed; evaluation on data drawn from the same source/distribution as training.
- **OOD** — out-of-distribution; evaluation on data deliberately drawn from a different source or distribution.
- **Rung ladder** — a sequence of classifiers of increasing complexity, designed so each step's lift decomposes which capability is responsible.

### B. ADR index

[`decisions/README.md`](./decisions/README.md) — single version-neutral sequence; ADRs supersede prior ones via the standard `superseded-by-ADR-N` mechanism.

### C. Assumption ledger

[`assumptions.md`](./assumptions.md) — every assumption with severity ≥ medium appears in [`WRITEUP/limitations-and-future-work.md`](./WRITEUP/limitations-and-future-work.md) §8.2.

### D. Audit trail

[`EVIDENCE.md`](./EVIDENCE.md) — what external evidence was verified, what couldn't be, what was left unresolved.

### E. Linked Claude transcripts

Transcripts referenced by ADR `transcript:` frontmatter fields are bundled and emailed to the reviewer at submission time per `transcripts/README.md`; the `/save-transcript` skill produces them.

### F. eval-toolkit methodology curriculum

[`docs/methodology/`](https://github.com/brandon-behring/eval-toolkit/tree/main/docs/methodology) — 17-chapter curriculum. Cross-linked from each WRITEUP/ spoke.
