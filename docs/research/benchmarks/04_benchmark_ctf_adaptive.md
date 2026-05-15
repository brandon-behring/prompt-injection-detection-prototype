---
title: CTF / red-team / adaptive benchmarks
dossier_id: benchmarks/04
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '04'
tags:
- evals
- benchmarks
related_dossiers: []
---
# CTF / red-team / adaptive benchmarks

Real-world adaptive challenge environments — humans-as-attackers. Anchors A4.

## D1. CTF / red-team / adaptive benchmarks

| Title | Authors (year) | Venue | arXiv/DOI | GitHub | One-line description | Key contribution |
|-------|----------------|-------|-----------|--------|----------------------|------------------|
| Tensor Trust: Interpretable Prompt Injection Attacks from an Online Game | Toyer et al. (2023) | ICLR 2024 | arXiv:2311.01011 | HumanCompatibleAI/tensor-trust | 126K+ prompt-injection attacks + 46K human-generated defenses, collected via an online attack-defense game | Largest dataset of human-generated adversarial examples for instruction-following LLMs; benchmark for prompt extraction + prompt hijacking |
| LLMail-Inject: A Dataset from a Realistic Adaptive Prompt Injection Challenge | Abdelnabi et al. (2025) | arXiv preprint | arXiv:2506.09956 | — | Dataset from a Microsoft-hosted email-context adaptive PI challenge; LLM-based mail-assistant scenario | Canonical reference for adaptive PI in agentic email contexts; companion to Microsoft's BIPIA work; project's `LLMail` slice draws on this data |
