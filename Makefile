.PHONY: install install-all test test-unit test-smoke test-integration test-all lint format coverage audit clean

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

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy --strict .

format:
	uv run ruff check --fix .
	uv run ruff format .

coverage:
	uv run pytest --cov=. --cov-report=term-missing

audit:
	uv run python scripts/regenerate_audit.py --check

clean:
	rm -rf .ruff_cache .mypy_cache .pytest_cache build dist *.egg-info __pycache__
