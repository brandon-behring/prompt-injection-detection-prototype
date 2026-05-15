---
title: Threat models and surveys
dossier_id: attacks_defenses/06
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '06'
tags:
- attacks
- defenses
related_dossiers: []
---
# Threat models and surveys

Field-level taxonomies, threat models, surveys, and standards bodies that frame the prompt-injection problem. Anchors A6 of the research plan.

## F1. Threat models and surveys

| Title | Authors (year) | Venue | arXiv/DOI | GitHub | One-line description | Key contribution |
|-------|----------------|-------|-----------|--------|----------------------|------------------|
| Formalizing and Benchmarking Prompt Injection Attacks and Defenses | Liu et al. (2024) | USENIX Security 2024 | arXiv:2310.12815 | — | Formalizes the prompt-injection problem; systematic evaluation of 5 attacks × 10 defenses × 10 LLMs × 7 tasks | Provides a common benchmark vocabulary for quantitatively comparing future PI attacks/defenses |
| The Prompt Report: A Systematic Survey of Prompt Engineering Techniques | Schulhoff et al. (2024) | arXiv preprint | arXiv:2406.06608 | — | 76-page systematic survey: 33-term vocabulary, 58 prompting techniques, PRISMA-method analysis of 1500+ papers | Modern field-wide survey covering prompting and security; companion to HackAPrompt benchmark |
| OWASP Top 10 for Large Language Model Applications | OWASP GenAI Security Project (2024-2025) | OWASP standards body | (no arXiv) | — | Standards-body framework: Top-10 security risks for LLM applications; LLM01 is Prompt Injection (Direct + Indirect) | Canonical industry-standard taxonomy; references in vendor security documentation, regulatory frameworks, and audit checklists |
