---
adr_id: "043"
slug: post-split-cross-source-leakage-cleanup
title: Post-split cross-source leakage cleanup — drop train+val rows that exact-match or cosine-near-match test
date: 2026-05-16
status: Accepted
claim_id: CLAIM-043
claim: Phase 1 Commit 5 pipeline surfaced an empirical leakage finding — 6 exact-hash plus 165 cosine greater-than-or-equal-0.85 train-plus-val versus test overlaps across 12 (fold, seed) splits despite ADR-016 Q4 within-source dedup running on every source. Root cause — ADR-016 Q5 specified cross-source dedup ONLY for benigns; positives weren't cross-source-deduped because LODO treats each positive source as a unit. But cross-source positive near-paraphrases DO leak across LODO folds when a near-paraphrase of a held-out-source row exists in another source's train data; this gives the model a "seen it before" advantage on the held-out test. ADR-043 closes this methodology gap by adding a post-split leakage-cleanup pass — for each (fold, seed) split, after make_splits runs but before materialize_splits, src/data/dedup.py::drop_train_test_leakage scans the train+val pool against the held-out test pool; rows in train+val that exact-match or cosine-greater-than-or-equal-0.85-match any test row are dropped (test stays intact). The threshold 0.85 matches the leakage scan threshold in src/data/audit.py::compute_leakage_report (per ADR-016 Q3 hard-locked invariant). The cleanup is implemented as a new function in src/data/dedup.py plus wired through src/data/splits.py::apply_leakage_cleanup which re-partitions the cleaned train+val into the same 80/20 ratio. Pipeline orchestrator scripts/run_data_pipeline.py invokes this between make_splits and materialize_splits. Pre-cleanup pipeline run (without ADR-043) recorded 6 exact plus 165 cosine overlaps; post-cleanup pipeline run records zero overlaps (leakage_clean equals True) honoring ADR-016 Q3 hard-locked leakage invariant. Drop cost — approximately 0.08 percent exact plus 0.17 percent cosine of the train+val pool per split (approximately 171 rows total dropped across 12 splits from a 4707-positive base; test pool unchanged). ADR-043 supersedes the implicit "no cross-source positive dedup" stance in ADR-016 Q5 for the leakage-cleanup step specifically — the rest of ADR-016 Q5 (benign cross-source LMSYS-priority dedup) is preserved unchanged.
source: Phase 1 Commit 5 pipeline run (background task bwgkvoy7z + earlier ble3xg5b2) — leakage_report.json empirical finding
acceptance_criterion: src/data/dedup.py::drop_train_test_leakage exists and drops train+val rows with cosine greater-than-or-equal threshold (default 0.85) to any test row; src/data/splits.py::apply_leakage_cleanup applies the function per (fold, seed) split and re-partitions cleaned train+val at 80/20; scripts/run_data_pipeline.py invokes apply_leakage_cleanup between make_splits and materialize_splits; post-cleanup re-run of pipeline records leakage_clean equals True in evals/leakage_report.json (zero exact plus zero cosine overlaps); ADR-043 cleanup_records counts persist in pipeline log for audit; afterword note added to WRITEUP/limitations-and-future-work.md explaining the methodology gap that ADR-043 closes (cross-source positive near-paraphrase leakage was not anticipated by ADR-016 Q5).
closing_commit: <FILLED-POST-COMMIT>
references:
  - decisions/ADR-016-data-design-bundle.md
  - decisions/ADR-041-phase-1-data-implementation-bundle.md
  - decisions/ADR-042-llm-prelabel-dedup-holdout-bootstrap.md
transcript: transcripts/2026-05-16__phase-1-implementation.md
---

# ADR-043: Post-split cross-source leakage cleanup — drop train+val rows that exact-match or cosine-near-match test

## Status

Accepted (2026-05-16).

## Context

ADR-016 §Q3 locked a hard invariant: "no exact-hash and no high-cosine train-test overlap" via the leakage scan deliverable. ADR-016 §Q4 locked within-source dedup at MiniLM cosine 0.80. ADR-016 §Q5 locked cross-source dedup BUT only for benigns (LMSYS + UltraChat) with LMSYS-priority tiebreak. Cross-source dedup for POSITIVES was not specified because the LODO splits inherently treat each positive source as a unit: the held-out source goes entirely to test; the other 3 positive sources go to train+val. The implicit assumption was that source-level disjointness suffices.

Phase 1 Commit 5 pipeline run surfaced the empirical reality:

| LODO held-out source | Exact-hash overlaps | Cosine ≥0.85 overlaps |
|---|---|---|
| deepset (fold 0) | 0 | 2 per seed × 3 seeds = 6 |
| lakera_gandalf (fold 1) | 0 | 16 per seed × 3 = 48 |
| lakera_mosscap (fold 2) | 0 | 30 per seed × 3 = 90 |
| hackaprompt (fold 3) | 2 per seed × 3 = 6 | 7 per seed × 3 = 21 |
| **Total across 12 splits** | **6** | **165** |

The pattern is structural — cross-source positive near-paraphrases exist (especially between Lakera datasets and HackAPrompt, where successful injection patterns converged). LODO test of, say, mosscap, contains rows whose near-paraphrases sit in HackAPrompt's train data — model has effectively "seen" the test pattern.

This is a methodology gap that needs closing before Phase 2 training begins (training on leaked data would inflate test scores).

## Decision

Add a post-split leakage cleanup pass:

1. `src/data/dedup.py::drop_train_test_leakage(train_val_df, test_df, threshold=0.85)` — scans train+val vs test; drops train+val rows that:
   - Exact-match any test text, OR
   - Have MiniLM cosine ≥ threshold (0.85) to any test row.
   Returns cleaned train+val + per-pair drop records (text snippets + cosines + reason).

2. `src/data/splits.py::apply_leakage_cleanup(splits, threshold=0.85)` — applies `drop_train_test_leakage` to each FoldSeedSplit; re-partitions cleaned train+val at the same 80/20 ratio that `make_splits` used. Returns cleaned splits + per-split cleanup-record list.

3. `scripts/run_data_pipeline.py` invokes `apply_leakage_cleanup` between `make_splits` and `materialize_splits`. Pipeline log records `n_dropped` per (fold, seed) for audit.

Threshold 0.85 matches `compute_leakage_report` in `src/data/audit.py` (per ADR-016 Q3 hard-locked invariant). Test pool is preserved intact (test = held-out source's full deduped pool).

ADR-016 Q5's cross-source BENIGN dedup (LMSYS-priority tiebreak) is preserved unchanged — ADR-043 specifically adds POST-SPLIT cleanup for the train+val vs test text-overlap surface, not before-split cross-source positive dedup. The reason for post-split rather than before-split — LODO splits define the test pool per fold; cross-source positive dedup before splitting would require a notion of "which fold" the dedup applies to (different folds want different rows kept). Post-split per-fold cleanup is clearer.

## Consequences

**Positive:**

- ADR-016 Q3 hard-locked leakage invariant satisfied — post-cleanup `leakage_clean = True` in `evals/leakage_report.json`.
- Methodology gap surfaced + closed in same commit; honest about the empirical finding.
- Cleanup records persist in pipeline log; reviewer can trace exactly which rows were dropped + why.
- Test pool unchanged — LODO held-out source full pool stays intact; only train+val rows that overlap with test are dropped.
- Cost is small — approximately 171 rows out of ~22,000 train+val pool per split (~0.8%).

**Negative / cost:**

- Train pool shrinks slightly (~3.6% of positive pool dropped across 12 splits; benigns unaffected because they aren't in test per LODO design).
- Implicit super-session of ADR-016 Q5's silence on cross-source positive overlap; documented here.
- Adds one O(N²) scan per split (already required by leakage scan); compute envelope unchanged.

**Neutral:**

- ADR-016 Q4 within-source dedup at 0.80 preserved unchanged.
- ADR-016 Q5 cross-source benign dedup at 0.80 with LMSYS-priority preserved unchanged.
- ADR-041 Q7 per-fold parquet materialization layout preserved unchanged (just fewer rows per train+val parquet).

## Alternatives Considered

- **Before-split cross-source positive dedup**: rejected — cross-source positive dedup requires a notion of "which fold" since LODO assigns sources to test differently per fold. Post-split per-fold cleanup is clearer and yields the same end-state with less ambiguity.
- **Tolerate the leakage with disclosure**: rejected — ADR-016 Q3 says "no exact-hash and no high-cosine train-test overlap" is a HARD-LOCKED invariant. Tolerating ~0.25% per-split leakage would compromise the locked invariant.
- **Drop EXACT-hash only; tolerate cosine**: rejected — same hard-lock rationale. The cosine threshold (0.85) is the same as the leakage scan threshold; consistency matters.
- **Higher cleanup threshold (0.90)**: rejected — would leave the 0.85-0.90 band of near-paraphrases as leaked. The 0.85 threshold is the locked leakage threshold per ADR-016 Q3.
- **Drop test rows instead of train rows**: rejected — test = held-out source's full pool per LODO Q1; dropping test rows would shrink the test set and violate LODO's "test on held-out source" definition. Dropping train rows preserves LODO test integrity.

## References

- ADR-016 (data design bundle — Q3 hard-locked leakage invariant + Q4 within-source dedup + Q5 cross-source benign dedup)
- ADR-041 (Phase 1 implementation bundle — Q7 per-fold parquet materialization)
- ADR-042 (LLM-pre-label dedup-holdout bootstrap)

## Transcript

See `transcripts/2026-05-16__phase-1-implementation.md` for the conversation that led to this decision (post-Commit-5 pipeline empirical finding).
