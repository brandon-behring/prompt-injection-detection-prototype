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

1. **Phase 0-00 — Brief alignment** (§Brief, 5 rows + closing kit-ratify step): user pastes brief (or key excerpts) into the conversation; `/save-transcript` captures it. Surface scope / deliverable / deadline / visibility / reviewer-profile / brief-mandated-metric constraints. Produces ADR-001. **Closing step (~10 min)**: walk the 4 §Kit-Ratify rows (Phase 0 strictness / brief-intake protocol / repository visibility / notebook format); rapid-ratify path — "accept all kit defaults" as one bulk decision if no override is needed.
2. **Phase 0-01 — Threat model** (§0, 4 rows): attack classes, language, length cap, truncation policy.
3. **Phase 0-02 — Data design** (§1, 7 rows): source slate, HF pinning, dedup, splits, ref-scorer audit, benign subsample ceilings.
4. **Phase 0-03 — Model scope** (§2, 9 rows): backbone, training-time scope, frozen-probe role, matched-budget controls, reference scorer selection, LoRA hyperparams, compute.
5. **Phase 0-04 — Eval framework** (§3, 8 rows): OOD slate, bootstrap N, multi-comparison correction, recall@FPR pinpoints, calibration battery, multi-seed protocol, paired-test method, cross-fold CI methodology.
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

**Status (2026-05-16)**: shipped across 6 commits (ecfa2b6, b8fe5ee, e988482, df72b01, 975b099, e4454c0). End-to-end pipeline produces 36 per-fold parquets + 36 index masks + 3 audit JSONs (`evals/data_audit.json`, `evals/leakage_report.json`, `evals/contamination_scan.json`) + preliminary `evals/dedup_calibration.json` (ADR-042 LLM-pre-label bootstrap). Locks: ADR-041 (implementation bundle), ADR-042 (LLM-pre-label refinement), ADR-043 (post-split leakage cleanup). 5 of 40 invariants green (manifest schema, dedup calibration, class balance, source disjoint, benign contamination). Operator follow-ups: (1) hand-examine `data/dedup_holdout.jsonl` per ADR-042 to raise `human_verified_pct` from 0 to 100 before v1.0.0 tag; (2) Phase 2 trainer reads `data/processed/fold-{0..3}/seed-{42,43,44}/{train,val,test}.parquet` directly.

**Replanning checkpoint**: before exiting Phase 1, audit data assumptions; if any locked decision broke (e.g., a source license changed), file a superseding ADR before moving to Phase 2.

## Phase 2 — Training

Per-rung config persisted in a versioned config file; all rungs trained successfully; training manifests captured; **per-row predictions persisted** alongside metrics.

**Status (2026-05-16)**: code shipped across 6 commits (8c053b0, edd3624, fc01c21, c366d26, 8151fba, _Commit6_). All 4 trained rungs implemented as YAML-canonical recipes per ADR-044 Q4: classical floor (TF-IDF + LR per ADR-017 — `verified_disjoint` contamination anchor) at `src/training/{tfidf_lr, train_classical}.py`; 3 transformer rungs (frozen-probe + LoRA + full-FT per ADR-015 + ADR-019 — `backbone-partial-disjoint`) at `src/training/train_modernbert.py` via classifier_type dispatch. ModernBERT-base SHA pinned at `8949b909` (live-fetched via `HfApi.model_info`). Per-rung orchestration per ADR-044 Q6: `scripts/train_classical_floor.py` runs locally on CPU; `scripts/train_rung.py --rung {frozen_probe|lora|full_ft}` runs per-rung GPU jobs via `configs/runpod/headline-<rung>.yaml` (runpod-deploy schema_version 2; H100/H200/A100/L40S 8-class failover; dual-DC US-MD-1+EU-RO-1). Cost discipline per ADR-020 dual-layer cap: per-pod $40/$60/$100 (frozen/lora/full-FT; total $200=HARD_CAP), `scripts/cost_rollup.py --check` aggregates manifests to `evals/cost_ledger.csv` and fails CI above $200. Locks: ADR-044 (Phase 2 implementation bundle; partial supersession of ADR-019 seed slate `(42,1337,2025)→(42,43,44)`). 8 of 40 invariants green: 3 new in Phase 2 (`test_classical_floor_rung_present`, `test_flash_attn_fallback_present`, `test_effective_batch_constant_across_gpu_classes`). `test_per_epoch_predictions_present` deferred to canonical GPU run (implementation body landed in Commit 4; unskip when 72 transformer parquets exist). Operator follow-ups before v1.0.0 tag: (1) `make headline-frozen-probe` / `headline-lora` / `headline-full-ft` to fire canonical runs (cost-cap-gated; interactive approval); (2) `make train-classical-floor` runs the 12 classical cells locally; (3) `make cost-rollup` aggregates per-run spend. Phase 3 (Evaluation) unblocked.

**Replanning checkpoint**: before exiting Phase 2, audit hyperparameter assumptions; commit any superseding ADRs.

## Phase 3 — Evaluation

All rung × slice metrics computed; OOD slate evaluated; calibration battery run; thresholds selected on validation only; results schema-validated.

**Status (2026-05-16)**: code shipped across 6 commits (c406f58, a6b5a95, a79fb45, 943f76e, a274919, _Commit6_). Locks: ADR-045 (Phase 3 implementation bundle; scoring-first canonical schema contract + 6-commit cadence + tiered reference-scorer execution + classical-scaffold smoke + full-pairwise paired-bootstrap persistence per Q6 user refinement + pydantic v2 schema validation throughout). Module landings per ADR-026 5-subpackage layout: `src/eval/schemas.py` (7 pydantic models — PredictionsRowModel + MetricsRecordModel + SliceMetricsModel + OperatingPointModel + CalibrationRecordModel + ReachabilityAuditModel + BootstrapCellModel); `src/scoring/{protectai, llm_judge_base, openai_judge, anthropic_judge}.py` per ADR-018 (4 reference rungs; Tier A free local in CI smoke; Tier B paid APIs with cache infra at `evals/audit/llm_judge_cache/` per A-007 + A-014); `src/eval/calibration_battery.py` per ADR-023 (eval-toolkit ECE 4-variant matrix + Brier + reliability + temperature + isotonic; `proba_to_logprobs` + `apply_temperature` helpers for binary-to-2-col-logit conversion); `src/eval/operating_points.py` per ADR-025 (dual-policy symmetric 1% via TargetFPRSelector + TargetRecallSelector; honest unreachable-target handling per A-009); `src/eval/slice_analysis.py` per ADR-021 (5-slice OOD slate + pooled-headline + per-slice spoke + 0.1% pinpoint volatility surfaces). Orchestration scripts per Commit 5: `scripts/{run_metrics_battery, fit_dual_policy_thresholds, run_bootstrap_battery, eval_from_hub}.py`. Full-pairwise bootstrap persistence per Q6 (~C(rungs, 2) × slices × metrics cells; WRITEUP narrative features 3 headline comparisons). T0 reproducibility tier `scripts/eval_from_hub.py` per ADR-034 — dry-run surface landed; full body gated on Phase 5 ADR-032 publication. 10 of 40 invariants green (3 new in Phase 3: `test_reference_scorer_schema_uniform`, `test_calibration_battery_outputs_4ece_plus_brier`, plus the prior Phase 2 8). 7 integration invariants (`test_dual_policy_threshold_pairing` + `test_verification_reachability_audit` + `test_ood_aggregation_layout` + `test_recall_at_fpr_pinpoint_volatility` + `test_bootstrap_n_and_stability_check` + `test_paired_across_rungs_pairing` + `test_cross_fold_ci_methodology`) deferred to Phase 4 canonical evals run (need 84 trained-rung predictions parquets from `make headline-*`). Discovery: eval-toolkit v0.31.0 has no `recall_at_fpr` primitive; implemented via `TargetFPRSelector(t).select(y, s).recall` in `src/eval/slice_analysis.py::compute_recall_at_fpr` (no library-first violation — selector primitive IS the upstream mechanism). Operator follow-ups before v1.0.0 tag: (1) `make headline-frozen-probe` / `headline-lora` / `headline-full-ft` produce the 72 transformer parquets (operator-approved canonical run); (2) `make metrics-battery` + `make dual-policy-thresholds` + `make bootstrap-battery` run against the canonical predictions; (3) `make eval-reference-scorers-paid` fires the LLM-judge slate with interactive approval per ADR-045 Q4. Phase 4 (Analysis) unblocked.

**Replanning checkpoint**: before exiting Phase 3, audit eval-design assumptions; commit any superseding ADRs.

## Phase 4 — Analysis

Bootstrap CIs computed for every headline metric; paired-bootstrap differences computed for every rung-vs-rung comparison of interest; MDE estimated for every reported CI; per-source breakdowns; reference-scorer audit completed.

**Status (2026-05-17)**: code shipped across 6 commits (70e34fd, 0bfb6e1, edc0a7b, 1b4ea1d, 87cdfeb, _Commit6_). Locks: ADR-046 (Phase 4 implementation bundle; 6-commit cadence + scaffold-with-classical + always-emit-both-CIs auto-flag + MDE-on-every-emitted-CI + LLM-rater audit included per Q5 user override + library-first hybrid figures per project-wide invariant codification at Q6 + Phase 5 prep deferred). Module landings per ADR-026 5-subpackage layout: `src/eval/marginal_bootstrap.py` (Commit 2; `eval_toolkit.bootstrap.bootstrap_ci` BCa wrappers; seed=1 headline + seed=2 stability check per ADR-022 multi-seed protocol; validated through MarginalBootstrapCellModel); `src/eval/cross_fold_ci.py` (Commit 2 headline + Commit 3 spoke; `eval_toolkit.bootstrap.cv_clt_ci` Bayle 2020 Theorem 3.1 headline + inline block-bootstrap-on-folds spoke pending upstream issue #21 + `a_008_flag_fired` boolean per A-008 sensitivity check); `src/eval/mde.py` (Commit 2; paired direct dispatch + marginal closed-form per upstream issue #20); `src/eval/figures.py` (Commit 4; library-first hybrid 7-figure slate — F3+F4+F6-right+F7-subpanels via `eval_toolkit.plotting.{plot_pr_curve, plot_reliability_diagram, plot_lift_ci, plot_bootstrap_distribution}` + project glue for F1+F2+F5+F6-left+F7-grid citing upstream issues #14+#15+#16+#22). Orchestration scripts per Commit 5: `scripts/{run_marginal_bootstrap, run_cv_clt_ci, run_mde, render_figures, audit_reference_scorers}.py`. SVG output to `docs/plots/` per ADR-030 with `{stem}.meta.json` provenance sidecars (figure_id + ADR-046 + commit_sha + timestamp_utc). Reference-scorer LLM-rater audit per Q5 user override fires via `scripts/audit_reference_scorers.py` with interactive approval gate per ADR-020 + `--dry-run` cost preview (~$5 per A-002 envelope; 4 reference rungs x ~50 disagreement-sampled pairs). 14 of 48 invariants green; 6 new Phase 4 invariants deferred to canonical evals run (`test_marginal_bootstrap_seed_stability` + `test_cv_clt_ci_headline_present` + `test_block_bootstrap_folds_spoke_present` + `test_a_008_flag_fired_when_ratio_exceeds_1_5` + `test_figures_slate_7_svgs_present` + `test_save_figure_provenance_chunks_present`). 169 smoke tests pass (~30s laptop; was 164). Library-first audit at Phase 4 entry surfaced no Phase 1-3 carryforward gaps post-ADR-047; Phase 4 ships on clean library-first baseline. Operator follow-ups before `v0.9.0-rc1` rehearsal tag: (1) `make headline-{frozen-probe,lora,full-ft}` produces the 72 transformer parquets (operator-approved canonical run, cost-cap-gated per ADR-020); (2) `make metrics-battery` + `make dual-policy-thresholds` + `make bootstrap-battery` (Phase 3) plus `make marginal-bootstrap` + `make cv-clt-ci` + `make mde-battery` + `make render-figures` (Phase 4) populate the canonical evals slate; (3) `make audit-reference-scorers` fires the LLM-rater pass with interactive approval. Phase 5 (Writeup) unblocked.

**Replanning checkpoint**: before exiting Phase 4, audit analysis assumptions; commit any superseding ADRs.

**Pre-Phase-5 rehearsal** (per ADR-033 + ADR-038): before exiting Phase 4, fire the `v0.9.0-rc1` rehearsal tag — this triggers the full publish pipeline (Quarto site build per ADR-030 + GH Pages deploy + HF Hub model card pushes per ADR-032) as a 24+ hour dress-rehearsal. If rehearsal fails, fix-forward via new commits + `v0.9.0-rc2`.

**Rehearsal-tag dispatch checklist** (load-bearing pre-`v0.9.0-rc1` gate per ADR-033):

1. `make phase4-all` completes cleanly (umbrella: `marginal-bootstrap` -> `cv-clt-ci` -> `mde-battery` -> `render-figures`).
2. `make audit-reference-scorers --dry-run` cost preview matches A-002 envelope; live pass fired with interactive approval per ADR-020.
3. `evals/audit/{cross_fold_ci_audit, mde_per_cell, reference_scorer_rater_audit}.{parquet,json}` all exist + match their pydantic v2 contracts.
4. `docs/plots/F{1..7}.svg` all exist with provenance sidecars carrying the headline commit SHA.
5. SPEC_SHEET §3.8 all 6 commits marked green; SUBMISSION_AUDIT.md regenerates cleanly via `make audit`.
6. `git tag v0.9.0-rc1` -> `git push origin v0.9.0-rc1` -> watch `.github/workflows/publish.yml` for the 24+ hour dress-rehearsal window. Failures route to fix-forward `v0.9.0-rc2` per ADR-033 tag discipline.

## Phase 5 — Writeup

All `WRITEUP.md` sections + 8 spokes (per ADR-031) drafted and populated; `index.qmd` reading-paths guide complete; all ADRs written and indexed; transcripts linked from the writeup appendix; EVIDENCE.md populated for every external-evidence claim; Quarto site renders cleanly via `make site` and via the `.github/workflows/publish.yml` GH Actions workflow per ADR-030; HF Hub model repos for headline rungs published per ADR-032 via `scripts/generate_model_cards.py`; `WRITEUP/reproducibility.md` documents T0+T1+T3 tier ladder per ADR-034.

**Phase 5 close fires `v1.0.0` submission tag per ADR-033** — CHANGELOG entry committed; `gh release create v1.0.0` with `_site.tar.gz` asset; all markers resolved.

**Replanning checkpoint**: before submission, run the full leak-audit grep + verification grep suite. Fix-forward any leakage.

Gate: every checkbox in `SPEC_SHEET.md` §2 Phase 5 ticked; reviewer URLs (source pin at `tree/v1.0.0` + live Quarto site + GH release page) all resolve; transcripts ready for private email attachment; all 6 submission-readiness integration gates per ADR-039 satisfied.

> *Phase tailoring locked at Phase 0-08 (per ADR-038):* 5-phase structure preserved; no Phase 4.5 / Phase 5a-b-c split; the rehearsal is a tag per ADR-033 not a phase; Phase 2b smoke-train preflight is unnecessary since `make smoke` per ADR-027 already covers laptop-only fixture-data preflight without a phase split; Phase 3+4 collapse is rejected since Phase 4 carries first-class statistical-inference work (paired-bootstrap + cv_clt_ci + MDE + reference-scorer audit per ADR-022 + ADR-024) that deserves its own phase-gate discipline.
