---
adr_id: 017
slug: trained-rung-slate-expansion
title: Trained-rung-slate expansion — TF-IDF plus LR classical floor and frozen-probe dual role
date: 2026-05-15
status: Accepted
claim_id: CLAIM-017
claim: Phase 0-03 expands the trained-rung slate from the three-condition ModernBERT-base lineup locked by ADR-015 to a four-rung architecture by prepending a classical-NLP floor rung — TF-IDF plus Logistic Regression — that restores the SPEC_GREENFIELD §2 documented common-pattern default (linear floor then frozen-features probe then off-the-shelf classifier then adapter-fine-tuned transformer) that ADR-007 originally deviated from. The classical floor rung uses sklearn TfidfVectorizer with combined word 1-2-grams capped at 15000 features and char 3-5-grams capped at 15000 features (FeatureUnion stacked sparse matrix), feeding sklearn LogisticRegression with solver=liblinear plus C=1.0 plus class_weight=balanced plus max_iter=1000 — fit-to-convergence with sklearn default tolerance, no epoch concept. The frozen-probe role (ledger row 332) is locked as both candidate detector (appears in headline table alongside LoRA and full-FT with same metrics and same statistical machinery) and diagnostic anchor (the methodology spoke uses the lift-delta chain TF-IDF+LR then frozen-probe then LoRA then full-FT as a three-step capability decomposition narrative — pretrained transformer features beat classical features, adapter tuning adds something, full backbone fine-tuning adds something beyond adapters). The expansion is methodologically additive — it does not supersede ADR-015 because ADR-015 locked the ModernBERT-base single-backbone architecture for the transformer slate (still valid) — the classical-NLP rung occupies a separate spec axis (different feature space, different library stack — sklearn versus HF). Training-time scope (ledger row 331) is formally locked at frozen-probe plus LoRA plus full-FT (the three conditions enumerated by ADR-015 plus the classical-floor addition) — uniform across all four trained rungs for clean cross-rung lift attribution.
source: SPEC_GREENFIELD.md §2 Model ledger rows 331 + 332 + Phase 0-03 walk Q1 + Q1b
acceptance_criterion: SPEC_GREENFIELD ledger row 331 carries locked-to-frozen-probe-plus-LoRA-plus-full-FT (see ADR-017 complements ADR-015) status; ledger row 332 carries locked-to-both-candidate-detector-plus-diagnostic-anchor (see ADR-017) status; SPEC_SHEET §4 model recipe gains new §4.1 (Classical floor rung — TF-IDF plus LR specification) before the existing transformer-rung sections; SPEC_SHEET §4 enumerates the trained-rung slate as four rungs (TF-IDF+LR plus ModernBERT-base across frozen-probe plus LoRA plus full-FT); assumptions.md A-001 updated to reflect run count of 48 (four trained rungs times three seeds times four LODO folds) instead of 36 with the fallback ladder still applicable to the transformer rungs; tests/test_invariants.py contains skip-marked stub test_classical_floor_rung_present asserting the TF-IDF+LR rung is in the trained-rung config enumeration with sklearn TfidfVectorizer plus LogisticRegression(class_weight=balanced) plus combined word-1-2-grams plus char-3-5-grams plus per-vectorizer max_features 15000; tests/test_invariants.py existing stub test_trained_backbone_modernbert_only_invariant is reframed to assert trained transformer rungs (not all trained rungs) contain exactly ModernBERT-base across three conditions (carve out the classical floor rung); WRITEUP methodology spoke contains a dedicated lift-delta-chain subsection narrating the three-step capability decomposition (TF-IDF+LR then frozen-probe quantifies pretrained-transformer-feature contribution, frozen-probe then LoRA quantifies adapter-tuning contribution, LoRA then full-FT quantifies full-backbone-FT contribution).
closing_commit: cfa7559
supersedes:
references:
  - https://arxiv.org/abs/1607.01759
  - https://arxiv.org/abs/2311.16119
  - https://arxiv.org/abs/1908.10084
  - https://arxiv.org/abs/1905.05950
  - https://arxiv.org/abs/2106.09685
  - https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html
  - https://scikit-learn.org/stable/modules/generated/sklearn.utils.class_weight.compute_class_weight.html
  - decisions/ADR-015-rung-architecture-refinement.md
  - decisions/ADR-007-rung-architecture-and-reference-scorers.md
  - SPEC_GREENFIELD.md §2 line 121 common pattern
transcript: transcripts/2026-05-15__phase-0-03__model-scope.md
---

# ADR-017: Trained-rung-slate expansion — TF-IDF plus LR classical floor and frozen-probe dual role

## Status

Accepted (2026-05-15). Complementary to ADR-015 (does not supersede — ADR-015's single-backbone-for-transformer-slate claim remains valid).

## Context

ADR-007 originally locked a six-trained-rung architecture (two backbones times three conditions) and skipped the SPEC_GREENFIELD §2 documented common-pattern "linear floor (TF-IDF plus LR)" entry. ADR-015 superseded ADR-007 by narrowing the transformer slate to a single backbone (ModernBERT-base across three conditions) to eliminate the per-backbone truncation confound on the indirect-injection slice. Neither ADR included the classical-NLP floor that SPEC §2 line 121 lists as the first rung of the common ladder pattern.

The Phase 0-03 walk surfaced that the rung-ladder framework in SPEC §2 was originally designed to enumerate four capability layers — linear features alone, pretrained features alone, adapter-tuned features, fully-fine-tuned features — each step's lift attributing to a specific capability contribution. Without the TF-IDF+LR floor, the architecture has no comparison point for "what classical NLP achieves" and the methodology spoke cannot answer "how much benefit does any level of transformer training give over classical features?"

Brandon's Phase 0-03 Q1 framing made this explicit — the frozen-probe was intended to be both candidate detector and diagnostic anchor (Option C), and the classical-NLP floor was specifically requested as a baseline rung to anchor the lift-delta narrative.

Adding the classical-NLP floor is spec-aligned (restores the SPEC §2 common pattern), methodologically additive (does not change ADR-015's transformer-architecture claims), and cheap (sklearn CPU compute for the TF-IDF+LR rung is approximately one to two dollars added on top of the existing GPU budget).

## Decision

### Trained-rung slate (four rungs)

| Rung | Model | Stack | Capability layer |
|---|---|---|---|
| 0 | TF-IDF + LR | sklearn | classical NLP — bag-of-features |
| 1 | ModernBERT-base, frozen-probe | HF (frozen body + linear head) | pretrained transformer features alone |
| 2 | ModernBERT-base, LoRA | HF + PEFT | adapter fine-tuning |
| 3 | ModernBERT-base, full-FT | HF Trainer | full backbone fine-tuning |

### Classical floor rung specification

- TfidfVectorizer (FeatureUnion of two): word 1-2-grams with max_features 15000 plus char 3-5-grams with max_features 15000 — combined sparse matrix dimension up to 30000 features
- Common vectorizer settings — sublinear_tf=True, lowercase=True, strip_accents=unicode
- LogisticRegression — solver=liblinear, C=1.0, class_weight=balanced, max_iter=1000, random_state per ADR-006 seed slate (42, 1337, 2025)
- Training — fit-to-convergence with sklearn default tolerance, no epoch concept; one fit per LODO fold per seed
- Inference — predict_proba on held-out positive source plus benign sample; per-row predictions persisted to evals/predictions/tfidf-lr__fold<F>__seed<S>.parquet (no epoch suffix since no epoch concept)

### Frozen-probe role lock (ledger row 332)

Both. The frozen-probe is evaluated as a detection rung in the headline table (same AUPRC plus AUROC plus recall@FPR plus ECE columns as LoRA and full-FT) AND serves as the linear-probe baseline anchor in the methodology spoke for the lift-delta decomposition. A one-paragraph framing note in WRITEUP/methodology.md handles the dual interpretation explicitly.

### Training-time scope lock (ledger row 331)

Frozen-probe plus LoRA plus full-FT. The three conditions enumerated by ADR-015 are formally locked at the ledger-row level (the row previously read open even though ADR-015's body enumerated the three conditions). This is bookkeeping that aligns the ledger with ADR-015's claim.

### Lift-delta-chain methodology spoke section

The methodology spoke gains a dedicated subsection narrating the three-step capability decomposition — TF-IDF+LR then frozen-probe delta quantifies pretrained-transformer-feature contribution; frozen-probe then LoRA delta quantifies adapter-tuning contribution; LoRA then full-FT delta quantifies full-backbone-FT contribution. Each delta is reported with bootstrap CI per ADR-006 plus the paired-bootstrap-difference methodology from eval-toolkit.

## Consequences

### Positive

- Restores the SPEC §2 common-pattern default that ADR-007 originally omitted; the architecture is now spec-aligned
- Adds the only fully verified-disjoint reference point (TF-IDF+LR trained on our LODO splits by construction; no possibility of pretrain contamination) — anchors the contamination-stratified comparison structure that ADR-018 codifies
- The lift-delta chain becomes a designed methodology contribution rather than a post-hoc observation
- Cheap — adds 12 sklearn CPU runs at near-zero cost (under five dollars total impact on the budget envelope)
- The frozen-probe dual role preserves both headline-table presence and diagnostic-anchor framing without adding compute

### Negative

- Increases trained-run count from 36 to 48 (four rungs times three seeds times four LODO folds); the increase is dominated by 12 sklearn CPU runs at near-zero compute cost
- The writeup spoke gains a dual-framing paragraph for the frozen-probe; modest narrative complexity
- The tests/test_invariants.py existing test_trained_backbone_modernbert_only_invariant requires reframing — the literal claim "trained rung slate contains exactly ModernBERT-base across three conditions" is now incorrect because the trained slate also contains TF-IDF+LR; the reframed invariant asserts "trained transformer rungs contain exactly ModernBERT-base across three conditions" (carves out the classical-NLP rung from the no-DeBERTa-fallback assertion)

### Phase 1 deliverables

- src/rungs/tfidf_lr.py — sklearn pipeline implementing the locked recipe with seed handling
- evals/predictions/tfidf-lr__fold<F>__seed<S>.parquet — per-row predictions for each of the 12 sklearn runs
- WRITEUP/methodology.md — lift-delta-chain subsection drafted

## Alternatives considered

- **Keep the 3-rung ADR-015 architecture without the classical floor** — rejected because the architecture has no comparison point for "what classical NLP achieves" and cannot answer the lift question "how much benefit does any level of transformer training give over classical features?" Brandon explicitly surfaced this gap in Q1 with the intent that the frozen-probe serve as both candidate detector and diagnostic anchor.
- **Use HashingVectorizer instead of TfidfVectorizer** — rejected for prototype because TfidfVectorizer is more interpretable (coefficients per feature support afterword feature-attribution analyses) and 30000-feature dimension is manageable. HashingVectorizer deferred to afterword for very-long-document handling.
- **Char-only n-grams or word-only n-grams** — rejected because combined word-1-2-grams plus char-3-5-grams capture both instruction-style patterns ("ignore previous instructions" type) and URL-encoded plus base64 plus delimiter attack patterns; either alone underperforms.
- **Grid-search C and class_weight on val** — rejected because the SPEC §2 hyperparameter-immutability rule prohibits val-set tuning; we use literature defaults.
- **Calibrated LR via CalibratedClassifierCV** — rejected for prototype because sklearn LR's predict_proba is reasonably calibrated for binary classification at our scale; deferred to afterword as a calibration-comparison extension.

## References

See frontmatter references list. Primary anchors — SPEC_GREENFIELD §2 line 121 common pattern; LoRA paper §5.4 ablations (Hu et al. 2021); BERT-rediscovers-pipeline (Tenney et al. 2019); Sentence-BERT (Reimers and Gurevych 2019); fastText char n-grams (Joulin et al. 2017); HackAPrompt 2023 baseline (Schulhoff et al. 2023); ADR-015 transformer-slate single-backbone claim; ADR-007 historical record.
