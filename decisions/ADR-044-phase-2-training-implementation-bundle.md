---
adr_id: "044"
slug: phase-2-training-implementation-bundle
title: Phase 2 training implementation bundle — seed slate reconciliation + manifest move + classical-floor location + YAML config schema + trainer split + per-rung orchestration + fixture preflight
date: 2026-05-16
status: Accepted
claim_id: CLAIM-044
claim: Phase 2 entry bundles seven implementation choices closing implementation gaps in ADR-015/017/019/020/026/027 and resolving three pre-lock inconsistencies surfaced at Phase 2 entry. Q1 — seed slate is set to (42, 43, 44) matching Phase 1's src/data/splits.py SEEDS constant (per ADR-041 materialization at data/processed/fold-N/seed-N/(train, val, test).parquet); body-text partial supersession of ADR-019 line 99 where (42, 1337, 2025) was an arbitrary 3-seed slate at the ADR-006 floor and re-materializing 12 splits would invalidate evals/leakage_report.json + evals/data_audit.json + evals/contamination_scan.json plus 36 parquets plus 36 index masks without methodology gain. The rest of ADR-019 (hyperparameter recipe — r=8, alpha=16, dropout=0.1, target_modules, lr=1e-4, warmup 10 percent, cosine schedule, 2 epochs, bf16, max_len=8192, WeightedTrainer, fp32 softmax cast) is preserved unchanged. Q2 — source manifest moved from data/source_manifest.yaml to configs/data/source_manifest.yaml honoring ADR-026's locked 5-subpackage layout which reserves data/ as non-committed HF cache plus processed parquets. Q3 — classical floor (TF-IDF + LR per ADR-017) lives at src/training/tfidf_lr.py honoring ADR-026 layout (ADR-017 line 92 mentioned src/rungs/tfidf_lr.py speculatively; ADR-026 is the later authoritative layout lock with no src/rungs/ subpackage). Q4 — per-rung YAML schema is primary source of truth; YAML lives at configs/rungs/<rung>.yaml; trainer code reads YAML and instantiates the recipe; ADR-019 is cited at YAML head as the lock with a do-not-edit-without-superseding-ADR comment; honors SPEC-§5 config-hash invariant per ADR-026 line 33 which only works if YAML is canonical. Q5 — trainer split by stack — src/training/train_modernbert.py handles the 3 transformer rungs via HF Trainer plus WeightedTrainer per ADR-019; src/training/train_classical.py handles the sklearn TF-IDF plus LR floor per ADR-017; both write to the uniform predictions parquet schema; satisfies ADR-026 line 73 multi-rung-trainer language by reading train_modernbert.py as the multi-rung trainer for the transformer slate. Q6 — orchestration granularity is per-rung — scripts/train_rung.py with --rung in (frozen_probe, lora, full_ft) sweeps 12 cells per invocation (3 seeds times 4 LODO folds); scripts/train_classical_floor.py runs the classical rung locally on CPU; 4 jobs total (1 local CPU plus 3 GPU); enables per-rung cost-cap budgets and per-rung resumability if a transformer rung fails mid-sweep. Q7 — Phase 2 extension of make smoke per ADR-027 line 75 wires configs/profiles/fixtures.yaml plus tests/fixtures/(parquet files) plus a tiny-data trainer path (approximately 50 examples times 4 sources times 1 fold times 1 seed times 1 epoch) for a sub-5-minute laptop CPU pipeline pass closing ADR-027's deferred fixture-pipeline wiring. Implementation cadence — 6 commits following Phase 1 precedent — Commit 1 (this commit) does manifest move + ADR-044 + paths; Commit 2 lands training primitives per ADR-019/020 (load_modernbert + lora_config + weighted_trainer + batch_table + training_args + softmax_cast); Commit 3 lands classical floor; Commit 4 lands ModernBERT trainer + 3 rung YAMLs; Commit 5 lands per-rung RunPod configs + train_rung.py orchestrator + cost_rollup.py + library_imports.md updates; Commit 6 lands fixtures + smoke pipeline + Makefile Phase 2 targets + ROADMAP Phase 2 close note.
source: Phase 2 walkthrough — /exploring-options Phase-2 seven-question ratify session 2026-05-16 following Phase 1's precedent (ADR-041 implementation bundle)
acceptance_criterion: configs/data/source_manifest.yaml exists at the new location and data/source_manifest.yaml no longer exists (git mv operation); all path references in src/data/loaders.py + src/data/manifest_validation.py + src/data/templates.py + scripts/pin_source_manifest.py + tests/test_invariants.py + Makefile + SPEC_SHEET.md + SPEC_GREENFIELD.md + assumptions.md + .gitignore are updated to the new path; test_source_manifest_schema_valid invariant still passes against the new path; ADR-019 frontmatter status remains Accepted (partial body-text supersession of seed slate only, recipe unchanged); 4-rung trained slate enumeration (classical_floor, frozen_probe, lora, full_ft) is implemented in subsequent commits with all rungs landing under src/training/; per-rung YAML configs land at configs/rungs/<rung>.yaml with ADR-019 cited at YAML head; per-rung orchestration via scripts/train_rung.py per ADR-044 Q6; Phase 2 make smoke extension lands per ADR-044 Q7 + ADR-027 line 75 wiring; 6-commit cadence closes with docs/ROADMAP.md Phase 2 close note + SUBMISSION_AUDIT regen + transcript checkpoint.
closing_commit: TBD
references:
  - decisions/ADR-015-rung-architecture-refinement.md
  - decisions/ADR-017-trained-rung-slate-expansion.md
  - decisions/ADR-019-lora-and-transformer-training-recipe.md
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md
  - decisions/ADR-026-module-layout-concern-grouped-subpackages.md
  - decisions/ADR-027-smoke-vs-canonical-execution-context-stratification.md
  - decisions/ADR-041-phase-1-data-implementation-bundle.md
transcript: transcripts/2026-05-16__phase-2-implementation.md
---

# ADR-044: Phase 2 training implementation bundle

## Status

Accepted (2026-05-16). Body-text partially supersedes ADR-019 for the seed slate only — the 3-tuple `(42, 1337, 2025)` is replaced by `(42, 43, 44)` to align with Phase 1 materialization per ADR-041; the rest of ADR-019 (recipe + LoRA config + TrainingArguments + WeightedTrainer + per-epoch save discipline + fp32 softmax cast) is preserved unchanged. ADR-019 frontmatter status remains Accepted (partial-supersession pattern matches the body-text-only convention established by ADR-043's relationship to ADR-016 Q5).

## Context

Phase 2 (Training) was unblocked at Phase 1 close (commit `496c085` + push to origin/main, 2026-05-16). The Phase 2 walkthrough surfaced three pre-lock inconsistencies that needed resolution at Phase 2 entry, plus four genuine implementation choices that the pre-locks left open.

### Three pre-lock inconsistencies

1. **Seed slate divergence**: ADR-019 line 99 specified `seed=42` iterated across `(42, 1337, 2025)` per ADR-006's three-seed floor. ADR-041 (Phase 1 implementation bundle) and `src/data/splits.py::SEEDS` materialized the 12 splits at `(42, 43, 44)` — a different arbitrary 3-tuple at the same ADR-006 floor. Phase 2's trainer must load `data/processed/fold-N/seed-N/(train|val|test).parquet`, so the trainer cannot use ADR-019's slate without re-materializing the data layer.

2. **Source manifest location**: Phase 1 implementation placed the manifest at `data/source_manifest.yaml`. ADR-026 (concern-grouped 5-subpackage layout, Phase 0-06) explicitly placed the manifest at `configs/data/source_manifest.yaml` and reserved `data/` as non-committed HF cache + processed parquets. Phase 1's choice violated ADR-026's reservation.

3. **Classical-floor module location**: ADR-017 line 92 referenced `src/rungs/tfidf_lr.py` as a Phase 1 deliverable. ADR-026 locked 5 subpackages `(data, training, scoring, eval, utils)` — no `src/rungs/`. The classical floor is a trained rung; it belongs in `src/training/`.

### Four implementation choices left open

ADR-019 + ADR-020 lock the training recipe (hyperparameters + GPU failover + adaptive batch + cost cap) at code-snippet level. ADR-026 locks the module layout. ADR-027 locks the smoke/canonical separation. What remained open at Phase 2 entry:

4. **YAML config schema** — what lives in `configs/rungs/<rung>.yaml`?
5. **Trainer architecture split** — single `trainer.py` with rung-mode branching, or split by stack?
6. **Orchestration granularity** — 48 runs total; single sweep, per-cell, or per-rung?
7. **Phase 2 `make smoke` extension** — what does ADR-027's deferred fixture-pipeline wiring look like in practice?

The `/exploring-options Phase-2` walkthrough generated 7 numbered questions covering both surfaces; the user ratified the 7 recommendations together (Phase 1 precedent). This ADR locks all seven; subsequent Phase 2 commits implement them.

## Decision

### Q1 — Seed slate `(42, 43, 44)` (partial supersession of ADR-019)

ADR-019 line 99 read `seed=42 # iterated across ADR-006 slate (42, 1337, 2025)`. This ADR replaces the parenthetical with `(42, 43, 44)` to match Phase 1's materialized splits. Both slates are arbitrary at the ADR-006 three-seed floor — neither has methodology-specific properties. Re-materializing splits would invalidate `evals/leakage_report.json`, `evals/data_audit.json`, `evals/contamination_scan.json`, 36 train/val/test parquets, and 36 index-mask parquets without methodology gain; preserving Phase 1's slate is the discipline-correct fix-forward.

The rest of ADR-019 is preserved unchanged: LoRA config (r=8, alpha=16, dropout=0.1, explicit target_modules enumeration), TrainingArguments (lr=1e-4, warmup_ratio=0.10, cosine schedule, 2 epochs, bf16, max_grad_norm=1.0, weight_decay=0.01, AdamW), data collator (max_length=8192, pad_to_multiple_of=8, dynamic padding + head-truncation), WeightedTrainer (sklearn-style class_weight balanced per-fold), per-epoch save discipline (epoch-2 headline; epoch-1 diagnostic; full-FT intermediates not persisted), and fp32 cast before final softmax.

### Q2 — Source manifest moved to `configs/data/source_manifest.yaml`

`git mv data/source_manifest.yaml configs/data/source_manifest.yaml` (this commit). Updates 10 path references across `src/data/`, `scripts/`, `tests/`, `Makefile`, `SPEC_SHEET.md`, `SPEC_GREENFIELD.md`, `assumptions.md`, `.gitignore`. The `data/` directory is now reserved per ADR-026 for non-committed artifacts (raw HF cache + processed parquets + dedup-holdout JSONL + contamination-templates parquet); `.gitignore` comment updated accordingly.

### Q3 — Classical floor at `src/training/tfidf_lr.py`

ADR-026 (later than ADR-017) is the authoritative layout lock. The 5-subpackage taxonomy has no `src/rungs/`. The classical floor is a trained rung, so it belongs in `src/training/`. ADR-017's reference to `src/rungs/tfidf_lr.py` was a speculative path naming pre-ADR-026; this ADR ratifies the canonical location.

### Q4 — Per-rung YAML schema (canonical source of truth)

Each `configs/rungs/<rung>.yaml` (4 files: `classical_floor.yaml`, `frozen_probe.yaml`, `lora.yaml`, `full_ft.yaml`) carries:

- **Header comment**: `# Locked per ADR-019 (transformer rungs) or ADR-017 (classical floor). Do not edit without superseding ADR.`
- **Identity**: `rung_id`, `rung_label`, `classifier_type` (one of: `classical`, `frozen_probe`, `lora`, `full_ft`)
- **Recipe**: all training hyperparameters per ADR-019 / ADR-017 (mirrored declaratively so the YAML is the config-hash source of truth per SPEC §5 + ADR-026 line 33)
- **Output paths**: `predictions_dir_template` (uses `{rung}`, `{fold}`, `{seed}`, `{epoch}` placeholders); `checkpoint_dir_template`

The trainer code reads the YAML and instantiates the recipe; runtime assertion that YAML values match ADR-019 / ADR-017 locked defaults (fail-loud on drift). The "canonical YAML" pattern means a `config-hash` derived from the YAML uniquely identifies the recipe — required for the SPEC §5 invariant.

### Q5 — Trainer split by stack

- `src/training/train_modernbert.py` — 3 transformer rungs (frozen-probe + LoRA + full-FT). HF Trainer + WeightedTrainer per ADR-019. Single file with mode dispatch on `classifier_type`.
- `src/training/train_classical.py` — sklearn TF-IDF + LR per ADR-017. Separate file; sklearn stack is unrelated to HF stack.

Both expose the same callable interface: `train(config: RungConfig, fold: int, seed: int) -> Path` returning the predictions parquet path. This satisfies ADR-026 line 73's "multi-rung trainer" language by treating `train_modernbert.py` as the multi-rung trainer for the transformer slate (the original ADR-026 wording was authored when classical-floor placement was assumed at `src/rungs/`).

### Q6 — Per-rung orchestration

- `scripts/train_classical_floor.py` — runs the 12 classical cells on CPU locally; sklearn `LogisticRegression` per ADR-017; near-zero cost; ~5 min wall-clock.
- `scripts/train_rung.py --rung {frozen_probe|lora|full_ft}` — sweeps 12 cells (3 seeds × 4 LODO folds) per invocation on a GPU pod via runpod-deploy. Each rung is one pod-job.

Total: 4 orchestrator invocations (1 local CPU + 3 GPU). Failure isolation: if `lora` fails mid-sweep, only that rung re-runs. Cost-cap maps cleanly to the per-rung budget (frozen-probe + LoRA < full-FT; per-rung RunPod configs sized accordingly).

### Q7 — Phase 2 `make smoke` extension

`configs/profiles/fixtures.yaml` carries the smoke profile — 4 sources × ~50 examples each × 1 LODO fold × 1 seed × 1 epoch (overrides default 4×3×2 cells). `tests/fixtures/` carries the synthetic parquets. `make smoke` (already partially wired per Phase 1) is extended to:

```makefile
smoke: test-smoke
    uv run python scripts/train_classical_floor.py --config configs/profiles/fixtures.yaml
    uv run python scripts/train_rung.py --rung frozen_probe --config configs/profiles/fixtures.yaml
```

Total wall-clock target: under 5 minutes on a laptop CPU (no GPU, no network). Validates the full Phase 2+ code path end-to-end without GPU before paying for cloud time. Closes ADR-027 line 75 deferred wiring.

## Consequences

### Positive

- All 7 implementation choices are auditable in a single ADR; subsequent commits cite ADR-044 Q-N for specific decisions.
- Seed reconciliation preserves Phase 1 artifacts (no re-materialization cost).
- Manifest move + classical-floor location honor ADR-026 layout lock (5-subpackage taxonomy intact).
- Per-rung orchestration enables per-rung resumability + per-rung cost caps + per-rung GPU class choices.
- Canonical YAML schema is required for the SPEC §5 config-hash invariant; "YAML as source" pattern satisfies it.
- Fixture preflight closes ADR-027 deferral and provides a 5-minute reviewer-friendly verification path.

### Negative / cost

- ADR-019's `(42, 1337, 2025)` seed slate is body-text-superseded; the partial-supersession pattern (no frontmatter `superseded_by` field) follows ADR-043's precedent and requires the reviewer to read ADR-044 to see the divergence.
- 10 path references updated across the repo for the manifest move; small but real change surface.
- Per-rung orchestration adds 4 CLI entrypoints (3 transformer rungs + 1 classical floor) where a single sweep would be 1; modest complexity for the failure-isolation gain.
- Fixture preflight requires `tests/fixtures/*.parquet` synthetic data — generated lazily or committed; either way adds repo churn.

### Neutral

- ADR-019 recipe (hyperparameters + WeightedTrainer + per-epoch save) preserved unchanged.
- ADR-020 compute infrastructure (GPU failover ladder + adaptive BATCH_TABLE + flash-attn fallback + dual-layer cost cap) preserved unchanged.
- ADR-026 5-subpackage layout preserved unchanged (in fact, more strictly honored).
- ADR-027 three-target Makefile preserved unchanged; the smoke target gains the fixture-pipeline wiring it always deferred to Phase 1+.

## Alternatives Considered

### Q1 alternatives
- **Re-materialize splits at `(42, 1337, 2025)`** — rejected; invalidates all Phase 1 evals JSONs + 36 parquets + 36 masks without methodology gain.
- **Quietly switch trainer seeds** — rejected per CLAUDE.md anti-pattern (no mutation of locked decision without superseding ADR).

### Q3 alternatives
- **Add `src/rungs/` via superseding ADR to ADR-026** — rejected; adds a sixth subpackage with one occupant for a non-load-bearing reason; ADR-026's 5-subpackage taxonomy is sufficient.
- **`src/scoring/tfidf_lr.py`** — rejected; `src/scoring/` per ADR-026 line 74 is for reference-scorer adapters (inference-only wrappers around external models); TF-IDF + LR is a trained rung in our slate, not a reference scorer.

### Q4 alternatives
- **Minimal YAML (selectors only, hyperparams in code)** — rejected; SPEC §5 config-hash invariant requires YAML to be canonical; minimal YAML means code is canonical and config-hash is meaningless.
- **Full snapshot YAML with runtime `assert config == code_defaults`** — rejected; the assertion is the wrong direction (code defaults are not the lock; YAML is).

### Q5 alternatives
- **Single `trainer.py` with 4-way dispatch on `classifier_type`** — rejected; sklearn stack and HF stack share no primitives; one file would be 400+ LoC with two disjoint code paths.
- **Four separate trainer files (one per rung)** — rejected; the three transformer rungs share the HF Trainer + WeightedTrainer + LoraConfig recipe; splitting them duplicates the recipe.

### Q6 alternatives
- **Single sweep CLI `scripts/train_all_rungs.py`** — rejected; all-or-nothing 10+ hour wall-clock; failure mid-sweep loses progress.
- **Per-cell CLI `scripts/train_one.py --rung X --seed Y --fold Z`** — rejected; runpod-deploy does not natively job-array; 48 separate pod invocations adds significant overhead vs 4 sweeps.

### Q7 alternatives
- **Smoke tests only (`pytest -m smoke`)** — rejected; doesn't validate the trainer code path end-to-end before paying for GPU time.
- **Fixture-data 1-epoch trial without full pipeline** — rejected; partial smoke leaves the eval JSON shape unverified.

## References

- ADR-015 — Rung architecture refinement (ModernBERT-base single-backbone trained transformer slate)
- ADR-017 — Trained-rung slate expansion (TF-IDF + LR classical floor + frozen-probe dual role)
- ADR-019 — LoRA + transformer training recipe (this ADR partially supersedes ADR-019 seed slate only)
- ADR-020 — Compute infrastructure + cost discipline (preserved unchanged)
- ADR-026 — Module layout (concern-grouped 5-subpackage taxonomy; this ADR strictly honors)
- ADR-027 — Smoke vs canonical separation (this ADR closes the deferred fixture-pipeline wiring per line 75)
- ADR-041 — Phase 1 data implementation bundle (this ADR aligns Phase 2 seeds with Phase 1 materialization)
- ADR-043 — Post-split cross-source leakage cleanup (precedent for body-text-only partial supersession pattern)

## Transcript

See `transcripts/2026-05-16__phase-2-implementation.md` for the `/exploring-options Phase-2` walkthrough that produced this bundle.
