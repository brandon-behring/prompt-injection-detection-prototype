"""Smoke tests for src/training/train_modernbert (Phase 2 Commit 4 per ADR-044).

Validates:
- YAML config loading + ``classifier_type`` validation for all 3 transformer rungs.
- ``prepare_model`` logic per mode (frozen-probe freezes backbone; lora wraps;
  full-FT unchanged) — uses mock + small ``torch.nn.Module`` so smoke tests do
  not download the ~150 MB ModernBERT-base weights.
- ``PerEpochPredictionsCallback`` writes parquets with the expected schema.
- ``PREDICTIONS_SCHEMA`` includes the ``epoch`` dimension per ADR-019.
- The 3 committed ``configs/rungs/*.yaml`` files parse + carry the right
  classifier types + identical seed slate.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pandas as pd
import pytest
import torch
import yaml
from torch import nn


@pytest.fixture
def transformer_config_dict() -> dict[str, Any]:
    """Synthetic frozen-probe-like config dict (structurally complete)."""
    return {
        "rung_id": "frozen_probe",
        "rung_label": "ModernBERT-base frozen-probe",
        "classifier_type": "frozen_probe",
        "backbone": {
            "hf_id": "answerdotai/ModernBERT-base",
            "revision": "8949b909ec900327062f0ebf497f51aef5e6f0c8",
        },
        "training": {
            "learning_rate": 1.0e-4,
            "warmup_ratio": 0.10,
            "lr_scheduler_type": "cosine",
            "num_train_epochs": 2,
            "bf16": True,
            "fp16": False,
            "max_grad_norm": 1.0,
            "weight_decay": 0.01,
            "effective_batch": 32,
            "save_strategy": "epoch",
            "eval_strategy": "no",
        },
        "tokenizer": {"max_length": 8192, "pad_to_multiple_of": 8, "truncation": True},
        "class_weight": "balanced",
        "seeds": [42, 43, 44],
        "predictions_dir": "evals/predictions",
        "predictions_file_template": "frozen-probe__fold{fold}__seed{seed}__epoch{epoch}.parquet",
        "checkpoint_dir_template": "evals/checkpoints/frozen_probe/fold{fold}/seed{seed}",
    }


class _FakeModernBERT(nn.Module):
    """Tiny stand-in for ModernBERT with a ``backbone`` + ``classifier`` split.

    Used by ``prepare_model`` smoke tests to verify the freeze logic without
    downloading the real ~150 MB ModernBERT-base weights.
    """

    def __init__(self) -> None:
        super().__init__()
        self.backbone = nn.Linear(10, 5)
        self.classifier = nn.Linear(5, 2)


@pytest.mark.smoke
def test_load_config_accepts_all_three_transformer_types(
    tmp_path: Path, transformer_config_dict: dict[str, Any]
) -> None:
    """load_config accepts frozen_probe + lora + full_ft."""
    from src.training.train_modernbert import VALID_CLASSIFIER_TYPES, load_config

    for mode in sorted(VALID_CLASSIFIER_TYPES):
        cfg = dict(transformer_config_dict)
        cfg["classifier_type"] = mode
        path = tmp_path / f"{mode}.yaml"
        path.write_text(yaml.safe_dump(cfg))
        parsed = load_config(path)
        assert parsed["classifier_type"] == mode


@pytest.mark.smoke
def test_load_config_rejects_invalid_type(
    tmp_path: Path, transformer_config_dict: dict[str, Any]
) -> None:
    """load_config raises on classifier_type=classical (wrong trainer for that rung)."""
    from src.training.train_modernbert import load_config

    cfg = dict(transformer_config_dict)
    cfg["classifier_type"] = "classical"
    path = tmp_path / "wrong.yaml"
    path.write_text(yaml.safe_dump(cfg))
    with pytest.raises(ValueError, match="classifier_type must be one of"):
        load_config(path)


@pytest.mark.smoke
def test_load_config_requires_backbone_fields(
    tmp_path: Path, transformer_config_dict: dict[str, Any]
) -> None:
    """load_config raises if backbone.hf_id / backbone.revision are missing."""
    from src.training.train_modernbert import load_config

    cfg = dict(transformer_config_dict)
    del cfg["backbone"]
    path = tmp_path / "no_backbone.yaml"
    path.write_text(yaml.safe_dump(cfg))
    with pytest.raises(ValueError, match="backbone.hf_id"):
        load_config(path)


@pytest.mark.smoke
def test_committed_transformer_configs_parse() -> None:
    """All 3 committed configs/rungs/{frozen_probe,lora,full_ft}.yaml parse correctly."""
    from src.training.train_modernbert import load_config

    repo_root = Path(__file__).resolve().parent.parent.parent
    for rung in ("frozen_probe", "lora", "full_ft"):
        cfg_path = repo_root / "configs" / "rungs" / f"{rung}.yaml"
        cfg = load_config(cfg_path)
        assert cfg["classifier_type"] == rung
        assert cfg["seeds"] == [42, 43, 44]
        assert cfg["backbone"]["hf_id"] == "answerdotai/ModernBERT-base"
        assert len(cfg["backbone"]["revision"]) >= 7
        # Per-epoch save discipline — template has {epoch} placeholder.
        assert "{epoch}" in cfg["predictions_file_template"]


@pytest.mark.smoke
def test_prepare_model_frozen_probe_freezes_backbone() -> None:
    """frozen_probe mode freezes all backbone params; classifier head trainable."""
    fake_model = _FakeModernBERT()
    with patch("src.training.train_modernbert.load_modernbert", return_value=fake_model):
        from src.training.train_modernbert import prepare_model

        result = prepare_model(
            classifier_type="frozen_probe",
            backbone_revision="dummy_sha",
        )
    # backbone.weight + backbone.bias frozen; classifier.weight + classifier.bias trainable.
    classifier_trainable = [
        param.requires_grad
        for name, param in result.named_parameters()
        if name.startswith("classifier")
    ]
    backbone_frozen = [
        not param.requires_grad
        for name, param in result.named_parameters()
        if not name.startswith("classifier")
    ]
    assert all(classifier_trainable), "all classifier params must be trainable"
    assert all(backbone_frozen), "all non-classifier params must be frozen"


@pytest.mark.smoke
def test_prepare_model_lora_wraps_with_peft() -> None:
    """lora mode wraps the base model via get_peft_model + LoraConfig."""
    fake_model = _FakeModernBERT()
    fake_wrapped = _FakeModernBERT()  # sentinel; PEFT actual wraps would differ

    with (
        patch("src.training.train_modernbert.load_modernbert", return_value=fake_model),
        patch("src.training.train_modernbert.get_peft_model", return_value=fake_wrapped) as gpm,
    ):
        from src.training.train_modernbert import prepare_model

        result = prepare_model(classifier_type="lora", backbone_revision="dummy")

    assert gpm.called, "get_peft_model must be called in lora mode"
    assert result is fake_wrapped
    # LoraConfig passed as second positional arg.
    _, lora_cfg = gpm.call_args.args
    assert lora_cfg.r == 8
    assert lora_cfg.lora_alpha == 16


@pytest.mark.smoke
def test_prepare_model_full_ft_leaves_unchanged() -> None:
    """full_ft mode leaves all params trainable (HF default)."""
    fake_model = _FakeModernBERT()
    with patch("src.training.train_modernbert.load_modernbert", return_value=fake_model):
        from src.training.train_modernbert import prepare_model

        result = prepare_model(classifier_type="full_ft", backbone_revision="dummy")
    assert result is fake_model
    assert all(p.requires_grad for p in result.parameters())


@pytest.mark.smoke
def test_prepare_model_rejects_unknown_type() -> None:
    """prepare_model raises ValueError on unknown classifier_type."""
    from src.training.train_modernbert import prepare_model

    with pytest.raises(ValueError, match="Unknown classifier_type"):
        prepare_model(classifier_type="classical", backbone_revision="dummy")


@pytest.mark.smoke
def test_predictions_schema_includes_epoch() -> None:
    """Per-epoch predictions schema includes the epoch dimension per ADR-019."""
    from src.training.train_modernbert import PREDICTIONS_SCHEMA

    assert "epoch" in PREDICTIONS_SCHEMA
    assert "predicted_proba_class1" in PREDICTIONS_SCHEMA
    assert "rung" in PREDICTIONS_SCHEMA


@pytest.mark.smoke
def test_per_epoch_callback_writes_parquet_shape(tmp_path: Path) -> None:
    """PerEpochPredictionsCallback writes parquet with the expected schema."""
    from src.training.train_modernbert import (
        PREDICTIONS_SCHEMA,
        PerEpochPredictionsCallback,
    )

    # Build a minimal model that returns deterministic logits regardless of input.
    class _DeterministicModel(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.classifier = nn.Linear(1, 2)

        def forward(self, **kwargs: Any) -> Any:
            input_ids = kwargs["input_ids"]
            batch_size = input_ids.shape[0]
            # Return [batch, 2] logits favoring class 0.
            logits = torch.zeros((batch_size, 2), dtype=torch.float32)
            logits[:, 0] = 1.0
            return type("Output", (), {"logits": logits})()

    model = _DeterministicModel()

    test_df = pd.DataFrame(
        {
            "text": ["hello world"] * 5,
            "label": [0, 1, 0, 1, 0],
            "source": ["smoke"] * 5,
            "row_idx_in_source": list(range(5)),
        }
    )

    # Use a tiny tokenizer-like object via the real ModernBERT tokenizer would
    # download weights. Instead build a class that mimics the calling shape.
    class _StubTokenizer:
        def __call__(
            self,
            texts: list[str],
            *,
            truncation: bool,
            max_length: int,
            padding: Any,
            return_tensors: str | None = None,
        ) -> Any:
            n = len(texts)
            ids = torch.zeros((n, 4), dtype=torch.long)
            mask = torch.ones((n, 4), dtype=torch.long)
            return type(
                "Encoding",
                (),
                {
                    "to": lambda self_, device: self_,  # noqa: ARG005
                    "items": lambda self_: {"input_ids": ids, "attention_mask": mask}.items(),
                    "__contains__": lambda self_, k: k in {"input_ids", "attention_mask"},
                    "input_ids": ids,
                    "attention_mask": mask,
                    "__iter__": lambda self_: iter({"input_ids": ids, "attention_mask": mask}),
                    "__getitem__": lambda self_, k: {
                        "input_ids": ids,
                        "attention_mask": mask,
                    }[k],
                    "keys": lambda self_: {"input_ids", "attention_mask"},
                },
            )()

    cb = PerEpochPredictionsCallback(
        rung_id="frozen_probe",
        fold=0,
        seed=42,
        test_df=test_df,
        tokenizer=_StubTokenizer(),  # type: ignore[arg-type]
        max_length=8,
        per_device_batch_size=2,
        predictions_root=tmp_path,
        predictions_file_template="frozen-probe__fold{fold}__seed{seed}__epoch{epoch}.parquet",
    )

    # Simulate on_epoch_end firing after epoch 1.
    class _FakeState:
        epoch: float = 1.0

    cb.on_epoch_end(
        args=None,  # type: ignore[arg-type]
        state=_FakeState(),  # type: ignore[arg-type]
        control=None,  # type: ignore[arg-type]
        model=model,
    )

    assert len(cb.written_paths) == 1
    out = pd.read_parquet(cb.written_paths[0])
    assert set(out.columns) >= set(PREDICTIONS_SCHEMA)
    assert len(out) == 5
    assert (out["epoch"] == 1).all()
    assert (out["rung"] == "frozen_probe").all()
    assert out["predicted_proba_class1"].between(0, 1).all()
