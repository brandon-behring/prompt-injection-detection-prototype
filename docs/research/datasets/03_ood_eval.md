---
title: Out-of-distribution evaluation datasets
dossier_id: datasets/03
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '03'
tags:
- data
- corpora
related_dossiers: []
---
# Out-of-distribution evaluation datasets

Datasets used as OOD evaluation probes — including hard-negative / over-refusal sets and indirect/agentic injection sets. Anchors `C1`–`C5`.

## C1. NotInject — over-defense hard negatives

- **NotInject — over-defense benchmark for prompt-guard models** — HuggingFace, 2024.
  - **Source:** https://huggingface.co/datasets/leolee99/NotInject
  - **Access:** hf datasets; auth_required: false
  - **Schema:** 339 benign samples enriched with PI trigger words; three difficulty levels (113 one-word + 113 two-word + 113 three-word triggers)
  - **License:** MIT (confirmed on HF dataset card during audit)
  - **Tasks:** classification (all benign — measures FALSE-POSITIVE rate of guards). Cite Li & Liu (2024) InjecGuard, arXiv:2410.22770.

## C2. XSTest — exaggerated-safety test suite

- **XSTest — exaggerated-safety test suite** — GitHub, 2024.
  - **Source:** https://github.com/paul-rottger/xstest
  - **Access:** direct (clone repo); auth_required: false
  - **Schema:** 450 prompts (250 safe across 10 prompt types + 200 contrastive unsafe)
  - **License:** check repository LICENSE
  - **Tasks:** classification (over-refusal evaluation). Cite Röttger et al. (2024), NAACL 2024, arXiv:2308.01263.

## C3. JailbreakBench JBB-Behaviors — standardized misuse-behavior set

- **JailbreakBench JBB-Behaviors** — HuggingFace, 2024.
  - **Source:** https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors
  - **Access:** hf datasets; auth_required: false
  - **Schema:** `behaviors` config has 200 rows (100 harmful + 100 benign); `judge_comparison` config has 300 rows. Aligned with OpenAI usage policies; harmful behaviors sourced 18% from AdvBench, 27% from TDC/HarmBench, 55% original
  - **License:** MIT (confirmed on HF dataset card during audit)
  - **Tasks:** classification + generation (jailbreak evaluation grid). Cite Chao et al. (2024), NeurIPS 2024 D&B, arXiv:2404.01318.

## C4. BIPIA — indirect-PI benchmark dataset

- **BIPIA — indirect-PI benchmark dataset** — GitHub, 2023.
  - **Source:** https://github.com/microsoft/BIPIA
  - **Access:** direct (clone repo); auth_required: false
  - **Schema:** 5 application tasks (email QA, web QA, table QA, summarization, code QA) × multiple attack types × position variants
  - **License:** check repository LICENSE
  - **Tasks:** classification (indirect-injection ASR evaluation). Cite Yi et al. (2023), KDD 2025, arXiv:2312.14197.

## C5. InjecAgent — tool-integrated agent injection set

- **InjecAgent — tool-integrated agent injection dataset** — GitHub, 2024.
  - **Source:** https://github.com/uiuc-kang-lab/InjecAgent
  - **Access:** direct (clone repo); auth_required: false
  - **Schema:** 1054 test cases × 17 user tools × 62 attacker tools; attack-intention split: direct-harm vs data-exfiltration
  - **License:** check repository LICENSE
  - **Tasks:** classification (agentic-injection evaluation). Cite Zhan et al. (2024), ACL 2024 Findings, arXiv:2403.02691.
