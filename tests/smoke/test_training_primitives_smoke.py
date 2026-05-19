"""Smoke tests for src/training/ primitives (Phase 2 Commit 2 per ADR-044).

Validates the locked recipes from ADR-019 + ADR-020:
- ``batch_table`` invariant (effective batch == 32 across GPU classes).
- ``lora_config`` returns the locked LoraConfig.
- ``training_args`` propagates seed + recipe constants.
- ``softmax_cast`` casts bf16 -> fp32 before softmax/sigmoid.
- ``load_backbone`` has the flash-attn-fallback try/except structure (source
  inspection; does not load weights — laptop-CPU-safe per ADR-027 smoke).
  v1.1.2 Phase A renamed from ``load_modernbert`` to generic ``load_backbone``
  per ADR-060 carryforward (DeBERTa-v3-base ablation needs a second backbone).
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest


@pytest.mark.smoke
def test_batch_table_effective_batch_invariant() -> None:
    """Every BATCH_TABLE entry preserves effective batch == 32 (ADR-019 lock)."""
    from src.training.batch_table import BATCH_TABLE, EFFECTIVE_BATCH

    assert EFFECTIVE_BATCH == 32
    for gpu_class, cfg in BATCH_TABLE.items():
        product = cfg.per_device * cfg.grad_accum
        assert product == EFFECTIVE_BATCH, (
            f"GPU class {gpu_class!r}: per_device={cfg.per_device} * "
            f"grad_accum={cfg.grad_accum} = {product} != {EFFECTIVE_BATCH}"
        )


@pytest.mark.smoke
def test_batch_config_validates_product() -> None:
    """BatchConfig __post_init__ raises ValueError when product != 32."""
    from src.training.batch_table import BatchConfig

    with pytest.raises(ValueError, match="violates effective-batch invariant"):
        BatchConfig(per_device=8, grad_accum=2)  # 16 != 32


@pytest.mark.smoke
@pytest.mark.parametrize(
    "device_name, expected_class",
    [
        ("NVIDIA H100 80GB HBM3", "H100"),
        ("NVIDIA H100 NVL", "H100"),
        ("NVIDIA H200", "H200"),
        ("NVIDIA A100-SXM4-80GB", "A100-80G"),
        ("NVIDIA A100 80GB PCIe", "A100-80G"),
        ("NVIDIA A100-SXM4-40GB", "A100-40G"),
        ("NVIDIA L40S", "L40S"),
        ("NVIDIA L40", "L40"),
    ],
)
def test_classify_gpu_known_classes(device_name: str, expected_class: str) -> None:
    """classify_gpu maps every ADR-020 pod.gpu_order entry to the right key."""
    from src.training.batch_table import classify_gpu

    assert classify_gpu(device_name) == expected_class


@pytest.mark.smoke
def test_classify_gpu_fails_loud_on_unknown() -> None:
    """classify_gpu raises KeyError on unrecognized GPU (per ADR-020 line 99)."""
    from src.training.batch_table import classify_gpu

    with pytest.raises(KeyError, match="not in BATCH_TABLE"):
        classify_gpu("AMD MI300X 192GB")  # not in pod.gpu_order


@pytest.mark.smoke
def test_lookup_batch_config_h100() -> None:
    """lookup_batch_config returns the H100 BatchConfig for an H100 device."""
    from src.training.batch_table import lookup_batch_config

    cfg = lookup_batch_config("NVIDIA H100 80GB HBM3")
    assert cfg.per_device == 16
    assert cfg.grad_accum == 2


@pytest.mark.smoke
def test_lora_config_locked_values() -> None:
    """build_lora_config returns the ADR-019 locked LoraConfig.

    PEFT may store target_modules / modules_to_save as set or list; we compare
    as sorted sets since the ADR locks the 4-module enumeration, not an order.
    """
    from src.training.lora_config import build_lora_config

    cfg = build_lora_config()
    assert cfg.r == 8
    assert cfg.lora_alpha == 16
    assert cfg.lora_dropout == 0.1
    # target_modules + modules_to_save may be list, set, or None per PEFT version.
    assert cfg.target_modules is not None
    assert set(cfg.target_modules) == {"Wqkv", "attn.Wo", "mlp.Wo", "mlp.Wi"}
    assert cfg.modules_to_save is not None
    assert set(cfg.modules_to_save) == {"classifier"}
    assert cfg.task_type == "SEQ_CLS"
    assert cfg.bias == "none"


@pytest.mark.smoke
def test_training_args_seed_propagation(tmp_path: Path) -> None:
    """build_training_args propagates seed + locks recipe constants."""
    from src.training.training_args import build_training_args

    args = build_training_args(
        output_dir=tmp_path,
        seed=43,
        per_device_train_batch_size=16,
        gradient_accumulation_steps=2,
    )
    assert args.seed == 43
    assert args.learning_rate == 1e-4
    assert args.warmup_ratio == 0.10
    assert args.lr_scheduler_type == "cosine"
    assert args.num_train_epochs == 2
    assert args.bf16 is True
    assert args.fp16 is False
    assert args.max_grad_norm == 1.0
    assert args.weight_decay == 0.01
    assert args.save_strategy == "epoch"
    assert args.eval_strategy == "no"


@pytest.mark.smoke
def test_softmax_fp32_cast() -> None:
    """softmax_fp32 casts bf16 inputs to fp32 before softmax."""
    import torch

    from src.training.softmax_cast import softmax_fp32

    bf16_logits = torch.tensor([[1.0, 2.0]], dtype=torch.bfloat16)
    out = softmax_fp32(bf16_logits)
    assert out.dtype == torch.float32
    assert torch.allclose(out.sum(dim=-1), torch.tensor([1.0]))


@pytest.mark.smoke
def test_sigmoid_fp32_cast() -> None:
    """sigmoid_fp32 casts bf16 inputs to fp32 before sigmoid."""
    import torch

    from src.training.softmax_cast import sigmoid_fp32

    bf16_logits = torch.tensor([0.0, 1.0], dtype=torch.bfloat16)
    out = sigmoid_fp32(bf16_logits)
    assert out.dtype == torch.float32
    assert torch.allclose(out[0], torch.tensor(0.5))


@pytest.mark.smoke
def test_flash_attn_fallback_structure_present() -> None:
    """load_backbone wraps from_pretrained in (ValueError, ImportError) try/except."""
    from src.training import load_backbone

    src = inspect.getsource(load_backbone)
    assert "except (ValueError, ImportError)" in src, (
        "load_backbone must catch (ValueError, ImportError) per ADR-020 flash-attn-fallback recipe"
    )
    assert "flash_attn_fallback" in src, (
        "load_backbone must emit flash_attn_fallback event in fallback branch per ADR-020 line 124"
    )


@pytest.mark.smoke
def test_compute_class_weights_balanced() -> None:
    """compute_class_weights_tensor returns sklearn balanced weights."""
    import numpy as np

    from src.training.weighted_trainer import compute_class_weights_tensor

    # 9 negatives + 1 positive (1:9 imbalance like Phase 1 LODO train pool).
    labels = np.array([0] * 9 + [1] * 1)
    weights = compute_class_weights_tensor(labels)

    assert weights.dtype.is_floating_point
    assert weights.shape == (2,)
    # sklearn balanced: w_c = n_samples / (n_classes * n_samples_c). For class 0
    # (9 samples): 10 / (2 * 9) = 0.555. For class 1 (1 sample): 10 / (2 * 1) = 5.0.
    assert abs(weights[0].item() - (10 / (2 * 9))) < 1e-5
    assert abs(weights[1].item() - (10 / (2 * 1))) < 1e-5
