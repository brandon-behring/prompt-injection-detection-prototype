"""Unit tests for scripts/audit_internal_anchors.py.

Targets the pure-function primitives:
- `heading_to_anchor` — Pandoc/Quarto auto-identifier slug-from-heading.
- `collect_anchors_for_file` — set of resolvable anchors in a markdown file
  (auto-generated from headings + explicit `{#id}` annotations).
- `collect_links_from_file` — intra-site markdown links with anchors.

Per v1.3.5 upstream-port-readiness: `heading_to_anchor` is a candidate
upstream eval-toolkit primitive (markdown-anchor convention helper).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audit_internal_anchors import (  # noqa: E402
    collect_anchors_for_file,
    collect_links_from_file,
    heading_to_anchor,
)


# ---- heading_to_anchor: pandoc-slug semantics ----


@pytest.mark.unit
def test_heading_to_anchor_basic_words() -> None:
    """Simple ASCII heading collapses spaces to single hyphens + lowercases."""
    assert heading_to_anchor("Validation thresholds are fragile") == (
        "validation-thresholds-are-fragile"
    )


@pytest.mark.unit
def test_heading_to_anchor_strips_leading_section_number() -> None:
    """`## 4.6 Foo Bar` yields `foo-bar`, not `46-foo-bar`."""
    assert heading_to_anchor("4.6 Validation thresholds are fragile") == (
        "validation-thresholds-are-fragile"
    )


@pytest.mark.unit
def test_heading_to_anchor_em_dash_collapses_to_single_hyphen() -> None:
    """Em-dash (`—`) is a non-alphanumeric stripped → adjacent spaces become 1 hyphen."""
    # "Epilogue — Limits + reproduction" → "epilogue-limits-reproduction"
    # (em-dash + space + plus + space all become non-alphanumeric strip targets;
    # whitespace runs collapse to single hyphen).
    assert heading_to_anchor("Epilogue — Limits + reproduction") == ("epilogue-limits-reproduction")


@pytest.mark.unit
def test_heading_to_anchor_slash_collapses_to_single_hyphen() -> None:
    """Slash collapses (not double-dash). `Rung / detector clarifier` → `rung-detector-clarifier`."""
    assert heading_to_anchor("Rung / detector clarifier") == "rung-detector-clarifier"


@pytest.mark.unit
def test_heading_to_anchor_strips_markdown_link_syntax() -> None:
    """`# [text](url) trailing` strips the link wrapper, keeps `text trailing`."""
    out = heading_to_anchor("[link text](https://example.com) trailing")
    assert "link" in out  # link's text content is preserved
    assert "https" not in out  # the URL part is dropped


@pytest.mark.unit
def test_heading_to_anchor_strips_emphasis_markers() -> None:
    """Backticks + asterisks + underscores are stripped before slug emission."""
    assert heading_to_anchor("`code` and **bold**") == "code-and-bold"


@pytest.mark.unit
def test_heading_to_anchor_alphanumeric_lead_preserved() -> None:
    """`1b Ablation results` keeps `1b` prefix (no leading-pure-digit-prefix strip)."""
    assert heading_to_anchor("1b Ablation results") == "1b-ablation-results"


# ---- collect_anchors_for_file ----


@pytest.mark.unit
def test_collect_anchors_for_file_picks_up_headings(tmp_path: Path) -> None:
    """All ATX headings yield slugified anchors."""
    md = tmp_path / "doc.md"
    md.write_text(
        "# Title\n\n## Section one\n\n### Subsection A\n\n## Section two\n",
        encoding="utf-8",
    )
    anchors = collect_anchors_for_file(md)
    assert "title" in anchors
    assert "section-one" in anchors
    assert "subsection-a" in anchors
    assert "section-two" in anchors


@pytest.mark.unit
def test_collect_anchors_for_file_respects_explicit_id(tmp_path: Path) -> None:
    """`## Heading {#explicit-id}` registers `explicit-id` (not the auto-slug)."""
    md = tmp_path / "doc.md"
    md.write_text(
        "## [1.3.2] — 2026-05-22 {#v1-3-2}\n\nContent.\n",
        encoding="utf-8",
    )
    anchors = collect_anchors_for_file(md)
    assert "v1-3-2" in anchors  # explicit ID wins
    # The auto-slug would be empty / "2026-05-22"; the explicit wins regardless.


@pytest.mark.unit
def test_collect_anchors_for_file_finds_inline_explicit_ids(tmp_path: Path) -> None:
    """`{#some-id}` on a non-heading line also registers."""
    md = tmp_path / "doc.md"
    md.write_text(
        "# Title\n\nSome prose with an inline anchor.{#inline-target}\n",
        encoding="utf-8",
    )
    anchors = collect_anchors_for_file(md)
    assert "title" in anchors
    assert "inline-target" in anchors


# ---- collect_links_from_file ----


@pytest.mark.unit
def test_collect_links_extracts_intra_site_links(tmp_path: Path) -> None:
    """Markdown `[text](path#anchor)` is extracted as a 4-tuple."""
    md = tmp_path / "doc.md"
    md.write_text(
        "Look at [Results](./RESULTS.md#headline) for the tables.\n",
        encoding="utf-8",
    )
    links = collect_links_from_file(md)
    assert len(links) == 1
    label, target_path, anchor, line_no = links[0]
    assert label == "Results"
    assert target_path == "./RESULTS.md"
    assert anchor == "headline"
    assert line_no == 1


@pytest.mark.unit
def test_collect_links_skips_external_urls(tmp_path: Path) -> None:
    """`https://...`, `mailto:`, `tel:` links are skipped."""
    md = tmp_path / "doc.md"
    md.write_text(
        "External: [GitHub](https://github.com)\n"
        "Email: [me](mailto:foo@bar.com)\n"
        "Tel: [phone](tel:+15555550100)\n",
        encoding="utf-8",
    )
    links = collect_links_from_file(md)
    assert links == []


@pytest.mark.unit
def test_collect_links_pure_fragment(tmp_path: Path) -> None:
    """`[text](#fragment)` is captured as same-file fragment link."""
    md = tmp_path / "doc.md"
    md.write_text("Jump to [section](#some-section).\n", encoding="utf-8")
    links = collect_links_from_file(md)
    assert len(links) == 1
    _label, target_path, anchor, _line_no = links[0]
    assert target_path == ""
    assert anchor == "some-section"
