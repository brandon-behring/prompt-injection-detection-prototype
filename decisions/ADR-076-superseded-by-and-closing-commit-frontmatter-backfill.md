---
adr_id: "076"
slug: superseded-by-and-closing-commit-frontmatter-backfill
title: Backfill superseded_by on ADR-046 + ADR-054 + ADR-061 (→ ADR-062) + closing_commit on ADR-071-075 per ADR-072 frontmatter-backfill discipline
date: 2026-05-21
status: Accepted
claim_id: CLAIM-076
claim: >-
  ADR-062 (Quarto writeup clarity + canonical figures, v1.2.0)
  declares `supersedes: [ADR-046, ADR-054, ADR-061]` in its
  frontmatter (line 29) but the inverse links are missing — ADR-046
  has empty `superseded_by:`, ADR-054 has `superseded_by: []`,
  ADR-061 has `superseded_by: []`. The supersession-chain forward
  links are correct; the back-links are stale. Separately,
  ADR-071 through ADR-075 (all 2026-05-20 governance ADRs)
  ship with empty `closing_commit:` frontmatter fields though the
  ADR-072 precedent (closing_commit `8105f37`) establishes that
  closing_commit population is governance-relevant audit-trail data.
  REPO_AUDIT_2026-05-21.md §P1-6 + §P2 (ADR-071-075 empty
  closing_commit) surface both gaps. This ADR treats the empty-back-link
  + empty-closing_commit gaps as the same frontmatter-backfill
  narrow-relaxation class established by ADR-072 (extending the
  ADR-067-070 chain). Populates: (a) ADR-046 + ADR-054 + ADR-061
  `superseded_by: ["062"]` to mirror ADR-062's forward declaration;
  (b) ADR-071-075 `closing_commit:` with the verified SHAs from
  git log (ADR-071 = `37c2b32`, ADR-072 = `8105f37`,
  ADR-073 = `ba342c7`, ADR-074 = `14f0c05`, ADR-075 = `428971c`).
  No decision content changes; only audit-trail completeness is
  restored.
source: REPO_AUDIT_2026-05-21.md §P1-6 (ADR-062 missing
  superseded_by back-links) + §P2 (ADR-071-075 empty
  closing_commit). SHAs verified via
  `git log --oneline --diff-filter=A -- "decisions/ADR-<NNN>-*.md"`
  for the file-introduction commit of each ADR. ADR-072 precedent
  applied to the back-link + closing_commit-backfill axis.
closing_commit:
transcript:
supersedes:
  - "046"  # on the empty-superseded_by-frontmatter axis only; decision-axis supersession lies with ADR-062
  - "054"  # same axis
  - "061"  # same axis
  - "071"  # on the empty-closing_commit-frontmatter axis only; ADR-071 closure stands
  - "072"  # same axis
  - "073"  # same axis
  - "074"  # same axis
  - "075"  # same axis
superseded_by:
acceptance_criterion: >-
  `grep '^superseded_by' decisions/ADR-046-*.md decisions/ADR-054-*.md
  decisions/ADR-061-*.md` shows three `["062"]` values (was empty/[]).
  `grep '^closing_commit' decisions/ADR-071-*.md decisions/ADR-072-*.md
  decisions/ADR-073-*.md decisions/ADR-074-*.md decisions/ADR-075-*.md`
  shows five populated SHAs (was empty). `scripts/regenerate_audit.py
  --check` passes after the backfill with 76 CLAIM rows (ADR-076 added).
linked_adrs:
  - "046"  # superseded_by backfilled
  - "054"  # superseded_by backfilled
  - "061"  # superseded_by backfilled
  - "062"  # the decision-axis superseder of 046+054+061; this ADR mirrors its forward declaration
  - "071"  # closing_commit backfilled
  - "072"  # precedent ADR for frontmatter-backfill discipline + closing_commit backfilled
  - "073"  # immutability rule consolidated re-statement (this ADR cites its narrow-relaxation framework) + closing_commit backfilled
  - "074"  # closing_commit backfilled
  - "075"  # closing_commit backfilled
---

# ADR-076: Backfill superseded_by + closing_commit frontmatter for ADR-046 + ADR-054 + ADR-061 + ADR-071-075

## Status

Accepted.

## Context

`REPO_AUDIT_2026-05-21.md` (the v1.2.12-close audit) surfaced two
related frontmatter gaps:

**Gap A — empty `superseded_by:` on ADR-046 + ADR-054 + ADR-061**.
`decisions/ADR-062-quarto-writeup-clarity-and-canonical-figures.md:29`
declares `supersedes: [ADR-046, ADR-054, ADR-061]`. The forward link
is correct. But the three superseded ADRs themselves have empty
back-links:

- `ADR-046:13` — `superseded_by:` (empty bare value)
- `ADR-054:69` — `superseded_by: []` (empty list)
- `ADR-061:55` — `superseded_by: []` (empty list)

The convention is that supersession is bidirectional in frontmatter
— the precedent at ADR-023 (`superseded_by: ["056"]`), ADR-036
(`superseded_by: ["055", "059"]`), and ADR-053 (post-ADR-054 backfill;
`superseded_by: [ADR-054]`) shows the established pattern. ADR-054
§F itself documents this convention: *"ADR-053 frontmatter is edited
in-place to add `superseded_by: [ADR-054]` per the established
convention (ADR-050 had its frontmatter edited when ADR-052 narrowly
superseded R2; same pattern here)."* The same pattern should apply
to ADR-046 + ADR-054 + ADR-061 → ADR-062.

**Gap B — empty `closing_commit:` on ADR-071 through ADR-075**.
The five 2026-05-20 governance ADRs (cross-ref slug-sweep + frontmatter
backfill + immutability re-statement + redaction governance + full-FT
OOD narrative unification) all ship with empty `closing_commit:`
frontmatter. The ADR-072 precedent (`closing_commit: v1.0.9 ...` on
ADR-051 and `closing_commit: v1.0.3` on ADR-052) established that
closing_commit population is governance-relevant audit-trail data
that should be backfilled when missing. ADR-072 itself has empty
`closing_commit:` — but the file-introduction commit SHAs for the
ADR-071..075 set are all verifiable from git log, so the gap is
mechanically closable.

Both gaps fall outside the four narrow-relaxation classes documented
in `CLAUDE.md` §Narrow exceptions (slug typos / broken external refs /
publisher-URL canon / render-only markdown) but inside the ADR-072
class (empty-frontmatter-field backfill), which `ADR-073` consolidates
under the immutability-rule re-statement: *"frontmatter completeness
restoration on the closing_commit + supersession-link axis is in the
same narrow-relaxation discipline as ADR-067-070."*

## Decision

Treat the missing `superseded_by:` and `closing_commit:` fields as
the ADR-072 narrow-relaxation class — frontmatter-only edits that
restore audit-trail completeness without touching decision content.

**Gap A backfill** (superseded_by → ADR-062):

- `ADR-046:13` — `superseded_by:` → `superseded_by:` (bullet-list)
  ```yaml
  superseded_by:
    - "062"  # Quarto writeup clarity + canonical figures (v1.2.0)
  ```
- `ADR-054:69` — `superseded_by: []` → bullet-list with `"062"`
- `ADR-061:55` — `superseded_by: []` → bullet-list with `"062"`

**Gap B backfill** (closing_commit ← verified SHAs):

The SHAs are verified by `git log --oneline --diff-filter=A -- "decisions/ADR-<NNN>-*.md"`
which reports the commit that first added each file:

- `ADR-071:37` — `closing_commit:` → `closing_commit: 37c2b32`
  (commit `feat(adr): ADR-071 cross-reference slug-sweep closure`)
- `ADR-072:32` — `closing_commit:` → `closing_commit: 8105f37`
  (commit `feat(adr): ADR-072 backfill ADR-051+052 frontmatter and structural debt`)
- `ADR-073:25` — `closing_commit:` → `closing_commit: ba342c7`
  (commit `feat(adr): ADR-073 immutability rule consolidated re-statement`)
- `ADR-074:27` — `closing_commit:` → `closing_commit: 14f0c05`
  (commit `feat(adr): ADR-074 redact verbatim self-criticism quote in ADR-064`)
- `ADR-075:27` — `closing_commit:` → `closing_commit: 428971c`
  (commit `feat(adr): ADR-075 unify full-FT OOD drop rationale (ADR-050+052)`)

ADR-076's own `closing_commit:` stays empty per the same precedent
ADR-072 set (a future ADR can backfill it; this is the well-known
recursive gap that terminates because each backfill ADR only
backfills the PRIOR ones).

`transcript:` fields on ADR-071-075 (and ADR-076 itself) stay empty
per the project's "transcripts gitignored except `transcripts/README.md`"
discipline; the field is reserved for future-session continuations
and need not be populated retroactively.

`SUBMISSION_AUDIT.md` regenerates via `scripts/regenerate_audit.py`;
CLAIM count goes 75 → 76 (this ADR added).

## Consequences

- ADR-062's forward-link supersession is now mirrored by ADR-046 +
  ADR-054 + ADR-061's back-links; supersession-chain integrity is
  restored on this v1.2.0 cluster
- ADR-071-075 carry verifiable closing_commit SHAs; a future reviewer
  can trace each ADR to its landing commit without needing CHANGELOG
  triangulation
- The "ADR-NNN frontmatter completeness" sweep that REPO_AUDIT_2026-05-21
  flagged is closed for the v1.2.0-v1.2.9 cluster
- Future ADRs in the v1.2.x trail (ADR-076 onward) start with the
  same empty-closing_commit pattern by design; the recursive backfill
  cycle is documented as a known governance pattern in this ADR
- All 8 target ADRs' decision content is unchanged; only frontmatter
  audit-trail metadata is restored
- v1.2.13 patch's subsequent commits (C2 reader-facing accuracy sweep
  through C7 audit-trail close) can safely claim "76 ADRs" because
  this commit lands first

## Alternatives Considered

1. **Leave the gaps unfilled.** Rejected — REPO_AUDIT_2026-05-21
   surfaced both as P1 (gap A) and P2 (gap B). The audit's "lessons
   noted" section explicitly flagged that the ADR-072 backfill
   pattern is now load-bearing for this class of debt; ignoring it
   means the next audit re-surfaces the same finding.
2. **Two separate ADRs** (ADR-076 = superseded_by; ADR-077 =
   closing_commit). Rejected — same narrow-relaxation class, same
   precedent (ADR-072), same authorization. Single ADR is cleaner;
   the audit trail isn't materially improved by splitting. (The
   v1.2.13 planning session's /exploring-options Q3 split-vs-unified
   question for CLAUDE.md/AGENTS.md edits considered the same
   question and locked split-by-semantic-concern; this case differs
   because both gaps share the same narrow-relaxation class and ADR
   precedent.)
3. **Backfill via direct edit, no ADR-076.** Rejected — same
   reasoning ADR-072 documented: the immutability rule (consolidated
   in ADR-073) means even narrow editorial frontmatter edits need an
   authorizing ADR. ADR-072 set the precedent; ADR-076 extends it
   to the back-link + closing_commit axis.
4. **Populate ADR-076's own closing_commit immediately.** Rejected —
   chicken-and-egg. The closing_commit value would be this commit's
   SHA, which doesn't exist until the commit lands. ADR-072 chose
   to leave its own closing_commit empty for a future ADR; ADR-076
   follows the same convention.
5. **Treat the closing_commit gap as a fifth narrow-relaxation
   class** (alongside ADR-067-070), rather than as an ADR-072-class
   extension. Rejected — the four classes ADR-067-070 + ADR-073's
   consolidated re-statement are about textual fixes (slugs / external
   refs / publisher URLs / markdown). Frontmatter backfill is a
   structural-completeness class; ADR-072 is its precedent ADR.
   Keeping the same class taxonomy preserves the ADR-067-070-073
   chain's clarity.
6. **Auto-detect future supersession-backlink gaps via tooling**
   (e.g., a script that inverts every `supersedes:` declaration to
   check `superseded_by:` reciprocity). Rejected as v1.2.13 scope —
   the audit's "lessons noted" section recommends this for the
   portfolio repo; out-of-scope here because it requires designing
   a project-wide invariant + lint hook + regression-test contract.

## Linked ADRs

- **ADR-046** (Phase 4 analysis implementation bundle): `superseded_by`
  backfilled to `["062"]`. Decision content unchanged. ADR-062's §C
  documents the canonical-figures supersession that closes ADR-046's
  open implementation surface.
- **ADR-054** (Results page as third entry artifact extending ADR-053):
  `superseded_by` backfilled to `["062"]`. ADR-062 supersedes both
  ADR-053 (reading-guide governance) + ADR-054 (results-page artifact)
  on the navigation-clarity axis.
- **ADR-061** (Quarto site navigation restructure): `superseded_by`
  backfilled to `["062"]`. ADR-062 supersedes the navigation
  restructure with a clarity-focused sequel.
- **ADR-062** (Quarto writeup clarity + canonical figures): the
  forward-declaring superseder. Its frontmatter is unchanged by
  this ADR.
- **ADR-071** (Cross-reference slug-sweep closure): `closing_commit`
  backfilled to `37c2b32`. Decision content unchanged.
- **ADR-072** (Backfill ADR-051+052 frontmatter): precedent ADR.
  `closing_commit` backfilled to `8105f37`. Decision content
  unchanged.
- **ADR-073** (Immutability rule consolidated re-statement):
  `closing_commit` backfilled to `ba342c7`. ADR-076 invokes
  ADR-073's narrow-relaxation framework for authorization.
- **ADR-074** (ADR-064 self-criticism quote redaction):
  `closing_commit` backfilled to `14f0c05`. Decision content
  unchanged.
- **ADR-075** (Full-FT OOD drop rationale unified narrative):
  `closing_commit` backfilled to `428971c`. Decision content
  unchanged.

## Transcript

Transcript file (gitignored per AGENTS.md):
`transcripts/2026-05-21__v1-2-13-remediation.md` (the v1.2.13
multi-round /exploring-options session that ratified the
remediation plan + this ADR's scope). `/save-transcript` will
land this file post-v1.2.13 close.
