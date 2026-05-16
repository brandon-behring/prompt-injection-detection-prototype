# Coding style — discipline pointer

Baseline coding style is taken from upstream `eval-toolkit` STYLE.md. Project deltas (places this repo intentionally differs) live below.

## Project deltas

- **Test coverage floor**: 70% flat across the repo (per ADR-028). CI command — `uv run pytest --cov --cov-fail-under=70 --cov-report=term-missing`. Co-locked process commitment — coverage gaps better addressed by upstream library tests (eval-toolkit / runpod-deploy) get filed as upstream issues with `[test-coverage-gap]` tag in `decisions/upstream_issues.md` rather than absorbed as low-value local tests; gaps that genuinely cannot be filed upstream get either tested locally OR documented as `[not-applicable]` deferral. eval-toolkit uses 90% (foundational-library rigor); this repo's case-study composition layer is debugging-grade per ADR-027.
- **Doctest scope**: narrowed to public-API examples only (not for internal helpers).
- **Docstring scope**: public-API only. Internal functions need only a one-line summary; full Google-style docstrings reserved for public entry points.
- **Test markers**: 4-marker stratification — `unit / smoke / integration / network` (per ADR-029). Registered in BOTH `pyproject.toml [tool.pytest.ini_options]` AND `tests/conftest.py` via `pytest_configure` `addinivalue_line` calls (must stay in sync — invariant test enforces). `--strict-markers` enabled so unknown markers fail loudly. `property` and `golden` markers explicitly NOT added — they belong upstream in eval-toolkit (math rigor lives upstream per ADR-027). `slow` and `gpu` sub-markers explicitly NOT added — `smoke` covers end-to-end timing; `pytest.importorskip` + `pytest.mark.skipif(not torch.cuda.is_available())` handles GPU-conditional skipping. Marker-add or marker-remove post-lock requires superseding ADR.
- **Line length**: 100 chars (per `pyproject.toml [tool.ruff]`). Diverges from PEP 8's 79; matches eval-toolkit + matches modern Python convention.

## Test rigor scope

Math-correctness rigor (Hypothesis property tests, golden-output snapshots, doctests on math kernels, ≥90% coverage floor) lives upstream in `eval-toolkit` where the math implementations live. The local test layer in this repo is **debugging-grade** by design (per ADR-027) — sufficient to catch glue-layer breakage, validate orchestration end-to-end, and serve as cloud-pod pre-flight smoke before paying for canonical runs; **not** sufficient to substitute for upstream library validation. Reviewers should consult eval-toolkit's test suite for math-correctness evidence; this repo's tests cover project-specific glue (data loaders, dedup calibration, reference-scorer adapters, threshold-fitting orchestrators).

## Type discipline

- **mypy** strict mode (`--strict`). `make lint` enforces.
- Public APIs: full type hints required. Internal helpers: hints where they disambiguate.
- Dataclasses for `Config` / `Result` classes are `@dataclass(frozen=True, slots=True)`. Invariant test enforces (see `tests/test_invariants.py:test_config_result_classes_frozen_slotted`).

## Anti-style

- **No emoji** in source / docs. Invariant test enforces (`tests/test_invariants.py:test_no_emoji_in_repo`).
- **No hand-rolled equivalents** to eval-toolkit / runpod-deploy / research_toolkit primitives. Project-specific glue is allowed (see `SPEC_GREENFIELD.md` §Tech-Stack library-first rule + `decisions/library_imports.md`).

## For everything else

Defer to upstream eval-toolkit STYLE.md.
