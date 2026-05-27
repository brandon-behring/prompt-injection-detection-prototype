"""Unit tests for scripts/audit_value_bindings.py.

Targets:
- BINDINGS / DETECTOR_ALIASES / METRIC_ALIASES / SLICE_ALIASES sanity.
- BindingKey schema (v1.3.11 adoption of upstream eval-toolkit v1.1.0).
- `should_skip` skip-pattern logic.
- The V1.3.1 ADR-080 synthetic regression (motivating bug class).
- A clean-case test (correct binding = no violation).
- Slice-disambiguation: same (detector, metric) across different slices.
- `scope='narrative'` filtering (table rows + CI brackets + code blocks
  are excluded; narrative prose is matched).
- Real-surface integration (gather_surfaces against the actual repo).

Per v1.3.11 — upgraded from v1.3.8 initial adoption. Consumer-side
migration from 2-tuple `(detector, metric)` schema to BindingKey
structured-key schema per eval-toolkit ADR 0005 (closes eval-toolkit#80).
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
    SLICE_ALIASES,
    gather_surfaces,
    should_skip,
)
from eval_toolkit.audit_value_bindings import (  # noqa: E402
    BindingKey,
    validate_reader_value_bindings,
)


@pytest.mark.unit
def test_bindings_uses_binding_key_schema() -> None:
    """v1.3.11: BINDINGS keys are BindingKey instances, not 2-tuples."""
    assert len(BINDINGS) >= 11, "expected >=11 entries after v1.3.11 expansion"
    for key in BINDINGS:
        assert isinstance(key, BindingKey), (
            f"key {key!r} is {type(key).__name__}, expected BindingKey"
        )


@pytest.mark.unit
def test_bindings_seed_contains_motivating_pair() -> None:
    """The V1.3.1 ADR-080 + V1.3.9 F1 bug class requires both TF-IDF + LoRA
    direct-validation bindings."""
    tfidf_key = BindingKey("TF-IDF", "AUPRC", "direct_validation")
    lora_key = BindingKey("LoRA", "AUPRC", "direct_validation")
    assert tfidf_key in BINDINGS
    assert lora_key in BINDINGS
    assert BINDINGS[tfidf_key] == 0.971
    assert BINDINGS[lora_key] == 0.974


@pytest.mark.unit
def test_bindings_covers_pooled_ood_headline_slate() -> None:
    """v1.3.11 expansion covers all 5 detectors on pooled_ood AUPRC."""
    expected = {
        BindingKey("frozen_probe", "AUPRC", "pooled_ood"): 0.364,
        BindingKey("ProtectAI-v1", "AUPRC", "pooled_ood"): 0.361,
        BindingKey("ProtectAI-v2", "AUPRC", "pooled_ood"): 0.314,
        BindingKey("LoRA", "AUPRC", "pooled_ood"): 0.293,
        BindingKey("TF-IDF", "AUPRC", "pooled_ood"): 0.291,
    }
    for key, expected_value in expected.items():
        assert key in BINDINGS, f"missing pooled_ood AUPRC binding for {key.detector}"
        assert BINDINGS[key] == expected_value, (
            f"{key.detector} pooled_ood AUPRC: expected {expected_value}, got {BINDINGS[key]}"
        )


@pytest.mark.unit
def test_detector_aliases_cover_canonical_keys() -> None:
    """Every canonical detector in BINDINGS has an alias entry.

    v1.3.14: `isinstance` filter is a runtime no-op (the v1.3.11
    invariant test `test_bindings_uses_binding_key_schema` already
    asserts ALL keys ARE BindingKey instances); the filter narrows
    the union BINDINGS key type (`BindingKey | tuple[...,]`) so
    mypy can resolve `.detector` attribute access. If a non-BindingKey
    key were ever added, the v1.3.11 invariant test fails first.
    """
    detectors_in_bindings = {key.detector for key in BINDINGS if isinstance(key, BindingKey)}
    for detector in detectors_in_bindings:
        assert detector in DETECTOR_ALIASES, f"missing aliases for {detector!r}"
        assert len(DETECTOR_ALIASES[detector]) >= 1


@pytest.mark.unit
def test_metric_aliases_cover_canonical_keys() -> None:
    """Every canonical metric in BINDINGS has an alias entry.

    See `test_detector_aliases_cover_canonical_keys` for the v1.3.14
    `isinstance` narrowing rationale.
    """
    metrics_in_bindings = {key.metric for key in BINDINGS if isinstance(key, BindingKey)}
    for metric in metrics_in_bindings:
        assert metric in METRIC_ALIASES, f"missing aliases for {metric!r}"
        assert len(METRIC_ALIASES[metric]) >= 1


@pytest.mark.unit
def test_slice_aliases_cover_canonical_keys() -> None:
    """v1.3.11: every non-default slice in BINDINGS has an alias entry.

    See `test_detector_aliases_cover_canonical_keys` for the v1.3.14
    `isinstance` narrowing rationale.
    """
    slices_in_bindings = {
        key.slice for key in BINDINGS if isinstance(key, BindingKey) and key.slice != "any"
    }
    for slice_name in slices_in_bindings:
        assert slice_name in SLICE_ALIASES, f"missing slice aliases for {slice_name!r}"
        assert len(SLICE_ALIASES[slice_name]) >= 1


@pytest.mark.unit
def test_should_skip_matches_decisions_subdir() -> None:
    """decisions/ subdir is skipped (ADRs themselves)."""
    import audit_value_bindings

    p = audit_value_bindings.REPO_ROOT / "decisions" / "README.md"
    assert should_skip(p) is True


@pytest.mark.unit
def test_should_skip_excludes_codex_audit_reports() -> None:
    """v1.3.11: *_codex.md files are skipped (gitignored audit reports)."""
    import audit_value_bindings

    p = audit_value_bindings.REPO_ROOT / "PUBLIC_DOCS_POLISH_AUDIT_codex.md"
    assert should_skip(p) is True


@pytest.mark.unit
def test_should_skip_excludes_submission_md() -> None:
    """v1.3.11: SUBMISSION.md is skipped (gitignored cover-letter draft)."""
    import audit_value_bindings

    p = audit_value_bindings.REPO_ROOT / "SUBMISSION.md"
    assert should_skip(p) is True


@pytest.mark.unit
def test_v1_3_1_adr080_regression_synthetic_fixture(tmp_path: Path) -> None:
    """Synthetic reconstruction of V1.3.1 ADR-080: TF-IDF said to reach 0.974
    AUPRC on direct-versus-benign validation. Canonical = 0.971; 0.974 is
    LoRA's value. validate_reader_value_bindings should flag this as a
    Violation.

    v1.3.11 update: slice context ("direct validation") in the fixture is
    required for the new BindingKey schema to match against the
    direct_validation slice binding.
    """
    md_path = tmp_path / "fake-writeup.md"
    md_path.write_text(
        "# Headline\n\n"
        "The TF-IDF + logistic regression baseline reaches 0.974 AUPRC "
        "on balanced direct+benign validation.\n",
        encoding="utf-8",
    )
    report = validate_reader_value_bindings(
        files=[md_path],
        bindings=BINDINGS,
        detector_aliases=DETECTOR_ALIASES,
        metric_aliases=METRIC_ALIASES,
        slice_aliases=SLICE_ALIASES,
        scope="narrative",
    )
    # Should flag: TF-IDF prose says 0.974 but canonical direct_validation
    # AUPRC for TF-IDF is 0.971.
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
        "On direct+benign validation, the TF-IDF + LR baseline reaches "
        "0.971 AUPRC. LoRA edges it out at 0.974 AUPRC on the same "
        "direct validation slate.\n",
        encoding="utf-8",
    )
    report = validate_reader_value_bindings(
        files=[md_path],
        bindings=BINDINGS,
        detector_aliases=DETECTOR_ALIASES,
        metric_aliases=METRIC_ALIASES,
        slice_aliases=SLICE_ALIASES,
        scope="narrative",
    )
    # No false positives on a clean, slice-disambiguated fixture.
    tfidf_lora_violations = [
        v for v in report.violations if v.detector in ("TF-IDF", "LoRA") and v.metric == "AUPRC"
    ]
    assert tfidf_lora_violations == [], (
        f"expected no TF-IDF/LoRA violations on clean fixture; got {tfidf_lora_violations}"
    )


@pytest.mark.unit
def test_slice_disambiguation_direct_vs_pooled_ood(tmp_path: Path) -> None:
    """v1.3.11: same (detector, metric) values across different slices should
    not cross-flag when slice context is in the surrounding prose."""
    md_path = tmp_path / "fake-multi-slice.md"
    md_path.write_text(
        "# Headline\n\n"
        "On balanced direct+benign validation, LoRA reaches AUPRC 0.974.\n"
        "On pooled OOD, LoRA scores AUPRC 0.293 — well below floor.\n",
        encoding="utf-8",
    )
    report = validate_reader_value_bindings(
        files=[md_path],
        bindings=BINDINGS,
        detector_aliases=DETECTOR_ALIASES,
        metric_aliases=METRIC_ALIASES,
        slice_aliases=SLICE_ALIASES,
        scope="narrative",
    )
    # Both LoRA values are canonical for their respective slices;
    # the validator should NOT cross-flag (0.974 against pooled_ood key,
    # or 0.293 against direct_validation key).
    lora_violations = [v for v in report.violations if v.detector == "LoRA"]
    assert lora_violations == [], (
        f"expected no LoRA violations with slice disambiguation; got {lora_violations}"
    )


@pytest.mark.unit
def test_scope_narrative_excludes_markdown_tables(tmp_path: Path) -> None:
    """v1.3.11: scope='narrative' should exclude markdown table rows from
    matching (per upstream v1.1.0 scope-correctness layer)."""
    md_path = tmp_path / "fake-table.md"
    md_path.write_text(
        "# Headline\n\n"
        "| Detector | AUPRC |\n"
        "|---|---:|\n"
        "| LoRA | 0.974 |\n"
        "| TF-IDF | 0.974 |\n",  # WRONG value but inside a table row
        encoding="utf-8",
    )
    report = validate_reader_value_bindings(
        files=[md_path],
        bindings=BINDINGS,
        detector_aliases=DETECTOR_ALIASES,
        metric_aliases=METRIC_ALIASES,
        slice_aliases=SLICE_ALIASES,
        scope="narrative",
    )
    # Table rows are excluded under scope='narrative'; even the wrong
    # TF-IDF/0.974 binding inside the table should not flag.
    tfidf_violations = [
        v for v in report.violations if v.detector == "TF-IDF" and v.metric == "AUPRC"
    ]
    assert tfidf_violations == [], (
        f"expected no TF-IDF/AUPRC violations under scope='narrative' "
        f"(table-row content); got {tfidf_violations}"
    )


@pytest.mark.unit
def test_gather_surfaces_against_real_repo() -> None:
    """Integration: gather_surfaces returns a non-empty list, all .md/.qmd."""
    surfaces = gather_surfaces()
    assert len(surfaces) > 0
    # All paths should end with .md or .qmd extension.
    assert all(p.suffix in (".md", ".qmd") for p in surfaces)
    # CHANGELOG + SUBMISSION_AUDIT + SUBMISSION + codex audit reports must
    # be excluded by SKIP_PATTERNS.
    surface_names = {p.name for p in surfaces}
    assert "CHANGELOG.md" not in surface_names
    assert "SUBMISSION_AUDIT.md" not in surface_names
    assert "SUBMISSION.md" not in surface_names
    assert "PUBLIC_DOCS_POLISH_AUDIT_codex.md" not in surface_names
    assert "HIRING_MANAGER_QUARTO_PRESENTATION_RESEARCH_codex.md" not in surface_names
