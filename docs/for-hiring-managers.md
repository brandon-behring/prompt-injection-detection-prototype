---
title: "For hiring managers in a hurry"
description: "Four questions, 60 seconds. What problem this project solves, what was found, why to trust it, and what it says about how the candidate thinks."
---

# For hiring managers in a hurry

Four questions, ~60 seconds. If you have 5 more minutes after this, jump to the [headline table on the landing page](../index.qmd) or the [one-page executive summary](../EXECUTIVE_SUMMARY.md). If you're a technical reviewer instead, see the [reading guide](../READING_GUIDE.md) for the audit-depth path.

## 1. What problem does this project solve?

**Prompt injection** is untrusted text trying to override the instructions an LLM system is supposed to follow ("ignore previous instructions and..."). The naive ask is "build a detector." The real question is: *do these detectors actually generalize to attacks they did not see during training?* Most public benchmarks score detectors on attacks similar to their training data; that overstates production safety. This project builds an out-of-distribution (OOD) evaluation harness and asks the harder question honestly.

## 2. What did the candidate find?

**The honest result is mostly negative.** On the pooled OOD slate (five held-out attack and benign sources), the best in-house detector — a frozen probe over ModernBERT-base — scored **AUPRC 0.364** versus a random-ranking floor of **0.374**. None of the trained detectors clearly beat the random floor. A v1.1.2 follow-up ablation also confirmed that switching to a different short-context backbone (DeBERTa-v3-base) with two truncation strategies produced **essentially identical** OOD performance — so the gap is **backbone-dominant**, not a context-window issue. See [RESULTS §1 + §1B](../RESULTS.md) for the per-detector and per-strategy tables.

## 3. Why should I trust the finding?

- **Held-out evaluation, not in-sample**: leave-one-dataset-out (LODO) splits ensure the test slate is unseen during training. No published benchmark numbers borrowed.
- **Statistical apparatus, not point estimates**: every reported AUPRC carries a 95% bootstrap confidence interval; figures show CI overlap so weak claims are visible.
- **Honest single-class slice handling**: when a slice has only positives or only negatives (BIPIA, InjecAgent, NotInject), AUPRC is undefined and reported as N/A — not silently zero-filled.

## 4. What does this say about how the candidate thinks?

- **Spec-Driven Development**: 60+ immutable Architecture Decision Records (ADRs) lock methodology choices *before* code is written. Each ADR carries context, decision, alternatives considered, consequences. Browse [decisions/](../decisions/) — every choice has a justification you can argue with.
- **Confound-control discipline**: when the headline result raised the natural follow-up question (*does a bigger context window fix the OOD gap?*), the candidate designed a controlled ablation (chunk-and-average vs head-truncation), not a hand-wave. Result was a publishable null. See [ADR-060](../decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md) + [ADR-063](../decisions/ADR-063-deberta-ablation-v1-1-2-execution-and-slot-shift.md).
- **Library-first invariant**: shared evaluation primitives (bootstrap CIs, calibration, leakage detection) live in dedicated upstream libraries (`eval-toolkit`, `runpod-deploy`, `research_toolkit`); local code is project-specific glue only. See [`decisions/library_imports.md`](../decisions/library_imports.md).

If you want the deeper read, the [WRITEUP hub](../WRITEUP.md) carries the cover narrative and links to 8 topic spokes (data decisions, model details, evaluation design, threshold policy, reference-scorer audit, methodology guarantees, limitations and future work, reproducibility). The full reading-guide is at [`READING_GUIDE.md`](../READING_GUIDE.md).
