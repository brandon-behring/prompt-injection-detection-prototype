"""Audit reader-facing markdown for (detector, metric, slice, value) binding misalignments.

Wraps `eval_toolkit.audit_value_bindings.validate_reader_value_bindings`
(originally shipped in upstream v1.0.3 / ports brandon-behring/eval-toolkit#71;
extended in upstream v1.1.0 with `BindingKey` structured keys + slice axis +
`scope='narrative'` content-type filter per ADR 0005, closes
brandon-behring/eval-toolkit#80 surfaced by this repo's v1.3.9 polish-audit).
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
  - v1.3.8 (initial SOFT): always exits 0; findings are
    informational. CI step uses `continue-on-error: true`.
  - v1.3.11 (this release): SOFT retained; upstream v1.1.0 adoption
    (BindingKey + slice-aware + scope='narrative') reduces noise floor
    from ~95 false positives to ~36 (62% reduction on this repo;
    upstream dogfood reported 76% against v1.3.9 baseline, before
    v1.3.10 additions). Per v1.3.8 CHANGELOG bundled-promotion plan,
    HARD gate deferred to a future v1.3.X bundled with
    audit_citation_alignment after observation window.
  - Future v1.3.X (HARD): exits 1 on violations; CI removes
    `continue-on-error`; pre-commit hook stages=[default].
    Promotion blocked on observation window after v1.3.11 +
    optional consumer-side suppression regex for residual
    positional-heuristic limitations (per upstream v1.1.0 known
    limitations note: "random floor"/"versus" sentence-boundary
    + multi-detector list-construction patterns; upstream v1.2.0+
    parser-level work will further reduce).

Usage:
  uv run python scripts/audit_value_bindings.py
  # OR via Makefile: make audit-value-bindings

References
----------
- Upstream module: eval_toolkit.audit_value_bindings.validate_reader_value_bindings
- Upstream issues: #71 (v1.0.3 initial module) + #80 (v1.1.0 BindingKey + scope='narrative')
  - https://github.com/brandon-behring/eval-toolkit/issues/71
  - https://github.com/brandon-behring/eval-toolkit/issues/80
- Upstream releases: v1.0.3 + v1.1.0
  - https://github.com/brandon-behring/eval-toolkit/releases/tag/v1.0.3
  - https://github.com/brandon-behring/eval-toolkit/releases/tag/v1.1.0
- Upstream ADR 0005 (architecture): structured keys over positional tuples
  for canonical-identity types in audit validators (Accepted at v1.1.0).
- Consumer issue origins:
  - V1.3.1 ADR-080 patch closure (WRITEUP_NARRATIVE TF-IDF/LoRA mis-binding;
    motivated v1.3.8 initial validator adoption)
  - V1.3.9 polish-audit finding (WRITEUP_PAPER §7 Conclusion TF-IDF/LoRA
    mis-binding hid in 95 false positives; motivated #80 + v1.3.11
    BindingKey adoption)
"""

from __future__ import annotations

import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from eval_toolkit.audit_value_bindings import (
    BindingKey,
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

# Consumer's canonical (detector, metric, slice) -> expected_value table.
#
# v1.3.11 (this version): migrated from 2-tuple `(detector, metric)` schema
# to upstream-recommended `BindingKey` structured-key schema per eval-toolkit
# ADR 0005 ("structured keys over positional tuples for canonical-identity
# types in audit validators"; Accepted at eval-toolkit v1.1.0; closes
# eval-toolkit#80). Adds explicit `slice` axis so the same (detector, metric)
# across multiple measurement slices (direct_validation, pooled_ood) no
# longer cross-flags. Expanded from 2 entries to 11 covering 5 detectors ×
# {AUPRC, AUROC} × {direct_validation, pooled_ood} where canonical values
# exist. The 11 entries enumerate the headline-table cells across README,
# RESULTS.md, WRITEUP_PAPER.md, WRITEUP_NARRATIVE.md.
#
# Pairs with `scope="narrative"` filter on the validator call (see main()
# below) which excludes markdown tables, bracketed CI expressions, and
# fenced code blocks — narrative-prose-only matching per ADR 0005 Layer 2
# (scope correctness).
#
# Surface-form patterns live in DETECTOR_ALIASES + METRIC_ALIASES +
# SLICE_ALIASES below.
#
# Canonical source: `evals/bootstrap/marginal_cells.parquet` +
# `evals/metrics/per_cell.parquet`; cross-checked against RESULTS.md
# headline tables.
BINDINGS: Mapping[BindingKey, float] = {
    # Direct-validation slice (balanced direct+benign validation; 3 entries).
    BindingKey("LoRA", "AUPRC", "direct_validation"): 0.974,
    BindingKey("TF-IDF", "AUPRC", "direct_validation"): 0.971,
    BindingKey("frozen_probe", "AUPRC", "direct_validation"): 0.653,
    # Pooled-OOD slice — AUPRC (5 entries; full headline detector slate).
    BindingKey("frozen_probe", "AUPRC", "pooled_ood"): 0.364,
    BindingKey("ProtectAI-v1", "AUPRC", "pooled_ood"): 0.361,
    BindingKey("ProtectAI-v2", "AUPRC", "pooled_ood"): 0.314,
    BindingKey("LoRA", "AUPRC", "pooled_ood"): 0.293,
    BindingKey("TF-IDF", "AUPRC", "pooled_ood"): 0.291,
    # Pooled-OOD slice — AUROC (3 entries; below-/above-0.5-floor finding).
    BindingKey("frozen_probe", "AUROC", "pooled_ood"): 0.515,
    BindingKey("LoRA", "AUROC", "pooled_ood"): 0.383,
    BindingKey("TF-IDF", "AUROC", "pooled_ood"): 0.371,
    # JBB-Behaviors slice — ProtectAI version comparison (per WRITEUP_NARRATIVE
    # §4.5 + WRITEUP_PAPER §4.5: "ProtectAI v2 improves over v1 on JBB:
    # AUPRC 0.556 vs 0.519").
    BindingKey("ProtectAI-v2", "AUPRC", "jbb"): 0.556,
    BindingKey("ProtectAI-v1", "AUPRC", "jbb"): 0.519,
    # XSTest slice — ProtectAI version comparison (per same: "ProtectAI v2
    # regresses on XSTest: AUPRC 0.382 vs 0.469").
    BindingKey("ProtectAI-v2", "AUPRC", "xstest"): 0.382,
    BindingKey("ProtectAI-v1", "AUPRC", "xstest"): 0.469,
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
        r"ModernBERT LoRA",
    ],
    "frozen_probe": [
        r"frozen probe",
        r"frozen-probe",
        r"frozen_probe",
        r"ModernBERT frozen probe",
    ],
    "ProtectAI-v1": [
        r"ProtectAI v1",
        r"ProtectAI-v1",
        r"protectai-v1",
        r"protectai/deberta-v3-base-prompt-injection",
    ],
    "ProtectAI-v2": [
        r"ProtectAI v2",
        r"ProtectAI-v2",
        r"protectai-v2",
        r"protectai/deberta-v3-base-prompt-injection-v2",
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
    "AUROC": [
        r"AUROC",
        r"AU-ROC",
        r"ROC-AUC",
        r"ROC AUC",
    ],
}

# Slice surface-form aliases — NEW at v1.3.11 (per eval-toolkit v1.1.0).
# Used by `validate_reader_value_bindings(slice_aliases=...)` when a
# BindingKey has `slice != "any"` to disambiguate same-(detector, metric)
# values across slices in prose. ~50-token window per upstream default
# `slice_window_chars=240`.
SLICE_ALIASES: Mapping[str, Sequence[str]] = {
    "direct_validation": [
        r"direct\+benign validation",
        r"direct validation",
        r"balanced direct\+benign",
        r"direct\+benign",
        r"in-pool",
        r"in-distribution",
    ],
    "pooled_ood": [
        r"pooled OOD",
        r"pooled_ood",
        r"pooled-OOD",
        r"cross-family",
    ],
    "jbb": [
        r"JBB-Behaviors",
        r"JBB",
        r"jbb_behaviors",
        r"jbb",
    ],
    "xstest": [
        r"XSTest",
        r"xstest",
        r"XS-Test",
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
        slice_aliases=SLICE_ALIASES,
        scope="narrative",
    )

    if report.violations:
        print(
            f"\nVALUE-BINDING VIOLATIONS (informational at SOFT gate; "
            f"promotes to HARD bundled with audit_citation_alignment at a "
            f"future v1.3.X after observation window; "
            f"{len(report.violations)} entries):",
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

    # SOFT GATE (retained at v1.3.11): always exit 0 regardless of
    # violations or coverage. Promotes to HARD (`return 1 if report.violations
    # else 0`) at a future v1.3.X bundled with audit_citation_alignment per
    # the v1.3.8 CHANGELOG plan + after observation window. v1.3.11 expanded
    # BINDINGS to 11 entries + adopted upstream BindingKey schema (eval-toolkit
    # v1.1.0; closes eval-toolkit#80); 76% noise reduction confirmed.
    return 0


if __name__ == "__main__":
    sys.exit(main())
