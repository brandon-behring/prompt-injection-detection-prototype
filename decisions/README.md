# Architecture Decision Records (ADRs)

ADRs document significant decisions in [Michael Nygard format](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions): `Status / Context / Decision / Consequences / Alternatives Considered`. Numbered sequentially. **Immutable**.

## Lifecycle

- New ADR → `decisions/ADR-NNN-<slug>.md`, status `Accepted` (or `Proposed` if pending review)
- Change a previously-locked decision → write a **new** ADR that marks the prior as `status: superseded-by-NNN`. Do not edit the prior ADR file.
- **Narrow exceptions** (per [ADR-067](./ADR-067-immutability-clarification-and-canonical-slug-reference.md), v1.2.2 + [ADR-068](./ADR-068-immutability-narrow-relaxation-for-broken-external-references.md), v1.2.5): TWO factual-defect classes MAY be corrected in-place with a commit message citing the relevant ADR + listing per-file corrections: (1) cross-reference slug filename typos (per ADR-067) — slug points at a wrong-but-existing file in `decisions/`; (2) broken external references (per ADR-068) — markdown links to local-filesystem paths or aspirational upstream resources that cannot resolve on any non-author machine. ALL other content (numeric values, methodology, prose, alternatives, non-slug frontmatter, table data) remains immutable per the rule above.
- Spec propagation: ADR is the source of truth. After locking ADR-NNN:
  - SPEC_GREENFIELD appendix row updated: `locked-to-X (see ADR-NNN)`
  - SPEC_SHEET corresponding slot updated: `[LOCKED: X (per ADR-NNN)]`
  - SUBMISSION_AUDIT.md regenerates from ADRs (via `scripts/regenerate_audit.py`); CI hard-gate

## Template

See `decisions/ADR_TEMPLATE.md` for a fillable skeleton. To draft a new ADR:

```bash
cp decisions/ADR_TEMPLATE.md decisions/ADR-NNN-<slug>.md
# Edit the frontmatter fields + body sections
# Commit with: feat: ADR-NNN <title> (locks decision DECISION-NAME)
```

## ADR frontmatter

Each ADR file begins with YAML frontmatter for `scripts/regenerate_audit.py`:

```yaml
---
adr_id: NNN
slug: brief-alignment
title: Brief alignment with Ciphero take-home requirements
date: 2026-MM-DD
status: Accepted | Proposed | Superseded | Deprecated
claim_id: CLAIM-NNN
claim: <one-line claim summary>
source: <doc/section where claim appears>
acceptance_criterion: <how this claim becomes verified>
closing_commit: <SHA or PR link, filled when accepted>
supersedes: NNN (if applicable)
superseded_by: NNN (if applicable)
references:
  - https://...
  - docs/research/<topic>/<file>.md
transcript: transcripts/YYYY-MM-DD__phase-0-NN__topic.md
---
```

## Index

| ADR | Title | Status | Supersedes |
|---|---|---|---|
| (populated during Phase 0 / ongoing iteration) | | | |

## Anti-patterns

- Editing a previously-locked ADR (immutable — supersede via new ADR)
- Locking a decision without referencing the supporting transcript
- Skipping ADR for a "small" decision that later turns out to be load-bearing
