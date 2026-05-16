"""Smoke tests for src/data/loaders.py — verify dispatch + 3 small HF sources.

Per ADR-027, smoke tests run on laptop with no GPU; network access required
for HF dataset fetch. These tests do NOT cover the heavy sources (lmsys-chat-1m
~1.5GB, ultrachat ~1GB) or git_repo sources (BIPIA, InjecAgent, XSTest) —
those are exercised by `make data-fetch` end-to-end in Phase 1 Commit 6.

The 3 sources covered here (deepset_prompt_injections, lakera_gandalf,
notinject) are each <500KB and resolve in seconds — safe for smoke runs.

Mark: `pytest -m smoke tests/smoke/test_loaders_smoke.py`.
"""

from __future__ import annotations

import pytest

from src.data.loaders import OUTPUT_COLUMNS, SourceNotFoundError, load_source


@pytest.mark.smoke
@pytest.mark.network
def test_load_source_deepset_prompt_injections() -> None:
    """deepset/prompt-injections loads, filters to label==1, matches output schema."""
    df = load_source("deepset_prompt_injections")
    assert list(df.columns) == list(OUTPUT_COLUMNS)
    assert len(df) > 0, "deepset returned 0 rows after positive filter"
    assert (df["label"] == 1).all(), "deepset normalizer should yield label==1 only"
    assert (df["source"] == "deepset_prompt_injections").all()
    assert df["text"].str.len().min() > 0
    # Per dossier estimate ~500-650; actual at pinned SHA may diverge — that's
    # an A-005 audit signal handled at `evals/data_audit.json` time, not here.


@pytest.mark.smoke
@pytest.mark.network
def test_load_source_lakera_gandalf() -> None:
    """Lakera/gandalf_ignore_instructions loads, all label==1, matches schema."""
    df = load_source("lakera_gandalf_ignore_instructions")
    assert list(df.columns) == list(OUTPUT_COLUMNS)
    assert len(df) > 0
    assert (df["label"] == 1).all()
    assert (df["source"] == "lakera_gandalf_ignore_instructions").all()


@pytest.mark.smoke
@pytest.mark.network
def test_load_source_notinject() -> None:
    """leolee99/NotInject loads, all label==0 (over-defense benigns), matches schema."""
    df = load_source("notinject")
    assert list(df.columns) == list(OUTPUT_COLUMNS)
    assert len(df) > 0
    assert (df["label"] == 0).all(), "NotInject is benign-by-construction; expected label==0"
    assert (df["source"] == "notinject").all()


@pytest.mark.unit
def test_load_source_unknown_raises() -> None:
    """load_source rejects names not in the locked slate."""
    with pytest.raises(SourceNotFoundError) as excinfo:
        load_source("not_a_real_source")
    assert "not_a_real_source" in str(excinfo.value)
