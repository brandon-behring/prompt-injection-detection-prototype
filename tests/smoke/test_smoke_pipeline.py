"""End-to-end smoke pipeline test (Phase 2 Commit 6 per ADR-027 + ADR-044 Q7).

Validates that ``scripts/train_classical_floor.py`` runs end-to-end against
the committed fixture parquets under ``tests/fixtures/processed/`` with the
``configs/profiles/classical_fixtures.yaml`` smoke profile, producing a valid
predictions parquet under ``tests/fixtures/predictions/``.

Closes the ADR-027 line 75 deferred fixture-pipeline wiring at Phase 2 level
(the Phase 3 extension to wire ``scripts/run_metrics_battery.py`` will come
later; this Commit 6 exercises the classical-floor trainer in the same
"fixture-data full pipeline pass" mode that ADR-027 specifies).

The transformer trainer is NOT exercised end-to-end here — running ModernBERT-
base on laptop CPU even with tiny data would take 10+ minutes, exceeding the
ADR-027 sub-10-min budget. Transformer-trainer structural integrity is covered
by ``tests/smoke/test_train_modernbert_smoke.py`` (10 mock-backed tests).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.mark.smoke
def test_fixtures_exist() -> None:
    """Committed fixture parquets exist + carry the expected schema."""
    fixtures_root = _REPO_ROOT / "tests" / "fixtures" / "processed" / "fold-0" / "seed-42"
    for split in ("train", "val", "test"):
        path = fixtures_root / f"{split}.parquet"
        assert path.exists(), f"missing fixture {path}"
        df = pd.read_parquet(path)
        assert set(df.columns) == {
            "text",
            "label",
            "source",
            "row_idx_in_source",
        }, f"{path} unexpected schema: {df.columns.tolist()}"
        assert len(df) > 0


@pytest.mark.smoke
def test_classical_floor_smoke_pipeline_end_to_end(tmp_path: Path) -> None:
    """make-smoke-equivalent: classical-floor trainer runs end-to-end on fixtures.

    Invokes ``scripts/train_classical_floor.py`` as a subprocess (matching
    how ``make smoke`` will invoke it) with the fixtures config + fixtures
    data; verifies the predictions parquet lands at the expected path with
    the expected schema. Runs in under 5 seconds on a laptop CPU.
    """
    predictions_root = tmp_path / "predictions"
    cmd = [
        sys.executable,
        str(_REPO_ROOT / "scripts" / "train_classical_floor.py"),
        "--config",
        str(_REPO_ROOT / "configs" / "profiles" / "classical_fixtures.yaml"),
        "--processed-root",
        str(_REPO_ROOT / "tests" / "fixtures" / "processed"),
        "--predictions-root",
        str(predictions_root),
        "--fold-only",
        "0",
        "--seed-only",
        "42",
    ]
    result = subprocess.run(  # noqa: S603 — controlled args; no shell
        cmd,
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert (
        result.returncode == 0
    ), f"train_classical_floor.py failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    out_path = predictions_root / "tfidf-lr__fold0__seed42.parquet"
    assert out_path.exists(), f"predictions parquet missing at {out_path}"

    preds = pd.read_parquet(out_path)
    assert len(preds) > 0
    expected_cols = {
        "rung",
        "fold",
        "seed",
        "row_idx_in_source",
        "source",
        "text",
        "label",
        "predicted_proba_class1",
    }
    assert expected_cols <= set(
        preds.columns
    ), f"predictions schema missing fields: {expected_cols - set(preds.columns)}"
    assert (preds["rung"] == "tfidf-lr").all()
    assert (preds["fold"] == 0).all()
    assert (preds["seed"] == 42).all()
    assert preds["predicted_proba_class1"].between(0, 1).all()


@pytest.mark.smoke
def test_generate_fixtures_is_idempotent(tmp_path: Path) -> None:
    """generate_fixtures.py is deterministic — re-running yields identical parquets.

    Uses --processed-root not as a flag (the script lacks one) but by checking
    that re-running the script over the committed fixtures produces the same
    byte content (read-after-write check).
    """
    import hashlib

    fixtures_root = _REPO_ROOT / "tests" / "fixtures" / "processed" / "fold-0" / "seed-42"
    if not (fixtures_root / "train.parquet").exists():
        pytest.skip("fixtures not generated yet; run scripts/generate_fixtures.py first")

    before = {
        split: hashlib.sha256((fixtures_root / f"{split}.parquet").read_bytes()).hexdigest()
        for split in ("train", "val", "test")
    }

    # Re-run the generator.
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(_REPO_ROOT / "scripts" / "generate_fixtures.py")],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"generate_fixtures.py failed: {result.stderr}"

    after = {
        split: hashlib.sha256((fixtures_root / f"{split}.parquet").read_bytes()).hexdigest()
        for split in ("train", "val", "test")
    }
    assert before == after, "generate_fixtures.py is not byte-deterministic (seed drift?)"
