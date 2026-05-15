# Coding style — discipline pointer

Baseline coding style is taken from upstream `eval-toolkit` STYLE.md. Project deltas (places this repo intentionally differs) live below.

## Project deltas

- **Test coverage floor**: `[OPEN: coverage floor; resolved at Phase 0]`. eval-toolkit uses 90%; case-study composition layer typically doesn't need foundational-library rigor.
- **Doctest scope**: narrowed to public-API examples only (not for internal helpers).
- **Docstring scope**: public-API only. Internal functions need only a one-line summary; full Google-style docstrings reserved for public entry points.
- **Test markers**: stratified `unit / smoke / integration / network` (registered in `tests/conftest.py` + mirrored in `pyproject.toml [tool.pytest.ini_options]`). `--strict-markers` enabled so unknown markers fail loudly.
- **Line length**: 100 chars (per `pyproject.toml [tool.ruff]`). Diverges from PEP 8's 79; matches eval-toolkit + matches modern Python convention.

## Type discipline

- **mypy** strict mode (`--strict`). `make lint` enforces.
- Public APIs: full type hints required. Internal helpers: hints where they disambiguate.
- Dataclasses for `Config` / `Result` classes are `@dataclass(frozen=True, slots=True)`. Invariant test enforces (see `tests/test_invariants.py:test_config_result_classes_frozen_slotted`).

## Anti-style

- **No emoji** in source / docs. Invariant test enforces (`tests/test_invariants.py:test_no_emoji_in_repo`).
- **No hand-rolled equivalents** to eval-toolkit / runpod-deploy / research_toolkit primitives. Project-specific glue is allowed (see `SPEC_GREENFIELD.md` §Tech-Stack library-first rule + `decisions/library_imports.md`).

## For everything else

Defer to upstream eval-toolkit STYLE.md.
