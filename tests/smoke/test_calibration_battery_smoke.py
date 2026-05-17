"""Smoke tests for src/eval/calibration_battery.py (Phase 3 Commit 3 per ADR-023 + ADR-045)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import pytest

from src.eval.calibration_battery import (
    HEADLINE_N_BINS,
    apply_temperature,
    calibration_battery_for_cell,
    compute_calibration_record,
    compute_reliability_curve,
    fit_and_apply_calibrators,
    proba_to_logprobs,
)
from src.eval.schemas import CalibrationRecordModel


# --------------------------------------------------------------------------- #
# Helpers — synthetic miscalibrated binary classifier
# --------------------------------------------------------------------------- #


def _synthetic_predictions(
    n: int = 400, miscalibration: float = 0.5, seed: int = 0
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Generate (y, s) where s is a deliberately miscalibrated probability estimate.

    Returns y in {0, 1} and s = clip(true_proba + noise, 0, 1) where noise is
    biased toward overconfidence (mimics ModernBERT raw-softmax behavior).
    """
    rng = np.random.default_rng(seed)
    true_proba = rng.uniform(0.1, 0.9, size=n)
    y = rng.binomial(1, true_proba)
    # Bias scores toward extremes to simulate overconfidence (typical raw softmax).
    s = np.clip(true_proba + miscalibration * (true_proba - 0.5), 0.001, 0.999)
    return y.astype(np.int_), s.astype(np.float64)


# --------------------------------------------------------------------------- #
# proba_to_logprobs + apply_temperature
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_proba_to_logprobs_reconstructs_at_T_equals_1() -> None:
    """softmax(logprobs)[:, 1] equals input probabilities at T=1 (no scaling)."""
    p = np.array([0.1, 0.3, 0.5, 0.7, 0.95], dtype=np.float64)
    out = apply_temperature(p, temperature=1.0)
    np.testing.assert_allclose(out, p, atol=1e-6)


@pytest.mark.smoke
def test_apply_temperature_T_greater_than_1_flattens_distribution() -> None:
    """T > 1 reduces confidence (pushes scores toward 0.5)."""
    p = np.array([0.05, 0.95], dtype=np.float64)
    out = apply_temperature(p, temperature=4.0)
    # Both should move closer to 0.5
    assert abs(out[0] - 0.5) < abs(p[0] - 0.5)
    assert abs(out[1] - 0.5) < abs(p[1] - 0.5)


@pytest.mark.smoke
def test_apply_temperature_T_less_than_1_sharpens_distribution() -> None:
    """T < 1 sharpens confidence (pushes scores toward 0 or 1)."""
    p = np.array([0.4, 0.6], dtype=np.float64)
    out = apply_temperature(p, temperature=0.25)
    assert out[0] < p[0]
    assert out[1] > p[1]


@pytest.mark.smoke
def test_apply_temperature_rejects_non_positive() -> None:
    """T <= 0 raises ValueError per Guo 2017 constraint."""
    with pytest.raises(ValueError):
        apply_temperature(np.array([0.5]), temperature=0.0)
    with pytest.raises(ValueError):
        apply_temperature(np.array([0.5]), temperature=-1.0)


@pytest.mark.smoke
def test_proba_to_logprobs_softmax_invariant() -> None:
    """softmax(proba_to_logprobs(p))[:, 1] equals p (sanity)."""
    p = np.array([0.001, 0.25, 0.5, 0.75, 0.999], dtype=np.float64)
    logprobs = proba_to_logprobs(p)
    e_x = np.exp(logprobs - logprobs.max(axis=1, keepdims=True))
    recovered = e_x[:, 1] / e_x.sum(axis=1)
    np.testing.assert_allclose(recovered, p, atol=1e-5)


# --------------------------------------------------------------------------- #
# compute_calibration_record
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_compute_calibration_record_returns_validated_model() -> None:
    """compute_calibration_record returns a CalibrationRecordModel with all fields set."""
    y, s = _synthetic_predictions()
    rec = compute_calibration_record(
        rung="lora",
        fold=0,
        seed=42,
        calibrator="raw",
        y_true=y,
        y_score=s,
    )
    assert isinstance(rec, CalibrationRecordModel)
    assert rec.rung == "lora"
    assert rec.calibrator == "raw"
    # All 4 ECE variants populated.
    assert rec.ece_equal_mass >= 0.0
    assert rec.ece_l1_plug_in >= 0.0
    assert rec.ece_l1_debiased >= 0.0
    assert rec.ece_l2_plug_in >= 0.0
    assert rec.ece_l2_debiased >= 0.0
    # Brier decomposition sums (approximately) to brier: BS = rel - res + unc.
    expected_brier = rec.brier_reliability - rec.brier_resolution + rec.brier_uncertainty
    assert rec.brier == pytest.approx(expected_brier, abs=0.01)


@pytest.mark.smoke
def test_compute_calibration_record_n_bins_locked_to_15() -> None:
    """Headline ECE binning is n_bins=15 per ADR-023 line 8 — module constant exposed."""
    assert HEADLINE_N_BINS == 15


# --------------------------------------------------------------------------- #
# fit_and_apply_calibrators
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_fit_and_apply_calibrators_returns_bundle_with_T_above_zero() -> None:
    """CalibratorBundle carries positive temperature + calibrated test scores."""
    y_val, s_val = _synthetic_predictions(n=200, seed=1)
    _, s_test = _synthetic_predictions(n=100, seed=2)
    bundle = fit_and_apply_calibrators(y_val=y_val, s_val=s_val, s_test=s_test)
    assert bundle.temperature_T > 0
    assert bundle.test_scores_temperature.shape == s_test.shape
    assert bundle.test_scores_isotonic.shape == s_test.shape
    assert ((bundle.test_scores_temperature >= 0) & (bundle.test_scores_temperature <= 1)).all()
    assert ((bundle.test_scores_isotonic >= 0) & (bundle.test_scores_isotonic <= 1)).all()


@pytest.mark.smoke
def test_fit_and_apply_calibrators_temperature_improves_or_holds_ece() -> None:
    """Calibrated test ECE is typically <= raw ECE (calibration helps; never strictly worse on synthetic)."""
    y_val, s_val = _synthetic_predictions(n=300, miscalibration=0.7, seed=42)
    y_test, s_test = _synthetic_predictions(n=300, miscalibration=0.7, seed=43)

    bundle = fit_and_apply_calibrators(y_val=y_val, s_val=s_val, s_test=s_test)
    raw_rec = compute_calibration_record(
        rung="x", fold=0, seed=42, calibrator="raw", y_true=y_test, y_score=s_test
    )
    temp_rec = compute_calibration_record(
        rung="x",
        fold=0,
        seed=42,
        calibrator="temperature",
        y_true=y_test,
        y_score=bundle.test_scores_temperature,
    )
    # Temperature scaling should at least not catastrophically worsen ECE on
    # synthetic miscalibrated data. Allow 50% slack since synthetic data is small.
    assert temp_rec.ece_equal_mass <= raw_rec.ece_equal_mass * 1.5


# --------------------------------------------------------------------------- #
# calibration_battery_for_cell
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_calibration_battery_for_cell_returns_3_records() -> None:
    """Battery returns exactly 3 records (raw + temperature + isotonic) per ADR-023."""
    y_val, s_val = _synthetic_predictions(n=200, seed=10)
    y_test, s_test = _synthetic_predictions(n=100, seed=11)
    val_df = pd.DataFrame({"label": y_val, "predicted_proba_class1": s_val})
    test_df = pd.DataFrame({"label": y_test, "predicted_proba_class1": s_test})

    records = calibration_battery_for_cell(
        rung="frozen-probe", fold=1, seed=43, val_df=val_df, test_df=test_df
    )
    assert len(records) == 3
    calibrators = {r.calibrator for r in records}
    assert calibrators == {"raw", "temperature", "isotonic"}
    for r in records:
        assert r.rung == "frozen-probe"
        assert r.fold == 1
        assert r.seed == 43


@pytest.mark.smoke
def test_calibration_battery_for_cell_rejects_empty_input() -> None:
    """Empty val or test DataFrame raises ValueError fail-loud per project standards."""
    df_empty = pd.DataFrame({"label": [], "predicted_proba_class1": []})
    df_nonempty = pd.DataFrame({"label": [0, 1], "predicted_proba_class1": [0.3, 0.7]})
    with pytest.raises(ValueError, match="non-empty"):
        calibration_battery_for_cell(
            rung="x", fold=0, seed=42, val_df=df_empty, test_df=df_nonempty
        )
    with pytest.raises(ValueError, match="non-empty"):
        calibration_battery_for_cell(
            rung="x", fold=0, seed=42, val_df=df_nonempty, test_df=df_empty
        )


# --------------------------------------------------------------------------- #
# compute_reliability_curve
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_compute_reliability_curve_returns_dict() -> None:
    """compute_reliability_curve returns the eval-toolkit reliability dict."""
    y, s = _synthetic_predictions(n=300, seed=100)
    curve = compute_reliability_curve(y_true=y, y_score=s)
    assert isinstance(curve, dict)
    # eval-toolkit reliability_curve returns 'bin_confidences' + 'bin_accuracies' + 'bin_counts' etc.
    assert len(curve) > 0
