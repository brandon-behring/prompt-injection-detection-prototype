---
adr_id: "067"
slug: immutability-clarification-and-canonical-slug-reference
title: Narrow immutability relaxation for factual-typo fixes in cross-reference slug filenames
date: 2026-05-19
status: Accepted
claim_id: CLAIM-067
claim: >-
  The ADR-immutability rule per CLAUDE.md ("ADRs are immutable; supersede via
  new ADR") was authored to protect DECISION content (methodology choices,
  locked numeric values, alternatives considered, prose rationale) from
  post-hoc revision — the audit-trail discipline that lets reviewers
  reconstruct what-was-thought-at-each-tag. Applying that same rule to
  **factual-typo defects in cross-reference slug filenames** (wrong slug
  pointing at a wrong-but-existing file in `decisions/`) is over-strict:
  fixing such defects does NOT alter decision content + does NOT break the
  audit trail. The current state — 14 broken slug-reference patterns
  documented in `.lycheeignore` + ADR-064 §D as "flagged-not-fixed" —
  imposes reader friction (404s on in-ADR cross-refs) without protecting
  anything load-bearing. v1.2.2 ADR-067 codifies a narrow exception:
  **factual typos in cross-reference slug filenames MAY be corrected
  in-place** in the affected ADR file, with the commit message citing
  ADR-067 + listing the per-file corrections. ALL other content (numeric
  values, methodology decisions, prose, alternatives considered, table
  data, frontmatter fields other than slug refs) remains immutable per
  the existing rule. v1.2.2 Commit 2 applies the relaxation to fix the
  14 documented broken refs (12 with canonical-correct slug substitutes;
  2 ADR-029 misattributions handled by removing the broken ref + citing
  CLAUDE.md directly). The 14 corresponding `.lycheeignore` patterns are
  deleted in the same commit (no longer ignored — actually working).
source: transcripts/2026-05-19__v1-2-2-library-first-refactor-and-immutability-clarification.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.2.2 close: `decisions/ADR-067-immutability-clarification-and-canonical-slug-reference.md`
  exists (this file). `CLAUDE.md` §"Phase 0 workflow" immutability-rule
  block updated with the narrow-relaxation clarification. `decisions/README.md`
  §Lifecycle updated with the same narrow-relaxation language.
  `docs/GLOSSARY.md` carries an entry for "Immutability relaxation
  (factual-typo class)" cross-referencing this ADR. All 14 broken
  slug-reference patterns flagged in `.lycheeignore` + ADR-064 §D
  resolve to canonical-correct slugs in the affected immutable ADRs
  (ADR-046, ADR-048, ADR-059, ADR-060, ADR-063, and any others
  discovered during `grep -rn` audit). The 14 corresponding patterns
  in `.lycheeignore` are deleted. The 2 ADR-029 misattributions
  (referencing non-existent "immutability ADR-029" slugs) are
  corrected by removing the broken ref + citing CLAUDE.md directly.
  Lychee CI passes on the v1.2.2 push (the previously-ignored refs
  now resolve cleanly without needing ignore patterns). Future PR
  reviews flag any in-place ADR edit that goes beyond slug-filename
  correction (numeric values + methodology + prose remain immutable
  per the existing rule).
closing_commit: v1.2.2
supersedes: []
superseded_by: []
references:
  - CLAUDE.md  # immutability rule lives here
  - decisions/README.md  # ADR lifecycle + frontmatter schema
  - decisions/ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md  # §D flagged-not-fixed inventory
  - decisions/ADR-066-library-first-carryforward-refactor-v1-2-2.md  # bundled at same release
  - .lycheeignore  # 14 patterns deleted after Commit 2 applies fixes
  - docs/GLOSSARY.md
transcript: transcripts/2026-05-19__v1-2-2-library-first-refactor-and-immutability-clarification.md
---

# ADR-067 — Narrow immutability relaxation for factual-typo fixes in cross-reference slug filenames

## Status

Accepted (2026-05-19; narrow clarification of the existing CLAUDE.md immutability rule — does NOT supersede prior ADRs; codifies a narrow exception applicable to factual-typo defects in cross-reference slug filenames only).

## §A Context — what the immutability rule was protecting + what it wasn't

CLAUDE.md §"Phase 0 workflow" states: *"The ADR is the source of truth. ADRs are immutable; supersede via new ADR marking prior `status: superseded-by-NNN`."* This rule was authored to protect the audit-trail discipline: a reviewer should be able to read any tagged release's ADRs + reconstruct exactly what-was-decided-at-that-tag without worrying that the decision content was edited post-hoc.

The rule applies cleanly to **decision content**:
- Methodology choices (e.g., "ADR-016 locks LODO 4-fold × 3 seeds")
- Locked numeric values (e.g., "ADR-019 locks LoRA r=8, alpha=16")
- Alternatives considered + why rejected
- Prose rationale + the consequences section
- Frontmatter fields like `claim`, `acceptance_criterion`, `closing_commit`

For these, the immutability rule is load-bearing: editing them in-place would silently rewrite history. The supersede-via-new-ADR mechanism preserves the audit trail.

The rule was ALSO applied — over-strictly — to **factual-typo defects in cross-reference slug filenames**. Example from ADR-046 line 15: `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md` is a broken reference (the actual filename is `ADR-006-headline-metrics-and-statistical-apparatus.md`). Fixing this typo:
- Does NOT change any decision content
- Does NOT alter the audit trail (the meaning of ADR-046 line 15's cross-reference is unchanged — it always meant "see ADR-006"; only the slug is typo'd)
- DOES improve reader experience (the in-ADR link resolves correctly)

ADR-064 §D documented 9 broken slug references; subsequent audit (.lycheeignore at v1.2.0 close) surfaced 14 total patterns. Treating these as "flagged-not-fixed per ADR-immutability discipline" imposes reader friction (404s on in-ADR cross-refs; lychee CI noise; documentation debt) without protecting any decision content.

This ADR codifies a narrow exception.

## §B Decision — narrow relaxation: factual-typo class only

ADRs remain immutable for **decision content** (per CLAUDE.md): methodology choices, locked values, alternatives considered, prose, frontmatter fields other than slug refs, table data, references list (except as covered below).

**Narrow exception**: **factual typos in cross-reference slug filenames** MAY be corrected in-place in the affected ADR file, subject to the following constraints:

### B1 — In-scope corrections (allowed in-place)

1. **Broken cross-reference slug filenames** where a slug points at a wrong-but-existing canonical file in `decisions/`. Example: `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md` → `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md` (the canonical filename for ADR-006).
2. **Slug filenames in the `references:` frontmatter list** that point at the wrong canonical filename. Same rule.
3. **Slug filenames in markdown body link syntax** (`[link text](decisions/ADR-NNN-wrong-slug.md)` → `[link text](decisions/ADR-NNN-correct-slug.md)`).

### B2 — Out-of-scope changes (REQUIRE superseding ADR per existing rule)

- **Numeric values** in claim text, acceptance criterion, prose, or tables (e.g., a stale `$9.92` cost figure stays as written; supersession via new ADR + postscript chain, as v1.2.1 ADR-065 §E did for ADR-063's $9.92).
- **Methodology decisions** (e.g., "LODO 4-fold" → "LODO 5-fold" is a decision change; requires superseding ADR).
- **Prose rationale** in §Context / §Decision / §Consequences (re-writing meaning requires supersession).
- **Alternatives considered list** (the alternatives recorded at decision time stay as recorded; supersession via new ADR for revisiting).
- **Frontmatter fields other than slug refs**: `claim_id`, `claim`, `source`, `acceptance_criterion`, `closing_commit`, `supersedes`, `superseded_by`, `transcript` all remain immutable.
- **Table content** (e.g., the per-rung AUPRC table in RESULTS.md is in scope of the writeup, not this ADR; but if a table appears IN an ADR body, the values stay).

### B3 — Commit message convention

In-place factual-typo fixes carry a commit message of the form:

```
docs: ADR-NNN factual-typo fixes per ADR-067 (slug filename corrections)

Per ADR-067 narrow-relaxation rule: factual typos in cross-reference slug
filenames MAY be corrected in-place. This commit fixes:

- decisions/ADR-XXX.md:LINE — was `<wrong-slug>` → corrected to `<right-slug>`
- decisions/ADR-YYY.md:LINE — was `<wrong-slug>` → corrected to `<right-slug>`
  ...

No decision content changed. ADR audit trail preserved.
```

The per-file enumeration in the commit message provides the audit trail: future readers running `git log` see exactly which slug refs were corrected when.

### B4 — Future PR review discipline

In-place ADR edits that go beyond the narrow scope (numeric values; methodology; prose; non-slug frontmatter) should be flagged by PR review + require a new superseding ADR per the existing rule. This ADR-067 narrow relaxation does NOT establish a slippery slope; it codifies a specific narrow class.

## §C Decision — apply the relaxation at v1.2.2 Commit 2 (consolidated inventory)

The full inventory of broken slug-reference patterns (per `.lycheeignore` at v1.2.0 close + post-v1.2.1 audit) is 14 patterns mapping to 12 canonical-correct slug substitutes + 2 ADR-029 misattributions:

### C1 — Canonical-correct slug substitutions (12 patterns)

| Broken pattern (in `.lycheeignore`) | Canonical-correct slug |
|---|---|
| `decisions/ADR-005-methodology-principles.md` | `decisions/ADR-005-methodology-principles.md` |
| `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md` | `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md` |
| `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md` | `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md` |
| `decisions/ADR-013-kit-ratify-bulk-strictness-intake-notebook-persistence.md` | `decisions/ADR-013-kit-ratify-bulk-strictness-intake-notebook-persistence.md` |
| `decisions/ADR-016-data-design-bundle.md` | `decisions/ADR-016-data-design-bundle.md` |
| `decisions/ADR-019-lora-and-transformer-training-recipe.md` | `decisions/ADR-019-lora-and-transformer-training-recipe.md` |
| `decisions/ADR-020-compute-infrastructure-and-cost-discipline.md` | `decisions/ADR-020-compute-infrastructure-and-cost-discipline.md` |
| `decisions/ADR-023-calibration-battery-and-interventions.md` | `decisions/ADR-023-calibration-battery-and-interventions.md` |
| `decisions/ADR-030-deliverable-format-quarto-html-site.md` | `decisions/ADR-030-deliverable-format-quarto-html-site.md` |
| `decisions/ADR-032-hf-hub-publication-headline-rungs-only.md` | `decisions/ADR-032-hf-hub-publication-headline-rungs-only.md` |
| `decisions/ADR-037-python-version-pin-3-13.md` | `decisions/ADR-037-python-version-pin-3-13.md` |
| `decisions/ADR-046-phase-4-analysis-implementation-bundle.md` | `decisions/ADR-046-phase-4-analysis-implementation-bundle.md` |

Commit 2 applies these substitutions via `grep -rn` audit across `decisions/*.md` + `find / -replace` edits.

### C2 — ADR-029 immutability misattributions (2 patterns)

Two patterns in `.lycheeignore` reference a non-existent "ADR-029 immutability" file:

- `ADR-029` — no such file exists
- `ADR-029` — no such file exists

The actual `decisions/ADR-029-test-marker-strategy-four-marker-ratification.md` is about test markers, NOT immutability. The misattribution surfaced because older CHANGELOG entries + ADR cross-refs cited "ADR-029" as the immutability ADR, but the immutability rule actually lives in `CLAUDE.md` (per memory entry `adr-029-immutability-misattribution-historical-drift`).

**Fix at Commit 2**: each occurrence of the broken ADR-029 immutability ref gets removed + replaced with an inline citation to CLAUDE.md (or to ADR-067 itself once it lands, since ADR-067 codifies the discipline). Pattern:

- `[ADR-029 immutability](decisions/ADR-029-...md)` → `CLAUDE.md immutability rule (clarified at ADR-067)`

### C3 — `.lycheeignore` cleanup at Commit 2

After the in-place corrections land, the 14 corresponding `.lycheeignore` patterns are deleted (since the refs are no longer broken). The .lycheeignore retains the HF Hub patterns + GitHub anchor patterns (those are intentional + unrelated).

Future `.lycheeignore` discipline: prefer fixing over ignoring (per ADR-064 §C2); only add ignore patterns when an external URL is verified-good for humans but 403s bots. Internal ADR cross-refs do NOT go in `.lycheeignore` — they get fixed per this ADR-067 narrow-relaxation rule.

## §D Decision — CLAUDE.md + decisions/README.md updates

Both documents get a one-paragraph addition next to their immutability-rule statement:

**CLAUDE.md §"Phase 0 workflow"** (after the existing immutability line):

> The ADR is the source of truth. ADRs are immutable; supersede via new ADR marking prior `status: superseded-by-NNN`.
>
> **Narrow exception** (per [ADR-067](./ADR-067-immutability-clarification-and-canonical-slug-reference.md)): factual typos in cross-reference slug filenames MAY be corrected in-place with a commit message citing ADR-067 + listing per-file corrections. ALL other content (numeric values, methodology, prose, alternatives, non-slug frontmatter) remains immutable.

**`decisions/README.md` §Lifecycle** (similar addition).

## §E Consequences

### E1 — Reader experience improved

After v1.2.2 Commit 2, readers clicking in-ADR cross-references resolve to the correct canonical filenames. No more 404s. No more `.lycheeignore` patterns hiding the brokenness from CI while showing 404s to humans.

### E2 — Audit-trail discipline preserved

The 12 slug-filename corrections do NOT change decision content; ADR audit trail remains intact (any future `git log decisions/ADR-XXX.md` shows the original commit + the v1.2.2 typo-fix commit; both are recoverable). The narrow scope (§B2 out-of-scope changes) prevents slippery-slope drift to decision-content edits.

### E3 — Documentation debt paid down

`.lycheeignore` shrinks by 14 patterns (from a v1.2.1 baseline of ~17 patterns to ~3 retained patterns for HF Hub + GitHub anchors). ADR-064 §D's "9 broken refs" inventory + the v1.2.1 post-audit "14 patterns" inventory is closed; future readers consult ADR-067 §C for the historical record.

### E4 — Future-proofing

If future patches introduce new broken slug refs (e.g., an ADR rename), ADR-067 §B is the canonical rule: fix in-place + commit message cites ADR-067. The `.lycheeignore` is NOT the right venue (per ADR-064 §C2's "prefer fixing over ignoring" discipline).

### E5 — ADR-029 misattribution permanently resolved

The historical drift (where CHANGELOG entries + cross-refs cited "ADR-029 immutability") is resolved by routing readers to CLAUDE.md (where the rule actually lives) + ADR-067 (which clarifies the narrow relaxation). Future content should cite CLAUDE.md + ADR-067 directly; historical CHANGELOG entries are unchanged (those are immutable per the project's CHANGELOG-as-historical-record convention — also captured in memory `adr-029-immutability-misattribution-historical-drift`).

### E6 — Cost-trivial

$0. CPU-only edits. No methodology change.

## Linked ADRs

- **References**:
  - CLAUDE.md — the source-of-truth for immutability (clarified by this ADR's narrow exception)
  - decisions/README.md — the ADR lifecycle + frontmatter schema (also gets the narrow-exception clarification at Commit 1)
  - [ADR-064](./ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md) §D — predecessor inventory of broken slug refs (flagged-not-fixed; this ADR enables the fix)
  - [ADR-066](./ADR-066-library-first-carryforward-refactor-v1-2-2.md) — bundled at v1.2.2 (independent decision)
- **Source**: `/exploring-options` round 8 Q3 (2026-05-19) — user signaled the broken-refs state was "weird, sounds like a mistake to have made that" → recommendation switched from "document the errata" (original Option B) to "fix the errata + codify narrow rule" (Option A).

## Transcript

`transcripts/2026-05-19__v1-2-2-library-first-refactor-and-immutability-clarification.md` — captures rounds 7 + 8 + the 9-commit execution.
