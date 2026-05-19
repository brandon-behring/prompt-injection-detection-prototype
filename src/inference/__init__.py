"""Phase 4 inference-strategy package (per ADR-026 + ADR-060).

Subpackage modules (v1.1.2 Phase B): windowed.

Submodule purpose
-----------------
- ``windowed``: chunk-and-average + head-truncation inference strategies
  for the DeBERTa-v3-base medium ablation per ADR-060. Reported side-by-
  side as confound controls in the ModernBERT-vs-DeBERTa-v3 long-context-
  vs-backbone-dominance comparison (RESULTS §1B).

History
-------
New package at v1.1.2 Phase B (per ADR-060 carryforward). Greenfield;
introduced because the existing src/training/ trainer's inference path
(``train_modernbert._predict_proba``) operates on single-window inputs
only — chunk-and-average requires multi-window forward-pass + per-window
softmax averaging.
"""
