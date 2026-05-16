---
adr_id: 004
slug: reviewer-profile-and-hub-and-spoke-writeup
title: Reviewer profile A1+A2 with hub-and-spoke writeup structure
date: 2026-05-15
status: Superseded
superseded_by: "031"
claim_id: CLAIM-004
claim: The submission is read by a dual audience — hiring manager (A1) and ML researcher (A2) — with no single reading-time bound. The PDF is the focused hub (≈ 10-15 pages, layered for both audiences); per-topic markdown spokes under WRITEUP/ carry depth that the PDF cross-links to.
source: SPEC_GREENFIELD.md §Brief row 307 (Reviewer profile + expected reading time)
acceptance_criterion: PDF has layered structure (exec summary + headlines for A1; methodology narrative + ADR-indexed appendix for A2); every section that could bloat emits a single inline link to a repo spoke; spokes are standalone-readable.
closing_commit: 2a7b123
references:
  - WRITEUP.md (this repo)
  - SUBMISSION_TEMPLATE.md
  - https://pandoc.org/MANUAL.html
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-004: Reviewer profile A1+A2 with hub-and-spoke writeup structure

## Status

Superseded by ADR-031 (2026-05-16) for the hub-artefact framing. Originally Accepted (2026-05-15).

**Supersession scope**: the A1+A2 dual-audience profile + B4 open-ended-layered reading-time stance + hub-and-spoke structure all survive. What changes: the *hub artefact* shifts from PDF (~10-15 pages) to the Quarto-rendered HTML site introduced by ADR-030, specifically the `index.qmd` entry-point file + Quarto sidebar nav declared in `_quarto.yml`. The spoke list is also finalized at 8 spokes (the 7 provisional spokes from ADR-004 + a new `WRITEUP/reproducibility.md` required by ADR-034 to document the T0+T1+T3 tier ladder). See `decisions/ADR-031-reviewer-reading-paths-quarto-site-entry.md` for the superseding decision.

## Context

The brief signals that the submission is read by *both* a hiring manager and an ML researcher, with no single reading-time bound. This is a dual-audience profile (A1 + A2), not a homogeneous mixed panel (A3). The two audiences need different things: A1 wants exec-readable headlines in ≈ 15 minutes; A2 wants methodology-readable depth in ≈ 45-60 minutes with audit paths into code and ADRs.

A monolithic 10-15-page PDF cannot serve both well. A repo-only artifact starves A1. The decision is *how to structure the writeup so each reader gets what they need without the artifact bloating*.

The hub-and-spoke pattern is the answer: a focused PDF (the hub) cross-links to topic-focused markdown writeups in the repo (the spokes). The PDF stays under bound; spokes carry depth. This is the standard pattern for technical documentation with mixed-depth readers; it pairs naturally with ADR-002 (PDF + repo deliverable).

## Decision

**Reviewer profile**: A1 + A2 (dual: hiring manager + ML researcher), not "mixed panel".

**Reading-time stance**: B4 (open-ended, layered). PDF cover-to-cover ≈ 15 min for the A1 path; full PDF + spokes ≈ 1-2 hours for the A2 path; deep code/ADR audit unbounded.

**Writeup structure — hub-and-spoke**:

1. **PDF (hub)**, ≈ 10-15 pages:
   - Exec summary + headline metrics table (A1 entry point; 15-min skim).
   - Methodology narrative — *what was chosen, why, what was deferred* (A2 entry point; 45-60 min read).
   - ADR-indexed appendix (stub summaries of each load-bearing decision).
   - Every section that could bloat emits a single inline link to its spoke instead.

2. **Repo spokes (depth)** under `WRITEUP/`, one file per load-bearing topic. Plausible (finalized Phase 0-07):
   - `WRITEUP/data-decisions.md` — source slate, dedup, splits, leakage scan
   - `WRITEUP/eval-design.md` — OOD slate, calibration battery, paired-bootstrap protocol
   - `WRITEUP/reference-scorer-audit.md` — LLM-judge + kappa findings
   - `WRITEUP/model-rungs.md` — frozen vs LoRA vs full-FT, matched-budget controls
   - `WRITEUP/threshold-policy.md` — three-pinpoint Recall@FPR + deployment scenarios
   - `WRITEUP/methodology-guarantees.md` — banned-approaches surfaced as guarantees
   - `WRITEUP/limitations-and-future-work.md` — structured limitations + extension conditions

3. **Cross-linking discipline**: PDF cites spokes via stable GitHub URLs at the submission tag. Tag-at-submission is finalized in Phase 0-07.

## Consequences

**Positive:**

- A1 reads the PDF cover-to-cover and never clicks a link; reading-time bound honored.
- A2 skims the PDF, identifies 2-3 decisions worth scrutinizing, follows spokes for depth.
- ADRs remain immutable; spokes remain evolving narrative — different artifacts, different lifecycles, no confusion.
- Scales naturally — adding a new methodology component adds a new spoke without bloating the PDF.

**Negative / cost:**

- Tag-at-submission discipline required (or PDF links break post-submission).
- More writeup surface area to keep coherent. Mitigation: spokes are standalone-readable and each closes with a "Limitations + when to extend" subsection per ADR-005.

**Neutral:**

- Spoke file list is provisional; Phase 0-07 §Submission PDF bundle composition row decides the exact list.

## Alternatives Considered

- **Monolithic PDF**: Single document, no spokes. *Rejected because* dual-audience profile cannot be served by one bound — depth for A2 bloats past A1's reading budget.
- **Mixed-panel (A3) framing with single depth target**: Treat audience as homogeneous. *Rejected because* the brief signals two distinct reader types; serving the average serves neither well.
- **Spokes-only (no PDF)**: Pure markdown. *Rejected because* A1 needs a narrative entry point; PDF is the canonical artifact for non-developer reviewers (per ADR-002).

## References

- `WRITEUP.md` (this repo) — kit-provided scaffold structured for mixed-audience
- Pandoc PDF docs — https://pandoc.org/MANUAL.html
- ADR-002 (PDF + repo deliverable; this ADR defines the *structure* within that deliverable)
- ADR-005 (project-level methodology principles; spokes implement the principles)
