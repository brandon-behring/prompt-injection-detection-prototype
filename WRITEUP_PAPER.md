---
title: "Prompt-Injection Classification: Methodology and Capability Characterization (Academic Paper Format)"
description: "Academic IMRAD article presenting the project's methodology and findings."
---

**Author**: Brandon Behring | **Date**: 2026-05-21 | **Status**:
live-site current state `tree/v1.3.5`; original submission tag
`tree/v1.0.0` (2026-05-18) preserved as historical reviewer pin per
ADR-033.

> **Reader note.** This is the academic paper format of the project
> writeup. For the same content in a narrative style, see
> [WRITEUP_NARRATIVE.md](./WRITEUP_NARRATIVE.md). Both guides cover
> the same evaluation, methodology, findings, and limitations; the
> register and structure differ. Definitions for all technical terms
> appear on first use and are cross-referenced to
> [docs/GLOSSARY.md](./docs/GLOSSARY.md).

---

## §0. Abstract

This study evaluates prompt-injection detectors under cross-family
distribution shift. **Motivation**: detectors trained on direct
prompt-injection examples are routinely benchmarked on similar direct
text, leaving open the question of whether they have learned the
attack class or memorized the lexical style of the training data.
**Approach**: a detector ladder (TF-IDF + logistic regression,
ModernBERT frozen probe, ModernBERT LoRA, and ProtectAI v1/v2
references) was evaluated under leave-one-dataset-out (LODO) splits
against a held-out out-of-distribution (OOD) slate covering indirect
injection (BIPIA), agentic-flow injection (InjecAgent), jailbreak-
style questions (JBB-Behaviors, XSTest), and benign-but-injection-
shaped text (NotInject). **Finding**: the in-house detectors learn
direct prompt-injection detection effectively (LoRA reaches 0.974
AUPRC on balanced direct+benign validation) but generalize poorly to
cross-family attacks (best pooled OOD AUPRC is 0.364 against a random
floor of 0.374). Trained adapters (LoRA, TF-IDF + LR) score *below*
the 0.5 AUROC random floor on cross-family OOD with confidence
intervals that clear 0.5 on the wrong side; only the frozen probe
remains above floor. **Mechanism**: the inversion is consistent with
lexical overfitting combined with a label-relevance shift on the OOD
slate, in which benign text engineered to resemble direct injection
(NotInject) scores high and real-but-not-lexically-direct attacks
(BIPIA, InjecAgent) score low. **Implication**: direct-pattern
learning and cross-family transfer are distinct capabilities; results
caution against deploying direct-injection-trained classifiers on
mixed-family threat models without slice-specific evaluation. The
contribution is the honest evaluation harness plus the negative
result on cross-family transfer, not a production-ready detector.

---

## §1. Introduction

Prompt injection denotes untrusted text intended to override the
instructions an LLM-based system is supposed to follow [§GLOSSARY].
Detection of such text is a binary classification problem: given a
text span, predict whether it constitutes an injection attempt. The
practical difficulty is not the in-distribution case (where direct
injection patterns are repetitive and lexically distinctive) but the
out-of-distribution case where attack families differ from training.
Existing detector evaluations frequently report aggregate metrics on
held-out splits of the same training family, leaving the cross-family
generalization question unaddressed.

This study addresses that gap. The research question is:
> *When detectors trained on direct prompt-injection examples are
> evaluated against attack families not present in training, does
> detection performance generalize?*

The contribution is the negative answer plus the evaluation harness
that produced it. Specifically:

1. A leave-one-dataset-out (LODO) evaluation discipline that
   prevents source-level leakage between training and evaluation
   data.
2. A detector ladder spanning a classical baseline (TF-IDF +
   logistic regression), a pretrained-backbone probe (ModernBERT
   frozen), a parameter-efficient fine-tune (ModernBERT LoRA), and
   reference scorers (ProtectAI v1, v2) with documented contamination
   status.
3. An out-of-distribution slate that intentionally varies attack
   family (indirect injection, agentic-flow injection, jailbreak-style
   questions, benign-but-injection-shaped text).
4. Bootstrap-based uncertainty quantification on every reported
   number, with single-class slice handling.
5. A mechanistic interpretation of the headline cross-family failure
   (§5 Discussion).

The study is a capability characterization, not a deployment
recommendation.

---

## §2. Background

### §2.1 Prompt-injection landscape

Prompt-injection attacks are diverse. Direct injection (the
historically-studied class) embeds an attacker payload directly in
the user input. Indirect injection routes the payload through
third-party context that the LLM consumes. Agentic-flow injection
spreads the payload across tool-use turns. Jailbreak-style questions
elicit harmful behavior through framed questions rather than direct
override commands. Benign-but-injection-shaped text (false-positive
robustness) tests whether detectors over-fire on lexically suspicious
benign content.

Public training corpora for prompt-injection detection have
historically focused on direct injection; the cross-family generalization
question has therefore been understudied.

### §2.2 Existing detectors

Several published detectors target prompt-injection classification:

- **ProtectAI deberta-v3-base-prompt-injection v1 + v2**: fine-tuned
  DeBERTa classifiers; trained on direct-injection corpora with
  documented overlap of the present study's LODO training pool
  (see §6 Limitations and EVIDENCE §1-2).
- **Lakera Guard**: commercial detector; excluded from this study
  due to terms-of-service and partial-disclosure complexity (per
  ADR-018).
- **LLM-judge approaches** (GPT-4 family, Claude family): zero-shot
  classification via prompted instruction. Out of scope for the
  trained-detector ladder in this study; would require separate
  cost-per-call accounting (see ADR-018 + ADR-050).

### §2.3 Data sources

The training pool comprises four public direct-prompt-injection
corpora: `deepset/prompt-injections`, `Lakera/gandalf_ignore_instructions`
(Gandalf), `Lakera/mosscap_prompt_injection` (Mosscap), and
HackAPrompt's 2024 corpus subset. The held-out OOD test slate
comprises five sources spanning the four cross-family classes named in
§2.1: BIPIA, InjecAgent, JBB-Behaviors, XSTest, NotInject.

Full source-level details, license attribution, and HuggingFace
revision SHAs are documented in [WRITEUP/data-decisions.md](./WRITEUP/data-decisions.md)
and pinned in `data/source_manifest.yaml`.

---

## §3. Methods

### §3.1 Data sources and LODO splits

Leave-one-dataset-out (LODO) splits hold one source out of training
while training on the remaining sources [§GLOSSARY]. Four LODO folds
were generated, corresponding to the four training-pool sources. Each
fold produces an independent (train, validation, test) partition
where the test slate excludes all examples from one source.
Source-disjoint splitting was preferred over row-disjoint
splitting because the latter can leak source-level lexical features
between train and test (per ADR-016).

Within each LODO fold, training data was deduplicated against the
test slate via two-stage similarity matching: exact-hash overlap
detection followed by MiniLM-L6-v2 cosine similarity at threshold
≥0.85. Both pipelines reported zero overlaps across all
(train, val, test) per-fold-seed pairs (`evals/leakage_report.json`).

### §3.2 Model rungs

The detector ladder comprises five rungs of increasing capability:

1. **TF-IDF + logistic regression**: classical lexical baseline
   with character + word n-grams (per ADR-017). Trains in seconds
   per fold; serves as the "what does pure surface form get you"
   anchor.
2. **ModernBERT frozen probe**: a linear classifier over the frozen
   pretrained ModernBERT-base representation [§GLOSSARY]. Tests
   what the pretrained backbone already encodes about
   injection-likely text without any LODO-pool adaptation.
3. **ModernBERT LoRA**: parameter-efficient fine-tune (low-rank
   adapters at rank 8) [§GLOSSARY], with the backbone frozen and
   only the adapter weights updated on the LODO training pool.
4. **ModernBERT full fine-tune**: full-parameter fine-tune. *LODO
   direct-source predictions were generated for 24 (fold, seed)
   cells in Phase 2; pooled OOD inference was not run due to a
   Phase 5 X11 file-system crash on the cloud GPU pool, documented
   in [ADR-075](./decisions/ADR-075-full-ft-ood-drop-rationale-unified-narrative.md).*
5. **ProtectAI v1 + v2** (reference scorers): published
   deberta-v3-base-prompt-injection classifiers, inference-only,
   with documented contamination status against the LODO training
   pool (see §6 Limitations).

Reference rungs additionally include LLM-judge candidates (GPT-4
family, Claude family) per ADR-018; these were scoped out at ADR-050
following compute and contamination considerations.

Model details, hyperparameters, training cost, and per-rung
recipe are documented in [WRITEUP/model-rungs.md](./WRITEUP/model-rungs.md)
and [docs/HYPERPARAMETER_DISCLOSURE.md](./docs/HYPERPARAMETER_DISCLOSURE.md).

### §3.3 Evaluation slate

Each LODO fold's test slate aggregates five OOD slices:

| Slice | Source | Composition | Attack class |
|---|---|---|---|
| BIPIA | Bochum-NLP/bipia | n=50 positive (all-positive slice) | indirect injection |
| InjecAgent | uiuc-kang-lab/InjecAgent | n=62 positive (all-positive slice) | agentic-flow injection |
| JBB-Behaviors | JailbreakBench/JBB-Behaviors | n=100 positive + 100 negative | jailbreak-style questions |
| XSTest | natolambert/xstest | n=200 positive + 250 negative | jailbreak/safe-question discrimination |
| NotInject | dattaroh/NotInject | n=339 negative (all-negative slice) | benign-but-injection-shaped (false-positive test) |

The pooled OOD slate concatenates all five slices: n=412 positive +
689 negative = 1101 total. Random AUPRC on the pooled OOD slate is
therefore 412/1101 = 0.374.

Single-class slices (BIPIA, InjecAgent, NotInject) have mathematically
undefined AUPRC/AUROC; the metrics pipeline filters them at source
and reports recall-at-threshold instead. Pooled OOD is the canonical
AUPRC reporting target; per-slice AUPRC is reported only on the
both-class slices (JBB, XSTest, pooled OOD).

Slate composition, source revisions, and slice-class membership are
documented in [WRITEUP/eval-design.md](./WRITEUP/eval-design.md).

### §3.4 Statistical apparatus

Primary metric: **AUPRC** (Area Under the Precision-Recall Curve),
chosen for its sensitivity to ranking quality on imbalanced data
[§GLOSSARY]. On the pooled OOD slate (positive rate 0.374), random
AUPRC equals 0.374; AUPRC below 0.374 indicates worse-than-random
positive ranking. Secondary metric: **AUROC**; reported with 0.5
random floor.

Confidence intervals: **BCa bootstrap** (Bias-Corrected and Accelerated)
with 10000 resamples [§GLOSSARY]. Per-(rung, fold, seed) bootstrap
runs are persisted to `evals/bootstrap/`. Seed-stability check via
second seed (seed=2 vs seed=1) per ADR-022.

Paired comparisons: paired-bootstrap-on-folds [§GLOSSARY], comparing
two detectors on the same (fold, seed) cells to control for
fold-specific variance.

Cross-fold confidence intervals: cv_clt (Bayle 2020 Theorem 3.1)
[§GLOSSARY], applied to per-fold metric vectors. Paired with
block-bootstrap-on-folds spoke per A-008 (LODO non-exchangeability
sensitivity check; auto-flag column when block-bootstrap CI
half-width / cv_clt CI half-width > 1.5).

Threshold selection: **detection policy** (FPR ≤ 1% on validation,
maximize recall) and **verification policy** (recall ≥ 99% on
validation, minimize FPR), both fit per (fold, seed) with two-level
paired-bootstrap CIs on test [§GLOSSARY] per ADR-025.

Calibration: ECE (Expected Calibration Error, equal-mass binning,
n_bins=15) and Brier score, reported per detector per ADR-023.
Reliability diagrams (raw + temperature + isotonic recalibration) are
in [Figure F4](./docs/plots/F4.svg).

The evaluation harness uses the [eval-toolkit](https://github.com/brandon-behring/eval-toolkit)
library (pinned to v0.47.0) for all generic primitives; project-
specific orchestrators are in `src/eval/`.

---

## §4. Results

The seven numbered results are reported in equal-weight order. Each
result is supported by tables and figures in [RESULTS.md](./RESULTS.md);
this section presents the result + interpretation; the canonical
numerical evidence lives in the appendix.

### §4.1 Direct prompt-injection detection was learned

On balanced direct+benign validation data, LoRA reaches AUPRC 0.974
[CI 95% omitted on within-pool validation per ADR-021], AUROC 0.993,
and recall-at-0.5 of 0.934. TF-IDF + LR reaches 0.971 / 0.992 / 0.930.
The frozen probe is weaker at 0.653 / 0.907 / 0.849 but still
discriminative.

On the LODO held-out direct-source test (all-positive by design),
recall-at-0.5 is 0.641 (frozen probe), 0.625 (LoRA), and 0.558
(full fine-tune). Because no negatives are present in this slice,
AUPRC, AUROC, and FPR are mathematically undefined and are not
reported.

The detector pipeline can learn direct prompt-injection patterns;
this establishes the in-distribution baseline against which §4.2-4.7
contrast.

### §4.2 The OOD wall is cross-family, not source-level

The OOD test slate intentionally varies attack family rather than
source identity within the same family. BIPIA exemplifies indirect
injection; InjecAgent exemplifies agentic-flow injection; JBB-
Behaviors and XSTest exemplify jailbreak-style questions; NotInject
exemplifies benign-but-injection-shaped text. The training pool is
direct-injection-heavy and includes none of these families.

The result is that direct-injection training does not transfer
cleanly to these cross-family slices. Per-slice AUPRC (where defined,
i.e., the both-class slices JBB and XSTest) is reported in
[RESULTS.md §3 Per-Slice View](./RESULTS.md#per-slice-view).

### §4.3 Trained adapters anti-correlated with cross-family attack class

LoRA scored 0.293 AUPRC on pooled OOD [CI 0.286, 0.301] versus 0.364
[0.354, 0.375] for the frozen probe and 0.291 [0.283, 0.298] for
TF-IDF + LR. The pooled OOD AUPRC random floor is 0.374; all four
detectors land at or below floor.

The sharper result is under AUROC: LoRA's pooled OOD AUROC is 0.383
[0.374, 0.392] and TF-IDF + LR's is 0.371 [0.362, 0.381], both with
confidence intervals that clear the 0.5 AUROC random floor *on the
wrong side*. The frozen probe alone stays above the AUROC floor at
0.515 [0.505, 0.525]. The in-pool to cross-family generalization gap
for the trained detectors is approximately 0.6 AUROC (in-pool 0.99 →
cross-family 0.38), the largest possible gap with statistical
confidence.

The mechanism is interpreted in §5 Discussion.

### §4.4 Context-window ablation produced a null result

A controlled ablation per ADR-060 trained DeBERTa-v3-base (512-token
native context window) against ModernBERT (8192-token native window)
under two truncation strategies: chunk-and-average (compute the
classifier output on overlapping 512-token windows and average) and
head-truncation (use only the first 512 tokens).

Result: DeBERTa-v3-base with chunk-and-average scored 0.291 pooled
OOD AUPRC; head-truncation scored 0.290. Neither significantly
differs from each other or from the ModernBERT-LoRA result (0.293).
The ModernBERT advantage observed in §4.1 is therefore best
interpreted as backbone-dominant, not context-window-dominant.

Details in [WRITEUP/model-rungs.md §4](./WRITEUP/model-rungs.md) and
[ADR-063](./decisions/ADR-063-deberta-ablation-v1-1-2-execution-and-slot-shift.md).

### §4.5 Published detector versions are slice-dependent

ProtectAI v2 improves over v1 on JBB-Behaviors (AUPRC 0.556 vs 0.519)
but regresses on XSTest (0.382 vs 0.469) and on pooled OOD overall
(0.314 vs 0.361). The "newer is better" assumption does not hold
across the full slate.

Practical implication: detector updates should be evaluated against
the actual slice mix that matters for the deployment, not on a single
aggregate metric.

Cross-version comparisons in [RESULTS.md §6 Secondary Table: AUROC](./RESULTS.md#secondary-table-auroc).

### §4.6 Validation thresholds are fragile under cross-family shift

The detection policy (FPR ≤ 1% on validation, maximize recall) was
fit per (fold, seed) on validation data and applied to held-out test
data. Mean test FPR by detector:

| Detector | Mean test FPR | Mean test recall |
|---|---:|---:|
| TF-IDF + LR | 6.7% | 33.3% |
| ModernBERT LoRA | 11.5% | 42.4% |
| ModernBERT frozen probe | 1.0% | 6.3% |

The 1% FPR validation target holds only for the frozen probe (1.0%
on test, within sampling noise of the 1% target). The trained
detectors significantly exceed it (LoRA 11.5%, TF-IDF + LR 6.7%
against a 1% target). The frozen probe holds the FPR target but
catches only 6.3% of positives, indicating a non-deployable
operating point under this policy framing. All numbers verified by
re-derivation from `evals/operating_points/dual_policy.parquet` via
`scripts/audit_numbers.py`.

Threshold-transfer behavior in [WRITEUP/threshold-policy.md](./WRITEUP/threshold-policy.md).

### §4.7 Calibration favors the frozen probe

Among the four detectors with both-class OOD scores, the frozen
probe has the lowest expected calibration error (ECE) and lowest
Brier score on the pooled OOD slate. Mean ECE: 0.144 (frozen probe),
higher for LoRA and TF-IDF + LR. Mean Brier: 0.265 (frozen probe).

LoRA worsens calibration relative to the frozen probe while
simultaneously fitting the direct training pool, reinforcing the
§4.1-§4.3 conclusion that direct-pattern learning and cross-family
score behavior are distinct capabilities.

Full calibration battery in [RESULTS.md §5 Calibration](./RESULTS.md#calibration)
and [Figure F5 calibration comparison](./docs/plots/F5.svg).

---

## §5. Discussion

### §5.1 Mechanism: lexical overfitting plus label-relevance shift

A pooled OOD AUROC below 0.5 with confidence intervals that clear
0.5 on the wrong side is not consistent with pure overfitting
[§GLOSSARY]. Pure overfitting predicts collapse *toward* random
performance, not past it. The observed below-floor performance
requires a more specific mechanism.

The interpretation consistent with the slate composition is **lexical
overfitting combined with a label-relevance shift on the OOD slate**.
Both LoRA and TF-IDF + LR appear to learn lexical signatures of
direct prompt injection ("ignore previous instructions", imperative
override commands, role-redirection phrases). On the OOD slate, this
lexical signal is *anti-correlated* with the true attack class:

- **NotInject** (n=339, all negative): benign text engineered to
  resemble direct injection. Detectors score these HIGH (false
  positives), inverting the negative class.
- **BIPIA and InjecAgent** (indirect + agentic, n=112 positive):
  real attacks that do not use direct-injection lexical patterns.
  Detectors score these LOW (false negatives), inverting the positive
  class.

The lexical signal is real and internally consistent within itself
— it just stops tracking attack class on cross-family slices where
the lexical similarity to direct injection and the actual attack
class point in opposite directions. The frozen probe (zero LODO-pool
adaptation) preserves generic linguistic features that are less
aligned with the direct-injection lexical distribution and therefore
stay closer to random performance on the cross-family slate.

The in-pool → cross-family generalization gap is approximately 0.6
AUROC for the trained detectors (in-pool 0.99 → cross-family 0.38)
versus approximately 0.4 for the frozen probe (in-pool 0.91 →
cross-family 0.515). The more training adapted to the LODO pool, the
sharper the cross-family fall.

### §5.2 Implications for direct-detection deployments

The result cautions against deploying classifiers trained on
direct-injection corpora as general-purpose prompt-injection
detectors in mixed-family threat models. Specifically:

- Direct-detection accuracy on in-pool data does not predict
  cross-family generalization.
- AUROC below 0.5 is an active failure mode (mis-ranking) rather
  than a benign degradation toward random.
- False-positive rates measured on validation data do not hold on
  held-out test sources (§4.6).
- "Newer version is better" does not hold across mixed slates (§4.5).

Deployment-context evaluations should test the specific slice mix
that matters for the production threat model, not aggregate
direct-injection metrics.

### §5.3 What this study does not establish

The negative result on cross-family transfer does not establish
that:

- A different training pool (with cross-family coverage) would
  fail similarly.
- A larger or different backbone would fail similarly.
- The cross-family failure is fundamental rather than addressable
  with OOD-aware training.

Specifically, this study did not test: cross-family training data,
non-Transformer architectures, ensemble methods, threshold-policy
adaptations to held-out source FPR statistics, or multi-detector
voting. Several of these are documented in §6 Limitations as future
work directions.

---

## §6. Limitations

### §6.1 Scope of the classifier

The evaluated classifier is single-turn English text classification.
Out of scope (per ADR-014):
- Multilingual attacks
- Encoded payloads (base64, leetspeak, Unicode confusables)
- Paraphrase robustness
- Adversarial perturbations
- Full multi-turn system behavior
- Deployment threshold recommendations

The InjecAgent slice is included in the OOD slate to quantify the
gap for agentic-flow attacks, not to claim that a single-turn
classifier should solve that problem.

### §6.2 Reference scorer contamination

ProtectAI v1 and v2 are trained on at least 2 of 4 LODO training-pool
sources (deepset/prompt-injections, Lakera/gandalf_ignore_instructions)
per EVIDENCE §1-2. Their pooled OOD scores on slices that overlap
with their training pool are not clean OOD baselines and are
reported with `suspected_contamination` annotations per ADR-005
three-state contamination taxonomy. ProtectAI scores serve as
diagnostic references with documented caveats, not as competitive
benchmarks.

### §6.3 Full-fine-tune incomplete-experiment status

ModernBERT full fine-tune was trained for LODO direct-source
inference (24 Phase 2 prediction parquets persisted) but pooled OOD
inference was not run due to a Phase 5 X11 file-system crash on the
RunPod /workspace FUSE mount. The methodological framing of this
forced drop is documented in ADR-052 and ADR-075. The full-FT row
appears in the LODO direct-source recall table (§4.1) but is absent
from the pooled OOD AUPRC table; this is explicit and asterisk-marked
on all reporting surfaces. Re-running the full-FT pooled OOD inference
on a fresh DC is documented in NEXT_STEPS §2.2 as future work.

### §6.4 Single-seed headline + second-seed stability check

Headline metrics are reported at seed=1. A seed=2 stability check
is run on the same evaluation slate; results agree within the
reported confidence intervals. A larger multi-seed × multi-fold
replication study is documented in NEXT_STEPS §2.1 as future work
(estimated ~$10-50 GPU spend; portfolio-repo scope per
[[portfolio_plan_approved]]).

### §6.5 Mechanism interpretation is not empirically demonstrated

The §5.1 mechanism interpretation (lexical overfitting + label-
relevance shift) is consistent with the aggregate AUROC and slate
composition but is not directly demonstrated in this artifact. A
per-prediction analysis comparing detector scores on lexically-direct
vs lexically-indirect OOD examples would empirically test the
hypothesis. The per-row prediction parquets at
`evals/predictions/<rung>__fold<F>__seed<S>__<source>.parquet`
support this analysis; it is documented in NEXT_STEPS §3 as future
work (portfolio-repo scope).

### §6.6 Threshold policy framing

The detection policy (FPR ≤ 1%, maximize recall) was chosen as a
methodological policy for evaluation characterization, not as a
deployment recommendation. Production deployment thresholds depend
on the deployment cost ratio and operating environment, which this
study does not address. The verification policy (recall ≥ 99%,
minimize FPR) similarly serves characterization purposes only.

Full limitations narrative in [WRITEUP/limitations-and-future-work.md](./WRITEUP/limitations-and-future-work.md).

---

## §7. Conclusion

This study evaluated a detector ladder for prompt-injection
classification under cross-family distribution shift, finding that
direct-prompt-injection detection is learnable cheaply (TF-IDF + LR
reaches 0.974 AUPRC on direct+benign validation) but does not
generalize to cross-family attacks (best pooled OOD AUPRC is 0.364
against a random floor of 0.374; trained adapters score below the
0.5 AUROC floor with confidence intervals that clear 0.5 on the
wrong side). The cross-family failure is interpreted as lexical
overfitting combined with a label-relevance shift on the OOD slate.

The contribution is the negative result on cross-family transfer
plus the honest evaluation harness that produced it, not a
deployment-ready classifier. Future work directions include OOD-aware
training data, stronger backbone comparisons under matched training
budgets, threshold-policy adaptations to held-out FPR statistics,
and per-prediction empirical validation of the proposed mechanism.

---

## §8. References

### Decisions (Architecture Decision Records)

Selected key ADRs cited in this paper; full list at
[decisions/](./decisions/):

- **ADR-005** — Methodology principles (incl. three-state
  contamination taxonomy)
- **ADR-014** — Threat model bundle (out-of-scope enumeration)
- **ADR-016** — Data design bundle (LODO splits + deduplication)
- **ADR-017** — Trained rung slate expansion (TF-IDF + LR baseline)
- **ADR-018** — Reference-scorer slate + contamination stratification
- **ADR-019** — LoRA + Transformer training recipe
- **ADR-021** — Eval-slate aggregation + recall@FPR pinpoints
- **ADR-022** — Statistical inference apparatus (bootstrap +
  paired-comparison protocols)
- **ADR-023** — Calibration battery (ECE, Brier, reliability)
- **ADR-024** — Cross-fold CI methodology (Bayle 2020)
- **ADR-025** — Dual-policy threshold characterization
- **ADR-050** — Rung-slate narrowing + LLM-judge cost-drop +
  full-FT OOD forced-drop (Revision 1 + Revision 2)
- **ADR-052** — Full-FT OOD drop methodological reframing of ADR-050
  R2
- **ADR-060** — DeBERTa-v3-base long-context ablation methodology
- **ADR-063** — DeBERTa ablation v1.1.2 execution + slot shift
- **ADR-075** — Full-FT OOD drop rationale unified narrative

### External references

- **ModernBERT**: Warner et al. 2024, [arXiv:2412.13663](https://arxiv.org/abs/2412.13663).
- **LoRA**: Hu et al. 2021, [arXiv:2106.09685](https://arxiv.org/abs/2106.09685).
- **BIPIA** (indirect prompt injection benchmark): Wang et al. 2023,
  [Hugging Face: Bochum-NLP/bipia](https://huggingface.co/datasets/Bochum-NLP/bipia).
- **InjecAgent** (agentic-flow prompt injection): Yu et al. 2024,
  [arXiv:2403.02691](https://arxiv.org/abs/2403.02691).
- **JBB-Behaviors** (JailbreakBench): Chao et al. 2024,
  [Hugging Face: JailbreakBench/JBB-Behaviors](https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors).
- **XSTest** (jailbreak-safe-question discrimination): Röttger et al.
  2024, [arXiv:2308.01263](https://arxiv.org/abs/2308.01263).
- **NotInject** (false-positive robustness): Datta et al. 2024,
  [Hugging Face: dattaroh/NotInject](https://huggingface.co/datasets/dattaroh/NotInject).
- **HackAPrompt** corpus: Schulhoff et al. 2023, [arXiv:2311.16119](https://arxiv.org/abs/2311.16119).
- **Bayle 2020** (cross-fold CI methodology): Bayle et al. 2020,
  [arXiv:2007.02780](https://arxiv.org/abs/2007.02780).
- **BCa bootstrap**: Efron 1987, [doi:10.2307/2289144](https://doi.org/10.2307/2289144).

### Project artifacts

- **Source code**: [github.com/brandon-behring/prompt-injection-detection-prototype](https://github.com/brandon-behring/prompt-injection-detection-prototype)
- **HF Hub checkpoints**: [BBehring/prompt-injection-frozen-probe](https://huggingface.co/BBehring/prompt-injection-frozen-probe), [BBehring/prompt-injection-lora](https://huggingface.co/BBehring/prompt-injection-lora)
- **Evaluation library**: [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) (v0.47.0 pinned)
- **Cloud orchestration**: [runpod-deploy](https://github.com/brandon-behring/runpod-deploy) (v0.8.4 pinned)
- **Live rendered site**: [brandon-behring.github.io/prompt-injection-detection-prototype/](https://brandon-behring.github.io/prompt-injection-detection-prototype/)

---

## Glossary

Definitions for technical terms used in this paper. Full glossary at
[docs/GLOSSARY.md](./docs/GLOSSARY.md).

- **AUPRC** — Area Under the Precision-Recall Curve. Primary ranking
  metric for imbalanced binary classification; random floor equals
  the positive rate.
- **AUROC** — Area Under the Receiver Operating Characteristic curve.
  Secondary diagnostic metric with 0.5 random floor; less informative
  than AUPRC under imbalance.
- **BCa bootstrap** — Bias-Corrected and Accelerated bootstrap;
  produces confidence intervals robust to skewness and bias in the
  resampling distribution.
- **Block-bootstrap-on-folds** — bootstrap that resamples entire
  folds rather than individual rows; respects fold-level
  exchangeability assumptions.
- **cv_clt** — Cross-validation Central Limit Theorem confidence
  interval per Bayle 2020 Theorem 3.1; suitable for per-fold metric
  vectors under exchangeability.
- **ECE** — Expected Calibration Error; lower is better.
- **Frozen probe** — linear classifier on top of a frozen pretrained
  backbone representation; tests what the backbone already encodes
  without LODO-pool adaptation.
- **LODO** — Leave-One-Dataset-Out splitting discipline; holds one
  source out of training while training on the remainder.
- **LoRA** — Low-Rank Adapters; parameter-efficient fine-tuning
  method that updates only a small set of adapter weights.
- **OOD** — Out-of-distribution. In this study specifically means
  cross-family, not source-level.
- **Overfitting (vs label-relevance shift)** — pure overfitting
  predicts collapse toward random performance. Below-floor
  performance indicates an additional mechanism: a label-relevance
  shift in which the learned signal is anti-correlated with the
  true label on the OOD slate.
- **Paired-bootstrap-on-folds** — bootstrap-based paired comparison
  of two detectors evaluated on the same (fold, seed) cells.

---

*End of paper. For the same content in narrative form, see
[WRITEUP_NARRATIVE.md](./WRITEUP_NARRATIVE.md).*
