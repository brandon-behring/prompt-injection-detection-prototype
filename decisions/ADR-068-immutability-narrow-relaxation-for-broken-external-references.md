---
adr_id: "068"
slug: immutability-narrow-relaxation-for-broken-external-references
title: Narrow immutability relaxation for broken external references in immutable ADRs (local-filesystem paths + aspirational upstream refs)
date: 2026-05-19
status: Accepted
claim_id: CLAIM-068
claim: >-
  ADR-067 established a narrow exception to the CLAUDE.md ADR-immutability
  rule for factual typos in cross-reference slug filenames (wrong-but-still-
  existing slug pointing at a wrong file in `decisions/`). The lychee CI
  introduced at v1.1.4 was non-functional from inception until v1.2.4
  (caught by the v1.2.3 patch + the additional v0.23.0 `--base` incompat
  fixed at v1.2.4); the FIRST end-to-end lychee scan at v1.2.4 surfaced
  TWO additional classes of broken markdown links inside immutable ADRs
  that are NOT covered by ADR-067's narrow exception but which exhibit
  the same audit-rationale (no decision content affected; CI can never
  resolve them; reader experience strictly improved by in-place fix):
  (a) **local-filesystem path references** — markdown links pointing at
  paths under `/home/<author>/...` or `../../../.claude/...` (author's
  own machine's filesystem leaking into committed text) — cannot resolve
  on any non-author machine, including CI runners and reviewer browsers;
  (b) **aspirational upstream references** — markdown links pointing at
  upstream resources (eval-toolkit/blob/main/docs/methodology/*.md) that
  do NOT exist upstream (author's mental model of planned-but-never-
  created upstream docs). ADR-068 extends the narrow-relaxation rule
  to cover both classes with the SAME §B2-style out-of-scope-list
  discipline (numeric values + methodology + prose + alternatives +
  non-slug frontmatter remain immutable). v1.2.6 applies the rule to
  fix 2 immutable-ADR markdown links (ADR-065 lines 108 + 122) plus
  the YAML frontmatter list-item in ADR-025 line 13. Mutable files
  (SPEC_SHEET.md + SPEC_GREENFIELD.md + WRITEUP/*.md + decisions/
  library_imports.md + CHANGELOG.md) are fixed in a separate commit
  without ADR-068 coverage (the rule applies ONLY to immutable ADRs).
source: v1.2.6 link-check fix-forward (root-cause analysis began during the v1.2.5 /exploring-options 4-question walk on 2026-05-19) — user picked all 4 recommended options including "Extend ADR-067 narrow relaxation → ADR-068 + in-place fix" + "Full structural fix — ADR-068 + DOI canon + triage"
acceptance_criterion: >-
  At v1.2.6 close: `decisions/ADR-068-immutability-narrow-relaxation-for-broken-external-references.md`
  exists (this file). `CLAUDE.md` §"Phase 0 workflow" immutability-rule
  block updated to cite both ADR-067 + ADR-068 as the two narrow exceptions.
  `decisions/README.md` §Lifecycle updated with the same dual-citation.
  `docs/GLOSSARY.md` entry for "Immutability relaxation" updated to list
  both classes. All 2 immutable-ADR markdown links flagged by lychee CI
  (ADR-065 lines 108 + 122) are replaced with descriptive prose preserving
  citation intent without retaining the broken link target. ADR-025 line 13
  (YAML frontmatter `references:` list-item pointing at non-existent
  eval-toolkit/blob/main/docs/methodology/thresholds.md) is replaced with a
  descriptive marker or the closest existing upstream URL. Lychee CI on
  the v1.2.6 push reports the affected immutable-ADR errors RESOLVED.
  Future PR reviews flag any in-place ADR edit that goes beyond the
  enumerated narrow scope (numeric values + methodology + prose + non-slug
  frontmatter + decision content remain immutable per the existing rule).
closing_commit: v1.2.6
supersedes: []
superseded_by: []
references:
  - CLAUDE.md  # immutability rule lives here; gets dual-narrow-exception update
  - decisions/README.md  # ADR lifecycle; gets dual-narrow-exception update
  - decisions/ADR-067-immutability-clarification-and-canonical-slug-reference.md  # precedent narrow relaxation
  - docs/GLOSSARY.md
transcript: transcripts/2026-05-19__v1-2-5-link-check-content-debt-and-immutability-extension.md
---

# ADR-068 — Narrow immutability relaxation for broken external references in immutable ADRs

## Status

Accepted (2026-05-19; second narrow clarification of the existing CLAUDE.md immutability rule — co-equal with ADR-067; covers a different class of factual defects).

## §A Context — discovery from the first end-to-end lychee scan

The lychee link-check CI workflow was introduced at v1.1.4 (`d3f63d8`) but was non-functional from inception until v1.2.4 due to a chain of v0.23.0 compatibility issues (`--exclude-mail` removed; `--base .` rejected). The v1.2.3 patch fixed `--exclude-mail`; the v1.2.4 patch fixed `--base`. Only on the v1.2.4 push (`3c44032`) did lychee execute end-to-end for the first time, surfacing 35 unique broken markdown links across 35+ files that had been masked for 5 patches.

Root-cause analysis (v1.2.5 /exploring-options walk, 2026-05-19) classified the failures into 7 patterns. Two of them — **A.1 local-filesystem path leakage** and **A.2 aspirational upstream references** — appear inside immutable ADRs (`decisions/ADR-NNN-<slug>.md` files) and are therefore protected by the CLAUDE.md immutability rule from in-place editing.

ADR-067 (v1.2.2) established a precedent narrow exception for factual typos in cross-reference slug filenames. The two newly-surfaced classes share the same audit rationale that motivated ADR-067:

1. **No decision content is affected.** A local-filesystem path is a citation/reference, not a methodology decision. An aspirational upstream link is a forward-reference to planned docs, not a methodology decision.
2. **CI cannot resolve them.** `file:///home/<author>/...` and `../../../.claude/...` paths require the author's own filesystem; they never resolve on any CI runner OR reviewer browser. Aspirational `eval-toolkit/blob/main/docs/methodology/*.md` URLs return 404 because those docs were planned but never created upstream.
3. **Reader experience strictly improves with in-place fix.** A reader clicking the broken link sees a 404. Replacing with descriptive prose preserves the citation intent + eliminates the 404.
4. **Audit trail is preserved.** The broken-link CONTENT is removed but the surrounding prose + the decision that referenced it remains immutable. Future `git log decisions/ADR-NNN.md` shows the original commit + the v1.2.6 broken-ref-fix commit; both are recoverable.

Both classes meet the §B-style narrow-scope test that ADR-067 applies to its own exception.

## §B Decision — narrow extension covering two additional classes

ADRs remain immutable for decision content (per CLAUDE.md + ADR-067 §B). ADR-067 covers the **factual-typo-in-cross-reference-slug** class. ADR-068 covers two additional narrow classes:

### B1 — In-scope corrections (allowed in-place per this ADR-068)

**Class X — Local-filesystem path references.** Markdown links (and YAML frontmatter URL strings) where the URL targets a path on the author's local filesystem:

- `file:///home/<author>/...`
- `/home/<author>/.../<anything>.md`
- `../../../.claude/projects/.../memory/<anything>.md`
- Any path resolving to a directory NOT present in the repo (verifiable via `[ -e <path> ]` check at CI runner).

Fix discipline: replace the broken link with descriptive prose that preserves the citation intent. Example transformation:
- Before: `[memory/library_first_is_project_wide_invariant.md](../../../.claude/projects/.../memory/library_first_is_project_wide_invariant.md)`
- After: `` `memory/library_first_is_project_wide_invariant.md` (project-local Claude memory; not committed) ``

The reader sees the SAME citation text (which is informative on its own — they know what concept is being referenced) without the broken-link target.

**Class Y — Aspirational upstream references.** Markdown links pointing at upstream resources that do NOT exist on the upstream repo:

- `https://github.com/<owner>/<repo>/blob/<branch>/<path>` where the path returns 404 from the upstream repo's API.
- Includes the 9 references to `github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/{bootstrap,calibration,comparison,leakage,reproducibility,splits,text_dedup,thresholds}.md` — verified non-existent via `gh api repos/brandon-behring/eval-toolkit/contents/docs/methodology` returns 404.

Fix discipline: replace the broken link with either (a) a descriptive prose statement citing the actual upstream primitive (e.g., `eval_toolkit.bootstrap_ci` from the [eval-toolkit README](https://github.com/brandon-behring/eval-toolkit#readme)) OR (b) the closest existing upstream URL (e.g., the repo's top-level README or the relevant source file). Preserves citation intent without retaining the broken link target.

### B2 — Out-of-scope changes (REQUIRE superseding ADR per existing rule)

Same as ADR-067 §B2; numeric values, methodology decisions, prose rationale, alternatives considered, non-slug frontmatter fields, and table content all remain immutable. ADR-068 covers ONLY the link-target text in broken external references; the surrounding sentence + paragraph + decision content stays as written.

Important: **ADR-068 applies ONLY to IMMUTABLE ADRs**. Mutable files (SPEC_SHEET.md, SPEC_GREENFIELD.md, WRITEUP/*.md, decisions/library_imports.md, CHANGELOG.md, NEXT_STEPS.md, README.md, etc.) can be edited freely per their existing mutability convention and do NOT need ADR-068 cover.

### B3 — Commit message convention

In-place broken-external-reference fixes in immutable ADRs carry a commit message of the form:

```
docs: ADR-NNN broken-external-reference fixes per ADR-068

Per ADR-068 narrow-relaxation rule (Class X / Class Y): broken external
references to local-filesystem paths or aspirational upstream resources
MAY be corrected in-place in immutable ADRs. This commit fixes:

- decisions/ADR-XXX.md:LINE — Class X local-fs path `<path>` → descriptive prose `<replacement>`
- decisions/ADR-YYY.md:LINE — Class Y aspirational upstream `<url>` → descriptive prose `<replacement>`
  ...

No decision content changed. ADR audit trail preserved.
```

### B4 — Future PR review discipline (unchanged from ADR-067)

In-place ADR edits that go beyond the narrow scopes (ADR-067 slug typos + ADR-068 broken external refs) should be flagged by PR review + require a new superseding ADR per the existing rule. ADR-068 does NOT establish a slippery slope; it codifies a specific narrow class adjacent to ADR-067.

## §C Decision — apply in the v1.2.6 fix-forward (consolidated inventory)

### C1 — Immutable-ADR markdown links covered by ADR-068 (3 fixes)

| File:line | Class | Broken link | Replacement |
|---|---|---|---|
| `decisions/ADR-065-writeup-accuracy-narrative-and-callout-conventions.md:108` | X | `[memory/adr-029-immutability-misattribution-historical-drift.md](../../../.claude/projects/.../memory/adr-029-immutability-misattribution-historical-drift.md)` | `` `memory/adr-029-immutability-misattribution-historical-drift.md` (project-local Claude memory; not committed) `` |
| `decisions/ADR-065-writeup-accuracy-narrative-and-callout-conventions.md:122` | X | `[memory/library_first_is_project_wide_invariant.md](../../../.claude/projects/.../memory/library_first_is_project_wide_invariant.md)` | `` `memory/library_first_is_project_wide_invariant.md` (project-local Claude memory; not committed) `` |
| `decisions/ADR-025-dual-policy-threshold-characterization.md:13` (YAML frontmatter `references:` list-item) | Y | `https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/thresholds.md` | Replace with `eval_toolkit.thresholds` (the actual upstream primitive surface), OR closest-existing upstream URL: `https://github.com/brandon-behring/eval-toolkit#readme`. Choose the README pointer for ADR-025 line 13 since it's the references-list field. |

### C2 — Mutable files (NOT covered by ADR-068; fixed separately in the v1.2.6 fix-forward)

For completeness — mutable files have similar fixes applied without ADR-068 coverage:

- `SPEC_SHEET.md` lines 313, 314, 316, 335: 4 aspirational eval-toolkit/methodology refs
- `SPEC_GREENFIELD.md` lines 82, 98, 111, 167, 172, 174, 203: 7 aspirational refs
- `WRITEUP/data-decisions.md` lines 96, 126, 134: 3 aspirational refs
- `WRITEUP/threshold-policy.md` line 56: 1 aspirational ref
- `decisions/library_imports.md` line 182: 1 local-fs path ref

These edits don't need ADR-068 cover; the mutability convention covers them.

## §D Decision — CLAUDE.md + decisions/README.md updates

Both documents get the dual-narrow-exception update (cites both ADR-067 + ADR-068):

**CLAUDE.md §"Phase 0 workflow"** (after the existing immutability line; replacing the prior ADR-067-only narrow-exception clause):

> The ADR is the source of truth. ADRs are immutable; supersede via new ADR marking prior `status: superseded-by-NNN`.
>
> **Narrow exceptions** (per [ADR-067](./ADR-067-immutability-clarification-and-canonical-slug-reference.md) + [ADR-068](./ADR-068-immutability-narrow-relaxation-for-broken-external-references.md)): TWO factual-defect classes MAY be corrected in-place with a commit message citing the relevant ADR + listing per-file corrections:
>
> 1. **Cross-reference slug filename typos** (per ADR-067) — a slug pointing at a wrong-but-existing file in `decisions/`.
> 2. **Broken external references** (per ADR-068) — markdown links pointing at local-filesystem paths or aspirational upstream resources that do not exist.
>
> ALL other content (numeric values, methodology, prose, alternatives, non-slug frontmatter, table data) remains immutable per the existing rule.

**`decisions/README.md` §Lifecycle** (similar dual-citation update).

## §E Consequences

### E1 — Reader experience improved (immutable-ADR class)

After the v1.2.6 fix-forward, readers reading ADR-025 / ADR-065 see descriptive prose where they previously saw broken markdown links. No more 404s on CI runners. No more misleading citation targets for non-author readers.

### E2 — Audit-trail discipline preserved

The 3 immutable-ADR fixes do NOT change decision content; ADR audit trail remains intact. Per-file `git log` shows the original commit + the v1.2.6 broken-ref-fix commit; both are recoverable. The narrow scope (§B2 out-of-scope) prevents slippery-slope drift to decision-content edits.

### E3 — Documentation debt paid down (v1.1.4 → v1.2.6 trail)

The lychee link-check CI was introduced at v1.1.4 as an "URL rot defense" but was non-functional from inception. v1.2.3 + v1.2.4 fixed the workflow's v0.23.0 compat issues; v1.2.6 closes the surfaced content debt (35 unique broken URLs across 7 root-cause classes). The lychee CI now runs end-to-end + actually catches link rot going forward.

### E4 — Two-ADR symmetry

ADR-067 and ADR-068 are co-equal narrow exceptions to the same CLAUDE.md immutability rule:
- ADR-067: slug typos in cross-references (wrong-but-existing target)
- ADR-068: broken external refs (target doesn't exist anywhere)

Both follow the same §B-discipline: in-scope corrections + out-of-scope changes + commit-message-convention + future-PR-review-discipline.

### E5 — Future PRs flagged on out-of-scope edits

If a future patch attempts to edit decision content in-place under the guise of ADR-067 or ADR-068, PR review should flag the diff + require a superseding ADR. The narrow-relaxation rules are NOT slippery slopes; they codify specific, well-defined factual-defect classes.

### E6 — Cost-trivial

$0. CPU-only edits across 3 immutable-ADR lines (ADR-025 line 13 + ADR-065 lines 108, 122) + the CLAUDE.md / decisions/README.md / GLOSSARY clarification updates.

## Linked ADRs

- **References**:
  - CLAUDE.md — the source-of-truth for immutability (clarified by ADR-067 + ADR-068 dual-narrow-exception)
  - decisions/README.md — the ADR lifecycle + frontmatter schema (also gets the dual-citation update)
  - [ADR-067](./ADR-067-immutability-clarification-and-canonical-slug-reference.md) — precedent narrow relaxation for slug typos; ADR-068 extends with two additional classes
- **Source**: v1.2.6 link-check fix-forward; root-cause analysis began during the v1.2.5 /exploring-options 4-question walk (2026-05-19), where the user picked "Extend ADR-067 narrow relaxation → ADR-068 + in-place fix (Recommended)" on Question 1 + "Full structural fix — ADR-068 + DOI canon + triage (Recommended)" on Question 4.

## Transcript

`transcripts/2026-05-19__v1-2-5-link-check-content-debt-and-immutability-extension.md` — captures the multi-class link-check content debt close + the ADR-068 narrow relaxation extension.
