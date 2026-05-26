"""Unit tests for scripts/audit_value_bindings.py.

Targets:
- BINDINGS / DETECTOR_ALIASES / METRIC_ALIASES sanity.
- `should_skip` skip-pattern logic.
- The V1.3.1 ADR-080 synthetic regression (motivating bug class).
- A clean-case test (correct binding = no violation).
- Real-surface integration (gather_surfaces against the actual repo).

Per v1.3.8 — consumer adoption of upstream
`eval_toolkit.audit_value_bindings` (shipped in v1.0.3; ports
brandon-behring/eval-toolkit#71).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audit_value_bindings import (  # noqa: E402
    BINDINGS,
    DETECTOR_ALIASES,
    METRIC_ALIASES,
    gather_surfaces,
    should_skip,
)
from eval_toolkit.audit_value_bindings import (  # noqa: E402
    validate_reader_value_bindings,
)


@pytest.mark.unit
def test_bindings_seed_contains_motivating_pair() -> None:
    """The V1.3.1 ADR-080 bug class requires both TF-IDF + LoRA bindings."""
    assert ("TF-IDF", "AUPRC") in BINDINGS
    assert ("LoRA", "AUPRC") in BINDINGS
    assert BINDINGS[("TF-IDF", "AUPRC")] == 0.971
    assert BINDINGS[("LoRA", "AUPRC")] == 0.974


@pytest.mark.unit
def test_detector_aliases_cover_canonical_keys() -> None:
    """Every canonical detector in BINDINGS has an alias entry."""
    detectors_in_bindings = {detector for detector, _ in BINDINGS}
    for detector in detectors_in_bindings:
        assert detector in DETECTOR_ALIASES, f"missing aliases for {detector!r}"
        assert len(DETECTOR_ALIASES[detector]) >= 1


@pytest.mark.unit
def test_metric_aliases_cover_canonical_keys() -> None:
    """Every canonical metric in BINDINGS has an alias entry."""
    metrics_in_bindings = {metric for _, metric in BINDINGS}
    for metric in metrics_in_bindings:
        assert metric in METRIC_ALIASES, f"missing aliases for {metric!r}"
        assert len(METRIC_ALIASES[metric]) >= 1


@pytest.mark.unit
def test_should_skip_matches_decisions_subdir() -> None:
    """decisions/ subdir is skipped (ADRs themselves)."""
    import audit_value_bindings

    p = audit_value_bindings.REPO_ROOT / "decisions" / "README.md"
    assert should_skip(p) is True


@pytest.mark.unit
def test_v1_3_1_adr080_regression_synthetic_fixture(tmp_path: Path) -> None:
    """Synthetic reconstruction of V1.3.1 ADR-080: TF-IDF said to reach 0.974
    AUPRC. Canonical = 0.971; 0.974 is LoRA's value. validate_reader_value_bindings
    should flag this as a Violation.
    """
    md_path = tmp_path / "fake-writeup.md"
    md_path.write_text(
        "# Headline\n\n"
        "The TF-IDF + logistic regression baseline reaches 0.974 AUPRC "
        "on balanced direct-versus-benign validation.\n",
        encoding="utf-8",
    )
    report = validate_reader_value_bindings(
        files=[md_path],
        bindings=BINDINGS,
        detector_aliases=DETECTOR_ALIASES,
        metric_aliases=METRIC_ALIASES,
    )
    # Should flag: TF-IDF prose says 0.974 but canonical is 0.971.
    assert len(report.violations) >= 1
    bug = next(
        (v for v in report.violations if v.detector == "TF-IDF" and v.metric == "AUPRC"),
        None,
    )
    assert bug is not None, f"expected TF-IDF/AUPRC violation; got {report.violations}"
    assert bug.found_value == 0.974
    assert bug.expected_value == 0.971


@pytest.mark.unit
def test_clean_case_correct_binding_no_violation(tmp_path: Path) -> None:
    """When the prose binding matches the canonical table, no violation."""
    md_path = tmp_path / "fake-correct.md"
    md_path.write_text(
        "# Headline\n\n"
        "The TF-IDF + logistic regression baseline reaches 0.971 AUPRC "
        "on direct validation. LoRA reaches 0.974 AUPRC.\n",
        encoding="utf-8",
    )
    report = validate_reader_value_bindings(
        files=[md_path],
        bindings=BINDINGS,
        detector_aliases=DETECTOR_ALIASES,
        metric_aliases=METRIC_ALIASES,
    )
    assert report.violations == ()
    # Both canonical bindings should match.
    assert report.coverage == pytest.approx(1.0)


@pytest.mark.unit
def test_gather_surfaces_against_real_repo() -> None:
    """Integration: gather_surfaces returns a non-empty list, all .md/.qmd."""
    surfaces = gather_surfaces()
    assert len(surfaces) > 0
    # All paths should end with .md or .qmd extension.
    assert all(p.suffix in (".md", ".qmd") for p in surfaces)
    # CHANGELOG and SUBMISSION_AUDIT must be excluded by SKIP_PATTERNS.
    surface_names = {p.name for p in surfaces}
    assert "CHANGELOG.md" not in surface_names
    assert "SUBMISSION_AUDIT.md" not in surface_names
