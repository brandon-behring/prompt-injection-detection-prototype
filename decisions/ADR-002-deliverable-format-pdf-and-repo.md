---
adr_id: 002
slug: deliverable-format-pdf-and-repo
title: Deliverable format — focused PDF plus public GitHub repo as evidence locker
date: 2026-05-15
status: Superseded
superseded_by: "030"
claim_id: CLAIM-002
claim: The submission deliverable is a focused PDF (rendered from WRITEUP.md + appendices) paired with a public GitHub repo containing ADRs, code, notebooks, training manifests, per-row predictions, and topic-focused markdown spokes for any reader who wants depth beyond the PDF.
source: SPEC_GREENFIELD.md §Brief row 305 (Deliverable format)
acceptance_criterion: At submission time, both artifacts exist and are mutually consistent — PDF cross-links to the repo at a stable git tag; repo contents reproduce the headline numbers in the PDF.
closing_commit: 2a7b123
references:
  - https://pandoc.org/MANUAL.html#creating-a-pdf
  - SUBMISSION_TEMPLATE.md
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-002: Deliverable format — focused PDF plus public GitHub repo as evidence locker

## Status

Superseded by ADR-030 (2026-05-16). Originally Accepted (2026-05-15).

**Supersession context**: Phase 0-07 Q1 walk surfaced a user pivot away from PDF — "I think a pdf is not needed. The repo, can provide the write as a html documentation to hyperlink between the products. But it should have a clear guide/TOC to help someone examine the repo." ADR-030 replaces the PDF + repo dual-artifact decision with a repo-only deliverable rendered as a Quarto HTML site via GitHub Actions. See `decisions/ADR-030-deliverable-format-quarto-html-site.md` for the superseding decision.

## Context

The brief is silent on deliverable format; the project must choose. The five candidate formats are PDF-only, repo-only, both, tarball, and hosted-demo. The Tight calendar (ADR-001) rules out hosted-demo on cost. Repo-only inflates reader time and lowers presentation polish. PDF-only severs reproducibility from the narrative.

The hybrid "PDF + repo link" pattern is the lowest-friction option for a dual-audience reviewer (A1 hiring manager + A2 ML researcher; see ADR-004). The PDF carries the 15-minute skim path; the repo carries the deep-audit path. The two artifacts stay in sync because the PDF is mechanically rendered from the repo's WRITEUP.md via pandoc.

## Decision

**Deliverable composition**: PDF + public GitHub repository.

**PDF role**: focused hub document (≈ 10-15 pages). Rendered from `WRITEUP.md` + selected appendices via pandoc. Cross-links to repo markdown spokes via stable GitHub URLs pinned to the submission git tag.

**Repo role**: evidence locker. Contains code, ADRs, training manifests, per-row predictions, notebooks (jupytext-paired per ADR-004 hub-and-spoke + future Q9 lock), and topic-focused markdown spokes (`WRITEUP/<topic>.md`) that the PDF references for depth.

**Submission delivery**: PDF emailed to reviewer + repo URL with stable tag. Tag-at-submission strategy is finalized in Phase 0-07 §Submission.

## Consequences

**Positive:**

- A1 (hiring manager) reads only the PDF; bounded reading time honored. A2 (ML researcher) skims the PDF, follows spoke links for the 2-3 decisions they want to scrutinize.
- Mechanical PDF-from-repo build keeps the two artifacts in sync — no separate maintenance burden.
- Public repo gives portfolio benefit and "show your work" optics. Aligns with kit's `[LOCKED]` default for visibility (ADR-003).

**Negative / cost:**

- Two artifacts to polish under Tight calendar; PDF build pipeline must be tested before submission day.
- Stable-tag discipline required — broken links from PDF to repo undermine the whole structure.

**Neutral:**

- Phase 0-07 decides exact PDF bundle composition (which appendices concat into the PDF) and exact spoke file list. This ADR fixes the *structure*, not the *contents*.

## Alternatives Considered

- **PDF only**: Reviewer reads top-to-bottom; reproducibility lives in a footnote. *Rejected because* it severs methodology from evidence; A2 reviewer cannot audit without leaving the artifact.
- **Repo only (no PDF)**: Maximum transparency. *Rejected because* reading time inflates; A1 reviewer is starved of a narrative entry point.
- **Tarball**: Self-contained bundle. *Rejected because* ADRs and transcripts are harder to navigate without unpacking; no inline rendering on GitHub.
- **Hosted demo + above**: Interactive Gradio/HF Space demo. *Rejected because* Tight calendar (ADR-001) cannot absorb 4+ hours of demo build.

## References

- Pandoc PDF docs — https://pandoc.org/MANUAL.html#creating-a-pdf
- `SUBMISSION_TEMPLATE.md` — kit-provided scaffold
- ADR-003 (repo visibility)
- ADR-004 (reviewer profile + hub-and-spoke structure)
