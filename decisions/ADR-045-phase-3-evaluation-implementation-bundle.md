---
adr_id: "045"
slug: phase-3-evaluation-implementation-bundle
title: Phase 3 evaluation implementation bundle — scoring-first contract + 6-commit cadence + tiered reference scorers + classical-scaffold + full-pairwise persistence with headline-only WRITEUP + pydantic schema validation
date: 2026-05-16
status: Accepted
claim_id: CLAIM-045
claim: Phase 3 entry bundles seven implementation choices closing implementation gaps in ADR-018/021/022/023/024/025/026/034 left open after Phase 0 lock and Phase 2 close. Q1 — pre-Phase-3 housekeeping is already satisfied (assumptions A-010 through A-016 backfilled in `assumptions.md` via the ADR-040 cycle 2026-05-16); no warm-up commit required. Q2 — Phase 3 ships in a 6-commit cadence mirroring Phase 2's proven pattern (ADR-044 precedent) — Commit 1 (this commit) does ADR-045 plus SPEC_SHEET §3.7 Phase 3 status table; Commit 2 lands `src/scoring/{protectai, lakera_api, llm_judge}.py` per ADR-018 (4 reference rungs at unified predictions parquet schema); Commit 3 lands `src/eval/calibration_battery.py` per ADR-023 (4-ECE matrix plus Brier plus reliability plus temperature plus isotonic interventions; validation-only fit per ADR-011 Guarantee 6); Commit 4 lands `src/eval/{operating_points, slice_analysis}.py` per ADR-025 plus ADR-021 (dual-policy thresholds with verification-reachability audit per A-009 plus 5-slice OOD aggregation with pooled-headline plus per-slice spoke); Commit 5 lands `scripts/{fit_dual_policy_thresholds, run_metrics_battery, run_bootstrap_battery, eval_from_hub}.py` per ADR-022/024/034 (full-pairwise paired-bootstrap persistence per Q6 below plus joblib orchestrator-layer parallelization on 64-core Threadripper plus T0-tier eval-from-hub reproducibility); Commit 6 closes with Makefile Phase 3 targets plus fixture-extension smoke pipeline plus ROADMAP Phase 3 close note plus Phase 4 unblock. Q3 — scoring layer ships first (Commit 2) before metric layer (Commits 3-4) so the uniform per-row predictions parquet schema serves as the canonical contract for all downstream consumers; the metric layer is scorer-agnostic via the contract — mirrors Phase 1's manifest-as-canonical pattern per ADR-041. Q4 — reference scorer execution is tiered — Tier A (ProtectAI v1 plus v2; free local HF inference per ADR-018; runs in CI smoke) lands in Commit 2 unconditionally; Tier B (gpt-4o-2024-08-06 plus claude-sonnet-4-6 LLM judges plus paid Lakera fallback if needed; paid APIs) ships as `scripts/run_reference_scorers.py --tier paid` with interactive approval prompt plus `--dry-run` cost preview mirroring Phase 2's `make headline-*` pattern from ADR-020; LLM judge cache infrastructure at `evals/audit/llm_judge_cache/<judge>__<row_hash>.json` per A-007 plus A-014 (cache survives mid-Phase deprecation). Q5 — transformer-output dependence is handled via scaffold-with-classical-floor smoke discipline — all `src/eval/` modules consume any predictions parquet matching the schema contract; smoke tests use the 12 classical-floor parquets plus the tiny fixture parquets at `tests/fixtures/processed/`; transformer-pred-consuming invariants (e.g., `test_per_epoch_predictions_present` per ADR-044) remain `@pytest.mark.skip` until the 72 transformer parquets exist (canonical GPU runs operator-gated per ADR-020); precedent matches ADR-027 fixture-first smoke discipline. Q6 — bootstrap battery scope persists full pairwise (6 rung-vs-rung comparisons across 4 rungs `(classical_floor, frozen_probe, lora, full_ft)` times 5 OOD slices times pooled levels — approximately 30 paired-bootstrap cells) but the WRITEUP narrative features only the 3 headline comparisons (classical-floor vs frozen-probe — does pretraining help; frozen-probe vs LoRA — does adaptation help; LoRA vs full-FT — is parameter efficiency worth it); persistence is the methodology contract per ADR-013 (post-hoc questions answered from disk without re-running the bootstrap); multi-comparison correction acknowledgment per ADR-022 covers the WRITEUP-featured set only. Q7 — schema validation uses pydantic v2 throughout `src/eval/` and `src/scoring/` — `PredictionsRowModel`, `MetricsRecordModel`, `SliceMetricsModel`, `OperatingPointModel`, `CalibrationRecordModel`, `ReachabilityAuditModel` are `BaseModel` classes validated on read/write; consistent with Phase 1's `configs/data/source_manifest.yaml` validation via pydantic per ADR-041. Implementation cadence follows Phase 1 plus Phase 2 precedent — each commit ships green-CI surface; ADR-045 cited in subsequent commits as `Q-N` for specific decisions.
source: Phase 3 walkthrough — /exploring-options "start phase 3" seven-question ratify session 2026-05-16 following Phase 1 (ADR-041) plus Phase 2 (ADR-044) precedent
acceptance_criterion: decisions/ADR-045-phase-3-evaluation-implementation-bundle.md exists at this path with Accepted status; SPEC_SHEET.md §3.7 Phase 3 implementation status table added mirroring §3.6 Phase 2 pattern with per-commit rows tracking green status; SUBMISSION_AUDIT.md regenerates via scripts/regenerate_audit.py with ADR-045 included; uniform predictions parquet schema (rung, fold, seed, row_idx_in_source, source, text, label, predicted_proba_class1, contamination_state) implemented as pydantic PredictionsRowModel in src/eval/schemas.py landing in Commit 2; src/scoring/{protectai, lakera_api, llm_judge}.py implementing the 4 reference rungs per ADR-018 land in Commit 2 with Tier A (ProtectAI) in CI smoke and Tier B (LLM judges plus Lakera) gated on paid-API approval; src/eval/calibration_battery.py wires the eval-toolkit ECE 4-variant matrix plus Brier plus reliability plus temperature plus isotonic interventions per ADR-023 lands in Commit 3; src/eval/{operating_points, slice_analysis}.py implementing ADR-025 dual-policy thresholds plus ADR-021 5-slice OOD aggregation land in Commit 4; scripts/{fit_dual_policy_thresholds, run_metrics_battery, run_bootstrap_battery, eval_from_hub}.py implementing per-rung orchestration plus full-pairwise paired-bootstrap persistence plus T0-tier eval-from-hub land in Commit 5; LLM judge cache infrastructure at evals/audit/llm_judge_cache/<judge>__<row_hash>.json operational per A-007 plus A-014; Makefile Phase 3 targets (eval-classical-floor, eval-reference-scorers-free, eval-reference-scorers-paid, calibration-battery, dual-policy-thresholds, bootstrap-battery, eval-from-hub, metrics-battery) plus tests/smoke/test_smoke_pipeline.py extension covering end-to-end calibration plus threshold-fit pass on classical-floor fixture predictions land in Commit 6; docs/ROADMAP.md Phase 3 close note added with deliverables plus operator follow-ups plus Phase 4 unblock confirmation; transcript checkpoint at transcripts/2026-05-16__phase-3-implementation.md captured via /save-transcript; bootstrap battery cell count equals approximately 30 (6 pairwise times 5 slices) persisted to evals/bootstrap/ with WRITEUP featuring 3 headline comparisons (classical-floor vs frozen-probe plus frozen-probe vs LoRA plus LoRA vs full-FT); contamination_state column carried through every predictions parquet plus every metrics parquet per ADR-005 plus ADR-018 four-tier taxonomy; verification reachability audit JSON at evals/audit/verification_reachability.json schema validated via pydantic ReachabilityAuditModel per ADR-025 plus A-009.
closing_commit: c406f58
references:
  - decisions/ADR-018-reference-scorer-slate-and-contamination-stratification.md
  - decisions/ADR-021-eval-slate-aggregation-and-recall-fpr-pinpoints.md
  - decisions/ADR-022-statistical-inference-apparatus.md
  - decisions/ADR-023-calibration-battery-and-interventions.md
  - decisions/ADR-024-cross-fold-ci-methodology.md
  - decisions/ADR-025-dual-policy-threshold-characterization.md
  - decisions/ADR-026-module-layout-concern-grouped-subpackages.md
  - decisions/ADR-027-smoke-vs-canonical-execution-context-stratification.md
  - decisions/ADR-034-reproducibility-tier-full-ladder.md
  - decisions/ADR-040-phase-0-audit-findings-and-assumption-backfill.md
  - decisions/ADR-041-phase-1-data-implementation-bundle.md
  - decisions/ADR-044-phase-2-training-implementation-bundle.md
transcript: transcripts/2026-05-16__phase-3-implementation.md
---

# ADR-045: Phase 3 evaluation implementation bundle

## Status

Accepted (2026-05-16). Does not supersede any prior ADR; closes seven implementation-level decisions left open after Phase 0 + Phase 2.

## Context

Phase 3 (Evaluation) was unblocked at Phase 2 close (commits `496c085..8b96946` pushed to origin/main 2026-05-16). `docs/ROADMAP.md:65` confirms Phase 2 shipped 8 commits (6 implementation + 2 fix-forward) landing all 4 trained rungs as YAML-canonical recipes per ADR-044.

### Pre-existing surface inherited by Phase 3

Phase 0 already locked the methodology surface for evaluation:

- **ADR-018** — 4 reference rungs (gpt-4o-2024-08-06 + claude-sonnet-4-6 + ProtectAI v1 + v2); contamination stratification along ADR-005 three-state taxonomy; per-axis matched-budget framing.
- **ADR-021** — pooled-headline + per-slice-spoke aggregation of the 5 OOD slices (NotInject + XSTest + JBB + BIPIA + InjecAgent); recall@FPR pinpoint triad with 0.1% pooled-only plus volatility-surfacing.
- **ADR-022** — paired_bootstrap_diff per-row for trained-vs-trained; cv_clt_ci on 12 per-(fold, seed) values for rank-based metrics; per-(seed) threshold protocol; 3-seed multi-seed at the ADR-006 floor.
- **ADR-023** — full 4-ECE matrix + Brier decomposition + reliability + temperature + isotonic; headline = ECE-equal-mass(n_bins=15) + Brier on raw scores per rung.
- **ADR-024** — cv_clt_ci (Bayle 2020 Theorem 3.1) headline + block-bootstrap-on-folds spoke; LODO non-exchangeability sensitivity-check flag per A-008.
- **ADR-025** — dual-policy thresholds symmetric 1% (FPR ≤ 1% detection + recall ≥ 99% verification); per-(rung, fold, seed) val-only fit; verification-reachability audit JSON per A-009.
- **ADR-026** — module layout: `src/eval/` for calibration_battery + operating_points + slice_analysis; `src/scoring/` for reference-scorer adapters.
- **ADR-034** — reproducibility T0 tier via `scripts/eval_from_hub.py` (`huggingface_hub.snapshot_download` per `decisions/library_imports.md`).

### What remained open at Phase 3 entry

Seven implementation-level questions the Phase 0 ADRs did not specify at code-snippet level:

1. Whether the Phase 0 final audit's 7-assumption backfill (A-010 through A-016) needed a warm-up commit before Phase 3 work begins, or whether prior session work already closed it.
2. The commit cadence — mirror Phase 2's proven 6-commit pattern, or decompose differently.
3. Implementation order — scoring layer first (to establish predictions schema as a canonical contract) vs metric layer first (to ship a green-CI metric battery against classical-floor predictions immediately).
4. Reference-scorer execution strategy — how to handle the mix of free local (ProtectAI) vs paid API (LLM judges + Lakera) under the ADR-020 cost-cap discipline.
5. Transformer-output dependence — block Phase 3 on canonical GPU runs (operator-gated), or scaffold the eval layer against classical-floor predictions with deferred-unskip for transformer invariants.
6. Bootstrap battery scope — full pairwise (6 rung-vs-rung × 5 slices ≈ 30 cells) vs headline-pairs-only (3 comparisons × 5 slices = 15 cells).
7. Schema validation tooling — pydantic vs pandera vs jsonschema for the per-row predictions plus metrics-record schema enforcement.

The `/exploring-options "start phase 3"` walkthrough generated 7 numbered questions; the user ratified all recommendations with one explicit refinement on Q6 ("save all results so if we wanted to we could always compare pairs if needed"). This ADR locks all seven; subsequent Phase 3 commits implement them.

## Decision

### Q1 — Pre-Phase-3 housekeeping is already complete

`assumptions.md` lines 30-36 already carry A-010 through A-016 (GitHub Pages availability + H100 spot pricing + GPU class availability + HF Hub stability + LLM judge model availability + ProtectAI repo stability + Brandon's productive-time availability) with the audit footer at line 38 attributing the backfill to "Phase 0 final audit (ADR-040 cycle 2026-05-16)". ADR-040 exists at `decisions/ADR-040-phase-0-audit-findings-and-assumption-backfill.md` and was closed in a prior session. No warm-up commit required; Phase 3 starts directly at Commit 1.

### Q2 — 6-commit cadence (Phase 2 precedent)

Per-commit decomposition:

| Commit | Deliverable | Invariant test landed |
|---|---|---|
| 1 (this) | ADR-045 + SPEC_SHEET §3.7 + audit regen | n/a |
| 2 | `src/scoring/{protectai, lakera_api, llm_judge}.py` + `src/eval/schemas.py` (pydantic models) + Tier-A smoke | `test_reference_scorer_schema_uniform` (Phase 3 stub unskip) |
| 3 | `src/eval/calibration_battery.py` + smoke | `test_calibration_battery_outputs_4ece_plus_brier` |
| 4 | `src/eval/{operating_points, slice_analysis}.py` + smoke | `test_dual_policy_threshold_pairing` + `test_verification_reachability_audit` + `test_ood_aggregation_layout` + `test_recall_at_fpr_pinpoint_volatility` |
| 5 | `scripts/{fit_dual_policy_thresholds, run_metrics_battery, run_bootstrap_battery, eval_from_hub}.py` + smoke | `test_full_pairwise_bootstrap_persisted` (Phase 3 stub unskip on classical-floor cells; transformer cells deferred to canonical) |
| 6 | Makefile Phase 3 targets + fixture-extension smoke pipeline + ROADMAP close note | n/a |

Mirrors ADR-044 cadence exactly. Each commit ships a green-CI surface; pre-commit gates apply uniformly (gitleaks + ruff + mypy strict + nbstripout + no-emoji + audit-in-sync).

### Q3 — Scoring layer first (canonical contract)

Commit 2 ships `src/scoring/` plus `src/eval/schemas.py` before Commits 3-4 ship `src/eval/`. The uniform predictions parquet schema becomes the canonical contract that the eval layer consumes scorer-agnostically:

```python
# src/eval/schemas.py
class PredictionsRowModel(BaseModel):
    rung: str            # e.g. "tfidf-lr", "frozen-probe", "gpt-4o-2024-08-06"
    fold: int            # 0..3 for LODO; -1 for reference scorers (no LODO fold concept)
    seed: int            # 42/43/44 for trained; -1 for reference (deterministic)
    epoch: int | None    # 1 or 2 for transformers; None for classical + reference
    row_idx_in_source: int
    source: str
    text: str
    label: int           # 0 (benign) or 1 (positive)
    predicted_proba_class1: float  # in [0, 1]
    contamination_state: Literal[
        "verified_disjoint",
        "backbone-partial-disjoint",
        "suspected_contamination",
        "vendor_black_box",
    ]
```

Reference-scorer predictions (Commit 2) and trained-rung predictions (from Phase 2 outputs) share this schema. Eval-layer modules (Commits 3-5) consume any parquet matching `PredictionsRowModel` without scorer-specific branching. Mirrors the Phase 1 manifest-as-canonical pattern (`configs/data/source_manifest.yaml` validated by pydantic per ADR-041).

### Q4 — Tiered reference-scorer execution

ADR-018 mandates 4 reference rungs; ADR-020 enforces dual-layer cost cap ($125 soft / $200 hard per project). Tiering separates free local inference (CI-safe, no cost-cap interaction) from paid API spend (interactive approval gate):

| Tier | Scorers | Cost | CI / dev surface | Approval flow |
|---|---|---|---|---|
| A | ProtectAI v1 + v2 | Free local HF inference (GPU or CPU); ~$0 marginal | `pytest -m smoke` (CPU mocked weights for speed) + `make eval-reference-scorers-free` | Auto (CI-safe) |
| B | gpt-4o-2024-08-06 + claude-sonnet-4-6 + Lakera fallback | Paid API; ~$10-12 budget envelope per A-002 | `make eval-reference-scorers-paid` | Interactive prompt + `--dry-run` cost preview first (mirrors `make headline-*` pattern from Phase 2) |

Tier A ships in Commit 2 unconditionally (HF model SHAs pinned via the manifest extension per ADR-018 Phase 1 deliverable list). Tier B ships in Commit 2 with the cache infrastructure operational; the runtime invocation happens at operator-driven `make eval-reference-scorers-paid` time. LLM judge cache at `evals/audit/llm_judge_cache/<judge>__<row_hash>.json` (per A-007 plus A-014 schema) is populated on first call and survives mid-Phase deprecation.

### Q5 — Scaffold-with-classical-floor smoke (transformer-output dependence)

All `src/eval/` modules consume any predictions parquet matching `PredictionsRowModel`. Smoke tests use:

- The 12 classical-floor parquets that `scripts/train_classical_floor.py` produces locally on CPU (per ADR-044 Q6, ~5 min total).
- The tiny fixture parquets at `tests/fixtures/processed/fold-0/seed-42/{train,val,test}.parquet` (per ADR-044 Q7).

Transformer-pred-consuming invariants stay `@pytest.mark.skip` with a `"deferred to canonical run — needs GPU per ADR-020"` reason until the 72 transformer parquets exist. This matches the ADR-027 fixture-first smoke discipline plus the ADR-044 Q7 + Commit 4 pattern. Phase 4 (Analysis) can begin against classical-floor predictions in parallel with the canonical GPU runs.

### Q6 — Full-pairwise persistence + headline-only WRITEUP (user refinement)

Bootstrap battery cell count: 4 rungs → C(4, 2) = 6 pairwise comparisons × 5 OOD slices = approximately 30 paired-bootstrap cells (slightly more once IID + pooled-OOD aggregation levels are included; the exact count is implementation-time and persisted to `evals/bootstrap/`).

Per the user's explicit Q6 refinement, **all 30 cells are computed and persisted** at Phase 3 cost (~10K bootstrap iterations per cell × 30 cells via joblib parallelization on 64-core Threadripper — minutes, not hours). Persistence preserves the methodology contract per ADR-013 (per-row predictions persisted; post-hoc questions answered from disk without re-running the bootstrap).

The WRITEUP narrative features only the **3 headline comparisons** (the curriculum-step ladder):

1. **Classical-floor vs frozen-probe** — does pretraining help? (TF-IDF+LR vs ModernBERT-base classifier-on-frozen-CLS)
2. **Frozen-probe vs LoRA** — does adaptation help? (Same backbone, untrained classifier vs LoRA-tuned)
3. **LoRA vs full-FT** — is parameter efficiency worth it? (Same recipe, ~88 adapter modules vs all-trainable backbone)

Multi-comparison correction acknowledgment per ADR-022 covers the WRITEUP-featured set (3 comparisons × 5 slices = 15 paired tests featured); the remaining ~15 persisted comparisons are available for Phase 4 analysis questions or post-hoc reviewer queries without additional compute.

### Q7 — pydantic v2 schema validation

Phase 1 used pydantic for `configs/data/source_manifest.yaml` validation (per ADR-041); Phase 3 extends pydantic to all `src/eval/` plus `src/scoring/` outputs. Models landed in Commit 2 at `src/eval/schemas.py`:

- `PredictionsRowModel` — per-row predictions parquet (see Q3)
- `MetricsRecordModel` — per-(rung, fold, seed) metric record (AUPRC + AUROC + R@FPR triad + ECE + Brier)
- `SliceMetricsModel` — per-(rung, slice) aggregation record
- `OperatingPointModel` — per-(rung, fold, seed, policy) operating-point record (detection + verification)
- `CalibrationRecordModel` — per-(rung, fold, seed, calibrator) calibration record (raw + temperature + isotonic)
- `ReachabilityAuditModel` — per-(rung, fold, seed) verification-reachability audit record per A-009
- `BootstrapCellModel` — per-(rung_a, rung_b, slice, n_resamples) paired-bootstrap result

Models validate on read (parquet → DataFrame → row-by-row Model) and on write (Model → row → DataFrame). Mismatch raises `ValidationError` fail-loud (no silent type coercion). Consistent with Phase 1 + Phase 2 discipline.

## Consequences

### Positive

- All 7 implementation choices auditable in a single ADR; subsequent commits cite ADR-045 Q-N for specific decisions (mirrors ADR-044's Q-N citation pattern).
- Scoring-first ordering establishes the canonical schema contract before the metric layer consumes it; refactor risk minimal.
- Tiered reference scorer execution preserves ADR-020 cost-cap discipline (Tier B is interactive-approval-gated) while unblocking Tier A in CI smoke + dev local flows.
- Scaffold-with-classical-floor smoke unblocks Phase 4 work in parallel with operator-gated canonical GPU runs; no Phase 3 → Phase 4 sequential blocker.
- Full-pairwise persistence (Q6 user refinement) eliminates the "what about comparison X-vs-Y?" reviewer-objection class without methodology compromise; WRITEUP narrative stays focused on the curriculum-step ladder.
- pydantic schema validation extends Phase 1 + Phase 2 discipline uniformly through Phase 3; fail-loud on schema drift.
- LLM judge cache at `evals/audit/llm_judge_cache/` mitigates A-007 (temperature=0 non-determinism) plus A-014 (mid-Phase deprecation); cached scores survive vendor model deprecations.

### Negative / cost

- Tier B paid-API spend (~$10-12 total per A-002 envelope) requires interactive operator approval at `make eval-reference-scorers-paid` time; not auto-runnable.
- Full-pairwise persistence is ~30 paired-bootstrap cells × 10K iterations each — fits joblib on 64-core Threadripper in minutes but adds disk footprint (~30 parquet files at `evals/bootstrap/`).
- Scaffold-with-classical-floor smoke means transformer-pred-consuming invariants stay skip-marked until canonical runs fire; documented as Phase 2 + Phase 3 operator follow-ups in ROADMAP.
- 6-commit cadence with green-CI gate per commit means slower than monolithic landing but matches Phase 1 + Phase 2 reviewability convention.

### Neutral

- ADR-018 + ADR-021 + ADR-022 + ADR-023 + ADR-024 + ADR-025 + ADR-026 + ADR-034 are all preserved unchanged; this ADR is purely implementation-level.
- `src/eval/` + `src/scoring/` module layout follows ADR-026 5-subpackage taxonomy strictly.
- Per-axis matched-budget framing (per ADR-018) preserved in the predictions parquet `contamination_state` column.

## Alternatives Considered

### Q2 alternatives

- **4-commit cadence (collapse scorers + eval-primitives + scripts into 1 commit each)** — rejected; harder to revert atomically; one commit hitting a pre-commit gate failure means rollback of 3 modules at once.
- **8-commit cadence (one per implementation file)** — rejected; commit overhead dominates; slower without methodology gain.

### Q3 alternatives

- **Metrics layer first (against classical-floor predictions)** — rejected; faster green-CI signal but risks baking scorer-specific assumptions into the metric layer that the scoring-layer-first contract prevents.
- **Parallel scoring + metric tracks** — rejected; requires careful schema contract upfront and discipline at the seam; not worth the wall-clock savings.

### Q4 alternatives

- **All-at-once paid-API gate** — rejected; blocks Tier A (ProtectAI free local) on Tier B (LLM judges paid) approval; defeats CI-safe smoke.
- **ProtectAI-only first pass (defer LLM judges to Phase 4)** — rejected; ADR-018 acceptance_criterion mandates the 4-rung slate; deferring breaks the 4-rung headline-table integration plus the contamination-stratification 4-tier disclosure gradient.

### Q5 alternatives

- **Block Phase 3 on canonical runs** — rejected; stalls Phase 4 unblocking indefinitely on operator approval; defeats the parallel-track shipping discipline.
- **Hybrid (scaffold Commits 1-4, block 5-6 on canonical runs)** — rejected; Commit 5 + 6 are orchestration + Makefile glue, not data-dependent; deferring them mixes the scaffold + canonical-data concerns.

### Q6 alternatives

- **Headline-pairs-only (3 comparisons × 5 slices = 15 cells)** — rejected per user Q6 refinement; would force re-running the bootstrap battery if a Phase 4 reviewer asks about a non-headline pairwise comparison.
- **Custom slate via configs/eval/comparisons.yaml** — rejected; adds configuration surface without methodology gain; full-pairwise persistence handles all post-hoc cases.

### Q7 alternatives

- **pandera** — rejected; richer DataFrame-column-level constraints but adds dependency; pydantic v2 already in pyproject.toml + Phase 1 + Phase 2 dependency surface.
- **jsonschema + manual pandas validation** — rejected; minimalist but higher boilerplate; loses the Phase 1 + Phase 2 consistency benefit.

## References

- ADR-018 — Reference scorer slate plus contamination stratification (4-rung slate plus 4-tier disclosure gradient)
- ADR-021 — Eval slate aggregation plus recall@FPR pinpoints (pooled-headline plus per-slice-spoke plus 0.1% volatility-surfacing)
- ADR-022 — Statistical inference apparatus (paired-bootstrap plus cv_clt_ci plus per-(seed) threshold protocol)
- ADR-023 — Calibration battery plus interventions (4-ECE plus Brier plus temperature plus isotonic)
- ADR-024 — Cross-fold CI methodology (cv_clt_ci headline plus block-bootstrap-on-folds spoke)
- ADR-025 — Dual-policy threshold characterization (symmetric 1% plus verification-reachability audit)
- ADR-026 — Module layout (concern-grouped 5-subpackage taxonomy)
- ADR-027 — Smoke vs canonical separation (fixture-first discipline preserved)
- ADR-034 — Reproducibility tier full ladder (T0 eval-from-hub plus T1 smoke plus T3 headline-cloud)
- ADR-040 — Phase 0 audit findings plus assumption backfill (A-010 through A-016 closed prior to Phase 3)
- ADR-041 — Phase 1 data implementation bundle (pydantic manifest validation precedent)
- ADR-044 — Phase 2 training implementation bundle (Q-N citation pattern precedent plus 6-commit cadence precedent)

## Transcript

See `transcripts/2026-05-16__phase-3-implementation.md` for the `/exploring-options "start phase 3"` walkthrough that produced this bundle.
