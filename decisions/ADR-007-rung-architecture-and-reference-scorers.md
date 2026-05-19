---
adr_id: 007
slug: rung-architecture-and-reference-scorers
title: Methodology rung architecture — trained backbones, LLM-judge reference rungs, Cohen's kappa
date: 2026-05-15
status: Superseded
superseded_by: 015
claim_id: CLAIM-007
claim: The rung slate comprises six trained rungs (DeBERTa-v3 + ModernBERT × {frozen-probe, LoRA, full-FT}) plus two LLM-judge reference rungs (one OpenAI model, one Anthropic model — specific model IDs finalized in Phase 0-03), plus optional existing-classifier baselines (Lakera Guard, ProtectAI LLM-Guard) as reference scorers. Cohen's kappa is computed pairwise across all rungs with bootstrap CIs on each kappa. Library stack — HuggingFace Transformers + PEFT + sentence-transformers; dependencies pinned via uv.lock.
source: SPEC_GREENFIELD.md §Brief row 308 (Q5-C4) + §2 Model rows 330-338
acceptance_criterion: At Phase 3 close, every rung in the slate has been trained (or inference-scored for reference rungs) on the locked train/eval splits; per-row predictions are persisted for every rung × seed × fold; the pairwise kappa matrix is rendered as a heatmap in WRITEUP/reference-scorer-audit.md; LLM-judge calls are reproducible (temp=0; prompt template versioned in repo).
closing_commit: e760faf
references:
  - https://arxiv.org/abs/2111.09543
  - https://arxiv.org/abs/2412.13663
  - https://arxiv.org/abs/2106.09685
  - https://huggingface.co/docs/peft
  - https://arxiv.org/abs/2306.05685
  - https://doi.org/10.1177/001316446002000104
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-007: Methodology rung architecture — trained backbones, LLM-judge reference rungs, Cohen's kappa

## Status

Superseded by ADR-015 (2026-05-15). The Phase 0-01 threat-model walk surfaced that the 2-backbone-with-per-backbone-cap framing produces an irreducible truncation confound on the indirect-injection zero-shot OOD slice; ADR-015 narrows the trained-rung slate to ModernBERT-base only to eliminate the confound. Reference rungs are preserved unchanged. This ADR remains as the historical record of the original rung-architecture decision; ADR-015 is the source of truth for current rung architecture.

## Context

The submission's methodology centerpiece is a rung sweep: which capability layer (frozen vs LoRA vs full-FT, English-default backbone vs long-context backbone) adds what to detection performance, and how do these trained classifiers compare against off-the-shelf reference scorers (LLM-as-judge + existing-classifier baselines)?

A single-backbone, single-rung demo is unsatisfying for a methodology-first submission (per ADR-005 Principle 1). The Q1 fallback ladder (ADR-001) commits to attempting a full 2×3 grid with infra leverage, retreating only if mid-Phase-2 surfaces infeasibility. Adding LLM-as-judge as a reference rung was a step-up beyond the kit's audit-only default — Brandon explicitly accepted the higher ambition given OpenAI + Anthropic API access. Cohen's kappa was added as the pairwise-agreement methodology: it measures agreement *above chance*, which is the correct framing for comparing two binary classifiers under class imbalance (Cohen 1960; Landis & Koch 1977 for interpretive bands cited with caveat — the bands are arbitrary).

## Decision

**Trained-rung slate (6 rungs)**:

- DeBERTa-v3 × {frozen-probe, LoRA, full-FT}
- ModernBERT × {frozen-probe, LoRA, full-FT}

LoRA via HuggingFace PEFT; full-FT and frozen-probe via standard HF Transformers + Trainer. Specific LoRA hyperparameters (r, α, dropout, target modules, lr, epochs, precision, batch, max_len, warmup) deferred to Phase 0-03 (ledger rows 335-337).

**Reference-rung slate (2-N rungs)**:

- LLM-judge: OpenAI model (specific ID — likely GPT-4o or equivalent — finalized Phase 0-03)
- LLM-judge: Anthropic model (specific ID — likely Claude Sonnet/Opus — finalized Phase 0-03)
- Optional: existing-classifier baselines (Lakera Guard, ProtectAI LLM-Guard) — finalized Phase 0-03 contingent on time

LLM-judge calls: temperature=0 (deterministic; multi-seed irrelevant); prompt template versioned in repo and documented; one call per eval row.

**Library stack**: HuggingFace Transformers + PEFT + sentence-transformers; PyTorch backbone; dependencies pinned via uv.lock (kit default ratified).

**Cohen's kappa methodology**:

- Pairwise kappa across all rungs (trained + reference + existing-classifier baselines).
- Bootstrap CIs on each kappa (10K iters; see ADR-006 for protocol).
- Rendered as a heatmap in `WRITEUP/reference-scorer-audit.md` spoke; supports the methodology narrative that high-kappa pairs make correlated errors (e.g., trained-classifier family agrees with itself; LLM-judges disagree with the trained family — suggesting ensemble potential).
- Landis-Koch interpretive bands mentioned once for orientation; not used as headline framing (the bands are arbitrary).

**Backbone-length-cap interaction** (per ADR-010): each backbone is judged on its native context window (512 for DeBERTa-v3; 8K for ModernBERT). Cross-backbone Δ-AUROC is reported with this caveat in the spoke.

## Consequences

**Positive:**

- 8-rung headline table (6 trained + 2 LLM-judge) gives a rich methodology comparison — backbone-effect, rung-effect, and trained-vs-LLM-judge-effect are all visible.
- Cohen's kappa is the methodology-first move: it quantifies *agreement structure*, not just *who scored higher*. Reveals where rungs make correlated errors.
- LLM-judge as reference rung pre-empts the reviewer question "did you compare against a strong baseline?" — yes, two of them.
- LLM-judge calls are deterministic (temp=0) so multi-seed protocol from ADR-006 doesn't apply to reference rungs; this controls API budget.
- HF + PEFT stack is library-first (per CLAUDE.md anti-pattern rule); no hand-rolled LoRA implementation.

**Negative / cost:**

- API budget for LLM-judge rungs: plausible eval set ~5K prompts × 2 judges × ~$0.005-$0.02/call ≈ **$50-200 total**. Recorded as assumption A-002 (severity: medium) in assumptions.md. Verification: actual cost tracked end of Phase 3.
- Cohen's kappa per-pair × 8 rungs = 28 pairs to render; the heatmap should be readable but is dense.
- LLM-judge prompt template is methodology-component-with-ADR (per CLAUDE.md anti-pattern rule); template versioning + audit is a Phase 0-03 deliverable.
- Six trained rungs × 3 seeds × ~30 min/training ≈ 9 hours GPU + analysis; tight against Q1 calendar.

**Neutral:**

- Phase 0-03 still walks §2 Model rows 332 (Frozen-probe role — candidate detector vs diagnostic rung — likely both per this ADR), 333 (matched-budget controls), 334 (specific reference scorer model IDs), 335-337 (LoRA hyperparams), 338 (compute budget). This ADR fixes the rung-slate structure and the kappa methodology; the specific model IDs and hyperparams are deferred.

## Alternatives Considered

- **DeBERTa-v3 only (single backbone)**: Cheap; field-standard in deployed prompt-guards. *Rejected because* can't separate backbone-effect from rung-effect; misses the ModernBERT comparison story (8K context vs 512 context).
- **ModernBERT only (single backbone)**: New SOTA. *Rejected because* less prior art for comparability; field-default DeBERTa-v3 must be a baseline.
- **LLM-judge as audit-only, not as detector rung**: Lower API cost. *Rejected because* Brandon explicitly stepped up to reference-rung framing — the API budget is acceptable and the comparison story strengthens.
- **Matthews correlation coefficient (MCC) instead of Cohen's kappa**: MCC handles class imbalance better than naive accuracy. *Rejected because* kappa more naturally answers "do these two raters agree above chance?" which is the methodology framing; MCC could be reported as a supplementary metric in the spoke without competing with kappa for narrative space.
- **Skip LLM-as-judge entirely**: Cleaner reproducibility; lower API cost. *Rejected because* an off-the-shelf strong baseline is a load-bearing comparison point for any detection submission; reviewers expect it.

## References

- DeBERTa-v3 (He et al. 2021) — https://arxiv.org/abs/2111.09543
- ModernBERT (Warner et al. 2024) — https://arxiv.org/abs/2412.13663
- LoRA (Hu et al. 2021) — https://arxiv.org/abs/2106.09685
- HF PEFT documentation — https://huggingface.co/docs/peft
- LLM-as-judge (Zheng et al. 2023) — https://arxiv.org/abs/2306.05685
- Cohen 1960 — Coefficient of Agreement for Nominal Scales — https://doi.org/10.1177/001316446002000104
- Landis & Koch 1977 — Observer Agreement for Categorical Data — https://doi.org/10.2307/2529310 (interpretive bands cited with caveat)
- scikit-learn cohen_kappa_score — https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html
- `docs/research/attacks_defenses/` — Lakera Guard / ProtectAI references
- ADR-005 (methodology principles, especially Principle 1)
- ADR-001 (fallback ladder may drop rungs in the trained slate)
- ADR-006 (bootstrap protocol for kappa CIs)
- ADR-013 (per-row prediction persistence pre-teardown)
