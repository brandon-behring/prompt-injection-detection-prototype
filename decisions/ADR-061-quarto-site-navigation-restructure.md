---
adr_id: "061"
slug: quarto-site-navigation-restructure
title: Quarto site navigation restructure — landing-page rebuild + navbar consolidation + sidebar hub-spoke nesting (narrow supersession of ADR-053 navigation contract)
date: 2026-05-19
status: Accepted
claim_id: CLAIM-061
claim: >-
  User feedback 2026-05-19 surfaced a discoverability problem on the
  live Quarto site: *"the quatro documents they seem really confusing
  and hard to follow, the whole points was them to be a cleaner
  version. ... it isn't immdiately clear to me where to find the
  results and explanations in clear language about wha they mean."*
  Explore-agent audit confirmed the root cause: although the headline
  results table is on the `index.qmd` landing page (lines 18-32) and
  the 5 interpretation patterns are there (lines 36-50), the navbar's
  9-item top-level fragmentation (Executive summary / Reading guide
  / Results / Methodology (TOC) / Spokes / Notebooks / Evidence /
  Reference / Decisions) buries them — and "Methodology (TOC)" + "Spokes"
  appear as peer items when actually the spokes are CHILDREN of the
  hub. The user perceived a "GitHub-blob-view of WRITEUP.md has more
  than the Quarto site" inversion (Quarto is actually the SUPERSET —
  hub + 8 spokes ~1,449 lines vs WRITEUP.md alone 292 lines), but the
  underlying UX problem is real regardless. v1.1.1 restructures the
  navigation: navbar 9 → 5 items (Results / Methodology dropdown /
  Decisions dropdown / Reference dropdown / Repo); sidebar nests 8
  spokes under WRITEUP.md via Quarto sub-sections; `index.qmd`
  rebuilt to ~30 lines (results + 5-bullet plain-language meaning +
  3 obvious drill-down links) with the displaced reading-guide
  content moved to a new `READING_GUIDE.md` page; hub-spoke
  signposting added (2-paragraph primer at top of WRITEUP.md +
  1-line back-link at top of each of 8 spokes); README "How to read"
  clarified. No methodology content rewritten — pure navigation +
  signposting changes. ADR-053 reading-guide governance dimensions 2
  (3-reading-paths) + 3 (headline-finding-block) + 4 (interpretation
  pedagogy) + 5 (pointer convention) all preserved; only dimension 1
  (navbar/sidebar architecture) is narrowly superseded.
source: transcripts/2026-05-19__v1-1-1-quarto-clarity-restructure.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.1.1 close: live Quarto site landing page shows results +
  plain-language interpretation above the fold (3 obvious links to
  drill deeper). Navbar has 5 top-level items (not 9). Sidebar shows
  "Methodology > Detailed spokes (8 topics) > ..." nesting. Each of
  8 WRITEUP/*.md spoke files has a 1-line back-link to WRITEUP.md at
  the top. WRITEUP.md has a 2-paragraph hub-spoke primer immediately
  after the title. `index.qmd` is ~30 lines (down from 137); the
  displaced reading-guide content lives at the new `READING_GUIDE.md`.
  `quarto render` builds clean. CI green on the v1.1.1 commit. ADR-053
  frontmatter shows `superseded_by: ["061"]` in-place per ADR-029
  convention. SUBMISSION_AUDIT.md regenerates with 61 CLAIM rows.
  Reviewer URLs all 200 (tree/v1.0.0 unchanged per ADR-033;
  releases/v1.1.1 newly resolvable; live Quarto site reflects v1.1.1).
closing_commit: v1.1.1
supersedes: [ADR-053]
superseded_by:
  - "062"  # back-link added per ADR-076 frontmatter-backfill discipline; ADR-062 supersedes navigation restructure with clarity-focused sequel
references:
  - decisions/ADR-030-deliverable-format-quarto-html-site.md
  - decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md
  - decisions/ADR-054-results-page-as-third-entry-artifact-extending-adr-053.md
  - decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md
  - https://quarto.org/docs/websites/website-navigation.html
transcript: transcripts/2026-05-19__v1-1-1-quarto-clarity-restructure.md
---

# ADR-061 — Quarto site navigation restructure (narrow supersession of ADR-053 navigation contract)

## Status

Accepted (2026-05-19; lands in v1.1.1 patch release alongside the
landing-page rebuild + hub-spoke signposting + README clarification).

## Context

[ADR-053](ADR-053-reading-guide-governance-and-newcomer-paths.md)
locked the v1.0.4 reading-guide architecture across 5 dimensions:

1. **Navbar/sidebar architecture** — 3 entry artifacts (EXECUTIVE_SUMMARY
   + index.qmd + RESULTS) + Methodology section with hub + 8 spokes +
   separate Notebooks/Evidence/Reference/Decisions sections.
2. **3-reading-paths** (A1 quick-skim / A2 audit / A3 reproduce).
3. **Headline-finding-block** required on the landing page.
4. **Interpretation pedagogy** (5 patterns required on the landing page).
5. **Pointer convention** (markdown links to deep content; no PDF).

User feedback 2026-05-19 surfaced a real discoverability issue at
dimension 1. The 9-item navbar fragments the entry points; "Methodology
(TOC)" + "Spokes" peer items confuse the hub-spoke relationship;
`index.qmd` is too dense (137 lines covering results + 5 interpretations
+ 3 reading paths + headline ADRs + repo map + submission anchors +
status). The 5-pattern interpretation pedagogy is technically prose-heavy
and not "plain language" by user expectation.

Dimensions 2-5 of ADR-053 are unchanged. Dimension 1 needs revision.

## Decision

Narrow supersession of ADR-053 dimension 1 (navbar/sidebar/landing-page
architecture). All other dimensions of ADR-053 preserved.

### Subsection A — Navbar simplification (9 items → 5)

`_quarto.yml` navbar:left changes:

```yaml
# OLD (9 items): EXECUTIVE_SUMMARY / index.qmd / RESULTS / WRITEUP.md /
# Spokes dropdown / Notebooks dropdown / EVIDENCE.md / Reference dropdown
# / Decisions dropdown.

# NEW (5 items):
navbar:
  left:
    - href: RESULTS.md
      text: Results
    - text: Methodology
      menu:
        - text: "Cover narrative (hub)"
          href: WRITEUP.md
        - text: "Reading guide"
          href: READING_GUIDE.md
        - href: WRITEUP/data-decisions.md
        - href: WRITEUP/model-rungs.md
        - href: WRITEUP/eval-design.md
        - href: WRITEUP/threshold-policy.md
        - href: WRITEUP/reference-scorer-audit.md
        - href: WRITEUP/methodology-guarantees.md
        - href: WRITEUP/limitations-and-future-work.md
        - href: WRITEUP/reproducibility.md
    - text: Decisions
      href: decisions/README.md
    - text: Reference
      menu:
        - EXECUTIVE_SUMMARY.md
        - EVIDENCE.md
        - SPEC_SHEET.md
        - SUBMISSION_AUDIT.md
        - NEXT_STEPS.md
        - assumptions.md
        - notebooks/01_canonical_results.ipynb
        - notebooks/02_frozen_vs_lora.ipynb
        - notebooks/03_calibration.ipynb
        - notebooks/04_ood_slate.ipynb
    - text: Repo
      href: https://github.com/brandon-behring/behring/prompt-injection-detection-prototype
      target: _blank
```

The single Methodology dropdown becomes the obvious entry to the
hub + 8 spokes + the new READING_GUIDE.md page. Notebooks collapse
into Reference (they're auxiliary artifacts, not primary methodology).
EVIDENCE.md moves to Reference (it's an audit-trail artifact, not a
methodology entry point). Repo is a direct GitHub link for users who
want to browse source.

### Subsection B — Sidebar hub-spoke nesting

`_quarto.yml` sidebar.contents Methodology section:

```yaml
# OLD: 9 peer items (WRITEUP.md + 8 spokes at same indent level).
# NEW: 2-level nesting.
- section: "Methodology"
  contents:
    - text: "Cover narrative (hub)"
      href: WRITEUP.md
    - text: "Reading guide"
      href: READING_GUIDE.md
    - section: "Detailed spokes (8 topics)"
      contents:
        - WRITEUP/data-decisions.md
        - WRITEUP/model-rungs.md
        - WRITEUP/eval-design.md
        - WRITEUP/threshold-policy.md
        - WRITEUP/reference-scorer-audit.md
        - WRITEUP/methodology-guarantees.md
        - WRITEUP/limitations-and-future-work.md
        - WRITEUP/reproducibility.md
```

The "Detailed spokes (8 topics)" sub-section is visually indented
under WRITEUP.md. A reader scanning the sidebar sees the hub-spoke
relationship at-a-glance — no longer 9 peer items.

### Subsection C — index.qmd landing page rebuild

`index.qmd` (137 lines → ~30 lines):

1. 1-paragraph thesis.
2. Headline finding table (the §1 AUPRC trio from RESULTS — unchanged content).
3. 5-bullet "What this means in plain language" — 1 sentence per
   interpretation pattern (distilled from the current ADR-053
   dimension-4 5-patterns; the deeper technical version is
   one click away via a "Full interpretation" link).
4. Three obvious drill-down links: "Full results + figures"
   (RESULTS.md), "Full methodology" (WRITEUP.md), "How to read this
   site" (READING_GUIDE.md).

The reading-guide content displaced from `index.qmd` (3 reading
paths + headline ADRs list + repo map + submission anchors + status)
moves to the new `READING_GUIDE.md` page. Per no-orphaned-code
invariant: the content is NOT duplicated — `index.qmd` is rewritten
and `READING_GUIDE.md` is the new home for the moved sections.

### Subsection D — WRITEUP.md hub-spoke primer

Insert 2-paragraph primer at WRITEUP.md immediately after the title
(before the current "Reading guide" table):

> **This is the hub of the methodology — a cover narrative + headline
> results. The detailed methodology lives in 8 spoke pages linked
> below; each spoke is a focused deep-dive on one topic (data design,
> rung ladder, evaluation, thresholds, calibration, reference-scorer
> audit, limitations, reproducibility).**
>
> **Reading on the live Quarto site: drill into each spoke from the
> Methodology dropdown in the navbar or the sidebar. Reading on
> GitHub: click each spoke link in the table below — the GitHub blob
> view of this file alone is the cover narrative; the full methodology
> requires all 8 spokes.**

The primer reframes WRITEUP.md as INTENTIONAL — not as an incomplete
document.

### Subsection E — Spoke→hub back-link (8 files)

Each of `WRITEUP/data-decisions.md`, `model-rungs.md`, `eval-design.md`,
`threshold-policy.md`, `reference-scorer-audit.md`,
`methodology-guarantees.md`, `limitations-and-future-work.md`,
`reproducibility.md` gains a 1-line back-link at the very top
(before any other content):

> *Part of the [WRITEUP methodology](../WRITEUP.md) — see the hub for
> the cover narrative + reading guide.*

Signposts the spoke as a child of the hub for any reader who
deep-links into a spoke (search, external link, sidebar click) without
seeing the hub first.

### Subsection F — README.md "How to read" clarified

README's reading-path section gains explicit Quarto-vs-GitHub guidance:

- **Quick read (5 min)**: live Quarto site → landing page (results +
  plain-language interpretation).
- **Full methodology (60 min)**: live Quarto site → Methodology
  dropdown → cover narrative + 8 spokes.
- **GitHub-only readers**: `WRITEUP.md` is only the cover narrative;
  the 8 `WRITEUP/*.md` spokes carry the detailed methodology — meant
  to be read together. Reading `WRITEUP.md` alone is executive-summary
  depth. Click the spoke links in the table at the top of `WRITEUP.md`
  to drill in.

Removes the user's mental-model inversion (GitHub-blob feels like the
full methodology when it's actually a subset).

## Consequences

- **Discoverability**: landing page now satisfies the user's
  "immediately clear where to find results + plain-language meaning"
  bar. Results above the fold; 5-bullet meaning right below; 3 obvious
  drill-down links.
- **Hub-spoke visual hierarchy**: navbar Methodology dropdown +
  sidebar 2-level nesting + WRITEUP.md primer + spoke back-links
  reinforce the same mental model from 4 angles.
- **ADR-053 narrow supersession**: only navigation dimension changes;
  3-reading-paths (now moved to READING_GUIDE.md but unchanged),
  headline-finding-block (preserved on index.qmd), interpretation
  pedagogy (5 patterns preserved; landing page gets distilled 1-line
  bullets + "Full interpretation" link to the technical version),
  pointer convention (markdown links unchanged) — all preserved.
- **No methodology drift**: zero changes to WRITEUP.md hub or 8 spoke
  contents (text body). Only navigation + signposting.
- **Reviewer URL pin unchanged**: per ADR-033, `tree/v1.0.0` stays;
  live Quarto site reflects the v1.1.1 restructure.
- **CHANGELOG.md `[1.1.1]` documents the change**; SUBMISSION_AUDIT.md
  regenerates with 61 CLAIM rows.

## Linked ADRs

- **Superseded (narrow, navigation dimension only)**: ADR-053 (the
  reading-guide governance ADR; dimensions 2-5 preserved).
- **Referenced**: ADR-030 (Quarto static-site renderer; rendering
  recipe unchanged); ADR-054 (RESULTS as 3rd entry artifact; preserved
  as the default landing-page target); ADR-033 (release strategy;
  v1.1.1 = patch release per the post-submission patch convention).
- **Source**: user feedback 2026-05-19 "the quatro documents they seem
  really confusing and hard to follow" + Explore-agent audit + plan
  file [PLAN_REF redacted; per ADR-068 Class B aspirational-upstream
  path] Phase 2.

## Transcript

Decisions surfaced during the 2026-05-19 v1.1.1 Quarto-clarity
restructure planning session; transcript at
`transcripts/2026-05-19__v1-1-1-quarto-clarity-restructure.md`.
