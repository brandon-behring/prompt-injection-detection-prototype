"""src/eval/ — Phase 3 evaluation primitives per ADR-026 + ADR-045.

Sub-modules:
- schemas: pydantic v2 contract for predictions, metrics, operating points,
  calibration records, reachability audits, bootstrap cells (per ADR-045 Q7).
- calibration_battery (Phase 3 Commit 3): ECE matrix + Brier + reliability +
  temperature + isotonic interventions per ADR-023.
- operating_points (Phase 3 Commit 4): dual-policy thresholds (detection +
  verification) with reachability audit per ADR-025.
- slice_analysis (Phase 3 Commit 4): 5-slice OOD aggregation per ADR-021.
"""
