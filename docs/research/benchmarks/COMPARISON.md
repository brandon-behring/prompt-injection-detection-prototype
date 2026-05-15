---
title: Comparison — Toolkit-produced ledger vs project's manual citations
dossier_id: benchmarks/COMPARISON
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: COMPARISON
tags:
- evals
- benchmarks
related_dossiers: []
---
# Comparison — Toolkit-produced ledger vs project's manual citations

**Date:** 2026-05-08
**Project:** `prompt_injection_detector`
**Slice:** Prompt-injection benchmarks (A1-D2)
**Toolkit ledger:** 10 entries; landmark recall 4/4 (Gate A passed); 0 hard 404s (Gate B passed); 0 audit DROP/CORRECT/FLAG, 7/7 spot-check passed.

## Project context

The project's primary benchmark-landscape artifact is `docs/methodology_landscape_review.md` plus per-benchmark coverage in `docs/red_team_research/05_datasets_and_benchmarks.md` (50 arXiv refs). Project's actual benchmark consumption: `data/dataset_inventory.json` lists Lakera Gandalf (covered in Slice 4), NotInject + XSTest as OOD-eval probes, plus references HackAPrompt / BIPIA / JailbreakBench in methodology context.

## Table 1 — Overlap (10 toolkit entries vs project)

| Toolkit anchor | arXiv ID | In project? |
|---|---|---|
| A1 Schulhoff 2023 HackAPrompt | 2311.16119 | [Y] (6 files) |
| A2 Chao 2024 JailbreakBench | 2404.01318 | [Y] (7 files) |
| A3 Mazeika 2024 HarmBench | 2402.04249 | [Y] (7 files) |
| B1 Yi 2023 BIPIA | 2312.14197 | [Y] (8 files) |
| B2 Debenedetti 2024 AgentDojo | 2406.13352 | [Y] (8 files) |
| B3 Zhan 2024 InjecAgent | 2403.02691 | [Y] (6 files) |
| C1 Li 2024 InjecGuard / NotInject | 2410.22770 | [N] NOT IN PROJECT |
| C2 Röttger 2024 XSTest | 2308.01263 | [Y] (4 files) |
| D1 Toyer 2023 TensorTrust | 2311.01011 | [Y] (2 files) |
| D2 Abdelnabi 2025 LLMail-Inject | 2506.09956 | [Y] (2 files) |

**Overlap: 9/10 = 90%.** All 4 held-out landmarks confirmed.

## Table 2 — Value-add

**C1 Li & Liu 2024 *InjecGuard*** (arXiv:2410.22770). The project uses NotInject (mentioned in `data/dataset_inventory.json` and `docs/red_team_research/`) but does not cite the InjecGuard paper that introduced NotInject as a hard-negative dataset. The project's NotInject reference is to the *artifact* (HuggingFace dataset). Adding the InjecGuard primary-source reference would strengthen the citation chain — the project currently cites NotInject as if it were a standalone dataset, when it's actually the diagnostic artifact accompanying the InjecGuard paper.

This is genuinely useful: future maintainers asking "where does NotInject's design come from?" would have a clean primary-source link. Concrete value-add.

## Table 3 — Gap (project benchmarks not in toolkit's 10)

The project's `methodology_landscape_review.md` and `red_team_research/05_datasets_and_benchmarks.md` cite additional benchmarks the toolkit did not surface in this 90-min slice:

- **AdvBench** — companion to GCG (Slice 1 § C1 — appears as "behaviors used by JailbreakBench"; not its own benchmark paper, which is why it's not its own entry here).
- **MaliciousInstruct** — Huang et al. 2023, an earlier safety benchmark.
- **TDC 2023 Red Teaming Track** — referenced via HarmBench; competition data, not paper.
- **OR-Bench** — Cui et al. 2024 over-refusal benchmark (alternative to XSTest).
- **WildJailbreak / WildGuardMix** — Allen AI's recent additions.
- **CySecBench** — Wan et al. cybersecurity-focused benchmark.
- **EasyJailbreak** — toolkit-style benchmark suite.

**Recall context:** the project's curators surfaced ~15-20 named benchmarks; the toolkit's 10 cover the canonical 90% by influence. The remaining are second-tier or specialized — appropriate trade-off for a single slice.

## Manual readback verdict

Slice 2 is the **strongest of the 4 slices** in terms of toolkit performance:
- 0 audit corrections (best in show)
- 17/17 URL freshness (cleanest)
- 9/10 project overlap with one genuine value-add primary-source link
- Lookup-recipe depth: 17 recipes for 10 entries (highest density)

The 4-sub-area decomposition (direct / indirect / hard-negative / CTF) cleanly separates benchmarks the project might mix together. The toolkit's added value here is the **structured lookup index** — `methodology_landscape_review.md` is prose; the agent_index README routes to canonical anchors per question.

## Verdict

For benchmarks specifically, the toolkit produced a **near-replica of the project's curation** with one structural improvement (InjecGuard primary-source link). Confidence is high that this slice could substitute for `methodology_landscape_review.md` as a quick-reference index. The project's depth (50+ benchmarks in `red_team_research/05`) still exceeds this 10-entry slice, but the headline canonical refs are fully covered.

**Cross-slice synergy:** this slice's `04_benchmark_ctf_adaptive.md` § D2 (LLMail-Inject) is the data source for the project's `llmail` evaluation slice. Slice 4 (datasets) will pick up the project's actual training/dev datasets (deepset, Lakera Gandalf, OASST1) — this slice cleanly leaves those for Slice 4.
