---
adr_id: "040"
slug: phase-0-audit-findings-and-assumption-backfill
title: Phase 0 final audit findings + 7-assumption backfill (A-010 through A-016)
date: 2026-05-16
status: Accepted
claim_id: CLAIM-040
claim: At Phase 0 close (after the Phase 0-08 submission tag rehearsal cadence locks), the user requested a final meta-review of the 39-ADR interview surface for (1) unstated assumptions, (2) inconsistent methodology, and (3) source-claim faithfulness. Three Explore agents conducted parallel audits — Agent 1 methodology consistency, Agent 2 unstated assumptions, Agent 3 source faithfulness. The audit produced one substantive actionable finding (7 unstated severity-≥-medium assumptions missing from assumptions.md) plus three false-alarm findings explicitly dismissed (ADR-015 acceptance_criterion staleness, Mosbach 2021 citation year, test-stub count of 39 vs claimed 40). ADR-040 documents (a) the audit cycle as a precedent for future periodic audits, (b) the 7-assumption backfill at A-010 through A-016 with severity calibration rationale (5 high — A-010 plus A-012 plus A-013 plus A-014 plus A-016; 2 medium — A-011 plus A-015 — calibrated by load-bearing-with-vs-without-recovery-primitive ladder), (c) the false-alarm dismissal rationales preserved for audit-trail completeness. Severity calibration philosophy locked — "high" reserved for load-bearing assumptions whose failure requires methodology adjustment without an automated recovery path; "medium" reserved for load-bearing assumptions with built-in recovery primitives (cost-reconciliation post-first-run for A-011; reference-rung subset fallback for A-015). The existing A-001 through A-009 conservative "medium"-only convention is preserved (not retro-calibrated — out of scope). Backfill scope — only Phase 0-07 plus Phase 0-08 introduced external-infrastructure assumptions that the parent ADRs (ADR-020 plus ADR-030 plus ADR-032 plus ADR-033 plus ADR-039) did not register at lock time; Phase 0-00 through Phase 0-06 surfaces had complete registration via A-001 through A-009. Dismissal rationales (preserved for completeness) — (1) ADR-015 acceptance_criterion text says 3 trained rungs × 3 seeds × 5 LODO folds equals 45 parquet files reflecting Phase 0-01 state at lock time; post-ADR-016 plus ADR-017 reality is 4 trained rungs × 3 seeds × 4 LODO folds equals 48 files. ADR-015 immutable per CLAUDE.md immutability discipline; ADR-017 acceptance_criterion correctly carries the post-classical-floor count; SPEC_SHEET §3.2 already reflects 48-file post-ADR-017 reality. NO action — text was correct at lock time. (2) Mosbach 2021 citation in ADR-019 — arXiv:2006.04884 submitted June 2020 plus revised March 2021 plus accepted at ICLR 2021. "Mosbach 2021" matches ICLR conference publication year per standard academic-citation convention. NO action — citation defensible. (3) Test-stub count claimed mismatch (40 vs 39 ADRs) — exact ^@pytest.mark.skip grep returns 39 stubs; 39 = 32 ADR-specific plus 7 kit-level pre-Phase-0 invariants. Earlier 41 count caught docstring substring matches. NO action — counts correct.
source: User request 2026-05-16 (Phase 0 final audit before submission); 3-agent parallel audit findings; plan at /home/brandon_behring/.claude/plans/twinkly-weaving-puppy.md
acceptance_criterion: decisions/ADR-040-*.md exists with adr_id quoted as 040 status Accepted; assumptions.md contains 7 new rows A-010 through A-016 each with severity field of either high or medium per ADR-040 calibration lock (high — A-010 plus A-012 plus A-013 plus A-014 plus A-016; medium — A-011 plus A-015); each new assumption row Linked-to column references ADR-040 plus the parent ADR(s) that introduced the assumption (e.g., A-010 references ADR-030 plus ADR-033 plus ADR-039; A-013 references ADR-016 plus ADR-032 plus ADR-034); assumptions.md trailing TBD note (line 31) extended with Phase 0-07 plus Phase 0-08 closing observation noting why these 7 were back-filled at the audit (parent ADRs did not register at lock time; surfaced by Phase 0 final audit per ADR-040); SPEC_SHEET §8 Linked ADRs trailer extends from ADR-039 to include ADR-040; tests/test_invariants.py contains skip-marked stub test_phase_0_audit_findings_documented asserting (1) ADR-040 file exists at decisions/ADR-040-*.md; (2) assumptions.md contains rows for each of A-010 through A-016 (regex grep for the literal ID strings at start-of-row); (3) each new row's severity field reads high or medium per the calibration lock (5 high plus 2 medium); (4) each new row's Linked-to column references ADR-040; SUBMISSION_AUDIT.md regenerates with 40 claims total (38 Accepted plus 2 Superseded — CLAIM-002 plus CLAIM-004). Dismissal rationales documented in this ADR body do NOT require additional invariant tests — ADR-015 staleness verified by reading ADR-017 acceptance_criterion plus SPEC_SHEET §3.2; Mosbach 2021 verified by ICLR 2021 publication-year convention; test-stub count verified by grep ^@pytest.mark.skip on tests/test_invariants.py.
closing_commit:
references:
  - https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
  - assumptions.md
  - decisions/ADR-005-project-level-methodology-principles.md
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md
  - decisions/ADR-030-deliverable-format-quarto-html-site.md
  - decisions/ADR-032-hf-hub-publication-headline-rungs-only.md
  - decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md
  - decisions/ADR-039-acceptance-criteria-six-gate-integration-checklist.md
transcript: transcripts/2026-05-16__phase-0-audit__missing-assumptions-backfill.md
---

# ADR-040: Phase 0 final audit findings + 7-assumption backfill

## Status

Accepted (2026-05-16). Final ADR of the Phase 0 interview surface — produced by a meta-audit triggered after Phase 0-08 close. Companion to ADR-001 through ADR-039 (the 39 decision-locking ADRs that this audit verified).

## Context

After Phase 0-08 closed (ADR-035 through ADR-039 plus 2 cross-section ratifications; commits `5427b95` + `104c76b`), the user requested a final meta-review of the Phase 0 interview surface before Phase 1 begins. The audit charter:

1. **Unstated assumptions**: identify decisions that depend on assumptions not properly surfaced in `assumptions.md`.
2. **Inconsistent methodology**: identify cross-ADR contradictions, terminological drift, supersession-trail gaps.
3. **Source-claim faithfulness**: verify that cited URLs / papers / library primitives actually support the claims made.

Three Explore agents conducted parallel audits. Findings were synthesized into a plan at `/home/brandon_behring/.claude/plans/twinkly-weaving-puppy.md`. The user reviewed and refined the plan via an `/exploring-options` cycle (Q1: formal ADR vs registry-only; Q2: severity calibration; Q3: invariant test stub scope). All three Q1-Q3 decisions are recorded below.

This ADR formalizes (a) the audit cycle as a precedent for future periodic audits, (b) the 7-assumption backfill, (c) the dismissal rationales for the three false-alarm findings.

## Decision

### Q1 lock — Formal ADR + registry backfill

ADR-040 documents the audit cycle as a formal artifact rather than only-via-commit-message + transcript. Rationale:
- Creates an auditable record of the audit cycle for future reviewers.
- Preserves the dismissal rationales (false alarms) as part of the auditable trail.
- Sets a precedent for periodic audit ADRs (e.g., post-Phase-1 audit could be ADR-NNN with the same structure).
- Rejected option A (registry-only) and option C (`docs/audit-log.md` hybrid).

### Q2 lock — Strict severity calibration (5 HIGH + 2 MEDIUM)

The 7 new assumptions are calibrated by load-bearing-with-vs-without-recovery-primitive ladder:

| ID | Severity | Rationale |
|---|---|---|
| A-010 | **high** | GH Pages outage requires manual local-build alternative; load-bearing on ADR-039 gate 6 |
| A-011 | medium | H100 spot drift handled by ADR-020 cost-reconciliation recipe post-first-run |
| A-012 | **high** | GPU exhaustion requires ADR-001 fallback-ladder activation (rung-count reduction) |
| A-013 | **high** | HF Hub outage collapses T0 reproducibility tier per ADR-034; requires local-cache fallback |
| A-014 | **high** | LLM judge deprecation invalidates 2 of 4 reference rungs per ADR-018; requires superseding ADR |
| A-015 | medium | ProtectAI repo loss leaves 2 of 4 reference rungs (LLM judges remain); TF-IDF+LR anchor unaffected |
| A-016 | **high** | Brandon work-time has NO automated recovery primitive; if false, submission misses |

Existing A-001 through A-009 conservative "medium"-only convention preserved (not retro-calibrated — out of scope).

The existing severity ladder per `assumptions.md` lines 7-10 (low / medium / high / critical) is reused; the audit explicitly rejects bumping any assumption to `critical` (none of the 7 change the project's framing — the highest-load-bearing case A-016 still preserves methodology contribution, just misses the deadline).

### Q3 lock — One invariant test stub (`test_phase_0_audit_findings_documented`)

`tests/test_invariants.py` gains one stub matching the existing one-stub-per-ADR pattern. The stub verifies the audit-output state mechanically — ADR-040 exists, assumptions.md has A-010..A-016, severity calibration matches the lock — but does NOT verify the truth of each assumption (assumptions are unverified by design; truth-verification happens via existing gates: ADR-039 gate 6 for A-010; Phase 2 RunPod preflight for A-012; Phase 5 WRITEUP-caveats for the rest).

Per-HIGH-assumption stubs were rejected because (a) most would duplicate ADR-039 gate 6, (b) others require billing real cloud/API calls to assert truth, (c) A-016 (Brandon work-time) is inherently un-testable in CI.

### Dismissal rationales (preserved for audit-trail)

Three audit findings were dismissed as NOT actionable. The dismissal rationales are recorded here so a future reviewer doesn't re-litigate them.

**Dismissal 1 — ADR-015 acceptance_criterion staleness**

Finding (Agent 1): ADR-015 acceptance_criterion text says "three trained rungs × three seeds × five LODO folds = 45 per-row prediction parquet files" but post-ADR-016 + ADR-017 reality is 4 trained rungs (TF-IDF + LR classical floor added per ADR-017) × 3 seeds × 4 LODO folds (per ADR-016) = 48 files.

Verdict: NOT actionable.

Rationale:
- ADR-015's text was correct at lock time (Phase 0-01 / Phase 0-02 state).
- CLAUDE.md immutability discipline: *"Change a previously-locked decision → write a new ADR that marks the prior as status: superseded-by-NNN. Do not edit the prior ADR file."*
- ADR-017 acceptance_criterion correctly carries the post-classical-floor count (48 files); SPEC_SHEET §3.2 (Phase 0-03+ instantiation layer) reflects the 48-file post-ADR-017 reality.
- The audit-trail chain (ADR-015 → ADR-017 → SPEC_SHEET §3.2) is intact; ADR-015's text is point-in-time-correct rather than stale.

**Dismissal 2 — Mosbach 2021 citation year**

Finding (Agent 3): Mosbach et al. paper (arXiv:2006.04884) was submitted June 2020; the ADR-019 citation as "Mosbach 2021" appears year-mismatched.

Verdict: NOT actionable.

Rationale:
- Paper accepted at **ICLR 2021** (conference proceedings).
- Standard academic-citation convention uses the conference/journal publication year, not the arXiv preprint submission year.
- "Mosbach 2021" matches ICLR 2021 publication-year convention; the citation is defensible.
- Agent 3 conflated arXiv preprint year with publication year — finding is editorial-level concern that the existing citation already satisfies.

**Dismissal 3 — Test-stub count (40 vs 39 ADRs)**

Finding (Agent 1): `grep -c "pytest.mark.skip"` returned 41 hits suggesting test-stub count drift; meanwhile 39 ADRs exist; reported as MAJOR mismatch.

Verdict: NOT actionable — false alarm.

Rationale:
- Exact `^@pytest.mark.skip` (start-of-line anchor) returns 39 stubs.
- 39 = 32 ADR-specific invariants + 7 kit-level (pre-Phase-0) invariants from SPEC_GREENFIELD §5 (`test_class_balance_per_fold`, `test_source_disjoint_train_test`, `test_hyperparameter_immutability`, `test_calibration_honesty_val_only`, `test_reporting_completeness_assumptions_in_caveats`, `test_no_emoji_in_repo`, `test_config_result_classes_frozen_slotted`).
- Earlier 41 count caught docstring substring matches mentioning "skip" inside test docstrings.
- ADR count (39 + this ADR-040 = 40) and stub count (39 ADR-aligned + 1 new for ADR-040 = 40) end up balanced after this remediation lands.
- Mechanical verification — `grep -c "^@pytest.mark.skip" tests/test_invariants.py` returns expected count.

## Consequences

### Positive

- **Audit-trail completeness** — the audit cycle is documented as a formal ADR; future reviewers see the full audit context plus the dismissal rationales without needing to re-run the audit.
- **Assumption registry honesty** — the 7 new entries surface real infrastructure-dependency assumptions that were silently in scope; the WRITEUP caveats block (per Phase 5 `test_reporting_completeness_assumptions_in_caveats`) will surface them to reviewers.
- **Severity calibration discipline** — the 5-HIGH-plus-2-MEDIUM split honestly differentiates load-bearing assumptions with automated recovery from those requiring methodology adjustment; the WRITEUP-caveats prioritization benefits.
- **Precedent for periodic audits** — Phase 1+ audits can use this ADR's structure (3-agent parallel audit + Q1-Q3 plan refinement + formal-ADR-plus-registry-backfill) without re-inventing the cycle.
- **No ADR retro-mutations** — the immutability discipline is preserved; ADR-015 staleness is recognized but not "fixed" since it was correct at lock time.

### Negative / cost

- **ADR count moves to 40** — slight inflation; one more ADR for reviewers to read; mitigated by the audit-trail-completeness benefit.
- **Calibration rationale text is dense** — Q2 severity ladder requires careful reading to follow; mitigated by the table in ADR-040 body.
- **Future audit ADRs add up** — periodic audit precedent could lead to ADR-NNN proliferation if not used judiciously; mitigated by reserving formal audit ADRs for genuine audit cycles (not routine reviews).

### Neutral

- **WRITEUP caveats block** — Phase 5 work item per `test_reporting_completeness_assumptions_in_caveats`; this ADR adds 7 entries to the surface but doesn't itself populate the caveats.
- **Existing A-001 through A-009 conservative severity** — preserved; retro-calibration is out of scope.
- **No new ADRs for false-alarm findings** — dismissed cleanly without spawning corrective ADRs that would inflate count unnecessarily.

### Limitation

The audit is point-in-time (2026-05-16); a future surprise (e.g., Phase 1 reveals a non-trivial methodology gap) requires a fresh audit cycle. ADR-040 is not a perpetual gate.

### Extension condition for revisit

- **Phase 1+ audit**: when a periodic audit is conducted (post-Phase-1 close, post-Phase-3 close, etc.), the same 3-agent + plan-refinement + formal-ADR pattern applies; future audit ADRs follow ADR-040's structure with their own ADR ID.
- **Reviewer-feedback-driven audit**: if a reviewer surfaces a methodology gap post-submission, fresh audit ADR with the gap-resolution rationale and (if applicable) assumption-registry updates.
- **Periodic A-XXX expansion**: if Phase 1+ surfaces additional unstated assumptions, append to `assumptions.md` without superseding ADR-040 (the calibration discipline is locked; specific entries are extensible).

## Alternatives Considered

- **Option A (registry-only; no ADR)** — minimum blast radius; preserves the A-001..A-009 pattern of "register alongside parent ADR, no audit ADR". Rejected at Q1 walk in favor of B because formal audit-trail artefact provides reviewer-readable narrative without git-log archaeology.
- **Option C (`docs/audit-log.md` hybrid)** — registry plus new audit-log doc-type. Rejected at Q1 walk because audit-log file would need its own format convention + sidebar nav entry; ADR-040 absorbs the narrative without introducing a new doc-type.
- **Option A on Q2 (conservative `medium`-only)** — match existing A-001..A-009 convention. Rejected at Q2 walk in favor of B because flat severity hides real load-bearing distinctions; HIGH vs MEDIUM differentiation helps WRITEUP-caveats prioritization.
- **Option B on Q3 (per-HIGH-assumption stubs)** — 6 stubs total. Rejected at Q3 walk because most stubs would either duplicate existing gates (A-010 vs ADR-039 gate 6) or require billing real cloud/API calls; the resulting stubs would be permanently skip-marked + provide no real verification.

## References

- Michael Nygard ADR pattern — https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- `assumptions.md` (the registry this audit backfills)
- ADR-005 (project-level methodology principles — the framing this audit verifies)
- ADR-020 (compute infrastructure — source of A-011 + A-012)
- ADR-030 (Quarto deliverable format — source of A-010)
- ADR-032 (HF Hub publication — source of A-013 + A-015)
- ADR-033 (release strategy — source of A-010 + A-016 timing dependency)
- ADR-039 (6-gate acceptance criteria — gate 6 covers A-010 truth-verification)
- Plan file `/home/brandon_behring/.claude/plans/twinkly-weaving-puppy.md` (the audit synthesis + Q1-Q3 refinement record)

## Transcript

See `transcripts/2026-05-16__phase-0-audit__missing-assumptions-backfill.md` for the conversation that led to this decision (3-agent parallel audit + Q1-Q3 walk + plan refinement).
