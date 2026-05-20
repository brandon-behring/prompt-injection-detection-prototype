---
adr_id: "027"
slug: smoke-vs-canonical-execution-context-stratification
title: Smoke vs canonical separation — three Makefile targets stratified by execution context
date: 2026-05-16
status: Accepted
claim_id: CLAIM-027
claim: Phase 0-06 locks the §5 Code architecture ledger row 349 (Smoke vs canonical separation) at three Makefile targets stratified by execution context. (1) make smoke runs pytest -m smoke + a fixture-data end-to-end pass through scripts/run_metrics_battery.py with configs/profiles/fixtures.yaml — laptop only, no GPU, no network, less than 10 minutes total. (2) make test-integration runs pytest -m integration — GPU-aware (uses CUDA via torch.cuda.is_available() if present, skips gracefully via pytest.importorskip and pytest.mark.skipif if not) — same target serves two execution contexts — local-GPU developer-workstation debugging AND cloud-pod pre-flight smoke check before paying for the canonical run. (3) make headline-cloud wraps runpod-deploy validate --all then runpod-deploy run --dry-run then runpod-deploy run --config configs/runpod/headline.yaml — RunPod-billed canonical evaluation deliverable, cost-cap-gated per ADR-020. The first two are tests (verification of glue + orchestration); the third is the actual evaluation deliverable, NOT a test. Math-rigor production-grade testing (Hypothesis property tests, golden-output snapshots) lives upstream in eval-toolkit (where the math implementations live and where the foundational-library-rigor 90% coverage floor applies); this repo's test layer is debugging-grade by design — sufficient to catch breakage before paying for cloud time, not sufficient to substitute for upstream library validation. This honest framing is documented in WRITEUP/methodology.md so reviewers do not interpret debugging-grade local tests as production-grade methodology validation. Smoke fixture data lives at tests/fixtures/ (not data/) to keep fixture-vs-real separation visible. A separate make headline-dry-run target exposes runpod-deploy run --dry-run standalone for cost preview without provisioning. Cost-cap discipline per A-002 (per-job soft cap $125; project-wide hard cap $200) gates the headline-cloud target via pre-flight validate-all check.
source: SPEC_GREENFIELD.md §5 Code architecture ledger row 349 + Phase 0-06 walk Q2
acceptance_criterion: SPEC_GREENFIELD ledger row 349 carries locked-to-three-makefile-targets-stratified-by-execution-context status (see ADR-027); SPEC_SHEET §6 Code architecture gains a "Smoke vs canonical separation" subsection enumerating the three targets with their execution-context bindings + the honest debugging-grade framing; SPEC_SHEET §6 acceptance criteria mention reproducibility via documented commands gets explicit pointer to make smoke (fast verification) + make headline-cloud (canonical reproduction); Makefile gains placeholder targets for headline-dry-run and headline-cloud (placeholder = echo + exit 0 until configs/runpod/headline.yaml lands at Phase 1; the existing test-smoke and test-integration targets are ratified as locked); STYLE.md gains a "Test rigor scope" subsection documenting the debugging-grade-here-rigorous-upstream split (per Q2 framing); WRITEUP/methodology.md (Phase 5 deliverable) is required to contain the same debugging-grade-vs-upstream framing paragraph so reviewers cannot interpret local test coverage as production-grade methodology validation; tests/test_invariants.py contains skip-marked stub test_smoke_target_completes_under_ten_minutes asserting that make smoke completes in under 10 minutes wall-clock on laptop without GPU + does not require network access (verified via subprocess timeout and network-disabled environment) and skip-marked stub test_integration_gpu_aware_skip asserting that pytest -m integration tests use pytest.importorskip("torch") and pytest.mark.skipif(not torch.cuda.is_available()) idiom rather than failing on no-GPU laptops.
closing_commit: fa1ad33
references:
  - https://github.com/brandon-behring/eval-toolkit/blob/main/Makefile
  - https://github.com/brandon-behring/runpod-deploy
  - https://docs.pytest.org/en/stable/how-to/skipping.html
  - decisions/ADR-013-kit-ratify-bulk-strictness-intake-notebook-persistence.md
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md
  - decisions/ADR-026-module-layout-concern-grouped-subpackages.md
  - decisions/library_imports.md
transcript: transcripts/2026-05-16__phase-0-06__code-test-discipline.md
---

# ADR-027: Smoke vs canonical separation — three Makefile targets stratified by execution context

## Status

Accepted (2026-05-16). Closes the second of 4 [OPEN] rows in Phase 0-06 (§5 Code architecture + §STYLE — rows 348-351 of SPEC_GREENFIELD ledger). Companion to ADR-026 (module layout), ADR-028 (coverage floor), and ADR-029 (test marker strategy).

## Context

SPEC_GREENFIELD §5 says smoke must run in less than 10 minutes on a laptop without GPU; canonical must reproduce headline numbers from a published config. The boundary determines what a reviewer can verify locally vs needs cloud access for. SPEC §6 says "a stranger can clone, install, and reproduce headline numbers via documented commands." Three options were considered for the surface that separates the two:

(A) **Single profile-switched target** — `make eval PROFILE={fixtures|full}`. One CLI surface; profile flag selects config. Hides the cost asymmetry (`PROFILE=full` typo on laptop = OOM crash + potential billed call); reviewer reading the Makefile must grok profile system before knowing which is cheap.

(B) **Two distinct targets** (`make smoke`, `make headline-cloud`) — spec default. Visual cost asymmetry; matches existing partial Makefile state; matches eval-toolkit Makefile precedent.

(C) **Three tiers** (laptop smoke / CPU full / GPU canonical) — gives reviewer a third middle option for reference-rung-only reproduction. Three configs to maintain; `full-cpu` is a half-measure that doesn't reproduce headline numbers.

User feedback at decision time reframed the question:

> "This is a prototype, not a production deployment. The golden-evals and thorough testing should be done in eval-toolkit where the math work resides. Smoke tests here and lightweight integration tests using the local GPU are useful for debugging as well as on the cloud GPU for smoke tests, but we are not claiming to have a rigorous deployment."

This reframing decouples three things that the original three options conflated:

1. **Math-rigor production-grade testing** (Hypothesis property tests, golden-output snapshots, ≥90% coverage on math kernels) belongs upstream in eval-toolkit where the math implementations live. Re-doing it here would duplicate work AND mislead reviewers into thinking this repo's test layer validates math correctness.
2. **Debugging-grade local testing** (smoke + lightweight integration) belongs here. Sufficient to catch breakage before paying for cloud time.
3. **Canonical evaluation orchestration** (the actual headline-cloud run) is a separate concept from testing. It is the deliverable, not a verification of the deliverable. Its Makefile target wraps runpod-deploy primitives but is not part of the test taxonomy.

The reframing produces a stratified-by-execution-context variant of (B): three targets but only two are tests.

## Decision

### Three Makefile targets, stratified by execution context

| Target | Execution context | Compute | Network | Wall-clock budget | Purpose |
|---|---|---|---|---|---|
| `make smoke` | laptop only | no GPU | no network | less than 10 min | dev debugging + reviewer "does this wire together" check |
| `make test-integration` | local GPU OR cloud pod | GPU when available; skip gracefully when not | optional | less than ~10 min | dev debugging on workstation GPU; pre-flight smoke on cloud pod before headline-cloud |
| `make headline-cloud` | RunPod (billed) | H100/equivalent per ADR-020 gpu_order failover | required | hours; cost-cap-gated at $125/job per ADR-020 + A-002 | **canonical evaluation deliverable** — not a test |

### Target details

#### `make smoke` (already partially implemented — `test-smoke` target exists)

```
test-smoke:
    uv run pytest -m smoke -q
```

To be augmented at Phase 1 with a fixture-data end-to-end pass:

```
smoke: test-smoke
    uv run python scripts/run_metrics_battery.py \
        --config configs/profiles/fixtures.yaml \
        --output evals/smoke/results.json
```

**Constraints**:

- No GPU dependencies (must execute on a laptop with `torch` available but no CUDA device).
- No network calls (fixture data lives in `tests/fixtures/`; HF dataset SHAs not fetched in smoke; LLM-judge calls mocked).
- Total wall-clock ≤ 10 min on a laptop (target ~5 min).

#### `make test-integration` (already partially implemented — `test-integration` target exists)

```
test-integration:
    uv run pytest -m integration -q
```

**GPU-awareness pattern** (the integration tests themselves):

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

**Dual execution contexts**:

- **Locally on developer workstation GPU**: `make test-integration` runs the GPU tests if a CUDA device is available; skips them otherwise. Useful for debugging trained-rung paths without paying for cloud time.
- **On cloud pod as pre-flight smoke**: same `make test-integration` invocation runs as part of the cloud pod startup sequence, before `make headline-cloud` proceeds. Validates that the cloud env (CUDA driver, flash-attn fallback recipe per ADR-020, HF cache, secrets injection) works end-to-end on the rented hardware before billing the canonical run.

#### `make headline-cloud` (placeholder target until Phase 1 lands `configs/runpod/headline.yaml`)

```
headline-cloud:
    runpod-deploy validate --all
    runpod-deploy run --dry-run --config configs/runpod/headline.yaml
    @read -p "Approve canonical run? [y/N] " ans && [ "$$ans" = "y" ] || exit 1
    runpod-deploy run --config configs/runpod/headline.yaml
```

**Cost-cap discipline** (per ADR-020 + A-002):

- `validate --all` enforces preflight schema + DC reachability + GPU stock check before any billing.
- `--dry-run` produces cost preview without provisioning (hits runpodctl + GraphQL pricing).
- Interactive approval gate prevents accidental invocation.
- `pod.gpu_order` 8-class failover ladder + `budget.cost_cap_usd=125` per `configs/runpod/headline.yaml` per ADR-020.

#### `make headline-dry-run` (placeholder target until Phase 1)

Standalone cost preview without the canonical run:

```
headline-dry-run:
    runpod-deploy validate --all
    runpod-deploy run --dry-run --config configs/runpod/headline.yaml
```

Useful pre-flight when revising the canonical config.

### Honest framing — debugging-grade here, rigorous upstream

WRITEUP/methodology.md (Phase 5 deliverable) is required to carry a paragraph documenting the testing-rigor split:

> "Math-correctness validation lives upstream in eval-toolkit (≥90% coverage floor, Hypothesis property tests, golden-output snapshots, doctests on math kernels). The local test layer in this prototype repo is debugging-grade — sufficient to catch glue-layer breakage and validate orchestration end-to-end before paying for cloud compute, not sufficient to substitute for upstream library validation. Reviewers should consult eval-toolkit's test suite for math-correctness evidence; this repo's test suite covers project-specific glue (data loaders, dedup calibration, reference-scorer adapters, threshold-fitting orchestrators)."

This honesty matters because the alternative (re-running upstream math tests here, or claiming our debugging-grade tests validate methodology) would either duplicate work or mislead reviewers about what was verified.

### Out-of-scope explicitly

- **Production-grade test rigor** in this repo (Hypothesis property tests, golden-output snapshots) — belongs upstream; if scope extends to production deployment, reopen via superseding ADR.
- **Re-implementation of upstream library tests** in this repo — anti-pattern (duplicates work, drifts from upstream, wastes review cycles).
- **A "full-CPU" middle tier** (Option C) — YAGNI for prototype; reference-rung-only ad-hoc reproduction is a curious-reviewer manual invocation, not a Makefile contract surface.

## Consequences

### Positive

- **Visual cost asymmetry preserved**: `make smoke` and `make test-integration` are obviously safe; `make headline-cloud` is obviously billed and gated by interactive approval.
- **Dual-execution-context integration tests get double duty**: same code, same Makefile target — runs locally for dev iteration AND on cloud pod for pre-flight smoke. No per-context boilerplate.
- **Honest framing kills the "did your tests prove methodology correctness" reviewer question**: WRITEUP/methodology.md paragraph defuses it upfront.
- **Existing Makefile targets ratified**: `test-smoke` and `test-integration` are unchanged; only `headline-cloud` + `headline-dry-run` need adding (as placeholders until Phase 1 produces `configs/runpod/headline.yaml`).

### Negative

- **`make smoke` cannot validate trained-rung numbers** — model weights too large for laptop, training requires GPU. Smoke validates glue and orchestration only.
- **`make test-integration` requires `torch` at install time** even on CPU-only laptops (for the `pytest.importorskip` to succeed; tests skip after that). Acceptable cost — `torch` is a project dependency anyway.
- **Cost-cap pre-flight depends on runpod-deploy** being available locally before invocation; CI cannot run `make headline-cloud` (by design — canonical runs are operator-initiated, not CI-triggered).

### Limitation

The 10-minute smoke budget and ~10-minute integration budget are empirical caps. If Phase 1 reveals smoke creeps to 15 min or integration to 30 min, reopen via ADR with the actual data. The caps are heuristics for reviewer-friendly fast-iteration loops, not load-bearing methodological commitments.

### Extension condition for revisit

If scope extends to production deployment (currently out-of-scope per the user reframing at decision time), add the production-grade test tier via superseding ADR — likely Hypothesis property tests on project-specific math (if any exists at that point) and golden-output snapshots for the canonical headline JSON shape.

## Alternatives considered

- **(A) Single profile-switched target** — rejected; hides cost asymmetry; typo-risk.
- **(B-as-stated) Two distinct targets without integration middle** — superseded by stratified-by-execution-context variant (this ADR); the integration tier is genuinely useful for both local debugging and cloud pre-flight.
- **(C) Three tiers with `full-cpu` middle** — rejected; YAGNI; reference-rung-only reproduction is ad-hoc, not a contract surface.
- **Rerun upstream math tests in this repo** — explicitly rejected per the user reframing; math rigor lives upstream where the math lives.
