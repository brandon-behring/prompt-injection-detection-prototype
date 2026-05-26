"""Audit reader-facing markdown for (detector, metric, value) binding misalignments.

Wraps `eval_toolkit.audit_value_bindings.validate_reader_value_bindings`
(shipped in upstream v1.0.3; ports brandon-behring/eval-toolkit#71).
Catches the bug class where reader prose pairs a detector name with the
WRONG canonical value — both values are present in the source-of-truth
table, but the binding is misordered.

Motivating bug (V1.3.1 ADR-080 audit-fix, 2026-05-22):
  `WRITEUP_NARRATIVE.md:38` said "TF-IDF + logistic regression baseline
  reaches 0.974 AUPRC on balanced direct-versus-benign validation."
  Canonical: TF-IDF direct val AUPRC = 0.971; LoRA direct val AUPRC =
  0.974. Both values exist; the bug is the wrong (detector, value)
  pairing. The existing `scripts/audit_numbers.py` + `audit_writeup_numbers.py`
  validate VALUES against source data; this validator extends to
  validate BINDINGS (the (detector, metric, value) triple itself).

Behavior:
  1. Globs reader-facing surfaces (top-level *.md / *.qmd + WRITEUP/*.md
     + docs/*.md). Skips CHANGELOG / SUBMISSION_AUDIT / decisions/ /
     transcripts/ / .venv/ / .quarto/.
  2. Invokes `validate_reader_value_bindings(files=..., bindings=BINDINGS,
     detector_aliases=..., metric_aliases=...)`.
  3. Prints violations + match coverage as a table to stderr.

Gate severity:
  - v1.3.8 (this release): SOFT — always exits 0; findings are
    informational. CI step uses `continue-on-error: true`.
  - v1.3.X (future): HARD — exits 1 on violations; CI removes
    `continue-on-error` per /exploring-options Q2 lock.

Usage:
  uv run python scripts/audit_value_bindings.py
  # OR via Makefile: make audit-value-bindings

References
----------
- Upstream module: eval_toolkit.audit_value_bindings.validate_reader_value_bindings
- Upstream issue: https://github.com/brandon-behring/eval-toolkit/issues/71
- Upstream release: https://github.com/brandon-behring/eval-toolkit/releases/tag/v1.0.3
- Consumer issue origin: V1.3.1 ADR-080 patch closure (WRITEUP_NARRATIVE TF-IDF/LoRA mis-binding)
"""

from __future__ import annotations

import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from eval_toolkit.audit_value_bindings import (
    ValueBindingsReport,
    Violation,
    validate_reader_value_bindings,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Reader-facing surfaces to audit. Mirrors the SURFACE_GLOBS pattern from
# scripts/audit_citation_alignment.py + audit_adr_count_claims.py.
SURFACE_GLOBS = [
    "*.md",
    "*.qmd",
    "WRITEUP/*.md",
    "docs/*.md",
]

# Files/directories to skip even if matched by globs.
SKIP_PATTERNS = [
    "CHANGELOG.md",  # version-pinned historical values are intentional
    "SUBMISSION_AUDIT.md",  # generated; may quote historical CLAIM values
    "decisions/",  # ADRs themselves; immutable per CLAUDE.md
    "transcripts/",  # gitignored; operator-side QA
    ".venv/",
    ".quarto/",
]

# Consumer's canonical (detector, metric) -> expected_value table.
# Pattern: keys are canonical identifiers; surface-form patterns live
# in DETECTOR_ALIASES + METRIC_ALIASES below.
#
# Initial seed at v1.3.8 — focused on the V1.3.1 ADR-080 motivating bug
# (TF-IDF mis-bound to LoRA's 0.974). Per /exploring-options Q3 lock,
# kept narrow at v1.3.8 SOFT-gate phase; expansion deferred to HARD-gate
# promotion patch (which will add the remaining canonical headline
# values across all 4 trained rungs × the key reported metrics).
BINDINGS: Mapping[tuple[str, str], float] = {
    # V1.3.1 ADR-080 motivating case (the bug that surfaced this validator).
    # Canonical source: src/eval/slice_analysis.py results;
    # cross-checked against RESULTS.md headline table.
    ("TF-IDF", "AUPRC"): 0.971,
    ("LoRA", "AUPRC"): 0.974,
}

# Detector surface-form aliases. Values are REGEX patterns (so e.g. `+`
# must be escaped as `\\+` in Python strings).
DETECTOR_ALIASES: Mapping[str, Sequence[str]] = {
    "TF-IDF": [
        r"TF-IDF",
        r"TFIDF",
        r"tfidf",
        r"TF-IDF \+ LR",
        r"TF-IDF \+ logistic regression",
    ],
    "LoRA": [
        r"LoRA",
        r"lora",
    ],
}

# Metric surface-form aliases. Pattern as above.
METRIC_ALIASES: Mapping[str, Sequence[str]] = {
    "AUPRC": [
        r"AUPRC",
        r"AU-PRC",
        r"PR-AUC",
        r"PR AUC",
    ],
}


def should_skip(path: Path) -> bool:
    """Return True if path matches a skip pattern."""
    relative = str(path.relative_to(REPO_ROOT))
    return any(pattern in relative for pattern in SKIP_PATTERNS)


def gather_surfaces() -> list[Path]:
    """Walk SURFACE_GLOBS; return filtered list of reader-facing markdown files."""
    paths: set[Path] = set()
    for pattern in SURFACE_GLOBS:
        paths.update(REPO_ROOT.glob(pattern))
    return sorted(p for p in paths if not should_skip(p))


def format_violation(violation: Violation) -> str:
    """Pretty-print a single Violation for stderr output."""
    try:
        rel = violation.file.relative_to(REPO_ROOT)
    except ValueError:
        rel = violation.file
    return (
        f"  WARN  {rel}:{violation.line} "
        f"{violation.detector}/{violation.metric} = {violation.found_value} "
        f"(expected {violation.expected_value}) "
        f"context: {violation.surrounding_text[:120]}"
    )


def main() -> int:
    """Run the value-bindings audit; exit 0 (SOFT gate at v1.3.8)."""
    surface_paths = gather_surfaces()
    print(
        f"audit_value_bindings: scanning {len(surface_paths)} reader-facing "
        f"surfaces against {len(BINDINGS)} canonical bindings"
    )

    report: ValueBindingsReport = validate_reader_value_bindings(
        files=surface_paths,
        bindings=BINDINGS,
        detector_aliases=DETECTOR_ALIASES,
        metric_aliases=METRIC_ALIASES,
    )

    if report.violations:
        print(
            f"\nVALUE-BINDING VIOLATIONS (informational at v1.3.8 SOFT gate; "
            f"promotes to HARD at v1.3.X; {len(report.violations)} entries):",
            file=sys.stderr,
        )
        for v in report.violations:
            print(format_violation(v), file=sys.stderr)
    else:
        print(
            f"\naudit_value_bindings: clean "
            f"({len(report.matched)} match(es); "
            f"coverage {report.coverage:.0%} of canonical bindings; "
            f"0 violations)"
        )

    # SOFT GATE at v1.3.8: always exit 0 regardless of violations or coverage.
    # Promotes to `return 1 if report.violations else 0` at a future v1.3.X.
    return 0


if __name__ == "__main__":
    sys.exit(main())
