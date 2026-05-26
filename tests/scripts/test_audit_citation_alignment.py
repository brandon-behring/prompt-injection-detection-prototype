"""Unit tests for scripts/audit_citation_alignment.py.

Targets:
- `parse_adr_frontmatter` — frontmatter title/slug extraction + category inference.
- `should_skip` — skip-pattern logic.
- The v1.3.2 P1-2 synthetic regression (motivating bug class).
- A clean-case test (correct citation = no finding).
- Real-decisions-dir integration (build_adr_subjects against the actual repo).

Per v1.3.7 — consumer adoption of upstream eval_toolkit.audit_citation_alignment
(shipped in v1.0.1; ports brandon-behring/eval-toolkit#73).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audit_citation_alignment import (  # noqa: E402
    CATEGORY_KEYWORDS,
    build_adr_subjects,
    parse_adr_frontmatter,
    should_skip,
)
from eval_toolkit.audit_citation_alignment import validate_citations  # noqa: E402


@pytest.mark.unit
def test_category_keywords_is_non_empty_dict() -> None:
    """Sanity: the consumer-side category map has the expected categories."""
    assert isinstance(CATEGORY_KEYWORDS, dict)
    assert len(CATEGORY_KEYWORDS) >= 8
    # Both load-bearing for the v1.3.2 P1-2 regression case:
    assert "reproducibility" in CATEGORY_KEYWORDS
    assert "test_markers" in CATEGORY_KEYWORDS


@pytest.mark.unit
def test_parse_adr_frontmatter_extracts_id_title_slug(tmp_path: Path) -> None:
    """Frontmatter title + slug get correctly extracted into ADRSubject."""
    adr_path = tmp_path / "ADR-029-test-marker-strategy.md"
    adr_path.write_text(
        "---\n"
        'title: "Test marker strategy"\n'
        'slug: "test-marker-strategy"\n'
        "---\n\n"
        "# ADR-029: Test marker strategy\n",
        encoding="utf-8",
    )
    subj = parse_adr_frontmatter(adr_path)
    assert subj is not None
    assert subj.adr_id == "029"
    assert subj.title == "Test marker strategy"
    assert subj.slug == "test-marker-strategy"
    # Category inferred via extract_adr_subject_category from CATEGORY_KEYWORDS:
    assert subj.category == "test_markers"


@pytest.mark.unit
def test_parse_adr_frontmatter_non_matching_filename_returns_none(tmp_path: Path) -> None:
    """Non-ADR-NNN filenames return None (filename regex guards)."""
    adr_path = tmp_path / "README.md"
    adr_path.write_text("---\ntitle: README\n---\n", encoding="utf-8")
    assert parse_adr_frontmatter(adr_path) is None


@pytest.mark.unit
def test_parse_adr_frontmatter_missing_frontmatter_returns_none(tmp_path: Path) -> None:
    """ADR file without YAML frontmatter returns None."""
    adr_path = tmp_path / "ADR-001-foo.md"
    adr_path.write_text("# ADR-001: foo\n\nBody without frontmatter.\n", encoding="utf-8")
    assert parse_adr_frontmatter(adr_path) is None


@pytest.mark.unit
def test_should_skip_matches_decisions_subdir() -> None:
    """decisions/ subdir is skipped (ADRs themselves)."""
    import audit_citation_alignment

    p = audit_citation_alignment.REPO_ROOT / "decisions" / "README.md"
    assert should_skip(p) is True


@pytest.mark.unit
def test_v1_3_2_p1_2_regression_synthetic_fixture(tmp_path: Path) -> None:
    """Synthetic reconstruction of v1.3.2 P1-2: ADR-029 (test_markers)
    cited for a 'reproducibility tier' claim. validate_citations should flag.
    """
    # Synthetic ADR-029 frontmatter (test_markers category)
    adr_029 = tmp_path / "ADR-029-test-marker-strategy.md"
    adr_029.write_text(
        '---\ntitle: "Test marker strategy"\nslug: "test-marker-strategy"\n---\n',
        encoding="utf-8",
    )
    # Synthetic ADR-034 frontmatter (reproducibility category)
    adr_034 = tmp_path / "ADR-034-reproducibility-tier-full-ladder.md"
    adr_034.write_text(
        "---\n"
        'title: "Reproducibility tier - full ladder T0 + T1 + T3"\n'
        'slug: "reproducibility-tier-full-ladder"\n'
        "---\n",
        encoding="utf-8",
    )
    subjects = {}
    for adr_path in [adr_029, adr_034]:
        subj = parse_adr_frontmatter(adr_path)
        assert subj is not None
        subjects[subj.adr_id] = subj

    # Sanity: category inference produced the expected categories.
    assert subjects["029"].category == "test_markers"
    assert subjects["034"].category == "reproducibility"

    # Reader-prose with the bug: "Two-tier reproduction (per ADR-029)"
    # claims reproducibility category but cites test_markers ADR.
    md_path = tmp_path / "fake-reproducibility-doc.md"
    md_path.write_text(
        "# Reproducibility\n\n"
        "Two-tier reproduction tier ladder (locked at Phase 0-07 per ADR-029):\n\n"
        "- T0: laptop smoke\n"
        "- T1: full cloud rerun\n",
        encoding="utf-8",
    )
    findings = validate_citations(
        markdown_text=md_path.read_text(encoding="utf-8"),
        markdown_path=md_path,
        adr_subjects=subjects,
        category_keywords=CATEGORY_KEYWORDS,
    )

    # Upstream validator should flag this misalignment.
    assert len(findings) >= 1
    bug_finding = next((f for f in findings if f.cited_adr_id == "029"), None)
    assert bug_finding is not None
    assert bug_finding.claim_category == "reproducibility"
    assert bug_finding.adr_actual_category == "test_markers"


@pytest.mark.unit
def test_clean_case_correct_citation_no_finding(tmp_path: Path) -> None:
    """When the cited ADR matches the claim category, no finding emitted."""
    adr_029 = tmp_path / "ADR-029-test-marker-strategy.md"
    adr_029.write_text(
        '---\ntitle: "Test marker strategy"\nslug: "test-marker-strategy"\n---\n',
        encoding="utf-8",
    )
    subj = parse_adr_frontmatter(adr_029)
    assert subj is not None
    subjects = {subj.adr_id: subj}

    md_path = tmp_path / "fake-test-doc.md"
    md_path.write_text(
        "# Test marker strategy\n\n"
        "Per ADR-029, tests use markers (unit marker / smoke marker / integration marker).\n",
        encoding="utf-8",
    )
    findings = validate_citations(
        markdown_text=md_path.read_text(encoding="utf-8"),
        markdown_path=md_path,
        adr_subjects=subjects,
        category_keywords=CATEGORY_KEYWORDS,
    )
    # Citation category matches ADR's actual category → no misalignment.
    assert findings == []


@pytest.mark.unit
def test_build_adr_subjects_against_real_decisions_dir() -> None:
    """Integration: build subjects from the real decisions/ dir; verify non-empty."""
    subjects = build_adr_subjects()
    # We have 81 ADRs at v1.3.6 close; v1.3.7 doesn't add ADRs (no methodology change).
    assert len(subjects) >= 80
    # Spot check: ADR-029 (test markers) should be parseable.
    assert "029" in subjects
    assert "marker" in (subjects["029"].title.lower() + subjects["029"].slug.lower())
