"""Unit tests for scripts/audit_superseded_by_backlinks.py.

Targets the pure-function primitives:
- `normalize_adr_id` — coerce various ADR id forms to 3-digit string.
- `parse_frontmatter` — YAML frontmatter extraction from ADR markdown.
- `extract_id_list` — flatten a `supersedes:` / `superseded_by:` field
  (which may be int / str / list / list-of-str-with-comments) to a list
  of normalized 3-digit ADR ids.

Per v1.3.5 upstream-port-readiness: the supersession-backlink validator
is a candidate upstream eval-toolkit primitive (per the audit/ subpackage
plan for #71/#72/#73).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audit_superseded_by_backlinks import (  # noqa: E402
    extract_id_list,
    normalize_adr_id,
    parse_frontmatter,
)


# ---- normalize_adr_id ----


@pytest.mark.unit
def test_normalize_adr_id_three_digit_string() -> None:
    """`"046"` stays `"046"`."""
    assert normalize_adr_id("046") == "046"


@pytest.mark.unit
def test_normalize_adr_id_strips_adr_prefix() -> None:
    """`"ADR-046"` returns `"046"`."""
    assert normalize_adr_id("ADR-046") == "046"


@pytest.mark.unit
def test_normalize_adr_id_pads_short_int() -> None:
    """Integer `46` returns 3-digit zero-padded `"046"`."""
    assert normalize_adr_id(46) == "046"


@pytest.mark.unit
def test_normalize_adr_id_strips_inline_comment() -> None:
    """`"ADR-046  # comment"` returns `"046"` (regex match ignores trailing)."""
    assert normalize_adr_id("ADR-046  # axis-only per comment") == "046"


@pytest.mark.unit
def test_normalize_adr_id_none_input() -> None:
    """`None` returns `None`."""
    assert normalize_adr_id(None) is None


@pytest.mark.unit
def test_normalize_adr_id_empty_string() -> None:
    """Empty string returns None."""
    assert normalize_adr_id("") is None


@pytest.mark.unit
def test_normalize_adr_id_unparseable() -> None:
    """Non-numeric string returns None."""
    assert normalize_adr_id("not-a-number") is None


# ---- parse_frontmatter ----


@pytest.mark.unit
def test_parse_frontmatter_well_formed_adr(tmp_path: Path) -> None:
    """Standard ADR frontmatter parses to a dict with expected keys."""
    md = tmp_path / "ADR-046-test.md"
    md.write_text(
        "---\n"
        'adr_id: "046"\n'
        "slug: test-adr\n"
        "title: Test ADR\n"
        "date: 2026-05-22\n"
        "status: Accepted\n"
        "---\n"
        "\n"
        "# ADR-046: Test ADR\n",
        encoding="utf-8",
    )
    fm = parse_frontmatter(md)
    assert fm is not None
    assert fm["adr_id"] == "046"
    assert fm["status"] == "Accepted"


@pytest.mark.unit
def test_parse_frontmatter_no_frontmatter_returns_none(tmp_path: Path) -> None:
    """File without `---` delimiters returns None."""
    md = tmp_path / "no-frontmatter.md"
    md.write_text("# Just a heading\n\nNo frontmatter.\n", encoding="utf-8")
    assert parse_frontmatter(md) is None


@pytest.mark.unit
def test_parse_frontmatter_unclosed_frontmatter_returns_none(tmp_path: Path) -> None:
    """File starting with `---` but no closing `---` returns None."""
    md = tmp_path / "unclosed.md"
    md.write_text("---\nadr_id: 999\nstill in frontmatter no close marker\n", encoding="utf-8")
    assert parse_frontmatter(md) is None


# ---- extract_id_list ----


@pytest.mark.unit
def test_extract_id_list_empty_inputs() -> None:
    """None / empty list / empty string all yield empty list."""
    assert extract_id_list(None) == []
    assert extract_id_list([]) == []
    assert extract_id_list("") == []


@pytest.mark.unit
def test_extract_id_list_single_string() -> None:
    """`"046"` yields `["046"]`."""
    assert extract_id_list("046") == ["046"]


@pytest.mark.unit
def test_extract_id_list_list_of_strings() -> None:
    """`["046", "054", "061"]` yields a 3-element list."""
    assert extract_id_list(["046", "054", "061"]) == ["046", "054", "061"]


@pytest.mark.unit
def test_extract_id_list_normalizes_mixed_forms() -> None:
    """Mixed int / string / `ADR-NNN` forms all normalize to 3-digit strings."""
    assert extract_id_list([46, "054", "ADR-061"]) == ["046", "054", "061"]
