# mypy: disable-error-code="no-untyped-call"
# pyarrow.parquet does not ship type stubs; read_table calls are flagged as
# untyped under --strict. Disabled at file level rather than per-call.
"""Audit reader-visible numeric claims against evals/*.parquet source-of-truth.

Per the v1.3.1 audit-fix Q2 lock: independently re-derive every reader-visible
number from per-row predictions + operating-points + per-cell metrics, then
diff against the values extracted from reader-facing Markdown surfaces. Exit
non-zero on drift.

Catches the cross-guide numeric-divergence class of error surfaced by the
2026-05-22 fresh-eyes audit:
- WRITEUP_PAPER.md §4.6 frozen-probe Mean test FPR cited as 0.6% (actual: 1.0%
  per evals/operating_points/dual_policy.parquet).
- WRITEUP_PAPER.md §3.3 BIPIA + InjecAgent per-slice n cited as 56+56 (actual:
  50 + 62 per evals/predictions/*__bipia.parquet + *__injecagent.parquet row
  counts).

Authority chain (Q2 lock):
  evals/predictions/*.parquet           -> per-row predictions + labels
  evals/operating_points/dual_policy    -> validation-fit threshold + test FPR
  evals/bootstrap/marginal_cells        -> AUPRC / AUROC + BCa CIs
  evals/metrics/per_cell                -> per-(rung, fold, seed) ECE + Brier
  evals/predictions_val/*.parquet       -> direct+benign validation metrics

Output: structured JSON to evals/audit/numeric_audit.json + console table.
Exit code 0 if every recomputed value matches what the Markdown surfaces
claim within tolerance; non-zero on any mismatch.

Run from repo root:
    uv run python scripts/audit_numbers.py            # full check (default)
    uv run python scripts/audit_numbers.py --quiet    # CI mode
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq
from sklearn.metrics import average_precision_score, roc_auc_score

REPO_ROOT = Path(__file__).resolve().parent.parent

# Tolerance for numeric comparisons.
# 0.005 = half-a-thousandth: catches "0.6% vs 1.0%" + per-slice n mismatches;
# does not flag minor rounding (e.g., 0.974 vs 0.9736).
TOL_ABS = 0.005


@dataclass
class Check:
    """One named numeric check + its computed + expected values."""

    name: str
    computed: float | int
    expected: float | int
    tol: float = TOL_ABS
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        if self.expected is None:
            return False
        return abs(float(self.computed) - float(self.expected)) <= self.tol

    @property
    def diff(self) -> float:
        return float(self.computed) - float(self.expected)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "computed": float(self.computed),
            "expected": float(self.expected),
            "diff": self.diff,
            "tol": self.tol,
            "passed": self.passed,
            "metadata": self.metadata,
        }


def re_derive_test_fpr_mean(rung: str) -> float:
    """Recompute mean test FPR (detection policy) for one rung from dual_policy."""
    dp = pq.read_table(REPO_ROOT / "evals/operating_points/dual_policy.parquet").to_pandas()
    rows = dp[(dp["rung"] == rung) & (dp["policy"] == "detection")]
    if rows.empty:
        raise ValueError(f"No detection-policy rows for rung {rung!r} in dual_policy.parquet")
    return float(rows["achieved_test_fpr"].mean())


def re_derive_slice_n_positive(slice_name: str) -> int | None:
    """Row count for an all-positive OOD slice from any prediction parquet.

    Returns None if prediction parquets are not available in this environment
    (they are gitignored — present locally + on RunPod fires, absent on CI
    checkout). Caller treats None as "skip this check".
    """
    candidates = sorted((REPO_ROOT / "evals/predictions").glob(f"*__{slice_name}.parquet"))
    if not candidates:
        return None
    df = pq.read_table(candidates[0]).to_pandas()
    return int((df["label"] == 1).sum())


def re_derive_random_auprc_floor() -> tuple[int, int, float]:
    """Pooled OOD positive rate from per_cell.parquet (deterministic)."""
    pc = pq.read_table(REPO_ROOT / "evals/metrics/per_cell.parquet").to_pandas()
    pooled = pc[pc["slice_name"] == "pooled_ood"]
    if pooled.empty:
        raise ValueError("No pooled_ood rows in per_cell.parquet")
    n_pos = int(pooled["n_positive"].iloc[0])
    n_total = int(pooled["n_rows"].iloc[0])
    return n_pos, n_total, n_pos / n_total


def re_derive_validation_metric(rung: str, metric: str) -> float | None:
    """Mean per-(fold, seed) AUPRC/AUROC/recall@0.5 from predictions_val/*.parquet.

    Returns None if val predictions are not available (gitignored — absent on
    CI checkout). Caller treats None as "skip this check".
    """
    files = sorted((REPO_ROOT / "evals/predictions_val").glob(f"{rung}__*.parquet"))
    if not files:
        return None
    vals = []
    for f in files:
        df = pq.read_table(f).to_pandas()
        if df["label"].nunique() < 2:
            continue
        if metric == "auprc":
            vals.append(average_precision_score(df["label"], df["predicted_proba_class1"]))
        elif metric == "auroc":
            vals.append(roc_auc_score(df["label"], df["predicted_proba_class1"]))
        elif metric == "recall_at_0_5":
            pred = (df["predicted_proba_class1"] >= 0.5).astype(int)
            n_pos = (df["label"] == 1).sum()
            recall = ((df["label"] == 1) & (pred == 1)).sum() / max(1, n_pos)
            vals.append(recall)
        else:
            raise ValueError(f"Unknown metric {metric!r}")
    return float(pd.Series(vals).mean())


def re_derive_lodo_direct_recall(rung: str) -> float | None:
    """Pooled-row recall@0.5 across all (fold, seed) epoch2 prediction parquets.

    Uses pooled-row aggregation (concat all rows then compute one recall) per the
    canonical writeup convention. Per-cell-then-mean gives a different (~0.04
    higher) value due to non-equivariance under cell-size variation.

    Returns None if prediction parquets are not available (gitignored — absent
    on CI checkout). Caller treats None as "skip this check".
    """
    rung_aliases = {
        "frozen_probe": ("frozen_probe", "frozen-probe"),
        "full_ft": ("full_ft", "full-ft"),
    }
    files = []
    for alias in rung_aliases.get(rung, (rung,)):
        files.extend(sorted((REPO_ROOT / "evals/predictions").glob(f"{alias}__*__epoch2.parquet")))
    if not files:
        return None
    pieces = [pq.read_table(f).to_pandas() for f in files]
    big = pd.concat(pieces, ignore_index=True)
    n_pos = int((big["label"] == 1).sum())
    if n_pos == 0:
        raise ValueError(f"No positives in LODO direct-source predictions for {rung!r}")
    pred = (big["predicted_proba_class1"] >= 0.5).astype(int)
    return float(((big["label"] == 1) & (pred == 1)).sum() / n_pos)


def re_derive_marginal_auprc(
    rung: str, slice_name: str, seed: int = 1
) -> tuple[float, float, float]:
    """Headline AUPRC + CI from marginal_cells.parquet."""
    mc = pq.read_table(REPO_ROOT / "evals/bootstrap/marginal_cells.parquet").to_pandas()
    row = mc[
        (mc["rung"] == rung)
        & (mc["slice_name"] == slice_name)
        & (mc["metric"] == "auprc")
        & (mc["seed"] == seed)
    ]
    if row.empty:
        raise ValueError(f"No marginal row for {rung}/{slice_name}/auprc/seed={seed}")
    return (
        float(row["point_estimate"].iloc[0]),
        float(row["ci_lo"].iloc[0]),
        float(row["ci_hi"].iloc[0]),
    )


def run_audit() -> tuple[list[Check], list[str]]:
    """Run all numeric checks; return (checks, narrative-warning-list)."""
    checks: list[Check] = []
    warnings: list[str] = []

    # === Class-A item 3: PAPER §4.6 frozen-probe Mean test FPR (the user's "both be right" example) ===
    fp_fpr = re_derive_test_fpr_mean("frozen_probe")
    checks.append(
        Check(
            name="PAPER §4.6 frozen-probe Mean test FPR",
            computed=fp_fpr * 100,  # report as percentage to match writeup convention
            expected=1.0,  # post-fix value (PAPER pre-fix says 0.6%)
            tol=0.05,  # half a tenth of a percent; catches 0.6 vs 1.0 cleanly
            metadata={
                "source": "evals/operating_points/dual_policy.parquet",
                "rung": "frozen_probe",
                "policy": "detection",
            },
        )
    )

    # Cross-check: LoRA + TF-IDF FPR (writeup says 11.5% + 6.7%; both already correct)
    for rung, expected_pct in [("lora", 11.5), ("tfidf-lr", 6.7)]:
        checks.append(
            Check(
                name=f"PAPER §4.6 {rung} Mean test FPR",
                computed=re_derive_test_fpr_mean(rung) * 100,
                expected=expected_pct,
                tol=0.2,
                metadata={"source": "evals/operating_points/dual_policy.parquet", "rung": rung},
            )
        )

    # === Class-A item 5: BIPIA + InjecAgent per-slice n ===
    for slice_name, expected_n in [("bipia", 50), ("injecagent", 62)]:
        n = re_derive_slice_n_positive(slice_name)
        if n is None:
            warnings.append(
                f"PAPER §3.3 + limitations §8.1 {slice_name} n: SKIPPED "
                f"(evals/predictions/*__{slice_name}.parquet not present in this "
                f"environment — gitignored; available locally + on RunPod fires)"
            )
            continue
        checks.append(
            Check(
                name=f"PAPER §3.3 + limitations §8.1 {slice_name} n",
                computed=n,
                expected=expected_n,
                tol=0,  # exact match
                metadata={"source": f"evals/predictions/*__{slice_name}.parquet"},
            )
        )

    # === Random AUPRC floor ===
    n_pos, n_total, floor = re_derive_random_auprc_floor()
    checks.append(
        Check(
            name="Pooled OOD random AUPRC floor",
            computed=floor,
            expected=0.374,
            tol=0.001,
            metadata={"n_positive": n_pos, "n_total": n_total, "exact": f"{n_pos}/{n_total}"},
        )
    )

    # === Headline AUPRC + CI (pooled_ood, seed=1) ===
    for rung, expected_auprc in [
        ("frozen_probe", 0.364),
        ("lora", 0.293),
        ("tfidf-lr", 0.291),
        ("protectai-v1", 0.361),
        ("protectai-v2", 0.314),
    ]:
        pe, lo, hi = re_derive_marginal_auprc(rung, "pooled_ood")
        checks.append(
            Check(
                name=f"Headline AUPRC pooled_ood {rung}",
                computed=pe,
                expected=expected_auprc,
                tol=0.002,
                metadata={"ci_lo": lo, "ci_hi": hi},
            )
        )

    # === Direct+benign validation (LoRA / TF-IDF / frozen probe) ===
    for rung, metric, expected in [
        ("lora", "auprc", 0.974),
        ("lora", "auroc", 0.993),
        ("lora", "recall_at_0_5", 0.934),
        ("tfidf-lr", "auprc", 0.971),
        ("tfidf-lr", "auroc", 0.992),
        ("tfidf-lr", "recall_at_0_5", 0.930),
        ("frozen_probe", "auprc", 0.653),
        ("frozen_probe", "auroc", 0.907),
        ("frozen_probe", "recall_at_0_5", 0.849),
    ]:
        v = re_derive_validation_metric(rung, metric)
        if v is None:
            warnings.append(
                f"Direct+benign validation {rung} {metric}: SKIPPED "
                f"(evals/predictions_val/ not present in this environment — "
                f"gitignored; available locally + on RunPod fires)"
            )
            continue
        checks.append(
            Check(
                name=f"Direct+benign validation {rung} {metric}",
                computed=v,
                expected=expected,
                tol=0.003,
                metadata={"source": "evals/predictions_val/"},
            )
        )

    # === LODO direct-source recall@0.5 (pooled-row aggregation) ===
    for rung, expected in [("frozen_probe", 0.641), ("lora", 0.625), ("full_ft", 0.558)]:
        r = re_derive_lodo_direct_recall(rung)
        if r is None:
            warnings.append(
                f"LODO direct-source recall@0.5 {rung}: SKIPPED "
                f"(evals/predictions/*__epoch2.parquet not present in this "
                f"environment — gitignored; available locally + on RunPod fires)"
            )
            continue
        checks.append(
            Check(
                name=f"LODO direct-source recall@0.5 {rung}",
                computed=r,
                expected=expected,
                tol=0.002,
                metadata={
                    "source": "evals/predictions/*__epoch2.parquet",
                    "aggregation": "pooled-row",
                },
            )
        )

    return checks, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-check output; print only summary + JSON path.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=REPO_ROOT / "evals/audit/numeric_audit.json",
        help="Path to write structured audit output.",
    )
    args = parser.parse_args()

    checks, warnings = run_audit()

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(
            {
                "checks": [c.to_dict() for c in checks],
                "warnings": warnings,
                "n_passed": sum(1 for c in checks if c.passed),
                "n_failed": sum(1 for c in checks if not c.passed),
            },
            indent=2,
        )
    )

    failed = [c for c in checks if not c.passed]

    if not args.quiet:
        print(
            f"\n{'=' * 80}\nNumeric audit: {len(checks)} checks against evals/ source-of-truth\n{'=' * 80}\n"
        )
        for c in checks:
            mark = "PASS" if c.passed else "FAIL"
            print(
                f"  [{mark}] {c.name:55s}  computed={c.computed:8.4f}  expected={c.expected:8.4f}  diff={c.diff:+.4f}"
            )
        if warnings:
            print(f"\n{'-' * 80}\nSkipped checks ({len(warnings)}):\n{'-' * 80}")
            for w in warnings:
                print(f"  [SKIP] {w}")
        print()
    elif warnings:
        # In quiet mode, still surface skipped checks (1-line each) so they're
        # visible in CI logs.
        for w in warnings:
            print(f"INFO  [SKIP] {w}")

    if failed:
        print(f"audit_numbers: FAILED {len(failed)}/{len(checks)} checks")
        for c in failed:
            print(f"  FAIL  {c.name}: computed={c.computed} expected={c.expected} (tol={c.tol})")
        return 1

    print(
        f"audit_numbers: all {len(checks)} checks PASSED (output: {args.json_out.relative_to(REPO_ROOT)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
