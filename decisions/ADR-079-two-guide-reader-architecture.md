---
adr_id: "079"
slug: two-guide-reader-architecture
title: Two-guide reader architecture (academic IMRAD + narrative arc) replacing the single-hybrid WRITEUP for v1.3.0
date: 2026-05-21
status: Accepted
claim_id: CLAIM-079
claim: >-
  User feedback 2026-05-21 diagnosed the existing single-guide
  architecture as "neither a narrative structure nor an academic
  structure like in a journal paper" with "random parts of results
  all over the place with no story" — the existing WRITEUP.md was a
  loose-narrative-with-numbered-sections hybrid, methodology placed
  AFTER findings (WRITEUP §9 vs §7), with the same content rendered
  3-4 times across index.qmd + EXECUTIVE_SUMMARY.md + WRITEUP.md +
  RESULTS.md in different framings. The v1.3.0 architectural response
  introduces **two reader-style guides**: WRITEUP_PAPER.md
  (academic IMRAD: Abstract / Introduction / Background / Methods /
  Results / Discussion / Limitations / Conclusion / References;
  formal academic register; passive voice; technical terminology
  with on-first-use definitions cross-referenced to docs/GLOSSARY.md)
  + WRITEUP_NARRATIVE.md (story arc: Hook / Setup / Investigation /
  Revelation / Other findings / Implications / Epilogue; plain-
  English first-person plural 'we' register; active voice; minimal
  jargon, defined on first use + cross-referenced to docs/GLOSSARY.md).
  Both guides cover the same content (problem, methodology, all 7
  findings, mechanism, limitations); the register and structure
  differ. Each guide treats the headline finding natively per its
  style (academic = Finding 3 of 7 equal-weight; narrative = Act-3
  dramatic revelation). Companion: ADR-078 absorbs EXECUTIVE_SUMMARY
  content into README. The current WRITEUP.md becomes a 1-page
  router stub directing readers to either guide; preserves backward
  references from 8 WRITEUP/ spokes + ADRs without breaking links.
  index.qmd rebuilt as 60-sec hook + chooser. READING_GUIDE.md
  rebuilt as 2-path router. Decision affects presentation surfaces
  only; no methodology / model / data / compute change.
source: User feedback 2026-05-21 "lets do one narrative one academic
  and the readme which has the executive summary. The academic and
  narrative should still cover everything, but the style can be
  different. Does that make any sense?" — locked via /exploring-
  options Q1 (3-guide initial scope) + Q1-revisit (reduced to 2
  guides + "lets think for a second" deliberation) + 4-question
  follow-on slate (file naming + sub-PR strategy + authorship +
  voice register).
closing_commit:
transcript:
supersedes:
  - "053"  # on the "reading-guide architecture dimension 1 (two entry artifacts: EXECUTIVE_SUMMARY + index.qmd)" axis only — superseded jointly with ADR-078; ADR-053 dimensions 3 (3-reading-paths) + 4 (Headline-finding-block) + 5 (interpretation-pedagogy + pointer-convention) unchanged
  - "054"  # same axis as ADR-053 supersession above — on the "RESULTS.md as third entry artifact" framing axis only; RESULTS becomes an appendix/tables-only reference in v1.3.0, not an entry artifact. Decision-axis only.
  - "061"  # same axis — on the "Quarto site navigation restructure" axis only; navbar gains 'Academic paper' + 'Narrative arc' entries; sidebar 'Entry' section drops EXECUTIVE_SUMMARY; 'Methodology guides (pick a style)' section introduces the two guides. Decision-axis only.
superseded_by:
acceptance_criterion: >-
  `ls WRITEUP_PAPER.md WRITEUP_NARRATIVE.md` returns both files.
  `head -3 WRITEUP_PAPER.md` shows the academic IMRAD title +
  reader-note pointing at WRITEUP_NARRATIVE.md as the alternative.
  `head -3 WRITEUP_NARRATIVE.md` shows the narrative title + reader-
  note pointing at WRITEUP_PAPER.md. `head -5 WRITEUP.md` shows the
  stub-redirect router language ("Pick how you want to read this").
  `head -5 index.qmd` shows the 60-sec hook with chooser between the
  two guides. `head -5 READING_GUIDE.md` shows the 2-path router.
  `_quarto.yml` navbar Methodology dropdown lists "Academic paper
  (IMRAD)" + "Narrative arc (story)" + "Router (pick a guide)".
  `_quarto.yml` sidebar "Methodology guides (pick a style)" section
  lists the same. `scripts/audit_adr_count_claims.py` exits 0
  (catches the 78→79 cascade across reader-facing surfaces).
  `scripts/audit_superseded_by_backlinks.py` exits 0 (ADR-079 →
  ADR-053+054+061 supersession edges correctly classified as axis-
  only via comment heuristic).
linked_adrs:
  - "004"  # reviewer-profile-and-hub-and-spoke-writeup (preserved; 8 WRITEUP/ spokes unchanged as deep-dive references)
  - "033"  # release strategy + reviewer URL pin (preserves WRITEUP.md jumbled hybrid at tree/v1.0.0 for historical reviewer)
  - "053"  # reading-guide governance (superseded on entry-artifacts axis)
  - "054"  # RESULTS as third entry artifact (superseded on entry-artifacts axis)
  - "061"  # navbar/sidebar restructure (superseded by v1.3.0 navbar + sidebar updates)
  - "062"  # writeup clarity + canonical figures (preserved; the canonical figures + reader-facing prose-style work informs both new guides)
  - "064"  # writeup hiring-manager clarity (preserved; the 'for-hiring-managers.md is the only first-person surface' precedent extended to WRITEUP_NARRATIVE first-person-plural)
  - "078"  # EXECUTIVE_SUMMARY absorbed into README (companion ADR; together with ADR-079 discharges v1.3.0 restructure governance)
---

# ADR-079: Two-guide reader architecture

## Status

Accepted.

## Context

User feedback in the 2026-05-21 v1.3.0 planning session diagnosed
the existing single-guide architecture (WRITEUP.md hub + 8 WRITEUP/
spokes + EXECUTIVE_SUMMARY.md + RESULTS.md + index.qmd) as:

> "neither a narrative structure to quarto nor is there an academic
> structure like in a journal paper — it seems random parts of the
> results all over the place with no story. I had a headline and
> still wanted to make sure the other results were shown — but it
> feels so jumbled"

Root-cause analysis from the structural heading map confirmed two
distinct failures:

1. **Cross-page redundancy.** The same content (headline finding,
   mechanism, direct-detection check, metrics primer) was rendered
   in 3-4 different framings across `index.qmd` + `EXECUTIVE_SUMMARY` +
   `WRITEUP` + `RESULTS`. Drift was incidental — each surface evolved
   independently across the v1.0.x patch trail rather than being
   designed as one coherent reader experience.

2. **Within-page register inconsistency.** WRITEUP.md mixed
   summary-style (executive-y) and detail-style (academic-y) without
   committing to either register. Methodology (§9 "in one paragraph")
   appeared AFTER Findings (§7) — backwards from academic IMRAD
   convention. The 7 findings were enumerated (academic-style) but
   framed narratively (story-style sentences with bolded takeaways),
   making each finding read like a story chapter even though they
   were listed like academic results.

The diagnosis: the existing WRITEUP was an enthusiastic-explainer
wearing an ill-fitting academic suit. Not coherent as a paper; not
coherent as a story.

## Decision

Adopt a **two-guide reader architecture** for v1.3.0 in which both
guides cover the same content but in different reading-style registers.
Companion to ADR-078 (EXECUTIVE_SUMMARY absorbed into README).

### Architecture

```
README.md                       # top-fold executive summary (per ADR-078) + 2-guide chooser
index.qmd                       # 60-sec landing + 2-guide chooser
WRITEUP_PAPER.md (NEW)          # ACADEMIC: IMRAD discipline (~530 lines)
WRITEUP_NARRATIVE.md (NEW)      # NARRATIVE: 5-act story (~570 lines)
WRITEUP.md                      # STUB-REDIRECT: 1-page router preserving backward refs
RESULTS.md                      # APPENDIX: tables-only (cross-ref'd by both guides; trim deferred to v1.3.1 if needed)
READING_GUIDE.md                # NAVIGATION: 2-path router
WRITEUP/data-decisions.md       # UNCHANGED: 8 domain spokes serve as deep-dive references for both guides
WRITEUP/eval-design.md          # ...
WRITEUP/model-rungs.md
WRITEUP/methodology-guarantees.md
WRITEUP/threshold-policy.md
WRITEUP/reference-scorer-audit.md
WRITEUP/reproducibility.md
WRITEUP/limitations-and-future-work.md
```

### Guide content outlines

**WRITEUP_PAPER.md** (academic IMRAD; ~530 lines):
- §0 Abstract (5-sentence structured: motivation / approach / finding
  / mechanism / implication)
- §1 Introduction (research question + contribution)
- §2 Background (prompt-injection landscape; existing detectors; data
  sources)
- §3 Methods (4 subsections: LODO splits / model rungs / evaluation
  slate / statistical apparatus)
- §4 Results (7 numbered equal-weight findings; headline = Finding 3
  of 7; no dedicated headline section)
- §5 Discussion (mechanism: lexical overfitting + label-relevance
  shift + implications)
- §6 Limitations (6 subsections incl. incomplete-experiment status)
- §7 Conclusion
- §8 References (ADR refs + external bibliography + project artifacts)
- Glossary (in-paper definitions; cross-ref to docs/GLOSSARY.md)

**WRITEUP_NARRATIVE.md** (narrative arc; ~570 lines):
- Act 0 — Hook (the surprise: anti-correlation; dramatic opening)
- Act 1 — Setup (what we wanted to know + threat-model context +
  out-of-scope)
- Act 2 — Investigation (LODO discipline + cross-family slate +
  5-rung detector ladder + statistical apparatus)
- Act 3 — Revelation (headline finding rendered as dramatic third-
  act reveal: AUPRC at floor + AUROC below 0.5 anti-correlation +
  mechanism interpretation)
- Act 4 — The other findings (Findings 4-7 as supporting cast in
  equal-weight enumeration; preserves the "don't bury the other
  results" requirement)
- Act 5 — Implications (3 cautious claims + 5 future-work priorities
  + broader-field implication)
- Epilogue — Limits + reproduction instructions + dig-deeper pointers
  + closing note

### Headline prominence per style

Each guide treats the headline finding natively per its style (per
the v1.3.0 plan Q4 lock):

- **PAPER**: Finding 3 is one of 7 equal-weight numbered results in
  §4 Results. Academic neutrality; no dedicated headline section.
- **NARRATIVE**: Headline is the dramatic Act-3 revelation. Story-
  arc convention demands a climactic third-act reveal; this is it.

The structural variation IS the reader-experience difference. Same
factual content; different rhetoric. This resolves the "headline yet
other results shown" tension explicitly — both guides cover all 7
findings; the headline gets prominence native to the guide's style.

### Voice register per Q4 lock

- **PAPER**: formal academic. Passive voice ("The methodology
  applies..."); technical terminology; numbered subsections;
  explicit confidence intervals; cross-references to ADRs and
  external papers; on-first-use jargon definitions + cross-ref to
  GLOSSARY.
- **NARRATIVE**: plain-English first-person plural ('we'). Active
  voice ("We wanted to know..."); minimal jargon; defined on first
  use + cross-ref to GLOSSARY. Extends the precedent set by
  docs/for-hiring-managers.md (per ADR-064: the only first-person
  surface) to first-person-plural for narrative.

### Both guides explain jargon

Both guides define jargon on first use and cross-reference the
canonical glossary at docs/GLOSSARY.md. This means PAPER doesn't
assume the reader knows all the ML terms (academic reviewer might be
from a different ML subfield), and NARRATIVE's accessibility doesn't
drop precision (story reader still gets accurate definitions). The
Q4 lock comment: "in both we should still explain jargon and include
the glossary."

### WRITEUP.md retired as stub-redirect

The current WRITEUP.md (the jumbled hybrid) becomes a 1-page stub:
"Pick how you'd like to read this: `[academic](../WRITEUP_PAPER.md)`
or `[narrative](../WRITEUP_NARRATIVE.md)`". This preserves backward references
from the 8 WRITEUP/ spokes + ADRs without breaking links. The
historical WRITEUP.md content is accessible at the reviewer URL pin
(`tree/v1.2.8`) per ADR-033.

### Supersession scope

This ADR supersedes ADR-053, ADR-054, ADR-061 on **specific reading-
guide architecture axes only**, not on their full decision content:

- **ADR-053**: superseded on dimension 1 ("Quarto reading-guide
  architecture" — the two-entry-artifact framing). Dimensions 3
  (3-reading-paths), 4 (Headline-finding-block requirement), and 5
  (interpretation-pedagogy + pointer-convention) unchanged. ADR-053
  dimension 2 was separately superseded by ADR-078 (EXECUTIVE_SUMMARY
  absorption).
- **ADR-054**: superseded on the "RESULTS.md as third entry artifact"
  framing. RESULTS becomes an appendix / tables-only reference in
  v1.3.0, not an entry artifact. ADR-054's body content (5 sections
  defining RESULTS structure) survives in form even though the
  artifact role changes.
- **ADR-061**: superseded on the navbar/sidebar restructure axis.
  v1.3.0 navbar gains "Academic paper" + "Narrative arc" entries;
  sidebar "Entry" section drops EXECUTIVE_SUMMARY; new "Methodology
  guides (pick a style)" section introduces the two guides.

ADR-062 (writeup clarity + canonical figures) is preserved unchanged;
the canonical figures + reader-facing prose-style work informs both
new guides.

ADR-004 (reviewer-profile-and-hub-and-spoke-writeup) is preserved
unchanged; the 8 WRITEUP/ spokes still serve as deep-dive references
for both guides.

### SUBMISSION_AUDIT.md cascade

This ADR's creation moves the ADR count from 78 → 79. The v1.2.14
`audit_adr_count_claims.py` invariant catches reader-facing ADR-count
claims that would go stale:
- `README.md`: 78 → 79
- `docs/for-hiring-managers.md`: 78 → 79
- `WRITEUP/methodology-guarantees.md`: 78 → 79
- `CLAUDE.md`: 78 → 79

`SUBMISSION_AUDIT.md` regenerates via `scripts/regenerate_audit.py`;
CLAIM count goes 78 → 79. Fourth time the audit_adr_count_claims
invariant has correctly fired across the v1.2.13/14/15/16 → v1.3.0
trail — validates v1.2.14 design intent.

## Consequences

- Reader path simplifies: index (60-sec) → README (full executive
  summary + chooser) → either guide (PAPER or NARRATIVE) → 8 spokes
  (depth). Each layer has a unique role; no cross-layer redundancy.
- Maintenance burden reduces in the long run (single-source-of-truth
  per surface); doubles temporarily during v1.3.x while both guides
  exist (any future result update touches PAPER + NARRATIVE +
  RESULTS; mitigation: results are frozen at v1.0.0, so write-once
  is acceptable).
- Reader-experience differentiation: academic reviewer gets a paper;
  story reader gets a story; both get the same content.
- The "headline but also other results" tension is structurally
  resolved: PAPER treats all 7 findings equal-weight (Finding 3 is
  just one of them); NARRATIVE gives the headline dramatic Act-3
  prominence + Acts 4's equal-weight enumeration of the other 6.
- Historical reviewer link to WRITEUP.md remains stable via the
  `tree/v1.2.8` pin (per ADR-033). Current-state WRITEUP.md is a
  redirect stub; readers following links land on the chooser and
  pick a guide.
- audit_adr_count_claims invariant catches the cascade (78→79); 4th
  time it has fired correctly in the trail.
- audit_superseded_by_backlinks invariant catches the ADR-079 →
  ADR-053/054/061 supersession edges; comment-heuristic classifies
  them as axis-only (correct).

## Alternatives Considered

1. **Three guides** (academic + narrative + hybrid). Initial Q1 lock
   was 3 guides; user reconsidered ("lets think for a second") +
   reduced to 2 + README-absorbs-EXEC-SUMMARY. Rationale: 3 guides
   produced 3× content duplication for a frozen artifact;
   well-executed 2 guides serve the same reader-types without the
   third "hybrid" guide (since hybrid is what the current jumbled
   WRITEUP.md was).
2. **One guide done well** (restructure WRITEUP to clean hybrid +
   add README Abstract). Rejected per Q1 lock — user prefers
   reader-type choice between paradigms. Hybrid alone doesn't
   address the "neither narrative nor academic" complaint
   structurally.
3. **Minimal triage** (kill redundancy, no restructure). Rejected
   per Q1 lock — symptomatic fix only; doesn't address the
   user-stated need for a story or academic structure.
4. **Pure academic IMRAD only** (one guide). Rejected — loses the
   story-reader path. The "for-hiring-managers" persona page exists
   but is only 5-min depth; the NARRATIVE guide serves the longer
   story-style read.
5. **Pure narrative arc only** (one guide). Rejected — loses the
   academic-reviewer path. Defensibility at peer review weaker
   without IMRAD discipline.
6. **Add MIGRATION.md mapping old WRITEUP sections to new guides**.
   Considered for v1.3.1; not in v1.3.0 scope. The WRITEUP.md
   stub-redirect + the historical reviewer URL pin together cover
   the migration use case.

## Linked ADRs

- **ADR-004** (Reviewer profile + hub-and-spoke writeup): preserved
  unchanged. The 8 WRITEUP/ spokes still serve as deep-dive
  references; the "hub" is now distributed between WRITEUP_PAPER and
  WRITEUP_NARRATIVE (cited from both as "WRITEUP/ spokes").
- **ADR-033** (Release strategy + reviewer URL pin): preserves the
  v1.0.0 EXECUTIVE_SUMMARY.md and v1.0.0 WRITEUP.md hybrid at the
  historical reviewer pin. v1.3.0 ships on live site + main only.
- **ADR-053** (Reading-guide governance): superseded on dimension 1
  axis only (entry artifacts framing); other dimensions unchanged.
- **ADR-054** (RESULTS as third entry artifact): superseded on the
  entry-artifacts framing axis. RESULTS becomes appendix/reference,
  not an entry artifact.
- **ADR-061** (Navbar/sidebar restructure): superseded on the
  navbar/sidebar structure axis. v1.3.0 introduces "Methodology
  guides (pick a style)" sidebar section + navbar entries for the
  two guides.
- **ADR-062** (Writeup clarity + canonical figures): preserved.
  Canonical figures inform both new guides.
- **ADR-064** (Writeup hiring-manager clarity): preserved. First-
  person-precedent at for-hiring-managers.md extended to NARRATIVE's
  first-person-plural.
- **ADR-078** (EXECUTIVE_SUMMARY absorbed into README): companion
  ADR for v1.3.0. Together with ADR-079 discharges the v1.3.0
  restructure governance.

## Transcript

Transcript file (gitignored per AGENTS.md): the 2026-05-21 v1.3.0
planning session — diagnosis of the jumbled-structure complaint,
4-question /exploring-options walk (paradigm + headline prominence +
version bump + v1.2.16 cleanup), follow-up 4-question slate (file
naming + sub-PR strategy + authorship + voice register), user-
locked 2-guide architecture after "lets think for a second"
deliberation. `/save-transcript 2026-05-21__v1-3-0-two-guide-
restructure` will land this file post-v1.3.0 close.
