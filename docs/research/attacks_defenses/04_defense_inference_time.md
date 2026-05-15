---
title: Inference-time defenses
dossier_id: attacks_defenses/04
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '04'
tags:
- attacks
- defenses
related_dossiers: []
---
# Inference-time defenses

Defenses applied at inference without retraining the base model: input pre-processing, classifier filtering, decoding-time interventions, structured prompts. Anchors A4 of the research plan.

## D1. Inference-time defenses

| Title | Authors (year) | Venue | arXiv/DOI | GitHub | One-line description | Key contribution |
|-------|----------------|-------|-----------|--------|----------------------|------------------|
| Defending Against Indirect Prompt Injection Attacks With Spotlighting | Hines et al. (2024) | arXiv preprint | arXiv:2403.14720 | — | Three prompt-engineering instantiations (delimiting, datamarking, encoding) that distinguish trusted vs untrusted input regions | Canonical reference for prompt-engineering-only indirect-injection defense; reduces ASR from >50% to <2% on GPT family |
| Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations | Inan et al. (2023) | arXiv preprint | arXiv:2312.06674 | meta-llama/PurpleLlama | Llama2-7B fine-tuned as a binary / multi-class safety classifier with customizable taxonomy | Open-source production-grade input/output safety classifier; subsequent Llama Guard 2 / 3 / 3-Vision iterations |
| NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications with Programmable Rails | Rebedea et al. (2023) | EMNLP 2023 Demo | arXiv:2310.10501 | NVIDIA-NeMo/Guardrails | Open-source toolkit for input / dialog / retrieval / output rails defined in a Colang DSL, runtime-independent of the underlying LLM | Canonical programmable-guardrails framework; widely-deployed industry baseline for inference-time safety controls |
| SmoothLLM: Defending Large Language Models Against Jailbreaking Attacks | Robey et al. (2023) | arXiv preprint | arXiv:2310.03684 | arobey1/smooth-llm | Randomized character-level perturbations of input prompt; aggregate predictions across copies | Exploits brittleness of GCG-style suffixes to character perturbations; SOTA defense against GCG / PAIR / RandomSearch |
| Baseline Defenses for Adversarial Attacks Against Aligned Language Models | Jain et al. (2023) | arXiv preprint | arXiv:2309.00614 | — | Three-baseline study: perplexity-filtering detection, paraphrasing/retokenization preprocessing, adversarial training | Canonical reference for "simple" defense baselines; perplexity filter catches gibberish suffixes (GCG) but misses semantic jailbreaks |
| SafeDecoding: Defending against Jailbreak Attacks via Safety-Aware Decoding | Xu et al. (2024) | ACL 2024 Main | arXiv:2402.08983 | uw-nsl/SafeDecoding | Decoding-time intervention that boosts probability of safety-disclaimer tokens in the candidate distribution | Token-level inference-time defense without retraining; effective across 6 jailbreak attacks × 5 LLMs |
