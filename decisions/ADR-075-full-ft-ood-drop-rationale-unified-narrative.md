---
adr_id: "075"
slug: full-ft-ood-drop-rationale-unified-narrative
title: Unify the ADR-050 Revision 2 (FUSE-crash-forced-drop) and ADR-052 (methodology-load-bearing-with-crash-as-trigger) framings into a single account
date: 2026-05-20
status: Accepted
claim_id: CLAIM-075
claim: >-
  ADR-050 Revision 2 (2026-05-18 morning) attributed the Phase 5
  full-FT OOD inference drop to an X11 FUSE EIO crash on /workspace
  MooseFS storage (operational forced-drop framing). ADR-052 (2026-
  05-18 hours later) narrowly superseded ADR-050 R2 to reframe the
  drop as methodologically load-bearing with the FUSE crash as
  proximate trigger. A skeptical reader reading both in sequence
  sees a same-day retcon of the load-bearing reason for cutting a
  planned experiment. This ADR consolidates the two framings into
  one prospective narrative that names both the methodological
  reasoning and the operational trigger together, removing the
  same-day retcon optic without changing the underlying outcome
  (full-FT OOD inference remains dropped; LODO comparison ships
  3-rung; OOD ships 2 trained rungs + 1 classical floor + 2
  reference scorers per ADR-050 R1 + R2 + ADR-052).
source: 2026-05-20 audit hiring-manager-curious finding — the
  ADR-050 → ADR-052 same-day reason-swap erodes reader trust in
  the rest of the ADR corpus. Unification removes the retcon optic
  while preserving both historical ADRs as artifacts.
closing_commit: 428971c
transcript:
supersedes:
  - "050"  # Revision 2 axis only; LLM-judge cost-drop (Revision 1) untouched
  - "052"  # entire scope — its sole purpose was the reframe of ADR-050 R2; ADR-075 absorbs that purpose
superseded_by:
acceptance_criterion: >-
  WRITEUP.md §8.1 + WRITEUP/limitations-and-future-work.md §8.1
  + WRITEUP/model-rungs.md §4.x cite ADR-075 (or ADR-050 R1 for
  the LLM-judge axis) as the single source of truth on the full-FT
  OOD drop rationale. Future reviewers see one coherent narrative
  rather than the ADR-050 R2 + ADR-052 sequence framed as
  competing rationales. ADR-050 R2 + ADR-052 remain in
  decisions/ as historical artifacts.
linked_adrs:
  - "050"  # Revision 2 only
  - "052"
  - "019"  # LoRA training recipe — provides the paired-bootstrap evidence
  - "022"  # statistical apparatus — defines the paired-bootstrap CI methodology
  - "020"  # cost discipline — names the GPU spend cap that constrained re-fire
  - "049"  # GPU order — names the A100 80GB platform the X11 crash hit
---

# ADR-075: full-FT OOD drop rationale -- unified narrative

## Status

Accepted.

## Context

ADR-050 was published in two revisions on 2026-05-18:

- **Revision 1**: LLM-judge reference scorers (gpt-4o-2024-08-06 +
  claude-sonnet-4-6) dropped at Phase 4 cost re-estimation when the
  envelope landed ~16x the original ADR-018 estimate ($14 -> $240)
  driven by per-row LLM-judge inference being charged at the full
  input-prompt token count. The `vendor_black_box` contamination tier
  therefore carries 0 rungs in this submission; the contamination-
  stratification gradient compresses from 4 tiers to 3.
- **Revision 2**: full-FT OOD inference dropped after the Phase 5 X11
  FUSE EIO crash on /workspace MooseFS storage. The 24 LODO direct-
  source predictions from Phase 2 survived; the post-Phase-5 OOD
  inference required a re-fire on Low-stock A100 80GB which the
  operational state didn't allow.

Hours later the same day, ADR-052 was published, reframing the full-FT
drop as methodologically load-bearing (LoRA's paired-bootstrap evidence
already showed fine-tuning was hurting OOD; the FUSE crash was the
proximate trigger that exposed an already-implicit decision, not the
cause of it).

A skeptical reader reading ADR-050 R2 then ADR-052 sees: "I cut a
planned experiment because it crashed -> wait, actually I cut it
because the methodology pointed there -> so why did you write ADR-050
R2 with the operational framing?" Same-day retcons in immutable records
erode reader trust in *any* ADR the author wrote, even when (as here)
the methodological reasoning is genuinely sound and the operational
trigger is genuinely separate.

ADR-050 Revision 1 (LLM-judge cost drop) is unaffected by this; that's
a separate decision on a different axis.

## Decision

Replace the two-ADR same-day retcon with one unified account in
ADR-075:

> Full-FT OOD inference was not run because BOTH (a) the Phase 4
> paired-bootstrap CI on LoRA already showed the fine-tuning direction
> was net-harmful for OOD generalization (LoRA -0.071 AUPRC vs
> frozen-probe on pooled_ood, CI clears zero; paired_cells.parquet
> seed=1 + seed=2 stability check 0/40 cells flagged), AND (b) the
> Phase 5 X11 re-fire attempt crashed on a FUSE EIO before any full-FT
> checkpoint persisted. The methodological reasoning is load-bearing;
> the operational event is the trigger that exposed the
> already-implicit decision. Both halves are real; neither would have
> independently sufficed for a defensible drop (without the LoRA
> evidence the FUSE crash would have required a re-fire attempt;
> without the FUSE crash the methodology argument alone might have
> deferred to v1.1.x rather than dropping at v1.0.x).

The unified narrative is the prospective citation. ADR-050 Revision 2
and ADR-052 are preserved as historical artifacts in `decisions/` — the
record of how the decision logic was authored in stages on 2026-05-18.
WRITEUP.md §8.1 + WRITEUP/limitations-and-future-work.md §8.1 +
WRITEUP/model-rungs.md §4.x cite ADR-075 as the single source of truth
on the full-FT OOD drop rationale.

ADR-050 R1 (LLM-judge cost drop) is preserved cleanly — separate
decision, separate ADR axis, untouched by this supersession.

## Consequences

- Reviewers reading the ADR sequence + the WRITEUP cross-references
  see one coherent rationale rather than two competing ones authored
  hours apart
- The same-day retcon optic is removed without erasing the historical
  record (ADR-050 R2 + ADR-052 both remain readable)
- ADR-050 R1 (LLM-judge cost drop) survives intact on its separate
  axis
- WRITEUP cross-references simplify: one ADR citation (ADR-075)
  instead of two with a "see also" thread between them
- Future references to the full-FT OOD drop in CHANGELOG, NEXT_STEPS,
  or other prose can cite ADR-075 directly rather than navigating
  the ADR-050 R2 -> ADR-052 history
- ADR-072 (frontmatter backfill for ADR-051 + ADR-052) and ADR-075
  both supersede ADR-052 on different axes — ADR-072 on the
  frontmatter axis (closing_commit + Alternatives Considered), ADR-075
  on the narrative axis (unified full-FT drop rationale). Both
  supersessions are documented; ADR-052's full historical content
  remains in `decisions/` for audit-trail purposes

## Alternatives Considered

1. **Leave ADR-050 R2 + ADR-052 as the two-ADR pair.** Rejected — the
   retcon optic is a real reader-trust risk for *any* ADR the author
   wrote. The methodological reasoning in ADR-052 is sound; the
   narrative structure (two ADRs authored hours apart with
   different framings) is the issue. Unifying removes the structural
   problem without changing the methodology content.
2. **Edit ADR-050 in place to incorporate ADR-052's framing.**
   Rejected — would violate the immutability rule (this is content
   change, not editorial fix; doesn't fit ADR-073's named exception
   classes). The immutability discipline is the load-bearing
   constraint; the cost of working within it is the supersession
   chain.
3. **Delete ADR-052.** Rejected — historical record (the decision-
   trail of the same-day reframe) is preserved by keeping both ADR-050
   R2 and ADR-052 in decisions/ while citing ADR-075 prospectively.
   Deletion would lose the lesson about how same-day retcons happen +
   why they should be avoided.
4. **Write ADR-052 differently at the time.** This isn't an
   alternative to ADR-075 (it's an alternative history); noting it
   here for completeness. The 2026-05-18 author's choice to write a
   second ADR rather than revise the first followed the immutability
   discipline (correctly); ADR-075 is the deferred-consolidation move
   the discipline supports.

## Linked ADRs

- ADR-050 Revision 2 (full-FT OOD drop via FUSE EIO): superseded on
  the prospective-citation axis only; the historical record (operational
  facts) remains intact
- ADR-050 Revision 1 (LLM-judge cost drop): NOT superseded; separate
  decision on a separate axis; remains in force
- ADR-052 (methodological reframing of ADR-050 R2): superseded entirely
  in prospective citation; its sole purpose was the ADR-050 R2 reframe
  which ADR-075 now subsumes. Historical content remains for
  audit-trail purposes
- ADR-019 (LoRA training recipe): provides the LoRA evidence that
  ADR-075 cites as the methodological half
- ADR-022 (statistical apparatus): defines the paired-bootstrap CI
  methodology that produced LoRA's -0.071 AUPRC delta vs frozen-probe
- ADR-020 (cost discipline): names the GPU spend cap that constrained
  the re-fire decision
- ADR-049 (GPU order): names the A100 80GB platform the X11 crash hit
- ADR-072 (frontmatter backfill for ADR-051 + ADR-052): supersedes
  ADR-052 on the orthogonal frontmatter axis; this ADR's narrative
  supersession + ADR-072's frontmatter supersession are
  complementary, not conflicting

## Transcript

Transcript file (gitignored per AGENTS.md): the 2026-05-20 audit
governance-audit cycle's identification of the ADR-050 -> ADR-052
same-day retcon as a contradiction class. Captured in
`~/notes/prompt-injection-audit-2026-05-20.md` (high-impact ADR
finding #5) and
`~/notes/prompt-injection-audit-2026-05-20-adr-appendix.md` (drafted
ADR-075).
