"""Generate HF Hub model cards for the published rungs (Q11 lock — expansive ADR-032 schema).

Per ADR-032 (HF Hub publication = headline rungs only with model card
discipline) + Q11 from the v1.0.0 closure /exploring-options:
- YAML frontmatter: license, tags, datasets (HF dataset IDs at SHAs per
  ADR-016), `model-index.results` (per-slice metric table from
  evals/results.json).
- Body: intended use ("research and methodology characterisation; NOT
  production deployment per ADR-005"), limitations link, contamination
  tier per ADR-005, citation block (repo URL at v1.0.0 + author + date),
  reproducibility commands (`make eval-from-hub RUNG=<rung>`).

Per Q10 lock: published rungs are frozen-probe + LoRA only (full-FT
weights missing locally per ADR-050).

Library-first: uses `huggingface_hub.ModelCard` for the card abstraction.

Output: writes
``evals/checkpoints/{rung_underscored}/fold0/seed42/checkpoint-1090/README.md``
per rung, ready for `huggingface_hub.upload_folder` to push to
``BBehring/prompt-injection-{rung}``.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

PUBLISHED_RUNGS = ["frozen-probe", "lora"]
PUBLISHED_RUNG_KEYS = {"frozen-probe": "frozen_probe", "lora": "lora"}
CANONICAL_CHECKPOINT = "checkpoint-1090"
REPO_URL = "https://github.com/brandon-behring/prompt-injection-detection-prototype"

# ADR-016 + ADR-021 LODO training-pool dataset slate (HF IDs only;
# revisions live in configs/data/source_manifest.yaml).
LODO_DATASETS = [
    "deepset/prompt-injections",
    "Lakera/gandalf_ignore_instructions",
    "Lakera/mosscap_prompt_injection",
    "hackaprompt/hackaprompt-dataset",
]


def _format_metric(metric_block: dict[str, Any]) -> str:
    """Format a metric block (point + CI) as a human-readable string."""
    if "point" in metric_block:
        return f"{metric_block['point']:.4f} [{metric_block['ci_lo']:.4f}, {metric_block['ci_hi']:.4f}]"
    return f"{metric_block:.4f}"


def _build_model_index_results(rung_block: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the YAML model-index.results list for the HF Hub card frontmatter."""
    results = []
    metrics = rung_block["metrics"]
    for slice_name in ["jbb_behaviors", "xstest", "pooled_ood"]:
        for metric_name in ["auprc", "auroc"]:
            key = f"{slice_name}/{metric_name}"
            if key not in metrics:
                continue
            block = metrics[key]
            results.append(
                {
                    "task": {"type": "text-classification", "name": "prompt-injection-detection"},
                    "dataset": {"name": slice_name, "type": "ood-slate"},
                    "metrics": [
                        {
                            "type": metric_name,
                            "value": round(block["point"], 4),
                            "name": metric_name.upper(),
                            "verified": False,
                        }
                    ],
                }
            )
    return results


def _build_card(rung: str, rung_block: dict[str, Any]) -> str:
    """Build the full model card markdown for one rung."""
    contamination_tier = rung_block["contamination_tier"]
    metrics = rung_block["metrics"]

    # YAML frontmatter (expansive per Q11 lock).
    frontmatter_lines = [
        "---",
        "license: apache-2.0",
        "tags:",
        "- text-classification",
        "- prompt-injection",
        "- safety",
        "- modernbert",
        "datasets:",
    ]
    frontmatter_lines.extend(f"- {ds}" for ds in LODO_DATASETS)
    frontmatter_lines.append("model-index:")
    frontmatter_lines.append(f"- name: prompt-injection-{rung}")
    frontmatter_lines.append("  results:")

    for result in _build_model_index_results(rung_block):
        frontmatter_lines.append("  - task:")
        frontmatter_lines.append(f"      type: {result['task']['type']}")
        frontmatter_lines.append(f"      name: {result['task']['name']}")
        frontmatter_lines.append("    dataset:")
        frontmatter_lines.append(f"      name: {result['dataset']['name']}")
        frontmatter_lines.append(f"      type: {result['dataset']['type']}")
        frontmatter_lines.append("    metrics:")
        for m in result["metrics"]:
            frontmatter_lines.append(f"    - type: {m['type']}")
            frontmatter_lines.append(f"      value: {m['value']}")
            frontmatter_lines.append(f"      name: {m['name']}")
            frontmatter_lines.append(f"      verified: {str(m['verified']).lower()}")
    frontmatter_lines.append("---")

    # Body — markdown sections per Q11 lock.
    body = f"""
# prompt-injection-{rung} — methodology submission rung

**Author**: Brandon Behring
**Date published**: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}
**Project**: [{REPO_URL}]({REPO_URL}) at `v1.0.0`
**Submission audit ledger**: see `SUBMISSION_AUDIT.md` in the repo.
**Contamination tier (ADR-005 taxonomy)**: `{contamination_tier}`.

This model card publishes the canonical fold0/seed42 checkpoint of the
`{rung}` rung from the methodology submission. The rung is one of a
5-rung ladder characterising what successive capability layers add to
prompt-injection detection across an IID test slate (4-source LODO
held-out positives) and a 5-slice OOD slate (BIPIA + InjecAgent +
JBB-Behaviors + XSTest + NotInject). **No rung is promoted as a
deployment recommendation** — each rung's trade-offs are characterised
per ADR-005 methodology-over-metrics framing.

## Intended use

Research-and-methodology-characterisation **only**. **NOT** production
deployment per ADR-005. The classifier-output behaviour is documented in
[the project WRITEUP]({REPO_URL}/blob/v1.0.0/WRITEUP.md) §5 + §7.

## Limitations

See
[the project's limitations spoke]({REPO_URL}/blob/v1.0.0/WRITEUP/limitations-and-future-work.md)
for the full list. Key points relevant to this checkpoint:

- LODO non-exchangeability (per assumption A-008) — train sets overlap
  across folds; per-fold variance reported in
  `evals/audit/cross_fold_ci_audit.parquet`.
- English-only; cross-language attacks out of scope per ADR-016.
- Single-class OOD slices (`bipia`, `injecagent`, `notinject`) have
  AUROC/AUPRC undefined per the project's WRITEUP §Methodology caveats
  convention; only `jbb_behaviors`, `xstest`, `pooled_ood` carry
  threshold-free ranking metrics.

## Headline results (canonical fold0/seed42; 95% BCa CI)

| Slice | AUPRC | AUROC |
|---|---|---|
"""

    for slice_name in ["jbb_behaviors", "xstest", "pooled_ood"]:
        auprc = metrics.get(f"{slice_name}/auprc")
        auroc = metrics.get(f"{slice_name}/auroc")
        auprc_str = _format_metric(auprc) if auprc else "n/a"
        auroc_str = _format_metric(auroc) if auroc else "n/a"
        body += f"| `{slice_name}` | {auprc_str} | {auroc_str} |\n"

    body += "\nPer-rung calibration (mean across folds × seeds):\n\n"
    body += "| Slice | recall@FPR=1% (mean) | ECE (equal-mass) | Brier |\n"
    body += "|---|---|---|---|\n"
    for slice_name in ["jbb_behaviors", "xstest", "pooled_ood"]:
        recall_key = f"{slice_name}/recall_at_fpr_1_mean"
        ece_key = f"{slice_name}/ece_equal_mass_mean"
        brier_key = f"{slice_name}/brier_mean"
        if recall_key in metrics:
            body += (
                f"| `{slice_name}` "
                f"| {metrics[recall_key]:.4f} "
                f"| {metrics[ece_key]:.4f} "
                f"| {metrics[brier_key]:.4f} |\n"
            )

    body += f"""
Source: `evals/results.json` at v1.0.0 (BCa bootstrap per ADR-022,
10 000 resamples). Full per-rung × per-slice grid in the project
[WRITEUP §Results]({REPO_URL}/blob/v1.0.0/WRITEUP.md).

## Reproducibility (T0)

```bash
git clone {REPO_URL}
cd prompt-injection-detection-prototype
make install
make eval-from-hub RUNG={rung}
```

This downloads the checkpoint, runs CPU eval against the local val slate,
and score-matches against `evals/results.json` within 1e-4 absolute per
ADR-034. ~10-30 min, $0 GPU.

Full T1 GPU re-eval via `make headline-cloud` (~$28 RunPod A100 80GB).

## Citation

```bibtex
@misc{{behring2026promptinjection{rung.replace("-", "")},
  author       = {{Behring, Brandon}},
  title        = {{prompt-injection-{rung} — methodology submission rung}},
  year         = {{2026}},
  url          = {{ {REPO_URL}/tree/v1.0.0 }}
}}
```

## Linked ADRs

ADR-005 (contamination taxonomy), ADR-015 (single-backbone slate),
ADR-016 (data design), ADR-019 (transformer training recipe), ADR-032
(HF Hub publication discipline), ADR-034 (T0 reproducibility tier),
ADR-050 (rung-slate narrowing).
"""
    return "\n".join(frontmatter_lines) + body


def main() -> int:
    """Generate README.md cards for each published rung."""
    results = json.loads((_REPO_ROOT / "evals" / "results.json").read_text())

    for rung in PUBLISHED_RUNGS:
        rung_key = PUBLISHED_RUNG_KEYS[rung]
        rung_block = results["per_rung"][rung]
        card_md = _build_card(rung, rung_block)

        out_path = (
            _REPO_ROOT
            / "evals"
            / "checkpoints"
            / rung_key
            / "fold0"
            / "seed42"
            / CANONICAL_CHECKPOINT
            / "README.md"
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(card_md)
        print(f"[generate-cards] {rung} -> {out_path} ({len(card_md)} chars)")

    print(f"[generate-cards] published_rungs: {PUBLISHED_RUNGS}")
    print("[generate-cards] next: `make publish-hub` to push to HF Hub.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
