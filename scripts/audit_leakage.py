"""Standalone CLI verifying that `evals/leakage_report.json` shows clean.

Wraps the leakage-audit pattern already enforced in CI via the
`leakage` job in `.github/workflows/ci.yml` so operators can run the
same check locally:

    python scripts/audit_leakage.py            # human-readable summary; exit 0/1
    python scripts/audit_leakage.py --check    # CI mode; exit 0 on clean else 1

Per the ADR-016 + ADR-039 gate 3 + ADR-043 leakage discipline. The
upstream primitives (`eval_toolkit.leakage.CrossSplitLeakageCheck` +
`run_leakage_checks`) compute the report; this script verifies the
persisted artifact at `evals/leakage_report.json` is clean. Decoupled
from the compute pipeline so reviewers can verify the gate without
running the full data pipeline.

Per the no-emoji invariant; pure ASCII output.

Landed at v1.0.6 per /exploring-options batch 6 Q1 (§1.5 close).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

LEAKAGE_REPORT_PATH = Path("evals/leakage_report.json")


def _load_report(path: Path) -> dict[str, Any]:
    """Load + minimally validate the leakage report JSON.

    Parameters
    ----------
    path : Path
        Path to the report JSON. Default `evals/leakage_report.json`.

    Returns
    -------
    dict[str, Any]
        The parsed report.

    Raises
    ------
    FileNotFoundError
        If the report file does not exist.
    ValueError
        If the report is not a JSON object or lacks `leakage_clean`.
    """
    if not path.exists():
        raise FileNotFoundError(f"leakage report not found at {path}")
    report: Any = json.loads(path.read_text())
    if not isinstance(report, dict):
        raise ValueError(f"leakage report at {path} is not a JSON object")
    if "leakage_clean" not in report:
        raise ValueError(f"leakage report at {path} missing required key `leakage_clean`")
    return report


def main(argv: list[str] | None = None) -> int:
    """Run the leakage audit; return exit code 0 on clean, 1 otherwise.

    Parameters
    ----------
    argv : list[str] | None
        Argv list (for testing); defaults to sys.argv[1:].

    Returns
    -------
    int
        0 if `leakage_clean=True` in the report; 1 otherwise.
    """
    parser = argparse.ArgumentParser(
        description="Verify evals/leakage_report.json shows leakage_clean=True"
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=LEAKAGE_REPORT_PATH,
        help=f"Path to leakage report JSON (default: {LEAKAGE_REPORT_PATH})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="CI mode: minimal output; exit 0 on clean, 1 on fail",
    )
    args = parser.parse_args(argv)

    try:
        report = _load_report(args.report)
    except (FileNotFoundError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    leakage_clean: bool = bool(report.get("leakage_clean", False))
    n_exact: int = int(report.get("total_exact_hash_overlaps", -1))
    n_cosine: int = int(report.get("total_cosine_overlaps", -1))
    cosine_threshold: float = float(report.get("cosine_threshold", 0.85))

    if leakage_clean:
        if args.check:
            print(
                f"OK: leakage_clean=True ({n_exact} exact, {n_cosine} cosine>={cosine_threshold})"
            )
        else:
            print("Leakage audit: CLEAN")
            print(f"  Source: {args.report}")
            print(f"  Exact-hash overlaps:   {n_exact}")
            print(f"  Cosine >= {cosine_threshold} overlaps: {n_cosine}")
            print(
                "  Per ADR-016 Q3 + ADR-039 gate 3 (intent) + ADR-043: leakage_clean=True is required."
            )
        return 0
    else:
        print(f"FAIL: leakage_clean=False in {args.report}", file=sys.stderr)
        print(f"  Exact-hash overlaps:   {n_exact}", file=sys.stderr)
        print(f"  Cosine >= {cosine_threshold} overlaps: {n_cosine}", file=sys.stderr)
        print(
            "  Resolution: investigate per-fold-seed entries; re-run dedup/leakage pipeline.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
