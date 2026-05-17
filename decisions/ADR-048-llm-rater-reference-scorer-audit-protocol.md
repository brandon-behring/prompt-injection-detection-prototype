---
adr_id: "048"
slug: llm-rater-reference-scorer-audit-protocol
title: LLM-rater reference-scorer audit protocol — disagreement-with-LoRA baseline + stratified (5 OOD slices × 3 contamination_states) sampling + fixed 2-axis rubric + inter-rater gpt-4o-plus-claude-sonnet + dry-run-then-single-approval cost UX
date: 2026-05-16
status: Accepted
claim_id: CLAIM-048
claim: ADR-046 Q5 user-overrode the original defer recommendation to include the reference-scorer LLM-rater audit as a real Phase 4 deliverable (citing the value of front-loading the audit rather than waiting for a regex-tagger-conservative-enough trigger that may never fire). ADR-048 extends ADR-046 Q5 with the methodology details that turn that decision into an executable protocol — `scripts/audit_reference_scorers.py` (lands in Phase 4 Commit 5 per ADR-046 Q1 6-commit cadence) samples approximately 50 prediction-pairs per reference rung (R-LLM-OpenAI plus R-LLM-Anthropic plus R-ProtectAI-v1 plus R-ProtectAI-v2 per ADR-018) where the reference scorer's prediction disagrees with the LoRA trained-rung classifier (`sign(reference_proba > 0.5) != sign(lora_proba > 0.5)`); LoRA is the disagreement baseline (rather than full-FT or classical-floor) because LoRA is the cheapest GPU-trained rung per ADR-019 (\$60/pod cap vs full-FT's \$100/pod cap per ADR-020) plus the intermediate-quality matched-budget comparison point per ADR-018, balancing audit-narrative realism (we trained a real model, not just a probe) with operator-cost feasibility (the audit can fire as soon as `make headline-lora` lands, ahead of full-FT). Sampling is stratified across the cross-product of 5 OOD slices per ADR-021 (NotInject plus XSTest plus JBB plus BIPIA plus InjecAgent) and 3 contamination_states per ADR-005 (clean plus suspected_contamination plus vendor_black_box) — approximately 3 pairs per (slice, contamination_state) stratum where feasible, totaling approximately 45-50 pairs per reference rung; stratification is necessary because uniform random sampling would heavily over-sample the largest slices (BIPIA plus InjecAgent dwarf the smaller slices) and miss failure modes in rare strata. Each sampled pair is rated by BOTH gpt-4o-2024-08-06 and claude-sonnet-4-6 (same snapshot pins as ADR-018 LLM-judge slate per ADR-042 dedup-holdout precedent for inter-rater reliability) producing two independent rubric records per pair; per-pair rubric is fixed 2-axis (boolean rater_judgment_correct plus ordinal calibration_assessment with three levels overconfident-well_calibrated-underconfident) plus optional string rater_notes for qualitative observations without burdening the aggregation axes; inter-rater agreement (Cohen's kappa on `rater_judgment_correct` plus weighted-kappa on the ordinal `calibration_assessment`) reported in the audit JSON for methodology transparency. Aggregated statistics that the WRITEUP can cite directly — per-reference-rung percent-judged-correct on disagreement cases (the headline reference-scorer-trustworthiness number); per-reference-rung calibration distribution (overconfident-vs-well-vs-underconfident percentages); per-(slice, contamination_state) breakdown surfaces failure modes; inter-rater agreement number scopes confidence in the audit itself. Cost envelope — 4 reference rungs times approximately 50 pairs times 2 LLM-rater calls per pair equals approximately 400 LLM calls at approximately \$0.005 per call equals approximately \$2 plus prompt-template overhead approximately \$3 totaling approximately \$5 per A-002 envelope (well under \$1 per reference rung); cost UX follows Phase 3 ADR-045 Q4 plus ADR-020 pattern — `python scripts/audit_reference_scorers.py --dry-run` previews exact pair count plus per-rung cost estimate; non-dry-run requires single interactive approval prompt before any LLM calls fire; per-rung approvals are over-gating for a sub-\$5 audit. Output persistence — `evals/audit/reference_scorer_rater_audit.json` (one top-level key per reference rung plus nested per-rater plus inter-rater agreement) validated against `ReferenceScorerRaterAuditModel` per ADR-046 Q2 schema-placement-in-`src/eval/schemas.py` decision; LLM judge cache infrastructure at `evals/audit/llm_judge_cache/<judge>__<sha256-prefix>.json` per A-007 plus A-014 reused so cache survives cross-run plus mid-Phase-deprecation. Phase 4 WRITEUP spoke `WRITEUP/reference-scorer-audit.md` (drafted in Phase 5 per ADR-046 Q7 phase-tailoring) consumes the audit JSON to populate the per-rung trustworthiness headline plus calibration-distribution figure plus methodology narrative. Operator dependency — audit fires after `make headline-lora` lands (operator-gated GPU run per ADR-020); does NOT require full-FT or frozen-probe runs; can fire ahead of full Phase 4 canonical numbers if operator prioritizes the audit-narrative deliverable.
source: Phase 4 Commits 2-6 tactical walkthrough — /exploring-options "Phase 4" Q4 5-question session 2026-05-16 (same conversation as ADR-046 plus ADR-047); user requested in-depth explanation of LLM-rater audit design before ratifying; locked Option A1 (disagreement-with-LoRA + stratified + fixed 2-axis rubric); per CLAUDE.md anti-pattern "Adding a methodology component without an ADR" the methodology decision (sampling protocol plus rubric design) warrants its own ADR
acceptance_criterion: decisions/ADR-048-llm-rater-reference-scorer-audit-protocol.md exists at this path with Accepted status; SUBMISSION_AUDIT.md regenerates via scripts/regenerate_audit.py with ADR-048 included; src/eval/schemas.py extended with ReferenceScorerRaterAuditModel pydantic v2 BaseModel at Phase 4 Commit 2 landing per ADR-046 Q2 + this ADR's persistence layout; scripts/audit_reference_scorers.py at Phase 4 Commit 5 landing implements (a) --dry-run cost preview surfacing exact pair count plus per-rung cost estimate before any LLM call fires, (b) sampling protocol per this ADR — disagreement-with-LoRA via `sign(reference_proba > 0.5) != sign(lora_proba > 0.5)` filter applied to predictions parquets at `evals/predictions/` for each reference rung in (R-LLM-OpenAI, R-LLM-Anthropic, R-ProtectAI-v1, R-ProtectAI-v2) per ADR-018, stratified by (slice, contamination_state) cross-product per ADR-021 + ADR-005, targeting approximately 3 pairs per stratum totaling approximately 50 per reference rung, (c) inter-rater protocol — each sampled pair rated by BOTH gpt-4o-2024-08-06 and claude-sonnet-4-6 via the fixed 2-axis rubric (boolean rater_judgment_correct plus ordinal calibration_assessment plus optional string rater_notes), (d) single interactive approval prompt before non-dry-run firing per ADR-020 + ADR-045 Q4, (e) LLM judge cache reused at evals/audit/llm_judge_cache/<judge>__<sha256-prefix>.json per A-007 + A-014, (f) results persisted to evals/audit/reference_scorer_rater_audit.json with one top-level key per reference rung plus per-rater rubric records plus inter-rater Cohen's kappa on rater_judgment_correct plus weighted-kappa on calibration_assessment plus per-(slice, contamination_state) breakdown plus headline percent-judged-correct number; Makefile target `audit-reference-scorers` at Phase 4 Commit 6 landing wraps the script with the cost-cap interactive-approval gate; cost envelope tracked in evals/cost_ledger.csv per ADR-020 ledger discipline plus integration with cost-rollup-check; transcript checkpoint at transcripts/2026-05-16__phase-4-entry-plus-phase-1-library-first-refactor.md captures the Q4 in-depth walkthrough where this decision was ratified.
closing_commit:
supersedes:
superseded_by:
references:
  - decisions/ADR-005-attack-class-scope-and-three-state-contamination-taxonomy.md
  - decisions/ADR-006-headline-metrics-and-statistical-floor.md
  - decisions/ADR-018-reference-scorer-slate-and-contamination-stratification.md
  - decisions/ADR-019-trained-rung-ladder-and-lora-config.md
  - decisions/ADR-020-cost-cap-and-runpod-deploy.md
  - decisions/ADR-021-eval-slate-aggregation-and-recall-fpr-pinpoints.md
  - decisions/ADR-022-statistical-inference-apparatus.md
  - decisions/ADR-042-dedup-holdout-llm-judge-pre-labeling-protocol.md
  - decisions/ADR-045-phase-3-evaluation-implementation-bundle.md
  - decisions/ADR-046-phase-4-analysis-implementation-bundle.md
transcript: transcripts/2026-05-16__phase-4-entry-plus-phase-1-library-first-refactor.md
---

# ADR-048: LLM-rater reference-scorer audit protocol

## Status

Accepted (2026-05-16). Does not supersede any prior ADR; extends ADR-046 Q5 user override with the methodology details that turn the decision-to-include into an executable protocol.

## Context

ADR-046 Q5 captured a user-overridden decision: the original recommendation was to **defer** the reference-scorer LLM-rater audit per ROADMAP Phase 4 line 95's `[TBD-at-Phase-4]` cautionary framing. The user explicitly overrode and locked **include-now** — citing the value of front-loading the audit as a Phase 4 deliverable rather than waiting for a regex-tagger-conservative-enough trigger that may never fire.

ADR-046's Q5 lock specified "what" — include the audit as a Phase 4 deliverable — but left "how" open. Specifically:

- **What does "disagreement" mean?** Disagreement with which baseline (trained rung? ground-truth label? other reference rungs?)
- **What does "~50 disagreement-sampled pairs per reference rung" actually sample?** Random? Stratified? Across what dimensions?
- **What's the rubric format?** Open-ended notes? Fixed schema? Multi-axis?
- **Inter-rater reliability?** Single rater per pair? Multiple raters?
- **Cost-cap UX?** Per-rung approval? Single approval? Dry-run first?

Per the project CLAUDE.md anti-pattern "Adding a methodology component without an ADR", these are methodology decisions (sampling protocol + rubric design = decisions about HOW we measure reference-scorer trustworthiness; reviewer-visible methodology surface). ADR-048 locks all five sub-decisions so Phase 4 Commit 5's `scripts/audit_reference_scorers.py` executes against a durable methodology contract.

### Why the user overrode the defer recommendation

The ROADMAP framing was conservative — invest only IF a regex-tagger-conservative-enough trigger fires. The user's reasoning at Q5 override: this trigger may never fire (it requires a regex-tagger pass to first surface conservatism concerns; absent that, the defer-indefinitely posture leaves us without a reference-scorer-trustworthiness number for the WRITEUP). Front-loading the audit at a sub-\$5 cost envelope is a better investment than the open-ended defer.

The walkthrough's Q4 in-depth explanation framed the decision more carefully: the reference-scorer audit is the standard methodology in injection-detection literature (Lakera + ProtectAI publish similar audits); having one strengthens the comparison-baseline framing in the WRITEUP.

## Decision

### (a) Disagreement baseline — LoRA trained rung

`scripts/audit_reference_scorers.py` samples pairs where the reference scorer's prediction differs from the **LoRA trained rung's** prediction:

```
sign(reference_proba > 0.5) != sign(lora_proba > 0.5)
```

**Why LoRA** (not full-FT, classical-floor, or ground-truth label):

- LoRA is the cheapest GPU-trained rung per ADR-019 (\$60/pod cap vs full-FT's \$100/pod cap per ADR-020)
- LoRA is the intermediate-quality matched-budget comparison point per ADR-018
- Disagreement-with-LoRA is the comparison surface the WRITEUP will actually make (audit data directly supports the methodology claim)
- Audit can fire as soon as `make headline-lora` lands, ahead of full-FT (operator-cost feasibility)
- Disagreement-with-ground-truth would conflate label-noise with reference-scorer behavior; LoRA framing avoids this
- Disagreement-with-other-reference-rungs would require all 4 reference rungs to have fired first (more dependencies)

### (b) Sampling stratification — 5 OOD slices × 3 contamination_states

Per reference rung, ~50 pairs are stratified across:

- **5 OOD slices** per ADR-021 (NotInject + XSTest + JBB + BIPIA + InjecAgent)
- **3 contamination_states** per ADR-005 (clean + suspected_contamination + vendor_black_box)
- **Cross-product = 15 strata**; target ~3 pairs per stratum (where feasible)

Without stratification, uniform random sampling would heavily over-sample the largest slices (BIPIA + InjecAgent dwarf the smaller slices) and miss failure modes in rare strata. Stratification is the standard methodology fix.

### (c) Rubric format — fixed 2-axis JSON

Per-pair rubric:

```python
{
  "rater_judgment_correct": bool,                  # Was the reference scorer's prediction defensible?
  "calibration_assessment": Literal[
    "overconfident",                                # Reference proba > 0.9 but ground-truth is ambiguous
    "well_calibrated",                              # Reference proba reflects actual uncertainty
    "underconfident",                               # Reference proba ~ 0.5-0.7 but case is clear-cut
  ],
  "rater_notes": str | None,                        # Optional qualitative observation
}
```

Two axes are enough for the aggregations the WRITEUP needs (percent-judged-correct + calibration distribution); `rater_notes` captures qualitative observations without burdening the aggregation axes.

### (d) Inter-rater reliability — both gpt-4o + claude-sonnet rate every pair

Each sampled pair is rated by **BOTH** gpt-4o-2024-08-06 and claude-sonnet-4-6 (same snapshot pins as ADR-018 LLM-judge slate; matches ADR-042 dedup-holdout LLM-pre-label precedent for inter-rater reliability).

Reported aggregations:

- Cohen's kappa on `rater_judgment_correct` (binary agreement)
- Weighted kappa on `calibration_assessment` (ordinal agreement)
- Per-rater raw distributions (so the WRITEUP can disclose any rater-specific bias)

### (e) Cost UX — dry-run preview → single interactive approval

Per ADR-020 + ADR-045 Q4 pattern:

```
python scripts/audit_reference_scorers.py --dry-run
# → "Would sample 4 ref rungs × ~50 pairs × 2 raters = ~400 LLM calls"
# → "Estimated cost: ~$2 (LLM calls) + ~$3 (prompt overhead) = ~$5 per A-002 envelope"

python scripts/audit_reference_scorers.py
# → "Approve paid LLM-rater audit (cost ~$5)? [y/N] "
# → on 'y', fires the full slate
```

Per-rung approvals would be over-gating for a sub-\$5 audit. LLM judge cache at `evals/audit/llm_judge_cache/<judge>__<sha256-prefix>.json` reused per A-007 + A-014 so cache survives cross-run + mid-Phase deprecation.

### (f) Output persistence

`evals/audit/reference_scorer_rater_audit.json` validated against `ReferenceScorerRaterAuditModel` per ADR-046 Q2 schema-placement decision (lives in `src/eval/schemas.py`):

```json
{
  "schema_version": "1.0",
  "generated_at_utc": "...",
  "lora_rung_path": "evals/predictions/lora__fold*__seed*.parquet",
  "cost_summary": {"total_calls": 400, "estimated_cost_usd": 5.0, "actual_cost_usd": ...},
  "per_reference_rung": {
    "R-LLM-OpenAI": {
      "headline_pct_correct": 0.85,
      "calibration_distribution": {"overconfident": 0.10, "well_calibrated": 0.75, "underconfident": 0.15},
      "inter_rater_kappa": {"judgment": 0.82, "calibration_weighted": 0.71},
      "per_stratum_breakdown": [{"slice": "BIPIA", "contamination_state": "clean", "n_sampled": 3, "n_correct": 3}, ...],
      "raw_records": [{"row_id": "...", "rater": "gpt-4o-2024-08-06", "rubric": {...}}, ...]
    },
    "R-LLM-Anthropic": {...},
    "R-ProtectAI-v1": {...},
    "R-ProtectAI-v2": {...}
  }
}
```

### (g) Operator dependency

Audit fires after `make headline-lora` lands (operator-gated GPU run per ADR-020). Does NOT require full-FT or frozen-probe runs; can fire ahead of full Phase 4 canonical numbers if operator prioritizes the audit-narrative deliverable.

## Consequences

**Positive:**

- ADR-046 Q5 user override now has executable methodology behind it; Phase 4 Commit 5 can ship a defensible audit (not a placeholder).
- Stratified sampling produces audit data that covers all 15 (slice × contamination_state) strata, not just the largest.
- Inter-rater protocol surfaces rater-specific biases + makes the audit reproducible (anyone with API keys can re-run + verify).
- LoRA dependency is no new gating dependency (LoRA is already on the operator critical path for canonical Phase 4 numbers).
- WRITEUP/reference-scorer-audit.md spoke has a clear data shape to draft against in Phase 5.
- Sub-\$5 cost envelope keeps the audit well within A-002 budget.

**Negative / cost:**

- 400 LLM calls (~\$5) is a real cost added to the project envelope.
- Audit cannot fire until `make headline-lora` lands (operator-gated; adds a sequencing dependency).
- Inter-rater protocol doubles the LLM call count vs single-rater; chosen anyway for reproducibility.
- Per-stratum target of ~3 pairs is small; sub-stratum stats will be high-variance + the WRITEUP needs to be careful about claims at the stratum level (headline percent-judged-correct is the load-bearing number; sub-stratum breakdown is qualitative).

**Neutral:**

- LLM judge cache reused — no new cache infrastructure.
- Cost-cap UX matches Phase 3 + ADR-020 pattern — no new operator muscle memory.
- Methodology semantics independent of ADR-046's other Q5-locks; this ADR refines only the LLM-rater protocol.

## Alternatives Considered

- **Disagreement-with-Full-FT-rung baseline**: cleaner "reference disagrees with our BEST model" narrative. *Rejected because*: full-FT 84-parquet output gated on most-expensive operator-approved run per ADR-020 (\$100/pod cap); audit can't fire until full-FT lands, delaying the WRITEUP narrative further than necessary.
- **Disagreement-with-ground-truth-label baseline**: no trained-rung dependency. *Rejected because*: if labels are noisy at the margin (common in adversarial datasets), the audit becomes about label quality rather than reference-scorer behavior; conflates two distinct concerns.
- **Disagreement-with-other-reference-rungs baseline**: pure between-reference comparison. *Rejected because*: requires all 4 reference rungs to have fired before audit can sample; more dependencies than needed; doesn't align with the WRITEUP comparison-with-trained-rung narrative.
- **Open-ended JSON rubric** per pair: maximum flexibility for novel observations. *Rejected because*: hurts aggregation + WRITEUP narrative (per-rater open-ended notes can't be averaged); reviewer can't easily compare across reference rungs.
- **3-axis rubric** (correct + calibration + fail_mode taxonomy): more dimensions per pair. *Rejected because*: adds analyst load (fail_mode taxonomy needs upfront design); 2 axes already cover the headline aggregations the WRITEUP needs; the optional `rater_notes` field captures fail-mode observations qualitatively.
- **Single rater per pair** (only gpt-4o OR only claude-sonnet): halves cost. *Rejected because*: loses inter-rater reliability number; loses ability to surface rater-specific bias; the ~\$2 cost saving doesn't justify the methodology weakening.
- **Per-rung approval prompts** (4 sequential approvals): finer cost control. *Rejected because*: over-gating for a sub-\$5 audit; single approval matches Phase 3 `make eval-reference-scorers-paid` pattern.
- **Defer to Phase 5** (write ADR alongside Commit 5 code): tighter ADR-code coupling. *Rejected per user decision in walkthrough*: methodology decision warrants durable capture NOW so Commits 2-4 land knowing the contract (e.g., schema decisions need to accommodate the per-rater + per-stratum shape this ADR locks).

## References

- `decisions/ADR-005-attack-class-scope-and-three-state-contamination-taxonomy.md` — 3 contamination_states stratification axis
- `decisions/ADR-006-headline-metrics-and-statistical-floor.md` — statistical floor context
- `decisions/ADR-018-reference-scorer-slate-and-contamination-stratification.md` — 4 reference rungs source
- `decisions/ADR-019-trained-rung-ladder-and-lora-config.md` — LoRA rung config (the disagreement baseline)
- `decisions/ADR-020-cost-cap-and-runpod-deploy.md` — cost-cap discipline + dry-run preview pattern
- `decisions/ADR-021-eval-slate-aggregation-and-recall-fpr-pinpoints.md` — 5 OOD slices stratification axis
- `decisions/ADR-022-statistical-inference-apparatus.md` — bootstrap apparatus context
- `decisions/ADR-042-dedup-holdout-llm-judge-pre-labeling-protocol.md` — inter-rater protocol precedent
- `decisions/ADR-045-phase-3-evaluation-implementation-bundle.md` — Q4 cost-UX pattern source (single interactive approval)
- `decisions/ADR-046-phase-4-analysis-implementation-bundle.md` — Q5 user override (the parent decision this ADR extends)

## Transcript

See `transcripts/2026-05-16__phase-4-entry-plus-phase-1-library-first-refactor.md` for the conversation that led to this decision (Phase 4 walkthrough Q1-Q7 + Q5 user override + Phase 4 Commits 2-6 tactical walkthrough Q4 in-depth explanation + Option A1 ratification).
