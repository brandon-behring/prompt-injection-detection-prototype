"""Unit tests for scripts/audit_writeup_numbers.py.

Targets the pure-function primitives (already library-shaped — minimal
refactor needed):
- `scan_adr_slugs` — detect ADR-NNN-<slug>.md references that don't match
  any real file (broken-slug class).
- `scan_url_slugs` — detect typo'd repo / HF Hub slugs (e.g.,
  `prompt-injection-detection-submission` ≠ canonical `-prototype`).
- `scan_version_strings` — detect stale version-string patterns
  (e.g., `v1.1.1 deferred`).
- `format_drift_report` — render Drift list as a human-readable per-
  category report.

Per v1.3.5 upstream-port-readiness: scan_* functions are the seed for
eval-toolkit #71 (detector→value binding validator) — the generic
`(claim, source_of_truth, surrounding_context) → Drift` shape.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audit_writeup_numbers import (  # noqa: E402
    Drift,
    format_drift_report,
    scan_adr_slugs,
    scan_url_slugs,
    scan_version_strings,
)


# ---- scan_adr_slugs ----


@pytest.mark.unit
def test_scan_adr_slugs_no_match_returns_empty() -> None:
    """Text with no ADR-NNN-slug.md references yields no drifts."""
    valid = {"ADR-001-foo.md", "ADR-002-bar.md"}
    drifts = scan_adr_slugs("just prose; no slug refs", Path("test.md"), valid)
    assert drifts == []


@pytest.mark.unit
def test_scan_adr_slugs_known_slug_no_drift() -> None:
    """Reference to a valid slug yields no drift."""
    valid = {"ADR-001-foo.md", "ADR-002-bar.md"}
    drifts = scan_adr_slugs(
        "See decisions/ADR-001-foo.md for context.",
        Path("test.md"),
        valid,
    )
    assert drifts == []


@pytest.mark.unit
def test_scan_adr_slugs_unknown_slug_flagged() -> None:
    """Reference to a non-existent slug yields a Drift with category='adr_slug'."""
    valid = {"ADR-001-foo.md", "ADR-002-bar.md"}
    drifts = scan_adr_slugs(
        "Reference to ADR-999-nonexistent.md should fail.",
        Path("test.md"),
        valid,
    )
    assert len(drifts) == 1
    assert drifts[0].category == "adr_slug"
    assert drifts[0].matched_text == "ADR-999-nonexistent.md"


@pytest.mark.unit
def test_scan_adr_slugs_with_decisions_prefix() -> None:
    """`decisions/ADR-NNN-slug.md` form is also extracted + validated."""
    valid = {"ADR-001-foo.md"}
    drifts = scan_adr_slugs(
        "[link](decisions/ADR-999-bad.md)",
        Path("test.md"),
        valid,
    )
    assert len(drifts) == 1


@pytest.mark.unit
def test_scan_adr_slugs_respects_broken_refs_skip_marker() -> None:
    """Lines flagged with 'cite as broken refs' are intentional documentation; skip."""
    valid = {"ADR-001-foo.md"}
    text = (
        "Wrong slug example (cite as broken refs): "
        "decisions/ADR-006-headline-metrics-and-statistical-floor.md\n"
    )
    drifts = scan_adr_slugs(text, Path("test.md"), valid)
    assert drifts == []


# ---- scan_url_slugs ----


@pytest.mark.unit
def test_scan_url_slugs_canonical_no_drift() -> None:
    """Canonical `brandon-behring/prompt-injection-detection-prototype` is fine."""
    drifts = scan_url_slugs(
        "https://github.com/brandon-behring/prompt-injection-detection-prototype",
        Path("test.md"),
    )
    assert drifts == []


@pytest.mark.unit
def test_scan_url_slugs_typo_submission_flagged() -> None:
    """`-submission` variant is a known typo class; flagged."""
    drifts = scan_url_slugs(
        "https://github.com/brandon-behring/prompt-injection-detection-submission",
        Path("test.md"),
    )
    # Both SUSPECT_REPO_SLUG_PATTERNS may match the same line — assert ≥1.
    assert len(drifts) >= 1
    assert all(d.category == "url_slug" for d in drifts)


# ---- scan_version_strings ----


@pytest.mark.unit
def test_scan_version_strings_stale_phrase_flagged() -> None:
    """`v1.1.1 deferred` is a known stale pattern; flagged."""
    drifts = scan_version_strings(
        "DeBERTa execution v1.1.1 deferred to a later release.",
        Path("test.md"),
    )
    assert len(drifts) == 1
    assert drifts[0].category == "stale_version"


@pytest.mark.unit
def test_scan_version_strings_changelog_history_section_skipped() -> None:
    """Historical CHANGELOG headings (`## ...`) skip the stale-pattern flag."""
    drifts = scan_version_strings(
        "## DeBERTa execution will land at v1.1.1",  # contains `##` marker
        Path("CHANGELOG.md"),
    )
    # Heading-level entries in CHANGELOG are historical; should skip.
    assert drifts == []


# ---- format_drift_report ----


@pytest.mark.unit
def test_format_drift_report_empty_returns_clean_message() -> None:
    """No drifts yields the 'clean' marker."""
    out = format_drift_report([])
    assert "0 drifts" in out
    assert "clean" in out


@pytest.mark.unit
def test_format_drift_report_groups_by_category() -> None:
    """Multi-category drifts are grouped under per-category headers."""
    drifts = [
        Drift(
            category="adr_slug",
            file_path=Path("a.md"),
            line_number=1,
            matched_text="ADR-999-bad.md",
            detail="broken",
        ),
        Drift(
            category="url_slug",
            file_path=Path("a.md"),
            line_number=2,
            matched_text="prompt-injection-detection-submission",
            detail="typo",
        ),
    ]
    out = format_drift_report(drifts)
    assert "2 drift(s)" in out
    assert "[adr_slug]" in out
    assert "[url_slug]" in out
