---
adr_id: "072"
slug: adr-051-052-frontmatter-and-structural-backfill
title: Backfill missing frontmatter fields + Alternatives sections + Status headings for ADR-051 + ADR-052 per ADR-067-style narrow-relaxation discipline
date: 2026-05-20
status: Accepted
claim_id: CLAIM-072
claim: >-
  ADR-051 + ADR-052 (both 2026-05-18 governance ADRs) ship with
  empty `closing_commit:` and `transcript:` frontmatter fields and
  no `## Alternatives Considered` body section. ADR-051 also lacks
  a `## Status` body section heading and opens with `# ADR-051 —`
  instead of `# ADR-051:` (template convention). The user's
  2026-05-18 self-audit (REPO_AUDIT_2026-05-18.md §P1.4) flagged
  ADR-049 + ADR-050 for the same class of gap, but those have
  since been populated (closing_commit `423c2c8` and `3b16036`
  respectively); the actual structural debt is in ADR-051 + ADR-052.
  This ADR treats the empty-frontmatter-fields gap as a fourth
  narrow-relaxation class adjacent to ADR-067-070 (slug typos /
  broken external refs / publisher-URL canon / render markdown
  fixes): populates the missing closing_commit values from
  observable tag history (ADR-051 Block A closed at v1.0.9 via
  ADR-058; ADR-052 introduced + closed at v1.0.3), adds the
  retrospective `## Alternatives Considered` sections documenting
  the decision space at lock time, restores the `## Status` body
  heading on ADR-051, and fixes ADR-051's opening line per template
  convention.
source: 2026-05-20 audit re-verification (grep on v1.2.8 head
  confirmed empty closing_commit/transcript + missing sections);
  ADR-067-070 narrow-relaxation methodology applied to the
  frontmatter-backfill class.
closing_commit: 8105f37
transcript:
supersedes:
  - "051"  # on the empty-frontmatter axis only; decision content unchanged
  - "052"  # same axis
superseded_by:
acceptance_criterion: >-
  `head -50 decisions/ADR-051-*.md` shows populated `closing_commit:`
  (value: `v1.0.9 (Block A; Block B carryforward to v1.1.x)`) and
  the body has `## Status`, `## Alternatives Considered` sections;
  the opening line reads `# ADR-051: ...` (colon, not em-dash).
  `head -50 decisions/ADR-052-*.md` shows populated
  `closing_commit:` (value: `v1.0.3`) and the body has
  `## Alternatives Considered`. `scripts/regenerate_audit.py
  --check` passes after the backfill.
linked_adrs:
  - "051"
  - "052"
  - "058"  # closed ADR-051 Block A
  - "075"  # supersedes ADR-052 on the narrative axis (separate concern from this frontmatter fix)
---

# ADR-072: ADR-051 + ADR-052 frontmatter and structural backfill

## Status

Accepted.

## Context

The user's 2026-05-18 self-audit (`decisions/audits/REPO_AUDIT_2026-05-18.md`
§P1.4) flagged ADR-049 + ADR-050 for empty frontmatter fields (`closing_commit:`,
`supersedes:`, `superseded_by:`). The 2026-05-20 audit re-verification confirms
ADR-049 + ADR-050 have since been populated (`closing_commit: 423c2c8` and
`3b16036` respectively). The user's flag was stale.

The actual structurally incomplete ADRs are ADR-051 and ADR-052, both 2026-05-18
governance ADRs that ship with:

- ADR-051: empty `closing_commit:` field (line 102), empty `transcript:`
  field (line 116), no `## Status` body section (jumps straight from
  frontmatter to `## Context`), no `## Alternatives Considered` section,
  and an opening line `# ADR-051 — ...` that uses an em-dash instead of
  the template-convention colon (`# ADR-051: ...`).
- ADR-052: empty `closing_commit:` field (line 86), empty `transcript:`
  field (line 98), no `## Alternatives Considered` section.

Both ADRs document substantive supersession decisions in the ADR-034 +
ADR-039 + ADR-050 chain. Their own frontmatter doesn't conform to the
schema they invoke — the immutability discipline applies to *other* ADRs
but these two skipped fields.

## Decision

Treat the empty-frontmatter-fields gap as a fourth narrow-relaxation
class adjacent to ADR-067 (Class A slug typos), ADR-068 (Class B broken
external references), ADR-069 (Class C publisher-URL canonicalization),
ADR-070 (Class D render-only markdown corrections). The same reasoning
applies: no decision content changes, only audit-trail completeness is
restored.

**ADR-051 backfill:**

- `closing_commit:` set to `v1.0.9 (Block A; Block B carryforward to v1.1.x)`.
  Block A (T0 score-match wiring) closed via ADR-058 which landed at
  v1.0.9. Block B (38 invariant-test stubs unskip per ADR-039 gate 3)
  remains carryforward to v1.1.x per ADR-051's own §Decision Block B
  narrative.
- `## Status` body section added (value: `Accepted.` — matches
  frontmatter).
- `## Alternatives Considered` section added retroactively, documenting
  the three alternatives surfaced at 2026-05-18 lock time: (1) drop both
  T0 + invariant commitments outright (rejected: methodology contracts
  can't be silently dropped); (2) fix-forward inline before v1.0.0 tag
  (rejected: time pressure at submission close + the implementation
  surface for both blocks was ~100 LOC + 38 test bodies, too large for
  the v1.0.0 rehearsal window); (3) no carryforward ADR, let ADR-034 +
  ADR-039 stand unmet (rejected: violates immutability discipline; the
  original commitments need an explicit superseding record).
- Opening line fixed: `# ADR-051 —` → `# ADR-051:` per
  `ADR_TEMPLATE.md` convention.

**ADR-052 backfill:**

- `closing_commit:` set to `v1.0.3`. ADR-052 is a methodological reframing
  ADR; the act of writing it is itself the closure event. Per git log,
  ADR-052 was introduced at commit `3ba4636` which sits under the v1.0.3
  tag.
- `## Alternatives Considered` section added retroactively, documenting
  the four alternatives surfaced at 2026-05-18 lock time: (1) re-fire
  full-FT OOD inference on a fresh DC (rejected: methodological reasoning
  was already load-bearing per LoRA's paired-bootstrap evidence; cost
  + repeat-FUSE-risk + ~$5-12 GPU spend didn't justify); (2) restart from
  clean checkpoint (rejected: same reasoning, same cost); (3) abandon
  outright with no ADR (rejected: documentation contract requires
  explicit reframe of ADR-050 Revision 2); (4) no ADR-052 reframing,
  let ADR-050 R2 stand as operational forced-drop (rejected: the
  methodological reasoning was real and load-bearing for the
  characterisation conclusions; same-day retcon optic is the trade-off
  for honest documentation of the actual decision logic).

`transcript:` fields remain empty for both ADRs per the project's
"transcripts gitignored except `transcripts/README.md`" discipline; the
field is reserved for future-session continuations and need not be
populated retroactively.

## Consequences

- Audit-trail completeness restored: `scripts/regenerate_audit.py --check`
  now sees populated closure metadata + complete body structure for
  ADR-051 and ADR-052
- Future reviewers checking frontmatter completeness no longer find a
  gap that contradicts the immutability discipline these ADRs themselves
  invoke
- The `## Alternatives Considered` sections retroactively document the
  decision space that was genuinely considered at lock-time (the
  transcripts capture it; this ADR surfaces a sanitized summary into the
  public record)
- ADR-051 + ADR-052 decisions are unchanged + remain immutable; only
  the frontmatter + missing-sections debt is closed
- Closes the loop on what the user's prior 2026-05-18 self-audit was
  trying to flag (the audit was right about the gap class; the targets
  shifted from ADR-049+050 to ADR-051+052 after the v1.0.x patch
  cycle populated 049+050)

## Alternatives Considered

1. **Leave ADR-051 + ADR-052 as-is.** Rejected — the SDD discipline
   applies to all ADRs including the meta-governance ones. Empty
   `closing_commit` is a methodology gap a reviewer checking frontmatter
   completeness would surface; ADR-051 also lacks template-required
   body sections.
2. **Backfill via direct edit, no ADR-072.** Rejected — the immutability
   rule means even narrow editorial edits need an authorizing ADR.
   ADR-067-070 established the precedent; ADR-072 extends it to the
   frontmatter-backfill class.
3. **Two separate ADRs (one for 051, one for 052).** Rejected — same
   class of fix, same scope, applied at the same time. One ADR is
   cleaner; the audit trail isn't materially improved by splitting.
4. **Treat ADR-029 misattribution refs (handled in ADR-071) and this
   frontmatter backfill as one ADR.** Rejected — they're different
   narrow-relaxation classes (slug-sweep vs frontmatter-backfill) with
   different supersession scopes. Cleaner to keep them as separate
   ADRs in the 071 → 072 → 073 → 074 → 075 sequence.

## Linked ADRs

- ADR-051 (v1.0.x-carryforward-of-t0-and-invariant-scaffolds):
  superseded on the empty-frontmatter axis only; decision content
  unchanged
- ADR-052 (full-ft-ood-drop-methodological-reframing-of-adr-050-r2):
  same supersession scope as ADR-051 here; ADR-075 separately
  supersedes ADR-052 on the narrative axis
- ADR-058 (eval-from-hub-non-dry-run-body-narrow-supersession-of-adr-051-block-a):
  closed ADR-051's Block A; cited in ADR-051's new closing_commit value
- ADR-067, ADR-068, ADR-069, ADR-070 (the 4-ADR
  immutability-relaxation chain): ADR-072 follows the same
  narrow-relaxation discipline (no decision content changes; audit
  trail strictly improved)
- ADR-075 (planned: full-ft-ood-drop-rationale-unified-narrative):
  supersedes ADR-052 entirely on the narrative axis; orthogonal to
  this ADR's frontmatter-axis supersession

## Transcript

Transcript file (gitignored per AGENTS.md): the 2026-05-20 audit
re-verification cycle that surfaced the stale REPO_AUDIT_2026-05-18.md
flag + identified the ADR-051+052 frontmatter gap; captured in
`~/notes/prompt-injection-audit-2026-05-20.md` (consumer side) and
`~/notes/prompt-injection-audit-2026-05-20-adr-appendix.md` (full ADR
governance audit).
