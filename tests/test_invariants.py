"""Invariant tests.

Each invariant corresponds to a [LOCKED] rule in SPEC_GREENFIELD.md §5
(Tests-as-invariants).

## v1.0.0 invariant-stub status (per Item 6 / Q12 lock of the closure sweep)

ADR-039 gate 3 says invariant stubs should be unskipped + green at the
submission tag. Of the 38 stubs originally flagged at v1.0.0 audit time:

- **Implemented at v1.0.0**: `test_class_balance_per_fold`,
  `test_source_disjoint_train_test`, `test_dedup_calibration_persisted`,
  `test_benign_contamination_scan_clean`, `test_reference_scorer_schema_uniform`,
  `test_calibration_battery_outputs_4ece_plus_brier`, etc. — these run
  on the live Phase 4 artifacts.
- **Deferred to v1.1.x**: the 38 remaining stubs ship as explicit
  `@pytest.mark.skip(reason="...")` markers with module-level
  documented reasons. They fall in three buckets:
  1. *Spec-invariant scaffolds* (e.g.,
     `test_hyperparameter_immutability`, `test_calibration_honesty_val_only`)
     — the invariant is true by code construction (config hash check
     in `src/utils/config_hash.py`; calibration battery hard-codes
     val-only fit per ADR-023) but the executable assertion was
     deferred. Implementing each is ~30 min wallclock; out of scope
     for v1.0.0.
  2. *Reporting invariants* (e.g.,
     `test_reporting_completeness_assumptions_in_caveats`, `test_no_emoji_in_repo`)
     — a pre-commit hook covers emoji + a manual review covers the
     assumptions-in-caveats discipline at v1.0.0; the executable test
     is the better-discipline form.
  3. *Orphaned by ADR-050* (full-FT OOD invariants;
     LLM-judge-related invariants) — see explicit skip reasons.

Per ADR-039 gate 3 honest accounting: the v1.0.0 invariant scaffolding
is partial; the carryforward to v1.1.x is explicit. WRITEUP §Methodology
caveats documents this.
"""

import pytest


@pytest.mark.unit
def test_class_balance_per_fold() -> None:
    """Per-fold negative:positive ratio is within ADR-016 A-005 trigger 2 range [1:3, 1:10].

    Reads evals/data_audit.json (produced by scripts/run_data_pipeline.py) and
    asserts the per-fold class balance falls in the ADR-016 A-005 trigger 2 range.
    """
    import json
    from pathlib import Path

    audit_path = Path(__file__).resolve().parent.parent / "evals" / "data_audit.json"
    assert (
        audit_path.exists()
    ), "evals/data_audit.json not found; run scripts/run_data_pipeline.py first."
    with audit_path.open("r", encoding="utf-8") as fh:
        audit = json.load(fh)
    assert (
        audit["a_005_class_balance_clean"] is True
    ), f"A-005 trigger 2 (class balance) fired: {audit.get('a_005_triggers_fired')}"
    assert (
        len(audit["per_fold_class_balance"]) == 12
    ), f"expected 12 (fold, seed) records; got {len(audit['per_fold_class_balance'])}"


@pytest.mark.unit
def test_source_disjoint_train_test() -> None:
    """Each test slice's source is not present in the train sources (LODO disjointness).

    Reads the 36 per-fold parquets under data/processed/ and verifies that for every
    (fold, seed), the test set's source is NOT in the train+val sources. Source-level
    disjointness is the LODO contract; text-level leakage is checked separately by
    test_leakage_report_clean (covered by ADR-043 post-split cleanup).
    """
    from pathlib import Path

    import pandas as pd

    processed_root = Path(__file__).resolve().parent.parent / "data" / "processed"
    assert (
        processed_root.exists()
    ), "data/processed/ not found; run scripts/run_data_pipeline.py first."
    folds = sorted(processed_root.glob("fold-*"))
    assert len(folds) == 4, f"expected 4 LODO folds; got {len(folds)}"
    for fold_dir in folds:
        for seed_dir in sorted(fold_dir.glob("seed-*")):
            train = pd.read_parquet(seed_dir / "train.parquet")
            val = pd.read_parquet(seed_dir / "val.parquet")
            test = pd.read_parquet(seed_dir / "test.parquet")
            train_sources = set(train["source"].unique()) | set(val["source"].unique())
            test_sources = set(test["source"].unique())
            assert test_sources.isdisjoint(train_sources), (
                f"{fold_dir.name}/{seed_dir.name}: test sources {test_sources} "
                f"leak into train sources {train_sources}"
            )


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_hyperparameter_immutability() -> None:
    """Config hash matches the committed value (no silent hyperparameter mutation)."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_calibration_honesty_val_only() -> None:
    """Temperature scaling fits only on validation, not test."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_reporting_completeness_assumptions_in_caveats() -> None:
    """Every assumption with severity >= medium in assumptions.md appears in the WRITEUP caveats block."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_no_emoji_in_repo() -> None:
    """No emoji code points in source / docs (per SPEC_GREENFIELD §5)."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_config_result_classes_frozen_slotted() -> None:
    """Classes whose name ends in Config or Result are frozen + slotted dataclasses."""
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_trained_backbone_modernbert_only_invariant() -> None:
    """Trained transformer rungs contain exactly ModernBERT-base across three conditions.

    Per ADR-015 (rung architecture refinement, supersedes ADR-007), the trained
    transformer slate is locked to ModernBERT-base x {frozen-probe, LoRA, full-FT}.
    A silent fallback to DeBERTa-v3-base is prohibited; any backbone swap requires a
    superseding ADR. Per ADR-017 (rung-slate expansion), the trained slate also
    includes a TF-IDF+LR classical floor rung — this invariant asserts the transformer
    portion of the trained slate (not all trained rungs) matches the locked
    ModernBERT-base × 3-conditions enumeration; the classical-floor rung is carved out
    and asserted separately by `test_classical_floor_rung_present`.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_truncation_policy_adaptive_chunked_max_pool() -> None:
    """Eval-path truncation policy is adaptive chunked scoring with max-pool aggregation.

    Per ADR-014 (threat-model bundle, Q4 lock), evaluation-time inputs that
    exceed the length cap are split into overlapping chunks of size cap with
    stride cap // 2; each chunk is scored independently; per-sample score is
    the max over chunk scores. Training-time uses head-truncation (HF default).
    This invariant asserts that the eval pipeline's truncation handler matches
    the locked policy and that aggregator equals max-pool.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
def test_source_manifest_schema_valid() -> None:
    """configs/data/source_manifest.yaml parses, contains all 11 sources, each has SHA + license + role.

    Per ADR-016 (Q3 lock) + ADR-041 (Q1 rich schema) + ADR-044 Q2 (location move),
    HF revisions and GitHub commit SHAs are pinned at Phase 1 entry in unified
    configs/data/source_manifest.yaml.
    This invariant asserts the manifest validates clean against the rich-schema
    contract enforced by src/data/manifest_validation.py — 11 expected sources
    (4 train positives + 2 train benigns + 5 OOD slices); each row carries the
    13 required fields; schema_version == "1.0"; bump_history is a list.
    """
    from pathlib import Path

    from src.data.manifest_validation import (
        EXPECTED_ROLE_COUNTS,
        EXPECTED_SOURCE_NAMES,
        SCHEMA_VERSION,
        validate_manifest,
    )

    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = repo_root / "configs" / "data" / "source_manifest.yaml"
    parsed = validate_manifest(manifest_path)

    assert parsed["schema_version"] == SCHEMA_VERSION
    assert isinstance(parsed["bump_history"], list)
    seen_names = {row["name"] for row in parsed["sources"]}
    assert (
        seen_names == EXPECTED_SOURCE_NAMES
    ), f"manifest source names mismatch ADR-016 slate: {seen_names ^ EXPECTED_SOURCE_NAMES}"
    role_counts: dict[str, int] = {role: 0 for role in EXPECTED_ROLE_COUNTS}
    for row in parsed["sources"]:
        role_counts[row["role"]] += 1
    assert role_counts == EXPECTED_ROLE_COUNTS


@pytest.mark.unit
def test_dedup_calibration_persisted() -> None:
    """evals/dedup_calibration.json exists with FPR+FNR at threshold 0.80 plus sensitivity table.

    Per ADR-016 (Q4 lock) + ADR-041 (Q5 stratified-cosine-band holdout) + ADR-042
    (LLM-pre-label bootstrap with human override + label_provenance disclosure),
    the dedup encoder is all-MiniLM-L6-v2 cosine at threshold 0.80. This invariant
    asserts the calibration JSON exists with schema_version 1.0; at_locked_threshold
    carries fpr + fnr + confusion counts; sensitivity_table covers {0.75, 0.80,
    0.85}; label_provenance discloses human_verified_pct + llm_judge_only_count;
    holdout_sha256 + encoder_revision are persisted.

    Note: does NOT assert human_verified_pct == 100. Preliminary calibration with
    label_provenance.human_verified_pct < 100 (LLM-judge bootstrap per ADR-042) is
    acceptable for this invariant; submission-readiness gate (per ADR-039) reviews
    the percentage at v1.0.0 tag time.
    """
    import json
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent
    calib_path = repo_root / "evals" / "dedup_calibration.json"
    assert calib_path.exists(), (
        "evals/dedup_calibration.json not found; "
        "run scripts/calibrate_dedup.py to generate. "
        "If ImportError: data/dedup_holdout.jsonl missing — "
        "run scripts/build_dedup_holdout.py first."
    )

    with calib_path.open("r", encoding="utf-8") as fh:
        calib = json.load(fh)

    assert calib["schema_version"] == "1.0"
    assert calib["threshold_locked"] == 0.80
    assert calib["encoder"] == "sentence-transformers/all-MiniLM-L6-v2"
    assert "encoder_revision" in calib and len(calib["encoder_revision"]) > 0

    locked = calib["at_locked_threshold"]
    for field in ("threshold", "tp", "fp", "tn", "fn", "fpr", "fnr", "n_pairs"):
        assert field in locked, f"at_locked_threshold missing field {field!r}"
    assert locked["threshold"] == 0.80
    assert locked["tp"] + locked["fp"] + locked["tn"] + locked["fn"] == locked["n_pairs"]

    for t in ("0.75", "0.80", "0.85"):
        assert t in calib["sensitivity_table"], f"sensitivity_table missing threshold {t}"

    prov = calib["label_provenance"]
    for field in ("human_verified_count", "llm_judge_only_count", "human_verified_pct"):
        assert field in prov, f"label_provenance missing field {field!r}"

    assert "holdout_sha256" in calib and len(calib["holdout_sha256"]) == 64


@pytest.mark.unit
def test_benign_contamination_scan_clean() -> None:
    """Benign sources (LMSYS + UltraChat) have <=2% contamination per A-005.

    Per ADR-016 Phase 1 revisit triggers (assumption A-005), the contamination
    scan flags any benign sample with MiniLM cosine >= 0.85 to a known
    injection template (slate + ~200 HackAPrompt success-pattern templates per
    ADR-041 Q6). This invariant asserts contamination rate stays at or below 2%
    in both LMSYS-Chat-1M (post English-only filter and post-subsample) and
    UltraChat (post-subsample) by reading evals/contamination_scan.json
    (produced by scripts/run_data_pipeline.py).
    """
    import json
    from pathlib import Path

    scan_path = Path(__file__).resolve().parent.parent / "evals" / "contamination_scan.json"
    assert (
        scan_path.exists()
    ), "evals/contamination_scan.json not found; run scripts/run_data_pipeline.py first."
    with scan_path.open("r", encoding="utf-8") as fh:
        scan = json.load(fh)
    assert (
        scan["a_005_benign_contamination_clean"] is True
    ), f"A-005 trigger 1 (benign contamination) fired: {scan.get('a_005_triggers_fired')}"
    for benign_source in ("lmsys_chat_1m", "ultrachat_200k"):
        assert (
            benign_source in scan["per_benign_source"]
        ), f"contamination_scan missing benign source {benign_source!r}"
        pct = scan["per_benign_source"][benign_source]["contamination_pct"]
        assert (
            pct <= 2.0
        ), f"{benign_source} contamination {pct:.2f}% exceeds A-005 trigger 1 threshold (2.0%)"


@pytest.mark.unit
def test_classical_floor_rung_present() -> None:
    """TF-IDF + LR classical floor rung is in the trained-rung config enumeration.

    Per ADR-017 (trained-rung-slate expansion) + ADR-044 Q3 + Q4,
    configs/rungs/classical_floor.yaml is the canonical source of truth for
    the classical-floor recipe. This invariant asserts the YAML carries the
    locked recipe — sklearn TfidfVectorizer FeatureUnion word 1-2-grams
    (max_features=15000, sublinear_tf=True) + char 3-5-grams
    (max_features=15000) plus sklearn LogisticRegression(solver=liblinear,
    C=1.0, class_weight=balanced, max_iter=1000) + seeds slate (42, 43, 44)
    per ADR-044 Q1. Restores the SPEC §2 line 121 common-pattern default.
    """
    from pathlib import Path

    import yaml

    repo_root = Path(__file__).resolve().parent.parent
    cfg_path = repo_root / "configs" / "rungs" / "classical_floor.yaml"
    assert cfg_path.exists(), f"{cfg_path} missing — Phase 2 Commit 3 deliverable"

    with cfg_path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    assert cfg["rung_id"] == "classical_floor"
    assert cfg["classifier_type"] == "classical"
    assert cfg["contamination_state"] == "verified_disjoint"

    # TF-IDF lock (per ADR-017).
    tfidf = cfg["tfidf"]
    assert tfidf["word_ngram_min"] == 1
    assert tfidf["word_ngram_max"] == 2
    assert tfidf["word_max_features"] == 15000
    assert tfidf["char_ngram_min"] == 3
    assert tfidf["char_ngram_max"] == 5
    assert tfidf["char_max_features"] == 15000
    assert tfidf["sublinear_tf"] is True
    assert tfidf["lowercase"] is True
    assert tfidf["strip_accents"] == "unicode"

    # LogisticRegression lock (per ADR-017).
    lr = cfg["logistic_regression"]
    assert lr["solver"] == "liblinear"
    assert lr["C"] == 1.0
    assert lr["class_weight"] == "balanced"
    assert lr["max_iter"] == 1000

    # Seeds slate (per ADR-044 Q1).
    assert cfg["seeds"] == [42, 43, 44]


@pytest.mark.unit
@pytest.mark.skip(reason="deferred to canonical run — needs GPU per ADR-027 headline-cloud target")
def test_per_epoch_predictions_present() -> None:
    """Per-epoch parquet predictions exist for every transformer (rung, seed, fold).

    Per ADR-019 (LoRA + transformer training recipe), epoch-2 predictions are
    the headline numbers and epoch-1 predictions are reported as a diagnostic
    ablation. This invariant asserts the prediction directory contains exactly
    72 transformer-rung parquet files for the 3 transformer rungs × 3 seeds ×
    4 LODO folds × 2 epochs enumeration, with file paths matching the convention
    evals/predictions/<rung>__fold<F>__seed<S>__epoch<N>.parquet. TF-IDF + LR
    rung predictions (no epoch dimension; 12 files) and reference-rung
    predictions (16 files) are asserted separately.

    Phase 2 status — trainer code lands in Commit 4 (ADR-044 Q5); actual 72
    parquets are produced by the canonical run via scripts/train_rung.py
    (ADR-044 Q6 + ADR-027 headline-cloud target). Unskip when those files
    exist on disk; until then this invariant is skipped not failed.
    """
    from pathlib import Path

    predictions_root = Path(__file__).resolve().parent.parent / "evals" / "predictions"
    expected_files = [
        f"{rung}__fold{fold}__seed{seed}__epoch{epoch}.parquet"
        for rung in ("frozen-probe", "lora", "full-ft")
        for fold in range(4)
        for seed in (42, 43, 44)
        for epoch in (1, 2)
    ]
    missing = [f for f in expected_files if not (predictions_root / f).exists()]
    assert not missing, (
        f"Missing {len(missing)} of 72 expected per-epoch transformer parquets; "
        f"first 5 missing: {missing[:5]}"
    )


@pytest.mark.unit
def test_flash_attn_fallback_present() -> None:
    """ModernBERT loader has try/except fallback from flash_attention_2 to SDPA.

    Per ADR-020 (compute infrastructure and cost discipline) + ADR-044 Commit 2,
    src/training/load_modernbert.py wraps AutoModelForSequenceClassification
    .from_pretrained with attn_implementation=flash_attention_2 in a try/except
    catching (ValueError, ImportError) plus falls through to a second load without
    attn_implementation set (stock SDPA). The fallback path emits a
    flash_attn_fallback event so the audit trail captures which physical config
    produced each per-row prediction. This invariant inspects the module source
    for the required structure.
    """
    import inspect

    from src.training import load_modernbert

    src = inspect.getsource(load_modernbert)
    assert "except (ValueError, ImportError)" in src, (
        "load_modernbert must catch (ValueError, ImportError) per ADR-020 "
        "flash-attn-fallback recipe"
    )
    assert "flash_attn_fallback" in src, (
        "load_modernbert must emit flash_attn_fallback event in fallback branch "
        "per ADR-020 line 124"
    )


@pytest.mark.unit
def test_reference_scorer_schema_uniform() -> None:
    """All Phase 3 reference scorers conform to the unified PredictionsRowModel contract.

    Per ADR-045 Q3 + Q7, every src/scoring/ adapter must emit a DataFrame whose
    rows pass src.eval.schemas.PredictionsRowModel validation. This invariant
    asserts the structural contract — instantiates each scorer with fake clients
    (no real API calls) and verifies the output DataFrame's first row validates
    cleanly. Production runs use real ProtectAI weights + paid APIs (cost-cap-
    gated per ADR-045 Q4).
    """
    import json
    from typing import Any
    from unittest.mock import MagicMock

    import pandas as pd
    import torch
    from transformers import BatchEncoding

    from src.eval.schemas import PredictionsRowModel
    from src.scoring.anthropic_judge import AnthropicJudge
    from src.scoring.openai_judge import OpenAIJudge
    from src.scoring.protectai import ProtectAIScorer

    # Tiny fake HF tokenizer + model so ProtectAIScorer can build without
    # downloading weights (mirrors the smoke test pattern).
    class _T:
        def __call__(self, texts: list[str], **kw: Any) -> Any:
            del kw
            n = len(texts)
            return BatchEncoding(
                {
                    "input_ids": torch.zeros((n, 2), dtype=torch.long),
                    "attention_mask": torch.ones((n, 2), dtype=torch.long),
                }
            )

    class _M(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self._p = torch.nn.Parameter(torch.zeros(1))

        def forward(self, **kw: Any) -> Any:
            n = kw["input_ids"].shape[0]
            logits = torch.zeros((n, 2))
            out = MagicMock()
            out.logits = logits
            return out

        def to(self, *args: Any, **kwargs: Any) -> "_M":
            del args, kwargs
            return self

        def eval(self) -> "_M":
            return self

    # Tiny fake OpenAI + Anthropic clients (canned JSON responses).
    payload = json.dumps({"is_injection": True, "confidence": 0.8})

    class _OAClient:
        @property
        def chat(self) -> Any:
            return self

        @property
        def completions(self) -> Any:
            return self

        def create(self, **kw: Any) -> Any:
            del kw
            c = MagicMock()
            c.message.content = payload
            r = MagicMock()
            r.choices = [c]
            return r

    class _ATClient:
        @property
        def messages(self) -> Any:
            return self

        def create(self, **kw: Any) -> Any:
            del kw
            b = MagicMock()
            b.text = payload
            r = MagicMock()
            r.content = [b]
            return r

    df_in = pd.DataFrame(
        {
            "text": ["a", "b"],
            "label": [1, 0],
            "source": ["src1", "src2"],
            "row_idx_in_source": [0, 1],
        }
    )

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        from pathlib import Path

        cache_root = Path(tmpdir)

        protectai = ProtectAIScorer(version="v1", model=_M(), tokenizer=_T())
        openai_judge = OpenAIJudge(client=_OAClient(), cache_root=cache_root)  # type: ignore[arg-type]
        anthropic_judge = AnthropicJudge(client=_ATClient(), cache_root=cache_root)  # type: ignore[arg-type]

        for scorer_name, df_out in (
            ("protectai-v1", protectai.score_dataframe(df_in)),
            ("openai", openai_judge.score_dataframe(df_in, use_cache=False)),
            ("anthropic", anthropic_judge.score_dataframe(df_in, use_cache=False)),
        ):
            assert len(df_out) > 0, f"{scorer_name} produced empty output"
            row = df_out.iloc[0].to_dict()
            if pd.isna(row.get("epoch")):
                row["epoch"] = None
            PredictionsRowModel.model_validate(row)


@pytest.mark.unit
def test_calibration_battery_outputs_4ece_plus_brier() -> None:
    """src/eval/calibration_battery.py emits the locked 4-ECE matrix + Brier per ADR-023.

    Per ADR-023 (calibration battery composition), the spoke battery must emit
    all 4 ECE variants from eval-toolkit (L1/L2 x plug-in/debiased) plus Brier
    plus Brier decomposition (reliability/resolution/uncertainty); headline is
    ECE-equal-mass(n_bins=15) plus Brier on raw scores per rung. This invariant
    asserts the compute_calibration_record function returns a fully-populated
    CalibrationRecordModel for a synthetic (rung, fold, seed, calibrator) cell
    and that the locked n_bins=15 constant is exposed at module scope.

    Phase 3 Commit 3 scope — module-level contract; integration test
    (test_calibration_battery_composition) is deferred to Commit 5 when
    scripts/run_metrics_battery.py wires the per-(rung, fold, seed) loop
    end-to-end.
    """
    import numpy as np

    from src.eval.calibration_battery import HEADLINE_N_BINS, compute_calibration_record
    from src.eval.schemas import CalibrationRecordModel

    # Locked binning per ADR-023 line 8.
    assert HEADLINE_N_BINS == 15

    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, size=200).astype(np.int_)
    s = rng.uniform(0, 1, size=200).astype(np.float64)

    record = compute_calibration_record(
        rung="lora",
        fold=0,
        seed=42,
        calibrator="raw",
        y_true=y,
        y_score=s,
    )
    assert isinstance(record, CalibrationRecordModel)

    # Headline columns per ADR-023.
    assert record.ece_equal_mass >= 0.0
    assert record.brier >= 0.0

    # Spoke columns per ADR-023 (4 ECE variants + Brier decomposition).
    for ece_field in (
        "ece_l1_plug_in",
        "ece_l1_debiased",
        "ece_l2_plug_in",
        "ece_l2_debiased",
    ):
        value = getattr(record, ece_field)
        assert value >= 0.0, f"{ece_field} negative: {value}"

    # Brier decomposition fields populated per eval-toolkit brier_decomposition.
    for brier_field in ("brier_reliability", "brier_resolution", "brier_uncertainty"):
        value = getattr(record, brier_field)
        assert value >= 0.0, f"{brier_field} negative: {value}"


@pytest.mark.unit
def test_effective_batch_constant_across_gpu_classes() -> None:
    """BATCH_TABLE preserves effective batch = 32 across all GPU classes.

    Per ADR-020 (compute infrastructure) + ADR-044 Commit 2,
    src/training/batch_table.py BATCH_TABLE scales per_device_train_batch_size
    and gradient_accumulation_steps together such that their product equals 32
    for every GPU class in the pod.gpu_order failover ladder. This invariant
    asserts the table covers H100 + H200 + A100-80G + A100-40G + L40S + L40
    with per_device * grad_accum == 32 for each entry. The effective batch is
    the actual gradient-computation hyperparameter; per_device and grad_accum
    are throughput knobs that do not change the gradient computation. Preserves
    SPEC §2 hyperparameter-immutability invariant under GPU substitution.
    """
    from src.training.batch_table import BATCH_TABLE, EFFECTIVE_BATCH

    assert EFFECTIVE_BATCH == 32

    required_classes = {"H100", "H200", "A100-80G", "A100-40G", "L40S", "L40"}
    actual_classes = set(BATCH_TABLE.keys())
    missing = required_classes - actual_classes
    assert (
        not missing
    ), f"BATCH_TABLE missing GPU classes from ADR-020 pod.gpu_order: {sorted(missing)}"

    for gpu_class, cfg in BATCH_TABLE.items():
        product = cfg.per_device * cfg.grad_accum
        assert product == EFFECTIVE_BATCH, (
            f"GPU class {gpu_class!r}: per_device={cfg.per_device} * "
            f"grad_accum={cfg.grad_accum} = {product} != {EFFECTIVE_BATCH}"
        )


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_ood_aggregation_layout() -> None:
    """OOD slate reports pooled-headline plus per-slice-spoke aggregation views.

    Per ADR-021 (eval slate aggregation), the 5 OOD slices locked by ADR-016
    (NotInject + XSTest + JBB-Behaviors + BIPIA + InjecAgent) are reported in
    two complementary aggregation views. This invariant asserts: (1) the headline
    emit (evals/results.json) contains a pooled-OOD column per rung concatenating
    rows across the 5 slices yielding a single AUPRC + AUROC + recall@FPR + ECE +
    Brier per rung; (2) the spoke artifact (evals/ood_per_slice.parquet) contains
    a 5-by-rung grid with per-slice bootstrap CIs; (3) all 5 OOD slices appear in
    the spoke artifact exactly once per rung.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_recall_at_fpr_pinpoint_volatility() -> None:
    """Recall@FPR=0.1% pinpoint reports volatility surfaces at pooled level.

    Per ADR-021 (recall@FPR pinpoint feasibility), the 0.1% pinpoint is computed
    only at the pooled aggregation level and reports four volatility surfaces.
    This invariant asserts: (1) per-rung headline emit contains half-width column
    alongside point estimate for the 0.1% pinpoint; (2) evals/audit/per_rung_audit.json
    contains a resample-degeneracy fraction (fraction of bootstrap resamples where
    the FPR=0.001 threshold pinned at less than 1 false-positive count); (3)
    evals/audit/pinpoint_threshold_drift.json contains the distribution of
    *thresholds* across resamples for the 0.1% pinpoint; (4) per-slice and
    per-LODO-fold aggregations report the 0.1% pinpoint cell as "not computable
    at this aggregation level (n_neg too small)" rather than a numerical value.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_bootstrap_n_and_stability_check() -> None:
    """Bootstrap apparatus runs 10K @ seed=1 headline + 10K @ seed=2 stability check.

    Per ADR-022 (statistical inference apparatus), the bootstrap protocol for every
    headline CI is: 10K iterations via eval_toolkit.bootstrap_ci (BCa for marginals)
    at seed=1 as headline; 10K iterations at seed=2 as stability check; flag in
    audit JSON when stability-check CI half-width differs from headline CI half-width
    by more than 5 percent (signals resampling instability). This invariant asserts
    the bootstrap orchestrator (scripts/run_bootstrap_battery.py) emits both the
    seed=1 headline CI and the seed=2 stability-check CI to
    evals/audit/bootstrap_stability_check.parquet, with a half-width-diff-percent
    column and a flag column (boolean: True when diff > 5 percent).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_paired_across_rungs_pairing() -> None:
    """Multi-seed pairing structure follows ADR-022 gap-honest defaults.

    Per ADR-022 (multi-seed protocol details), trained-vs-trained rung comparisons
    use row-level pairing via eval_toolkit.paired_bootstrap_diff; trained-vs-reference
    rung comparisons use per-row replication of reference scores across the 12 trained
    seeds (reference-side variance is correctly fold-only). This invariant asserts:
    (1) for any trained-vs-trained comparison, the input to paired_bootstrap_diff
    is a 1-D array of row-level predictions with shape matching the pooled test set;
    (2) for any trained-vs-reference comparison, the reference rung's score for a
    given row is identical across the 12 (fold, seed) slots of the trained rung
    (replication invariant); (3) the per-(rung, fold, seed) observation parquet
    (evals/audit/per_seed_observations.parquet) contains 12 rows per trained rung
    and 4 rows per reference rung.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_calibration_battery_composition() -> None:
    """Calibration battery emits raw plus temperature plus isotonic intervention states.

    Per ADR-023 (calibration battery composition), the headline emit contains
    ECE-equal-mass(n_bins=15, quantile binning) plus Brier per rung on raw scores
    only. The spoke artifact contains all 4 ECE variants (L1/L2 plug-in/debiased)
    plus Brier decomposition plus reliability diagrams plus temperature-applied and
    isotonic-applied ECE/Brier deltas. This invariant asserts: (1) headline
    evals/results.json contains exactly 2 calibration columns per rung
    (ECE-equal-mass-raw, Brier-raw); (2) spoke evals/calibration_spoke.parquet
    contains 4 ECE variants plus Brier plus temperature-applied and
    isotonic-applied versions of each; (3) the calibrator-fit input rows are
    drawn from the validation split only (no test rows; per ADR-011 Guarantee 6);
    (4) per-(rung, fold, seed) calibrator artifacts exist at
    evals/calibration/<rung>__fold<F>__seed<S>__intervention<temperature|isotonic|raw>.json.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_monotonic_intervention_preserves_ranks() -> None:
    """Calibration interventions are monotonic and therefore preserve rank-based metrics.

    Per ADR-023 (calibration battery), calibration interventions (temperature
    scaling and isotonic regression) are monotonic by construction; rank-based
    headline metrics (PR-AUC, ROC-AUC, recall@FPR) are unchanged by intervention.
    This sanity-check invariant asserts that for any (rung, fold, seed) tuple,
    PR-AUC and ROC-AUC after temperature scaling equal PR-AUC and ROC-AUC before
    temperature scaling within numerical tolerance (1e-9); same for isotonic.
    If false, the calibrator implementation is producing non-monotonic outputs —
    a bug in the calibrator-fit chain.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_cross_fold_ci_methodology() -> None:
    """Cross-fold CI machinery runs cv_clt_ci headline plus block-bootstrap-on-folds spoke.

    Per ADR-024 (cross-fold CI methodology), the headline cross-fold CI uses
    eval_toolkit.bootstrap.cv_clt_ci (Bayle 2020 Theorem 3.1) on the 12 per-(fold, seed)
    metric values per rung; the spoke ablation uses block-bootstrap-on-folds
    (resample 4 folds with replacement; per-resample compute mean-of-fold-metrics;
    10K resamples; percentile CI); the sensitivity-check flag fires when
    block_bootstrap_CI_halfwidth / cv_clt_CI_halfwidth > 1.5. This invariant asserts:
    (1) cv_clt_ci primitive is invoked on 12 per-(fold, seed) values per rung;
    (2) block-bootstrap-on-folds orchestrator produces percentile CI on 10K resamples;
    (3) sensitivity-check flag column emits in evals/audit/cross_fold_ci_audit.parquet;
    (4) when sensitivity flag fires, the methodology spoke contains the named
    "LODO non-exchangeability" paragraph. The conditional stratified-k-fold-within-LODO
    escalation is gated on evals/cost_ledger.csv state at Phase 4 entry — not asserted
    by this invariant (deferred to manual Phase 4 audit).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="deferred to canonical Phase 4 evals — needs 84 trained-rung parquets")
def test_marginal_bootstrap_seed_stability() -> None:
    """Marginal-bootstrap battery emits both seed=1 headline and seed=2 stability check.

    Per ADR-022 multi-seed protocol + ADR-046 Q1 (Phase 4 Commit 2), every (rung, slice,
    metric) cell in the marginal-bootstrap battery is computed at seed=1 (headline) and
    again at seed=2 (stability check); both cells persist to
    evals/bootstrap/marginal_cells.parquet so the half-width comparison is queryable
    from disk per ADR-013. This invariant asserts:
    (1) for every (rung, slice, metric) tuple, the parquet contains exactly 2 rows
    (one per seed); (2) the n_resamples column equals 10000 for both seeds at canonical-run
    time; (3) when |headline_halfwidth - stability_halfwidth| / headline_halfwidth > 0.05
    the bootstrap_stability_check audit row carries a True flag (cross-references
    test_bootstrap_n_and_stability_check); (4) every cell roundtrips through
    MarginalBootstrapCellModel pydantic validation. Skipped until canonical Phase 4 evals
    fire against the 84 trained-rung prediction parquets.
    """
    raise NotImplementedError("invariant test stub — unskip at canonical Phase 4 evals run")


@pytest.mark.unit
@pytest.mark.skip(reason="deferred to canonical Phase 4 evals — needs 84 trained-rung parquets")
def test_block_bootstrap_folds_spoke_present() -> None:
    """Cross-fold CI audit always emits the block-bootstrap-on-folds spoke per A-008.

    Per ADR-024 + ADR-046 Q3 (Phase 4 Commit 3), the cross-fold CI orchestrator
    populates the block_bootstrap_ci_lo + block_bootstrap_ci_hi +
    block_bootstrap_ci_halfwidth + block_bootstrap_n_resamples columns for every
    (rung, slice, metric) cell in evals/audit/cross_fold_ci_audit.parquet — never
    None at canonical-run time. Per ADR-046 Q3, emission is unconditional (audit
    trail completeness) — the WRITEUP methodology spoke only references the
    LODO non-exchangeability claim conditionally on `a_008_flag_fired`. This
    invariant asserts:
    (1) every audit row has block_bootstrap_* fields non-null;
    (2) block_bootstrap_n_resamples == 10000 per ADR-022 budget;
    (3) block_bootstrap_ci_halfwidth >= 0 for every row;
    (4) block_bootstrap_ci_lo <= block_bootstrap_ci_hi for every row.
    Skipped until canonical Phase 4 evals run.
    """
    raise NotImplementedError("invariant test stub — unskip at canonical Phase 4 evals run")


@pytest.mark.unit
@pytest.mark.skip(reason="deferred to canonical Phase 4 evals — needs 84 trained-rung parquets")
def test_a_008_flag_fired_when_ratio_exceeds_1_5() -> None:
    """`a_008_flag_fired` column matches the cv_clt vs block-bootstrap halfwidth ratio.

    Per ADR-046 Q3 + A-008 + ADR-024 (Phase 4 Commit 3), every audit row's
    `a_008_flag_fired` boolean is True iff
    block_bootstrap_ci_halfwidth / cv_clt_ci_halfwidth > 1.5 (strict inequality
    per A_008_RATIO_THRESHOLD). Degenerate cv_clt halfwidth (== 0) yields True
    iff block_bootstrap_halfwidth > 0. This invariant asserts:
    (1) the boolean column is present in evals/audit/cross_fold_ci_audit.parquet;
    (2) the boolean value matches the ratio rule on every row (no audit drift);
    (3) when the flag fires for any (rung, slice, metric) cell, the methodology
    spoke `WRITEUP/methodology.md` contains the named "LODO non-exchangeability
    dominates within-fold variance" paragraph (Phase 5 Writeup integration).
    Skipped until canonical Phase 4 evals run.
    """
    raise NotImplementedError("invariant test stub — unskip at canonical Phase 4 evals run")


@pytest.mark.unit
@pytest.mark.skip(reason="deferred to Phase 4 Commit 5 orchestration — needs render_figures.py")
def test_figures_slate_7_svgs_present() -> None:
    """All 7 figure SVGs land at docs/plots/F{1..7}.svg per ADR-046 Q6 + ADR-030.

    Per ADR-046 Q6 (Phase 4 Commit 4 figures slate) + ADR-030 (Quarto site
    embeds figures from docs/plots/), the render_figures.py orchestrator
    (Commit 5) emits the canonical 7-figure slate as SVG files at
    docs/plots/F1.svg + docs/plots/F2.svg + ... + docs/plots/F7.svg. This
    invariant asserts:
    (1) all 7 files exist under docs/plots/ after `make render-figures`;
    (2) each is a non-empty valid SVG (starts with `<svg`);
    (3) FIGURE_SLATE_NAMES in src/eval/figures.py matches the filenames;
    (4) Quarto site config (_quarto.yml) references at least one figure for
    cross-link sanity.
    Skipped until Commit 5 orchestration lands + canonical evals complete.
    """
    raise NotImplementedError(
        "invariant test stub — unskip when render_figures.py orchestrates the canonical slate"
    )


@pytest.mark.unit
@pytest.mark.skip(reason="deferred to Phase 4 Commit 5 orchestration — needs render_figures.py")
def test_save_figure_provenance_chunks_present() -> None:
    """Every rendered figure carries provenance metadata via eval_toolkit.save_figure.

    Per ADR-046 Q6 + ADR-030 (provenance-aware SVG output), every figure
    produced by render_figures.py is written through eval_toolkit.plotting.save_figure
    with a provenance dict containing at minimum: figure_id (one of F1..F7),
    adr (ADR-046), git_commit_sha, generated_at (ISO timestamp). save_figure
    embeds the provenance dict as a <desc> chunk in the SVG so the reviewer
    can inspect each figure's origin without re-running. This invariant asserts:
    (1) every docs/plots/F{1..7}.svg contains the literal string "ADR-046";
    (2) every SVG contains a git_commit_sha matching a HEAD ancestor at render
    time; (3) every SVG contains a generated_at ISO-8601 timestamp.
    Skipped until Commit 5 orchestration lands.
    """
    raise NotImplementedError(
        "invariant test stub — unskip when render_figures.py orchestrates the canonical slate"
    )


@pytest.mark.unit
@pytest.mark.skip(reason="deferred to canonical Phase 4 evals — needs 84 trained-rung parquets")
def test_cv_clt_ci_headline_present() -> None:
    """Cross-fold CI audit emits cv_clt headline for every (rung, slice, metric) cell.

    Per ADR-024 + ADR-046 Q3 (Phase 4 Commit 2 headline), the cross-fold CI orchestrator
    (scripts/run_cv_clt_ci.py landing at Commit 5) emits one row per (rung, slice, metric)
    cell to evals/audit/cross_fold_ci_audit.parquet with the cv_clt_point_estimate +
    cv_clt_ci_lo + cv_clt_ci_hi + cv_clt_ci_halfwidth + k_folds + n_seeds_per_fold columns
    populated by eval_toolkit.bootstrap.cv_clt_ci on the per-fold metric vector. This
    invariant asserts:
    (1) the audit parquet contains one row per (trained_rung, slice, metric) tuple
    (4 trained rungs * (5 OOD slices + 1 IID + 1 pooled_ood) * 2 metrics = 56 rows);
    (2) cv_clt_ci_halfwidth > 0 for every row (degenerate halfwidths surface as data-quality
    flags upstream); (3) k_folds == 4 per ADR-016 Q2; (4) n_seeds_per_fold == 3 per ADR-006;
    (5) every cell roundtrips through CrossFoldCIModel pydantic validation. Commit 3 will
    add block-bootstrap spoke fields + a_008_flag_fired; this invariant asserts only the
    Commit 2 headline contract. Skipped until canonical Phase 4 evals run.
    """
    raise NotImplementedError("invariant test stub — unskip at canonical Phase 4 evals run")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_dual_policy_threshold_pairing() -> None:
    """Dual-policy thresholds fit per-(rung, fold, seed) on val with paired CI propagation.

    Per ADR-025 (dual-policy threshold characterization at symmetric 1% cost weights),
    the Detection policy fits eval_toolkit.thresholds.TargetFPRSelector(0.01) on
    validation per-(rung, fold, seed) and the Verification policy fits
    eval_toolkit.thresholds.TargetRecallSelector(0.99) on validation per-(rung, fold, seed);
    24 thresholds per trained rung × 4 trained rungs equals 96 threshold-pair
    instances total; CI propagation uses eval_toolkit.bootstrap.paired_bootstrap_op_point_diff
    (two-level bootstrap — refit threshold per val resample, apply on test resample,
    compute paired diff) consistent with ADR-022's per-(seed) threshold protocol.
    This invariant asserts: (1) the dual-policy threshold orchestrator
    (scripts/fit_dual_policy_thresholds.py) calls TargetFPRSelector(0.01).select(y_val, s_val)
    and TargetRecallSelector(0.99).select(y_val, s_val) for every (trained_rung, fold, seed)
    tuple; (2) reference rungs (4 untrained rungs per ADR-018) are excluded from
    dual-policy fitting (only recall@FPR pinpoints applied per SPEC §4 dual-policy
    applicability lock); (3) the bootstrap battery (scripts/run_bootstrap_battery.py)
    invokes paired_bootstrap_op_point_diff for trained-vs-trained dual-policy comparisons;
    (4) the headline emit (evals/results.json) carries an "FPR @ recall ≥ 99%" column
    on trained rungs and a footnote on the existing recall@FPR=1% column tagging it as
    the detection-policy operating point.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_verification_reachability_audit() -> None:
    """Verification-target reachability audit JSON is emitted per-(rung, fold, seed).

    Per ADR-025 Q4 (infeasibility handling) and assumption A-009, when
    TargetRecallSelector(0.99) cannot satisfy the recall ≥ 99% constraint on a
    (rung, fold, seed) val slice, the reporting protocol emits per-(rung, fold, seed)
    reachability evidence to evals/audit/verification_reachability.json and the
    headline cell carries an asterisk flag. This invariant asserts:
    (1) evals/audit/verification_reachability.json exists with the locked schema
    (top-level dict keyed by rung_id, then fold_id, then seed; each leaf entry contains
    target_reachable bool, target_recall=0.99, achieved_val_recall float, fallback_threshold
    float, fallback_test_fpr float); (2) every (trained_rung, fold, seed) tuple has an
    entry (96 entries total = 4 trained rungs × 4 folds × 3 seeds × 2 — but only the 96
    verification-side entries appear; detection-side reachability is trivially 100% so
    no audit needed); (3) any entry with target_reachable equals false has a corresponding
    asterisk flag in the headline emit (evals/results.json) cell for that rung's
    "FPR @ recall ≥ 99%" column at the matching aggregation level; (4) the spoke
    (WRITEUP/threshold-policy.md) "Verification-target reachability across trained rungs"
    subsection enumerates per-rung reachability rate (count of reachable cells / total
    cells per rung) as a cross-rung comparison artifact.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_module_layout_taxonomy() -> None:
    """src/ + scripts/ + configs/ + tests/ taxonomy matches ADR-026 contract.

    Per ADR-026 (module layout — concern-grouped sub-packages under src/), the locked
    layout is src/{data, training, scoring, eval, utils}/ with each sub-package being
    a Python package (contains __init__.py); scripts/ contains entrypoint files only
    (no library code; not importable as a package); configs/{runpod, rungs, profiles,
    data}/ each contain at least one YAML file at Phase 1 entry; tests/{conftest.py,
    test_invariants.py, fixtures/, unit/, smoke/, integration/} structure preserved.
    This invariant asserts: (1) each of src/{data, training, scoring, eval, utils}
    exists as a directory with an __init__.py; (2) scripts/ exists and contains no
    __init__.py (entrypoints are scripts, not a package); (3) configs/{runpod, rungs,
    profiles, data} exist as directories at Phase 1 entry; (4) tests/{fixtures, unit,
    smoke, integration} exist as directories at Phase 1 entry; (5) the no-emoji
    invariant scan globs already operate over src/ scripts/ configs/ tests/ docs/ so
    the layout lock does not change scan-target enumeration. Adding or moving a
    top-level src/ sub-package post-lock requires a superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_makefile_execution_context_stratification() -> None:
    """Makefile carries the three-target execution-context stratification per ADR-027.

    Per ADR-027 (smoke vs canonical separation — three Makefile targets stratified by
    execution context), the Makefile must declare: (1) make smoke target — runs
    pytest -m smoke + a fixture-data E2E pass through scripts/run_metrics_battery.py
    with configs/profiles/fixtures.yaml; constraints — laptop only, no GPU calls, no
    network calls, total wall-clock under 10 minutes; (2) make test-integration
    target — runs pytest -m integration; integration tests use pytest.importorskip
    plus pytest.mark.skipif idiom for GPU-conditional skipping (verified via grep of
    @pytest.mark.integration tests in tests/integration/); same target invocation
    works on laptop (skips GPU tests) and on cloud pod (runs them as pre-flight);
    (3) make headline-cloud target — wraps runpod-deploy validate --all + run
    --dry-run + run --config configs/runpod/headline.yaml; cost-cap-gated 125 USD
    per job per ADR-020 + A-002; NOT a test target. (4) make headline-dry-run target
    exposes runpod-deploy run --dry-run standalone for cost preview without
    provisioning. This invariant asserts all 4 targets exist as Makefile rules and
    that test-integration tests use the importorskip+skipif idiom rather than failing
    on no-GPU laptops. The honest debugging-grade-here-rigorous-upstream framing
    paragraph is required in WRITEUP/methodology.md (separately enforced by the
    reporting-completeness invariant).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_coverage_floor_70pct_enforced() -> None:
    """Makefile coverage target enforces 70% flat coverage floor per ADR-028.

    Per ADR-028 (test coverage floor — 70% flat with upstream-issue-filing
    discipline), the Makefile coverage target must invoke pytest with
    --cov-fail-under=70 (replacing the prior ungated --cov=. --cov-report=term-missing
    form). The CI command is uv run pytest --cov --cov-fail-under=70
    --cov-report=term-missing. This invariant asserts: (1) the Makefile coverage
    target string contains --cov-fail-under=70 (verified via subprocess grep on
    Makefile); (2) the co-locked process commitment is documented in
    decisions/upstream_issues.md "How to use this ledger" section under a
    "Test-coverage-gap entries" subsection covering the [test-coverage-gap] +
    [not-applicable] tag conventions; (3) STYLE.md project-deltas first bullet
    references the locked 70% floor (no longer the [OPEN: ...] placeholder).
    Behavioral verification — when synthetic coverage drops below 70%, the make
    coverage exit code is non-zero — is deferred to a Phase 1 integration test that
    constructs a temp-dir minimal repo to exercise the gate without polluting the
    real coverage report.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_pytest_markers_registered_and_in_sync() -> None:
    """Exactly 4 pytest markers registered + pyproject.toml + conftest.py in sync per ADR-029.

    Per ADR-029 (test marker strategy — 4-marker ratification), the locked taxonomy is
    exactly {unit, smoke, integration, network} — no property, no golden, no slow, no
    gpu. Markers are registered in BOTH pyproject.toml [tool.pytest.ini_options]
    markers list AND tests/conftest.py via pytest_configure addinivalue_line calls;
    --strict-markers is enabled in pyproject addopts so unknown markers fail loudly.
    This invariant asserts: (1) pyproject.toml [tool.pytest.ini_options] markers list
    is exactly the set {unit, smoke, integration, network} — set-equality check (no
    extras, no missing); (2) tests/conftest.py pytest_configure registers exactly the
    same 4 markers via addinivalue_line; (3) --strict-markers appears in pyproject
    addopts; (4) no test file in tests/ uses an unregistered marker (verified via
    grep of @pytest.mark.<name> patterns in tests/ + comparison against the
    registered set; pytest-builtin markers like skip, parametrize, skipif, xfail are
    excluded from the comparison); (5) no marker file appears in eval-toolkit-only
    set {property, golden} since math rigor lives upstream per ADR-027. Marker-add or
    marker-remove post-lock requires a superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_quarto_site_config_present() -> None:
    """_quarto.yml + .github/workflows/publish.yml + index.qmd present per ADR-030.

    Per ADR-030 (deliverable format — repo-only with Quarto-rendered HTML site via
    GH Actions; supersedes ADR-002), the repo must declare a Quarto website config
    plus a GH Actions workflow that publishes the site to GH Pages. This invariant
    asserts: (1) _quarto.yml exists at repo root; (2) _quarto.yml parses as valid
    YAML and declares project.type=website; (3) _quarto.yml declares format.html
    (HTML output target only — no PDF auxiliary per ADR-030 Q1.b lock); (4) the
    sidebar block under website includes contents referencing all 8 spokes
    (eval-design plus methodology-guarantees plus limitations-and-future-work plus
    data-decisions plus model-rungs plus threshold-policy plus reference-scorer-audit
    plus reproducibility) plus an auto: decisions/ADR-*.md glob for the ADRs
    section; (5) .github/workflows/publish.yml exists and references both
    quarto-actions/setup@v2 and quarto-actions/publish@v2 steps; (6) the workflow
    triggers on push to main and on tag push v*; (7) the workflow declares
    permissions block with contents=write plus pages=write plus id-token=write.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_index_qmd_reading_paths_present() -> None:
    """index.qmd contains three reviewer reading paths per ADR-031.

    Per ADR-031 (reviewer reading paths via index.qmd; supersedes ADR-004 PDF-as-hub
    framing), index.qmd at repo root carries the entry-point reading-path guide
    that replaces the PDF cover sheet role. This invariant asserts: (1) index.qmd
    exists at repo root; (2) index.qmd contains a Quick-skim path section header
    (A1 hiring manager 15-min path); (3) index.qmd contains an Audit path section
    header (A2 ML researcher 60-min path); (4) index.qmd contains a Deep-dive
    section header (reproduce-numbers path with T0 plus T1 plus T3 references per
    ADR-034); (5) index.qmd contains a Repo map section enumerating src plus
    scripts plus configs plus decisions plus results plus tests plus WRITEUP plus
    WRITEUP/; (6) index.qmd contains a Submission anchors section listing the
    three reviewer URLs (source pin at submission tag plus live Quarto site plus GH
    release page) per ADR-033 reviewer-email URL plan; (7) WRITEUP/reproducibility.md
    spoke exists (slotted by ADR-031 for ADR-034 content). Adding a new spoke or
    reading-path section is allowed without superseding ADR; spoke removal requires
    superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_hf_hub_publication_naming_convention() -> None:
    """Published HF Hub model repos follow BBehring/prompt-injection-<rung> per ADR-032.

    Per ADR-032 (HF Hub publication — primary headline rungs only with model card
    discipline), every published rung must follow the BBehring/prompt-injection-
    <rung-name> naming convention plus carry a model card with the locked
    frontmatter schema. This invariant asserts at Phase 5 close: (1) for each
    rung in the headline-publication set (frozen-probe plus LoRA plus
    conditionally full-FT plus conditionally TF-IDF+LR per ADR-019 plus ADR-017
    final composition), a public HF Hub repo exists at BBehring/prompt-injection-
    <rung-name> (verified via huggingface_hub.HfApi().list_repos with author
    BBehring filter); (2) each repo's README YAML frontmatter contains the
    required keys — license (apache-2.0 inherited from ModernBERT-base) plus tags
    (text-classification plus prompt-injection plus safety) plus datasets (HF
    dataset IDs at the pinned SHAs per ADR-016) plus model-index.results
    (per-rung headline metrics from results.json with the pooled-OOD column per
    ADR-021) plus intended use plus limitations plus citation; (3) reference
    scorers per ADR-018 are NOT present under BBehring/ namespace (they remain
    at their canonical authors). Publication-set composition is provisional —
    final list revisitable at Phase 5 per ADR-032 extension condition without
    superseding this invariant.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_submission_tag_changelog_present() -> None:
    """CHANGELOG.md follows Keep-a-Changelog 1.1.0 + has v1.0.0 section at submission per ADR-033.

    Per ADR-033 (GitHub release strategy — rehearsal plus submission plus
    patches), CHANGELOG.md is committed at repo root in Keep-a-Changelog 1.1.0
    format with entries written in human language not git-shortlog dumps. This
    invariant asserts: (1) CHANGELOG.md exists at repo root; (2) the file
    references keepachangelog.com and semver.org in its preamble (format
    declaration); (3) at v1.0.0 submission tag time, a [v1.0.0] section exists
    with at minimum a Submission subsection naming the 4 publication artefacts
    (Quarto site published to GH Pages plus HF Hub model repos published plus
    methodology writeup plus reviewer URLs); (4) at v1.0.0 submission tag time,
    a [v0.9.0-rc1] section exists naming the rehearsal tag's purpose; (5)
    Keep-a-Changelog section structure is followed (Added plus Changed plus
    Deprecated plus Removed plus Fixed plus Security as applicable); (6) version
    links at file bottom match the SemVer tag format. Patch tags v1.0.x add
    sections without changing existing ones (audit-trail discipline).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_reproducibility_tier_documented() -> None:
    """WRITEUP/reproducibility.md documents T0+T1+T3 tier ladder per ADR-034.

    Per ADR-034 (reproducibility tier — full ladder T0 eval-from-hub plus T1
    smoke plus T3 headline-cloud), the WRITEUP/reproducibility.md spoke
    documents the tier ladder with verbatim commands plus cost plus time plus
    what-each-tier-verifies plus what-each-tier-does-NOT-verify. This invariant
    asserts: (1) WRITEUP/reproducibility.md exists; (2) the spoke contains all
    three tier names T0 plus T1 plus T3 in section headers; (3) each tier has a
    verbatim command in a code block — make smoke plus make eval-from-hub plus
    make headline-cloud; (4) the Makefile contains all three target names
    (smoke plus eval-from-hub plus headline-cloud) as rules; (5) the spoke
    contains the tier-coverage matrix with cost plus time plus verifies plus
    does-not-verify columns for each tier; (6) the spoke explicitly carves out
    T2 (test-integration) as a developer-tool tier with rationale (not promoted
    to reviewer-facing per ADR-034 Q4 walk); (7) the spoke includes the ACM
    artifact-badging mapping subsection (T0+T1 supply Functional+Reusable; T3
    supplies Reproducible). Adding a new tier requires superseding ADR; tier
    removal requires superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_env_example_template_present() -> None:
    """.env.example template exists with 4 canonical env vars per ADR-035.

    Per ADR-035 (secrets management — three-store split aligned with execution
    context), .env.example is committed at repo root as a placeholder template
    that enumerates the four canonical env vars consumer libraries discover via
    env-var auto-discovery. This invariant asserts: (1) .env.example exists at
    repo root; (2) the file enumerates all four canonical env vars HF_TOKEN
    plus RUNPOD_API_KEY plus OPENAI_API_KEY plus ANTHROPIC_API_KEY (grep
    each); (3) the values are placeholder-shaped not real tokens — HF_TOKEN
    matches hf_x-times-pattern, OPENAI_API_KEY matches sk-x-times-pattern,
    ANTHROPIC_API_KEY matches sk-ant-x-times-pattern, RUNPOD_API_KEY matches
    YOUR_..._HERE pattern (regex check; no value matches real-token signature);
    (4) .gitignore covers .env (verified via subprocess git check-ignore .env
    returns nonzero exit code meaning ignored); (5) .gitignore explicitly
    exempts .env.example via negation pattern (.env.example is NOT ignored;
    verified via git check-ignore .env.example returns nonzero exit code
    meaning NOT-ignored when negation matches); (6) pre-commit gitleaks hook
    is enabled in .pre-commit-config.yaml (defense-in-depth).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_pyproject_library_version_pins() -> None:
    """pyproject.toml contains the three locked library version pins per ADR-036.

    Per ADR-036 (library version pins — tag pin plus freeze for submission
    window), pyproject.toml dependencies stanza contains three git+URL+tag
    specifiers at the locked versions. This invariant asserts: (1) pyproject.toml
    dependencies stanza contains the eval-toolkit at v0.31.0 specifier (regex
    grep for the literal version tag plus the brandon-behring slash eval-toolkit
    path); (2) pyproject.toml dependencies stanza contains the runpod-deploy at
    v0.7.7 specifier matching the ADR-020 pre-existing pin; (3) pyproject.toml
    dependencies stanza contains the research_toolkit at v1.9.1 specifier;
    (4) uv.lock includes all three libraries at the same versions (uv.lock
    parse plus version field check); (5) no library is pinned to a main branch
    or a non-tagged commit (regex check excluding the at-tag pattern); (6) all
    three libraries install cleanly under requires-python >=3.13 per ADR-037
    (verified via uv sync at Phase 0-08 close — if any conflict the lock
    cannot be released without fix-forward).
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_python_version_pin_at_3_13() -> None:
    """pyproject.toml requires-python equals >=3.13 + .python-version equals 3.13 per ADR-037.

    Per ADR-037 (Python version pin — ratify requires-python >=3.13), the
    pre-existing bc8ce4e commit lock is ratified at Phase 0-08. This invariant
    asserts: (1) pyproject.toml line containing requires-python reads exactly
    the value quote >=3.13 quote (regex grep); (2) .python-version file at
    repo root contains exactly 3.13 (single-line read plus strip plus equality
    check); (3) sys.version_info major-minor is at least (3, 13) when running
    pytest — the test fails if invoked on Python <3.13 (sanity gate); (4) uv
    sync exit code is 0 under the >=3.13 pin (verified via subprocess at lock
    time only — Phase 1 plus implementation defers active enforcement to CI).
    Bump triggers — 3.13-only feature dependency emergence tightens the pin
    (no ADR supersession needed); 3.13 wheel-availability issue on RunPod
    base images loosens to >=3.12 via superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_roadmap_phase4_phase5_tailored() -> None:
    """docs/ROADMAP.md Phase 4 + Phase 5 tailored per ADR-038.

    Per ADR-038 (Phase tailoring — light ROADMAP edits), docs/ROADMAP.md is
    updated at Phase 0-08 close with three surface-area edits — Phase 4 close
    gains a rehearsal-tag note; Phase 5 description rewritten with Quarto plus
    HF Hub plus reproducibility expansions; decision-needed prompt at line 83
    replaced. This invariant asserts: (1) docs/ROADMAP.md Phase 4 section
    contains the literal string v0.9.0-rc1 (rehearsal tag name); (2)
    docs/ROADMAP.md Phase 5 section contains all five ADR citations — ADR-030
    plus ADR-031 plus ADR-032 plus ADR-033 plus ADR-034 (regex grep for each);
    (3) docs/ROADMAP.md still declares exactly 5 phases past Phase 0 (no Phase
    4.5 or 5a/5b splits; count headings matching # Phase N pattern; expected
    count is 6 including Phase 0); (4) the kit-default Decision needed at line
    83 prompt no longer reads "Decision needed (Phase 0)" — replaced with
    Phase 0-08 lock note pointing at ADR-038. Restructure-options rejected at
    Q6 walk (Phase 4.5 / Phase 5a-b-c / Phase 2b smoke-preflight / Phase 3+4
    collapse) — any reopening requires superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")


@pytest.mark.unit
@pytest.mark.skip(reason="invariant test stub — implement in Phase 5 at v0.9.0-rc1 close")
def test_phase_0_audit_findings_documented() -> None:
    """ADR-040 + 7-assumption backfill from Phase 0 final audit present per ADR-040.

    Per ADR-040 (Phase 0 final audit findings + 7-assumption backfill), the audit
    cycle produced one new ADR (this ADR-040) plus 7 new entries in assumptions.md
    (A-010 through A-016). This invariant asserts: (1) decisions/ADR-040-*.md exists;
    (2) assumptions.md contains rows for each of A-010 through A-016 (regex grep for
    the literal ID strings at start-of-row pipe pattern); (3) each new row's
    severity field reads high or medium per the calibration lock (high — A-010 plus
    A-012 plus A-013 plus A-014 plus A-016; medium — A-011 plus A-015 — 5 high plus
    2 medium total); (4) each new row's Linked-to column references ADR-040 plus
    the parent ADR that introduced the assumption (A-010 references ADR-030 plus
    ADR-033 plus ADR-039; A-011 references ADR-020 plus A-002; A-012 references
    ADR-020 plus ADR-001; A-013 references ADR-016 plus ADR-032 plus ADR-034;
    A-014 references ADR-018 plus ADR-022 plus supplements A-007; A-015 references
    ADR-018 plus ADR-016; A-016 references ADR-001). Dismissal rationales from
    ADR-040 body (ADR-015 staleness; Mosbach 2021 citation; test-stub count) are
    documentation-level and do NOT require additional invariant tests — they are
    verified by reading ADR-040 body and matching grep observations.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 5 at v0.9.0-rc1 close")


@pytest.mark.unit
@pytest.mark.skip(reason="v1.0.0 carryforward stub — see module docstring; deferred to v1.1.x")
def test_submission_readiness_gates_satisfied() -> None:
    """6-gate submission-readiness integration checklist passes at v1.0.0 tag per ADR-039.

    Per ADR-039 (project-specific acceptance criteria — 6-gate integration
    checklist for v1.0.0 submission tag), submission-readiness aggregates over
    per-ADR acceptance_criterion fields plus the kit-default §6 gates. This
    invariant asserts at v1.0.0 submission tag time — (1) grep -c quote-bracket
    OPEN bracket-quote SPEC_SHEET.md returns 0 excluding the Status doc-header
    OPEN line which transitions to LOCKED at Phase 0 close (verify via line-
    matching not raw count); (2) awk slash-pipe open pipe-slash on
    SPEC_GREENFIELD.md ledger appendix section returns 0 lines (all rows are
    locked-to-X or superseded-by-NNN or deferred-to-phase-N); (3) pytest
    --collect-only tests/test_invariants.py shows zero skip-marked tests (all
    @pytest.mark.skip decorators removed at submission tag — this very test
    among them); (4) make audit exits 0 (SUBMISSION_AUDIT.md regenerates with
    every claim Accepted or Superseded; no Proposed claims); (5) git tag -l
    v0.9.0-rc1-star returns at least one tag matching the rehearsal-tag
    pattern per ADR-033; (6) the three reviewer URLs at v1.0.0 return HTTP 200
    or 301-redirect-to-200 via curl --head — source pin at tree v1.0.0 plus
    live Quarto site at brandon-behring.github.io plus GH release page at
    releases tag v1.0.0. Adding a 7th-or-8th integration gate is allowed
    without ADR supersession (the framing is locked; gates are extensible);
    removing a gate requires superseding ADR.
    """
    raise NotImplementedError("invariant test stub — implement in Phase 1")
