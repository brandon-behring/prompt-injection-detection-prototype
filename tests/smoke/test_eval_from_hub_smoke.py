"""Smoke tests for ``scripts/eval_from_hub.py`` per ADR-051 §Block A close.

Tests the T0 score-match wiring landed at v1.0.9 (ADR-058 narrow supersession
of ADR-051 Block A):

- ``--dry-run`` mode: subprocess invocation, no HF Hub download, exit 0.
- Score-match logic: per-row tolerance check via direct import (Q6 lock —
  mocked-only / CI-hermetic; no real ``snapshot_download``).
- Reference predictions parquet loader: validates schema lookup path.
- Published-rungs validator: validates ``evals/results.json`` lookup.

Real HF Hub fetch + CPU inference is NOT exercised in smoke tests (would
require network + ~500MB+ model download + ~30s CPU inference per slice).
That path is exercised by ``make eval-from-hub RUNG=frozen-probe`` for
the reviewer-facing T0 contract.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture(scope="module")
def eval_from_hub_module() -> Any:
    """Import ``scripts.eval_from_hub`` for in-process unit testing."""
    sys.path.insert(0, str(_REPO_ROOT))
    return importlib.import_module("scripts.eval_from_hub")


def test_eval_from_hub_dry_run_smoke() -> None:
    """``--dry-run --rung frozen-probe`` should exit 0 + print repo_id."""
    result = subprocess.run(
        [
            sys.executable,
            str(_REPO_ROOT / "scripts" / "eval_from_hub.py"),
            "--rung",
            "frozen-probe",
            "--dry-run",
        ],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "BBehring/prompt-injection-frozen-probe" in result.stdout
    assert "--dry-run" in result.stdout


def test_eval_from_hub_dry_run_lora() -> None:
    """``--dry-run --rung lora`` should exit 0 + print the lora repo_id."""
    result = subprocess.run(
        [
            sys.executable,
            str(_REPO_ROOT / "scripts" / "eval_from_hub.py"),
            "--rung",
            "lora",
            "--dry-run",
        ],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "BBehring/prompt-injection-lora" in result.stdout


def test_score_match_summary_within_tolerance(eval_from_hub_module: Any) -> None:
    """Per-row deltas all below 1e-4 → passed=True, n_exceed=0."""
    rng = np.random.default_rng(seed=42)
    reference = rng.uniform(0.1, 0.9, size=100).astype(np.float64)
    # Inject deltas all below tolerance (max 5e-5).
    deltas = rng.uniform(-5e-5, 5e-5, size=100).astype(np.float64)
    new_probs = reference + deltas

    passed, stats = eval_from_hub_module._score_match_summary(
        new_probs=new_probs,
        reference_probs=reference,
        tolerance=1e-4,
    )

    assert passed is True
    assert stats["n_exceed"] == 0
    assert stats["n_total"] == 100
    assert stats["max_abs_delta"] < 1e-4


def test_score_match_summary_exceeds_tolerance(eval_from_hub_module: Any) -> None:
    """Single row above 1e-4 → passed=False, n_exceed=1; strict-mode exit 1 contract."""
    reference = np.full(50, 0.5, dtype=np.float64)
    new_probs = reference.copy()
    # Inject one row well above tolerance.
    new_probs[17] = 0.5 + 1e-3  # delta = 1e-3, exceeds 1e-4 tolerance.

    passed, stats = eval_from_hub_module._score_match_summary(
        new_probs=new_probs,
        reference_probs=reference,
        tolerance=1e-4,
    )

    assert passed is False
    assert stats["n_exceed"] == 1
    assert stats["n_total"] == 50
    assert stats["max_abs_delta"] == pytest.approx(1e-3, abs=1e-9)


def test_score_match_summary_length_mismatch_raises(eval_from_hub_module: Any) -> None:
    """Length mismatch should raise ValueError per no-silent-failures discipline."""
    new_probs = np.zeros(10)
    reference = np.zeros(15)
    with pytest.raises(ValueError, match="Length mismatch"):
        eval_from_hub_module._score_match_summary(
            new_probs=new_probs,
            reference_probs=reference,
            tolerance=1e-4,
        )


def test_resolve_published_rungs(eval_from_hub_module: Any) -> None:
    """``evals/results.json`` must list frozen-probe + lora as published per ADR-032."""
    publishable = eval_from_hub_module._resolve_published_rungs()
    assert "frozen-probe" in publishable
    assert "lora" in publishable
    # tfidf-lr + full-ft NOT published per ADR-050.
    assert "full-ft" not in publishable
    assert "tfidf-lr" not in publishable


def test_load_reference_predictions_frozen_probe_bipia(eval_from_hub_module: Any) -> None:
    """Reference parquet at evals/predictions/frozen_probe__fold0__seed42__bipia.parquet must load."""
    df = eval_from_hub_module._load_reference_predictions(
        rung="frozen-probe",
        eval_slice="bipia",
    )
    assert len(df) > 0
    # PredictionsRowModel-required columns per src/eval/schemas.py.
    for col in ("rung", "fold", "seed", "source", "text", "label", "predicted_proba_class1"):
        assert col in df.columns, f"missing column: {col}"
    # Per-row scores are valid probabilities.
    proba = df["predicted_proba_class1"].to_numpy()
    assert (proba >= 0.0).all()
    assert (proba <= 1.0).all()


def test_load_reference_predictions_missing_raises(eval_from_hub_module: Any) -> None:
    """Missing reference parquet → FileNotFoundError with diagnostic per ADR-051 contract."""
    with pytest.raises(FileNotFoundError, match="Reference predictions parquet missing"):
        eval_from_hub_module._load_reference_predictions(
            rung="frozen-probe",
            eval_slice="nonexistent_slice_xyz",
        )


def test_rung_to_underscore_translation(eval_from_hub_module: Any) -> None:
    """Kebab→underscore translation for HF Hub ↔ file-system naming."""
    assert eval_from_hub_module._rung_to_underscore("frozen-probe") == "frozen_probe"
    assert eval_from_hub_module._rung_to_underscore("lora") == "lora"
    assert eval_from_hub_module._rung_to_underscore("tfidf-lr") == "tfidf_lr"
    assert eval_from_hub_module._rung_to_underscore("full-ft") == "full_ft"
