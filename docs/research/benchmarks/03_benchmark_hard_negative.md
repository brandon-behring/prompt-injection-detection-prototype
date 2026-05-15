---
title: Hard-negative and over-refusal benchmarks
dossier_id: benchmarks/03
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '03'
tags:
- evals
- benchmarks
related_dossiers: []
---
# Hard-negative and over-refusal benchmarks

Datasets that probe over-defense — benign-but-superficially-suspicious inputs that well-calibrated models should NOT refuse. Anchors A3.

## C1. Hard-negative and over-refusal benchmarks

| Title | Authors (year) | Venue | arXiv/DOI | GitHub | One-line description | Key contribution |
|-------|----------------|-------|-----------|--------|----------------------|------------------|
| InjecGuard: Benchmarking and Mitigating Over-defense in Prompt Injection Guardrail Models | Li & Liu (2024) | arXiv preprint | arXiv:2410.22770 | — | Introduces NotInject (339 benign samples enriched with prompt-injection trigger words) + the InjecGuard guardrail model with the MOF training strategy | Canonical reference for prompt-guard over-defense measurement; demonstrates SOTA models drop near 60% accuracy on trigger-word-enriched benign inputs |
| XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models | Röttger et al. (2024) | NAACL 2024 | arXiv:2308.01263 | paul-rottger/xstest | 250 safe prompts (across 10 prompt types) + 200 contrastive unsafe prompts; tests refuse/comply behavior | Canonical reference for over-refusal evaluation; argues exaggerated safety is lexical-overfitting consequence; widely cited as the over-refusal baseline |
