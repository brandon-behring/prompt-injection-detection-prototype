"""CLI entrypoint — T0 reproducibility tier per ADR-034 + ADR-045 Q5.

Per ADR-034, the T0 reproducibility tier supports reviewer-side
eval-only reproduction via `huggingface_hub.snapshot_download` —
downloads a published headline rung checkpoint from
`BBehring/prompt-injection-<rung>` (per ADR-032), runs inference on
a small eval slice, and score-matches the per-row
``predicted_proba_class1`` against the committed reference predictions
parquet at ``evals/predictions/<rung>__fold0__seed42__<slice>.parquet``
within ``1e-4`` absolute tolerance per ADR-034 §Tier T0 + ADR-051
§Block A landing condition.

This script is the entrypoint surface; it does NOT itself train or
require GPU. Inference uses CPU + fp32 cast at softmax per ADR-019
numerical-stability discipline.

Per ADR-045 SPEC_SHEET §3.7 Commit 5, this is the only Phase 3 script
that interacts with HF Hub at inference time. The non-dry-run body
wired at v1.0.9 (ADR-058 narrowly supersedes ADR-051 Block A).

Inputs
------
``--rung`` — which published rung to evaluate (lora / frozen-probe).
Only the rungs listed in ``evals/results.json::published_rungs`` are
score-matchable; ``full-ft`` and ``tfidf-lr`` raise ValueError because
they have no HF Hub publication per ADR-032 + ADR-050.

``--eval-slice`` (default ``bipia``) — which OOD slice to evaluate on.
Must match a slice name in the reference predictions parquet.

``--n-rows`` (default 100) — number of rows to score (T0 verification
scope; full eval is T3 reproducibility per ADR-034). If the reference
parquet has fewer rows, all rows are used.

Outputs
-------
``--predictions-out`` (default ``evals/predictions/t0_eval_from_hub.parquet``)
— PredictionsRowModel rows with the re-derived per-row scores.

Exit codes
----------
0 — score-match within ``1e-4`` absolute tolerance for every sampled row.
1 — score-match failed for at least one row (strict mode per
    /exploring-options 2026-05-19 Q1 lock; prints per-row delta diagnostics).
2 — invalid arguments (rung not published, reference parquet missing).

Usage
-----
.. code-block:: bash

    uv run python scripts/eval_from_hub.py --rung lora --eval-slice bipia
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Locked HF Hub naming convention per ADR-032.
HF_HUB_NAMESPACE: str = "BBehring"
HF_HUB_REPO_PATTERN: str = "{namespace}/prompt-injection-{rung}"

# Allowlist of headline rungs eligible for T0 publication per ADR-032.
PUBLISHED_RUNGS: frozenset[str] = frozenset({"tfidf-lr", "frozen-probe", "lora", "full-ft"})

# ADR-034 §Tier T0 + ADR-051 §Block A landing condition: per-row absolute
# tolerance for the score-match contract.
SCORE_MATCH_TOLERANCE: float = 1e-4

# Canonical checkpoint pinned per evals/results.json.
CANONICAL_FOLD: int = 0
CANONICAL_SEED: int = 42

# Inference defaults; matches src/training/train_modernbert.py + ADR-019.
INFERENCE_MAX_LENGTH: int = 8192
INFERENCE_BATCH_SIZE: int = 4


def _rung_to_underscore(rung: str) -> str:
    """Convert kebab-case rung (HF Hub / results.json) to underscore form (file system)."""
    return rung.replace("-", "_")


def _load_reference_predictions(rung: str, eval_slice: str) -> Any:
    """Load the committed reference predictions parquet for (rung, fold0, seed42, slice).

    Parameters
    ----------
    rung : str
        Kebab-case rung name (e.g. ``"frozen-probe"``).
    eval_slice : str
        OOD slice name (e.g. ``"bipia"``).

    Returns
    -------
    pandas.DataFrame
        Reference predictions with PredictionsRowModel-compatible columns.

    Raises
    ------
    FileNotFoundError
        If the reference parquet does not exist at the expected path.
    """
    import pandas as pd

    rung_us = _rung_to_underscore(rung)
    parquet_path = (
        _REPO_ROOT
        / "evals"
        / "predictions"
        / f"{rung_us}__fold{CANONICAL_FOLD}__seed{CANONICAL_SEED}__{eval_slice}.parquet"
    )
    if not parquet_path.exists():
        raise FileNotFoundError(
            f"Reference predictions parquet missing: {parquet_path}. "
            f"Expected schema per src/eval/schemas.py::PredictionsRowModel "
            f"(rung={rung_us}, fold={CANONICAL_FOLD}, seed={CANONICAL_SEED}, "
            f"slice={eval_slice})."
        )
    return pd.read_parquet(parquet_path)


def _resolve_published_rungs() -> frozenset[str]:
    """Return rungs actually publishable per ``evals/results.json::published_rungs``.

    Returns
    -------
    frozenset of str
        Kebab-case rung names with reference scores committed.

    Raises
    ------
    FileNotFoundError
        If ``evals/results.json`` is missing.
    """
    results_path = _REPO_ROOT / "evals" / "results.json"
    if not results_path.exists():
        raise FileNotFoundError(
            f"evals/results.json missing at {results_path}; required to determine "
            f"published rungs per ADR-032 + ADR-051 Block A score-match contract."
        )
    with results_path.open("r") as f:
        data = json.load(f)
    return frozenset(data["published_rungs"])


def _download_checkpoint(repo_id: str) -> Path:
    """Download the published HF Hub checkpoint via ``huggingface_hub.snapshot_download``.

    Parameters
    ----------
    repo_id : str
        HF Hub repository identifier (e.g. ``"BBehring/prompt-injection-frozen-probe"``).

    Returns
    -------
    pathlib.Path
        Local path to the downloaded snapshot directory.
    """
    from huggingface_hub import snapshot_download

    local_path = snapshot_download(repo_id=repo_id)
    return Path(local_path)


def _load_model_and_tokenizer(rung: str, snapshot_path: Path) -> tuple[Any, Any]:
    """Load model + tokenizer from a downloaded HF Hub snapshot.

    Dispatches on rung architecture:

    - ``frozen-probe`` / ``full-ft``: full ``AutoModelForSequenceClassification``
      checkpoint (tokenizer co-located in the snapshot).
    - ``lora``: LoRA adapter only; loads base ModernBERT then wraps via
      ``PeftModel.from_pretrained``; tokenizer loaded from the pinned backbone.

    Parameters
    ----------
    rung : str
        Kebab-case rung name.
    snapshot_path : pathlib.Path
        Local path to the downloaded HF Hub snapshot.

    Returns
    -------
    tuple
        ``(model, tokenizer)`` ready for ``_predict_proba``.

    Raises
    ------
    ValueError
        If the rung architecture is not supported.
    """
    import torch
    from torch.nn import Module
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    device = "cpu"

    if rung == "lora":
        from peft import PeftModel

        from src.training.load_backbone import load_backbone

        backbone_hf_id = "answerdotai/ModernBERT-base"
        backbone_revision = "8949b909ec900327062f0ebf497f51aef5e6f0c8"
        base = load_backbone(
            hf_id=backbone_hf_id,
            revision=backbone_revision,
            num_labels=2,
        )
        model: Any = PeftModel.from_pretrained(cast(Module, base), str(snapshot_path))
        tokenizer = AutoTokenizer.from_pretrained(
            backbone_hf_id,
            revision=backbone_revision,
        )
    elif rung in ("frozen-probe", "full-ft"):
        model = AutoModelForSequenceClassification.from_pretrained(
            str(snapshot_path),
            torch_dtype=torch.float32,
        )
        tokenizer = AutoTokenizer.from_pretrained(str(snapshot_path))
    else:
        raise ValueError(
            f"Rung '{rung}' is not supported for T0 score-match. "
            f"Supported: frozen-probe, lora, full-ft. tfidf-lr requires a "
            f"different (sklearn-pickle) loader and is not yet wired."
        )

    model = model.to(device).eval()
    return model, tokenizer


def _score_match_summary(
    *,
    new_probs: Any,
    reference_probs: Any,
    tolerance: float,
) -> tuple[bool, dict[str, float]]:
    """Compare per-row predictions against the reference; return (passed, stats).

    Parameters
    ----------
    new_probs : numpy.ndarray
        Newly-computed ``predicted_proba_class1`` values (shape ``(N,)``).
    reference_probs : numpy.ndarray
        Reference values from the committed predictions parquet.
    tolerance : float
        Absolute per-row tolerance per ADR-034 §Tier T0.

    Returns
    -------
    tuple
        ``(passed, stats)`` where ``passed`` is True iff every row is within
        tolerance; ``stats`` carries ``max_abs_delta``, ``mean_abs_delta``,
        ``n_exceed``, ``n_total``.

    Raises
    ------
    ValueError
        If the two arrays have different lengths (programmer error).
    """
    import numpy as np

    if len(new_probs) != len(reference_probs):
        raise ValueError(
            f"Length mismatch: new_probs ({len(new_probs)}) vs "
            f"reference_probs ({len(reference_probs)})"
        )

    deltas = np.abs(new_probs.astype(np.float64) - reference_probs.astype(np.float64))
    max_abs_delta = float(deltas.max()) if len(deltas) > 0 else 0.0
    mean_abs_delta = float(deltas.mean()) if len(deltas) > 0 else 0.0
    n_exceed = int((deltas > tolerance).sum())
    n_total = int(len(deltas))
    passed = n_exceed == 0
    return passed, {
        "max_abs_delta": max_abs_delta,
        "mean_abs_delta": mean_abs_delta,
        "n_exceed": float(n_exceed),
        "n_total": float(n_total),
    }


def _emit_predictions_parquet(
    *,
    sampled_df: Any,
    new_probs: Any,
    rung: str,
    predictions_out: Path,
) -> None:
    """Write the re-derived predictions to a PredictionsRowModel-compatible parquet.

    Parameters
    ----------
    sampled_df : pandas.DataFrame
        The reference rows that were re-scored (carries text/label/source/etc.).
    new_probs : numpy.ndarray
        Re-derived ``predicted_proba_class1`` values aligned with ``sampled_df``.
    rung : str
        Kebab-case rung name (e.g. ``"frozen-probe"``).
    predictions_out : pathlib.Path
        Destination parquet path.
    """
    import pandas as pd

    predictions_out.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(
        {
            "rung": _rung_to_underscore(rung),
            "fold": CANONICAL_FOLD,
            "seed": CANONICAL_SEED,
            "epoch": sampled_df["epoch"].to_numpy() if "epoch" in sampled_df.columns else 2,
            "row_idx_in_source": sampled_df["row_idx_in_source"].to_numpy(),
            "source": sampled_df["source"].to_numpy(),
            "text": sampled_df["text"].to_numpy(),
            "label": sampled_df["label"].to_numpy(),
            "predicted_proba_class1": new_probs.astype(float),
            "contamination_state": "backbone-partial-disjoint",
        }
    )
    out_df.to_parquet(predictions_out, index=False)


def _print_diagnostics(
    *,
    rung: str,
    eval_slice: str,
    repo_id: str,
    passed: bool,
    stats: dict[str, float],
    tolerance: float,
    deltas_sample: Any,
) -> None:
    """Print a human-readable score-match summary to stdout (and stderr on fail)."""
    stream = sys.stdout if passed else sys.stderr
    verdict = "PASS" if passed else "FAIL"
    print(
        f"[t0-eval] {verdict} score-match for rung={rung} slice={eval_slice} (repo={repo_id}):",
        file=stream,
    )
    print(f"[t0-eval]   tolerance       = {tolerance:.6f}", file=stream)
    print(f"[t0-eval]   n_total         = {int(stats['n_total'])}", file=stream)
    print(f"[t0-eval]   n_exceed        = {int(stats['n_exceed'])}", file=stream)
    print(f"[t0-eval]   max_abs_delta   = {stats['max_abs_delta']:.6e}", file=stream)
    print(f"[t0-eval]   mean_abs_delta  = {stats['mean_abs_delta']:.6e}", file=stream)
    if not passed and deltas_sample is not None:
        import numpy as np

        # Show top-5 exceedances by absolute delta.
        top_idx = np.argsort(deltas_sample)[::-1][:5]
        print("[t0-eval]   top-5 exceedances (row_idx, |delta|):", file=stream)
        for idx in top_idx:
            print(f"[t0-eval]     row {int(idx):5d}  |delta|={deltas_sample[idx]:.6e}", file=stream)


def main() -> int:
    """T0 reproducibility tier — download a published rung + per-row score-match.

    Returns
    -------
    int
        Process exit code (0=pass, 1=score-match fail (strict), 2=invalid args).
    """
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
            f"[t0-eval] --dry-run; would download {repo_id} + score "
            f"{args.n_rows} {args.eval_slice} rows"
        )
        return 0

    # Validate the requested rung is actually publishable per evals/results.json.
    publishable = _resolve_published_rungs()
    if args.rung not in publishable:
        print(
            f"[t0-eval] ERROR: rung '{args.rung}' is not in evals/results.json "
            f"published_rungs={sorted(publishable)}. T0 score-match requires a "
            f"committed reference score per ADR-032 + ADR-051 Block A.",
            file=sys.stderr,
        )
        return 2

    # 1. Load the committed reference predictions parquet.
    try:
        reference_df = _load_reference_predictions(args.rung, args.eval_slice)
    except FileNotFoundError as err:
        print(f"[t0-eval] ERROR: {err}", file=sys.stderr)
        return 2

    n_available = len(reference_df)
    n_to_score = min(args.n_rows, n_available)
    sampled_df = reference_df.iloc[:n_to_score].reset_index(drop=True)
    print(
        f"[t0-eval] reference parquet: {n_available} rows; "
        f"sampling first {n_to_score} for score-match"
    )

    # 2. Download the published HF Hub checkpoint.
    print(f"[t0-eval] downloading {repo_id} via huggingface_hub.snapshot_download...")
    snapshot_path = _download_checkpoint(repo_id)
    print(f"[t0-eval] snapshot at {snapshot_path}")

    # 3. Load model + tokenizer (architecture dispatch per rung).
    print(f"[t0-eval] loading {args.rung} model+tokenizer on CPU...")
    model, tokenizer = _load_model_and_tokenizer(args.rung, snapshot_path)

    # 4. Run CPU inference (library-first: reuse src.training.train_modernbert._predict_proba).
    from src.training.train_modernbert import _predict_proba

    print(f"[t0-eval] running CPU inference on {n_to_score} rows...")
    probs = _predict_proba(
        model=model,
        tokenizer=tokenizer,
        test_df=sampled_df,
        max_length=INFERENCE_MAX_LENGTH,
        per_device_batch_size=INFERENCE_BATCH_SIZE,
    )
    new_probs = probs[:, 1].astype(float)
    reference_probs = sampled_df["predicted_proba_class1"].to_numpy(dtype=float)

    # 5. Score-match per ADR-034 §Tier T0 + ADR-051 §Block A.
    passed, stats = _score_match_summary(
        new_probs=new_probs,
        reference_probs=reference_probs,
        tolerance=SCORE_MATCH_TOLERANCE,
    )

    import numpy as np

    deltas_sample = np.abs(new_probs - reference_probs)
    _print_diagnostics(
        rung=args.rung,
        eval_slice=args.eval_slice,
        repo_id=repo_id,
        passed=passed,
        stats=stats,
        tolerance=SCORE_MATCH_TOLERANCE,
        deltas_sample=deltas_sample,
    )

    # 6. Emit predictions parquet regardless of pass/fail (for diagnostics).
    _emit_predictions_parquet(
        sampled_df=sampled_df,
        new_probs=new_probs,
        rung=args.rung,
        predictions_out=args.predictions_out,
    )
    print(f"[t0-eval] wrote predictions parquet: {args.predictions_out}")

    # Strict mode per /exploring-options 2026-05-19 Q1 lock: exit 1 on any row
    # exceeding tolerance. No-silent-failures discipline.
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
