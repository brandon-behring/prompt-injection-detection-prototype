.PHONY: install install-all test test-unit test-smoke test-integration test-all smoke lint format coverage audit headline-dry-run headline-cloud eval-from-hub site site-preview clean \
        data-pin-manifest data-prepare data-fetch data-dedup data-splits data-audit \
        data-templates data-dedup-holdout data-dedup-prelabel data-dedup-calibrate \
        generate-fixtures train-classical-floor train-rung cost-rollup cost-rollup-check \
        headline-frozen-probe headline-lora headline-full-ft \
        eval-classical-floor eval-reference-scorers-free eval-reference-scorers-paid \
        metrics-battery dual-policy-thresholds bootstrap-battery

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
# Phase 2 wiring per ADR-044 Q7 + Phase 3 wiring per ADR-045 Commit 6: runs
# pytest -m smoke (covers ~80+ tests across data + training + Phase 3 eval
# + scoring + scripts) plus a classical-floor fixture-pipeline pass plus an
# end-to-end metrics-battery pass over the fixture predictions (verifies
# Phase 3 eval orchestration wires through). Transformer trainers are
# exercised structurally via mocks; full GPU-backed runs are canonical via
# headline-{frozen-probe,lora,full-ft}.
smoke: test-smoke
	uv run python scripts/train_classical_floor.py \
		--config configs/profiles/classical_fixtures.yaml \
		--processed-root tests/fixtures/processed \
		--predictions-root tests/fixtures/predictions \
		--fold-only 0 --seed-only 42
	uv run python scripts/run_metrics_battery.py \
		--predictions-root tests/fixtures/predictions \
		--metrics-out tests/fixtures/metrics/per_cell.parquet
	uv run python scripts/eval_from_hub.py --rung lora --dry-run

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
# Phase 2 wiring per ADR-044 Q6: dry-runs all 3 per-rung configs.
headline-dry-run:
	runpod-deploy validate --config configs/runpod/headline-frozen_probe.yaml --all
	runpod-deploy validate --config configs/runpod/headline-lora.yaml --all
	runpod-deploy validate --config configs/runpod/headline-full_ft.yaml --all
	runpod-deploy run --dry-run --config configs/runpod/headline-frozen_probe.yaml
	runpod-deploy run --dry-run --config configs/runpod/headline-lora.yaml
	runpod-deploy run --dry-run --config configs/runpod/headline-full_ft.yaml

# `make headline-cloud` — Phase 2 umbrella. Fires all 3 transformer rungs in
# sequence (frozen-probe → lora → full-ft) per ADR-044 Q6. Each gated by its
# own interactive approval. Use headline-{rung} targets for per-rung control.
headline-cloud: headline-frozen-probe headline-lora headline-full-ft

# `make eval-from-hub RUNG=<name>` — T0 reproducibility tier (per ADR-034).
# Downloads a published BBehring/prompt-injection-<rung-name> checkpoint per ADR-032
# and runs eval-only against the data slate. Verifies headline scores reproduce
# without re-training. Laptop-compatible (CPU-feasible eval).
# Phase 3 wiring per ADR-045 Commit 5; full body gated on Phase 5 ADR-032 publication.
eval-from-hub:
	@if [ -z "$(RUNG)" ]; then echo "ERROR: RUNG=<rung-name> required (e.g., make eval-from-hub RUNG=lora)"; exit 2; fi
	uv run python scripts/eval_from_hub.py --rung $(RUNG)

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

# ---------------------------------------------------------------------------
# Phase 2 (Training) targets — per ADR-015 + ADR-017 + ADR-019 + ADR-020 + ADR-044.
# Source secrets via .env.local (HF_TOKEN gates ModernBERT-base download).
# ---------------------------------------------------------------------------

# `make generate-fixtures` — regenerate tests/fixtures/processed/* parquets
# (per ADR-027 + ADR-044 Q7). Idempotent (seeded by 1337).
generate-fixtures:
	uv run python scripts/generate_fixtures.py

# `make train-classical-floor` — train all 12 (fold, seed) cells of the
# TF-IDF + LR classical-floor rung locally on CPU (per ADR-017 + ADR-044 Q6).
# Wall-clock ~5 min; near-zero cost. Reads configs/rungs/classical_floor.yaml.
train-classical-floor:
	uv run python scripts/train_classical_floor.py

# `make train-rung RUNG=<frozen_probe|lora|full_ft>` — train one transformer
# rung's 12 (fold, seed) cells (per ADR-019 + ADR-044 Q5 + Q6).
# Intended for cloud runs via runpod-deploy; local GPU OK for debugging.
# For canonical headline runs use `make headline-<rung>` (cost-cap gated).
train-rung:
	@if [ -z "$(RUNG)" ]; then echo "ERROR: RUNG=<frozen_probe|lora|full_ft> required"; exit 2; fi
	uv run python scripts/train_rung.py --rung $(RUNG)

# `make cost-rollup` — aggregate artifacts/runpod/*/runpod_deploy_pull_manifest.json
# files plus evals/audit/llm_judge_cache/*.json into evals/cost_ledger.csv
# (per ADR-020 dual-layer cost cap discipline).
cost-rollup:
	uv run python scripts/cost_rollup.py

# `make cost-rollup-check` — fail exit 1 if cumulative spend > $200 hard cap
# (CI-gated per ADR-020 + ADR-044 Q6).
cost-rollup-check:
	uv run python scripts/cost_rollup.py --check

# `make headline-frozen-probe` — canonical frozen-probe rung run on RunPod
# (per ADR-020 + ADR-044 Q6). Cost-cap $40/pod. Interactive-approval gated.
headline-frozen-probe:
	runpod-deploy validate --config configs/runpod/headline-frozen_probe.yaml --all
	runpod-deploy run --dry-run --config configs/runpod/headline-frozen_probe.yaml
	@read -p "Approve frozen-probe canonical run (cap \$$40)? [y/N] " ans && [ "$$ans" = "y" ] || exit 1
	runpod-deploy run --config configs/runpod/headline-frozen_probe.yaml

# `make headline-lora` — canonical LoRA rung run on RunPod. Cost-cap $60/pod.
headline-lora:
	runpod-deploy validate --config configs/runpod/headline-lora.yaml --all
	runpod-deploy run --dry-run --config configs/runpod/headline-lora.yaml
	@read -p "Approve LoRA canonical run (cap \$$60)? [y/N] " ans && [ "$$ans" = "y" ] || exit 1
	runpod-deploy run --config configs/runpod/headline-lora.yaml

# `make headline-full-ft` — canonical full-FT rung run on RunPod. Cost-cap $100/pod.
headline-full-ft:
	runpod-deploy validate --config configs/runpod/headline-full_ft.yaml --all
	runpod-deploy run --dry-run --config configs/runpod/headline-full_ft.yaml
	@read -p "Approve full-FT canonical run (cap \$$100)? [y/N] " ans && [ "$$ans" = "y" ] || exit 1
	runpod-deploy run --config configs/runpod/headline-full_ft.yaml

# ---------------------------------------------------------------------------
# Phase 3 (Evaluation) targets — per ADR-018 + ADR-021 + ADR-022 + ADR-023 +
# ADR-024 + ADR-025 + ADR-034 + ADR-045.
# Tier A reference scorers (ProtectAI v1+v2) are CI-safe (free local HF).
# Tier B reference scorers (LLM judges) are cost-cap-gated (paid APIs;
# interactive approval per ADR-045 Q4).
# ---------------------------------------------------------------------------

# `make eval-classical-floor` — run the classical-floor end-to-end eval against
# Phase 1 splits (or fixtures via --processed-root override). Operator-friendly
# convenience target combining trainer + metrics battery.
eval-classical-floor:
	uv run python scripts/train_classical_floor.py
	uv run python scripts/run_metrics_battery.py --rung-pattern tfidf-lr

# `make eval-reference-scorers-free` — Tier A reference scorers (ProtectAI v1+v2);
# free local HF inference; safe for CI per ADR-045 Q4.
# Placeholder until the cost-cap-gated dispatcher script (Commit 5+ follow-up) lands.
eval-reference-scorers-free:
	@echo "[eval-reference-scorers-free] Tier A (ProtectAI v1+v2; free local HF inference)"
	@echo "[eval-reference-scorers-free] uv run python -c \"from src.scoring.protectai import ProtectAIScorer; ...\""
	@echo "[eval-reference-scorers-free] Phase 3 scaffolding present; full dispatcher deferred to Phase 4 wiring"

# `make eval-reference-scorers-paid` — Tier B reference scorers (OpenAI + Anthropic
# LLM judges); paid APIs; cost-cap-gated with interactive approval per ADR-045 Q4 +
# ADR-020 dual-layer cost cap. Requires OPENAI_API_KEY + ANTHROPIC_API_KEY env vars.
eval-reference-scorers-paid:
	@echo "[eval-reference-scorers-paid] Tier B (gpt-4o-2024-08-06 + claude-sonnet-4-6 LLM judges)"
	@echo "[eval-reference-scorers-paid] Estimated cost: ~\$$12 per A-002 envelope (LLM judge ~\$$0.005 x ~5K rows x 2 judges)"
	@read -p "Approve paid-API reference-scorer eval? [y/N] " ans && [ "$$ans" = "y" ] || exit 1
	@echo "[eval-reference-scorers-paid] Phase 3 scaffolding present; full dispatcher deferred to Phase 4 wiring"

# `make metrics-battery` — sweep (rung, fold, seed, slice) over predictions
# parquets; emit MetricsRecordModel + pooled-OOD rows per ADR-021. Reads
# evals/predictions/; writes evals/metrics/per_cell.parquet.
metrics-battery:
	uv run python scripts/run_metrics_battery.py

# `make dual-policy-thresholds` — fit detection (FPR ≤ 1%) + verification
# (recall ≥ 99%) operating points per-(trained_rung, fold, seed) on val per
# ADR-025. Emits OperatingPointModel parquet + ReachabilityAuditModel nested-
# JSON per A-009.
dual-policy-thresholds:
	uv run python scripts/fit_dual_policy_thresholds.py

# `make bootstrap-battery` — full-pairwise paired-bootstrap CI per ADR-022
# (defaults to n=10000 @ seed=1 headline; rerun with --seed 2 for stability
# check). Persistence is full-pairwise per ADR-045 Q6 so post-hoc questions
# answer from disk without rerunning.
bootstrap-battery:
	uv run python scripts/run_bootstrap_battery.py
