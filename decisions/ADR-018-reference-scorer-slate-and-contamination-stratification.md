---
adr_id: 018
slug: reference-scorer-slate-and-contamination-stratification
title: Reference scorer slate and contamination stratification — OpenAI plus Anthropic LLM-judges plus ProtectAI v1 and v2 plus per-axis matched-budget
date: 2026-05-15
status: Accepted
claim_id: CLAIM-018
claim: Phase 0-03 locks the reference-rung slate at four rungs — one OpenAI LLM-judge (gpt-4o-2024-08-06 stable snapshot) plus one Anthropic LLM-judge (claude-sonnet-4-6 with date-suffixed snapshot ID pinned at Phase 1 entry per Anthropic API documentation snapshot suffix convention) plus two ProtectAI off-the-shelf classifiers (deberta-v3-base-prompt-injection v1 plus deberta-v3-base-prompt-injection-v2) — and partially supersedes ADR-015 reference-slate enumeration by dropping Lakera Guard (ToS verification overhead plus partial-disclosure complexity unacceptable for prototype scope, named in afterword extension) and adding ProtectAI v1 alongside v2 (provides internal v1-to-v2 lift comparison parallel to the trained-rung-lift narrative — what off-the-shelf classifier updates buy you). LLM-judge calls use temperature equals zero (deterministic; multi-seed irrelevant per ADR-007 line 50 framework preserved); prompt template versioned in repo; one call per eval row. The four reference rungs are stratified along ADR-005 three-state contamination taxonomy — TF-IDF+LR is verified_disjoint (trained on our LODO splits by construction, no possibility of pretrain contamination); ModernBERT-base across the three transformer conditions is backbone-partial-disjoint (fine-tuning disjoint by LODO construction; backbone pretrain corpus may include eval sources); ProtectAI v1 and v2 are suspected_contamination (partial training-corpus disclosure may include eval positives); gpt-4o and claude-sonnet-4-6 are vendor_black_box (closed corpora may include eval sources via web-scale pretraining). The trained-rung-vs-reference comparison is reported with this stratification explicit in a dedicated WRITEUP methodology spoke section so reviewer interpretation aligns — any trained-rung lift over LLM-judges is despite the LLM-judge pretrain advantage, and the TF-IDF+LR rung provides the only fully-disjoint anchor. Matched-budget controls (ledger row 333) lock to per-axis — data and eval methodology are matched (same train and eval splits per ADR-016; same metrics and statistical machinery per ADR-006); training compute is not matched (each rung uses its natural recipe; training compute is reported alongside the metric so AUPRC versus compute can be plotted as a Pareto frontier — the rung-ladder IS the Pareto frontier). Per-axis matching is the only framing that coherently handles the heterogeneous cost classes (LLM-judge dollars-per-call versus trained rungs GPU-minutes versus ProtectAI inference-only). A new assumption A-006 (severity medium) registers the contamination caveat and gates the methodology spoke section.
source: SPEC_GREENFIELD.md §2 Model ledger rows 333 + 334 + Phase 0-03 walk Q2 + Q3
acceptance_criterion: SPEC_GREENFIELD ledger row 333 carries locked-to-per-axis-matched-data-and-eval-not-compute (see ADR-018) status; ledger row 334 carries locked-to-gpt-4o-2024-08-06-plus-claude-sonnet-4-6-plus-protectai-v1-plus-protectai-v2-drop-lakera (see ADR-018 partially supersedes ADR-015) status; SPEC_SHEET §4 reference-rung enumeration is updated to four rungs (gpt-4o-2024-08-06 plus claude-sonnet-4-6 plus ProtectAI v1 plus ProtectAI v2); SPEC_SHEET §4 gains a contamination-state column annotating each rung with the ADR-005 three-state taxonomy label (verified_disjoint or backbone-partial-disjoint or suspected_contamination or vendor_black_box); assumptions.md gains A-006 new (severity medium — all reference rungs carry uncontrolled training-data leakage relative to our eval slate; ProtectAI v1 plus v2 partial-disclosure may include eval positive sources; gpt-4o plus claude-sonnet-4-6 closed corpora may include eval sources via web-scale pretraining; ModernBERT-base backbone for trained rungs 2-4 backbone pretrain corpus may include eval sources; reporting consequence — every reference-rung headline metric reported with explicit contamination-state tag; methodology spoke includes contamination-stratification subsection; Phase 1 mitigation — contamination scan via MiniLM cosine between eval set and known public mirrors of training data provides partial evidence of overlap for ProtectAI plus does not help for LLM judges closed corpora); data/source_manifest.yaml from ADR-016 is extended with a models section pinning HF revision SHAs for ProtectAI v1 plus v2 plus a judges section pinning LLM-judge snapshot IDs (gpt-4o-2024-08-06 plus claude-sonnet-4-6 with date-suffixed snapshot ID resolved at Phase 1 entry); EVIDENCE.md gains an entry per reference rung per the 3-state taxonomy with the contamination-state label and rationale; WRITEUP methodology spoke contains a dedicated Contamination stratification subsection narrating the four-tier disclosure gradient; WRITEUP methodology spoke contains a dedicated Matched-budget framing subsection narrating per-axis matching plus the Pareto frontier framing for compute reporting; LLM-judge prompt template is versioned in src/judges/prompt_template_v1.md plus calls use temperature equals zero per ADR-007 framework.
closing_commit: cfa7559
supersedes: "015"
superseded_by:
  - "050"  # back-link added per ADR-077 frontmatter-backfill discipline; ADR-050 supersedes ADR-018 on the rung-slate narrowing axis
references:
  - https://arxiv.org/abs/2306.05685
  - https://arxiv.org/abs/2311.18964
  - https://arxiv.org/abs/2310.18018
  - https://arxiv.org/abs/2406.01574
  - https://arxiv.org/abs/2009.06489
  - https://platform.openai.com/docs/deprecations
  - https://huggingface.co/protectai/deberta-v3-base-prompt-injection
  - https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2
  - https://huggingface.co/blog/peft
  - https://arxiv.org/abs/2204.06745
  - decisions/ADR-015-rung-architecture-refinement.md
  - decisions/ADR-007-rung-architecture-and-reference-scorers.md
  - decisions/ADR-005-methodology-principles.md
  - decisions/ADR-016-data-design-bundle.md
transcript: transcripts/2026-05-15__phase-0-03__model-scope.md
---

# ADR-018: Reference scorer slate and contamination stratification

## Status

Accepted (2026-05-15). Partially supersedes ADR-015 reference-slate enumeration (drops Lakera Guard; adds ProtectAI v1). ADR-015's transformer-architecture claims (single-backbone ModernBERT-base for the trained transformer slate) remain valid; this ADR refines only the reference-rung portion.

## Context

ADR-007 originally framed the reference-rung slate as two LLM-judges (one OpenAI plus one Anthropic) plus two optional existing-classifier baselines (Lakera Guard plus ProtectAI). ADR-015 preserved that framing unchanged. Phase 0-03 Q3 surfaced three load-bearing methodology concerns that ADR-007 and ADR-015 did not address explicitly.

First, specific LLM-judge model IDs were deferred — Phase 0-03 must commit to snapshot identifiers (not aliases) so the eval is reproducible. Snapshot IDs are stable for approximately twelve months; aliases drift silently and break reproducibility — the rule from ADR-016 (SHA-pinning for data sources) extends to model versions.

Second, Lakera Guard inclusion carries ToS-audit overhead (commercial APIs often restrict benchmark publication) plus vendor-black-box methodology complexity. For prototype scope, the simpler call is to drop Lakera and rely on ProtectAI as the only off-the-shelf-classifier reference rung — the methodology story remains complete with ProtectAI plus the two LLM-judges, and the Lakera comparison can be named in the afterword as an extension that requires a separate ToS-verification step.

Third, Brandon's Phase 0-03 Q3 framing surfaced an even sharper methodology concern — no reference rung is fully verified_disjoint relative to our eval slate. ProtectAI's training corpus disclosure is partial. The LLM-judges (gpt-4o, claude-sonnet-4-6) are trained on essentially all public web text up to their cutoff and may have seen mosscap, HackAPrompt, PromptBench, and similar public eval datasets. Even the ModernBERT-base backbone (used for trained rungs 2 through 4) was pretrained on a web-scale corpus that may include our eval sources. The Phase 0-03 walk added ProtectAI v1 alongside v2 specifically to enable an internal off-the-shelf lift comparison (v1 to v2 lift — what classifier updates buy you, parallel to the trained-rung-lift narrative TF-IDF+LR to frozen-probe to LoRA to full-FT).

Combining these three concerns surfaces a stronger methodology contribution than the original ADR-007 framing — the rung slate now spans every level of the ADR-005 three-state contamination taxonomy, and the methodology spoke can explicitly stratify reference-rung interpretation by contamination disclosure. This turns the contamination concern from a footnote into a methodology axis.

Matched-budget controls (Q2 / ledger row 333) is the related methodology decision — should cross-rung comparisons hold compute budget constant? The natural answer for our heterogeneous slate is per-axis — match data and eval methodology (already locked by ADR-016 and ADR-006), let training compute vary, report it as a Pareto frontier. This handles the heterogeneous cost classes (LLM-judge dollars, GPU-minutes, inference-only) coherently without forcing artificial budget constraints.

## Decision

### Reference-rung slate (four rungs)

| Rung | Model ID | Cost class | Contamination state |
|---|---|---|---|
| R1 | gpt-4o-2024-08-06 | API USD per call | vendor_black_box |
| R2 | claude-sonnet-4-6 (snapshot ID pinned at Phase 1) | API USD per call | vendor_black_box |
| R3 | protectai/deberta-v3-base-prompt-injection (v1) | local inference (CPU or GPU) | suspected_contamination |
| R4 | protectai/deberta-v3-base-prompt-injection-v2 | local inference (CPU or GPU) | suspected_contamination |

Lakera Guard is dropped from the reference slate; named in WRITEUP/limitations-and-future-work.md as an afterword extension requiring ToS verification.

### LLM-judge call framework (preserved from ADR-007)

- Temperature equals zero (deterministic; multi-seed irrelevant)
- One call per eval row
- Prompt template versioned in src/judges/prompt_template_v1.md and documented; cross-judge prompt is identical (only the API endpoint differs)
- Per-row predictions persisted to evals/predictions/<judge>__fold<F>.parquet (no seed dimension since deterministic; no epoch dimension since no training)

### ProtectAI v1-versus-v2 comparison framework

- Both models loaded at native config (DeBERTa-v3-base, 512-token cap, no fine-tuning by us)
- Both pinned via HF revision SHA in data/source_manifest.yaml (extended with models section)
- Inference uses bf16 on GPU (matches trained-rung precision per ADR-019)
- Per-row predictions persisted to evals/predictions/protectai-v1__fold<F>.parquet and evals/predictions/protectai-v2__fold<F>.parquet
- Methodology spoke gains a v1-to-v2 lift subsection parallel to the trained-rung lift chain

### Contamination stratification

Complete rung-slate contamination taxonomy after ADR-017 plus ADR-018 locks (eight rungs total):

| Rung | Contamination state |
|---|---|
| TF-IDF + LR | verified_disjoint |
| ModernBERT-base frozen-probe | backbone-partial-disjoint |
| ModernBERT-base LoRA | backbone-partial-disjoint |
| ModernBERT-base full-FT | backbone-partial-disjoint |
| ProtectAI v1 | suspected_contamination |
| ProtectAI v2 | suspected_contamination |
| gpt-4o-2024-08-06 | vendor_black_box |
| claude-sonnet-4-6 | vendor_black_box |

The methodology spoke includes a dedicated Contamination stratification subsection explaining the four-tier disclosure gradient and framing the reference-rung comparison as "what trained-from-scratch (TF-IDF+LR fully-disjoint anchor) achieves versus what potentially-memorized off-the-shelf models achieve" — any trained-rung lift over LLM-judges is despite the LLM-judge pretrain advantage.

### Matched-budget controls (per-axis) — ledger row 333

- Matched — data (same train and eval splits per ADR-016); eval methodology (same metrics, same statistical machinery per ADR-006)
- Not matched — training compute (each rung uses natural recipe; ADR-017 plus ADR-019 specify each rung's recipe)
- Reported — training compute per rung in the writeup (wall-clock on the GPU class detected at runtime; per ADR-020 runpod-deploy primitives capture this in the per-pod manifest); the methodology spoke plots AUPRC versus compute as a Pareto frontier — the rung-ladder IS the Pareto frontier

Per-axis matching is the only framing that coherently handles the heterogeneous cost classes (LLM-judge dollars-per-call versus trained rungs GPU-minutes versus ProtectAI inference-only). Matched-training-compute would violate SPEC §2 hyperparameter-immutability (would require val-set tuning to find the budget cutoff) and would not fit the LLM-judge or ProtectAI cost classes coherently.

## Consequences

### Positive

- Snapshot model IDs are pinned for reproducibility (gpt-4o-2024-08-06 stable; claude-sonnet-4-6 with date-suffixed snapshot resolved at Phase 1)
- Contamination stratification turns a weakness into a methodology contribution — the rung slate now spans every level of the three-state taxonomy
- ProtectAI v1-to-v2 lift comparison parallels the trained-rung lift chain — surfaces what off-the-shelf classifier updates buy you
- Per-axis matched-budget aligns with SPEC §2 hyperparameter-immutability plus accommodates the heterogeneous rung cost classes
- Dropping Lakera simplifies scope (no ToS audit, no vendor-black-box complexity beyond the LLM-judges)
- API budget remains within A-002 envelope — approximately ten to twelve dollars total for both LLM-judge rungs

### Negative

- Dropping Lakera removes one commercial-API data point; mitigated by the afterword extension flag
- The methodology spoke gains a dedicated contamination-stratification section plus a per-axis matched-budget section; the writeup is denser but more honest
- A-006 is a new severity-medium assumption — surfaces in the WRITEUP caveats block per the reporting-completeness invariant
- The four-reference-rung slate plus the four-trained-rung slate gives eight rungs total; the Cohen's kappa pairwise matrix (preserved from ADR-007) becomes a 28-pair heatmap which is dense but readable

### Phase 1 deliverables

- data/source_manifest.yaml — extend with models section (ProtectAI v1 plus v2 HF revision SHAs) plus judges section (gpt-4o snapshot ID plus claude-sonnet-4-6 snapshot ID with date suffix resolved at Phase 1)
- src/judges/prompt_template_v1.md — versioned LLM-judge prompt template
- src/judges/openai_caller.py and src/judges/anthropic_caller.py — temp=0 API wrappers with manifest-pinned snapshot IDs
- src/rungs/protectai_v1.py and src/rungs/protectai_v2.py — HF inference wrappers at native config with bf16 on GPU
- evals/predictions/{gpt-4o,claude-sonnet-4-6,protectai-v1,protectai-v2}__fold<F>.parquet — per-rung per-fold predictions
- EVIDENCE.md — contamination-state entry per reference rung per the 3-state taxonomy
- WRITEUP methodology spoke — Contamination stratification subsection plus Matched-budget framing subsection

## Alternatives considered

- **Include Lakera Guard with vendor-black-box framing plus ToS audit** — rejected for prototype scope; the ToS audit overhead and the partial-disclosure complexity exceed the marginal methodology value of one additional commercial-API data point. Named in afterword extension.
- **Drop LLM-judges entirely (use ProtectAI only)** — rejected because LLM-judges provide an upper-bound signal under maximum-memorization conditions ("ceiling achievable by a frontier model that may have memorized everything"); if our trained rungs approach or beat that ceiling despite the contamination disadvantage, the result is stronger; if we lose, the contamination framing upper-bounds the gap. The Cohen's kappa pairwise structure also benefits from the LLM-judge rungs.
- **Use GPT-4o-mini or Claude Haiku for cost** — rejected because budget-tier judges risk strawman framing if they underperform; the methodology question is "is the LLM-judge a strong baseline?" which requires capable mid-tier models. The mid-tier (gpt-4o + claude-sonnet-4-6) pair adds approximately ten dollars to the budget — negligible against A-002 envelope.
- **Use frontier-tier judges (gpt-4.1 or claude-opus-4-7)** — rejected for prototype; mid-tier is the methodology-balanced choice. Frontier-tier comparison named in afterword extension as ablation study at smaller eval slice.
- **Use ProtectAI v2 only without v1** — rejected because the v1-to-v2 lift comparison parallels the trained-rung-lift narrative and surfaces what off-the-shelf updates buy you; adding v1 is one extra inference run per fold at near-zero compute cost.
- **Yes-match-training-compute (give every trained rung the same budget)** — rejected because it violates SPEC §2 hyperparameter-immutability (matched-budget would force val-set tuning to find the budget cutoff) plus does not fit LLM-judge or ProtectAI cost classes coherently.
- **No matched-budget (natural recipes, no compute reporting)** — rejected because reviewer may push back on "of course full-FT wins, it had more compute"; per-axis matching exposes the compute axis explicitly as a Pareto frontier rather than hiding it.

## References

See frontmatter references list. Primary anchors — Zheng et al. 2023 LLM-as-a-Judge methodology; Zhou et al. 2024 LLM evaluation contamination survey; Sainz et al. 2023 NLP evaluation in trouble (contamination disclosure central to eval methodology); MMLU-Pro 2024 contamination-stratified evaluation; Hooker 2021 Hardware Lottery (matched-compute critique); OpenAI deprecation policy for snapshot IDs; ProtectAI v1 plus v2 model cards; HuggingFace PEFT comparative study; EleutherAI GPT-NeoX paper §6 (multi-rung evaluation framing); ADR-015 transformer-slate single-backbone claim; ADR-007 historical record; ADR-005 contamination taxonomy; ADR-016 data design plus source manifest.
