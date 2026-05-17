"""Pydantic v2 schema contract for Phase 3 evaluation outputs (per ADR-045 Q7).

These models are the canonical contract that Phase 3 scoring + eval modules
serialize through. Every parquet + JSON written under `evals/predictions/`,
`evals/metrics/`, `evals/calibration/`, `evals/operating_points/`,
`evals/audit/verification_reachability.json`, and `evals/bootstrap/` is
validated against one of these models on read AND on write.

Per ADR-045 Q3, `PredictionsRowModel` is the cross-cutting contract that
unifies the trained-rung outputs (classical-floor + 3 ModernBERT rungs from
Phase 2) with the reference-scorer outputs (ProtectAI v1/v2 + 2 LLM judges
from Phase 3 Commit 2) so the downstream metric layer in Commits 3-5 is
scorer-agnostic.

Design rules
------------
- All models are `frozen=True` (immutable after construction) and
  `extra="forbid"` (unknown fields raise `ValidationError` — fail loud).
- Field constraints are expressed as Pydantic `Field(...)` validators
  rather than hand-rolled __post_init__ checks.
- Reference scorers (no LODO concept, deterministic) use sentinel
  `fold=-1, seed=-1`; trained rungs use actual integers.
- `epoch` is `int | None`: None for classical + reference, 1 or 2 for
  transformer rungs per ADR-019.
- `contamination_state` is a `Literal` of the 4 ADR-005 + ADR-018 taxonomy
  states; any new state requires superseding the ADR-005 taxonomy lock.

Used by
-------
- `src/scoring/{protectai, openai_judge, anthropic_judge}.py` (Commit 2) on
  write.
- `src/eval/{calibration_battery, operating_points, slice_analysis}.py`
  (Commits 3-4) on read.
- `scripts/{fit_dual_policy_thresholds, run_metrics_battery,
  run_bootstrap_battery, eval_from_hub}.py` (Commit 5) end-to-end.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ADR-005 + ADR-018 four-tier contamination taxonomy.
ContaminationState = Literal[
    "verified_disjoint",
    "backbone-partial-disjoint",
    "suspected_contamination",
    "vendor_black_box",
]

# ADR-025 dual-policy taxonomy.
PolicyName = Literal["detection", "verification"]

# ADR-023 calibrator taxonomy.
CalibratorName = Literal["raw", "temperature", "isotonic"]

# ADR-022 CI method taxonomy.
CIMethod = Literal["percentile", "bca"]


class PredictionsRowModel(BaseModel):
    """One row in a predictions parquet — the cross-scorer contract per ADR-045 Q3.

    Trained rungs (classical_floor + 3 ModernBERT rungs) have integer fold +
    seed; reference scorers (ProtectAI v1/v2 + LLM judges) use -1 sentinels
    because they have no LODO fold concept and are deterministic per ADR-018.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: str = Field(
        ..., min_length=1, description="Rung identifier (e.g. 'tfidf-lr', 'gpt-4o-2024-08-06')"
    )
    fold: int = Field(..., ge=-1, le=3, description="LODO fold 0..3, or -1 for reference scorers")
    seed: int = Field(
        ..., description="Training seed (42/43/44) or -1 for deterministic reference scorers"
    )
    epoch: int | None = Field(
        None, description="Transformer epoch (1 or 2); None for classical + reference"
    )
    row_idx_in_source: int = Field(..., ge=0)
    source: str = Field(..., min_length=1)
    text: str
    label: int = Field(..., ge=0, le=1, description="Binary ground truth: 0=benign, 1=positive")
    predicted_proba_class1: float = Field(..., ge=0.0, le=1.0)
    contamination_state: ContaminationState


class MetricsRecordModel(BaseModel):
    """Per-(rung, fold, seed, slice) metric record per ADR-021 + ADR-023.

    `slice` is "iid" or "pooled_ood" or one of the 5 named OOD slice names
    (notinject, xstest, jbb_behaviors, bipia, injecagent). Per ADR-021 the
    0.1% recall@FPR pinpoint is reported as None for any non-pooled slice
    (n_neg too small); the field is nullable to encode this honestly.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: str = Field(..., min_length=1)
    fold: int = Field(..., ge=-1, le=3)
    seed: int = Field(...)
    slice_name: str = Field(..., min_length=1)
    n_rows: int = Field(..., gt=0)
    n_positive: int = Field(..., ge=0)
    n_negative: int = Field(..., ge=0)
    auprc: float = Field(..., ge=0.0, le=1.0)
    auroc: float = Field(..., ge=0.0, le=1.0)
    recall_at_fpr_0_1: float | None = Field(
        None, ge=0.0, le=1.0, description="0.1% pinpoint; None when n_neg too small per ADR-021"
    )
    recall_at_fpr_1: float = Field(..., ge=0.0, le=1.0)
    recall_at_fpr_5: float = Field(..., ge=0.0, le=1.0)
    ece_equal_mass: float = Field(
        ..., ge=0.0, le=1.0, description="ECE-equal-mass(n_bins=15) per ADR-023 headline"
    )
    brier: float = Field(..., ge=0.0, le=1.0)


class SliceMetricsModel(BaseModel):
    """Per-(rung, slice) aggregated metric across folds × seeds per ADR-021 spoke.

    Aggregation is mean-of-(fold, seed) for trained rungs (12 obs per rung);
    mean-of-fold for reference scorers (4 obs per rung).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: str = Field(..., min_length=1)
    slice_name: str = Field(..., min_length=1)
    n_observations: int = Field(..., gt=0, description="Number of (fold, seed) obs aggregated")
    auprc_mean: float = Field(..., ge=0.0, le=1.0)
    auprc_ci_lo: float = Field(..., ge=0.0, le=1.0)
    auprc_ci_hi: float = Field(..., ge=0.0, le=1.0)
    auroc_mean: float = Field(..., ge=0.0, le=1.0)
    recall_at_fpr_1_mean: float = Field(..., ge=0.0, le=1.0)
    recall_at_fpr_5_mean: float = Field(..., ge=0.0, le=1.0)
    ece_equal_mass_mean: float = Field(..., ge=0.0, le=1.0)
    brier_mean: float = Field(..., ge=0.0, le=1.0)


class OperatingPointModel(BaseModel):
    """Per-(rung, fold, seed, policy) operating point per ADR-025 dual-policy.

    `policy="detection"` fits TargetFPRSelector(0.01); `policy="verification"`
    fits TargetRecallSelector(0.99). Both fit on validation only per ADR-011
    Guarantee 6. `target_reachable` distinguishes feasible vs fallback cells
    per A-009; only meaningful for verification policy (detection is trivially
    reachable at any FPR ≥ achievable_fpr_floor).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: str = Field(..., min_length=1)
    fold: int = Field(
        ..., ge=0, le=3, description="Trained rungs only per ADR-025; no reference scorers"
    )
    seed: int = Field(...)
    policy: PolicyName
    target_value: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="0.01 for detection (FPR target); 0.99 for verification (recall target)",
    )
    threshold: float = Field(..., ge=0.0, le=1.0)
    target_reachable: bool
    achieved_val_metric: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="achieved_val_fpr for detection; achieved_val_recall for verification",
    )
    achieved_test_recall: float = Field(..., ge=0.0, le=1.0)
    achieved_test_fpr: float = Field(..., ge=0.0, le=1.0)
    achieved_test_precision: float = Field(..., ge=0.0, le=1.0)


class CalibrationRecordModel(BaseModel):
    """Per-(rung, fold, seed, calibrator) calibration record per ADR-023.

    Headline columns: `ece_equal_mass` + `brier`. Spoke columns: full 4-ECE
    matrix (L1/L2 × plug-in/debiased) + Brier decomposition.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: str = Field(..., min_length=1)
    fold: int = Field(..., ge=-1, le=3)
    seed: int = Field(...)
    calibrator: CalibratorName
    ece_equal_mass: float = Field(..., ge=0.0, le=1.0)
    ece_l1_plug_in: float = Field(..., ge=0.0, le=1.0)
    ece_l1_debiased: float = Field(..., ge=0.0, le=1.0)
    ece_l2_plug_in: float = Field(..., ge=0.0, le=1.0)
    ece_l2_debiased: float = Field(..., ge=0.0, le=1.0)
    brier: float = Field(..., ge=0.0, le=1.0)
    brier_reliability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Per eval-toolkit brier_decomposition — calibration error component",
    )
    brier_resolution: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Per eval-toolkit brier_decomposition — discrimination component",
    )
    brier_uncertainty: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Per eval-toolkit brier_decomposition — base-rate variance component",
    )


class ReachabilityAuditModel(BaseModel):
    """Per-(rung, fold, seed) verification-target reachability per ADR-025 + A-009.

    Emitted to `evals/audit/verification_reachability.json`. Unreachable cells
    carry asterisks in the headline emit.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: str = Field(..., min_length=1)
    fold: int = Field(..., ge=0, le=3)
    seed: int = Field(...)
    target_reachable: bool
    target_recall: float = Field(default=0.99, ge=0.0, le=1.0)
    achieved_val_recall: float = Field(..., ge=0.0, le=1.0)
    fallback_threshold: float = Field(..., ge=0.0, le=1.0)
    fallback_test_fpr: float = Field(..., ge=0.0, le=1.0)


class BootstrapCellModel(BaseModel):
    """One paired-bootstrap cell per ADR-022 + ADR-045 Q6 full-pairwise persistence.

    With 4 rungs there are C(4,2) = 6 pairwise comparisons; with 5 OOD slices +
    IID + pooled_ood that becomes ~30+ cells per metric. All persisted to
    `evals/bootstrap/` per ADR-045 Q6 user refinement so post-hoc analysis can
    answer "what about X-vs-Y?" without re-running the bootstrap.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung_a: str = Field(..., min_length=1)
    rung_b: str = Field(..., min_length=1)
    slice_name: str = Field(..., min_length=1)
    metric: str = Field(
        ..., min_length=1, description="auprc, auroc, recall_at_fpr_1, ece_equal_mass, brier, etc."
    )
    n_resamples: int = Field(..., gt=0)
    seed: int = Field(
        ..., description="Bootstrap seed (1 = headline, 2 = stability check per ADR-022)"
    )
    point_estimate_a: float = Field(..., ge=0.0, le=1.0)
    point_estimate_b: float = Field(..., ge=0.0, le=1.0)
    point_estimate_diff: float = Field(..., description="b - a; sign indicates direction")
    ci_lo: float
    ci_hi: float
    ci_method: CIMethod


class MarginalBootstrapCellModel(BaseModel):
    """One per-(rung, slice, metric) marginal-bootstrap CI cell per ADR-022 + ADR-046 Q1 (Commit 2).

    Marginal CI (single-rung, no pairing) wraps `eval_toolkit.bootstrap.bootstrap_ci`.
    Per ADR-022, the headline protocol fires 10000 iterations at seed=1 and a stability
    check at 10000 iterations at seed=2; both seeds are persisted as separate cells so
    the stability-check half-width comparison is queryable from disk per ADR-013.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: str = Field(..., min_length=1)
    slice_name: str = Field(..., min_length=1)
    metric: str = Field(..., min_length=1)
    n_resamples: int = Field(..., gt=0)
    seed: int = Field(..., description="1=headline, 2=stability check per ADR-022")
    point_estimate: float = Field(..., ge=0.0, le=1.0)
    ci_lo: float = Field(..., ge=0.0, le=1.0)
    ci_hi: float = Field(..., ge=0.0, le=1.0)
    ci_method: CIMethod
    n_obs: int = Field(..., gt=0, description="Number of source rows the CI was computed over")


class CrossFoldCIModel(BaseModel):
    """One per-(rung, slice, metric) cross-fold CI cell per ADR-024 + ADR-046 Q3.

    Always emits the cv_clt headline (Bayle 2020 Theorem 3.1 via
    `eval_toolkit.bootstrap.cv_clt_ci`). Commit 3 extension fills the block-bootstrap
    spoke fields + `a_008_flag_fired` boolean per A-008 sensitivity check; Commit 2
    leaves the spoke fields as None pending the extension.

    Persisted to `evals/audit/cross_fold_ci_audit.parquet` for the full per-cell
    audit trail per ADR-013 persist-everything-report-selectively pattern.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: str = Field(..., min_length=1)
    slice_name: str = Field(..., min_length=1)
    metric: str = Field(..., min_length=1)
    k_folds: int = Field(..., ge=2, description="Number of folds the metric vector spans")
    n_seeds_per_fold: int = Field(..., ge=1, description="Within-fold seeds aggregated per ADR-022")

    cv_clt_point_estimate: float = Field(..., ge=0.0, le=1.0)
    cv_clt_ci_lo: float = Field(..., ge=0.0, le=1.0)
    cv_clt_ci_hi: float = Field(..., ge=0.0, le=1.0)
    cv_clt_ci_halfwidth: float = Field(..., ge=0.0)

    block_bootstrap_ci_lo: float | None = Field(
        default=None,
        description="Filled by Commit 3 block-bootstrap-on-folds spoke per A-008.",
    )
    block_bootstrap_ci_hi: float | None = Field(default=None)
    block_bootstrap_ci_halfwidth: float | None = Field(default=None, ge=0.0)
    block_bootstrap_n_resamples: int | None = Field(default=None, gt=0)
    a_008_flag_fired: bool | None = Field(
        default=None,
        description=(
            "True iff block_bootstrap_ci_halfwidth / cv_clt_ci_halfwidth > 1.5 per A-008. "
            "Commit 2 leaves this None; Commit 3 always fills it."
        ),
    )


class MDECellModel(BaseModel):
    """One per-(rung-or-pair, slice, metric, source_ci) MDE cell per ADR-006 + ADR-046 Q4.

    Derived from an upstream CI (`PairedBootstrapCI` or marginal `BootstrapCI`) via
    `eval_toolkit.bootstrap.mde_from_ci` for the paired case; an inline closed-form
    fallback covers the marginal case pending upstream eval-toolkit issue #20.

    `source_ci_kind` discriminates the upstream CI provenance:
        - "paired_bootstrap"  -> ADR-022 trained-vs-trained / trained-vs-reference
        - "marginal_bootstrap" -> Commit 2 marginal per-rung CIs
        - "cv_clt"             -> Commit 2 + 3 cross-fold headline
        - "block_bootstrap"    -> Commit 3 cross-fold spoke (A-008)
        - "paired_op_point"    -> ADR-025 dual-policy operating-point diffs
        - "paired_ece"         -> ADR-023 calibration battery ECE deltas

    All cells persisted to `evals/audit/mde_per_cell.parquet` so the Phase 5 WRITEUP
    can draw any reporting subset without re-running.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung_a: str = Field(..., min_length=1)
    rung_b: str | None = Field(
        default=None,
        description="None for marginal / cross-fold cells; populated for paired cells.",
    )
    slice_name: str = Field(..., min_length=1)
    metric: str = Field(..., min_length=1)
    source_ci_kind: Literal[
        "paired_bootstrap",
        "marginal_bootstrap",
        "cv_clt",
        "block_bootstrap",
        "paired_op_point",
        "paired_ece",
    ]
    ci_halfwidth: float = Field(..., ge=0.0, description="Upstream CI half-width input")
    alpha: float = Field(default=0.05, gt=0.0, lt=1.0)
    power: float = Field(default=0.8, gt=0.0, lt=1.0)
    mde: float = Field(..., gt=0.0, description="Minimum detectable effect at (alpha, power)")
    n: int = Field(
        ...,
        description="Source n where known; -1 sentinel when derived from CI-only path per eval-toolkit MDEEstimate.n convention",
    )
