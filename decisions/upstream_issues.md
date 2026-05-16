# Upstream issues filed during this iteration

Ledger tying anti-hand-rolling discipline to its evidence. Every discovered library gap, bug, or feature request is filed to the relevant upstream GitHub repo before any local workaround. Local site lists where the dependency or workaround lives in this repo.

Filed issues go to:

- `brandon-behring/eval-toolkit` — evaluation primitives
- `brandon-behring/runpod-deploy` — cloud orchestration
- `brandon-behring/research_toolkit` — dossier production

Triage label on filed issues: `tracked`.

| Date | Repo | Issue # | Title | Local site (file:line) | Status |
|---|---|---|---|---|---|
| 2026-05-15 | `brandon-behring/eval-toolkit` | `[TBD at Phase 4 entry]` | Add optional `n_jobs` parameter to `paired_bootstrap_diff` for internal resample-loop parallelization | `scripts/run_bootstrap_battery.py` (Phase 4 deliverable per ADR-022) | proposed; ledger-tracked pending Phase 4 file-time |

## How to use this ledger

When you discover a gap during Phase 1+ work:

1. File the upstream issue with `tracked` label (use `gh issue create`)
2. Add a row to this ledger with the issue URL + the local file:line that depends on it
3. If a workaround is unavoidable, leave a TODO comment in code citing the issue number; remove when upstream lands

A workaround that hand-rolls a primitive without first filing the issue is an anti-pattern (see `SPEC_GREENFIELD.md` §7 Anti-patterns).
