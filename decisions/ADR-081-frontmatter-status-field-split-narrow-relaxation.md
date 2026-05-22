---
adr_id: "081"
slug: frontmatter-status-field-split-narrow-relaxation
title: Authorize frontmatter `status:` field split (verbose-context → pure-Nygard `status:` + new `lifecycle-note:`) as an extension of the ADR-072 / ADR-076 / ADR-077 frontmatter-backfill narrow-relaxation discipline; apply to ADR-060 as the seed case
date: 2026-05-22
status: Accepted
claim_id: CLAIM-081
claim: >-
  The v1.3.2 audit surfaced ADR-060's frontmatter `status:` field as
  carrying non-Nygard verbose context: `status: Accepted (methodology
  lock — infrastructure landed; execution deferred to v1.1.1 per
  /exploring-options 2026-05-19 Path B lock)`. The parenthetical
  context is load-bearing operationally (it explains why ADR-060 was
  marked Accepted at v1.1.0 even though execution didn't land until
  v1.1.2 per ADR-063) but breaks the canonical Michael-Nygard
  `status: <{Proposed, Accepted, Superseded, Deprecated, Rejected}>`
  schema. ADR-060 is the only such ADR in the 80-ADR corpus (as of
  v1.3.1 close); future ADRs may similarly want to surface
  lifecycle-context that doesn't fit pure Nygard.

  This ADR extends the existing frontmatter-backfill narrow-relaxation
  discipline (ADR-072 → ADR-076 → ADR-077) to a new field-split axis:
  any ADR whose `status:` is non-Nygard MAY have its frontmatter split
  in-place into pure-Nygard `status:` + a new `lifecycle-note:` field
  carrying the verbose context. No decision content changes; only
  frontmatter audit-trail metadata is restructured. The split
  preserves the prior author's intent (the verbose context survives in
  `lifecycle-note:`) while restoring schema-compliance of `status:`.

  Applied to ADR-060 in the same patch (sole seed case as of v1.3.2):
    - Before: `status: Accepted (methodology lock — infrastructure
      landed; execution deferred to v1.1.1 per /exploring-options
      2026-05-19 Path B lock)`
    - After: `status: Accepted` + new field `lifecycle-note:
      methodology lock — infrastructure landed; execution deferred
      to v1.1.1 per /exploring-options 2026-05-19 Path B lock`.

  `decisions/README.md` schema documentation is updated to enumerate
  `lifecycle-note:` as an OPTIONAL frontmatter field.

  Cascades from this ADR's creation:
    - SUBMISSION_AUDIT.md CLAIM row count: 80 → 81.
    - README + docs/for-hiring-managers + WRITEUP/methodology-guarantees
      + CLAUDE.md ADR-count claims: 80 → 81 (caught mechanically by
      v1.2.14's `audit_adr_count_claims.py` invariant — proving its
      design intent on the 7th consecutive ADR-add).
source: >-
  v1.3.2 multi-LLM audit cycle (Claude AUDIT_CLAUDE_2026-05-22 P3-3
  finding) surfaced ADR-060's non-Nygard `status:` field. Per
  /exploring-options 2026-05-22 Q2 lock (B1 — narrow-relaxation
  frontmatter edit, not in-place body change). The discipline matches
  the ADR-072 / ADR-076 / ADR-077 frontmatter-backfill chain — edit
  frontmatter, leave body untouched, document the precedent in a new
  ADR so future readers can see the audit trail.
acceptance_criterion: >-
  `grep '^status:' decisions/ADR-060-*.md` returns `status: Accepted`
  (pure Nygard). `grep '^lifecycle-note:' decisions/ADR-060-*.md`
  returns the previously-parenthesized text. `decisions/README.md`
  documents `lifecycle-note:` as an OPTIONAL frontmatter field.
  `scripts/audit_adr_count_claims.py` exits 0 (the v1.2.14 invariant
  catches reader-facing surfaces' "80 ADRs" → "81 ADRs" requirement;
  this ADR's creation cascades through). `scripts/regenerate_audit.py
  --check` passes after the split with 81 CLAIM rows.
  `scripts/audit_superseded_by_backlinks.py` exits 0 (ADR-081's
  axis-only supersession of ADR-060 is correctly classified via
  comment heuristic).
closing_commit:
transcript:
supersedes:
  - "060"  # frontmatter-axis only (status-field-split: verbose `status:` → pure-Nygard `status:` + new `lifecycle-note:` field); ADR-060 body / decision / consequences / alternatives content unchanged
superseded_by:
linked_adrs:
  - "060"  # the seed case for status-field-split narrow-relaxation
  - "063"  # the execution ADR that landed ADR-060's deferred-to-v1.1.1 work at v1.1.2 (the `lifecycle-note:` context refers to this)
  - "067"  # original narrow-relaxation Class A (cross-ref slug typos) precedent
  - "068"  # Class B (broken external references) precedent
  - "069"  # Class C (publisher-URL → DOI canonicalization) precedent
  - "070"  # Class D (Quarto render-only Markdown corrections) precedent
  - "072"  # original frontmatter-backfill narrow-relaxation precedent (closing_commit + Alternatives backfill for ADR-051 + ADR-052)
  - "073"  # immutability rule consolidated re-statement (the canonical immutability framework ADR-081 invokes)
  - "076"  # superseded_by + closing_commit frontmatter backfill precedent
  - "077"  # supersession-backlink + octal-quoting frontmatter backfill precedent
references:
  - decisions/ADR-072-adr-051-and-adr-052-frontmatter-and-structural-backfill.md
  - decisions/ADR-076-superseded-by-and-closing-commit-frontmatter-backfill.md
  - decisions/ADR-077-supersession-backlink-and-frontmatter-octal-quoting-backfill.md
---

# ADR-081: Frontmatter `status:` field-split narrow-relaxation

## Status

Accepted.

## Context

CLAUDE.md's project-level immutability discipline says: *"ADRs are
immutable; supersede via new ADR marking prior `status: superseded-by-NNN`."*
Four narrow-relaxation classes exist per ADR-067 + ADR-068 + ADR-069
+ ADR-070 (consolidated in ADR-073), covering surface-level factual /
render defects:

- **Class A** (ADR-067) — cross-reference slug filename typos.
- **Class B** (ADR-068) — broken external references (404 paths +
  publisher-URL → DOI canonicalization).
- **Class C** (ADR-069) — publisher-URL → DOI canonicalization.
- **Class D** (ADR-070) — Quarto render-only Markdown corrections.

A fifth class — frontmatter-backfill — was developed across ADR-072,
ADR-076, and ADR-077 to authorize editing specific frontmatter fields
(`closing_commit:`, `superseded_by:`, octal-quoted `supersedes:` /
`superseded_by:` integer values) without superseding the prior ADR's
decision content. The discipline: edit frontmatter, leave body
untouched, document the precedent in a new ADR so future readers can
see the audit trail.

The v1.3.2 multi-LLM audit cycle (Claude AUDIT_CLAUDE_2026-05-22
P3-3) surfaced a sibling case: **ADR-060's `status:` field carries
non-Nygard verbose context**.

ADR-060 frontmatter:
```
status: Accepted (methodology lock — infrastructure landed; execution deferred to v1.1.1 per /exploring-options 2026-05-19 Path B lock)
```

The parenthetical context is operationally meaningful: ADR-060 locked
the DeBERTa-v3-base medium ablation methodology at v1.1.0 while
deferring execution; ADR-063 then landed the execution at v1.1.2. A
reader inspecting ADR-060 in isolation benefits from knowing the
status is qualified with that lifecycle context.

But the canonical Michael Nygard schema restricts `status:` to the
literal set `{Proposed, Accepted, Superseded, Deprecated, Rejected}`
(see `decisions/README.md` schema notes). ADR-060's verbose form
breaks any parser that expects pure-Nygard `status:` — including
`scripts/audit_*.py` script `status` checks.

This ADR authorizes a sixth frontmatter-backfill axis: **`status:` field
split**.

## Decision

Adopt a sixth frontmatter-backfill narrow-relaxation axis: any ADR
whose `status:` is non-Nygard MAY have its frontmatter restructured
in-place into:

- pure-Nygard `status:` (one of `{Proposed, Accepted, Superseded,
  Deprecated, Rejected}`)
- a new OPTIONAL `lifecycle-note:` field carrying the previously-
  parenthesized verbose context.

The decision-content body of the affected ADR remains untouched per
the ADR-073 immutability rule.

### Applied to ADR-060

Before:
```yaml
status: Accepted (methodology lock — infrastructure landed; execution deferred to v1.1.1 per /exploring-options 2026-05-19 Path B lock)
```

After:
```yaml
status: Accepted
lifecycle-note: methodology lock — infrastructure landed; execution deferred to v1.1.1 per /exploring-options 2026-05-19 Path B lock
```

ADR-060 is the only such ADR in the 80-ADR corpus as of v1.3.1 close;
this is a single-ADR seed application.

### Schema documentation update

`decisions/README.md` is updated to enumerate `lifecycle-note:` as an
OPTIONAL frontmatter field, modeled after the canonical Michael
Nygard schema with project-specific extensions.

### Relationship to prior narrow-relaxation classes

This is **frontmatter-axis only**, identical in discipline to ADR-072
+ ADR-076 + ADR-077. The decision-content body of ADR-060 (Context,
Decision, Consequences, Alternatives Considered) is unchanged. ADR-060's
core methodology lock (medium-ablation scope + chunk-and-average vs
head-truncation truncation strategies + 5-slice OOD evaluation +
ablation-appendix framing) stands as locked.

## Consequences

### Positive

- ADR-060's `status:` field is now pure Nygard, enabling clean
  programmatic status checks (audit scripts, dashboard parsers,
  decision-record tooling).
- The verbose context is preserved in `lifecycle-note:`, not erased.
- The discipline extends gracefully to future ADRs that want to
  surface lifecycle-context (e.g., a future Accepted-pending-execution
  ADR can populate `status: Accepted` + `lifecycle-note: pending
  execution at vX.Y.Z`).
- `decisions/README.md` schema documentation is now first-class for
  the `lifecycle-note:` field.

### Negative / cost

- One more narrow-relaxation class (sixth) for future contributors to
  understand. Mitigation: this ADR-081 + the existing ADR-067/068/069/
  070/072/073/076/077 chain are the documentation surface; a
  contributor confused by the discipline reads the chain.
- The `lifecycle-note:` field is project-specific (not pure Nygard).
  Mitigation: this is acknowledged + the field is OPTIONAL; pure
  Nygard parsers can ignore it without losing the `status:` semantics.

### Neutral

- The audit-trail discipline (immutable body + frontmatter-axis
  narrow-relaxation) is preserved. ADR-060 → ADR-081 is the
  axis-only-supersession edge per the ADR-076 / ADR-077 pattern; the
  decision content of ADR-060 stands.

## Alternatives Considered

1. **Document the verbose form as legitimate in `decisions/README.md`
   (option B2 from the v1.3.2 /exploring-options Q2 walk).** Rejected:
   would normalize a parse-hostile non-Nygard `status:` for future
   ADRs; the discipline of pure-Nygard `status:` is load-bearing for
   any programmatic status check (including the v1.2.14
   `audit_adr_count_claims.py` invariant + future analogues).
2. **Leave ADR-060 as-is + document the audit-script limitation
   (option B3 from the v1.3.2 walk).** Rejected: the audit script
   isn't the problem — pure-Nygard `status:` is the project's
   canonical schema. The deviation is in ADR-060's frontmatter, not
   in the script.
3. **Write a new ADR-061-class structural-supersession that fully
   supersedes ADR-060.** Rejected: ADR-060's decision content is
   correct and locked; the issue is purely frontmatter-schema. A
   full-content supersession would be disproportionate to the change.
4. **Extend the existing ADR-076 or ADR-077 directly (without a new
   ADR).** Rejected: ADR-076 + ADR-077 are themselves immutable; an
   extension requires a new ADR per the chain pattern (ADR-072 →
   ADR-076 → ADR-077 → ADR-081). This ADR-081 IS the extension.

## Linked ADRs

- **ADR-060** (DeBERTa-v3-base medium ablation methodology — the seed
  case for this narrow-relaxation axis; status-field-split applied to
  ADR-060 in the same v1.3.2 patch).
- **ADR-063** (DeBERTa ablation v1.1.2 execution + slot shift — the
  ADR whose existence retrospectively justifies ADR-060's verbose
  `lifecycle-note:` context).
- **ADR-067** + **ADR-068** + **ADR-069** + **ADR-070** (the original
  four narrow-relaxation classes A–D — establish the discipline).
- **ADR-072** (ADR-051 + ADR-052 frontmatter + structural backfill —
  the original frontmatter-backfill narrow-relaxation precedent).
- **ADR-073** (immutability rule consolidated re-statement — the
  canonical immutability framework this ADR invokes).
- **ADR-076** (superseded_by + closing_commit frontmatter backfill —
  direct precedent for the frontmatter-backfill chain).
- **ADR-077** (supersession-backlink + frontmatter octal-quoting
  backfill — second precedent + audit-tool that catches missing
  backlinks; will correctly classify ADR-081 → ADR-060 as axis-only
  via comment heuristic).

## Transcript

Decision trail captured in the v1.3.2 audit-remediation session
(2026-05-22), driven by `/exploring-options` walk-through (Q2 lock B1
— narrow-relaxation frontmatter edit). Plan file:
`~/.claude/plans/i-want-to-write-spicy-whisper.md`. Per the
gitignore-by-default transcript discipline, the transcript stays
private; `/save-transcript 2026-05-22__v1-3-2-audit-remediation` will
land the file post-v1.3.2 close.
