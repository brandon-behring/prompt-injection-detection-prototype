"""CLI entrypoint — inference dispatcher for the (scorer × slice) grid.

Per ADR-018 + ADR-021 + ADR-046 Phase 4 inference recovery (X10 series). The
Phase 3 placeholder Makefile recipes `eval-reference-scorers-free` and
`eval-reference-scorers-paid` were echo-only stubs; this script wires the
actual dispatcher.

Scope (X10 / locked Round 2 Q1 = drop LLM judges):

- **Tier A (free)**: ProtectAI v1 + v2 on LODO test sources (4) + OOD slices (5).
- **Trained rungs**: frozen-probe + LoRA OOD inference using locally-persisted
  checkpoints; full-FT deferred until X11 re-fire produces checkpoints (its
  current checkpoints were deleted per ADR-019 cleanup_intermediate_checkpoints).
- **Tier B (paid LLM judges)**: explicitly SKIPPED — see plan file's Round 2
  Q1 decision (~$240 vs $14 estimate; not worth tonight's session budget).

Outputs conform to `src.eval.schemas.PredictionsRowModel`. File naming:

- Reference scorers (LODO + OOD): `<rung>__<source>.parquet`
- Trained rungs (OOD only):       `<rung>__fold<F>__seed<S>__<source>.parquet`

Per-source error isolation: a single source failing (e.g., HF Hub rate limit
on jbb_behaviors) skips that slice but does NOT abort the whole batch. Failed
slices are reported at the end.

Library-first: ProtectAI scorers are existing primitives in
`src.scoring.protectai.ProtectAIScorer.score_dataframe`. Source loading is
existing `src.data.loaders.load_source`. No reinvention.

Usage
-----
.. code-block:: bash

    # Tier A: ProtectAI v1+v2 on all LODO test sources + 5 OOD slices (10 cells)
    uv run python scripts/run_inference_battery.py --tier ref-free

    # Trained-rung OOD only (extends Phase 2 LODO predictions with OOD slices)
    uv run python scripts/run_inference_battery.py --tier trained --rung lora

    # Specific sources only (smoke test)
    uv run python scripts/run_inference_battery.py --tier ref-free --sources xstest

    # Smoke mode: limit each slice to 100 rows for fast end-to-end validation
    uv run python scripts/run_inference_battery.py --tier ref-free --sources bipia --smoke 50
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, cast

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.loaders import load_source  # noqa: E402
from src.scoring.protectai import ProtectAIScorer  # noqa: E402
from src.training.tfidf_lr import build_tfidf_lr_pipeline  # noqa: E402
from src.training.train_classical import load_config as load_classical_config  # noqa: E402

LODO_SOURCES: tuple[str, ...] = (
    "deepset_prompt_injections",
    "hackaprompt",
    "lakera_gandalf_ignore_instructions",
    "lakera_mosscap_prompt_injection",
)

OOD_SOURCES: tuple[str, ...] = (
    "notinject",
    "xstest",
    "jbb_behaviors",
    "bipia",
    "injecagent",
)

ALL_REFERENCE_SOURCES: tuple[str, ...] = LODO_SOURCES + OOD_SOURCES


def _load_source_with_smoke_cap(name: str, smoke_n: int | None) -> pd.DataFrame:
    """Load a source via src.data.loaders; optionally cap to smoke_n rows."""
    df = load_source(name)
    if smoke_n is not None and len(df) > smoke_n:
        df = df.head(smoke_n).reset_index(drop=True)
    return df


def run_protectai_tier(
    sources: list[str],
    output_root: Path,
    smoke_n: int | None,
) -> tuple[int, list[tuple[str, str, str]]]:
    """Score the (ProtectAI v1, v2) × sources grid.

    Returns
    -------
    (n_success, failures) where failures is a list of (scorer_id, source, error_msg) tuples.
    """
    n_success = 0
    failures: list[tuple[str, str, str]] = []
    from typing import Literal as _Literal

    for version in cast(tuple[_Literal["v1", "v2"], ...], ("v1", "v2")):
        print(f"[inference-battery] loading ProtectAI {version} ...", flush=True)
        scorer = ProtectAIScorer(version=version)
        rung_id = f"protectai-{version}"
        for src in sources:
            try:
                t0 = time.time()
                df_in = _load_source_with_smoke_cap(src, smoke_n)
                if df_in.empty:
                    print(f"[inference-battery] SKIP {rung_id}/{src}: empty source", flush=True)
                    continue
                df_out = scorer.score_dataframe(df_in)
                out_path = output_root / f"{rung_id}__{src}.parquet"
                output_root.mkdir(parents=True, exist_ok=True)
                df_out.to_parquet(out_path, index=False)
                elapsed = time.time() - t0
                print(
                    f"[inference-battery] wrote {rung_id}/{src}: {len(df_out)} rows in {elapsed:.1f}s",
                    flush=True,
                )
                n_success += 1
            except Exception as exc:  # noqa: BLE001 — error isolation per ADR-018
                msg = f"{type(exc).__name__}: {exc}"
                print(f"[inference-battery] FAIL {rung_id}/{src}: {msg}", flush=True)
                failures.append((rung_id, src, msg))
    return n_success, failures


def run_trained_rung_tier(
    rung: str,
    sources: list[str],
    output_root: Path,
    smoke_n: int | None,
) -> tuple[int, list[tuple[str, str, str]]]:
    """Score trained rung × (fold × seed × source) — OOD slates only.

    Uses checkpoints at `evals/checkpoints/<rung>/fold<F>/seed<S>/checkpoint-*/`.
    Loads each checkpoint, runs inference on each source DataFrame.

    Returns (n_success, failures) per pattern in run_protectai_tier.
    """
    # Late import to avoid loading torch + transformers in tier=ref-free path.
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from peft import PeftModel

    from src.training.train_modernbert import _predict_proba  # noqa: E402
    from src.training.load_modernbert import load_modernbert  # noqa: E402

    checkpoint_root = _REPO_ROOT / "evals" / "checkpoints" / rung
    if not checkpoint_root.exists():
        return 0, [(rung, "—", f"no checkpoints at {checkpoint_root}")]

    n_success = 0
    failures: list[tuple[str, str, str]] = []

    # Pre-load source DataFrames once (~10s total) — reused across (fold, seed).
    print(f"[inference-battery] pre-loading {len(sources)} sources ...", flush=True)
    src_dfs: dict[str, pd.DataFrame] = {}
    for src in sources:
        try:
            src_dfs[src] = _load_source_with_smoke_cap(src, smoke_n)
        except Exception as exc:  # noqa: BLE001
            failures.append((rung, src, f"load: {type(exc).__name__}: {exc}"))

    backbone_id = "answerdotai/ModernBERT-base"
    backbone_revision = "8949b909ec900327062f0ebf497f51aef5e6f0c8"
    tokenizer = AutoTokenizer.from_pretrained(backbone_id, revision=backbone_revision)

    # Iterate (fold, seed) checkpoints.
    for fold_dir in sorted(checkpoint_root.glob("fold*")):
        fold = int(fold_dir.name.replace("fold", ""))
        for seed_dir in sorted(fold_dir.glob("seed*")):
            seed = int(seed_dir.name.replace("seed", ""))
            # Pick the highest-numbered checkpoint (final-epoch) per cell.
            ckpts = sorted(
                seed_dir.glob("checkpoint-*"),
                key=lambda p: int(p.name.replace("checkpoint-", "")),
            )
            if not ckpts:
                continue
            ckpt = ckpts[-1]

            try:
                print(
                    f"[inference-battery] loading {rung}/fold{fold}/seed{seed}/{ckpt.name}",
                    flush=True,
                )
                if rung == "lora":
                    # PEFT: load base + apply adapter
                    base = load_modernbert(revision=backbone_revision, num_labels=2)
                    # cast to nn.Module so PeftModel.from_pretrained typing is happy
                    from torch.nn import Module

                    model: Any = PeftModel.from_pretrained(cast(Module, base), str(ckpt))
                else:
                    # frozen-probe / full-FT: standard HF from_pretrained on checkpoint dir
                    model = AutoModelForSequenceClassification.from_pretrained(str(ckpt))
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model = model.to(device)
                model.eval()

                for src, df_in in src_dfs.items():
                    if df_in.empty:
                        continue
                    try:
                        t0 = time.time()
                        # Use the same _predict_proba helper the training code uses
                        probs = _predict_proba(
                            model=model,
                            tokenizer=tokenizer,
                            test_df=df_in,
                            max_length=8192,
                            per_device_batch_size=2 if device == "cpu" else 8,
                        )
                        out = pd.DataFrame(
                            {
                                "rung": rung,
                                "fold": fold,
                                "seed": seed,
                                "epoch": 2,  # use final-epoch checkpoint
                                "row_idx_in_source": df_in["row_idx_in_source"].to_numpy(),
                                "source": df_in["source"].to_numpy(),
                                "text": df_in["text"].to_numpy(),
                                "label": df_in["label"].to_numpy(),
                                "predicted_proba_class1": probs[:, 1].astype(float),
                                "contamination_state": "backbone-partial-disjoint",
                            }
                        )
                        out_path = output_root / f"{rung}__fold{fold}__seed{seed}__{src}.parquet"
                        output_root.mkdir(parents=True, exist_ok=True)
                        out.to_parquet(out_path, index=False)
                        elapsed = time.time() - t0
                        print(
                            f"[inference-battery] wrote {rung}/fold{fold}/seed{seed}/{src}: "
                            f"{len(out)} rows in {elapsed:.1f}s",
                            flush=True,
                        )
                        n_success += 1
                    except Exception as exc:  # noqa: BLE001
                        msg = f"{type(exc).__name__}: {exc}"
                        print(
                            f"[inference-battery] FAIL {rung}/fold{fold}/seed{seed}/{src}: {msg}",
                            flush=True,
                        )
                        failures.append((f"{rung}/fold{fold}/seed{seed}", src, msg))

                # Free GPU memory before next checkpoint
                del model
                if device == "cuda":
                    torch.cuda.empty_cache()
            except Exception as exc:  # noqa: BLE001
                msg = f"{type(exc).__name__}: {exc}"
                print(
                    f"[inference-battery] FAIL load {rung}/fold{fold}/seed{seed}: {msg}", flush=True
                )
                failures.append((f"{rung}/fold{fold}/seed{seed}", "—", f"load: {msg}"))

    return n_success, failures


def run_classical_floor_ood_tier(
    sources: list[str],
    output_root: Path,
    smoke_n: int | None,
) -> tuple[int, list[tuple[str, str, str]]]:
    """Classical floor (TF-IDF + LR) per ADR-017: re-fit per (fold, seed) + score OOD sources.

    Why re-fit instead of loading: train_classical_floor.py does NOT persist
    the fitted Pipeline (only emits per-row LODO predictions parquets). For
    OOD extension, we re-fit on each (fold, seed) train.parquet (~5 sec each;
    12 cells × ~5s = 60 sec total) — cheap enough.

    Returns (n_success, failures) per pattern in run_protectai_tier.
    """
    config_path = _REPO_ROOT / "configs" / "rungs" / "classical_floor.yaml"
    if not config_path.exists():
        return 0, [("tfidf-lr", "—", f"config not found: {config_path}")]
    cfg = load_classical_config(config_path)
    processed_root = _REPO_ROOT / "data" / "processed"
    rung_id = "tfidf-lr"
    n_success = 0
    failures: list[tuple[str, str, str]] = []

    # Pre-load source DataFrames once.
    print(f"[inference-battery] pre-loading {len(sources)} sources ...", flush=True)
    src_dfs: dict[str, pd.DataFrame] = {}
    for src in sources:
        try:
            src_dfs[src] = _load_source_with_smoke_cap(src, smoke_n)
        except Exception as exc:  # noqa: BLE001
            failures.append((rung_id, src, f"load: {type(exc).__name__}: {exc}"))

    folds = list(range(4))
    seeds = list(cfg.get("seeds", [42, 43, 44]))
    for fold in folds:
        for seed in seeds:
            try:
                train_path = processed_root / f"fold-{fold}" / f"seed-{seed}" / "train.parquet"
                if not train_path.exists():
                    failures.append(
                        (rung_id, f"fold{fold}/seed{seed}", f"missing train: {train_path}")
                    )
                    continue
                train_df = pd.read_parquet(train_path)
                pipeline = build_tfidf_lr_pipeline(
                    seed=seed,
                    tfidf_cfg=cfg["tfidf"],
                    lr_cfg=cfg["logistic_regression"],
                )
                t0 = time.time()
                pipeline.fit(train_df["text"].tolist(), train_df["label"].astype(int).to_numpy())
                print(
                    f"[inference-battery] fit tfidf-lr fold{fold}/seed{seed} in {time.time() - t0:.1f}s",
                    flush=True,
                )

                for src, df_in in src_dfs.items():
                    if df_in.empty:
                        continue
                    try:
                        t0 = time.time()
                        probs = pipeline.predict_proba(df_in["text"].tolist())  # shape (N, 2)
                        out = pd.DataFrame(
                            {
                                "rung": rung_id,
                                "fold": fold,
                                "seed": seed,
                                "epoch": None,  # classical has no epoch concept per ADR-017
                                "row_idx_in_source": df_in["row_idx_in_source"].to_numpy(),
                                "source": df_in["source"].to_numpy(),
                                "text": df_in["text"].to_numpy(),
                                "label": df_in["label"].to_numpy(),
                                "predicted_proba_class1": probs[:, 1].astype(float),
                                "contamination_state": "verified_disjoint",
                            }
                        )
                        out_path = output_root / f"{rung_id}__fold{fold}__seed{seed}__{src}.parquet"
                        output_root.mkdir(parents=True, exist_ok=True)
                        out.to_parquet(out_path, index=False)
                        elapsed = time.time() - t0
                        print(
                            f"[inference-battery] wrote {rung_id}/fold{fold}/seed{seed}/{src}: "
                            f"{len(out)} rows in {elapsed:.1f}s",
                            flush=True,
                        )
                        n_success += 1
                    except Exception as exc:  # noqa: BLE001
                        msg = f"{type(exc).__name__}: {exc}"
                        print(
                            f"[inference-battery] FAIL {rung_id}/fold{fold}/seed{seed}/{src}: {msg}",
                            flush=True,
                        )
                        failures.append((f"{rung_id}/fold{fold}/seed{seed}", src, msg))
            except Exception as exc:  # noqa: BLE001
                msg = f"{type(exc).__name__}: {exc}"
                print(
                    f"[inference-battery] FAIL fit {rung_id}/fold{fold}/seed{seed}: {msg}",
                    flush=True,
                )
                failures.append((f"{rung_id}/fold{fold}/seed{seed}", "—", f"fit: {msg}"))
    return n_success, failures


def main() -> int:
    """Parse args, dispatch to selected tier, report success + failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tier",
        required=True,
        choices=["ref-free", "trained", "classical-ood"],
        help=(
            "ref-free = ProtectAI v1+v2 (LODO + OOD); "
            "trained = frozen-probe / LoRA / full-FT on OOD slates only (LODO from canonical); "
            "classical-ood = TF-IDF + LR re-fit per (fold, seed) on OOD slates only (LODO from make train-classical-floor)"
        ),
    )
    parser.add_argument(
        "--rung",
        choices=["frozen_probe", "lora", "full_ft"],
        help="Required when --tier trained; selects which trained rung's checkpoints to load",
    )
    parser.add_argument(
        "--sources",
        default=None,
        help=(
            "Comma-separated source names; default = all 9 (LODO + OOD) for ref-free, "
            "or 5 OOD slates only for trained tier"
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=_REPO_ROOT / "evals" / "predictions",
    )
    parser.add_argument(
        "--smoke",
        type=int,
        default=None,
        help="If set, cap each source to N rows for fast smoke validation (e.g., --smoke 50)",
    )
    args = parser.parse_args()

    # Default sources by tier.
    if args.sources:
        sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    elif args.tier == "ref-free":
        sources = list(ALL_REFERENCE_SOURCES)
    else:  # trained — OOD only (LODO predictions already exist from canonical training)
        sources = list(OOD_SOURCES)

    print(f"[inference-battery] tier={args.tier} sources={sources}", flush=True)
    if args.smoke:
        print(f"[inference-battery] SMOKE mode: cap each source to {args.smoke} rows", flush=True)
    t_start = time.time()

    if args.tier == "ref-free":
        n_success, failures = run_protectai_tier(sources, args.output_root, args.smoke)
    elif args.tier == "trained":
        if not args.rung:
            print("[inference-battery] ERROR: --rung required for --tier trained", file=sys.stderr)
            return 2
        n_success, failures = run_trained_rung_tier(
            args.rung, sources, args.output_root, args.smoke
        )
    elif args.tier == "classical-ood":
        n_success, failures = run_classical_floor_ood_tier(sources, args.output_root, args.smoke)
    else:
        print(f"[inference-battery] ERROR: unknown tier {args.tier!r}", file=sys.stderr)
        return 2

    elapsed = time.time() - t_start
    print(
        f"[inference-battery] DONE tier={args.tier}: {n_success} cells in {elapsed:.1f}s",
        flush=True,
    )
    if failures:
        print(f"[inference-battery] {len(failures)} failures:", file=sys.stderr)
        for scorer, src, msg in failures:
            print(f"  - {scorer}/{src}: {msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
