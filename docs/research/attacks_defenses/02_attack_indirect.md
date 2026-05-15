---
title: Indirect / agentic prompt-injection attacks
dossier_id: attacks_defenses/02
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '02'
tags:
- attacks
- defenses
related_dossiers: []
---
# Indirect / agentic prompt-injection attacks

Attacks where the malicious instruction reaches the LLM via embedded / retrieved / tool-mediated content — not directly from the user. Anchors A2 of the research plan.

## B1. Indirect / agentic prompt-injection attacks

| Title | Authors (year) | Venue | arXiv/DOI | GitHub | One-line description | Key contribution |
|-------|----------------|-------|-----------|--------|----------------------|------------------|
| Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection | Greshake et al. (2023) | ACM AISec 2023 | arXiv:2302.12173 | — | Threat-model paper introducing indirect prompt injection through retrieved/embedded content (web pages, documents, emails) | Canonical reference for the indirect-injection threat model; "data and instructions are blurred"; comprehensive attack-surface taxonomy |
| PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models | Zou et al. (2024) | USENIX Security 2025 | arXiv:2402.07867 | sleeepeer/PoisonedRAG | First systematic knowledge-corruption attack on RAG: inject 5 malicious texts per target question into a knowledge database | Establishes RAG knowledge bases as a practical attack surface; demonstrates existing defenses are insufficient |
