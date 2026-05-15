# Library imports — discipline ledger

This repo uses three load-bearing libraries (see `SPEC_GREENFIELD.md` §Tech-Stack). Anything implementable as a library primitive is filed upstream (see `upstream_issues.md`); this ledger lists what is actually imported / invoked from each library. Updated incrementally as code lands.

The ledger is **positive evidence**: not just "we don't hand-roll" but "here is exactly what we use from each library." Reviewer-readable; CI-friendly.

## eval-toolkit imports (https://github.com/brandon-behring/eval-toolkit)

| Primitive | Imported in | Purpose |
|---|---|---|
| `(populated as code lands at Phase 1+)` | | |

## runpod-deploy imports (https://github.com/brandon-behring/runpod-deploy)

| CLI / module | Invoked in | Purpose |
|---|---|---|
| `(populated as code lands at Phase 1+)` | | |

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
