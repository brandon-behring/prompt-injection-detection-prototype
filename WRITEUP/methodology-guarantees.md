---
title: "Methodology guarantees"
description: "Three-library tooling split, prediction-persistence pattern, SDD discipline, and library-first invariant for the prompt-injection evaluation."
---

*Deep-dive reference for the methodology in [WRITEUP_PAPER.md](../WRITEUP_PAPER.md) (academic) and [WRITEUP_NARRATIVE.md](../WRITEUP_NARRATIVE.md) (narrative). Pick a guide for the cover narrative; this spoke goes deeper.*

> **How to read this spoke**: For a fast skim, focus on the bolded **Result** subsections + the final §Summary if present. For a full audit, read the methodology paragraphs + the ADR references in headers.

:::{.callout-note}
## Summary

- **Three-library tooling split**: `eval-toolkit` (methodology-aware harness — bootstrap CIs / calibration / leakage / splits / paired-bootstrap), `runpod-deploy` (cloud orchestration), `research_toolkit` (literature dossier pipeline). Each survives across iterations as a durable knowledge artifact.
- **Prediction-persistence pattern [LOCKED]**: 282 prediction parquets persisted per ADR-013 + ADR-021 so downstream threshold / calibration analyses run from artifacts without re-running inference.
- **SDD / ADR process**: 81 ADRs accepted across Phase 0-00 through ADR-081 (ADR-078 EXECUTIVE_SUMMARY absorption + ADR-079 two-guide reader architecture + ADR-080 reviewer-URL-pin numeric correction + ADR-081 frontmatter `status:` field-split narrow-relaxation; v1.3.0 + v1.3.1 + v1.3.2 governance closures); each significant decision locked before code; `SUBMISSION_AUDIT.md` regenerates from ADR frontmatter via `scripts/regenerate_audit.py` (CI hard-gate per ADR-039).
- **Library-first invariant** (project-wide per Phase 4 Q6 reaffirmation): audit `eval-toolkit + runpod-deploy + research_toolkit` BEFORE writing project glue. Upstream gaps land in `decisions/upstream_issues.md` before any local workaround. ADR-047 retrofitted 4 hand-rolls in a single carryforward refactor.
:::

This spoke covers §6 — the three-library tooling split + SDD / ADR
process discipline that backs every methodology claim in the
writeup. For the statistical apparatus that consumes these
guarantees see [`eval-design.md`](./eval-design.md); for headline
results see [WRITEUP_PAPER §4](../WRITEUP_PAPER.md#results) (academic) or [WRITEUP_NARRATIVE Act 3](../WRITEUP_NARRATIVE.md#act-3-revelation) (narrative); for the data tables alone see [RESULTS §1](../RESULTS.md#cross-family-ood-table-auprc).

## 6.1 [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) — methodology-aware evaluation harness

A library-grade harness for binary classification with three tiers:

- **Tier 1: functional core** — `bootstrap_ci`,
  `paired_bootstrap_diff`, `mde_from_ci`, PR-AUC / ROC-AUC / Brier /
  ECE variants, `reliability_curve`, `fit_temperature`,
  `fit_isotonic_calibrator`, `cv_clt_ci`. Pure numpy / scipy /
  sklearn.
- **Tier 2: Protocol-based orchestration** — `Scorer`,
  `SliceAwareScorer`, `LeakageCheck`, `Splitter`,
  `ThresholdSelector`, `DatasetLoader`, `SimilarityStrategy`.
  Opt-in versioning per protocol object.
- **Tier 3: reproducibility scaffolding** — versioned JSON schemas
  (`results.v1.json`, `results_full.v1.json`, `manifest.v1.json`
  through `manifest.v3.json`; v3 adds required `contamination_flags`
  field for the three-state reference-scorer audit taxonomy).
  NeurIPS-aligned manifest capturing seeds, git SHA, data hashes,
  data revisions, GPU info, leakage report, guardrails, source
  roles. See
  eval-toolkit `reproducibility` methodology (see [README](https://github.com/brandon-behring/eval-toolkit#readme))
  for the NeurIPS-checklist field mapping.

Plus methodology notes referenced from the
[eval-toolkit README](https://github.com/brandon-behring/eval-toolkit#readme)
covering leakage, splits, thresholds, calibration, comparison,
bootstrap, length stratification, text dedup, versioning, fairness,
reproducibility, and testing.

*Why eval lives as a separate library*: it survives across
iterations, it accumulates methodology curriculum as a durable
knowledge artifact, and versioned JSON schemas let downstream parsers
gate on format changes. Reuse is across projects, not just within
this project.

## 6.2 [runpod-deploy](https://github.com/brandon-behring/runpod-deploy) — cloud orchestration

Cloud orchestration for training and evaluation runs on rented GPUs.
*Why deployment is a separate concern*: cost-bearing infrastructure
(rented A100/H100 hours) needs different discipline from modelling
code; separating it makes both auditable independently. See
`configs/runpod/headline-*.yaml` for the canonical-run YAML
templates; runbook commentary inlined in
[`reproducibility.md`](./reproducibility.md) §10.2.

**Result**: prediction-persistence pattern `[LOCKED]`. `runpod-deploy`
pulls per-row score artifacts in addition to metrics JSON, so
downstream threshold / calibration analyses run from persisted
predictions without re-running inference. The submission persists 282
prediction parquets per ADR-013 + ADR-021 at
`evals/predictions/<rung>__fold<F>__seed<S>__<source>.parquet`
schema-validated against `src.eval.schemas.PredictionsRowModel`.

## 6.3 SDD / ADR process

This repo practices custom-hybrid SDD: spec + ADRs + assumption
registry + tests-as-invariants. Every significant decision is an
ADR; every assumption is in the registry with a severity tag; every
spec claim that can be made executable is a test.

The phase-by-phase process gates in
[`../SPEC_SHEET.md`](../SPEC_SHEET.md) §2 — work-completed and
tests-passing, not metric thresholds — instantiate the discipline.

**ADR closure trail**:
- 50 ADRs accepted across Phase 0-00 through the v1.0.0 submission
  gate at ADR-050 (the snapshot at submission time; post-v1.0.0
  patch governance extends the trail to ADR-076 at v1.2.13 close).
- `SUBMISSION_AUDIT.md` regenerates from ADR frontmatter via
  `scripts/regenerate_audit.py` (CI hard gate per ADR-039).
- Transcripts for multi-turn decision conversations live at
  `transcripts/<YYYY-MM-DD>__<slug>.md` (gitignored by default;
  emailed to the reviewer separately at submission). Each ADR
  references its source transcript in the `transcript:` frontmatter
  field.

**Result**: the **library-first invariant** (Phase 4 entry walkthrough
Q6 reaffirmation) is project-wide. At every module-design step audit
`eval-toolkit + runpod-deploy + research_toolkit` for an existing
primitive BEFORE writing project glue. ADR-047 retrofitted 4
hand-rolls in `src/data/` in a single carryforward refactor commit;
future module additions follow the same audit discipline. Upstream
gaps land in `decisions/upstream_issues.md` *before* a local workaround.

## Library-first carryforward refactor (ADR-047)

Triggered by Phase 4 entry walkthrough Q6 user reaffirmation of the
library-first invariant as project-wide; retroactive audit identified
4 hand-rolls in `src/data/` where `eval-toolkit` ships fitting
primitives. Closed at Commit 4 (2026-05-16); two upstream
contributions filed at audit close:

- [eval-toolkit#18](https://github.com/brandon-behring/eval-toolkit/issues/18)
  (wire 50-pair golden dedup-holdout into eval-toolkit CI fixtures)
- [eval-toolkit#19](https://github.com/brandon-behring/eval-toolkit/issues/19)
  (3-pattern cookbook docs)

Each refactor commit deleted orphaned local helpers in-commit per
the no-orphaned-code discipline.

## Cross-references

- **Statistical apparatus consuming these guarantees** → [`eval-design.md`](./eval-design.md)
- **Reproducibility recipe consuming the toolchain** → [`reproducibility.md`](./reproducibility.md)
- **Per-decision ADR trail** → [`../decisions/`](../decisions/) + [`../SUBMISSION_AUDIT.md`](../SUBMISSION_AUDIT.md)
- **Upstream-issue ledger** → [`../decisions/upstream_issues.md`](../decisions/upstream_issues.md)

**Linked ADRs**: ADR-013 (per-row predictions persistence), ADR-020
(cost cap + GPU failover discipline), ADR-026 (module layout),
ADR-027 (smoke vs canonical), ADR-039 (submission-readiness gates),
ADR-047 (library-first carryforward refactor).
