---
title: Direct-attack benchmarks
dossier_id: benchmarks/01
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '01'
tags:
- evals
- benchmarks
related_dossiers: []
---
# Direct-attack benchmarks

Benchmarks scoring direct prompt-injection / jailbreak attacks. Anchors A1.

## A1. Direct-attack benchmarks

| Title | Authors (year) | Venue | arXiv/DOI | GitHub | One-line description | Key contribution |
|-------|----------------|-------|-----------|--------|----------------------|------------------|
| Ignore This Title and HackAPrompt: Exposing Systemic Vulnerabilities of LLMs through a Global Scale Prompt Hacking Competition | Schulhoff et al. (2023) | EMNLP 2023 | arXiv:2311.16119 | — | Global prompt-hacking competition collecting 600K+ adversarial prompts on GPT-3, FlanT5-XXL, ChatGPT | Largest crowdsourced direct-injection dataset; 29-technique taxonomy; canonical reference for human-generated attack diversity |
| JailbreakBench: An Open Robustness Benchmark for Jailbreaking Large Language Models | Chao et al. (2024) | NeurIPS 2024 D&B Track | arXiv:2404.01318 | JailbreakBench/jailbreakbench | Standardized evaluation framework: 100 misuse behaviors aligned with OpenAI usage policies + jailbreak artifact repo + leaderboard | Canonical reference for reproducible jailbreak evaluation; addresses prior literature's incomparability via standardized scoring functions |
| HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal | Mazeika et al. (2024) | ICML 2024 | arXiv:2402.04249 | centerforaisafety/HarmBench | Large-scale benchmark: 18 red-team methods × 33 target LLMs; standard + contextual + multimodal behaviors | Canonical automated-red-team evaluation framework; introduces efficient adversarial-training method that improves robustness across attacks |
