---
adr_id: "050"
slug: rung-slate-narrowing-llm-judges-and-full-ft-ood-dropped
title: Rung slate narrowing — LLM judges dropped (cost) + full-FT OOD dropped (FUSE EIO crash); narrow supersession of ADR-018 reference slate + ADR-021 OOD comparison scope
date: 2026-05-18
status: Accepted
claim_id: CLAIM-050
claim: >-
  Phase 4-5 canonical recovery surfaced two rung-slate revisions that materially
  change the reference-comparison narrative and require explicit ADR documentation
  per the project anti-pattern "Mutating a locked decision without writing a
  superseding ADR". Revision 1 (cost — LLM judges dropped) — ADR-018 locked the
  four-rung reference slate as gpt-4o-2024-08-06 + claude-sonnet-4-6 + ProtectAI
  v1 + ProtectAI v2 with an estimated cost envelope of approximately 14 USD
  across both LLM judges plus the LLM-rater audit; Phase 4 cost re-estimation
  against the actual OOD slate sizing (~24k val rows + ~13k pooled OOD slices
  for both detection comparison + rater audit) revealed an actual envelope
  closer to 240 USD (16x the original estimate) — driven by (a) per-row
  LLM-judge inference being charged at the full input-prompt token count
  whereas the original estimate assumed shorter-prompt heuristics, plus (b) the
  rater-audit disagreement-sampled cohort scaling with total prediction volume
  rather than a fixed ~50-pair cohort. User-locked decision (Round 2 Q1,
  2026-05-17 ultra-think risk surfacing) drop LLM judges entirely from the
  reference comparison. The TF-IDF+LR classical floor (verified_disjoint) +
  ProtectAI v1 + v2 (suspected_contamination) remain as the reference rungs;
  the vendor_black_box tier is empty. ADR-018 contamination-stratification
  narrative still holds for the remaining rungs; the four-tier disclosure
  gradient compresses to three tiers (verified_disjoint,
  backbone-partial-disjoint, suspected_contamination). Revision 2 (operational —
  full-FT OOD dropped) — ADR-019 + ADR-021 locked the trained-rung slate as
  classical-floor + frozen-probe + LoRA + full-FT with OOD scoring on all 3
  transformer rungs across the 5-slice OOD slate. Phase 5 X11 full-FT re-fire
  (configured per the runpod-rsync-everything-before-delete memory rule to
  persist checkpoints via cleanup_intermediate_checkpoints set to false)
  crashed mid-training on a FUSE EIO during shutil.copytree of the 598 MB
  optimizer.pt to /workspace MooseFS-backed storage; the trainer crashed before
  any cell final checkpoint persisted to durable storage. The pre-crash full-FT
  LODO predictions (24 parquets from Phase 2 original orchestrator-fired
  full-FT run) survived; full-FT OOD inference is methodologically impossible
  without re-firing a 6-12 hour A100 80GB pod plus a likely repeat of the FUSE
  crash. User-locked decision (Round 4, 2026-05-18 FUSE-crash recovery) abandon
  full-FT OOD; ship 2-rung OOD via the alive pod (frozen-probe + LoRA). full-FT
  remains in the LODO comparison (3-rung ladder narrative — frozen-probe to
  LoRA to full-FT — holds on the LODO held-out attack-source generalization
  test); OOD comparison drops to 2 trained rungs + 1 classical floor + 2
  reference scorers (ProtectAI v1 + v2) = 5 rungs total. Consequences for the
  WRITEUP narrative — the methodology spoke gains a Limitations subsection
  naming both drops with the operational rationale (LLM-judge cost overrun +
  FUSE EIO crash); the headline AUPRC-vs-rung chart on OOD shows 5 rungs not 6;
  the LODO chart shows the full 3-rung trained ladder. Per-axis matched-budget
  framing from ADR-018 is unchanged. ADR-005 contamination taxonomy retains
  all 4 tier labels but the vendor_black_box tier carries 0 rungs in this
  submission.
source: >-
  Phase 4-5 canonical recovery — /exploring-options Round 2 Q1 (LLM-judge cost)
  + Round 4 (FUSE crash recovery) + Round-by-round /exploring-options
  walkthrough 2026-05-17 through 2026-05-18.
acceptance_criterion: >-
  decisions/ADR-050-rung-slate-narrowing-llm-judges-and-full-ft-ood-dropped.md
  exists at this path with Accepted status; SUBMISSION_AUDIT.md regenerates via
  scripts/regenerate_audit.py with ADR-050 included and ADR-018 marked
  superseded-in-part-by-050 on the reference-rung enumeration axis (specifically
  the gpt-4o + claude-sonnet-4-6 entries) and ADR-021 marked
  superseded-in-part-by-050 on the trained-rung OOD comparison scope
  (specifically the full-FT OOD entries); evals/predictions/ contains 0
  LLM-judge predictions + 0 full-FT OOD predictions; SPEC_SHEET §4
  reference-rung enumeration is annotated to indicate that LLM-judge rungs were
  dropped post-lock per ADR-050 with a one-line cost rationale; the WRITEUP
  methodology spoke gains a Limitations subsection covering both rung drops
  with cost-overrun rationale for LLM judges and FUSE-EIO operational rationale
  for full-FT OOD; the OOD analysis chart legend shows 5 rungs (not 6); the
  LODO analysis chart legend shows 3 trained rungs (frozen-probe + LoRA +
  full-FT) where full-FT remains in scope per the surviving Phase 2 LODO
  predictions; A-006 contamination-caveat assumption is unchanged (the three
  remaining contamination tiers are still active); cost_ledger.csv shows 0
  USD LLM-judge entries and the full-FT re-fire entry carries the failed
  status + manual_recovery true + the FUSE EIO crash notes.
closing_commit:
supersedes:
superseded_by:
references:
  - decisions/ADR-005-honest-methodology-over-claimed-best-numbers.md
  - decisions/ADR-018-reference-scorer-slate-and-contamination-stratification.md
  - decisions/ADR-019-lora-and-transformer-training-recipe.md
  - decisions/ADR-021-slice-aggregation-and-headline-metric-protocol.md
  - decisions/upstream_issues.md
  - https://github.com/astral-sh/uv/issues/17801
  - https://github.com/moosefs/moosefs/discussions/380
transcript:
---

# ADR-050: Rung slate narrowing — LLM judges dropped (cost) + full-FT OOD dropped (FUSE EIO crash)

## Status

Accepted (2026-05-18). Narrowly supersedes ADR-018 on the reference-rung enumeration axis (gpt-4o + claude-sonnet-4-6 dropped; ProtectAI v1 + v2 retained); narrowly supersedes ADR-021 on the trained-rung OOD comparison scope (full-FT OOD dropped; full-FT LODO retained). All other axes of ADR-018 + ADR-021 + ADR-019 are unchanged.

## Context

Phase 4 (Analysis) and Phase 5 (Writeup) canonical recovery, fired across 2026-05-17 and 2026-05-18, surfaced two rung-slate revisions that change the reference-comparison narrative. Both revisions are operational responses to costs the methodology-design phase did not account for, not methodological retreats from the original design intent.

### Drop 1 — LLM judges (cost overrun, 16x original envelope)

ADR-018 locked the reference slate at four rungs:

1. OpenAI gpt-4o-2024-08-06 (LLM-judge; vendor_black_box contamination tier)
2. Anthropic claude-sonnet-4-6 (LLM-judge; vendor_black_box contamination tier)
3. ProtectAI deberta-v3-base-prompt-injection v1 (suspected_contamination tier)
4. ProtectAI deberta-v3-base-prompt-injection v2 (suspected_contamination tier)

The cost envelope cited in ADR-018 was approximately 14 USD across both LLM judges plus the LLM-rater audit (A-002 envelope). Pre-Phase-4 cost re-estimation against the actual OOD inference scope (~24k val rows for detection comparison + ~13k pooled OOD slate + ~5 OOD subslate evaluations + rater audit cohort) recomputed the envelope at approximately 240 USD — a 16x overrun. Drivers:

- **Per-row token count** — original estimate assumed short-prompt heuristics. Actual evaluation prompts on long injection examples (e.g., BIPIA email-body attacks, hackaprompt multi-paragraph evasions) hit 1k-3k input tokens routinely. At gpt-4o-2024-08-06 input pricing of approximately $2.50 per million tokens, ~30k rows * 2k tokens ~= 60M tokens per judge ~= $150 per LLM judge.
- **Rater audit scaling** — the disagreement-sampled cohort in ADR-018's rater-audit protocol scales with total prediction volume, not a fixed ~50-pair cohort. At the full Phase 3 prediction count, the audit cohort grows to ~200 pairs which moves the rater audit envelope from ~$5 to ~$30.

User-locked decision (2026-05-17 22:00 UTC, /exploring-options Round 2 Q1 ultra-think risk surfacing): drop LLM judges entirely. The case-study value of the reference comparison concentrates in the contamination-state gradient between TF-IDF+LR (verified_disjoint) and the trained rungs (backbone-partial-disjoint), where the headline ladder-vs-floor story lives. The LLM judges contribute the vendor_black_box anchor but at 16x the budget — value-per-dollar collapses.

### Drop 2 — full-FT OOD (FUSE EIO crash, operational)

ADR-019 locked the trained-rung slate at 4 rungs (classical-floor + frozen-probe + LoRA + full-FT) and ADR-021 locked the OOD comparison scope to scoring all 3 transformer rungs (frozen-probe + LoRA + full-FT) across the 5-slice OOD slate.

Phase 5 X11 full-FT re-fire was configured per the runpod-rsync-everything-before-delete memory rule (cleanup_intermediate_checkpoints: false + the X9 staging fix routing trainer writes through /root/training_staging then copying back to /workspace at cell-end). Cell 1 (fold0/seed42) trained successfully; the trainer process then attempted shutil.copytree of checkpoint-545/optimizer.pt (598 MB) from /root/training_staging → /workspace/.../evals/checkpoints/full_ft/, and MooseFS (FUSE-backed /workspace storage) returned [Errno 5] Input/output error mid-copy. The trainer crashed; the orchestrator's checkpoint rsync returned exit-23 (file vanished during transfer).

Recovery options assessed (full /exploring-options Round 4 walkthrough):

| Option | Cost | Risk |
|---|---|---|
| Re-fire full-FT with config changes to bypass FUSE | $1-3 + 6-12 hr | High — FUSE EIO bug class is non-deterministic; second crash plausible |
| Re-fire full-FT to a different RunPod datacenter | $1-3 + 6-12 hr | Medium — DC-specific MooseFS deployment unclear |
| Abandon full-FT OOD; ship 2-rung OOD | $0 | Low — methodology-spoke Limitations note covers the drop |

User-locked decision (2026-05-18 06:30 UTC, /exploring-options Round 4 recovery): abandon full-FT OOD; ship 2-rung OOD via the alive pod. full-FT remains in the LODO comparison (the 3-rung ladder narrative — frozen-probe → LoRA → full-FT — holds on LODO via the surviving Phase 2 LODO predictions).

## Decision

### Reference rung enumeration (supersedes ADR-018)

Reference rungs in this submission:
- TF-IDF + LR classical floor (verified_disjoint)
- ProtectAI deberta-v3-base-prompt-injection v1 (suspected_contamination)
- ProtectAI deberta-v3-base-prompt-injection v2 (suspected_contamination)

Reference rungs dropped from ADR-018:
- gpt-4o-2024-08-06 (vendor_black_box) — cost overrun
- claude-sonnet-4-6 (vendor_black_box) — cost overrun

### Trained rung OOD scope (supersedes ADR-021 on OOD scope only)

Trained rungs scored on the 5-slice OOD slate:
- frozen-probe (12 cells × 5 slices = 60 OOD predictions)
- LoRA (12 cells × 5 slices = 60 OOD predictions)

Trained rungs scored on LODO held-out attack source ONLY (no OOD):
- full-FT (24 LODO predictions; 0 OOD predictions)

### LODO scope (unchanged)

All 4 trained rungs scored on LODO. The 3-rung transformer ladder narrative + classical-floor anchor holds.

### Cost discipline preserved

Total submission spend at Phase 5 close: approximately $15.32 (under the $80 soft-flag, $125 soft cap, and $200 hard cap per ADR-020).

## Consequences

### Methodology-spoke narrative changes

The WRITEUP methodology spoke gains a Limitations subsection naming both drops:

> **Limitation 1**: LLM-judge reference scorers (gpt-4o-2024-08-06 + claude-sonnet-4-6) were dropped at Phase 4 cost re-estimation when the actual inference-prompt token counts revealed a ~16x envelope overrun ($14 → $240). The vendor_black_box contamination tier therefore has no rungs in this submission. The contamination-stratification gradient compresses from 4 tiers to 3.
>
> **Limitation 2**: full-FT OOD inference was dropped at Phase 5 X11 re-fire when a FUSE EIO crash on RunPod's MooseFS-backed /workspace storage destroyed the full-FT checkpoints mid-persistence. Re-fire was operationally fragile (non-deterministic FUSE bug class; 6-12 hr A100 wall-time). full-FT remains in the LODO comparison; OOD comparison ships 2 trained rungs (frozen-probe + LoRA).

### Submission-audit consequences

- `SUBMISSION_AUDIT.md` regenerates with ADR-018 marked `superseded-in-part-by-050` on the reference enumeration axis (judges only) and ADR-021 marked `superseded-in-part-by-050` on the trained-rung OOD scope axis (full-FT only).
- `SPEC_SHEET §4` annotates the reference enumeration with ADR-050 + cost-rationale link.
- `evals/cost_ledger.csv` carries 0 USD LLM-judge entries (no calls made) + the full-FT re-fire manifest with `failed: true` + `manual_recovery: true` + FUSE EIO notes.

### Assumptions changes

- A-006 (contamination caveat from ADR-018) remains active for the 3 retained contamination tiers (verified_disjoint, backbone-partial-disjoint, suspected_contamination).
- A-007 (LLM-judge non-determinism caveat from ADR-022) becomes vacuous in this submission (no LLM judges fired). Documented in the methodology spoke; A-007 stays in `assumptions.md` for future ADR cross-references.

## Alternatives Considered

### Alternative 1: Reduce LLM-judge prompt template to short-form for cost control

Cost reduction estimate: ~30% (still ~$170). Insufficient to bring the envelope back to the original ~$14. Rejected.

### Alternative 2: LLM-judge a sub-sample only (e.g., 1k rows per slice instead of full)

Cost reduction estimate: ~80%. But: a sub-sampled LLM-judge evaluation no longer matches the methodology-spoke "every reference rung scores every row of every slice" lock from ADR-018. Methodology drift unacceptable; surfaces as a reviewer concern. Rejected.

### Alternative 3: Re-fire full-FT with custom storage routing (output_dir on /root + post-train rsync)

This is effectively what X11 already attempted. The FUSE EIO bug fires on the cross-mount copy step itself (shutil.copytree from /root to /workspace). Custom routing doesn't avoid the cross-mount copy unless we ship checkpoints to a different remote target — which is out of scope for a 5-day case study. Rejected.

### Alternative 4: Retry full-FT in a different RunPod datacenter

MooseFS is deployed across RunPod datacenters with similar configuration; the FUSE EIO bug class is not DC-specific per the upstream MooseFS#380 discussion. Mid-confidence the second DC would crash identically. The $1-3 + 6-12 hr cost is not worth a ~50% expected-completion rate. Rejected.

## Reuse trail

- The 3-rung transformer ladder narrative (frozen-probe → LoRA → full-FT) survives on LODO via the surviving Phase 2 24 predictions per rung
- The 5-rung OOD reference comparison (frozen-probe + LoRA + tfidf-lr + protectai-v1 + protectai-v2) holds on the 5-slice OOD slate
- ADR-018 contamination stratification (4 tiers) compresses to 3 tiers; the methodology-spoke narrative absorbs this with a Limitations note
- ADR-019 + ADR-021 storage-discipline + slice-aggregation locks remain valid for the trained-rung work that did succeed
