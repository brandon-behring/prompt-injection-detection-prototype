---
title: Training-positives datasets
dossier_id: datasets/01
verification_status: verified
verified_at: '2026-05-15'
confidence_level: high
claim_family: '01'
tags:
- data
- corpora
related_dossiers: []
---
# Training-positives datasets

Public datasets containing prompt-injection / jailbreak attack examples — used as positive-class training material. Anchors `A1`–`A4`.

## A1. deepset/prompt-injections — canonical small training set

- **deepset prompt-injections** — HuggingFace, 2023.
  - **Source:** https://huggingface.co/datasets/deepset/prompt-injections
  - **Access:** hf datasets; auth_required: false
  - **Schema:** 662 rows (546 train + 116 test); 263 prompt injections + 399 legitimate; includes translations + stacked prompts
  - **License:** Apache-2.0
  - **Tasks:** classification (binary safe/unsafe); the project uses this as primary positive-class training data

## A2. Lakera/gandalf_ignore_instructions — real-world ignore-instruction attacks

- **Lakera Gandalf — Ignore Instructions Variant** — HuggingFace, 2023.
  - **Source:** https://huggingface.co/datasets/Lakera/gandalf_ignore_instructions
  - **Access:** hf datasets; auth_required: false
  - **Schema:** ~1000 rows filtered by similarity ≥0.825 to "Ignore all previous instructions" from 279K Gandalf prompts in July 2023
  - **License:** MIT
  - **Tasks:** classification (positive examples — direct PI). Cite Pfister et al. 2025 *Gandalf the Red* (arXiv:2501.07927).

## A3. Lakera/mosscap_prompt_injection — DEF CON 31 CTF data

- **Lakera Mosscap Prompt Injection** — HuggingFace, 2023.
  - **Source:** https://huggingface.co/datasets/Lakera/mosscap_prompt_injection
  - **Access:** hf datasets; auth_required: false
  - **Schema:** 280K rows (mixed labelled/unlabelled), per-prompt level metadata (Level 1-8), columns: level, prompt, answer
  - **License:** MIT
  - **Tasks:** classification (mixed positive/negative); larger sibling to gandalf_ignore_instructions

## A4. HackAPrompt — global-competition attack dataset

- **HackAPrompt Dataset** — HuggingFace, 2023.
  - **Source:** https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset
  - **Access:** hf datasets; auth_required: false
  - **Schema:** 600K+ adversarial prompts collected against GPT-3 / FlanT5-XXL / ChatGPT in a global competition; per-prompt success metadata
  - **License:** check dataset card (publication-derived)
  - **Tasks:** classification (positive examples). Cite Schulhoff et al. (2023), EMNLP 2023, arXiv:2311.16119
