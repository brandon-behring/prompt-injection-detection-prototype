"""Locked TrainingArguments factory per ADR-019 (transformer training recipe).

Shared across all 3 transformer rungs (frozen-probe, LoRA, full-FT). Per-GPU
batch sizing is supplied at runtime via ``batch_table.lookup_batch_config`` so
the effective batch (32) stays constant across the ADR-020 GPU failover ladder.

Public API
----------
- ``LEARNING_RATE``, ``WARMUP_RATIO``, ``NUM_TRAIN_EPOCHS``, ``MAX_GRAD_NORM``,
  ``WEIGHT_DECAY`` — locked scalars per ADR-019.
- ``DATALOADER_NUM_WORKERS``, ``LOGGING_STEPS`` — throughput knobs.
- ``build_training_args(output_dir, seed, per_device_train_batch_size,
  gradient_accumulation_steps)`` — returns ``TrainingArguments`` with the
  locked recipe.

GPU-efficiency throughput knobs (added at Phase 4 X4 pre-flight, 2026-05-17)
---------------------------------------------------------------------------
Following the ADR-020 precedent that ``per_device_train_batch_size`` and
``gradient_accumulation_steps`` are throughput knobs (not methodology knobs)
when their product (effective batch) stays constant, the following A100/H100
hygiene flags are throughput-only and preserve the methodology contract:

- ``tf32=True`` — Ampere TF32 cores for FP32 matmul (optimizer + layernorm).
  ~5-10% speedup; ~10-bit mantissa precision on FP32 matmuls is well below
  the seed-noise floor at lr=1e-4 + 2 epochs + 3-seed protocol per ADR-019.
- ``optim="adamw_torch_fused"`` — fused AdamW kernel; ~10-20% faster on
  Ampere+. Same optimizer (AdamW); just the fused CUDA kernel variant.
- ``dataloader_num_workers=4`` — parallel tokenizer batches (CPU prep
  overlaps GPU compute); critical for max_length=8192 sequences where
  padding+collation can become CPU-bound.
- ``dataloader_pin_memory=True`` — pinned memory for faster H2D transfer
  (HF default; explicit for clarity).
- ``dataloader_persistent_workers=True`` — keeps workers alive across epochs
  (avoids spin-up overhead on epoch boundary).
- ``gradient_checkpointing=False`` — explicit; we have 80GB VRAM headroom
  on A100-SXM4-80GB; gradient checkpointing trades ~30% compute for memory
  which we do not need.
- ``logging_steps=10`` — visibility on a 1-2h run (HF default 500 is too
  sparse for headline-* monitoring).
- ``report_to="none"`` — disable W&B / TensorBoard reporting (no env
  configured; saves overhead).

Effective batch invariant per ADR-019 + ADR-020 BATCH_TABLE preserved.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import torch
from transformers import TrainingArguments

LEARNING_RATE: Final[float] = 1e-4
WARMUP_RATIO: Final[float] = 0.10
NUM_TRAIN_EPOCHS: Final[int] = 2
MAX_GRAD_NORM: Final[float] = 1.0
WEIGHT_DECAY: Final[float] = 0.01

# Throughput knobs (added at Phase 4 X4; see module docstring for rationale).
DATALOADER_NUM_WORKERS: Final[int] = 4
LOGGING_STEPS: Final[int] = 10


def _ampere_or_newer() -> bool:
    """Return True iff the local CUDA device is Ampere (SM 8.0) or newer.

    HF Trainer's ``TrainingArguments(tf32=True)`` raises at construction time
    on non-Ampere hardware (including no-GPU smoke runners), so the tf32 flag
    must be gated on this detection. Returns False on CPU-only hosts.
    """
    if not torch.cuda.is_available():
        return False
    major, _minor = torch.cuda.get_device_capability()
    return major >= 8


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
        Plus GPU-efficiency throughput knobs (see module docstring).
    """
    # Hardware-gated knobs — tf32 is Ampere+ only; bf16 + fused-AdamW require
    # CUDA. Smoke tests run on CPU-only hosts so these must degrade gracefully.
    has_cuda = torch.cuda.is_available()
    use_tf32 = _ampere_or_newer()
    use_bf16 = has_cuda  # bf16 requires CUDA; fallback to fp32 on CPU smoke
    use_fused_adamw = has_cuda  # fused AdamW kernel requires CUDA
    return TrainingArguments(
        output_dir=str(output_dir),
        learning_rate=LEARNING_RATE,
        warmup_ratio=WARMUP_RATIO,
        lr_scheduler_type="cosine",
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        num_train_epochs=NUM_TRAIN_EPOCHS,
        bf16=use_bf16,
        fp16=False,
        tf32=use_tf32,
        max_grad_norm=MAX_GRAD_NORM,
        weight_decay=WEIGHT_DECAY,
        save_strategy="epoch",
        eval_strategy="no",
        seed=seed,
        optim="adamw_torch_fused" if use_fused_adamw else "adamw_torch",
        gradient_checkpointing=False,
        dataloader_num_workers=DATALOADER_NUM_WORKERS,
        dataloader_pin_memory=True,
        dataloader_persistent_workers=True,
        logging_steps=LOGGING_STEPS,
        report_to="none",
        # AdamW eps=1e-8 inherited from HF Trainer defaults.
    )
