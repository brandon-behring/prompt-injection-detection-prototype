# Prompt-injection classification —  methodology + capability characterization

**Author**: Brandon Behring · **Date**: `[TBD: populated at Phase 5]` · **Status**: `[TBD: populated at Phase 5]`

---

## 1. Motivation

Prompt-injection — text designed to override or subvert the instructions an LLM-based system is operating under — is one of the load-bearing failure modes for any system that exposes an LLM to untrusted input. Ciphero's verification-layer thesis is that we cannot govern what we cannot verify; one primitive in that stack is a classifier that scores whether a span of text is an injection attempt.

The same scores serve two operational contexts:

- **Detection** — *catch injections coming in*. Tolerates false positives more than false negatives (an alert costs less than a missed attack at the input boundary).
- **Verification** — *confirm clean text actually is clean*. Tolerates false negatives more than false positives (a confidently-clean assertion is the dangerous one).

These are not two classifiers; they are two threshold policies on the same scores, with different cost weights. See §5.3 for how the same primitive is configured to characterise both.

This writeup characterises a rung ladder of prompt-injection classifiers — `[OPEN: rung ladder; resolved at Phase 0]` — across an OOD slate, with the question: *what does each capability layer add, and where does the IID/OOD gap fall?* The work is **methodology + capability characterization braided**: the ladder is the instrument; the eval methodology rigor is what makes the characterization defensible; the brief's two asks (models of increasing complexity + OOD coverage) are the targets.

**Honest-OOD thesis**: IID numbers are the easy part. The interesting question for any classifier that might one day touch a deployment surface is *which capabilities help when the distribution shifts, and which ones only inflate the IID number*. That question — not "what's the best PR-AUC" — drives this document's structure.

**Deployment is not on the roadmap.** This is characterisation, not recommendation. No rung is promoted as the deployment choice; each rung's trade-offs are reported and the reader is left to draw their own deployment conclusions if they have one to make.

**Linked ADRs**: `[ADR-001, ADR-017]`.

**Known gaps**: `[TBD: any motivation-level caveats]`.

---

## 2. Approach overview

The brief asked for two things: *models of increasing complexity* and *the right amount of OOD coverage*. The rung ladder satisfies the first ask and is the **instrument** for the second: when a rung helps IID but not OOD, that tells us its added capability is data-pattern-fitting rather than generalisation; when a rung helps both, the added capability is more durable.

| Element | Role | Why |
|---|---|---|
| Rung ladder `[OPEN: rung composition; resolved at Phase 0]` | Instrument | Each step's lift over the previous decomposes *which capability* matters. |
| OOD slate `[OPEN: OOD slate composition; resolved at Phase 0]` | Measurement | Quantifies what each capability adds when the distribution shifts. |
| Dual cost-weight thresholds | Score-behaviour characterisation | Shows what the same scores deliver under two different operational cost regimes. |
| Statistical rigor (CIs + paired comparisons + MDE) | Defensibility | Lets us claim differences honestly and quantify when we lack the power to claim anything. |

We do **not** pick a deployment leader. The intent is to demonstrate what each rung delivers and where it breaks; readers with a specific deployment context can map our characterisation onto their cost constraints.

**Linked ADRs**: `[ADR-002, ADR-014, ADR-017, ADR-021]`.

**Known gaps**: `[TBD: populated at Phase 5]`.

---

## 3. Data design

### 3.1 Why these sources

`[TBD: paragraph naming each source and why it earned a place in the pool — populated at Phase 5 from Phase 0 source-slate lock]`

Sources: `[OPEN]` — Phase 0 picks from candidates documented in `docs/research/datasets/`. Full table in [`SPEC_SHEET.md` §3.1](./SPEC_SHEET.md).

### 3.2 Dedup — *why this matters more than people think*

Label-blind dedup looks innocuous and is wrong. It removes minimal pairs — cases where two near-identical texts have *different* labels — which are exactly the informative examples a classifier needs to learn the decision boundary. We use **calibrated semantic dedup** (encoder + threshold locked at Phase 0); label-aware (within-source, drop; cross-label, preserve); cross-source minimal pairs preserved.

`[FIGURE 3: dedup-threshold calibration histogram for the selected encoder]` → `docs/plots/figure3-dedup-calibration.png`

Calibration evidence: `evals/dedup_calibration.json` `[TBD: populated at Phase 5]`.

See [methodology/text_dedup.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/text_dedup.md) for the general framework.

### 3.3 Leakage handling + reference-scorer audit

Three checks for in-pool leakage, plus a separate reference-scorer audit:

1. **Exact-hash overlap** — no test row's hash appears in train.
2. **High-cosine overlap** — no test row has cosine ≥ `[OPEN: threshold]` to any train row of the same label.
3. **Cross-source benign dedup** — `[OPEN]` ordering (before-split / after-split). The rule prevents fold-leakage failures when within-source dedup leaves benign duplicates that survive the split.
4. **Reference-scorer training-overlap audit** — `[LOCKED]` any external reference scorer gets its publicly-named training datasets crossed with project sources. Where disclosure is only at category level, the audit shifts to fold-pattern + scope-mismatch analysis — see EVIDENCE.md §1–2.

Reported as `[TBD: per-slice overlap percentages]`. See [methodology/leakage.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/leakage.md).

### 3.4 Splits

`[OPEN]` Splits structure (single / k-fold / source-disjoint LODO / hybrid). When ≥3 positive sources are available, source-disjoint LODO is the field-standard choice (Fomin 2025, "When Benchmarks Lie"). See [methodology/splits.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/splits.md).

**Linked ADRs**: filled in once Phase 0 locks each row.

**Known gaps**: `[TBD: surfaced during Phase 0 + Phase 1 work; populated at Phase 5]`.

---

## 4. Model recipe — the rung ladder

Each rung answers *what does this capability layer add over the rung below?* Hyperparameters are locked before training begins; no val-set gridsearch. Training compute target is `[OPEN]` (Phase 0 locks per SPEC_GREENFIELD §Tech-Stack). Per-rung detail below; the locked recipe lives in [`SPEC_SHEET.md` §4](./SPEC_SHEET.md).

### 4.1 Rung 1 — *the linear floor*

`[OPEN]` Linear baseline (e.g. n-gram features + logistic regression). Deterministic; one fit per fold. *Why this rung exists*: a linear model is the minimum-viable classifier for the task; everything above it has to earn its complexity.

`[TBD: one-paragraph result interpretation against §7 numbers]`

### 4.2 Rung 2 — *what the backbone already encodes*

`[OPEN]` Frozen-transformer representations + linear head. *Why this rung exists*: it separates *pretraining alone* from *fine-tuning*. If the frozen probe matches or beats Rung 1 but the fine-tuned rung doesn't lift further, fine-tuning isn't adding capability — it's overfitting.

`[TBD: one-paragraph result interpretation]`

### 4.3 Rung 3 — *the fine-tuning ceiling at the project's compute budget*

`[OPEN]` Adapter-fine-tuned transformer. Backbone, adapter rank, training-time scope, epoch count, precision, batch size, seed protocol — all locked at Phase 0 per SPEC_GREENFIELD §2 Model ledger rows. *Why this rung exists*: it's the maximally-adapted model in the compute budget. If anything above the frozen probe is worth doing, this rung is where it shows.

`[TBD: result interpretation]`

### 4.4 Rung 4 — *narrow-scope reference scorer (optional)*

`[OPEN]` Off-the-shelf classifier with narrow scope (e.g. direct-injection only). Inference-only. *Why this rung exists*: a publicly-trained narrow-scope detector is the "is this better than something already on the shelf for this attack class" bar.

*Caveat*: reference scorers carry training-overlap audit obligations per EVIDENCE.md §1. Reported as diagnostic reference, not as a clean baseline.

`[TBD: result interpretation]`

### 4.5 Rung 5 — *broad-scope reference scorer (optional)*

`[OPEN]` Off-the-shelf classifier with broader stated scope. Inference-only. *Why this rung exists*: a broader-scope reference completes the reference picture. Caveat: when training-data disclosure is at category level only, contamination cannot be verified; the audit shifts to fold-pattern + scope-mismatch analysis per EVIDENCE.md §2.

`[TBD: result interpretation]`

**Linked ADRs**: filled in once Phase 0 locks each rung.

**Known gaps**: `[TBD: surfaced during Phase 0 + Phase 1 work; populated at Phase 5]`.

---

## 5. Evaluation framework — and *why* each test exists

This section is the heart of the writeup. Every test below is reported with effect sizes and CIs — never p-values. The choice is methodological: in finite-sample settings, *what's the effect and how confident are we in it* is the answerable question; *is this nonzero at α=0.05* is a question whose answer depends on the sample size more than the phenomenon.

### 5.1 Headline descriptive metrics

`[TBD: results per §7]` reported with bootstrap CIs:

- **PR-AUC** — the most relevant ranking metric for class-imbalanced tasks where precision and recall both matter. F1 alone is misleading at any chosen threshold; PR-AUC integrates over thresholds.
- **ROC-AUC** — reported alongside for class-prior-independent ranking. Less useful than PR-AUC under our priors but standard for cross-paper comparison.
- **recall@FPR ∈ {0.1%, 1%, 5%}** `[TBD: 0.1% pinpoint, if recall@0.1%FPR is selected at Phase 0]` — operational pinpoints. The 1% point is the canonical reporting threshold (PromptShield 2025).
- **ECE (equal-mass + Kumar-2019 debiased) + Brier** — calibration; see §5.2 calibration battery.

See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md) for why each metric is preferred over plain F1.

### 5.2 Statistical tests

**Stance**: report effect sizes and CIs. Do not rely on p-values. This is the modern preference in applied ML evaluation and is aligned with [eval-toolkit](https://github.com/brandon-behring/eval-toolkit)'s primitive design.

#### Per-metric bootstrap CIs — `bootstrap_ci`

*Why*: a point estimate of PR-AUC hides finite-sample variance. Without a CI, claiming rung A beats rung B is irresponsible — the gap may be smaller than the sampling noise. Per-row resampling preserves label distribution and avoids parametric assumptions.

Method: percentile bootstrap; 10000 resamples; pinned seed (`bootstrap_seed=42`). Stability check at `bootstrap_seed=43` — per-fold CI shifts > 0.01 flag instability. See [methodology/bootstrap.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/bootstrap.md).

#### Paired-bootstrap differences for rung-vs-rung — `paired_bootstrap_diff`

*Why*: when two rungs are evaluated on the same test set, their per-row errors are correlated. Paired bootstrap accounts for that correlation without requiring parametric assumptions like DeLong's. One primitive covers AUC differences, recall@FPR differences, and threshold-based differences uniformly — no need to mix DeLong + McNemar + permutation tests.

Method: per-row pairing; matched resamples; CI on the paired Δ. Reported wherever we make a comparative claim. See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md).

#### MDE — `mde_from_ci`

*Why*: a wide CI that excludes "no difference" is still informative; a wide CI that *includes* "no difference" can mean either "the rungs are equivalent" or "we don't have power to tell." MDE distinguishes these. A claim of equivalence requires MDE small enough to rule out the smallest difference we'd care about.

Method: derive MDE from CI width at α=0.05, power=0.80. Report alongside every CI that includes zero.

#### Calibration battery — `reliability_curve` + `fit_temperature` + `fit_isotonic` + ECE variants + Brier

*Why*: even without a deployment goal, calibration tells you whether the scores mean what they claim. A score of 0.9 should fire injections ~90% of the time. ECE quantifies the gap; Brier is a proper scoring rule that combines calibration and discrimination so an improvement can't game one at the other's expense; reliability curves diagnose *where* miscalibration concentrates (over-confident on the cleanest? under-confident on the most ambiguous?). Temperature and isotonic scaling are the standard post-hoc calibration repairs, fit on validation only.

`[FIGURE 4: reliability curves all rungs (IID + OOD)]` → `docs/plots/figure4-reliability-curves.png` `[TBD: (candidate) requires per-row predictions persisted;  adds]`

See [methodology/calibration.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/calibration.md).

#### CV-CLT CI for cross-fold variance — `cv_clt_ci`

*Why*: when we run source-disjoint k-fold as a supplement, per-fold metrics aren't independent — train sets overlap across folds. A naive standard-error treatment overstates confidence. CLT-based CI with Nadeau-Bengio-style variance correction handles the dependence properly. See [methodology/splits.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/splits.md).

### 5.3 Operating points — detection vs verification (score-behaviour characterisation)

#### 5.3.a Context

The same classifier serves two different operational contexts. **Detection** wants to *catch injections* — false negatives are the high-cost error; tolerate false positives up to an alerting-budget. **Verification** wants to *confirm clean* — false positives (calling clean text injection) are the high-cost error; tolerate some missed injections at the verification boundary.

These contexts ask different questions of the same scores. Reporting only one operating point hides what the classifier can do under the other cost regime.

#### 5.3.b Methodology

Both policies use eval-toolkit's `ThresholdSelector` protocol on **validation** (never test). The two policies differ only in cost weights:

- **Detection policy**: target FPR ≤ 1% on validation; among thresholds satisfying that constraint, maximise TPR.
- **Verification policy**: target FNR ≤ 1% on validation; among thresholds satisfying that constraint, maximise TNR.

Symmetric cost-weight configurations of the same primitive. Operationally-interpretable targets (FPR/FNR) — not score-space targets — so the same selection rule applies across heterogeneous rungs whose score scales aren't comparable. See [methodology/thresholds.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/thresholds.md).

**Scope note** `[OPEN]`: dual-policy threshold characterisation applies only to **in-house rungs**. Reference scorers (off-the-shelf reference detectors) carry training-overlap caveats that make operating-point characterisation misleading; for those, we report recall@FPR pinpoints only.

#### 5.3.c Dual-cost-weight characterisation (in-house rungs)

For a representative rung (`[TBD: (candidate) DeBERTa-LoRA, the fine-tuned ceiling]`), we report both policies side by side:

| Policy | Threshold | Recall | Precision | TPR | FPR | FNR | TNR |
|---|---:|---:|---:|---:|---:|---:|---:|
| Detection (FPR ≤ 1%) | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` |
| Verification (FNR ≤ 1%) | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` |

This is **characterisation, not deployment recommendation**. We are showing what the scores deliver under each cost weight, not advocating either policy for any deployment.

### 5.4 Per-source / per-style breakdown

*Why*: aggregate metrics hide heterogeneity. A 0.95 average PR-AUC can mask a 0.6 PR-AUC on one source that is in fact the source you care about. Per-source breakdowns are mandatory for any OOD claim because OOD is defined by *which source* the test rows came from.

`[FIGURE 5: per-source PR-AUC ± CI for the fine-tuned rung]` → `docs/plots/figure5-per-source-pr-auc.png`

The project also ships a per-attack-style heuristic tagger (regex-based; conservative). `[TBD: tagger coverage report — populated at Phase 5]`. See EVIDENCE.md §3.

### 5.5 OOD slate

`[OPEN]` OOD slate composition — populated at Phase 0 from `docs/research/benchmarks/` candidate set.

| Slice | Source | Class composition | Probe target | Why chosen |
|---|---|---|---|---|
| `[OPEN]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` | `[TBD: populated at Phase 5]` |

See [methodology/splits.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/splits.md) for the source-disjoint discipline we apply.

### 5.6 Adversarial robustness

`[TBD: largely deferred; named but not exhaustively probed]`

The adversarial threat model for a prompt-injection classifier includes:

- **Paraphrase attacks** — semantic equivalents that don't share surface n-grams with training injections.
- **Encoded payloads** — base64, leetspeak, hex, Unicode confusables, ROT13.
- **Multi-turn injection** — payload split across multiple conversation turns.
- **Indirect injection via context channels** — payload arriving via retrieved documents, tool outputs, or user-attached files.

What was tested: `[TBD: populated at Phase 5]`. What was deliberately not tested: `[TBD: populated at Phase 5]`. *Why deferred*: `[TBD — typically scope/data-availability]`. See §8 for the consolidated deferred list.

This sub-section exists so that an evaluator from a security-focused company can see the threat model is named even where the work was not done. It is not a claim of coverage.

**Linked ADRs**: `[ADR-008, ADR-021, ADR-022, ADR-023, ADR-024]`.

**Known gaps**: `[TBD: populated at Phase 5]`.

---

## 6. Tooling & infrastructure

The modelling work, the evaluation harness, and the cloud orchestration live in three separate repos. The split is intentional.

### 6.1 [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) — methodology-aware evaluation harness

A library-grade harness for binary classification with three tiers:

- **Tier 1: functional core** — `bootstrap_ci`, `paired_bootstrap_diff`, `mde_from_ci`, PR-AUC / ROC-AUC / Brier / ECE variants, `reliability_curve`, `fit_temperature`, `fit_isotonic`, `cv_clt_ci`. Pure numpy/scipy/sklearn.
- **Tier 2: Protocol-based orchestration** — `Scorer`, `SliceAwareScorer`, `LeakageCheck`, `Splitter`, `ThresholdSelector`, `DatasetLoader`, `SimilarityStrategy`. Opt-in versioning per protocol object.
- **Tier 3: reproducibility scaffolding** — versioned JSON schemas (`results.v1.json`, `results_full.v1.json`, `manifest.v1.json`); NeurIPS-aligned manifest capturing seeds, git SHA, data hashes, GPU info, leakage report.

Plus a [16-chapter methodology curriculum](https://github.com/brandon-behring/eval-toolkit/tree/main/docs/methodology) covering leakage, splits, thresholds, calibration, comparison, bootstrap, length stratification, text dedup, versioning, fairness, reproducibility, and testing.

*Why eval lives as a separate library*: it survives across iterations, it accumulates methodology curriculum as a durable knowledge artifact, and versioned JSON schemas let downstream parsers gate on format changes. Reuse is across projects, not just within this project.

### 6.2 [runpod-deploy](https://github.com/brandon-behring/runpod-deploy) — cloud orchestration

Cloud orchestration for training and evaluation runs on rented GPUs. *Why deployment is a separate concern*: cost-bearing infrastructure (rented H100 hours) needs different discipline from modelling code; separating it makes both auditable independently. See `[TBD: (candidate) docs/cloud-canonical-runbook.md]`.

**Prediction-persistence pattern** `[LOCKED]`: `runpod-deploy` pulls per-row score artifacts in addition to metrics JSON, so downstream threshold/calibration analyses run from persisted predictions without re-running inference.

### 6.3 SDD / ADR process

This repo practices custom-hybrid SDD: spec + ADRs + assumption registry + tests-as-invariants. Every significant decision is an ADR; every assumption is in the registry with a severity tag; every spec claim that can be made executable is a test.

The phase-by-phase process gates in [`SPEC_SHEET.md` §2](./SPEC_SHEET.md) — work-completed and tests-passing, not metric thresholds — instantiate the discipline.

**Linked ADRs**: filled in once Phase 0 locks each row.

**Known gaps**: `[TBD: populated at Phase 5]`.

---

## 7. Results

`[TBD: 1-paragraph framing — what the headline characterisation table tells us]`

`[FIGURE 6: ROC curves all rungs, IID vs OOD side by side]` → `docs/plots/figure6-roc-curves.png` `[TBD: (candidate) requires per-row predictions persisted]`
`[FIGURE 7: PR-AUC ± CI bar chart per rung × slice]` → `docs/plots/figure7-pr-auc-bars.png`

### 7.1 The IID-vs-OOD gap (primary narrative)

`[TBD: 2–3 paragraphs walking through the gap for each rung; what gap-size means; which rungs close vs widen the gap — populated at Phase 5 from per-rung × per-slice numbers]`

### 7.2 Reference scorer #1 — training-overlap finding

`[TBD: populated at Phase 5 from EVIDENCE.md §1 audit results. Frame: name the reference scorer's stated scope, name overlapping training data in the project pool (if any), report per-fold scores, conclude with the three-state taxonomy verdict (verified_disjoint / suspected_contamination / vendor_black_box).]`

### 7.3 Reference scorer #2 — training-overlap finding

`[TBD: populated at Phase 5 from EVIDENCE.md §2 audit results. Frame: same as §7.2. If disclosure is category-level only, report fold-pattern + scope-mismatch analysis as suggestive-but-not-dispositive evidence. Disambiguation via cross-source same-style ablation deferred to §8.]`

### 7.4 Which capabilities help OOD vs only help IID (secondary narrative)

`[TBD: rung-by-rung interpretation of OOD lift vs IID lift — populated at Phase 5]`

### 7.5 Score-behaviour at the two operating points

`[TBD: discussion of the §5.3 dual-cost-weight table — what the score behaviour at each cost regime says about the classifier — populated at Phase 5]`

### 7.6 Calibration findings

`[TBD: per-rung ECE/Brier interpretation; what the reliability curves reveal about where miscalibration concentrates — populated at Phase 5]`

### 7.7 Frozen probe vs adapter-fine-tuned

`[TBD: per-fold paired-bootstrap comparison between the frozen-probe rung and the adapter-fine-tuned rung — populated at Phase 5. The "fine-tune contribution" lift, with CI, is the headline number here.]`

### 7.8 The headline characterisation claims

Distilled summary `[TBD: populated at Phase 5]`:

- `[TBD: claim 1]`
- `[TBD: claim 2]`
- `[TBD: claim 3]`
- `[TBD: claim 4]`

Each claim is supported by a specific row × CI in §7.1–7.7, not a hand-wave.

**Linked ADRs**: filled in once Phase 0 locks each row.

**Known gaps**: `[TBD: populated at Phase 5]`.

---

## 8. Limitations & deliberately deferred

This chapter consolidates what we *consciously did not do*. These are not failures — they are scope decisions we can defend. The companion chapter §9 covers things we *tried and abandoned*; the distinction matters.

### 8.1 Scope deferrals

- **Deployment** — out of roadmap. The work is characterisation; no deployment recommendation; no deployment-readiness testing.
- **Adversarial red-teaming** — threat model named in §5.6, not exhaustively probed. *Why deferred*: `[TBD: populated at Phase 5]`.
- **Agentic-flow coverage** — multi-step / tool-use injection. *Why deferred*: `[TBD: populated at Phase 5]`.
- **Conformal prediction** — distribution-free uncertainty quantification beyond bootstrap. *Why deferred*: `[TBD: populated at Phase 5]`.
- **Cross-language coverage** — English-only `[OPEN]`. *Why deferred*: `[TBD: populated at Phase 5]`.
- **Cross-source same-style ablation** `[OPEN]` — would disambiguate "training contamination" from "attack-style difficulty" for reference scorers. May be underpowered if per-style sample size is small; in that case treated as an explicit limitation. See EVIDENCE.md §3.
- `[TBD: additional scope deferrals — populated at Phase 0]`

### 8.2 Methodology caveats

- `[TBD: e.g., single-seed primary; small-N OOD slices; reference-scorer leakage caveats — populated at Phase 5]`

Each deferred item has a *why* — usually scope or data availability — and is named in [`NEXT_STEPS.md`](./NEXT_STEPS.md) where applicable.

**Linked ADRs**: filled in once Phase 0 locks each row.

---

## 9. Negative results — architectures and approaches tried and abandoned

`[OPEN]` This chapter exists because honest framing requires showing the experimental work that did not pan out, not just the work that did. Negative results are interesting: they tell the next iteration *what not to spend time on*.

### 9.1 Hyperparameter / training dead-ends

`[TBD: hyperparameter sweeps that didn't matter or that revealed unexpected dynamics — populated at Phase 5 from any factorial / sensitivity work; if none, document as "no hyperparameter dead-ends explored at the chosen compute budget"]`

### 9.2 Architectures evaluated and dropped

`[TBD: items — e.g., alternative backbones tried, rungs that didn't earn their complexity]`

### 9.3 Data-pipeline experiments that didn't matter

`[TBD: items — e.g., dedup thresholds swept, augmentation strategies tried, source-mix variants]`

### 9.4 What the negatives imply for v6

`[TBD: one paragraph — what the negative space tells the next iteration]`

**Linked ADRs**: `[TBD: any ADRs documenting roll-back decisions]`.

---

## 10. Reproducibility

The work reproduces at three levels:

### 10.1 Local

```bash
make install         # uv sync --extra dev
make lint            # ruff + mypy strict
make test            # invariants + math correctness + smoke
make diagnostics-smoke  # [OPEN] no-external-services smoke pass (~10 min)
```

### 10.2 Cloud

Canonical numbers reproduce from `runpod-deploy`:

```bash
make preflight    # [TBD] CPU preflight — gates invariants before GPU spend
make h100         # [TBD] canonical H100 path
```

Runbook: `[TBD: (candidate) docs/cloud-canonical-runbook.md]`.

### 10.3 Evaluation

Eval invocation through `eval-toolkit` captures a NeurIPS-aligned manifest at `evals/manifest.json` covering seeds, git SHA, data hashes, GPU info, and a leakage report. `evals/results.json` is schema-validated against eval-toolkit's `results.v1.json`. **The project persists per-row predictions** at `evals/predictions.parquet` `[TBD: scoped at Phase 0]`.

### 10.4 Data + checkpoints

- Data sources: licenses + download instructions in [`SPEC_SHEET.md` §3](./SPEC_SHEET.md). HF revisions `[LOCKED]` SHA-pinned at  build time (forward-only).
- Checkpoints: `[TBD: HF Hub URL for checkpoints]`.
- Predictions: `[TBD: GitHub release tag with predictions tarball]`.

### 10.5 Transcripts

`[TBD: populated at Phase 5]` Selected Claude-Code transcripts illustrating key decision points are in `transcripts/` and referenced from the appendix. Examples: `[transcript: dedup-threshold-bake-off]`, `[transcript: ood-slice-selection]`, `[transcript: protectai-overlap-audit]`.

**Linked ADRs**: `[ADR-016, ADR-025, ADR-027]`.

---

## 11. Lessons & reflections

`[TBD: populated at Phase 5]` Short. What surprised. What the SDD process bought; what it cost.

- `[TBD: lesson 1]`
- `[TBD: lesson 2]`
- `[TBD: lesson 3]`

---

## 12. Appendix

### A. Glossary

- **Detection policy** — threshold selection targeting FPR ≤ 1% on validation; characterises high-recall-low-FP behaviour.
- **Verification policy** — threshold selection targeting FNR ≤ 1% on validation; characterises high-precision-on-clean behaviour.
- **LODO** — leave-one-dataset-out cross-validation; source-disjoint k-fold where each fold holds out an entire dataset source.
- **LoRA** — Low-Rank Adaptation; parameter-efficient fine-tuning method.
- **PR-AUC** — area under the precision-recall curve; threshold-free ranking metric for class-imbalanced tasks.
- **ECE** — expected calibration error; mean absolute gap between predicted-probability bins and observed frequencies.
- **MDE** — minimum detectable effect; the smallest difference your sample size can reliably detect at a given power.
- **IID** — independent and identically distributed; evaluation on data drawn from the same source/distribution as training.
- **OOD** — out-of-distribution; evaluation on data deliberately drawn from a different source or distribution.
- **Rung ladder** — a sequence of classifiers of increasing complexity, designed so each step's lift decomposes which capability is responsible.

### B. ADR index

[`decisions/README.md`](./decisions/README.md) — single version-neutral sequence;  ADRs supersede prior ones via the standard `superseded-by-ADR-N` mechanism.

### C. Assumption ledger

[`assumptions.md`](./assumptions.md) — every assumption with severity ≥ medium appears in §8.2 above.

### D. Audit trail

[`EVIDENCE.md`](./EVIDENCE.md) — what external evidence was verified, what couldn't be, what was left unresolved.

### E. Linked Claude transcripts

`[TBD: populated at Phase 5]` Resolved from `[transcript: <slug>]` placeholders to `transcripts/<slug>.md` once the transcript-export skill exists.

### F. eval-toolkit methodology curriculum

[`docs/methodology/`](https://github.com/brandon-behring/eval-toolkit/tree/main/docs/methodology) — 16-chapter curriculum. Cross-linked from §3, §5.1–5.5, and §6.1 above.
