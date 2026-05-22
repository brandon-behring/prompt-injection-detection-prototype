---
adr_id: "078"
slug: executive-summary-absorbed-into-readme
title: Absorb EXECUTIVE_SUMMARY content into README; retire EXECUTIVE_SUMMARY.md as standalone file
date: 2026-05-21
status: Accepted
claim_id: CLAIM-078
claim: >-
  The reading-guide architecture before v1.3.0 has 4 reader-facing
  distillation surfaces — index.qmd (60-sec landing) + README.md
  (repo-level orientation) + EXECUTIVE_SUMMARY.md (1-page summary) +
  WRITEUP.md (methodology hub) — with same content rendered in 3-4
  framings on EXECUTIVE_SUMMARY + index + WRITEUP. The v1.3.0
  restructure (see ADR-079) introduces 2 reader-style guides
  (WRITEUP_PAPER.md + WRITEUP_NARRATIVE.md) which require a clear
  separation between the depth-0 entry (README + index) and the
  depth-1 reading guides. To avoid maintaining 3+ overlapping
  distillation surfaces, EXECUTIVE_SUMMARY.md is retired and its
  content absorbed into README.md as the README's top-fold
  §"Executive summary" section. Behavior changes: (a) README.md
  becomes the canonical 1-page distillation reachable both from the
  repo root + via direct link on the live site; (b) EXECUTIVE_SUMMARY.md
  is removed from `_quarto.yml` render allowlist + sidebar + navbar +
  cross-references; (c) the historical reviewer URL pin (`tree/v1.0.0`
  per ADR-033) preserves the EXECUTIVE_SUMMARY.md file at submission
  time so external academic citations of EXECUTIVE_SUMMARY remain
  resolvable. Decision affects presentation surfaces only; no
  methodology / model / data / compute change.
source: User feedback 2026-05-21 surfacing the "neither narrative nor
  academic structure — random parts of results all over the place"
  diagnosis; subsequent /exploring-options Q1.1 lock ("the executive
  summary can be on the readme?") + Q1 main scope reduction from 3
  guides to 2 guides + README absorption.
closing_commit:
transcript:
supersedes:
  - "053"  # on the "two-entry-artifacts" reading-guide-architecture axis only; ADR-053 dimensions 2 + 3 + 4 + 5 (hub-spoke / 3-reading-paths / headline-finding-block / interpretation-pedagogy / pointer-convention) unchanged
superseded_by:
acceptance_criterion: >-
  `ls EXECUTIVE_SUMMARY.md 2>&1` returns "No such file or directory"
  on the v1.3.0 tip. `grep '^## Executive summary' README.md` returns
  1+ match. `_quarto.yml` render allowlist has no `EXECUTIVE_SUMMARY.md`
  entry; navbar Reference dropdown has no "Executive summary" entry;
  sidebar Entry section has no `EXECUTIVE_SUMMARY.md` entry.
  `decisions/audits/REPO_AUDIT_2026-05-21.md` does NOT cite the
  retirement as a delta (it precedes v1.3.0). Audit scripts all exit 0
  (incl. v1.2.14 audit_adr_count_claims after 77→78 cascade per
  ADR-078's creation).
linked_adrs:
  - "033"  # reviewer URL pin (preserves EXECUTIVE_SUMMARY at tree/v1.0.0)
  - "053"  # reading-guide governance (superseded on entry-artifacts axis)
  - "054"  # RESULTS as third entry artifact (separately superseded by ADR-079 on the entry-artifacts axis)
  - "061"  # navbar/sidebar restructure (separately superseded by ADR-079)
  - "062"  # Quarto writeup clarity + canonical figures (preserved; not in conflict)
  - "079"  # 2-guide architecture (companion ADR; introduces WRITEUP_PAPER + WRITEUP_NARRATIVE)
---

# ADR-078: EXECUTIVE_SUMMARY absorbed into README

## Status

Accepted.

## Context

Before v1.3.0, the reading-guide architecture (per ADR-053 + ADR-054 +
ADR-061 + ADR-062) had 4 reader-facing distillation surfaces:

| File | Role | Length |
|---|---|---|
| `index.qmd` | 60-sec landing (depth 0) | ~140 lines |
| `README.md` | Repo-level orientation (depth 0.5) | ~141 lines |
| `EXECUTIVE_SUMMARY.md` | 1-page narrative distillation (depth 1) | ~152 lines |
| `WRITEUP.md` | Methodology hub (depth 1) | ~280 lines |

Plus `RESULTS.md` (~300 lines; tables + commentary) and 8 WRITEUP/
spokes (deep-dive references).

Same content (headline finding, mechanism, direct-detection check,
metrics primer) was rendered with different prose on `EXECUTIVE_SUMMARY`,
`index`, `WRITEUP`, and `RESULTS`. User flagged the cumulative effect
in 2026-05-21 feedback:
> "neither a narrative structure to quarto nor is there an academic
> structure like in a journal paper — it seems random parts of the
> results all over the place with no story"

Root-cause analysis showed: the duplication was incidental drift, not
designed redundancy. Each surface evolved independently across the
v1.0.x patch trail.

The v1.3.0 architectural response (per ADR-079) introduces 2 reader-
style guides (`WRITEUP_PAPER.md` academic IMRAD + `WRITEUP_NARRATIVE.md`
narrative arc), each covering the same content in its native style.
This makes EXECUTIVE_SUMMARY.md redundant: the depth-1 surface is now
served by 2 reader-style guides, not a single distillation.

## Decision

Absorb EXECUTIVE_SUMMARY content into README as a top-fold
§"Executive summary" section + retire EXECUTIVE_SUMMARY.md.

### README structure after absorption

```
README.md
├── Title + badges + 1-paragraph framing
├── § Executive summary (NEW; absorbed from EXECUTIVE_SUMMARY.md)
│   ├── Bottom line (2-sided result)
│   ├── Pooled OOD AUPRC table
│   ├── Mechanism: lexical overfitting + label-relevance shift
│   └── Direct detection check tables
├── § Read the site (chooser between WRITEUP_PAPER and WRITEUP_NARRATIVE)
└── <details> Below the fold (existing repo-orientation content)
    ├── What this project is
    ├── What "OOD" means here
    ├── Why trust the result
    ├── Reproduce — three tiers
    ├── How this project thinks
    ├── Repository map
    ├── Key terms (quick reference)
    ├── What it does not claim
    └── Submission anchors
```

### EXECUTIVE_SUMMARY.md retirement

- File deleted from the working tree at v1.3.0 PR-1.
- `_quarto.yml` render allowlist entry removed.
- Navbar `Reference` dropdown entry removed.
- Sidebar `Entry` section entry removed.
- Historical reviewer URL pin (`tree/v1.0.0` per ADR-033) preserves the
  v1.0.0 EXECUTIVE_SUMMARY.md unchanged; external academic citations
  of EXECUTIVE_SUMMARY remain resolvable at the historical pin.
- Cross-references in WRITEUP, RESULTS, index, READING_GUIDE,
  docs/for-hiring-managers, and ADRs (where they cite
  EXECUTIVE_SUMMARY.md as a reading-path target) updated to point at
  README.md#executive-summary (the new canonical anchor).

### Supersession

This ADR supersedes ADR-053 on **dimension 2 ("two-entry-artifacts:
EXECUTIVE_SUMMARY + index.qmd")** only. ADR-053 dimensions 1 (Quarto
reading-guide architecture), 3 (3-reading-paths), 4 (Headline-finding-
block requirement), and 5 (interpretation-pedagogy + pointer-convention)
are unchanged. The supersession is on a single axis; ADR-053 remains
the authoritative reading-guide governance ADR for its other dimensions.

ADR-054 (RESULTS.md as third entry artifact) and ADR-061 (Quarto navbar/
sidebar restructure) are separately superseded by ADR-079 (the
companion 2-guide architecture ADR for v1.3.0). ADR-078 + ADR-079
together discharge the v1.3.0 restructure governance.

## Consequences

- 1-page distillation is canonical at `README.md#executive-summary`;
  no competing distillation surface exists on the depth-1 reading-
  guide layer.
- Reader path simplifies: index (60-sec) → README (full executive
  summary + chooser) → either guide (PAPER or NARRATIVE).
- Maintenance burden reduces: any future result update touches README
  only (was: README + EXECUTIVE_SUMMARY + index headline + WRITEUP §6).
- Historical reviewer link to EXECUTIVE_SUMMARY remains stable via
  the `tree/v1.0.0` pin (per ADR-033 + ADR-064-era reviewer URL pin
  discipline). Reviewer URL pin is now `tree/v1.2.8`; reviewers
  navigating to EXECUTIVE_SUMMARY through current-state links would
  hit a 404 — mitigated by the README anchor + the redirect that
  could be added at v1.3.x if needed.
- v1.2.14 `audit_adr_count_claims.py` invariant catches the cascade
  effect of ADR-078's creation (76 → 77 → 78 reader-facing ADR count
  claims); this is the third time the invariant has fired correctly
  in the v1.2.13/14/15/16 → v1.3.0 trail.

## Alternatives Considered

1. **Keep EXECUTIVE_SUMMARY.md as the 1-page distillation surface;
   make WRITEUP_PAPER + WRITEUP_NARRATIVE deeper than it.** Rejected
   per Q1.1 lock — would leave 4 reader-facing distillation surfaces
   (index + README + EXECUTIVE_SUMMARY + 2 guides = 5 total). Worsens
   the redundancy problem the v1.3.0 restructure is solving.
2. **Make EXECUTIVE_SUMMARY.md a stub-redirect to README#executive-
   summary.** Rejected — adds a redirect-page surface; better to
   delete the file outright since the README anchor + the historical
   `tree/v1.0.0` pin together cover both current and historical use.
3. **Move EXECUTIVE_SUMMARY content into index.qmd (not README).**
   Rejected — README is the canonical repo-root entry for GitHub
   readers; index.qmd is the canonical live-site landing. Both should
   show the executive summary; the index gets a brief inline summary
   (60 seconds) and the README gets the full version (depth 1).
4. **Defer this absorption to v1.3.1.** Rejected — ADR-079's 2-guide
   architecture is the v1.3.0 restructure; absorbing
   EXECUTIVE_SUMMARY in the same release is the natural pairing
   (separate ADRs but companion architecture changes).

## Linked ADRs

- **ADR-033** (GitHub release strategy + reviewer URL pin): preserves
  EXECUTIVE_SUMMARY.md at the historical `tree/v1.0.0` pin for
  external academic citations.
- **ADR-053** (Reading-guide governance + newcomer paths): superseded
  on dimension 2 ("two-entry-artifacts") only. Other dimensions
  unchanged.
- **ADR-054** (RESULTS.md as third entry artifact): separately
  superseded by ADR-079 on the entry-artifacts axis (RESULTS becomes
  tables-only appendix, no longer an entry artifact at v1.3.0).
- **ADR-061** (Quarto navbar/sidebar restructure): separately
  superseded by ADR-079 (navbar gains "Academic paper" + "Narrative
  arc" entries; sidebar "Entry" section drops EXECUTIVE_SUMMARY).
- **ADR-062** (Quarto writeup clarity + canonical figures): preserved
  unchanged; ADR-062's narrative-clarity work is reflected in both
  WRITEUP_PAPER and WRITEUP_NARRATIVE.
- **ADR-079** (2-guide reader architecture for v1.3.0): companion ADR
  introducing WRITEUP_PAPER.md + WRITEUP_NARRATIVE.md; together with
  ADR-078 discharges the v1.3.0 restructure governance.

## Transcript

Transcript file (gitignored per AGENTS.md): the 2026-05-21 v1.3.0
planning session that diagnosed the jumbled-structure complaint,
walked through 3 → 2 guide reduction via /exploring-options, and
locked the architecture. `/save-transcript 2026-05-21__v1-3-0-
two-guide-restructure` will land this file post-v1.3.0 close.
