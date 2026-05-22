---
title: "Data decisions"
description: "Source slate, deduplication discipline, leakage handling, and LODO split structure for the prompt-injection evaluation."
---

# Data decisions

*Deep-dive reference for the methodology in [WRITEUP_PAPER.md](../WRITEUP_PAPER.md) (academic) and [WRITEUP_NARRATIVE.md](../WRITEUP_NARRATIVE.md) (narrative). Pick a guide for the cover narrative; this spoke goes deeper.*

> **How to read this spoke**: For a fast skim, focus on the bolded **Result** subsections + the final §Summary if present. For a full audit, read the methodology paragraphs + the ADR references in headers.

:::{.callout-note}
## Summary

- **Source slate**: 4 positive-attack sources (4707 rows post-dedup) + 2 benign sources (17246 rows) + 5 held-out OOD slices. All sources pinned at HF revision SHAs per ADR-016 + ADR-041.
- **Dedup discipline**: calibrated semantic dedup at cosine 0.80 (encoder `sentence-transformers/all-MiniLM-L6-v2`); label-aware (within-source drop; cross-label preserve); cross-source minimal pairs preserved per ADR-042.
- **Leakage check**: 0 exact-hash overlaps + 0 cosine overlaps at threshold 0.85 across all (train, val, test) per-fold-seed pairs — `evals/leakage_report.json` carries `leakage_clean: True`.
- **Splits structure**: source-disjoint LODO (4-fold; 3 seeds = 12 cells per rung) per ADR-016. Field-standard choice when ≥3 positive sources are available (Fomin 2025, "When Benchmarks Lie").
:::

This spoke covers data-slate decisions — source selection, dedup
discipline, leakage handling, and split structure. For the headline
characterisation that consumes these decisions, see
[WRITEUP_PAPER §4 Results](../WRITEUP_PAPER.md#results) (academic)
or [WRITEUP_NARRATIVE Act 3](../WRITEUP_NARRATIVE.md#act-3-revelation)
(narrative); for the numbers + figures alone see
[RESULTS §1](../RESULTS.md#cross-family-ood-table-auprc).

## 3.1 Why these sources

The data slate locked at Phase 0-02 per ADR-016 (data design bundle):
4 positive-attack sources (LODO training pool) + 2 benign sources +
5 held-out OOD slates. Per-source rationale + post-dedup counts:

**Positive attack sources (LODO training pool)** — each source provides
a stylistically-distinct slice of the prompt-injection space; LODO
ensures held-out generalization on attack style, not just held-out rows:

- `deepset_prompt_injections` — 170 rows (post-dedup; raw 203). Short
  curated direct-injection probes. Earned its place as the
  smallest-but-canonical reference source.
- `lakera_gandalf_ignore_instructions` — 525 rows (raw 777). Formulaic
  "ignore the above" patterns from the Gandalf game; representative of
  the most-common direct-injection style.
- `lakera_mosscap_prompt_injection` — 2362 rows (raw 3000). Longer,
  more diverse Mosscap game attacks; stylistically different from
  Gandalf.
- `hackaprompt` — 1650 rows (raw 2891). Mixed-style adversarial
  attempts from the HackAPrompt competition; many multi-paragraph
  attacks.

Total positive pool post-dedup: **4707 rows**. Cross-source dedup at
cosine threshold 0.80 (encoder:
`sentence-transformers/all-MiniLM-L6-v2`) per ADR-042.

**Benign sources** — provide the negative class (label=0):

- `lmsys_chat_1m` — 7724 rows (raw 10000; ~22 % dedup). User-vs-ChatGPT
  chat logs. Earned its place as a high-volume, stylistically-realistic
  negative source.
- `ultrachat_200k` — 9522 rows (raw 10000; ~5 % dedup). Synthetic
  multi-turn conversations. Provides a benign-text variety class
  `lmsys_chat_1m` doesn't cover (creative writing, structured Q&A).

Total benign pool: **17246 rows**.

**OOD slates** — 5 held-out distributions per ADR-021 NOT used during
training; evaluation-only:

- `notinject` (HF Hub) — synthetic prompt-injection-LIKE-but-benign
  sequences; tests false-positive robustness. All-negative by design.
- `xstest` (HF Hub) — exaggerated safety + jailbreak-as-questions;
  cross-distribution shift from training. Both classes present.
- `jbb_behaviors` (HF Hub) — JailbreakBench harmful-behavior
  elicitations. Both classes present.
- `bipia` (local git repo) — indirect prompt injection via email body
  content. All-positive by source design.
- `injecagent` (local git repo) — multi-turn agentic-flow injections.
  All-positive by source design.

All 11 sources are pinned at HF revision SHAs (where applicable) per
`configs/data/source_manifest.yaml` per ADR-016 + ADR-041.

## 3.2 Dedup — *why this matters more than people think*

Label-blind dedup looks innocuous and is wrong. It removes minimal
pairs — cases where two near-identical texts have *different* labels —
which are exactly the informative examples a classifier needs to learn
the decision boundary. This project uses **calibrated semantic dedup**
(encoder + threshold locked at Phase 0); label-aware (within-source,
drop; cross-label, preserve); cross-source minimal pairs preserved.

Calibration evidence: `evals/dedup_calibration.json` records
`threshold_locked: 0.80` (cosine) for the cross-source
benign-vs-attack pair classifier per ADR-042. Encoder:
`sentence-transformers/all-MiniLM-L6-v2` revision
`c9745ed1d9f207416be6d2e6f8de32d1f16199bf`. 50-pair golden holdout
(25 banded + 25 random) at SHA-256
`250eb96…001f3`; at locked threshold: tp=12, fp=0, tn=32, fn=6;
FPR=0, FNR=33.3 %. Operator follow-up gated at v1.0.0: raise
`human_verified_pct` from 0 to 100 by manually examining
`data/dedup_holdout.jsonl` and confirming each LLM-pre-label is correct.

See eval-toolkit `text_dedup` methodology (see [README](https://github.com/brandon-behring/eval-toolkit#readme))
for the general framework.

## 3.3 Leakage handling + reference-scorer audit

Three checks for in-pool leakage, plus a separate reference-scorer
audit:

1. **Exact-hash overlap** — no test row's hash appears in train.
2. **High-cosine overlap** — no test row has cosine ≥ 0.85 (locked
   per ADR-016 Q3) to any train row of the same label.
3. **Cross-source benign dedup** — locked at *after-split* per
   ADR-043 (post-split leakage cleanup). The rule prevents fold-
   leakage failures when within-source dedup leaves benign duplicates
   that survive the split.
4. **Reference-scorer training-overlap audit** — `[LOCKED]` any
   external reference scorer gets its publicly-named training datasets
   crossed with project sources. Where disclosure is only at category
   level, the audit shifts to fold-pattern + scope-mismatch analysis —
   see [`../EVIDENCE.md`](../EVIDENCE.md) §1-2.

**Result**: 0 exact-hash overlaps + 0 cosine overlaps at threshold
0.85 across all (train, val, test) per-fold-seed pairs —
`evals/leakage_report.json` carries `leakage_clean: True`. The
eval-toolkit leakage check suite operationalises the 8-type taxonomy
from Kapoor & Narayanan 2023 (arXiv:2207.07048) — 294 non-replicating
papers traced to leakage — via reference implementations:
`ExactDuplicateCheck`, `NearDuplicateCheck`, `NormalizedFormLeakageCheck`,
`CrossSplitLeakageCheck`, `LabelConflictCheck`, `GroupLeakageCheck`,
`TemporalLeakageCheck`. See
eval-toolkit `leakage` methodology (see [README](https://github.com/brandon-behring/eval-toolkit#readme)).

## 3.4 Splits

**Result**: splits structure locked at *source-disjoint LODO* (4-fold;
3 seeds = 12 cells per rung) per ADR-016. When ≥3 positive sources are
available, source-disjoint LODO is the field-standard choice (Fomin
2025, "When Benchmarks Lie"). See
eval-toolkit `splits` methodology (see [README](https://github.com/brandon-behring/eval-toolkit#readme)).

## Cross-references

- **Reference-scorer contamination audit** → [`reference-scorer-audit.md`](./reference-scorer-audit.md)
- **Statistical apparatus that consumes these splits** → [`eval-design.md`](./eval-design.md)
- **Per-row predictions schema + provenance** → [`reproducibility.md`](./reproducibility.md)

**Linked ADRs**: ADR-016 (data design bundle), ADR-021 (slice
aggregation), ADR-041 (Phase 1 implementation), ADR-042 (dedup
calibration), ADR-043 (post-split leakage cleanup).
