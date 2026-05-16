---
adr_id: "030"
slug: deliverable-format-quarto-html-site
title: Deliverable format — repo-only with Quarto-rendered HTML site via GitHub Actions (supersedes ADR-002)
date: 2026-05-16
status: Accepted
claim_id: CLAIM-030
claim: Phase 0-07 supersedes ADR-002 (PDF + repo dual-artifact). The deliverable is a public GitHub repository only — no PDF. The repo's writeup surface is rendered as a static HTML site by Quarto from the existing .md files (WRITEUP.md hub plus WRITEUP/ spokes plus decisions/ ADRs plus a new index.qmd entry-point). The site auto-publishes to GitHub Pages on push to main and on tag push via a .github/workflows/publish.yml workflow using quarto-actions/setup@v2 plus quarto-actions/publish@v2. Output target is HTML only — no PDF auxiliary — to keep the build surface minimal and honor the user's pivot away from PDF. Quarto rendering preserves the hub-and-spoke structure locked by ADR-004 (now superseded by ADR-031) while replacing the PDF hub artefact with the Quarto site's index.qmd plus sidebar navigation. Source format stays .md — Quarto natively renders .md files — so no migration to .qmd is required. Reviewer email at submission carries three URLs — repo tree at submission tag for source pin; live GH Pages site for rendered reading; GH release page for CHANGELOG and asset bundle — plus transcripts as private email attachment per existing convention. The PDF-build pipeline scoped for Phase 5 in ADR-002 is removed; pandoc plus LaTeX dependencies drop out of pyproject.toml plus Makefile. Limitation — Quarto binary dependency adds a build-tool install to the contributor surface; first-time GitHub Pages plus GH Actions setup carries deadline risk that the v0.9.0-rc1 rehearsal tag from ADR-033 explicitly mitigates. Extension condition — if a reviewer requests a PDF post-submission, Quarto can produce one from the same source via format augment in frontmatter; addition requires superseding ADR per the SDD discipline.
source: SPEC_GREENFIELD.md §Submission ledger row 347 + ADR-002 supersession trigger + Phase 0-07 walk Q1
acceptance_criterion: ADR-002 frontmatter status changes from Accepted to Superseded with superseded_by 030; SPEC_GREENFIELD ledger row 300 (Deliverable format) carries a supersession note pointing at ADR-030; SPEC_GREENFIELD ledger row 347 (PDF bundle composition) status changes from open to locked-to-quarto-html-via-gh-actions (see ADR-030, ADR-031); _quarto.yml exists at repo root declaring project type website with output-dir _site and a navbar plus sidebar referencing WRITEUP.md plus the spoke list plus decisions/; .github/workflows/publish.yml exists declaring on push branches main plus tags v* triggers with quarto-actions/setup@v2 plus quarto-actions/publish@v2 target gh-pages and permissions block (contents write plus pages write plus id-token write); GH Pages enablement is configured (Settings then Pages then Source then gh-pages branch); tests/test_invariants.py contains skip-marked stub test_quarto_site_config_present asserting _quarto.yml exists and parses as valid YAML and declares project type website and that .github/workflows/publish.yml exists and references the two quarto-actions steps; SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit:
supersedes: "002"
references:
  - https://quarto.org/docs/websites/
  - https://quarto.org/docs/publishing/github-pages.html
  - https://github.com/quarto-dev/quarto-actions
  - decisions/ADR-002-deliverable-format-pdf-and-repo.md
  - decisions/ADR-001-brief-alignment-tight-calendar-with-fallback-ladder.md
  - decisions/ADR-027-smoke-vs-canonical-execution-context-stratification.md
transcript: transcripts/2026-05-16__phase-0-07__submission-deliverables.md
---

# ADR-030: Deliverable format — repo-only with Quarto-rendered HTML site via GitHub Actions

## Status

Accepted (2026-05-16). **Supersedes ADR-002** (PDF + repo dual-artifact). Closes the first of 4 [OPEN] rows in Phase 0-07 (§Submission — rows 347-350 of SPEC_GREENFIELD ledger). Companion to ADR-031 (reviewer reading paths), ADR-032 (HF Hub publication), ADR-033 (GitHub release strategy), and ADR-034 (reproducibility tier).

## Context

ADR-002 (2026-05-15) locked the deliverable as PDF + public GitHub repo dual-artifact. The PDF was to be rendered from `WRITEUP.md` + selected appendices via pandoc; the repo carried evidence-locker depth.

During Phase 0-07 walk Q1 (2026-05-16), the user pivoted:

> "I think a pdf is not needed. The repo, can provide the write as a html documentation to hyperlink between the products. But it should have a clear guide/TOC to help someone examine the repo."

The pivot is allowed under the brief — ADR-002's own context noted *"The brief is silent on deliverable format; the project must choose"*. The user further clarified they had Quarto specifically in mind for the HTML renderer, conditional on GitHub Actions hosting being available.

The PDF + repo decision in ADR-002 carried two costs the pivot removes:
- Pandoc + LaTeX (`tinytex` or system LaTeX) build pipeline as a Phase 5 work item — non-trivial under ADR-001 tight calendar.
- Stable-tag PDF→repo cross-link discipline — PDF permalinks need to survive post-submission edits.

Quarto + GH Pages instead provides:
- Native sidebar nav + full-text search + cross-references (`@sec-eval-design`, `@adr-027`) — richer affordance than PDF.
- Single-binary build via `quarto-actions/setup@v2` — no LaTeX surface.
- Auto-publish on push + tag via `quarto-actions/publish@v2` — versioned reviewer URL with `_site/` as build artefact.
- All `.md` files render natively — zero migration cost from existing `WRITEUP.md` + `WRITEUP/*.md` + `decisions/ADR-*.md`.

The hub-and-spoke pattern locked by ADR-004 (now superseded by ADR-031) survives — the hub artefact shifts from PDF to the Quarto site's `index.qmd` entry-point + sidebar navigation; spokes remain as `WRITEUP/*.md` files reachable from the sidebar.

## Decision

**Deliverable composition**: public GitHub repository **only**. No PDF.

**Rendering**: Quarto static-site renderer. `_quarto.yml` at repo root declares the site configuration. Output target is **HTML only** (`format: html`); no PDF auxiliary.

**Source format**: existing `.md` files unchanged. Quarto natively renders `.md` files — no migration to `.qmd` (except `index.qmd` as the new entry-point file).

**Hosting**: GitHub Pages via `.github/workflows/publish.yml` workflow using `quarto-actions/setup@v2` + `quarto-actions/publish@v2` with `target: gh-pages`. Triggers on push to `main` (continuous deploy) and on tag push `v*` (per ADR-033 release tags also trigger publish for the canonical-submission build).

**Reviewer submission URL plan** (3 URLs + private attachment):
1. Source pin — `https://github.com/brandon-behring/prompt-injection-detection-submission/tree/v1.0.0` (canonical submission anchor; never drifts; per ADR-033).
2. Live rendered site — `https://brandon-behring.github.io/prompt-injection-detection-submission/` (reflects latest publish; reviewer reads here).
3. GH release page — `https://github.com/brandon-behring/prompt-injection-detection-submission/releases/tag/v1.0.0` (carries CHANGELOG.md + `_site.tar.gz` asset for offline readers; per ADR-033).
4. Transcripts as private email attachment per existing convention (gitignored, not committed).

**Removed scope**: PDF build pipeline. `pandoc` and any LaTeX dependencies drop out of `pyproject.toml` and `Makefile`. `make pdf` target (if previously planned) is removed; `make site` target (Quarto render) is added per ADR-027's Makefile pattern.

## Consequences

### Positive

- **Zero pandoc/LaTeX surface** — removes a Phase 5 build-pipeline work item that carried real risk under ADR-001 tight calendar (LaTeX issues on submission day are a classic foot-gun).
- **Richer reader affordance** — sidebar nav + full-text search + cross-references that a PDF cannot provide; A2 reviewer can audit specific topics without paging.
- **All artefacts in one browsing surface** — ADRs, transcripts (committed ones), code, configs, writeup spokes all render in the same Quarto site or render natively on GitHub — one click apart.
- **Native `.md` rendering** — zero migration cost; `WRITEUP.md` + spokes + ADRs render as-is.
- **Reviewer URL is a rendered HTML site, not a markdown-source view** — eliminates the "view rendered or view source?" confusion GitHub markdown has.
- **Honors the user's explicit pivot** without back-fitting PDF compromises.

### Negative / cost

- **Quarto binary dependency** added to the contributor surface — anyone building the site locally needs Quarto installed (`brew install quarto` or platform equivalent; ~200MB). GH Actions handles this via `quarto-actions/setup@v2` so CI is unaffected.
- **First-time GH Pages + GH Actions setup carries deadline risk** — permissions misconfigs, first-tag-push failures are common foot-guns. ADR-033 explicitly mitigates via the `v0.9.0-rc1` rehearsal tag that fires the publish pipeline before submission day.
- **Offline reading is degraded vs PDF** — reviewer reading on a flight needs either `_site.tar.gz` (per ADR-033 release asset) or `git clone + quarto preview` locally. Acceptable trade — most reviewers read online.
- **`_site/` build artefact policy** — `_site/` must be `.gitignore`'d (GH Pages serves from `gh-pages` branch; not from `main`). Committing `_site/` to `main` would pollute git history with rendered HTML.

### Neutral

- **Quarto version pinning** deferred to Phase 0-08 (library version pinning sub-session). `_quarto.yml` itself doesn't pin Quarto version; the GH Actions `quarto-actions/setup@v2` step pins via the action's input.
- **Phase 5 work item shifts** — was "build PDF via pandoc + render WRITEUP.md"; is now "stand up Quarto site + verify GH Pages publish + finalize sidebar nav". Similar order-of-magnitude effort; lower failure surface (Quarto is more predictable than pandoc + LaTeX).
- **PDF as future auxiliary remains possible** — Quarto can produce `format: [html, pdf]` from the same source. Addition requires a superseding ADR (per SDD discipline); not scoped here.

### Limitation

The Quarto site is rendered HTML. If a reviewer needs paper-form reading or a sealed-PDF audit trail (e.g., for a regulator), the auxiliary-PDF extension is the right answer — but it adds back the LaTeX surface this ADR was explicitly removing. Trade is acceptable for the current reviewer profile (A1 hiring manager + A2 ML researcher per ADR-031).

### Extension condition for revisit

- **Reviewer-requested PDF**: if a reviewer asks for a PDF version post-submission, add `format: [html, pdf]` via superseding ADR; Quarto produces both from the same source. The supersession should also re-enable `tinytex` install in CI.
- **Production-grade deployment scope extension**: if the writeup expands to include a deployment-grade artefact, the Quarto site + a deployment-grade companion (Docker container, hosted demo) become joint deliverables via superseding ADR.
- **GH Pages publish failure on submission day**: if `quarto publish` fails after `v0.9.0-rc1` rehearsal succeeded, fallback is to commit `_site/` to a `submission-site` branch and point reviewer URL at a raw HTML-Preview URL — fix-forward, not abandon-the-format.

## Alternatives Considered

- **PDF + repo (the original ADR-002)** — superseded by the user's explicit pivot; build-surface cost was disproportionate to the affordance.
- **GitHub-native markdown rendering (no Quarto)** — zero build pipeline; works today via GitHub's native `.md` renderer; user explicitly preferred Quarto's sidebar + search + cross-refs polish over GitHub-native's bare-minimum rendering.
- **MkDocs Material + GH Pages** — similar to Quarto in affordance; user picked Quarto specifically (academic tooling familiarity; cross-ref support).
- **Docusaurus / GitBook / Read-the-Docs** — heavier doc-site platforms; overkill for a ~10-15 page methodology writeup; user did not request them.
- **Local Quarto render + manual `quarto publish gh-pages`** — no CI; same reviewer URL as the chosen option; user explicitly required GitHub Actions hosting (rules this out).
- **HTML + PDF dual-output via Quarto** — adds back the LaTeX surface this ADR removes; user explicitly stated "PDF not needed"; deferred to superseding-ADR extension condition.

## References

- Quarto websites quickstart — https://quarto.org/docs/websites/
- Quarto GitHub Pages publishing — https://quarto.org/docs/publishing/github-pages.html
- `quarto-actions` GitHub Actions — https://github.com/quarto-dev/quarto-actions
- ADR-002 (deliverable format PDF + repo — superseded by this ADR)
- ADR-001 (tight calendar — informs the deadline-risk mitigation via ADR-033 rehearsal tag)
- ADR-027 (Makefile execution-context stratification — `make site` joins the target taxonomy)

## Transcript

See `transcripts/2026-05-16__phase-0-07__submission-deliverables.md` for the conversation that led to this decision (Q1 walk + user Quarto + GH Actions pivot).
