"""Unit tests for scripts/audit_rendered_site.py.

Targets the pure-function primitives:
- `is_external_or_fragment` — link-classification (skip external / fragment).
- `_plain_text_from_html` — HTML-tag-strip + entity-unescape + whitespace
  normalization (helper for the long-table-cell check).
- `expected_html_paths` — derives expected rendered HTML paths from the
  static input lists (ROOT_MARKDOWN_INPUTS + docs/*.md glob + NOTEBOOK_INPUTS).

Per v1.3.5 upstream-port-readiness: these helpers are local-glue for now
but the link-classification + HTML-text-extraction patterns are reusable
upstream as eval-toolkit `audit.rendered_site_invariants` if eval-toolkit
ever consumes Quarto-rendered sites for evidence storage.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audit_rendered_site import (  # noqa: E402
    _plain_text_from_html,
    expected_html_paths,
    is_external_or_fragment,
)


# ---- is_external_or_fragment ----


@pytest.mark.unit
def test_is_external_http() -> None:
    """`https://...` is classified external."""
    assert is_external_or_fragment("https://github.com/foo/bar") is True


@pytest.mark.unit
def test_is_external_mailto() -> None:
    """`mailto:` is external."""
    assert is_external_or_fragment("mailto:foo@bar.com") is True


@pytest.mark.unit
def test_is_external_pure_fragment() -> None:
    """`#section-id` is treated as same-page fragment (skipped)."""
    assert is_external_or_fragment("#section-id") is True


@pytest.mark.unit
def test_is_external_empty_link() -> None:
    """Empty link string is treated as external/skip."""
    assert is_external_or_fragment("") is True


@pytest.mark.unit
def test_is_external_relative_path_not_external() -> None:
    """`./RESULTS.html` is intra-site (not external)."""
    assert is_external_or_fragment("./RESULTS.html") is False


@pytest.mark.unit
def test_is_external_absolute_path_not_external() -> None:
    """`/decisions/ADR-001.html` is intra-site (no netloc)."""
    assert is_external_or_fragment("/decisions/ADR-001.html") is False


@pytest.mark.unit
def test_is_external_javascript_skipped() -> None:
    """`javascript:` is treated as external/skip."""
    assert is_external_or_fragment("javascript:void(0)") is True


# ---- _plain_text_from_html ----


@pytest.mark.unit
def test_plain_text_strips_tags() -> None:
    """`<b>bold</b>` becomes `bold` after tag-strip."""
    assert _plain_text_from_html("<b>bold</b>") == "bold"


@pytest.mark.unit
def test_plain_text_unescapes_entities() -> None:
    """HTML entities like `&amp;` decode to plain characters."""
    assert _plain_text_from_html("a &amp; b") == "a & b"


@pytest.mark.unit
def test_plain_text_collapses_whitespace_runs() -> None:
    """Multiple whitespace + newlines collapse to single spaces."""
    out = _plain_text_from_html("<p>foo\n\nbar    baz</p>")
    assert out == "foo bar baz"


@pytest.mark.unit
def test_plain_text_handles_nested_tags() -> None:
    """Nested `<a><span>...</span></a>` flattens."""
    assert _plain_text_from_html('<a href="x"><span>linked</span></a>') == "linked"


# ---- expected_html_paths ----


@pytest.mark.unit
def test_expected_html_paths_includes_root_markdown_renderings(tmp_path: Path) -> None:
    """Each ROOT_MARKDOWN_INPUTS entry produces an expected `<name>.html` under site_root."""
    paths = expected_html_paths(tmp_path)
    names = {p.name for p in paths}
    assert "README.html" in names
    assert "RESULTS.html" in names
    assert "WRITEUP_PAPER.html" in names
    assert "WRITEUP_NARRATIVE.html" in names


@pytest.mark.unit
def test_expected_html_paths_includes_notebooks(tmp_path: Path) -> None:
    """Notebook stems (`01_canonical_results`, etc.) appear under `notebooks/`."""
    paths = expected_html_paths(tmp_path)
    notebook_paths = [p for p in paths if p.parent.name == "notebooks"]
    assert len(notebook_paths) >= 4
    names = {p.name for p in notebook_paths}
    assert "01_canonical_results.html" in names
    assert "04_ood_slate.html" in names
