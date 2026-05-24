"""Unit tests for scripts/audit_adr_count_claims.py.

Targets the pure-function primitives:
- `actual_adr_count` — counts decisions/ADR-*.md files.
- `should_skip` — applies the skip-pattern list to a Path.
- `is_historical_snapshot` — heuristic detection of historical-snapshot
  qualifiers in a ±CONTEXT_WINDOW around a count-claim match.
- `audit_file` — per-file scan returning (failures, info) lists.

Per v1.3.5 upstream-port-readiness for eval-toolkit #73 (audit subpackage
+ ADR-citation-alignment validator). These primitives are the seed for
`src/eval_toolkit/audit/citation_alignment.py` (or similar) in the
upstream PR; tests demonstrate the semantics the upstream port must
preserve.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make scripts/ importable; the audit scripts are CLI-style top-level modules,
# not a package, so we add their parent dir to sys.path.
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audit_adr_count_claims import (  # noqa: E402  (sys.path manipulation above)
    actual_adr_count,
    audit_file,
    is_historical_snapshot,
    should_skip,
)


@pytest.mark.unit
def test_actual_adr_count_counts_only_matching_filenames(tmp_path: Path) -> None:
    """Glob pattern matches `ADR-NNN-*.md` files and only those."""
    (tmp_path / "ADR-001-foo.md").touch()
    (tmp_path / "ADR-002-bar.md").touch()
    (tmp_path / "ADR-003-baz.md").touch()
    (tmp_path / "README.md").touch()  # not an ADR
    (tmp_path / "ADR_TEMPLATE.md").touch()  # underscore not hyphen — not ADR-NNN
    assert actual_adr_count(tmp_path) == 3


@pytest.mark.unit
def test_actual_adr_count_empty_dir(tmp_path: Path) -> None:
    """Empty decisions dir returns 0 (not an error)."""
    assert actual_adr_count(tmp_path) == 0


@pytest.mark.unit
def test_should_skip_matches_decisions_subdir() -> None:
    """`decisions/` substring in relative path triggers skip."""
    # We can only test paths under REPO_ROOT; use a path we know exists.
    import audit_adr_count_claims

    repo_root = audit_adr_count_claims.REPO_ROOT
    adr_path = repo_root / "decisions" / "README.md"
    assert should_skip(adr_path) is True


@pytest.mark.unit
def test_should_skip_does_not_skip_writeup_md() -> None:
    """WRITEUP.md is a reader-facing surface; not skipped."""
    import audit_adr_count_claims

    repo_root = audit_adr_count_claims.REPO_ROOT
    writeup_path = repo_root / "WRITEUP.md"
    assert should_skip(writeup_path) is False


@pytest.mark.unit
def test_is_historical_snapshot_detects_phase_close() -> None:
    """`Phase N close` qualifier within context window flags as historical."""
    lines = [
        "Some preamble line.",
        "ADR governance pattern: NN ADRs accepted across Phase 0-00 through Phase 5 close.",
        "Trailing detail.",
    ]
    # Match is on line 2 (1-indexed); context window default is ±3 lines.
    assert is_historical_snapshot(lines, match_line_no=2) is True


@pytest.mark.unit
def test_is_historical_snapshot_detects_through_adr_n() -> None:
    """`accepted across ... through ADR-NNN` qualifier flags as historical."""
    lines = [
        "SDD discipline: 75 ADRs accepted across Phase 0-00 through ADR-075.",
    ]
    assert is_historical_snapshot(lines, match_line_no=1) is True


@pytest.mark.unit
def test_is_historical_snapshot_no_qualifier_is_current_claim() -> None:
    """A plain count claim with no historical qualifier is current."""
    lines = [
        "## Repository map",
        "- 80 ADRs documenting methodology + governance",
        "- 5 figures (F1-F5)",
    ]
    assert is_historical_snapshot(lines, match_line_no=2) is False


@pytest.mark.unit
def test_audit_file_flags_current_mismatch_as_failure(tmp_path: Path) -> None:
    """Current-state count claim that doesn't match actual triggers a failure."""
    md = tmp_path / "fake-reader-surface.md"
    md.write_text(
        "# Project map\n\n"
        "- **80 immutable Architecture Decision Records** under decisions/\n"
        "- Source-disjoint LODO splits\n",
        encoding="utf-8",
    )
    # Tell audit_file the actual count is 81, so the "80" claim is stale.
    failures, info = audit_file(md, actual_count=81)
    assert len(failures) == 1
    assert "claims 80, actual 81" in failures[0]
    assert info == []


@pytest.mark.unit
def test_audit_file_flags_historical_claim_as_info(tmp_path: Path) -> None:
    """Count claim with historical qualifier nearby is INFO, not FAILURE."""
    md = tmp_path / "fake-historical.md"
    md.write_text(
        "# Methodology guarantees\n\n"
        "## SDD process\n"
        "- 50 ADRs accepted across Phase 0-00 through ADR-050 "
        "(governance trail unchanged at submission gate)\n",
        encoding="utf-8",
    )
    failures, info = audit_file(md, actual_count=81)
    assert failures == []
    assert len(info) == 1
    assert "claims 50, actual 81" in info[0]


@pytest.mark.unit
def test_audit_file_no_match_no_drift(tmp_path: Path) -> None:
    """File with no count claims emits neither failure nor info."""
    md = tmp_path / "plain.md"
    md.write_text(
        "# Just prose.\n\nNo numbers here that match the ADR pattern.\n", encoding="utf-8"
    )
    failures, info = audit_file(md, actual_count=81)
    assert failures == []
    assert info == []


@pytest.mark.unit
def test_audit_file_matches_actual_no_drift(tmp_path: Path) -> None:
    """Count claim that matches actual is neither failure nor info."""
    md = tmp_path / "current.md"
    md.write_text("- 81 ADRs in decisions/\n", encoding="utf-8")
    failures, info = audit_file(md, actual_count=81)
    assert failures == []
    assert info == []


@pytest.mark.unit
def test_audit_file_handles_unicode_decode_error_gracefully(tmp_path: Path) -> None:
    """Binary file matched by glob is skipped (no exception)."""
    binary = tmp_path / "binary.md"  # masquerading as .md but bytes are non-utf8
    binary.write_bytes(b"\xff\xfe\x00\x01\x02 binary blob")
    failures, info = audit_file(binary, actual_count=81)
    assert failures == []
    assert info == []
