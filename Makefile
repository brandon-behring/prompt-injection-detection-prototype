.PHONY: install install-all test test-unit test-smoke test-integration test-all smoke lint format coverage audit headline-dry-run headline-cloud eval-from-hub site site-preview clean \
        data-pin-manifest data-prepare data-fetch data-dedup data-splits data-audit \
        data-templates data-dedup-holdout data-dedup-prelabel data-dedup-calibrate

install:
	uv sync --extra dev

install-all:
	uv sync --all-extras

test: test-unit

test-unit:
	uv run pytest -m unit -q

test-smoke:
	uv run pytest -m smoke -q

test-integration:
	uv run pytest -m integration -q

test-all:
	uv run pytest -q

# `make smoke` — laptop-only, no GPU, no network, <10 min total (per ADR-027).
# Phase 0 close: equivalent to test-smoke until configs/profiles/fixtures.yaml lands at Phase 1.
# Phase 1+ extension: `uv run python scripts/run_metrics_battery.py --config configs/profiles/fixtures.yaml --output evals/smoke/results.json`.
smoke: test-smoke

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy --strict .

format:
	uv run ruff check --fix .
	uv run ruff format .

# `make coverage` — 70% flat coverage floor enforced (per ADR-028).
# Co-locked process — coverage gaps better addressed upstream get filed at the
# upstream repo per `decisions/upstream_issues.md` with `[test-coverage-gap]` tag,
# not absorbed as low-value local tests.
coverage:
	uv run pytest --cov --cov-fail-under=70 --cov-report=term-missing

audit:
	uv run python scripts/regenerate_audit.py --check

# `make headline-dry-run` — cost preview without provisioning (per ADR-027 + ADR-020).
# Placeholder until `configs/runpod/headline.yaml` lands at Phase 1.
headline-dry-run:
	@echo "[headline-dry-run] placeholder — implement at Phase 1 entry per ADR-027 + ADR-020"
	@echo "[headline-dry-run] expected wiring: runpod-deploy validate --all && runpod-deploy run --dry-run --config configs/runpod/headline.yaml"

# `make headline-cloud` — canonical evaluation deliverable (per ADR-027 + ADR-020).
# NOT a test target. Cost-cap-gated at \$$125/job per ADR-020 + A-002.
# Placeholder until `configs/runpod/headline.yaml` lands at Phase 1.
headline-cloud:
	@echo "[headline-cloud] placeholder — implement at Phase 1 entry per ADR-027 + ADR-020"
	@echo "[headline-cloud] expected wiring: runpod-deploy validate --all && runpod-deploy run --dry-run --config configs/runpod/headline.yaml && interactive-approval && runpod-deploy run --config configs/runpod/headline.yaml"

# `make eval-from-hub RUNG=<name>` — T0 reproducibility tier (per ADR-034).
# Downloads a published BBehring/prompt-injection-<rung-name> checkpoint per ADR-032
# and runs eval-only against the data slate. Verifies headline scores reproduce
# without re-training. Laptop-compatible (CPU-feasible eval).
# Placeholder until `scripts/eval_from_hub.py` lands at Phase 3.
eval-from-hub:
	@if [ -z "$(RUNG)" ]; then echo "ERROR: RUNG=<rung-name> required (e.g., make eval-from-hub RUNG=modernbert-lora)"; exit 2; fi
	@echo "[eval-from-hub] placeholder — implement at Phase 3 entry per ADR-034"
	@echo "[eval-from-hub] expected wiring: uv run python scripts/eval_from_hub.py --rung $(RUNG) --output results/predictions/eval-from-hub__$(RUNG).parquet"

# `make site` — render the Quarto HTML site to _site/ (per ADR-030).
# Local render only; CI publishes to GH Pages on tag push via .github/workflows/publish.yml.
site:
	quarto render

# `make site-preview` — live-reload dev server for local Quarto preview.
site-preview:
	quarto preview

clean:
	rm -rf .ruff_cache .mypy_cache .pytest_cache build dist *.egg-info __pycache__ _site .quarto

# ---------------------------------------------------------------------------
# Phase 1 (Data) targets — per ADR-016 + ADR-041 Q7 + ADR-043 leakage cleanup.
# Source secrets via .env.local (HF_TOKEN gates: hackaprompt, lmsys-chat-1m).
# ---------------------------------------------------------------------------

# `make data-pin-manifest` — live-fetch HF + GitHub SHAs; write configs/data/source_manifest.yaml
# (per ADR-041 Q2 + ADR-044 Q2 relocation). Idempotent — schema-drift detection rewrites on field changes.
data-pin-manifest:
	uv run python scripts/pin_source_manifest.py

# `make data-prepare` — canonical Phase 1 umbrella per ADR-041 Q7.
# Loads 11 sources + within-source dedup + cross-source LMSYS-priority dedup
# + LODO k=4 x 3 seeds splits + ADR-043 post-split leakage cleanup +
# materialize 36 parquets + 36 index masks + data_audit/leakage_report/
# contamination_scan JSONs. Wall-clock ~10 min after HF caches warm.
data-prepare:
	uv run python scripts/run_data_pipeline.py

# ADR-041 Q7 originally proposed 4 granular targets (data-fetch, data-dedup,
# data-splits, data-audit). The actual implementation went monolithic via
# run_data_pipeline.py because intermediate parquet materialization would add
# disk + complexity without benefit at the ~10-min wall-clock. Granular partial
# re-runs are a future-work axis (--from-stage / --to-stage flags). For now,
# these targets all delegate to data-prepare; the names are preserved for
# ADR-041 Q7 backward-compat and operator muscle memory.
data-fetch: data-prepare
data-dedup: data-prepare
data-splits: data-prepare
data-audit: data-prepare

# `make data-templates` — extract ~200 successful-injection templates from
# HackAPrompt for contamination corpus (per ADR-041 Q6).
data-templates:
	uv run python scripts/extract_hackaprompt_templates.py

# `make data-dedup-holdout` — generate 50 stratified-cosine-band candidate pairs
# for dedup threshold calibration (per ADR-041 Q5). Writes data/dedup_holdout.jsonl.
data-dedup-holdout:
	uv run python scripts/build_dedup_holdout.py

# `make data-dedup-prelabel` — LLM-judge pre-label the 50 holdout pairs via
# gpt-4o-2024-08-06 (per ADR-042). Requires OPENAI_API_KEY in env.
data-dedup-prelabel:
	uv run python scripts/llm_prelabel_dedup_holdout.py

# `make data-dedup-calibrate` — read labeled holdout; compute FPR + FNR + sensitivity
# table at {0.75, 0.80, 0.85}; write evals/dedup_calibration.json.
data-dedup-calibrate:
	uv run python scripts/calibrate_dedup.py
