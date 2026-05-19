---
adr_id: "056"
slug: binary-calibrator-refactor-and-platt-beta-narrow-supersession-of-adr-023
title: Calibration battery refactor to eval-toolkit `_binary` API + Platt + Beta calibrators landed — narrow supersession of ADR-023 "temperature + isotonic only" scope deferral
date: 2026-05-19
status: Accepted
claim_id: CLAIM-056
claim: >-
  ADR-023 §Decision deferred Platt + Beta calibrators as out-of-scope
  ("temperature + isotonic suffice for the audit") because eval-toolkit
  didn't ship them in scalar-prob form at v0.31.0 lock time. v0.40.0
  shipped `fit_platt_binary` + `fit_beta_binary` (eval-toolkit#43; filed
  v1.0.6; closed v1.0.8 within ~17 min of filing). v1.0.8 lands the full
  4-calibrator binary battery (temperature + isotonic + Platt + Beta)
  uniformly on the eval-toolkit `_binary` API family with the canonical
  `(params_tuple, apply)` return shape. The `src/eval/calibration_battery.py`
  refactor: (a) replaces `fit_temperature(val_logprobs, y_val)` (multi-class
  log-prob API; what we missed at earlier pin bumps) with
  `fit_temperature_binary(y_true, y_score)` (v0.35.0; scalar-prob sibling);
  (b) adds `fit_platt_binary` + `fit_beta_binary` (v0.40.0); (c) wraps
  `fit_isotonic_calibrator` in local adapter `fit_isotonic_binary_local`
  returning `(None, apply)` for shape consistency until eval-toolkit#44
  ships native `fit_isotonic_binary`; (d) deletes hand-rolled
  `proba_to_logprobs` + `apply_temperature` helpers (now duplicated by
  upstream's internal apply callable); (e) extends `CalibratorBundle`
  NamedTuple with `platt_params`, `test_scores_platt`, `beta_params`,
  `test_scores_beta` fields.
source: transcripts/2026-05-19__phase-13-pypi-install-and-platt-beta.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.0.8 close, `src/eval/calibration_battery.py` imports
  `fit_temperature_binary` + `fit_platt_binary` + `fit_beta_binary` from
  `eval_toolkit.calibration`; `fit_temperature` (multi-class) not imported;
  `proba_to_logprobs` + `apply_temperature` deleted from the module.
  `CalibratorBundle` NamedTuple has 7 fields (temperature_T +
  test_scores_temperature + test_scores_isotonic + platt_params +
  test_scores_platt + beta_params + test_scores_beta). 7/7 smoke tests in
  `tests/smoke/test_calibration_battery_smoke.py` pass (proba_to_logprobs
  + apply_temperature tests removed; new
  `test_fit_and_apply_calibrators_returns_bundle_with_4_calibrators`
  added). Local `fit_isotonic_binary_local` adapter present + removal
  trigger documented (when eval-toolkit#44 ships). 167/167 broader smoke
  suite green (171 - 4 deleted = 167). ADR-023 frontmatter `superseded_by`
  updated to `["056"]` in-place per ADR-029 convention.
closing_commit: v1.0.8
supersedes: [ADR-023]
superseded_by: []
references:
  - https://github.com/brandon-behring/eval-toolkit/releases/tag/v0.40.0
  - https://github.com/brandon-behring/eval-toolkit/issues/43
  - https://github.com/brandon-behring/eval-toolkit/issues/44
  - https://github.com/Microsoft/calibration/Kull-2017-Beta-calibration  # paper reference
transcript: transcripts/2026-05-19__phase-13-pypi-install-and-platt-beta.md
---

# ADR-056 — Binary calibrator refactor + Platt + Beta landed (narrow supersession of ADR-023)

## Status

Accepted (2026-05-19; landed in v1.0.8 alongside ADR-055 PyPI switch
+ ADR-057 manifest backfill).

## Context

[ADR-023](ADR-023-calibration-battery-and-interventions.md) (Phase 0-04) locked the
calibration battery to **temperature + isotonic** + ECE 4-variant
matrix + Brier + reliability curves. Platt scaling + Beta calibration
were considered but deferred — at our v0.31.0 pin time, eval-toolkit's
upstream scalar-prob binary calibrator family was incomplete: only
`fit_temperature_binary` (v0.35.0+; we missed it then bumped past) and
the multi-shape `fit_*_calibrator` family (`fit_platt_calibrator` +
`fit_beta_calibrator` exist but return non-canonical shapes like bare
`Callable` or `PlattFit` dataclass). The deferral was the library-first
correct call.

**v0.40.0 (2026-05-18)** shipped `fit_platt_binary` + `fit_beta_binary`
per [eval-toolkit#43](https://github.com/brandon-behring/eval-toolkit/issues/43)
(filed by us at v1.0.6; closed ~17 min after filing — fastest upstream
turnaround of the v1.0.x series). Both adopt the canonical
`(params_tuple, apply)` return shape matching `fit_temperature_binary`.
This completes 3 of 4 binary scalar-prob calibrators on the canonical
shape; `fit_isotonic_binary` is the remaining gap, filed at v1.0.8 as
[eval-toolkit#44](https://github.com/brandon-behring/eval-toolkit/issues/44).

**Diagnosis of our prior miss**: `src/eval/calibration_battery.py`
used `fit_temperature(val_logprobs, y_val)` — the multi-class
log-prob API. We constructed a 2-column log-prob array via local
helper `proba_to_logprobs` then called the multi-class fitter. This
was correct numerically but used the wrong upstream API: `fit_temperature_binary`
(v0.35.0+) takes scalar `y_score` directly + handles the log-prob
conversion internally. We caught this gap during the v1.0.8 preliminary
analysis.

## Decision

**Refactor `src/eval/calibration_battery.py` to use the eval-toolkit
`_binary` API family uniformly across all 4 calibrators**:

| Calibrator | v1.0.7 API (deleted) | v1.0.8 API (canonical) |
|---|---|---|
| Temperature | `fit_temperature(val_logprobs, y_val)` → `dict[str, float]` | `fit_temperature_binary(y_true, y_score)` → `(float, apply)` |
| Isotonic | `fit_isotonic_calibrator(y_true, y_score)` → `Callable` | Local `fit_isotonic_binary_local` → `(None, apply)` (adapter pending #44) |
| Platt | (NOT IMPLEMENTED) | `fit_platt_binary(y_true, y_score)` → `((a, b), apply)` |
| Beta | (NOT IMPLEMENTED) | `fit_beta_binary(y_true, y_score)` → `((a, b, c), apply)` |

All 4 calibrators share signature `(y_true, y_score) → (params_tuple, apply_callable)`,
enabling uniform iteration in consumer code (e.g., the v1.0.7 notebook
03_calibration could iterate the 4-calibrator dict for reliability-quartet
rendering at v1.0.9+).

**Extensions to `CalibratorBundle` NamedTuple**:

```python
class CalibratorBundle(NamedTuple):
    temperature_T: float
    test_scores_temperature: NDArray[np.float64]
    test_scores_isotonic: NDArray[np.float64]
    platt_params: tuple[float, float]           # NEW v1.0.8
    test_scores_platt: NDArray[np.float64]      # NEW v1.0.8
    beta_params: tuple[float, float, float]     # NEW v1.0.8
    test_scores_beta: NDArray[np.float64]       # NEW v1.0.8
```

**Deletions** (no-orphaned-code invariant per project memory):

- `proba_to_logprobs(p)` — converted scalar prob to 2-column log-prob;
  duplicated upstream `fit_temperature_binary`'s internal conversion.
- `apply_temperature(p, T)` — applied temperature to scalar prob;
  duplicated upstream's `apply` callable returned by `fit_temperature_binary`.
- 4 test functions in `tests/smoke/test_calibration_battery_smoke.py`
  that exercised the deleted helpers (`test_proba_to_logprobs_*` +
  `test_apply_temperature_*`).

**Library-first adapter for isotonic** (`fit_isotonic_binary_local`):

```python
def fit_isotonic_binary_local(y_true, y_score):
    """Local shape-adapter; removed when eval-toolkit#44 lands."""
    apply = fit_isotonic_calibrator(y_true, y_score)
    return (None, apply)
```

`(None, apply)` shape mirrors `(params_tuple, apply)` of the other 3
calibrators; isotonic is non-parametric (no params to introspect),
so `None` is explicit. **Removal trigger**: upstream eval-toolkit#44
ships + we bump the pin (likely v1.0.9 or v1.1.0).

## Consequences

### Positive

- **4-calibrator binary battery landed**. ADR-023's original Platt +
  Beta deferral is now closed via library-first consumption (not local
  hand-roll).
- **Consistent API shape across calibrators** — uniform `(params, apply)`
  return enables iterate-the-4-calibrator-dict consumer patterns
  (RunManifest logging, reliability-quartet rendering at v1.0.9+).
- **Library-first invariant honored**: 3 of 4 calibrators from eval-toolkit
  upstream; 1 local adapter for the remaining gap (with upstream
  issue filed + removal trigger documented).
- **Code surface shrunk by ~60 lines**: `proba_to_logprobs` (23 lines)
  + `apply_temperature` (28 lines) + 4 helper-tests deleted.
- **NEXT_STEPS §1.4 closed** at v1.0.8 ("Status: closed via Platt + Beta
  upstream consume + _binary refactor").

### Negative

- **In-place edit on ADR-023 frontmatter** — `superseded_by: [056]`
  added. Per ADR-029 immutability convention; body unchanged.
- **CalibratorBundle field count grew 3 → 7** — downstream consumers
  (currently only `calibration_battery_for_cell` at line 282) need
  updating. Smoke test `test_fit_and_apply_calibrators_returns_bundle_*`
  updated to cover all 7 fields.
- **Local adapter `fit_isotonic_binary_local` introduces a deletion-
  target obligation** — when eval-toolkit#44 ships, we must remove
  the adapter (per upstream_issues.md removal trigger).

### Neutral

- **Numeric output stability**: `fit_temperature_binary` is documented
  as a thin wrapper over the same underlying multi-class fitter as
  `fit_temperature` (per upstream v0.35.0 changelog). Smoke-tested
  `test_fit_and_apply_calibrators_temperature_improves_or_holds_ece`
  passes on the synthetic miscalibrated data; full numerical parity
  verification would require running canonical calibration_battery
  against canonical val slice on actual rung predictions — out of scope
  for v1.0.8 (no canonical regen; just refactor of the fitter API).
- **ADR-023's ECE 4-variant matrix + Brier decomposition + reliability
  curves** all preserved unchanged. Only the calibrator-fitter source
  changes.

## Alternatives Considered

### A. Keep `fit_temperature` (multi-class API); add Platt + Beta on new API

Heterogeneous calibrator matrix. **Rejected** per preliminary-analysis
discussion: inconsistent API shapes would require a glue layer in
calibration_battery.py and confuse future contributors. Refactor cost
is ~30 min more than additive add; consistency benefits compound.

### B. Don't add Platt + Beta; honor ADR-023's original deferral

Keep the calibration battery at 2 calibrators (temperature + isotonic).
**Rejected**: NEXT_STEPS §1.4 explicitly listed Platt + Beta as
tactical close items; eval-toolkit#43 was filed for upstream consume;
the v0.40.0 ship makes the deferral artificial. Path 3 calls for
closure.

### C. Implement Platt + Beta locally (not library-first)

Hand-roll Platt + Beta in `src/eval/calibration_battery.py`. **Rejected**:
violates library-first invariant. eval-toolkit#43 was the correct
file-first move; upstream resolved in ~17 min.

### D. Defer the temperature API refactor; add Platt + Beta only

Add Platt + Beta on the new API without refactoring temperature.
**Rejected** per the preliminary-analysis discussion (Option B in
batch 11 Q3): inconsistent matrix; consumer would need shape-glue.
The refactor is ~30 min extra for full consistency.

## Links

- [ADR-023 — Calibration battery design](ADR-023-calibration-battery-and-interventions.md) — narrowly superseded on the "Platt + Beta deferred" sub-decision only; ECE + Brier + reliability curve + temperature + isotonic + validation-only-fitting all preserved.
- [ADR-055 — eval-toolkit PyPI install](ADR-055-eval-toolkit-pypi-install-narrow-supersession-of-adr-036.md) — enabled the v0.40.0 bump that made Platt + Beta available.
- [eval-toolkit#43](https://github.com/brandon-behring/eval-toolkit/issues/43) — Platt + Beta request (filed v1.0.6; closed v1.0.8 in 17 min).
- [eval-toolkit#44](https://github.com/brandon-behring/eval-toolkit/issues/44) — `fit_isotonic_binary` request (filed v1.0.8; consume when shipped).
- [Kull, Silva Filho, Flach 2017](https://proceedings.mlr.press/v54/kull17a/kull17a.pdf) — Beta calibration paper.
- [Platt 1999](https://www.researchgate.net/publication/2594015_Probabilistic_Outputs_for_Support_Vector_Machines_and_Comparisons_to_Regularized_Likelihood_Methods) — original Platt scaling paper.
