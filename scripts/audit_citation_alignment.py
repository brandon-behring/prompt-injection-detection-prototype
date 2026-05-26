"""Audit reader-facing markdown for ADR-citation alignment misalignments.

Wraps `eval_toolkit.audit_citation_alignment.validate_citations` (shipped
in upstream v1.0.1; ports brandon-behring/eval-toolkit#73). Catches the
bug class where a reader-facing surface cites "per ADR-NNN" but the
cited ADR's actual subject doesn't match the surrounding claim category.

Motivating bug class: v1.3.2 P1-2 — `docs/REPRODUCIBILITY.md:76` cited
ADR-029 (test_markers) for a reproducibility-tier-lock claim. The actual
reproducibility-tier-lock ADR is ADR-034. v1.3.2 fixed the instance;
this validator is preemptive against the bug class.

Behavior:
  1. Walks `decisions/ADR-*.md` and parses frontmatter (`title:` + `slug:`)
     into `ADRSubject` records; categories inferred via the consumer's
     `CATEGORY_KEYWORDS` map.
  2. Globs reader-facing surfaces (top-level *.md / *.qmd + WRITEUP/*.md
     + docs/*.md). Skips CHANGELOG / SUBMISSION_AUDIT / decisions/ /
     transcripts/ / .venv/ / .quarto/.
  3. Invokes `validate_citations(...)` per file.
  4. Prints findings as a table to stderr.

Gate severity:
  - v1.3.7 (this release): SOFT — always exits 0; findings are
    informational. CI job uses `continue-on-error: true`.
  - v1.3.8 (planned): HARD — exits 1 on findings; CI removes
    `continue-on-error`.

Usage:
  uv run python scripts/audit_citation_alignment.py
  # OR via Makefile: make audit-citation-alignment

References
----------
- Upstream module: eval_toolkit.audit_citation_alignment.validate_citations
- Upstream issue: https://github.com/brandon-behring/eval-toolkit/issues/73
- Upstream PR: https://github.com/brandon-behring/eval-toolkit/pull/74
- Consumer plan: .scratch/v1-3-7-prestage-plan.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from eval_toolkit.audit_citation_alignment import (
    ADRSubject,
    extract_adr_subject_category,
    validate_citations,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DECISIONS_DIR = REPO_ROOT / "decisions"

# Reader-facing surfaces to audit. Globs relative to REPO_ROOT.
# Mirrors the SURFACE_GLOBS pattern from scripts/audit_adr_count_claims.py.
SURFACE_GLOBS = [
    "*.md",
    "*.qmd",
    "WRITEUP/*.md",
    "docs/*.md",
]

# Files/directories to skip even if matched by globs.
SKIP_PATTERNS = [
    "CHANGELOG.md",  # version-pinned historical citations are intentional
    "SUBMISSION_AUDIT.md",  # generated; may contain historical CLAIM citations
    "SUBMISSION.md",  # gitignored cover-letter draft; not a reader-facing claim
    "AUDIT_CLAUDE_",  # historical audit transcripts; describe bugs not claim them
    "_codex.md",  # gitignored Codex audit reports per .gitignore *_codex.md
    "draft.md",  # legacy v0.x draft; predates v1.0.0 schema
    "draft_review.md",  # legacy v0.x review draft
    "decisions/",  # ADRs themselves; immutable per CLAUDE.md
    "transcripts/",  # gitignored; operator-side QA
    ".venv/",
    ".quarto/",
]

# Consumer's claim-category keyword map.
# Pattern: first-match-wins; categories tested in dict-insertion order so
# more-specific categories should appear EARLIER. Substring match,
# case-insensitive (per upstream extract_adr_subject_category semantics).
#
# Initial seed at v1.3.7: derived from the v1.3.2 P1-2 bug surface area
# (test_markers ↔ reproducibility confusion) + the broader claim taxonomy
# visible across `decisions/`. Expand based on what `validate_citations`
# flags as None × None (no category match on either side) during real runs.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "reproducibility": ["reproduc", "tier ladder", "T0 ", "T1 ", "T3 "],
    "test_markers": ["marker", "smoke marker", "unit marker", "integration marker"],
    "cost": ["cost", "budget", "GPU spend", "compute spend"],
    "calibration": ["calibrat", "ECE", "Brier", "isotonic", "Platt"],
    "contamination": ["contaminat", "disjoint", "verified_disjoint", "backbone-partial"],
    "threshold": ["threshold", "FPR", "operating point", "TargetFPRSelector"],
    "leakage": ["leakage", "SHA-256", "TF-IDF cosine", "near-dedup"],
    "data": ["dataset", "BIPIA", "InjecAgent", "JBB", "XSTest", "LMSYS", "HackAPrompt"],
    "training": ["LoRA", "frozen probe", "full-FT", "ModernBERT", "DeBERTa"],
    "evaluation": ["AUPRC", "AUROC", "bootstrap", "DeLong", "MDE"],
    "reading_guide": ["reading guide", "newcomer path", "reviewer path"],
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
ADR_FILE_RE = re.compile(r"^ADR-(\d{3})-(.+)\.md$")


def parse_adr_frontmatter(adr_path: Path) -> ADRSubject | None:
    """Parse ADR frontmatter into an ADRSubject.

    Parameters
    ----------
    adr_path : Path
        Path to an ADR-NNN-*.md file.

    Returns
    -------
    ADRSubject | None
        Subject with title + slug + category (inferred via
        `extract_adr_subject_category`). Returns None for:
        non-ADR-NNN filenames, files lacking YAML frontmatter, files
        with no `title:` field, or binary files.
    """
    match = ADR_FILE_RE.match(adr_path.name)
    if not match:
        return None
    adr_id = match.group(1)
    slug_from_filename = match.group(2)

    try:
        text = adr_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None

    fm_match = FRONTMATTER_RE.match(text)
    if not fm_match:
        return None
    fm_body = fm_match.group(1)

    title = ""
    slug = slug_from_filename
    for raw_line in fm_body.split("\n"):
        line = raw_line.strip()
        if line.startswith("title:"):
            title = line[len("title:") :].strip().strip('"').strip("'")
        elif line.startswith("slug:"):
            slug = line[len("slug:") :].strip().strip('"').strip("'")

    if not title:
        return None

    category = extract_adr_subject_category(title, slug, CATEGORY_KEYWORDS)
    return ADRSubject(adr_id=adr_id, title=title, slug=slug, category=category)


def build_adr_subjects() -> dict[str, ADRSubject]:
    """Walk `decisions/ADR-*.md`; return `{adr_id: ADRSubject}`."""
    subjects: dict[str, ADRSubject] = {}
    for adr_path in sorted(DECISIONS_DIR.glob("ADR-*.md")):
        subject = parse_adr_frontmatter(adr_path)
        if subject is not None:
            subjects[subject.adr_id] = subject
    return subjects


def should_skip(path: Path) -> bool:
    """Return True if path matches a skip pattern."""
    relative = str(path.relative_to(REPO_ROOT))
    return any(pattern in relative for pattern in SKIP_PATTERNS)


def main() -> int:
    """Run the citation-alignment audit; exit 0 (SOFT gate at v1.3.7)."""
    if not DECISIONS_DIR.is_dir():
        print(f"ERROR: {DECISIONS_DIR} not found", file=sys.stderr)
        return 2

    adr_subjects = build_adr_subjects()
    print(f"audit_citation_alignment: built {len(adr_subjects)} ADR subjects from decisions/")

    surface_paths: set[Path] = set()
    for pattern in SURFACE_GLOBS:
        surface_paths.update(REPO_ROOT.glob(pattern))
    surface_paths = {p for p in surface_paths if not should_skip(p)}

    all_findings = []
    for path in sorted(surface_paths):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        findings = validate_citations(
            markdown_text=text,
            markdown_path=path,
            adr_subjects=adr_subjects,
            category_keywords=CATEGORY_KEYWORDS,
        )
        all_findings.extend(findings)

    if all_findings:
        print(
            f"\nCITATION MISALIGNMENTS (informational at v1.3.7 SOFT gate; "
            f"promotes to HARD at v1.3.8; {len(all_findings)} entries):",
            file=sys.stderr,
        )
        for f in all_findings:
            rel = f.file.relative_to(REPO_ROOT) if f.file.is_absolute() else f.file
            print(
                f"  WARN  {rel}:{f.line} cites ADR-{f.cited_adr_id} "
                f"(claim={f.claim_category}, actual={f.adr_actual_category}) "
                f"context: {f.surrounding_text[:120]}",
                file=sys.stderr,
            )
    else:
        print(
            f"\naudit_citation_alignment: clean "
            f"(scanned {len(surface_paths)} reader-facing surfaces; "
            f"0 citation misalignments found)"
        )

    # SOFT GATE at v1.3.7: always exit 0; findings are informational only.
    # Promotes to `return 1 if all_findings else 0` at v1.3.8 (HARD gate).
    return 0


if __name__ == "__main__":
    sys.exit(main())
