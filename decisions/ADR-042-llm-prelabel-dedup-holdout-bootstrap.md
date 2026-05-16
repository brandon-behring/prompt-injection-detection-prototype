---
adr_id: "042"
slug: llm-prelabel-dedup-holdout-bootstrap
title: LLM-judge pre-label as Q5 holdout-labeling bootstrap with human override
date: 2026-05-16
status: Accepted
claim_id: CLAIM-042
claim: ADR-041 Q5 locks Brandon-hand-labeled 50-pair stratified-cosine-band holdout as the dedup calibration ground truth (option A; option D LLM-judge labels was explicitly rejected because judge prior may contaminate calibration). ADR-042 refines (does not supersede) Q5 with a labeling-workflow bootstrap — gpt-4o-2024-08-06 produces a preliminary llm_judge_label per pair plus llm_judge_reasoning rationale plus llm_judge_model snapshot identifier; Brandon hand-examines each pair and either confirms (sets human_label equals llm_judge_label) or overrides (sets human_label to the corrected truth). The calibration script resolves the effective true_duplicate via priority order — human_label takes precedence when non-null else falls back to llm_judge_label. The calibration JSON discloses label_provenance with human_verified_count plus llm_judge_only_count plus human_verified_pct plus llm_judge_model so reviewers can read off exactly which fraction of labels carry human verification. The ground-truth methodology stays Brandon-hand-labeled-when-possible — the LLM bootstrap only fills in initial values that humans review; this preserves ADR-041 Q5's rejection of pure-LLM-judge labeling while accelerating the labeling workflow. The choice of gpt-4o-2024-08-06 matches the snapshot pinned by ADR-018 for the headline LLM-as-rater (consistency across the LLM-judge usage surface).
source: User request to use OpenAI judge bootstrap on Phase 1 Commit 3 holdout (post-build_dedup_holdout.py run)
acceptance_criterion: scripts/llm_prelabel_dedup_holdout.py exists at repo root and accepts OPENAI_API_KEY via environment plus writes llm_judge_label plus llm_judge_reasoning plus llm_judge_model fields per pair to data/dedup_holdout.jsonl; scripts/calibrate_dedup.py resolves true_duplicate via priority order human_label greater-than llm_judge_label plus persists label_provenance disclosure block in evals/dedup_calibration.json; .env.local is gitignored and accepted by the script via os.environ.get(OPENAI_API_KEY); openai>=1.50 added to pyproject.toml dependencies.
closing_commit: <FILLED-POST-COMMIT>
references:
  - decisions/ADR-041-phase-1-data-implementation-bundle.md
  - decisions/ADR-018-llm-judge-and-reference-rung-pins.md
  - decisions/ADR-035-secrets-management-three-store-split.md
  - https://platform.openai.com/docs/models/gpt-4o
transcript: transcripts/2026-05-16__phase-1-implementation.md
---

# ADR-042: LLM-judge pre-label as Q5 holdout-labeling bootstrap with human override

## Status

Accepted (2026-05-16).

## Context

Phase 1 Commit 3 landed the dedup pipeline per ADR-016 Q4 + ADR-041 Q5 — including the 50-pair stratified-cosine-band holdout builder (`scripts/build_dedup_holdout.py`) and the calibration script (`scripts/calibrate_dedup.py`). ADR-041 Q5 locked option A (Brandon hand-labels each of 50 candidate pairs) and explicitly rejected option D (LLM-judge labels 100 pairs plus Brandon spot-checks 20) on the grounds that the judge prior could contaminate the calibration and that near-duplicate judgment quality on LLM judges is unknown.

Operationally, however, hand-labeling 50 pairs of prompt-injection texts via cold-start visual inspection imposes approximately 1-2 hours of researcher time. User flagged a pragmatic acceleration — let an LLM judge produce a preliminary label per pair so the researcher's hand-examination becomes an *override* pass rather than a *from-scratch* pass.

The methodological tension to resolve: how to accelerate without sacrificing the rigor that ADR-041 Q5 locked. The answer landed on a layered-provenance design — both labels persist; humans win where present; calibration discloses the labeling provenance fraction.

## Decision

### Bootstrap workflow

```
build_dedup_holdout.py  ->  llm_prelabel_dedup_holdout.py  ->  Brandon reviews  ->  calibrate_dedup.py
(generates 50 candidates)   (sets llm_judge_label)            (sets human_label)    (resolves + persists)
```

### Per-pair fields persisted to `data/dedup_holdout.jsonl`

| Field | Type | Set by | Notes |
|---|---|---|---|
| `pair_id` | int | builder | unique ID |
| `text_a`, `text_b`, `idx_a`, `idx_b`, `source_a`, `source_b`, `cosine`, `band` | various | builder | candidate-pair payload |
| `llm_judge_label` | bool or null | prelabel script | gpt-4o-2024-08-06 verdict |
| `llm_judge_reasoning` | str | prelabel script | one-sentence rationale (max ~250 chars) |
| `llm_judge_model` | str | prelabel script | snapshot identifier (`gpt-4o-2024-08-06`) |
| `human_label` | bool or null | Brandon (manual) | null = not yet reviewed |
| `true_duplicate` | bool | calibrate script | resolved via priority (see below) |

### Label-resolution rule (calibrate-time)

```
if human_label is not None:
    true_duplicate = human_label
    provenance = "human"
elif llm_judge_label is not None:
    true_duplicate = llm_judge_label
    provenance = "llm_judge"
else:
    HoldoutNotLabeledError
```

### Calibration JSON disclosure (`evals/dedup_calibration.json`)

The calibration JSON gains a top-level `label_provenance` block:

```json
{
  "label_provenance": {
    "human_verified_count": 12,
    "llm_judge_only_count": 38,
    "human_verified_pct": 24.0,
    "llm_judge_model": "gpt-4o-2024-08-06"
  }
}
```

This block lets reviewers read off exactly which fraction of the 50 labels carries human verification vs LLM-judge only. The eventual goal is `human_verified_pct = 100.0` once Brandon's hand-examination completes; the bootstrap state permits a calibration run at lower verification (preliminary; flagged in the calibration JSON).

### Judge model + parameters

- Model — `gpt-4o-2024-08-06` (matches ADR-018 LLM-as-rater snapshot for consistency across the LLM-judge usage surface).
- Temperature — 0.0 (deterministic judgments).
- Response format — JSON object `{is_duplicate: bool, reasoning: str}`.
- max_tokens — 300 (typical responses <100 tokens).
- Retry policy — exponential backoff 3 attempts; failures recorded with `llm_judge_label: null` plus `FAILED:` reasoning text.

### Cost envelope

Approximately $0.0025 per pair at 2026-05 OpenAI pricing for gpt-4o-2024-08-06; 50 pairs ~= $0.12 total. Well below the ADR-016 compute envelope ($60-115).

### Key invariant — methodology is still hand-labeled

The ground-truth labeling methodology stays Brandon-hand-labeled — the LLM bootstrap is a UI affordance that fills in initial values for the researcher's review. Brandon's `human_label` is the authoritative ground truth wherever set. The calibration JSON's `human_verified_pct` discloses to the reviewer exactly how much of the calibration is human-verified.

## Consequences

**Positive:**

- Acceleration — researcher labeling time approximately halves; LLM-pre-label makes each pair a fast review-and-confirm rather than a from-scratch decision.
- Provenance preserved — `llm_judge_label` + `human_label` persist as separate fields; calibration JSON discloses the split.
- ADR-018 LLM-judge usage gets a small dogfood — same model snapshot used for headline rating gets exercised on the dedup-judgment task; any quality issues surface early.
- Re-runnable — if Brandon overrides many LLM labels, the calibration JSON's `human_verified_pct` rises; calibration regenerates trivially.
- Compatible with ADR-041 Q5 strict option A — when `human_verified_pct = 100`, the LLM-pre-label is effectively just initial UI state that was always overwritten; no methodology compromise.

**Negative / cost:**

- Additional dep — `openai>=1.50` enters `pyproject.toml`; openai SDK adds approximately 5MB. Acceptable.
- Cost — approximately $0.12 for 50 pairs; trivial vs total budget.
- Risk of researcher confirmation bias — if the LLM's preliminary label biases Brandon's judgment, the hand-examination becomes less independent. Mitigation — `llm_judge_reasoning` is shown alongside the label so Brandon evaluates the reasoning + can spot weak LLM justifications.
- Risk of low `human_verified_pct` at submission — if Brandon does not hand-examine all 50 before submission, the calibration JSON ships with disclosure `human_verified_pct < 100` and reviewer may flag. Mitigation — submission-readiness gate 1 (zero `[OPEN]` in SPEC_SHEET) is checked at v1.0.0 tag; SPEC_SHEET §3.5 status row tracks Phase 1 Commit 3 close including holdout-labeling completeness.

**Neutral:**

- ADR-041 Q5 remains the authoritative locked methodology; ADR-042 is a tooling refinement that operates within Q5.
- The 0.80 threshold + the MiniLM encoder + the stratified-cosine-band sampling structure are unchanged.

## Alternatives Considered

- **Pure ADR-041 Q5 option A (no LLM bootstrap)**: rejected for this iteration as the user explicitly requested LLM-pre-label acceleration; ADR-041 Q5's methodology is preserved via the human-override + provenance-disclosure design.
- **Pure LLM-judge labeling (no human override) per ADR-041 Q5 option D**: rejected — same rationale ADR-041 Q5 used; pure LLM labels carry judge-prior contamination risk.
- **Human-only labeling with LLM as second opinion (inverse provenance priority)**: rejected — would require Brandon to label from scratch first; defeats the acceleration purpose.
- **Different judge model (gpt-4o-mini-2024-07-18, o1-mini)**: rejected for this iteration — gpt-4o-2024-08-06 matches the ADR-018 snapshot for consistency. Cheaper or smarter alternatives can be explored as a future-work axis if the judge quality surfaces issues.

## References

- ADR-016 (data design bundle — dedup encoder + threshold locks)
- ADR-018 (LLM-judge and reference-rung pins — `gpt-4o-2024-08-06` snapshot)
- ADR-035 (secrets management — `OPENAI_API_KEY` env-var discovery)
- ADR-041 (Phase 1 implementation bundle — Q5 stratified-cosine-band holdout)
- OpenAI gpt-4o model card — https://platform.openai.com/docs/models/gpt-4o

## Transcript

See `transcripts/2026-05-16__phase-1-implementation.md` for the conversation that led to this decision.
