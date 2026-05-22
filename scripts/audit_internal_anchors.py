# mypy: disable-error-code="no-untyped-call"
"""Audit intra-site markdown anchor links for resolvability.

Per the v1.3.1 audit Q8 lock — preventive guardrail for the dead-anchor class
of error surfaced by the 2026-05-22 fresh-eyes audit. Catches the exact class
of failure Lane-3 found: `[link text](./WRITEUP.md#results)` where the target
file has no anchor `results`. The full CI lychee run catches this too, but
post-tag; this hook catches it pre-commit.

Scope (intentionally narrow vs full lychee):
- Reader-facing markdown surfaces only: top-level `*.md` + `*.qmd` + spokes
  under `WRITEUP/` + `docs/*.md`. Not: `decisions/ADR-*.md` (immutable; if a
  slug is wrong it falls under the ADR-067 / ADR-071 sweep, not this hook).
- Internal links only: `./path.md#anchor` or `../path.md#anchor` patterns.
  External URLs (`https://...`) are out of scope (lychee in CI handles those).
- Anchor format: Quarto's slug-from-heading convention (lowercase ASCII; non-
  alphanumeric runs collapsed to single hyphens; leading section-number prefix
  preserved without dot, e.g. `## 4.6 Foo Bar` -> `46-foo-bar`).

Run from repo root:
    uv run python scripts/audit_internal_anchors.py        # full check
    uv run python scripts/audit_internal_anchors.py --quiet
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Surfaces this hook checks. Decisions ADRs deliberately excluded (immutable;
# slug-typo class handled by ADR-067-class narrow relaxations).
INPUT_GLOBS = [
    "*.md",
    "*.qmd",
    "WRITEUP/*.md",
    "docs/*.md",
]

# Markdown link pattern: [text](path#anchor) or [text](#anchor)
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

# Heading capture: # Heading text  (1-6 #s).
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*(\{[^}]*\})?\s*$", re.MULTILINE)

# Optional explicit anchor in {.cls #id} or {#id}.
EXPLICIT_ID_RE = re.compile(r"\{[^}]*#([A-Za-z0-9_-]+)[^}]*\}")


def heading_to_anchor(text: str) -> str:
    """Replicate Pandoc / Quarto's auto-identifier slug-from-heading convention.

    Pandoc's algorithm (https://pandoc.org/MANUAL.html#extension-auto_identifiers):
    1. Remove formatting (links, emphasis, etc.)
    2. Remove all non-alphanumeric chars except `_`, `-`, `.`
    3. Replace whitespace runs with single hyphen
    4. Lowercase
    5. Remove everything up to the first letter (identifiers may not begin
       with a digit or punctuation)

    Observed Quarto behavior matches this. Critically: a heading like
    `## 4.6 Validation thresholds are fragile` yields anchor
    `validation-thresholds-are-fragile`, NOT `46-validation-thresholds-are-fragile`.
    """
    # Strip markdown link [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Strip backticks, asterisks, underscores (formatting markers)
    text = re.sub(r"[`*]", "", text)
    # Step 2: remove disallowed chars (keep letters, digits, _, -, .)
    text = re.sub(r"[^A-Za-z0-9_.\-\s]", "", text)
    # Step 3: whitespace runs -> single hyphen
    text = re.sub(r"\s+", "-", text)
    # Step 4: lowercase
    text = text.lower()
    # Step 5: drop dots (e.g., "4.7" → "47"); Quarto's auto-identifier strips them
    text = text.replace(".", "")
    # Step 6: drop any leading section-number prefix of the form `\d+(\.\d+)*-`
    # Quarto strips numeric/section prefixes when followed by hyphen ("4-results"
    # → "results"; "46-validation-..." → "validation-..."). Preserves
    # alphanumeric leads like "1b-ablation-..." which Quarto keeps.
    text = re.sub(r"^[0-9]+-", "", text)
    return text.strip("-")


def collect_anchors_for_file(path: Path) -> set[str]:
    """Return the set of resolvable anchors in `path`."""
    text = path.read_text()
    anchors: set[str] = set()
    for match in HEADING_RE.finditer(text):
        _level, heading, attrs = match.groups()
        # Explicit attribute id wins if present
        explicit = EXPLICIT_ID_RE.search(attrs or "")
        if explicit:
            anchors.add(explicit.group(1))
        else:
            anchors.add(heading_to_anchor(heading))
    # Inline explicit ids on non-heading lines (e.g., `{#some-id}`)
    for m in EXPLICIT_ID_RE.finditer(text):
        anchors.add(m.group(1))
    return anchors


def collect_links_from_file(path: Path) -> list[tuple[str, str, str, int]]:
    """Return (link_text, target_path, anchor, line_no) tuples.

    Only intra-site links (relative paths or pure fragments) are emitted.
    External URLs (http/https/mailto/etc.) are skipped.
    """
    text = path.read_text()
    out = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for m in LINK_RE.finditer(line):
            label, target = m.group(1), m.group(2)
            if "://" in target or target.startswith("mailto:") or target.startswith("tel:"):
                continue
            # Split path#anchor
            if "#" in target:
                target_path, anchor = target.split("#", 1)
            else:
                target_path, anchor = target, ""
            out.append((label, target_path, anchor, line_no))
    return out


def resolve_target(source: Path, target_path: str) -> Path | None:
    """Resolve a relative-link target to an absolute Path; None if external."""
    if not target_path:
        return source  # pure fragment, same file
    # Quarto rewrites .md -> .html on render, but in source we have .md
    if target_path.startswith("/"):
        candidate = REPO_ROOT / target_path.lstrip("/")
    else:
        candidate = (source.parent / target_path).resolve()
    # Also try the .html -> .md fallback for cross-renders (rarely needed in
    # *source* MD but defensive)
    if not candidate.exists() and candidate.suffix == ".html":
        candidate = candidate.with_suffix(".md")
    return candidate


def audit() -> tuple[list[str], list[str]]:
    """Run audit; return (failures, info_notes)."""
    failures: list[str] = []
    info_notes: list[str] = []

    files: list[Path] = []
    for pattern in INPUT_GLOBS:
        files.extend(sorted(REPO_ROOT.glob(pattern)))
    # Deduplicate (top-level glob may catch decisions/ etc. via */* — defensive)
    files = sorted({f for f in files if f.is_file()})

    # Cache anchors by file
    anchors_cache: dict[Path, set[str]] = {}

    def anchors_for(p: Path) -> set[str]:
        if p not in anchors_cache:
            anchors_cache[p] = collect_anchors_for_file(p)
        return anchors_cache[p]

    # Track per-file failure count for grouped reporting
    grouped: dict[Path, list[str]] = defaultdict(list)

    for source in files:
        for label, target_path, anchor, line_no in collect_links_from_file(source):
            target = resolve_target(source, target_path)
            if target is None:
                continue
            # Target file must exist (or be the source itself for pure fragments)
            if not target.exists() and target_path:
                # Allow .html targets when the .md sibling exists (Quarto rewrite)
                md_alt = target.with_suffix(".md") if target.suffix == ".html" else None
                if md_alt and md_alt.exists():
                    target = md_alt
                else:
                    msg = f"{source.relative_to(REPO_ROOT)}:{line_no}: link target file missing: '{target_path}' (label={label!r})"
                    grouped[source].append(msg)
                    continue
            # If there's an anchor, check it resolves on the target file
            if anchor:
                # Only check anchors on .md / .qmd targets (HTML / asset files
                # we cannot statically verify without rendering).
                if target.suffix in (".md", ".qmd"):
                    available = anchors_for(target)
                    if anchor not in available:
                        msg = (
                            f"{source.relative_to(REPO_ROOT)}:{line_no}: dead anchor "
                            f"#{anchor} on {target.relative_to(REPO_ROOT)} (label={label!r})"
                        )
                        grouped[source].append(msg)

    for source, msgs in sorted(grouped.items()):
        failures.extend(msgs)

    info_notes.append(f"audit_internal_anchors: scanned {len(files)} files")

    return failures, info_notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="Suppress info notes on success")
    args = parser.parse_args()

    failures, info_notes = audit()

    if failures:
        print(f"audit_internal_anchors: FAILED ({len(failures)} dead anchors / missing targets)")
        for f in failures[:50]:
            print(f"  FAIL  {f}")
        if len(failures) > 50:
            print(f"  ... and {len(failures) - 50} more (truncated)")
        return 1

    if not args.quiet:
        for note in info_notes:
            print(f"INFO  {note}")
    print("audit_internal_anchors: all internal anchors resolved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
