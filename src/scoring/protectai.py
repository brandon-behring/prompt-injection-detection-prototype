"""ProtectAI deberta-v3-base-prompt-injection scorer (v1 + v2) per ADR-018.

Tier A reference scorer per ADR-045 Q4 — free local HF inference; safe for
CI smoke. Both v1 + v2 share the same inference path; the model repository
+ revision SHA discriminate them. Inference uses bf16 on GPU when available
plus head-truncation at 512 tokens (DeBERTa-v3-base native cap) per ADR-018
line 76.

Outputs conform to the unified PredictionsRowModel contract from
`src.eval.schemas` per ADR-045 Q3. Contamination state is hardcoded to
`suspected_contamination` per ADR-018 four-tier taxonomy (ProtectAI's
training corpus disclosure is partial and may include eval positives).

Usage
-----
.. code-block:: python

    from src.scoring.protectai import ProtectAIScorer

    scorer = ProtectAIScorer(version="v1")  # or "v2"
    df_out = scorer.score_dataframe(df_in, source_column="source")
    # df_out has PredictionsRowModel schema; rung="protectai-v1", fold=-1, seed=-1, epoch=None.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, cast

import numpy as np
import pandas as pd
import torch
from numpy.typing import NDArray
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.eval.schemas import PredictionsRowModel

# Locked HF model IDs per ADR-018 line 60.
_REPO_V1: str = "protectai/deberta-v3-base-prompt-injection"
_REPO_V2: str = "protectai/deberta-v3-base-prompt-injection-v2"
_RUNG_V1: str = "protectai-v1"
_RUNG_V2: str = "protectai-v2"

# DeBERTa-v3-base native context cap per ADR-018 line 76.
PROTECTAI_MAX_LENGTH: int = 512

# ProtectAI both versions report class 1 = "INJECTION" per their model cards.
_INJECTION_LABEL_INDEX: int = 1


@dataclass(frozen=True, slots=True)
class ProtectAIConfig:
    """Frozen config for a single ProtectAI scorer invocation."""

    version: Literal["v1", "v2"]
    repo_id: str
    rung_id: str
    revision: str | None  # SHA from configs/data/source_manifest.yaml models section; None = HEAD
    max_length: int = PROTECTAI_MAX_LENGTH
    batch_size: int = 32
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    dtype: torch.dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32


def _resolve_config(version: Literal["v1", "v2"], revision: str | None) -> ProtectAIConfig:
    """Build a ProtectAIConfig from the version + revision-SHA inputs."""
    if version == "v1":
        return ProtectAIConfig(version="v1", repo_id=_REPO_V1, rung_id=_RUNG_V1, revision=revision)
    return ProtectAIConfig(version="v2", repo_id=_REPO_V2, rung_id=_RUNG_V2, revision=revision)


class ProtectAIScorer:
    """ProtectAI v1 + v2 inference wrapper.

    Loads the HF model + tokenizer once; reuses across `score_batch` calls
    for throughput. Use a fresh instance per (version, revision) tuple.

    Parameters
    ----------
    version : {"v1", "v2"}
        Which ProtectAI model to load.
    revision : str or None, optional
        HF revision SHA from the manifest's models section. None loads HEAD
        (only acceptable in dev / smoke — production runs must pin via the
        manifest per ADR-018 line 124).
    model : Any, optional
        Pre-loaded HF model for test injection. If provided, skips
        `from_pretrained` (allows smoke tests to use a tiny mock).
    tokenizer : Any, optional
        Pre-loaded HF tokenizer for test injection.
    """

    def __init__(
        self,
        *,
        version: Literal["v1", "v2"],
        revision: str | None = None,
        model: Any = None,
        tokenizer: Any = None,
    ) -> None:
        self.config = _resolve_config(version=version, revision=revision)
        if model is None or tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.config.repo_id,
                revision=self.config.revision,
            )
            loaded_model = AutoModelForSequenceClassification.from_pretrained(
                self.config.repo_id,
                revision=self.config.revision,
                torch_dtype=self.config.dtype,
            )
            self._model = loaded_model.to(self.config.device)
        else:
            self._tokenizer = tokenizer
            self._model = model.to(self.config.device) if hasattr(model, "to") else model
        self._model.eval()

    def score_batch(self, texts: list[str]) -> NDArray[np.float64]:
        """Score a batch of texts; return per-text predicted_proba_class1.

        Parameters
        ----------
        texts : list of str
            Input texts (length unconstrained; head-truncated to
            `max_length=512` at tokenization per DeBERTa-v3-base native cap).

        Returns
        -------
        numpy.ndarray
            Float64 array of shape (len(texts),) with values in [0, 1].
        """
        if not texts:
            return np.zeros(0, dtype=np.float64)

        all_scores: list[NDArray[np.float64]] = []
        with torch.no_grad():
            for start in range(0, len(texts), self.config.batch_size):
                batch = texts[start : start + self.config.batch_size]
                encoded = self._tokenizer(
                    batch,
                    truncation=True,
                    max_length=self.config.max_length,
                    padding=True,
                    return_tensors="pt",
                ).to(self.config.device)
                logits = self._model(**encoded).logits  # shape (B, 2)
                # ADR-019 line 35 fp32 cast before softmax (applies to all
                # transformer scorers for numerical stability).
                probs = torch.softmax(logits.float(), dim=-1)
                inj_probs = probs[:, _INJECTION_LABEL_INDEX].detach().cpu().numpy()
                all_scores.append(inj_probs.astype(np.float64))
        return np.concatenate(all_scores)

    def score_dataframe(
        self,
        df: pd.DataFrame,
        *,
        text_column: str = "text",
        label_column: str = "label",
        source_column: str = "source",
        row_idx_column: str = "row_idx_in_source",
    ) -> pd.DataFrame:
        """Score a DataFrame with the Phase 1 data schema; return PredictionsRowModel rows.

        Output schema matches `src.eval.schemas.PredictionsRowModel`:
        - rung = "protectai-v1" or "protectai-v2"
        - fold = -1 (reference scorers have no LODO fold concept per ADR-018)
        - seed = -1 (deterministic; multi-seed irrelevant per ADR-007)
        - epoch = None (inference-only, no training)
        - contamination_state = "suspected_contamination" (ADR-018)
        """
        if df.empty:
            return _empty_predictions_df()

        texts = df[text_column].astype(str).tolist()
        scores = self.score_batch(texts)
        out = pd.DataFrame(
            {
                "rung": self.config.rung_id,
                "fold": -1,
                "seed": -1,
                "epoch": None,
                "row_idx_in_source": df[row_idx_column].astype(int).to_numpy(),
                "source": df[source_column].astype(str).to_numpy(),
                "text": df[text_column].astype(str).to_numpy(),
                "label": df[label_column].astype(int).to_numpy(),
                "predicted_proba_class1": scores,
                "contamination_state": "suspected_contamination",
            }
        )
        # Validate at least the first row against the pydantic contract — fail
        # loud if the schema drifted vs ADR-045 Q3.
        _validate_first_row(out)
        return out


def _empty_predictions_df() -> pd.DataFrame:
    """Empty DataFrame with PredictionsRowModel columns; used when input is empty."""
    return pd.DataFrame(
        columns=[
            "rung",
            "fold",
            "seed",
            "epoch",
            "row_idx_in_source",
            "source",
            "text",
            "label",
            "predicted_proba_class1",
            "contamination_state",
        ]
    )


def _validate_first_row(df: pd.DataFrame) -> None:
    """Validate the first row against PredictionsRowModel; raises ValidationError on drift."""
    if df.empty:
        return
    first = df.iloc[0].to_dict()
    # pandas may surface NaN for None on object columns; coerce for validator.
    if pd.isna(cast(Any, first.get("epoch"))):
        first["epoch"] = None
    PredictionsRowModel.model_validate(first)
