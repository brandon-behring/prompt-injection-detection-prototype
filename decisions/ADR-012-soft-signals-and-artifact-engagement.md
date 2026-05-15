---
adr_id: 012
slug: soft-signals-and-artifact-engagement
title: Soft-signals naming discipline and external artifact engagement set
date: 2026-05-15
status: Accepted
claim_id: CLAIM-012
claim: Eight soft signals are explicitly named in the WRITEUP — calibration, OOD honesty, reproducibility, writing clarity, engineering taste, methodology over results, time-budgeted craftsmanship, honesty about limitations — each aligned by prior ADR locks and cited at the relevant section as the reason a particular methodology choice was made. The default external artifact engagement set covers — Lakera Guard / ProtectAI as reference scorer rungs (per ADR-007); JailbreakBench (Chao 2024), HarmBench (Mazeika 2024), InjecAgent (Zhan 2024) cited and acknowledged; NotInject (Li & Liu 2024) replicated via OOD inclusion; BIPIA (Yi 2023) compared against; PromptShield (Microsoft 2024) acknowledged as Recall@FPR-pinpoint influence; OWASP LLM Top 10 cited if industry-standard threat-model framing is relevant.
source: SPEC_GREENFIELD.md §Brief row 308 (Q5-C9 + Q5-C10)
acceptance_criterion: Every soft signal listed appears explicitly in the WRITEUP at the relevant methodology section ("the brief emphasizes X, so we…"); every external artifact in the engagement set is either cited in the WRITEUP references or implemented as a rung / OOD slice as the engagement level mandates.
closing_commit:
references:
  - https://arxiv.org/abs/2404.01318
  - https://arxiv.org/abs/2402.04249
  - https://arxiv.org/abs/2403.02691
  - https://arxiv.org/abs/2410.22770
  - https://arxiv.org/abs/2312.14197
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-012: Soft-signals naming discipline and external artifact engagement set

## Status

Accepted (2026-05-15)

## Context

Soft signals (Q5-C9) are reviewer-weighted hints the brief carries without literally mandating. Naming them in the writeup demonstrates careful reading. External artifact engagement (Q5-C10) is the analogous question for prior work: which papers, benchmarks, models does the submission engage with, and at what level? Failing to engage with cited or canonical artifacts reads as "didn't do the homework"; over-engaging dilutes the methodology focus.

Both rows are brief-derived. The user verbally summarized that the brief is consistent with a methodology-first submission and ratified the default soft-signal list + default engagement set. This ADR records that ratification.

## Decision

### Part 1 — Eight soft signals, each named in the WRITEUP

| Soft signal | Where named | Aligned by ADR |
|---|---|---|
| Calibration | Headline metrics narrative (ECE is in the 4-metric headline) | ADR-006 |
| OOD honesty | Data design narrative (source-disjoint LODO + NotInject inclusion) | ADR-008 |
| Reproducibility | Process narrative (two-tier laptop + GPU canonical) | ADR-009 |
| Writing clarity | Front-matter (hub-and-spoke structure made explicit) | ADR-004 |
| Engineering taste | Process narrative (marker tests, uv.lock, pre-commit) | ADR-009 |
| Methodology > results | Front-matter (Principle 1 cited from ADR-005) | ADR-005 |
| Time-budgeted craftsmanship | Limitations narrative (fallback ladder discussion) | ADR-001 + ADR-005 |
| Honesty about limitations | Limitations narrative (structured-limitations principle) | ADR-005 Principle 3 + ADR-010 |

Naming discipline: at each relevant WRITEUP section, the prose explicitly cites the signal: *"the brief emphasizes [X], so we [methodology-choice-Y]"*. Shows the brief was read carefully and the methodology choices respond to it.

### Part 2 — Default external artifact engagement set

| Artifact | Engagement level | Implementation |
|---|---|---|
| Lakera Guard / ProtectAI LLM-Guard | **Compare against** | Reference-scorer rungs in the rung slate (per ADR-007); finalize model IDs in Phase 0-03 contingent on time. |
| JailbreakBench (Chao et al. 2024, NeurIPS D&B, arXiv:2404.01318) | **Cite + acknowledge** | Methodology section; not used as primary eval (different task: red-team vs detector). |
| HarmBench (Mazeika et al. 2024, ICML, arXiv:2402.04249) | **Cite + acknowledge** | Methodology section; same rationale as JailbreakBench. |
| InjecGuard / NotInject (Li & Liu 2024, arXiv:2410.22770) | **Replicate** | NotInject benign-trigger hard negatives included in OOD slate (per ADR-008); over-defense framing surfaced in WRITEUP. |
| BIPIA (Yi et al. 2023, arXiv:2312.14197) | **Compare against** | Indirect-injection OOD slice (per ADR-010 Bound 2: direct + indirect in scope). |
| InjecAgent (Zhan et al. 2024, ACL Findings, arXiv:2403.02691) | **Cite + acknowledge** | OOD stretch probe; agentic injection is out-of-primary-scope per ADR-010 Bound 2. |
| PromptShield (Microsoft 2024, provisional arXiv:2405.14478) | **Cite + acknowledge** | Influence on Recall@FPR=1% pinpoint choice (per ADR-006); cited in metrics-choice rationale. |
| OWASP LLM Top 10 | **Cite + acknowledge** (conditional) | Cite if industry-standard threat-model framing is relevant; otherwise omit. |

## Consequences

**Positive:**

- Soft-signal naming discipline produces a writeup that reads as carefully-targeted-at-the-brief rather than generic-ML-submission. Differentiates from equivalently-rigorous submissions that don't surface the brief-reading.
- Default engagement set is dossier-grounded — every external artifact mapped here is in `docs/research/MANIFEST.json` and has a verified summary in the dossier files.
- Engagement levels are concrete: "compare against" maps to rungs; "replicate" maps to OOD slices; "cite + acknowledge" maps to references. No ambiguity.

**Negative / cost:**

- Eight soft signals × one explicit naming each = eight prose hooks to write into the WRITEUP. Bounded.
- Default engagement set risks over-citing if the brief doesn't actually emphasize all listed artifacts. Mitigation: the engagement levels are calibrated (most are "cite + acknowledge", which is cheap); only Lakera/ProtectAI, NotInject, and BIPIA carry implementation cost (already locked in ADR-007/008/010).

**Neutral:**

- If during Phase 1-4 the brief surfaces additional soft signals or cited artifacts that the user didn't recall in the verbal summary, a superseding ADR would record the update.

## Alternatives Considered

- **Leave soft signals implicit** (in methodology choices but not named in the writeup): Cheaper. *Rejected* because explicit naming is the methodology-first move; differentiator for an A2 reviewer.
- **Smaller engagement set (e.g., only Lakera + JailbreakBench)**: Smaller paperwork. *Rejected* because the dossier-grounded artifacts each correspond to a load-bearing comparison (over-defense via NotInject; indirect-injection via BIPIA; metrics-influence via PromptShield) — dropping any narrows the methodology story.
- **Speculative inclusion of OWASP LLM Top 10 / NIST AI RMF unconditionally**: Demonstrates industry-standard awareness. *Rejected* because over-claiming without brief signal is the failure mode the soft-signal discipline guards against. Conditional inclusion is the right stance.

## References

- JailbreakBench (Chao et al. 2024 NeurIPS D&B) — https://arxiv.org/abs/2404.01318
- HarmBench (Mazeika et al. 2024 ICML) — https://arxiv.org/abs/2402.04249
- InjecAgent (Zhan et al. 2024 ACL) — https://arxiv.org/abs/2403.02691
- InjecGuard / NotInject (Li & Liu 2024) — https://arxiv.org/abs/2410.22770
- BIPIA (Yi et al. 2023) — https://arxiv.org/abs/2312.14197
- PromptShield (Microsoft 2024 provisional) — https://arxiv.org/abs/2405.14478
- HackAPrompt (Schulhoff et al. 2023 EMNLP) — https://arxiv.org/abs/2311.16119
- OWASP LLM Top 10 — https://owasp.org/www-project-top-10-for-large-language-model-applications/
- `docs/research/MANIFEST.json` — dossier index
- ADR-001 (time-budgeted craftsmanship — fallback ladder)
- ADR-005 (methodology > results; honesty about limitations)
- ADR-006 (calibration in headlines; PromptShield influence)
- ADR-007 (Lakera/ProtectAI reference rungs)
- ADR-008 (OOD honesty via LODO + NotInject; BIPIA in OOD slate)
- ADR-009 (reproducibility + engineering taste)
- ADR-010 (honesty about limitations via structured extension conditions)
