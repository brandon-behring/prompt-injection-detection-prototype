---
adr_id: "074"
slug: adr-064-self-criticism-quote-redaction
title: Replace verbatim self-criticism quote in ADR-064 frontmatter claim + body context with a neutral paraphrase preserving the decision
date: 2026-05-20
status: Accepted
claim_id: CLAIM-074
claim: >-
  ADR-064 ("writeup-hiring-manager-clarity-and-consistency-pass")
  has a title slug that explicitly contains "hiring-manager-clarity"
  — a curious reviewer who searches the candidate's profile + the
  keyword "hiring-manager" lands on this ADR. The frontmatter
  `claim:` field (lines 9-16) and body §A Context (lines 105-110)
  contain a verbatim user-feedback quote that includes the phrase
  "doesn't demonstrate clear thought" — an embarrassing
  self-assessment string surviving in an immutable record that any
  hiring manager wandering into decisions/ will see. The decision
  context (what changed and why) survives intact without the
  verbatim quote. This ADR replaces the verbatim quote with a
  neutral paraphrase per ADR-073 Class A / Class B-adjacent
  narrow-relaxation discipline (no decision content changes; reader
  experience strictly improved).
source: 2026-05-20 audit hiring-manager-curious risk finding — the
  single most embarrassing string in decisions/ sits in a publicly
  rendered ADR. Verbatim quote preserved privately in the
  transcript file (gitignored, emailed separately at submission).
closing_commit: 14f0c05
transcript:
supersedes:
  - "064"  # on the embedded-quote axis only; decisions B1–B6, C1–C2, D1, E1–E5 all unchanged
superseded_by:
acceptance_criterion: >-
  `grep "doesn't demonstrate clear thought" decisions/ADR-064-*.md`
  returns 0 matches. ADR-064's claim + body context narrate the
  decision provenance without the verbatim self-criticism phrase.
  ADR-064's actual decisions (B1-B6, C1-C2, D1, E1-E5) remain
  unchanged. The transcript file (private) preserves the original
  verbatim user feedback for audit-trail completeness.
linked_adrs:
  - "064"
  - "062"  # baseline before the clarity pass
  - "067"  # narrow-relaxation precedent
  - "073"  # consolidated immutability rule (Class B-adjacent: "embedded prose that doesn't render correctly" / "embedded text that doesn't serve the decision")
---

# ADR-074: Redact verbatim self-criticism quote in ADR-064

## Status

Accepted.

## Context

ADR-064 documents the writeup-hiring-manager-clarity-and-consistency
pass that landed across v1.1.4 and v1.2.0. The ADR is well-structured
and its decisions (B1-B6 commit cadence, C1-C2 spoke density,
D1 figure refinements, E1-E5 release shape) are load-bearing for the
post-v1.1.3 narrative arc.

The ADR also has a problem: it embeds a verbatim user-feedback quote
from 2026-05-19 that includes the phrase "doesn't demonstrate clear
thought." This quote appears in two places:

1. The frontmatter `claim:` field (lines 9-16). This field is rendered
   into the live Quarto site via `decisions/ADR-*.md` in `_quarto.yml`,
   so the quote is publicly readable on the rendered site.
2. The body §A Context section (lines 105-110), which repeats the
   quote with ellipses + the expanded user instruction.

ADR-064's title slug also literally contains
"hiring-manager-clarity-and-consistency-pass." A curious hiring
manager who searches the candidate's GitHub profile for
"hiring-manager" lands on this ADR. They then read the verbatim
quote.

The decision context (post-v1.1.3 user review surfaced that the
writeup needed a clarity pass; 6-commit cadence + DeBERTa §1B +
landing-page redesign + nav simplification followed) is preserved
intact by a neutral paraphrase. The verbatim user wording serves no
decision-anchoring function — the substantive feedback (jargon
density, plot-interpretation cues, table-context framing under-served)
can be summarized professionally.

Per ADR-073's consolidated immutability rule, this fix sits adjacent
to Class B ("broken external references — embedded content that
doesn't serve the decision") or could justify a future Class E
("embedded prose with hiring-manager-optic cost"). The principle is
consistent: no decision content changes; only the surface artifact
is improved.

## Decision

Replace the verbatim self-criticism quote in ADR-064 at both
occurrence sites with a neutral paraphrase.

**Frontmatter `claim:` field (lines 9-16):**

Before:

```
User feedback 2026-05-19 (post-v1.1.3 ADR-062 baseline): *"the
writeup/quatro is a little obscure and hard to follow and is not very
polished. Imagine a new person coming to it and understanding the
problem and understanding what the plots say and don't say what the
metrics mean. It is jargon heavy and dense and pretty unreadable to a
hiring manager and doesn't demonstrate clear thought."* Then expanded:
*"take a broad look over everything including readme etc and other
documentations to make sure we are consistent throughout the guide."*
```

After:

```
Post-v1.1.3 user review (ADR-062 baseline) surfaced that the Quarto
writeup needed a hiring-manager clarity pass: jargon density,
plot-interpretation cues, and table-context framing were under-served.
User expansion: ensure consistency across README and other
documentation surfaces.
```

**Body §A Context section (lines 105-110):**

Before:

```
User feedback 2026-05-19 (post-v1.1.3): *"the writeup/quatro is a
little obscure and hard to follow ... jargon heavy and dense and
pretty unreadable to a hiring manager ... doesn't demonstrate clear
thought."* Then expanded: *"take a broad look over everything
including readme etc and other documentations to make sure we are
consistent throughout the guide."*
```

After:

```
Post-v1.1.3 user review (ADR-062 baseline) flagged that the Quarto
writeup needed a hiring-manager clarity pass: jargon density,
plot-interpretation cues, table-context framing under-served. Plus
a documentation-wide consistency review across README, RESULTS,
EXECUTIVE_SUMMARY, and reference docs.
```

ADR-064's decisions (B1-B6, C1-C2, D1, E1-E5) are entirely unchanged.
Only the verbatim wording in two prose surfaces is replaced. The
original verbatim user feedback remains preserved in the (private,
gitignored) transcript file per AGENTS.md transcript discipline.

## Consequences

- The single most embarrassing string in `decisions/` ("doesn't
  demonstrate clear thought") no longer appears in a publicly
  readable artifact
- ADR-064's decisions remain unchanged + remain immutable
- Future hiring-manager reviewers wandering into `decisions/ADR-064`
  see professional neutral language describing the post-v1.1.3
  clarity-pass motivation
- Transcript file (private; emailed separately at submission)
  preserves the original verbatim feedback for audit-trail
  completeness — the substantive critique is not lost, just not
  exposed in the public-rendered ADR surface
- ADR-064's title slug remains "writeup-hiring-manager-clarity-and-
  consistency-pass" — the slug is descriptive of the decision and
  doesn't carry the embarrassing phrasing; not changing it
- Establishes precedent for Class B-adjacent / Class E
  ("embedded-prose-with-optic-cost") narrow relaxations in the
  consolidated ADR-073 framework

## Alternatives Considered

1. **Leave the verbatim quote intact.** Rejected — the embarrassment
   cost is real (the quote is publicly readable on the rendered site
   + searchable via the slug). The decision content survives the
   paraphrase intact. There's no reason to preserve the verbatim
   public-facing wording when (a) the substance is preserved in the
   paraphrase and (b) the original is preserved privately in the
   transcript.
2. **Delete ADR-064 entirely.** Rejected — the decisions it documents
   (B1-B6 commit cadence, C1-C2 spoke density, D1 figure refinements,
   E1-E5 release shape) are load-bearing for the post-v1.1.3 narrative
   arc. Supersession (not deletion) is the right move.
3. **Paraphrase the body but leave the `claim:` field verbatim.**
   Rejected — the `claim:` field is rendered to the live site as part
   of the ADR frontmatter display (`scripts/regenerate_audit.py` reads
   `claim:` into `SUBMISSION_AUDIT.md`; `_quarto.yml` renders both).
   Both surfaces need the redaction or neither.
4. **Rename ADR-064's slug to remove "hiring-manager."** Rejected — the
   slug is descriptive of the decision; renaming would itself be a
   broken-ref class that would need its own slug-sweep treatment
   (ADR-071-style). Not worth the cascade.

## Linked ADRs

- ADR-064 (writeup-hiring-manager-clarity-and-consistency-pass):
  superseded on the embedded-quote axis only; decisions B1-B6,
  C1-C2, D1, E1-E5 all unchanged + remain in force
- ADR-062 (the pre-v1.1.3 baseline that motivated ADR-064's pass):
  not superseded; provides the context the paraphrase preserves
- ADR-067 (narrow-relaxation precedent — Class A slug typos):
  ADR-074 follows the same discipline pattern (no decision content
  changes; surface fix)
- ADR-073 (consolidated immutability rule): ADR-074 is the first
  documented Class B-adjacent / Class E candidate; if a future
  ADR-074-style embedded-prose redaction is needed, fold the class
  into ADR-073 then

## Transcript

Transcript file (gitignored per AGENTS.md): the 2026-05-20 audit
hiring-manager-curious finding identified ADR-064's verbatim quote as
the highest-impact single-string redaction target. Captured in
`~/notes/prompt-injection-audit-2026-05-20.md` (P0-5) and
`~/notes/prompt-injection-audit-2026-05-20-adr-appendix.md` (drafted
ADR-074).
