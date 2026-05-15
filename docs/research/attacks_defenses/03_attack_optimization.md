---
title: Optimization-based attacks
dossier_id: attacks_defenses/03
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '03'
tags:
- attacks
- defenses
related_dossiers: []
---
# Optimization-based attacks

Gradient-, search-, or LLM-driven generation of adversarial suffixes / prompts. Anchors A3 of the research plan.

## C1. Optimization-based attacks

| Title | Authors (year) | Venue | arXiv/DOI | GitHub | One-line description | Key contribution |
|-------|----------------|-------|-----------|--------|----------------------|------------------|
| Universal and Transferable Adversarial Attacks on Aligned Language Models | Zou et al. (2023) | arXiv preprint | arXiv:2307.15043 | llm-attacks/llm-attacks | Greedy Coordinate Gradient (GCG): replace one token at a time in adversarial suffix using gradient-informed candidate selection | Canonical reference for gradient-based adversarial suffixes; demonstrates transferability across open and black-box models including ChatGPT, Bard, Claude |
| AutoDAN: Generating Stealthy Jailbreak Prompts on Aligned Large Language Models | Liu et al. (2024) | ICLR 2024 | arXiv:2310.04451 | SheltonLiu-N/AutoDAN | Hierarchical genetic-algorithm jailbreak generator initialized from handcrafted prompt prototypes | Stealthy attacks (low perplexity, semantically coherent) defeat perplexity-based detection that catches GCG; canonical genetic-algorithm jailbreak |
| Jailbreaking Black Box Large Language Models in Twenty Queries | Chao et al. (2023) | arXiv preprint | arXiv:2310.08419 | patrickrchao/JailbreakingLLMs | PAIR (Prompt Automatic Iterative Refinement): attacker LLM iteratively refines candidate jailbreaks using in-context history | Black-box query-efficient attack: typically <20 queries vs ~10K for GCG; canonical reference for LLM-driven jailbreak generation |
| Tree of Attacks: Jailbreaking Black-Box LLMs Automatically | Mehrotra et al. (2023) | NeurIPS 2024 | arXiv:2312.02119 | RICommunity/TAP | Tree-of-thoughts attack search with pruning of unpromising candidate prompts before sending to target | >80% ASR on GPT-4-Turbo and GPT-4o with <30 queries; canonical pruned-search jailbreak |
