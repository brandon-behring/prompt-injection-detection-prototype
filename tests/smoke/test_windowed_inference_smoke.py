"""Smoke tests for src/inference/windowed.py (v1.1.2 Phase B per ADR-060).

Validates the chunk-and-average + head-truncation truncation strategies and
the predict_with_strategy dispatcher. Uses mocked tokenizers + deterministic
models so smoke tests do not download DeBERTa-v3-base weights (~440 MB)
and run laptop-CPU-safe per ADR-027.

Coverage
--------
- ``chunk_and_average_inference``: window-count arithmetic + per-window
  softmax averaging on hand-controlled fixtures (1-window short text;
  3-window long text); output shape + dtype; ValueError validation on
  bad window_size / stride.
- ``head_truncation_inference``: batched-across-text inference path;
  output shape + dtype; ValueError validation on bad params.
- ``predict_with_strategy``: dispatch routing to each backend; ValueError
  on unknown strategy.
- Constants: ADR-060 locked defaults (window_size=512, stride=256).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import numpy as np
import pytest
import torch
from torch import nn


# --------------------------------------------------------------------------- #
# Test fixtures: stub tokenizer + deterministic models.
# --------------------------------------------------------------------------- #


class _MockBatchEncoding(dict[str, torch.Tensor]):
    """Mimics HF BatchEncoding for the minimal API used by windowed.py."""

    def __init__(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> None:
        super().__init__(input_ids=input_ids, attention_mask=attention_mask)
        self.input_ids = input_ids
        self.attention_mask = attention_mask

    def to(self, device: Any) -> "_MockBatchEncoding":
        """CPU-only smoke tests; .to() is a no-op."""
        return self


class _StubTokenizer:
    """Stub tokenizer mimicking HF sliding-window output for tests.

    Behavior:
    - If called with ``return_overflowing_tokens=True``: emits exactly
      ``n_windows_per_text`` windows per text (single-text input expected;
      chunk_and_average iterates per-text). Each window's first token is
      set to its window index + 1, so a model can distinguish windows.
    - Otherwise (head_truncation path): emits exactly 1 window per text in
      a batch input list. Sets first token to text-index + 1.

    Records each call in ``self.calls`` for assertion-driven tests.
    """

    def __init__(self, n_windows_per_text: int = 1) -> None:
        self.n_windows_per_text = n_windows_per_text
        self.calls: list[dict[str, Any]] = []

    def __call__(
        self,
        text_or_texts: Any,
        *,
        max_length: int,
        stride: int | None = None,
        return_overflowing_tokens: bool = False,
        truncation: bool = True,
        padding: Any = None,
        return_tensors: str | None = None,
        **kwargs: Any,
    ) -> _MockBatchEncoding:
        self.calls.append(
            {
                "text_or_texts": text_or_texts,
                "max_length": max_length,
                "stride": stride,
                "return_overflowing_tokens": return_overflowing_tokens,
                "padding": padding,
            }
        )
        if return_overflowing_tokens:
            n = self.n_windows_per_text
        else:
            n = len(text_or_texts) if isinstance(text_or_texts, list) else 1
        input_ids = torch.zeros((n, max_length), dtype=torch.long)
        attention_mask = torch.ones((n, max_length), dtype=torch.long)
        for i in range(n):
            input_ids[i, 0] = i + 1  # window/text id encoded in first token
        return _MockBatchEncoding(input_ids=input_ids, attention_mask=attention_mask)


class _ConstantLogitsModel(nn.Module):
    """Returns fixed logits regardless of input — for fixed-output tests."""

    def __init__(self, logits: tuple[float, float] = (0.0, 1.0)) -> None:
        super().__init__()
        # Need a real param so next(model.parameters()).device works.
        self._anchor = nn.Linear(1, 1)
        self.target_logits = logits
        self.n_forward_calls = 0

    def forward(self, **kwargs: Any) -> Any:
        self.n_forward_calls += 1
        input_ids = kwargs["input_ids"]
        n = input_ids.shape[0]
        out = torch.zeros((n, 2), dtype=torch.float32)
        out[:, 0] = self.target_logits[0]
        out[:, 1] = self.target_logits[1]
        return type("Output", (), {"logits": out})()


class _PerWindowLogitsModel(nn.Module):
    """Returns logits that depend on input_ids[:, 0] so each window gets a different score.

    Per-window logits: (0.0, input_ids[i, 0] - 1). So a window whose first
    token == 1 gets logits (0, 0) → class-1 softmax = 0.5; first token == 2
    gets (0, 1) → class-1 softmax ≈ 0.7311; first token == 3 → (0, 2) →
    class-1 softmax ≈ 0.8808; etc. Used to verify per-window averaging.
    """

    def __init__(self) -> None:
        super().__init__()
        self._anchor = nn.Linear(1, 1)

    def forward(self, **kwargs: Any) -> Any:
        input_ids = kwargs["input_ids"]
        n = input_ids.shape[0]
        first_tokens = input_ids[:, 0].float() - 1.0  # (n,)
        out = torch.zeros((n, 2), dtype=torch.float32)
        out[:, 1] = first_tokens
        return type("Output", (), {"logits": out})()


# --------------------------------------------------------------------------- #
# ADR-060 locked constants.
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_locked_constants_match_adr060() -> None:
    """ADR-060 locks window_size=512 + stride=256 + chunk-and-average + head-truncation."""
    from src.inference.windowed import (
        PER_DEVICE_BATCH_SIZE_DEFAULT,
        STRIDE_DEFAULT,
        VALID_STRATEGIES,
        WINDOW_SIZE_DEFAULT,
    )

    assert WINDOW_SIZE_DEFAULT == 512, "ADR-060 locks DeBERTa-v3 native 512-token window"
    assert STRIDE_DEFAULT == 256, "ADR-060 locks 50% overlap (stride 256 for window 512)"
    assert PER_DEVICE_BATCH_SIZE_DEFAULT > 0
    assert VALID_STRATEGIES == frozenset({"chunk_and_average", "head_truncation"})


# --------------------------------------------------------------------------- #
# chunk_and_average_inference tests.
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_chunk_and_average_single_window_short_text() -> None:
    """Short text (1 window) returns the single window's class-1 prob unchanged."""
    from src.inference.windowed import chunk_and_average_inference

    tokenizer: Any = _StubTokenizer(n_windows_per_text=1)
    model = _ConstantLogitsModel(logits=(0.0, 1.0))  # softmax class-1 ≈ 0.7311
    out = chunk_and_average_inference(model, tokenizer, ["short text"])
    assert out.shape == (1,)
    assert out.dtype == np.float64
    expected = float(torch.softmax(torch.tensor([0.0, 1.0]), dim=-1)[1])
    assert abs(out[0] - expected) < 1e-6
    assert model.n_forward_calls == 1


@pytest.mark.smoke
def test_chunk_and_average_three_windows_constant_logits() -> None:
    """3-window long text with constant per-window logits: mean == that constant."""
    from src.inference.windowed import chunk_and_average_inference

    tokenizer: Any = _StubTokenizer(n_windows_per_text=3)
    model = _ConstantLogitsModel(logits=(0.0, 1.0))
    out = chunk_and_average_inference(model, tokenizer, ["long text"])
    assert out.shape == (1,)
    expected = float(torch.softmax(torch.tensor([0.0, 1.0]), dim=-1)[1])
    assert abs(out[0] - expected) < 1e-6
    assert model.n_forward_calls == 1, "Should batch all windows in one forward call"


@pytest.mark.smoke
def test_chunk_and_average_per_window_averaging_arithmetic() -> None:
    """3-window text with per-window-varying logits: result = mean of 3 distinct probs."""
    from src.inference.windowed import chunk_and_average_inference

    tokenizer: Any = _StubTokenizer(n_windows_per_text=3)
    model = _PerWindowLogitsModel()
    out = chunk_and_average_inference(model, tokenizer, ["text"])
    # Per-window logits: (0, 0), (0, 1), (0, 2) -> class-1 = sigmoid(0)=0.5,
    # sigmoid(1)≈0.7311, sigmoid(2)≈0.8808 (since softmax over 2 classes ==
    # sigmoid of logit difference).
    expected_class1 = [
        float(torch.softmax(torch.tensor([0.0, float(i)]), dim=-1)[1]) for i in range(3)
    ]
    expected_mean = sum(expected_class1) / 3
    assert abs(out[0] - expected_mean) < 1e-6


@pytest.mark.smoke
def test_chunk_and_average_multiple_texts() -> None:
    """Multiple texts: outer loop per text; output shape (N,)."""
    from src.inference.windowed import chunk_and_average_inference

    tokenizer: Any = _StubTokenizer(n_windows_per_text=2)
    model = _ConstantLogitsModel(logits=(0.0, 1.0))
    texts = ["text_a", "text_b", "text_c"]
    out = chunk_and_average_inference(model, tokenizer, texts)
    assert out.shape == (3,)
    # Per-text invocations: 3 outer loop iterations, each calls tokenizer once
    # + model once. So 3 model.forward calls (NOT batched across texts).
    assert model.n_forward_calls == 3
    assert len(tokenizer.calls) == 3
    # Verify each tokenizer call used the sliding-window protocol.
    for call in tokenizer.calls:
        assert call["return_overflowing_tokens"] is True
        assert call["max_length"] == 512
        assert call["stride"] == 256
        assert call["padding"] == "max_length"


@pytest.mark.smoke
def test_chunk_and_average_rejects_zero_window_size() -> None:
    """window_size <= 0 raises ValueError."""
    from src.inference.windowed import chunk_and_average_inference

    tokenizer: Any = _StubTokenizer(n_windows_per_text=1)
    model = _ConstantLogitsModel()
    with pytest.raises(ValueError, match="window_size must be positive"):
        chunk_and_average_inference(model, tokenizer, ["text"], window_size=0)


@pytest.mark.smoke
def test_chunk_and_average_rejects_zero_stride() -> None:
    """stride <= 0 raises ValueError."""
    from src.inference.windowed import chunk_and_average_inference

    tokenizer: Any = _StubTokenizer(n_windows_per_text=1)
    model = _ConstantLogitsModel()
    with pytest.raises(ValueError, match="stride must be positive"):
        chunk_and_average_inference(model, tokenizer, ["text"], stride=0)


@pytest.mark.smoke
def test_chunk_and_average_rejects_stride_exceeds_window() -> None:
    """stride > window_size raises ValueError (would skip tokens)."""
    from src.inference.windowed import chunk_and_average_inference

    tokenizer: Any = _StubTokenizer(n_windows_per_text=1)
    model = _ConstantLogitsModel()
    with pytest.raises(ValueError, match=r"stride .* must be <= window_size"):
        chunk_and_average_inference(model, tokenizer, ["text"], window_size=512, stride=1024)


# --------------------------------------------------------------------------- #
# head_truncation_inference tests.
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_head_truncation_basic_shape_and_dtype() -> None:
    """head_truncation_inference returns shape (N,) of float64."""
    from src.inference.windowed import head_truncation_inference

    tokenizer: Any = _StubTokenizer()  # head path: 1 window per text in batch
    model = _ConstantLogitsModel(logits=(0.0, 1.0))
    out = head_truncation_inference(model, tokenizer, ["a", "b", "c"], per_device_batch_size=2)
    assert out.shape == (3,)
    assert out.dtype == np.float64
    expected = float(torch.softmax(torch.tensor([0.0, 1.0]), dim=-1)[1])
    assert all(abs(v - expected) < 1e-6 for v in out)


@pytest.mark.smoke
def test_head_truncation_batching_across_texts() -> None:
    """5 texts at per_device_batch_size=2 should yield 3 batches (2+2+1)."""
    from src.inference.windowed import head_truncation_inference

    tokenizer: Any = _StubTokenizer()
    model = _ConstantLogitsModel(logits=(0.0, 1.0))
    out = head_truncation_inference(
        model, tokenizer, ["a", "b", "c", "d", "e"], per_device_batch_size=2
    )
    assert out.shape == (5,)
    assert model.n_forward_calls == 3, "5 texts at batch_size=2 should yield 3 forward calls"
    # Verify each tokenizer call used the head-truncation protocol
    # (no return_overflowing_tokens, no stride).
    for call in tokenizer.calls:
        assert call["return_overflowing_tokens"] is False
        assert call["stride"] is None
        assert call["max_length"] == 512


@pytest.mark.smoke
def test_head_truncation_rejects_zero_window_size() -> None:
    """window_size <= 0 raises ValueError."""
    from src.inference.windowed import head_truncation_inference

    tokenizer: Any = _StubTokenizer()
    model = _ConstantLogitsModel()
    with pytest.raises(ValueError, match="window_size must be positive"):
        head_truncation_inference(model, tokenizer, ["text"], window_size=0)


@pytest.mark.smoke
def test_head_truncation_rejects_zero_batch_size() -> None:
    """per_device_batch_size <= 0 raises ValueError."""
    from src.inference.windowed import head_truncation_inference

    tokenizer: Any = _StubTokenizer()
    model = _ConstantLogitsModel()
    with pytest.raises(ValueError, match="per_device_batch_size must be positive"):
        head_truncation_inference(model, tokenizer, ["text"], per_device_batch_size=0)


# --------------------------------------------------------------------------- #
# predict_with_strategy dispatch tests.
# --------------------------------------------------------------------------- #


@pytest.mark.smoke
def test_predict_with_strategy_dispatches_chunk_and_average() -> None:
    """strategy='chunk_and_average' routes to chunk_and_average_inference."""
    from src.inference import windowed

    tokenizer: Any = _StubTokenizer(n_windows_per_text=1)
    model = _ConstantLogitsModel(logits=(0.0, 1.0))
    sentinel = np.array([0.42, 0.99], dtype=np.float64)
    with (
        patch.object(windowed, "chunk_and_average_inference", return_value=sentinel) as ca,
        patch.object(windowed, "head_truncation_inference") as ht,
    ):
        out = windowed.predict_with_strategy(
            model=model, tokenizer=tokenizer, texts=["a", "b"], strategy="chunk_and_average"
        )
    assert ca.called, "chunk_and_average_inference must be invoked"
    assert not ht.called, "head_truncation_inference must NOT be invoked"
    np.testing.assert_array_equal(out, sentinel)


@pytest.mark.smoke
def test_predict_with_strategy_dispatches_head_truncation() -> None:
    """strategy='head_truncation' routes to head_truncation_inference."""
    from src.inference import windowed

    tokenizer: Any = _StubTokenizer()
    model = _ConstantLogitsModel(logits=(0.0, 1.0))
    sentinel = np.array([0.11, 0.22], dtype=np.float64)
    with (
        patch.object(windowed, "chunk_and_average_inference") as ca,
        patch.object(windowed, "head_truncation_inference", return_value=sentinel) as ht,
    ):
        out = windowed.predict_with_strategy(
            model=model, tokenizer=tokenizer, texts=["a", "b"], strategy="head_truncation"
        )
    assert ht.called, "head_truncation_inference must be invoked"
    assert not ca.called, "chunk_and_average_inference must NOT be invoked"
    np.testing.assert_array_equal(out, sentinel)


@pytest.mark.smoke
def test_predict_with_strategy_rejects_unknown_strategy() -> None:
    """Unknown strategy raises ValueError per ADR-060 lock + no-silent-failures."""
    from src.inference.windowed import predict_with_strategy

    tokenizer: Any = _StubTokenizer()
    model = _ConstantLogitsModel()
    with pytest.raises(ValueError, match="Unknown truncation strategy"):
        predict_with_strategy(
            model=model,
            tokenizer=tokenizer,
            texts=["text"],
            strategy="native",  # type: ignore[arg-type]
        )
