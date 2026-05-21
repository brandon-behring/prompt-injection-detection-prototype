---
adr_id: "071"
slug: adr-cross-reference-slug-sweep-closure
title: Execute the slug-sweep authorized by ADR-067 + ADR-068 + ADR-069 that was never actually completed in any prior commit
date: 2026-05-20
status: Accepted
claim_id: CLAIM-071
claim: >-
  ADR-067 + ADR-068 + ADR-069 + ADR-070 (2026-05-19, the four-ADR
  immutability-relaxation chain) authorized four narrow classes of
  in-place editorial fixes to immutable ADRs: slug typos (Class A),
  broken external references (Class B), publisher-URL to DOI
  canonicalization (Class C), render-only markdown corrections
  (Class D). The Class A authorization specifically said the slug
  substitutions would land in v1.2.2 and v1.2.6 commits, with
  corresponding patterns deleted from `.lycheeignore`. The
  substitution commits never landed.
  As of 2026-05-20 audit re-verification, 59 broken
  `decisions/ADR-NNN-<wrong-slug>.md` references still ship across
  21 ADR files; ADR-067's own §C1 substitution table contains 14
  live broken markdown links in its wrong-slug column; the
  `.lycheeignore` patterns ADR-067 §C3 said would be removed at
  v1.2.2 are still present.
  This ADR closes the loop: applies the full slug-mapping table
  derived from ADR-067 §C1 + the post-2026-05-20 audit extension
  (33 patterns total mapping to ~15 canonical files) across all
  22 affected ADRs; strips the local-fs path leak in ADR-040
  (`/home/brandon_behring/.claude/plans/twinkly-weaving-puppy.md`,
  3 occurrences); removes the corresponding `.lycheeignore`
  patterns; and removes the 2 ADR-029 misattribution references
  (which cited a non-existent "immutability ADR-029" slug — actual
  ADR-029 is `test-marker-strategy-four-marker-ratification`) per
  ADR-067 §C2.5 "remove without replacement" rule.
source: 2026-05-20 audit re-verification; ADR-067 §C1 canonical
  mapping table + post-2026-05-20 audit extension; user request
  to close the documented-but-unexecuted authorization loop.
closing_commit: 37c2b32
transcript:
supersedes:
  - "067"  # on the "the sweep has been applied" claim only — narrow-relaxation methodology unchanged
  - "068"  # same axis — Class B broken external references; the prose-replacement at ADR-025 line 13 is applied
  - "069"  # same axis — Class C publisher-URL to DOI canonicalization; ADR-071 covers the documented mappings only
superseded_by:
acceptance_criterion: >-
  `git grep "decisions/ADR-[0-9]\{3\}-[a-z0-9-]*\.md"
  decisions/ADR-*.md` shows zero references to non-existent ADR
  files (all targets resolve to existing canonical filenames).
  The `.lycheeignore` no longer contains the broken-slug patterns
  ADR-067 §C3 promised to remove at v1.2.2. The
  `/home/brandon_behring/.claude/plans/` path no longer appears in
  any committed file. CI lychee check passes on `decisions/` with
  the smaller ignore set.
linked_adrs:
  - "067"
  - "068"
  - "069"
  - "070"
  - "029"  # the misattribution target (test-marker-strategy)
  - "040"  # local-fs path leak source
---

# ADR-071: ADR cross-reference slug-sweep closure

## Status

Accepted.

## Context

The 2026-05-19 four-ADR immutability-relaxation chain (ADR-067 through
ADR-070) authorized four narrow classes of in-place editorial fixes to
immutable ADRs. Each ADR documented the authorization + the canonical
substitution patterns; ADR-067 §C1 in particular includes a 14-row
canonical mapping table covering the most common broken slug references.

The 2026-05-20 audit re-verification revealed that the *authorizations*
landed in the audit trail but the corresponding *substitution commits*
never landed in the working tree:

- 59 broken `decisions/ADR-NNN-<wrong-slug>.md` markdown references
  still ship across 21 ADR files (re-grep on the v1.2.8 HEAD)
- ADR-067 §C1's own canonical mapping table contains 14 live broken
  markdown links in its wrong-slug column (the table is presented as
  "here are the slugs that need fixing" — the broken column was not
  removed after the fix landed because the fix never landed)
- The `.lycheeignore` patterns ADR-067 §C3 said would be removed at
  v1.2.2 + v1.2.6 are still present in the file
- ADR-040 line 9 + line 38 + line 166 still cite a local-fs path
  `/home/brandon_behring/.claude/plans/twinkly-weaving-puppy.md` that
  ADR-067 Class A would have stripped under the "factual-typo /
  unintended-leak" reading (the local plan file is gitignored;
  emailed separately at submission per AGENTS.md transcript
  discipline; should not be publicly referenced in immutable ADRs)
- 2 references to non-existent slugs `ADR-029-adr-immutability-and-
  supersession-discipline.md` + `ADR-029-immutable-adrs-supersede-
  dont-edit.md` survive in ADR-067 itself; the actual ADR-029 is
  `test-marker-strategy-four-marker-ratification`, not an
  immutability ADR. These were already flagged in ADR-067 §C2.5 for
  "remove without replacement" treatment.

A reader following any of the 59 broken `[link](path)` cross-references
inside `decisions/` gets a GitHub 404. The four-ADR relaxation chain
documents the *intent* to fix this but the working tree never reflected
the documented intent.

## Decision

Apply the canonical slug-mapping table across the 22 affected ADRs
(21 originally surfaced + ADR-064 which carries 6 broken refs flagged
in the v1.2.8 audit but not yet swept). The full mapping covers 33
broken patterns resolving to 15 canonical filenames:

**ADR-001:** `ADR-001-brief-alignment-tight-calendar-with-fallback-ladder.md`
→ `ADR-001-submission-deadline-and-scope-ambition.md`

**ADR-005:** 4 wrong variants → `ADR-005-methodology-principles.md`
(`attack-class-scope-and-three-state-contamination-taxonomy`,
`honest-methodology-over-claimed-best-numbers`, `methodology-over-metrics`,
`project-level-methodology-principles`)

**ADR-006:** 3 wrong variants → `ADR-006-headline-metrics-and-statistical-apparatus.md`
(`headline-metrics-and-statistical-floor`, `single-seed-protocol-for-comparative-claims`,
`statistical-multi-seed-protocol`)

**ADR-013, ADR-015:** 1 wrong each → canonical bundles

**ADR-016:** 2 wrong variants → `ADR-016-data-design-bundle.md`

**ADR-018, ADR-021, ADR-023, ADR-031, ADR-032, ADR-033, ADR-036,
ADR-037, ADR-042, ADR-043, ADR-046:** 1 wrong variant each →
canonical filename

**ADR-019:** 3 wrong variants → `ADR-019-lora-and-transformer-training-recipe.md`

**ADR-020:** 3 wrong variants → `ADR-020-compute-infrastructure-and-cost-discipline.md`

**ADR-030:** 2 wrong variants → `ADR-030-deliverable-format-quarto-html-site.md`

**Special: ADR-029 misattributions** (2 patterns). Per ADR-067 §C2.5,
replace the wrong-slug ref with the bare `ADR-029` identifier (no link
target). The narrative around them stays; only the misattributed link
target is stripped. Reason: the actual ADR-029 is
`test-marker-strategy-four-marker-ratification`; the "immutability"
methodology is documented in `CLAUDE.md` + `AGENTS.md` + ADR-005, not
in any standalone ADR-029-immutability file (which never existed).

**Special: ADR-040 local-fs path strip** (3 occurrences on lines 9, 38,
166). Replace `/home/brandon_behring/.claude/plans/twinkly-weaving-puppy.md`
with neutral prose: "the Phase 0 audit synthesis plan file (gitignored;
emailed separately at submission)". Same content meaning; no
local-filesystem-path leak in a public ADR.

**`.lycheeignore` cleanup:** Remove any lines matching the 33
broken-slug patterns + the 2 ADR-029 misattribution patterns. Smaller
`.lycheeignore` reduces ongoing maintenance friction + makes the
remaining ignored patterns more legibly load-bearing.

Commit message format follows ADR-067 §B3 + ADR-068 §B3 type-prefixed
discipline: `chore(adr): ADR-071 slug-sweep closure — apply 67 §C1
canonical mappings + extension`.

## Consequences

- Lychee CI passes on a smaller `.lycheeignore` (smaller surface to
  maintain; remaining ignores are clearly justified)
- The 4-ADR relaxation chain (067-070) becomes load-bearing rather
  than ceremonial — it documents the rules that ADR-071 actually
  followed in execution
- Reader experience improves materially: a reviewer clicking any of
  the 59 broken refs gets the correct target
- No methodology decisions change — every fix is editorial (slug
  typo, factual-typo strip, link-target removal); claim text, status,
  numeric values, acceptance criteria, prose all unchanged
- Resolves the "documented intent without execution" optic that
  currently makes the 067-070 chain look like process-ceremony
  without follow-through
- ADR-067's own §C1 mapping table is updated: the wrong-slug column
  is rewritten to use the canonical filenames (the table now reads
  as a *historical record* of "here are the fixes applied" rather
  than "here are the fixes pending")

## Alternatives Considered

1. **Leave the 59 refs broken indefinitely.** Rejected — ADR-067
   explicitly authorizes the fix; not executing leaves the chain as
   documented intent with no payoff. A reviewer concludes either the
   rules are decorative or the author lost track of follow-through.
2. **One ADR per fix-class** (separate ADR-071 for slug-sweep, ADR-072
   for ADR-040 fs-path strip, ADR-073 for `.lycheeignore` cleanup).
   Rejected — would extend the 067-070 chain to 8+ ADRs; the
   consolidation pattern argues against this. Single ADR-071 covering
   all editorial corrections is cleaner.
3. **Skip the ADR; just do the rewrites under ADR-067's existing
   authorization.** Rejected — the immutability rule means even
   surface fixes need an authorizing record. ADR-067 wrote the
   authorization but never logged the execution. ADR-071 is the
   execution log + closes the audit loop.

## Linked ADRs

- ADR-067 (immutability narrow relaxation — Class A slug typos):
  superseded on the "applied" axis only; methodology unchanged
- ADR-068 (Class B broken external references): same supersession
  scope
- ADR-069 (Class C publisher-URL → DOI canonicalization): same
  supersession scope (covered the documented patterns; future
  publisher-URL fixes need separate ADR or extension)
- ADR-070 (Class D render-only markdown corrections): not superseded
  here; the markdown corrections it documents are out of scope for
  ADR-071's slug-focused execution
- ADR-029 (test-marker-strategy-four-marker-ratification): not
  superseded; ADR-071 strips misattribution refs that pointed at a
  non-existent immutability-ADR-029 slug
- ADR-040 (phase-0-audit-findings-and-assumption-backfill): not
  superseded; ADR-071 applies the local-fs-path strip authorized
  under Class A "unintended-leak" reading

## Transcript

Transcript file (gitignored per AGENTS.md): the 2026-05-20 audit
re-verification cycle + slug-sweep execution captured in the audit
report at `~/notes/prompt-injection-audit-2026-05-20.md` (consumer
side) and the appendix at
`~/notes/prompt-injection-audit-2026-05-20-adr-appendix.md`.
