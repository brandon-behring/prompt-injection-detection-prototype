# Library imports — discipline ledger

This repo uses three load-bearing libraries (see `SPEC_GREENFIELD.md` §Tech-Stack). Anything implementable as a library primitive is filed upstream (see `upstream_issues.md`); this ledger lists what is actually imported / invoked from each library. Updated incrementally as code lands.

The ledger is **positive evidence**: not just "we don't hand-roll" but "here is exactly what we use from each library." Reviewer-readable; CI-friendly.

## Version pinning lock (Phase 0-08 per ADR-036)

| Library | Pinned version | pyproject.toml specifier |
|---|---|---|
| `eval-toolkit` | `v0.31.0` | `eval-toolkit @ git+https://github.com/brandon-behring/eval-toolkit@v0.31.0` |
| `runpod-deploy` | `v0.7.7` (matches ADR-020 pre-existing pin) | `runpod-deploy @ git+https://github.com/brandon-behring/runpod-deploy@v0.7.7` |
| `research_toolkit` | `v1.9.1` | `research_toolkit @ git+https://github.com/brandon-behring/research_toolkit@v1.9.1` |

**Pinning strategy** (per ADR-036): tag pin + freeze for submission window (Phase 0-08 close → `v1.0.0` submission tag per ADR-033); `uv.lock` provides byte-level reproducibility on top.

**Python pin** (per ADR-037): `requires-python = ">=3.13"` + `.python-version = 3.13`.

**Bump triggers** — exactly three:
1. Blocking upstream bug that breaks a use-pattern documented below.
2. Critical security fix (CVE-grade) in the upstream.
3. Post-submission reviewer-feedback patch per ADR-033 `v1.0.x` discipline.

Routine "the upstream has a new release" is NOT a bump trigger. Each bump produces a new commit + an entry in `decisions/upstream_issues.md` referencing the trigger; bumps do NOT supersede ADR-036 (the discipline is locked; specific versions move). Freeze expires at `v2.0.0` per ADR-033 major-bump discipline.

## Secrets discipline (Phase 0-08 per ADR-035)

All consumer libraries (`huggingface_hub`, `openai`, `anthropic`, `runpod-deploy` CLI) discover tokens via their default env-var auto-discovery. Token storage uses a three-store split aligned with execution context — local `.env` (gitignored; per ADR-035) + RunPod pod-secrets via `runpod-deploy` config + GH Actions repo Secrets. `.env.example` committed at repo root as a placeholder template enumerating the four canonical env vars (`HF_TOKEN` + `RUNPOD_API_KEY` + `OPENAI_API_KEY` + `ANTHROPIC_API_KEY`). See ADR-035 for rotation protocol + preflight verification.

## eval-toolkit imports (https://github.com/brandon-behring/eval-toolkit)

| Primitive | Imported in | Purpose |
|---|---|---|
| `eval_toolkit.splits.SourceDisjointKFoldSplitter` + `eval_toolkit.harness.EvalSlice` | `src/data/splits.py::make_splits` (Phase 1 library-first carryforward refactor per ADR-047 Commit 2) | LODO source-disjoint k-fold partition (k=4 per ADR-016 Q2 + TRAIN_POSITIVE_SOURCES tuple length); upstream docstring notes "Generalizes the source-disjoint split pattern from prompt-injection-sdd" — abstracted from this project's predecessor. Project glue remaps upstream-shuffled fold order back to TRAIN_POSITIVE_SOURCES tuple order (deterministic fold_id-to-source mapping); composes per-seed stratified 80/20 train/val + benigns-in-every-train-pool discipline on top |
| `eval_toolkit.text_dedup.near_dedup` | `src/data/dedup.py::dedup_within_source` + `dedup_cross_source_benigns` (ADR-047 Commit 3) | Greedy forward-scan near-dedup at threshold 0.80 per ADR-016 Q4. `dedup_within_source` invokes per-(source, label) cell; `dedup_cross_source_benigns` invokes on priority-first-concatenated DataFrame (LMSYS-priority tiebreak naturally encoded by forward-scan over priority-first ordering per ADR-016 Q5). Project glue maps upstream's `(dropped_idx, kept_idx, similarity)` triples to project-specific dropped_records dicts |
| `eval_toolkit.text_dedup.EmbeddingCosineStrategy(embedder=compute_embeddings)` | `src/data/dedup.py::_embedding_strategy` (ADR-047 Commit 3) | Strategy class passed to `near_dedup` + `pairs_across`; toolkit owns cosine + k-NN, project owns the embedder (`compute_embeddings` is a MiniLM-L6-v2 sentence-transformer wrapper per ADR-016 Q4) |
| `eval_toolkit.text_dedup.EmbeddingCosineStrategy.pairs_across` | `src/data/dedup.py::drop_train_test_leakage` + `src/data/audit.py::compute_contamination_scan` (ADR-047 Commit 3 + Commit 4) | Per-(candidate_train_val) top-1 max-cosine to test set; k=1 returns shape (n_query, 1) similarities + indices. Used in cosine-leakage layer (exact-hash layer stays as set-intersection project-specific layer per ADR-016 Q3). Also used in compute_contamination_scan for per-source max-cosine-to-reference scan per ADR-041 Q6 + A-006 |
| `eval_toolkit.text_dedup.EmbeddingCosineStrategy.pairs_within` | `scripts/build_dedup_holdout.py::_enumerate_within_source_pairs` (ADR-047 Commit 4) | Within-source pair enumeration for the 50-pair dedup-holdout calibration corpus per ADR-041 Q5; k_neighbors=N-1 covers every other row; project glue dedupes ordered (i, j>i) pairs + assigns each to its cosine band {[0.55-0.65), [0.65-0.75), ..., [0.95-1.00)} |
| `eval_toolkit.leakage.CrossSplitLeakageCheck` + `eval_toolkit.leakage.run_leakage_checks` + `eval_toolkit.harness.EvalSlice` | `src/data/audit.py::compute_leakage_report` (ADR-047 Commit 4) | Per-(fold, seed) train+val vs test leakage detection via upstream Check Protocol. ADR-047 acceptance criterion specified [ExactDuplicateCheck + NearDuplicateCheck + CrossSplitLeakageCheck]; implementation uses only CrossSplitLeakageCheck since the other two operate within-split and would always report zero findings post-dedup_within_source (which runs upstream in the data pipeline per ADR-041 Q7). Project-dict output schema preserved by extracting test-side drop count from LeakageFinding.drop_indices |
| `eval_toolkit.bootstrap.bootstrap_ci` | `src/eval/marginal_bootstrap.py::compute_marginal_bootstrap_cell` (Phase 4 Commit 2 per ADR-046 Q1); `scripts/run_marginal_bootstrap.py` (Phase 4 Commit 5 orchestrator) | Per-rung marginal BCa-bootstrap CI; 10K iterations @ seed=1 headline + 10K @ seed=2 stability check (per ADR-022); validated through MarginalBootstrapCellModel |
| `eval_toolkit.bootstrap.paired_bootstrap_diff` | `scripts/run_bootstrap_battery.py` (Phase 3 Commit 5, landed) | Rung-vs-rung paired-bootstrap Δ-CI on persisted row-level predictions; full-pairwise persistence per ADR-045 Q6 (~C(rungs, 2) × slices × metrics cells); percentile CI per `bootstrap.py:489` (per ADR-022 + ADR-006) |
| `eval_toolkit.bootstrap.paired_bootstrap_ece_diff` | `scripts/run_bootstrap_battery.py` (Phase 4 deliverable) | Paired-bootstrap Δ-CI specifically for ECE (per ADR-023 calibration battery + ADR-022 paired-across-rungs) |
| `eval_toolkit.bootstrap.cv_clt_ci` | `src/eval/cross_fold_ci.py::compute_cross_fold_ci_cell` (Phase 4 Commit 2 headline + Commit 3 spoke); `scripts/run_cv_clt_ci.py` (Phase 4 Commit 5 orchestrator) | Cross-fold CI via Bayle 2020 Theorem 3.1 on per-fold metric vector (K folds x S seeds-per-fold reduced to K fold means per ADR-022 multi-seed protocol); headline cross-fold CI machinery per ADR-024; validated through CrossFoldCIModel. Commit 3 always pairs each headline cv_clt CI with an inline block-bootstrap-on-folds spoke (workaround pending upstream issue #21; same module) + auto-flag column per A-008 |
| `eval_toolkit.metrics.pr_auc` + `roc_auc` (entry above for Phase 3 Commit 4 landing) | `scripts/run_metrics_battery.py` (Phase 3 Commit 5) | Aggregator script orchestrates per-(rung, fold, seed, slice) calls to `src/eval/slice_analysis.py::compute_metric_record` (no separate `recall_at_fpr` primitive exists in eval-toolkit; recall@FPR is computed via `TargetFPRSelector(t).select(y, s).recall` wrapped in `src/eval/slice_analysis.py::compute_recall_at_fpr` per ADR-021) |
| `eval_toolkit.metrics.expected_calibration_error_equal_mass` | `src/eval/calibration_battery.py` (Phase 3 Commit 3, landed) | Headline ECE-equal-mass(n_bins=15, quantile binning) per ADR-023 |
| `eval_toolkit.metrics.expected_calibration_error` + `_debiased` + `_l2` + `_l2_debiased` | `src/eval/calibration_battery.py` (Phase 3 Commit 3, landed) | Full 4-ECE matrix for methodology spoke per ADR-023 |
| `eval_toolkit.metrics.brier_score` + `brier_decomposition` | `src/eval/calibration_battery.py` (Phase 3 Commit 3, landed) | Headline Brier per rung + spoke decomposition (reliability/resolution/uncertainty) per ADR-023 |
| `eval_toolkit.calibration.reliability_curve` | `src/eval/calibration_battery.py` (Phase 3 Commit 3, landed) | Reliability diagrams per rung (equal-mass quantile binning) for spoke per ADR-023 |
| `eval_toolkit.calibration.fit_temperature` | `src/eval/calibration_battery.py` (Phase 3 Commit 3, landed) | Temperature scaling calibrator fit on val per-(rung, fold, seed) per ADR-023 + ADR-011 Guarantee 6 |
| `eval_toolkit.calibration.fit_isotonic_calibrator` | `src/eval/calibration_battery.py` (Phase 3 Commit 3, landed) | Isotonic regression calibrator fit on val per-(rung, fold, seed) per ADR-023 + ADR-011 Guarantee 6 |
| `eval_toolkit.calibration.maximum_calibration_error` | `src/eval/calibration_battery.py` (Phase 3 deliverable; audit-only; not yet wired) | Worst-bin calibration error dumped to `evals/calibration/per_obs_audit.parquet` per ADR-023 |
| `eval_toolkit.bootstrap.mde_from_ci` | `src/eval/mde.py::mde_from_paired_ci_record` (Phase 4 Commit 2 per ADR-046 Q4); `scripts/run_mde.py` (Phase 4 Commit 5 orchestrator sweeping ~100 cells) | MDE on every reported CI per ADR-006 — direct path for PairedBootstrapCI inputs; marginal-CI inputs use the closed-form workaround in `src/eval/mde.py::mde_from_marginal_ci_record` pending upstream issue #20 (same numerical formula; API generalization) |
| `eval_toolkit.thresholds.TargetFPRSelector` | `src/eval/operating_points.py` (Phase 3 Commit 4, landed); `scripts/fit_dual_policy_thresholds.py` (Phase 3 Commit 5) | Detection-policy threshold fit on val per-(rung, fold, seed); FPR ≤ 1% target (per ADR-025) |
| `eval_toolkit.thresholds.TargetRecallSelector` | `src/eval/operating_points.py` (Phase 3 Commit 4, landed); `scripts/fit_dual_policy_thresholds.py` (Phase 3 Commit 5) | Verification-policy threshold fit on val per-(rung, fold, seed); recall ≥ 99% target (per ADR-025); honest infeasibility reporting via try/except RuntimeError → target_reachable=False per A-009 |
| `eval_toolkit.metrics.metrics_at_threshold` | `src/eval/operating_points.py` (Phase 3 Commit 4, landed); also `src/eval/slice_analysis.py` via `use_metrics_at_threshold_for_diagnostic` wrapper | At-threshold metrics dict (recall, fpr, precision, etc.) used by both dual-policy fit + diagnostic dumps |
| `eval_toolkit.metrics.pr_auc` + `roc_auc` | `src/eval/slice_analysis.py::compute_metric_record` (Phase 3 Commit 4, landed) | Rank-based descriptive metrics per ADR-006 + ADR-021 + ADR-022 |
| `eval_toolkit.bootstrap.paired_bootstrap_op_point_diff` | `scripts/run_bootstrap_battery.py` (Phase 4 deliverable) | Two-level bootstrap CI for dual-policy operating-point metrics (refit threshold per val resample, apply on test resample, paired diff); per ADR-025 + ADR-022 per-(seed) threshold protocol |
| `eval_toolkit.metrics.metrics_at_threshold` | `scripts/fit_dual_policy_thresholds.py` + `src/eval/operating_points.py` (Phase 3 deliverable) | Compute (precision, recall, FPR, F1) at fitted threshold; per ADR-025 dual-policy reporting layout |
| Glue: `joblib.Parallel(n_jobs=-1)` (NOT eval-toolkit; project-specific orchestrator-layer parallelization) | `scripts/run_bootstrap_battery.py` (Phase 4 deliverable) | Parallelize ~10000 independent CI computations across 64-core Threadripper; library-first discipline preserves primitives as single-threaded shipped, parallelism is at call-site (per ADR-022) |

## runpod-deploy imports (https://github.com/brandon-behring/runpod-deploy) [v0.7.7 pinned]

| CLI / module | Invoked in | Purpose |
|---|---|---|
| `runpod-deploy validate --all` | `Makefile` target `validate-runpod-config` | Preflight schema + DC reachability + GPU stock check before any billed run (per ADR-020) |
| `runpod-deploy run --dry-run` | `Makefile` target `headline-dry-run` | Cost preview without provisioning — hits runpodctl + GraphQL pricing (per ADR-020) |
| `runpod-deploy run --config ...` | `Makefile` target `headline-cloud` | Canonical headline run (per ADR-020) |
| `runpod-deploy logs --config ...` | live-tail during runs | Active-pod log streaming |
| `runpod-deploy stop --state-file ...` | emergency teardown | Cost-cap breach + ADR-013 pre-teardown checklist |
| `runpod-deploy manifest-summary` | `scripts/cost_rollup.py` | Per-run cost capture from `runpod_deploy_pull_manifest.json` (per ADR-020 cost-reconciliation recipe) |
| `pod.gpu_order` + `pod.datacenters` schema | `configs/runpod/headline.yaml` | 8-class GPU failover × 2-DC failover (per ADR-020) |
| `budget.cost_cap_usd` + `assumed_hourly_rate_usd` | `configs/runpod/headline.yaml` | Per-job soft cap $125 (= A-002 upper bound; per ADR-020) |
| `preflight.check_gpu_availability` (internal; invoked by `validate --all`) | preflight pipeline | Pre-spend GPU-stock check across gpu_order × datacenters cross-product |
| Recipe: **flash-attention-fallback** | `src/training/load_modernbert.py` | Cross-GPU-class portability via `try/except (ValueError, ImportError)` (per ADR-020) |
| Recipe: **cost-reconciliation** | `scripts/cost_rollup.py` | Post-run actual-vs-assumed reconciliation via `runpod_deploy_pull_manifest.json` (per ADR-020 dual-layer cost tracking) |
| `events.emit_event` (in flash-attn-fallback recipe) | `src/training/load_modernbert.py` fallback branch | Audit-trail emission when fallback fires |

## Quarto + GitHub Actions (introduced by ADR-030 + ADR-033)

Quarto is the writeup-rendering engine introduced at Phase 0-07 close per ADR-030 (deliverable format = repo-only with Quarto-rendered HTML site via GH Actions; supersedes ADR-002 PDF + repo). Listed here to preserve the library-first discipline trail; Quarto version pinning is deferred to Phase 0-08 (library version pinning sub-session).

| Library / action | Invoked in | Purpose |
|---|---|---|
| `quarto` (single-binary CLI; system install) | `Makefile` targets `site` + `site-preview` | Local Quarto site render (`quarto render`) + live-reload dev server (`quarto preview`) per ADR-030 |
| `quarto-actions/setup@v2` | `.github/workflows/publish.yml` | CI Quarto install (per ADR-030 GH Actions hosting lock) |
| `quarto-actions/publish@v2` | `.github/workflows/publish.yml` | Auto-publish rendered `_site/` to GH Pages via `gh-pages` branch on push to `main` and on tag push `v*` (per ADR-030 + ADR-033 tag-triggers-publish) |
| `_quarto.yml` website config | repo root | Sidebar nav for 8 spokes + auto-include of all ADRs; `format: html` only (no PDF auxiliary per ADR-030 Q1.b lock) |
| `index.qmd` entry-point | repo root | Reviewer reading-path guide (A1 + A2 + deep-dive paths per ADR-031) |

## huggingface_hub publication-side use (introduced by ADR-032)

Beyond ADR-013's persistence-side use of HF Hub (cache + checkpoint storage), ADR-032 introduces *publication-side* use — pushing the headline rungs to public `BBehring/prompt-injection-<rung>` model repos with model card discipline.

| Primitive | Invoked in | Purpose |
|---|---|---|
| `huggingface_hub.HfApi.upload_folder` | `scripts/generate_model_cards.py` (Phase 5 deliverable) | Push trained checkpoint + model card README to public HF Hub model repo per ADR-032 |
| `huggingface_hub.HfApi.list_repos` | `tests/test_invariants.py::test_hf_hub_publication_naming_convention` (Phase 5 verification) | Verify naming convention `BBehring/prompt-injection-<rung-name>` for all published rungs |
| `huggingface_hub.snapshot_download` | `scripts/eval_from_hub.py` (Phase 3 deliverable; T0 reproducibility tier per ADR-034) | Download a published checkpoint for eval-only reproduction; pin via `revision=<SHA>` if drift detected per ADR-034 extension condition |

## Phase 3 Evaluation deps (introduced incrementally per ADR-045 across Commits 1–6)

| Library | First imported in | Purpose | Pinned at |
|---|---|---|---|
| `pydantic` | `src/eval/schemas.py` (Commit 2) | v2 BaseModel contract for PredictionsRowModel + MetricsRecordModel + SliceMetricsModel + OperatingPointModel + CalibrationRecordModel + ReachabilityAuditModel + BootstrapCellModel per ADR-045 Q7 | `>=2.5` (`pyproject.toml`) |
| `anthropic` | `src/scoring/anthropic_judge.py` (Commit 2) | claude-sonnet-4-6 LLM-judge client per ADR-018 line 58; `client.messages.create(temperature=0)` | `>=0.40` (`pyproject.toml`) |
| `transformers.AutoModelForSequenceClassification` + `AutoTokenizer` | `src/scoring/protectai.py` (Commit 2) | ProtectAI v1 + v2 inference loaders per ADR-018 line 76 (DeBERTa-v3-base; head-truncation 512; bf16 GPU) | `>=4.48` (already pinned for Phase 2) |
| `openai.OpenAI` | `src/scoring/openai_judge.py` (Commit 2) | gpt-4o-2024-08-06 LLM-judge client per ADR-018 line 58; `chat.completions.create(temperature=0, response_format=json_object)` | `>=1.50` (already pinned for Phase 1 ADR-042) |

**Phase 3 scoring entrypoints**:

- `src/scoring/protectai.py::ProtectAIScorer(version, revision)` — ProtectAI v1+v2 wrapper; reads HF model+tokenizer at pinned SHA; runs in CI smoke with mock model.
- `src/scoring/llm_judge_base.py::LLMJudgeBase` — abstract base with cache infra at `evals/audit/llm_judge_cache/<judge>__<text_sha256_first_16>.json` per A-007 + A-014.
- `src/scoring/openai_judge.py::OpenAIJudge` — gpt-4o-2024-08-06 subclass.
- `src/scoring/anthropic_judge.py::AnthropicJudge` — claude-sonnet-4-6 subclass.
- `src/scoring/prompts/prompt_template_v1.md` — versioned LLM-judge prompt template per ADR-018 line 67.

## Phase 1 Data deps (introduced incrementally per ADR-041 across Commits 1–6)

| Library | First imported in | Purpose | Pinned at |
|---|---|---|---|
| `huggingface_hub` | `scripts/pin_source_manifest.py` (Commit 1) | `HfApi.dataset_info(repo_id).sha` for revision SHA discovery per ADR-041 Q2 | `>=0.25` (`pyproject.toml`) |
| `pyyaml` (graduated dev → main dep) | `src/data/manifest_validation.py` + `scripts/pin_source_manifest.py` (Commit 1) | Manifest YAML parse/serialize per ADR-041 Q1 rich-schema | `>=6` (`pyproject.toml`) |
| `datasets` | `src/data/loaders.py` (Commit 2) | `load_dataset(repo, name=subset, split=split, revision=sha)` per ADR-041 Q4 HF dispatch | `>=3.0` (`pyproject.toml`) |
| `pandas` + `pandas-stubs` | `src/data/loaders.py` (Commit 2) | DataFrame uniform schema `(text, label, source, row_idx_in_source)`; parquet IO at Commit 4 | `>=2.2` (`pyproject.toml`) + `>=2.2` dev |
| `pyarrow` | `src/data/loaders.py` (transitive via pandas; Commit 4 parquet) | parquet engine | `>=17` (`pyproject.toml`) |
| `sentence-transformers` | `src/data/dedup.py` (Commit 3) | `all-MiniLM-L6-v2` embedder per ADR-016 Q4 + `THRESHOLD=0.80` locked constant | `>=3.0` (`pyproject.toml`) |
| `numpy` | `src/data/dedup.py` + `scripts/build_dedup_holdout.py` (Commit 3) | pairwise cosine matrix ops; `default_rng(seed)` for deterministic sampling | `>=2.0` (`pyproject.toml`) |
| `scikit-learn` | `src/data/splits.py` (Commit 4) | `sklearn.model_selection.train_test_split(stratify=y, random_state=seed)` for within-fold 80/20 (per ADR-016 Q2; SEEDS={42, 43, 44} per ADR-006) | `>=1.5` (`pyproject.toml`) |
| `torch` (transitive via sentence-transformers) | `src/data/dedup.py` (Commit 3) | encoder backend; CPU-only inference on laptop; flash-attn fallback in Phase 2+ trainer | pinned by sentence-transformers transitive |
| `openai` | `scripts/llm_prelabel_dedup_holdout.py` (Commit 3 supplement per ADR-042) | gpt-4o-2024-08-06 judge for dedup-pair-near-duplicate bootstrap labeling (same snapshot as ADR-018 headline rater); `chat.completions.create(temperature=0, response_format=json_object)` | `>=1.50` (`pyproject.toml`) |

**Dedup pipeline entrypoints**:

- `scripts/build_dedup_holdout.py` — Generates 50 stratified-cosine-band candidate pairs from
  the 4 train-positive sources; writes `data/dedup_holdout.jsonl` with `true_duplicate: null`
  (TBD — hand-labeled by Brandon per ADR-041 Q5).
- `scripts/calibrate_dedup.py` — Reads labeled holdout; writes `evals/dedup_calibration.json` with
  FPR + FNR at locked threshold 0.80 + sensitivity table at {0.75, 0.80, 0.85}.

Workflow: `build_dedup_holdout` → hand-label → `calibrate_dedup` → unskip `test_dedup_calibration_persisted`.

**Pin script entrypoint**: `scripts/pin_source_manifest.py` (Commit 1) — one-time + bump-driven; live-fetches HF SHAs via `huggingface_hub.HfApi.dataset_info` + GitHub SHAs via `subprocess.run(["git", "ls-remote", url, "HEAD"])`; writes `data/source_manifest.yaml`; idempotent re-runs; SHA-mismatch raises `SHAMismatchError` unless `--force` records `bump_history` entry per ADR-036.

**Manifest validator entrypoint**: `src/data/manifest_validation.py::validate_manifest(path)` (Commit 1) — invoked from `tests/test_invariants.py::test_source_manifest_schema_valid` + `scripts/pin_source_manifest.py` post-write sanity check.

**Audit + leakage + contamination pipeline (Commit 5)**:

- `src/data/audit.py::compute_data_audit(...)` — per-source counts + per-fold class balance + length distribution; operationalizes ADR-016 A-005 triggers 2 + 4.
- `src/data/audit.py::compute_leakage_report(splits)` — exact-hash + cosine >= 0.85 train+val vs test overlap per (fold, seed); ADR-016 Q3 hard-locked invariant.
- `src/data/audit.py::compute_contamination_scan(benigns, ood, slate, templates)` — per-row max cosine to (slate ∪ templates) reference corpus; ADR-016 A-005 trigger 1 + A-006 + ADR-041 Q6.
- `src/data/templates.py::extract_hackaprompt_templates(spec)` — ~200 successful-injection templates from HackAPrompt; balanced across 10 difficulty levels; disjoint sample seed (1337) from slate (42).
- `scripts/run_data_pipeline.py` — end-to-end orchestrator (load + dedup + split + leakage-cleanup + materialize + audit + leakage + contamination); writes 3 evals/ JSONs + 36 per-fold parquets + 36 index masks.

**ADR-043 post-split leakage cleanup**:

- `src/data/dedup.py::drop_train_test_leakage(train_val_df, test_df, threshold=0.85)` — scans train+val vs test for exact-hash + cosine ≥0.85 overlaps; drops train-side rows; returns cleaned df + per-pair drop records.
- `src/data/splits.py::apply_leakage_cleanup(splits, threshold=0.85)` — applies the above to all 12 (fold, seed) splits; re-partitions cleaned train+val at the 80/20 ratio.
- Wired between `make_splits` and `materialize_splits` in `scripts/run_data_pipeline.py`. Pipeline log records `n_dropped` per split (exact + cosine breakdown) for audit.

## research_toolkit usage (https://github.com/brandon-behring/research_toolkit)

The literature dossier at `docs/research/` was produced by this toolkit's skill pipeline. New dossier work invokes the same skills:

| Skill / artifact | Used in | Purpose |
|---|---|---|
| `/research-plan` | docs/research/<topic>/research_plan.md | sub-area planning + claim_family taxonomy |
| `/research-gather` | docs/research/<topic>/bib_ledger.yml | verified primary sources via WebSearch + WebFetch |
| `/dossier-build` | docs/research/<topic>/dossier/ | topic tables; one row per entry |
| `/agent-index` | docs/research/<topic>/ | 5-bullet-per-entry synthesis + AGENT-INDEX |
| `/dossier-audit` | docs/research/<topic>/audit_trail.md | DROP/CORRECT/FLAG decisions |
| `/url-freshness-check` | docs/research/<topic>/url_check_report.md | URL HEAD-check status |
