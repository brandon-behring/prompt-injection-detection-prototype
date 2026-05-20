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
import textwrap

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


def normalize(value: object) -> str:
    """Return one-line text suitable for Markdown paragraphs."""
    return re.sub(r"\s+", " ", str(value or "").strip())


def wrap(value: object, width: int = 100) -> str:
    """Wrap generated prose so the audit does not become one unreadable line."""
    text = normalize(value)
    if not text:
        return "_Not recorded._"
    return textwrap.fill(text, width=width, break_long_words=False, break_on_hyphens=False)


def adr_sort_key(item: tuple[pathlib.Path, dict[str, object]]) -> tuple[int, str]:
    path, fm = item
    try:
        return (int(path.name.split("-", 2)[1]), path.name)
    except ValueError:
        try:
            return (int(str(fm.get("adr_id", ""))), path.name)
        except ValueError:
            return (9999, path.name)


def adr_label_from_path(path: pathlib.Path) -> str:
    try:
        return f"ADR-{int(path.name.split('-', 2)[1]):03d}"
    except ValueError:
        return path.stem


def render() -> str:
    """Build SUBMISSION_AUDIT.md content from ADR frontmatter."""
    records: list[tuple[pathlib.Path, dict[str, object]]] = []
    for adr in sorted(ADR_DIR.glob("ADR-*.md")):
        fm = parse_adr(adr)
        if fm is None or "claim_id" not in fm:
            continue
        records.append((adr, fm))

    records.sort(key=adr_sort_key)

    header = (
        "# Submission audit — claim status ledger\n\n"
        "> **How to read this page.** This is a generated audit ledger for "
        "reviewers who want to trace claims back to decision records. It is "
        "not the main narrative. Start with `README.md`, `RESULTS.md`, or "
        "`WRITEUP.md` for the project story.\n\n"
        "*Generated from `decisions/ADR-*.md` frontmatter. Do not edit this "
        "file directly; update the ADR frontmatter or this generator, then run "
        "`python scripts/regenerate_audit.py`.*\n\n"
        "## Claim index\n\n"
        "| Claim ID | ADR | Status | Closing commit/ADR |\n"
        "|---|---|---|---|\n"
    )
    if not records:
        return header + "| (no ADRs yet) | | OPEN | |\n"

    index_rows: list[str] = []
    detail_sections: list[str] = ["\n## Claim details\n"]
    for adr, fm in records:
        claim_id = normalize(fm["claim_id"])
        status = normalize(fm.get("status", "OPEN"))
        closing_commit = normalize(fm.get("closing_commit", ""))
        title = normalize(fm.get("title", adr.stem))
        adr_link = f"[{adr_label_from_path(adr)}]({adr.relative_to(REPO).as_posix()})"
        index_rows.append(f"| {claim_id} | {adr_link} | {status} | {closing_commit} |")

        detail_sections.append(
            "\n"
            '<div class="ledger-detail">\n\n'
            f"### {claim_id} - {adr_link}: {title}\n\n"
            f"**Status**: {status}\n\n"
            f"**Source**: {normalize(fm.get('source', '')) or '_Not recorded._'}\n\n"
            f"**Closing commit/ADR**: {closing_commit or '_Not recorded._'}\n\n"
            "**Claim**\n\n"
            f"{wrap(fm.get('claim', ''))}\n\n"
            "**Acceptance criterion**\n\n"
            f"{wrap(fm.get('acceptance_criterion', ''))}\n\n"
            "</div>\n"
        )

    return header + "\n".join(index_rows) + "\n" + "\n".join(detail_sections)


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
