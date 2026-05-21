# prompt-injection-detection-prototype

[![Documentation](https://img.shields.io/badge/docs-live-blue)](https://brandon-behring.github.io/prompt-injection-detection-prototype/) [![CI](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/ci.yml/badge.svg)](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/ci.yml) [![Publish](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/publish.yml/badge.svg)](https://github.com/brandon-behring/prompt-injection-detection-prototype/actions/workflows/publish.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE) [![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

**A methodology-focused evaluation of prompt-injection detectors under cross-family distribution shift.** Asks one question: when detectors trained on direct prompt-injection examples meet attack families they didn't see, do they still work?

**Result, two-sided:**

- **Direct detection is learned**, and learnable cheaply --- TF-IDF + LR reaches **0.971 AUPRC** on balanced direct+benign validation; LoRA matches at **0.974**. The neural lift over the lexical baseline is small.
- **Cross-family generalization fails.** On pooled OOD, the best detector lands at AUPRC **0.364** against a random floor of **0.374** --- at the floor, not above. Under AUROC, LoRA (0.383) and TF-IDF (0.371) both clear the 0.5 floor **on the wrong side**: their rankings are anti-correlated with truth on cross-family attacks. The frozen ModernBERT probe alone stays above floor (AUROC 0.515).

This is a capability characterization, not a deployment recommendation. The artifact's contribution is the honest evaluation harness plus the negative result on cross-family transfer.

## Read the site, three depths

- **~60 seconds →** [Project at a glance](https://brandon-behring.github.io/prompt-injection-detection-prototype/docs/for-hiring-managers.html): what problem, what found, why trust, how I think
- **~45 minutes →** [Results](https://brandon-behring.github.io/prompt-injection-detection-prototype/RESULTS.html) (canonical tables + 5 figures) → [Writeup](https://brandon-behring.github.io/prompt-injection-detection-prototype/WRITEUP.html) (methodology hub + 8 spokes)
- **Reproduce →** [T0 laptop / T1 smoke / T3 cloud tier ladder](https://brandon-behring.github.io/prompt-injection-detection-prototype/WRITEUP/reproducibility.html) (~$0 / ~$0 / ~$125)

License: [MIT](./LICENSE) · Author: Brandon Behring · Reproducibility: T0 score-matches against published HF Hub checkpoints within 1e-4 tolerance

---

<details>
<summary><strong>Below the fold — headline tables, repo orientation, reproduction quickstart</strong></summary>

## What this project is

- **A capability characterization**, not a deployment recommendation.
- **A detector-ladder evaluation**: TF-IDF + LR, ModernBERT frozen probe, ModernBERT LoRA, and ProtectAI v1/v2 references. (Full fine-tune ran for LODO direct-source only; pooled OOD inference crashed --- see [ADR-075](./decisions/ADR-075-full-ft-ood-drop-rationale-unified-narrative.md).)
- **A held-out family evaluation**: indirect injection, agentic-flow injection, jailbreak-style questions, and benign-but-injection-shaped text.
- **A reproducible artifact**: source-disjoint splits, leakage checks, persisted predictions, confidence intervals, calibration metrics, and Quarto-rendered documentation.

## Pooled OOD table

| Detector | Pooled OOD AUPRC | Read |
|---|---:|---|
| ModernBERT frozen probe | 0.364 [0.354, 0.375] | best in-house score, still at random floor |
| ProtectAI v1\* | 0.361 [0.330, 0.391] | reference scorer with verified training-pool overlap; not a clean OOD baseline |
| ProtectAI v2\* | 0.314 [0.283, 0.345] | reference scorer with verified training-pool overlap; does not dominate v1 |
| ModernBERT LoRA | 0.293 [0.286, 0.301] | trained adapter ranks below random; AUROC 0.383 below 0.5 floor |
| TF-IDF + LR | 0.291 [0.283, 0.298] | classical floor; AUROC 0.371 also below 0.5 floor |

\* ProtectAI v1 + v2 were trained on at least 2 of 4 LODO training-pool sources
(`deepset/prompt-injections`, `Lakera/gandalf_ignore_instructions`) per
[EVIDENCE](./EVIDENCE.md) §1-2. Pooled OOD scores on slices that overlap with
that training pool are not clean OOD baselines.

For `pooled_ood`, random AUPRC is **412 / 1101 = 0.374**. That is why the 0.364 frozen-probe score is not a success claim. Under AUROC (random floor 0.5), LoRA and TF-IDF + LR both land below the floor with CIs that clear 0.5 on the wrong side --- the mechanism is lexical overfitting + a label-relevance shift on the OOD slate; see [EXECUTIVE_SUMMARY](./EXECUTIVE_SUMMARY.md) §Mechanism for the full read. Direct-detection tables (balanced validation + LODO held-out direct-source recall) live in [RESULTS](./RESULTS.md) §Direct Prompt-Injection Performance.

## What "OOD" means here

"OOD" = **cross-family**, not just a new source name. The training pool is direct-injection-heavy (4 sources: deepset, Gandalf, Mosscap, HackAPrompt). The held-out OOD slate covers:

- **Indirect injection** (BIPIA) --- payload arriving through document context
- **Agentic-flow injection** (InjecAgent) --- payload split across tool-use turns
- **Jailbreak-as-question** (JBB-Behaviors, XSTest) --- harmful elicitation framed as questions
- **Benign-but-injection-shaped** (NotInject) --- false-positive robustness

That mismatch is the experiment.

## Why trust the result

- **Held-out at the source level (LODO), not just the row level.** Leave-one-dataset-out splits ensure the test slate doesn't share a source with training. `evals/leakage_report.json` reports zero exact-hash overlaps and zero cosine-≥0.85 overlaps across all (train, val, test) per-fold-seed pairs.
- **Every reported number carries a 95% bootstrap CI.** Effect-size + CI reporting, not p-values. BCa bootstrap with 10000 resamples; seed-stability check at second seed.
- **Honest single-class slice handling.** BIPIA + InjecAgent (all-positive) and NotInject (all-negative) have mathematically undefined AUPRC/AUROC; the metrics pipeline filters them at source. Recall-at-threshold is reported on those slices instead.
- **Reference scorer contamination is audited, not assumed.** [EVIDENCE](./EVIDENCE.md) §1-2 documents that ProtectAI v1 + v2 were trained on ≥2 of 4 LODO training-pool sources; their pooled OOD scores on overlapping slices are upper-bound, not clean OOD.

## Reproduce --- three tiers

```bash
git clone https://github.com/brandon-behring/prompt-injection-detection-prototype
cd prompt-injection-detection-prototype
make install

# T1 — laptop smoke (~$0, <10 min)
make test-smoke

# T0 — score-match against published HF Hub checkpoints (~$0, ~20 min)
make eval-from-hub RUNG=frozen-probe
make eval-from-hub RUNG=lora
# Score-matches against evals/results.json within 1e-4 absolute tolerance per ADR-058.

# T3 — full retraining from scratch on cloud GPU (~$125, hours)
make headline-cloud  # cost-capped per ADR-020
```

HF Hub checkpoints: [`BBehring/prompt-injection-frozen-probe`](https://huggingface.co/BBehring/prompt-injection-frozen-probe) · [`BBehring/prompt-injection-lora`](https://huggingface.co/BBehring/prompt-injection-lora)

Other useful targets:

```bash
make site             # render Quarto site locally
make audit            # regenerate/check ADR-derived submission audit
make render-figures   # render canonical F1-F5 figures from evals/
```

## How this project thinks

- **Spec-driven development** --- 76 immutable Architecture Decision Records under [`decisions/`](./decisions/) lock methodology choices before code lands.
- **Library-first invariant** --- shared evaluation primitives live in upstream libraries ([eval-toolkit](https://github.com/brandon-behring/eval-toolkit), [runpod-deploy](https://github.com/brandon-behring/runpod-deploy), [research_toolkit](https://github.com/brandon-behring/research_toolkit)); local code is project-specific glue. Upstream gaps land in [`decisions/upstream_issues.md`](./decisions/upstream_issues.md) before any local workaround.
- **Confound-control discipline** --- when the headline result raised the natural follow-up ("does a longer context window fix the OOD gap?"), a controlled DeBERTa-v3-base ablation was designed (chunk-and-average vs head-truncation). Result: a publishable null. See [ADR-060](./decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md).

## Repository map

| Path | Contents |
|---|---|
| [`index.qmd`](./index.qmd) | first-reader landing page |
| [`RESULTS.md`](./RESULTS.md) | exact tables, 5 canonical figures, raw artifact pointers |
| [`WRITEUP.md`](./WRITEUP.md) | methodology hub |
| [`WRITEUP/`](./WRITEUP/) | 8 detailed methodology spokes |
| [`EVIDENCE.md`](./EVIDENCE.md) | external-evidence audit trail |
| [`NEXT_STEPS.md`](./NEXT_STEPS.md) | future-work surface |
| [`decisions/`](./decisions/) | 76 ADRs documenting methodology + governance |
| [`evals/`](./evals/) | metrics, bootstrap CIs, operating points, per-row predictions |
| [`docs/plots/`](./docs/plots/) | F1-F5 figures + metadata sidecars (provenance trail) |
| [`notebooks/`](./notebooks/) | static-rendered Jupytext appendices |
| [`src/`](./src/), [`scripts/`](./scripts/), [`tests/`](./tests/) | implementation + verification |

## Key terms

- **AUPRC** --- primary ranking metric; random floor equals the positive rate.
- **OOD** --- out-of-distribution. Here the important shift is cross-family, not just a different source name.
- **LODO** --- leave-one-dataset-out. One source is held out while the detector is trained on the others.
- **FPR** --- false-positive rate. A 1% FPR target means no more than one false alarm per 100 benign examples.
- **ECE/Brier** --- calibration errors; lower is better.

More definitions in [`docs/GLOSSARY.md`](./docs/GLOSSARY.md).

## What it does not claim

Single-turn English text classification only. Not in scope: multilingual attacks, encoded payloads (base64/leetspeak/Unicode confusables), paraphrase robustness, adversarial perturbations, full multi-turn system behavior, deployment threshold recommendations. The [reference-scorer audit](./WRITEUP/reference-scorer-audit.md) §5.6 names the threat-model deferrals explicitly.

## Submission anchors

- **Current state:** [`tree/v1.2.13`](https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.2.13) (2026-05-21) --- live-site source
- **Original submission tag:** [`tree/v1.0.0`](https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.0.0) (2026-05-18) --- preserved as historical reviewer pin per ADR-033
- **Live rendered site:** <https://brandon-behring.github.io/prompt-injection-detection-prototype/>
- **HF Hub checkpoints:** [frozen probe](https://huggingface.co/BBehring/prompt-injection-frozen-probe), [LoRA](https://huggingface.co/BBehring/prompt-injection-lora)

</details>
