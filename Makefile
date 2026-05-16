.PHONY: install install-all test test-unit test-smoke test-integration test-all smoke lint format coverage audit headline-dry-run headline-cloud eval-from-hub site site-preview clean

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
