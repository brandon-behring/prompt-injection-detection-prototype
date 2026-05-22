"""Audit numerical / ADR slug / version-string / URL claims on reviewer-facing markdown.

Per ADR-065 §B (locked at v1.2.1; introduced as a closing-polish drift defense
on top of ADR-064 §C2's lychee CI markdown-link-checker). Catches semantic
drift that lychee does NOT cover: stale dollar figures, wrong-but-existing ADR
slug refs, stale version strings, typo'd repo slugs.

Configurable failure mode per ADR-065 §B2:

    uv run python scripts/audit_writeup_numbers.py                 # --strict (default); exit 1 on drift
    uv run python scripts/audit_writeup_numbers.py --report-only   # always exit 0; print report

CI invocation (per ADR-065 §B4): `.github/workflows/audit-writeup.yml` runs
default-strict on push to main + PR + weekly schedule (mirrors lychee CI).

Project-internal per ADR-065 §B3 — audit tooling is meta-level, not a
methodology primitive subject to the strengthened library-first invariant.
Logged in `decisions/library_imports.md` with explicit
`audit-tooling-not-primitive` tag.

Per the no-emoji invariant; pure ASCII output.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# Canonical sources for cross-check (per ADR-065 §B1).
COST_LEDGER_PATH = Path("evals/cost_ledger.csv")
PER_CELL_PARQUET = Path("evals/metrics/per_cell.parquet")
DECISIONS_DIR = Path("decisions")

# Reviewer-facing surfaces per ADR-065 §B1, updated per ADR-078 (EXECUTIVE_SUMMARY
# absorbed into README) + ADR-079 (two-guide reader architecture adds WRITEUP_PAPER
# + WRITEUP_NARRATIVE; WRITEUP.md becomes a router stub).
REVIEWER_FACING_FILES = [
    Path("index.qmd"),
    Path("README.md"),
    Path("RESULTS.md"),
    Path("WRITEUP.md"),
    Path("WRITEUP_PAPER.md"),
    Path("WRITEUP_NARRATIVE.md"),
    Path("READING_GUIDE.md"),
    Path("NEXT_STEPS.md"),
    Path("CHANGELOG.md"),
    Path("docs/for-hiring-managers.md"),
    Path("docs/GLOSSARY.md"),
] + sorted(Path("WRITEUP").glob("*.md"))

# Canonical project identifiers (per ADR-065 §B1 category 4).
CANONICAL_REPO_SLUG = "brandon-behring/prompt-injection-detection-prototype"
CANONICAL_HF_HUB_USER = "BBehring"
CANONICAL_HF_HUB_REPOS = {"prompt-injection-frozen-probe", "prompt-injection-lora"}

# Wrong-but-plausible repo slugs to catch (typo class).
SUSPECT_REPO_SLUG_PATTERNS = [
    r"brandon-behring/prompt-injection-detection-submission\b",
    r"brandon-behring/prompt-injection\b(?!-detection-prototype)",
]

# Stale version-string patterns per ADR-065 §B1 category 3.
STALE_VERSION_PATTERNS = [
    r"\bv1\.1\.1\s+deferred\b",
    r"\bv1\.0\.x\s+pending\b",
    r"DeBERTa\s+(?:execution\s+)?will\s+land\b",
    r"\bpending\s+v1\.1\.[012]\b",
]


@dataclass
class Drift:
    """A single detected drift on a reviewer-facing markdown surface."""

    category: str
    file_path: Path
    line_number: int
    matched_text: str
    detail: str


def load_canonical_cumulative_cost() -> float:
    """Sum `actual_cost_usd` across all rows in `evals/cost_ledger.csv`.

    Returns
    -------
    float
        Canonical cumulative project cost per ADR-065 §E. Currently $17.08
        rounded to cents (full precision $17.0807) as of v1.2.0 close.

    Raises
    ------
    FileNotFoundError
        If `evals/cost_ledger.csv` does not exist (means caller is running
        from wrong working directory).
    """
    if not COST_LEDGER_PATH.exists():
        raise FileNotFoundError(
            f"canonical cost ledger missing at {COST_LEDGER_PATH}; run from repo root"
        )
    df = pd.read_csv(COST_LEDGER_PATH)
    return float(df["actual_cost_usd"].sum())


def known_adr_slugs() -> set[str]:
    """Enumerate the set of valid ADR slug filenames in `decisions/`.

    Returns
    -------
    set[str]
        Set of filenames like `ADR-001-some-slug.md` that actually exist.

    Raises
    ------
    FileNotFoundError
        If `decisions/` does not exist.
    """
    if not DECISIONS_DIR.is_dir():
        raise FileNotFoundError(f"decisions dir missing at {DECISIONS_DIR}")
    return {p.name for p in DECISIONS_DIR.glob("ADR-*.md")}


def scan_adr_slugs(text: str, file_path: Path, valid_slugs: set[str]) -> list[Drift]:
    """Detect references to ADR slugs that do not match any real file.

    Catches the broken-slug class that lychee covers AND
    semantically-wrong-but-existing slug refs (per ADR-065 §B1 category 2).

    Skips intentional broken-slug documentation patterns (postscripts that
    enumerate flagged-not-fixed broken refs in immutable ADRs per ADR-064 §D).

    Parameters
    ----------
    text : str
        Markdown text content.
    file_path : Path
        File-of-origin for drift annotation.
    valid_slugs : set[str]
        Set of valid ADR-NNN-<slug>.md filenames from `decisions/`.

    Returns
    -------
    list[Drift]
        One Drift per non-matching ADR slug reference.
    """
    drifts: list[Drift] = []
    # Match `ADR-NNN-some-slug.md` references; allow optional `decisions/` prefix.
    pattern = re.compile(r"(?:decisions/)?(ADR-\d{3}-[a-z0-9-]+\.md)")
    # Skip-context markers (intentional broken-slug documentation per ADR-064 §D).
    # Markers may appear on the same line OR the previous line (markdown soft
    # wraps can place the marker before the slug it labels).
    skip_markers = ("cite as", "broken refs", "wrong slug", "broken slug")
    all_lines = text.splitlines()
    for line_no, line in enumerate(all_lines, start=1):
        prev_line = all_lines[line_no - 2] if line_no > 1 else ""
        if any(marker in line.lower() or marker in prev_line.lower() for marker in skip_markers):
            continue
        for match in pattern.finditer(line):
            candidate = match.group(1)
            if candidate not in valid_slugs:
                drifts.append(
                    Drift(
                        category="adr_slug",
                        file_path=file_path,
                        line_number=line_no,
                        matched_text=candidate,
                        detail=f"slug {candidate!r} not in decisions/ (broken ref)",
                    )
                )
    return drifts


def scan_cumulative_cost(text: str, file_path: Path, canonical_cost: float) -> list[Drift]:
    """Detect cumulative-cost figures that drift from the canonical sum.

    Targets dollar figures that appear in a *cumulative-cost* context
    (per ADR-065 §B1 category 1). Skip the v1.1.2-spend-specific `$1.34`
    figure (correct + self-consistent per ADR-064 §D). Skip historical
    figures whose +/-15-line context flags them as stale / superseded /
    canonical-elsewhere (e.g., the v1.1.4 + v1.2.1 CHANGELOG postscripts).

    Parameters
    ----------
    text : str
        Markdown text content.
    file_path : Path
        File-of-origin for drift annotation.
    canonical_cost : float
        Canonical cumulative cost from `evals/cost_ledger.csv` sum.

    Returns
    -------
    list[Drift]
        One Drift per stale cumulative-cost figure.
    """
    drifts: list[Drift] = []
    canonical_str = f"${canonical_cost:.2f}"
    all_lines = text.splitlines()
    # Markers indicating the surrounding context flags this figure as
    # historical / superseded (postscript convention per ADR-064 §D + ADR-065 §E).
    flag_markers = (
        "stale",
        "flagged",
        "postscript",
        "canonical figure",
        "canonical cumulative",
        "superseded",
        "historical",
        "$17.08",
        "adr-065",
    )
    # Match "Cumulative ... $X.XX" or "cumulative ... $X.XX" within a line.
    pattern = re.compile(r"[Cc]umulative\s+(?:project\s+)?(?:spend|cost)[^.]*?\$(\d+\.\d{2})")
    for line_no, line in enumerate(all_lines, start=1):
        for match in pattern.finditer(line):
            cited = f"${match.group(1)}"
            if cited == canonical_str:
                continue
            # Skip immutable ADR-063 line refs.
            if "ADR-063" in line:
                continue
            # Skip if +/-15-line context flags the figure as historical /
            # superseded / canonical-elsewhere.
            start = max(0, line_no - 16)
            end = min(len(all_lines), line_no + 15)
            context = "\n".join(all_lines[start:end]).lower()
            if any(marker in context for marker in flag_markers):
                continue
            drifts.append(
                Drift(
                    category="cumulative_cost",
                    file_path=file_path,
                    line_number=line_no,
                    matched_text=cited,
                    detail=(
                        f"cited {cited} differs from canonical {canonical_str} "
                        f"(per evals/cost_ledger.csv sum per ADR-065 §E)"
                    ),
                )
            )
    return drifts


def scan_version_strings(text: str, file_path: Path) -> list[Drift]:
    """Detect stale version-string patterns per ADR-065 §B1 category 3.

    Patterns like `v1.1.1 deferred`, `DeBERTa will land`, etc. Should reflect
    the current v1.2.0+ state at v1.2.1 close.

    Parameters
    ----------
    text : str
        Markdown text content.
    file_path : Path
        File-of-origin for drift annotation.

    Returns
    -------
    list[Drift]
        One Drift per stale version-string match.
    """
    drifts: list[Drift] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for pat in STALE_VERSION_PATTERNS:
            for match in re.finditer(pat, line):
                # Skip historical CHANGELOG entries (immutable per
                # CLAUDE.md ADR-discipline; visible audit trail of past states).
                if file_path.name == "CHANGELOG.md" and "##" in line:
                    continue
                drifts.append(
                    Drift(
                        category="stale_version",
                        file_path=file_path,
                        line_number=line_no,
                        matched_text=match.group(0),
                        detail=f"stale pattern {match.group(0)!r} should reflect v1.2.0+ state",
                    )
                )
    return drifts


def scan_url_slugs(text: str, file_path: Path) -> list[Drift]:
    """Detect typo'd repo / HF Hub slugs per ADR-065 §B1 category 4.

    Catches `prompt-injection-submission` → should be `-prototype`, or
    HF Hub mis-attribution.

    Parameters
    ----------
    text : str
        Markdown text content.
    file_path : Path
        File-of-origin for drift annotation.

    Returns
    -------
    list[Drift]
        One Drift per suspect URL/slug match.
    """
    drifts: list[Drift] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for pat in SUSPECT_REPO_SLUG_PATTERNS:
            for match in re.finditer(pat, line):
                drifts.append(
                    Drift(
                        category="url_slug",
                        file_path=file_path,
                        line_number=line_no,
                        matched_text=match.group(0),
                        detail=(
                            f"suspect slug {match.group(0)!r} — canonical is {CANONICAL_REPO_SLUG}"
                        ),
                    )
                )
    return drifts


def audit_file(path: Path, valid_slugs: set[str], canonical_cost: float) -> list[Drift]:
    """Run all 4 audit categories on a single markdown file.

    Parameters
    ----------
    path : Path
        Reviewer-facing markdown file to audit.
    valid_slugs : set[str]
        Valid ADR slug filenames from `decisions/`.
    canonical_cost : float
        Canonical cumulative cost figure.

    Returns
    -------
    list[Drift]
        All drifts found across the 4 scan categories.
    """
    if not path.exists():
        return [
            Drift(
                category="missing_file",
                file_path=path,
                line_number=0,
                matched_text="",
                detail=f"reviewer-facing surface {path} does not exist",
            )
        ]
    text = path.read_text(encoding="utf-8")
    return (
        scan_adr_slugs(text, path, valid_slugs)
        + scan_cumulative_cost(text, path, canonical_cost)
        + scan_version_strings(text, path)
        + scan_url_slugs(text, path)
    )


def format_drift_report(drifts: list[Drift]) -> str:
    """Format drift list as human-readable per-category report.

    Parameters
    ----------
    drifts : list[Drift]
        All detected drifts across all files.

    Returns
    -------
    str
        Multi-line report, grouped by category.
    """
    if not drifts:
        return "audit_writeup_numbers: 0 drifts (clean)\n"
    by_category: dict[str, list[Drift]] = {}
    for d in drifts:
        by_category.setdefault(d.category, []).append(d)
    lines: list[str] = [f"audit_writeup_numbers: {len(drifts)} drift(s) found\n"]
    for category in sorted(by_category):
        category_drifts = by_category[category]
        lines.append(f"\n[{category}] {len(category_drifts)} drift(s):")
        for d in category_drifts:
            lines.append(f"  {d.file_path}:{d.line_number}: {d.matched_text}  -- {d.detail}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Run the writeup-numbers audit.

    Parameters
    ----------
    argv : list[str] | None
        Argv list (for testing); defaults to sys.argv[1:].

    Returns
    -------
    int
        0 on clean or `--report-only`; 1 on drift in `--strict` mode.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Audit numerical / ADR-slug / version-string / URL claims on "
            "reviewer-facing markdown per ADR-065 §B."
        )
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help=(
            "Always exit 0; print drift report. Useful for local-dev iteration "
            "while tuning false-positive filters. CI uses default --strict."
        ),
    )
    parser.add_argument(
        "--files",
        nargs="*",
        type=Path,
        default=None,
        help=("Override list of files to audit (defaults to ADR-065 §B1 12-surface list)."),
    )
    args = parser.parse_args(argv)

    files_to_audit = args.files if args.files else REVIEWER_FACING_FILES
    valid_slugs = known_adr_slugs()
    canonical_cost = load_canonical_cumulative_cost()

    all_drifts: list[Drift] = []
    for path in files_to_audit:
        all_drifts.extend(audit_file(path, valid_slugs, canonical_cost))

    report = format_drift_report(all_drifts)
    print(report)

    if args.report_only:
        return 0
    return 1 if all_drifts else 0


if __name__ == "__main__":
    sys.exit(main())
