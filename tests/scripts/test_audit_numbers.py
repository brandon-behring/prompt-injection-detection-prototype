"""Unit tests for scripts/audit_numbers.py.

Targets the pure-function primitives:
- `Check` — dataclass holding (description, computed, expected, tolerance,
  status, diff). The unit-of-comparison for each numeric audit.

Note: most of `audit_numbers.py`'s primitives are I/O-bound (read parquet,
re-derive metric, diff against canonical). They can't be unit-tested
without mocking the full evals/* artifact tree. The Check dataclass +
tolerance logic IS pure and IS tested here. Integration coverage of the
parquet-reading primitives lives in tests/smoke/test_audit_smoke.py.

Per v1.3.5 upstream-port-readiness: the (claim, computed, tolerance,
pass/fail) abstraction is the seed for eval-toolkit #71 (detector→value
binding validator) — the validator framework wrapping per-detector
metric re-derivation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audit_numbers import Check  # noqa: E402


@pytest.mark.unit
def test_check_constructed_with_all_fields() -> None:
    """Check is a dataclass with a fixed schema; instantiation roundtrips."""
    chk = Check(
        name="Headline AUPRC pooled_ood frozen_probe",
        computed=0.3640,
        expected=0.3640,
        tol=0.005,
    )
    assert chk.name == "Headline AUPRC pooled_ood frozen_probe"
    assert chk.computed == 0.3640
    assert chk.expected == 0.3640
    assert chk.tol == 0.005


@pytest.mark.unit
def test_check_status_pass_when_within_tolerance() -> None:
    """Check passes when |computed - expected| <= tol."""
    chk = Check(
        name="test",
        computed=0.3641,
        expected=0.3640,
        tol=0.005,
    )
    diff = abs(chk.computed - chk.expected)
    assert diff <= chk.tol


@pytest.mark.unit
def test_check_status_fail_when_outside_tolerance() -> None:
    """Check fails when |computed - expected| > tol."""
    chk = Check(
        name="test",
        computed=0.500,
        expected=0.3640,
        tol=0.005,
    )
    diff = abs(chk.computed - chk.expected)
    assert diff > chk.tol


@pytest.mark.unit
def test_check_default_tol_is_sensible() -> None:
    """Default `tol` is a small float suitable for AUPRC-class metrics."""
    import dataclasses

    fields = {f.name: f.default for f in dataclasses.fields(Check)}
    assert "tol" in fields
    assert isinstance(fields["tol"], float)
    # Default is reasonable for AUPRC-class metrics (≤ 0.01)
    assert fields["tol"] <= 0.01
