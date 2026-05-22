---
adr_id: "080"
slug: reviewer-url-pin-numeric-correction-adr-078-079
title: Correct reviewer URL pin numeric defect in ADR-078 + ADR-079 (tree/v1.2.8 → tree/v1.0.0); axis-only supersession on the reviewer-URL-pin axis
date: 2026-05-22
status: Accepted
claim_id: CLAIM-080
claim: >-
  ADR-033 (GitHub release strategy + reviewer URL pin) canonically
  pins the historical reviewer URL at `tree/v1.0.0` (ADR-033 §C
  artifact-pin table line 113: "Canonical source pin | Never drifts").
  CHANGELOG v1.3.0 confirms ("Reviewer URL pin `tree/v1.0.0` unchanged
  per ADR-033"). Three reader-facing surfaces contradict that pin by
  asserting `tree/v1.2.8` as the historical reviewer URL pin "per
  ADR-033": `WRITEUP.md:48`, `decisions/ADR-078:164`, and
  `decisions/ADR-079:228` + `decisions/ADR-079:291`. ADR-078 even
  self-contradicts within one paragraph (line 163: "the `tree/v1.0.0`
  pin (per ADR-033)" vs line 164: "Reviewer URL pin is now
  `tree/v1.2.8`"). The v1.2.8 references are factually wrong — ADR-033
  does not pin v1.2.8 anywhere; the historical content the cited links
  intend to surface (the old single-hybrid WRITEUP.md jumbled-state +
  the retired EXECUTIVE_SUMMARY.md file) IS preserved at `tree/v1.0.0`
  per ADR-033's never-drift discipline. The v1.2.8 tag exists in repo
  history (it shipped the Quarto navigation restructure per ADR-061)
  but it is not the ADR-033 reviewer pin, and citing it as such
  misleads any reader following the link. This ADR corrects the
  numeric defect on the reviewer-URL-pin axis only: WRITEUP.md
  (mutable) is edited in place; ADR-078 + ADR-079 bodies remain
  unchanged per CLAUDE.md immutability; their `superseded_by:`
  frontmatter is backfilled to `["080"]` per the ADR-076 / ADR-077
  frontmatter-backfill narrow-relaxation discipline (extended from
  ADR-072 precedent). All other content in ADR-078 + ADR-079 (the
  EXECUTIVE_SUMMARY absorption decision + the two-guide reader
  architecture decision; their alternatives considered, consequences,
  linked ADRs) stands as locked. This is the FIRST axis-only
  supersession on a factual numeric-correction axis distinct from
  the prior axis-only supersessions on reading-guide-architecture
  axes (ADR-076 through ADR-079).
source: Audit performed 2026-05-22 against the live GH-Pages
  deployment + repo source. Live verification confirmed all three
  surfaces render the wrong `tree/v1.2.8` claim. ADR-033 §C +
  CHANGELOG v1.3.0 entry confirm `tree/v1.0.0` as the source-of-truth
  pin. Audit lock via /exploring-options Q1 (audit-fix + ADR-080
  axis-only supersession). Per-commit fix-forward at
  release/v1.3.1 PR-1.
acceptance_criterion: >-
  `grep -n 'tree/v1.2.8' WRITEUP.md` returns zero hits (after the
  WRITEUP.md edit in this PR). `grep '^superseded_by' decisions/ADR-078-*.md`
  + `... ADR-079-*.md` both show `["080"]`. `decisions/ADR-080-*.md`
  exists with `supersedes: ["078", "079"]` (axis-only comments).
  `scripts/regenerate_audit.py --check` passes after the ADR-080
  landing (CLAIM count 79 → 80). `scripts/audit_adr_count_claims.py`
  exits 0 (catches 79→80 cascade across reader-facing surfaces;
  6th correct firing of the v1.2.14 invariant; the same hit-set as
  the v1.3.0 cascade plus the surfaces v1.3.0 missed: CLAUDE.md +
  CHANGELOG header narrative + WRITEUP.md +
  WRITEUP/methodology-guarantees.md). ADR-078 + ADR-079 body content
  (numeric claims, alternatives, decision rationale, prose) unchanged.
closing_commit:
transcript:
supersedes:
  - "078"  # on the reviewer-URL-pin numeric axis only (ADR-078 §Consequences line 164 "Reviewer URL pin is now tree/v1.2.8"); decision-axis content (EXECUTIVE_SUMMARY absorption) unchanged
  - "079"  # on the reviewer-URL-pin numeric axis only (ADR-079 §Decision/Stub-redirect line 228 + §Consequences line 291); decision-axis content (two-guide reader architecture) unchanged
superseded_by:
linked_adrs:
  - "033"  # GitHub release strategy + reviewer URL pin — the canonical source-of-truth pin (tree/v1.0.0) ADR-080 is correcting toward
  - "067"  # immutability clarification + canonical slug reference — original narrow-relaxation class precedent
  - "068"  # immutability narrow relaxation for broken external references — class 2 precedent for in-place fixes
  - "069"  # immutability narrow relaxation for publisher-URL → DOI canonicalization — class 3 precedent
  - "070"  # Quarto render-only Markdown corrections — class 4 precedent
  - "072"  # ADR-051+052 frontmatter + structural backfill — frontmatter-backfill narrow-relaxation precedent
  - "073"  # immutability rule consolidated re-statement — the canonical immutability framework ADR-080 invokes
  - "076"  # superseded_by + closing_commit frontmatter backfill — direct precedent for the ADR-080 frontmatter-backfill on ADR-078/079
  - "077"  # supersession-backlink + frontmatter octal-quoting backfill — second precedent + audit-tool that catches missing backlinks
  - "078"  # EXECUTIVE_SUMMARY absorbed into README — superseded on reviewer-URL-pin numeric axis only
  - "079"  # two-guide reader architecture — superseded on reviewer-URL-pin numeric axis only
---

# ADR-080: Correct reviewer URL pin numeric defect in ADR-078 + ADR-079 (tree/v1.2.8 → tree/v1.0.0); axis-only supersession on the reviewer-URL-pin axis

## Status

Accepted.

## Context

A fresh-eyes audit performed 2026-05-22 against the live GH-Pages
deployment at `https://brandon-behring.github.io/prompt-injection-detection-prototype/`
surfaced a factual numeric error propagated across three reader-facing
surfaces. Each surface claims the historical reviewer URL pin is
`tree/v1.2.8` and cites ADR-033 as the authorizing decision. ADR-033
does no such thing.

**Source-of-truth verification** (live + source):

- `decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md:113`
  artifact-pin table: `https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.0.0`
  is listed as "Canonical source pin | Never drifts".
- `CHANGELOG.md` v1.3.0 entry confirms: "Reviewer URL pin `tree/v1.0.0`
  unchanged per ADR-033."
- `index.qmd:82`, `README.md:213`, `READING_GUIDE.md:94-95`,
  `WRITEUP_PAPER.md:10`, `WRITEUP_NARRATIVE.md:11`, ADR-079 frontmatter
  comment line 71 + Linked-ADRs section line 336, and ADR-078 frontmatter
  line 24 + Consequences line 131 + line 163 + line 183 + line 197 all
  cite `tree/v1.0.0` correctly per ADR-033.

**The three defective surfaces**:

- `WRITEUP.md:48` — "the historical content remains accessible at the
  reviewer URL pin (`tree/v1.2.8`) per ADR-033."
- `decisions/ADR-078:164` — inside the Consequences section: "Reviewer
  URL pin is now `tree/v1.2.8`; reviewers navigating to EXECUTIVE_SUMMARY
  through current-state links would hit a 404 — mitigated by the README
  anchor + the redirect that could be added at v1.3.x if needed."
  Note: the SAME paragraph at line 163 says "the `tree/v1.0.0` pin (per
  ADR-033)" — the two sentences contradict each other.
- `decisions/ADR-079:228` — inside the Stub-redirect §: "The historical
  WRITEUP.md content is accessible at the reviewer URL pin
  (`tree/v1.2.8`) per ADR-033."
- `decisions/ADR-079:291` — inside the Consequences section: "Historical
  reviewer link to WRITEUP.md remains stable via the `tree/v1.2.8` pin
  (per ADR-033). Current-state WRITEUP.md is a redirect stub; readers
  following links land on the chooser and pick a guide."

**Why this matters**: ADR-033's purpose is to give an external academic
reviewer a stable URL pinned to the submission state, never to drift.
Citing `tree/v1.2.8` as that pin tells a reader to fetch a tree state
that was the v1.2.8 Quarto-navigation-restructure intermediate state
(per ADR-061), not the original submission state. A reviewer following
the incorrect link sees the navigation-restructure state, not the
submission-original. The semantic claim "per ADR-033" is also false:
ADR-033 makes no v1.2.8 commitment.

**Why this falls into a supersession (not a narrow-relaxation) case**:
The four CLAUDE.md narrow-relaxation classes (slug typo / broken
external ref / publisher-URL canonicalization / render-only Markdown)
all cover surface defects that don't change the prose intent of the
ADR. The v1.2.8 claim in ADR-078 + ADR-079 IS the prose intent — both
ADRs explicitly assert a specific reviewer-URL-pin commitment in their
body text. Correcting that commitment is a meaningful change to the
ADRs' stated claims (even though it harmonizes them with ADR-033 +
the other reader-facing surfaces). Therefore axis-only supersession,
not in-place edit, is the correct discipline.

The ADR-076-class frontmatter-backfill narrow-relaxation (per ADR-073
consolidated re-statement) DOES authorize editing the `superseded_by:`
frontmatter on ADR-078 + ADR-079 to point to ADR-080 — that's
audit-trail completeness, not decision-content alteration.

## Decision

Adopt the following two-part discipline for correcting the reviewer-URL-pin
numeric defect:

### Part A — ADR-080 axis-only supersession of ADR-078 + ADR-079

This ADR (ADR-080) supersedes ADR-078 + ADR-079 **on the
reviewer-URL-pin numeric axis only**. The corrected position is:

> The historical reviewer URL pin is `tree/v1.0.0` per ADR-033.
> No other tag is the historical reviewer URL pin. Any reader
> following a "historical reviewer URL pin per ADR-033" link should
> go to `tree/v1.0.0`.

The historical content that ADR-078 + ADR-079 describe as accessible
at the reviewer-URL pin (the pre-v1.3.0 EXECUTIVE_SUMMARY.md content
+ the pre-v1.3.0 jumbled-hybrid WRITEUP.md content) IS preserved at
`tree/v1.0.0` — the never-drift submission state contains both files
unchanged. The historical-content-preservation claim that ADR-078 +
ADR-079 make is correct; only the tag they cite was wrong.

ADR-078 + ADR-079 bodies are unchanged per CLAUDE.md immutability.
Their `superseded_by:` frontmatter is backfilled to `["080"]` per
the ADR-076 / ADR-077 narrow-relaxation discipline (extended from
ADR-072 frontmatter-backfill precedent).

### Part B — WRITEUP.md in-place correction

`WRITEUP.md` is a mutable Markdown file (not under CLAUDE.md
ADR-immutability). The single-line correction is:

- `WRITEUP.md:48` — `tree/v1.2.8` → `tree/v1.0.0` (and remove the
  parenthetical-citation confusion; clarify that the historical
  pre-v1.3.0 content is preserved at the ADR-033 reviewer pin per
  ADR-080).

### Cascade — 79 → 80 ADR-count claims across reader-facing surfaces

This ADR's creation moves the ADR count from 79 → 80. The
`scripts/audit_adr_count_claims.py` invariant (added at v1.2.14)
catches reader-facing ADR-count claims that would otherwise go stale.
Cascade hit-set:

- `README.md` (2 hits: line 173 + line 189): `79 → 80`
- `CLAUDE.md` (line 13): `79 ADRs at v1.3.0 close` → keep as historical
  v1.3.0 statement (the count was 79 AT v1.3.0; ADR-080 lands at
  v1.3.1). The /exploring-options Q1 lock decision is to update
  CLAUDE.md's v1.3.0-close clause to "79 ADRs at v1.3.0 close (80 at
  v1.3.1 including ADR-080)" to reflect both points-in-time.
- `WRITEUP.md` (line 33): `79 → 80`.
- `WRITEUP_NARRATIVE.md` (line 553): `79 → 80`.
- `READING_GUIDE.md` (line 83): `79 → 80`.
- `WRITEUP/methodology-guarantees.md` (line 12): `79 ADRs accepted
  across Phase 0-00 through ADR-079` → `80 ADRs accepted across
  Phase 0-00 through ADR-080`.
- `docs/for-hiring-managers.md` (line 84): `79 → 80`.
- `CHANGELOG.md` (line 126): the historical v1.3.0 release-note
  reference to "79 ADRs" is left unchanged (it documents a past state).

`SUBMISSION_AUDIT.md` regenerates via `scripts/regenerate_audit.py`;
CLAIM row count goes 79 → 80.

## Consequences

**Positive:**

- The factual reviewer-URL-pin claim is internally consistent across all
  three previously-defective surfaces + ADR-033 source-of-truth +
  every other reader-facing surface.
- A reviewer following any "historical reviewer URL pin per ADR-033"
  link now lands at the correct tag (`tree/v1.0.0`) — the original
  submission state ADR-033 designed the never-drift discipline to
  preserve.
- The SDD discipline is preserved: ADR-078 + ADR-079 bodies stay
  immutable; the correction is recorded as a new ADR with full audit
  trail rather than via an in-place rewrite that would erase the
  defect from history.
- The `audit_adr_count_claims.py` invariant fires its 6th correct time
  across the v1.2.13 → v1.2.14 → v1.2.15 → v1.2.16 → v1.3.0 → v1.3.1
  trail — validating the v1.2.14 design intent.

**Negative / cost:**

- ADR count cascade across 7 reader-facing surfaces (vs the 5-surface
  cascade in v1.3.0); the cascade is mechanically caught by the
  invariant + applied in a single commit.
- ADR-078 + ADR-079 bodies retain their v1.2.8 prose; a reader
  reading those ADRs in isolation will see the wrong claim, then
  must follow the `superseded_by: ["080"]` frontmatter pointer to
  ADR-080 for the correction. This is the standard cost of the
  axis-only supersession pattern (same trade-off ADR-076 + ADR-077
  + ADR-079 inherited).

**Neutral:**

- The v1.2.8 tag itself is unaffected; it remains a valid repo tag
  pointing at the Quarto-navigation-restructure intermediate state
  per ADR-061 (which is not the reviewer URL pin).
- ADR-078 + ADR-079 decision content (EXECUTIVE_SUMMARY absorption
  + two-guide reader architecture) stands as locked. ADR-080 does
  not revisit those decisions.

## Alternatives Considered

1. **Extend the narrow-relaxation set to a fifth class ("numeric
   tag-reference defect")** and correct ADR-078 + ADR-079 bodies in
   place. *Rejected*: the v1.2.8 claim IS the prose intent of those
   ADRs' Consequences + Stub-redirect sections (not a typo / broken
   ref / publisher canonicalization / render-only delimiter). Editing
   those in place would erase the defect from history. The four
   existing narrow-relaxation classes are all surface defects; this
   one is a factual claim about a tag commitment.
2. **Don't fix the ADRs; only fix WRITEUP.md** and leave ADR-078 +
   ADR-079 with their incorrect v1.2.8 claims. *Rejected*: a reader
   following any "tree/v1.2.8 per ADR-033" link from ADR-078 + ADR-079
   would land at the wrong tree state + see the false ADR-033
   citation. The defect is reader-visible on the live site (both ADRs
   render to live HTML); fixing only one of three surfaces leaves the
   other two misleading.
3. **Bigger fix: rewrite ADR-078 + ADR-079 entirely** to reflect the
   correct pin + all other minor v1.3.0 polish. *Rejected*: scope
   creep + violates the axis-only supersession pattern that has
   served the v1.2.x → v1.3.0 trail (ADR-076 / ADR-077 / ADR-078 /
   ADR-079 all axis-only-supersession). The single numeric defect
   warrants a single axis-only supersession.
4. **Treat as a CLAUDE.md amendment** (extend the narrow-relaxation
   set to authorize this specific class). *Rejected*: same reasoning
   as Option 1 + amendments to CLAUDE.md are themselves load-bearing
   governance changes that warrant their own ADR + transcript trail.
   Single ADR-080 is the cleanest option.

## Linked ADRs

- **ADR-033** (GitHub release strategy + reviewer URL pin): the
  source-of-truth ADR pinning `tree/v1.0.0` as the canonical reviewer
  URL. ADR-080 cites this as the authority being correctly applied
  by the post-fix state.
- **ADR-067 / ADR-068 / ADR-069 / ADR-070** (the four narrow-relaxation
  classes consolidated in ADR-073): cited to clarify that ADR-080's
  axis-only-supersession discipline is distinct from the in-place
  narrow-relaxation classes.
- **ADR-072** (ADR-051 + ADR-052 frontmatter + structural backfill):
  the frontmatter-backfill narrow-relaxation precedent that authorizes
  editing `superseded_by:` on ADR-078 + ADR-079.
- **ADR-073** (immutability rule consolidated re-statement): the
  canonical immutability framework ADR-080 invokes for the body-vs-
  frontmatter distinction.
- **ADR-076** (superseded_by + closing_commit frontmatter backfill):
  direct precedent for the frontmatter-backfill pattern applied here.
- **ADR-077** (supersession-backlink + frontmatter octal-quoting
  backfill): the audit-tool ADR (`scripts/audit_superseded_by_backlinks.py`)
  that catches missing backlinks — will correctly classify ADR-080 →
  ADR-078/079 as axis-only via comment heuristic.
- **ADR-078** (EXECUTIVE_SUMMARY absorbed into README): superseded
  on reviewer-URL-pin numeric axis only. EXECUTIVE_SUMMARY-absorption
  decision content unchanged.
- **ADR-079** (two-guide reader architecture): superseded on
  reviewer-URL-pin numeric axis only. Two-guide-architecture decision
  content unchanged.

## Transcript

Audit + decision trail captured in the v1.3.1 audit-fix session
(2026-05-22), driven by `/exploring-options` walk-through of 9
decision-shaping questions (Q1-Q9). Plan file:
`~/.claude/plans/i-want-to-audit-abundant-meerkat.md`. Per the
gitignore-by-default transcript discipline, the transcript stays
private; `/save-transcript 2026-05-22__v1-3-1-audit-fix` will land
the file post-v1.3.1 close.
