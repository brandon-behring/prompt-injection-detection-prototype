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
