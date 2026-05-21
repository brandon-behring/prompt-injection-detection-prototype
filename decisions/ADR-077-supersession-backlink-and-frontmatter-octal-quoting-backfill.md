---
adr_id: "077"
slug: supersession-backlink-and-frontmatter-octal-quoting-backfill
title: Backfill supersession back-links + quote octal-risk YAML integer fields in ADR-007 + ADR-015 + ADR-018 + ADR-021 + ADR-052 frontmatter per ADR-076 frontmatter-backfill discipline
date: 2026-05-21
status: Accepted
claim_id: CLAIM-077
claim: >-
  The v1.2.15 supersession-backlink invariant (new
  `scripts/audit_superseded_by_backlinks.py`) surfaced two classes of
  frontmatter debt beyond what ADR-076 covered:

  Class 1 — YAML octal-parsing source bugs. Three ADR frontmatter
  fields contain bare integer values that YAML 1.1 parses as OCTAL
  rather than the author's intended string. `ADR-007.superseded_by:
  015` and `ADR-018.supersedes: 015` both round-trip to decimal 13
  (interpreted as ADR-013, not ADR-015 as the author intended).
  `ADR-015.supersedes: 007` coincidentally round-trips correctly
  (octal 7 == decimal 7) but is octal-risk for the same reason. The
  fix: quote each ("015" / "007"); identical intent, parser-safe.

  Class 2 — supersession back-link gaps. Four ADRs lack `superseded_by:`
  entries for declared full-axis (not axis-only per ADR-076 convention)
  supersession edges:
    - ADR-015 declares `supersedes: ADR-007` (post-quote) but ADR-015
      itself is then superseded by ADR-018 (post-quote) — ADR-015's
      `superseded_by:` was empty; backfill to `["018"]`.
    - ADR-018 declares `supersedes: ADR-015` (post-quote) and is itself
      superseded by ADR-050 — ADR-018's `superseded_by:` was empty;
      backfill to `["050"]`.
    - ADR-050 declares `supersedes: ADR-021` but ADR-021's
      `superseded_by:` was empty; backfill to `["050"]`.
    - ADR-075 declares `supersedes: ADR-052` ("entire scope" per the
      explicit ADR-075 comment, not axis-only) but ADR-052's
      `superseded_by:` was empty; backfill to `["075"]`.

  Both classes are extensions of the ADR-076 frontmatter-backfill
  pattern (extended from ADR-072 precedent): no decision content
  changes; only frontmatter audit-trail metadata is restored. The
  v1.2.15 audit-tool now exits 0 with these fixes in place.

  Cascades from this ADR's creation:
    - SUBMISSION_AUDIT.md CLAIM row count: 76 → 77.
    - README + docs/for-hiring-managers + WRITEUP/methodology-guarantees
      + CLAUDE.md ADR-count claims: 76 → 77 (caught mechanically by
      v1.2.14's `audit_adr_count_claims.py` invariant — proving its
      design intent).
source: v1.2.15 audit-tool development surfaced 5 backlink violations
  after axis-only comment heuristic filtering. Per v1.2.15 plan Q2
  lock (halt + surface) → user lock (path 1 + backfill-in-v1.2.15).
  Octal-quoting subclass surfaced during root-cause investigation
  (yaml.safe_load parses bare `015` as decimal 13 per YAML 1.1
  octal rules; same bug bit `collect_adrs` in the new audit script).
closing_commit:
transcript:
supersedes:
  - "007"  # frontmatter-axis only (octal-quoting); decision content unchanged
  - "015"  # frontmatter-axis (octal-quoting + superseded_by backfill); decision content unchanged
  - "018"  # frontmatter-axis (octal-quoting + superseded_by backfill); decision content unchanged
  - "021"  # frontmatter-axis only (superseded_by backfill); decision content unchanged
  - "052"  # frontmatter-axis only (superseded_by backfill); decision content unchanged
superseded_by:
acceptance_criterion: >-
  `scripts/audit_superseded_by_backlinks.py` exits 0 (no FAIL
  entries; INFO entries for axis-only edges + closing_commit
  exempt set are unchanged). `grep '^superseded_by' decisions/ADR-015-*.md
  decisions/ADR-018-*.md decisions/ADR-021-*.md decisions/ADR-052-*.md`
  shows populated values. `grep 'superseded_by:\s*"015"' decisions/ADR-007-*.md`
  shows quoted form. `grep 'supersedes:\s*"015"' decisions/ADR-018-*.md`
  + `grep 'supersedes:\s*"007"' decisions/ADR-015-*.md` show quoted forms.
  `scripts/audit_adr_count_claims.py` exits 0 (the v1.2.14 invariant
  catches reader-facing surfaces' "76 ADRs" → "77 ADRs" requirement;
  this ADR's creation cascades through). `scripts/regenerate_audit.py
  --check` passes after the backfill with 77 CLAIM rows.
linked_adrs:
  - "007"  # superseded_by field quoted + back-link target
  - "015"  # superseded_by populated + supersedes quoted (defensive)
  - "018"  # superseded_by populated + supersedes quoted
  - "021"  # superseded_by populated
  - "050"  # forward-declarer to ADR-018 + ADR-021 (no change to ADR-050)
  - "052"  # superseded_by populated
  - "072"  # original frontmatter-backfill precedent
  - "075"  # forward-declarer to ADR-052 (no change to ADR-075)
  - "076"  # immediate-precedent backfill ADR
---

# ADR-077: Backfill supersession back-links + quote octal-risk YAML integer fields

## Status

Accepted.

## Context

The v1.2.15 patch introduced `scripts/audit_superseded_by_backlinks.py`,
a sibling invariant to v1.2.14's `audit_adr_count_claims.py`. The new
tool checks that every `supersedes: [N]` declaration has a corresponding
`superseded_by: [self]` entry on the target ADR. Edges marked axis-only
via YAML comment (per the v1.2.13/v1.2.14 narrow-relaxation discipline)
are EXEMPT from the bidirectional invariant and reported as INFO.

After the axis-only heuristic correctly classified 19 of 24 violations
as INFO, **5 real FAILs remained**. Root-cause investigation surfaced
**two distinct frontmatter-completeness debt classes**:

### Class 1 — YAML octal-parsing source bugs (3 fields)

YAML 1.1 (and Python's `pyyaml`) parses bare integer literals with
leading zero as octal. `ADR-007.superseded_by: 015` round-trips as
decimal 13, not the author's intended ADR-015 reference. Three
frontmatter fields had this bug:

- `ADR-007.superseded_by: 015` → parsed as 13; intent was "015"
- `ADR-015.supersedes: 007` → parsed as 7; intent was "007"
  (coincidentally correct because octal 7 == decimal 7, but
  still octal-risk and should be quoted defensively)
- `ADR-018.supersedes: 015` → parsed as 13; intent was "015"

The audit-tool itself initially bit this bug (4 ADRs dropped due to
adr_id field octal-collision); fix landed in `collect_adrs` (filename
as source of truth for adr_id, not the YAML field). The same bug
existed in three substantive `supersedes`/`superseded_by` fields and
required source-side correction.

### Class 2 — Supersession back-link gaps (4 ADRs)

After the quote-fix, the audit-tool's remaining 5 FAILs reduced to 4
real backlink gaps (one of the 5 was the post-quote ADR-018 → ADR-015
edge, which produced the new gap on ADR-015 below):

- **ADR-015** ← ADR-018 (post-quote): ADR-015's `superseded_by:` was
  empty; needs `["018"]`.
- **ADR-018** ← ADR-050: ADR-018's `superseded_by:` was empty; needs
  `["050"]`.
- **ADR-021** ← ADR-050: ADR-021's `superseded_by:` was empty; needs
  `["050"]`.
- **ADR-052** ← ADR-075: ADR-075 declares `supersedes: ["052"]` with
  comment "entire scope — its sole purpose was the reframe of ADR-050
  R2; ADR-075 absorbs that purpose" — explicit FULL supersession, not
  axis-only. ADR-052's `superseded_by:` was empty; needs `["075"]`.

## Decision

Treat both classes as the ADR-076 frontmatter-backfill narrow-relaxation
class (extended from ADR-072). No decision content changes in any of
the 7 affected ADRs; only frontmatter audit-trail metadata is restored
to parser-safe + bidirectionally-consistent state.

### Class 1 fixes (octal-quoting)

- `ADR-007.superseded_by: 015` → `superseded_by: "015"`
- `ADR-015.supersedes: 007` → `supersedes: "007"` (defensive; same intent)
- `ADR-018.supersedes: 015` → `supersedes: "015"`

### Class 2 fixes (backlink populations)

- `ADR-015.superseded_by:` → bullet list with `["018"]`
- `ADR-018.superseded_by:` → bullet list with `["050"]`
- `ADR-021.superseded_by:` → bullet list with `["050"]`
- `ADR-052.superseded_by:` → bullet list with `["075"]`

Each `superseded_by:` field gets a comment matching the v1.2.14 ADR-076
convention: `# back-link added per ADR-077 frontmatter-backfill discipline`.

### Cascading edits (caught by v1.2.14 invariant)

This ADR's creation moves the ADR count from 76 → 77. The v1.2.14
`audit_adr_count_claims.py` invariant catches reader-facing ADR-count
claims that would go stale:

- `README.md:100` + `README.md:114`: "76 immutable ADRs" → "77"
- `docs/for-hiring-managers.md:83`: "76 immutable ADRs" → "77"
- `WRITEUP/methodology-guarantees.md:12`: "76 ADRs ... ADR-076" →
  "77 ADRs ... ADR-077"
- `CLAUDE.md:13`: "76 ADRs at v1.2.13 close" → "77 ADRs at v1.2.15
  close" + extend governance parenthetical with ADR-077

`SUBMISSION_AUDIT.md` regenerates via `scripts/regenerate_audit.py`;
CLAIM count goes 76 → 77.

ADR-077's own `closing_commit:` stays empty per the same precedent ADR-072
+ ADR-076 set (future ADR can backfill; the recursive gap is well-known).
Same for `transcript:` (per the gitignored-transcripts discipline).

## Consequences

- The supersession chain on the ADR-007/013/015/018/021/050/052/075
  cluster is now bidirectionally consistent; reviewer reading any
  superseded ADR's frontmatter can trace forward to its full-axis
  superseder(s).
- The `audit_superseded_by_backlinks.py` invariant catches future
  instances of this class mechanically (extends the v1.2.14 audit-tool
  pattern).
- YAML octal-parsing pitfall is mitigated at the 3 known sites; future
  ADRs should quote all bare-integer ID values in supersedes /
  superseded_by / adr_id fields (lint-checked by the audit-tool
  going forward — any unquoted leading-zero would parse-mismatch the
  filename).
- v1.2.14's `audit_adr_count_claims.py` invariant correctly caught the
  cascade-bump requirement (76 → 77 on reader-facing surfaces) when
  this ADR landed — validates the design intent of the v1.2.14 invariant.
- Decision content unchanged across all 7 modified ADRs (frontmatter
  metadata only).

## Alternatives Considered

1. **Defer the backlink gaps to a separate v1.2.16 audit cycle.**
   Rejected per v1.2.15 plan Q2 → user lock (path 1 backfill in
   v1.2.15). Keeps the audit→remediation cycle tight; defers
   nothing.
2. **Fix only the octal-quoting bugs; leave backlink gaps for later.**
   Rejected: the new audit-tool wouldn't pass; the v1.2.15 patch
   couldn't ship. Both classes need closure in the same patch for
   audit-tool wiring to land green.
3. **Add octal-quoting linter as a separate audit-tool.**
   Rejected: the existing `audit_superseded_by_backlinks.py` already
   surfaces the symptoms (octal-parsed integers produce wrong target
   IDs in the backlink check). A dedicated tool would duplicate
   coverage. Future v1.3.x could harden via a YAML-aware linter if
   the project wants explicit lint of all bare integers in frontmatter.
4. **Two separate ADRs (one per class).** Rejected — same
   frontmatter-backfill narrow-relaxation class; same authorization
   basis (ADR-072 + ADR-076 precedent); same v1.2.15 audit-tool
   driver. One ADR cleaner.

## Linked ADRs

- **ADR-007** (Rung architecture + reference scorers; superseded by
  ADR-013 + ADR-015): `superseded_by` field's bare-integer value
  quoted for parser-safety. Decision content unchanged.
- **ADR-013** (Kit ratify): historical existing back-link on ADR-007
  remains correct (`superseded_by` already correctly mentions ADR-013
  per prior history pre-quote-fix). Unchanged in this backfill.
- **ADR-015** (Rung architecture refinement; supersedes ADR-007,
  superseded by ADR-018): `supersedes:` value quoted; `superseded_by:`
  backfilled to `["018"]`. Decision content unchanged.
- **ADR-018** (Reference-scorer slate + contamination stratification;
  partially supersedes ADR-015): `supersedes:` value quoted;
  `superseded_by:` backfilled to `["050"]`. Decision content unchanged.
- **ADR-021** (Eval-slate aggregation + recall/FPR pinpoints):
  `superseded_by:` backfilled to `["050"]`. Decision content unchanged.
- **ADR-050** (Rung-slate narrowing + LLM-judges drop): forward-
  declarer; no edit. Reference target for ADR-018 + ADR-021 backlinks.
- **ADR-052** (Full-FT OOD drop methodological reframing of ADR-050 R2):
  `superseded_by:` backfilled to `["075"]`. Decision content unchanged.
- **ADR-072** (ADR-051 + ADR-052 frontmatter backfill): precedent for
  this ADR's narrow-relaxation discipline.
- **ADR-075** (Full-FT OOD drop rationale unified narrative): forward-
  declarer to ADR-052; supersession explicitly marked "entire scope"
  in ADR-075's frontmatter comment. No edit.
- **ADR-076** (Supersession + closing_commit frontmatter backfill):
  immediate precedent for this ADR. Extended scope here covers octal-
  quoting subclass not anticipated at ADR-076 time.

## Transcript

Transcript file (gitignored per AGENTS.md): the v1.2.15 session that
developed the new audit-tool, surfaced the 5 real findings, root-
caused the octal-parsing subclass, and ratified the path-1 backfill
direction. `/save-transcript` will land this file post-v1.2.15
close.
