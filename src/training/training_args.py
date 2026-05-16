"""Locked TrainingArguments factory per ADR-019 (transformer training recipe).

Shared across all 3 transformer rungs (frozen-probe, LoRA, full-FT). Per-GPU
batch sizing is supplied at runtime via ``batch_table.lookup_batch_config`` so
the effective batch (32) stays constant across the ADR-020 GPU failover ladder.

Public API
----------
- ``LEARNING_RATE``, ``WARMUP_RATIO``, ``NUM_TRAIN_EPOCHS``, ``MAX_GRAD_NORM``,
  ``WEIGHT_DECAY`` — locked scalars per ADR-019.
- ``build_training_args(output_dir, seed, per_device_train_batch_size,
  gradient_accumulation_steps)`` — returns ``TrainingArguments`` with the
  locked recipe.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from transformers import TrainingArguments

LEARNING_RATE: Final[float] = 1e-4
WARMUP_RATIO: Final[float] = 0.10
NUM_TRAIN_EPOCHS: Final[int] = 2
MAX_GRAD_NORM: Final[float] = 1.0
WEIGHT_DECAY: Final[float] = 0.01


def build_training_args(
    *,
    output_dir: Path,
    seed: int,
    per_device_train_batch_size: int,
    gradient_accumulation_steps: int,
) -> TrainingArguments:
    """Build ``TrainingArguments`` for any transformer rung at any seed.

    Parameters
    ----------
    output_dir : Path
        HF Trainer's output directory (per-(rung, fold, seed) sub-tree).
    seed : int
        Per ADR-044 Q1, one of ``(42, 43, 44)``.
    per_device_train_batch_size : int
        From ``batch_table.lookup_batch_config`` (ADR-020 BATCH_TABLE).
    gradient_accumulation_steps : int
        From ``batch_table.lookup_batch_config`` (ADR-020 BATCH_TABLE).

    Returns
    -------
    TrainingArguments
        Per ADR-019 recipe lock — ``lr=1e-4``, ``warmup_ratio=0.10``, cosine
        schedule, ``2 epochs``, ``bf16=True``, ``max_grad_norm=1.0``,
        ``weight_decay=0.01``, ``save_strategy="epoch"``, ``eval_strategy="no"``.
    """
    return TrainingArguments(
        output_dir=str(output_dir),
        learning_rate=LEARNING_RATE,
        warmup_ratio=WARMUP_RATIO,
        lr_scheduler_type="cosine",
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        num_train_epochs=NUM_TRAIN_EPOCHS,
        bf16=True,
        fp16=False,
        max_grad_norm=MAX_GRAD_NORM,
        weight_decay=WEIGHT_DECAY,
        save_strategy="epoch",
        eval_strategy="no",
        seed=seed,
        # AdamW (default) + AdamW eps=1e-8 inherited from HF Trainer defaults.
    )
