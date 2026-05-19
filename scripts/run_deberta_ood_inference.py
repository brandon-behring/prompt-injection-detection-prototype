"""Run DeBERTa-v3-base OOD inference on the 5-slice slate per ADR-060.

The Phase 2 ``scripts/run_inference_battery.py`` orchestrator was designed
for ModernBERT rungs whose checkpoints live at
``evals/checkpoints/<rung>/fold<F>/seed<S>/checkpoint-<step>/`` and use the
``native`` (single-pass, max_length=8192) inference path. The DeBERTa
ablation per ADR-060 has a different shape:
  - Checkpoints under ``evals/checkpoints/deberta_v3_base/<strategy>/fold0/seed42/``
    (extra nesting level for the 2 truncation strategies).
  - Inference path = ``predict_with_strategy`` from ``src/inference/windowed.py``
    (chunk-and-average + head-truncation strategies).

Rather than overload the ModernBERT-shaped ``run_inference_battery.py`` for
the ablation, this script implements the narrower DeBERTa OOD-inference
dispatch directly. Output parquets land at
``evals/predictions/deberta_v3_base_<strategy>__fold0__seed42__<slice>.parquet``
matching the existing ``<rung>__fold<F>__seed<S>__<slice>.parquet`` naming
that ``scripts/run_metrics_battery.py`` consumes.

Usage
-----
.. code-block:: bash

    uv run python scripts/run_deberta_ood_inference.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.loaders import load_source  # noqa: E402
from src.inference.windowed import predict_with_strategy  # noqa: E402

OOD_SOURCES: tuple[str, ...] = (
    "notinject",
    "xstest",
    "jbb_behaviors",
    "bipia",
    "injecagent",
)
STRATEGIES: tuple[str, ...] = ("chunk_and_average", "head_truncation")
BACKBONE_HF_ID: str = "microsoft/deberta-v3-base"
BACKBONE_REVISION: str = "8ccc9b6f36199bec6961081d44eb72fb3f7353f3"
FOLD: int = 0
SEED: int = 42
EPOCH_REPORTED: int = 2  # ADR-019 — headline epoch is epoch-2 (final)

# Inference window+stride per ADR-060 methodology lock (DeBERTa-v3 native 512;
# 50% overlap for chunk_and_average).
WINDOW_SIZE: int = 512
STRIDE: int = 256
PER_DEVICE_BATCH_SIZE: int = 4


def main() -> int:
    """Run DeBERTa OOD inference; write 10 parquets (2 strategies x 5 slices)."""
    output_root = _REPO_ROOT / "evals" / "predictions"
    output_root.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(BACKBONE_HF_ID, revision=BACKBONE_REVISION)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[deberta-ood] device={device}")

    for strategy in STRATEGIES:
        ckpt_dir = (
            _REPO_ROOT
            / "evals"
            / "checkpoints"
            / "deberta_v3_base"
            / strategy
            / f"fold{FOLD}"
            / f"seed{SEED}"
        )
        ckpts = sorted(
            ckpt_dir.glob("checkpoint-*"),
            key=lambda p: int(p.name.replace("checkpoint-", "")),
        )
        if not ckpts:
            print(f"[deberta-ood] ERROR: no checkpoints at {ckpt_dir}", file=sys.stderr)
            return 1
        final_ckpt = ckpts[-1]  # epoch-2 final checkpoint
        print(f"[deberta-ood] loading {strategy} from {final_ckpt}")

        model = AutoModelForSequenceClassification.from_pretrained(
            str(final_ckpt),
            torch_dtype=torch.float32,
        )
        model = model.to(device).eval()

        rung_id = f"deberta_v3_base_{strategy}"
        for src in OOD_SOURCES:
            t0 = time.time()
            df_in = load_source(src)
            class1 = predict_with_strategy(
                model=model,
                tokenizer=tokenizer,
                texts=df_in["text"].tolist(),
                strategy=strategy,  # type: ignore[arg-type]
                window_size=WINDOW_SIZE,
                stride=STRIDE,
                per_device_batch_size=PER_DEVICE_BATCH_SIZE,
            )
            df_out = pd.DataFrame(
                {
                    "rung": rung_id,
                    "fold": FOLD,
                    "seed": SEED,
                    "epoch": EPOCH_REPORTED,
                    "row_idx_in_source": df_in["row_idx_in_source"].to_numpy(),
                    "source": df_in["source"].to_numpy(),
                    "text": df_in["text"].to_numpy(),
                    "label": df_in["label"].to_numpy(),
                    "predicted_proba_class1": class1.astype(float),
                }
            )
            out_path = output_root / f"{rung_id}__fold{FOLD}__seed{SEED}__{src}.parquet"
            df_out.to_parquet(out_path, index=False)
            print(
                f"[deberta-ood] wrote {out_path.name}: {len(df_out)} rows in {time.time() - t0:.1f}s",
                flush=True,
            )

        del model
        if device == "cuda":
            torch.cuda.empty_cache()

    print("[deberta-ood] DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
