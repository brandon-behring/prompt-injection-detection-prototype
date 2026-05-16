"""ModernBERT-base loader with flash-attn-2 -> SDPA fallback (per ADR-020).

Per ADR-020 line 102, runpod-deploy's GPU failover ladder may land us on
smaller GPU classes without flash_attention_2 support. The recipe wraps
``AutoModelForSequenceClassification.from_pretrained`` in a try/except catching
``(ValueError, ImportError)``; the fallback path emits a ``flash_attn_fallback``
event so the audit trail captures which physical config produced each per-row
prediction.

Public API
----------
- ``MODERNBERT_BASE_HF_ID`` — ``"answerdotai/ModernBERT-base"``.
- ``load_modernbert(revision, num_labels=2, attn_impl_preferred="flash_attention_2",
  event_logger=None)`` — backbone loader with fallback recipe.
"""

from __future__ import annotations

from typing import Callable, cast

import torch
from transformers import AutoModelForSequenceClassification

MODERNBERT_BASE_HF_ID: str = "answerdotai/ModernBERT-base"


def load_modernbert(
    *,
    revision: str,
    num_labels: int = 2,
    attn_impl_preferred: str = "flash_attention_2",
    event_logger: Callable[..., None] | None = None,
) -> AutoModelForSequenceClassification:
    """Load ModernBERT-base with flash-attn-2 + SDPA fallback recipe.

    Parameters
    ----------
    revision : str
        HF revision SHA pinned via ``configs/data/source_manifest.yaml`` models
        section (per ADR-016 + ADR-018; manifest extension at Phase 1+).
    num_labels : int, optional
        Number of classification labels; default 2 (binary injection vs benign).
    attn_impl_preferred : str, optional
        Preferred attention implementation; default ``"flash_attention_2"`` per
        ADR-020. Fallback path uses HF default (SDPA on torch >= 2.1, eager
        otherwise) per the runpod-deploy flash-attention-fallback recipe.
    event_logger : Callable, optional
        Callable accepting ``(event_name: str, **payload)``. On fallback,
        called with ``("flash_attn_fallback", gpu=torch.cuda.get_device_name(0))``.
        If ``None``, fallback is silent (smoke-test path).

    Returns
    -------
    AutoModelForSequenceClassification
        Loaded ModernBERT-base model with ``attn_implementation`` set per the
        fallback ladder.

    Raises
    ------
    Exception
        Any exception other than ``(ValueError, ImportError)`` from
        ``from_pretrained`` propagates unchanged (e.g., network failure,
        revision SHA not found on HF Hub).
    """
    try:
        model = AutoModelForSequenceClassification.from_pretrained(
            MODERNBERT_BASE_HF_ID,
            revision=revision,
            attn_implementation=attn_impl_preferred,
            torch_dtype=torch.bfloat16,
            num_labels=num_labels,
        )
        return cast(AutoModelForSequenceClassification, model)
    except (ValueError, ImportError):
        if event_logger is not None and torch.cuda.is_available():
            event_logger("flash_attn_fallback", gpu=torch.cuda.get_device_name(0))
        model = AutoModelForSequenceClassification.from_pretrained(
            MODERNBERT_BASE_HF_ID,
            revision=revision,
            torch_dtype=torch.bfloat16,
            num_labels=num_labels,
        )
        return cast(AutoModelForSequenceClassification, model)
