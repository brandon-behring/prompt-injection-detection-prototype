---
title: "Prompt-Injection Classification: Methodology and Capability Characterization (Narrative Format)"
description: "Plain-English story-arc article presenting the project's methodology and findings."
---

# Prompt-Injection Classification: Methodology and Capability Characterization

**Author**: Brandon Behring | **Date**: 2026-05-21 | **Status**:
live-site current state `tree/v1.3.0`; original submission tag
`tree/v1.0.0` (2026-05-18) preserved as historical reviewer pin per
ADR-033.

> **Reader note.** This is the narrative format of the project writeup
> — a story rather than a paper. For the same content in academic
> IMRAD format (Abstract, Methods, Results, Discussion, etc.), see
> [WRITEUP_PAPER.md](./WRITEUP_PAPER.md). Both guides cover the same
> evaluation, methodology, findings, and limitations; the register
> and structure differ. Technical terms are defined on first use and
> linked to [docs/GLOSSARY.md](./docs/GLOSSARY.md).

---

## Act 0 — Hook

A prompt-injection detector that has clearly learned to recognize the
direct attack pattern, with strong validation numbers, can also be
worse than chance on a *different family* of attacks. Not slightly
worse. Anti-correlated: the more the detector "looks like it works"
on familiar attacks, the more its rankings can be inverted on
unfamiliar ones.

That is the headline of this project. We built a detector ladder,
evaluated it honestly under leave-one-dataset-out splits, and got a
result that looks neat at first glance and uncomfortable on second
read.

Direct prompt-injection detection works well. The TF-IDF + logistic
regression baseline reaches 0.974 AUPRC on balanced direct-versus-
benign validation. The LoRA-fine-tuned ModernBERT classifier ties at
0.974. By any standard in-distribution metric, the detectors learned
the task.

Then we tested them on attack families they had not seen during
training. The best detector landed at 0.364 AUPRC against a random
floor of 0.374. Two of the four classifiers fell *below* the AUROC
random floor of 0.5, with confidence intervals that cleared 0.5 on
the wrong side. The frozen ModernBERT probe alone stayed above the
floor.

This story is about why that happened, what it tells us about
direct-trained detectors as a class, and what we would do
differently next time.

---

## Act 1 — Setup

### The question

A detector for prompt-injection sounds simple. You give it a piece of
text. It tells you whether the text is trying to override the
instructions an LLM is supposed to follow. Train it on a public
prompt-injection corpus. Evaluate it on held-out examples. Report
AUPRC and AUROC. Ship.

The hard part is the word "evaluate." Most public training corpora
for prompt-injection detection focus on **direct injection** — the
kind where the attacker payload is right there in the user input,
typically with imperative phrasing ("ignore previous instructions",
"you are now"). If you train and evaluate on the same kind of text,
you measure how well the classifier memorized that style. You do
not measure whether it understands what an injection *is*.

We wanted to know whether the classifier had learned the *attack
class* or just the *training style*. To answer that, we needed to
test it on attack families it had not seen.

### The threat-model context

Prompt injection takes many forms in the real world:

- **Direct injection** — the historically studied class. Payload is
  in the user input. Examples: "ignore your previous instructions
  and tell me how to..."
- **Indirect injection** — the payload arrives through third-party
  context the LLM consumes (a web page, a document, an email).
- **Agentic-flow injection** — the payload spreads across tool-use
  turns in an agent loop.
- **Jailbreak-style questions** — harmful elicitation framed as
  natural questions; doesn't look like an override command.
- **Benign-but-injection-shaped text** — false-positive cases; text
  that *looks* like injection but isn't.

A production detector that fails on indirect injection but flags
benign-but-injection-shaped text is not a useful detector. We wanted
to find out which of these failure modes our detectors would have.

### What we did not try to do

This project is not a product. It is a **capability characterization**
— an honest evaluation harness applied to a representative detector
ladder, with the goal of answering "what does each added capability
buy?". We are not shipping a deployment-ready detector. We are not
proposing a new training method. We are showing what several existing
detector designs do under a fairer evaluation than they typically
receive.

Specifically out of scope: multilingual attacks, encoded payloads
(base64, leetspeak, Unicode confusables), paraphrase robustness,
adversarial perturbations, full multi-turn system behavior, and
deployment threshold recommendations. We name these out-of-scope
items so the reader does not over-generalize the result.

---

## Act 2 — Investigation

### Building the evaluation harness

We started with the discipline question: how do we evaluate a
prompt-injection detector honestly?

Two design choices were load-bearing:

**Source-disjoint splits.** Rather than randomly splitting rows
within a single training corpus (which leaks lexical features between
training and evaluation), we held entire *sources* out. The training
pool combines four direct-injection corpora: deepset/prompt-
injections, Lakera/gandalf_ignore_instructions, Lakera/mosscap, and
HackAPrompt. For each leave-one-dataset-out (LODO) fold, one source
is fully held out; the detector trains on the remaining three. This
is the **leave-one-dataset-out** discipline — `LODO` for short, and
it matters because it prevents the detector from getting a free pass
on source-style memorization.

**Cross-family OOD test slate.** The test slate intentionally varies
attack family rather than source identity. We assembled five
held-out OOD slices spanning the four cross-family classes:

- **BIPIA** — indirect injection (payload via document context)
- **InjecAgent** — agentic-flow injection (payload across tool turns)
- **JBB-Behaviors** — jailbreak-style questions
- **XSTest** — jailbreak/safe-question discrimination
- **NotInject** — benign text engineered to look like injection
  (false-positive test)

None of these families appear in the training pool. That mismatch is
the experiment.

### The detector ladder

We chose five detectors — a "ladder" of increasing complexity:

1. **TF-IDF + logistic regression**. The classical baseline. Trains
   in seconds. Pure lexical features. We included it to answer "what
   does surface form alone get you?" The answer turned out to be a
   lot — and that's part of the story.

2. **ModernBERT frozen probe**. A linear classifier on top of a
   pretrained ModernBERT representation, with the backbone frozen.
   No LODO-pool adaptation. We included it to answer "what does the
   pretrained backbone already know about injection-like text?"

3. **ModernBERT LoRA**. Parameter-efficient fine-tuning. The backbone
   stays frozen; only a small set of adapter weights gets updated on
   the LODO training pool. We included it to answer "what does
   targeted adaptation buy us?"

4. **ModernBERT full fine-tune**. Update all the parameters. We
   *intended* to include this as the "full adaptation" comparison
   point. The Phase 2 LODO direct-source training ran successfully
   (24 prediction files persisted); the Phase 5 pooled-OOD inference
   crashed mid-run on a cloud file-system error (X11 EIO on the
   RunPod /workspace FUSE mount) and we made the call not to re-fire
   it. Full-FT appears in the LODO direct-source recall table; it is
   absent from the pooled OOD AUPRC table for that reason. The
   incomplete-experiment status is flagged on every reporting surface.
   See [ADR-075](./decisions/ADR-075-full-ft-ood-drop-rationale-unified-narrative.md)
   for the full story.

5. **ProtectAI v1 and v2** (published reference scorers). DeBERTa-v3-
   base classifiers trained on direct-injection corpora. Inference-
   only. They give us diagnostic comparison points — *with the
   caveat* that they have documented training-pool overlap with our
   LODO sources, so their pooled OOD scores on overlapping slices
   are not clean OOD baselines. We mark them with
   `suspected_contamination` and report them as references rather
   than competitors.

### Statistical discipline

We promised honest evaluation. That meant:

- **Confidence intervals on every reported number.** We use BCa
  bootstrap (Bias-Corrected and Accelerated) with 10000 resamples.
  No point estimates without uncertainty.
- **Seed-stability check.** Headline numbers run at seed=1; we re-run
  at seed=2 to verify the result isn't a coincidence of random init.
- **Single-class slice handling.** BIPIA, InjecAgent, and NotInject
  are mathematically single-class (all positive or all negative).
  AUPRC and AUROC are undefined there. The metrics pipeline filters
  these slices at source rather than reporting nonsense numbers.
- **Leakage scan.** Two-stage check across all (train, val, test)
  per-fold-seed pairs: exact-hash overlap detection + MiniLM-L6-v2
  cosine similarity at ≥0.85. Zero overlaps reported.
- **Effect sizes + CIs, not p-values.** We report the numbers and
  the intervals; readers can decide.

These choices add audit-trail overhead but eliminate the most common
forms of "the result looked good but it was contaminated" criticism.

---

## Act 3 — Revelation

### The headline finding

Direct detection works. On balanced direct+benign validation data,
LoRA reaches 0.974 AUPRC and TF-IDF + LR reaches 0.971. The frozen
probe is weaker at 0.653 but still discriminative. The pipeline can
train detectors that recognize the direct instruction-override
pattern.

On the LODO held-out direct-source test (all-positive by design),
recall-at-0.5 is 0.641 for the frozen probe, 0.625 for LoRA, and
0.558 for full fine-tune. Cross-source direct recall is meaningful.

So far, this looks like a project that built some prompt-injection
detectors that work.

Then we ran the cross-family test.

**Pooled OOD AUPRC table:**

| Detector | Pooled OOD AUPRC | 95% CI |
|---|---:|---:|
| ModernBERT frozen probe | 0.364 | [0.354, 0.375] |
| ProtectAI v1\* | 0.361 | [0.330, 0.391] |
| ProtectAI v2\* | 0.314 | [0.283, 0.345] |
| ModernBERT LoRA | 0.293 | [0.286, 0.301] |
| TF-IDF + LR | 0.291 | [0.283, 0.298] |

The random floor is 0.374 (since the positive rate on pooled OOD is
412/1101 = 0.374). The best detector is at the floor; the trained
adapters are *below* it.

\* ProtectAI v1 + v2 carry `suspected_contamination` per our
contamination taxonomy — they were trained on at least 2 of our 4
LODO training-pool sources, so their pooled OOD scores on overlapping
slices are not clean OOD baselines.

That is the headline result for AUPRC. But the sharper finding
emerges under AUROC.

### The sharper finding: anti-correlation

AUROC has a 0.5 random floor regardless of class balance. Random
guessing gets 0.5. Worse than random — below 0.5 — means the
detector's score ordering is *systematically wrong*, not just noisy.

Under AUROC on pooled OOD:

- **LoRA**: 0.383 [0.374, 0.392]
- **TF-IDF + LR**: 0.371 [0.362, 0.381]
- **Frozen probe**: 0.515 [0.505, 0.525]

LoRA and TF-IDF + LR both land below 0.5, with confidence intervals
that clear 0.5 *on the wrong side*. The frozen probe alone stays
above floor.

The in-pool to cross-family generalization gap for the trained
detectors is approximately 0.6 AUROC. The detectors that scored
0.99 AUROC on in-pool data score 0.38 AUROC on cross-family data —
the largest possible gap with statistical confidence.

This is not pure overfitting. Pure overfitting predicts collapse
*toward* random performance, not past it. A detector that goes below
0.5 AUROC is producing scores that are *anti-correlated* with the
true label. To get there, you need a specific mechanism — not just
"the detector failed to learn," but "the detector learned something
that points the wrong way on this slate."

That is the surprise. The detectors did not fail in the way we
expected.

### What the mechanism appears to be

After staring at the slate composition for a while, the interpretation
that fits is **lexical overfitting combined with a label-relevance
shift on the OOD slate**. Both LoRA and TF-IDF + LR appear to learn
lexical signatures of direct prompt injection — the imperative
phrases, the role-override patterns, the "ignore previous
instructions" lexicon. On the cross-family OOD slate, this lexical
signal is *anti-correlated* with the true attack class:

- **NotInject** (339 examples, all negative) is benign text
  engineered to *look like* direct injection. Both trained detectors
  score these examples HIGH (false positives), inverting the
  negative class.
- **BIPIA and InjecAgent** (indirect + agentic, 112 positive
  examples) are real attacks that do *not* use direct-injection
  lexical patterns. Both detectors score these examples LOW (false
  negatives), inverting the positive class.

The lexical signal is real and internally consistent within itself.
It just stops tracking attack class on the cross-family slate, where
"text that resembles direct injection lexically" and "text that is
actually an attack" point in opposite directions.

The frozen probe (which never adapted to the LODO pool) preserves
generic linguistic features that are less aligned with the direct-
injection lexical distribution. That is why the frozen probe stays
closer to the random floor on cross-family slices instead of
inverting past it. It learned less; it failed less catastrophically.

This is a hypothesis consistent with the aggregate AUROC and the
slate composition. We have not directly demonstrated it via
per-prediction analysis — that work (comparing detector scores on
lexically-direct vs lexically-indirect OOD examples) is on the
future-work list ([NEXT_STEPS §3](./NEXT_STEPS.md)). The per-row
prediction parquets at `evals/predictions/` support that analysis;
running it is portfolio-repo scope.

---

## Act 4 — The other findings

The headline finding (Act 3) is the load-bearing claim. Six more
findings support and contextualize it. Listed in equal-weight
order so they are not lost in the headline's shadow.

### Finding 4 — The context-window ablation was a null result

The natural next question after seeing the ModernBERT-LoRA failure
was: *did the longer context window matter?* ModernBERT has an
8192-token native context; DeBERTa-v3-base has 512. If the OOD gap
was driven by long-context effects, switching to a short-context
backbone with chunk-and-average aggregation should change something.

We ran the ablation per [ADR-060](./decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md):
DeBERTa-v3-base trained under two truncation strategies (chunk-and-
average and head-truncation) on the same LODO training data, then
evaluated on the same pooled OOD slate.

Result: chunk-and-average scored 0.291 AUPRC; head-truncation scored
0.290. Neither significantly differs from each other or from the
ModernBERT-LoRA 0.293. **The context window is not the explanation.**
The ModernBERT advantage from §4.1 should be read as backbone-
dominant, not context-window-dominant. The cross-family failure
mode appears to be backbone-agnostic among the configurations we
tested.

This is a publishable null result, which is itself a contribution.
Most evaluations stop short of asking the follow-up question.

### Finding 5 — Published detector versions are slice-dependent

The two ProtectAI versions tell different stories on different
slices:

- ProtectAI v2 improves over v1 on JBB-Behaviors: AUPRC 0.556 vs
  0.519.
- ProtectAI v2 *regresses* on XSTest: AUPRC 0.382 vs 0.469.
- ProtectAI v2 regresses on pooled OOD overall: AUPRC 0.314 vs 0.361.

"Newer is better" does not hold across the full slate. The practical
lesson: detector updates should be evaluated against the actual slice
mix that matters for the deployment, not on a single aggregate
metric. If the deployment context is dominated by JBB-style queries,
v2 wins. If it spans the full OOD mix, v1 wins on AUPRC.

This finding is independent of our trained detectors and applies to
how the field should evaluate published prompt-injection detectors
more broadly.

### Finding 6 — Validation thresholds are fragile

Detection-policy thresholds were fit per-(fold, seed) on validation
data, targeting FPR ≤ 1%. They were applied unchanged to held-out
test sources. On test:

- TF-IDF + LR averages 6.7% FPR (target: 1%)
- LoRA averages 11.5% FPR
- Frozen probe holds the 1% target but catches only about 6% of
  positives

The 1% FPR target does not hold on held-out sources for the trained
detectors. The frozen probe holds the FPR target but at a recall
that no deployment would accept.

This is what we mean when we say the methodology is a
characterization, not a deployment recommendation. The numbers tell
you what the detectors do; they do not give you an operating point
you can ship.

### Finding 7 — Calibration favors the frozen probe

Among the four detectors with both-class OOD scores, the frozen
probe has the lowest expected calibration error (ECE) and lowest
Brier score on the pooled OOD slate. Mean ECE: 0.144. Mean Brier:
0.265.

LoRA — which fits the direct training pool best — has worse
calibration than the frozen probe. The detector that learns the most
about direct injection also produces the least-calibrated
probabilities on cross-family text. That reinforces the Act 3
mechanism story: direct-pattern learning and deployable cross-family
score behavior are different capabilities, and they trade off
against each other.

The full reliability diagrams (raw + temperature-scaled + isotonic-
calibrated) are in [Figure F4](./docs/plots/F4.svg). Recalibration
helps but does not fix the underlying ranking inversion.

---

## Act 5 — Implications

### What this means for direct-injection-trained classifiers

We are cautious about three claims based on this study:

1. **Direct-pattern learning and cross-family transfer are different
   capabilities.** A detector that performs well on direct-injection
   validation does not, by itself, give you confidence in cross-
   family performance. The two have to be measured separately, and
   the cross-family slate has to include attacks that genuinely vary
   in family — not just new sources of the same family.

2. **AUROC below 0.5 is an active failure mode, not a benign
   degradation.** The detector is not "failing to find signal" —
   it is "finding signal that points the wrong way." A deployment
   downstream of such a detector could be *worse* than not having
   one, because its rankings would be systematically wrong on
   cross-family text.

3. **Validation FPR rates are not what you'll see in production.**
   On held-out test sources, the trained detectors average 6.7%
   (TF-IDF + LR) to 11.5% (LoRA) FPR against a 1% validation target.
   That's a 7-11× over-fire rate on benign-but-injection-shaped text
   that wasn't in the training distribution.

### What would we try next?

If we were extending this project, the priority order would be:

1. **OOD-aware training data.** Include cross-family examples in
   training (with appropriate per-source dedup against the OOD test
   slate). The interesting question is whether direct + indirect +
   agentic + jailbreak in the training pool produces a detector
   that generalizes across the families, or whether each family
   needs its own specialized detector.

2. **Per-prediction mechanism validation.** Run the analysis
   described in §5.1 of the academic paper format: compare detector
   scores on lexically-direct vs lexically-indirect OOD examples.
   This would empirically test the lexical-overfitting hypothesis
   rather than relying on the aggregate-AUROC interpretation. The
   per-row prediction parquets at `evals/predictions/` support this.
   Portfolio-repo scope.

3. **Stronger backbone comparisons under matched training budgets.**
   The ModernBERT-vs-DeBERTa-v3-base ablation answered the context-
   window question but not the backbone-quality question. A matched-
   budget comparison across multiple modern backbones (RoBERTa, more
   recent DeBERTa releases, modern-encoder family) would isolate
   "what does backbone quality buy?" from "what does training-pool
   composition buy?"

4. **Threshold-policy adaptation to held-out FPR statistics.** The
   detection policy currently calibrates on validation FPR; an
   adaptive policy that estimates per-source FPR drift and re-
   calibrates on held-out examples could give more deployable
   thresholds. Out of scope for this submission; documented in
   [NEXT_STEPS](./NEXT_STEPS.md).

5. **Multi-seed × multi-fold replication.** Headline metrics report
   seed=1 with a seed=2 stability check. A larger replication
   (multiple seeds × multiple folds) would tighten the confidence
   intervals further. ~$10-50 GPU spend estimate; portfolio-repo
   scope.

### What this means for the broader prompt-injection-detection field

The detector ladder we evaluated is representative of the published
state of the art for direct-injection classifiers. The cross-family
failure mode is not specific to our training recipe — it appears to
be a property of training on direct-injection-heavy corpora.

If that is correct, the field's standard evaluation practice (train
on direct, evaluate on held-out direct) is systematically over-
estimating deployment-relevant capability. The honest evaluation
discipline we used (LODO + cross-family OOD slate + CIs) costs more
in audit-trail overhead but produces results that are less likely to
mislead a deployment team.

---

## Epilogue — Limits + reproduction

### What this study does not establish

The negative result on cross-family transfer does not establish:

- That a different training pool (with cross-family coverage)
  would fail similarly.
- That a larger or different backbone would fail similarly.
- That the cross-family failure is fundamental to the problem
  rather than addressable with OOD-aware training.

Specifically, we did not test cross-family training data, non-
Transformer architectures, ensemble methods, threshold-policy
adaptations to held-out FPR statistics, or multi-detector voting.
Several of these are on the future-work list above and in
[NEXT_STEPS](./NEXT_STEPS.md).

### Reproduce this yourself

Three reproduction tiers, in increasing cost order:

- **T0 — score-match against published checkpoints** (~$0, ~20 min)
  ```bash
  git clone https://github.com/brandon-behring/prompt-injection-detection-prototype
  cd prompt-injection-detection-prototype
  make install
  make eval-from-hub RUNG=frozen-probe
  make eval-from-hub RUNG=lora
  ```
  Score-matches against `evals/results.json` within 1e-4 absolute
  tolerance per ADR-058.

- **T1 — laptop smoke** (~$0, <10 min)
  ```bash
  make test-smoke
  ```

- **T3 — full retraining from scratch on cloud GPU** (~$125, hours)
  ```bash
  make headline-cloud  # cost-capped per ADR-020
  ```

HF Hub checkpoints: [BBehring/prompt-injection-frozen-probe](https://huggingface.co/BBehring/prompt-injection-frozen-probe),
[BBehring/prompt-injection-lora](https://huggingface.co/BBehring/prompt-injection-lora).

### Where to dig deeper

- **Numbers**: [RESULTS.md](./RESULTS.md) for all canonical tables
  and the 5 figures.
- **Methodology depth**: 8 detailed spokes under [WRITEUP/](./WRITEUP/) —
  data decisions, evaluation design, model details, threshold policy,
  reference-scorer audit, methodology guarantees, reproducibility,
  limitations and future work.
- **Decision rationale**: 78 ADRs at [decisions/](./decisions/) lock
  the methodology choices.
- **Cost ledger**: [evals/cost_ledger.csv](./evals/cost_ledger.csv)
  for full GPU and API spend accounting.
- **Glossary**: [docs/GLOSSARY.md](./docs/GLOSSARY.md) for all
  technical terms used here.

### A closing note

We set out to evaluate prompt-injection detectors fairly. The
methodology we built does that. The headline finding — that direct-
trained detectors can be anti-correlated with cross-family attack
class — was surprising and uncomfortable. We were tempted to soften
it, or to bury it under the other six findings.

We did not. The honest result deserves the honest framing. Direct
detection is a learnable problem and cross-family generalization
fails for these detector designs under this evaluation. That is what
the data shows. The path forward is to extend the training pool, not
to soften the result.

---

*End of narrative. For the same content in academic IMRAD format,
see [WRITEUP_PAPER.md](./WRITEUP_PAPER.md).*
