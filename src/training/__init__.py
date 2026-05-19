"""Phase 2 training primitives package (per ADR-026 + ADR-044).

Subpackage modules (Commit 2): batch_table, lora_config, training_args,
weighted_trainer, load_backbone, softmax_cast.

Subpackage modules (Commits 3-4): tfidf_lr, train_classical, train_modernbert.

History
-------
v1.1.2 Phase A (per ADR-060 carryforward): ``load_modernbert`` was renamed
to ``load_backbone`` to accept an explicit ``hf_id`` kwarg, so the same loader
serves both ModernBERT-base (ADR-019) and DeBERTa-v3-base (ADR-060). The
flash-attn-fallback recipe is unchanged.
"""
