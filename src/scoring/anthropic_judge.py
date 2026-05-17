"""Anthropic claude-sonnet-4-6 LLM-judge reference scorer (per ADR-018).

Date-suffixed snapshot ID pinned at Phase 1 entry per ADR-018 line 58. Calls
`client.messages.create` at temperature=0 with the v1 shared prompt template.

Cost envelope per A-002 + ADR-018: ~$0.005 per call x ~5K rows = ~$25 worst
case; cost-cap-gated via `make eval-reference-scorers-paid` per ADR-045 Q4.

Note on snapshot naming
-----------------------
ADR-018 references "claude-sonnet-4-6 with date-suffixed snapshot ID pinned
at Phase 1 per Anthropic API docs". The concrete date-suffix is set at Phase
1 entry by reading the actual API-side snapshot. This module uses the model
constant `ANTHROPIC_JUDGE_MODEL` which can be patched at runtime by a future
ADR or hot-fix without restructuring the class.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, ClassVar, Final

from anthropic import Anthropic

from src.scoring.llm_judge_base import JUDGE_TEMPERATURE, LLMJudgeAPIError, LLMJudgeBase

# Locked snapshot ID per ADR-018. The literal "claude-sonnet-4-6" is the
# alias used in the spec; the API endpoint may accept a longer date-suffixed
# form (e.g., "claude-sonnet-4-6-20260501"); resolved at Phase 1 entry. If
# Anthropic deprecates this alias mid-Phase per A-014, a superseding ADR swaps
# the constant to the successor snapshot ID.
ANTHROPIC_JUDGE_MODEL: Final[str] = "claude-sonnet-4-6"

_MAX_OUTER_RETRIES: Final[int] = 2

# Max output tokens — JSON response is short (~50 tokens typical).
_MAX_TOKENS: Final[int] = 200


class AnthropicJudge(LLMJudgeBase):
    """Anthropic claude-sonnet-4-6 judge per ADR-018.

    Parameters
    ----------
    client : anthropic.Anthropic, optional
        Pre-constructed client (for test injection). If None, constructs
        from env-var `ANTHROPIC_API_KEY` per ADR-035 secrets discipline.
    cache_root : pathlib.Path, optional
        Override default cache root.
    """

    judge_name: ClassVar[str] = ANTHROPIC_JUDGE_MODEL

    def __init__(
        self,
        *,
        client: Anthropic | None = None,
        cache_root: Path | None = None,
    ) -> None:
        super().__init__(cache_root=cache_root)
        if client is None:
            if not os.environ.get("ANTHROPIC_API_KEY"):
                raise EnvironmentError(
                    "ANTHROPIC_API_KEY not set; pass `client=` for test injection or "
                    "set the env-var per ADR-035 secrets discipline."
                )
            client = Anthropic()
        self._client = client

    def _call_api(self, text: str) -> dict[str, Any]:
        """Call Anthropic messages API; return parsed JSON dict."""
        user_msg = self._user_template.format(text=text[:8000])
        last_err: Exception | None = None
        for _ in range(_MAX_OUTER_RETRIES + 1):
            try:
                resp = self._client.messages.create(
                    model=ANTHROPIC_JUDGE_MODEL,
                    max_tokens=_MAX_TOKENS,
                    temperature=JUDGE_TEMPERATURE,
                    system=self._system_prompt,
                    messages=[{"role": "user", "content": user_msg}],
                )
                content = _extract_text(resp)
                parsed: dict[str, Any] = json.loads(content)
                _validate_judge_response(parsed)
                return parsed
            except (json.JSONDecodeError, ValueError) as err:
                last_err = err
                continue
        raise LLMJudgeAPIError(
            f"{ANTHROPIC_JUDGE_MODEL} failed after {_MAX_OUTER_RETRIES + 1} attempts: {last_err}"
        )


def _extract_text(resp: Any) -> str:
    """Extract the assistant text from an Anthropic Messages API response.

    The Messages API returns `content` as a list of content blocks; we want
    the first text block's `.text` attribute.
    """
    content_blocks = resp.content
    if not content_blocks:
        raise LLMJudgeAPIError(f"{ANTHROPIC_JUDGE_MODEL} returned empty content")
    first = content_blocks[0]
    text = getattr(first, "text", None)
    if not text:
        raise LLMJudgeAPIError(f"{ANTHROPIC_JUDGE_MODEL} first content block has no .text")
    text_str: str = str(text).strip()
    # Anthropic sometimes wraps JSON in markdown ```json fences; strip them.
    if text_str.startswith("```"):
        first_newline = text_str.find("\n")
        last_fence = text_str.rfind("```")
        if first_newline > 0 and last_fence > first_newline:
            text_str = text_str[first_newline + 1 : last_fence].strip()
    return text_str


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
