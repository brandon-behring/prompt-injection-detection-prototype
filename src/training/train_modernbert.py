"""Multi-rung ModernBERT trainer (frozen_probe + lora + full_ft) per ADR-019 + ADR-044 Q5.

Dispatches on ``classifier_type`` from YAML config — ``frozen_probe`` /
``lora`` / ``full_ft``. Reads data from ``data/processed/``, fits via HF
``Trainer`` + ``WeightedTrainer``, persists per-row predictions per
``(rung, fold, seed, epoch)`` parquet per ADR-019 §Per-epoch save discipline.
Full-FT intermediate checkpoint subdirs are deleted post-training per ADR-019
line 154 storage policy.

Public API
----------
- ``load_config(config_path)`` -> dict — parses + validates a transformer YAML.
- ``prepare_model(classifier_type, backbone_revision, event_logger)`` -> model
  in the correct rung mode (freeze backbone / wrap with PEFT / no-op).
- ``train_one_cell(config_path, fold, seed, processed_root, predictions_root,
  checkpoint_root, event_logger)`` -> list of per-epoch parquet paths.
- ``PREDICTIONS_SCHEMA`` — tuple of column names in each per-epoch parquet.
- ``PerEpochPredictionsCallback`` — TrainerCallback hooking ``on_epoch_end``.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Callable, cast

import numpy as np
import pandas as pd
import torch
import yaml
from datasets import Dataset
from numpy.typing import NDArray
from peft import get_peft_model
from transformers import (
    AutoTokenizer,
    DataCollatorWithPadding,
    PreTrainedTokenizerBase,
    TrainerCallback,
    TrainerControl,
    TrainerState,
    TrainingArguments,
)

from src.training.batch_table import BatchConfig, lookup_batch_config
from src.training.load_modernbert import load_modernbert
from src.training.lora_config import build_lora_config
from src.training.softmax_cast import softmax_fp32
from src.training.training_args import build_training_args
from src.training.weighted_trainer import WeightedTrainer, compute_class_weights_tensor

VALID_CLASSIFIER_TYPES: frozenset[str] = frozenset({"frozen_probe", "lora", "full_ft"})

PREDICTIONS_SCHEMA: tuple[str, ...] = (
    "rung",
    "fold",
    "seed",
    "epoch",
    "row_idx_in_source",
    "source",
    "text",
    "label",
    "predicted_proba_class1",
)


def load_config(config_path: Path) -> dict[str, Any]:
    """Load and validate a transformer rung YAML config.

    Parameters
    ----------
    config_path : Path
        Path to ``configs/rungs/{frozen_probe, lora, full_ft}.yaml``.

    Returns
    -------
    dict
        Parsed + validated YAML.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    ValueError
        If ``classifier_type`` is not in ``VALID_CLASSIFIER_TYPES`` or required
        ``backbone.hf_id`` + ``backbone.revision`` fields are missing.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Rung config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    classifier_type = cfg.get("classifier_type")
    if classifier_type not in VALID_CLASSIFIER_TYPES:
        raise ValueError(
            f"{config_path}: classifier_type must be one of {sorted(VALID_CLASSIFIER_TYPES)}; "
            f"got {classifier_type!r}"
        )
    backbone = cfg.get("backbone") or {}
    if "hf_id" not in backbone or "revision" not in backbone:
        raise ValueError(
            f"{config_path}: must carry backbone.hf_id + backbone.revision per ADR-044 Q4"
        )
    return cast(dict[str, Any], cfg)


def prepare_model(
    *,
    classifier_type: str,
    backbone_revision: str,
    event_logger: Callable[..., None] | None = None,
) -> Any:
    """Build the ModernBERT model in the right rung mode.

    Parameters
    ----------
    classifier_type : str
        One of ``"frozen_probe"`` / ``"lora"`` / ``"full_ft"``.
    backbone_revision : str
        HF revision SHA for ``answerdotai/ModernBERT-base``.
    event_logger : Callable, optional
        Forwarded to ``load_modernbert`` for flash-attn fallback audit logging.

    Returns
    -------
    torch.nn.Module
        - ``frozen_probe``: backbone params have ``requires_grad=False``;
          classifier head trainable.
        - ``lora``: backbone wrapped via ``get_peft_model`` + ADR-019
          ``LoraConfig``; classifier head in ``modules_to_save``.
        - ``full_ft``: all params trainable (HF default).

    Raises
    ------
    ValueError
        If ``classifier_type`` is not in ``VALID_CLASSIFIER_TYPES``.
    """
    if classifier_type not in VALID_CLASSIFIER_TYPES:
        raise ValueError(
            f"Unknown classifier_type: {classifier_type!r}; "
            f"must be one of {sorted(VALID_CLASSIFIER_TYPES)}"
        )
    model: Any = load_modernbert(
        revision=backbone_revision,
        num_labels=2,
        event_logger=event_logger,
    )
    if classifier_type == "frozen_probe":
        for name, param in model.named_parameters():
            param.requires_grad = name.startswith("classifier")
    elif classifier_type == "lora":
        lora_cfg = build_lora_config()
        model = get_peft_model(model, lora_cfg)
    # full_ft: HF default leaves all params trainable; no action needed.
    return model


def _cpu_fallback_batch_config() -> BatchConfig:
    """BatchConfig for laptop-CPU smoke runs (no CUDA).

    Honors the ADR-020 effective-batch invariant (per_device * grad_accum == 32)
    while choosing a very small per_device to avoid CPU OOM at max_length=8192.
    """
    return BatchConfig(per_device=2, grad_accum=16)


def _get_batch_config() -> BatchConfig:
    """Resolve BatchConfig from current GPU; fall back to CPU smoke config."""
    if torch.cuda.is_available():
        return lookup_batch_config(torch.cuda.get_device_name(0))
    return _cpu_fallback_batch_config()


def _predict_proba(
    model: Any,
    tokenizer: PreTrainedTokenizerBase,
    test_df: pd.DataFrame,
    max_length: int,
    per_device_batch_size: int,
) -> NDArray[np.float32]:
    """Run inference on ``test_df``; return ``[N, 2]`` fp32 probabilities.

    Per ADR-019 numerical-stability discipline, applies ``softmax_fp32`` (casts
    bf16 logits to fp32 before softmax).
    """
    model.eval()
    device = next(model.parameters()).device

    chunks: list[NDArray[np.float32]] = []
    with torch.no_grad():
        for start in range(0, len(test_df), per_device_batch_size):
            batch_texts = test_df["text"].iloc[start : start + per_device_batch_size].tolist()
            inputs = tokenizer(
                batch_texts,
                truncation=True,
                max_length=max_length,
                padding=True,
                return_tensors="pt",
            ).to(device)
            outputs = model(**inputs)
            probs = softmax_fp32(outputs.logits)
            chunks.append(probs.cpu().numpy().astype(np.float32))
    return np.vstack(chunks)


def _write_predictions_parquet(
    *,
    model: Any,
    tokenizer: PreTrainedTokenizerBase,
    test_df: pd.DataFrame,
    rung_id: str,
    fold: int,
    seed: int,
    epoch: int,
    max_length: int,
    per_device_batch_size: int,
    predictions_root: Path,
    predictions_file_template: str,
) -> Path:
    """Run inference on test_df + write the per-epoch predictions parquet.

    Returns
    -------
    Path
        Absolute path to the written parquet file.
    """
    probs = _predict_proba(model, tokenizer, test_df, max_length, per_device_batch_size)
    predictions = pd.DataFrame(
        {
            "rung": rung_id,
            "fold": fold,
            "seed": seed,
            "epoch": epoch,
            "row_idx_in_source": test_df["row_idx_in_source"].to_numpy(),
            "source": test_df["source"].to_numpy(),
            "text": test_df["text"].to_numpy(),
            "label": test_df["label"].to_numpy(),
            "predicted_proba_class1": probs[:, 1],
        }
    )
    predictions_root.mkdir(parents=True, exist_ok=True)
    out_path = predictions_root / predictions_file_template.format(
        fold=fold, seed=seed, epoch=epoch
    )
    predictions.to_parquet(out_path, index=False)
    return out_path


class PerEpochPredictionsCallback(TrainerCallback):
    """Save per-row predictions after each epoch (per ADR-019 §Per-epoch save).

    Hooks HF Trainer's ``on_epoch_end`` event with the live in-memory model
    (no disk round-trip required). Per ADR-019 the headline number is the
    epoch-2 prediction; epoch-1 is reported as a diagnostic ablation.

    Parameters
    ----------
    rung_id, fold, seed : str/int/int
        Identify the (rung, fold, seed) cell.
    test_df : pandas.DataFrame
        Held-out test set (per LODO fold).
    tokenizer : PreTrainedTokenizerBase
        ModernBERT tokenizer (loaded once at trainer entry).
    max_length, per_device_batch_size : int/int
        Inference-time tokenization + batching (smaller batch sizes are fine
        at inference because backward graphs are not constructed).
    predictions_root : Path
        ``evals/predictions/`` (parquet files written here).
    predictions_file_template : str
        Format string with ``{fold}``, ``{seed}``, ``{epoch}`` placeholders.
    """

    def __init__(
        self,
        *,
        rung_id: str,
        fold: int,
        seed: int,
        test_df: pd.DataFrame,
        tokenizer: PreTrainedTokenizerBase,
        max_length: int,
        per_device_batch_size: int,
        predictions_root: Path,
        predictions_file_template: str,
    ) -> None:
        self.rung_id = rung_id
        self.fold = fold
        self.seed = seed
        self.test_df = test_df
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.per_device_batch_size = per_device_batch_size
        self.predictions_root = predictions_root
        self.predictions_file_template = predictions_file_template
        self.written_paths: list[Path] = []

    def on_epoch_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs: Any,
    ) -> TrainerControl:
        """Run inference on test_df + save predictions parquet for the just-finished epoch."""
        model = kwargs.get("model")
        if model is None:
            return control
        epoch = int(round(state.epoch)) if state.epoch is not None else 0
        out_path = _write_predictions_parquet(
            model=model,
            tokenizer=self.tokenizer,
            test_df=self.test_df,
            rung_id=self.rung_id,
            fold=self.fold,
            seed=self.seed,
            epoch=epoch,
            max_length=self.max_length,
            per_device_batch_size=self.per_device_batch_size,
            predictions_root=self.predictions_root,
            predictions_file_template=self.predictions_file_template,
        )
        self.written_paths.append(out_path)
        return control


def _cleanup_intermediate_checkpoints(checkpoint_dir: Path) -> None:
    """Remove HF Trainer ``checkpoint-N`` subdirs (full-FT storage discipline per ADR-019)."""
    if not checkpoint_dir.exists():
        return
    for child in checkpoint_dir.iterdir():
        if child.is_dir() and child.name.startswith("checkpoint-"):
            shutil.rmtree(child)


def train_one_cell(
    *,
    config_path: Path,
    fold: int,
    seed: int,
    processed_root: Path,
    predictions_root: Path,
    checkpoint_root: Path,
    checkpoint_staging_root: Path | None = None,
    event_logger: Callable[..., None] | None = None,
) -> list[Path]:
    """Train one ``(rung, fold, seed)`` cell; write per-epoch predictions parquets.

    Parameters
    ----------
    config_path : Path
        Path to ``configs/rungs/<rung>.yaml``.
    fold : int
        LODO fold index (0-3 per ADR-016).
    seed : int
        One of ``(42, 43, 44)`` per ADR-044 Q1.
    processed_root : Path
        Phase 1 materialized splits root (``data/processed/``).
    predictions_root : Path
        Per-epoch parquet output root (``evals/predictions/``).
    checkpoint_root : Path
        Final-checkpoint root. After training completes the final-epoch dir
        is copied here (``evals/checkpoints/``); orchestrator artifact-pull
        finds it at this path.
    checkpoint_staging_root : Path, optional
        If set, HF Trainer writes per-step checkpoints here during training;
        after ``trainer.train()`` + ``_cleanup_intermediate_checkpoints`` the
        remaining final-epoch dir is copied to ``checkpoint_root``. Workaround
        for FUSE F_SETLKW hangs (HF Trainer atomic-save stalls on MooseFS).
        On RunPod pods set this to ``/root/training_staging`` (overlay disk).
        Default ``None`` keeps prior behavior (Trainer writes directly to
        ``checkpoint_root``).
    event_logger : Callable, optional
        Forwarded to flash-attn fallback recipe in ``load_modernbert``.

    Returns
    -------
    list[Path]
        Per-epoch parquet paths (length == ``training.num_train_epochs``).

    Raises
    ------
    FileNotFoundError
        If the per-(fold, seed) split parquets are missing.
    """
    cfg = load_config(config_path)
    classifier_type: str = cfg["classifier_type"]
    rung_id: str = cfg["rung_id"]

    seed_dir = processed_root / f"fold-{fold}" / f"seed-{seed}"
    train_path = seed_dir / "train.parquet"
    test_path = seed_dir / "test.parquet"
    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError(f"Phase 1 splits missing for fold={fold} seed={seed} at {seed_dir}")
    train_df = pd.read_parquet(train_path)
    test_df = pd.read_parquet(test_path)

    tokenizer = AutoTokenizer.from_pretrained(
        cfg["backbone"]["hf_id"],
        revision=cfg["backbone"]["revision"],
    )
    model = prepare_model(
        classifier_type=classifier_type,
        backbone_revision=cfg["backbone"]["revision"],
        event_logger=event_logger,
    )

    max_length: int = cfg["tokenizer"]["max_length"]
    train_encodings = tokenizer(
        train_df["text"].tolist(),
        truncation=True,
        max_length=max_length,
        padding=False,  # dynamic padding via DataCollator at batch time
    )
    train_dataset = Dataset.from_dict(
        {
            **train_encodings,
            "labels": train_df["label"].astype(int).tolist(),
        }
    )

    batch_cfg = _get_batch_config()
    rel_dir = cfg["checkpoint_dir_template"].format(fold=fold, seed=seed)
    final_output_dir = checkpoint_root / rel_dir
    # Staging dir: where HF Trainer writes during training. Defaults to final_output_dir
    # (preserves prior behavior). When staging_root differs, atomic-save hangs on FUSE
    # paths (HF Trainer's atomic-rename protocol stalls on MooseFS F_SETLKW); pinning
    # staging to /root (overlay disk) bypasses the bug. Final-epoch dir is copied to
    # final_output_dir after training completes for orchestrator artifact pull.
    if checkpoint_staging_root is not None:
        staging_output_dir = checkpoint_staging_root / rel_dir
    else:
        staging_output_dir = final_output_dir
    training_args = build_training_args(
        output_dir=staging_output_dir,
        seed=seed,
        per_device_train_batch_size=batch_cfg.per_device,
        gradient_accumulation_steps=batch_cfg.grad_accum,
    )

    class_weights = compute_class_weights_tensor(train_df["label"].astype(int).to_numpy())

    callback = PerEpochPredictionsCallback(
        rung_id=rung_id,
        fold=fold,
        seed=seed,
        test_df=test_df,
        tokenizer=tokenizer,
        max_length=max_length,
        per_device_batch_size=batch_cfg.per_device,
        predictions_root=predictions_root,
        predictions_file_template=cfg["predictions_file_template"],
    )
    trainer = WeightedTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=DataCollatorWithPadding(
            tokenizer,
            pad_to_multiple_of=cfg["tokenizer"].get("pad_to_multiple_of", 8),
        ),
        class_weights=class_weights,
        callbacks=[callback],
    )
    trainer.train()

    # Full-FT storage discipline (per ADR-019 line 154) — predictions are the
    # audit-relevant artifact; intermediate ~150 MB weight checkpoints are not.
    if cfg.get("cleanup_intermediate_checkpoints", False):
        _cleanup_intermediate_checkpoints(staging_output_dir)

    # If we trained into a staging dir off-/workspace (FUSE bypass), copy the
    # remaining final-epoch contents to final_output_dir for orchestrator pull.
    # Simple file-by-file copy (NOT atomic-rename) sidesteps the FUSE F_SETLKW
    # bug that broke HF Trainer's atomic-save. shutil.copytree's recursive copy
    # uses ordinary open()/write() syscalls on FUSE — those work normally.
    if checkpoint_staging_root is not None and staging_output_dir != final_output_dir:
        if staging_output_dir.exists():
            final_output_dir.mkdir(parents=True, exist_ok=True)
            for child in staging_output_dir.iterdir():
                dest = final_output_dir / child.name
                if child.is_dir():
                    shutil.copytree(child, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(child, dest)
            # Free /root space — staging dir no longer needed after copy succeeds
            shutil.rmtree(staging_output_dir, ignore_errors=True)

    return callback.written_paths
