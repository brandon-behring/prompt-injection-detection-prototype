---
adr_id: "057"
slug: manifest-schema-v3-backfill-conventions
title: Per-prediction provenance manifests via scripts/backfill_provenance.py — schema, location, naming, idempotency
date: 2026-05-19
status: Accepted
claim_id: CLAIM-057
claim: >-
  v1.0.8 closes NEXT_STEPS §1.9 (Manifest backfill pipeline) by adding
  `scripts/backfill_provenance.py` + emitting per-prediction provenance
  JSON at `evals/manifests/<rung>__<fold>__<seed>__<slice>.json` for
  each of 282 prediction parquets. Schema captures `git_sha` +
  `config_hash` + `contamination_flag` (ADR-005 three-state taxonomy) +
  rung + fold + seed + slice + n_rows + predictions_relpath +
  generated_at_utc. Provenance lives in sibling JSON, not in the parquet
  columns themselves — minimizes risk of corrupting the 282-file
  artifact set + decouples provenance bump from parquet regen. Per-
  prediction shape (vs single rolled-up) chosen per /exploring-options
  batch 11 Q1 lock (matches upstream manifest.v3 fine-grained
  convention; reviewer can audit any single cell). Three filename
  patterns supported: trained-with-tail (transformer per-slice +
  per-epoch), trained-no-tail (classical floor LODO cells), reference
  (ungridded protectai-v1/v2). Idempotent: re-running on same git SHA
  + same configs produces byte-identical manifest content (modulo
  generated_at_utc; that field is documented as the regen-stamp).
source: transcripts/2026-05-19__phase-13-pypi-install-and-platt-beta.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.0.8 close, `scripts/backfill_provenance.py` exists + `make
  backfill-provenance` Makefile target invokes it. Running
  `python scripts/backfill_provenance.py` emits 282 manifest.json files
  under `evals/manifests/`. Running `--check` mode reports `OK: all 282
  manifests present` + exits 0. Each manifest carries the 8 required
  fields (schema_version + adr_ref + generated_at_utc + git_sha +
  config_hash + contamination_flag + rung + n_rows +
  predictions_relpath) + optional fold + seed + slice_name + epoch
  per the parquet's filename pattern. Contamination flags map cleanly
  to the 3-state taxonomy (vendor_black_box tier carries 0 entries per
  ADR-050 R1). `decisions/library_imports.md` notes the new script;
  CHANGELOG `[1.0.8]` carries the §1.9 closure narrative.
closing_commit: v1.0.8
supersedes: []
superseded_by: []
references:
  - https://github.com/brandon-behring/eval-toolkit  # upstream manifest schema
  - docs/MANIFEST_SCHEMA.md  # project-local schema documentation
transcript: transcripts/2026-05-19__phase-13-pypi-install-and-platt-beta.md
---

# ADR-057 — Per-prediction provenance manifests via scripts/backfill_provenance.py

## Status

Accepted (2026-05-19; landed in v1.0.8 alongside ADR-055 PyPI switch +
ADR-056 calibrator refactor).

## Context

[ADR-013](ADR-013-kit-ratify-bulk-strictness-intake-notebook-persistence.md) locked
the persistence discipline (predictions parquets pulled to local
storage before pod teardown) but did not specify a per-prediction
provenance manifest format. [ADR-016](ADR-016-data-design-bundle.md) ties
data sources to SHAs via `configs/data/source_manifest.yaml` (data-
layer provenance). [ADR-032](ADR-032-hf-hub-publication-headline-rungs-only.md) ties
HF Hub model cards to `evals/results.json` (rung-aggregate provenance).
Neither covers the *per-prediction* layer: for each of 282 prediction
parquets, what was the exact git SHA + config hash + contamination
status at the time of generation?

NEXT_STEPS §1.9 (tactical next steps, original scope per the seed)
called for `scripts/backfill_provenance.py` to inject `git_sha` +
`config_hash` + `contamination_flags` columns into the prediction
parquets. We deferred this through Phases 1-5. v1.0.8 closes the
backfill, but with a refinement: **provenance lives in sibling JSON
manifests, not in the parquet columns themselves**.

Three reasons for the sibling-JSON convention:

1. **Risk minimization**: re-writing 282 parquets risks corrupting
   the source-of-truth artifact set. The parquets are themselves the
   primary evidence (per ADR-013 + RESULTS §5). Sibling JSON is
   non-destructive.
2. **Provenance bump decoupling**: a future git_sha change (e.g., v1.0.9
   ships, predictions unchanged) should not require re-writing 282
   parquets. The JSON manifest is cheap to regenerate.
3. **Upstream schema alignment**: `docs/MANIFEST_SCHEMA.md` (per ADR-032
   model card schema work) describes manifest.v3 as a JSON document,
   not parquet columns. Sibling JSON matches.

## Decision

**Per-prediction provenance manifest** at
`evals/manifests/<rung>__<fold>__<seed>__<slice>.json` (mirroring the
parquet stem). For each prediction parquet under `evals/predictions/`,
exactly one manifest file. 282 manifests total at v1.0.8 close.

**Manifest schema** (JSON):

```json
{
  "schema_version": "1.0",
  "adr_ref": "ADR-013 + ADR-016 + ADR-032 + ADR-057",
  "generated_at_utc": "<ISO-8601 timestamp at backfill run>",
  "git_sha": "<full 40-char SHA of HEAD at backfill time>",
  "config_hash": "<SHA-256 of configs/rungs/<rung>.yaml content; null for reference scorers>",
  "contamination_flag": "<one of: verified_disjoint, backbone-partial-disjoint, suspected_contamination>",
  "rung": "<rung name; e.g. frozen_probe, lora, full_ft, tfidf-lr, protectai-v1, protectai-v2>",
  "n_rows": <integer; row count of the prediction parquet>,
  "predictions_relpath": "evals/predictions/<filename>.parquet",

  "// optional fields (per filename pattern)": "",
  "fold": <integer 0-3; trained-rung LODO fold index>,
  "seed": <integer 42/43/44; trained-rung seed>,
  "slice_name": "<bipia | injecagent | jbb_behaviors | xstest | notinject | iid>",
  "epoch": <integer; trained-rung epoch number; only for transformer per-epoch outputs>
}
```

**Three filename patterns supported by the backfill**:

| Pattern | Example | Rung type |
|---|---|---|
| Trained-with-tail | `lora__fold0__seed42__bipia.parquet` | Transformer per-slice / per-epoch (frozen_probe, lora, full_ft) |
| Trained-no-tail | `tfidf-lr__fold0__seed42.parquet` | Classical floor (single output per LODO cell) |
| Reference | `protectai-v1__bipia.parquet` | Reference scorers (ungridded; not LODO-trained) |

**Contamination flag map** (per ADR-005 three-state taxonomy + ADR-050
R1 narrowing to 3 tiers — vendor_black_box empty in this submission):

| Rung | contamination_flag |
|---|---|
| `tfidf-lr` / `tfidf_lr` | `verified_disjoint` (trained on our LODO splits by construction; ADR-017) |
| `frozen_probe` / `frozen-probe` | `backbone-partial-disjoint` (ModernBERT pretrain corpus; ADR-015) |
| `lora` | `backbone-partial-disjoint` (same backbone; ADR-019) |
| `full_ft` / `full-ft` | `backbone-partial-disjoint` (same backbone) |
| `protectai-v1` | `suspected_contamination` (published reference scorer; partial training-corpus disclosure; ADR-018 + ADR-006) |
| `protectai-v2` | `suspected_contamination` (same) |

**Idempotency** (per ADR-013 Guarantee 6):

- Re-running `scripts/backfill_provenance.py` on the same git SHA + same
  `configs/rungs/*.yaml` content produces byte-identical manifest content
  EXCEPT for the `generated_at_utc` field (documented stamp).
- `--check` mode does NOT regenerate; only verifies presence of all 282
  manifests + reports missing ones.

**Filter modes**:

- `--rung <rung>` — backfill only manifests for one rung (e.g.
  `--rung lora` writes 84 manifests).
- `--check` — verify all 282 manifests exist; exit 0 if all present,
  1 with missing-list if any absent.

## Consequences

### Positive

- **NEXT_STEPS §1.9 closed** at v1.0.8.
- **Per-prediction provenance auditability**: reviewer can `cat
  evals/manifests/lora__fold0__seed42__bipia.json` to see exactly the
  config + git SHA + contamination tier that produced that one cell.
- **Non-destructive**: parquets unchanged; provenance lives in sibling
  JSON. Future provenance bumps (e.g., re-stamp at v1.0.9 release) cost
  ~10 seconds of script time, not 282 parquet rewrites.
- **Schema-versioned**: `schema_version: "1.0"` field future-proofs
  consumer code; future manifest format changes bump the version.
- **Idempotent**: same git SHA + same configs → byte-identical
  manifests; reviewer can re-verify integrity.

### Negative

- **282 new committed files** (~140 KB total; ~500 bytes each). Adds
  visual noise to `evals/manifests/` directory listing. Mitigation:
  one subdirectory; clear filename mirroring the parquet stem.
- **Reference scorers have `null` config_hash**: protectai-v1/v2 don't
  have a `configs/rungs/<rung>.yaml`; the field is null per JSON
  convention. Documented in the schema above.
- **Generated_at_utc is non-idempotent**: re-running stamps a new
  timestamp. Acceptable per ADR-013 timestamp-as-stamp pattern; the
  rest of the manifest is byte-stable.

### Neutral

- **Original NEXT_STEPS §1.9 proposed column injection** (parquet
  columns). v1.0.8 chose sibling JSON instead per the 3-reason
  diagnosis above. This is a refinement, not a violation of §1.9
  intent (the *information* lands as planned; only the *carrier* is
  JSON not parquet).
- **eval-toolkit native column-injection** may ship later (no upstream
  issue filed at v1.0.8; potential v2.x retraining concern). Future
  v2.x retraining can emit these columns natively at training time
  + retire the backfill script.

## Alternatives Considered

### A. Inject columns into the 282 parquets (NEXT_STEPS §1.9 original)

**Rejected**: destructive to the source-of-truth artifact set; re-write
risk on 282 files. Sibling JSON achieves the same auditability
non-destructively.

### B. Single rolled-up `evals/manifests.parquet` (282 rows)

**Rejected** per /exploring-options batch 11 Q1 lock: per-prediction
JSON matches upstream manifest.v3 fine-grained convention; reviewer
can audit any single cell; deviates less from `docs/MANIFEST_SCHEMA.md`
spec.

### C. Both: per-prediction + rolled-up index

**Rejected** per batch 11 Q1 lock: per-prediction is sufficient;
rollup is `find evals/manifests -name '*.json' | xargs cat | jq` away
when needed.

### D. Don't backfill; close §1.9 as not-adopted

**Rejected**: §1.9 was a load-bearing v1.0.x close per Path 3. The
provenance gap is real (reviewers should be able to verify per-cell
git_sha + config_hash + contamination_flag).

## Links

- [ADR-013 — Persistence discipline before pod teardown](ADR-013-kit-ratify-bulk-strictness-intake-notebook-persistence.md) — manifest extends the per-prediction-parquet persistence.
- [ADR-016 — Data design (per-source SHA pinning + LODO splits)](ADR-016-data-design-bundle.md) — manifest's `config_hash` complements `source_manifest.yaml` data-layer SHAs.
- [ADR-032 — HF Hub model card schema](ADR-032-hf-hub-publication-headline-rungs-only.md) — manifest's `contamination_flag` matches the model card's ADR-005 tier field.
- [ADR-005 — Methodology over metrics + 3-state contamination taxonomy](ADR-005-methodology-principles.md) — sources the `contamination_flag` enum.
- [ADR-050 — Rung-slate narrowing + LLM-judge drop](ADR-050-rung-slate-narrowing-llm-judges-and-full-ft-ood-dropped.md) — vendor_black_box tier carries 0 entries.
- [`docs/MANIFEST_SCHEMA.md`](../docs/MANIFEST_SCHEMA.md) — upstream manifest.v3 schema documentation.
- [`scripts/backfill_provenance.py`](../scripts/backfill_provenance.py) — the v1.0.8 implementation.
