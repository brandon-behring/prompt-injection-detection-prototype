"""src/scoring/ — Phase 3 reference-scorer adapters per ADR-026 + ADR-018.

The 4 reference rungs from ADR-018 are organized as 2 vendor families:
- ProtectAI (v1 + v2) — local HF inference; free Tier A (CI-safe)
- LLM judges (gpt-4o-2024-08-06 + claude-sonnet-4-6) — paid API; Tier B
  (cost-cap-gated; interactive approval required)

All scorers write to the unified parquet schema enforced by
`src.eval.schemas.PredictionsRowModel` per ADR-045 Q3.

Per ADR-018 contamination taxonomy:
- ProtectAI v1 + v2 → `suspected_contamination`
- gpt-4o-2024-08-06 + claude-sonnet-4-6 → `vendor_black_box`
"""
