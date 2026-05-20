---
adr_id: "073"
slug: adr-immutability-rule-consolidated-re-statement
title: Collapse the four-ADR narrow-relaxation chain (ADR-067/068/069/070) into a single consolidated immutability rule with four named exception classes
date: 2026-05-20
status: Accepted
claim_id: CLAIM-073
claim: >-
  The 2026-05-19 four-ADR immutability-relaxation chain
  (ADR-067/068/069/070) authorized four narrow classes of in-place
  editorial fixes to immutable ADRs. Each ADR in the chain insists
  it is "not a slippery slope"; the existence of four sequential
  relaxations in a single day undercuts that insistence from a
  reader-perception standpoint. This ADR consolidates the four
  narrow-relaxation classes into a single canonical immutability
  rule with named exception classes (A through D), reducing the
  visible "immutability is loose" surface from four signals to one
  rule + four named exceptions. ADRs 067/068/069/070 remain in
  decisions/ as historical artifacts documenting *when* each class
  was added; the prospective rule citation moves to ADR-073.
source: 2026-05-20 audit hiring-manager-curious risk finding —
  4-ADR chain in 1 day reads as process-fragility for a 5-day
  artifact. Consolidation reduces the optic without changing the
  underlying authorization.
closing_commit:
transcript:
supersedes:
  - "067"  # consolidated; decision content retained as Class A
  - "068"  # consolidated; retained as Class B
  - "069"  # consolidated; retained as Class C
  - "070"  # consolidated; retained as Class D
superseded_by:
acceptance_criterion: >-
  decisions/README.md §Lifecycle (or equivalent) cites ADR-073 as
  the canonical immutability rule reference; ADRs 067-070 remain
  reachable but are no longer cited as the prospective rule. New
  contributors learn one rule with four classes instead of one
  rule + four patches. CLAUDE.md immutability section simplified
  to cite ADR-073.
linked_adrs:
  - "067"
  - "068"
  - "069"
  - "070"
  - "071"  # the actual execution of Class A + Class B authorizations from 067/068
  - "072"  # the frontmatter-backfill class (treated as adjacent class; could be Class E in a future extension)
---

# ADR-073: ADR immutability rule -- consolidated re-statement

## Status

Accepted.

## Context

ADR-067 + ADR-068 + ADR-069 + ADR-070 were authored on 2026-05-19 as
four sequential narrow-relaxation ADRs to the project's immutability
discipline. Each ADR addresses a distinct class of editorial fix:

- ADR-067: slug typos in cross-reference filenames (Class A)
- ADR-068: broken external references (Class B)
- ADR-069: publisher-URL to DOI canonicalization (Class C)
- ADR-070: render-only markdown corrections (Class D)

Each individually is defensible. The cumulative optic — four
immutability-relaxation ADRs in a single day for a 5-day project — is
the issue. From a hiring-manager or reviewer perspective scanning the
ADR sequence, four consecutive "this is NOT a slippery slope" ADRs
read as exactly the kind of process-fragility they protest against.

The same authorizations live in fewer visible artifacts if consolidated
into a single canonical immutability ADR with four named exception
classes. The four classes remain co-equal; the consolidation is
presentation-only.

## Decision

Replace the four-ADR chain with one canonical immutability ADR that
restates the rule + names the four exception classes.

**The rule (consolidated re-statement):**

ADRs are immutable. Once Accepted, an ADR's claim text, decision
content, numeric values, status field, and acceptance criteria are
fixed. Mutations require a new superseding ADR with explicit
justification.

**The four narrow exception classes** — co-equal, all editorial only,
no decision content changes:

- **Class A -- Slug typos.** Authorized scope: substitute a wrong
  filename slug in a markdown cross-reference for the correct one when
  the linked file exists with a different slug. Example:
  `decisions/ADR-006-headline-metrics-and-statistical-floor.md` ->
  `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md`.
  Methodology choices + numeric values + status fields are not
  touched. (Original authorization: ADR-067.)

- **Class B -- Broken external references.** Authorized scope: replace
  aspirational upstream documentation paths with the actual existing
  path, or remove the reference if no such path exists. Example: a
  link to an `eval-toolkit/docs/methodology/*.md` path that was never
  created upstream gets either rewritten to the actual README anchor
  or removed entirely. (Original authorization: ADR-068.)

- **Class C -- Publisher-URL to DOI canonicalization.** Authorized
  scope: replace `publisher.example.com/foo` URLs with
  `doi.org/10.xxxx/yyyy` for academic references when the DOI
  resolution is verified. The substitution is content-equivalent
  (same paper; one is the canonical address). (Original
  authorization: ADR-069.)

- **Class D -- Render-only markdown corrections.** Authorized scope:
  fix markdown rendering errors (mismatched fence delimiters, escape
  sequences that don't render, broken inline code spans) where the
  underlying decision content is unchanged. Example: ADR-NNN body has
  a triple-backtick where a quadruple-backtick is needed to escape an
  internal code-fence example. (Original authorization: ADR-070.)

**Shared constraints across all four classes:**

1. No decision content may be modified — only the surface artifact.
2. Each fix must be referenced in a commit message with the ADR
   number that authorizes it (Class A: ADR-073-A; Class B: ADR-073-B;
   etc., or ADR-067/068/069/070 if citing the historical
   authorization).
3. A reader of the ADR's `git log` history sees both the original
   ADR commit and the fix commits.
4. If a fix is borderline between classes, write a new narrow-
   relaxation ADR rather than stretching an existing class. The
   four classes are intentionally narrow.

ADRs 067, 068, 069, 070 remain in `decisions/` as historical artifacts.
They are the record of *when* each class was added to the rule and
*why*. They are superseded on the "prospective rule" axis only — the
prospective citation moves to ADR-073. Their authorization for past
fixes (e.g., ADR-071 cites ADR-067's Class A authorization) remains
intact.

## Consequences

- `decisions/README.md` §Lifecycle (or wherever the immutability rule
  lives) cites ADR-073 as the canonical reference instead of the
  4-ADR chain
- `CLAUDE.md` + `AGENTS.md` immutability sections simplified to cite
  ADR-073's named-classes structure
- New contributors learn one rule with four classes instead of one
  rule + four patches
- Reader scanning the ADR sequence sees one immutability ADR (with
  four exception classes) rather than five (one rule + four
  relaxations)
- Backward-compatibility preserved: `git log` still shows the chain's
  full history; ADRs 067-070 are not deleted; supersession
  preserves the historical record
- Trades 4 visible "immutability is loose" signals for 1 visible
  "immutability has 4 narrow exceptions" signal — same authorization
  surface, smaller cognitive load
- If a fifth exception class is needed in the future (e.g.,
  frontmatter backfill per ADR-072), it gets added to ADR-073 as
  Class E rather than being a separate relaxation ADR

## Alternatives Considered

1. **Leave the 4 ADRs as-is.** Rejected — the count is the optic.
   Reducing visible chain length is the value of this consolidation.
   ADRs 067-070 individually are well-written; the issue is the
   aggregate pattern they create when read in sequence.
2. **Delete ADRs 067-070 entirely.** Rejected — the historical
   record (when each class was added, and why) is load-bearing for
   audit-trail integrity. Supersession (not deletion) is the right
   move. Per ADR-005 methodology discipline, even superseded ADRs
   remain readable.
3. **Three classes instead of four** (collapse Class C + Class D as
   "external reference fixes"). Rejected — Class D is render-
   correctness, distinct from Class C's content-canonicalization.
   Keep the distinction; future contributors need to know which
   kind of fix they're authorizing.
4. **Add ADR-072's frontmatter-backfill as Class E preemptively.**
   Rejected — ADR-072 is its own narrow-relaxation ADR for a
   specific case (ADR-051+052 frontmatter). If the
   frontmatter-backfill class repeats, fold it into ADR-073 then.
   Don't anticipate classes that may not recur.

## Linked ADRs

- ADR-067 (Class A): consolidated; historical authorization remains
  intact for ADR-071's Class A fixes
- ADR-068 (Class B): consolidated; historical authorization remains
  intact for ADR-071's Class B fixes (in particular the
  ADR-025 line 13 prose-replacement)
- ADR-069 (Class C): consolidated; no Class C fixes have shipped yet
  (the publisher-URL substitutions ADR-069 documents were never
  executed); future Class C fixes cite ADR-073 (or ADR-069
  historically)
- ADR-070 (Class D): consolidated; ADR-070 itself documented one
  triple-backtick to quadruple-backtick fix; future Class D fixes
  cite ADR-073
- ADR-071 (slug-sweep closure): executed the Class A + Class B
  authorizations; cites ADR-067/068 + ADR-073 (prospectively)
- ADR-072 (frontmatter backfill): adjacent narrow-relaxation class
  (Class E if folded in later); ADR-073 explicitly leaves room for
  this in §Alternatives Considered

## Transcript

Transcript file (gitignored per AGENTS.md): the 2026-05-20 audit cycle's
hiring-manager-curious finding on the 4-ADR chain optic. Captured in
`~/notes/prompt-injection-audit-2026-05-20.md` (P0-3 + capstone-template
implications) and `~/notes/prompt-injection-audit-2026-05-20-adr-appendix.md`
(High-impact finding #3 + drafted ADR-073).
