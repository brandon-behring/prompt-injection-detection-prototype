"""fp32 cast before final softmax/sigmoid (per ADR-019 numerical-stability discipline).

Applies to all trained transformer rungs (bf16 inference) + ProtectAI v1/v2
inference path per ADR-018. Preserves numerical stability uniformly across the
bf16-inference rungs.

Public API
----------
- ``softmax_fp32(logits, dim=-1)`` — softmax with fp32 cast.
- ``sigmoid_fp32(logits)`` — sigmoid with fp32 cast.
"""

from __future__ import annotations

import torch


def softmax_fp32(logits: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """Softmax with fp32 cast before computation (per ADR-019).

    Parameters
    ----------
    logits : torch.Tensor
        Pre-softmax logits, typically ``bf16`` from the transformer head.
    dim : int, optional
        Dimension to apply softmax over (default ``-1``, last dim).

    Returns
    -------
    torch.Tensor
        Softmax-normalized probabilities in ``fp32``.
    """
    return torch.softmax(logits.float(), dim=dim)


def sigmoid_fp32(logits: torch.Tensor) -> torch.Tensor:
    """Sigmoid with fp32 cast before computation (per ADR-019).

    Parameters
    ----------
    logits : torch.Tensor
        Pre-sigmoid logits, typically ``bf16``.

    Returns
    -------
    torch.Tensor
        Sigmoid-activated values in ``fp32``.
    """
    return torch.sigmoid(logits.float())
