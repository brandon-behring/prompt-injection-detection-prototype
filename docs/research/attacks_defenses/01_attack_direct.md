---
title: Direct prompt-injection attacks
dossier_id: attacks_defenses/01
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '01'
tags:
- attacks
- defenses
related_dossiers: []
---
# Direct prompt-injection attacks

User-channel attacks: malicious instructions arrive in the prompt itself. Anchors A1 of the research plan.

## A1. Direct prompt-injection attacks

| Title | Authors (year) | Venue | arXiv/DOI | GitHub | One-line description | Key contribution |
|-------|----------------|-------|-----------|--------|----------------------|------------------|
| Ignore Previous Prompt: Attack Techniques For Language Models | Perez & Ribeiro (2022) | NeurIPS ML Safety Workshop 2022 (Best Paper) | arXiv:2211.09527 | agencyenterprise/PromptInject | First systematic study of "ignore previous instructions" goal-hijacking and prompt-leaking on GPT-3 | Establishes the canonical direct-injection attack pattern; PromptInject framework for handcrafted adversarial prompt composition |
| Jailbroken: How Does LLM Safety Training Fail? | Wei, Haghtalab & Steinhardt (2023) | NeurIPS 2023 | arXiv:2307.02483 | — | Diagnostic analysis of jailbreak failure modes; tests SOTA models against curated attacks | Two-failure-mode taxonomy: competing objectives + mismatched generalization; argues safety-capability parity is required |
| Prompt Injection attack against LLM-integrated Applications | Liu et al. (2023) | arXiv preprint | arXiv:2306.05499 | — | Empirical attack study on 36 commercial LLM-integrated applications using the HouYi attack | Demonstrates real-world impact: 31 of 36 applications vulnerable; 10 vendors confirmed (incl. Notion); shifts injection from academic to operational threat |
| Many-shot Jailbreaking | Anil et al. (2024) | NeurIPS 2024 | (no arXiv) | — | Long-context jailbreak using hundreds of in-context demonstrations of jailbroken assistant behavior | Establishes power-law scaling of attack success with shot count; works on 4+ vendor families; canonical reference for long-context-window attack surface |
