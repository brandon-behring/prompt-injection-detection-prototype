#!/usr/bin/env python3
"""Regenerate SUBMISSION_AUDIT.md from decisions/ADR-*.md frontmatter.

ADRs are the source of truth for claim status. This script reads each
ADR's YAML frontmatter (claim_id, claim, source, status, acceptance
criterion, closing commit) and regenerates SUBMISSION_AUDIT.md so the
audit register stays drift-free.

Usage:
    python scripts/regenerate_audit.py          # write SUBMISSION_AUDIT.md
    python scripts/regenerate_audit.py --check  # exit 1 if SUBMISSION_AUDIT.md is stale
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
ADR_DIR = REPO / "decisions"
AUDIT = REPO / "SUBMISSION_AUDIT.md"


def parse_adr(path: pathlib.Path) -> dict[str, object] | None:
    """Extract YAML frontmatter from an ADR file."""
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    parsed = yaml.safe_load(m.group(1))
    return parsed if isinstance(parsed, dict) else None


def render() -> str:
    """Build SUBMISSION_AUDIT.md content from ADR frontmatter."""
    rows: list[str] = []
    for adr in sorted(ADR_DIR.glob("ADR-*.md")):
        fm = parse_adr(adr)
        if fm is None or "claim_id" not in fm:
            continue
        rows.append(
            f"| {fm['claim_id']} "
            f"| {fm.get('claim', '')} "
            f"| {fm.get('source', '')} "
            f"| {fm.get('status', 'OPEN')} "
            f"| {fm.get('acceptance_criterion', '')} "
            f"| {fm.get('closing_commit', '')} |"
        )

    header = (
        "# Submission audit — claim status ledger\n\n"
        "*Generated from `decisions/ADR-*.md` frontmatter. Do not edit "
        "directly; run `python scripts/regenerate_audit.py` to regenerate.*\n\n"
        "| Claim ID | Claim | Source | Status | Acceptance criterion | "
        "Closing commit/ADR |\n"
        "|---|---|---|---|---|---|\n"
    )
    body = "\n".join(rows) if rows else "| (no ADRs yet) | | | OPEN | | |"
    return header + body + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if SUBMISSION_AUDIT.md is out of sync with ADRs",
    )
    args = parser.parse_args()

    new = render()
    if args.check:
        if AUDIT.exists() and AUDIT.read_text() == new:
            return 0
        print(
            "SUBMISSION_AUDIT.md is out of sync with ADRs. "
            "Run `python scripts/regenerate_audit.py` to regenerate.",
            file=sys.stderr,
        )
        return 1
    AUDIT.write_text(new)
    print(f"wrote {AUDIT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
