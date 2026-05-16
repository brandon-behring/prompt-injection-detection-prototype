---
adr_id: "038"
slug: phase-tailoring-light-roadmap-edits
title: Phase tailoring — light ROADMAP edits to Phase 4 close + Phase 5 description (preserves 5-phase structure)
date: 2026-05-16
status: Accepted
claim_id: CLAIM-038
claim: Phase 0-08 locks SPEC_GREENFIELD ledger row 313 (Phase tailoring) at light tailoring of docs/ROADMAP.md Phase 4 close plus Phase 5 description while preserving the kit-level 5-phase structure (Phase 1 Data plus Phase 2 Training plus Phase 3 Evaluation plus Phase 4 Analysis plus Phase 5 Writeup). Phase 0-07 expanded the Phase 5 surface (Quarto site per ADR-030 plus 8 spokes per ADR-031 plus HF Hub model card publication per ADR-032 plus rehearsal-tag-fires-publish-pipeline per ADR-033 plus T0+T1+T3 tier-ladder spoke per ADR-034) without altering the phase structure; SPEC_SHEET §2 Phase 5 gate checklist was updated at Phase 0-07 close to reflect these additions but docs/ROADMAP.md was left at kit-level pre-tailoring text. ADR-038 closes the drift by tailoring ROADMAP.md to match. Two surface-area edits — (1) Phase 4 close gains a 2-line note that before exiting Phase 4 the v0.9.0-rc1 rehearsal tag fires per ADR-033 triggering the full publish pipeline (Quarto site build per ADR-030 plus GH Pages deploy plus HF Hub model card pushes per ADR-032) as a 24-plus hour dress-rehearsal with fix-forward via new commits plus v0.9.0-rc2 if rehearsal fails; (2) Phase 5 description rewritten to replace deliverable bundle assembled with Quarto site published to GH Pages via the .github/workflows/publish.yml workflow per ADR-030 plus 8 spokes populated plus index.qmd reading-paths guide complete plus HF Hub model repos for headline rungs published per ADR-032 plus WRITEUP/reproducibility.md documents T0+T1+T3 tier ladder per ADR-034 plus Phase 5 close fires v1.0.0 submission tag per ADR-033 with GH release CHANGELOG plus _site.tar.gz asset. Phases 1-3 description text preserved unchanged — Phase 0-07 additions don't touch Phases 1-3. The decision-needed prompt at ROADMAP line 83 (project-specific tailoring of the phase structure — e.g., add a Phase 2b for a smoke-train preflight; collapse Phase 3+4 if analysis is light) is answered with no structural restructure — 5-phase frame preserved; the rehearsal is a tag (not a phase) per ADR-033; Phase 4 plus Phase 5 are the right granularity; Phase 2b smoke-train preflight is unnecessary since make smoke per ADR-027 already covers laptop-only fixture-data preflight without a phase split; Phase 3+4 collapse is rejected since Phase 4 carries first-class statistical-inference work (paired-bootstrap plus cv_clt_ci plus MDE plus reference-scorer audit per ADR-022 plus ADR-024) that deserves the same phase-gate discipline as Phase 3 metric computation. Limitation — tailoring forks ROADMAP from the kit-level template; anyone running a future project from the same kit must not copy this project's ROADMAP back into the kit. Extension condition — Phase 1+ surprise that warrants ROADMAP-level tailoring (e.g., a major training-pipeline pivot that re-orders Phase 2 plus Phase 3 gates) updates ROADMAP via superseding ADR-038 with the new tailoring; reviewer feedback signals splitting Phase 5 into 5a writeup plus 5b publication plus 5c submission gets restructured via superseding ADR — currently below the friction threshold.
source: SPEC_GREENFIELD.md Roadmap ledger row 313 + docs/ROADMAP.md line 83 decision-needed prompt + Phase 0-08 walk Q6
acceptance_criterion: SPEC_GREENFIELD ledger row 313 carries locked-to-light-roadmap-edits-phase4-plus-phase5 status (see ADR-038); docs/ROADMAP.md Phase 4 close section gains a paragraph naming the v0.9.0-rc1 rehearsal tag plus the full publish pipeline cite (Quarto site build per ADR-030 plus GH Pages deploy plus HF Hub model card pushes per ADR-032); docs/ROADMAP.md Phase 5 description is rewritten to replace the kit-default deliverable bundle assembled line with the Phase 0-07 additions (Quarto site published plus 8 spokes plus index.qmd plus HF Hub publish plus reproducibility spoke plus v1.0.0 submission tag); docs/ROADMAP.md Phases 1-3 text preserved unchanged (verified via diff); the decision-needed prompt at line 83 is replaced with a brief note pointing at ADR-038 (no structural restructure; rehearsal is a tag not a phase); tests/test_invariants.py contains skip-marked stub test_roadmap_phase4_phase5_tailored asserting (1) docs/ROADMAP.md Phase 4 section contains the v0.9.0-rc1 rehearsal tag name; (2) docs/ROADMAP.md Phase 5 section contains all four ADR citations (ADR-030 plus ADR-031 plus ADR-032 plus ADR-033 plus ADR-034); (3) docs/ROADMAP.md still declares exactly 5 phases past Phase 0 (no Phase 4.5 or 5a/5b splits); SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit: 5427b95
references:
  - docs/ROADMAP.md
  - decisions/ADR-030-deliverable-format-quarto-html-site.md
  - decisions/ADR-031-reviewer-reading-paths-quarto-site-entry.md
  - decisions/ADR-032-hf-hub-publication-headline-rungs-only.md
  - decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md
  - decisions/ADR-034-reproducibility-tier-full-ladder.md
  - SPEC_SHEET.md
transcript: transcripts/2026-05-16__phase-0-08__process-tech-stack-acceptance.md
---

# ADR-038: Phase tailoring — light ROADMAP edits to Phase 4 close + Phase 5 description

## Status

Accepted (2026-05-16). Closes SPEC_GREENFIELD ledger row 313 (Phase tailoring) + answers the `[Decision needed (Phase 0)]` prompt at `docs/ROADMAP.md` line 83. Companion to ADR-030/031/032/033/034 (the Phase 0-07 additions that drive the tailoring).

## Context

`docs/ROADMAP.md` defines five phases past Phase 0:
- Phase 1 — Data
- Phase 2 — Training
- Phase 3 — Evaluation
- Phase 4 — Analysis
- Phase 5 — Writeup

Each phase has process gates (work-completed and tests-passing, *not* metric thresholds) + a replanning checkpoint before exiting.

Phase 0-07 work expanded the Phase 5 surface (per ADR-030/031/032/033/034) without altering the phase structure:
- ADR-030: Phase 5 publishes Quarto site to GH Pages (was: "PDF bundled" — superseded; "deliverable bundle assembled" remained in ROADMAP).
- ADR-031: Phase 5 populates 8 WRITEUP spokes + `index.qmd` reading-path guide.
- ADR-032: Phase 5 publishes HF Hub model card repos.
- ADR-033: Phase 4 close fires `v0.9.0-rc1` rehearsal tag; Phase 5 close fires `v1.0.0` submission tag.
- ADR-034: Phase 5 documents T0+T1+T3 tier ladder in `WRITEUP/reproducibility.md` + ships `make eval-from-hub`.

**`SPEC_SHEET.md` §2 Phase 5 gate checklist was already updated at Phase 0-07 close** to reflect these additions (per Q1 work). So `docs/ROADMAP.md` and `SPEC_SHEET.md` drifted — ROADMAP at kit-level pre-tailoring; SPEC_SHEET at project-specific post-tailoring.

Three options were considered (per Phase 0-08 Q6 walk):

(A) Accept ROADMAP as-is — kit-level high abstraction; SPEC_SHEET carries detail.
(B) Light tailoring of Phase 4 + Phase 5 — reference Phase 0-07 additions inline.
(C) Restructure phases (Phase 4.5 / Phase 5a-b-c split).

User selection at Q6 walk: **B**.

## Decision

### Surface-area edits to `docs/ROADMAP.md`

**Edit 1 — Phase 4 close gains a 2-line note**:

> **Replanning checkpoint**: before exiting Phase 4, audit analysis assumptions; commit any superseding ADRs.
>
> **Pre-Phase-5 rehearsal**: before exiting Phase 4, fire the `v0.9.0-rc1` rehearsal tag per ADR-033 — this triggers the full publish pipeline (Quarto site build per ADR-030 + GH Pages deploy + HF Hub model card pushes per ADR-032) as a 24+ hour dress-rehearsal. If rehearsal fails, fix-forward via new commits + `v0.9.0-rc2`.

**Edit 2 — Phase 5 description rewritten**:

> ## Phase 5 — Writeup
>
> All `WRITEUP.md` sections + 8 spokes (per ADR-031) drafted and populated; `index.qmd` reading-paths guide complete; all ADRs written and indexed; transcripts linked from the writeup appendix; EVIDENCE.md populated for every external-evidence claim; Quarto site renders cleanly via `make site` and via the `.github/workflows/publish.yml` GH Actions workflow per ADR-030; HF Hub model repos for headline rungs published per ADR-032 via `scripts/generate_model_cards.py`; `WRITEUP/reproducibility.md` documents T0+T1+T3 tier ladder per ADR-034.
>
> **Phase 5 close fires `v1.0.0` submission tag per ADR-033** (CHANGELOG entry committed; `gh release create v1.0.0` with `_site.tar.gz` asset; all markers resolved).
>
> **Replanning checkpoint**: before submission, run the full leak-audit grep + verification grep suite. Fix-forward any leakage.
>
> Gate: every checkbox in SPEC_SHEET §2 Phase 5 ticked; reviewer URLs (source pin at `tree/v1.0.0` + live Quarto site + GH release page) all resolve; transcripts ready for private email attachment.

**Edit 3 — Decision-needed prompt at line 83 replaced**:

> *(Phase 0-08 lock per ADR-038: 5-phase structure preserved; no Phase 4.5 / Phase 5a-b-c split; the rehearsal is a tag per ADR-033 not a phase; Phase 2b smoke-train preflight is unnecessary since `make smoke` per ADR-027 already covers laptop-only fixture-data preflight without a phase split; Phase 3+4 collapse is rejected since Phase 4 carries first-class statistical-inference work — paired-bootstrap + cv_clt_ci + MDE + reference-scorer audit per ADR-022 + ADR-024 — that deserves the same phase-gate discipline as Phase 3 metric computation.)*

**Phases 1-3 description text preserved unchanged** — Phase 0-07 additions don't touch Phases 1-3.

### What's NOT changed

- **5-phase structure** preserved.
- **Replanning-checkpoint discipline** preserved (per kit-level framing).
- **Process-gates-not-outcome-gates framing** preserved (per ADR-005 + kit-default).
- **Phase 1 / Phase 2 / Phase 3 descriptions** preserved.

## Consequences

### Positive

- **ROADMAP + SPEC_SHEET in sync** — reviewer reading either doc gets the same picture of Phase 4 close + Phase 5 expectations.
- **Minimum-blast-radius tailoring** — only Phase 4 + Phase 5 entries change; surface-area is small.
- **5-phase structure preserved** — no Phase 4.5; no Phase 5a/5b split; reviewer familiar with the kit recognizes the structure immediately.
- **ADR references inline** — ROADMAP becomes audit-trail entry-point with direct citations to ADR-030/031/032/033/034.
- **Decision-needed prompt resolved** — the `[Decision needed (Phase 0)]` at ROADMAP line 83 is closed by this ADR with explicit no-structural-restructure rationale.

### Negative / cost

- **Forks ROADMAP from kit-level template** — anyone running a future project from the same kit must not copy this project's ROADMAP back into the kit. Mitigation: tailoring is contained to Phase 4 + Phase 5 entries citing this project's ADRs (won't apply to other projects anyway).
- **Two-doc sync discipline** — future ROADMAP edits must also update SPEC_SHEET §2 if Phase gates change. Mitigation: the SPEC_SHEET-as-binding-gate-checklist + ROADMAP-as-narrative split is clear; reviewer audits via either.

### Neutral

- **Phase numbering unchanged** — Phase 1-5 retain their numbers.
- **`WRITEUP/` directory** referenced in ROADMAP edits — already created at Phase 0-07 close.
- **Phase tailoring is a one-time lock at Phase 0-08** — Phase 1+ phase changes (e.g., a major training-pipeline pivot) supersede ADR-038.

### Limitation

ROADMAP and SPEC_SHEET sync must be maintained — if a future Phase 1+ surprise drives a Phase-gate edit, both docs need updating. Mitigation: any Phase-gate edit lives in a superseding ADR (e.g., ADR-040 if Phase 2 ordering changes) — the ADR is the trigger that fans out edits to both docs.

### Extension condition for revisit

- **Phase 1+ pivot** that re-orders Phase 2 + Phase 3 gates (e.g., a training-pipeline failure forces a different rung ordering) — supersedes ADR-038 with the new tailoring; updates ROADMAP + SPEC_SHEET together.
- **Reviewer feedback** signaling Phase 5 split (5a writeup + 5b publication + 5c submission) would be clearer — supersedes ADR-038 with the split structure. Currently below the friction threshold for that change.
- **Kit-level ROADMAP template update** at some future date — at that point, decide whether to fork-and-merge or stay tailored.

## Alternatives Considered

- **(A) Accept ROADMAP as-is** — ROADMAP stays high-level kit doc; SPEC_SHEET carries project-specific detail. Rejected per Q6 walk because ROADMAP would carry stale "PDF bundled" text contradicting ADR-030; reviewer reading ROADMAP alone would get a stale picture.
- **(C) Restructure phases (Phase 4.5 / Phase 5a-b-c)** — over-formalizes; rehearsal is a tag per ADR-033 not a phase; 5-phase structure is well-understood. Rejected per Q6 walk.
- **Add a Phase 2b smoke-train preflight** (suggested in the ROADMAP line 83 decision-needed prompt) — `make smoke` per ADR-027 already covers laptop-only fixture-data preflight without a phase split. Rejected.
- **Collapse Phase 3+4** (suggested in the ROADMAP line 83 decision-needed prompt) — Phase 4 carries first-class statistical-inference work that deserves its own phase-gate discipline. Rejected.

## References

- `docs/ROADMAP.md` (the kit-level doc this ADR tailors)
- `SPEC_SHEET.md` §2 Phase 5 gate checklist (updated at Phase 0-07 close; this ADR brings ROADMAP in sync)
- ADR-030 (Quarto + GH Actions publish — Phase 5 deliverable)
- ADR-031 (reviewer reading paths — 8 spokes + `index.qmd` — Phase 5 deliverable)
- ADR-032 (HF Hub publication — Phase 5 deliverable)
- ADR-033 (release strategy — `v0.9.0-rc1` rehearsal at Phase 4 close + `v1.0.0` submission at Phase 5 close)
- ADR-034 (reproducibility tier — `WRITEUP/reproducibility.md` Phase 5 deliverable)

## Transcript

See `transcripts/2026-05-16__phase-0-08__process-tech-stack-acceptance.md` for the conversation that led to this decision (Q6 walk + option B selection).
