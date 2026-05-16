# Library imports — discipline ledger

This repo uses three load-bearing libraries (see `SPEC_GREENFIELD.md` §Tech-Stack). Anything implementable as a library primitive is filed upstream (see `upstream_issues.md`); this ledger lists what is actually imported / invoked from each library. Updated incrementally as code lands.

The ledger is **positive evidence**: not just "we don't hand-roll" but "here is exactly what we use from each library." Reviewer-readable; CI-friendly.

## eval-toolkit imports (https://github.com/brandon-behring/eval-toolkit)

| Primitive | Imported in | Purpose |
|---|---|---|
| `(populated as code lands at Phase 1+)` | | |

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
