---
title: Indirect / agentic benchmarks
dossier_id: benchmarks/02
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '02'
tags:
- evals
- benchmarks
related_dossiers: []
---
# Indirect / agentic benchmarks

Benchmarks where attack content arrives via retrieved/embedded/tool content. Anchors A2.

## B1. Indirect / agentic benchmarks

| Title | Authors (year) | Venue | arXiv/DOI | GitHub | One-line description | Key contribution |
|-------|----------------|-------|-----------|--------|----------------------|------------------|
| Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models | Yi et al. (2023) | KDD 2025 | arXiv:2312.14197 | microsoft/BIPIA | First benchmark for indirect prompt injection: 5 application tasks (email QA, web QA, table QA, summarization, code QA) × multiple attack types × position variants | Canonical reference for indirect-PI evaluation; demonstrates universal vulnerability with ASRs up to 80% on GPT-4 in unmitigated configurations |
| AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents | Debenedetti et al. (2024) | NeurIPS 2024 D&B Track | arXiv:2406.13352 | ethz-spylab/agentdojo | Extensible environment with 97 realistic tasks (email, banking, travel) and 629 security test cases; supports adaptive attacks and defenses | Canonical reference for agentic-LLM injection evaluation; SOTA LLMs solve <66% of tasks even without attacks |
| InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents | Zhan et al. (2024) | ACL 2024 Findings | arXiv:2403.02691 | uiuc-kang-lab/InjecAgent | Benchmark with 1054 test cases × 17 user tools × 62 attacker tools; categorizes attack intentions into direct harm + data exfiltration | First benchmark dedicated to tool-integrated LLM agent vulnerability; ReAct-prompted GPT-4 vulnerable 24% of the time |
