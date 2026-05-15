---
adr_id: NNN
slug: <kebab-case-slug>
title: <one-line title>
date: YYYY-MM-DD
status: Accepted  # Accepted | Proposed | Superseded | Deprecated
claim_id: CLAIM-NNN
claim: <one-line claim summary>
source: <doc/section where claim appears>
acceptance_criterion: <how this becomes verified>
closing_commit:  # filled after commit lands
supersedes:  # optional: e.g., ADR-NNN-old-decision
superseded_by:  # optional; set when a later ADR supersedes this one
references:
  - <URL or docs/research/<topic>/<file>.md>
transcript: transcripts/YYYY-MM-DD__<slug>.md
---

# ADR-NNN: <title>

## Status

Accepted (YYYY-MM-DD)

## Context

<2–3 paragraphs: what problem this decision is solving, what forces are at play, why a decision is needed now>

## Decision

<the choice made, in one paragraph. Be specific — name the rule, value, or approach selected>

## Consequences

**Positive:**

- <consequence>
- <consequence>

**Negative / cost:**

- <consequence>
- <consequence>

**Neutral:**

- <consequence>

## Alternatives Considered

- **<option 1>**: <one-line description>. *Rejected because*: <reason>.
- **<option 2>**: <one-line description>. *Rejected because*: <reason>.
- **<option 3>**: <one-line description>. *Rejected because*: <reason>.

## References

- <URL to peer-reviewed paper / library docs / methodology guide>
- <docs/research/<topic>/<file>.md cross-ref>
- <related ADR cross-ref>

## Transcript

See `transcripts/YYYY-MM-DD__<slug>.md` for the conversation that led to this decision.
