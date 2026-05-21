# prompt-injection-detection-prototype

[![Documentation](https://img.shields.io/badge/docs-live-blue)](https://brandon-behring.github.io/prompt-injection-detection-prototype/) [![CI](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/ci.yml/badge.svg)](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/ci.yml) [![Publish](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/publish.yml/badge.svg)](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/publish.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE) [![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

This is a methodology-focused prompt-injection classifier evaluation. It asks a
simple question: if detectors are trained on direct prompt-injection examples,
can they detect that pattern, and do they still work when the attack family
changes?

The headline answer is two-sided: **direct detection works better;
cross-family generalization fails**. The detectors learned direct prompt
injection patterns, but none of the evaluated detectors clearly beat the random
floor on the pooled held-out attack-family slice.

## What This Project Is

- **A capability characterization**, not a deployment recommendation.
- **A detector-ladder evaluation**: TF-IDF + LR, ModernBERT frozen probe,
  ModernBERT LoRA, and ProtectAI v1/v2 references.
- **A held-out family evaluation**: indirect injection, agentic-flow injection,
  jailbreak-style questions, and benign-but-injection-shaped text.
- **A reproducible artifact**: source-disjoint splits, leakage checks,
  persisted predictions, confidence intervals, calibration metrics, and
  Quarto-rendered documentation.

## Headline Result

| Result view | Best in-house result | Read |
|---|---:|---|
| Balanced validation, direct + benign | LoRA AUPRC **0.974**, AUROC **0.993**, recall@0.5 **0.934** | direct-pattern detection worked |
| LODO held-out direct-source test | frozen-probe recall@0.5 **0.641** | recall-only because the slice is all positive |
| Pooled OOD | frozen-probe AUPRC **0.364** vs random floor **0.374** | cross-family ranking did not beat guessing |

The balanced validation view shows that the detector stack can learn the direct
prompt-injection pattern. The held-out direct-source test is stricter but
all-positive, so false positives, AUPRC, and AUROC are omitted there. The OOD
view is the hard failure mode.

## Pooled OOD Table

| Detector | Pooled OOD AUPRC | Read |
|---|---:|---|
| ModernBERT frozen probe | 0.364 [0.354, 0.375] | best in-house score, still at random floor |
| ProtectAI v1\* | 0.361 [0.330, 0.391] | reference scorer with verified training-pool overlap; not a clean OOD baseline |
| ProtectAI v2\* | 0.314 [0.283, 0.345] | reference scorer with verified training-pool overlap; does not dominate v1 |
| ModernBERT LoRA | 0.293 [0.286, 0.301] | fine-tuning was actively harmful; AUROC 0.383 below 0.5 floor |
| TF-IDF + LR | 0.291 [0.283, 0.298] | classical floor; AUROC 0.371 also below 0.5 floor |

\* ProtectAI v1 + v2 were trained on at least 2 of 4 LODO training-pool sources
(`deepset/prompt-injections`, `Lakera/gandalf_ignore_instructions`) per
[EVIDENCE](./EVIDENCE.md) §1-2. Pooled OOD scores on slices that overlap with
that training pool are not clean OOD baselines.

For `pooled_ood`, random AUPRC is **412 / 1101 = 0.374**. That is why the
0.364 frozen-probe score is not a success claim. Under AUROC (random floor
0.5), LoRA and TF-IDF + LR both land below the floor with CIs that clear 0.5
on the wrong side --- the mechanism is lexical overfitting + a label-relevance
shift on the OOD slate; see [EXECUTIVE_SUMMARY](./EXECUTIVE_SUMMARY.md)
§Mechanism for the full read.

## Direct Detection Check

The direct-task result is the contrast for the OOD failure: the detectors did
learn direct prompt-injection patterns, but that skill did not transfer cleanly
to new attack families.

**Balanced direct+benign validation**

| Detector | AUPRC | AUROC | Recall@0.5 | Interpretation |
|---|---:|---:|---:|---|
| ModernBERT LoRA | **0.974** | **0.993** | **0.934** | strongest direct-pattern detector |
| TF-IDF + LR | 0.971 | 0.992 | 0.930 | lexical direct baseline is also strong |
| ModernBERT frozen probe | 0.653 | 0.907 | 0.849 | weaker ranking, still discriminative |

**Held-out direct-source recall**

| Detector | Recall@0.5 | Interpretation |
|---|---:|---|
| ModernBERT frozen probe | **0.641** | best direct-source holdout recall |
| ModernBERT LoRA | 0.625 | similar recall, but worse pooled OOD ranking |
| ModernBERT full fine-tune\*\* | 0.558 | lower direct-source recall |

\*\* Full-FT shows LODO direct-source data only (24 Phase 2 predictions
persisted); the comparable pooled OOD inference was **not run** (Phase 5 X11
crash, see
[ADR-075](./decisions/ADR-075-full-ft-ood-drop-rationale-unified-narrative.md)).
Full-FT is absent from the Pooled OOD table above for that reason.

The held-out direct-source slice is all-positive, so false positives, AUPRC,
and AUROC are undefined and omitted.

## How To Read The Site

- **5-minute read**: start at the
  [live landing page](https://brandon-behring.github.io/prompt-injection-detection-prototype/).
  It explains the problem, setup, result, and limits in plain language, then
  points to the 60-second project-at-a-glance tour.
- **Results audit**: read [RESULTS.md](./RESULTS.md). It contains the exact
  tables, five canonical figures, and raw artifact pointers.
- **Methodology audit**: read [WRITEUP.md](./WRITEUP.md), then the eight spoke
  pages under [`WRITEUP/`](./WRITEUP/).
- **Decision audit**: read [`decisions/`](./decisions/) for the methodology and
  governance trail.

## Key Terms

- **AUPRC**: primary ranking metric; random floor equals the positive rate.
- **OOD**: out-of-distribution. Here the important shift is cross-family, not
  just a different source name.
- **LODO**: leave-one-dataset-out. One source is held out while the detector is
  trained on the others.
- **FPR**: false-positive rate. A 1% FPR target means no more than one false
  alarm per 100 benign examples.
- **ECE/Brier**: calibration errors; lower is better.

More definitions are in [`docs/GLOSSARY.md`](./docs/GLOSSARY.md).

## Reproduce

```bash
git clone https://github.com/brandon-behring/prompt-injection-detection-prototype
cd prompt-injection-detection-prototype
make install
make test-smoke
make eval-from-hub RUNG=frozen-probe
make eval-from-hub RUNG=lora
```

Useful targets:

```bash
make site             # render Quarto site
make audit            # regenerate/check ADR-derived submission audit
make render-figures   # render canonical F1-F5 figures from evals/
make headline-cloud   # optional full cloud reproduction path
```

## Repository Map

| Path | Role |
|---|---|
| `index.qmd` | plain-language live-site landing page |
| `EXECUTIVE_SUMMARY.md` | one-page decision-maker summary |
| `RESULTS.md` | exact result grids, figures, raw artifacts |
| `WRITEUP.md` + `WRITEUP/` | methodology hub and detailed spokes |
| `NEXT_STEPS.md` | completed carryforward log plus live future-work questions |
| `evals/` | canonical metrics, bootstrap artifacts, predictions |
| `docs/plots/` | canonical reviewer figures F1-F5 plus provenance sidecars |
| `decisions/` | Architecture Decision Records |
| `src/`, `scripts/`, `tests/` | implementation and verification code |

## What It Does Not Claim

This does not cover multilingual attacks, encoded payloads, paraphrase
robustness, adversarial perturbations, or full multi-turn system behavior. It
is an evaluation artifact and capability characterization, not a ready-to-ship
detector.

## License

[MIT](./LICENSE)
