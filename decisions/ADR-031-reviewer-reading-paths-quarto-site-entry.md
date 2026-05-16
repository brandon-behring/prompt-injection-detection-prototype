---
adr_id: "031"
slug: reviewer-reading-paths-quarto-site-entry
title: Reviewer reading paths — index.qmd entry-point with Quarto sidebar nav (supersedes ADR-004)
date: 2026-05-16
status: Accepted
claim_id: CLAIM-031
claim: Phase 0-07 supersedes ADR-004 (PDF-as-hub framing) while preserving its hub-and-spoke structure plus A1+A2 dual-audience reading paths plus B4 open-ended-layered reading-time stance. The hub artefact shifts from PDF to the Quarto-rendered HTML site introduced by ADR-030 — specifically the new index.qmd entry-point file at repo root plus the sidebar nav declared in _quarto.yml. index.qmd plays the role of the PDF cover sheet — it carries reviewer reading-path guidance (A1 skim ~15 minutes; A2 audit ~60 minutes; deep-dive reproduce-numbers path) plus a TOC link list into WRITEUP.md plus WRITEUP/ spokes plus decisions/ ADRs plus configs plus results. Sidebar nav in _quarto.yml provides global navigation across every page so a reviewer never needs to backtrack to index.qmd to jump topics. The spoke list finalized at this lock — eight spokes — WRITEUP/eval-design.md plus WRITEUP/methodology-guarantees.md plus WRITEUP/limitations-and-future-work.md plus WRITEUP/data-decisions.md plus WRITEUP/model-rungs.md plus WRITEUP/threshold-policy.md plus WRITEUP/reference-scorer-audit.md plus WRITEUP/reproducibility.md (new — required by ADR-034 to document the T0+T1+T3 tier ladder). Every spoke is standalone-readable plus closes with a limitations-plus-when-to-extend subsection per ADR-005. Cross-link discipline — relative markdown paths between spokes resolve under Quarto rendering; permalinks from outside the site use stable submission tag per ADR-033. The ADR-004 PDF cover-to-cover constraint is replaced by a single-screen-fit constraint on index.qmd plus the Quarto sidebar must surface all spokes (no link-only depth files hidden from the sidebar). Limitation — Quarto sidebar nav requires reviewers to be in-browser plus comfortable with sidebar UI; the offline-reading degradation noted in ADR-030 applies here too. Extension condition — if a new methodology spoke surfaces during Phase 1+ (e.g., a contamination-scan deep dive that is too long for limitations-and-future-work.md), add the spoke to WRITEUP/ plus update _quarto.yml sidebar plus add an index.qmd link entry; no superseding ADR needed for spoke addition (the spoke list is provisional); spoke removal does require a superseding ADR (audit-trail discipline).
source: SPEC_GREENFIELD.md §Brief ledger row 302 (reviewer profile) supersession trigger + ADR-004 supersession trigger + Phase 0-07 walk Q1
acceptance_criterion: ADR-004 frontmatter status changes from Accepted to Superseded with superseded_by 031; SPEC_GREENFIELD ledger row 302 (Reviewer profile) carries a supersession note pointing at ADR-031; index.qmd exists at repo root with three reading-path sections (A1 quick-skim plus A2 audit plus deep-dive reproduce-numbers) plus a TOC link list into WRITEUP.md plus all 8 spokes plus decisions/ plus configs/ plus results/; _quarto.yml sidebar block surfaces every spoke under a Methodology section plus every ADR under a Decisions section (Quarto sidebar auto-include glob applied to the decisions/ADR-*.md pattern); WRITEUP/reproducibility.md exists as a placeholder spoke skeleton with at minimum a title plus a tier-ladder table stub (full content populated at Phase 5 per ADR-034); tests/test_invariants.py contains skip-marked stub test_index_qmd_reading_paths_present asserting index.qmd exists and contains the three reading-path section headers; SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit: 7979dc9
supersedes: "004"
references:
  - https://quarto.org/docs/websites/website-navigation.html
  - https://quarto.org/docs/websites/website-tools.html#sidebar-tools
  - decisions/ADR-004-reviewer-profile-and-hub-and-spoke-writeup.md
  - decisions/ADR-005-project-level-methodology-principles.md
  - decisions/ADR-030-deliverable-format-quarto-html-site.md
  - decisions/ADR-034-reproducibility-tier-full-ladder.md
transcript: transcripts/2026-05-16__phase-0-07__submission-deliverables.md
---

# ADR-031: Reviewer reading paths — index.qmd entry-point with Quarto sidebar nav

## Status

Accepted (2026-05-16). **Supersedes ADR-004** (reviewer profile + hub-and-spoke writeup with PDF as hub). Closes the reading-path companion to ADR-030's deliverable-format pivot. Phase 0-07 Q1 second of two surgical supersession ADRs.

## Context

ADR-004 (2026-05-15) locked the reviewer profile as dual-audience (A1 hiring manager + A2 ML researcher) with B4 open-ended-layered reading-time stance and hub-and-spoke writeup structure where the *PDF was the hub* (≈ 10-15 pages) and topic markdown files under `WRITEUP/` were the spokes.

ADR-030 (2026-05-16) supersedes ADR-002's PDF + repo dual-artifact deliverable with a repo-only deliverable rendered as a Quarto HTML site. The PDF artefact no longer exists — so the "PDF is the hub" claim from ADR-004 needs explicit superseding.

What survives from ADR-004:
- **Dual-audience A1+A2 profile** (not a mixed-panel A3 framing).
- **B4 reading-time stance** (open-ended, layered): ~15 min skim path for A1, ~60 min audit path for A2, unbounded deep-dive for code+ADR audit.
- **Hub-and-spoke structure** — focused hub + topic spokes.
- **Spokes remain markdown files under `WRITEUP/`** — content unchanged.

What needs replacement:
- **Hub artefact**: PDF → Quarto site `index.qmd` entry-point + sidebar nav.
- **Cross-link discipline**: PDF-to-spoke permalinks at submission tag → Quarto relative-path cross-links within the site + stable-tag URLs for outbound references (still per ADR-033 tag pinning).
- **Spoke discoverability**: PDF readers had to follow embedded links → Quarto site readers see all spokes in the sidebar nav simultaneously (a strict affordance upgrade).

The spoke list from ADR-004 was provisional (7 spokes); Phase 0-07 finalizes the list at 8 spokes — the 7 from ADR-004 plus a new `WRITEUP/reproducibility.md` required by ADR-034 to document the T0+T1+T3 reproducibility tier ladder.

## Decision

**Reviewer profile** (preserved from ADR-004): A1 + A2 dual-audience, B4 open-ended-layered reading-time stance.

**Hub artefact**: `index.qmd` at repo root + Quarto sidebar nav declared in `_quarto.yml`. Together these replace the PDF cover sheet + table-of-contents role.

**`index.qmd` content** (entry-point structure):

1. **Title + author + submission tag** (top matter; Quarto renders YAML frontmatter into the page header).
2. **Reviewer reading paths** section with three sub-paths:
   - **Quick-skim path (A1 — hiring manager, ~15 min)** — links to `WRITEUP.md` §1-2, headline-results section, limitations spoke.
   - **Audit path (A2 — ML researcher, ~60 min)** — links to full `WRITEUP.md` + critical-path spokes (eval-design, methodology-guarantees, limitations, reference-scorer-audit).
   - **Deep-dive (reproduce numbers)** — links to reproducibility spoke + Makefile targets + HF Hub model URLs.
3. **Repo map** — flat enumeration of `src/`, `scripts/`, `configs/`, `decisions/`, `results/`, `WRITEUP.md` + `WRITEUP/` with one-line descriptions.

**Sidebar nav** declared in `_quarto.yml` (Quarto websites sidebar syntax):

```yaml
website:
  sidebar:
    style: docked
    search: true
    contents:
      - section: "Reading guide"
        contents: [index.qmd]
      - section: "Methodology"
        contents:
          - WRITEUP.md
          - WRITEUP/eval-design.md
          - WRITEUP/methodology-guarantees.md
          - WRITEUP/limitations-and-future-work.md
          - WRITEUP/data-decisions.md
          - WRITEUP/model-rungs.md
          - WRITEUP/threshold-policy.md
          - WRITEUP/reference-scorer-audit.md
          - WRITEUP/reproducibility.md
      - section: "Decisions (ADRs)"
        contents:
          - auto: "decisions/ADR-*.md"
```

**Spoke list finalization** (8 spokes; supersedes ADR-004's provisional 7):

| Spoke | Role | Phase populated |
|---|---|---|
| `WRITEUP/data-decisions.md` | source slate, dedup, splits, leakage scan | Phase 1 |
| `WRITEUP/model-rungs.md` | frozen vs LoRA vs full-FT, matched-budget controls | Phase 2 |
| `WRITEUP/eval-design.md` | OOD slate, calibration battery, paired-bootstrap protocol | Phase 3-4 |
| `WRITEUP/reference-scorer-audit.md` | LLM-judge + kappa findings | Phase 4 |
| `WRITEUP/threshold-policy.md` | dual-policy detection + verification operating points | Phase 4 |
| `WRITEUP/methodology-guarantees.md` | banned-approaches surfaced as guarantees | Phase 5 |
| `WRITEUP/limitations-and-future-work.md` | structured limitations + extension conditions | Phase 5 |
| `WRITEUP/reproducibility.md` | **(NEW per ADR-034)** T0+T1+T3 tier ladder with commands | Phase 5 |

**Cross-link discipline**:
- Within the Quarto site: relative markdown paths (`[eval-design](WRITEUP/eval-design.md)`); Quarto resolves these at render time.
- From outside the site (e.g., reviewer email, GH issues, external papers): permalinks via stable submission tag per ADR-033 (`https://github.com/.../tree/v1.0.0/WRITEUP/eval-design.md`).

**Sidebar-visibility constraint**: every methodology spoke MUST appear in the sidebar. No link-only-depth spokes (the PDF-era pattern where a spoke was referenced by URL but absent from any nav). Reason: Quarto's sidebar IS the reader's navigation surface; spokes invisible to the sidebar are functionally hidden.

## Consequences

### Positive

- **Sidebar nav is a strict affordance upgrade over PDF embedded links** — reader sees all 8 spokes simultaneously; can jump between any pair without backtracking; full-text search across all pages.
- **`index.qmd` reading-path guide does the PDF cover-sheet job better** — explicit reader-profile-matched paths (A1 / A2 / deep-dive) instead of leaving the reader to infer reading order.
- **Spoke list finalized** — removes ADR-004's "provisional 7 spokes; final list in Phase 0-07" footnote; Phase 5 work knows the full spoke surface in advance.
- **Cross-link discipline simplified** — relative markdown paths within the site (Quarto resolves); stable-tag permalinks only needed for external references.
- **A1/A2/B4 framing preserved** — the dual-audience profile and reading-time stance from ADR-004 carry over unchanged; only the hub artefact swap is new.
- **`WRITEUP/reproducibility.md` slotted in** — ADR-034's tier-ladder documentation has an explicit home rather than being orphaned in WRITEUP.md proper.

### Negative / cost

- **8 spokes vs ADR-004's 7** — one additional spoke to populate at Phase 5 (reproducibility.md). Acceptable cost; aligned with ADR-034 acceptance criterion.
- **Sidebar nav requires in-browser reading** — offline readers see the static `_site/` snapshot but lose the sidebar's live search affordance. Mitigated by `_site.tar.gz` GH release asset per ADR-033.
- **`index.qmd` is a new file** — content overlap risk with `WRITEUP.md` §1 motivation (potential duplication). Mitigation: `index.qmd` is reading-paths-only (TOC + reading guides); `WRITEUP.md` is methodology content. Distinct concerns.

### Neutral

- **Sidebar `auto:` pattern for ADRs** — `auto: "decisions/ADR-*.md"` glob-expands at Quarto build time; all 34+ ADRs auto-list without manual maintenance. New ADRs added later (Phase 0-08+) appear automatically.
- **`WRITEUP/reproducibility.md` content fully defined by ADR-034** — this ADR only carves out the slot; ADR-034 owns the content schema.
- **No required `WRITEUP.md` content edits** — `WRITEUP.md` itself is unchanged by this ADR; the reading-paths and TOC are in `index.qmd`, not retrofitted into `WRITEUP.md`.

### Limitation

The Quarto sidebar nav assumes the reader is comfortable with a docs-site UI. Reviewers expecting a single-document PDF cover-to-cover read get a discovery affordance instead of a linear path. Mitigation: `index.qmd` "Quick-skim path (A1)" section provides explicit linear ordering for readers who prefer that approach.

### Extension condition for revisit

- **Spoke addition**: if Phase 1+ surfaces a new methodology spoke (e.g., a contamination-scan deep dive that doesn't fit in `limitations-and-future-work.md`), add the spoke to `WRITEUP/` + update `_quarto.yml` sidebar + add an `index.qmd` link entry. No superseding ADR needed for spoke addition.
- **Spoke removal**: requires a superseding ADR (audit-trail discipline; spoke removal is a methodology-coverage claim change, not a presentation choice).
- **Sidebar structure rework**: if Quarto sidebar limits prove costly (e.g., 30+ ADRs make the Decisions section unwieldy), introduce sub-categorization via superseding ADR.
- **`index.qmd` reading-path expansion**: a new reviewer profile (e.g., regulator audit path with compliance-focused links) added via spoke + sidebar updates; no superseding ADR needed for path addition since the profile structure is extensible.

## Alternatives Considered

- **Monolithic Quarto page (single `WRITEUP.qmd` with no spokes)** — discards the hub-and-spoke pattern; single-page-with-anchors approach. *Rejected because* ADR-004's dual-audience reasoning (different readers want different depth) still applies and Quarto sidebar nav is the natural fit.
- **`README.md` as the hub instead of `index.qmd`** — GitHub renders `README.md` natively at repo root; Quarto can include it too. *Rejected because* Quarto convention treats `index.qmd` as the website landing page; using `README.md` would force a redirect chain or two-entry-point confusion.
- **PDF cover sheet retained + sidebar nav supplement** — hybrid PDF-for-A1 + HTML-for-A2 split. *Rejected because* ADR-030 explicitly removed PDF surface; reintroducing for cover-sheet role re-adds the LaTeX dependency the supersession was removing.
- **Keep ADR-004's 7-spoke list (skip `WRITEUP/reproducibility.md`)** — defer ADR-034's tier ladder to a section within `WRITEUP.md` proper. *Rejected because* the tier-ladder content is substantial (~1-2 pages with commands + cost notes) and pollutes the methodology narrative; standalone spoke is cleaner.

## References

- Quarto website navigation — https://quarto.org/docs/websites/website-navigation.html
- Quarto sidebar tools — https://quarto.org/docs/websites/website-tools.html#sidebar-tools
- ADR-004 (reviewer profile + hub-and-spoke PDF — superseded by this ADR)
- ADR-005 (project-level methodology principles — spokes implement the principles)
- ADR-030 (Quarto deliverable format — this ADR's reading-path framing is rendered on top of ADR-030's site)
- ADR-034 (reproducibility tier — owns `WRITEUP/reproducibility.md` content schema)

## Transcript

See `transcripts/2026-05-16__phase-0-07__submission-deliverables.md` for the conversation that led to this decision (Q1 walk + supersession framing).
