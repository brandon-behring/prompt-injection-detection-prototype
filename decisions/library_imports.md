# Library imports — discipline ledger

This repo uses three load-bearing libraries (see `SPEC_GREENFIELD.md` §Tech-Stack). Anything implementable as a library primitive is filed upstream (see `upstream_issues.md`); this ledger lists what is actually imported / invoked from each library. Updated incrementally as code lands.

The ledger is **positive evidence**: not just "we don't hand-roll" but "here is exactly what we use from each library." Reviewer-readable; CI-friendly.

## eval-toolkit imports (https://github.com/brandon-behring/eval-toolkit)

| Primitive | Imported in | Purpose |
|---|---|---|
| `eval_toolkit.bootstrap.bootstrap_ci` | `scripts/run_bootstrap_battery.py` (Phase 4 deliverable) | Per-rung marginal BCa-bootstrap CI; 10K iterations @ seed=1 headline + 10K @ seed=2 stability check (per ADR-022) |
| `eval_toolkit.bootstrap.paired_bootstrap_diff` | `scripts/run_bootstrap_battery.py` (Phase 4 deliverable) | Rung-vs-rung paired-bootstrap Δ-CI on persisted row-level predictions; percentile CI per `bootstrap.py:489` (per ADR-022 + ADR-006) |
| `eval_toolkit.bootstrap.paired_bootstrap_ece_diff` | `scripts/run_bootstrap_battery.py` (Phase 4 deliverable) | Paired-bootstrap Δ-CI specifically for ECE (per ADR-023 calibration battery + ADR-022 paired-across-rungs) |
| `eval_toolkit.bootstrap.cv_clt_ci` | `scripts/run_bootstrap_battery.py` (Phase 4 deliverable) | Cross-fold CI via Bayle 2020 Theorem 3.1 on 12 per-(fold, seed) per-rung metric values; headline cross-fold CI machinery per ADR-024 |
| `eval_toolkit.metrics.pr_auc` + `roc_auc` + `recall_at_fpr` | `scripts/run_metrics_battery.py` (Phase 3 deliverable) | Rank-based descriptive metrics per ADR-006 + ADR-021 + ADR-022 |
| `eval_toolkit.metrics.expected_calibration_error_equal_mass` | `src/eval/calibration_battery.py` (Phase 3 deliverable) | Headline ECE-equal-mass(n_bins=15, quantile binning) per ADR-023 |
| `eval_toolkit.metrics.expected_calibration_error` + `_debiased` + `_l2` + `_l2_debiased` | `src/eval/calibration_battery.py` (Phase 3 deliverable) | Full 4-ECE matrix for methodology spoke per ADR-023 |
| `eval_toolkit.metrics.brier_score` + `brier_decomposition` | `src/eval/calibration_battery.py` (Phase 3 deliverable) | Headline Brier per rung + spoke decomposition (refinement / reliability / uncertainty) per ADR-023 |
| `eval_toolkit.calibration.reliability_curve` | `src/eval/calibration_battery.py` (Phase 3 deliverable) | Reliability diagrams per rung (equal-mass quantile binning) for spoke per ADR-023 |
| `eval_toolkit.calibration.fit_temperature` | `src/eval/calibration_battery.py` (Phase 3 deliverable) | Temperature scaling calibrator fit on val per-(rung, fold, seed) per ADR-023 + ADR-011 Guarantee 6 |
| `eval_toolkit.calibration.fit_isotonic_calibrator` | `src/eval/calibration_battery.py` (Phase 3 deliverable) | Isotonic regression calibrator fit on val per-(rung, fold, seed) per ADR-023 + ADR-011 Guarantee 6 |
| `eval_toolkit.calibration.maximum_calibration_error` | `src/eval/calibration_battery.py` (Phase 3 deliverable; audit-only) | Worst-bin calibration error dumped to `evals/calibration/per_obs_audit.parquet` per ADR-023 |
| `eval_toolkit.bootstrap.mde_from_ci` | `scripts/run_bootstrap_battery.py` (Phase 4 deliverable) | MDE on every reported CI per ADR-006 |
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
