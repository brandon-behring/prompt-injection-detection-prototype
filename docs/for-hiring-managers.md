---
title: "Project at a glance"
description: "Four questions, ~60 seconds: what problem this project solves, what was found, why to trust the finding, and what the work says about how the candidate thinks."
---

For a slightly longer read, see the [headline table on the
landing page](../index.qmd) or the [one-page executive
summary](../README.md#executive-summary) (absorbed into README per
ADR-078). For an audit-depth path, see the [reading
guide](../READING_GUIDE.md).

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

- **Spec-Driven Development**: 81 immutable Architecture Decision Records
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

The same set of signals indexed against concrete repo evidence:

| Hiring signal | Evidence in the repo | Where to inspect |
|---|---|---|
| Designs fair ML evaluations | LODO source-disjoint splits, OOD/direct separation, undefined-metric handling on single-class slices | [RESULTS.md](../RESULTS.md), [WRITEUP/eval-design](../WRITEUP/eval-design.md) |
| Handles negative results honestly | Pooled OOD failure is the headline (not hidden); below-floor AUROC framed explicitly | [README §Executive summary](../README.md#executive-summary), [WRITEUP_PAPER §4 Results](../WRITEUP_PAPER.md) |
| Methodology before results | 81 ADRs locked before code; SPEC_GREENFIELD pre-flight spec | [decisions/](../decisions/), [SPEC_GREENFIELD.md](../SPEC_GREENFIELD.md) |
| Controls confounds | DeBERTa context-window ablation; null result published | [WRITEUP/model-rungs.md](../WRITEUP/model-rungs.md), [ADR-060](../decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md) |
| Builds reproducible artifacts | Per-row predictions + bootstrap CIs with seed-stability check + T0/T1/T3 cost tiers | [WRITEUP/reproducibility.md](../WRITEUP/reproducibility.md), [evals/](../evals/) |
| Library-first / upstream contribution | eval-toolkit primitives; upstream issues filed before any local workaround | [decisions/library_imports.md](../decisions/library_imports.md), [decisions/upstream_issues.md](../decisions/upstream_issues.md) |
| Writes for multiple audiences | Hiring scan, README, paper, narrative, results-only, ADR trail | Quarto sidebar |
| Audit-class self-discipline | Project-shipped audit validators (audit_value_bindings, audit_citation_alignment); upstream issues filed when the validator's own quality is the gap | [scripts/audit_*.py](../scripts/), [decisions/upstream_issues.md](../decisions/upstream_issues.md) |

## 5. How to review this in 5 minutes

If you want a structured way to assess this beyond the 60-second
scan above, here is a concrete 5-minute review path:

1. **~1 min** — this page (§1–§4): problem framing, result, trust basis, candidate-thinking signals.
2. **~1 min** — [RESULTS.md §Pooled OOD AUPRC](../RESULTS.md): does the random-floor framing hold up; do CIs make sense?
3. **~1 min** — [§3 trust bullets above + WRITEUP/methodology-guarantees](../WRITEUP/methodology-guarantees.md): are the methodology guarantees credible end-to-end?
4. **~1 min** — [WRITEUP/reproducibility.md](../WRITEUP/reproducibility.md): can the artifact actually be re-run at T0 (laptop) / T3 (cloud)?
5. **~1 min** — [WRITEUP/limitations-and-future-work.md](../WRITEUP/limitations-and-future-work.md): does the candidate know what this work does NOT prove?

If anything in step 2 or 3 looks shaky, the [evals/](../evals/)
directory has the raw artifacts: per-fold metrics, bootstrap-CI
sidecars, persisted predictions per row. The [`scripts/audit_*.py`](../scripts/)
audits run on every push (see `.github/workflows/audit-writeup.yml`).

If you want the deeper read, pick a guide:
[WRITEUP_PAPER.md](../WRITEUP_PAPER.md) (academic IMRAD; ~20–25 min) or
[WRITEUP_NARRATIVE.md](../WRITEUP_NARRATIVE.md) (5-act narrative; ~15–20 min)
— both cover the same content + cite the 8 topic spokes
([WRITEUP/](../WRITEUP/)) for deep dives on data decisions, model
details, evaluation design, threshold policy, reference-scorer audit,
methodology guarantees, limitations + future work, and reproducibility.
The full reading-guide is at [`READING_GUIDE.md`](../READING_GUIDE.md).

If you want the supporting analysis, the **Notebooks** sidebar section provides
4 static rendered appendices with frozen output cells: per-cell results,
calibration diagrams, and held-out slice breakdowns. Operators regenerate those
appendix outputs via `make notebooks` against the committed evaluation parquets.
