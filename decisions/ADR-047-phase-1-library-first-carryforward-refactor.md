---
adr_id: "047"
slug: phase-1-library-first-carryforward-refactor
title: Phase 1 library-first carryforward refactor — audit findings + remediation plan (splits + dedup + leakage_report + contamination_scan migration to eval-toolkit primitives; orphaned code removed in-commit)
date: 2026-05-16
status: Accepted
claim_id: CLAIM-047
claim: Phase 4 entry walkthrough surfaced a project-wide library-first invariant reaffirmed by the user at Q6 (figures slate) — "we are not handrolling tools that can be better handled by my eval-toolkit and separately tested there with golden eval data sets" — applied retroactively to Phases 1 plus 2 plus 3 (shipped) and prospectively to Phase 5 (planned). The audit pass against `src/data/` plus `src/training/` plus `src/scoring/` plus `src/eval/` identified four confirmed Phase 1 hand-rolls — `src/data/splits.py::make_splits` reimplements the source-disjoint k-fold partition that eval-toolkit's `SourceDisjointKFoldSplitter` was literally abstracted from a predecessor of this project to provide (per its own docstring); `src/data/dedup.py::{dedup_within_source, drop_train_test_leakage, dedup_cross_source_benigns}` reimplements the greedy-near-dedup + cross-corpus dedup machinery that eval-toolkit's `near_dedup` plus `cross_dedup` plus `EmbeddingCosineStrategy` already provide turnkey; `src/data/audit.py::compute_leakage_report` reimplements the train↔eval leakage detection that eval-toolkit's `run_leakage_checks([ExactDuplicateCheck(), NearDuplicateCheck(...), CrossSplitLeakageCheck()])` already orchestrates; `src/data/audit.py::compute_contamination_scan` reimplements per-row max-cosine-to-reference-corpus machinery that eval-toolkit's `SimilarityStrategy.pairs_across(query, reference, k=1)` already provides via the strategy Protocol. Phase 2 (`src/training/`) and Phase 3 (`src/scoring/` + `src/eval/{calibration_battery, operating_points, slice_analysis}.py`) are confirmed clean — Phase 2 uses HF Transformers plus LoRA plus sklearn (eval-toolkit doesn't compete), Phase 3 scoring is project-specific LLM-judge plus ProtectAI wrappers, and Phase 3 eval is already library-first per `decisions/library_imports.md` ledger lines 39 through 53. Phase 5 (Quarto site plus model card generation plus WRITEUP authoring plus HF Hub upload) is confirmed clean in pre-audit. Remediation plan — four refactor commits, each consuming the upstream primitive plus deleting now-unreachable local helpers in-commit per the no-orphaned-code-during-refactor discipline (saved as memory 2026-05-16); local project-owned embedder glue (`src/data/dedup.py::{get_encoder, compute_embeddings, encoder_revision_sha}` — sentence-transformer all-MiniLM-L6-v2 loader plus SHA-pinning plus batched encoding) preserved as the `embedder=` callable passed to `EmbeddingCosineStrategy(embedder=compute_embeddings)`; locked constants preserved bit-for-bit (within-source dedup THRESHOLD=0.80 per ADR-016 Q4; cross-source dedup THRESHOLD=0.80 + LMSYS-priority cross-source dedup per ADR-016 Q4-A; train↔test leakage cleanup threshold=0.85 per ADR-043; benign contamination threshold=0.85 per ADR-041 Q6; CONTAMINATION_THRESHOLD plus BENIGN_CONTAMINATION_THRESHOLD_PCT trigger gates per ADR-041 Q6 + ADR-016 A-005); `evals/leakage_report.json` schema migration required (project-dict to `LeakageReport`-derived JSON or adapter wrapper) — preserved-callers updated in the same commit. Two upstream contributions filed — issue #18 (wire dedup-holdout golden test against this project's 50-pair adversarial dataset; the "separately tested there with golden eval data sets" requirement from the project-wide invariant) and issue #19 (cookbook docs for the 3 compositional patterns that caused the original hand-rolls). Refactor sequencing — Commit 1 (this) lands ADR-047 plus SPEC_SHEET §3.5 audit-findings row plus SUBMISSION_AUDIT regen; Commit 2 refactors `src/data/splits.py` (`SourceDisjointKFoldSplitter` consumer); Commit 3 refactors `src/data/dedup.py` (`near_dedup` plus `cross_dedup` plus `EmbeddingCosineStrategy` consumer; project-owned embedder preserved); Commit 4 refactors `src/data/audit.py` (`run_leakage_checks` plus `pairs_across` consumer; `evals/leakage_report.json` schema migration). After Commit 4 lands plus all data-pipeline invariants pass plus `make data-prepare` regenerates 36 split parquets plus dedup-holdout calibration re-runs cleanly, ADR-046 (Phase 4 implementation bundle per prior ratification) lands and Phase 4 Commit 1 begins. Net effect — library-first invariant honored retroactively; reviewer-facing audit story strengthened; ~50 percent of `src/data/` LoC removed; methodology semantics + locked constants preserved bit-for-bit; no Phase 4 scope or schedule change beyond a 4-commit delay.
source: Phase 4 entry walkthrough — /exploring-options 7-question Phase 4 ratify session 2026-05-16; user reaffirmation at Q6 reframed library-first as project-wide invariant requiring retroactive audit; audit pass executed in-session against Phases 1 plus 2 plus 3 (shipped) plus Phase 5 (planned)
acceptance_criterion: decisions/ADR-047-phase-1-library-first-carryforward-refactor.md exists at this path with Accepted status; SPEC_SHEET.md §3.5 (Phase 1 status table) gains an audit-findings row tracking the 4-refactor sequence (Commits 1-4) with green status as each lands; SUBMISSION_AUDIT.md regenerates via scripts/regenerate_audit.py with ADR-047 included; decisions/upstream_issues.md ledger reflects issues #18 (golden dedup-holdout test contribution) and #19 (3-pattern cookbook docs contribution) at filed status; src/data/splits.py refactored to consume eval_toolkit.splits.SourceDisjointKFoldSplitter for the source-disjoint partition with project glue retained for the (3-seed × stratified 80/20 train/val) nested split per ADR-016 Q2 with no orphaned helpers remaining; src/data/dedup.py refactored to consume eval_toolkit.text_dedup.{near_dedup, cross_dedup, EmbeddingCosineStrategy(embedder=compute_embeddings)} for greedy-near-dedup plus train↔test cross-corpus dedup with local pairwise_cosines plus _greedy_first_occurrence_mask helpers deleted in-commit; src/data/audit.py::compute_leakage_report refactored to consume eval_toolkit.leakage.run_leakage_checks with ExactDuplicateCheck plus NearDuplicateCheck(threshold=0.85) plus CrossSplitLeakageCheck() with evals/leakage_report.json schema migrated (project-dict to LeakageReport-derived JSON or adapter); src/data/audit.py::compute_contamination_scan refactored to consume eval_toolkit.text_dedup.EmbeddingCosineStrategy(embedder=compute_embeddings).pairs_across(query, reference, k=1) with project-specific per-source aggregation glue retained plus local _per_row_max_cosine_to_ref helper deleted in-commit; locked constants (within-source dedup THRESHOLD=0.80 per ADR-016 Q4; cross-source dedup THRESHOLD=0.80 per ADR-016 Q4-A; leakage cleanup threshold=0.85 per ADR-043; CONTAMINATION_THRESHOLD=0.85 plus BENIGN_CONTAMINATION_THRESHOLD_PCT per ADR-041 Q6) preserved bit-for-bit; make data-prepare regenerates 36 split parquets plus dedup-holdout calibration re-runs cleanly with identical or near-identical FPR plus FNR plus sensitivity-table cells; data-pipeline invariants (test_splits_lodo_partition_disjoint plus test_dedup_within_source_threshold_applied plus test_leakage_report_persisted plus test_contamination_scan_persisted) all pass against refactored code; transcript checkpoint at transcripts/2026-05-16__phase-4-entry-plus-phase-1-library-first-refactor.md captured via /save-transcript after Commit 4 close; ADR-046 (Phase 4 implementation bundle) writing unblocked at Commit 4 close; Phase 4 Commit 1 begins after ADR-046 lands.
closing_commit: ab8a501
supersedes:
superseded_by:
references:
  - decisions/ADR-016-data-design-bundle.md
  - decisions/ADR-041-phase-1-data-implementation-bundle.md
  - decisions/ADR-042-llm-prelabel-dedup-holdout-bootstrap.md
  - decisions/ADR-043-post-split-cross-source-leakage-cleanup.md
  - decisions/ADR-036-library-version-pins-tag-pin-plus-freeze.md
  - decisions/library_imports.md
  - decisions/upstream_issues.md
  - https://github.com/brandon-behring/eval-toolkit/issues/18
  - https://github.com/brandon-behring/eval-toolkit/issues/19
  - https://github.com/brandon-behring/eval-toolkit/blob/v0.31.0/src/eval_toolkit/splits.py
  - https://github.com/brandon-behring/eval-toolkit/blob/v0.31.0/src/eval_toolkit/text_dedup.py
  - https://github.com/brandon-behring/eval-toolkit/blob/v0.31.0/src/eval_toolkit/leakage.py
transcript: transcripts/2026-05-16__phase-4-entry-plus-phase-1-library-first-refactor.md
---

# ADR-047: Phase 1 library-first carryforward refactor

## Status

Accepted (2026-05-16). Does not supersede ADR-041 (Phase 1 implementation bundle), ADR-042 (dedup-holdout protocol), or ADR-043 (post-split leakage cleanup) — those locked the **methodology**; this ADR locks the **library-first carryforward refactor of the implementation** while preserving every methodology constant bit-for-bit.

## Context

### How the audit was triggered

Phase 4 entry walkthrough generated a 7-question `/exploring-options` ratify session (per Phase 0 + Phase 2 + Phase 3 precedent). Q6 (figures slate) initially proposed hand-rolled matplotlib for the 7-figure slate; the user pushed back — `eval-toolkit` ships `plotting.py` with `plot_pr_curve`, `plot_reliability_diagram`, `plot_bootstrap_distribution`, `plot_metric_bars`, `plot_lift_ci`, `plot_score_histograms`, `plot_confusion_matrix_grid`, `save_figure` (PNG/PDF/SVG with provenance iTXt), `set_plot_style` + `PALETTE` — and the project's library-first invariant requires consuming these before any local glue. Four upstream gaps surfaced (`plot_roc_curve` + `plot_pareto_frontier` + `plot_slice_metric_heatmap` + `paired_bootstrap_diff` `n_jobs` kwarg) and were filed as issues #14 + #15 + #16 + #17 on `brandon-behring/eval-toolkit` before any local Phase 4 figures-slate glue ships.

User then reaffirmed the rule as project-wide — "this is true throughout everything in this project so we want to make sure are not handrolling tools that can be better handled by my eval-toolkit and separately tested there with golden eval data sets etc" — and explicitly extended the audit retroactively to Phases 1 + 2 + 3 (already-shipped) plus prospectively to Phase 5 (planned).

### Audit method

For each `src/` subpackage, the audit (a) inventoried the public API surface (every `def` + `class` at module top-level), (b) inventoried the corresponding eval-toolkit module's public API surface (where one exists with overlapping module-name semantics — `src/data/dedup.py` ↔ `eval_toolkit.text_dedup`; `src/data/splits.py` ↔ `eval_toolkit.splits`; `src/data/audit.py` ↔ `eval_toolkit.leakage`; etc.), (c) read both signatures + docstrings + reference impls + confirmed semantic match, (d) classified each local symbol as **hand-roll** (upstream primitive fits cleanly), **partial overlap** (upstream has machinery, project glue composes around it), or **project-specific** (no upstream equivalent; legitimate local code).

### Audit results

| Phase | Module | Classification | Refactor target |
|---|---|---|---|
| **Phase 1** | `src/data/splits.py::make_splits` | hand-roll | `SourceDisjointKFoldSplitter` |
| **Phase 1** | `src/data/dedup.py` (3 fns) | hand-roll | `near_dedup` + `cross_dedup` + `EmbeddingCosineStrategy(embedder=compute_embeddings)` |
| **Phase 1** | `src/data/audit.py::compute_leakage_report` | hand-roll | `run_leakage_checks([ExactDuplicateCheck(), NearDuplicateCheck(...), CrossSplitLeakageCheck()])` |
| **Phase 1** | `src/data/audit.py::compute_contamination_scan` | partial overlap | `EmbeddingCosineStrategy(embedder=compute_embeddings).pairs_across(query, reference, k=1)` + project per-source aggregation glue |
| Phase 1 | `src/data/manifest_validation.py` | project-specific | config-time YAML schema for `source_manifest.yaml` — `eval_toolkit.manifest` is runtime artifact provenance — different concern |
| Phase 1 | `src/data/loaders.py` | project-specific | per-source bespoke normalizers (HackAPrompt + LMSYS-Chat-1M + ...) — `HFDatasetsLoader` is generic — project glue legitimate |
| Phase 1 | `src/data/templates.py` | project-specific | HackAPrompt template extraction — no upstream equivalent |
| Phase 2 | `src/training/*.py` | clean | HF Transformers + LoRA + sklearn — `eval-toolkit` doesn't compete here |
| Phase 3 | `src/scoring/*.py` | clean | LLM-judge wrappers + ProtectAI inference — no upstream overlap |
| Phase 3 | `src/eval/{calibration_battery, operating_points, slice_analysis}.py` | clean | already library-first per `decisions/library_imports.md` lines 39-53 |
| Phase 3 | `src/eval/schemas.py` | clean | pydantic models for project-specific row schemas; `eval_toolkit.schemas/` is JSON schemas for artifact validation — different concern |
| Phase 5 (planned) | model card / Quarto / WRITEUP / HF Hub upload | clean | no upstream overlap |

The **damning detail** for hand-roll #1: `eval_toolkit.splits.SourceDisjointKFoldSplitter`'s own docstring reads "Generalizes the source-disjoint split pattern from `prompt-injection-sdd`" — meaning the upstream primitive was abstracted FROM a predecessor of THIS project, then we didn't use it here. The strongest possible "should be upstream" signal.

### Project-wide invariant codified

Two memory files locked the relevant rules:

- `library-first-is-project-wide-invariant` — audit eval-toolkit + runpod-deploy + research_toolkit at EVERY module-design step, file upstream issues for gaps before workaround.
- `no-orphaned-code-during-refactor` — when refactoring to consume an upstream primitive, delete the now-unreachable local helpers in the SAME commit; never ship a transition commit with both paths live.

Both apply going forward to Phase 4 + Phase 5 work.

## Decision

### Refactor sequence (4 commits)

Each refactor lands as its own commit per the established cadence (Phase 1 + Phase 2 + Phase 3 all used per-commit module landings). Each commit (a) consumes the upstream primitive, (b) deletes the now-unreachable local helpers + unused imports in the same commit, (c) preserves locked methodology constants bit-for-bit, (d) re-runs the relevant invariants + fixture regeneration.

| Commit | Deliverable | Invariants verified |
|---|---|---|
| 1 (this) | ADR-047 + SPEC_SHEET §3.5 audit-findings row + SUBMISSION_AUDIT regen | n/a |
| 2 | `src/data/splits.py` refactor — `SourceDisjointKFoldSplitter` consumer; round-robin source-bucket logic deleted in-commit; project glue for nested seed split + stratified 80/20 train/val preserved per ADR-016 Q2 | `test_splits_lodo_partition_disjoint` + `test_splits_per_seed_stratification` |
| 3 | `src/data/dedup.py` refactor — `near_dedup` + `cross_dedup` + `EmbeddingCosineStrategy(embedder=compute_embeddings)` consumers; local `pairwise_cosines` + `_greedy_first_occurrence_mask` deleted in-commit; project-owned embedder glue (`get_encoder` + `compute_embeddings` + `encoder_revision_sha`) preserved | `test_dedup_within_source_threshold_applied` + `test_dedup_cross_source_lmsys_priority` + dedup-holdout calibration re-run cleanly |
| 4 | `src/data/audit.py` refactor — `compute_leakage_report` consumes `run_leakage_checks`; `compute_contamination_scan` consumes `EmbeddingCosineStrategy.pairs_across`; local `_per_row_max_cosine_to_ref` deleted in-commit; `evals/leakage_report.json` schema migration to `LeakageReport`-derived JSON (or adapter wrapper preserving downstream consumers) | `test_leakage_report_persisted` + `test_contamination_scan_persisted` + 3 pre-existing data-pipeline invariants |

After Commit 4 lands + all data-pipeline invariants pass + `make data-prepare` regenerates 36 split parquets + dedup-holdout calibration re-runs cleanly, **ADR-046 (Phase 4 implementation bundle)** lands and Phase 4 Commit 1 begins.

### Locked constants preserved bit-for-bit

| Constant | Value | Source | Refactor preserves |
|---|---|---|---|
| Within-source dedup threshold | 0.80 | ADR-016 Q4 | `near_dedup(threshold=0.80)` |
| Cross-source dedup threshold | 0.80 | ADR-016 Q4-A | `cross_dedup(threshold=0.80)` |
| Train↔test leakage cleanup threshold | 0.85 | ADR-043 | `NearDuplicateCheck(threshold=0.85)` |
| Benign contamination threshold | 0.85 | ADR-041 Q6 | `pairs_across(...) >= 0.85` |
| Sentence-transformer model | `all-MiniLM-L6-v2` | ADR-016 Q4 | preserved in `get_encoder()` (project-owned) |
| LODO k folds | 4 | ADR-016 Q2 | `SourceDisjointKFoldSplitter(k=4)` |
| Seeds | (42, 43, 44) | ADR-006 | project seed-loop glue |
| Val fraction | 0.20 | ADR-016 Q2 | project `train_test_split(test_size=0.20)` |

### Project-owned glue preserved

- `src/data/dedup.py::get_encoder()` — sentence-transformer factory (project owns model choice + revision SHA per `encoder_revision_sha()`)
- `src/data/dedup.py::compute_embeddings(texts, batch_size=64)` — batched encoding wrapper (project owns batch size + normalization choice)
- `src/data/dedup.py::encoder_revision_sha()` — pinning utility (project owns the pin)
- `src/data/splits.py::FoldSeedSplit` dataclass — project-specific (fold_id, seed, held_out_source, train, val, test) tuple
- `src/data/splits.py::apply_leakage_cleanup` — project orchestrator wiring `drop_train_test_leakage` (post-refactor: `cross_dedup`) into the splits pipeline per ADR-043
- `src/data/audit.py::compute_data_audit` — per-source class-balance + length-distribution audit (project-specific reporting layout)
- Per-source aggregation glue in `compute_contamination_scan` — flag rate per source + percentile reporting (project-specific layout for `evals/contamination_scan.json`)

### Upstream contributions

Two filed at audit close:

- `brandon-behring/eval-toolkit#18` — wire the project's 50-pair golden dedup-holdout dataset (`data/dedup_holdout.jsonl` per ADR-041 Q5 + ADR-042) into eval-toolkit's CI test fixtures; closes the "separately tested there with golden eval data sets" gap directly.
- `brandon-behring/eval-toolkit#19` — add cookbook docs covering the 3 compositional patterns that caused the original hand-rolls (nested seed-split composition over `SourceDisjointKFoldSplitter`; callable-embedder pattern for `EmbeddingCosineStrategy`; `pairs_across` for cross-corpus contamination scan).

## Consequences

**Positive:**

- Library-first invariant honored retroactively; project audit story strengthens (reviewer-facing — explicit ADR documenting the audit + remediation + upstream contributions; no silent technical debt).
- ~50 percent of `src/data/` LoC removed (orphaned helpers deleted per no-orphaned-code discipline); maintenance surface shrinks correspondingly.
- Upstream eval-toolkit benefits from the golden dedup-holdout contribution (issue #18) — every future eval-toolkit consumer gains regression coverage against this project's adversarial corpus.
- The 3-pattern cookbook docs contribution (issue #19) reduces the likelihood of similar hand-rolls in other downstream consumers + in this project's future modules.
- Phase 4 + Phase 5 work proceeds with cleaner library-first hygiene as the baseline expectation.

**Negative / cost:**

- Phase 4 start delayed by 4 commits (~half-day to a day of focused work for the refactors + invariant re-runs + fixture regeneration).
- `evals/leakage_report.json` schema migration creates a one-time discontinuity in the audit artifact format; downstream consumers (any analysis script reading the JSON) need updating in the same commit.
- Dedup-holdout calibration re-runs may surface tiny numerical drift if `near_dedup`'s greedy-scan order differs imperceptibly from local impl (e.g., tie-breaking); rare but not impossible.
- `make data-prepare` re-runs the full 11-source data pipeline (~10 min wall-clock per ADR-041 Q7); per-fold split parquets regenerate; downstream Phase 2 trained-rung parquets are unaffected (they consume the splits + retrain triggers stay manual).

**Neutral:**

- Methodology semantics unchanged (every locked constant + every threshold + every protocol preserved bit-for-bit); no methodology ADR superseded.
- `decisions/library_imports.md` ledger expands with the new eval-toolkit primitive uses (planned post-refactor table-update).
- `SUBMISSION_AUDIT.md` regenerates clean; CI gate stays green.
- ADR-046 (Phase 4 implementation bundle) writing is briefly deferred but content unchanged.

## Alternatives Considered

- **File issues + write ADR-047 (defer refactor) + proceed to Phase 4 immediately**: Skip the refactor; ADR-047 documents "acknowledged + scheduled post-submission per `v1.0.x`". *Rejected because*: lower discipline; reviewer-facing audit story weaker; by the time submission lands, carryforward debt may be larger; the user explicitly chose Option A (refactor now) when presented with the four-way alternative.
- **File issues only + proceed to Phase 4 (skip ADR for now)**: Just file the upstream issues to mark the gap; no ADR. *Rejected because*: no immutable record of the audit + decision; future-you may not remember the gap exists; weakest discipline option; violates the SPEC_GREENFIELD anti-pattern "Adding a methodology component without an ADR" (the refactor *is* a methodology-adjacent change even though it preserves methodology semantics).
- **Pause Phase 4 entirely; full Phase 1 audit + refactor sprint (3-5 days)**: Treat this as a Phase 1 errata sprint; refactor + comprehensive 4th-confirmation + dedup-holdout calibration re-run against upstream primitives + extra scoping discussions. *Rejected because*: overscope — the audit findings are already confirmed at a level sufficient for the 4-commit refactor; a multi-day sprint would lose Phase 4 momentum without proportional benefit.
- **Refactor only the most damning hand-roll (`make_splits`) + defer the rest**: Skip dedup + leakage + contamination_scan refactors. *Rejected because*: arbitrary; if the library-first invariant applies, it applies to all 4 hand-rolls; partial refactor leaves the inconsistency the audit was meant to close.
- **In-place rewrite of ADR-041 to embed the library-first language retroactively**: Edit ADR-041 to say "uses eval_toolkit primitives" as if it always had. *Rejected because*: violates the ADR immutability constraint per `decisions/README.md` ("ADRs are immutable; supersede via new ADR"); the right pattern is exactly what this ADR does — a new ADR documenting the audit + remediation + carryforward.

## References

- `decisions/ADR-016-data-design-bundle.md` — methodology source for LODO k=4 plus seed plus threshold constants
- `decisions/ADR-041-phase-1-data-implementation-bundle.md` — Phase 1 implementation bundle being carryforward-refactored
- `decisions/ADR-042-llm-prelabel-dedup-holdout-bootstrap.md` — dedup-holdout dataset that issue #18 contributes upstream
- `decisions/ADR-043-post-split-cross-source-leakage-cleanup.md` — leakage cleanup threshold = 0.85 source
- `decisions/ADR-036-library-version-pins-tag-pin-plus-freeze.md` — eval-toolkit `v0.31.0` pin
- `decisions/library_imports.md` — discipline ledger (positive evidence of upstream consumption; expands post-refactor)
- `decisions/upstream_issues.md` — discipline ledger (gap-filing record; entries #14-19 listed)
- `https://github.com/brandon-behring/eval-toolkit/issues/18` — golden dedup-holdout test contribution
- `https://github.com/brandon-behring/eval-toolkit/issues/19` — 3-pattern cookbook docs contribution
- `https://github.com/brandon-behring/eval-toolkit/blob/v0.31.0/src/eval_toolkit/splits.py` — `SourceDisjointKFoldSplitter` source (docstring cites the predecessor abstraction)
- `https://github.com/brandon-behring/eval-toolkit/blob/v0.31.0/src/eval_toolkit/text_dedup.py` — `near_dedup` + `cross_dedup` + `EmbeddingCosineStrategy` + `SimilarityStrategy.pairs_across` source
- `https://github.com/brandon-behring/eval-toolkit/blob/v0.31.0/src/eval_toolkit/leakage.py` — `run_leakage_checks` + `ExactDuplicateCheck` + `NearDuplicateCheck` + `CrossSplitLeakageCheck` source

## Transcript

See `transcripts/2026-05-16__phase-4-entry-plus-phase-1-library-first-refactor.md` for the conversation that led to this decision (the Phase 4 entry walkthrough Q6 user-reaffirmation + retroactive audit pass + four-way option ratification).
