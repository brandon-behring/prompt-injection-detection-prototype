# Submission — Ciphero AI applied-scientist take-home (v5)

**Author**: Brandon Behring (brandonzinho@me.com)
**Repo**: [github.com/brandon-behring/prompt-injection-sdd](https://github.com/brandon-behring/prompt-injection-sdd)
**Date**: `[TBD]`

---

## Cover note

Attached is my methodology-first prompt-injection classification PoC for the Ciphero AI applied-scientist role. The brief asked for **models of increasing complexity** + **the right amount of OOD coverage**; I built both and put the rigor into the evaluation framework rather than into the model itself.

The work is *methodology + capability characterization braided*: a rung ladder `[LOCKED: LR-TFIDF → Frozen DeBERTa probe → DeBERTa-LoRA → ProtectAI v2 → Llama Prompt Guard 2]` (inherited from v4) characterises what each capability layer contributes, evaluated through [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) — a methodology-aware harness with bootstrap CIs, paired comparisons, calibration battery, leakage detection, and a 16-chapter methodology curriculum. Cloud runs are orchestrated through [runpod-deploy](https://github.com/brandon-behring/runpod-deploy).

The package separates in-pool competitiveness, external shift, benign over-defense, and calibration without collapsing them into one blended score. No deployment leader is promoted; the methodology rigor and capability-layer characterization are the artifact. Detection and verification operating modes are reported as a score-behavior characterisation, not a deployment recommendation.

**Recommended entry point**: `README.md` → `WRITEUP.md` §1 motivation + §5 eval framework + §7 results + §9 negative results → `SPEC_SHEET.md` process gates → `NEXT_STEPS.md` → `EVIDENCE.md` audit trail.

`[CANDIDATE]` *(Reading order includes §5 because methodology rigor is part of the value being demonstrated.)*

---

## What's in the package

### Primary deliverable (PDF, 5 documents bundled)

- **`prompt-injection-detection.pdf`** `[TBD path; TBD size]` — single print-ready PDF containing:
  - `README.md` — skim deliverable, headline characterization table, navigation.
  - `WRITEUP.md` — full methodology + capability characterization (~5000 words across 12 sections).
  - `NEXT_STEPS.md` — tactical next steps on v5 infrastructure + aspirational v6 directions.
  - `SPEC_SHEET.md` — v5 specification including phase-by-phase process gates.
  - `EVIDENCE.md` — audit trail: external evidence verified, confounds named, gaps deferred.

### Reproducibility infrastructure

- **`docs/DIAGNOSTICS.md`** `[CANDIDATE]` — fresh-clone reproducibility runbook.
- **`make diagnostics-smoke`** `[CANDIDATE]` — one-shot install + lint + test + analysis-pipeline smoke.
- **GitHub Actions CI** — every push runs lint + invariant tests; badge in `README.md`.
- **HF Hub** `[TBD URL]` — v5 checkpoints with per-row predictions persisted (gap inherited from v4 — see `EVIDENCE.md` §6).
- **GitHub release** `[TBD tag]` — predictions tarball + evidence files for canonical reproduction.

### Evidence sources

- **`evals/v5/REPORT.md`** `[TBD]` — v5 canonical matrix.
- **`evals/v5/results.json`** `[TBD]` — schema-validated against eval-toolkit `results.v1.json`.
- **`evals/v5/predictions.parquet`** `[CANDIDATE: new for v5]` — per-row predictions persisted (v4 gap closed).
- **`evals/v5/analysis/`** `[TBD]` — bootstrap CIs, paired comparisons, calibration, MDE, per-source breakdowns, threshold characterizations.
- **[eval-toolkit](https://github.com/brandon-behring/eval-toolkit)** — methodology curriculum + primitive implementations.
- **[runpod-deploy](https://github.com/brandon-behring/runpod-deploy)** — cloud orchestration runbook + manifests.
- **`transcripts/`** `[TBD]` — selected Claude-Code transcripts illustrating decision points.

---

## How to reach me

- **GitHub issue**: [github.com/brandon-behring/prompt-injection-sdd/issues](https://github.com/brandon-behring/prompt-injection-sdd/issues)
- **Email**: brandonzinho@me.com

Thank you for the opportunity. I'd welcome a follow-up conversation.

— Brandon
