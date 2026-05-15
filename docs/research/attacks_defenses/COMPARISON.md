---
title: Comparison — Toolkit-produced ledger vs project's manual citations
dossier_id: attacks_defenses/COMPARISON
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: COMPARISON
tags:
- attacks
- defenses
related_dossiers: []
---
# Comparison — Toolkit-produced ledger vs project's manual citations

**Date:** 2026-05-08
**Project:** `prompt_injection_detector`
**Slice:** Prompt-injection attacks and defenses (A1-F3)
**Toolkit ledger:** 23 entries; landmark recall 4/4 (Gate A passed); 0 hard 404s (Gate B passed); 0 audit DROP, 2 CORRECT (F2 title, E3 first author), 0 FLAG.

## Project context

The project has the deepest existing manual curation here: `docs/red_team_research/00..07_*.md` is **3,811 lines / 393 arXiv references** across 7 files (direct attacks / indirect+agentic / defenses / training-time threats / datasets+benchmarks / tools+vendors / standards). Plus `literature_review.md`, `literature_review_extended.md`, and `methodology_landscape_review.md`.

This slice's 23 entries are NOT meant to compete with the project's 393. They represent the **canonical high-impact subset** that one ~90-minute toolkit run produces, and the question is whether the toolkit's most-recent canonical refs match what the project's hand-curated work also identified as canonical.

## Table 1 — Overlap (my 23 entries vs project's 393)

| Toolkit anchor | arXiv ID | In project? |
|---|---|---|
| A1 Perez & Ribeiro 2022 | 2211.09527 | [Y] (4 files) |
| A2 Wei et al. 2023 Jailbroken | 2307.02483 | [Y] (1 file) |
| A3 Liu et al. 2023 HouYi | 2306.05499 | [Y] (2 files) |
| A4 Anil et al. 2024 Many-shot | (no arXiv) | [Y] (red_team_research/01, /07; literature_review_extended) |
| B1 Greshake et al. 2023 | 2302.12173 | [Y] (5 files) |
| B2 Zou et al. 2024 PoisonedRAG | 2402.07867 | [Y] (6 files) |
| C1 Zou et al. 2023 GCG | 2307.15043 | [Y] (6 files) |
| C2 Liu et al. 2024 AutoDAN | 2310.04451 | [Y] (5 files) |
| C3 Chao et al. 2023 PAIR | 2310.08419 | [Y] (5 files) |
| C4 Mehrotra et al. 2023 TAP | 2312.02119 | [Y] (5 files) |
| D1 Hines et al. 2024 Spotlighting | 2403.14720 | [Y] (6 files) |
| D2 Inan et al. 2023 Llama Guard | 2312.06674 | [Y] (2 files) |
| D3 Rebedea et al. 2023 NeMo Guardrails | 2310.10501 | [Y] (2 files) |
| D4 Robey et al. 2023 SmoothLLM | 2310.03684 | [Y] (4 files) |
| D5 Jain et al. 2023 Baseline Defenses | 2309.00614 | [Y] (1 file) |
| D6 Xu et al. 2024 SafeDecoding | 2402.08983 | [Y] (1 file) |
| E1 Bai et al. 2022 Constitutional AI | 2212.08073 | [Y] (4 files) |
| E2 Wallace et al. 2024 Instruction Hierarchy | 2404.13208 | [Y] (5 files) |
| E3 Sharma et al. 2025 Constitutional Classifiers | 2501.18837 | [Y] (3 files) |
| E4 Chen et al. 2024 StruQ | 2402.06363 | [Y] (4 files) |
| F1 Liu et al. 2024 Formalizing PI | 2310.12815 | [Y] (6 files) |
| F2 Schulhoff et al. 2024 Prompt Report | 2406.06608 | [N] NOT IN PROJECT |
| F3 OWASP LLM Top 10 | (no arXiv) | [Y] (red_team_research/02, /06, /07) |

**Overlap: 22 / 23 = 95.7%.** Of the toolkit's blind-discovered entries, all but one are also cited by the project's manual curation.

## Table 2 — Value-add (toolkit found, project didn't cite)

Only one entry: **F2 Schulhoff et al. 2024 *The Prompt Report*** (arXiv:2406.06608). A 76-page PRISMA-method survey of 1500+ papers across 58 prompting techniques. Authored with OpenAI, Microsoft, Google, Princeton, Stanford, etc. Companion to HackAPrompt benchmark. The project doesn't cite this anywhere. Genuine value-add: it's a single-anchor canonical reference that would have served the project's `docs/literature_review.md` well.

## Table 3 — Gap (project has, toolkit didn't surface)

The project has ~370 arXiv references the toolkit did NOT produce in this 90-minute slice. This is **expected, not a toolkit failure** — a single research-gather run targets the canonical ~20-30 entries per claim_family, not exhaustive coverage. A representative sample of canonical entries the project has that this toolkit run missed:

- **CaMeL** (Capabilities-Based Mediated Lookup, 2025) — capability-flow control for agentic LLMs (cited in `literature_review_extended.md`).
- **Garak** — open-source LLM red-team toolkit (project's `06_tools_and_vendors.md`).
- **Rebuff / Lakera Guard / Microsoft Prompt Shields** — vendor classifiers (project's `06`).
- **Backdoor / training-time-threat literature** — RAFT, instruction-backdoor papers (project's `04_training_time_threats.md`, 78 arXiv refs).
- **Specific persuasion / role-play attacks** — Yu et al. PAP, Andriushchenko et al., etc. (project's `01`).
- **Fine-tuning attacks / preference-poisoning** — Qi et al. 2023, fine-tuning subverts safety (project's `04`).
- **Specific defense papers** — RAIN, In-context Defense, ALMs, Self-Reminder (project's `03`, 91 arXiv refs).

**To match the project's coverage**, the toolkit would need 5-10× more `/research-gather` invocations across narrower sub-areas. That's a deliberate trade-off: the project's curators spent likely 40-80 hours on `red_team_research/`; this slice was ~90 minutes.

## Manual readback verdict

The toolkit's blind output reproduces the project's headline canonical references (95.7% overlap on the toolkit's 23 entries) and adds one survey the project missed. What it provides on top of the project's already-strong content:

1. **5-bullet per-paper structure (Source/Code/Mechanism/Result/Status)** — the project's `red_team_research` files are dense prose tables; the toolkit's structured bullets are easier for an LLM agent to parse deterministically.
2. **22 lookup recipes + 22-term glossary in a single README** — the project has `00_overview.md` (a similar role) but no equivalent question-routing layer.
3. **Per-anchor section IDs** (`A1` … `F3`) — the project's `red_team_research` uses topic headings without canonical short anchors; the toolkit's format is more agent-grippable.

What the toolkit cannot replicate: the project's depth (393 vs 23 references), domain-specific synthesis tying findings to the project's own evaluation slices and ProtectAI v2 comparisons, and 670+ entries of total knowledge-graph context across the broader curated material.

## Verdict

For this slice, **the toolkit is complementary, not a replacement**. The project's `red_team_research/` is the deeper artifact; the toolkit's 23-entry version is a fast canonical-anchors index that:
- Hits 95.7% recall on its own targeted entries vs project citations
- Adds one missing survey (Schulhoff 2024)
- Provides a structured agent-grippable surface the project lacks

The toolkit's per-slice budget (~90 min) is not the unit needed to match a multi-week curation. Instead, the toolkit's value at this scope is the **structured synthesis layer** — useful as an *additional* lookup index alongside `red_team_research/`, not as a replacement.
