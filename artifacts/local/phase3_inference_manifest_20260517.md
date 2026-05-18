# Phase 3 inference outputs — 2026-05-17 local-CPU recovery batch

## What ran

X10 recovery (per `decisions/upstream_issues.md` line 25 + plan file):

1. **Classical floor LODO** (`make train-classical-floor`) — 12 cells × 1 LODO test source each = 12 parquets
   - Time: 3 min wall (180s)
   - Output: `evals/predictions/tfidf-lr__fold{0..3}__seed{42,43,44}.parquet`

2. **Classical floor OOD** (`scripts/run_inference_battery.py --tier classical-ood`) — 12 cells × 5 OOD slates = 60 parquets
   - Time: 184s wall
   - Output: `evals/predictions/tfidf-lr__fold{F}__seed{S}__{notinject,xstest,jbb_behaviors,bipia,injecagent}.parquet`

3. **ProtectAI v1 + v2 reference scorers** (`scripts/run_inference_battery.py --tier ref-free`) — 2 versions × 9 sources (4 LODO + 5 OOD) = 18 parquets
   - Time: 260s wall
   - Output: `evals/predictions/protectai-{v1,v2}__<source>.parquet`

Total: 90 new prediction parquets (13 MB on disk). All gitignored under `evals/predictions/` per Phase 0-04 storage discipline.

## What's still missing (per Path A recovery)

- Trained-rung OOD inference (frozen-probe + LoRA + full-FT × 5 OOD slates × 12 cells). DEFERRED to Phase 5 GPU pod re-fire (CPU too slow at ~60-90 min per rung).
- LLM judges (OpenAI gpt-4o + Anthropic claude-sonnet-4-6). EXPLICITLY DROPPED for tonight per Round 2 Q1 (~$240 actual vs $14 estimate).
- val.parquet inference for trained rungs (would give both-class AUROC/AUPRC on val per cell). DEFERRED — covered by Phase 4 metrics-battery once OOD lands.

## Cost

$0 — all local CPU.

## Verification commands

```
ls evals/predictions/tfidf-lr__fold*__seed*.parquet | grep -vE "__notinject|__xstest|__jbb_behaviors|__bipia|__injecagent" | wc -l   # 12 (LODO)
ls evals/predictions/tfidf-lr__fold*__seed*__*.parquet | wc -l                                                                       # 60 (OOD)
ls evals/predictions/protectai-v1__*.parquet | wc -l                                                                                  # 9
ls evals/predictions/protectai-v2__*.parquet | wc -l                                                                                  # 9
```
