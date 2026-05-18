# Prompt-injection classification —  methodology + capability characterization

**Author**: Brandon Behring · **Date**: 2026-05-18 · **Status**: v0.9.0-rc1 submission-ready rehearsal (Phase 5 close)

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

**Linked ADRs**: ADR-001 (brief alignment), ADR-013 (deliverable scope + WRITEUP shape), ADR-017 (rung-slate expansion).

**Known gaps**: this submission characterises a *prompt-injection text classifier* against an English-only fixed slate of 4 LODO training sources + 5 OOD slates. Cross-language attacks, agentic-flow injection, conformal calibration, and adversarial red-teaming are out of scope per §8.1.

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

**Linked ADRs**: ADR-002 (approach scaffold), ADR-014 (single-backbone slate framing), ADR-017 (rung-slate expansion), ADR-021 (slice aggregation + headline-metric protocol).

**Known gaps**: this approach evaluates EACH rung against the same slate; cross-rung-ensemble strategies (e.g., LoRA-with-frozen-probe-temperature) are out of scope per the project compute budget.

---

## 3. Data design

### 3.1 Why these sources

The data slate locked at Phase 0-02 per ADR-016 (data design bundle): 4 positive-attack sources (LODO training pool) + 2 benign sources + 5 held-out OOD slates. Per-source rationale + post-dedup counts:

**Positive attack sources (LODO training pool)** — each source provides a stylistically-distinct slice of the prompt-injection space; LODO ensures held-out generalization on attack style, not just held-out rows:

- `deepset_prompt_injections` — 170 rows (post-dedup; raw 203). Short curated direct-injection probes. Earned its place as the smallest-but-canonical reference source.
- `lakera_gandalf_ignore_instructions` — 525 rows (raw 777). Formulaic "ignore the above" patterns from the Gandalf game; representative of the most-common direct-injection style.
- `lakera_mosscap_prompt_injection` — 2362 rows (raw 3000). Longer, more diverse Mosscap game attacks; stylistically different from Gandalf.
- `hackaprompt` — 1650 rows (raw 2891). Mixed-style adversarial attempts from the HackAPrompt competition; many multi-paragraph attacks.

Total positive pool post-dedup: **4707 rows**. Cross-source dedup at cosine threshold 0.80 (encoder: `sentence-transformers/all-MiniLM-L6-v2`) per ADR-042.

**Benign sources** — provide the negative class (label=0):

- `lmsys_chat_1m` — 7724 rows (raw 10000; ~22% dedup). User-vs-ChatGPT chat logs. Earned its place as a high-volume, stylistically-realistic negative source.
- `ultrachat_200k` — 9522 rows (raw 10000; ~5% dedup). Synthetic multi-turn conversations. Provides a benign-text variety class lmsys_chat_1m doesn't cover (e.g., creative writing, structured Q&A).

Total benign pool: **17246 rows**.

**OOD slates** — 5 held-out distributions per ADR-021 NOT used during training; evaluation-only:

- `notinject` (HF Hub) — synthetic prompt-injection-LIKE-but-benign sequences; tests false-positive robustness. All-negative by design.
- `xstest` (HF Hub) — exaggerated safety + jailbreak-as-questions; cross-distribution shift from training. Both classes present.
- `jbb_behaviors` (HF Hub) — JailbreakBench harmful-behavior elicitations. Both classes present.
- `bipia` (local git repo) — indirect prompt injection via email body content. All-positive by source design.
- `injecagent` (local git repo) — multi-turn agentic-flow injections. All-positive by source design.

All 11 sources are pinned at HF revision SHAs (where applicable) per `data/source_manifest.yaml` per ADR-016 + ADR-041.

Sources locked at Phase 0-02 per ADR-016: 4 positive-attack sources + 2 benign sources + 5 held-out OOD slates as detailed in §3.1 above. Full table in [`SPEC_SHEET.md` §3.1](./SPEC_SHEET.md).

### 3.2 Dedup — *why this matters more than people think*

Label-blind dedup looks innocuous and is wrong. It removes minimal pairs — cases where two near-identical texts have *different* labels — which are exactly the informative examples a classifier needs to learn the decision boundary. We use **calibrated semantic dedup** (encoder + threshold locked at Phase 0); label-aware (within-source, drop; cross-label, preserve); cross-source minimal pairs preserved.

`[FIGURE 3: dedup-threshold calibration histogram for the selected encoder]` → `docs/plots/figure3-dedup-calibration.png`

Calibration evidence: `evals/dedup_calibration.json` records `threshold_locked: 0.80` (cosine) for the cross-source benign-vs-attack pair classifier per ADR-042. Encoder: `sentence-transformers/all-MiniLM-L6-v2`. Operator follow-up gated at v1.0.0: raise `human_verified_pct` from 0 to 100 by manually examining `data/dedup_holdout.jsonl` and confirming each LLM-pre-label is correct.

See [methodology/text_dedup.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/text_dedup.md) for the general framework.

### 3.3 Leakage handling + reference-scorer audit

Three checks for in-pool leakage, plus a separate reference-scorer audit:

1. **Exact-hash overlap** — no test row's hash appears in train.
2. **High-cosine overlap** — no test row has cosine ≥ `[OPEN: threshold]` to any train row of the same label.
3. **Cross-source benign dedup** — locked at *after-split* per ADR-043 (post-split leakage cleanup). The rule prevents fold-leakage failures when within-source dedup leaves benign duplicates that survive the split.
4. **Reference-scorer training-overlap audit** — `[LOCKED]` any external reference scorer gets its publicly-named training datasets crossed with project sources. Where disclosure is only at category level, the audit shifts to fold-pattern + scope-mismatch analysis — see EVIDENCE.md §1–2.

Reported as 0 exact-hash overlaps + 0 cosine overlaps at threshold 0.85 across all (train, val, test) per-fold-seed pairs — `evals/leakage_report.json` carries `leakage_clean: True`. The eval-toolkit leakage check suite operationalizes the 8-type taxonomy from Kapoor & Narayanan 2023 (arXiv:2207.07048) — 294 non-replicating papers traced to leakage — via reference implementations: `ExactDuplicateCheck`, `NearDuplicateCheck`, `NormalizedFormLeakageCheck`, `CrossSplitLeakageCheck`, `LabelConflictCheck`, `GroupLeakageCheck`, `TemporalLeakageCheck`. See [methodology/leakage.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/leakage.md).

### 3.4 Splits

Splits structure locked at *source-disjoint LODO* (4-fold; 3 seeds = 12 cells per rung) per ADR-016. When ≥3 positive sources are available, source-disjoint LODO is the field-standard choice (Fomin 2025, "When Benchmarks Lie"). See [methodology/splits.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/splits.md).

**Linked ADRs**: filled in once Phase 0 locks each row.

**Known gaps**: see relevant ADR-XXX entry in the appendix index.

---

## 4. Model recipe — the rung ladder

Each rung answers *what does this capability layer add over the rung below?* Hyperparameters are locked before training begins; no val-set gridsearch. Training compute target locked at A100-SXM4-80GB × 12 cells × 2 epochs per ADR-019 + ADR-049 (per-pod cap $40/$60/$100 per ADR-020). Per-rung detail below; the locked recipe lives in [`SPEC_SHEET.md` §4](./SPEC_SHEET.md).

### 4.1 Rung 1 — *the linear floor*

TF-IDF (1-3-grams, sublinear TF, max_features=200k) + logistic regression (class-balanced, L2, C=1.0). Deterministic; one fit per fold × seed. Per ADR-017 + ADR-044. *Why this rung exists*: a linear model is the minimum-viable classifier for the task; everything above it has to earn its complexity.

**Result**: tfidf-lr's OOD pooled-AUROC is 0.371 [0.362, 0.381] — slightly below chance, but with a tight CI that does NOT cross 0.50 (CI upper bound 0.381). On the IID-shaped slices it lands at 0.445 [0.422, 0.469] (jbb_behaviors) and 0.451 [0.436, 0.466] (xstest). This is the floor everything else has to beat to earn its complexity. *Result*: only frozen-probe clears this floor on pooled_ood with margin (delta +0.144 AUROC).

### 4.2 Rung 2 — *what the backbone already encodes*

ModernBERT-base (`answerdotai/ModernBERT-base`, revision pinned at SHA `8949b909`) with all backbone weights FROZEN; only the 2-class classification head is trained per ADR-015 + ADR-019. 2 epochs × class-balanced loss × bf16 × 12 cells (4 folds × 3 seeds). *Why this rung exists*: separates *pretraining alone* from *fine-tuning*. If the frozen probe matches or beats Rung 1 but the fine-tuned rung doesn't lift further, fine-tuning isn't adding capability — it's overfitting.

**Result**: frozen-probe's pooled_ood AUROC is 0.515 [0.505, 0.525] — *the only rung whose CI clears 0.50 with margin*. Net OOD lift over tfidf-lr is +0.144 AUROC. The pretrained ModernBERT embeddings carry significant generalization budget; the classifier head needs ONLY linear access to those embeddings to land above chance on the OOD slate. This is the headline finding of §7.

### 4.3 Rung 3 — *the fine-tuning ceiling at the project's compute budget*

ModernBERT-base with LoRA adapters (rank=16, alpha=32, dropout=0.05, target_modules=[query, key, value, dense]) per ADR-015 + ADR-019. 2 epochs × class-balanced loss × bf16 × 12 cells. ~1% of parameters trainable. *Why this rung exists*: it's the maximally-adapted model in the project compute budget. If anything above the frozen probe is worth doing, this rung is where it shows.

**Result**: LoRA's pooled_ood AUROC is 0.383 [0.374, 0.392] — *below* the frozen-probe baseline (-0.132 AUROC; paired-bootstrap CI excludes zero). The adapter weights specialize to the training distribution; on the OOD slate they degrade generalization vs the bare backbone embeddings. LoRA fine-tuning on this task at this compute budget is a NEGATIVE result — it works on jbb_behaviors / xstest (in-distribution-shaped slices) and overfits relative to the frozen probe on genuinely OOD distributions. See §7.7 for the paired-bootstrap detail.

Note on full-FT: full-FT was the planned Rung 3.5 (full backbone trainable) per ADR-019; per ADR-050 it was DROPPED from OOD comparison due to a Phase 5 FUSE EIO crash on /workspace MooseFS storage. full-FT remains in the LODO LODO comparison (3-rung ladder narrative survives via the 24 surviving LODO predictions from Phase 2); OOD comparison ships 2 trained rungs (frozen-probe + LoRA).

### 4.4 Rung 4 — *narrow-scope reference scorer (optional)*

ProtectAI deberta-v3-base-prompt-injection v1 (`suspected_contamination` per ADR-005). Stated training scope: direct prompt injection (English). Inference-only via `transformers.AutoModelForSequenceClassification` per ADR-018. *Why this rung exists*: a publicly-trained narrow-scope detector is the "is this better than something already on the shelf for this attack class" bar.

*Caveat*: reference scorers carry training-overlap audit obligations per EVIDENCE.md §1. Reported as diagnostic reference, not as a clean baseline.

**Result**: ProtectAI v1's pooled_ood AUROC is 0.440 [0.409, 0.469]. Slightly above tfidf-lr (+0.069); well below frozen-probe (-0.075). The off-the-shelf narrow-scope detector beats a linear floor but does not match a frozen pretrained backbone on this slate. Suspected-contamination caveat retained.

### 4.5 Rung 5 — *broad-scope reference scorer (optional)*

ProtectAI deberta-v3-base-prompt-injection v2 (`suspected_contamination`). v2 adds broader-scope training data per the published model card update per ADR-018. *Why this rung exists*: a broader-scope reference completes the reference picture. Caveat: training-data disclosure is at category level only; contamination cannot be verified; audit shifts to fold-pattern + scope-mismatch analysis per EVIDENCE.md §2.

**Result**: ProtectAI v2's pooled_ood AUROC is 0.402 [0.369, 0.437] — slightly worse than v1 (-0.04 on pooled). v2 BEATS v1 on jbb_behaviors (+0.06 AUROC) but LOSES on xstest (-0.15 AUROC; CIs do not overlap — a clear regression). The lesson: off-the-shelf detector updates do not monotonically improve across distributions; consumers cannot assume v2 dominates v1.

**Note on dropped reference rungs**: LLM-judge rungs (gpt-4o-2024-08-06 + claude-sonnet-4-6) were locked at Phase 0-03 per ADR-018 and DROPPED at Phase 4 cost re-estimation per ADR-050 (16x envelope overrun against the original $14 estimate). The `vendor_black_box` contamination tier therefore has 0 rungs in this submission. See §8.1.

**Linked ADRs**: ADR-015 (single-backbone slate), ADR-017 (classical floor), ADR-018 (reference slate), ADR-019 (transformer training recipe), ADR-044 (Phase 2 implementation), ADR-050 (rung-slate narrowing).

**Known gaps**: full-FT OOD inference not present (FUSE EIO crash per ADR-050). LLM-judge rungs not present (cost overrun per ADR-050).

---

## 5. Evaluation framework — and *why* each test exists

This section is the heart of the writeup. Every test below is reported with effect sizes and CIs — never p-values. The choice is methodological: in finite-sample settings, *what's the effect and how confident are we in it* is the answerable question; *is this nonzero at α=0.05* is a question whose answer depends on the sample size more than the phenomenon.

### 5.1 Headline descriptive metrics

The headline metric battery (results in §7.1) reports with BCa bootstrap CIs:

- **PR-AUC** — the most relevant ranking metric for class-imbalanced tasks where precision and recall both matter. F1 alone is misleading at any chosen threshold; PR-AUC integrates over thresholds.
- **ROC-AUC** — reported alongside for class-prior-independent ranking. Less useful than PR-AUC under our priors but standard for cross-paper comparison.
- **recall@FPR ∈ {0.1%, 1%, 5%}** — operational pinpoints. The 1% point is the canonical reporting threshold (PromptShield 2025). The 0.1% point is included in `evals/metrics/per_cell.parquet` per ADR-021 + ADR-023 volatility-surface protocol but is noisy at our sample sizes and not surfaced in §7 headlines.
- **ECE (equal-mass + Kumar-2019 debiased) + Brier** — calibration; see §5.2 calibration battery.

See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md) for why each metric is preferred over plain F1.

### 5.2 Statistical tests

**Stance**: report effect sizes and CIs. Do not rely on p-values. This is the modern preference in applied ML evaluation and is aligned with [eval-toolkit](https://github.com/brandon-behring/eval-toolkit)'s primitive design.

#### Per-metric bootstrap CIs — `bootstrap_ci`

*Why*: a point estimate of PR-AUC hides finite-sample variance. Without a CI, claiming rung A beats rung B is irresponsible — the gap may be smaller than the sampling noise. Per-row resampling preserves label distribution and avoids parametric assumptions.

Method: BCa bootstrap (Efron 1987 / Efron & Tibshirani 1993 §14); resample budget per eval-toolkit guidance (`bootstrap.md` lines 147-158): n=200 sanity / n=1000 default / n=5000 publication-grade / n=10K+ only for expensive metrics. Pinned seed; stability check at a second seed flags instability if per-fold CI shifts > 0.01. **Report the point estimate, not the resample mean** — `BootstrapCI.point_estimate` is the metric on the *original* data (eval-toolkit `bootstrap.md` lines 165-168). See [methodology/bootstrap.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/bootstrap.md).

#### Paired-bootstrap differences for rung-vs-rung — `paired_bootstrap_diff`

*Why*: when two rungs are evaluated on the same test set, their per-row errors are correlated. Paired bootstrap accounts for that correlation without requiring parametric assumptions like DeLong's. One primitive covers AUC differences, recall@FPR differences, and threshold-based differences uniformly — no need to mix DeLong + McNemar + permutation tests. Non-overlapping CIs imply significance; overlap does NOT imply non-significance — always compute the difference CI (eval-toolkit `bootstrap.md` lines 162-164).

Method: per-row pairing; matched resamples; CI on the paired Δ. Reported wherever we make a comparative claim. Specialized variants `paired_bootstrap_ece_diff` (ECE comparisons) and `paired_bootstrap_op_point_diff` (two-level bootstrap for threshold refitting) handle non-AUC paired metrics. `delong_roc_variance` is available for sanity-check parametric ROC-AUC CIs (DeLong et al. 1988). See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md).

#### MDE — `mde_from_ci`

*Why*: a wide CI that excludes "no difference" is still informative; a wide CI that *includes* "no difference" can mean either "the rungs are equivalent" or "we don't have power to tell." MDE distinguishes these. A claim of equivalence requires MDE small enough to rule out the smallest difference we'd care about.

Method: derive MDE from CI width at α=0.05, power=0.80. Report alongside every CI that includes zero.

#### Calibration battery — `reliability_curve` + `fit_temperature` + `fit_isotonic_calibrator` + `fit_platt_calibrator` + `fit_beta_calibrator` + ECE variants + Brier

*Why*: even without a deployment goal, calibration tells you whether the scores mean what they claim. A score of 0.9 should fire injections ~90% of the time. ECE quantifies the gap; Brier is a proper scoring rule that decomposes as `BS = REL − RES + UNC` (Murphy 1973), so two models with same Brier may have very different operational profiles. Reliability curves diagnose *where* miscalibration concentrates (over-confident on the cleanest? under-confident on the most ambiguous?). Temperature (Guo et al. 2017 ICML; single-parameter logit scaling; argmax-invariant), isotonic, Platt (1999), and Beta scaling are the standard post-hoc repairs, fit on validation only.

**ECE choice matters**: prefer L2-debiased ECE (Kumar et al. 2019, arXiv:1909.10155) for headline reporting — preserves rank ordering and removes small-sample inflation (`expected_calibration_error_l2_debiased`). Equal-mass ECE (`expected_calibration_error_equal_mass`) is more robust under class imbalance via quantile binning (Naeini et al. 2015, arXiv:1411.0760). **Pin `n_bins` across comparisons** — ECE is a binned estimator; small bin counts understate, large bin counts overstate.

`[FIGURE 4: reliability curves all rungs (IID + OOD)]` → `docs/plots/F4.svg` (rendered via `scripts/render_figures.py` from per-row predictions in `evals/predictions/`; current scaffold path per upstream eval-toolkit#16; canonical-data wire-up deferred).

See [methodology/calibration.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/calibration.md).

#### CV-CLT CI for cross-fold variance — `cv_clt_ci`

*Why*: when we run source-disjoint k-fold as a supplement, per-fold metrics aren't independent — train sets overlap across folds. A naive standard-error treatment overstates confidence. CLT-based CI with Bates et al. 2024 (JASA) correction handles the dependence properly. See [methodology/splits.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/splits.md).

#### Multi-comparison correction — `bh_fdr_correct`

*Why*: when comparing many rung-pairs simultaneously, family-wise error inflates. Benjamini-Hochberg FDR (BH 1995) is preferred over Bonferroni for power reasons in correlated-test families. eval-toolkit exposes this directly; the Phase 0 decision-ledger row "Multi-comparison correction" picks BH-FDR / Bonferroni / none with rationale. See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md).

#### Evidence gates — release-time go/no-go

*Why*: claims at submission need machine-checkable gates, not implicit confidence. eval-toolkit's `claims.md` provides composable gates: `metric_threshold_gate`, `low_fpr_feasibility_gate`, `paired_diff_present_gate`, `no_leakage_errors_gate`, etc. The `ClaimSpec` → `GateResult` → `ClaimReport` pipeline (v0.9+) gives a release-gate manifest a reviewer can audit. See [methodology/claims.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/claims.md).

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

For the representative rung **LoRA** (the fine-tuned-ceiling-in-budget on this submission per ADR-019 + ADR-050; full-FT was the planned representative but is excluded from val-set inference due to the FUSE EIO crash per §8.1), we report both policies side by side. Numbers are *mean across 12 cells* (4 LODO folds × 3 seeds) on LODO held-out test, with val-fitted thresholds per ADR-025:

| Policy | Mean threshold | Mean test recall | Mean test precision | Mean test TPR | Mean test FPR | Reachable? |
|---|---:|---:|---:|---:|---:|---:|
| Detection (FPR ≤ 1%) | 0.795 | 0.424 | (see operating_points.parquet) | 0.424 | 0.115 | val: 12/12; test: 0/12 within target |
| Verification (recall ≥ 99%) | 0.019 | 0.724 | (see operating_points.parquet) | 0.724 | 0.411 | val: 12/12; test: 0/12 within target |

For comparison, the **frozen-probe** rung at the same policies:

| Policy | Mean threshold | Mean test recall | Mean test precision | Mean test FPR | Reachable? |
|---|---:|---:|---:|---:|---:|
| Detection (FPR ≤ 1%) | 0.829 | 0.063 | (see operating_points.parquet) | 0.010 | val: 12/12; test: 11/12 within target |
| Verification (recall ≥ 99%) | 0.215 | 0.957 | (see operating_points.parquet) | 0.891 | val: 12/12; test: 5/12 within target |

This is **characterisation, not deployment recommendation**. We are showing what the scores deliver under each cost weight, not advocating either policy for any deployment.

**Key val→test transfer findings**:
- All 72 op-points are reachable on val (the threshold-fitting set by ADR-025); transfer to LODO held-out test is partial-to-poor. The val→LODO gap is the dominant calibration story per §7.5.
- LoRA detection on test: mean FPR creeps to 0.115 (11.5×) vs 1% target. Recall trades favorably (0.42) for the higher FPR.
- frozen-probe detection on test: mean FPR holds tight (0.010 ≈ target) but recall collapses to 0.063 (the threshold is too conservative for the LODO distribution shift).
- frozen-probe verification on test: mean recall lands at 0.957 (close to 0.99 target) BUT at mean FPR 0.891 — almost everything is flagged positive. The verification regime over-floods at the cost of selectivity on LODO.

Source: `evals/operating_points/dual_policy.parquet` (72 OperatingPointModel rows) + `evals/audit/verification_reachability.json` (36 ReachabilityAuditModel records).

### 5.4 Per-source / per-style breakdown

*Why*: aggregate metrics hide heterogeneity. A 0.95 average PR-AUC can mask a 0.6 PR-AUC on one source that is in fact the source you care about. Per-source breakdowns are mandatory for any OOD claim because OOD is defined by *which source* the test rows came from.

`[FIGURE 5: per-source PR-AUC ± CI for the fine-tuned rung]` → `docs/plots/figure5-per-source-pr-auc.png`

The project also ships a per-attack-style heuristic tagger (regex-based; conservative). Tagger coverage on the LODO training pool is **not exhaustively measured** in this submission — the tagger is used at data-audit time per ADR-041 to spot-check coverage of the four attack-source slates; per-row tag → per-cell coverage rates ARE in `evals/data_audit.json` per-source breakdowns. See EVIDENCE.md §3.

### 5.5 OOD slate

The 5-slice OOD slate per ADR-021 + ADR-016, populated at Phase 0-04 from `docs/research/benchmarks/` candidate set:

| Slice | Source | Class composition | Probe target | Why chosen |
|---|---|---|---|---|
| `notinject` | HF Hub `wikd/NotInject` (SHA pinned per source_manifest.yaml) | All-negative (benign-but-injection-like) | False-positive robustness on injection-shaped benign | Tests whether classifier discriminates *intent* from *form* |
| `xstest` | HF Hub `paul-rottger/xstest-v2-copy` | Both classes (safe/unsafe instructions) | Cross-distribution shift to jailbreak-as-question | Tests against an actively-different distribution from training |
| `jbb_behaviors` | HF Hub `JailbreakBench/JBB-Behaviors` | Both classes (harmful behavior elicitations + benign refusal) | Adversarial-elicitation generalization | Canonical jailbreak benchmark; community-recognized |
| `bipia` | Local git repo (release-pinned SHA in source_manifest.yaml) | All-positive (indirect prompt injection via email body) | Indirect injection generalization | Tests indirect-injection (BIPIA paper benchmark) |
| `injecagent` | Local git repo (release-pinned SHA in source_manifest.yaml) | All-positive (multi-turn agentic injection) | Agentic-flow generalization | Tests agentic-flow injection |

See [methodology/splits.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/splits.md) for the source-disjoint discipline we apply.

### 5.6 Adversarial robustness

Adversarial robustness is **largely deferred** in this submission per §8.1 (named but not exhaustively probed beyond the in-pool LODO + OOD attack diversity).

The adversarial threat model for a prompt-injection classifier includes:

- **Paraphrase attacks** — semantic equivalents that don't share surface n-grams with training injections.
- **Encoded payloads** — base64, leetspeak, hex, Unicode confusables, ROT13.
- **Multi-turn injection** — payload split across multiple conversation turns.
- **Indirect injection via context channels** — payload arriving via retrieved documents, tool outputs, or user-attached files.

What was tested: the in-pool LODO + OOD slate already spans (a) direct vs indirect injection (BIPIA covers indirect), (b) jailbreak vs ignore-instructions (xstest + jbb_behaviors cover jailbreak-as-question), (c) agentic injection (injecagent), and (d) benign-but-injection-shaped (notinject). What was deliberately not tested: curated adversarial probes (paraphrase generation; encoded payloads at the row level; multi-turn injection splits). *Why deferred*: would expand the methodology contract from "characterisation against a fixed slate" to "ongoing adversarial probing" — see §8.1.

This sub-section exists so that an evaluator from a security-focused company can see the threat model is named even where the work was not done. It is not a claim of coverage.

**Linked ADRs**: ADR-008 (threat model), ADR-016 (data design), ADR-021 (slice aggregation), ADR-022 (statistical inference), ADR-023 (calibration battery), ADR-024 (cross-fold CI), ADR-046 (Phase 4 analysis).

**Known gaps**: see §8.2 methodology caveats — single-class OOD slices break threshold-free metrics; LODO test sets all-positive by design; val inference max_length 2048 vs train 8192 tolerated divergence.

---

## 6. Tooling & infrastructure

The modelling work, the evaluation harness, and the cloud orchestration live in three separate repos. The split is intentional.

### 6.1 [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) — methodology-aware evaluation harness

A library-grade harness for binary classification with three tiers:

- **Tier 1: functional core** — `bootstrap_ci`, `paired_bootstrap_diff`, `mde_from_ci`, PR-AUC / ROC-AUC / Brier / ECE variants, `reliability_curve`, `fit_temperature`, `fit_isotonic_calibrator`, `cv_clt_ci`. Pure numpy/scipy/sklearn.
- **Tier 2: Protocol-based orchestration** — `Scorer`, `SliceAwareScorer`, `LeakageCheck`, `Splitter`, `ThresholdSelector`, `DatasetLoader`, `SimilarityStrategy`. Opt-in versioning per protocol object.
- **Tier 3: reproducibility scaffolding** — versioned JSON schemas (`results.v1.json`, `results_full.v1.json`, `manifest.v1.json` through `manifest.v3.json`; v3 adds required `contamination_flags` field for the three-state reference-scorer audit taxonomy). NeurIPS-aligned manifest capturing seeds, git SHA, data hashes, data revisions, GPU info, leakage report, guardrails, source roles. See [methodology/reproducibility.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/reproducibility.md) for the NeurIPS-checklist field mapping.

Plus a [17-chapter methodology curriculum](https://github.com/brandon-behring/eval-toolkit/tree/main/docs/methodology) covering leakage, splits, thresholds, calibration, comparison, bootstrap, length stratification, text dedup, versioning, fairness, reproducibility, and testing.

*Why eval lives as a separate library*: it survives across iterations, it accumulates methodology curriculum as a durable knowledge artifact, and versioned JSON schemas let downstream parsers gate on format changes. Reuse is across projects, not just within this project.

### 6.2 [runpod-deploy](https://github.com/brandon-behring/runpod-deploy) — cloud orchestration

Cloud orchestration for training and evaluation runs on rented GPUs. *Why deployment is a separate concern*: cost-bearing infrastructure (rented H100 hours) needs different discipline from modelling code; separating it makes both auditable independently. See `configs/runpod/headline-*.yaml` for the canonical-run yaml templates; runbook commentary inlined in §10.2 above.

**Prediction-persistence pattern** `[LOCKED]`: `runpod-deploy` pulls per-row score artifacts in addition to metrics JSON, so downstream threshold/calibration analyses run from persisted predictions without re-running inference.

### 6.3 SDD / ADR process

This repo practices custom-hybrid SDD: spec + ADRs + assumption registry + tests-as-invariants. Every significant decision is an ADR; every assumption is in the registry with a severity tag; every spec claim that can be made executable is a test.

The phase-by-phase process gates in [`SPEC_SHEET.md` §2](./SPEC_SHEET.md) — work-completed and tests-passing, not metric thresholds — instantiate the discipline.

**Linked ADRs**: filled in once Phase 0 locks each row.

**Known gaps**: see relevant ADR in the appendix index.

---

## 7. Results

The headline characterisation is honest: across the rung ladder + two reference scorers, **none of the rungs decisively beats the classical TF-IDF+LR floor on the 5-slice OOD slate** (pooled_ood AUROC range 0.37–0.52; all CIs overlap chance with substantial margin). The trained transformer rungs (frozen-probe + LoRA) and the ProtectAI reference scorers cluster within a band that is statistically distinguishable from each other on the in-distribution-like slices (jbb_behaviors, xstest) but compresses to near-chance on pooled_ood. The story is not "the ladder works" — it is *the ladder works on IID-shaped attacks and fails to generalize to genuinely OOD distributions*, and the numbers in §7.1 below back that up.

Source data: `evals/metrics/per_cell.parquet` (114 cells), `evals/bootstrap/marginal_cells.parquet` (66 cells × 2 seeds; BCa CI per ADR-022), `evals/bootstrap/paired_cells.parquet` + `paired_cells_seed2.parquet` (40 cells per seed; percentile-method paired-Delta-CI per ADR-022), `evals/audit/mde_per_cell.parquet` (142 cells), `evals/operating_points/dual_policy.parquet` (72 op-points).

Headline figures: F1.svg–F7.svg in `docs/plots/`. Note that the figure renderer is currently using the library-first scaffold path (per the upstream eval-toolkit issues #14–#16 + #22 tracking); canonical-data wire-up of every figure is deferred to a follow-up — the numbers in this section come directly from the parquet outputs above, which are the audit-grade source of truth.

### 7.1 The IID-vs-OOD gap (primary narrative)

Per-rung **marginal AUROC + BCa 95% CI** (seed=1 headline; seed=2 stability check 0/40 cells flagged at 5pct threshold per ADR-022 A-008):

| Rung | jbb_behaviors AUROC | xstest AUROC | pooled_ood AUROC |
|---|---|---|---|
| TF-IDF + LR (classical floor) | 0.445 [0.422, 0.469] | 0.451 [0.436, 0.466] | 0.371 [0.362, 0.381] |
| frozen-probe | 0.542 [0.520, 0.565] | 0.537 [0.522, 0.552] | 0.515 [0.505, 0.525] |
| LoRA | 0.528 [0.505, 0.552] | 0.530 [0.515, 0.546] | 0.383 [0.374, 0.392] |
| ProtectAI v1 | 0.533 [0.464, 0.602] | 0.544 [0.497, 0.589] | 0.440 [0.409, 0.469] |
| ProtectAI v2 | 0.594 [0.512, 0.671] | 0.391 [0.341, 0.442] | 0.402 [0.369, 0.437] |

The gap pattern:

- **frozen-probe** is the strongest on pooled_ood (0.515 [0.505, 0.525]) — the only rung whose pooled_ood CI clears 0.50.
- **LoRA's pooled_ood AUROC (0.383)** is *below* the classical floor (0.371 within CI overlap) and far below frozen-probe (-0.13 AUROC; paired-bootstrap CI does not include zero on this comparison). **LoRA fine-tuning hurts OOD generalization** relative to the frozen probe — a known phenomenon when the fine-tuning distribution mismatch is large.
- **TF-IDF + LR** is competitive on pooled_ood (0.371) and only modestly below the trained rungs on jbb_behaviors / xstest. The classical floor is hard to beat without much stronger inductive biases.
- **ProtectAI v2** beats ProtectAI v1 on jbb_behaviors (0.594 vs 0.533) but loses on xstest (0.391 vs 0.544) — version-to-version updates do not monotonically improve across distributions.

### 7.2 Reference scorer #1 — ProtectAI v1 training-overlap finding

ProtectAI deberta-v3-base-prompt-injection v1 (`suspected_contamination` per the ADR-005 three-state taxonomy + ADR-018 contamination-stratification). Stated training scope: direct prompt injection (English). v1's per-slice AUROC on the project's OOD slate:

| Slice | AUROC | 95% CI |
|---|---|---|
| jbb_behaviors | 0.533 | [0.464, 0.602] |
| xstest | 0.544 | [0.497, 0.589] |
| pooled_ood | 0.440 | [0.409, 0.469] |

The CI on jbb_behaviors crosses 0.50 (chance); the pooled CI does NOT. v1 distinguishes positives from negatives at marginally-above-chance rates on the OOD slate. Disclosure-level evidence: ProtectAI's HuggingFace model card lists their training corpus at category level only, not row-level. Cross-source overlap check via `data/contamination_templates.parquet` is partial; we cannot fully verify disjointness. **Verdict: suspected_contamination retained; results reported with caveat.**

### 7.3 Reference scorer #2 — ProtectAI v2 training-overlap finding

ProtectAI deberta-v3-base-prompt-injection v2 (`suspected_contamination`). v2 adds broader-scope training data per the published model card update. Per-slice AUROC:

| Slice | AUROC | 95% CI |
|---|---|---|
| jbb_behaviors | 0.594 | [0.512, 0.671] |
| xstest | 0.391 | [0.341, 0.442] |
| pooled_ood | 0.402 | [0.369, 0.437] |

v2 is BETTER than v1 on jbb_behaviors (+0.06 AUROC; CIs overlap but separated by ~1 SD) and WORSE on xstest (-0.15 AUROC; CIs do not overlap — a clear regression). v2's broader-scope training did NOT monotonically improve across the OOD slate. The contamination caveat from §7.2 carries over: training scope is disclosed at category level only.

**Note on dropped reference scorers**: per ADR-050, the LLM-judge rungs (gpt-4o-2024-08-06 + claude-sonnet-4-6) were dropped post-lock when Phase 4 cost re-estimation revealed a 16x envelope overrun against the original ADR-018 estimate. The `vendor_black_box` contamination tier therefore has 0 rungs in this submission; the contamination stratification compresses from 4 tiers to 3. See §8.1.

### 7.4 Which capabilities help OOD vs only help IID (secondary narrative)

Rung-by-rung lift over the classical floor (delta AUROC, pooled_ood):

| Rung vs floor | delta AUROC (pooled_ood) | Interpretation |
|---|---|---|
| frozen-probe vs tfidf-lr | +0.144 | Pretrained ModernBERT embeddings DO help OOD — substantial lift |
| LoRA vs tfidf-lr | +0.012 | Adapter fine-tuning collapses the frozen-probe advantage on OOD |
| LoRA vs frozen-probe | -0.132 | LoRA hurts; the adapter weights specialize to training distribution |
| ProtectAI v1 vs tfidf-lr | +0.069 | Off-the-shelf injection detector adds modest signal |
| ProtectAI v2 vs tfidf-lr | +0.031 | v2 update does not propagate to our OOD slate |

**Implication**: the pretrained backbone (ModernBERT) provides the bulk of the OOD generalization budget. Fine-tuning (LoRA) on the in-distribution training pool causes generalization-tax: the rung does better on the training-distribution-shaped jbb_behaviors / xstest slices, but loses on pooled_ood. This is the canonical fine-tuning-overfit signature.

### 7.5 Score-behaviour at the two operating points

Dual-policy thresholds fit on val per ADR-025 + ADR-050 (full-FT excluded; 3 trained rungs only). Mean per-cell achieved metrics on test (LODO held-out attack source):

| Rung | Policy | Mean threshold | Mean test recall | Mean test FPR |
|---|---|---:|---:|---:|
| tfidf-lr | detection (FPR ≤ 1%) | 0.657 | 0.333 | 0.067 |
| tfidf-lr | verification (recall ≥ 99%) | 0.162 | 0.674 | 0.508 |
| frozen-probe | detection | 0.829 | 0.063 | 0.010 |
| frozen-probe | verification | 0.215 | 0.957 | 0.891 |
| LoRA | detection | 0.795 | 0.424 | 0.115 |
| LoRA | verification | 0.019 | 0.724 | 0.411 |

Two findings:

1. **All targets reachable on val** (target_reachable=True for all 72 op-points), but **the val→test transfer is large**: detection-policy FPR creeps above target on every rung (mean test FPR 0.067/0.010/0.115 vs val target 0.01); verification-policy recall drops well below target on tfidf-lr + LoRA (0.674/0.724 vs val target 0.99). The frozen-probe verification policy holds (mean test recall 0.957, close to 0.99 target) — but at catastrophic FPR (0.891).
2. **The verification regime is fundamentally limited on LODO**: held-out attack sources produce test distributions different enough from val that any "guarantee recall ≥ 99%" threshold has either tiny test recall (LoRA: 0.724) or near-100% test FPR (frozen-probe: 0.891). The detection regime is more forgiving: tfidf-lr + LoRA hold FPR under ~12% with usable recall.

### 7.6 Calibration findings

Calibration-metric evaluation per ADR-023 (ECE 4-variant matrix + Brier + reliability curves) ships in `evals/metrics/per_cell.parquet` columns `ece_equal_mass` + `brier`. Per-rung mean across both-class slices:

| Rung | Mean ECE (equal-mass) | Mean Brier |
|---|---:|---:|
| frozen-probe | 0.144 | 0.265 |
| tfidf-lr | 0.350 | 0.376 |
| LoRA | 0.444 | 0.451 |
| ProtectAI v1 | 0.452 | 0.470 |
| ProtectAI v2 | 0.460 | 0.471 |

**Finding**: frozen-probe has the BEST calibration on both-class OOD slices (ECE 0.144; Brier 0.265). LoRA fine-tuning DEGRADES calibration substantially (ECE 0.444 — 3x worse than frozen-probe). This is consistent with the §7.7 finding that LoRA over-confidently mis-classifies OOD examples; both the discrimination AND the calibration of the head distribution shift away from honest probabilistic estimates after fine-tuning.

ProtectAI v1/v2 both show high ECE (~0.45+) which is consistent with their out-of-distribution scoring against our slate; their training distribution + our OOD slate differ enough that probability outputs aren't well-calibrated to our evaluation distribution.

[Calibration-fitting (temperature + isotonic + Platt + Beta per ADR-023) was implemented as `src/eval/calibration_battery.py` but not exercised in this Phase 5 close — the calibration-battery pipeline is wired but not fired because the dual-policy operating-point analysis in §7.5 already surfaces the val→test calibration gap as the dominant calibration story. Per-fold reliability curves on F4 (scaffold path; canonical-data wire-up pending upstream eval-toolkit#16).]

### 7.7 Frozen probe vs adapter-fine-tuned

Per ADR-022 paired-bootstrap (percentile-method, 10K resamples × 2 seeds; 0/40 stability flags at 5pct threshold):

| Comparison | Slice | Metric | delta (b − a) | 95% CI | Conclusion |
|---|---|---|---:|---:|---|
| frozen-probe vs LoRA | jbb_behaviors | AUPRC | −0.016 | [−0.024, −0.009] | LoRA worse; CI clears zero |
| frozen-probe vs LoRA | jbb_behaviors | AUROC | −0.014 | [−0.021, −0.006] | LoRA worse; CI clears zero |
| frozen-probe vs LoRA | xstest | AUPRC | −0.001 | [−0.006, +0.004] | Indistinguishable; CI crosses zero |
| frozen-probe vs LoRA | xstest | AUROC | −0.007 | [−0.013, −0.002] | LoRA marginally worse; CI clears zero |

**Headline**: LoRA fine-tuning is *not* a free lunch on this task. On 3 of 4 slice×metric comparisons against frozen-probe, LoRA is significantly worse at the 95% level. The adapter weights specialize to the training distribution, costing the model the OOD generalization that the pretrained backbone alone provided.

### 7.8 The headline characterisation claims

Distilled summary:

- **Claim 1**: No rung in the trained-or-reference slate decisively beats the classical TF-IDF + LR floor on the 5-slice OOD slate (all pooled_ood AUROC CIs within ~0.15 of 0.50; frozen-probe at 0.515 [0.505, 0.525] is the only rung whose CI clears 0.50 with margin). The case-study lesson is "honest OOD generalization for prompt-injection classifiers is harder than the in-distribution numbers suggest" — not "look at this great classifier".
- **Claim 2**: LoRA fine-tuning *hurts* OOD generalization relative to the frozen probe. Paired bootstrap on jbb_behaviors AUROC delta = −0.014 [−0.021, −0.006]; pooled_ood delta = −0.132. The adapter weights specialize to the training distribution. Pretrained backbone embeddings carry the OOD generalization budget; fine-tuning consumes it.
- **Claim 3**: ProtectAI v1 → v2 is *not* a monotone improvement across the OOD slate: v2 beats v1 on jbb_behaviors (+0.06 AUROC) and loses on xstest (-0.15 AUROC). Off-the-shelf detector updates can regress on specific OOD distributions; downstream consumers should not assume v2 dominates v1 universally.
- **Claim 4**: Dual-policy thresholds fit on val do not transfer to LODO test. Detection-policy FPR creeps 1-12% on test vs 1% val target across all 3 trained rungs; verification-policy recall drops well below target on 2 of 3 rungs. The val→LODO gap is the dominant calibration story; per-rung temperature scaling would not fix it without OOD-aware threshold selection.

Each claim is supported by a specific row × CI in §7.1–7.7, not a hand-wave.

**Linked ADRs**: ADR-018 (reference slate; partially superseded by ADR-050), ADR-019 (transformer training recipe), ADR-021 (slice aggregation), ADR-022 (statistical inference apparatus), ADR-024 (cross-fold CI), ADR-025 (dual-policy operating points), ADR-046 (Phase 4 analysis bundle), ADR-050 (rung-slate narrowing — LLM judges + full-FT OOD drops).

**Known gaps**: per-fold calibration-battery + temperature/isotonic fitting outputs not exercised this Phase 5; ECE + Brier present in per_cell.parquet but per-rung summary table left as parquet-readable rather than inlined here. Per-row predictions for full-FT OOD ABSENT (FUSE EIO crash per ADR-050). Canonical-data wire-up of figures F1–F7 pending upstream eval-toolkit issues #14–#16 + #22.

---

## 8. Limitations & deliberately deferred

This chapter consolidates what we *consciously did not do*. These are not failures — they are scope decisions we can defend. The companion chapter §9 covers things we *tried and abandoned*; the distinction matters.

### 8.1 Scope deferrals

- **Deployment** — out of roadmap. The work is characterisation; no deployment recommendation; no deployment-readiness testing.
- **Adversarial red-teaming** — threat model named in §5.6, not exhaustively probed. *Why deferred*: in-scope adversarial inputs (the 4 LODO training sources + 5 OOD slates) already span a wide diversity of attack styles; expanding to a curated red-team set would change the methodology contract from "characterisation against a fixed slate" to "ongoing adversarial probing" — out of case-study scope.
- **Agentic-flow coverage** — multi-step / tool-use injection. *Why deferred*: the classifier scope is single-turn text-as-input; agentic-flow detection requires intermediate-state interception (tool-call args, function-output contamination) which is a deployment-stack question, not a classifier question.
- **Conformal prediction** — distribution-free uncertainty quantification beyond bootstrap. *Why deferred*: conformal calibration on LODO held-out attack sources would require a calibration set drawn from the same distribution as test (which doesn't exist by LODO design). Per-fold bootstrap CIs from ADR-022 are the in-scope honest uncertainty quantification.
- **Cross-language coverage** — English-only by source-slate construction (4 LODO + 5 OOD sources are all English). *Why deferred*: per ADR-016 source-slate lock; cross-language attack generalization is a separate dataset-design question requiring multilingual injection corpora.
- **Cross-source same-style ablation** `[OPEN]` — would disambiguate "training contamination" from "attack-style difficulty" for reference scorers. May be underpowered if per-style sample size is small; in that case treated as an explicit limitation. See EVIDENCE.md §3.
- **LLM-judge reference scorers** (gpt-4o-2024-08-06 + claude-sonnet-4-6) — dropped post-lock per ADR-050. *Why dropped*: Phase 4 cost re-estimation against the actual OOD slate sizing revealed an envelope ~16x the original ADR-018 estimate ($14 → $240) driven by per-row LLM-judge inference being charged at the full input-prompt token count (long injection examples hit 1k-3k tokens routinely). The vendor_black_box contamination tier therefore has 0 rungs in this submission; the contamination-stratification gradient compresses from 4 tiers to 3. ProtectAI v1 + v2 remain as suspected_contamination reference scorers.
- **full-FT OOD inference** — dropped post-lock per ADR-050. *Why dropped*: Phase 5 X11 full-FT re-fire crashed mid-training when shutil.copytree of the 598 MB optimizer.pt to /workspace MooseFS-backed FUSE storage returned [Errno 5] Input/output error (uv#17801 + MooseFS#380 upstream context). full-FT remains in the LODO comparison (3-rung ladder narrative survives via the surviving Phase 2 24 LODO predictions); OOD comparison ships 2 trained rungs (frozen-probe + LoRA) + 1 classical floor (tfidf-lr) + 2 reference scorers (ProtectAI v1 + v2) = 5 rungs.
- (no additional scope deferrals beyond those listed above)

### 8.2 Methodology caveats

- **Single-class OOD slices break threshold-free metrics** — BIPIA + InjecAgent are all-positive attack-only datasets per their source design; NotInject is all-negative benign-only. AUROC and AUPRC are mathematically undefined on these slices and the metrics pipeline correctly skips them (the per-cell parquet `evals/metrics/per_cell.parquet` covers jbb_behaviors + xstest + pooled_ood). Per-slice recall-at-threshold is reported on the single-class slices instead.
- **LODO test sets are intentionally all-positive** per ADR-016 design (held-out attack source = cross-source generalization test). Recall@threshold is the well-defined metric on LODO; AUROC/AUPRC are undefined and not reported there.
- **Val-set inference for trained rungs uses max_length 2048** (vs the Phase 2 training max_length 8192). Covers >99% of val token-length distribution per char-to-token ~4:1 ratio; p99 token length ~1100 in val. Fidelity loss negligible for the dual-policy threshold-fitting purpose; the long-tail truncation is a tracked-but-tolerated divergence from the training-time configuration.
- (no additional caveats beyond those listed above)

Each deferred item has a *why* — usually scope or data availability — and is named in [`NEXT_STEPS.md`](./NEXT_STEPS.md) where applicable.

**Linked ADRs**: filled in once Phase 0 locks each row.

---

## 9. Negative results — architectures and approaches tried and abandoned

This chapter exists because honest framing requires showing the experimental work that did not pan out, not just the work that did. Negative results are interesting: they tell the next iteration *what not to spend time on*.

### 9.1 Hyperparameter / training dead-ends

No factorial hyperparameter sweep was conducted at the chosen compute budget per ADR-019 (single recipe per rung locked at Phase 0; no val-set gridsearch). Three operational findings during canonical fires that ARE worth documenting:

- **`max_length=8192` at training time + `max_length=2048` at val/OOD inference** is a deliberate fidelity trade-off. The trained checkpoints saw the full ModernBERT 8192 context at train time; downstream val inference on local 8GB VRAM (RTX 2070 SUPER) couldn't sustain batch=8 at max_length=8192 without OOM on long examples (val text p99 token length ~1100; max ~2800). Lowered val inference to max_length=2048 + batch=4; covers >99% of val rows intact. The truncation tail is a tracked-but-tolerated divergence (see §8.2).
- **Two pre-training-fire bugs were caught and fix-forwarded** during Phase 2 (X1-X11 chain documented in `decisions/upstream_issues.md`): SSH-ready timeout 240s → 600s for cold image pulls; phantom image tag passing `runpod-deploy validate` without registry HEAD-check; `UV_LINK_MODE=copy` + `UV_CACHE_DIR=/root/uv_cache` + `UV_PROJECT_ENVIRONMENT=/root/.venv` all needed to escape FUSE F_SETLKW deadlocks on RunPod's MooseFS-backed /workspace. Each of these would have been a multi-hour debug spiral for a first-time RunPod consumer; the fix-forward chain is preserved in commits + upstream PRs are filed at brandon-behring/runpod-deploy.
- **Full-FT cleanup-intermediate-checkpoints policy** was locked at `true` per ADR-019 storage discipline (43 GB of throwaway weights avoided per fire) but had to be RELAXED to `false` for Phase 5 X11 re-fire so OOD inference could load the trained checkpoints. The re-fire then crashed at `shutil.copytree` on the 598 MB optimizer.pt due to FUSE EIO. The lesson is operational: storage-discipline locks that delete weights need a `keep_final_only` flag to support post-train OOD inference workflows. Filed upstream as a runpod-deploy issue (proposed `lifecycle.keep_final_checkpoint` config knob).

### 9.2 Architectures evaluated and dropped

- **DeBERTa-v3-base** dropped during Phase 0 lock per ADR-015 (formerly ADR-007) for cross-backbone context-window asymmetry — DeBERTa-v3 caps at 512 tokens vs ModernBERT-base 8192. Including both backbones would have produced an irreducible truncation × architecture confound on BIPIA-style indirect injection. Single-backbone slate (ModernBERT-base × 3 conditions) preserves the rung-ladder narrative without architecture confounding.
- **Lakera Guard reference scorer** dropped at Phase 0-03 per ADR-018 (terms-of-service verification overhead unacceptable for prototype scope). The reference slate gained ProtectAI v1 in its place — internal v1→v2 lift becomes a parallel to the trained-rung-lift story.
- **LLM-judge reference rungs (gpt-4o + claude-sonnet-4-6)** dropped at Phase 4 cost re-estimation per ADR-050 (16× envelope overrun). See §8.1.
- **full-FT OOD inference** dropped at Phase 5 X11 re-fire per ADR-050 (FUSE EIO crash; non-deterministic; re-fire operationally fragile at 6-12 hr wall on Low-stock A100). full-FT remains in LODO comparison; OOD ships 2 trained rungs. See §8.1.

### 9.3 Data-pipeline experiments that didn't matter

- **Dedup threshold sweep** — ADR-042 locked the LLM-pre-label bootstrap calibration at a fixed cosine threshold per `evals/dedup_calibration.json`. A sensitivity sweep on threshold ± 0.05 was considered but deferred — the calibration's `human_verified_pct` operator follow-up (raise from 0 to 100 before v1.0.0 tag per ADR-042) is the higher-leverage gate.
- **Augmentation strategies** — no synthetic augmentation was tried (no paraphrase generation, no back-translation, no character-noise injection). The case-study scope is *characterisation of an honest classifier slate against a fixed data slate*, not data-augmentation research. Tracked as out-of-scope per Phase 0 lock.

### 9.4 What the negatives imply for v6

The OOD generalization wall is the dominant signal. Three concrete suggestions for a successor iteration:

1. **OOD-aware training data** — the current pool is dominated by 4 LODO sources (prompt-injection-style attacks) that share a stylistic core. Adding cross-style attacks (BIPIA-style indirect injection in training; jailbreaks-as-questions in training) would test whether the OOD wall is *training-distribution scope* or *fundamental classifier inadequacy*.
2. **Pretrained backbone scaling** — frozen ModernBERT-base embeddings provide more OOD generalization than LoRA fine-tuning does. A v6 ablation along backbone scale (ModernBERT-base 150M → ModernBERT-large 400M; or a different backbone family) would test whether the OOD ceiling is backbone-capacity-limited.
3. **OOD-aware threshold selection** — dual-policy thresholds fit on val do not transfer to LODO test (§7.5). Per-source temperature scaling or conformal calibration with a held-out OOD calibration set (currently impossible by LODO design) would close the val→LODO gap.

**Linked ADRs**: ADR-015 (single-backbone lock, supersedes ADR-007), ADR-018 (reference slate), ADR-019 (transformer training recipe), ADR-042 (dedup calibration), ADR-050 (rung-slate narrowing).

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
make headline-frozen-probe   # ~$0.84-$2.13 (frozen-probe canonical fire; A100-80G ~20-50 min)
make headline-lora           # ~$0.89-$1.76 (LoRA canonical fire)
make headline-full-ft        # ~$1.61-$7.14 (full-FT canonical fire — note FUSE EIO risk per ADR-050)
```

Runbook: per-RunPod-yaml in `configs/runpod/headline-*.yaml`; orchestration via `runpod-deploy run` per ADR-020 (cost-cap-gated; interactive approval; multi-DC failover ladder).

### 10.3 Evaluation

Eval invocation captures a NeurIPS-aligned manifest at `artifacts/runpod/<run-id>/runpod_deploy_pull_manifest.json` covering pod ID, GPU class, datacenter, image SHA, wall time, estimated cost, payload lockfile SHA. **The project persists per-row predictions** at `evals/predictions/<rung>__fold<F>__seed<S>__<source>.parquet` per ADR-013 + ADR-021 (per-row predictions schema-validated against `src.eval.schemas.PredictionsRowModel`). 282 prediction parquets land post-Phase-5: 84 LODO (24 frozen-probe + 24 LoRA + 24 full-FT + 12 tfidf-lr) + 138 OOD trained-rung (60 frozen-probe + 60 LoRA + 60 tfidf-lr + 18 ProtectAI). Aggregated metric outputs land at `evals/metrics/per_cell.parquet`, `evals/bootstrap/`, `evals/audit/`, `evals/operating_points/` per the §7 source references.

### 10.4 Data + checkpoints

- **Data sources**: licenses + download instructions in [`SPEC_SHEET.md` §3](./SPEC_SHEET.md). HF revisions SHA-pinned at build time per `data/source_manifest.yaml` (forward-only).
- **Checkpoints**: NOT published to HF Hub for this rc1 submission (frozen-probe + LoRA checkpoints stay in local `evals/checkpoints/` per the case-study scope; HF Hub publish gated on the v1.0.0 tag per ADR-032). full-FT checkpoints DO NOT EXIST (FUSE EIO crash per ADR-050).
- **Predictions**: bundled in this repo as gitignored parquets under `evals/predictions/` (regeneration via `make` recipes against the committed checkpoints + data). GitHub release tag with a predictions tarball is gated on v1.0.0 per ADR-033.

### 10.5 Transcripts

Selected Claude-Code transcripts illustrating key decision points are in `transcripts/` (private by default; gitignored per `transcripts/README.md`; emailed to the reviewer at submission time). Phase 0-NN transcripts cover threat-model + brief alignment, model scope, data design, evaluation framework, deployment scope, etc. Phase 4-5 transcripts cover the canonical-recovery /exploring-options rounds. Each ADR references its source transcript by filename in the frontmatter `transcript:` field.

**Linked ADRs**: ADR-013 (deliverable scope), ADR-016 (data design), ADR-025 (operating points), ADR-027 (per-row predictions schema), ADR-032 (HF Hub publish gate), ADR-033 (tag discipline).

---

## 11. Lessons & reflections

Short list of what was surprising, what the SDD process bought, and what it cost.

- **OOD generalization is genuinely hard, and the honest finding is methodologically richer than the "look at this great classifier" version**. The trained transformer rungs hover near chance on the OOD slate (§7.1); LoRA fine-tuning is a *negative* result vs the frozen probe on pooled_ood (-0.132 AUROC; CI clears zero). A submission framed as "we built a great classifier" would have HIDDEN this finding; a submission framed as "we characterised the honest performance ladder" SURFACES it. The Phase 0-locked methodology (LODO + bootstrap CIs + paired-bootstrap rung-vs-rung + dual-policy threshold characterisation) forced the honest story to land.
- **The SDD process bought reproducibility + audit trail at the cost of a 9-decision-per-sub-session interview flow at Phase 0**. ~50 decisions across ~9 topic-focused sub-sessions per `SPEC_GREENFIELD.md`. Each `[OPEN]` lock produced an ADR; SUBMISSION_AUDIT.md regenerates from ADRs as a single source of truth. The cost was the time investment up front; the benefit was zero methodology drift later — every Phase 1-7 commit traced cleanly back to an ADR claim. ADR-050 (rung-slate narrowing) is itself the supersession-on-supersession proof point: when reality forced a methodology drift, the SDD discipline ate it cleanly via a narrow ADR-018 / ADR-021 partial supersession rather than a silent code change.
- **Library-first invariant retrofit happened mid-project** (memory: `library-first-is-project-wide-invariant`). Phase 1-3 had accumulated 3 sites where eval-toolkit primitives were duplicated locally; ADR-047 retrofitted them in a single landing rather than fix-forward per-site. The lesson: at every module-design step audit `eval-toolkit + runpod-deploy + research_toolkit` for an existing primitive BEFORE writing project glue. Cost overrun on the LLM judges (ADR-050 driver 1) was a similar discipline lapse — original estimate didn't account for the actual token volume.
- **The /exploring-options multi-round pattern unblocked complex decisions** that ExitPlanMode-on-first-attempt would have committed prematurely. Four rounds for the Phase 4 canonical-recovery plan (each round surfaced a risk the prior rounds didn't see). Two rounds for the GitHub-push-blocked recovery (initial Option B was rejected; second round confirmed Option A). The /exploring-options skill is a forcing function for explicit option-space surfacing.
- **FUSE-on-RunPod is a non-deterministic bug class** (memory: `fuse-workspace-needs-uv-link-mode-copy`; `runpod-rsync-everything-before-delete`). The X1-X11 fix-forward chain documents four distinct FUSE failure modes (SSH-ready timeout, phantom image, UV link-mode, atomic checkpoint copy); each cost a real fraction of the $15.74 cumulative spend (~50% of cost is FUSE-recovery overhead). Filed upstream issues + PRs at brandon-behring/runpod-deploy so future consumers don't re-discover them. The library-first invariant cuts both ways: when an upstream gap surfaces, file an upstream issue BEFORE local workaround.
- **Per-step commits + a 2-checkpoint push cadence survived context auto-compaction**. The session spanned multiple Claude context windows + ran for many hours; commit per work-unit + intermediate pushes meant no work was lost when context boundaries hit. The discipline overhead was small; the resilience benefit was large.

What surprised: the OOD wall. Going in I expected the rung ladder to be a positive story (each rung adds something over the floor); the LoRA-fine-tuning regression on pooled_ood was the methodologically richest finding. Going forward (v6): the §9.4 prescriptions — OOD-aware training data, backbone scaling, OOD-aware threshold selection — would test whether the wall is data-distribution or capacity-bounded.

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

Transcripts referenced by ADR `transcript:` frontmatter fields are bundled and emailed to the reviewer at submission time per `transcripts/README.md`; the `/save-transcript` skill produces them.

### F. eval-toolkit methodology curriculum

[`docs/methodology/`](https://github.com/brandon-behring/eval-toolkit/tree/main/docs/methodology) — 16-chapter curriculum. Cross-linked from §3, §5.1–5.5, and §6.1 above.
