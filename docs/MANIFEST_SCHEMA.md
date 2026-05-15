# Manifest schema

Every canonical evaluation run produces a `manifest.json` capturing provenance. The schema is owned upstream by [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) (`manifest.v1.json` or later versions); this file documents the **expected fields** so a reviewer inspecting `evals/<run>/manifest.json` knows what's there and why each field exists.

`[OPEN]` Exact schema version is locked at Phase 0-08 (library version pinning); the field list below reflects the upstream-as-of-seed expectation.

## Required fields

| Field | Type | Purpose |
|---|---|---|
| `captured_at` | ISO 8601 timestamp | When the run completed |
| `git_sha` | string | Repo commit at run time |
| `config_hash` | string (sha256) | Hash of the trainer / eval config — ensures hyperparameter immutability invariant holds |
| `data_hashes` | map(str → sha256) | One entry per output artifact: `metrics_full.csv`, `predictions_full.parquet`, per-seed parquets, etc. |
| `data_revisions` | map(str → commit) | HuggingFace dataset + model commit SHAs at fetch time |
| `contamination_flags` | map(str → enum) | Per reference scorer, the three-state taxonomy verdict: `verified_disjoint` / `suspected_contamination` / `vendor_black_box` |
| `guardrails` | list(audit-record) | Outcomes of locked audit rules: leakage checks, schema validation, etc. Each record carries audit name + detail + location + n_pairs + severity |
| `code_versions` | map(str → version) | eval-toolkit version + any other load-bearing library versions |
| `env` | map(str → version) | Python, numpy, pandas, scipy, sklearn, torch, transformers, etc. |
| `gpu_info` | map(str → val) | `count`, `memory_gb`, `name` |

## Optional fields

| Field | Type | Purpose |
|---|---|---|
| `cuda_version` | string | CUDA toolkit version at run time |
| `dirty_flag` | bool | True if the repo had uncommitted changes at capture (informational; canonical runs should always be clean) |

## Cross-references

- **Locked by**: `SPEC_GREENFIELD.md` decision ledger §6 row "Per-row prediction persistence" (locked); §Tech-Stack rows "library version pins" (Phase 0 fills exact eval-toolkit version)
- **Verified by**: Phase 4 evaluation outputs at `evals/<run>/manifest.json`; the `tests/test_invariants.py:test_hyperparameter_immutability` stub will check `config_hash` matches the committed config
- **Reviewer entry**: `docs/REPRODUCIBILITY.md` references this schema for the fresh-clone recipe
- **Contamination taxonomy** mapping: `docs/THREAT_MODEL.md` reference-scorer audit section; `EVIDENCE.md` §1-2 per-scorer verdicts

## Why this schema

Reviewers will inspect manifests to verify reproducibility claims. Documenting the expected field list at seed time prevents guessing later. The schema is **upstream-owned** (eval-toolkit publishes the canonical JSON Schema); this project follows the upstream contract rather than inventing its own provenance format.
