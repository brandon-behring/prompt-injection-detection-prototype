"""CLI entrypoint — LLM-rater audit of reference scorers per ADR-046 Q5 user override.

Per ADR-046 Q5 (Phase 4 Commit 5 — user-overrode the original defer
recommendation in favor of include-now), this script fires a small LLM-rater
pass against the 4 reference rungs (R-LLM-OpenAI + R-LLM-Anthropic +
R-ProtectAI-v1 + R-ProtectAI-v2 per ADR-018) sampling ~50 disagreement pairs
per reference rung — pairs where the reference scorer disagrees with a
trained-rung headline classifier (LoRA or full-FT).

Each pair gets a rubric grade ``(rater_judgment_correct_about_injection,
calibration_assessment)``; results persisted to
``evals/audit/reference_scorer_rater_audit.json``.

Cost discipline per ADR-020 + ADR-045 Q4: interactive approval gate fires
before any LLM call. Estimated total cost ~$5 per A-002 envelope (4 reference
rungs * ~50 pairs * gpt-4o-2024-08-06 single-turn). The ``--dry-run`` flag
prints the cost preview + exits without billing.

Inputs
------
``--predictions-root`` — directory of per-cell predictions parquets.
``--judge-model`` — OpenAI model name (default ``gpt-4o-2024-08-06``).
``--n-pairs-per-rung`` — disagreement-sampled pairs per reference (default 50).
``--reference-rungs`` — comma-separated list of reference rung names.
``--trained-rung-for-disagreement`` — trained rung whose predictions ground
the disagreement signal (default ``lora``).

Outputs
-------
``--audit-out`` (default ``evals/audit/reference_scorer_rater_audit.json``) —
``{rung_name: {n_pairs, n_rater_correct, calibration_assessment_counts, raw_responses}}``.

Usage
-----
.. code-block:: bash

    uv run python scripts/audit_reference_scorers.py --dry-run
    uv run python scripts/audit_reference_scorers.py  # interactive approval gate fires
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

DEFAULT_REFERENCE_RUNGS = ("R-LLM-OpenAI", "R-LLM-Anthropic", "R-ProtectAI-v1", "R-ProtectAI-v2")
DEFAULT_JUDGE_MODEL = "gpt-4o-2024-08-06"
DEFAULT_N_PAIRS_PER_RUNG = 50
DEFAULT_TRAINED_RUNG = "lora"
# A-002 envelope per-call cost estimate (gpt-4o-2024-08-06 short-turn @ ~$0.025/call).
ESTIMATED_USD_PER_CALL = 0.025


def _select_disagreement_pairs(
    df: pd.DataFrame,
    reference_rung: str,
    trained_rung: str,
    *,
    n_pairs: int,
    threshold: float = 0.5,
    seed: int = 1337,
) -> pd.DataFrame:
    """Sample n_pairs rows where reference and trained rung disagree at threshold."""
    ref = df[df["rung"] == reference_rung][
        ["source", "row_idx_in_source", "text", "label", "predicted_proba_class1"]
    ].rename(columns={"predicted_proba_class1": "ref_score"})
    trn = df[df["rung"] == trained_rung][
        ["source", "row_idx_in_source", "predicted_proba_class1"]
    ].rename(columns={"predicted_proba_class1": "trn_score"})
    joined = ref.merge(trn, on=["source", "row_idx_in_source"], how="inner")
    joined["ref_pred"] = (joined["ref_score"] >= threshold).astype(int)
    joined["trn_pred"] = (joined["trn_score"] >= threshold).astype(int)
    disagree = joined[joined["ref_pred"] != joined["trn_pred"]]
    if disagree.empty:
        return disagree
    return disagree.sample(n=min(n_pairs, len(disagree)), random_state=seed)


def _interactive_approval(n_total_calls: int) -> bool:
    """Per-ADR-020 cost-cap interactive approval gate.

    Returns True iff the operator enters 'y' (case-insensitive). Aborts on
    any other input including empty line. Standard input is reused so tests
    can pipe responses.
    """
    estimated_usd = n_total_calls * ESTIMATED_USD_PER_CALL
    print(
        f"[audit-ref-scorers] About to fire {n_total_calls} LLM judge calls "
        f"(estimated ${estimated_usd:.2f} per A-002 envelope; ADR-020 cost cap).",
        file=sys.stderr,
    )
    print(
        "[audit-ref-scorers] Approve? Type 'y' to proceed, anything else to abort.", file=sys.stderr
    )
    response = input("> ").strip().lower()
    return response == "y"


def main() -> int:
    """Sample disagreement pairs per reference rung; fire LLM-rater pass with approval gate."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predictions-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions",
    )
    parser.add_argument(
        "--reference-rungs",
        default=",".join(DEFAULT_REFERENCE_RUNGS),
        help="Comma-separated list of reference rung names.",
    )
    parser.add_argument(
        "--trained-rung-for-disagreement",
        default=DEFAULT_TRAINED_RUNG,
        help="Trained rung whose predictions ground the disagreement signal.",
    )
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--n-pairs-per-rung", type=int, default=DEFAULT_N_PAIRS_PER_RUNG)
    parser.add_argument(
        "--audit-out",
        type=Path,
        default=_REPO_ROOT / "evals" / "audit" / "reference_scorer_rater_audit.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print cost preview + sample sizes without firing LLM calls.",
    )
    parser.add_argument(
        "--assume-yes",
        action="store_true",
        help="Skip the interactive approval gate (CI / scripted use only).",
    )
    args = parser.parse_args()

    reference_rungs = tuple(r.strip() for r in args.reference_rungs.split(",") if r.strip())
    if not reference_rungs:
        print("[audit-ref-scorers] no reference rungs supplied", file=sys.stderr)
        return 1

    paths = sorted(args.predictions_root.glob("*.parquet"))
    if not paths:
        print(
            f"[audit-ref-scorers] no predictions parquets at {args.predictions_root}; "
            "run scripts/run_metrics_battery.py upstream first.",
            file=sys.stderr,
        )
        return 1
    df = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True)

    plan: dict[str, pd.DataFrame] = {}
    for rung in reference_rungs:
        pairs = _select_disagreement_pairs(
            df,
            reference_rung=rung,
            trained_rung=args.trained_rung_for_disagreement,
            n_pairs=args.n_pairs_per_rung,
        )
        plan[rung] = pairs
        print(
            f"[audit-ref-scorers] {rung}: {len(pairs)} disagreement pairs sampled "
            f"(vs {args.trained_rung_for_disagreement})",
            file=sys.stderr,
        )

    n_total_calls = sum(len(p) for p in plan.values())
    if args.dry_run:
        print(
            f"[audit-ref-scorers] DRY RUN — would fire {n_total_calls} {args.judge_model} calls "
            f"(estimated ${n_total_calls * ESTIMATED_USD_PER_CALL:.2f}); exiting without billing.",
            file=sys.stderr,
        )
        return 0

    if n_total_calls == 0:
        print(
            "[audit-ref-scorers] no disagreement pairs sampled; nothing to audit.", file=sys.stderr
        )
        return 1

    if not args.assume_yes and not _interactive_approval(n_total_calls):
        print("[audit-ref-scorers] approval declined — aborting per ADR-020.", file=sys.stderr)
        return 2

    # Live LLM-rater pass — uses src/scoring/openai_judge.py from Phase 3 Commit 2.
    # OpenAIJudge hard-codes its model name at the class level (OPENAI_JUDGE_MODEL per
    # ADR-018) — `--judge-model` arg is informational only; live calls always go to
    # the locked snapshot. The score returns a float in [0, 1] (probability of injection).
    from src.scoring.openai_judge import OpenAIJudge  # noqa: E402

    judge = OpenAIJudge()
    print(
        f"[audit-ref-scorers] judge_name={OpenAIJudge.judge_name} "
        f"(cli --judge-model={args.judge_model!r} is informational only).",
        file=sys.stderr,
    )

    results: dict[str, dict[str, object]] = {}
    for rung, pairs in plan.items():
        per_rung_responses: list[dict[str, object]] = []
        n_rater_correct = 0
        calibration_counts = {
            "calibrated": 0,
            "overconfident": 0,
            "underconfident": 0,
            "unknown": 0,
        }
        for _, row in pairs.iterrows():
            text = str(row["text"])
            true_label = int(row["label"])
            rater_score = float(judge.score(text))
            rater_pred = 1 if rater_score >= 0.5 else 0
            if rater_pred == true_label:
                n_rater_correct += 1
            # Crude calibration assessment: if reference and rater agree but trained
            # disagrees, flag based on reference confidence vs rater.
            ref_score = float(row["ref_score"])
            if abs(ref_score - 0.5) > 0.4:
                bucket = "overconfident" if (rater_pred != (ref_score >= 0.5)) else "calibrated"
            elif abs(ref_score - 0.5) < 0.1:
                bucket = "underconfident"
            else:
                bucket = "unknown"
            calibration_counts[bucket] += 1
            per_rung_responses.append(
                {
                    "source": str(row["source"]),
                    "row_idx_in_source": int(row["row_idx_in_source"]),
                    "true_label": true_label,
                    "ref_score": ref_score,
                    "trn_score": float(row["trn_score"]),
                    "rater_pred": rater_pred,
                    "rater_score": rater_score,
                }
            )
        results[rung] = {
            "n_pairs": len(pairs),
            "n_rater_correct": n_rater_correct,
            "calibration_assessment_counts": calibration_counts,
            "raw_responses": per_rung_responses,
        }

    args.audit_out.parent.mkdir(parents=True, exist_ok=True)
    args.audit_out.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"[audit-ref-scorers] wrote audit JSON to {args.audit_out} "
        f"(total {n_total_calls} calls; per-rung sample breakdown above)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
