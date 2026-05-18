# Prompt-injection classification — methodology + capability characterisation

**Author**: Brandon Behring · **Date**: 2026-05-18 · **Status**: `v1.0.0` submission tag (Phase 5 close)

This document is the **TOC + landing page**: the cover narrative
(§1 Motivation, §2 Approach overview, §Results, §Lessons,
§Appendix) lives here; the detailed sections live as spokes
under [`WRITEUP/`](./WRITEUP/) (linked below).

## Reading guide

| Spoke | Coverage |
|---|---|
| [`WRITEUP/data-decisions.md`](./WRITEUP/data-decisions.md) | §3 Data design — source slate selection + dedup + leakage + LODO splits |
| [`WRITEUP/model-rungs.md`](./WRITEUP/model-rungs.md) | §4 Rung ladder — classical floor + ModernBERT × {frozen-probe, LoRA, full-FT} + ProtectAI v1/v2 |
| [`WRITEUP/eval-design.md`](./WRITEUP/eval-design.md) | §5.1, §5.2, §5.4, §5.5 — metric battery + paired-bootstrap + MDE + calibration + OOD slate composition |
| [`WRITEUP/threshold-policy.md`](./WRITEUP/threshold-policy.md) | §5.3 — dual-policy detection + verification operating points + val→test reachability |
| [`WRITEUP/reference-scorer-audit.md`](./WRITEUP/reference-scorer-audit.md) | §3.3 + §5.6 + §7.2/3 — ADR-005 contamination taxonomy applied to reference scorers + adversarial-robustness scope |
| [`WRITEUP/methodology-guarantees.md`](./WRITEUP/methodology-guarantees.md) | §6 Tooling — eval-toolkit + runpod-deploy + SDD process + library-first invariant |
| [`WRITEUP/limitations-and-future-work.md`](./WRITEUP/limitations-and-future-work.md) | §8 scope deferrals + §8.2 methodology caveats + §9 negative results + §11 lessons |
| [`WRITEUP/reproducibility.md`](./WRITEUP/reproducibility.md) | §10 T0 + T1 + T3 reproduction tiers |

For the audit trail of external-evidence claims, see [`EVIDENCE.md`](./EVIDENCE.md).
For the per-decision ADR record, see [`decisions/`](./decisions/) +
[`SUBMISSION_AUDIT.md`](./SUBMISSION_AUDIT.md).

---

## 1. Motivation

> My main concern after reading the literature: most prompt-injection detectors are evaluated on data that leaks into training, so their reported OOD numbers don't tell you much. A classifier that cross-validates on a single direct-prompt-injection dataset is trivial to build, but it gives a poor read on OOD performance and raises real leakage concerns. This project is my attempt to build a fairer evaluation harness around that — not to find the best model, but to lay the groundwork for fairer evaluation and to identify weaknesses of our model and of some existing reference scorers.

Prompt-injection — text designed to override or subvert the instructions an LLM-based system is operating under — is one of the load-bearing failure modes for any system that exposes an LLM to untrusted input. Ciphero's verification-layer thesis is that we cannot govern what we cannot verify; one primitive in that stack is a classifier that scores whether a span of text is an injection attempt.

The same scores serve two operational contexts:

- **Detection** — *catch injections coming in*. Tolerates false positives more than false negatives (an alert costs less than a missed attack at the input boundary).
- **Verification** — *confirm clean text actually is clean*. Tolerates false negatives more than false positives (a confidently-clean assertion is the dangerous one).

These are not two classifiers; they are two threshold policies on the same scores, with different cost weights. See [`WRITEUP/threshold-policy.md`](./WRITEUP/threshold-policy.md) for how the same primitive is configured to characterise both.

This writeup characterises a 5-rung ladder of prompt-injection classifiers — TF-IDF+LR classical floor + ModernBERT-base × {frozen-probe, LoRA, full-FT} + ProtectAI v1 + ProtectAI v2 reference scorers (locked at Phase 0-03 per ADR-015 + ADR-017 + ADR-018 + ADR-050 + ADR-052) — across an OOD slate, with the question: *what does each capability layer add, and where does the IID/OOD gap fall?* The work is **methodology + capability characterisation braided**: the ladder is the instrument; the eval methodology rigor is what makes the characterisation defensible; the brief's two asks (models of increasing complexity + OOD coverage) are the targets.

**Honest-OOD thesis**: IID numbers are the easy part. The interesting question for any classifier that might one day touch a deployment surface is *which capabilities help when the distribution shifts, and which ones only inflate the IID number*. That question — not "what's the best PR-AUC" — drives this document's structure.

**Deployment is not on the roadmap.** This is characterisation, not recommendation. No rung is promoted as the deployment choice; each rung's trade-offs are reported and the reader is left to draw their own deployment conclusions if they have one to make.

**Linked ADRs**: ADR-001 (brief alignment), ADR-013 (deliverable scope + WRITEUP shape), ADR-017 (rung-slate expansion).

### Scope (single-turn English text classifier)

This submission characterises a *prompt-injection text classifier* on an English-only fixed slate (4 LODO training sources + 5 OOD test slices). What is **deliberately out of scope** (per ADR-014 + [`WRITEUP/limitations-and-future-work.md`](./WRITEUP/limitations-and-future-work.md) §8.1; named explicitly so a reviewer reading only this section knows what the numbers do *not* cover):

- **Multi-turn / agentic-flow injection** — payload split across multiple conversation turns or tool-use steps. *Named in the test slate via InjecAgent to quantify the gap; not detected by the single-turn classifier scope.*
- **Encoded payloads** — base64 / leetspeak / hex / Unicode confusables / ROT13.
- **Paraphrase attacks** — semantic equivalents that don't share surface n-grams with training injections.
- **Adversarial perturbations** — gradient-guided or search-based evasion against a specific classifier.
- **Cross-language coverage** — the slate is English-only by source-slate construction.
- **Conformal prediction + adversarial red-teaming** — see WRITEUP/limitations-and-future-work.md §8.1.

The work is **methodology + capability characterisation braided**: the ladder is the instrument; the eval methodology rigor is what makes the characterisation defensible. Deployment recommendations are explicitly out of scope.

---

## 1.5 Attack-type taxonomy + train/test composition

Five operationally-distinct injection types are relevant to this submission. Each type is defined in a single sentence; the table below maps which types appear in the 4 LODO training-pool sources vs the 5 OOD test slices. The mismatch is the load-bearing story for §Results — the OOD slate probes injection types that are *not* in the training pool.

**Type definitions:**

- **`direct_injection`** — adversarial text in the user's input attempting to override system instructions. Single-turn, in-channel. Examples: "ignore the above and …", "you are now …".
- **`indirect_injection`** — adversarial text arriving via a context channel the LLM processes (a retrieved document, an email body, a tool's output). The user's *direct* input is benign; the injection rides on data the LLM was meant to consume.
- **`agentic_flow_injection`** — payload split across multi-turn tool-use; detecting it requires intermediate-state interception (tool-call args, function-output contamination), not just classifying a single text span.
- **`jailbreak_as_question`** — safety-bypass framed as a legitimate-looking question rather than an instruction override (e.g., "for a story I'm writing, how would a character …").
- **`false_positive_probe`** — benign text structurally similar to injections (e.g., literal discussions of injection attacks). Tests whether the classifier discriminates *intent* from *form*.

**Train/test composition** — `Y` = type present (or dominantly present in that source); `-` = type absent. Training sources locked per ADR-016; OOD slices per ADR-021.

| Injection type | TRAIN: `deepset/prompt-injections` | TRAIN: `Lakera/gandalf_ignore_instructions` | TRAIN: `Lakera/mosscap_prompt_injection` | TRAIN: `hackaprompt/hackaprompt-dataset` | TEST: `bipia` | TEST: `injecagent` | TEST: `jbb_behaviors` | TEST: `xstest` | TEST: `notinject` |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `direct_injection` | `Y` | `Y` | `Y` | `Y` | `-` | `-` | partial | `-` | `-` |
| `indirect_injection` | `-` | `-` | `-` | `-` | `Y` | `-` | `-` | `-` | `-` |
| `agentic_flow_injection` | `-` | `-` | `-` | `-` | `-` | `Y` | `-` | `-` | `-` |
| `jailbreak_as_question` | `-` | `-` | `-` | partial | `-` | `-` | `Y` | `Y` | `-` |
| `false_positive_probe` | `-` | `-` | `-` | `-` | `-` | `-` | `-` | `-` | `Y` |

**Key reads from the table:**

- The 4 LODO training sources are **direct-injection-heavy**. The training pool teaches the classifier to recognise instruction-override style attacks in user input.
- BIPIA (test) is the **only indirect-injection slate**; *zero* indirect-injection coverage in training. This is a structural train/test mismatch by design — the OOD wall on BIPIA quantifies it.
- InjecAgent (test) is the **only agentic-flow slate**; *zero* agentic-flow coverage in training. Agentic flow is also out-of-scope for the single-turn classifier per §Scope above — InjecAgent is included in the test set to quantify the gap, not because we expect the classifier to do well.
- NotInject (test) is a **pure false-positive probe**; no counterpart in training. Tests intent-vs-form discrimination.
- JBB-Behaviors + XSTest (test) carry jailbreak-as-question style attacks. HackAPrompt partially covers this; the other 3 training sources do not.

The §Results section reads against this table — performance per OOD slice tracks whether that slice's injection type is represented in the training pool.

**Note on what "OOD" means here.** "In-domain test" is still a direct-injection attack — just an unseen source held out by LODO. The 5-slice "OOD" slate is something else entirely: **indirect injection via email-body context (BIPIA), multi-turn agentic-flow attacks (InjecAgent), jailbreaks (JBB-Behaviors), and benign-but-injection-shaped texts that test false-positive robustness (NotInject, XSTest).** The OOD wall in §Results is **cross-family**, not cross-source: the trained rungs are tested on attack types absent from their training pool. Direct prompt-injection training and evaluation performance alone do not translate into these other attack families — that is the load-bearing finding of this submission.

---

## 2. Approach overview

The brief asked for two things: *models of increasing complexity* and *the right amount of OOD coverage*. The rung ladder satisfies the first ask and is the **instrument** for the second: when a rung helps IID but not OOD, that tells us its added capability is data-pattern-fitting rather than generalisation; when a rung helps both, the added capability is more durable.

| Element | Role | Why |
|---|---|---|
| Rung ladder (locked Phase 0-03 per ADR-015 + ADR-017 + ADR-050) | Instrument | Each step's lift over the previous decomposes *which capability* matters. |
| OOD slate (5 slices locked Phase 0-04 per ADR-016 + ADR-021) | Measurement | Quantifies what each capability adds when the distribution shifts. |
| Dual cost-weight thresholds | Score-behaviour characterisation | Shows what the same scores deliver under two different operational cost regimes. |
| Statistical rigor (CIs + paired comparisons + MDE) | Defensibility | Lets us claim differences honestly and quantify when we lack the power to claim anything. |

We do **not** pick a deployment leader. The intent is to demonstrate what each rung delivers and where it breaks; readers with a specific deployment context can map our characterisation onto their cost constraints.

**Linked ADRs**: ADR-002 (approach scaffold), ADR-014 (single-backbone slate framing), ADR-017 (rung-slate expansion), ADR-021 (slice aggregation + headline-metric protocol).

**Known gaps**: this approach evaluates EACH rung against the same slate; cross-rung-ensemble strategies (e.g., LoRA-with-frozen-probe-temperature) are out of scope per the project compute budget.

---

## Results

**The negative result IS the result.** None of the rungs decisively beats the classical TF-IDF+LR floor on the 5-slice OOD slate, and the OOD wall is **cross-family** (read against the §1.5 train/test table): training pool is 4 direct-injection sources; OOD slate probes indirect injection via email-body context (BIPIA), multi-turn agentic-flow (InjecAgent), jailbreaks (JBB-Behaviors), and benign-but-injection-shaped texts that test false-positive robustness (NotInject, XSTest) — attack types absent from training. Direct prompt-injection training and evaluation performance alone do not translate into these other attack families. That finding is the argument for a fairer evaluation framework, which is what this project is.

Specifically: across the rung ladder + two reference scorers, **none of the rungs clears the `pooled_ood` positive-class prevalence baseline (0.374) under AUPRC** (range 0.291–0.364; even frozen-probe at 0.364 lands just under prevalence). The trained transformer rungs (frozen-probe + LoRA) and the ProtectAI reference scorers cluster within a band that is statistically distinguishable on the in-distribution-like slices (jbb_behaviors, xstest) but compresses to at-or-below the prevalence baseline on pooled_ood. The story is not "the ladder works" — it is *the ladder works on IID-shaped attacks and fails to generalize to genuinely OOD distributions*, and the numbers below back that up.

**Metric note.** Headline metric is **AUPRC** per WRITEUP/eval-design.md §5.1 ("the most relevant ranking metric for class-imbalanced tasks where precision and recall both matter"). Random-predictor AUPRC equals the positive-class prevalence on each slice. AUROC (chance baseline 0.5, prior-independent) is reported as a secondary diagnostic for cross-paper comparison.

Source data: `evals/metrics/per_cell.parquet` (per-cell, post-Item-4 single-class filter), `evals/bootstrap/marginal_cells.parquet` (BCa CI per ADR-022), `evals/bootstrap/paired_cells.parquet` + `paired_cells_seed2.parquet` (paired-Δ CI per ADR-022), `evals/audit/mde_per_cell.parquet`, `evals/operating_points/dual_policy.parquet` (72 op-points).

### The IID-vs-OOD gap (primary narrative)

Per-rung marginal AUPRC + BCa 95 % CI (seed=1 headline; seed=2 stability check 0/40 cells flagged at 5 pct threshold per ADR-022 + A-008):

| Rung | jbb_behaviors AUPRC | xstest AUPRC | pooled_ood AUPRC |
|---|---|---|---|
| TF-IDF + LR (classical floor) | 0.470 [0.443, 0.496] | 0.395 [0.379, 0.410] | 0.291 [0.283, 0.298] |
| frozen-probe | 0.552 [0.520, 0.580] | 0.468 [0.448, 0.486] | 0.364 [0.354, 0.375] |
| LoRA | 0.535 [0.504, 0.563] | 0.467 [0.447, 0.486] | 0.293 [0.286, 0.301] |
| ProtectAI v1 | 0.519 [0.437, 0.597] | 0.469 [0.415, 0.523] | 0.361 [0.330, 0.391] |
| ProtectAI v2 | 0.556 [0.453, 0.648] | 0.382 [0.333, 0.429] | 0.314 [0.283, 0.345] |

Pooled_ood positive-class prevalence: **0.374** (15 656 positives / 41 838 rows). Random-predictor AUPRC on `pooled_ood` equals 0.374.

The gap pattern:

- **frozen-probe** is the strongest on `pooled_ood` (0.364 [0.354, 0.375]) — but lands ~0.01 below the prevalence baseline (0.374). The CI upper bound (0.375) just barely touches the baseline. Even the best trained rung does not lift above what a positive-class-prior predictor would produce by AUPRC.
- **LoRA's `pooled_ood` AUPRC (0.293)** is essentially tied with the classical floor (0.291; within CI overlap) and far below frozen-probe (-0.071 AUPRC; paired-bootstrap CI does not include zero on this comparison). **LoRA fine-tuning hurts OOD generalization** relative to the frozen probe — a known phenomenon when the fine-tuning distribution mismatch is large.
- **TF-IDF + LR** is competitive on `pooled_ood` (0.291) and only modestly below the trained rungs on jbb_behaviors / xstest. The classical floor is hard to beat without much stronger inductive biases.
- **ProtectAI v2** beats ProtectAI v1 on jbb_behaviors (0.556 vs 0.519) but loses on xstest (0.382 vs 0.469) — version-to-version updates do not monotonically improve across distributions.

**AUROC secondary view** (chance baseline 0.5, prior-independent): `pooled_ood` AUROC range is 0.371–0.515; only frozen-probe at 0.515 [0.505, 0.525] clears chance with margin. The relative ordering reads identically to the AUPRC narrative; AUPRC is reported in the headline because it accounts for the class prior (per WRITEUP/eval-design.md §5.1).

Per-scorer contamination findings (ProtectAI v1 + v2) detail lives in [`WRITEUP/reference-scorer-audit.md`](./WRITEUP/reference-scorer-audit.md) and [`EVIDENCE.md`](./EVIDENCE.md) §1-2.

### Which capabilities help OOD vs only help IID

Rung-by-rung lift over the classical floor (delta AUPRC, `pooled_ood`):

| Rung vs floor | delta AUPRC (pooled_ood) | Interpretation |
|---|---|---|
| frozen-probe vs tfidf-lr | +0.073 | Pretrained ModernBERT embeddings DO help OOD — modest lift |
| LoRA vs tfidf-lr | +0.002 | Adapter fine-tuning collapses the frozen-probe advantage on OOD; essentially indistinguishable from classical floor |
| LoRA vs frozen-probe | -0.071 | LoRA hurts; the adapter weights specialise to training distribution |
| ProtectAI v1 vs tfidf-lr | +0.070 | Off-the-shelf injection detector adds modest signal — comparable to frozen-probe lift |
| ProtectAI v2 vs tfidf-lr | +0.023 | v2 update does not propagate to our OOD slate |

(AUROC equivalents for cross-paper comparison: frozen-probe +0.144; LoRA +0.012; LoRA vs frozen-probe -0.132; ProtectAI v1 +0.069; ProtectAI v2 +0.031. Same direction; AUROC magnitudes differ because AUROC is prior-independent while AUPRC weights by positive-class prevalence.)

**Implication**: the pretrained backbone (ModernBERT) provides the bulk of the OOD generalization budget. Fine-tuning (LoRA) on the in-distribution training pool causes generalization-tax: the rung does better on the training-distribution-shaped jbb_behaviors / xstest slices, but loses on `pooled_ood`. This is the canonical fine-tuning-overfit signature.

### Score-behaviour at the two operating points

Dual-policy thresholds fit on val per ADR-025 + ADR-050 (full-FT excluded; 3 trained rungs only). Mean per-cell achieved metrics on test (LODO held-out attack source):

| Rung | Policy | Mean threshold | Mean test recall | Mean test FPR |
|---|---|---:|---:|---:|
| tfidf-lr | detection (FPR ≤ 1 %) | 0.657 | 0.333 | 0.067 |
| tfidf-lr | verification (recall ≥ 99 %) | 0.162 | 0.674 | 0.508 |
| frozen-probe | detection | 0.829 | 0.063 | 0.010 |
| frozen-probe | verification | 0.215 | 0.957 | 0.891 |
| LoRA | detection | 0.795 | 0.424 | 0.115 |
| LoRA | verification | 0.019 | 0.724 | 0.411 |

Two findings:

1. **All targets reachable on val** (target_reachable=True for all 72 op-points), but **the val→test transfer is large**: detection-policy FPR creeps above target on every rung; verification-policy recall drops well below target on tfidf-lr + LoRA. The frozen-probe verification policy holds (mean test recall 0.957, close to 0.99 target) — but at catastrophic FPR (0.891).
2. **The verification regime is fundamentally limited on LODO**: held-out attack sources produce test distributions different enough from val that any "guarantee recall ≥ 99 %" threshold has either tiny test recall (LoRA: 0.724) or near-100 % test FPR (frozen-probe: 0.891).

For the full narrative + reachability-audit detail see [`WRITEUP/threshold-policy.md`](./WRITEUP/threshold-policy.md).

### Calibration findings

Per-rung mean across both-class slices:

| Rung | Mean ECE (equal-mass) | Mean Brier |
|---|---:|---:|
| frozen-probe | 0.144 | 0.265 |
| tfidf-lr | 0.350 | 0.376 |
| LoRA | 0.444 | 0.451 |
| ProtectAI v1 | 0.452 | 0.470 |
| ProtectAI v2 | 0.460 | 0.471 |

**Finding**: frozen-probe has the BEST calibration on both-class OOD slices (ECE 0.144; Brier 0.265). LoRA fine-tuning DEGRADES calibration substantially (ECE 0.444 — 3× worse than frozen-probe). This is consistent with the per-row finding that LoRA over-confidently mis-classifies OOD examples; both the discrimination AND the calibration of the head distribution shift away from honest probabilistic estimates after fine-tuning. ProtectAI v1/v2 both show high ECE (~0.45+) which is consistent with their out-of-distribution scoring against our slate.

### Frozen probe vs adapter fine-tuned (paired bootstrap)

Per ADR-022 paired-bootstrap (percentile-method, 10K resamples × 2 seeds; 0/40 stability flags at 5 pct threshold):

| Comparison | Slice | Metric | delta (b − a) | 95 % CI | Conclusion |
|---|---|---|---:|---:|---|
| frozen-probe vs LoRA | jbb_behaviors | AUPRC | −0.016 | [−0.024, −0.009] | LoRA worse; CI clears zero |
| frozen-probe vs LoRA | jbb_behaviors | AUROC | −0.014 | [−0.021, −0.006] | LoRA worse; CI clears zero |
| frozen-probe vs LoRA | xstest | AUPRC | −0.001 | [−0.006, +0.004] | Indistinguishable; CI crosses zero |
| frozen-probe vs LoRA | xstest | AUROC | −0.007 | [−0.013, −0.002] | LoRA marginally worse; CI clears zero |

**Headline**: LoRA fine-tuning is *not* a free lunch on this task. On 3 of 4 slice × metric comparisons against frozen-probe, LoRA is significantly worse at the 95 % level. The adapter weights specialise to the training distribution, costing the model the OOD generalization that the pretrained backbone alone provided.

### The headline characterisation claims

Distilled summary:

- **Claim 1**: No rung in the trained-or-reference slate clears the `pooled_ood` positive-class prevalence baseline (0.374) under AUPRC. The best rung (frozen-probe AUPRC 0.364 [0.354, 0.375]) lands ~0.01 below the prevalence baseline; the CI upper bound just barely touches it. By AUROC (chance baseline 0.5), only frozen-probe at 0.515 [0.505, 0.525] clears chance with margin. The case-study lesson: "honest OOD generalization for prompt-injection classifiers is harder than the in-distribution numbers suggest" — not "look at this great classifier".
- **Claim 2**: LoRA fine-tuning *hurts* OOD generalization relative to the frozen probe. Paired bootstrap on jbb_behaviors AUPRC delta = −0.016 [−0.024, −0.009]; `pooled_ood` AUPRC delta = −0.071 (AUROC equivalent: −0.014 jbb_behaviors; −0.132 `pooled_ood` — same direction). The adapter weights specialise to the training distribution. Pretrained backbone embeddings carry the OOD generalization budget; fine-tuning consumes it.
- **Claim 3**: ProtectAI v1 → v2 is *not* a monotone improvement across the OOD slate: v2 beats v1 on jbb_behaviors (+0.037 AUPRC; +0.06 AUROC) and loses on xstest (-0.087 AUPRC; -0.15 AUROC). Off-the-shelf detector updates can regress on specific OOD distributions; downstream consumers should not assume v2 dominates v1 universally.
- **Claim 4**: Dual-policy thresholds fit on val do not transfer to LODO test. Detection-policy FPR creeps 1-12 % on test vs 1 % val target across all 3 trained rungs; verification-policy recall drops well below target on 2 of 3 rungs. The val→LODO gap is the dominant calibration story; per-rung temperature scaling would not fix it without OOD-aware threshold selection.

Each claim is supported by a specific row × CI above, not a hand-wave.

**Linked ADRs**: ADR-018 (reference slate; partially superseded by ADR-050), ADR-019 (transformer training recipe), ADR-021 (slice aggregation), ADR-022 (statistical inference apparatus), ADR-024 (cross-fold CI), ADR-025 (dual-policy operating points), ADR-046 (Phase 4 analysis bundle), ADR-050 (rung-slate narrowing — LLM judges + full-FT OOD drops).

**Known gaps**: per-fold calibration-battery + temperature/isotonic fitting outputs not exercised this Phase 5; per-row predictions for full-FT OOD ABSENT (FUSE EIO crash per ADR-050). Canonical-data wire-up of figures F1–F7 pending upstream eval-toolkit issues #14–#16 + #22.

### Takeaways (for the intro-only reader)

Three takeaways for the reviewer who reads only §1 + §1.5 + §2 + §Results.

1. **What was characterised.** A 5-rung ladder (TF-IDF+LR classical floor + ModernBERT-base frozen-probe + ModernBERT-base LoRA + ProtectAI v1 + ProtectAI v2) on 5 OOD slices spanning the five injection types in §1.5: `direct_injection`, `indirect_injection`, `agentic_flow_injection`, `jailbreak_as_question`, `false_positive_probe`. **Single-turn English text classification only**, with bootstrap CIs + paired-bootstrap rung-vs-rung + calibration battery + dual-policy thresholds per ADR-022 / ADR-023 / ADR-025.

2. **What the OOD wall reveals — read against the §1.5 train/test table.** The OOD slate is hardest on the injection types *not* in the training pool. BIPIA (the only `indirect_injection` slate) and InjecAgent (the only `agentic_flow_injection` slate) both have zero counterparts in the 4 LODO training sources. The trained transformer rungs land at or below the `pooled_ood` positive-class prevalence baseline of 0.374 under AUPRC (frozen-probe 0.364; LoRA 0.293; classical floor 0.291). **LoRA's `pooled_ood` AUPRC is essentially tied with the classical floor and -0.071 below frozen-probe** — fine-tuning the head onto direct-injection training data DECREASES OOD generalization vs leaving the pretrained backbone embeddings intact. **The pretrained backbone — not the LODO training pool — carries what little OOD generalization budget exists**, and even that doesn't lift above the prevalence baseline in absolute terms. On the injection types that *are* in training (`direct_injection` via jbb_behaviors partial; `jailbreak_as_question` via XSTest), the trained rungs do modestly better but still cluster in a tight band around 0.47–0.55 AUPRC. By AUROC (chance baseline 0.5), only frozen-probe at 0.515 [0.505, 0.525] clears chance with margin; LoRA at 0.383 falls below. *In short: the rung ladder is doing approximately as well as could be expected given what it was shown, and the OOD gap quantifies what training data alone cannot fix.*

3. **What's deferred, what to take away.** Multi-turn agentic flows, encoded payloads, paraphrase attacks, and adversarial perturbations are NOT tested (per §Scope above). A deployment context that includes those attack classes cannot rely on these numbers; [`WRITEUP/limitations-and-future-work.md`](./WRITEUP/limitations-and-future-work.md) §9.4 names what would need to land to extend coverage (OOD-aware training data, backbone scaling, OOD-aware threshold selection). **The honest reading**: this is a methodology + capability *characterisation*, not a leaderboard claim. The headline finding — *fine-tuning consumes the OOD generalization budget the pretrained backbone provides* — is methodologically richer than a "great classifier" framing would have allowed.

---

## Lessons (brief)

Long form in [`WRITEUP/limitations-and-future-work.md`](./WRITEUP/limitations-and-future-work.md) §11. Punch lines:

- The OOD generalization wall is the dominant signal; honest framing surfaces it where a "great classifier" framing would have hidden it.
- The SDD process bought reproducibility + audit trail at the cost of a ~50-decision Phase 0 interview flow. ADR-050 (rung-slate narrowing) is the supersession-on-supersession proof point — when reality forced a methodology drift, the discipline ate it cleanly.
- The library-first invariant retrofit (ADR-047) was a discipline lapse caught at Phase 4 entry and recovered in one carryforward refactor. The cost-overrun on LLM judges (ADR-050 driver 1) was a similar lapse — original estimate didn't account for actual token volume.
- FUSE-on-RunPod is a non-deterministic bug class; ~50 % of cumulative spend ($15.74) was FUSE-recovery overhead. Filed upstream issues + PRs at brandon-behring/runpod-deploy.
- Per-step commits + 2-checkpoint push cadence survived multi-day context auto-compaction.

---

## 12. Appendix

### A. Glossary

- **Detection policy** — threshold selection targeting FPR ≤ 1 % on validation; characterises high-recall-low-FP behaviour.
- **Verification policy** — threshold selection targeting FNR ≤ 1 % on validation; characterises high-precision-on-clean behaviour.
- **LODO** — leave-one-dataset-out cross-validation; source-disjoint k-fold where each fold holds out an entire dataset source.
- **LoRA** — Low-Rank Adaptation; parameter-efficient fine-tuning method.
- **PR-AUC** — area under the precision-recall curve; threshold-free ranking metric for class-imbalanced tasks.
- **ECE** — expected calibration error; mean absolute gap between predicted-probability bins and observed frequencies.
- **MDE** — minimum detectable effect; the smallest difference your sample size can reliably detect at a given power.
- **IID** — independent and identically distributed; evaluation on data drawn from the same source/distribution as training.
- **OOD** — out-of-distribution; evaluation on data deliberately drawn from a different source or distribution.
- **Rung ladder** — a sequence of classifiers of increasing complexity, designed so each step's lift decomposes which capability is responsible.

### B. ADR index

[`decisions/README.md`](./decisions/README.md) — single version-neutral sequence; ADRs supersede prior ones via the standard `superseded-by-ADR-N` mechanism.

### C. Assumption ledger

[`assumptions.md`](./assumptions.md) — every assumption with severity ≥ medium appears in [`WRITEUP/limitations-and-future-work.md`](./WRITEUP/limitations-and-future-work.md) §8.2.

### D. Audit trail

[`EVIDENCE.md`](./EVIDENCE.md) — what external evidence was verified, what couldn't be, what was left unresolved.

### E. Linked Claude transcripts

Transcripts referenced by ADR `transcript:` frontmatter fields are bundled and emailed to the reviewer at submission time per `transcripts/README.md`; the `/save-transcript` skill produces them.

### F. eval-toolkit methodology curriculum

[`docs/methodology/`](https://github.com/brandon-behring/eval-toolkit/tree/main/docs/methodology) — 17-chapter curriculum. Cross-linked from each WRITEUP/ spoke.
