# Code quality discipline

`[LOCKED]` discipline for this iteration. Concrete values populated at Phase 1; placeholders below mark the choices Phase 0 / Phase 1 must lock.

## Lint + format

- **Ruff** for lint + format. `make lint` runs `ruff check .` + `ruff format --check .`.
- `make format` runs `ruff check --fix .` + `ruff format .`.
- Line length: see `pyproject.toml [tool.ruff]`.

## Types

- **mypy** strict mode. `make lint` runs `mypy --strict .`.
- All public APIs have type hints. Internal functions: hints required where types disambiguate.

## Tests

- **pytest** with marker stratification (see `tests/conftest.py`): `unit`, `smoke`, `integration`, `network`.
- `make test-unit` runs the fast deterministic suite (always-on CI gate).
- `make test-smoke` runs end-to-end smoke (~5 min, opt-in CI gate).
- `make test-integration` runs network / GPU integration (workflow_dispatch only).
- Coverage floor: `[OPEN: coverage floor; resolved at Phase 0]` (see STYLE.md §coverage).

## Imports — library-first discipline

`[LOCKED]` Never hand-roll equivalents to `eval-toolkit`, `runpod-deploy`, or `research_toolkit` primitives. Project-specific glue (data loaders, custom scorers using upstream primitives) is allowed and expected. See `decisions/library_imports.md` for the running ledger.

## Commits

`[LOCKED]` Each meaningful work unit is its own commit. Type-prefixed messages (`feat:`, `refactor:`, `docs:`, `chore:`, `test:`, `fix:`, `seed:`). `Co-Authored-By: Claude <noreply@anthropic.com>` trailer. Reference `ADR-NNN` in commits that lock or supersede a Phase 0 decision. **No amend / no squash / no force-push** — fix-forward over history rewriting.

## Pre-commit hooks

See `.pre-commit-config.yaml`. Hooks include ruff, mypy, a no-emoji check, and a markdown-link sanity check. Run `pre-commit install` once after clone to activate locally; CI runs the same hooks as a hard gate.

## Invariant tests

See `tests/test_invariants.py`. Skip-marked stubs at seed; Phase 1 implements:

- Class balance per fold
- Source-disjoint train/test
- Hyperparameter immutability (config hash committed)
- Calibration honesty (val-only fits)
- Reporting completeness (severity-≥-medium assumptions appear in WRITEUP caveats)
- No-emoji (CJK / emoji unicode code points absent from source)
- Frozen dataclass for `Config` / `Result` classes
