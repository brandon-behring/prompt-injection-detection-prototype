"""Smoke tests for src/eval/mde.py (Phase 4 Commit 2 per ADR-046 Q4 + ADR-006)."""

from __future__ import annotations

import numpy as np
import pytest
from eval_toolkit.bootstrap import paired_bootstrap_diff
from eval_toolkit.metrics import pr_auc

from src.eval.mde import mde_from_marginal_ci_record, mde_from_paired_ci_record
from src.eval.schemas import MDECellModel


# --------------------------------------------------------------------------- #
# mde_from_paired_ci_record — eval-toolkit direct path
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_mde_from_paired_ci_record_schema_valid() -> None:
    """One paired-CI MDE roundtrips through MDECellModel."""
    rng = np.random.default_rng(0)
    n = 300
    y = rng.integers(0, 2, size=n).astype(np.int_)
    s_a = np.clip(y + rng.normal(0, 0.3, size=n), 0.001, 0.999)
    s_b = np.clip(y + rng.normal(0, 0.25, size=n), 0.001, 0.999)
    paired = paired_bootstrap_diff(y, s_a, s_b, metric=pr_auc, n_resamples=300, rng=1)
    cell = mde_from_paired_ci_record(
        paired,
        rung_a="rungA",
        rung_b="rungB",
        slice_name="iid",
        metric="auprc",
        source_ci_kind="paired_bootstrap",
    )
    assert isinstance(cell, MDECellModel)
    assert cell.source_ci_kind == "paired_bootstrap"
    assert cell.mde > 0.0
    assert cell.alpha == 0.05
    assert cell.power == 0.8
    assert cell.ci_halfwidth > 0.0


# --------------------------------------------------------------------------- #
# mde_from_marginal_ci_record — closed-form workaround per upstream #20
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_mde_from_marginal_ci_record_schema_valid() -> None:
    cell = mde_from_marginal_ci_record(
        rung="frozen_probe",
        slice_name="pooled_ood",
        metric="auprc",
        ci_lo=0.80,
        ci_hi=0.90,
        n=500,
    )
    assert isinstance(cell, MDECellModel)
    assert cell.rung_a == "frozen_probe"
    assert cell.rung_b is None
    assert cell.ci_halfwidth == pytest.approx(0.05)
    assert cell.mde > 0.0
    assert cell.n == 500


@pytest.mark.smoke
def test_mde_from_marginal_ci_record_rejects_invalid_alpha() -> None:
    with pytest.raises(ValueError, match="alpha"):
        mde_from_marginal_ci_record(
            rung="r", slice_name="s", metric="m", ci_lo=0.0, ci_hi=0.1, n=10, alpha=0.0
        )


@pytest.mark.smoke
def test_mde_from_marginal_ci_record_rejects_invalid_power() -> None:
    with pytest.raises(ValueError, match="power"):
        mde_from_marginal_ci_record(
            rung="r", slice_name="s", metric="m", ci_lo=0.0, ci_hi=0.1, n=10, power=1.5
        )


@pytest.mark.smoke
def test_mde_from_marginal_ci_record_rejects_zero_width() -> None:
    with pytest.raises(ValueError, match="ci_hi > ci_lo"):
        mde_from_marginal_ci_record(
            rung="r", slice_name="s", metric="m", ci_lo=0.5, ci_hi=0.5, n=10
        )


@pytest.mark.smoke
def test_mde_marginal_scales_linearly_with_halfwidth() -> None:
    """Doubling the CI half-width should double the MDE (sigma scales linearly)."""
    cell_a = mde_from_marginal_ci_record(
        rung="r", slice_name="s", metric="m", ci_lo=0.40, ci_hi=0.50, n=100
    )
    cell_b = mde_from_marginal_ci_record(
        rung="r", slice_name="s", metric="m", ci_lo=0.30, ci_hi=0.50, n=100
    )
    assert cell_b.mde == pytest.approx(2.0 * cell_a.mde, rel=1e-6)
