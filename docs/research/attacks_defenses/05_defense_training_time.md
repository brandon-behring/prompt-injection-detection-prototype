---
title: Training-time defenses
dossier_id: attacks_defenses/05
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '05'
tags:
- attacks
- defenses
related_dossiers: []
---
# Training-time defenses

Defenses that modify model weights via training: alignment, instruction-hierarchy training, structured-query fine-tuning, classifier safeguards trained on synthetic data. Anchors A5 of the research plan.

## E1. Training-time defenses

| Title | Authors (year) | Venue | arXiv/DOI | GitHub | One-line description | Key contribution |
|-------|----------------|-------|-----------|--------|----------------------|------------------|
| Constitutional AI: Harmlessness from AI Feedback | Bai et al. (2022) | arXiv preprint | arXiv:2212.08073 | — | Two-stage training: SL phase (model self-critiques + revises) + RL phase (RLAIF using AI-feedback preference model) governed by a "constitution" of principles | Canonical reference for AI-feedback alignment without per-output human labels; powers Anthropic's harmlessness training |
| The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions | Wallace et al. (2024) | arXiv preprint | arXiv:2404.13208 | — | Synthetic-data fine-tuning teaching the model an explicit privilege hierarchy (system > developer > user > tool) | OpenAI's canonical privilege-aware training; drastically improves robustness to injection types unseen during training |
| Constitutional Classifiers: Defending against Universal Jailbreaks across Thousands of Hours of Red Teaming | Sharma et al. (2025) | arXiv preprint | arXiv:2501.18837 | — | Input/output classifier safeguards trained on a "constitution" defining harmful and harmless content categories | Canonical reference for production-grade classifier-based jailbreak defense; >3000 hours of red-teaming with no universal jailbreak found |
| StruQ: Defending Against Prompt Injection with Structured Queries | Chen et al. (2024) | USENIX Security 2025 | arXiv:2402.06363 | Sizhe-Chen/StruQ | Front-end formats prompts vs data into separate channels; LLM fine-tuned to follow only the prompt channel | Canonical reference for structured-query training-time defense; significantly resists prompt injection with minimal utility loss |
