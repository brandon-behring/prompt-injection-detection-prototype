"""CLI wrapper for src.data.templates.extract_hackaprompt_templates (per ADR-041 Q6).

Writes data/contamination_templates.parquet (gitignored). The orchestration
script scripts/run_data_pipeline.py imports the library function directly
without going through this CLI; this entry point exists for standalone use
+ for the future make data-contamination-templates target (Commit 6).

Usage:
    source .env.local && uv run python scripts/extract_hackaprompt_templates.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.manifest_validation import validate_manifest  # noqa: E402
from src.data.templates import (  # noqa: E402
    DEFAULT_SAMPLE_SEED,
    DEFAULT_TARGET_COUNT,
    extract_hackaprompt_templates,
)


def main() -> int:
    """CLI entry — extract templates + write to parquet."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=_REPO_ROOT / "data" / "contamination_templates.parquet",
        help="Output parquet path (default data/contamination_templates.parquet)",
    )
    parser.add_argument(
        "--target-count",
        type=int,
        default=DEFAULT_TARGET_COUNT,
        help=f"Approximate template count (default {DEFAULT_TARGET_COUNT})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SAMPLE_SEED,
        help=f"Random seed for level-balanced sample (default {DEFAULT_SAMPLE_SEED})",
    )
    args = parser.parse_args()

    manifest = validate_manifest(_REPO_ROOT / "data" / "source_manifest.yaml")
    spec = next(row for row in manifest["sources"] if row["name"] == "hackaprompt")

    print(f"[extract_hackaprompt_templates] HackAPrompt SHA {spec['revision_sha'][:12]}")
    df = extract_hackaprompt_templates(spec, target_count=args.target_count, sample_seed=args.seed)
    print(f"[extract_hackaprompt_templates] extracted {len(df)} templates")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.output, index=False)
    print(f"[extract_hackaprompt_templates] wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
