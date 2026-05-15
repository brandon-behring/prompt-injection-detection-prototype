---
adr_id: 010
slug: scope-limits-with-extension-conditions
title: Scope limits with per-bound extension conditions
date: 2026-05-15
status: Accepted
claim_id: CLAIM-010
claim: Submission scope is bounded along six axes — language (English-only), attack class (direct + indirect), input length (per-backbone cap, 512 for DeBERTa-v3 and 8K for ModernBERT), model size (sub-1B parameters), deployment surface (text-only classifier + LLM-judge reference rungs), adversarial-strength budget (static attacks only). Each bound is paired with the explicit conditions under which extending past it would or wouldn't make sense, per ADR-005 Principle 3 (structured limitations with extension conditions). Decision-relevant extension framings replace generic "future work" boilerplate.
source: SPEC_GREENFIELD.md §Brief row 308 (Q5-C7) + §0 Threat rows 319-322 + §2 Model row 330 + §2 Model row 331
acceptance_criterion: WRITEUP/limitations-and-future-work.md spoke enumerates all six scope bounds with their extension conditions; every ADR for a methodology component (per CLAUDE.md anti-pattern) names the bound it operates within.
closing_commit: e760faf
references:
  - https://arxiv.org/abs/2412.13663
  - https://arxiv.org/abs/2312.14197
  - https://arxiv.org/abs/2403.02691
  - https://arxiv.org/abs/2307.15043
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-010: Scope limits with per-bound extension conditions

## Status

Accepted (2026-05-15)

## Context

ADR-005 Principle 3 mandates that every scope-bound, methodology choice, and metric reported in the writeup be paired with **(a)** the limitation it imposes and **(b)** the conditions under which extending past it would or wouldn't make sense. This ADR enumerates the six brief-level scope bounds (Q5-C7) and locks each with its extension condition. The structured-limitations approach replaces generic "future work could include X" boilerplate with decision-relevant framings that map to a reader's deployment context.

The dossier at `docs/research/attacks_defenses/` covers all attack classes (direct, indirect, optimization-based, training-time defenses, threat models); the dossier-default scope (direct + indirect) is the field-standard middle ground. ModernBERT's 8K native context (Warner et al. 2024) makes per-backbone length caps a principled honest choice rather than an artefactual difference to hide.

## Decision

**Six scope bounds**, each with an extension condition:

### Bound 1 — Language scope: **English-only**

- **Limitation**: detector performance on non-English inputs is not characterized.
- **Extend if**: deployment targets non-English markets; threat model includes multilingual attackers (Yong et al. 2023, "Low-Resource Languages Jailbreak GPT-4").
- **Don't extend if**: production scope is English; benchmark literature alignment matters more than market coverage.

### Bound 2 — Attack-class scope: **Direct + indirect prompt injection**

- **Limitation**: optimization-based attacks (GCG; Zou et al. 2023, arXiv:2307.15043), full agentic injection (InjecAgent more than as OOD probe), and multimodal injection are not in scope.
- **Extend to agentic if**: deployment surface includes tool-use / agentic workflows.
- **Extend to adversarial-optimization if**: threat model includes determined adversaries with gradient access to a similar model.
- **Don't extend if**: deployment is chat-text classifier only.

### Bound 3 — Input length cap: **Per-backbone (512 DeBERTa-v3 / 8K ModernBERT)**

- **Limitation**: cross-backbone Δ-AUROC comparison is confounded by context-window difference. Reported in the spoke with this caveat.
- **Extend (standardize across backbones) if**: cross-backbone Δ-AUROC is the headline comparison and length-confound is unacceptable.
- **Don't extend if**: each backbone is judged on its native context window (current framing). This preserves the ModernBERT-vs-DeBERTa-v3 motivation — 8K context is *the reason* to include ModernBERT.

### Bound 4 — Model size: **Sub-1B parameters**

- **Limitation**: detector capabilities at >1B parameters (e.g., RoBERTa-large variants, decoder-based detectors) are not characterized.
- **Extend if**: inference latency budget is non-binding; deployment is offline batch.
- **Don't extend if**: edge/runtime/throughput-bound deployment.

### Bound 5 — Deployment surface: **Text-only classifier + LLM-judge reference rungs**

- **Limitation**: no runtime-integration experiments (e.g., classifier-in-the-loop with an LLM agent).
- **Extend to runtime integration if**: full deployment story needed (e.g., end-to-end agentic workflow guard).
- **Don't extend if**: this is a methodology submission with the classifier as artifact (current framing).

### Bound 6 — Adversarial-strength budget: **Static attacks only**

- **Limitation**: adaptive red-team (GCG against your detector; PAIR; TAP) is not in scope.
- **Extend to adaptive if**: deployment is production-critical AI security.
- **Don't extend if**: this is a methodology + baseline submission with explicit-deferral framing (current). Avoids dilution of the methodology focus under Tight calendar.

## Consequences

**Positive:**

- The structured-limitations table in `WRITEUP/limitations-and-future-work.md` reads as decision-relevant guidance, not boilerplate. A1 (hiring manager) reviewer maps their deployment context to one of the extend/don't-extend rows.
- The per-backbone length-cap (Bound 3) preserves the *motivation* for including ModernBERT — its 8K context is the reason. Standardizing to 512 would erase the comparison's point.
- Bound 2 (direct + indirect) covers the deployable scope; agentic InjecAgent can live in OOD slate without becoming the writeup's center.
- Bound 6 (static attacks only) is the Tight-calendar discipline — adaptive red-team is a separate sub-project, not a half-day addition.

**Negative / cost:**

- Six bounds × extension-condition prose = a meaningful spoke chapter. Tractable but real writing work.
- Bound 3 (per-backbone length cap) introduces a confound in cross-backbone comparisons that must be honestly reported every time the comparison is made.
- Bound 6 (static-only) requires explicit "future work" framing in the writeup to pre-empt the inevitable reviewer question "what about adaptive attacks?"

**Neutral:**

- Phase 0-01 still walks the §0 Threat rows (319 attack-classes, 320 language, 321 length-cap, 322 truncation policy). This ADR captures the brief-level locks; truncation policy specifically remains open (head/tail/middle/adaptive) and is finalized in Phase 0-02.

## Alternatives Considered

- **Multilingual scope**: Cover English + Spanish + Chinese. *Rejected* under Tight calendar; dossier and benchmark literature are predominantly English; multilingual adds eval-set complexity without proportional methodology gain.
- **Direct-only scope**: Cleaner; smaller eval slate. *Rejected* because direct + indirect is the field standard; BIPIA + InjecAgent are dossier-vetted candidates.
- **Standardized length cap (e.g., 512 across both backbones)**: Removes the confound in Bound 3. *Rejected* because it erases ModernBERT's motivation; the honest move is to report each backbone on its native context and surface the confound explicitly.
- **Sub-2B parameter budget**: Larger models. *Rejected* because Sub-1B already covers DeBERTa-v3-large (~435M) and ModernBERT-large (~395M); going larger doesn't tell a meaningfully different deployment story for prompt-guard work.
- **Adaptive-red-team in scope**: Stronger robustness story. *Rejected* under Tight calendar; would dilute the methodology focus; better as explicit future work.

## References

- ModernBERT (Warner et al. 2024) — https://arxiv.org/abs/2412.13663
- BIPIA (Yi et al. 2023) — https://arxiv.org/abs/2312.14197
- InjecAgent (Zhan et al. 2024) — https://arxiv.org/abs/2403.02691
- GCG (Zou et al. 2023) — https://arxiv.org/abs/2307.15043
- Yong et al. 2023 (Low-Resource Languages Jailbreak) — relevant for Bound 1 extension
- `docs/research/attacks_defenses/01_attack_direct.md` through `06_threat_model_survey.md`
- ADR-005 (Principle 3 — structured limitations with extension conditions, directly applied here)
- ADR-007 (rung architecture references Bound 4 model-size budget)
- ADR-008 (data scope references Bound 2 attack classes)
