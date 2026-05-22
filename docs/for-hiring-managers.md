---
title: "Project at a glance"
description: "Four questions, ~60 seconds: what problem this project solves, what was found, why to trust the finding, and what the work says about how the candidate thinks."
---

# Project at a glance

Four questions, ~60 seconds.

For a slightly longer read, see the [headline table on the
landing page](../index.qmd) or the [one-page executive
summary](../EXECUTIVE_SUMMARY.md). For an audit-depth path, see
the [reading guide](../READING_GUIDE.md).

## 1. What problem does this project solve?

**Prompt injection** is untrusted text trying to override the instructions an LLM system is supposed to follow ("ignore previous instructions and...").

The naive ask is "build a detector." The real question is: *do these detectors
actually generalize to attacks they did not see during training?* Most public
benchmarks score detectors on attacks similar to their training data; that
overstates production safety. This project builds an out-of-distribution (OOD)
evaluation harness and asks the harder question honestly.

## 2. What did the candidate find?

**The honest result is two-sided: direct detection works better; cross-family generalization fails.**

**OOD contrast**

| Detector | Pooled OOD AUPRC | Interpretation |
|---|---:|---|
| ModernBERT frozen probe | **0.364** vs random floor **0.374** | best in-house score, still not a success claim |
| ModernBERT LoRA | 0.293 (AUROC 0.383 below 0.5 floor) | trained adapter is anti-correlated with cross-family attack class --- lexical overfitting + slate-induced label-relevance inversion |
| TF-IDF + LR | 0.291 (AUROC 0.371 also below 0.5 floor) | classical floor, roughly tied with LoRA; same mechanism |

**The deeper failure** (one sentence): in-pool AUROC 0.99 collapses to 0.38
cross-family --- LoRA + TF-IDF both fall below the 0.5 random floor (CIs
clear the wrong side) while the frozen probe holds at 0.515; the
direct-injection lexical signal both detectors learned is *anti-correlated*
with cross-family attack class on this slate.

**Direct detection check**

| Detector | Balanced direct+benign validation | Interpretation |
|---|---:|---|
| ModernBERT LoRA | AUPRC **0.974**, AUROC **0.993**, recall@0.5 **0.934** | strongest direct-pattern detector |
| TF-IDF + LR | AUPRC 0.971, AUROC 0.992, recall@0.5 0.930 | lexical direct baseline is also strong |
| ModernBERT frozen probe | AUPRC 0.653, AUROC 0.907, recall@0.5 0.849 | weaker ranking, still discriminative |

| Detector | Held-out direct-source recall@0.5 | Interpretation |
|---|---:|---|
| ModernBERT frozen probe | **0.641** | best direct-source holdout recall |
| ModernBERT LoRA | 0.625 | similar direct-source recall, but worse pooled OOD ranking |
| ModernBERT full fine-tune\*\* | 0.558 | lower direct-source holdout recall |

\*\* Full-FT shows LODO direct-source data only (24 Phase 2 predictions); the
comparable pooled OOD inference was **not run** (Phase 5 X11 crash, see
[ADR-075](../decisions/ADR-075-full-ft-ood-drop-rationale-unified-narrative.md)).
Full-FT is absent from the OOD contrast table above for that reason.

The held-out direct-source test is all-positive, so false positives, AUPRC,
and AUROC are omitted there. The context-window follow-up was also a null
result: the v1.1.2 DeBERTa-v3-base ablation produced essentially identical OOD
performance under two truncation strategies, so the gap is backbone-dominant,
not a context-window issue.

See [RESULTS](../RESULTS.md) for the direct, OOD, and ablation tables.

## 3. Why should I trust the finding?

- **Held-out evaluation, not training-set performance**:
  leave-one-dataset-out (LODO) splits ensure the test slate is unseen during
  training. No published benchmark numbers borrowed.
- **Direct and OOD results separated**: validation direct+benign AUPRC shows whether the detector learned the basic pattern; pooled OOD AUPRC shows whether that pattern transfers to new attack families.
- **Statistical apparatus, not point estimates**: every reported AUPRC carries a 95% bootstrap confidence interval (an uncertainty band); figures show CI overlap so weak claims are visible.
- **Honest single-class slice handling**: when a slice has only positives or
  only negatives (BIPIA, InjecAgent, NotInject), undefined metrics are omitted
  from summary tables instead of silently filled with zeros.

## 4. What does this say about how the candidate thinks?

- **Spec-Driven Development**: 78 immutable Architecture Decision Records
  (ADRs) lock methodology choices *before* code is written. Browse
  [decisions/](../decisions/) for the justification trail.
- **Confound-control discipline**: when the headline result raised the natural
  follow-up question (*does a bigger context window fix the OOD gap?*), the
  candidate designed a controlled ablation. The result was a publishable null.
  See [ADR-060](../decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md)
  and [ADR-063](../decisions/ADR-063-deberta-ablation-v1-1-2-execution-and-slot-shift.md).
- **Library-first invariant**: shared evaluation primitives live in upstream
  libraries (`eval-toolkit`, `runpod-deploy`, `research_toolkit`); local code
  is project-specific glue. See [`decisions/library_imports.md`](../decisions/library_imports.md).

If you want the deeper read, the [WRITEUP hub](../WRITEUP.md) carries the cover
narrative and links to 8 topic spokes: data decisions, model details,
evaluation design, threshold policy, reference-scorer audit, methodology
guarantees, limitations and future work, and reproducibility. The full
reading-guide is at [`READING_GUIDE.md`](../READING_GUIDE.md).

If you want the supporting analysis, the **Notebooks** sidebar section provides
4 static rendered appendices with frozen output cells: per-cell results,
calibration diagrams, and held-out slice breakdowns. Operators regenerate those
appendix outputs via `make notebooks` against the committed evaluation parquets.
