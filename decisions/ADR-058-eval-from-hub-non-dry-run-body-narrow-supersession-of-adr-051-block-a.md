---
adr_id: "058"
slug: eval-from-hub-non-dry-run-body-narrow-supersession-of-adr-051-block-a
title: scripts/eval_from_hub.py non-dry-run body wired — narrow supersession of ADR-051 Block A (T0 score-match carryforward); Block B (38 invariant scaffolds) remains carryforward
date: 2026-05-19
status: Accepted
claim_id: CLAIM-058
claim: >-
  ADR-051 narrowly superseded ADR-034 §Tier T0 + ADR-039 §gate 3 via two
  carryforward blocks with explicit v1.1.x landing conditions. v1.0.9
  closes Block A — the T0 score-match wiring at `scripts/eval_from_hub.py`
  — by replacing the stub that exited 2 with the full body:
  `huggingface_hub.snapshot_download(repo_id)` → architecture-dispatched
  load (`AutoModelForSequenceClassification.from_pretrained` for
  frozen-probe + full-ft; base ModernBERT + `PeftModel.from_pretrained`
  for lora) → CPU inference via library-first reuse of
  `src.training.train_modernbert._predict_proba` → per-row score-match
  against the committed reference predictions parquet at
  `evals/predictions/<rung>__fold0__seed42__<slice>.parquet` within
  1e-4 absolute tolerance per ADR-034 §Tier T0. Strict-mode exit code
  per /exploring-options 2026-05-19 Q1 lock: exit 1 on any row exceeding
  tolerance (no silent failures); exit 0 on all-pass; exit 2 on invalid
  args (rung not in `evals/results.json::published_rungs`, reference
  parquet missing). Smoke coverage at `tests/smoke/test_eval_from_hub_smoke.py`
  (9 tests; mocked-only per Q6 lock — no real HF Hub fetch in CI).
  Block B (38 invariant scaffolds in `tests/test_invariants.py`) remains
  carryforward to v1.1.x per ADR-051 — Block B is orthogonal to T0
  wiring and out of scope for v1.0.9. The narrow supersession scope of
  this ADR is **Block A only**.
source: transcripts/2026-05-19__v1-0-9-adr-051-block-a-close.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.0.9 close, `scripts/eval_from_hub.py` non-dry-run path executes
  the full wiring (snapshot_download → load → CPU inference → per-row
  score-match → emit predictions parquet) instead of returning 2 with a
  carryforward message. `make eval-from-hub RUNG=frozen-probe` and
  `RUNG=lora` exit 0 with score-match summary within 1e-4 tolerance per
  ADR-034 §Tier T0 §Score-match contract. `uv run pytest
  tests/smoke/test_eval_from_hub_smoke.py -v` reports 9/9 passing.
  `uv run mypy --strict scripts/eval_from_hub.py` returns 0. ADR-051
  frontmatter `superseded_by` updated to `["058"]` in-place per ADR-029
  convention (narrow Block A only; Block B remains carryforward).
closing_commit: v1.0.9
supersedes: [ADR-051]
superseded_by: []
references:
  - decisions/ADR-034-reproducibility-tier-full-ladder.md
  - decisions/ADR-051-v1.0.x-carryforward-of-t0-and-invariant-scaffolds.md
  - decisions/ADR-032-hf-hub-publication-headline-rungs-only.md
  - decisions/ADR-019-lora-and-transformer-training-recipe.md
  - scripts/eval_from_hub.py
  - tests/smoke/test_eval_from_hub_smoke.py
  - evals/results.json
transcript: transcripts/2026-05-19__v1-0-9-adr-051-block-a-close.md
---

# ADR-058 — eval_from_hub non-dry-run body wired (narrow supersession of ADR-051 Block A)

## Status

Accepted (2026-05-19; landed in v1.0.9 patch alongside eval-toolkit
v0.40.0 → v0.42.0 bump + `fit_isotonic_binary_local` adapter removal
per library-first invariant + eval-toolkit#44 closure).

## Context

[ADR-051](ADR-051-v1.0.x-carryforward-of-t0-and-invariant-scaffolds.md)
was written at v1.0.2 (2026-05-18) to formally document the two
governance gaps that the v1.0.0 / v1.0.1 submission tags did not close:

- **Block A** — `scripts/eval_from_hub.py` non-dry-run body was a
  ~7-line stub that printed a carryforward message and exited 2.
  ADR-034 §Tier T0 §Score-match contract was unmet from the consumer
  side (publish half closed cleanly at v1.0.1).
- **Block B** — 38 stubs in `tests/test_invariants.py` carried
  `@pytest.mark.skip(reason="v1.0.0 carryforward stub")`. ADR-039
  §gate 3 ("all stubs unskipped + green") was unmet.

ADR-051 narrowly superseded ADR-034 (T0 axis only; T1 + T3 unchanged)
+ ADR-039 (gate 3 axis only; gates 1+2+4+5+6 unchanged) and codified
both as v1.1.x carryforwards with explicit landing conditions.

v1.0.9 closes **Block A**. Block B remains a v1.1.x carryforward.

## Decision

Implement the full ADR-034 §Tier T0 score-match contract in
`scripts/eval_from_hub.py` and narrowly supersede ADR-051 — Block A
only. ADR-051 Block B (38 invariant scaffolds) remains carryforward
to v1.1.x; this ADR does not affect it.

### Block A — implementation shape

Per the /exploring-options 2026-05-19 6-question execution-lock:

- **Q1 lock — score-match strictness**: exit 1 on any row exceeding
  1e-4 absolute tolerance (no silent failures discipline per project
  Python standards). Per-row delta diagnostics printed to stderr on
  fail (top-5 exceedances by |delta|).
- **Q6 lock — smoke test fetch strategy**: mocked-only for CI
  hermeticity. Real `huggingface_hub.snapshot_download` + CPU inference
  are NOT exercised in CI (would require network + ~500MB checkpoint
  download per slice; ~30s CPU inference per slice). The reviewer-
  facing path (`make eval-from-hub RUNG=frozen-probe`) exercises the
  full body live.

### Architecture-dispatched model loading

`scripts/eval_from_hub.py::_load_model_and_tokenizer` dispatches by rung:

- `frozen-probe` / `full-ft` → `AutoModelForSequenceClassification.from_pretrained(snapshot_path)`
  with co-located tokenizer.
- `lora` → base `ModernBERT-base` (pinned revision
  `8949b909ec900327062f0ebf497f51aef5e6f0c8` per ADR-015) + `PeftModel.from_pretrained(snapshot_path)`;
  tokenizer loaded from the pinned backbone (LoRA adapter folders do
  not ship a tokenizer).

CPU only; `torch.float32`; library-first reuse of
`src.training.train_modernbert._predict_proba` for the inference loop
(softmax_fp32 cast per ADR-019 numerical-stability discipline).

### Score-match reference parquet

Per-row comparison against `evals/predictions/<rung_underscore>__fold0__seed42__<slice>.parquet`
(committed reference; rung name uses underscore form per file-system
convention: `frozen_probe`, `lora`, `full_ft`). The HF Hub repo_id
uses kebab-case per ADR-032: `BBehring/prompt-injection-<rung>`.
ADR-058's `_rung_to_underscore` helper bridges the two naming
conventions.

The per-row delta is computed as `abs(new_proba - reference_proba)`
where:

- `new_proba` = re-derived `predicted_proba_class1` from the freshly-
  downloaded HF Hub checkpoint.
- `reference_proba` = committed `predicted_proba_class1` from the
  canonical fold0/seed42 training run.

A passing run requires every row's `|delta| ≤ 1e-4`. ADR-034 §Tier T0
tolerance is per-row, not aggregated; the per-row formulation is
strictly conservative (per-row pass implies aggregated AUPRC/AUROC
pass; the converse is not true).

### Eval slice + sample size

The `--eval-slice` CLI argument (default `bipia`) selects which OOD
slice to score-match. The `--n-rows` argument (default 100) samples
the first N rows of the reference parquet (deterministic; matches
the committed run's row ordering). If the reference parquet has
fewer than N rows, all rows are used.

For reviewer-facing T0 verification, `make eval-from-hub RUNG=<rung>`
runs with defaults; n=100 is sufficient to detect any non-trivial
checkpoint divergence (CPU vs GPU floating-point differences at fp32
are typically < 1e-5; the 1e-4 tolerance has a 10× safety margin).

### Library-first reuse

This implementation reuses existing project + library primitives
rather than hand-rolling:

- `huggingface_hub.snapshot_download` — upstream library, not
  hand-rolled fetching.
- `transformers.AutoModelForSequenceClassification` + `AutoTokenizer`
  — upstream library.
- `peft.PeftModel.from_pretrained` — upstream library; lora
  architecture-aware loading.
- `src.training.load_modernbert.load_modernbert` — internal helper for
  base ModernBERT loading at pinned revision.
- `src.training.train_modernbert._predict_proba` — internal inference
  loop with softmax_fp32 cast per ADR-019.

No new methodology primitives are introduced; all components are
upstream library calls or existing internal helpers.

## Consequences

- **Reviewer experience**: `make eval-from-hub RUNG=frozen-probe` +
  `RUNG=lora` now exit 0 with score-match summary; the auto-generated
  HF Hub model cards (live since v1.0.1) become executable from the
  consumer side. The T0 reproducibility contract is sealed.
- **ADR-051 supersession scope**: this ADR narrowly supersedes ADR-051
  **Block A only**. ADR-051 Block B (38 invariant scaffolds) remains
  carryforward to v1.1.x. ADR-051's frontmatter gains
  `superseded_by: ["058"]` per ADR-029 in-place convention; ADR-051's
  status remains Accepted (the body documents both blocks; only one
  is now closed).
- **No methodology changes**: the implementation reuses existing
  primitives; no new ADR for inference loop / tokenization / etc.
  is needed. The only governance addition is this ADR.
- **Smoke coverage**: 9 tests added at `tests/smoke/test_eval_from_hub_smoke.py`
  covering (a) `--dry-run` subprocess invocation for both published
  rungs, (b) score-match tolerance logic with synthetic numpy arrays
  (within-tol, exceeds-tol, length-mismatch), (c) published-rungs
  validator against `evals/results.json`, (d) reference parquet
  loader, (e) kebab↔underscore rung-name translation. Per Q6 lock:
  no real HF Hub fetch; CI hermetic.
- **CHANGELOG entry**: `[1.0.9]` documents the closure narrative +
  the eval-toolkit v0.40.0 → v0.42.0 bump that lands in the same
  commit (consumes eval-toolkit#44 / `fit_isotonic_binary` upstream
  per library-first invariant; removes `fit_isotonic_binary_local`
  adapter from v1.0.8).

## Linked ADRs

- **Superseded (narrow, Block A only)**: ADR-051.
- **Referenced**: ADR-034 (the T0 contract this ADR closes); ADR-032
  (HF Hub publication; v1.0.1 deliverable that closed the publish
  half); ADR-019 (softmax_fp32 numerical stability discipline reused
  in inference); ADR-039 (gate 3 — Block B of ADR-051 unchanged by
  this ADR).
- **Source**: REPO_AUDIT_2026-05-18 §P0 "HF Hub / T0 reproducibility
  is unfinished" (audit finding that motivated ADR-051; this ADR
  closes the Block A half).

## Transcript

Decisions surfaced during the 2026-05-19 v1.0.9 planning session
(`/exploring-options` 6-question execution-lock; transcript at
`transcripts/2026-05-19__v1-0-9-adr-051-block-a-close.md`).
