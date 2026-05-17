"""OpenAI gpt-4o-2024-08-06 LLM-judge reference scorer (per ADR-018).

Stable snapshot per ADR-018 line 58 + OpenAI deprecation policy. Calls
`client.chat.completions.create` at temperature=0 with the v1 shared prompt
template. Response is `response_format={"type": "json_object"}` constrained
to JSON parsing.

Cost envelope per A-002 + ADR-018: ~$0.005 per call x ~5K rows = ~$25 worst
case; cost-cap-gated via `make eval-reference-scorers-paid` per ADR-045 Q4.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, ClassVar, Final

from openai import OpenAI

from src.scoring.llm_judge_base import JUDGE_TEMPERATURE, LLMJudgeAPIError, LLMJudgeBase

# Locked snapshot per ADR-018 line 58.
OPENAI_JUDGE_MODEL: Final[str] = "gpt-4o-2024-08-06"

# Vendor SDK retries handle transient failures; this is an outer-loop retry
# for cases the SDK marks as non-retryable (e.g., bad JSON parse).
_MAX_OUTER_RETRIES: Final[int] = 2


class OpenAIJudge(LLMJudgeBase):
    """OpenAI gpt-4o judge per ADR-018.

    Parameters
    ----------
    client : openai.OpenAI, optional
        Pre-constructed client (for test injection). If None, constructs
        from env-var `OPENAI_API_KEY` per ADR-035 secrets discipline.
    cache_root : pathlib.Path, optional
        Override default cache root at `evals/audit/llm_judge_cache/`.
    """

    judge_name: ClassVar[str] = OPENAI_JUDGE_MODEL

    def __init__(
        self,
        *,
        client: OpenAI | None = None,
        cache_root: Path | None = None,
    ) -> None:
        super().__init__(cache_root=cache_root)
        if client is None:
            if not os.environ.get("OPENAI_API_KEY"):
                raise EnvironmentError(
                    "OPENAI_API_KEY not set; pass `client=` for test injection or "
                    "set the env-var per ADR-035 secrets discipline."
                )
            client = OpenAI()
        self._client = client

    def _call_api(self, text: str) -> dict[str, Any]:
        """Call OpenAI chat.completions API; return parsed JSON dict."""
        user_msg = self._user_template.format(text=text[:8000])  # head-truncate to bound context
        last_err: Exception | None = None
        for _ in range(_MAX_OUTER_RETRIES + 1):
            try:
                resp = self._client.chat.completions.create(
                    model=OPENAI_JUDGE_MODEL,
                    messages=[
                        {"role": "system", "content": self._system_prompt},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=JUDGE_TEMPERATURE,
                    response_format={"type": "json_object"},
                )
                content = resp.choices[0].message.content
                if content is None:
                    raise LLMJudgeAPIError(f"{OPENAI_JUDGE_MODEL} returned None content")
                parsed: dict[str, Any] = json.loads(content)
                _validate_judge_response(parsed)
                return parsed
            except (json.JSONDecodeError, ValueError) as err:
                last_err = err
                continue
        raise LLMJudgeAPIError(
            f"{OPENAI_JUDGE_MODEL} failed after {_MAX_OUTER_RETRIES + 1} attempts: {last_err}"
        )


def _validate_judge_response(parsed: dict[str, Any]) -> None:
    """Validate parsed judge JSON has the required fields per the v1 prompt template."""
    if "is_injection" not in parsed:
        raise ValueError(f"judge response missing 'is_injection' field: {parsed!r}")
    if "confidence" not in parsed:
        raise ValueError(f"judge response missing 'confidence' field: {parsed!r}")
    if not isinstance(parsed["is_injection"], bool):
        raise ValueError(f"is_injection must be bool, got {type(parsed['is_injection']).__name__}")
    if not isinstance(parsed["confidence"], (int, float)):
        raise ValueError(f"confidence must be number, got {type(parsed['confidence']).__name__}")
