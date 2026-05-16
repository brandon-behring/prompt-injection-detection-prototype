"""Locked LoRA configuration per ADR-019 (LoRA + transformer training recipe).

Hyperparameters from LoRA paper (Hu et al. 2021) + HF PEFT defaults; specific
choices documented in ADR-019 §Decision. Explicit ``target_modules`` enumeration
(not ``all-linear`` auto-detection) per SDD discipline — deterministic across
PEFT versions; removes silent dependency on PEFT auto-detection logic.

Public API
----------
- ``LORA_R``, ``LORA_ALPHA``, ``LORA_DROPOUT`` — locked scalars.
- ``LORA_TARGET_MODULES`` — 4-tuple of suffixes covering ModernBERT's fused
  QKV + attention output + both MLP projections (4 × 22 layers = 88 LoRA
  adapters total in ModernBERT-base).
- ``LORA_MODULES_TO_SAVE`` — classifier head (full-FT alongside the adapters).
- ``build_lora_config()`` — returns the locked LoraConfig instance.
"""

from __future__ import annotations

from typing import Final

from peft import LoraConfig

LORA_R: Final[int] = 8
LORA_ALPHA: Final[int] = 16
LORA_DROPOUT: Final[float] = 0.1

# Per ADR-019 line 70 — explicit enumeration. ModernBERT encoder layer modules:
# Wqkv (fused QKV), attn.Wo (attention output), mlp.Wi (MLP input proj),
# mlp.Wo (MLP output proj). 4 modules × 22 layers = 88 LoRA adapters total.
LORA_TARGET_MODULES: Final[tuple[str, ...]] = ("Wqkv", "attn.Wo", "mlp.Wo", "mlp.Wi")
LORA_MODULES_TO_SAVE: Final[tuple[str, ...]] = ("classifier",)


def build_lora_config() -> LoraConfig:
    """Build the locked ``LoraConfig`` per ADR-019.

    Returns
    -------
    LoraConfig
        ``r=8`` + ``alpha=16`` + ``dropout=0.1`` + 4 explicit ``target_modules`` +
        ``modules_to_save=["classifier"]`` + ``task_type="SEQ_CLS"`` + ``bias="none"``.
    """
    return LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=list(LORA_TARGET_MODULES),
        modules_to_save=list(LORA_MODULES_TO_SAVE),
        task_type="SEQ_CLS",
        bias="none",
    )
