# Reproducibility — recipe

Convenience aggregator. Canonical content lives in the `Makefile`, `pyproject.toml`, and `docs/MANIFEST_SCHEMA.md`. This file gives a single-page reproduction recipe that a fresh-clone reviewer can follow.

## Fresh-clone reproduction

```bash
git clone https://github.com/brandon-behring/prompt-injection-detection-prototype
cd prompt-injection-detection-prototype
make install        # uv sync --extra dev
make lint           # ruff + mypy strict
make test           # tests/test_invariants.py invariants
make coverage       # pytest --cov
```

## Expected runtime (post-Phase 4 state)

- `make install`: ~30 seconds with warm uv cache; ~2 minutes from scratch
- `make lint`: ~5 seconds
- `make test`: ~30 seconds (~220 tests; invariants live + smoke parametrised)
- `make test-smoke`: ~1 minute (laptop-friendly, no GPU, no network)
- `make coverage`: ~45 seconds (currently 89.82 %)
- `make audit`: ~5 seconds (`scripts/regenerate_audit.py --check`)

Headline + cloud reproduction targets (Phase 4):

- `make headline-frozen-probe`: frozen-probe headline eval via runpod-deploy
  (~30 min on A100 80GB; ~$3 per cell)
- `make headline-lora`: LoRA headline eval (~45 min; ~$5)
- `make headline-full-ft`: full-FT headline eval (~6h; ~$20; LODO only —
  OOD dropped per ADR-050)
- `make headline-cloud`: meta-target for all three above
- `make eval-from-hub RUNG=<frozen-probe|lora>`: T0 reproducibility — pulls
  the canonical fold0/seed42 checkpoint from HF Hub and score-matches
  within 1e-4 (per ADR-034). CPU-only (~10-30 min per rung).
- `make metrics-battery`: regenerate the full per-cell metrics parquet +
  bootstrap CIs from existing prediction parquets (CPU-only; ~5 minutes)

## Environment

Python `>=3.13` (pinned at Phase 0-08; see `pyproject.toml` + `.python-version`).
Load-bearing dependencies pinned at Phase 0:

- `eval-toolkit` (evaluation primitives) — version locked at Phase 0-08
- `runpod-deploy` (cloud orchestration) — version locked at Phase 0-08
- `research_toolkit` (dossier production) — version locked at Phase 0-08

`uv.lock` is committed for byte-reproducible dependency resolution. `.python-version` pins the interpreter.

## Manifest provenance (per Phase 4 evaluation run)

Every canonical eval run produces a `manifest.json` capturing:

- `git_sha` (repo state at run time)
- `config_hash` (sha256 of trainer/eval config)
- `data_hashes` (sha256 per artifact: metrics, predictions, parquets)
- `data_revisions` (HuggingFace dataset + model commit SHAs)
- `contamination_flags` (three-state taxonomy per reference scorer)
- `guardrails` (audit-rule outcomes: leakage checks, schema validation)
- `code_versions` (eval-toolkit version)
- `env` (Python, torch, transformers, etc.)
- `gpu_info` (count, memory_gb, name)

Full field list: `docs/MANIFEST_SCHEMA.md`. The schema is owned upstream by `eval-toolkit`'s manifest version; this project follows the upstream contract.

## CI gates

`.github/workflows/ci.yml` runs on every push + PR:

- **Hard gates** (block merge): pre-commit hooks, ruff, mypy strict, unit tests, audit-register-in-sync
- **Soft gate** (continue-on-error): smoke tests
- **Opt-in** (workflow_dispatch only): integration tests, network tests, notebook execution

## Reviewer reproduction tier

Three-tier reproduction ladder (locked at Phase 0-07 via [ADR-034](../decisions/ADR-034-reproducibility-tier-full-ladder.md);
implementation wired at v1.0.9 via [ADR-058](../decisions/ADR-058-eval-from-hub-non-dry-run-body-narrow-supersession-of-adr-051-block-a.md)).
Matches the contract documented in [`WRITEUP/reproducibility.md`](../WRITEUP/reproducibility.md),
the `README` "Reproduce — three tiers" section, and `READING_GUIDE.md` Path D.

- **Tier 0 (T0) — HF Hub score match** (laptop; ~$0; ~10–30 min): `make
  eval-from-hub RUNG=frozen-probe` and `make eval-from-hub RUNG=lora`
  pull the canonical fold0/seed42 checkpoint from
  `BBehring/prompt-injection-<rung>`, run CPU inference against the
  local val slate, and score-match against `evals/results.json` within
  1e-4 absolute (ADR-034 tolerance). Verifies eval-pipeline integrity
  + checkpoint-download integrity without retraining.
- **Tier 1 (T1) — laptop smoke** (laptop; ~$0; <10 min): `make smoke`
  runs `pytest -m smoke` + a fixture-data end-to-end pass through
  `scripts/run_metrics_battery.py`. Verifies code health (every
  import resolves; every entry-point runs; no schema mismatches). Does
  **NOT** verify math correctness — uses fixture data, not real data.
- **Tier 3 (T3) — headline cloud** (cloud-GPU; ~$125+; ~hours): `make
  headline-cloud` runs the full retrain-and-eval pass through
  `runpod-deploy` per the
  [ADR-020](../decisions/ADR-020-compute-infrastructure-and-cost-discipline.md)
  cost cap (`budget.cost_cap_usd = 125.0`). Verifies the entire
  training-through-eval pipeline, including data preparation. The
  only tier that re-derives headline numbers from scratch.

T2 (`make test-integration`) is a developer-tool tier (requires a
local GPU); not part of the reviewer-facing ladder because T0 covers
eval and T3 covers full retraining (per ADR-034).

T0 is the recommended reviewer path — cheapest + highest coverage for
most readers. T3 is the deepest verification level for reviewers who
want to independently re-derive every headline number. The ladder
maps onto [ACM Artifact Review and Badging](https://www.acm.org/publications/policies/artifact-review-and-badging-current)
conventions: T0 + T1 supply *Available* + *Functional* + *Reusable*;
T3 supplies *Reproducible*.

## Cross-references

- `Makefile` — canonical commands
- `pyproject.toml` — dependency declarations + tool configs
- `docs/MANIFEST_SCHEMA.md` — eval-output schema
- `.github/workflows/ci.yml` — CI gate definitions
- `SPEC_GREENFIELD.md` decision ledger §Submission row "Reproducibility tier"
