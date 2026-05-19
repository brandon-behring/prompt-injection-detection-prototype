"""Windowed inference strategies for the ADR-060 DeBERTa-v3-base ablation.

Implements 2 truncation strategies per the locked methodology (reported
side-by-side as confound controls — neither claimed canonical):

- ``chunk_and_average_inference``: tokenize the full text; emit
  ``window_size``-token windows with ``stride`` overlap; per-window
  forward pass; average per-window class-1 softmax probabilities to
  obtain the final ``predicted_proba_class1``. Captures long-context
  signal at the cost of window-edge artifacts.
- ``head_truncation_inference``: tokenize the full text; take the first
  ``window_size`` tokens; standard single-window forward pass; emit
  ``predicted_proba_class1`` directly. Strict DeBERTa-v3 native
  behavior; loses information past the head window.

The pair isolates the long-context-vs-backbone confound in the
ModernBERT-vs-DeBERTa-v3-base headline ladder per ADR-060. A wide
chunk-and-average advantage over head-truncation indicates the
ModernBERT win is context-window-dominant; a narrow gap indicates the
ModernBERT win is backbone-dominant. Both directions are publishable.

History
-------
v1.1.2 Phase B (per ADR-060 carryforward). Greenfield; project-internal
infrastructure. Chunk-and-average is a ModernBERT-vs-DeBERTa-v3
confound-control pattern specific to this ablation, NOT a generic
eval-toolkit primitive (eval-toolkit's scope is evaluation metrics +
calibration + bootstrap, not model-inference strategies).

Implementation notes
--------------------
- Uses HF tokenizer's native sliding-window support via
  ``return_overflowing_tokens=True`` + ``stride`` parameters (library-
  first; avoids hand-rolling window-stride arithmetic). HF's tokenizer
  naturally handles short-text (<= window_size → 1 window) and long-text
  (>window_size → N windows) cases; partial-last-window padding is
  marked correctly via ``attention_mask`` so the model behaves correctly
  on it.
- Per-window forward pass is batched across all windows for a single
  text (one ``model(**enc)`` call per text). This is efficient on small
  models like DeBERTa-v3-base (~140M params): even a 30-window long text
  fits a single forward pass on L4/A100 at bf16.
- Numerical stability: ``softmax_fp32`` from ``src.training.softmax_cast``
  applies the fp32 cast before softmax per ADR-019.

Public API
----------
- ``chunk_and_average_inference(model, tokenizer, texts, window_size=512,
  stride=256)`` -> ``NDArray[np.float64]`` of shape ``(len(texts),)``.
- ``head_truncation_inference(model, tokenizer, texts, window_size=512,
  per_device_batch_size=4)`` -> ``NDArray[np.float64]`` of shape
  ``(len(texts),)``.
- ``predict_with_strategy(model, tokenizer, texts, strategy, window_size=512,
  stride=256, per_device_batch_size=4)`` -> ``NDArray[np.float64]`` —
  dispatches to one of the above per ADR-060 strategy lock.
"""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import torch
from numpy.typing import NDArray
from transformers import PreTrainedTokenizerBase

from src.training.softmax_cast import softmax_fp32

# Locked methodology constants per ADR-060.
WINDOW_SIZE_DEFAULT: int = 512  # DeBERTa-v3 native attention window
STRIDE_DEFAULT: int = 256  # 50% overlap per ADR-060 chunk_and_average
PER_DEVICE_BATCH_SIZE_DEFAULT: int = 4  # head_truncation across-text batching

TruncationStrategy = Literal["chunk_and_average", "head_truncation"]
VALID_STRATEGIES: frozenset[str] = frozenset(("chunk_and_average", "head_truncation"))


def _validate_window_params(window_size: int, stride: int | None) -> None:
    """Raise ValueError on invalid window_size / stride per ADR-060 lock.

    Parameters
    ----------
    window_size : int
        Must be positive.
    stride : int or None
        If not None: must be positive AND <= window_size (overlap is required
        for full coverage; stride > window_size would skip tokens).

    Raises
    ------
    ValueError
        With diagnostic context per the no-silent-failures discipline.
    """
    if window_size <= 0:
        raise ValueError(f"window_size must be positive per ADR-060 methodology; got {window_size}")
    if stride is not None:
        if stride <= 0:
            raise ValueError(f"stride must be positive per ADR-060 methodology; got {stride}")
        if stride > window_size:
            raise ValueError(
                f"stride ({stride}) must be <= window_size ({window_size}) "
                f"to ensure overlapping coverage of the full text"
            )


def chunk_and_average_inference(
    model: Any,
    tokenizer: PreTrainedTokenizerBase,
    texts: list[str],
    window_size: int = WINDOW_SIZE_DEFAULT,
    stride: int = STRIDE_DEFAULT,
) -> NDArray[np.float64]:
    """Chunk-and-average inference per ADR-060 methodology lock.

    For each text:
      1. Tokenize via HF native sliding-window (``stride`` +
         ``return_overflowing_tokens=True``).
      2. Forward-pass all windows for the text in a single batched call.
      3. Apply ``softmax_fp32`` to get per-window class probabilities
         (ADR-019 numerical stability).
      4. Average per-window predicted_proba_class1 -> final per-text score.

    Parameters
    ----------
    model : torch.nn.Module
        Sequence-classification model (e.g. DeBERTa-v3-base) in eval mode.
        Caller's responsibility to place on the right device; this function
        infers device from ``next(model.parameters()).device``.
    tokenizer : PreTrainedTokenizerBase
        Tokenizer matched to ``model`` (e.g. DeBERTa-v3 SentencePiece).
    texts : list[str]
        Inference inputs. Any length; windowing handles >window_size.
    window_size : int, optional
        Per-window token cap; default 512 (DeBERTa-v3 native window per
        ADR-060).
    stride : int, optional
        Overlap stride between windows; default 256 (50% overlap per ADR-060).

    Returns
    -------
    NDArray[np.float64]
        Shape ``(len(texts),)``; per-text averaged predicted_proba_class1.

    Raises
    ------
    ValueError
        If ``window_size`` or ``stride`` are invalid per ``_validate_window_params``.
    """
    _validate_window_params(window_size, stride)

    device = next(model.parameters()).device
    out = np.empty(len(texts), dtype=np.float64)

    model.eval()
    with torch.no_grad():
        for i, text in enumerate(texts):
            enc = tokenizer(
                text,
                max_length=window_size,
                stride=stride,
                return_overflowing_tokens=True,
                truncation=True,
                padding="max_length",
                return_tensors="pt",
            ).to(device)
            outputs = model(
                input_ids=enc["input_ids"],
                attention_mask=enc["attention_mask"],
            )
            probs = softmax_fp32(outputs.logits)  # (n_windows, 2)
            class1 = probs[:, 1].cpu().numpy().astype(np.float64)
            out[i] = float(class1.mean())

    return out


def head_truncation_inference(
    model: Any,
    tokenizer: PreTrainedTokenizerBase,
    texts: list[str],
    window_size: int = WINDOW_SIZE_DEFAULT,
    per_device_batch_size: int = PER_DEVICE_BATCH_SIZE_DEFAULT,
) -> NDArray[np.float64]:
    """Head-truncation inference per ADR-060 methodology lock.

    For each text: tokenize the full text; take the first ``window_size``
    tokens; standard single-window forward pass; emit
    ``predicted_proba_class1`` directly. Strict DeBERTa-v3 native
    behavior; loses information past the head window.

    Parameters
    ----------
    model, tokenizer, texts : same as ``chunk_and_average_inference``.
    window_size : int, optional
        Head truncation length; default 512 (DeBERTa-v3 native).
    per_device_batch_size : int, optional
        Inference batch size across texts; default 4. Each text -> 1 window,
        so batching across texts is straightforward (no per-text variable
        window count).

    Returns
    -------
    NDArray[np.float64]
        Shape ``(len(texts),)``; per-text predicted_proba_class1.

    Raises
    ------
    ValueError
        If ``window_size`` or ``per_device_batch_size`` are not positive.
    """
    _validate_window_params(window_size, stride=None)
    if per_device_batch_size <= 0:
        raise ValueError(f"per_device_batch_size must be positive; got {per_device_batch_size}")

    device = next(model.parameters()).device
    chunks: list[NDArray[np.float64]] = []

    model.eval()
    with torch.no_grad():
        for start in range(0, len(texts), per_device_batch_size):
            batch = texts[start : start + per_device_batch_size]
            enc = tokenizer(
                batch,
                max_length=window_size,
                truncation=True,
                padding=True,
                return_tensors="pt",
            ).to(device)
            outputs = model(**enc)
            probs = softmax_fp32(outputs.logits)  # (B, 2)
            chunks.append(probs[:, 1].cpu().numpy().astype(np.float64))

    return np.concatenate(chunks)


def predict_with_strategy(
    *,
    model: Any,
    tokenizer: PreTrainedTokenizerBase,
    texts: list[str],
    strategy: TruncationStrategy,
    window_size: int = WINDOW_SIZE_DEFAULT,
    stride: int = STRIDE_DEFAULT,
    per_device_batch_size: int = PER_DEVICE_BATCH_SIZE_DEFAULT,
) -> NDArray[np.float64]:
    """Dispatch to chunk_and_average vs head_truncation per ADR-060 lock.

    Reads the strategy switch (from ``configs/rungs/deberta_v3_base.yaml::
    truncation_strategy`` or per-fire env override) and routes accordingly.

    Parameters
    ----------
    strategy : Literal["chunk_and_average", "head_truncation"]
        Truncation strategy. Locked enumeration per ADR-060; unknown values
        raise ValueError (no-silent-failures discipline).
    (other params): forwarded to the dispatched function.

    Returns
    -------
    NDArray[np.float64]
        Shape ``(len(texts),)``; per-text predicted_proba_class1.

    Raises
    ------
    ValueError
        If ``strategy`` is not in ``VALID_STRATEGIES``.
    """
    if strategy not in VALID_STRATEGIES:
        raise ValueError(
            f"Unknown truncation strategy: {strategy!r}; must be one of "
            f"{sorted(VALID_STRATEGIES)} per ADR-060 methodology lock"
        )
    if strategy == "chunk_and_average":
        return chunk_and_average_inference(
            model=model,
            tokenizer=tokenizer,
            texts=texts,
            window_size=window_size,
            stride=stride,
        )
    # strategy == "head_truncation" (only remaining valid value).
    return head_truncation_inference(
        model=model,
        tokenizer=tokenizer,
        texts=texts,
        window_size=window_size,
        per_device_batch_size=per_device_batch_size,
    )
