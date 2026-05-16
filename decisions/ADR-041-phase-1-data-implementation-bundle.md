---
adr_id: "041"
slug: phase-1-data-implementation-bundle
title: Phase 1 (Data) implementation bundle — manifest schema, SHA pinning, validator placement, loader arch, holdout sourcing, contamination corpus, output materialization
date: 2026-05-16
status: Accepted
claim_id: CLAIM-041
claim: Phase 1 entry locks seven implementation sub-decisions that operationalize ADR-016 (data design bundle) plus ADR-026 (module layout). (Q1) data/source_manifest.yaml uses the rich schema (13 fields per source — name plus hf_id plus type plus revision_sha plus license plus role plus expected_n plus cap plus selection_seed plus language_filter plus subset plus split plus citation_arxiv) at schema_version 1.0 with top-level bump_history list; inlining keeps ADR-016 Q6 ceilings + Q5 LMSYS English filter + dossier provenance grep-able next to the SHAs. (Q2) HF + GitHub SHAs are live-fetched once at Phase 1 entry via scripts/pin_source_manifest.py — huggingface_hub.HfApi.dataset_info for HF datasets; subprocess git ls-remote HEAD for GitHub-cloneable sources (xstest plus BIPIA plus InjecAgent). Re-runs are idempotent if upstream SHAs unchanged; mismatch triggers SHAMismatchError unless --force flag records a bump_history entry per ADR-036 bump-trigger policy. (Q3) manifest_validation.py lives at src/data/manifest_validation.py — ADR-026 §Decision-tree comment explicitly listed "manifest validation" as a src/data/ concern; the 3 files in the §Decision tree are illustrative not exhaustive; no ADR-026 supersession needed. (Q4) src/data/loaders.py uses a single load_source(name) dispatch function with per-source _normalize_<source> helpers in the same file (option D) — HF datasets.load_dataset(repo, revision=sha) handles fetch + cache via HF default cache; English-only filter applied to lmsys-chat-1m before subsample (per ADR-016 Q5); column normalization produces a uniform (text, label, source) row schema. (Q5) The 50-pair dedup calibration holdout is created via stratified-cosine-band sampling — 5 cosine bands {[0.95-1.0], [0.85-0.95], [0.75-0.85], [0.65-0.75], [0.55-0.65]} times 5 pairs per band; Brandon hand-labels each by visual inspection (ground-truth duplicate-or-not); banding ensures the FPR + FNR measurement at the locked 0.80 threshold actually probes the decision boundary; persisted to data/dedup_holdout.jsonl (gitignored — contains source content). (Q6) The contamination scan reference corpus is the slate-plus-templates blend (option B) — A-006's "known public training-data mirrors" is interpreted operationally as (a) the 4 train-positive sources themselves (cross-source contamination check) plus (b) approximately 200 templates extracted from HackAPrompt success-pattern metadata (canonical injection-template space per Schulhoff 2023 attack-technique taxonomy); generic-web-text mirrors (The Pile plus C4 plus RedPajama) deferred to afterword as scope-expansion extension. (Q7) Post-dedup output is materialized as per-fold parquet under data/processed/fold-{0..3}/seed-{42,43,44}/{train,val,test}.parquet (48 files); index masks persisted under data/processed/index_masks/ for reverse-trace; Makefile gains 5 granular targets data-fetch + data-dedup + data-splits + data-audit + data-prepare (umbrella). Sub-decisions Q5 plus Q6 are methodology refinements to ADR-016 §Q4 calibration evidence + assumption A-006 acceptance criteria; Q1 + Q2 + Q3 + Q4 + Q7 are implementation specifics flowing from ADR-016 + ADR-026 deferred-to-Phase-1 surfaces.
source: /exploring-options Phase-1 walk (post-Phase-0 compaction); ADR-016 §Q3 + §Q4 + §Q5 + §Q6 + §Q7 deferred implementation specifics; ADR-026 §Decision tree comment "manifest validation"
acceptance_criterion: data/source_manifest.yaml exists at repo root with schema_version equals 1.0 plus bump_history list plus 11 sources each carrying the 13 rich-schema fields; src/data/manifest_validation.py raises ManifestSchemaError on any contract violation (missing field plus wrong type plus role-count mismatch plus slate-completeness mismatch); scripts/pin_source_manifest.py runs idempotently against unchanged remotes; data/dedup_holdout.jsonl exists with 25 plus 25 stratified-cosine-band pairs and is gitignored; evals/contamination_scan.json includes per-eval-row max-cosine to the (slate plus approximately 200 templates) reference corpus; data/processed/fold-N/seed-S/{train,val,test}.parquet emit per the 48-file LODO times seed grid; Makefile carries five granular data- targets plus data-prepare umbrella; tests/test_invariants.py unskips test_source_manifest_schema_valid (Commit 1) plus test_dedup_calibration_persisted (Commit 3) plus test_benign_contamination_scan_clean (Commit 5).
closing_commit: ecfa2b6
references:
  - decisions/ADR-016-data-design-bundle.md
  - decisions/ADR-026-module-layout-concern-grouped-subpackages.md
  - decisions/ADR-036-library-version-pins-tag-pin-plus-freeze.md
  - decisions/ADR-040-phase-0-audit-findings-and-assumption-backfill.md
  - https://huggingface.co/docs/huggingface_hub/main/en/package_reference/hf_api
  - https://huggingface.co/docs/datasets/main/en/package_reference/loading_methods
  - https://www.sbert.net/docs/pretrained_models.html
  - https://arxiv.org/abs/1908.10084
  - https://arxiv.org/abs/2311.16119
transcript: transcripts/2026-05-16__phase-1-implementation.md
---

# ADR-041: Phase 1 (Data) implementation bundle — manifest schema, SHA pinning, validator placement, loader arch, holdout sourcing, contamination corpus, output materialization

## Status

Accepted (2026-05-16).

## Context

ADR-016 locked the §1 Data methodology bundle (source slate plus splits plus HF pinning plus dedup encoder plus ordering plus ceilings plus reference-scorer audit) at Phase 0-02. ADR-026 locked the §5 Code architecture module-layout taxonomy at Phase 0-06. Both ADRs deferred several implementation specifics to Phase 1 entry:

- ADR-016 §Q3 said "HF dataset revisions plus GitHub commit SHAs pinned at Phase 1 entry in unified data/source_manifest.yaml" but did not specify the manifest schema shape, SHA discovery method, or revision-bump workflow.
- ADR-016 §Q4 said "50-pair labeled holdout" for dedup calibration but did not specify the holdout sampling strategy or labeling method.
- ADR-026 §Decision tree listed loaders.py + dedup.py + splits.py with a comment line `# source loaders, dedup, LODO splits, manifest validation`, leaving manifest_validation.py placement implied-but-not-explicit.
- Assumption A-006 (contamination scan) said "known public training-data mirrors" but did not specify the reference corpus.

A post-Phase-0 /exploring-options Phase-1 walk surfaced 7 implementation decision points, posed them with options + pros/cons + recommendation, and the user ratified the 7 recommendations as a bundle. This ADR documents the 7 locks.

Sub-decisions Q1 plus Q2 plus Q3 plus Q4 plus Q7 are implementation specifics that flow directly from ADR-016 + ADR-026 deferred-to-Phase-1 surfaces — they do not introduce new methodology beyond what ADR-016 + ADR-026 imply.

Sub-decisions Q5 plus Q6 are methodology refinements — Q5 specifies the holdout sampling strategy beyond ADR-016 §Q4's "50-pair labeled holdout"; Q6 operationalizes A-006's "known public training-data mirrors" as a specific (slate plus templates) corpus blend. These two sub-decisions warrant ADR documentation under the project anti-pattern rule against "Adding a methodology component without an ADR."

## Decision

### Q1 — Manifest schema shape (rich = option B)

`data/source_manifest.yaml` carries the rich schema at `schema_version: "1.0"`. Top-level keys are `schema_version` plus `generated_at_utc` plus `pin_method` plus `adr_ref` plus `bump_history` plus `sources`. The `sources` list contains 11 rows, each with 13 fields:

| Field | Type | Purpose |
|---|---|---|
| `name` | str | Internal source key (snake_case; e.g., `lmsys_chat_1m`) |
| `hf_id` | str | Upstream identifier (HF repo or GitHub repo path) |
| `type` | str | `hf_dataset` or `git_repo` |
| `revision_sha` | str | Pinned commit/revision SHA (40-char preferred) |
| `license` | str | License identifier (e.g., `CC-BY-4.0`) |
| `role` | str | `train_positive`, `train_benign`, or `ood_eval` |
| `expected_n` | int | Post-dedup row-count estimate from dossier |
| `cap` | int or None | Subsample ceiling per ADR-016 Q6 (None = use all) |
| `selection_seed` | int or None | Seed for random subsample (None if `cap` is None) |
| `language_filter` | str or None | ISO 639-1 code (e.g., `en` for LMSYS-Chat-1M) |
| `subset` | str or None | HF dataset config/subset (e.g., `behaviors` for JBB) |
| `split` | str or None | HF split name (e.g., `train`, `train_sft`) |
| `citation_arxiv` | str or None | arXiv ID for provenance (e.g., `2309.11998`) |

Validator `src/data/manifest_validation.py` enforces presence + types + role-count mismatch + slate-completeness — `validate_manifest(path)` returns the parsed dict on success or raises `ManifestSchemaError` with field-level context.

### Q2 — Live-fetch SHAs (option A)

`scripts/pin_source_manifest.py` is the one-time + bump-driven entry point. HF datasets resolve via `huggingface_hub.HfApi.dataset_info(repo_id).sha`; GitHub-cloneable sources (xstest, BIPIA, InjecAgent) resolve via `subprocess.run(["git", "ls-remote", url, "HEAD"])`. HF_TOKEN auto-discovers from environment (per ADR-035) for gated datasets (lmsys-chat-1m).

Re-runs are idempotent — fresh SHAs vs prior manifest SHAs are compared; identical = no-op; mismatch = `SHAMismatchError` unless `--force` flag records a `bump_history` entry. `bump_history` schema per entry: `{bumped_at_utc, trigger, diffs: [{name, prior, fresh}]}`.

### Q3 — `manifest_validation.py` placement (option A)

The validator lives at `src/data/manifest_validation.py`. ADR-026 §Decision tree's comment line for `src/data/` reads `# source loaders, dedup, LODO splits, manifest validation` — manifest validation is explicitly listed as a `src/data/` concern. The 3 files named under the tree (`loaders.py`, `dedup.py`, `splits.py`) are illustrative not exhaustive. No ADR-026 supersession needed; adding `manifest_validation.py` is consistent with the locked taxonomy.

### Q4 — Loader architecture (option D — HF dispatch + per-source normalize family)

`src/data/loaders.py` exposes a single `load_source(name: str) -> pandas.DataFrame` dispatch function. The function reads `data/source_manifest.yaml` to resolve `(hf_id, type, revision_sha, split, subset, language_filter, cap, selection_seed)` per source; calls `datasets.load_dataset(hf_id, name=subset, split=split, revision=revision_sha)` for HF datasets; clones + reads + parses CSV/JSON for GitHub sources; dispatches to a private `_normalize_<source>(ds)` helper for column normalization + label encoding (each source has bespoke column names — deepset uses `text`/`label`; mosscap uses `prompt`/`tag`; etc.).

HF default cache (`~/.cache/huggingface/datasets/`) handles repeat-fetch acceleration. For RunPod-pod consumption, `HF_HOME` may point at a persistent volume to survive cold-start re-fetches; for laptop usage, the default cache suffices.

The English-only language filter for `lmsys_chat_1m` is applied inside `_normalize_lmsys_chat_1m` via the `language` column (post-Phase-1 audit may surface that LMSYS-Chat-1M has language tags or requires fasttext-langdetect — choice documented in `decisions/library_imports.md`).

### Q5 — Stratified-cosine-band holdout (option A)

The 50-pair dedup calibration holdout is built via stratified-cosine-band sampling:

1. Compute pairwise MiniLM-L6-v2 cosines within each of the 4 train-positive sources (deepset, lakera-gandalf, mosscap, hackaprompt).
2. From each source's within-source pair distribution, sample candidate pairs in 5 cosine bands: `[0.95, 1.0)`, `[0.85, 0.95)`, `[0.75, 0.85)`, `[0.65, 0.75)`, `[0.55, 0.65)`.
3. Take 5 candidate pairs from each band (25 pairs total across the bands) and another 5 random pairs uniformly across the range — round-robin across sources to spread coverage; total 25 + 25 = 50.
4. Brandon labels each pair by visual inspection — `true_duplicate: bool` (semantic-near-duplicate or surface-form-near-duplicate per ADR-016 Q4 dedup spec).
5. Persist to `data/dedup_holdout.jsonl` (gitignored — contains source content) plus a SHA-256 digest of the JSONL bytes recorded in `evals/dedup_calibration.json` for tamper-evident provenance.

The 5-band design ensures the FPR + FNR measurement at the locked 0.80 threshold (per ADR-016 §Q4) actually probes the decision boundary — without banding, the random sample would be dominated by the low-cosine mass and report uninformative FPR/FNR ≈ 0 / ≈ 0.

### Q6 — Contamination-scan reference corpus (option B — slate + ~200 templates)

`evals/contamination_scan.json` checks per-eval-row max-cosine to a two-component reference corpus:

1. **Cross-source slate**: each OOD eval row's max-cosine across the 4 train-positive source pools (post-dedup). Catches the realistic threat — did this OOD row appear (or near-paraphrase appear) in a train-positive pool?
2. **Extracted injection templates** (approximately 200): templates extracted from HackAPrompt success-pattern metadata — Schulhoff 2023 catalogues 29 prompt-injection attack techniques; for each technique we extract approximately 7 templates from observed-success patterns. Templates capture the canonical injection-template space; catches near-paraphrase contamination with the broader injection-template distribution.

Per-row scan output: `{eval_source, eval_row_idx, max_cosine_slate, max_cosine_templates, max_cosine_overall, flagged: max_cosine_overall >= 0.85}`.

Generic-web-text mirrors (The Pile, C4, RedPajama) are deferred to afterword. ADR-016 compute envelope (approximately $60-115 total) did not price in The-Pile-sized scans; the realistic threat model for prompt-injection eval contamination is template-level overlap not generic-web-text overlap. If reviewer pushes back, point to the future-work spoke + the afterword commitment.

### Q7 — Output materialization + Makefile execution surface (option A)

Post-dedup + post-split outputs materialize as per-fold parquet:

```
data/processed/
├── fold-0/seed-42/{train,val,test}.parquet
├── fold-0/seed-43/{train,val,test}.parquet
├── fold-0/seed-44/{train,val,test}.parquet
├── fold-1/...
├── ... (48 parquet files total — 4 folds × 3 seeds × 3 roles)
└── index_masks/
    └── fold-N__seed-S__{train,val,test}.npy
```

Each parquet carries columns `(text, label, source, row_idx_in_source)`. Index masks (`numpy.ndarray[int64]`) persist the source-row indices for reverse-trace at audit time (e.g., `evals/leakage_report.json` cites specific row pairs that would-have-been-leaks-pre-dedup).

`Makefile` gains 5 granular Phase 1 targets plus 1 umbrella:

- `make data-fetch` — runs `pin_source_manifest` then materializes raw per-source rows to `data/raw/<source>.parquet` (gitignored).
- `make data-dedup` — runs MiniLM dedup + cross-source LMSYS-priority pass; materializes deduped pool to `data/processed/deduped_pool.parquet`.
- `make data-splits` — runs LODO × seeds × stratified 80/20; materializes 48 per-fold parquet files.
- `make data-audit` — runs counts + class-balance + leakage + contamination scans; writes `evals/{data_audit,leakage_report,contamination_scan,dedup_calibration}.json`.
- `make data-prepare` — umbrella that runs all four in order; idempotent; outputs are timestamp-checked.

## Consequences

**Positive:**

- Manifest is grep-able and reviewer-readable — every per-source decision (cap, seed, language filter, split, citation) is visible in one file.
- SHA pinning at Phase 1 entry plus idempotent re-runs plus explicit `bump_history` workflow gives a tamper-evident audit trail; ADR-036 bump-trigger policy operationalizes.
- Manifest validator + invariant test `test_source_manifest_schema_valid` enforces the rich schema at CI — no silent drift in manifest shape.
- Single-file loader (`loaders.py` with `_normalize_*` helpers) keeps per-source quirk-handling local without splitting into 11 files.
- Stratified-cosine-band holdout produces an actually-informative FPR + FNR at the 0.80 threshold (vs random sample which would be uninformative).
- Contamination corpus blend (slate + templates) covers the realistic threat (template-level overlap) at proportionate cost; generic-pretraining-mirror extension is named for future work.
- Per-fold materialized parquet is the shape ADR-015 + ADR-017 trainer consumes directly; granular Makefile targets enable partial rebuilds during Phase 1 debugging.

**Negative / cost:**

- Live-fetching SHAs requires network at Phase 1 entry; HF_TOKEN required for gated datasets (lmsys-chat-1m may require accepting the dataset card; document in `decisions/library_imports.md`).
- 48 parquet files plus dedup pool plus raw cache approximately 500 MB on disk under `data/`; all gitignored.
- Stratified-cosine-band labeling consumes approximately 1-2 hours of researcher time (Brandon hand-labels); offset by producing a defensible FPR + FNR measurement.
- Template-extraction from HackAPrompt success-pattern metadata requires processing HackAPrompt-success-rows; one-time cost approximately 30 min; templates persist as `data/contamination_templates.parquet` (gitignored).
- Manifest_validation.py adds a 4th file to `src/data/` beyond ADR-026 §Decision tree's explicit 3 — defensible per the §Decision tree comment line listing manifest validation as a concern; documented in this ADR's §Q3.

**Neutral:**

- ADR-016 + ADR-026 locks preserved unchanged; ADR-041 fills in deferred implementation specifics. No supersession.
- Six new Phase 1 deps added across commits 1-4 (huggingface_hub, datasets, sentence-transformers, pandas, pyarrow, scikit-learn); declared in `pyproject.toml` `[project.dependencies]`; locked via `uv.lock` at submission tag.
- Three invariant test stubs unskip across commits 1 + 3 + 5 — schema-valid, dedup-calibration, contamination-clean.

## Alternatives Considered

- **Q1 option A (minimal 5-field schema)**: rejected — loses provenance (citation, dossier reference) and ADR-016 Q6 cap rationale visibility.
- **Q1 option C (two-tier inline minimal + sidecar detail)**: rejected — two files to keep in sync; `bump_history` harder to maintain across files.
- **Q2 option B (read from dossier MANIFEST.json)**: rejected — dossier doesn't record every source SHA; staleness risk.
- **Q2 option C (pin to "main" tag)**: explicitly banned by ADR-016 §Q3 + ADR-011 Guarantee 8.
- **Q3 option B (manifest_validation in src/utils/)**: rejected — schism; manifest is a data concern; loaders.py would import from utils/.
- **Q3 option C (scripts/validate_manifest.py only)**: rejected — no reusable validator class; tests cannot import.
- **Q3 option D (inline inside loaders.py)**: rejected — couples loading with validation; harder to test isolated.
- **Q4 option A (one load_source dispatch, no normalize family)**: rejected — each HF dataset has bespoke column shapes; central dispatch without per-source helpers would balloon into a giant if/elif tree inside one function.
- **Q4 option B (separate parquet materialization for raw)**: rejected — raw pre-dedup is throwaway; only post-dedup pool plus per-fold splits warrant materialization.
- **Q4 option C (per-source classes)**: rejected — more boilerplate; ADR-026 guideline (≤50 LoC per module) tighter as a class-per-source pattern.
- **Q5 option B (random 50 pairs)**: rejected — random sample dominated by low-cosine pairs; uninformative FPR/FNR around the 0.80 threshold.
- **Q5 option C (adversarial paraphrase-generator pairs)**: rejected — synthetic positives are not in-distribution; calibration may be optimistic.
- **Q5 option D (LLM-judge labels 100 pairs + spot-check 20)**: rejected — judge prior may contaminate calibration; near-duplicate task quality on judges is unknown.
- **Q6 option A (slate only)**: rejected — doesn't catch near-paraphrase contamination with the broader injection-template distribution.
- **Q6 option C (slate + templates + The Pile / C4 / RedPajama sample)**: rejected for prototype — compute envelope (approximately $60-115) didn't price in The-Pile-sized scans; deferred to afterword.
- **Q6 option D (slate-only minimal)**: rejected — under-specifies A-006's "known public training-data mirrors" wording.
- **Q7 option B (single deduped store + index masks only)**: rejected — trainer has to apply masks at load; harder for reviewer to spot-check a single fold.
- **Q7 option C (per-fold parquet + single umbrella Make target only)**: rejected — slower Phase 1 debugging iteration; can't partially rebuild.

## References

- ADR-016 (data design bundle — locks methodology surface)
- ADR-026 (module layout — locks `src/data/` taxonomy including "manifest validation" comment)
- ADR-036 (library version pins + bump-trigger policy)
- ADR-040 (Phase 0 audit findings + assumption backfill — A-006 contamination assumption)
- huggingface_hub HfApi docs — https://huggingface.co/docs/huggingface_hub/main/en/package_reference/hf_api
- HF datasets load_dataset docs — https://huggingface.co/docs/datasets/main/en/package_reference/loading_methods
- Sentence-Transformers pretrained models — https://www.sbert.net/docs/pretrained_models.html
- Reimers and Gurevych 2019 "Sentence-BERT" — https://arxiv.org/abs/1908.10084
- HackAPrompt (Schulhoff et al. 2023, EMNLP) — https://arxiv.org/abs/2311.16119

## Transcript

See `transcripts/2026-05-16__phase-1-implementation.md` for the conversation that led to this decision (post-Phase-0-compaction /exploring-options Phase-1 walk).
