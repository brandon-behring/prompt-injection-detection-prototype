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

Two-tier reproduction (locked at Phase 0-07 via ADR-029):

- **Tier 0 (T0) — HF Hub score match** (no GPU): `make eval-from-hub
  RUNG=frozen-probe` and `make eval-from-hub RUNG=lora` pull the canonical
  fold0/seed42 checkpoint from `BBehring/prompt-injection-<rung>`, run CPU
  inference against the local val slate, and score-match against
  `evals/results.json` within 1e-4 absolute (ADR-034 tolerance). ~10-30
  min per rung. Verifies eval-pipeline integrity + checkpoint-download
  integrity.
- **Tier 1 (T1) — full canonical re-eval** (GPU; A100 80GB): `make
  headline-cloud` re-runs frozen-probe + LoRA + full-FT through the full
  LODO matrix via `runpod-deploy`. ~7h wall-clock; ~$28 GPU spend (per
  ADR-039 cost envelope). Verifies the full training-through-eval
  pipeline.

T0 is the recommended reviewer path. T1 is offered for the reviewer who
wants to independently verify training-side numerics; T0 alone covers
the methodology-and-eval-side reproducibility claim.

## Cross-references

- `Makefile` — canonical commands
- `pyproject.toml` — dependency declarations + tool configs
- `docs/MANIFEST_SCHEMA.md` — eval-output schema
- `.github/workflows/ci.yml` — CI gate definitions
- `SPEC_GREENFIELD.md` decision ledger §Submission row "Reproducibility tier"
