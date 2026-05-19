"""Generic HF backbone loader with flash-attn-2 -> SDPA fallback (per ADR-020).

Per ADR-020 line 102, runpod-deploy's GPU failover ladder may land us on smaller
GPU classes without flash_attention_2 support. The recipe wraps
``AutoModelForSequenceClassification.from_pretrained`` in a try/except catching
``(ValueError, ImportError)``; the fallback path emits a ``flash_attn_fallback``
event so the audit trail captures which physical config produced each per-row
prediction.

The function accepts an arbitrary ``hf_id`` so the same primitive serves both
the ModernBERT-base rungs (per ADR-019) and the DeBERTa-v3-base ablation
(per ADR-060). DeBERTa-v3 does not natively support flash_attention_2; the
fallback branch transparently degrades to stock SDPA on torch >= 2.1.

History
-------
v1.1.2 Phase A refactor (per ADR-060 carryforward): renamed from
``load_modernbert(*, revision, ...)`` to ``load_backbone(*, hf_id, revision, ...)``
to support DeBERTa-v3-base as a second backbone without code duplication. The
``MODERNBERT_BASE_HF_ID`` module-level constant was dropped — backbone identity
now flows from YAML config (``configs/rungs/<rung>.yaml::backbone.hf_id``)
through ``train_modernbert.py::prepare_model`` to this loader, preserving the
single-source-of-truth invariant per ADR-044 Q4.

Public API
----------
- ``load_backbone(*, hf_id, revision, num_labels=2,
  attn_impl_preferred="flash_attention_2", event_logger=None)`` — generic
  backbone loader with the flash-attn-fallback recipe.
"""

from __future__ import annotations

from typing import Callable, cast

import torch
from transformers import AutoModelForSequenceClassification


def load_backbone(
    *,
    hf_id: str,
    revision: str,
    num_labels: int = 2,
    attn_impl_preferred: str = "flash_attention_2",
    event_logger: Callable[..., None] | None = None,
) -> AutoModelForSequenceClassification:
    """Load any HF sequence-classification backbone with flash-attn-2 + SDPA fallback.

    Parameters
    ----------
    hf_id : str
        Hugging Face Hub model repository identifier — e.g.
        ``"answerdotai/ModernBERT-base"`` (per ADR-019) or
        ``"microsoft/deberta-v3-base"`` (per ADR-060). Must be passed
        explicitly; no default — this preserves the YAML-as-source-of-truth
        invariant per ADR-044 Q4.
    revision : str
        HF revision SHA pinned via the appropriate config file
        (``configs/data/source_manifest.yaml`` for ModernBERT per ADR-016 + ADR-018;
        ``configs/rungs/deberta_v3_base.yaml::backbone.revision`` for DeBERTa
        per ADR-060). Pinning is required for byte-level reproducibility.
    num_labels : int, optional
        Number of classification labels; default 2 (binary injection vs benign).
    attn_impl_preferred : str, optional
        Preferred attention implementation; default ``"flash_attention_2"`` per
        ADR-020. The fallback path uses HF default (SDPA on torch >= 2.1, eager
        otherwise) per the runpod-deploy flash-attention-fallback recipe.
        DeBERTa-v3 does not support flash_attention_2 so will deterministically
        hit the fallback branch; ModernBERT supports it natively on H100/H200/
        A100-class GPUs.
    event_logger : Callable, optional
        Callable accepting ``(event_name: str, **payload)``. On fallback, called
        with ``("flash_attn_fallback", gpu=torch.cuda.get_device_name(0), hf_id=hf_id)``.
        If ``None``, fallback is silent (smoke-test path).

    Returns
    -------
    AutoModelForSequenceClassification
        Loaded backbone with ``attn_implementation`` set per the fallback ladder.

    Raises
    ------
    Exception
        Any exception other than ``(ValueError, ImportError)`` from
        ``from_pretrained`` propagates unchanged (e.g., network failure,
        revision SHA not found on HF Hub).
    """
    try:
        model = AutoModelForSequenceClassification.from_pretrained(
            hf_id,
            revision=revision,
            attn_implementation=attn_impl_preferred,
            torch_dtype=torch.bfloat16,
            num_labels=num_labels,
        )
        return cast(AutoModelForSequenceClassification, model)
    except (ValueError, ImportError):
        if event_logger is not None and torch.cuda.is_available():
            event_logger(
                "flash_attn_fallback",
                gpu=torch.cuda.get_device_name(0),
                hf_id=hf_id,
            )
        model = AutoModelForSequenceClassification.from_pretrained(
            hf_id,
            revision=revision,
            torch_dtype=torch.bfloat16,
            num_labels=num_labels,
        )
        return cast(AutoModelForSequenceClassification, model)
