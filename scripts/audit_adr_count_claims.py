"""Audit that "NN immutable Architecture Decision Records" / "NN ADRs" claims
across reader-facing surfaces match the actual ADR file count.

Motivated by REPO_AUDIT_2026-05-21 visual-verification finding D1: v1.2.13
added ADR-076 but README's "75 ADRs" claim went stale because the source
audit (REPO_AUDIT_2026-05-21.md) only flagged the audit-time-stale "70"
counts on other surfaces, not the chain-effect.

Behavior:
  1. Counts decisions/ADR-*.md files (the source of truth).
  2. Enumerates reader-facing surfaces (top-level *.md + *.qmd,
     WRITEUP/*.md, docs/*.md). Skips:
       - CHANGELOG.md (intentionally version-pinned historical counts)
       - decisions/ (ADRs themselves; some quote count claims as
         historical-at-lock-time and are immutable)
       - transcripts/ (gitignored; operator-side QA)
  3. For each surface, greps the count-claim pattern.
  4. Reports mismatches. Historical-snapshot claims (with qualifiers
     like "at Phase X close" / "submission gate" / "snapshot at" /
     explicit version "v1.X.X") are flagged as INFO; reviewable but
     not failing.
  5. Exit 0 if all *current* claims match. Exit 1 if any current claim
     is stale.

Usage:
  uv run python scripts/audit_adr_count_claims.py

CI / pre-commit: invoked from .pre-commit-config.yaml + ci.yml.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Reader-facing surfaces to audit. Globs relative to REPO_ROOT.
# Order roughly by reader-priority for stable output.
SURFACE_GLOBS = [
    "*.md",
    "*.qmd",
    "WRITEUP/*.md",
    "docs/*.md",
]

# Files/directories to skip even if matched by globs.
SKIP_PATTERNS = [
    "CHANGELOG.md",  # version-pinned historical counts are intentional
    "SUBMISSION_AUDIT.md",  # generated; may contain historical CLAIM counts
    "draft_review.md",  # operator review document; quotes example text
    "decisions/",  # ADRs themselves; immutable per CLAUDE.md
    "transcripts/",  # gitignored; operator-side QA
    ".venv/",
    ".quarto/",
]

# Pattern matching "N immutable Architecture Decision Records" or "N ADRs".
# The `\bADRs\b` clause matches plain "75 ADRs" but not "ADR-75" or "75ms".
ADR_COUNT_RE = re.compile(r"\b(\d+)\s+(?:immutable\s+Architecture\s+Decision\s+Records|ADRs)\b")

# Keywords near a claim (within a ±2-line context window) that indicate
# the claim is a historical snapshot (not the current count). Case-insensitive.
HISTORICAL_QUALIFIERS_RE = re.compile(
    r"\b(?:snapshot|submission\s+gate|Phase\s+\d+\s+close|"
    r"(?:at|through)\s+v\d+\.\d+\.\d+\s+close|"
    r"accepted\s+across.*through\s+ADR-\d+|"
    r"closure\s+trail)\b",
    re.IGNORECASE | re.DOTALL,
)

# How many lines around a match to scan for historical qualifiers.
CONTEXT_WINDOW = 3


def actual_adr_count(decisions_dir: Path) -> int:
    """Count ADR files matching decisions/ADR-*.md."""
    return len(list(decisions_dir.glob("ADR-*.md")))


def should_skip(path: Path) -> bool:
    """Return True if path matches a skip pattern."""
    relative = str(path.relative_to(REPO_ROOT))
    return any(pattern in relative for pattern in SKIP_PATTERNS)


def is_historical_snapshot(lines: list[str], match_line_no: int) -> bool:
    """Return True if a CONTEXT_WINDOW around `match_line_no` contains a
    historical-snapshot qualifier."""
    start = max(0, match_line_no - 1 - CONTEXT_WINDOW)
    end = min(len(lines), match_line_no + CONTEXT_WINDOW)
    context = "\n".join(lines[start:end])
    return bool(HISTORICAL_QUALIFIERS_RE.search(context))


def audit_file(path: Path, actual_count: int) -> tuple[list[str], list[str]]:
    """Return (failures, info) lists for a single file.

    failures: current-claim mismatches (cause CI failure)
    info: historical-snapshot claims (reviewable, non-failing)
    """
    failures: list[str] = []
    info: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return failures, info  # skip binary files matched by glob

    rel = path.relative_to(REPO_ROOT)
    for line_no, line in enumerate(lines, start=1):
        for match in ADR_COUNT_RE.finditer(line):
            claimed = int(match.group(1))
            if claimed == actual_count:
                continue
            entry = (
                f"{rel}:{line_no} claims {claimed}, actual {actual_count} "
                f"(context: {line.strip()[:120]})"
            )
            if is_historical_snapshot(lines, line_no):
                info.append(entry)
            else:
                failures.append(entry)
    return failures, info


def main() -> int:
    decisions_dir = REPO_ROOT / "decisions"
    if not decisions_dir.is_dir():
        print(f"ERROR: {decisions_dir} not found", file=sys.stderr)
        return 2

    actual = actual_adr_count(decisions_dir)
    print(f"audit_adr_count_claims: actual ADR count = {actual}")

    surface_paths: set[Path] = set()
    for pattern in SURFACE_GLOBS:
        surface_paths.update(REPO_ROOT.glob(pattern))
    # Drop skipped paths.
    surface_paths = {p for p in surface_paths if not should_skip(p)}

    all_failures: list[str] = []
    all_info: list[str] = []
    for path in sorted(surface_paths):
        failures, info = audit_file(path, actual)
        all_failures.extend(failures)
        all_info.extend(info)

    if all_info:
        print(f"\nHISTORICAL SNAPSHOTS (informational; {len(all_info)} entries):")
        for entry in all_info:
            print(f"  INFO  {entry}")

    if all_failures:
        print(
            f"\nFAILURES (current-claim stale; {len(all_failures)} entries):",
            file=sys.stderr,
        )
        for entry in all_failures:
            print(f"  FAIL  {entry}", file=sys.stderr)
        return 1

    print(
        f"\naudit_adr_count_claims: clean "
        f"(scanned {len(surface_paths)} reader-facing surfaces; "
        f"{len(all_info)} historical-snapshot claim(s) noted)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
