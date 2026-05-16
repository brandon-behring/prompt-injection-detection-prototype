---
adr_id: "029"
slug: test-marker-strategy-four-marker-ratification
title: Test marker strategy — ratify 4-marker stratification (unit / smoke / integration / network)
date: 2026-05-16
status: Accepted
claim_id: CLAIM-029
claim: Phase 0-06 locks the §STYLE ledger row 351 (Test marker strategy) by ratifying the existing 4-marker stratification — unit, smoke, integration, network — already declared in pyproject.toml [tool.pytest.ini_options] markers list, mirrored in tests/conftest.py via pytest_configure addinivalue_line calls, and documented in STYLE.md project-deltas section. --strict-markers is enabled in pyproject addopts so unknown markers fail loudly. Marker semantics — unit (fast, deterministic, no IO, no GPU, no network, less than 1 second per test typical); smoke (end-to-end fixture-data pass through real code paths, less than 10 minutes total, no GPU, no network); integration (exercises real external dependencies — GPU, HF Hub, RunPod — may skip via pytest.importorskip or pytest.mark.skipif on laptops without GPU per ADR-027 dual-execution-context pattern); network (strictly requires network access — HF Hub fetch, runpod-deploy GraphQL — skipped in offline CI). property and golden markers are explicitly NOT added — they belong upstream in eval-toolkit per ADR-027 debugging-grade-here-rigorous-upstream split. slow marker explicitly NOT added — smoke already plays this role for end-to-end tests; if a unit test ever creeps over 30 seconds, that is a code-smell the marker should not paper over. gpu sub-marker explicitly NOT added — pytest.importorskip("torch") plus pytest.mark.skipif(not torch.cuda.is_available()) is the standard idiom and handles the local-vs-cloud dual-execution case cleanly without taxonomy proliferation. Limitation — the 4-marker strata do not capture every cross-cutting concern; the discipline relies on conditional-skip idioms within a marker. Extension conditions — add gpu sub-marker if conditional skipif boilerplate exceeds approximately 5 tests; add slow if any unit test crosses 30 seconds; add property only if scope extends to writing project-specific math primitives (currently out-of-scope; math lives upstream). Adding or removing a marker post-lock requires a superseding ADR.
source: SPEC_GREENFIELD.md §STYLE ledger row 351 + STYLE.md "project deltas" + pyproject.toml [tool.pytest.ini_options] + tests/conftest.py + Phase 0-06 walk Q4
acceptance_criterion: SPEC_GREENFIELD ledger row 351 carries locked-to-four-marker-ratification status (see ADR-029); STYLE.md project-deltas section "Test markers" bullet is preserved as-locked (no edit needed — already correct); pyproject.toml [tool.pytest.ini_options] markers list and tests/conftest.py pytest_configure addinivalue_line calls remain in sync (already in sync at ADR-029 entry); tests/test_invariants.py contains skip-marked stub test_pytest_markers_registered_and_in_sync asserting that (1) pyproject.toml [tool.pytest.ini_options] declares exactly the 4 markers (unit, smoke, integration, network) — set equality check; (2) tests/conftest.py pytest_configure registers exactly the same 4 markers via addinivalue_line; (3) --strict-markers is enabled in addopts; (4) no test file uses an unregistered marker (verified via grep of @pytest.mark.* in tests/ + comparison against the registered set); test_marker_semantics_unit_no_io stub asserting that pytest -m unit tests do not perform network requests or GPU calls — verified via socket-blocking + cuda.is_available-mocked pytest run; SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit: TBD
references:
  - https://docs.pytest.org/en/stable/how-to/mark.html
  - https://docs.pytest.org/en/stable/how-to/skipping.html
  - https://github.com/brandon-behring/eval-toolkit/blob/main/STYLE.md
  - decisions/ADR-026-module-layout-concern-grouped-subpackages.md
  - decisions/ADR-027-smoke-vs-canonical-execution-context-stratification.md
  - decisions/ADR-028-coverage-floor-70pct-with-upstream-issue-filing.md
transcript: transcripts/2026-05-16__phase-0-06__code-test-discipline.md
---

# ADR-029: Test marker strategy — ratify 4-marker stratification

## Status

Accepted (2026-05-16). Closes the fourth and final [OPEN] row in Phase 0-06 (§5 Code architecture + §STYLE — rows 348-351 of SPEC_GREENFIELD ledger). Companion to ADR-026 (module layout), ADR-027 (smoke vs canonical), and ADR-028 (coverage floor).

## Context

pytest markers (`@pytest.mark.unit`, `@pytest.mark.smoke`, etc.) let the suite be sliced by intent — `pytest -m unit` runs only fast deterministic tests; `pytest -m integration` runs GPU/network-dependent ones. Markers must be registered (in `conftest.py` or `pyproject.toml`) for `--strict-markers` to allow them; unregistered markers fail loudly.

The current state of the marker taxonomy is provisional but consistent across three artefacts:

- `pyproject.toml [tool.pytest.ini_options]` registers `unit`, `smoke`, `integration`, `network` (4 markers) with `addopts = "-v --tb=short --strict-markers"`.
- `tests/conftest.py` mirrors the same 4 markers via `pytest_configure` + `addinivalue_line` calls.
- `STYLE.md` "project deltas" section documents the 4-marker stratification.

The Q2 reframing (per ADR-027) — "math rigor lives upstream in eval-toolkit; here is debugging-grade" — pre-decides that `golden` and `property` markers should NOT be added here. They belong upstream where the math implementations and their golden contracts live.

Five options were considered:

(A) **Ratify existing 4 markers** — zero churn; honors ADR-027 framing.

(B) **4 + slow** (5 markers) — adds `slow` for tests >30s. Redundant with `smoke` (smoke is already "~5min, end-to-end").

(C) **3 markers (drop network)** — simplifies by removing currently-unused marker. Wastes an ADR cycle when first network-dependent test lands at Phase 1.

(D) **4 + gpu** (5 markers) — separates CUDA from generic integration. Marker proliferation; `pytest.importorskip` + `skipif` idiom handles it without a marker.

(E) **5 markers with both gpu and network** — hybrid of A and D. Same proliferation cost as D.

## Decision

### Locked marker taxonomy — exactly 4 markers

| Marker | Registered location | Semantics | Wall-clock target | Allowed external deps |
|---|---|---|---|---|
| `unit` | pyproject + conftest | fast, deterministic, no IO | < 1 sec/test | none |
| `smoke` | pyproject + conftest | end-to-end fixture-data pass | < 10 min total | none (no GPU, no network) |
| `integration` | pyproject + conftest | exercises real external deps; may skip via importorskip/skipif | ~5-10 min | GPU, HF Hub, RunPod (per pre-flight per ADR-027) |
| `network` | pyproject + conftest | strictly requires network access | varies | network only (HF Hub fetch, runpod-deploy GraphQL) |

### `--strict-markers` enabled

Already enabled in `pyproject.toml [tool.pytest.ini_options] addopts = "-v --tb=short --strict-markers"`. Unknown markers fail loudly — prevents typos like `@pytest.mark.itegration` from silently registering as a new marker.

### Two-source registration (pyproject + conftest)

Both `pyproject.toml` AND `tests/conftest.py` register the markers. Reasons:

- **pyproject is canonical** (read by pytest at config time; visible to PEP-621-aware tools).
- **conftest mirrors for IDE discoverability** (PyCharm + VS Code pytest integrations introspect `pytest_configure` calls; descriptions surface in the IDE marker dropdown).

The two MUST stay in sync — invariant test `test_pytest_markers_registered_and_in_sync` enforces.

### Markers explicitly NOT added (with rationale)

- **`property`**: Hypothesis property-based tests belong upstream in eval-toolkit (where math kernels live and where the strategy library `eval_toolkit` already uses Hypothesis with `hypothesis.extra.numpy`). Adding `property` here would either duplicate upstream tests or pretend project-specific math exists when it does not.
- **`golden`**: golden-output snapshot tests (where the output IS the contract) belong upstream — eval-toolkit uses `golden` for `docs.py` output. This repo has no docs-output contract surface; results.json is structural-but-not-byte-exact (per-row predictions vary by RNG seed).
- **`slow`**: redundant with `smoke` for end-to-end tests; if a `unit` test crosses 30s, that's a code-smell the marker should not paper over (the test should be re-classified as smoke or refactored).
- **`gpu`**: standard pattern below handles GPU-conditional skipping cleanly without taxonomy proliferation.

```python
import pytest
import torch

@pytest.mark.integration
def test_modernbert_load_on_gpu() -> None:
    pytest.importorskip("torch")
    if not torch.cuda.is_available():
        pytest.skip("GPU required")
    # ... actual test
```

If Phase 1 reveals chronic friction with this pattern (e.g., >5 tests need it), reopen via ADR to add `gpu` sub-marker.

### Marker-add or marker-remove protocol

Adding or removing a marker post-lock requires a superseding ADR with rationale (e.g., "Phase 1 produced 8 GPU-conditional tests; the importorskip+skipif boilerplate is paying real cost; adding `gpu` sub-marker"). Quietly editing `pyproject.toml` or `conftest.py` is an anti-pattern (the in-sync invariant test would catch it but the supersession-without-ADR pattern is what the SDD discipline forbids).

## Consequences

### Positive

- **Zero churn**: existing artefacts (`pyproject.toml`, `conftest.py`, `STYLE.md`, `Makefile` `test-unit`/`test-smoke`/`test-integration` targets) are already aligned with the locked taxonomy.
- **`--strict-markers` catches typos**: any `@pytest.mark.<typo>` fails loudly at test-collection time.
- **Aligns with ADR-027 framing**: math-correctness rigor (`property`, `golden`) explicitly stays upstream; this layer is debugging-grade.
- **Two-source registration matches IDE expectations** without sacrificing canonical pyproject declaration.

### Negative

- **`network` marker not currently used** at lock time — risk of dead-letter taxonomy. Mitigated by Phase 1 expectations: HF dataset SHA-pinning tests (per ADR-016) will land marked `network`.
- **No `gpu` sub-marker** means GPU-conditional tests carry the `importorskip` + `skipif` boilerplate. Acceptable cost for prototype scope; reopen if boilerplate proliferates.
- **`slow` absence** means a `unit` test that grows to 30s+ has nowhere to escape to without re-classification. Treated as a feature, not a bug.

### Limitation

The 4-marker strata do not capture every cross-cutting concern (no `slow`, no `gpu`, no `flaky`, no `property`). The discipline relies on `pytest.mark.skipif` + `pytest.importorskip` to handle conditional skipping within a marker. If this pattern produces verbose boilerplate at Phase 1 (~5+ tests), reopen via superseding ADR.

### Extension condition for revisit

- **`gpu` sub-marker**: if conditional `skipif(not torch.cuda.is_available())` boilerplate appears in 5+ tests.
- **`slow`**: if any `unit` test legitimately crosses 30s and cannot be split or re-marked as smoke.
- **`property`**: only if scope extends to writing project-specific math primitives (currently out-of-scope per ADR-027 prototype-grade framing; math kernels live upstream).
- **`flaky`**: only if Phase 1 reveals genuinely-flaky tests that cannot be made deterministic; preference is to fix the flakiness, not paper over with a marker.

## Alternatives considered

- **(B) 4 + slow** — rejected; redundant with `smoke`; absence is a feature.
- **(C) 3 markers (drop network)** — rejected; HF SHA-pin tests will need it at Phase 1; pre-registering avoids ADR-cycle waste.
- **(D) 4 + gpu** — rejected; standard `importorskip + skipif` idiom handles it; reopen if boilerplate proliferates.
- **(E) 5 with gpu + network** — rejected; same proliferation cost as D.
