"""Adaptive batch sizing — preserves effective batch = 32 across GPU classes (per ADR-020 + ADR-044).

Per ADR-020, runpod-deploy's pod.gpu_order failover ladder may land us on any
of 8+ GPU classes. The BATCH_TABLE scales per_device_train_batch_size +
gradient_accumulation_steps together so their product (effective batch) stays
constant at 32 across classes. This is NOT hyperparameter tuning — effective
batch (the gradient-computation hyperparameter) is held constant; per_device +
grad_accum are throughput knobs that do not change the gradient computation.
Preserves SPEC §2 hyperparameter-immutability invariant under GPU substitution.

Public API
----------
- ``BATCH_TABLE`` — frozen mapping from GPU class key to BatchConfig.
- ``EFFECTIVE_BATCH`` — 32 (locked per ADR-019).
- ``classify_gpu(device_name) -> str`` — maps torch.cuda.get_device_name() to a
  BATCH_TABLE key; fail-loud on unknown class (per ADR-020 line 99).
- ``lookup_batch_config(device_name) -> BatchConfig`` — convenience wrapper.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Mapping

EFFECTIVE_BATCH: Final[int] = 32


@dataclass(frozen=True, slots=True)
class BatchConfig:
    """Per-device batch sizing for a single GPU class.

    Attributes
    ----------
    per_device : int
        per_device_train_batch_size for HF Trainer.
    grad_accum : int
        gradient_accumulation_steps for HF Trainer.

    Notes
    -----
    Invariant: per_device * grad_accum == ``EFFECTIVE_BATCH`` (32). Enforced
    in ``__post_init__``; violation raises ``ValueError``.
    """

    per_device: int
    grad_accum: int

    def __post_init__(self) -> None:
        if self.per_device * self.grad_accum != EFFECTIVE_BATCH:
            raise ValueError(
                f"BatchConfig(per_device={self.per_device}, grad_accum={self.grad_accum}) "
                f"violates effective-batch invariant — product must equal {EFFECTIVE_BATCH}"
            )


# Per ADR-020 lines 76-84. Keyed on classify_gpu output, NOT raw device names.
BATCH_TABLE: Final[Mapping[str, BatchConfig]] = {
    "H100": BatchConfig(per_device=16, grad_accum=2),
    "H200": BatchConfig(per_device=16, grad_accum=2),
    "A100-80G": BatchConfig(per_device=16, grad_accum=2),
    "A100-40G": BatchConfig(per_device=8, grad_accum=4),
    "L40S": BatchConfig(per_device=8, grad_accum=4),
    "L40": BatchConfig(per_device=4, grad_accum=8),
}


def classify_gpu(device_name: str) -> str:
    """Map ``torch.cuda.get_device_name()`` output to a BATCH_TABLE key.

    Parameters
    ----------
    device_name : str
        Output of ``torch.cuda.get_device_name(0)`` on the pod, e.g.
        ``"NVIDIA H100 80GB HBM3"`` or ``"NVIDIA A100-SXM4-40GB"``.

    Returns
    -------
    str
        BATCH_TABLE key — one of ``{H100, H200, A100-80G, A100-40G, L40S, L40}``.

    Raises
    ------
    KeyError
        If ``device_name`` does not match any BATCH_TABLE key. Per ADR-020 line
        99 fail-loud discipline — never silently default to a smaller batch
        config; require explicit ADR amendment.
    """
    name = device_name.upper()
    if "H100" in name:
        return "H100"
    if "H200" in name:
        return "H200"
    if "A100" in name:
        # Distinguish A100 80GB vs 40GB — RunPod part numbers include explicit memory.
        if "80G" in name or "80GB" in name:
            return "A100-80G"
        if "40G" in name or "40GB" in name:
            return "A100-40G"
        raise KeyError(
            f"A100 variant {device_name!r} not in BATCH_TABLE — add explicit entry "
            f"(per ADR-020 BATCH_TABLE supersession discipline)"
        )
    if "L40S" in name:
        return "L40S"
    if "L40" in name:
        return "L40"
    raise KeyError(
        f"GPU device name {device_name!r} not in BATCH_TABLE — add explicit entry "
        f"+ update ADR-020 BATCH_TABLE if a new GPU class needs support"
    )


def lookup_batch_config(device_name: str) -> BatchConfig:
    """Look up the BatchConfig for a GPU by device name.

    Parameters
    ----------
    device_name : str
        Output of ``torch.cuda.get_device_name(0)``.

    Returns
    -------
    BatchConfig
        Batch config for the classified GPU class.

    Raises
    ------
    KeyError
        Via ``classify_gpu`` if the device name is not in the table.
    """
    return BATCH_TABLE[classify_gpu(device_name)]
