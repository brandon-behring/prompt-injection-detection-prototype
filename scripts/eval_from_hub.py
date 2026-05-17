"""CLI entrypoint — T0 reproducibility tier per ADR-034 + ADR-045 Q5.

Per ADR-034, the T0 reproducibility tier supports reviewer-side
eval-only reproduction via `huggingface_hub.snapshot_download` —
downloads a published headline rung checkpoint from
`BBehring/prompt-injection-<rung>` (per ADR-032) and runs inference on
a small eval slice to verify the methodology numbers reproduce.

This script is the entrypoint surface; it does NOT itself train or
require GPU. Inference uses bf16 if torch.cuda.is_available() else fp32.

Per ADR-045 SPEC_SHEET §3.7 Commit 5, this is the only Phase 3 script
that interacts with HF Hub at inference time; per ADR-034 it stays
lightweight (eval on a small sample for verification; the full eval
re-run requires Phase 1 + Phase 2 + Phase 3 wired end-to-end).

Inputs
------
``--rung`` — which published rung to evaluate (lora / frozen-probe / full-ft
/ tfidf-lr if classical published per ADR-032 final composition).

``--eval-slice`` (default ``bipia``) — which OOD slice to evaluate on.

``--n-rows`` (default 100) — number of rows to score (T0 verification scope;
full eval is T3 reproducibility per ADR-034).

Outputs
-------
``--predictions-out`` (default ``evals/predictions/t0_eval_from_hub.parquet``)
— PredictionsRowModel rows.

Usage
-----
.. code-block:: bash

    uv run python scripts/eval_from_hub.py --rung lora --eval-slice bipia
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Locked HF Hub naming convention per ADR-032.
HF_HUB_NAMESPACE: str = "BBehring"
HF_HUB_REPO_PATTERN: str = "{namespace}/prompt-injection-{rung}"

# Allowlist of headline rungs eligible for T0 publication per ADR-032.
PUBLISHED_RUNGS: frozenset[str] = frozenset({"tfidf-lr", "frozen-probe", "lora", "full-ft"})


def main() -> int:
    """T0 reproducibility tier — download a published rung + score a tiny eval slice."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rung",
        required=True,
        choices=sorted(PUBLISHED_RUNGS),
        help="Headline rung to download from HF Hub per ADR-032",
    )
    parser.add_argument("--eval-slice", default="bipia")
    parser.add_argument("--n-rows", type=int, default=100)
    parser.add_argument(
        "--predictions-out",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions" / "t0_eval_from_hub.parquet",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip HF download + inference; just print the resolved repo_id",
    )
    args = parser.parse_args()

    repo_id = HF_HUB_REPO_PATTERN.format(namespace=HF_HUB_NAMESPACE, rung=args.rung)
    print(f"[t0-eval] resolved HF repo: {repo_id}")

    if args.dry_run:
        print(
            f"[t0-eval] --dry-run; would download {repo_id} + score {args.n_rows} {args.eval_slice} rows"
        )
        return 0

    # Full T0 implementation requires the publishing pipeline (Phase 5
    # ADR-032 deliverable). At Phase 3 Commit 5, the script's argparse +
    # contract surface is the deliverable; the body is gated until
    # `BBehring/prompt-injection-<rung>` repos exist.
    print(
        f"[t0-eval] HF Hub repo {repo_id} not yet published (Phase 5 ADR-032 deliverable). "
        f"Re-run after `scripts/generate_model_cards.py` populates the model repo.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
