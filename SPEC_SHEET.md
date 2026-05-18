# Project specification (filled at end of Phase 0)

**Status**: `[LOCKED]` (Phase 0 closed at Phase 0-08 — every [OPEN] ledger row in SPEC_GREENFIELD locked to ADR-NNN; 39 ADRs accepted across Phase 0-00 through Phase 0-08; remaining `[OPEN]` text references in this doc are documentation about the spec lifecycle convention, not unresolved decisions)
**Type**: Single-version SDD spec; revisions tracked via ADRs (Michael Nygard format)

> **Role of this document.** SPEC_GREENFIELD.md is the authoritative pre-Phase-0 spec — it defines the contract and the open decisions. SPEC_SHEET.md is the post-Phase-0 fill-in form: same skeleton, but each `[OPEN]` row gets replaced with `[LOCKED: <chosen value>]` once Phase 0 resolves it. Phase 1 cannot begin until SPEC_SHEET.md has zero `[OPEN]` rows.

> **Companion docs**:
> - [`code_quality.md`](./code_quality.md) — implementation discipline
> - [`assumptions.md`](./assumptions.md) — registry of unverified assumptions
> - [`decisions/`](./decisions/) — ADR index + immutable decision records
> - [`EVIDENCE.md`](./EVIDENCE.md) — external-evidence audit trail

---

## Context

This submission targets the morning of 2026-05-18 (≈ 2.5 working days from Phase 0-00 start on 2026-05-15), with **Long-scope ambition refined by Phase 0-01 + Phase 0-03 + Phase 0-04 + Phase 0-05 + Phase 0-06 + Phase 0-07 + Phase 0-08 (and post-Phase-0-08 final audit per ADR-040 surfacing 7 backfilled assumptions A-010 through A-016)** (4-rung trained slate — TF-IDF + LR classical floor per ADR-017 + ModernBERT-base × {frozen-probe, LoRA, full-FT} per ADR-015 — plus 4 reference rungs at their published native configs — `gpt-4o-2024-08-06` + `claude-sonnet-4-6` + `protectai/deberta-v3-base-prompt-injection` (v1) + `protectai/deberta-v3-base-prompt-injection-v2` per ADR-018 partially supersedes ADR-015 reference slate (Lakera dropped, ProtectAI v1 added) — with 3-seed multi-seed protocol per ADR-006 floor formalized per ADR-022 paired-across-rungs implementation, full OOD slate aggregated per ADR-021 (pooled headline + per-slice spoke), paired-bootstrap apparatus per ADR-006 + ADR-022 with cross-fold CI via eval-toolkit `cv_clt_ci` (Bayle 2020) headline + block-bootstrap-on-folds spoke ablation per ADR-024, and calibration battery via raw + temperature + isotonic interventions per ADR-023) leveraging `runpod-deploy` 0.7.7 + `eval-toolkit` library infrastructure (per ADR-020 — 8-class GPU failover + dual-DC + adaptive batch + dual-layer cost cap; per ADR-022 joblib parallelization on 64-core Threadripper at orchestrator layer), and an explicit fallback ladder updated per ADR-015 (1×3 → 1×2 → 1×1 for transformer rungs; TF-IDF+LR classical floor retained across all fallbacks per ADR-017) that activates if mid-Phase-2 surfaces infeasibility (per ADR-001). The single-backbone refinement eliminates the per-backbone-truncation confound on the indirect-injection zero-shot OOD slice that the original 2-backbone framing would have produced (per ADR-014 Q3/Q4 walk). The full 8-rung slate is stratified along ADR-005's three-state contamination taxonomy (per ADR-018) — TF-IDF+LR verified_disjoint anchor + transformer rungs backbone-partial-disjoint + ProtectAI v1/v2 suspected_contamination + LLM judges vendor_black_box — making contamination disclosure a methodology axis rather than a footnote. Total: 48 trained runs (4 rungs × 3 seeds × 4 LODO folds; TF-IDF+LR runs are sklearn CPU, transformer runs are H100/equivalent bf16 with per-epoch prediction save) plus 100 prediction parquet files (84 trained + 16 reference) feeding cv_clt_ci on 12 per-(fold, seed) values per rung plus per-row paired-bootstrap on pooled rows. The deliverable is a public GitHub repo rendered as a Quarto-built static HTML site auto-published to GitHub Pages via a `quarto-actions/publish@v2` workflow (per ADR-030 supersedes ADR-002 — PDF removed; pandoc + LaTeX dependencies dropped). The site uses an `index.qmd` entry-point + Quarto sidebar nav declared in `_quarto.yml` to surface 8 spokes + decisions/ ADRs to a dual A1+A2 audience (hiring manager + ML researcher; per ADR-031 supersedes ADR-004 — A1+A2 + B4 + hub-and-spoke survive; hub artefact shifts from PDF to Quarto site). The submission is governed by three project-level methodology principles (ADR-005): methodology over metrics, honest evaluation preferred even when models look worse, and structured limitations with extension conditions.

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
- `[LOCKED: per ADR-005 + ADR-017]` Not picking a leader rung — each rung's trade-offs are characterized, no rung is promoted as the deployment recommendation. The rung-ladder IS the Pareto frontier (per ADR-005 methodology-over-metrics + ADR-017 trained-rung-slate-as-Pareto-instrument framing).
- `[LOCKED-via-omission]` No additional non-goals surfaced during Phase 0-00 through Phase 0-08; the three above + the rung-recommendation non-goal cover the project scope.

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
- [ ] Per-rung checkpoint persisted to HF Hub `[LOCKED: BBehring/prompt-injection-<rung-name> for the headline rungs only — frozen-probe + LoRA + conditionally full-FT + conditionally TF-IDF+LR — with model card discipline (license + tags + datasets + model-index + intended use + limitations + citation); reference scorers per ADR-018 NOT republished; per ADR-032]`

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
- [ ] Per-source / per-style breakdowns computed (LLM-as-rater rubric audit `[TBD-at-Phase-4]` — invest only if regex-based per-style tagger proves conservative enough to warrant audit; deferred per ADR-005 methodology + ADR-018 reference-scorer framing)
- [ ] Figures 1–7 (or the project's named slate) rendered to `docs/plots/`

Gate: every checkbox ticked; analysis JSON outputs match schemas.

### Phase 5: Writeup

- [ ] All WRITEUP sections drafted
- [ ] All  ADRs written and indexed in `decisions/README.md`
- [ ] Transcripts linked from WRITEUP appendix
- [ ] EVIDENCE.md populated for every external-evidence claim
- [ ] Quarto site published to GH Pages (per ADR-030); `_quarto.yml` + `index.qmd` + `.github/workflows/publish.yml` exist; `quarto render` succeeds locally and via the GH Actions workflow
- [ ] HF Hub model repos published per ADR-032 (headline rungs only with model card discipline)
- [ ] CHANGELOG.md committed per ADR-033 (Keep-a-Changelog 1.1.0 format); `v0.9.0-rc1` rehearsal tag fired (catches first-time-CI issues); `v1.0.0` submission tag created; GH release object carries CHANGELOG + `_site.tar.gz` asset
- [ ] `WRITEUP/reproducibility.md` spoke populated with T0+T1+T3 tier ladder per ADR-034
- [ ] All `[TBD: value]` / `[OPEN]` markers in submission templates resolved or justified

Gate: every checkbox ticked; reviewer URLs (source pin at `tree/v1.0.0` + live Quarto site + GH release page) all resolve; transcripts ready for private email attachment.

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

`[LOCKED: 5 OOD slices (per ADR-016) reported in two aggregation views (per ADR-021)]` — direct over-defense + over-refusal + mixed-direct + indirect zero-shot + agentic-stretch. HarmBench + Tensor Trust + LLMail-Inject deferred to afterword as named next-iteration extensions.

**Aggregation layout** (per ADR-021): **PDF executive headline table** carries a single pooled-OOD column per rung (concatenated rows across the 5 slices, single AUPRC + AUROC + recall@FPR + ECE + Brier per rung). **Methodology spoke** at `WRITEUP/ood-analysis.md` (new file) carries the 5-by-rung per-slice grid with per-slice bootstrap CIs computed on the same persisted predictions via paired-bootstrap apparatus per ADR-006 + ADR-022 — no extra compute beyond additional metric calls. Pooled-and-per-slice reporting applies ADR-004 hub-and-spoke framing to OOD: pooled for A1 (hiring manager exec scan); per-slice for A2 (ML researcher generalization-question-by-question read). Aligns with Demsar 2006 JMLR multi-dataset reporting guidance.

| Slice | Source | Role | Why |
|---|---|---|---|
| NotInject | `leolee99/NotInject` | Hard-negative (benign-with-injection-triggers) | Tests over-defense per InjecGuard 2024 methodology; explicitly invites worse-but-honest evaluation per ADR-005 Principle 2 |
| XSTest | `paul-rottger/xstest` | Hard-negative (over-refusal) | Tests exaggerated-safety patterns per Röttger 2024 NAACL |
| JBB-Behaviors | `JailbreakBench/JBB-Behaviors` | Mixed (100 harmful + 100 benign) | Standardized misuse-behavior evaluation per Chao 2024 NeurIPS D&B |
| BIPIA | `microsoft/BIPIA` | Indirect (zero-shot OOD per ADR-014 Q1) | Indirect-injection benchmark per Yi 2023 KDD; the load-bearing zero-shot transfer measurement |
| InjecAgent | `uiuc-kang-lab/InjecAgent` | Agentic (stretch probe) | Tool-integrated agent injection per Zhan 2024 ACL; agentic transfer-of-transfer caveat per ADR-010 Bound 2 |

**Linked ADRs**: ADR-014 (threat-model bundle — attack-class scope), ADR-015 (rung architecture — 3 ModernBERT-base trained + 4 reference rungs), ADR-016 (this — data design bundle), ADR-008 (data scope brief-level locks — preserved), ADR-041 (Phase 1 implementation bundle — manifest rich-schema + live-fetch SHA pinning + manifest_validation.py placement + loader dispatch + stratified-cosine-band dedup holdout + slate-plus-templates contamination corpus + per-fold parquet materialization).

### 3.5 Phase 1 implementation status

`[Phase 1 in progress per ADR-041]` Operationalization of §3.1–3.4 locks. Per-commit status:

| Phase 1 commit | Deliverable | Invariant test | Status |
|---|---|---|---|
| Commit 1 | `configs/data/source_manifest.yaml` (live-fetched SHAs; rich schema; bump_history=[]; relocated from `data/` per ADR-044 Q2) + `src/data/manifest_validation.py` + `scripts/pin_source_manifest.py` | `test_source_manifest_schema_valid` | **green** |
| Commit 2 | `src/data/loaders.py` (HF dispatch + 11 normalizers) + `tests/smoke/test_loaders_smoke.py` (3 small HF sources) | smoke tests | **green** (3 smoke + dispatch unit) |
| Commit 3 | `src/data/dedup.py` + `scripts/build_dedup_holdout.py` + `scripts/calibrate_dedup.py` + 4 smoke tests; preliminary `evals/dedup_calibration.json` via ADR-042 LLM-pre-label bootstrap (gpt-4o-2024-08-06; full 4-source coverage; FPR=0.00 FNR=0.33 at locked 0.80; FPR jumps to 0.063 at 0.75 — 0.80 lock at the precision-recall knee) | `test_dedup_calibration_persisted` **green** | **green**; `human_verified_pct=0` pending Brandon's hand-examination per ADR-042 |
| Commit 4 | `src/data/splits.py` (LODO k=4 x 3 seeds x stratified 80/20) + `materialize_splits` + `materialize_index_masks` + 9 smoke tests | `test_class_balance_per_fold` + `test_source_disjoint_train_test` (unskip in Commit 5 with real data) | **green** |
| Commit 5 | `src/data/audit.py` + `src/data/templates.py` + `scripts/extract_hackaprompt_templates.py` + `scripts/run_data_pipeline.py` end-to-end orchestrator + ADR-043 post-split leakage cleanup; `evals/{data_audit,leakage_report,contamination_scan}.json` materialized (4707 deduped positives + 17246 deduped benigns + 1101 OOD; 180 leaked train rows dropped via ADR-043; A-005 triggers 1+2 clean; leakage_clean=True) | `test_benign_contamination_scan_clean` + `test_class_balance_per_fold` + `test_source_disjoint_train_test` all **green** | **green** (5 invariants total) |
| Commit 6 | `Makefile` Phase 1 targets (`data-pin-manifest`, `data-prepare` umbrella, `data-fetch`/`data-dedup`/`data-splits`/`data-audit` ADR-041-Q7-compat aliases, `data-templates`, `data-dedup-{holdout,prelabel,calibrate}`) + `docs/ROADMAP.md` Phase 1 close note + SUBMISSION_AUDIT regen + transcript checkpoint + push | n/a | **green** |

#### 3.5.1 Phase 1 library-first carryforward refactor (per ADR-047)

`[Phase 1 carryforward refactor in progress per ADR-047]` Triggered by Phase 4 entry walkthrough Q6 user reaffirmation of the library-first invariant as project-wide; retroactive audit identified 4 hand-rolls in `src/data/` where `eval-toolkit` ships fitting primitives. Two upstream contributions filed at audit close: issue [#18](https://github.com/brandon-behring/eval-toolkit/issues/18) (wire 50-pair golden dedup-holdout into eval-toolkit CI fixtures); issue [#19](https://github.com/brandon-behring/eval-toolkit/issues/19) (3-pattern cookbook docs). Each refactor commit deletes orphaned local helpers in-commit per the no-orphaned-code discipline (saved as memory 2026-05-16).

| Refactor commit | Deliverable | Invariants verified | Status |
|---|---|---|---|
| Commit 1 (ADR-047 setup) | ADR-047 + SPEC_SHEET §3.5.1 + upstream issues #18 + #19 filed + `decisions/upstream_issues.md` ledger updated + SUBMISSION_AUDIT regen | n/a | **pending commit** |
| Commit 2 (splits refactor) | `src/data/splits.py::make_splits` consumes `eval_toolkit.splits.SourceDisjointKFoldSplitter`; project glue maps upstream-shuffled fold order back to TRAIN_POSITIVE_SOURCES tuple order (deterministic fold_id-to-source mapping preserved across refactor); per-seed stratified 80/20 train/val + benigns-in-every-train-pool preserved | 9 splits smoke tests + 5 invariants (`test_class_balance_per_fold` + `test_source_disjoint_train_test` + ...) all pass | **green** |
| Commit 3 (dedup refactor) | `src/data/dedup.py::{dedup_within_source, drop_train_test_leakage, dedup_cross_source_benigns}` consume `eval_toolkit.text_dedup.{near_dedup, EmbeddingCosineStrategy(embedder=compute_embeddings), EmbeddingCosineStrategy.pairs_across}`; `_greedy_first_occurrence_mask` deleted in-commit (no remaining callers); `pairwise_cosines` retained pending Commit 4 (still has callers in `audit.py` + `build_dedup_holdout.py` + test); project-owned embedder glue (`get_encoder` + `compute_embeddings` + `encoder_revision_sha`) preserved; `compute_embeddings` signature broadened from `list[str]` to `Sequence[str]` for upstream `Callable[[Sequence[str]], ndarray]` Protocol compat (non-breaking — all callers pass list) | 4 dedup smoke tests pass (including `test_dedup_cross_source_lmsys_priority` priority-source reason preservation); 123/123 smoke total + 10 invariants pass; mypy + ruff green | **green** |
| Commit 4 (audit refactor + close) | `src/data/audit.py::compute_leakage_report` consumes `run_leakage_checks([CrossSplitLeakageCheck])` per fold (ExactDuplicateCheck + NearDuplicateCheck dropped per implementation note — they would always report zero findings post-`dedup_within_source`); `compute_contamination_scan` consumes `EmbeddingCosineStrategy.pairs_across(query, reference, k=1)` + project per-source aggregation glue; project-dict output schemas preserved for both. `_per_row_max_cosine_to_ref` (audit.py local helper) deleted in-commit. `pairwise_cosines` (dedup.py) deleted in-commit (now truly orphaned after audit.py + `build_dedup_holdout.py` refactors away from it). `test_pairwise_cosines_symmetric` (tested deleted primitive) deleted in-commit. `scripts/build_dedup_holdout.py::_enumerate_within_source_pairs` refactored to use `EmbeddingCosineStrategy.pairs_within(texts, n-1)` so the script's `pairwise_cosines` import dependency is severed. Output schema for `evals/leakage_report.json` preserved (CrossSplitLeakageCheck count maps to existing `cosine_ge_085_overlaps` field) — no schema migration needed | 6 audit+dedup smoke tests pass (test_compute_data_audit_yields_per_source_counts + test_compute_leakage_report_zero_overlaps_on_disjoint_splits + test_compute_contamination_scan_unrelated_benigns_clean + test_compute_embeddings_shape_and_norm + test_dedup_within_source_drops_near_duplicates + test_dedup_cross_source_lmsys_priority); 122/122 smoke total (was 123; -1 from deleted test_pairwise_cosines_symmetric) + 10 invariants pass; mypy + ruff green | **green** |

**Phase 1 library-first carryforward refactor CLOSED at Commit 4.** ADR-046 (Phase 4 implementation bundle per prior 7-question ratification) writing unblocked; Phase 4 Commit 1 begins after ADR-046 lands.

### 3.6 Phase 2 implementation status

`[Phase 2 in progress per ADR-044]` Operationalization of §4 locks. Per-commit status:

| Phase 2 commit | Deliverable | Invariant test | Status |
|---|---|---|---|
| Commit 1 | ADR-044 (Phase 2 implementation bundle; partial supersession of ADR-019 seed slate `(42,1337,2025)→(42,43,44)`) + manifest move `data/`→`configs/data/` per Q2 + 10-file path-ref update | `test_source_manifest_schema_valid` (still green at new path) | **green** |
| Commit 2 | `src/training/{batch_table, lora_config, training_args, weighted_trainer, load_modernbert, softmax_cast}.py` per ADR-019 + ADR-020 + 18 smoke tests | `test_flash_attn_fallback_present` + `test_effective_batch_constant_across_gpu_classes` **green** | **green** (7 invariants total) |
| Commit 3 | `src/training/{tfidf_lr, train_classical}.py` per ADR-017 + `configs/rungs/classical_floor.yaml` + `scripts/train_classical_floor.py` + 5 smoke tests | `test_classical_floor_rung_present` **green** | **green** (8 invariants total) |
| Commit 4 | `src/training/train_modernbert.py` multi-rung HF Trainer dispatch (frozen_probe + lora + full_ft via classifier_type) + `configs/rungs/{frozen_probe, lora, full_ft}.yaml` (ModernBERT-base SHA pinned at `8949b909`) + `PerEpochPredictionsCallback` per ADR-019 + 10 smoke tests | `test_per_epoch_predictions_present` (deferred to canonical run; needs GPU) | **green** (8 invariants total; per-epoch invariant deferred) |
| Commit 5 | `configs/runpod/headline-{frozen_probe, lora, full_ft}.yaml` (runpod-deploy schema_version 2 — H100/H200/A100/L40S failover; cost caps $40/$60/$100) + `scripts/train_rung.py` per-rung sweep + `scripts/cost_rollup.py` aggregator + 8 smoke tests | n/a (cloud runs at canonical) | **green** (code lands; runs deferred to canonical) |
| Commit 6 | `tests/fixtures/processed/fold-0/seed-42/*.parquet` (100/24/24 rows; 12KB total; reproducible via `scripts/generate_fixtures.py` at seed=1337) + `configs/profiles/classical_fixtures.yaml` + `tests/smoke/test_smoke_pipeline.py` (3 tests; fixture-pipeline + idempotency) + `Makefile` Phase 2 targets (`generate-fixtures`, `train-classical-floor`, `train-rung RUNG=<...>`, `cost-rollup`, `cost-rollup-check`, `headline-{frozen-probe,lora,full-ft}`) + `make smoke` extended to fixture-pipeline pass per ADR-027 line 75 + `docs/ROADMAP.md` Phase 2 close note | n/a | **green** |

### 3.7 Phase 3 implementation status

`[Phase 3 in progress per ADR-045]` Operationalization of §5 locks. Per-commit status:

| Phase 3 commit | Deliverable | Invariant test | Status |
|---|---|---|---|
| Commit 1 | ADR-045 (Phase 3 implementation bundle; scoring-first contract + 6-commit cadence + tiered ref-scorers + classical-scaffold + full-pairwise persistence with headline-only WRITEUP + pydantic schema validation) + SPEC_SHEET §3.7 status table + SUBMISSION_AUDIT regen | n/a | **in progress** |
| Commit 2 | `src/scoring/{protectai, llm_judge_base, openai_judge, anthropic_judge}.py` per ADR-018 + `src/eval/schemas.py` (pydantic models — PredictionsRowModel, MetricsRecordModel, SliceMetricsModel, OperatingPointModel, CalibrationRecordModel, ReachabilityAuditModel, BootstrapCellModel) + versioned prompt template at `src/scoring/prompts/prompt_template_v1.md` + Tier-A (ProtectAI) CI smoke + Tier-B (LLM judges) cache infrastructure at `evals/audit/llm_judge_cache/<judge>__<sha256-prefix>.json` per A-007 + A-014 + 22 smoke tests | `test_reference_scorer_schema_uniform` **green** | **green** (9 invariants total) |
| Commit 3 | `src/eval/calibration_battery.py` per ADR-023 (eval-toolkit ECE 4-variant matrix `expected_calibration_error{,_debiased,_l2,_l2_debiased}` + `expected_calibration_error_equal_mass` headline at n_bins=15 + `brier_score` + `brier_decomposition` reliability/resolution/uncertainty + `fit_temperature` + `fit_isotonic_calibrator` + `reliability_curve`; validation-only fit per ADR-011 Guarantee 6; `proba_to_logprobs` + `apply_temperature` helpers for binary-to-2-col-logit conversion) + 12 smoke tests | `test_calibration_battery_outputs_4ece_plus_brier` **green** | **green** (10 invariants total) |
| Commit 4 | `src/eval/operating_points.py` per ADR-025 (TargetFPRSelector(0.01) detection + TargetRecallSelector(0.99) verification per-(rung, fold, seed) val fit; `fit_operating_point` + `fit_dual_policy_for_cell` + `compute_reachability_audit` per A-009) + `src/eval/slice_analysis.py` per ADR-021 (5-slice OOD slate `compute_metric_record` + pooled-headline `compute_pooled_ood_record` + per-slice spoke `aggregate_slice_across_observations` + 0.1% pinpoint volatility surfaces `compute_pinpoint_volatility` per ADR-021 line 53-65) + 20 smoke tests | module-level smoke tests cover contract (`test_dual_policy_threshold_pairing` + `test_verification_reachability_audit` + `test_ood_aggregation_layout` + `test_recall_at_fpr_pinpoint_volatility` are integration-level invariants deferred to Commit 5 when scripts wire end-to-end) | **green** (10 invariants total; 4 stubs deferred to Commit 5) |
| Commit 5 | `scripts/run_metrics_battery.py` (loads predictions parquets per rung × fold × seed × slice; emits `MetricsRecordModel` + pooled-OOD records via `src/eval/slice_analysis.py`) + `scripts/fit_dual_policy_thresholds.py` (sweeps trained-rung × fold × seed; reference scorers filtered via `TRAINED_RUNGS` allowlist per SPEC §4; emits `OperatingPointModel` + `ReachabilityAuditModel` nested-JSON per A-009) + `scripts/run_bootstrap_battery.py` (full-pairwise C(rungs, 2) × slices × metrics via `eval_toolkit.bootstrap.paired_bootstrap_diff`; persists `BootstrapCellModel` per Q6 user refinement so post-hoc questions answer from disk; WRITEUP features the 3 headline comparisons) + `scripts/eval_from_hub.py` T0-tier dry-run surface per ADR-034 (full body gated on Phase 5 ADR-032 publication) + 5 subprocess-based smoke tests covering all 4 entrypoints | smoke covers contract; integration invariants (`test_dual_policy_threshold_pairing` + `test_verification_reachability_audit` + `test_ood_aggregation_layout` + `test_recall_at_fpr_pinpoint_volatility` + `test_bootstrap_n_and_stability_check` + `test_paired_across_rungs_pairing` + `test_cross_fold_ci_methodology`) remain skip-marked pending Phase 4 canonical evals run on full 84-parquet trained-rung output | **green** (10 invariants total; 7 integration stubs deferred to Phase 4) |
| Commit 6 | Makefile Phase 3 targets (`eval-classical-floor`, `eval-reference-scorers-free` Tier-A scaffold, `eval-reference-scorers-paid` Tier-B with interactive approval per ADR-045 Q4, `metrics-battery`, `dual-policy-thresholds`, `bootstrap-battery`, `eval-from-hub` Phase-3-wired) + `make smoke` extension (now includes `run_metrics_battery.py` end-to-end pass on classical-floor fixture predictions + `eval_from_hub.py --dry-run` per ADR-027 sub-10-min budget) + `tests/fixtures/metrics/` gitignored + `docs/ROADMAP.md` Phase 3 close note + Phase 4 unblock | n/a | **green** |

### 3.8 Phase 4 implementation status

`[Phase 4 in progress per ADR-046]` Operationalization of §5 plus ADR-006 + ADR-022 + ADR-024 + ADR-025 (plus partial supersession of ROADMAP `[TBD-at-Phase-4]` reference-scorer-audit-deferred framing per ADR-046 Q5 user override → include-now-locked). Per-commit status:

| Phase 4 commit | Deliverable | Invariant test | Status |
|---|---|---|---|
| Commit 1 | ADR-046 (Phase 4 implementation bundle; 6-commit cadence + scaffold-with-classical + always-emit-both-CIs auto-flag + MDE-on-every-emitted-CI + LLM-rater audit included per user override + library-first hybrid figures per project-wide invariant codification + Phase 5 prep deferred) + SPEC_SHEET §3.8 status table + SUBMISSION_AUDIT regen | n/a | **green** |
| Commit 2 | `src/eval/marginal_bootstrap.py` per ADR-022 (bootstrap_ci wrappers; 10K @ seed=1 headline + 10K @ seed=2 stability check) + `src/eval/cross_fold_ci.py` (cv_clt_ci headline per ADR-024; block-bootstrap spoke fields scaffolded as None pending Commit 3) + `src/eval/mde.py` per ADR-006 (mde_from_paired_ci_record direct wrap + mde_from_marginal_ci_record closed-form workaround per upstream issue #20) + 3 new pydantic schemas (MarginalBootstrapCellModel + CrossFoldCIModel + MDECellModel) + 18 smoke tests | `test_marginal_bootstrap_seed_stability` + `test_cv_clt_ci_headline_present` (deferred-unskip at canonical evals run; 44 total tests collect cleanly) | **green** |
| Commit 3 | `src/eval/cross_fold_ci.py` extension — `compute_block_bootstrap_on_folds` (inline NumPy workaround per upstream issue #21; vectorized resample of K folds with replacement; percentile CI per ADR-022) + `compute_a_008_flag` (strict `> 1.5` per A_008_RATIO_THRESHOLD; degenerate-cv_clt edge case handled) + `compute_cross_fold_ci_cell` always populates both cv_clt + block fields + the boolean flag; 10 new smoke tests cover halfwidth ordering + seed determinism + flag rule + threshold constant | `test_block_bootstrap_folds_spoke_present` + `test_a_008_flag_fired_when_ratio_exceeds_1_5` (deferred-unskip at canonical evals run; 46 total tests collect) | **green** |
| Commit 4 | `src/eval/figures.py` per Q6 — library-first hybrid 7-figure slate; consumes `eval_toolkit.plotting.{plot_pr_curve, plot_reliability_diagram, plot_bootstrap_distribution, plot_lift_ci, save_figure, set_plot_style, PALETTE}` for F3 + F4 + F6-right + F7-subpanels + project glue for F1 Pareto + F2 ROC + F5 heatmap + F6-left + F7 grid layout (cites upstream issues #14 + #15 + #16 + new #22 `plot_metric_bars ax kwarg` for F6-left as TODOs); SVG output via `save_figure` writes a `{stem}.meta.json` sidecar carrying provenance per ADR-030; 14 smoke tests pass headless via `matplotlib.use("Agg")`; matplotlib graduated to main deps from notebook extras | `test_figures_slate_7_svgs_present` + `test_save_figure_provenance_chunks_present` (deferred-unskip when Commit 5 orchestrates the canonical slate; 48 total tests collect) | **green** |
| Commit 5 | Orchestration scripts — `scripts/run_marginal_bootstrap.py` per Q4 (sweeps marginal cells x both seeds per ADR-022) + `scripts/run_cv_clt_ci.py` per Q3 (sweeps both cv_clt + block fields + a_008 flag) + `scripts/run_mde.py` per Q4 (aggregates MDE across paired + marginal + cv_clt + block cells via closed-form path; emits `evals/audit/mde_per_cell.parquet`) + `scripts/render_figures.py` per Q6 (canonical + scaffold paths; emits `docs/plots/F{1..7}.svg` + per-figure `.meta.json` provenance sidecars) + `scripts/audit_reference_scorers.py` per Q5 user override (samples disagreement pairs vs trained rung, interactive approval gate per ADR-020 + `--dry-run` cost preview + `--assume-yes` for CI; uses OpenAIJudge from Phase 3 Commit 2 with locked OPENAI_JUDGE_MODEL per ADR-018) + 5 subprocess-based smoke tests | smoke covers contract; canonical-data invariants deferred to operator-gated runs | **green** |
| Commit 6 | Makefile Phase 4 targets (`marginal-bootstrap`, `cv-clt-ci`, `mde-battery`, `render-figures`, `audit-reference-scorers`, `phase4-all` umbrella) + extended `make smoke` (now also runs `scripts/render_figures.py --scaffold` writing 7 SVG + sidecars to `tests/fixtures/plots/`; under ADR-027 sub-10-min budget) + `tests/fixtures/plots/` gitignored + `docs/ROADMAP.md` Phase 4 status + close note + 6-step `v0.9.0-rc1` rehearsal-tag dispatch checklist per ADR-033 + Phase 5 (Writeup) unblock | n/a | **green** |

After Commit 6 lands + invariants pass, **v0.9.0-rc1 rehearsal tag fires** triggering the full publish pipeline (Quarto site build per ADR-030 + GH Pages deploy + HF Hub model card pushes per ADR-032) as a 24+ hour dress-rehearsal per ADR-033 + ADR-038. Phase 5 (Writeup) begins after.

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

`[LOCKED: PR-AUC + ROC-AUC + recall@FPR={0.1pct-pooled-only, 1pct, 5pct} + ECE-equal-mass(n_bins=15, quantile) + Brier on raw scores per rung (per ADR-021 + ADR-023)]`. All reported with bootstrap CIs per ADR-022 + ADR-024 (cv_clt_ci on 12 (fold, seed) per-rung values for rank-based metrics; pool-rows-and-compute-once for per-row metrics; 10K @ seed=1 + 10K @ seed=2 stability check; >5% half-width flag).

**Dual-policy operating-point columns** (per ADR-025) — trained rungs only — gain one new headline column **"FPR @ recall ≥ 99%"** (verification policy operating point via `TargetRecallSelector(0.99)` on val); the existing **R@FPR=1%** column carries a footnote tagging it as the **detection policy** operating point via `TargetFPRSelector(0.01)` on val. Headline footprint per trained rung settles at: AUPRC | AUROC | R@FPR=0.1%* | R@FPR=1%† | R@FPR=5% | FPR@R≥99%† | ECE | Brier (* = ADR-021 0.1%-pooled-only volatility flag; † = dual-policy operating points). Reference rungs receive blank cells in the verification column with footnote pointing to the SPEC §4 dual-policy applicability lock (only trained rungs get dual-policy framing; reference scorers report recall@FPR pinpoints only with contamination caveats per ADR-018).

**Recall@FPR pinpoint volatility surfacing** (per ADR-021) — for the 0.1% pinpoint at pooled level: half-width column alongside point estimate; flag marker when half-width > 0.5 × point estimate; resample-degeneracy fraction emitted to `evals/audit/per_rung_audit.json`; per-resample threshold-drift dump to `evals/audit/pinpoint_threshold_drift.json`; methodology spoke explains why 0.1% reports wider CIs and is not computable per-slice. The 0.1% pinpoint is reported only at the pooled aggregation level (pooled n_neg ≈ 16-20K yielding 16-20 FPs at threshold); at per-slice or per-LODO-fold aggregation it is reported as "not computable at this aggregation level (n_neg too small)".

**Calibration battery composition** (per ADR-023) — **Headline**: ECE-equal-mass(n_bins=15, quantile binning) + Brier on raw scores per rung. **Spoke** (`WRITEUP/calibration.md`): all 4 ECE variants from eval-toolkit (L1/L2 × plug-in/debiased) + Brier decomposition (refinement / reliability / uncertainty) + reliability diagrams (equal-mass quantile) + intervention deltas — temperature scaling (Guo 2017 1-parameter) + isotonic regression (non-parametric monotonic remapping); both calibrators fit on validation only per-(rung, fold, seed) per ADR-011 Guarantee 6; calibration interventions are monotonic and therefore do NOT change rank-based headline metrics (PR-AUC, ROC-AUC, recall@FPR).

### 5.2 Statistical tests

**Stance**: report effect sizes and CIs only. No p-values. The work characterises differences and their uncertainty rather than claiming significance.

Anchored to [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) primitives:

- `bootstrap_ci` — per-metric finite-sample uncertainty. See [methodology/bootstrap.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/bootstrap.md).
- `paired_bootstrap_diff` — paired comparisons across rungs on the same test set. See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md).
- `mde_from_ci` — minimum detectable effect.
- Calibration battery (`reliability_curve`, `fit_temperature`, `fit_isotonic_calibrator`, ECE variants, Brier). See [methodology/calibration.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/calibration.md).
- `cv_clt_ci` — CLT-based CI for cross-fold variance.

**Cross-fold CI methodology**: `[LOCKED: cv_clt_ci (Bayle 2020 Annals of Statistics Theorem 3.1 implementation at eval-toolkit src/eval_toolkit/bootstrap.py:963) headline + block-bootstrap-on-folds spoke ablation + conditional stratified-k-fold-within-LODO escalation if Phase 4 compute budget permits (per ADR-024)]`. `cv_clt_ci` operates on the 12 per-(fold, seed) metric values yielded by ADR-022's compute-per-(fold, seed)-then-aggregate rule for rank-based metrics. Block-bootstrap-on-folds spoke ablation directly addresses the LODO non-exchangeability concern (folds are not exchangeable — each fold holds out a different positive source with different size and attack-style character). **Sensitivity-check flag**: if `block_bootstrap_CI_halfwidth / cv_clt_CI_halfwidth > 1.5` for any rung, methodology spoke names "LODO non-exchangeability dominates within-fold variance; headline CI may understate uncertainty" (assumption A-008). Bates 2024 JASA nested-CV + Nadeau-Bengio 2003 standalone correction explicitly deferred to afterword.

**Paired-test method**: `[LOCKED: eval-toolkit paired_bootstrap_diff (Efron-Tibshirani 1993 §10.3 row-level pairing) per ADR-022; DeLong + McNemar + Cochran-Q rejected at the row level with multi-source-LODO-specific rationale (DeLong's asymptotic Gaussian assumption breaks at per-fold n ≈ 4-5K benigns; designed for AUROC only; produces p-value contradicting estimation-over-testing; LODO fold-blocking violates iid assumption)]`.

**Multi-seed protocol** (per ADR-022 + ADR-006 + ADR-016): `[LOCKED: 3 seeds {42, 1337, 2025} paired across rungs; trained rungs 12 obs per rung (4 LODO folds × 3 seeds); reference rungs 4 obs per rung (4 folds × no seed dimension); trained-vs-trained pairing is row-level via paired_bootstrap_diff; trained-vs-reference pairing replicates reference scores across the 12 trained seeds (reference-side variance fold-only); rank-based metrics per-(fold, seed)-then-mean; per-row metrics pool rows across (fold, seed); recall@FPR thresholds per-(seed) from val; calibration interventions per-(rung, fold, seed); per-(rung, fold, seed) observations dumped to evals/audit/per_seed_observations.parquet per ADR-011 Guarantee 5]`.

**Multi-comparison correction** (per ADR-022 + ADR-006): `[LOCKED: no formal correction applied; methodology spoke at WRITEUP/methodology.md gains "Family of comparisons" acknowledgment paragraph citing Gelman & Loken 2014 forking-paths + ASA 2016 statement on p-values]`. Estimation-over-testing means correction does not apply (correction applies to significance-testing; we report effect sizes).

### 5.3 Operating points — detection vs verification

`[LOCKED]` Dual-policy framing on **in-house rungs only**. Reference scorers (off-the-shelf reference detectors) get recall@FPR pinpoints with explicit contamination caveats; no dual-policy framing (would imply deployment-ready operating points that don't survive the contamination caveat).

`[LOCKED: Detection — FPR ≤ 1% via eval_toolkit.TargetFPRSelector(0.01); Verification — FNR ≤ 1% (equivalently recall ≥ 99%) via eval_toolkit.TargetRecallSelector(0.99); per-(rung, fold, seed) fitting on validation only; 24 thresholds per trained rung × 4 trained rungs = 96 threshold-pair instances; paired_bootstrap_op_point_diff two-level bootstrap (refit per resample) for CI propagation; cost-weighted thresholding remains rejected per ADR-006 (no CostSensitiveSelector use); per ADR-025]`.

**Headline integration**: detection-policy operating point coincides numerically with the recall@FPR=1% headline pinpoint already locked in ADR-021 — captured as a footnote on the existing R@FPR=1% column. Verification-policy operating point gains one new headline column "FPR @ recall ≥ 99%" per trained rung (see §5.1).

**Spoke**: full dual-policy operating-point grid (4 trained rungs × 2 policies × {pooled-IID + pooled-OOD + 4 per-LODO-fold + 5 per-OOD-slice} aggregation levels = 80 cells per policy with paired_bootstrap_op_point_diff CIs) + **Verification-target reachability across trained rungs** subsection (per assumption A-009; honest infeasibility reporting via asterisk + audit JSON `evals/audit/verification_reachability.json`) + ≥3 deployment scenarios per ADR-006 + optional **Recall-floor sensitivity sweep** afterword regenerating verification operating points at recall floors {95%, 99%, 99.9%} from persisted predictions per ADR-013 (zero new training compute) — all in `WRITEUP/threshold-policy.md`. See [methodology/thresholds.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/thresholds.md) for the eval-toolkit primitive surface.

### 5.4 Per-source and per-style breakdowns

Required for any OOD claim — aggregate metrics hide heterogeneity. Reported alongside the headline IID/OOD numbers. Per-style heuristic tagger regex-based) is conservative;  may `[TBD: (candidate) invest in LLM-as-rater rubric audit]`.

### 5.5 Adversarial robustness

`[TBD: largely deferred; named but not exhaustively probed]` — the threat model (paraphrase, encoded payloads, multi-turn injection, base64/leetspeak obfuscation) is named; what was not tested is named explicitly in WRITEUP §5.6 and §8.

**Linked ADRs**: ADR-021 (eval slate aggregation + recall@FPR pinpoints), ADR-022 (statistical inference apparatus — bootstrap N + multi-comparison + multi-seed + paired-test), ADR-023 (calibration battery — raw + temperature + isotonic), ADR-024 (cross-fold CI methodology — cv_clt_ci headline + block-bootstrap-on-folds spoke), ADR-025 (dual-policy threshold characterization — symmetric 1% targets + per-(rung, fold, seed) fitting + verification-reachability audit).

---

## 6. Code architecture

The work spans three repos:

- **`prompt-injection-detection-prototype`** (this repo) — modelling: data loading, training, classification API, project-specific scoring code.
- **[`eval-toolkit`](https://github.com/brandon-behring/eval-toolkit)** — evaluation harness: metrics, bootstrap, calibration, threshold selection, leakage detection, slice-aware orchestration, reproducibility manifests, versioned JSON schemas.
- **[`runpod-deploy`](https://github.com/brandon-behring/runpod-deploy)** — cloud orchestration for training/eval runs on rented GPUs. **the project's additions**: prediction-persistence pull-pattern + checkpoint upload-to-HF-Hub pattern.

The split is intentional: methodology curriculum and primitives live in `eval-toolkit` so they survive across iterations; cloud orchestration lives in `runpod-deploy` so it's reusable across projects.

### 6.1 Module layout (per ADR-026)

`[LOCKED: concern-grouped sub-packages under src/]`

```
src/
  data/        # loaders, dedup, LODO splits, manifest validation
  training/    # ModernBERT loader, LoRA configurator, trainer
  scoring/     # reference-scorer adapters (one module per scorer)
  eval/        # calibration_battery, operating_points, slice_analysis
  utils/       # config_hash, paths, logging glue
scripts/       # CLI entrypoints — argparse + IO; orchestrate src/ calls
configs/
  runpod/      # canonical RunPod config per ADR-020
  rungs/       # per-rung YAML hyperparameters per SPEC §5 config discipline
  profiles/    # smoke vs canonical profile configs per ADR-027
  data/        # source manifest with HF SHAs per ADR-016
tests/
  conftest.py  # marker registration + shared fixtures
  test_invariants.py  # 25+ tests-as-invariants per SPEC §5
  fixtures/    # smoke-test fixture data (NOT real data)
  unit/        # pytest -m unit
  smoke/       # pytest -m smoke
  integration/ # pytest -m integration
```

Boundaries — `src/` is library code (importable, no side effects); `scripts/` is entrypoint glue (argparse + IO; not importable); `configs/` is YAML data; `tests/` is verification. Adding or moving a top-level `src/` sub-package requires a superseding ADR.

### 6.2 Smoke vs canonical separation (per ADR-027)

`[LOCKED: three Makefile targets stratified by execution context]`

| Target | Execution context | Compute | Network | Wall-clock | Purpose |
|---|---|---|---|---|---|
| `make smoke` | laptop only | no GPU | no network | <10 min | dev debugging + reviewer "does this wire together" check |
| `make test-integration` | local GPU OR cloud pod | GPU when available; skip gracefully when not | optional | ~5-10 min | dev debugging on workstation GPU; pre-flight smoke on cloud pod |
| `make headline-cloud` | RunPod (billed) | H100/equivalent per ADR-020 gpu_order failover | required | hours; cost-cap-gated $125/job per ADR-020 + A-002 | **canonical evaluation deliverable** — not a test |

**Honest framing** (required in `WRITEUP/methodology.md`): math-correctness validation lives upstream in `eval-toolkit` (≥90% coverage floor, Hypothesis property tests, golden-output snapshots, doctests on math kernels). The local test layer in this prototype repo is debugging-grade — sufficient to catch glue-layer breakage before paying for cloud compute, not sufficient to substitute for upstream library validation. Reviewers consult eval-toolkit's test suite for math-correctness evidence.

A separate `make headline-dry-run` target exposes `runpod-deploy run --dry-run` standalone for cost preview without provisioning.

### 6.3 Linked ADRs

ADR-026 (module layout), ADR-027 (smoke vs canonical), ADR-028 (coverage floor), ADR-029 (test marker strategy).

---

## 7. Verification & acceptance criteria

### 6-gate integration checklist for `v1.0.0` submission tag (per ADR-039)

This iteration is submission-ready when all six gates pass:

1. **Zero `[OPEN]` in `SPEC_SHEET.md`** — every slot reads `[LOCKED: ... (per ADR-NNN)]` OR `[TBD-at-Phase-N]` with explicit rationale. Verified via `grep -c "\[OPEN\]" SPEC_SHEET.md` returns 0 (excluding the doc-header `Status: [OPEN]` line which transitions to `[LOCKED]` at Phase 0 close).
2. **Zero `open` rows in `SPEC_GREENFIELD.md` ledger appendix** — every row reads `locked-to-X (see ADR-NNN)` OR `superseded-by-NNN` OR `deferred-to-phase-N` with explicit rationale. Verified via `awk '/^\| open \|/' SPEC_GREENFIELD.md` returns 0 lines.
3. **All `tests/test_invariants.py` stubs unskipped + green** — every `@pytest.mark.skip` decorator removed; `pytest -m unit` exits clean. Verified via `pytest -m unit tests/test_invariants.py` + `pytest --collect-only` shows zero skipped tests.
4. **`SUBMISSION_AUDIT.md` regenerates cleanly** — every claim in `Accepted` OR `Superseded` state (no `Proposed` at submission tag). Verified via `make audit` (wraps `scripts/regenerate_audit.py --check`) exits 0.
5. **`v0.9.0-rc1` rehearsal tag fired successfully before `v1.0.0`** (per ADR-033) — verified via `git tag -l v0.9.0-rc1*` returns at least one tag + `gh run list --workflow publish.yml` shows green status for that tag.
6. **All three reviewer URLs at `v1.0.0` resolve** — source pin at `tree/v1.0.0` + live Quarto site at GH Pages URL + GH release page with CHANGELOG + `_site.tar.gz` asset (per ADR-033). Verified via `curl --head` returns HTTP 200 (or 301-redirect-to-200) for all three URLs.

Per-ADR `acceptance_criterion:` frontmatter fields collectively cover the granular gates (data manifests + calibration artefacts + threshold reachability + HF Hub model card schema + etc.). Gate 4 is the mechanical check that all per-ADR criteria are satisfied.

### Kit-default §6 gates (preserved; subsumed by gates 3 + 4 above but listed explicitly for kit-level continuity)

- `make test` passes (incl. invariants for class balance, source-disjoint, frozen-dataclass, no-emoji, reporting-completeness).
- `make lint` clean.
- `evals/results.json` schema-validated against eval-toolkit's `results.v1.json`.
- All assumptions with severity ≥ medium in `assumptions.md` appear in the WRITEUP caveats block.

### Submission-readiness sign-off

`SUBMISSION_TEMPLATE.md` (or `SUBMISSION.md` cover-letter) quotes the 6 gates so the submission-readiness check is reviewer-readable at submission tag. The submission is not ready until every gate above passes.

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

**Linked ADRs**: ADR-001, ADR-025, ADR-026, ADR-027, ADR-028, ADR-029, ADR-030, ADR-031, ADR-032, ADR-033, ADR-034, ADR-035, ADR-036, ADR-037, ADR-038, ADR-039, ADR-040, ADR-041, ADR-042, ADR-043.

---

## 9. Submission deliverables (Phase 0-07)

`[LOCKED]` Submission deliverables locked at Phase 0-07 — see ADR-030 (deliverable format = Quarto HTML site via GH Actions; supersedes ADR-002 PDF + repo) + ADR-031 (reviewer reading paths via `index.qmd` + sidebar nav; supersedes ADR-004 PDF-as-hub framing) + ADR-032 (HF Hub publication = headline rungs only with model card discipline) + ADR-033 (release strategy = `v0.9.0-rc1` rehearsal + `v1.0.0` submission + `v1.0.x` post-submission patches; CHANGELOG + `_site.tar.gz` release asset) + ADR-034 (reproducibility tier = full ladder T0 eval-from-hub + T1 smoke + T3 headline-cloud).

**Reviewer email at submission** carries three URLs + private attachment:
1. Source pin — `https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.0.0`
2. Live rendered Quarto site — `https://brandon-behring.github.io/prompt-injection-detection-prototype/`
3. GH release page — `https://github.com/brandon-behring/prompt-injection-detection-prototype/releases/tag/v1.0.0`
4. Transcripts as private attachment per existing convention (gitignored).

**Linked ADRs**: ADR-030, ADR-031, ADR-032, ADR-033, ADR-034.

---

## 9. Open questions deferred to future iterations

`[TBD — populate as  work proceeds]`

- `[TBD: value]`
- `[TBD: value]`

---

## Appendix: decision trace

`[TBD: link to the planning artifact at ~/.claude/plans/<planning-slug>.md]`
