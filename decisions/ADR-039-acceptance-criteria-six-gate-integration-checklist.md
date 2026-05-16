---
adr_id: "039"
slug: acceptance-criteria-six-gate-integration-checklist
title: Project-specific acceptance criteria — 6-gate integration checklist for v1.0.0 submission tag
date: 2026-05-16
status: Accepted
claim_id: CLAIM-039
claim: Phase 0-08 locks SPEC_GREENFIELD ledger row 351 (Project-specific acceptance criteria) at a 6-gate integration checklist that aggregates across the per-ADR acceptance_criterion fields plus the kit-level §6 verification gates plus the SPEC_SHEET §2 Phase 5 gate checklist. The 6 gates — (1) zero [OPEN] in SPEC_SHEET (every slot reads [LOCKED — value (per ADR-NNN)] or [TBD-at-Phase-N] with explicit rationale); (2) zero open rows in SPEC_GREENFIELD ledger appendix (every row reads locked-to-X (see ADR-NNN) or superseded-by-NNN or deferred-to-phase-N with explicit rationale); (3) all 39-plus tests/test_invariants.py stubs unskipped plus green at submission tag (every @pytest.mark.skip decorator removed; pytest -m unit exits clean); (4) SUBMISSION_AUDIT.md regenerates cleanly with every claim in Accepted or Superseded state (no Proposed claims at submission tag — verified by make audit which wraps scripts/regenerate_audit.py --check); (5) v0.9.0-rc1 rehearsal tag fired successfully before v1.0.0 submission tag per ADR-033 (verified by git tag -l v0.9.0-rc1 showing the tag exists plus the corresponding GH Actions workflow run shows green status); (6) all three reviewer URLs at v1.0.0 resolve — source pin at GitHub tree v1.0.0 plus live Quarto site at GitHub Pages URL plus GH release page with CHANGELOG plus _site.tar.gz asset (per ADR-033). Per-ADR acceptance_criterion fields collectively cover the granular gates (data manifests plus calibration artefacts plus threshold reachability plus HF Hub model card schema plus etc.) — those stay in the ADRs as source of truth; ADR-039 references them rather than restating. Kit-default §6 gates preserved — make test passes (incl. invariants); make lint clean; evals/results.json schema-validated against eval-toolkit results.v1.json schema; all severity-≥-medium assumptions in assumptions.md appear in WRITEUP caveats block. The submission-readiness sign-off lives at SPEC_SHEET §7 (existing kit-default section) plus expanded to include the 6 integration gates plus a per-ADR-criteria reference plus a per-Phase-5-gate reference. Limitation — integration-level gates assume per-ADR acceptance_criterion fields are well-formed; an ADR with vague acceptance criteria can pass aggregation while leaving real gaps; mitigation is the reviewer-protocol at ADR lock time (each new ADR's acceptance criterion is reviewed for verifiability — already standard practice across the 39 ADRs). Extension condition — Phase 1+ surprise reveals an integration-level gate missing from the 6 (e.g., verify the cost ledger CSV passes schema validation) adds a 7th-or-8th gate via Phase 1+ ADR amendment without superseding ADR-039 (the framing is locked; the specific gates are extensible); methodology revision (post-submission v2.0.0) materially changes the gate set supersedes ADR-039 with a new gates ADR.
source: SPEC_GREENFIELD.md §6 Verify ledger row 351 + Phase 0-08 walk Q7 + SPEC_GREENFIELD §6 line 252 decision-needed prompt
acceptance_criterion: SPEC_GREENFIELD ledger row 351 carries locked-to-six-gate-integration-checklist status (see ADR-039); SPEC_SHEET §7 Verification and acceptance criteria gains the 6-gate integration checklist with the per-ADR-criteria pointer plus the kit-default §6 gates preserved; SUBMISSION_TEMPLATE.md or a SUBMISSION.md sign-off section quotes the 6 gates so the submission-readiness check is reviewer-readable at submission tag; tests/test_invariants.py contains skip-marked stub test_submission_readiness_gates_satisfied asserting at v1.0.0 submission tag (1) grep -c open SPEC_GREENFIELD.md decision-ledger appendix section returns 0; (2) grep -c [OPEN] SPEC_SHEET.md returns 0 excluding the Status [OPEN] document-level header which transitions to [LOCKED] at Phase 0 close; (3) pytest --collect-only tests/test_invariants.py shows zero skip-marked tests; (4) make audit exits 0; (5) git tag -l v0.9.0-rc1 returns the tag name (rehearsal fired); (6) the three reviewer URLs return HTTP 200 (or 301 redirect to a 200) — checkable via curl --head; SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit:
references:
  - SPEC_SHEET.md
  - SPEC_GREENFIELD.md
  - decisions/README.md
  - decisions/ADR-005-project-level-methodology-principles.md
  - decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md
transcript: transcripts/2026-05-16__phase-0-08__process-tech-stack-acceptance.md
---

# ADR-039: Project-specific acceptance criteria — 6-gate integration checklist for `v1.0.0` submission tag

## Status

Accepted (2026-05-16). Closes SPEC_GREENFIELD ledger row 351 (Project-specific acceptance criteria) + the `[Decision needed]` prompt at SPEC_GREENFIELD §6 line 252. Companion to ADR-033 (release strategy — `v0.9.0-rc1` rehearsal + `v1.0.0` submission cadence that this checklist gates).

## Context

`SPEC_GREENFIELD.md` §6 line 252 prompts: *"Decision needed: project-specific acceptance criteria (e.g., required reproducibility tier, runtime targets, CI gates)."*

The kit-default acceptance criteria already on the table (per `SPEC_SHEET.md` §7):

- All WRITEUP sections drafted with `[TBD]` markers resolved.
- All ADRs written + indexed.
- Transcripts linked.
- EVIDENCE.md populated for external-evidence claims.
- ~~PDF bundled~~ (superseded by ADR-030 — Quarto site published).
- `make test` passes (including all `tests/test_invariants.py` stubs unskipped + green).
- `make lint` clean.
- `evals/results.json` schema-validated against `eval-toolkit`'s `results.v1.json` schema.
- All severity-≥-medium assumptions in `assumptions.md` appear in WRITEUP caveats block.

The **operational acceptance criteria** are largely already encoded as the 39+ skip-marked invariant tests in `tests/test_invariants.py` (29 from prior Phase 0 work + 5 from Phase 0-07 + 5 from Phase 0-08 invariant stubs). Each ADR's `acceptance_criterion:` frontmatter field names the specific gates that ADR is responsible for; `SUBMISSION_AUDIT.md` auto-generates from these via `scripts/regenerate_audit.py`.

Row 351 asks: what **additional** project-specific submission-readiness criteria to layer on top — the integration-level gates that aggregate over the per-ADR criteria.

Three options were considered (per Phase 0-08 Q7 walk):

(A) Layer 8-10 explicit project-specific submission gates.
(B) Cite per-ADR criteria as collectively sufficient — minimal additional spec.
(C) Hybrid — small set of 5-7 integration-level gates + cite per-ADR criteria for detail.

User selection at Q7 walk: **C**.

## Decision

### 6-gate integration checklist for `v1.0.0` submission tag

| # | Gate | Verification | Source |
|---|---|---|---|
| 1 | Zero `[OPEN]` in `SPEC_SHEET.md` | every slot reads `[LOCKED: ... (per ADR-NNN)]` OR `[TBD-at-Phase-N]` with explicit rationale | `grep -c "\[OPEN\]" SPEC_SHEET.md` returns 0 (excluding the doc-header `Status: [OPEN]` line which transitions to `[LOCKED]` at Phase 0 close) |
| 2 | Zero `open` rows in `SPEC_GREENFIELD.md` ledger appendix | every row reads `locked-to-X (see ADR-NNN)` OR `superseded-by-NNN` OR `deferred-to-phase-N` with explicit rationale | `awk '/^\| open \|/' SPEC_GREENFIELD.md` returns 0 lines |
| 3 | All `tests/test_invariants.py` stubs unskipped + green | every `@pytest.mark.skip` decorator removed; `pytest -m unit` exits clean | `pytest -m unit tests/test_invariants.py` exits 0; `pytest --collect-only` shows zero skipped tests |
| 4 | `SUBMISSION_AUDIT.md` regenerates cleanly | every claim in `Accepted` OR `Superseded` state (no `Proposed` at submission tag) | `make audit` (wraps `scripts/regenerate_audit.py --check`) exits 0 |
| 5 | `v0.9.0-rc1` rehearsal tag fired successfully before `v1.0.0` | rehearsal tag exists + corresponding GH Actions workflow run shows green status | `git tag -l v0.9.0-rc1*` returns at least one tag; `gh run list --workflow publish.yml` shows green status for that tag |
| 6 | All three reviewer URLs at `v1.0.0` resolve | source pin at `tree/v1.0.0` + live Quarto site at GH Pages URL + GH release page with CHANGELOG + `_site.tar.gz` asset (per ADR-033) | `curl --head` returns HTTP 200 (or 301-redirect-to-200) for all three URLs |

### Per-ADR `acceptance_criterion` fields collectively cover the granular gates

Each ADR's `acceptance_criterion:` frontmatter field names the specific verification gate for that ADR's decision. The 6 integration gates aggregate over these per-ADR fields without restating them. `SUBMISSION_AUDIT.md` regeneration (gate 4) is the single mechanical check that all per-ADR criteria are satisfied.

This avoids:
- **Duplicating granular gates** in this ADR (would drift from the per-ADR sources of truth).
- **Hiding integration-level gates** in scattered per-ADR criteria (some gates aggregate across multiple ADRs — gate 5 spans ADR-030 + ADR-032 + ADR-033; gate 6 spans ADR-030 + ADR-033).

### Kit-default §6 gates preserved

The kit-default acceptance criteria (per `SPEC_SHEET.md` §7) carry forward unchanged:

- `make test` passes (incl. invariants).
- `make lint` clean.
- `evals/results.json` schema-validated against `eval-toolkit`'s `results.v1.json` schema.
- All severity-≥-medium assumptions in `assumptions.md` appear in WRITEUP caveats block.

These gates are subsumed by gates 3 + 4 in the integration checklist but listed explicitly in `SPEC_SHEET.md` §7 for kit-level continuity.

### Submission-readiness sign-off location

The 6-gate checklist lives at `SPEC_SHEET.md` §7 (existing kit-default section, expanded with the integration gates + per-ADR-criteria pointer + per-Phase-5-gate reference). The `SUBMISSION_TEMPLATE.md` (or `SUBMISSION.md` cover-letter) quotes the 6 gates so the submission-readiness check is reviewer-readable at submission tag.

## Consequences

### Positive

- **Single sign-off checklist** for `v1.0.0` submission tag — explicit + verifiable + auditable.
- **Aligns with ADR-033 cadence** — gate 5 (rehearsal-tag-fired) explicitly bridges Phase 4 close → Phase 5 close transition.
- **Avoids duplication** — per-ADR `acceptance_criterion` fields stay source-of-truth for granular gates; integration ADR aggregates without restating.
- **Auditable via mechanical checks** — every gate has a verifiable command (grep / awk / pytest / make audit / git tag / curl).
- **Compatible with kit-default §6** — kit gates preserved + augmented; reviewer familiar with the kit recognizes the structure.

### Negative / cost

- **Integration-level gates assume per-ADR `acceptance_criterion` fields are well-formed** — an ADR with vague acceptance criteria can pass aggregation while leaving real gaps. Mitigation: each new ADR's acceptance criterion is reviewed at lock time for verifiability (already standard practice across the 39 ADRs).
- **The "all invariant tests unskipped + green" gate is a single-bit gate** — doesn't capture coverage or test-quality nuance. Mitigation: ADR-028's 70% coverage floor + upstream-issue-filing discipline covers this from a different angle.
- **6 gates is the right number, not 5 or 7** — judgment call; mitigation: gate-add/remove via Phase 1+ ADR amendment if Phase 1+ surfaces a missing or redundant gate.

### Neutral

- **Per-ADR criteria stay the source of truth** for granular gates.
- **Kit-default §6 gates remain in scope** — gate 3 + gate 4 subsume them mechanically but listing them explicitly in SPEC_SHEET §7 preserves kit-level continuity.

### Limitation

The 6 gates cover *submission-readiness for the canonical methodology submission*. They do NOT cover:

- **Post-submission reviewer-feedback responsiveness** — patches under `v1.0.x` per ADR-033 are not gated by this checklist; they're individual fix-forward commits.
- **Production-grade deployment** — out-of-scope per ADR-005 + ADR-027 prototype-grade framing; production scope extension requires a superseding ADR-039 with additional deployment-readiness gates.
- **Test coverage nuance** — gate 3 verifies invariants run green; gate 4 verifies audit cleanliness; neither captures the 70% coverage floor per ADR-028 (that's a separate `make coverage` gate, kit-default).

### Extension condition for revisit

- **Phase 1+ reveals a missing integration gate** (e.g., "verify the cost ledger CSV passes schema validation"; "verify the per-row predictions parquet files all parse via the locked schema") — add a 7th/8th gate via Phase 1+ ADR amendment without superseding ADR-039 (the framing is locked; specific gates are extensible).
- **Methodology revision (post-submission `v2.0.0` per ADR-033 major-bump)** materially changes the gate set — supersedes ADR-039 with a new gates ADR.
- **Production-grade deployment scope extension** triggers superseding ADR with additional deployment-readiness gates (uptime + monitoring + rollback + canary release).

## Alternatives Considered

- **(A) Layer 8-10 explicit project-specific submission gates** — more text to maintain; partial redundancy with SPEC_SHEET §2 Phase 5 gates; rejected in favor of C (6 gates with per-ADR pointer for detail).
- **(B) Cite per-ADR criteria as collectively sufficient** — minimal additional spec but hides integration-level gates that don't sit naturally in any one ADR (e.g., gate 5 spans multiple ADRs). Rejected per Q7 walk.

## References

- `SPEC_SHEET.md` §7 (existing kit-default acceptance criteria; this ADR expands)
- `SPEC_GREENFIELD.md` §6 (kit-level acceptance criteria framing + the `[Decision needed]` prompt at line 252)
- `decisions/README.md` (ADRs are source of truth; each ADR's `acceptance_criterion` frontmatter field)
- ADR-005 (project-level methodology principles — informs the prototype-grade scope framing)
- ADR-033 (release strategy — `v0.9.0-rc1` rehearsal + `v1.0.0` submission cadence that this checklist gates)

## Transcript

See `transcripts/2026-05-16__phase-0-08__process-tech-stack-acceptance.md` for the conversation that led to this decision (Q7 walk + option C selection).
