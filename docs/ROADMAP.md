# Roadmap

This file is the Roadmap portion of the project Constitution (alongside `MISSION.md` and `TECH_STACK.md`). The phases below are `[LOCKED]` as discipline (each phase has a checklist of work-completed and tests-passing — never metric thresholds, so the eval reports what was found rather than what was needed to advance). Phase structure may be tailored to project specifics; the recommendation below works for a typical instantiation.

## Phase 0 — Spec lock-in interview `[LOCKED]`

Runs as topic-focused sub-sessions, each driven by the `/exploring-options` skill against `SPEC_GREENFIELD.md`'s decision ledger.

> **For each `[OPEN]` decision walked, the interview must surface:**
>
> 1. Concrete explanation of what the decision means.
> 2. Options with pros/cons.
> 3. **2-3 definitive reference URLs** (peer-reviewed paper, library docs, methodology guide).
> 4. Recommendation with rationale.
>
> Primary reference source: `docs/research/` dossier (MANIFEST.json's `claim_family` field maps decisions to supporting research). Supplement with web search for additional authoritative references — note: the dossier covers methodology decisions (~30 of 50 ledger rows); non-methodology rows (brief alignment, library version pinning, submission deliverables, repo hygiene) rely on web search.
>
> **Fresh-investigation rule:** at runtime, read `docs/research/` files live; do not pre-load assumed candidates from training memory or prior knowledge.

After each sub-session, invoke `/save-transcript phase-0-NN__<topic>` (skill at `.claude/skills/save-transcript/`) to checkpoint locally. Transcripts are private by default (gitignored); emailed to the reviewer separately at submission time.

Each locked decision becomes one ADR at `decisions/ADR-NNN-<slug>.md` (ADRs are the source of truth; the appendix ledger row and SPEC_SHEET slot reference the ADR-NNN as authoritative). ADRs are immutable; supersede via new ADR marking prior `status: superseded-by-NNN`.

### Kit-level supersession path

If Phase 0-00 brief alignment (or any subsequent sub-session) surfaces a constraint that contradicts a kit-level `[LOCKED]` decision documented in spec text (MISSION / TECH_STACK / ROADMAP / SPEC_GREENFIELD), write a new ADR that names the specific spec section/rule and supersedes it. Kit-level decisions are the default; the brief is authoritative when it contradicts.

### Recommended sub-session sequence (~9 sub-sessions covering ~50 ledger rows)

1. **Phase 0-00 — Brief alignment** (§Brief, 5 rows): user pastes brief (or key excerpts) into the conversation; `/save-transcript` captures it. Surface scope / deliverable / deadline / visibility / reviewer-profile / brief-mandated-metric constraints. Produces ADR-001.
2. **Phase 0-01 — Threat model** (§0, 3 rows): attack classes, language, length cap.
3. **Phase 0-02 — Data design** (§1, 6 rows): source slate, HF pinning, dedup, splits, ref-scorer audit.
4. **Phase 0-03 — Model scope** (§2, 9 rows): backbone, training-time scope, frozen-probe role, matched-budget controls, reference scorer selection, LoRA hyperparams, compute.
5. **Phase 0-04 — Eval framework** (§3, 7 rows): OOD slate, bootstrap N, multi-comparison correction, recall@FPR pinpoints, calibration battery, multi-seed protocol, paired-test method.
6. **Phase 0-05 — Threshold + cost-weight** (§4, 1 row).
7. **Phase 0-06 — Code + test discipline** (§5 + §STYLE, 4 rows): module layout, smoke-vs-canonical, coverage floor, test markers.
8. **Phase 0-07 — Submission deliverables** (§Submission, 4 rows): PDF bundle, HF Hub checkpoints, GitHub release strategy, reproducibility tier.
9. **Phase 0-08 — Process + acceptance + library pinning + GPU/secrets** (§6 + §Tech-Stack, ~11 rows).

### Phase 0 close criterion

Closes when:

1. Every `[OPEN]` row in the ledger is `locked-to-X` and references an ADR.
2. SPEC_SHEET has zero `[OPEN]` slots.
3. `assumptions.md` carries every severity-≥-medium assumption surfaced during the interview.
4. `tests/test_invariants.py` has skip-marked stubs for every invariant in SPEC_GREENFIELD §5.

Phase 1 cannot start until all four hold.

**Replanning checkpoint**: before exiting this phase, audit whether any `[LOCKED]` assumption has been invalidated. If yes: write a superseding ADR, update the SPEC_SHEET slot, cascade to WRITEUP §<relevant>, commit `chore: phase-0 replan`.

## Phase 1 — Data

Sources defined and licensed; audit complete; semantic dedup applied and calibrated against labelled holdouts; cross-source benign dedup applied; leakage scan run; splits locked and persisted.

**Replanning checkpoint**: before exiting Phase 1, audit data assumptions; if any locked decision broke (e.g., a source license changed), file a superseding ADR before moving to Phase 2.

## Phase 2 — Training

Per-rung config persisted in a versioned config file; all rungs trained successfully; training manifests captured; **per-row predictions persisted** alongside metrics.

**Replanning checkpoint**: before exiting Phase 2, audit hyperparameter assumptions; commit any superseding ADRs.

## Phase 3 — Evaluation

All rung × slice metrics computed; OOD slate evaluated; calibration battery run; thresholds selected on validation only; results schema-validated.

**Replanning checkpoint**: before exiting Phase 3, audit eval-design assumptions; commit any superseding ADRs.

## Phase 4 — Analysis

Bootstrap CIs computed for every headline metric; paired-bootstrap differences computed for every rung-vs-rung comparison of interest; MDE estimated for every reported CI; per-source breakdowns; reference-scorer audit completed.

**Replanning checkpoint**: before exiting Phase 4, audit analysis assumptions; commit any superseding ADRs.

## Phase 5 — Writeup

All sections drafted; all ADRs written and indexed; transcripts linked from the writeup appendix; EVIDENCE.md populated; deliverable bundle assembled; all markers resolved.

**Replanning checkpoint**: before submission, run the full leak-audit grep + verification grep suite. Fix-forward any leakage. Tag `v1.0.0` after all checks pass.

> **Decision needed (Phase 0):** project-specific tailoring of the phase structure (e.g., add a Phase 2b for a smoke-train preflight; collapse Phase 3+4 if analysis is light).
