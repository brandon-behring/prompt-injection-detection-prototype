---
adr_id: "052"
slug: full-ft-ood-drop-methodological-reframing-of-adr-050-r2
title: Full-FT OOD inference drop — methodological reframing; narrow supersession of ADR-050 Revision 2 (FUSE-crash-only framing)
date: 2026-05-18
status: Accepted
claim_id: CLAIM-052
claim: >-
  ADR-050 Revision 2 attributed the Phase 5 full-FT OOD inference
  drop solely to an X11 FUSE EIO crash on /workspace MooseFS storage
  (operational forced-drop framing). This ADR narrowly supersedes
  Revision 2 to reframe the drop as **methodologically load-bearing
  + operationally triggered**: the rung-ladder + paired-bootstrap
  CI inspection at LoRA results had already established that
  further fine-tune investment on the v1.0.x training scope was
  unlikely to pay off; the FUSE crash was the proximate trigger
  that exposed a decision the methodology already pointed toward.
  Revision 1 (LLM-judge cost drop) is unchanged. The
  vendor_black_box contamination tier still carries 0 rungs in
  this submission. ADR-050 Revision 2's operational facts remain
  accurate; the load-bearing reason is restated.

  Methodological reasoning that decided the post-crash choice.
  Phase 4 paired-bootstrap analysis showed LoRA's pooled_ood AUPRC
  delta vs frozen-probe at -0.071 (CI clears zero;
  paired_cells.parquet seed=1 + seed=2 stability check 0/40 cells
  flagged) — fine-tuning the head onto the LODO direct-injection
  training pool was actively HURTING OOD generalization relative
  to leaving the pretrained ModernBERT-base embeddings intact.
  Full-FT (full backbone trainable; ~149M parameters trainable vs
  LoRA's ~1.5M) was a larger version of the same fine-tuning
  mechanism that LoRA had just shown to be net-harmful on OOD.
  Expected marginal benefit of full-FT-OOD over LoRA-OOD on the
  same training pool: low. Cost of re-firing full-FT OOD inference
  on a Low-stock A100 80GB: ~6-12 hours wall + repeat-FUSE-risk
  + ~$5-12 GPU spend + operator approval gates per ADR-020.
  Cost-benefit lands on drop.

  Retrospective self-awareness on full-FT LODO investment. With
  the data-set sizes used (~4.7K positives + ~17K benigns
  post-dedup, no augmentation) and the paired-bootstrap evidence
  that LoRA → frozen-probe delta is negative on OOD, the
  rung-ladder + CI inspection now suggests the full-FT LODO
  investment itself was likely not load-bearing for the
  characterisation conclusions of this submission. A v1.1.x
  iteration with a larger training pool (e.g., augmentation;
  cross-source injection-style addition) might revisit
  full-FT as the rung where the additional parameter budget
  starts to pay; the v1.0.x scope locks full-FT in LODO (per
  the original ADR-019 commitment that produced the 24 Phase 2
  LODO predictions) and drops full-FT from OOD. The FUSE crash
  is the proximate operational event that exposed the
  decision-not-to-push-through; the methodological reasoning
  above is the load-bearing justification.

  Consequences. Reviewer-facing surface: WRITEUP §8.1 full-FT
  bullet rewritten to lead with the methodological reasoning +
  acknowledge the FUSE crash as trigger. WRITEUP/model-rungs.md
  §4.3 full-FT Note paragraph re-anchored to the same framing.
  README does not surface ADR-052 directly (the headline finding
  is unchanged: LoRA + frozen-probe + 2 ProtectAI = 5-rung OOD
  slate). Governance-trail: ADR-050 frontmatter gains
  `superseded_by: [ADR-052]` on the Revision 2 axis only;
  Revision 1 (LLM-judge cost drop) is untouched.
source: >-
  Post-v1.0.2 review of REPO_AUDIT_2026-05-18 + user's
  cover-letter draft language (draft.md) that framed the full-FT
  decision as methodological judgment rather than operational
  forced-drop. The cover-letter version is the more honest
  read of the decision-not-to-push-through; ADR-050 R2's
  operational-only framing under-states the methodological
  reasoning that decided the post-crash choice. AskUserQuestion
  4-Q batch 2026-05-18 #N+2 Q1 user-locked the methodological-
  load-bearing-with-crash-as-trigger framing.
acceptance_criterion: >-
  decisions/ADR-052-...md exists at this path with Accepted status;
  decisions/ADR-050-...md frontmatter gains
  `superseded_by: [ADR-052]` (narrow — Revision 2 axis only);
  WRITEUP/limitations-and-future-work.md §8.1 full-FT bullet
  rewritten to lead with methodological reasoning + acknowledge
  FUSE crash as operational trigger; WRITEUP/model-rungs.md §4.3
  full-FT Note paragraph re-anchored to the same framing;
  SUBMISSION_AUDIT.md regenerates via
  scripts/regenerate_audit.py with ADR-052 included; CHANGELOG
  [1.0.3] entry summarises the supersession.
closing_commit:
supersedes:
  - ADR-050
superseded_by:
references:
  - decisions/ADR-019-lora-and-transformer-training-recipe.md
  - decisions/ADR-022-statistical-inference-apparatus.md
  - decisions/ADR-050-rung-slate-narrowing-llm-judges-and-full-ft-ood-dropped.md
  - decisions/ADR-051-v1.0.x-carryforward-of-t0-and-invariant-scaffolds.md
  - WRITEUP.md
  - WRITEUP/limitations-and-future-work.md
  - WRITEUP/model-rungs.md
transcript:
---

# ADR-052 — Full-FT OOD inference drop: methodological reframing of ADR-050 Revision 2

## Context

ADR-050 Revision 2 (2026-05-18) attributed the Phase 5 full-FT OOD
inference drop entirely to operational events: the X11 full-FT
re-fire (configured per the runpod-rsync-everything-before-delete
memory rule) crashed mid-training when `shutil.copytree` of the
598 MB `optimizer.pt` to /workspace MooseFS-backed FUSE storage
returned `[Errno 5] Input/output error` (uv#17801 + MooseFS#380
upstream context). The framing locked the full-FT OOD drop as a
**forced operational outcome** — the rung was lost to a non-
deterministic FUSE failure mode that re-firing would likely re-
trigger at ~$5-12 additional spend.

User's cover-letter draft (draft.md, post-v1.0.2 review) framed the
same decision differently: *"A fully fine-tuned ModernBERT-base
model. However, with the data set sizes used and without any data
augmentation, it did not seem worthwhile to spend further GPU
compute here. To me, this is the benefit of doing model rungs and
confidence intervals to see if we are getting any benefit."* The
cover-letter version describes a methodological judgment that
the rung ladder + paired-bootstrap CI had already pointed toward
**before** the FUSE crash forced the choice into the open. Both
framings are factually true; ADR-050 R2 captures the *trigger* +
not the *decision*. ADR-052 narrowly supersedes Revision 2 to
restate the load-bearing reason.

## Decision

Drop full-FT OOD inference at Phase 5 per the methodological
reasoning enumerated below. The FUSE crash is the operational
event that exposed the decision; it is NOT the load-bearing
reason.

### Methodological reasoning (load-bearing)

Phase 4 paired-bootstrap analysis (per ADR-022, 10K resamples × 2
seeds; `evals/bootstrap/paired_cells.parquet` +
`paired_cells_seed2.parquet`; 0/40 cells flagged at 5 pct stability
threshold) established:

- LoRA's `pooled_ood` AUPRC delta vs frozen-probe at **-0.071**
  (paired-bootstrap 95 % CI clears zero — LoRA significantly
  worse).
- LoRA's `pooled_ood` AUROC delta vs frozen-probe at **-0.132**
  (CI clears zero — same conclusion via AUROC).
- LoRA's `jbb_behaviors` AUPRC delta vs frozen-probe at **-0.016**
  (CI clears zero — LoRA worse on the in-distribution-shape
  slice too).
- Frozen-probe's `pooled_ood` AUPRC at 0.364 [0.354, 0.375] —
  the highest in the slate but still below the `pooled_ood`
  positive prevalence baseline of 0.374 (random-predictor
  AUPRC equals positive prevalence).

The interpretation: **fine-tuning the head onto the LODO
direct-injection training pool was actively HURTING OOD
generalization** relative to leaving the pretrained ModernBERT-base
embeddings intact. The frozen-probe rung — which adapts NOTHING
from the LODO training pool except a 2-class classification head —
is the strongest rung on the OOD slate.

Full-FT extends the same fine-tuning mechanism that LoRA had just
shown to be net-harmful: where LoRA trains ~1.5M parameters
(adapter modules + classification head), full-FT trains ~149M
parameters (full backbone + adapter + head). On the same training
pool, full-FT is a *larger version* of the same mechanism.

Expected marginal benefit of full-FT-OOD over LoRA-OOD: **low**.
The natural prior is that more parameters fine-tuned on a training
pool that is hurting OOD generalization will hurt OOD generalization
*more*, not *less*. A theoretical upside argument exists (full-FT
might learn a representation that resists the overfitting LoRA
shows) but the prior weight is small relative to the evidence
LoRA already produced.

### Operational facts (trigger, not reason)

- **Phase 2**: full-FT trained for LODO per ADR-019 plan
  (`evals/predictions/full-ft__fold*__seed*__*.parquet` — 24 LODO
  prediction parquets; the 3-rung LODO ladder narrative survives).
- **Phase 5 X11**: full-FT OOD inference re-fire attempted.
  Configured per the runpod-rsync-everything-before-delete memory
  rule (cleanup_intermediate_checkpoints set to false so OOD
  inference could load the trained checkpoints from
  /workspace MooseFS-backed storage).
- **X11 crash**: trainer crashed mid-training when
  `shutil.copytree` of the 598 MB `optimizer.pt` to /workspace
  returned `[Errno 5] Input/output error` (FUSE EIO; matches the
  uv#17801 + MooseFS#380 upstream issues we'd already documented
  in `decisions/upstream_issues.md`).
- **Post-crash decision point**: re-fire vs drop.
  - Re-fire cost: ~6-12 hours wall on A100 80GB (Low stock per
    ADR-049) + ~$5-12 GPU spend + repeat-FUSE-risk + operator
    approval gates per ADR-020 cost cap.
  - Drop cost: 0; full-FT LODO predictions already saved from
    Phase 2; OOD comparison narrative ships as 5-rung slate
    (frozen-probe + LoRA + tfidf-lr + ProtectAI v1 + v2) — see
    ADR-050 R1.
- **Decision (locked at the post-crash point, 2026-05-18)**: drop.
  Reason = methodological (LoRA evidence above). FUSE crash =
  proximate trigger.

### Retrospective self-awareness on full-FT LODO investment

With:

- Data-set sizes used: ~4.7K positives + ~17K benigns post-dedup
  (per `WRITEUP/data-decisions.md` §3.1 + §3.2).
- No augmentation (no paraphrase generation, no back-translation,
  no character-noise injection per `WRITEUP/limitations-and-future-work.md`
  §9.3).
- LoRA paired-bootstrap CI evidence that further fine-tuning on
  this pool hurts OOD.

The rung-ladder + CI inspection now suggests the full-FT LODO
investment itself was likely **not load-bearing** for the
characterisation conclusions of this submission. The frozen-probe
+ LoRA pair already produces the headline finding (pretrained
backbone carries the OOD budget; fine-tuning consumes it).
Full-FT LODO predictions are retained (they exist; dropping them
would lose evidence) but the v1.1.x scope might revisit *whether
to run full-FT at all* on a pool this size.

A v1.1.x iteration with:

- A materially larger training pool (e.g., cross-source augmentation
  bringing in indirect / agentic / jailbreak-style examples), AND
- An augmentation strategy that addresses the cross-family
  generalization gap surfaced in this submission,

…would justify revisiting full-FT — the additional parameter
budget might start to pay off when the training pool no longer
biases the gradient against the OOD slices it'll be evaluated on.

## Consequences

- **Governance**: ADR-050 frontmatter gains `superseded_by:
  [ADR-052]` on the Revision 2 axis only. Revision 1 (LLM-judge
  cost drop) is unchanged. `vendor_black_box` tier still carries
  0 rungs.
- **Reviewer-facing**: WRITEUP §8.1 full-FT bullet rewritten to
  lead with methodological reasoning. WRITEUP/model-rungs.md §4.3
  full-FT Note paragraph re-anchored. README §Headline
  characterisation does not surface ADR-052 directly — the headline
  numbers are unchanged.
- **Implementation**: zero code or methodology changes ship with
  ADR-052. It is governance-only.
- **Audit-trail**: SUBMISSION_AUDIT.md regenerates via
  `scripts/regenerate_audit.py` with ADR-052 included.

## Linked ADRs

- **Superseded (narrow, Revision 2 axis only)**: ADR-050
  (full-FT OOD drop axis; Revision 1 LLM-judge drop axis
  unchanged).
- **Referenced**: ADR-019 (transformer training recipe; original
  full-FT plan), ADR-022 (paired-bootstrap apparatus; produced the
  LoRA vs frozen-probe delta evidence), ADR-051 (v1.0.x
  carryforward of T0 + invariant scaffolds; sibling governance
  patch).

## Transcript

Decisions surfaced during the 2026-05-18 post-v1.0.2 narrative-
import session: user's cover-letter draft (draft.md) framed
full-FT as a methodological judgment; the framing was traced
against ADR-050 R2 (operational forced-drop) + the actual paired-
bootstrap evidence (LoRA -0.071 AUPRC vs frozen-probe). 4-Q
AskUserQuestion batch user-locked the methodological-load-bearing-
with-crash-as-trigger framing. No transcript file required — the
conversation history + commit-message bodies are the audit trail.
