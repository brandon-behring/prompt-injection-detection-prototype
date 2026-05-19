# prompt-injection-detection-prototype

[![Documentation](https://img.shields.io/badge/docs-live-blue)](https://brandon-behring.github.io/prompt-injection-detection-prototype/) [![CI](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/ci.yml/badge.svg)](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/ci.yml) [![Publish](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/publish.yml/badge.svg)](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/publish.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE) [![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

This is a methodology-focused prompt-injection classifier evaluation. It asks a
simple question: if detectors are trained on direct prompt-injection examples,
do they still work when the attack family changes?

The headline answer is **mostly no**. On the pooled held-out attack-family
slice (the out-of-distribution, or OOD, test), none of the evaluated detectors
clearly beats the random floor for AUPRC, the primary ranking metric.

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

| Detector | Pooled OOD AUPRC | Read |
|---|---:|---|
| ModernBERT frozen probe | 0.364 [0.354, 0.375] | best in-house score, still at random floor |
| ProtectAI v1 | 0.361 [0.330, 0.391] | diagnostic reference; contamination caveats |
| ProtectAI v2 | 0.314 [0.283, 0.345] | does not dominate v1 |
| ModernBERT LoRA | 0.293 [0.286, 0.301] | fine-tuning hurt OOD performance |
| TF-IDF + LR | 0.291 [0.283, 0.298] | classical floor, roughly tied with LoRA |

For `pooled_ood`, random AUPRC is **412 / 1101 = 0.374**. That is why the
0.364 frozen-probe score is not a success claim.

## How To Read The Site

- **5-minute read**: start at the
  [live landing page](https://brandon-behring.github.io/prompt-injection-detection-prototype/).
  It explains the problem, setup, result, and limits in plain language, then
  points to the 60-second hiring-manager tour.
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
is an evaluation artifact and a negative result, not a ready-to-ship detector.

## License

[MIT](./LICENSE)
