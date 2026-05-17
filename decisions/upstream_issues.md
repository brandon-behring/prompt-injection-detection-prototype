# Upstream issues filed during this iteration

Ledger tying anti-hand-rolling discipline to its evidence. Every discovered library gap, bug, or feature request is filed to the relevant upstream GitHub repo before any local workaround. Local site lists where the dependency or workaround lives in this repo.

Filed issues go to:

- `brandon-behring/eval-toolkit` — evaluation primitives
- `brandon-behring/runpod-deploy` — cloud orchestration
- `brandon-behring/research_toolkit` — dossier production

Triage label on filed issues: `tracked`.

| Date | Repo | Issue # | Title | Local site (file:line) | Status |
|---|---|---|---|---|---|
| 2026-05-15 | `brandon-behring/eval-toolkit` | [#17](https://github.com/brandon-behring/eval-toolkit/issues/17) | Add optional `n_jobs` parameter to `paired_bootstrap_diff` for internal resample-loop parallelization | `scripts/run_bootstrap_battery.py` (Phase 4 deliverable per ADR-022) | filed 2026-05-16 at Phase 4 entry; awaiting upstream triage |
| 2026-05-16 | `brandon-behring/eval-toolkit` | [#14](https://github.com/brandon-behring/eval-toolkit/issues/14) | Add `plot_roc_curve` (sibling to `plot_pr_curve`) | `src/eval/figures.py` Phase 4 F2 deliverable per ADR-046 | filed; PR candidate (mirrors `plot_pr_curve` signature) |
| 2026-05-16 | `brandon-behring/eval-toolkit` | [#15](https://github.com/brandon-behring/eval-toolkit/issues/15) | Add `plot_pareto_frontier` for cost-vs-performance scatter with frontier overlay | `src/eval/figures.py` Phase 4 F1 deliverable per ADR-046 | filed; awaiting upstream scoping triage |
| 2026-05-16 | `brandon-behring/eval-toolkit` | [#16](https://github.com/brandon-behring/eval-toolkit/issues/16) | Add `plot_slice_metric_heatmap` for `(group_x × group_y × metric)` grids | `src/eval/figures.py` Phase 4 F5 deliverable per ADR-046 | filed; awaiting upstream scoping triage |
| 2026-05-16 | `brandon-behring/eval-toolkit` | [#18](https://github.com/brandon-behring/eval-toolkit/issues/18) | Wire dedup-holdout golden test against this project's 50-pair adversarial dataset | `data/dedup_holdout.jsonl` + `scripts/calibrate_dedup.py` + `evals/dedup_calibration.json` | filed at Phase 1 library-first audit (per ADR-047); golden-test contribution candidate |
| 2026-05-16 | `brandon-behring/eval-toolkit` | [#19](https://github.com/brandon-behring/eval-toolkit/issues/19) | Add cookbook docs: 3 compositional patterns (nested-seed splits + callable-embedder strategy + pairs_across contamination scan) | `src/data/{splits, dedup, audit}.py` (Phase 1 hand-rolls that motivated this) | filed at Phase 1 library-first audit (per ADR-047); docs PR candidate |
| 2026-05-16 | `brandon-behring/eval-toolkit` | [#20](https://github.com/brandon-behring/eval-toolkit/issues/20) | Generalize `mde_from_ci` to accept `BootstrapCI \| PairedBootstrapCI` for marginal-MDE use case | `scripts/run_mde.py` Phase 4 deliverable per ADR-046 Q4 | filed at Phase 4 Q1-audit; inline-formula workaround per ADR-006 mandate; TODO cites this issue |
| 2026-05-16 | `brandon-behring/eval-toolkit` | [#21](https://github.com/brandon-behring/eval-toolkit/issues/21) | Add `block_bootstrap_on_folds` (CV-aware block bootstrap; complement to `cv_clt_ci`) | `src/eval/cross_fold_ci.py` Phase 4 deliverable per ADR-046 Q3 + ADR-024 + A-008 | filed at Phase 4 Q1-audit; inline impl workaround; TODO cites this issue |
| 2026-05-17 | `brandon-behring/eval-toolkit` | [#22](https://github.com/brandon-behring/eval-toolkit/issues/22) | Add `ax: Axes \| None` kwarg to `plot_metric_bars` (parity with `plot_pr_curve` / `plot_reliability_diagram` / `plot_lift_ci` / `plot_bootstrap_distribution`) | `src/eval/figures.py::render_f6_lodo_breakdown` Phase 4 Commit 4 per ADR-046 Q6 | filed at Phase 4 Commit 4 figures audit; bare-matplotlib bars workaround in F6 left panel; TODO cites this issue |
| 2026-05-17 | `brandon-behring/runpod-deploy` | [#88](https://github.com/brandon-behring/runpod-deploy/issues/88) | Make SSH-ready timeout configurable (default 240s too aggressive for cold image pulls) | `scripts/runpod_deploy_long_ssh.py` (monkey-patch shim with 600s deadline); Makefile `headline-{frozen-probe,lora,full-ft}` use shim for `run --config` | filed at Phase 4 canonical-run first-fire (2026-05-17); pod axzeexq75ley3k provisioned + RUNNING but SSH never populated within 240s window on cold pull of cudnn-devel image; shim removed when upstream lands + we bump pin |
| 2026-05-17 | `brandon-behring/runpod-deploy` | [#92](https://github.com/brandon-behring/runpod-deploy/issues/92) (doc) + [#93](https://github.com/brandon-behring/runpod-deploy/pull/93) (PR) + [#94](https://github.com/brandon-behring/runpod-deploy/issues/94) (scan-consumer) | UV_LINK_MODE=copy + UV_CACHE_DIR + UV_PROJECT_ENVIRONMENT off /workspace required on FUSE-mounted /workspace (silent hang under default hardlink mode + git-resolution F_SETLKW hang + HF Trainer atomic-save F_SETLKW hang) | `configs/runpod/headline-{frozen_probe,lora,full_ft}.yaml` `remote_env.exports` (Phase 4 X7 + X8 commits `13f06b8`/`8af73ae`); memory entry `memory/fuse-workspace-needs-uv-link-mode-copy.md` (3 FUSE failure modes); seed manifest + cost ledger (`artifacts/runpod/manual-20260517T155912Z/runpod_deploy_pull_manifest.json` + `evals/cost_ledger.csv` commit `7c1f36c`) | X7 (UV_LINK_MODE=copy) filed first at Phase 4 re-fire #4 hang diagnosis (2026-05-17); rediscovered v5 2026-05-15 lesson at ~$3 sunk cost. X8 amendment (PR #93 commit [e05210a](https://github.com/brandon-behring/runpod-deploy/pull/93/commits/e05210a) + [PR comment](https://github.com/brandon-behring/runpod-deploy/pull/93#issuecomment-4471599214)) covers 2 more FUSE failure modes (git-resolution + HF Trainer save) — UV_LINK_MODE=copy is necessary but NOT sufficient. Cross-references posted: [#92 comment](https://github.com/brandon-behring/runpod-deploy/issues/92#issuecomment-4471601526), [#94 comment with 4 scan-consumer extensions](https://github.com/brandon-behring/runpod-deploy/issues/94#issuecomment-4471604777). External verification: [uv#17801](https://github.com/astral-sh/uv/issues/17801), [MooseFS#380](https://github.com/moosefs/moosefs/discussions/380), [Linux kernel patch 2025-12-23](https://lkml.org/lkml/2025/12/23/264). Workaround removal trigger: PR #93 merges + version bump. |
| 2026-05-17 | `brandon-behring/runpod-deploy` | [#90](https://github.com/brandon-behring/runpod-deploy/issues/90) (feat) | `lifecycle.on_success: recycle` — resume paused pods on `run` retry (avoid re-provisioning when only config edits changed) | bypassed orchestrator via manual SSH for `i5p43hfq88zpqt` recovery (Phase 4 re-fire #5); no local code dependency (waiting on upstream feature) | Issue pre-existed (filed by brandon-behring earlier 2026-05-17); added [consumer-evidence comment](https://github.com/brandon-behring/runpod-deploy/issues/90#issuecomment-4471608331) with $4.78 5-pod cost breakdown + stock-roulette use case + validation of proposed design + offer to beta test. Workaround removal trigger: PR for recycle action lands + version bump. |
| 2026-05-17 | `brandon-behring/runpod-deploy` | [#97](https://github.com/brandon-behring/runpod-deploy/issues/97) (feat) | `validate --all` should HTTP HEAD-check `pod.image` against the public registry (catch phantom tags before pod fires) | no local code dependency (validate-time check; consumer-side fix was image-refresh in `configs/runpod/headline-*.yaml` Phase 4 X5 commit `b629181`) | Filed 2026-05-17 with cost evidence ~$0.62 burned on 2 phantom-image pods (axzeexq75ley3k + 3fka953y6xfjtd) before diagnosis. Proposed implementation: parse image namespace → HEAD Docker Hub tags API → warn at validate time. Workaround removal trigger: feature lands. |
| 2026-05-17 | `brandon-behring/runpod-deploy` | [#98](https://github.com/brandon-behring/runpod-deploy/issues/98) (docs) | Makefile-recipe pattern doc when `runpod-deploy` is in `[project.optional-dependencies] dev` (consumers hit cryptic PATH error otherwise) | `Makefile` recipes use `uv run runpod-deploy ...` (Phase 4 X4 sed-rewrite commit `a04e016`) | Filed 2026-05-17 after Phase 4 X3 → X4 sequence hit the trap. Proposed: extend `docs/source/recipes/local-preflight-then-run.md` with a Makefile-recipes section. Cross-references issue #94 (scan-consumer) for the related static-analysis warning. Workaround removal trigger: doc lands. |

## How to use this ledger

When you discover a gap during Phase 1+ work:

1. File the upstream issue with `tracked` label (use `gh issue create`)
2. Add a row to this ledger with the issue URL + the local file:line that depends on it
3. If a workaround is unavoidable, leave a TODO comment in code citing the issue number; remove when upstream lands

A workaround that hand-rolls a primitive without first filing the issue is an anti-pattern (see `SPEC_GREENFIELD.md` §7 Anti-patterns).

### Test-coverage-gap entries (per ADR-028)

When a coverage gap surfaces under the 70% floor that would be better addressed by an upstream library test (e.g., a test pattern that should live in eval-toolkit's harness coverage, or a runpod-deploy preflight scenario) rather than absorbed as a low-value local test:

1. File the upstream issue with the proposed test pattern (sketch, not implementation), the rationale (why upstream is the right home), the local file:line that depends on the absent test, and the `tracked` label.
2. Add a row to this ledger with the `[test-coverage-gap]` prefix in the Title column + the issue URL + the local file:line.

When a gap genuinely cannot be filed upstream (project-specific glue) AND cannot be cheaply tested locally:

1. Leave a code comment with the rationale (e.g., `# noqa: COV — Phase 0-06 deferral; project-specific orchestration glue, see decisions/upstream_issues.md`).
2. Add a row to this ledger with the `[not-applicable]` prefix in the Title column + the local file:line + the deferral rationale in the Status column.

Both forms preserve the discipline trail without forcing local anti-tests under the 70% floor.

A coverage gap that gets papered over with a no-op test (or with `# pragma: no cover` and no ledger entry) is an anti-pattern.
