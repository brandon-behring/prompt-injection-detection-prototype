---
adr_id: 014
slug: threat-model-bundle
title: Threat-model bundle — attack-class scope, language, length cap, truncation policy
date: 2026-05-15
status: Accepted
claim_id: CLAIM-014
claim: Phase 0-01 locks four §0 Threat decisions as a single bundle — (Q1) attack-class scope is direct injection as primary trained scope plus indirect injection as zero-shot OOD probe via BIPIA (no labeled indirect training data exists in the dossier-vetted slate; the asymmetry is intentional and surfaced as a methodology finding rather than papered over); (Q2) language scope is English-only (reaffirms ADR-010 Bound 1; every dossier-vetted eval slice is English; multilingual extension would require both data and researcher-auditability that this submission lacks); (Q3) length cap is per-backbone native (refines ADR-010 Bound 3; under ADR-015's single-backbone refinement this resolves to ModernBERT 8192 for the trained rung, with reference rungs running at their published native caps — ProtectAI deberta-v3 at 512, Lakera as-API, LLM-judges full-sample); (Q4) truncation policy is adaptive chunked scoring with max-pool aggregation and stride equal to cap divided by two at evaluation time, plus head-truncation at training time (HF default since training-positives are short and the cap rarely bites at train time); a chunked-vs-head ablation on the BIPIA slice is mandatory and lives in WRITEUP/truncation-ablation.md as a methodology-quantification artifact rather than a hidden detail.
source: SPEC_GREENFIELD.md §0 Threat rows 319-322 + Phase 0-01 walk
acceptance_criterion: SPEC_GREENFIELD ledger rows 319/320/321/322 carry locked-to-X (see ADR-014) status; the SPEC_SHEET §3.3 truncation slot carries the bracketed LOCKED marker naming adaptive-chunked-max-pool (per ADR-014); tests/test_invariants.py contains skip-marked stubs test_trained_backbone_modernbert_only_invariant and test_truncation_policy_adaptive_chunked_max_pool; the Phase 1 length-histogram audit produces evals/length_histograms.{train,ood}.json with per-slice quantiles on the ModernBERT-base tokenizer; if BIPIA samples with token-length above 8192 exceed 15 percent of the slice, a superseding ADR-016 adjusts the chunk-stride or aggregation policy; the WRITEUP/truncation-ablation.md spoke reports delta-AUROC and delta-Recall-at-FPR-1-percent between adaptive-chunked and head-truncation on the BIPIA slice.
closing_commit:
references:
  - https://arxiv.org/abs/2302.12173
  - https://arxiv.org/abs/2310.12815
  - https://arxiv.org/abs/2312.14197
  - https://arxiv.org/abs/2307.03172
  - https://huggingface.co/docs/transformers/main_classes/tokenizer
  - https://owasp.org/www-project-top-10-for-large-language-model-applications/
  - https://arxiv.org/abs/2412.13663
  - https://arxiv.org/abs/2111.09543
transcript: transcripts/2026-05-15__phase-0-01__threat-model.md
---

# ADR-014: Threat-model bundle — attack-class scope, language, length cap, truncation policy

## Status

Accepted (2026-05-15)

## Context

Phase 0-01 walks four §0 Threat rows (319 attack classes, 320 language, 321 length cap, 322 truncation policy). Three of the four were partially pre-resolved by ADR-010 Bounds 1/2/3, but the formal sub-session lock surfaced load-bearing refinements that ADR-010 had left ambiguous and that the data state forces to disambiguate.

The single most important finding from the walk is that **the dossier-vetted training-positives slate (deepset/prompt-injections + Lakera/gandalf + Lakera/mosscap + HackAPrompt) contains no direct-vs-indirect label** — every training corpus consists of direct user-channel attacks. Indirect-injection samples appear only in the OOD evaluation slate via BIPIA (Yi et al. 2023, KDD 2025) and InjecAgent (Zhan et al. 2024, ACL Findings). This forces ADR-010 Bound 2's "direct + indirect in scope" framing to disambiguate between trained-on-scope (direct only) and evaluation-scope (direct + indirect zero-shot transfer). Conflating the two would be the kind of methodology-laxity that ADR-005 Principle 2 (honest evaluation preferred) explicitly forbids.

The second load-bearing finding is that encoder context-window limits are architectural, not stylistic. DeBERTa-v3's 512-token ceiling is hardcoded via its relative-position attention scheme; ModernBERT's 8192-token native context uses rotary positional embeddings trained at 8K. BIPIA samples (median 1-3K tokens; 95th percentile around 4K-plus) routinely exceed 512 — making the truncation policy load-bearing for indirect-injection detection on a 512-cap backbone. This cascades into the rung-architecture refinement ADR-015 supersedes ADR-007, which eliminates the cross-backbone truncation confound by narrowing the trained-rung slate to ModernBERT-base only.

The walk also re-examined the language-scope question through both a data lens (every dossier-vetted eval slice is English-only — there is no multilingual benchmark of equivalent rigor) and a researcher-auditability lens (this researcher cannot independently audit non-English samples; cross-lingual claims would carry epistemological weakness that the methodology-first framing does not accept).

## Decision

### Q1 — Attack-class scope: direct primary trained + indirect zero-shot OOD probe

Direct injection is the primary trained scope. Indirect injection is included in the evaluation scope as a zero-shot OOD probe via BIPIA — the detector is not trained on any indirect-injection samples. Cross-class transfer performance is reported transparently as zero-shot, not as in-distribution detection. Agentic injection (InjecAgent) remains a stretch OOD probe per ADR-010 Bound 2; optimization-based attacks (GCG, PAIR, TAP) remain out of scope per ADR-010 Bound 6.

This refines ADR-010 Bound 2 (which had said "direct + indirect in scope" without disambiguating trained-on from evaluated-on) — does not supersede it. ADR-010 Bound 2's structured-limitations framing carries forward unchanged.

### Q2 — Language scope: English-only

English-only. Reaffirms ADR-010 Bound 1. All four training-positives corpora, all five OOD slices (NotInject, XSTest, JBB-Behaviors, BIPIA, InjecAgent), and all dossier-vetted benchmarks are English-anchored. Multilingual extension would require (a) parallel multilingual training and eval corpus of at least 5K labeled samples per language with explicit translation-vs-native distinction, (b) native-speaker red-team annotation per target language, (c) per-language attack-taxonomy expertise, (d) cross-lingual transfer methodology to disentangle detector capacity from translation quality and tokenizer fragmentation — none of which this submission's data slate or researcher skill set provides at the methodology-first rigor floor.

### Q3 — Length cap: per-backbone native; effectively 8192 under ADR-015

Per-backbone native cap. Refines ADR-010 Bound 3. Under ADR-015 (rung-architecture refinement; supersedes ADR-007) the trained-rung slate is ModernBERT-base only — so the per-backbone framing resolves to a single native cap of 8192 for the trained rung. Reference rungs run at their published native caps without our preprocessing applied — ProtectAI deberta-v3-base at its native 512 with head-truncation (the as-deployed behavior), Lakera Guard via its API at whatever the API does, LLM-judges (OpenAI and Anthropic models) at their native context windows (>=128K) receiving the full sample. The asymmetry is intentional — we compare against published baselines as they would actually be deployed, not as they would behave under our truncation policy.

### Q4 — Truncation policy: adaptive chunked scoring with max-pool aggregation; stride equal to cap divided by two

At training time, head-truncation is used (HF tokenizer default — `truncation_side="right"`). Training-positives are short (95th percentile estimated under 500 tokens per dossier characterization) so the cap rarely bites at training time.

At evaluation time on all slices, adaptive chunked scoring is the code-path policy. Inputs that fit in the cap pass through as a single chunk (the common case for direct-OOD slices and short BIPIA samples on ModernBERT's 8K cap). Inputs that exceed the cap are split into overlapping chunks of size `cap` with stride `cap // 2` (50 percent overlap so no token sits at a chunk boundary in both chunks — minimizing boundary attacks where an injection payload spans two chunks). Each chunk is scored independently. Per-sample score is the max over chunk scores (max-pool aggregation — matches the adversarial threat model: any successful injection chunk equals attack-succeeded; provides clean AUROC interpretation as a single continuous score per sample).

A mandatory ablation re-runs BIPIA eval with head-truncation throughout and reports delta-AUROC plus delta-Recall-at-FPR-1-percent between the two policies per backbone — quantifies the methodology choice rather than asserting it. The ablation lives in `WRITEUP/truncation-ablation.md` as a load-bearing methodology artifact.

### Phase 1 validation checkpoint

The Phase 1 length-histogram audit produces `evals/length_histograms.{train,ood}.json` with per-slice quantiles computed on the ModernBERT-base tokenizer. If BIPIA samples with token-length above 8192 exceed 15 percent of the slice, the adaptive-chunked policy becomes load-bearing on the headline indirect-injection slice (not just a conditional safeguard), and a superseding ADR-016 adjusts the chunk-stride or aggregation policy (e.g., hierarchical encoding, learned aggregator, or tighter stride). The 15-percent threshold is a 3x tolerance over the qualitative dossier estimate of about 5 percent of BIPIA samples exceeding 8K.

## Consequences

**Positive:**

- Direct primary trained scope plus indirect zero-shot OOD framing is honest about the data state (no labeled indirect training data exists); the asymmetry becomes a methodology finding rather than a hidden compromise.
- English-only scope is grounded in both data state (every eval slice English-anchored) and researcher-auditability (cross-lingual claims would carry second-hand epistemological weakness this submission rejects).
- Per-backbone native cap under ADR-015's single-backbone refinement eliminates the cross-backbone truncation confound that the original ADR-007 2-backbone-with-different-caps framing would have produced — the cross-backbone delta-AUROC would have been irreducibly partly architecture and partly truncation aggregation.
- Adaptive chunked scoring at eval time matches deployment realism — a production detector cannot silently miss attacks because input exceeds the cap.
- Max-pool aggregation matches the adversarial threat model; the per-chunk OR-equivalent semantics align with how attackers actually exploit detectors (any successful chunk equals attack).
- Mandatory chunked-vs-head ablation quantifies the truncation policy rather than asserting it — aligns with ADR-005 Principle 1 (methodology over metrics) and Principle 2 (honest evaluation preferred).
- Reference-rung as-published policy preserves apples-to-apples comparison with deployed baselines (ProtectAI, Lakera) — the submission tests "our ModernBERT detector versus deployed baselines as they exist" rather than "our detector versus baselines modified by our preprocessing".
- Phase 1 validation checkpoint with explicit 15-percent threshold makes the truncation policy's load-bearing-ness empirically verifiable; ADR-016 supersession path is concrete rather than vague.

**Negative / cost:**

- Zero-shot transfer framing for indirect-injection metrics requires explicit "zero-shot OOD" labeling in the headline table — a small but recurring writeup tax in every section that references BIPIA performance.
- Adaptive chunked scoring on inputs above the cap adds inference compute proportional to ceiling-of-((L minus cap) divided by stride) plus one. For ModernBERT at 8K stride 4096 the multiplier is small (most samples fit in 1 chunk; outliers in 2-3 chunks). Manageable.
- Max-pool aggregation inflates the false-positive rate on long benign documents — every chunk gets a chance to false-fire. Reported as a known limitation; mean-pool alternative reported in the spoke as a second-axis ablation if Phase 1 reveals high benign-FPR. Surfaced explicitly in `WRITEUP/limitations-and-future-work.md`.
- Boundary-spanning injection payloads (where the payload straddles a chunk boundary) appear fragmented in both adjacent chunks; 50-percent overlap mitigates but does not eliminate. Documented as a known failure mode.
- ProtectAI deberta-v3 as a reference rung suffers from head-truncation at 512 on BIPIA — its zero-shot indirect scores reflect the truncation bias. This is the point of testing the published baseline as-deployed; should be surfaced explicitly in the writeup so reviewers do not interpret ProtectAI's BIPIA degradation as detector incapability.
- Assumption A-004 added (severity: medium): BIPIA outlier-rate above 8K stays at or below 15 percent of the slice; if invalidated by Phase 1 audit, ADR-016 supersedes the truncation-policy lock.

**Neutral:**

- ADR-010 Bounds 1, 2, 3 are refined (not superseded); the structured-limitations framing they established carries forward into `WRITEUP/limitations-and-future-work.md`.
- The training-time head-truncation policy matches every published deberta-v3 prompt-injection reproduction; no methodology branch at training time.
- Phase 0-02 (data design) still walks the source slate, dedup, splits, ref-scorer audit, and benign subsample ceilings. This ADR fixes the threat-model and truncation policy; data composition specifics are deferred.

## Alternatives Considered

- **Direct-only scope (drop indirect from eval entirely)**: Cleanest train/eval scope symmetry. Rejected because it ignores the operationally-most-relevant threat surface (Greshake 2023); reviewer would ask "did you test indirect?" with no honest answer; would contradict ADR-012's default engagement set listing BIPIA as a "compare against" artifact.
- **Direct plus indirect joint primary scope (claim indirect as in-distribution)**: Inflates the apparent scope. Rejected under ADR-005 Principle 2 (honest evaluation preferred) — calling indirect "primary scope" without indirect training data is methodology-laxity.
- **Synthetic indirect training data via direct-payload-into-benign-doc pasting**: Cheap to generate. Rejected because the synthetic distribution becomes a methodology object — reviewer asks "is your synthetic payload distribution representative?"; bias-risk if generation uses an LLM (the LLM's payload preferences leak into training); risks dishonestly inflating in-distribution indirect AUROC.
- **English plus 1-2 high-resource languages (Spanish or Chinese)**: Broader deployment story. Rejected because no dossier-vetted multilingual OOD benchmark exists at equivalent rigor; researcher cannot independently audit non-English samples; tokenizer-coverage confound would stack on per-backbone-cap confound producing two simultaneous confounds in a 2.5-day submission.
- **Head-truncation throughout eval (no chunking)**: Matches every published deberta-v3 reproduction. Rejected because it systematically misses indirect-injection payloads at adversarial positions in long documents; produces a false-negative bias on the headline indirect slice by construction.
- **Tail-truncation (keep last cap tokens, drop earlier)**: Preserves recency. Rejected because it drops the instruction-channel content at the start (direct attacks) and still drops the middle (indirect payloads at middle positions).
- **Middle-truncation (keep head plus tail, drop middle)**: Lost-in-the-Middle (Liu et al. 2023, NAACL) motivates dropping the middle as the weakest-attention region in generation tasks. Rejected because Liu 2023's finding is for generation; for adversarial detection where the attacker chooses payload position, middle-truncation is exactly the worst policy — Greshake-style payloads sit in middle positions by design.
- **Mean-pool aggregation instead of max-pool**: More conservative on benign-FPR. Rejected as default — does not match the adversarial threat model (any chunk firing equals attack succeeded). Recommended as a second-axis ablation if Phase 1 reveals high benign-FPR on long documents.
- **Learned chunk aggregator (MLP on chunk scores)**: Optimal for the distribution. Rejected because it would require per-chunk labels we do not have; risk of overfitting on small labeled set; methodology-laxity risk if any tuning happens on test.

## References

- Greshake et al. 2023, "Not what you've signed up for" (ACM AISec; canonical indirect threat model) — https://arxiv.org/abs/2302.12173
- Liu et al. 2024, "Formalizing and Benchmarking Prompt Injection Attacks and Defenses" (USENIX Security) — https://arxiv.org/abs/2310.12815
- Yi et al. 2023, BIPIA (KDD 2025; indirect-PI benchmark) — https://arxiv.org/abs/2312.14197
- Liu et al. 2023, "Lost in the Middle" (NAACL 2024) — https://arxiv.org/abs/2307.03172
- HF tokenizer truncation documentation — https://huggingface.co/docs/transformers/main_classes/tokenizer
- OWASP LLM Top 10 (LLM01 = Direct + Indirect Prompt Injection) — https://owasp.org/www-project-top-10-for-large-language-model-applications/
- ModernBERT (Warner et al. 2024) — https://arxiv.org/abs/2412.13663
- DeBERTa-v3 (He et al. 2023) — https://arxiv.org/abs/2111.09543
- `docs/research/attacks_defenses/01_attack_direct.md` through `06_threat_model_survey.md`
- `docs/research/datasets/01_train_positives.md` + `03_ood_eval.md`
- `docs/research/benchmarks/02_benchmark_indirect_agentic.md`
- ADR-005 (Principles 1 and 2 — methodology over metrics; honest evaluation preferred)
- ADR-010 (Bounds 1, 2, 3 — refined by this ADR; structured-limitations framing preserved)
- ADR-015 (rung-architecture refinement — supersedes ADR-007; eliminates cross-backbone truncation confound)
- ADR-011 (methodology guarantees — Guarantees 5 and 6: per-row predictions, threshold on validation only)
- ADR-012 (BIPIA, Lakera, ProtectAI in engagement set — preserved)

## Transcript

See `transcripts/2026-05-15__phase-0-01__threat-model.md` for the conversation that led to this decision.
