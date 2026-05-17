"""Abstract base for LLM-judge reference scorers (per ADR-018 + ADR-045 Q4).

Tier B reference scorers per ADR-045 Q4 — paid APIs; cost-cap-gated; not
auto-runnable in CI. Concrete subclasses live in `openai_judge.py` (gpt-4o-
2024-08-06) and `anthropic_judge.py` (claude-sonnet-4-6).

Per ADR-018 line 64-69 the call framework is fixed across judges — one call
per eval row at temperature=0, single shared prompt template at
`src/scoring/prompts/prompt_template_v1.md`. Only the API endpoint differs;
the prompt holds constant so the trained-rung-vs-LLM-judge comparison is not
confounded by prompt-engineering deltas.

Cache infrastructure
--------------------
Per A-007 (LLM-judge temperature=0 non-determinism) plus A-014 (mid-Phase
deprecation), every API response is cached at
`evals/audit/llm_judge_cache/<judge>__<text_sha256_first_16>.json` before
the score is returned. Subsequent calls with the same text hit the cache.
The cache survives mid-Phase deprecation of source snapshots — cached
scores remain valid for reporting even if the upstream model is removed.

Cache file schema (per A-007 line 27):
- judge_name : str  — e.g. "gpt-4o-2024-08-06"
- text_sha256 : str  — full 64-char hex digest
- timestamp : str  — ISO 8601 UTC
- temperature : float  — always 0.0
- prompt_template_version : str  — "v1" currently
- response_raw : str  — verbatim JSON string from the model
- predicted_label : int  — 0 or 1 derived from response.is_injection
- predicted_proba_class1 : float  — derived per the prompt template's score derivation rule
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar, Final

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from src.eval.schemas import ContaminationState, PredictionsRowModel

# Locked prompt template version per ADR-018.
PROMPT_TEMPLATE_VERSION: Final[str] = "v1"

# Cache root per A-007 + A-014. Always under repo's evals/audit/ subdirectory.
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent.parent
DEFAULT_CACHE_ROOT: Final[Path] = _REPO_ROOT / "evals" / "audit" / "llm_judge_cache"

# Locked temperature per ADR-018 line 65 (deterministic; multi-seed irrelevant).
JUDGE_TEMPERATURE: Final[float] = 0.0


class LLMJudgeAPIError(RuntimeError):
    """Raised when an LLM judge API call fails irrecoverably (after retries)."""


def _text_hash(text: str) -> str:
    """Return SHA-256 hex digest of the text (used for cache key + audit)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_prompt_template() -> tuple[str, str]:
    """Parse `prompts/prompt_template_v1.md` for the system + user blocks.

    Returns
    -------
    (system, user_template) : tuple[str, str]
        The system message (literal) and the user message template containing
        the `{text}` placeholder. Both stripped of leading/trailing whitespace.
    """
    template_path = (
        Path(__file__).resolve().parent
        / "prompts"
        / f"prompt_template_{PROMPT_TEMPLATE_VERSION}.md"
    )
    if not template_path.exists():
        raise FileNotFoundError(f"prompt template missing at {template_path}")

    content = template_path.read_text(encoding="utf-8")
    # Parse markdown: between "## System message" + next "##" header is system;
    # between "## User message" + next "##" is user.
    system_block = _extract_fenced_block(content, header="## System message")
    user_block = _extract_fenced_block(content, header="## User message")
    return system_block, user_block


def _extract_fenced_block(markdown: str, *, header: str) -> str:
    """Extract the first fenced code block following a ## header in markdown.

    Parameters
    ----------
    markdown : str
        Full markdown source.
    header : str
        Header to search for (e.g., "## System message").

    Returns
    -------
    str
        Code-block body with surrounding whitespace stripped. Raises if
        the header or its code fence cannot be located.
    """
    header_idx = markdown.find(header)
    if header_idx < 0:
        raise ValueError(f"prompt template missing section: {header!r}")
    fence_start = markdown.find("```", header_idx)
    if fence_start < 0:
        raise ValueError(f"prompt template section {header!r} missing opening ``` fence")
    # Skip the optional language hint on the fence line.
    fence_body_start = markdown.find("\n", fence_start) + 1
    fence_end = markdown.find("```", fence_body_start)
    if fence_end < 0:
        raise ValueError(f"prompt template section {header!r} missing closing ``` fence")
    return markdown[fence_body_start:fence_end].strip()


class LLMJudgeBase(ABC):
    """Abstract base for OpenAI + Anthropic LLM judges per ADR-018.

    Concrete subclasses must set `judge_name` (e.g., "gpt-4o-2024-08-06")
    and implement `_call_api(text)` returning the parsed JSON dict
    `{"is_injection": bool, "confidence": float}` per the v1 prompt template.

    Instances are stateless apart from the cache root + the prompt template
    (loaded once at __init__ from the markdown file).
    """

    judge_name: ClassVar[str] = ""  # subclass-specific
    contamination_state: ClassVar[ContaminationState] = "vendor_black_box"

    def __init__(self, *, cache_root: Path | None = None) -> None:
        if not self.judge_name:
            raise ValueError(f"{type(self).__name__} must set judge_name class attribute")
        self.cache_root: Path = cache_root if cache_root is not None else DEFAULT_CACHE_ROOT
        self._system_prompt, self._user_template = _load_prompt_template()

    # ------------------------------------------------------------------ #
    # Abstract API surface — concrete subclasses implement.
    # ------------------------------------------------------------------ #

    @abstractmethod
    def _call_api(self, text: str) -> dict[str, Any]:
        """Call the vendor API at temperature=0; return parsed JSON dict.

        Parameters
        ----------
        text : str
            Eval row text (caller's responsibility to truncate if needed).

        Returns
        -------
        dict
            Parsed response with keys `is_injection: bool` and
            `confidence: float`. Raise `LLMJudgeAPIError` on irrecoverable
            failure after vendor SDK retries.
        """

    # ------------------------------------------------------------------ #
    # Concrete shared infrastructure.
    # ------------------------------------------------------------------ #

    def _cache_path(self, text_hash: str) -> Path:
        """Cache file path for one (judge, text_hash) — first 16 hex chars to keep names short."""
        return self.cache_root / f"{self.judge_name}__{text_hash[:16]}.json"

    def _derive_score(self, response: dict[str, Any]) -> tuple[int, float]:
        """Derive `predicted_label` + `predicted_proba_class1` from a parsed response.

        Score derivation rule per `prompt_template_v1.md`:
        - `predicted_label = 1 if response['is_injection'] else 0`
        - `predicted_proba_class1 = response['confidence']` when is_injection=True
        - `predicted_proba_class1 = 1 - response['confidence']` when is_injection=False
        """
        is_inj = bool(response.get("is_injection", False))
        conf = float(response.get("confidence", 0.5))
        # Clamp to [0, 1] in case the judge returns slightly out-of-range numbers.
        conf = max(0.0, min(1.0, conf))
        proba = conf if is_inj else 1.0 - conf
        label = 1 if is_inj else 0
        return label, proba

    def score(self, text: str, *, use_cache: bool = True) -> float:
        """Score one text; cache-or-call. Returns `predicted_proba_class1` in [0, 1].

        Parameters
        ----------
        text : str
            Eval row text.
        use_cache : bool
            If True (default), check cache before calling API + persist on
            cache miss. If False, always call API + never persist (used by
            smoke tests where caching would pollute the repo).

        Returns
        -------
        float
            Predicted probability that the text is a prompt-injection attack
            (class 1), in [0, 1].
        """
        text_hash = _text_hash(text)
        cache_path = self._cache_path(text_hash)

        if use_cache and cache_path.exists():
            with cache_path.open("r", encoding="utf-8") as fh:
                cached = json.load(fh)
            # Cache-hit returns the persisted proba directly (no re-derivation).
            return float(cached["predicted_proba_class1"])

        response = self._call_api(text)
        label, proba = self._derive_score(response)

        if use_cache:
            self.cache_root.mkdir(parents=True, exist_ok=True)
            entry = {
                "judge_name": self.judge_name,
                "text_sha256": text_hash,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "temperature": JUDGE_TEMPERATURE,
                "prompt_template_version": PROMPT_TEMPLATE_VERSION,
                "response_raw": json.dumps(response),
                "predicted_label": label,
                "predicted_proba_class1": proba,
            }
            with cache_path.open("w", encoding="utf-8") as fh:
                json.dump(entry, fh, indent=2)

        return proba

    def score_batch(self, texts: list[str], *, use_cache: bool = True) -> NDArray[np.float64]:
        """Score a list of texts (sequential — APIs are per-call, no native batching)."""
        if not texts:
            return np.zeros(0, dtype=np.float64)
        return np.array(
            [self.score(text=t, use_cache=use_cache) for t in texts],
            dtype=np.float64,
        )

    def score_dataframe(
        self,
        df: pd.DataFrame,
        *,
        text_column: str = "text",
        label_column: str = "label",
        source_column: str = "source",
        row_idx_column: str = "row_idx_in_source",
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """Score a DataFrame with the Phase 1 data schema; return PredictionsRowModel rows."""
        if df.empty:
            return _empty_predictions_df()
        texts = df[text_column].astype(str).tolist()
        scores = self.score_batch(texts, use_cache=use_cache)
        out = pd.DataFrame(
            {
                "rung": self.judge_name,
                "fold": -1,
                "seed": -1,
                "epoch": None,
                "row_idx_in_source": df[row_idx_column].astype(int).to_numpy(),
                "source": df[source_column].astype(str).to_numpy(),
                "text": df[text_column].astype(str).to_numpy(),
                "label": df[label_column].astype(int).to_numpy(),
                "predicted_proba_class1": scores,
                "contamination_state": self.contamination_state,
            }
        )
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
    """Validate the first row against PredictionsRowModel; raises on drift."""
    if df.empty:
        return
    first = df.iloc[0].to_dict()
    if pd.isna(first.get("epoch")):
        first["epoch"] = None
    PredictionsRowModel.model_validate(first)
