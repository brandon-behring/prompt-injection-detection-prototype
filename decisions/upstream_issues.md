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

### Test-coverage-gap entries (per ADR-028)

When a coverage gap surfaces under the 70% floor that would be better addressed by an upstream library test (e.g., a test pattern that should live in eval-toolkit's harness coverage, or a runpod-deploy preflight scenario) rather than absorbed as a low-value local test:

1. File the upstream issue with the proposed test pattern (sketch, not implementation), the rationale (why upstream is the right home), the local file:line that depends on the absent test, and the `tracked` label.
2. Add a row to this ledger with the `[test-coverage-gap]` prefix in the Title column + the issue URL + the local file:line.

When a gap genuinely cannot be filed upstream (project-specific glue) AND cannot be cheaply tested locally:

1. Leave a code comment with the rationale (e.g., `# noqa: COV — Phase 0-06 deferral; project-specific orchestration glue, see decisions/upstream_issues.md`).
2. Add a row to this ledger with the `[not-applicable]` prefix in the Title column + the local file:line + the deferral rationale in the Status column.

Both forms preserve the discipline trail without forcing local anti-tests under the 70% floor.

A coverage gap that gets papered over with a no-op test (or with `# pragma: no cover` and no ledger entry) is an anti-pattern.
