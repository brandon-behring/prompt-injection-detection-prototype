"""Phase 4 MDE primitives per ADR-006 + ADR-046 Q4 (Commit 2).

MDE (minimum detectable effect) wraps any upstream CI half-width into a
detectable-effect figure at (alpha=0.05, power=0.8) by default per ADR-006.

Both the paired-CI and marginal-CI paths delegate to
`eval_toolkit.bootstrap.mde_from_ci` (eval-toolkit v0.34.0 generalized the
signature to accept `BootstrapCI | PairedBootstrapCI` — closes upstream
issue #20). Project glue is the `MDECellModel` schema wrapping that
carries cell metadata (rung_a/rung_b, slice_name, source_ci_kind) the
upstream primitive doesn't track.

Library-first
-------------
- `eval_toolkit.bootstrap.mde_from_ci` covers BOTH the paired path AND
  the marginal-CI path as of v0.34.0 (single Union'd entry point).
"""

from __future__ import annotations

from typing import Literal

from eval_toolkit.bootstrap import (
    BootstrapCI,
    MDEEstimate,
    PairedBootstrapCI,
    mde_from_ci,
)

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
    """MDE from a marginal-CI half-width via eval-toolkit `mde_from_ci`.

    eval-toolkit v0.34.0 generalized `mde_from_ci` to accept
    `BootstrapCI | PairedBootstrapCI` (closes upstream #20). This wrapper
    constructs a synthetic `BootstrapCI` from the (ci_lo, ci_hi) inputs +
    delegates to the upstream primitive — no math here; just the schema-
    wrapping into `MDECellModel`.

    ``n`` is sentinel -1 if unknown (matches eval-toolkit MDEEstimate.n
    convention when the source arrays are unavailable). The synthetic
    BootstrapCI's `point_estimate` is set to the CI midpoint (informational
    only; the MDE formula only uses ci_lo/ci_hi/confidence).
    """
    if ci_hi <= ci_lo:
        raise ValueError(f"Require ci_hi > ci_lo; got ci_lo={ci_lo}, ci_hi={ci_hi}")

    ci = BootstrapCI(
        point_estimate=(ci_lo + ci_hi) / 2.0,
        ci_low=ci_lo,
        ci_high=ci_hi,
        confidence=0.95,
        n_resamples=1,  # informational; not used by mde_from_ci
        method=source_ci_kind,
    )
    est = mde_from_ci(ci, alpha=alpha, power=power)
    halfwidth = (ci_hi - ci_lo) / 2.0
    return MDECellModel(
        rung_a=rung,
        rung_b=None,
        slice_name=slice_name,
        metric=metric,
        source_ci_kind=source_ci_kind,
        ci_halfwidth=halfwidth,
        alpha=alpha,
        power=power,
        mde=float(est.mde),
        n=n,
    )
