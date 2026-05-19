"""Phase 3 calibration battery per ADR-023 + ADR-045 Commit 3.

Headline (per ADR-023 line 8): ECE-equal-mass(n_bins=15, quantile binning) +
Brier on raw scores per rung. Spoke (per ADR-023 line 255-256): all 4 ECE
variants from eval-toolkit (L1/L2 × plug-in/debiased) + Brier decomposition
(reliability/resolution/uncertainty) + reliability diagrams + intervention
deltas (temperature scaling per Guo 2017 + isotonic regression per
Niculescu-Mizil & Caruana 2005); both calibrators fit on validation only
per-(rung, fold, seed) per ADR-011 Guarantee 6.

All eval-toolkit primitives used here are pinned at v0.31.0 per ADR-036
+ decisions/library_imports.md.

Public API
----------
- `compute_calibration_record(rung, fold, seed, calibrator, y_true, y_score)`
  -> CalibrationRecordModel: compute full ECE matrix + Brier + Brier
  decomposition for one (rung, fold, seed, calibrator) cell.
- `fit_and_apply_calibrators(y_val, s_val, s_test)` -> CalibratorBundle:
  fit temperature + isotonic on val; apply to test; return T plus
  calibrated test scores.
- `calibration_battery_for_cell(rung, fold, seed, val_df, test_df)`
  -> list[CalibrationRecordModel] of length 3 (raw + temperature + isotonic).
- `compute_reliability_curve(y_true, y_score)` -> dict for the spoke
  reliability diagrams.

Convention: this module operates on binary classification only (label in
{0, 1}, score = predicted_proba_class1 in [0, 1]); multi-class extension
is afterword scope per ADR-005 + SPEC §scope.
"""

from __future__ import annotations

from typing import Any, Final, Literal, NamedTuple

import numpy as np
import pandas as pd
from eval_toolkit.calibration import (
    fit_beta_binary,
    fit_isotonic_binary,
    fit_platt_binary,
    fit_temperature_binary,
    reliability_curve,
)
from eval_toolkit.metrics import (
    brier_decomposition,
    brier_score,
    expected_calibration_error,
    expected_calibration_error_debiased,
    expected_calibration_error_equal_mass,
    expected_calibration_error_l2,
    expected_calibration_error_l2_debiased,
)
from numpy.typing import NDArray

from src.eval.schemas import CalibrationRecordModel, CalibratorName

# Locked headline binning per ADR-023.
HEADLINE_N_BINS: Final[int] = 15


def compute_calibration_record(
    *,
    rung: str,
    fold: int,
    seed: int,
    calibrator: CalibratorName,
    y_true: NDArray[np.int_],
    y_score: NDArray[np.float64],
) -> CalibrationRecordModel:
    """Compute the full ADR-023 spoke battery for one (rung, fold, seed, calibrator) cell.

    Parameters
    ----------
    rung : str
        Rung identifier (e.g. "lora", "gpt-4o-2024-08-06").
    fold : int
        LODO fold or -1 for reference scorers.
    seed : int
        Training seed or -1 for reference scorers.
    calibrator : {"raw", "temperature", "isotonic"}
        Which calibrator's outputs `y_score` carries; raw = no calibration applied.
    y_true : numpy.ndarray
        Binary ground-truth labels in {0, 1}, shape (n,).
    y_score : numpy.ndarray
        Predicted (and possibly calibrator-applied) probabilities, shape (n,), in [0, 1].

    Returns
    -------
    CalibrationRecordModel
        Validated record carrying ECE 4-variant matrix + Brier + Brier decomposition.
    """
    y_score_arr = np.asarray(y_score, dtype=np.float64)
    y_true_arr = np.asarray(y_true, dtype=np.int_)

    ece_em = float(
        expected_calibration_error_equal_mass(y_true_arr, y_score_arr, n_bins=HEADLINE_N_BINS)
    )
    ece_l1_plug = float(expected_calibration_error(y_true_arr, y_score_arr, n_bins=HEADLINE_N_BINS))
    ece_l1_deb = float(
        expected_calibration_error_debiased(y_true_arr, y_score_arr, n_bins=HEADLINE_N_BINS)
    )
    ece_l2_plug = float(
        expected_calibration_error_l2(y_true_arr, y_score_arr, n_bins=HEADLINE_N_BINS)
    )
    ece_l2_deb = float(
        expected_calibration_error_l2_debiased(y_true_arr, y_score_arr, n_bins=HEADLINE_N_BINS)
    )

    brier_val_raw = brier_score(y_true_arr, y_score_arr)
    if not isinstance(brier_val_raw, (int, float)):
        raise TypeError(
            f"brier_score returned non-scalar {type(brier_val_raw).__name__} — "
            f"check empty_strategy handling"
        )
    brier_val = float(brier_val_raw)

    bd = brier_decomposition(y_true_arr, y_score_arr, n_bins=HEADLINE_N_BINS)

    return CalibrationRecordModel(
        rung=rung,
        fold=fold,
        seed=seed,
        calibrator=calibrator,
        ece_equal_mass=ece_em,
        ece_l1_plug_in=ece_l1_plug,
        ece_l1_debiased=ece_l1_deb,
        ece_l2_plug_in=ece_l2_plug,
        ece_l2_debiased=ece_l2_deb,
        brier=brier_val,
        brier_reliability=float(bd["reliability"]),
        brier_resolution=float(bd["resolution"]),
        brier_uncertainty=float(bd["uncertainty"]),
    )


class CalibratorBundle(NamedTuple):
    """Fitted 4-calibrator binary battery applied to test scores per ADR-023 + ADR-056.

    All 4 calibrators use the eval_toolkit `_binary` API family with the
    canonical ``(params_tuple, apply)`` return shape. Refactor landed at
    v1.0.8 (ADR-056 narrow supersession of ADR-023 "temperature + isotonic
    only" scope deferral).

    Fields
    ------
    temperature_T : float
        Fitted temperature from `fit_temperature_binary` (v0.35.0; scalar
        Guo-2017 temperature in (0, ∞]).
    test_scores_temperature : NDArray[np.float64]
        Temperature-calibrated test probabilities.
    test_scores_isotonic : NDArray[np.float64]
        Isotonic-regressed test probabilities (non-parametric; no params
        to expose).
    platt_params : tuple[float, float]
        `(a, b)` for Platt scaling sigmoid σ(a·s + b); v0.40.0
        `fit_platt_binary` per eval-toolkit#43.
    test_scores_platt : NDArray[np.float64]
        Platt-scaled test probabilities.
    beta_params : tuple[float, float, float]
        `(a, b, c)` for 3-parameter Kull-2017 Beta calibration; v0.40.0
        `fit_beta_binary` per eval-toolkit#43.
    test_scores_beta : NDArray[np.float64]
        Beta-calibrated test probabilities.
    """

    temperature_T: float
    test_scores_temperature: NDArray[np.float64]
    test_scores_isotonic: NDArray[np.float64]
    platt_params: tuple[float, float]
    test_scores_platt: NDArray[np.float64]
    beta_params: tuple[float, float, float]
    test_scores_beta: NDArray[np.float64]


def fit_and_apply_calibrators(
    *,
    y_val: NDArray[np.int_],
    s_val: NDArray[np.float64],
    s_test: NDArray[np.float64],
) -> CalibratorBundle:
    """Fit temperature + isotonic on validation; apply to test; return CalibratorBundle.

    Validation-only fit per ADR-011 Guarantee 6 + ADR-023 line 255. Test
    rows are NEVER seen by the calibrator-fit; the calibrator is applied
    to test scores after fit.

    Parameters
    ----------
    y_val : numpy.ndarray
        Validation binary labels in {0, 1}, shape (n_val,).
    s_val : numpy.ndarray
        Validation raw predicted probabilities, shape (n_val,), in [0, 1].
    s_test : numpy.ndarray
        Test raw predicted probabilities, shape (n_test,), in [0, 1].

    Returns
    -------
    CalibratorBundle
        Carries fitted temperature T plus calibrated test scores for both
        interventions.
    """
    y_val_arr = np.asarray(y_val, dtype=np.int_)
    s_val_arr = np.asarray(s_val, dtype=np.float64)
    s_test_arr = np.asarray(s_test, dtype=np.float64)

    # Library-first per ADR-005 + ADR-056 — all 4 calibrators on
    # eval_toolkit `_binary` API family with `(params_tuple, apply)` shape.
    temperature_T, apply_temp = fit_temperature_binary(y_val_arr, s_val_arr)
    test_scores_temperature = np.asarray(apply_temp(s_test_arr), dtype=np.float64)

    # Isotonic via upstream `fit_isotonic_binary` (v0.42.0 closes eval-toolkit#44).
    _, apply_iso = fit_isotonic_binary(y_val_arr, s_val_arr)
    test_scores_isotonic = np.asarray(apply_iso(s_test_arr), dtype=np.float64)

    # Platt (v0.40.0 NEW per eval-toolkit#43).
    platt_params, apply_platt = fit_platt_binary(y_val_arr, s_val_arr)
    test_scores_platt = np.asarray(apply_platt(s_test_arr), dtype=np.float64)

    # Beta (v0.40.0 NEW per eval-toolkit#43; 3-parameter Kull-2017 fit).
    beta_params, apply_beta = fit_beta_binary(y_val_arr, s_val_arr)
    test_scores_beta = np.asarray(apply_beta(s_test_arr), dtype=np.float64)

    return CalibratorBundle(
        temperature_T=float(temperature_T),
        test_scores_temperature=test_scores_temperature,
        test_scores_isotonic=test_scores_isotonic,
        platt_params=platt_params,
        test_scores_platt=test_scores_platt,
        beta_params=beta_params,
        test_scores_beta=test_scores_beta,
    )


def calibration_battery_for_cell(
    *,
    rung: str,
    fold: int,
    seed: int,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> list[CalibrationRecordModel]:
    """Run full battery (raw + temperature + isotonic) for one (rung, fold, seed) cell.

    Parameters
    ----------
    rung : str
        Rung identifier propagated to all 3 output records.
    fold : int
        LODO fold (0..3) or -1 for reference scorers.
    seed : int
        Training seed.
    val_df : pandas.DataFrame
        Validation predictions parquet rows; must carry "label" + "predicted_proba_class1".
    test_df : pandas.DataFrame
        Test predictions parquet rows; must carry "label" + "predicted_proba_class1".

    Returns
    -------
    list of CalibrationRecordModel
        Length 3: one record per calibrator (raw + temperature + isotonic).
    """
    if val_df.empty or test_df.empty:
        raise ValueError("calibration_battery_for_cell requires non-empty val_df + test_df")

    y_val = val_df["label"].to_numpy(dtype=np.int_)
    s_val = val_df["predicted_proba_class1"].to_numpy(dtype=np.float64)
    y_test = test_df["label"].to_numpy(dtype=np.int_)
    s_test = test_df["predicted_proba_class1"].to_numpy(dtype=np.float64)

    bundle = fit_and_apply_calibrators(y_val=y_val, s_val=s_val, s_test=s_test)

    # Explicit Literal-typed tuple list so mypy can verify CalibratorName conformance.
    cells: list[tuple[CalibratorName, NDArray[np.float64]]] = [
        ("raw", s_test),
        ("temperature", bundle.test_scores_temperature),
        ("isotonic", bundle.test_scores_isotonic),
    ]
    records: list[CalibrationRecordModel] = []
    for calibrator, scores in cells:
        records.append(
            compute_calibration_record(
                rung=rung,
                fold=fold,
                seed=seed,
                calibrator=calibrator,
                y_true=y_test,
                y_score=scores,
            )
        )
    return records


def compute_reliability_curve(
    *,
    y_true: NDArray[np.int_],
    y_score: NDArray[np.float64],
    n_bins: int = HEADLINE_N_BINS,
    strategy: Literal["uniform", "quantile"] = "quantile",
) -> dict[str, Any]:
    """Return reliability-curve dict from eval-toolkit for the spoke diagrams.

    Per ADR-023 line 255, equal-mass quantile binning matches the headline
    ECE-equal-mass convention so the diagrams are visually congruent with
    the headline metric.

    Parameters
    ----------
    y_true : numpy.ndarray
        Binary labels in {0, 1}.
    y_score : numpy.ndarray
        Predicted probabilities in [0, 1].
    n_bins : int
        Number of bins (default = HEADLINE_N_BINS).
    strategy : str
        "quantile" (default; equal-mass) or "uniform".

    Returns
    -------
    dict
        Reliability-curve dict from eval-toolkit (per-bin midpoints, accuracies,
        confidences, weights).
    """
    curve: dict[str, Any] = reliability_curve(
        np.asarray(y_true, dtype=np.int_),
        np.asarray(y_score, dtype=np.float64),
        n_bins=n_bins,
        strategy=strategy,
    )
    return curve
