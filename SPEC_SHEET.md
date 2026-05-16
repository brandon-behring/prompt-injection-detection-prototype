# Project specification (filled at end of Phase 0)

**Status**: `[OPEN]` (`DRAFT` → `PROPOSED` → `LOCKED` — locks once Phase 0 closes all decisions)
**Type**: Single-version SDD spec; revisions tracked via ADRs (Michael Nygard format)

> **Role of this document.** SPEC_GREENFIELD.md is the authoritative pre-Phase-0 spec — it defines the contract and the open decisions. SPEC_SHEET.md is the post-Phase-0 fill-in form: same skeleton, but each `[OPEN]` row gets replaced with `[LOCKED: <chosen value>]` once Phase 0 resolves it. Phase 1 cannot begin until SPEC_SHEET.md has zero `[OPEN]` rows.

> **Companion docs**:
> - [`code_quality.md`](./code_quality.md) — implementation discipline
> - [`assumptions.md`](./assumptions.md) — registry of unverified assumptions
> - [`decisions/`](./decisions/) — ADR index + immutable decision records
> - [`EVIDENCE.md`](./EVIDENCE.md) — external-evidence audit trail

---

## Context

This submission targets the morning of 2026-05-18 (≈ 2.5 working days from Phase 0-00 start on 2026-05-15), with **Long-scope ambition refined by Phase 0-01** (1×3 trained-rung slate — ModernBERT-base × {frozen-probe, LoRA, full-FT} per ADR-015 supersedes ADR-007 — plus 4 reference rungs at their published native configs — OpenAI LLM-judge + Anthropic LLM-judge + Lakera Guard + ProtectAI deberta-v3 — with 3-seed multi-seed protocol per ADR-006 floor, full OOD slate, and paired-bootstrap apparatus per ADR-006) leveraging `runpod-deploy` + `eval-toolkit` library infrastructure, and an explicit fallback ladder updated per ADR-015 (1×3 → 1×2 → 1×1) that activates if mid-Phase-2 surfaces infeasibility (per ADR-001). The single-backbone refinement eliminates the per-backbone-truncation confound on the indirect-injection zero-shot OOD slice that the original 2-backbone framing would have produced (per ADR-014 Q3/Q4 walk). The deliverable is a focused PDF rendered from `WRITEUP.md` + a public GitHub repo serving as the evidence locker (ADR-002 + ADR-003), structured as a **hub-and-spoke writeup** for a dual A1+A2 audience (hiring manager + ML researcher; ADR-004). The submission is governed by three project-level methodology principles (ADR-005): methodology over metrics, honest evaluation preferred even when models look worse, and structured limitations with extension conditions.

- **Locked methodology defaults**: process discipline + validated content patterns are `[LOCKED]` generically; project-specific instantiation details (datasets, rungs, hyperparams, OOD slate, budget) are `[OPEN]` for Phase 0
- **Resolved at Phase 0**: see `decisions/` for ADRs locked during the spec interview
- **Open at start of Phase 0**: see SPEC_GREENFIELD ledger appendix for the ~50 [OPEN] decisions resolved during the interview

This is an **exploration spec** for an SDD-disciplined iteration — not a production system, not a paper, not a publishable benchmark. The work is *methodology + capability characterization braided*: characterize what each capability layer adds, using an evaluation methodology rigorous enough to detect real differences and quantify uncertainty.

---

## 1. Goal & non-goals

**Goal**: `[TBD: one-paragraph statement of what  commits to deliver]`

**Non-goals**:
- Not optimizing for SOTA PR-AUC.
- Not building a deployable service. Deployment is not on the roadmap.
- Not creating a publishable benchmark.
- `[OPEN]` Not picking a leader rung — each rung's trade-offs are characterized, no rung is promoted as the deployment recommendation.
- `[TBD: additional non-goals; populated at Phase 0]`

**Scope authority**: the spec itself is the scope cap. Anything not specified here is out of  scope. Adding scope post-spec-freeze requires an ADR with explicit "Why this is in scope now" justification.

---

## 2. Phases & process gates

the project work is structured into six phases. Each phase has a gate checklist of work-completed and tests-passing — **not metric thresholds**. The intent is to make movement between phases auditable, not to bind the project's narrative to specific numerical outcomes.

### Phase 0: Spec lock-in interview `[LOCKED]`

- [ ] Agent reads this spec end-to-end
- [ ] Every `[OPEN]` / `[TBD: value]` decision is surfaced as a clarifying question
- [ ] Human picks options for each surfaced decision
- [ ] Decisions are recorded as ADRs (Michael Nygard format)
- [ ] Phase 1 cannot start until every decision is resolved or explicitly deferred

Gate: `decisions/` directory contains an ADR for every Phase-0-resolved decision; `transcripts/` directory contains the interview transcript.

### Phase 1: Data

- [ ] Sources defined and licenses verified
- [ ] Audit complete; counts and class balance documented in `evals/data_audit.json`
- [ ] Semantic dedup applied per `[ADR-003]` (calibrated MiniLM @ 0.80); calibration evidence persisted at `evals/dedup_calibration.json`
- [ ] Cross-source benign dedup applied before split
- [ ] Leakage scan run; results in `evals/leakage_report.json`
- [ ] Train/val/test splits locked and persisted

Gate: every checkbox ticked; `tests/test_data.py` and `tests/test_leakage.py` green.

### Phase 2: Training

- [ ] Each rung's config persisted at `config/<rung>.yaml`
- [ ] All rungs trained successfully on `[TBD: (candidate) H100 via runpod-deploy]`
- [ ] Training artifacts captured per `runpod-deploy` manifest (git SHA, seed, GPU info, env)
- [ ] **Per-row predictions persisted** at `evals/predictions/<rung>__<fold>__<seed>.parquet` `[LOCKED]`
- [ ] Per-rung checkpoint persisted to `[TBD: HF Hub at BBehring/<project>; resolved at Phase 0]`

Gate: every checkbox ticked; training manifests schema-validated.

### Phase 3: Evaluation

- [ ] All rung × slice metrics computed via `eval-toolkit`
- [ ] OOD slate evaluated end-to-end (~4 slices typical; final composition resolved at Phase 0)
- [ ] Calibration battery run (ECE + Brier + reliability) for every rung
- [ ] Thresholds selected on validation only (detection-policy and verification-policy on in-house rungs; recall@FPR pinpoints on all rungs)
- [ ] `evals/results.json` schema-validated against `eval-toolkit`'s `results.v1.json` schema

Gate: every checkbox ticked; `evals/results.json` parses cleanly.

### Phase 4: Analysis

- [ ] Bootstrap CIs computed for every headline metric
- [ ] Paired-bootstrap differences computed for every rung-vs-rung comparison of interest
- [ ] MDE estimated for every reported CI
- [ ] Per-source / per-style breakdowns computed (LLM-as-rater rubric audit `[OPEN]`)
- [ ] Figures 1–7 (or the project's named slate) rendered to `docs/plots/`

Gate: every checkbox ticked; analysis JSON outputs match schemas.

### Phase 5: Writeup

- [ ] All WRITEUP sections drafted
- [ ] All  ADRs written and indexed in `decisions/README.md`
- [ ] Transcripts linked from WRITEUP appendix
- [ ] EVIDENCE.md populated for every external-evidence claim
- [ ] PDF bundled: README + WRITEUP + NEXT_STEPS + SPEC_SHEET + EVIDENCE
- [ ] All `[TBD: value]` / `[OPEN]` markers in submission templates resolved or justified

Gate: every checkbox ticked; PDF reads cleanly start-to-finish.

---

## 3. Data design

### 3.1 Train pool composition

`[LOCKED: Path α — full source slate (per ADR-016)]` — 4 positive sources + 2 benign sources + 5 OOD slices. HarmBench + Tensor Trust + LLMail-Inject deferred to afterword.

| Source | Approx N (post-dedup, capped) | Role | License | LODO fold |
|---|---|---|---|---|
| `deepset/prompt-injections` | ~500-650 (use all) | Train pos | Apache-2.0 | 1 |
| `Lakera/gandalf_ignore_instructions` | ~800-1000 (use all) | Train pos | MIT | 2 |
| `Lakera/mosscap_prompt_injection` | 3000 (cap) | Train pos | MIT | 3 |
| `hackaprompt/hackaprompt-dataset` | 3000 (cap) | Train pos | per dataset card | 4 |
| `lmsys/lmsys-chat-1m` | 10000 (cap; English-only filter) | Train neg | CC-BY-4.0 | (stratified across folds) |
| `HuggingFaceH4/ultrachat_200k` | 10000 (cap) | Train neg | Apache-2.0 | (stratified across folds) |
| `leolee99/NotInject` | 339 | OOD hard-neg (over-defense) | MIT | (never trained) |
| `paul-rottger/xstest` | 450 | OOD hard-neg (over-refusal) | per repo | (never trained) |
| `JailbreakBench/JBB-Behaviors` | 200 (100 harmful + 100 benign) | OOD mixed | MIT | (never trained) |
| `microsoft/BIPIA` | per-task | OOD indirect (zero-shot per ADR-014) | per repo | (never trained) |
| `uiuc-kang-lab/InjecAgent` | 1054 | OOD agentic (stretch probe) | per repo | (never trained) |

**Benign subsample ceilings per source**: `[LOCKED: 3K positives per source for mosscap+HackAPrompt; use-all for deepset+Lakera-gandalf post-dedup; 10K benigns per source for LMSYS+UltraChat; random subsample at seed=42 (per ADR-016)]`. Class balance per LODO training pool ≈ 1:2 to 1:2.7 (positives:benigns). Quality-filtered HackAPrompt + attack-type-stratified + length-stratified subsamples deferred to afterword.

### 3.2 Splits

`[LOCKED: LODO k=4 over positive sources + 3 seeds per LODO fold; no internal k-fold (per ADR-016)]`. Source-disjoint Leave-One-Dataset-Out at outer level (4 folds, one held-out positive source per fold) + 3 random-initialization seeds = 12 observations per rung = 36 trained runs across the 3 ModernBERT-base conditions from ADR-015. Within each LODO fold: single 80/20 train/val random split (no nested k-fold); val used for threshold selection + calibration fitting + early-stopping per ADR-011 Guarantee 6. Per-rung bootstrap CIs from 12 observations (10K bootstrap iterations, BCa marginal per ADR-006); rung-vs-rung paired-bootstrap uses (LODO-fold × seed) pairing; MDE on Δ-AUROC ≈ 0.03. Stratified k-fold within LODO (Fomin 2025 / Nadeau-Bengio 2003 variance decomposition; ~5x compute) deferred to afterword.

### 3.3 Dedup, leakage prevention, cross-source label conflicts

- **Semantic dedup**: `[LOCKED: sentence-transformers/all-MiniLM-L6-v2 cosine at threshold 0.80; simplified calibration via FPR+FNR on 50-pair labeled holdout persisted to evals/dedup_calibration.json (per ADR-016)]`. Label-aware (within (source, label) cells); deterministic first-occurrence retention; cross-label minimal pairs preserved per SPEC_GREENFIELD lock. MPNet-base-v2 + full 4-gate selection rule + cross-encoder reranker deferred to afterword.
- **Cross-source minimal pairs**: `[LOCKED]` preserve-and-flag.
- **Cross-source benign dedup ordering**: `[LOCKED: within-source-first → cross-source (LMSYS-priority tiebreak) → LODO split (per ADR-016)]`. Pipeline: within-source dedup pass per source → cross-source dedup pass (LMSYS-priority on cross-source near-duplicates because LMSYS is real-user data; UltraChat is synthetic) → split into LODO folds with benign stratification.
- **Leakage invariants**: `tests/test_leakage.py` asserts no exact-hash and no high-cosine train-test overlap.
- **Reference-scorer training-overlap audit**: `[LOCKED]` see WRITEUP §3.3 + EVIDENCE.md §1–2.

**Truncation policy for inputs > length cap**: `[LOCKED: adaptive-chunked-max-pool stride=cap//2 at eval time; head-truncation at training time (per ADR-014)]`. Training-positives are short so head-truncation rarely bites at train time (HF tokenizer default `truncation_side="right"`). At eval time, inputs exceeding the cap are split into overlapping chunks of size `cap` with stride `cap // 2` (50 percent overlap so no token sits at a chunk boundary in both chunks); each chunk is scored independently; per-sample score is the max over chunk scores (max-pool aggregation — matches adversarial threat model). Under ADR-015 single-backbone refinement (ModernBERT-base at 8K native), adaptive chunked rarely activates (only on samples exceeding 8K tokens — about 5 percent of BIPIA per dossier estimate). Reference rungs run at their published native configurations including their native truncation policies (ProtectAI head-truncation at 512; Lakera as-API; LLM-judges receive full sample). Mandatory chunked-vs-head ablation on the BIPIA slice lives in `WRITEUP/truncation-ablation.md`. Phase 1 validation checkpoint: if BIPIA outlier-rate above 8K exceeds 15 percent of the slice, a superseding ADR-016 adjusts chunk-stride or aggregation policy.

### 3.4 OOD slate

`[LOCKED: 5 OOD slices (per ADR-016)]` — direct over-defense + over-refusal + mixed-direct + indirect zero-shot + agentic-stretch. HarmBench + Tensor Trust + LLMail-Inject deferred to afterword as named next-iteration extensions.

| Slice | Source | Role | Why |
|---|---|---|---|
| NotInject | `leolee99/NotInject` | Hard-negative (benign-with-injection-triggers) | Tests over-defense per InjecGuard 2024 methodology; explicitly invites worse-but-honest evaluation per ADR-005 Principle 2 |
| XSTest | `paul-rottger/xstest` | Hard-negative (over-refusal) | Tests exaggerated-safety patterns per Röttger 2024 NAACL |
| JBB-Behaviors | `JailbreakBench/JBB-Behaviors` | Mixed (100 harmful + 100 benign) | Standardized misuse-behavior evaluation per Chao 2024 NeurIPS D&B |
| BIPIA | `microsoft/BIPIA` | Indirect (zero-shot OOD per ADR-014 Q1) | Indirect-injection benchmark per Yi 2023 KDD; the load-bearing zero-shot transfer measurement |
| InjecAgent | `uiuc-kang-lab/InjecAgent` | Agentic (stretch probe) | Tool-integrated agent injection per Zhan 2024 ACL; agentic transfer-of-transfer caveat per ADR-010 Bound 2 |

**Linked ADRs**: ADR-014 (threat-model bundle — attack-class scope), ADR-015 (rung architecture — 3 ModernBERT-base trained + 4 reference rungs), ADR-016 (this — data design bundle), ADR-008 (data scope brief-level locks — preserved).

---

## 4. Model recipe (locked, no gridsearch)

Each rung is locked before training begins. No val-set hyperparameter gridsearch.

### 4.1 Rung 1 — *linear floor*
`[OPEN]` Linear baseline (e.g. TF-IDF + logistic regression). Deterministic.

### 4.2 Rung 2 — *frozen-features probe*
`[LOCKED: ModernBERT-base frozen-probe (per ADR-015)]` — Transformer body frozen; linear head trained on pooled CLS or mean-pooled embeddings. Deterministic at a pinned seed; one of 3 trained rungs.

### 4.3 Rung 3 — *adapter-fine-tuned*
`[LOCKED: ModernBERT-base LoRA (per ADR-015)]` — PEFT-LoRA adapters; full backbone frozen. Specific LoRA hyperparameters (r, α, dropout, target modules, lr, epochs, precision, batch, max_len, warmup, seed protocol) deferred to Phase 0-03 per SPEC_GREENFIELD §2 Model ledger rows 335-337. One of 3 trained rungs.

### 4.4 Rung 4 — *full-FT trained backbone*
`[LOCKED: ModernBERT-base full-FT (per ADR-015)]` — Full backbone parameters trainable; standard HF Trainer with eval-toolkit metric callbacks. One of 3 trained rungs. With the frozen-probe and LoRA rungs, completes the 1×3 trained-rung slate.

### 4.5 Reference rungs — *4 published baselines at native config*
`[LOCKED: 4 reference rungs (per ADR-007 reference slate preserved by ADR-015)]` —
- **R-LLM-OpenAI**: One OpenAI LLM-judge (specific model ID deferred to Phase 0-03 — likely GPT-4o or successor); temperature=0; one call per eval row; receives full sample (128K+ native context); prompt template versioned in repo.
- **R-LLM-Anthropic**: One Anthropic LLM-judge (specific model ID deferred to Phase 0-03 — likely Claude Sonnet 4 or successor); temperature=0; one call per eval row; receives full sample; prompt template versioned in repo.
- **R-Lakera**: Lakera Guard via API; called at whatever the API does (no preprocessing override on our side).
- **R-ProtectAI**: `protectai/deberta-v3-base-prompt-injection` (open-weights); inference-only at its published native config — head-truncation at 512 (no preprocessing override on our side).

Each reference rung is called at its published native configuration including its native truncation policy. Apples-to-apples comparison against deployed baselines requires testing them as they exist, not as preprocessed by us. Training-data overlap audit per EVIDENCE.md §1-2.

### 4.6 Additional rungs

`[LOCKED: NONE in primary slate; future-work extensions per ADR-015 alternatives — ModernBERT-large size-up, matched-context cross-backbone control, alternate classification head, calibration via validation-fit temperature]`. Calibration is a separate methodology axis (Phase 0-04 walks the calibration battery, ledger row 343).

**Linked ADRs**: filled in once Phase 0 locks each rung.

---

## 5. Eval design

### 5.1 Primary descriptive metrics

PR-AUC, ROC-AUC, recall@FPR={0.1%, 1%, 5%} `[OPEN: recall@FPR pinpoints; resolved at Phase 0]`, ECE (equal-mass + Kumar-2019 debiased), Brier. All reported with bootstrap CIs.

### 5.2 Statistical tests

**Stance**: report effect sizes and CIs only. No p-values. The work characterises differences and their uncertainty rather than claiming significance.

Anchored to [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) primitives:

- `bootstrap_ci` — per-metric finite-sample uncertainty. See [methodology/bootstrap.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/bootstrap.md).
- `paired_bootstrap_diff` — paired comparisons across rungs on the same test set. See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md).
- `mde_from_ci` — minimum detectable effect.
- Calibration battery (`reliability_curve`, `fit_temperature`, `fit_isotonic_calibrator`, ECE variants, Brier). See [methodology/calibration.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/calibration.md).
- `cv_clt_ci` — CLT-based CI for cross-fold variance.

**Cross-fold CI methodology**: `[OPEN]` — bootstrap-per-fold / CV-CLT (Bates 2024) / Nadeau-Bengio 2003. LODO folds are not independent; the choice affects whether headline cross-fold CIs are valid. See SPEC_GREENFIELD ledger §3 Eval row "Cross-fold CI methodology".

### 5.3 Operating points — detection vs verification

`[LOCKED]` Dual-policy framing on **in-house rungs only**. Reference scorers (off-the-shelf reference detectors) get recall@FPR pinpoints with explicit contamination caveats; no dual-policy framing (would imply deployment-ready operating points that don't survive the contamination caveat).

Detection (FPR ≤ 1%) + Verification (FNR ≤ 1%) selected on **validation only** via eval-toolkit's `ThresholdSelector` protocol. See [methodology/thresholds.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/thresholds.md).

### 5.4 Per-source and per-style breakdowns

Required for any OOD claim — aggregate metrics hide heterogeneity. Reported alongside the headline IID/OOD numbers. Per-style heuristic tagger regex-based) is conservative;  may `[TBD: (candidate) invest in LLM-as-rater rubric audit]`.

### 5.5 Adversarial robustness

`[TBD: largely deferred; named but not exhaustively probed]` — the threat model (paraphrase, encoded payloads, multi-turn injection, base64/leetspeak obfuscation) is named; what was not tested is named explicitly in WRITEUP §5.6 and §8.

**Linked ADRs**: ADR-021, ADR-022, ADR-023.

---

## 6. Code architecture

The work spans three repos:

- **`prompt-injection-detection-prototype`** (this repo) — modelling: data loading, training, classification API, project-specific scoring code.
- **[`eval-toolkit`](https://github.com/brandon-behring/eval-toolkit)** — evaluation harness: metrics, bootstrap, calibration, threshold selection, leakage detection, slice-aware orchestration, reproducibility manifests, versioned JSON schemas.
- **[`runpod-deploy`](https://github.com/brandon-behring/runpod-deploy)** — cloud orchestration for training/eval runs on rented GPUs. **the project's additions**: prediction-persistence pull-pattern + checkpoint upload-to-HF-Hub pattern.

The split is intentional: methodology curriculum and primitives live in `eval-toolkit` so they survive across iterations; cloud orchestration lives in `runpod-deploy` so it's reusable across projects.

---

## 7. Verification & acceptance criteria

This iteration is considered complete when **all five Phase 5 gates pass**:

- All WRITEUP sections drafted with `[TBD: value]` markers resolved.
- All  ADRs written.
- Transcripts linked.
- EVIDENCE.md populated for every external-evidence claim.
- PDF bundled.
- Markers explained.

Plus the standard quality gates that apply to every phase:

- `make test` passes (incl. invariants for class balance, source-disjoint, frozen-dataclass, no-emoji, reporting-completeness).
- `make lint` clean.
- `evals/results.json` schema-validated against eval-toolkit's `results.v1.json`.
- All assumptions with severity ≥ medium in `assumptions.md` appear in the WRITEUP caveats block.

---

## 8. SDD process notes

1. **Spec freeze**: once this document is `LOCKED`, changes require an ADR.
2. **Phase 0 interview**: `[LOCKED]` agent reads spec, surfaces decisions, human picks, decisions become ADRs. .
3. **Process gates, not outcome gates**: phase gates check that work was done and tests pass — not that metrics hit a target.  deliberately avoids tying phase movement to outcome numbers so that the eval reports what was found rather than what was needed to advance.
4. **Transcript capture**: `[LOCKED]` every session where decisions are discussed produces a transcript in `transcripts/`. .
5. **Prediction persistence**: `[LOCKED]` per-row predictions are persisted alongside metrics. `runpod-deploy` pulls per-row score artifacts so downstream analyses (calibration, threshold sweeps, ROC curves) run from persisted predictions without re-running inference.
6. **ADR cadence**: one ADR per significant decision; format per Michael Nygard.
7. **Assumption updates**: when an assumption is invalidated mid-implementation, update `assumptions.md` and write a corrective ADR.
8. **Tests-as-invariants**: every spec claim that can be made executable as a test, must be.

**Linked ADRs**: ADR-001, ADR-025, ADR-026.

---

## 9. Open questions deferred to future iterations

`[TBD — populate as  work proceeds]`

- `[TBD: value]`
- `[TBD: value]`

---

## Appendix: decision trace

`[TBD: link to the planning artifact at ~/.claude/plans/<planning-slug>.md]`
