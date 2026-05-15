# Submission — cover-letter template

> **This is the cover-letter TEMPLATE.** It is committed to the public repo for transparency about the submission's structure. The filled-in version is `SUBMISSION.md` (gitignored; emailed to the reviewer separately at submission time).
>
> Fill the three `[TBD: filled at submission]` slots locally (`cp SUBMISSION_TEMPLATE.md SUBMISSION.md` then edit), save, and email it as the cover letter alongside the public repo URL.

**Author**: Brandon Behring
**Date**: `[TBD: date]`
**Recipient**: `[TBD: recipient]`
**Role**: `[TBD: role]`
**Repo**: [github.com/brandon-behring/prompt-injection-detection-prototype](https://github.com/brandon-behring/prompt-injection-detection-prototype)

---

## Cover note

This submission delivers a methodology-first prompt-injection classifier prototype: a structured case study demonstrating spec-driven development, library-first integration, and audited-evidence discipline.

The brief asked for **models of increasing complexity** and **the right amount of OOD coverage**. Both axes are delivered; the rigor lives in the evaluation framework rather than the model itself. A rung ladder of classifiers `[OPEN: rung ladder; resolved at Phase 0]` characterises what each capability layer contributes, evaluated through [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) — a methodology-aware harness with bootstrap CIs, paired comparisons, calibration battery, leakage detection, and a 16-chapter methodology curriculum. Cloud runs are orchestrated through [runpod-deploy](https://github.com/brandon-behring/runpod-deploy); the literature dossier underlying the methodology choices was produced via [research_toolkit](https://github.com/brandon-behring/research_toolkit).

The package separates in-pool competitiveness, external shift, benign over-defense, and calibration without collapsing them into one blended score. No deployment leader is promoted; the methodology rigor and capability-layer characterization are the artifact. Detection and verification operating modes are reported as a score-behaviour characterisation, not a deployment recommendation.

**Recommended entry point**: `README.md` → `WRITEUP.md` §1 motivation + §5 eval framework + §7 results + §9 negative results → `SPEC_SHEET.md` process gates → `NEXT_STEPS.md` → `EVIDENCE.md` audit trail.

`[LOCKED]` *(Reading order includes §5 because methodology rigor is part of the value being demonstrated.)*

---

## What's in the package

### Primary deliverable (PDF, 5 documents bundled)

- **`prompt-injection-detection.pdf`** `[TBD: built at Phase 5]` — single print-ready PDF containing:
  - `README.md` — skim deliverable, headline characterization table, navigation.
  - `WRITEUP.md` — full methodology + capability characterization (~5000 words across 12 sections).
  - `NEXT_STEPS.md` — tactical next steps + aspirational directions.
  - `SPEC_SHEET.md` — project specification including phase-by-phase process gates.
  - `EVIDENCE.md` — audit trail: external evidence verified, confounds named, gaps deferred.

### Reproducibility infrastructure

- **`docs/REPRODUCIBILITY.md`** — fresh-clone reproducibility runbook.
- **`make diagnostics-smoke`** `[OPEN: smoke-test target; resolved at Phase 0]` — one-shot install + lint + test + analysis-pipeline smoke.
- **GitHub Actions CI** — every push runs lint + invariant tests; badge in `README.md`.
- **HF Hub** `[TBD: URL once checkpoints uploaded at Phase 2]` — checkpoints with per-row predictions persisted (see `EVIDENCE.md` §6).
- **GitHub release** `[TBD: v1.0.0 at submission per CHANGELOG]` — predictions tarball + evidence files for canonical reproduction.

### Evidence sources

- **`evals/REPORT.md`** `[TBD: populated at Phase 4]` — canonical matrix.
- **`evals/results.json`** `[TBD: populated at Phase 4]` — schema-validated against eval-toolkit `results.v1.json`.
- **`evals/predictions.parquet`** `[TBD: populated at Phase 2]` — per-row predictions persisted.
- **`evals/analysis/`** `[TBD: populated at Phase 4]` — bootstrap CIs, paired comparisons, calibration, MDE, per-source breakdowns, threshold characterizations.
- **[eval-toolkit](https://github.com/brandon-behring/eval-toolkit)** — methodology curriculum + primitive implementations.
- **[runpod-deploy](https://github.com/brandon-behring/runpod-deploy)** — cloud orchestration runbook + manifests.
- **Transcripts** — Phase 0 decision conversations (private; emailed separately to the reviewer, not in the public repo).

---

## How to reach me

- **GitHub issue**: [github.com/brandon-behring/prompt-injection-detection-prototype/issues](https://github.com/brandon-behring/prompt-injection-detection-prototype/issues)
- **Email**: brandon.m.behring@gmail.com

Thank you for the opportunity to share this work. I'd welcome a follow-up conversation.

— Brandon
