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

## Expected runtime (current seed state)

- `make install`: ~30 seconds with warm uv cache; ~2 minutes from scratch
- `make lint`: ~5 seconds
- `make test`: ~1 second (7 skip-marked invariant stubs at seed; populated at Phase 1)
- `make coverage`: same as `make test` at seed; meaningful once code lands

Phase 1+ targets (planned, not yet implemented):
- `make diagnostics-smoke`: laptop-friendly smoke pass `[OPEN: resolved at Phase 0-05]`
- `make canonical-eval`: full eval matrix via runpod-deploy `[OPEN: resolved at Phase 0-08]`

## Environment

Python `>=3.10` (pinned at Phase 0-08; see `pyproject.toml`). Load-bearing dependencies pinned at Phase 0:

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

`[OPEN: reproducibility tier; resolved at Phase 0-07]` — Phase 0 decides whether canonical numbers are reproducible from laptop-only (smoke) or require GPU rental (canonical-eval). Default if unsure: both — laptop-only smoke + a one-shot `make canonical-eval` that documents the GPU class + expected runtime + expected cost.

## Cross-references

- `Makefile` — canonical commands
- `pyproject.toml` — dependency declarations + tool configs
- `docs/MANIFEST_SCHEMA.md` — eval-output schema
- `.github/workflows/ci.yml` — CI gate definitions
- `SPEC_GREENFIELD.md` decision ledger §Submission row "Reproducibility tier"
