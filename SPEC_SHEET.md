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

This submission targets the morning of 2026-05-18 (≈ 2.5 working days from Phase 0-00 start on 2026-05-15), with **Long-scope ambition refined by Phase 0-01 + Phase 0-03** (4-rung trained slate — TF-IDF + LR classical floor per ADR-017 + ModernBERT-base × {frozen-probe, LoRA, full-FT} per ADR-015 — plus 4 reference rungs at their published native configs — `gpt-4o-2024-08-06` + `claude-sonnet-4-6` + `protectai/deberta-v3-base-prompt-injection` (v1) + `protectai/deberta-v3-base-prompt-injection-v2` per ADR-018 partially supersedes ADR-015 reference slate (Lakera dropped, ProtectAI v1 added) — with 3-seed multi-seed protocol per ADR-006 floor, full OOD slate, and paired-bootstrap apparatus per ADR-006) leveraging `runpod-deploy` 0.7.7 + `eval-toolkit` library infrastructure (per ADR-020 — 8-class GPU failover + dual-DC + adaptive batch + dual-layer cost cap), and an explicit fallback ladder updated per ADR-015 (1×3 → 1×2 → 1×1 for transformer rungs; TF-IDF+LR classical floor retained across all fallbacks per ADR-017) that activates if mid-Phase-2 surfaces infeasibility (per ADR-001). The single-backbone refinement eliminates the per-backbone-truncation confound on the indirect-injection zero-shot OOD slice that the original 2-backbone framing would have produced (per ADR-014 Q3/Q4 walk). The full 8-rung slate is stratified along ADR-005's three-state contamination taxonomy (per ADR-018) — TF-IDF+LR verified_disjoint anchor + transformer rungs backbone-partial-disjoint + ProtectAI v1/v2 suspected_contamination + LLM judges vendor_black_box — making contamination disclosure a methodology axis rather than a footnote. Total: 48 trained runs (4 rungs × 3 seeds × 4 LODO folds; TF-IDF+LR runs are sklearn CPU, transformer runs are H100/equivalent bf16 with per-epoch prediction save). The deliverable is a focused PDF rendered from `WRITEUP.md` + a public GitHub repo serving as the evidence locker (ADR-002 + ADR-003), structured as a **hub-and-spoke writeup** for a dual A1+A2 audience (hiring manager + ML researcher; ADR-004). The submission is governed by three project-level methodology principles (ADR-005): methodology over metrics, honest evaluation preferred even when models look worse, and structured limitations with extension conditions.

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

`[LOCKED: LODO k=4 over positive sources + 3 seeds per LODO fold; no internal k-fold (per ADR-016)]`. Source-disjoint Leave-One-Dataset-Out at outer level (4 folds, one held-out positive source per fold) + 3 random-initialization seeds = 12 observations per rung. With the 4-rung trained slate locked by ADR-017 + ADR-019 (TF-IDF+LR + ModernBERT × {frozen-probe, LoRA, full-FT}), this is **48 trained runs** total (4 rungs × 3 seeds × 4 LODO folds); 12 are sklearn CPU runs (TF-IDF+LR), 36 are H100/equivalent bf16 transformer runs with per-epoch prediction save per ADR-019 (72 transformer prediction files + 12 TF-IDF+LR prediction files = 84 trained-rung prediction parquets). Within each LODO fold: single 80/20 train/val random split (no nested k-fold); val used for threshold selection + calibration fitting + early-stopping per ADR-011 Guarantee 6 (NOT used for hyperparameter tuning per SPEC §2 hyperparameter-immutability). Per-rung bootstrap CIs from 12 observations (10K bootstrap iterations, BCa marginal per ADR-006); rung-vs-rung paired-bootstrap uses (LODO-fold × seed) pairing; MDE on Δ-AUROC ≈ 0.03. Stratified k-fold within LODO (Fomin 2025 / Nadeau-Bengio 2003 variance decomposition; ~5x compute) deferred to afterword.

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

### 4.1 Rung 1 — *classical floor (TF-IDF + LR)*
`[LOCKED: sklearn TF-IDF + LogisticRegression (per ADR-017)]` — Combined sparse features via FeatureUnion: word 1-2-grams (`max_features=15000`, `sublinear_tf=True`, `lowercase=True`, `strip_accents=unicode`) + char 3-5-grams (`max_features=15000`); concatenated → up to 30K-dim sparse matrix. Classifier: `LogisticRegression(solver='liblinear', C=1.0, class_weight='balanced', max_iter=1000)` — fit-to-convergence; no epoch concept; deterministic per seed (ADR-006 slate: 42, 1337, 2025). 3 seeds × 4 LODO folds = 12 sklearn CPU runs. Contamination state: **verified_disjoint** (trained on our LODO splits by construction).

### 4.2 Rung 2 — *frozen-features probe*
`[LOCKED: ModernBERT-base frozen-probe (per ADR-015 + ADR-019)]` — Transformer body frozen; linear classifier head (2-class) trained on `[CLS]`-pooled embeddings via `WeightedTrainer` subclass (CrossEntropyLoss with per-fold sklearn `class_weight='balanced'` tensor; per ADR-019). `bf16=True` with fp32 cast before final softmax. 2 epochs; cosine LR schedule with 10% warmup; lr=1e-4. Per-epoch checkpoint + per-epoch parquet predictions persisted. Dual role per ADR-017: candidate detector in headline table AND diagnostic anchor in methodology spoke. Contamination state: **backbone-partial-disjoint** (fine-tuning disjoint by LODO; backbone pretrain corpus may overlap eval sources).

### 4.3 Rung 3 — *LoRA adapter-fine-tuned*
`[LOCKED: ModernBERT-base LoRA (per ADR-015 + ADR-019)]` — PEFT-LoRA adapters; backbone frozen; classifier head full-FT via `modules_to_save=["classifier"]`. **Locked recipe** (per ADR-019): `LoraConfig(r=8, lora_alpha=16, lora_dropout=0.1, target_modules=["Wqkv", "attn.Wo", "mlp.Wo", "mlp.Wi"], task_type="SEQ_CLS", bias="none")` — explicit module enumeration (4 LoRA modules per encoder × 22 layers = 88 adapter modules), not `"all-linear"` auto-detection. `TrainingArguments`: lr=1e-4, warmup_ratio=0.10, lr_scheduler_type=cosine, per_device_train_batch_size=16 + gradient_accumulation_steps=2 (effective batch 32; ADR-020 BATCH_TABLE scales for non-H100 classes), num_train_epochs=2, bf16=True, max_grad_norm=1.0, weight_decay=0.01, save_strategy="epoch", eval_strategy="no". `DataCollatorWithPadding(max_length=8192, pad_to_multiple_of=8)` — dynamic padding, head-truncation per ADR-014 Q4 training-time. Per-fold sklearn `class_weight='balanced'` via `WeightedTrainer`. Contamination state: **backbone-partial-disjoint**.

### 4.4 Rung 4 — *full-FT trained backbone*
`[LOCKED: ModernBERT-base full-FT (per ADR-015 + ADR-019)]` — Full backbone parameters trainable; standard HF Trainer + eval-toolkit metric callbacks + `WeightedTrainer` subclass for class-weighted CE. Same recipe as Rung 3 (lr=1e-4, 2 epochs, bf16, effective batch 32, etc.). Intermediate (epoch-1) weight checkpoints **not** persisted to disk (~1.8 GB throwaway across 12 runs); per-row predictions for epoch-1 are saved without the underlying weights since predictions are the audit-relevant artifact. Final epoch checkpoint is persisted per ADR-013 pre-teardown checklist. Contamination state: **backbone-partial-disjoint**.

### 4.5 Reference rungs — *4 published baselines at native config*
`[LOCKED: 4 reference rungs (per ADR-018 partially supersedes ADR-015)]` — Lakera Guard dropped (afterword extension); ProtectAI v1 + v2 both included for internal lift comparison.

- **R-LLM-OpenAI**: `gpt-4o-2024-08-06` (stable snapshot per ADR-018); temperature=0; one call per eval row; receives full sample (128K+ native context); prompt template at `src/judges/prompt_template_v1.md`. Contamination state: **vendor_black_box**.
- **R-LLM-Anthropic**: `claude-sonnet-4-6` (date-suffixed snapshot ID pinned at Phase 1 per Anthropic API docs); temperature=0; one call per eval row; receives full sample; same prompt template as OpenAI judge. Contamination state: **vendor_black_box**.
- **R-ProtectAI-v1**: `protectai/deberta-v3-base-prompt-injection` (HF revision SHA-pinned at Phase 1 per ADR-016 manifest); inference-only at native config (head-truncation at 512); bf16 on GPU. Contamination state: **suspected_contamination**.
- **R-ProtectAI-v2**: `protectai/deberta-v3-base-prompt-injection-v2` (HF revision SHA-pinned at Phase 1); inference-only at native config (head-truncation at 512); bf16 on GPU. Contamination state: **suspected_contamination**.

Each reference rung is called at its published native configuration including its native truncation policy. Apples-to-apples comparison against deployed baselines requires testing them as they exist, not as preprocessed by us. Training-data overlap audit per EVIDENCE.md §1-2. The methodology spoke includes a dedicated **Contamination stratification** subsection (per ADR-018) narrating the four-tier disclosure gradient (verified_disjoint → backbone-partial-disjoint → suspected_contamination → vendor_black_box); the trained-rung-vs-reference comparison is framed as "what trained-from-scratch (TF-IDF+LR fully-disjoint anchor) achieves versus what potentially-memorized off-the-shelf models achieve."

### 4.6 Per-epoch prediction-save discipline
`[LOCKED: epoch-2 headline, epoch-1 diagnostic (per ADR-019)]` — Per-row predictions persisted for every transformer (rung, seed, fold, epoch) combination → 72 transformer prediction parquets + 12 TF-IDF+LR (no-epoch) + 16 reference rungs = 100 total prediction files. File-path convention: `evals/predictions/<rung>__fold<F>__seed<S>__epoch<N>.parquet`. Discipline rule pre-committed: epoch-2 predictions are the publication number; epoch-1 predictions are reported as a diagnostic ablation in the methodology spoke (the per-(rung, seed, fold) epoch-1→epoch-2 AUPRC delta plot surfaces undertraining-vs-overfitting boundaries).

### 4.7 Matched-budget controls
`[LOCKED: per-axis (per ADR-018)]` — Match data (same train/eval splits per ADR-016) + eval methodology (same metrics, same statistical machinery per ADR-006); do NOT match training compute. Each rung uses its natural recipe; training compute is reported alongside the metric so AUPRC-vs-compute can be plotted as a Pareto frontier — the rung-ladder IS the Pareto frontier. Per-axis matching is the only framing that coherently handles the heterogeneous cost classes (LLM-judge $/call, trained rungs GPU-minutes, ProtectAI inference-only). Documented as a dedicated **Matched-budget framing** subsection in the methodology spoke.

### 4.8 Compute infrastructure (per ADR-020)
`[LOCKED: runpod-deploy 0.7.7 with 8-class GPU failover, dual-DC, adaptive batch, dual-layer cost cap]` —
- **`pod.gpu_order`** (priority): H100 80GB HBM3 → H100 NVL → H100 SXM → H100 PCIe → H200 → H200 NVL → A100-SXM4-80GB → A100 80GB PCIe → L40S → A100-SXM4-40GB (emergency)
- **`pod.datacenters`**: [US-MD-1, EU-RO-1] (dual-DC failover)
- **`BATCH_TABLE`** (preserves effective batch = 32 across GPU classes): H100/H200/A100-80G use (per_device=16, grad_accum=2); A100-40G/L40S use (8, 4); L40 uses (4, 8). Pre-locked lookup keyed on `torch.cuda.get_device_name`; fail-loud on unlisted GPU.
- **flash_attention_2 fallback** per runpod-deploy recipe: `try/except (ValueError, ImportError)` around model load → degrades to stock SDPA on smaller classes; `events.emit_event("flash_attn_fallback", ...)` for audit.
- **Cost cap (dual-layer)**: per-job `budget.cost_cap_usd=125.0` (orchestrator-enforced; = A-002 upper-bound soft cap) + project-wide hard cap $200 enforced by `scripts/cost_rollup.py` CI-gated check aggregating across all per-pod `runpod_deploy_pull_manifest.json` files + API call logs.
- **`assumed_hourly_rate_usd=3.50`** (H100 spot midpoint; reconciled post-first-run per cost-reconciliation recipe).
- **Preflight discipline**: `runpod-deploy validate --all` + `runpod-deploy run --dry-run` before any billed run.
- **Cost tracking** (dual-layer): per-pod automatic via `runpod_deploy_pull_manifest.json` + per-Makefile-target rollup in `evals/cost_ledger.csv` (cols: timestamp, target, est_cost_usd, actual_cost_usd, gpu_hours, api_calls, notes).

### 4.9 Future-work extensions (afterword)

`[LOCKED: NONE in primary slate; future-work extensions named per ADR-015 + ADR-017 + ADR-018 + ADR-019 alternatives]` — ModernBERT-large size-up, matched-context cross-backbone control, alternate classification head (MLP), calibration via validation-fit temperature, Lakera Guard re-addition (ToS-permitting), frontier-tier judge ablation (gpt-4.1 / opus-4-7), reasoning-judge ablation (o1/o3), multi-judge ensemble, rank ablation (r=4/r=16/r=32), target-module ablation (Q+V vs all-linear), DoRA / rs-LoRA / VeRA, 1-epoch-locked schedule comparison, 3-epoch convergence study, focal loss vs class-weighting, per-source learning-curve decomposition, hashing vectorizer for long docs, calibrated LR via CalibratedClassifierCV. Calibration is a separate methodology axis (Phase 0-04 walks the calibration battery, ledger row 343).

**Linked ADRs**: ADR-015 + ADR-017 + ADR-018 + ADR-019 + ADR-020 (compute + cost discipline).

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
