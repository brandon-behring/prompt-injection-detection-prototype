"""WeightedTrainer subclass with sklearn-style class_weight balanced loss (per ADR-019).

Implements ``CrossEntropyLoss`` with a per-fold-recomputed ``compute_class_weight``
tensor. Uniform convention with the TF-IDF + LR classical floor rung's
``class_weight="balanced"`` setting (per ADR-017), enabling clean cross-rung
lift attribution across the 4-rung trained slate.

Public API
----------
- ``WeightedTrainer`` — HF ``Trainer`` subclass overriding ``compute_loss``.
- ``compute_class_weights_tensor(train_labels)`` — sklearn balanced weights as
  a ``torch.Tensor``.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import torch
from numpy.typing import NDArray
from sklearn.utils.class_weight import compute_class_weight
from torch.nn import CrossEntropyLoss
from transformers import Trainer


class WeightedTrainer(Trainer):
    """HF Trainer with sklearn-style class_weight balanced CE loss.

    Parameters
    ----------
    class_weights : torch.Tensor
        Per-class loss weights (per-fold recomputed via sklearn
        ``compute_class_weight``; passed in by the trainer entrypoint).
    """

    def __init__(self, *args: Any, class_weights: torch.Tensor, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._class_weights = class_weights

    def compute_loss(  # type: ignore[override]
        self,
        model: Any,
        inputs: dict[str, Any],
        return_outputs: bool = False,
        **kwargs: Any,
    ) -> Any:
        """CE loss with class_weights tensor moved to the logits' device."""
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = CrossEntropyLoss(weight=self._class_weights.to(logits.device))
        loss = loss_fct(logits, labels)
        return (loss, outputs) if return_outputs else loss


def compute_class_weights_tensor(train_labels: NDArray[np.int_]) -> torch.Tensor:
    """Compute sklearn-style class_weight balanced as a torch tensor.

    Parameters
    ----------
    train_labels : numpy.ndarray
        1-D int array of training labels (0 or 1).

    Returns
    -------
    torch.Tensor
        Float32 tensor of length 2 — sklearn balanced weights for class 0 + 1.
    """
    weights = compute_class_weight(
        class_weight="balanced",
        classes=np.array([0, 1]),
        y=train_labels,
    )
    return torch.tensor(weights, dtype=torch.float32)
