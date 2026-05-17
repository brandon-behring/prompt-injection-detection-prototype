"""Phase 4 MDE primitives per ADR-006 + ADR-046 Q4 (Commit 2).

MDE (minimum detectable effect) wraps any upstream CI half-width into a
detectable-effect figure at (alpha=0.05, power=0.8) by default per ADR-006.

The paired-CI path delegates directly to `eval_toolkit.bootstrap.mde_from_ci`
which accepts a `PairedBootstrapCI`. The marginal-CI / cross-fold-CI path uses
the closed-form fallback below pending upstream eval-toolkit issue #20
(generalize `mde_from_ci` to accept `BootstrapCI | PairedBootstrapCI`).

Closed-form fallback derivation
-------------------------------
For a normal-distribution approximation of the CI:

    sigma = (ci_hi - ci_lo) / (2 * z_{alpha/2})

The standard two-sided MDE formula is then:

    MDE = (z_{alpha/2} + z_{beta}) * sigma

This matches the inner derivation of `eval_toolkit.bootstrap.mde_from_ci`
(same numerical formula); the upstream issue is API surface, not math.

Library-first
-------------
- `eval_toolkit.bootstrap.mde_from_ci` covers the paired path exactly.
- `scipy.stats.norm.ppf` supplies the quantile constants.
"""

from __future__ import annotations

from typing import Literal

from eval_toolkit.bootstrap import MDEEstimate, PairedBootstrapCI, mde_from_ci
from scipy.stats import norm

from src.eval.schemas import MDECellModel

SourceCIKind = Literal[
    "paired_bootstrap",
    "marginal_bootstrap",
    "cv_clt",
    "block_bootstrap",
    "paired_op_point",
    "paired_ece",
]


def mde_from_paired_ci_record(
    paired: PairedBootstrapCI,
    *,
    rung_a: str,
    rung_b: str,
    slice_name: str,
    metric: str,
    source_ci_kind: Literal[
        "paired_bootstrap", "paired_op_point", "paired_ece"
    ] = "paired_bootstrap",
    alpha: float = 0.05,
    power: float = 0.8,
) -> MDECellModel:
    """Wrap eval-toolkit MDE-from-paired-CI into the project MDECellModel schema."""
    est: MDEEstimate = mde_from_ci(paired, alpha=alpha, power=power)
    halfwidth = (float(paired.ci_high) - float(paired.ci_low)) / 2.0
    return MDECellModel(
        rung_a=rung_a,
        rung_b=rung_b,
        slice_name=slice_name,
        metric=metric,
        source_ci_kind=source_ci_kind,
        ci_halfwidth=halfwidth,
        alpha=alpha,
        power=power,
        mde=float(est.mde),
        n=int(est.n),
    )


def mde_from_marginal_ci_record(
    *,
    rung: str,
    slice_name: str,
    metric: str,
    ci_lo: float,
    ci_hi: float,
    n: int,
    source_ci_kind: Literal[
        "marginal_bootstrap", "cv_clt", "block_bootstrap"
    ] = "marginal_bootstrap",
    alpha: float = 0.05,
    power: float = 0.8,
) -> MDECellModel:
    """Closed-form MDE from a marginal-CI half-width.

    Workaround pending upstream eval-toolkit issue #20; the math is identical
    to `mde_from_ci`'s inner formula. ``n`` is sentinel -1 if unknown (matches
    eval-toolkit MDEEstimate.n convention when the source arrays are unavailable).
    """
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0, 1); got {alpha}")
    if not (0.0 < power < 1.0):
        raise ValueError(f"power must be in (0, 1); got {power}")
    if ci_hi <= ci_lo:
        raise ValueError(f"Require ci_hi > ci_lo; got ci_lo={ci_lo}, ci_hi={ci_hi}")

    z_alpha_half = float(norm.ppf(1.0 - alpha / 2.0))
    z_beta = float(norm.ppf(power))
    halfwidth = (ci_hi - ci_lo) / 2.0
    sigma = halfwidth / z_alpha_half
    mde = (z_alpha_half + z_beta) * sigma
    return MDECellModel(
        rung_a=rung,
        rung_b=None,
        slice_name=slice_name,
        metric=metric,
        source_ci_kind=source_ci_kind,
        ci_halfwidth=halfwidth,
        alpha=alpha,
        power=power,
        mde=mde,
        n=n,
    )
