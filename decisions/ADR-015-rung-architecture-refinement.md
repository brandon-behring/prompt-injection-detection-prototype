---
adr_id: 015
slug: rung-architecture-refinement
title: Rung architecture refinement — ModernBERT-base only trained slate, supersedes ADR-007
date: 2026-05-15
status: Accepted
claim_id: CLAIM-015
claim: The trained-rung slate is narrowed from the original two-backbones-by-three-conditions matrix (six trained rungs, DeBERTa-v3 plus ModernBERT each at frozen-probe, LoRA, full-FT) to a single-backbone-by-three-conditions slate (three trained rungs, ModernBERT-base at frozen-probe, LoRA, full-FT) because the per-backbone native context-window asymmetry from ADR-014 Q3 (DeBERTa-v3 capped at 512 tokens vs ModernBERT capped at 8192) produces an irreducible truncation confound on the indirect-injection zero-shot OOD slice — the cross-backbone delta-AUROC on BIPIA would be partly architecture and partly chunked-vs-native truncation aggregation, with no decomposition possible inside the project's compute and calendar budget. Reference rungs from ADR-007 are preserved unchanged — OpenAI LLM-judge plus Anthropic LLM-judge plus Lakera Guard plus ProtectAI deberta-v3-base-prompt-injection — each called at its published native configuration including its native truncation policy. Multi-seed protocol at the ADR-006 floor of three seeds yields three trained rungs times three seeds times five LODO folds equals 45 training runs per evaluation. The fallback ladder is updated to 1x3 then 1x2 then 1x1; the original 2x3 then 2x2 step is no longer applicable. Backbone choice is hard-locked to ModernBERT-base; a silent fallback to DeBERTa-v3-base is explicitly prohibited — any catastrophic operational issue (checkpoint inaccessible, library compatibility break under uv pin resolution) requires a superseding ADR rather than a silent swap.
source: SPEC_GREENFIELD.md §2 Model row 330 (Backbone choice) + ADR-014 Q3/Q4 walk
acceptance_criterion: ADR-007 carries status Superseded with superseded_by 015; SPEC_GREENFIELD ledger row 330 reads locked-to-ModernBERT-base (see ADR-015); SPEC_SHEET context paragraph and §4 model recipe reflect the 1x3 trained slate with three trained rungs plus four reference rungs; assumptions.md A-002 budget revised; tests/test_invariants.py has skip-marked stub test_trained_backbone_modernbert_only_invariant asserting the trained-rung slate contains exactly ModernBERT-base across three conditions; the Phase 2 training pipeline produces three trained rungs times three seeds times five LODO folds equals 45 per-row prediction parquet files at evals/predictions/.
closing_commit: 727767c
supersedes: "007"
superseded_by:
  - "018"  # back-link added per ADR-077 frontmatter-backfill discipline; ADR-018 partially supersedes ADR-015 reference-slate enumeration
references:
  - https://arxiv.org/abs/2412.13663
  - https://arxiv.org/abs/2111.09543
  - https://arxiv.org/abs/2106.09685
  - https://huggingface.co/docs/peft
  - https://arxiv.org/abs/2306.05685
  - https://doi.org/10.1177/001316446002000104
transcript: transcripts/2026-05-15__phase-0-01__threat-model.md
---

# ADR-015: Rung architecture refinement — ModernBERT-base only trained slate, supersedes ADR-007

## Status

Accepted (2026-05-15). Supersedes ADR-007.

## Context

ADR-007 locked a six-trained-rung architecture (DeBERTa-v3 plus ModernBERT, each at frozen-probe, LoRA, full-FT) plus reference rungs (LLM-judges plus Lakera plus ProtectAI). The Phase 0-01 walk surfaced a load-bearing finding that ADR-007 had not anticipated — the per-backbone native context-window asymmetry produces an irreducible truncation confound on the indirect-injection zero-shot OOD slice.

Concretely — DeBERTa-v3 has a 512-token hardcoded context cap from its relative-position attention scheme; ModernBERT has an 8192-token native context from rotary positional embeddings. BIPIA (Yi et al. 2023, KDD 2025) — the dossier-vetted indirect-injection benchmark — has samples with median 1-3K tokens and 95th percentile around 4K-plus. Under the original 2-backbone framing, evaluating DeBERTa-v3 on BIPIA requires adaptive chunked scoring (3-8 chunks per sample at stride 256, max-pool aggregation per ADR-014 Q4) while evaluating ModernBERT on BIPIA fits 95-percent-plus of samples in a single native pass. The cross-backbone delta-AUROC on BIPIA would therefore be partly architecture-driven and partly truncation-aggregation-driven, with no clean decomposition possible inside the submission's compute and calendar budget. A reviewer reading the cross-backbone delta would not be able to attribute the difference cleanly to detector capacity versus context-window-handling.

The mandatory chunked-vs-head ablation in ADR-014 quantifies the confound but does not eliminate it. Per ADR-005 Principle 2 (honest evaluation preferred even when models look worse), the methodology-first move is to eliminate the confound at the rung-architecture level rather than report a confounded headline metric with an explanatory caveat. This means narrowing the trained-rung slate to a single backbone whose native context covers the indirect-injection eval slice — ModernBERT-base.

The submission's contribution shifts from "two-backbone-by-three-condition matrix with cross-backbone delta" to "three-condition comparison on a modern long-context backbone plus zero-shot transfer to indirect" — a different headline narrative, but a cleaner methodology story. ProtectAI's deberta-v3-base-prompt-injection remains in the reference-rung slate as the canonical published deberta-v3 baseline, so the submission still engages with the deberta-v3 landscape — just as a reference rung run at its published native config rather than as a co-trained backbone in the headline grid.

## Decision

### Trained-rung slate (3 rungs)

- ModernBERT-base, frozen-probe (transformer body frozen; linear head trained on pooled CLS or mean-pooled embeddings)
- ModernBERT-base, LoRA (PEFT-LoRA adapters; full backbone frozen; specific hyperparams r, alpha, dropout, target modules deferred to Phase 0-03 ledger rows 335-337)
- ModernBERT-base, full-FT (full backbone parameters trainable)

Library stack unchanged from ADR-007 — HuggingFace Transformers plus PEFT for LoRA plus sentence-transformers for any pooling helpers; PyTorch backbone; dependencies pinned via uv.lock per ADR-007's library lock. Specific LoRA hyperparameters remain Phase 0-03 deliverables.

### Reference-rung slate (4 rungs) — preserved from ADR-007 unchanged

- LLM-judge: one OpenAI model, specific ID deferred to Phase 0-03 (likely GPT-4o or successor); temperature equals zero (deterministic); one call per eval row; prompt template versioned in repo
- LLM-judge: one Anthropic model, specific ID deferred to Phase 0-03 (likely Claude Sonnet 4 or successor); temperature equals zero; one call per eval row; prompt template versioned in repo
- Lakera Guard: API-based reference rung; called at whatever the API does (no preprocessing override on our side)
- ProtectAI deberta-v3-base-prompt-injection: open-weights canonical baseline; run at its published native config including its native head-truncation at 512 (no preprocessing override on our side)

The reference-rung inference policy is "as-published native config" — per ADR-014 Q3 reference-rung-asymmetry clarification, we measure each reference rung as it would actually be deployed, not as it would behave under our truncation policy applied uniformly. ProtectAI's BIPIA scores will reflect the head-truncation false-negative bias at 512; this is the point of testing the published baseline as-deployed and should be surfaced explicitly in the writeup.

### Multi-seed protocol

Three seeds is the ADR-006 floor; preserved. Three trained rungs times three seeds times five LODO folds equals 45 training runs per evaluation cycle. Adaptive escalation to five seeds remains a Phase 4 sensitivity option per ADR-006's "if budget permits" clause, but is not pre-committed.

### Cohen's kappa methodology — preserved from ADR-007

Pairwise Cohen's kappa across all seven rungs (3 trained plus 4 reference) — 21 pair-comparisons. Bootstrap CIs on each kappa (10K iters per ADR-006 protocol). Rendered as a heatmap in `WRITEUP/reference-scorer-audit.md`. Landis-Koch interpretive bands mentioned once for orientation; not used as headline framing.

### Updated fallback ladder

The ADR-001 fallback ladder is updated from `2x3 → 2x2 → 1x2 → 1x1` to `1x3 (current) → 1x2 → 1x1`. The original `2x3 → 2x2` step is no longer applicable because the 2-backbone framing is voided. Successive fallback steps drop one training condition each — first full-FT (most expensive), then LoRA, leaving frozen-probe as the 1x1 floor.

### Hard-lock — silent backbone fallback prohibited

If catastrophic operational issues arise with ModernBERT-base (checkpoint unavailable on HF Hub, library compatibility break under uv pin resolution, RunPod incompatibility), the response is a superseding ADR-016 (or later number) that explicitly re-walks the backbone choice. A silent swap to DeBERTa-v3-base is prohibited — the swap would reintroduce the per-backbone-truncation confound that this ADR exists to eliminate, voiding the methodology contribution.

### Reference-rung as-published policy

Reference rungs are not subject to our adaptive chunked scoring policy. ProtectAI runs at native 512 head-truncation; Lakera runs at whatever its API does; LLM-judges receive the full sample (their 128K-plus native contexts cover everything). The asymmetry is the point — apples-to-apples comparison against deployed baselines requires testing them as they exist, not as preprocessed by us.

## Consequences

**Positive:**

- Eliminates the per-backbone-truncation confound on the indirect-injection zero-shot OOD slice — cross-rung deltas are now interpretable as condition effects (frozen vs LoRA vs full-FT) rather than entangled with truncation policy.
- Halves training compute relative to ADR-007 (3 trained rungs versus 6) — fits the revised A-002 budget envelope ($25-125 total) comfortably.
- ModernBERT-base aligns with deployment realism — 8K context covers the indirect-injection scenario (RAG chunks, emails, retrieved documents) natively; the submission tests a backbone whose context window matches the operational threat surface.
- Reference-rung slate unchanged preserves the engagement set from ADR-012 — Lakera and ProtectAI as compare-against baselines; ProtectAI's deberta-v3 stays in the analysis as the canonical published baseline, just not as a co-trained rung.
- ProtectAI as-published-config reference rung produces an honest "deployed baseline performance under realistic input handling" comparison — reveals how much the head-truncation-at-512 limitation costs on indirect-injection-detection in production.
- Cohen's kappa methodology from ADR-007 scales cleanly — 7 rungs produce 21 pair-comparisons (smaller than the original 8 rungs producing 28 pairs); kappa heatmap remains readable.
- Soft-signal alignment from ADR-012 is strengthened — methodology-over-metrics (ADR-005 Principle 1) gains: clean rung-comparison versus confounded cross-backbone; honesty-about-limitations (Principle 3) gains: confound eliminated rather than ablation-quantified-but-still-present; time-budgeted-craftsmanship gains: halved compute frees budget headroom.
- Multi-seed budget headroom — at 45 runs versus the original 90 runs from ADR-007, the freed compute supports either Phase 4 sensitivity rerun at 5 seeds on one rung or tighter LODO-fold-count exploration as a secondary methodology axis.

**Negative / cost:**

- ADR-007's "two-backbone matrix" framing is voided — the submission narrative shifts from "backbone effect plus condition effect" to "condition effect on a modern backbone". Less methodology-axis-coverage, but cleaner per-axis decomposition.
- Reviewer may ask "why only ModernBERT?" — answer is the chained ADR-014 Q3/Q4 walk plus this ADR-015 supersession; the methodology trail is auditable but requires the reviewer to read the supersession.
- DeBERTa-v3-base is dropped from the trained slate; researchers expecting the field-default deberta-v3 baseline as a trained rung will find it only as a reference rung — must be surfaced explicitly in the writeup's reference-rung-audit narrative.
- Hard-lock prohibits silent fallback; if ModernBERT-base catastrophic issue arises, the project must write ADR-016 rather than silently swapping backbones — adds ADR-write overhead in the worst case but preserves methodology integrity.
- Assumption A-002 (API budget) revised downward to $25-125 total — verification at end of Phase 3 against cumulative cost still required.

**Neutral:**

- ADR-006 statistical apparatus unchanged — paired bootstrap, BCa marginal CIs, MDE on every CI, 3-pinpoint Recall@FPR, 4-metric headline table all apply identically.
- ADR-008 data scope unchanged — same training-positives slate, same OOD eval slate, same dedup and split methodology.
- ADR-009 process mandates unchanged — two-tier reproducibility (laptop smoke plus GPU canonical), marker-based testing, pre-commit only, jupytext-paired notebooks, compute disclosure.
- ADR-010 Bounds 1-6 preserved — Bound 4 (sub-1B parameters) is more tightly satisfied (ModernBERT-base is approximately 149M); Bound 3 (per-backbone caps) effectively resolves to "ModernBERT 8K natively, reference rungs at their published caps".
- ADR-011 methodology guarantees unchanged — all eight guarantees apply identically; Guarantee 4 (Cohen's kappa for any hand-labeling audit) carries forward.
- ADR-012 external-artifact engagement set unchanged — Lakera and ProtectAI still in the reference-rung slate; BIPIA still in OOD slate; soft-signal alignment table from ADR-012 holds.
- ADR-013 pre-teardown persistence checklist applies with fewer artifacts to checkpoint (3 trained rungs versus 6); simpler operational profile.

## Alternatives Considered

- **Keep both backbones (ADR-007 as written)**: 6 trained rungs; cross-backbone delta reported with explicit truncation-confound framing; mandatory ablation quantifies. Rejected because the confound on the indirect-injection slice is irreducible — the ablation can quantify but cannot decompose; the methodology-first move is to eliminate the confound at the rung-architecture level rather than report a confounded headline metric with an explanatory caveat.
- **Keep both backbones; relegate indirect to spoke-only OOD probe (Path C from the Q4 walk)**: 6 trained rungs; headline on direct slices only where no truncation confound exists; indirect reported in spoke as zero-shot probe without cross-backbone delta. Rejected because it walks back ADR-014 Q1's B1 framing where indirect zero-shot transfer is a load-bearing measurement; still pays 2x compute without the cross-backbone indirect comparison being headline-worthy.
- **DeBERTa-v3-base only (drop ModernBERT)**: Smaller backbone; field-default for deberta-v3-prompt-injection reproductions; cheaper compute. Rejected because DeBERTa-v3's 512-token cap mismatches the indirect-injection-detection deployment scenario — every BIPIA sample requires chunking; the methodology story would be "deploying an undersized-context backbone on long-input indirect-injection" which is not the methodology contribution we want to make.
- **ModernBERT-large instead of ModernBERT-base**: Larger model; stronger absolute metrics; same 8K context. Rejected for this iteration because the Phase 0-03 preview leaning is all-base for compute discipline (matches A-002 budget cleanly; supports denser multi-seed); ModernBERT-large remains a future-work extension axis surfaced in `WRITEUP/limitations-and-future-work.md`.
- **Add a third condition to the trained slate (e.g., LoRA with two hyperparameter configurations)**: Broader condition coverage. Rejected because Phase 0-03 has not walked the LoRA hyperparameter specifics yet; expanding condition coverage premature.
- **Five seeds (escalate above ADR-006 floor)**: Tighter bootstrap CIs; better MDE. Rejected as the primary protocol because three seeds is the ADR-006 floor and the Path B compute headroom is better spent on Phase 4 sensitivity rerun at 5 seeds on one rung (a methodology-validation check) than on uniform 5-seed protocol (a precision-only gain).
- **Soft fallback to DeBERTa-v3-base if ModernBERT-base unavailable**: Operationally simpler. Rejected because a backbone swap is a substantive methodology change — silent fallback would reintroduce the per-backbone-truncation confound that this ADR exists to eliminate. The supersession requirement is the discipline floor.

## References

- ModernBERT (Warner et al. 2024) — https://arxiv.org/abs/2412.13663
- DeBERTa-v3 (He et al. 2023) — https://arxiv.org/abs/2111.09543
- LoRA (Hu et al. 2021) — https://arxiv.org/abs/2106.09685
- HF PEFT documentation — https://huggingface.co/docs/peft
- LLM-as-judge (Zheng et al. 2023) — https://arxiv.org/abs/2306.05685
- Cohen 1960 — Coefficient of Agreement for Nominal Scales — https://doi.org/10.1177/001316446002000104
- ADR-007 (superseded by this ADR)
- ADR-001 (fallback ladder updated to `1x3 → 1x2 → 1x1`)
- ADR-005 (Principle 1 methodology over metrics; Principle 2 honest evaluation preferred — direct rationale for the supersession)
- ADR-006 (3-seed floor preserved; paired bootstrap protocol unchanged)
- ADR-010 (Bound 3 per-backbone caps now resolves to single-backbone-native; Bound 4 sub-1B more tightly satisfied)
- ADR-012 (Lakera plus ProtectAI engagement preserved; soft-signal alignment strengthened)
- ADR-013 (pre-teardown persistence simpler with fewer rungs)
- ADR-014 (threat-model bundle that surfaced the confound forcing this supersession)

## Transcript

See `transcripts/2026-05-15__phase-0-01__threat-model.md` for the conversation that led to this decision.
