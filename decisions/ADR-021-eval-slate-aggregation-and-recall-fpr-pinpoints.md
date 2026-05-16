---
adr_id: 021
slug: eval-slate-aggregation-and-recall-fpr-pinpoints
title: Eval slate aggregation — pooled headline plus per-slice spoke and recall@FPR pinpoint feasibility
date: 2026-05-15
status: Accepted
claim_id: CLAIM-021
claim: Phase 0-04 locks the per-rung reporting layout for the §3 Eval framework as follows. (1) OOD slate aggregation — the 5 OOD slices locked by ADR-016 (NotInject plus XSTest plus JBB-Behaviors plus BIPIA plus InjecAgent) are reported in two complementary aggregation views. The PDF executive headline table carries a single pooled-OOD column per rung (concatenated rows across the 5 slices, single AUPRC plus AUROC plus recall@FPR plus ECE plus Brier per rung). The methodology spoke at WRITEUP/ood-analysis.md (new) carries the 5-rung-by-slice grid with per-slice bootstrap CIs computed on the same persisted predictions — no extra compute. Pooled-and-per-slice reporting is the hub-and-spoke ADR-004 framing applied to OOD — pooled for A1 (hiring manager exec scan) plus per-slice for A2 (ML researcher generalization-question-by-question read). (2) Recall@FPR pinpoints — the {0.1 percent, 1 percent, 5 percent} triad pre-locked by ADR-006 is ratified at the ledger-row level with one operational refinement — the 0.1 percent pinpoint is computed and reported at the pooled aggregation level only (where benign sample size of approximately 16 thousand to 20 thousand pooled rows yields a meaningful bootstrap CI), not at per-slice or per-LODO-fold aggregation levels (where benign sample size of approximately 200 to 1054 rows reduces the operating-point threshold to 0 to 1 false-positive count and the recall value becomes undefined or ill-conditioned). (3) Bootstrap volatility surfacing — for the 0.1 percent pinpoint specifically, the reporting discipline pre-commits four surfaces — half-width column alongside point estimate; flag marker when half-width exceeds 0.5 times point estimate; resample-degeneracy audit (fraction of resamples that pinned at less than 1 false-positive count); per-resample threshold-drift dump to evals/audit/pinpoint_threshold_drift.json. The methodology spoke explains why the 0.1 percent pinpoint is reported with wider CIs and is not computable per-slice — references PromptShield 2024-2025 larger-scale precedent for context.
source: SPEC_GREENFIELD.md §3 Eval ledger rows 339 and 342 + Phase 0-04 walk Q1 + Q4
acceptance_criterion: SPEC_GREENFIELD ledger row 339 carries locked-to-pooled-headline-plus-per-slice-spoke status; ledger row 342 carries locked-to-0.1pct-pooled-only-plus-volatility-surfacing status; SPEC_SHEET §3.4 OOD slate adds an aggregation-layout subsection naming pooled-headline + per-slice-spoke; SPEC_SHEET §5.1 primary descriptive metrics replaces [OPEN] on recall@FPR pinpoints with [LOCKED — {0.1pct pooled-only, 1pct, 5pct} per ADR-021]; WRITEUP/ood-analysis.md spoke filename pre-committed; WRITEUP/methodology.md gains a "Volatility surfacing at low-FPR pinpoints" subsection; tests/test_invariants.py contains skip-marked stub test_ood_aggregation_layout asserting the 5-slice configuration plus pooled-concatenation pipeline plus per-slice bootstrap CI computation pattern; tests/test_invariants.py contains skip-marked stub test_recall_at_fpr_pinpoint_volatility asserting the bootstrap-volatility-flag pipeline emits half-width + degeneracy-fraction columns for the 0.1 percent pinpoint at pooled level.
closing_commit:
references:
  - https://www.jmlr.org/papers/v7/demsar06a.html
  - https://arxiv.org/abs/2405.14478
  - https://arxiv.org/abs/2410.22770
  - https://dl.acm.org/doi/10.1145/1143844.1143874
  - decisions/ADR-016-data-design-bundle.md
  - decisions/ADR-006-headline-metrics-and-statistical-apparatus.md
  - decisions/ADR-004-reviewer-profile-and-hub-and-spoke-writeup.md
  - decisions/ADR-005-methodology-principles.md
  - docs/research/benchmarks/03_benchmark_hard_negative.md
transcript: transcripts/2026-05-15__phase-0-04__eval-framework.md
---

# ADR-021: Eval slate aggregation — pooled headline plus per-slice spoke and recall@FPR pinpoint feasibility

## Status

Accepted (2026-05-15). Ratifies and refines the OOD slate from ADR-016 plus the recall@FPR pinpoint triad from ADR-006 at the §3 Eval ledger-row level.

## Context

ADR-016 (Phase 0-02) locked the 5 OOD slices but did not specify the aggregation layout — pooled vs per-slice vs both. ADR-006 (Phase 0-00) pre-locked the recall@FPR pinpoint triad {0.1 percent, 1 percent, 5 percent} from the brief mandate but did not address the feasibility of the 0.1 percent pinpoint at the per-slice and per-LODO-fold aggregation levels.

The §3 Eval-level walk in Phase 0-04 surfaced two related concerns:

1. The 5 OOD slices probe fundamentally different generalization questions (over-defense, over-refusal, mixed-misuse, indirect zero-shot, agentic stretch) with heterogeneous sample sizes (n equals 200 to 1054). Pooling them at the headline level loses per-question signal; reporting only per-slice loses an at-a-glance summary number. Demsar 2006 argues per-dataset reporting is the field standard in multi-dataset settings; pooling is acceptable only when datasets are comparably representative — ours are not.

2. The 0.1 percent recall@FPR pinpoint corresponds to a threshold operating at approximately 5 false-positives on a 5 thousand-row test pool (per-LODO-fold benign sample size). On per-slice aggregations (n less than or equal to 1054), the 0.1 percent threshold maps to 0 to 1 false-positive count and the recall value becomes ill-defined under bootstrap resampling. PromptShield 2024-2025 reports recall at FPR equals 0.1 percent on tens-of-thousands of samples; our scale is an order of magnitude smaller per-slice but rescued by pooled aggregation across folds plus slices.

The ADR-004 hub-and-spoke writeup framing provides the natural resolution path — pooled in headline for A1 reviewer; per-slice in spoke for A2 reviewer.

## Decision

### OOD slate aggregation (ledger row 339)

**Pooled headline plus per-slice spoke.** The pooled-OOD column concatenates rows across the 5 OOD slices and computes a single AUPRC plus AUROC plus recall@FPR plus ECE plus Brier per rung; this column sits alongside the pooled-IID column in the PDF executive headline table. The 5-by-rung per-slice grid lives in WRITEUP/ood-analysis.md spoke with per-slice bootstrap CIs computed via the same paired-bootstrap apparatus from ADR-006 plus ADR-022 on the persisted per-row predictions — no extra compute beyond the additional metric calls.

### Recall@FPR pinpoints feasibility (ledger row 342)

**{0.1 percent pooled-only, 1 percent, 5 percent}.** The triad pre-locked by ADR-006 is ratified at the row level. The 0.1 percent pinpoint is computed and reported only at the pooled aggregation level (concatenated rows across 4 LODO folds plus 5 OOD slices plus per-fold-IID, approximately 16 thousand to 20 thousand pooled benigns yielding approximately 16 to 20 false-positives at the threshold — wide-but-meaningful bootstrap CI). At per-slice or per-LODO-fold aggregation, the 0.1 percent threshold pins at 0 to 1 false-positive count and the recall value is reported as "not computable at this aggregation level (n_neg too small)" rather than fabricated. The 1 percent and 5 percent pinpoints are computed at every aggregation level.

### Bootstrap volatility surfacing (ledger row 342 refinement)

For the 0.1 percent pinpoint at pooled level the following volatility surfaces are pre-committed:

| Surface | Implementation |
|---|---|
| Half-width column | Bootstrap CI half-width reported alongside point estimate in the pinpoint table |
| Wide-CI flag marker | Asterisk plus footnote when half-width exceeds 0.5 times point estimate |
| Resample-degeneracy audit | Fraction of bootstrap resamples where the FPR equals 0.001 threshold pinned at less than 1 false-positive count emitted to evals/audit/per_rung_audit.json |
| Per-resample threshold-drift | Distribution of *thresholds* (not just recall values) across resamples dumped to evals/audit/pinpoint_threshold_drift.json |
| Methodology spoke explanation | WRITEUP/methodology.md subsection "Why the 0.1 percent pinpoint is reported with wider CIs and is not computable per-slice" |

The 1 percent and 5 percent pinpoints are reported with point estimate plus standard bootstrap CI without the additional volatility surfaces (sample sizes are sufficient that volatility is not load-bearing).

## Consequences

### Positive

- Aligns with ADR-004 hub-and-spoke — pooled headline serves A1 reviewer's exec-scan need; per-slice spoke serves A2 reviewer's per-question generalization read
- Aligns with ADR-005 Principle 2 (honest evaluation preferred) — pooled-only is dishonest about slice heterogeneity; per-slice-only is dishonest about no-headline-summary; pooled-plus-per-slice surfaces both
- Honors ADR-006 recall@FPR triad at the headline level without fabricating 0.1 percent recall on 0 to 1 false-positive counts at finer aggregation
- 0.1 percent volatility surfacing converts a methodology constraint into a named methodology finding rather than a hidden numerical fragility — methodology contribution
- Zero extra training compute — all metrics computed from persisted per-row predictions on local 64-core Threadripper CPU per ADR-022 parallelization-via-glue plan

### Negative

- Wider headline table (pooled-IID plus pooled-OOD plus 3 recall@FPR pinpoints plus ECE plus Brier per rung) — landscape orientation or two-row header in PDF
- WRITEUP/ood-analysis.md is a new spoke file; one more deliverable in Phase 5
- 0.1 percent volatility surfaces add 2 audit JSON files plus 1 spoke subsection; modest narrative complexity

### Neutral

- Per-slice statistical aggregation uses the same paired-bootstrap apparatus from ADR-006 plus ADR-022; no new inferential machinery
- Stratification along ADR-005 contamination taxonomy (per ADR-018) reported per-slice and per-rung — natural cross-section with the per-slice grid

## Alternatives considered

- **Pooled aggregation only**: simpler exec table; rejected because loses the per-question generalization story and weight-biases toward larger slices (InjecAgent n equals 1054 dominates JBB n equals 200 in the pool)
- **Per-slice only**: most honest per-question; rejected because no single headline OOD number; A1 reviewer must scan 5 rows
- **Per-slice plus macro-average (no pooled)**: GLUE/SuperGLUE convention; rejected because macro-average can hide slice-level CIs and the equal-weight assumption isn't justified across heterogeneous slices
- **Drop the 0.1 percent pinpoint entirely**: simpler; rejected because loses the strict-deployment / over-defense story that 0.1 percent specifically probes per InjecGuard 2024 plus PromptShield 2024-2025
- **Replace 0.1 percent with 0.5 percent**: compromise; rejected because departs from ADR-006 specific triad without a methodology justification beyond convenience

## Phase 1 deliverables

- WRITEUP/ood-analysis.md spoke filename pre-committed
- WRITEUP/methodology.md subsection "Volatility surfacing at low-FPR pinpoints"
- evals/audit/pinpoint_threshold_drift.json schema documented in evals/audit/README.md
- evals/audit/per_rung_audit.json schema documented in evals/audit/README.md

## References

See frontmatter references list. Primary anchors — Demsar 2006 JMLR multi-dataset reporting; PromptShield 2024-2025 recall@FPR low-pinpoint precedent; InjecGuard 2024 over-defense methodology; Davis and Goadrich 2006 PR-vs-ROC variance discussion; ADR-016 OOD slate; ADR-006 pinpoint pre-lock; ADR-004 hub-and-spoke writeup; ADR-005 Principle 2.

## Transcript

See `transcripts/2026-05-15__phase-0-04__eval-framework.md` for the conversation that led to this decision.
