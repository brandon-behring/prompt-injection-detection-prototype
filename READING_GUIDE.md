---
title: "Reading guide"
description: "Navigation router for the prompt-injection classifier evaluation. Two reading-style guides + persona-specific paths."
---

# Reading guide

This page routes you to the part of the writeup that fits your purpose.

The project ships with **two reading-style guides** covering the same
content (per [ADR-079](./decisions/ADR-079-two-guide-reader-architecture.md)):

| Guide | Style | Length | Best for |
|---|---|---|---|
| [WRITEUP_PAPER.md](./WRITEUP_PAPER.md) | Academic IMRAD (Abstract / Methods / Results / Discussion / Limits / Refs) | ~20–25 min | Reviewers expecting journal-paper discipline |
| [WRITEUP_NARRATIVE.md](./WRITEUP_NARRATIVE.md) | Story arc (Hook / Setup / Investigation / Revelation / Implications) | ~15–20 min | Readers preferring plain-English first-person prose |

Both guides cover the same content. Pick the register that fits.

## Persona-specific paths

### Path A — Academic reviewer (~20–25 min)

Read [WRITEUP_PAPER.md](./WRITEUP_PAPER.md) end-to-end. It is structured
as a journal paper (Abstract, Introduction, Background, Methods,
Results, Discussion, Limitations, Conclusion, References). Cross-
references to ADRs at every methodology decision. Bibliography includes
external papers, project artifacts, and ADR citations.

If you want depth on a specific subsection, the methodology spokes are
at [WRITEUP/](./WRITEUP/) — 8 files covering data decisions, evaluation
design, model details, threshold policy, reference-scorer audit,
methodology guarantees, reproducibility, and limitations + future work.

### Path B — Story reader (~15–20 min)

Read [WRITEUP_NARRATIVE.md](./WRITEUP_NARRATIVE.md) end-to-end. It is
structured as a 5-act story arc with an epilogue. Plain-English voice;
defines technical terms on first use.

The story's third act surfaces the headline finding dramatically (the
anti-correlation result). The fourth act covers the 6 supporting
findings as equal-weight enumeration so the headline doesn't drown out
the rest.

### Path C — Hiring manager (60 seconds)

Read [Project at a glance](./docs/for-hiring-managers.md). Four
questions: what problem, what found, why trust, how the candidate
thinks. This is the shortest reader path.

### Path D — Reproducer (~15–20 min setup + ~$0 to ~$125 compute)

Three tiers per [WRITEUP/reproducibility.md](./WRITEUP/reproducibility.md):

- **T0** — score-match against published HF Hub checkpoints (~$0, ~20 min)
- **T1** — laptop smoke test (~$0, <10 min)
- **T3** — full retraining on cloud GPU (~$125, hours; cost-capped per ADR-020)

Commands in [README §Reproduce — three tiers](./README.md#reproduce-three-tiers).
Cost ledger at [evals/cost_ledger.csv](./evals/cost_ledger.csv).

### Path E — Just the numbers

Read [RESULTS.md](./RESULTS.md). Tables-only appendix; no narrative
prose. 5 canonical figures + raw artifact pointers.

## Result map

| Result section | Where it lives |
|---|---|
| Headline pooled OOD AUPRC (Finding 3) | [README §Executive summary](./README.md#executive-summary), [WRITEUP_PAPER §4.3](./WRITEUP_PAPER.md), [WRITEUP_NARRATIVE Act 3 Finding 3](./WRITEUP_NARRATIVE.md), [RESULTS §1](./RESULTS.md) |
| Direct detection check (Finding 1) | [README §Executive summary](./README.md#executive-summary), [WRITEUP_PAPER §4.1](./WRITEUP_PAPER.md), [WRITEUP_NARRATIVE Act 3 Finding 1](./WRITEUP_NARRATIVE.md), [RESULTS §Direct Prompt-Injection Performance](./RESULTS.md) |
| OOD wall is cross-family, not source-level (Finding 2) | [WRITEUP_PAPER §4.2](./WRITEUP_PAPER.md), [WRITEUP_NARRATIVE Act 3 Finding 2](./WRITEUP_NARRATIVE.md), [WRITEUP/eval-design §5.5](./WRITEUP/eval-design.md) |
| Mechanism (lexical overfitting + label-relevance shift) | [README §Executive summary](./README.md#executive-summary), [WRITEUP_PAPER §5.1](./WRITEUP_PAPER.md), [WRITEUP_NARRATIVE Act 3](./WRITEUP_NARRATIVE.md) |
| Context-window ablation | [WRITEUP_PAPER §4.4](./WRITEUP_PAPER.md), [WRITEUP_NARRATIVE Finding 4](./WRITEUP_NARRATIVE.md), [RESULTS §1B](./RESULTS.md) |
| Calibration | [WRITEUP_PAPER §4.7](./WRITEUP_PAPER.md), [WRITEUP_NARRATIVE Finding 7](./WRITEUP_NARRATIVE.md), [RESULTS §5](./RESULTS.md) |
| Threshold fragility | [WRITEUP_PAPER §4.6](./WRITEUP_PAPER.md), [WRITEUP_NARRATIVE Finding 6](./WRITEUP_NARRATIVE.md), [RESULTS §4](./RESULTS.md) |

## Glossary + decisions

- **Glossary**: [docs/GLOSSARY.md](./docs/GLOSSARY.md) — all technical
  terms used in either guide, with cross-references.
- **Decisions**: 81 ADRs at [decisions/](./decisions/) lock the
  methodology choices. Both guides cite specific ADRs at every
  methodology decision point.
- **Evidence trail**: [EVIDENCE.md](./EVIDENCE.md) for external-evidence
  audit (training corpus contamination, reference scorer training
  pools, etc.).

## Submission anchors

- **Current state**: [`tree/v1.3.2`](https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.3.2)
  (2026-05-21) — live-site source.
- **Original submission tag**: [`tree/v1.0.0`](https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.0.0)
  (2026-05-18) — preserved as historical reviewer pin per ADR-033.
- **Live rendered site**: <https://brandon-behring.github.io/prompt-injection-detection-prototype/>.

## Repo map

See [README §Repository map](./README.md#repository-map).
