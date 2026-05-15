---
adr_id: 008
slug: data-scope-public-only-hybrid-splits
title: Data scope — public-only sources, hybrid splits, NotInject inclusion (brief-level lock)
date: 2026-05-15
status: Accepted
claim_id: CLAIM-008
claim: Training and evaluation data come from public sources only (HuggingFace-hosted; dataset revisions pinned by SHA at lock time); splits are hybrid (source-disjoint Leave-One-Dataset-Out for OOD slate + random k-fold within in-distribution sources); licenses are mixed and documented per source (full audit deliverable in Phase 0-02); NotInject-style benign-trigger hard negatives are included in the OOD slate to test over-defense per the InjecGuard 2024 methodology.
source: SPEC_GREENFIELD.md §Brief row 308 (Q5-C5) + §1 Data rows 323-329
acceptance_criterion: Phase 0-02 produces a full source-slate manifest (per-source row counts, license, role, HF revision SHA); Phase 1 leakage scan confirms no train-eval overlap above thresholds documented in evals/leakage_report.json; the OOD slate includes a NotInject-equivalent benign-trigger slice.
closing_commit: e760faf
references:
  - https://huggingface.co/datasets/deepset/prompt-injections
  - https://huggingface.co/datasets/Lakera/gandalf_ignore_instructions
  - https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset
  - https://huggingface.co/datasets/leolee99/NotInject
  - https://arxiv.org/abs/2410.22770
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-008: Data scope — public-only sources, hybrid splits, NotInject inclusion (brief-level lock)

## Status

Accepted (2026-05-15)

## Context

Brandon stated during Q4 that "the most important decisions may end up being about choosing the right training data and the right evaluation data sets — and it may be doing that right means the models look worse because they are evaluated honestly." This makes data-design decisions load-bearing under ADR-005 Principle 2 (honest evaluation preferred). The Q5-C5 walk surfaces brief-level constraints; the methodology-level specifics (which datasets, what dedup encoder, what split ratios) are deferred to Phase 0-02.

The dossier at `docs/research/datasets/` documents the public training-positives candidates (deepset, Lakera/gandalf, Lakera/mosscap, HackAPrompt) and the OOD eval candidates (NotInject, XSTest, JBB-Behaviors, BIPIA, InjecAgent). A training-benigns slate is not in the dossier and is a Phase 0-02 gap (plausible candidates: LMSYS-Chat-1M, ShareGPT, ultrachat).

## Decision

**Source-slate scope**: public-only. All datasets are HuggingFace-hosted (or GitHub-cloneable for repo-based sources like XSTest, BIPIA, InjecAgent). Closed-source / proprietary datasets are banned per ADR-011 (methodology guarantees).

**HF dataset revision pinning**: pin by SHA at lock time. Floating `revision="main"` is rejected — reproducibility floor matches CLAUDE.md library-first discipline.

**Splits structure**: hybrid.

- **Source-disjoint Leave-One-Dataset-Out (LODO)** for the OOD slate — at least one full dataset reserved as never-seen-in-training.
- **Random k-fold** within in-distribution sources (specific k = Phase 0-02 decision; likely 5-fold given typical eval-toolkit conventions).
- Cross-source benign dedup applied **before split** to prevent near-duplicate leakage (final ordering finalized in Phase 0-02 per ledger row 326).

**License handling**: mixed licenses documented per source. License audit is a Phase 0-02 deliverable. Datasets with restrictive terms (e.g., CC-BY-NC or research-only) are flagged; if unworkable, the slate shrinks.

**NotInject-style benign-trigger hard negatives** are included in the OOD slate to test over-defense (InjecGuard 2024 methodology). This is the move that explicitly invites honest-evaluation degradation per ADR-005 Principle 2: expected effect is *lower* headline numbers than within-distribution evaluation would show, and that is the right framing.

**Deferred to Phase 0-02**: specific source-slate composition; benign training pool (LMSYS-Chat-1M / ShareGPT / ultrachat / other); dedup encoder + threshold (likely calibrated MiniLM ≈ 0.80 per kit hint); cross-source benign dedup ordering (before-split lean); benign subsample ceilings per source; truncation policy for inputs > length cap.

## Consequences

**Positive:**

- Reproducibility floor: pinned HF revisions + public-only sources + license docs means any reviewer can re-fetch and re-run.
- LODO splits prevent the "benchmarks lie" failure mode (Fomin 2025): a model that exploits source-specific artefacts is exposed by LODO when those artefacts vanish in held-out sources.
- NotInject inclusion is the methodology-signature move — explicitly invites worse-but-honest evaluation per ADR-005 Principle 2. Reviewers see this as competent scoping, not as a methodology mistake.
- Phase 0-02 work is well-scoped: source slate, benign pool, dedup specifics, truncation policy, license audit — each a tractable sub-decision.

**Negative / cost:**

- License audit work (Phase 0-02) is real — must verify HackAPrompt, XSTest, BIPIA, InjecAgent licenses on each repo/dataset card; if any are restrictive, the slate shrinks.
- LODO splits typically produce wider CIs than within-distribution splits (less data per fold). The estimation-over-testing stance (ADR-006) means these wider CIs are reported honestly, not hidden.
- Training-benigns slate selection is a Phase 0-02 gap; bad benign-pool choices (e.g., wrong domain) would degrade in-distribution performance unrelated to detection capability.

**Neutral:**

- Phase 0-02 walks rows 322 (truncation policy), 323 (specific source selection), 325 (dedup encoder+threshold), 326 (benign dedup ordering), 329 (subsample ceilings). This ADR fixes the brief-level scope; the methodology-level specifics remain open.

## Alternatives Considered

- **Public + LLM-generated training augmentation**: Adversarial variants via OpenAI/Anthropic API. *Rejected* (at the brief level — could be revisited in Phase 0-02 as an OOD-only augmentation). Distribution-shift risk + API cost; default to public-real data.
- **Random splits only (no LODO)**: Easier; tighter CIs. *Rejected because* less honest about OOD generalization; benchmarks-lie risk.
- **Single hold-out dataset (not LODO)**: Simpler than LODO. *Rejected because* one held-out source doesn't characterize generalization across the source-distribution space; LODO across ≥2 OOD sources is the credible move.
- **No NotInject inclusion**: Higher headline numbers; smaller OOD slate. *Rejected because* exactly contradicts ADR-005 Principle 2; missing the over-defense story is missing the most-current methodology stake in the literature.

## References

- deepset/prompt-injections — https://huggingface.co/datasets/deepset/prompt-injections
- Lakera/gandalf_ignore_instructions — https://huggingface.co/datasets/Lakera/gandalf_ignore_instructions
- Lakera/mosscap_prompt_injection — https://huggingface.co/datasets/Lakera/mosscap_prompt_injection
- HackAPrompt (Schulhoff et al. 2023, EMNLP) — https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset + https://arxiv.org/abs/2311.16119
- NotInject / InjecGuard (Li & Liu 2024) — https://huggingface.co/datasets/leolee99/NotInject + https://arxiv.org/abs/2410.22770
- XSTest (Röttger et al. 2024 NAACL) — https://arxiv.org/abs/2308.01263
- JBB-Behaviors (Chao et al. 2024 NeurIPS D&B) — https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors + https://arxiv.org/abs/2404.01318
- BIPIA (Yi et al. 2023) — https://github.com/microsoft/BIPIA + https://arxiv.org/abs/2312.14197
- InjecAgent (Zhan et al. 2024 ACL) — https://github.com/uiuc-kang-lab/InjecAgent + https://arxiv.org/abs/2403.02691
- HuggingFace datasets revision pinning — https://huggingface.co/docs/datasets/loading#load
- `docs/research/datasets/01_train_positives.md`
- `docs/research/datasets/03_ood_eval.md`
- ADR-005 (Principle 2 — honest evaluation preferred; rationale for NotInject)
- ADR-011 (methodology guarantees — closed-source dataset ban)
