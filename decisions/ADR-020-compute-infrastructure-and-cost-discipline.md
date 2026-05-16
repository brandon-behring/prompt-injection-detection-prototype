---
adr_id: 020
slug: compute-infrastructure-and-cost-discipline
title: Compute infrastructure and cost discipline — runpod-deploy 0.7.7 primitives, GPU failover, adaptive batch sizing, dual-layer cost tracking
date: 2026-05-15
status: Accepted
claim_id: CLAIM-020
claim: Phase 0-03 locks the compute infrastructure plus cost discipline by adopting runpod-deploy 0.7.7 primitives end-to-end rather than hand-rolling equivalents (per the library-first discipline from CLAUDE.md). GPU class lock (ledger row 338) is an eight-class failover ladder via pod.gpu_order in priority order — NVIDIA H100 80GB HBM3 plus NVIDIA H100 NVL plus NVIDIA H100 SXM plus NVIDIA H100 PCIe plus NVIDIA H200 plus NVIDIA H200 NVL (tier 1 — 80GB plus bf16 native plus flash-attention-2 native) then NVIDIA A100-SXM4-80GB plus NVIDIA A100 80GB PCIe (tier 2 — 80GB plus bf16 native plus flash-attention-2 native plus ~50 percent H100 throughput) then NVIDIA L40S (tier 3 — 48GB plus bf16 native plus flash-attention-2 with fallback) then NVIDIA A100-SXM4-40GB (emergency tier 4 — 40GB plus bf16 OK plus may need flash-attention fallback). Datacenter failover via pod.datacenters set to US-MD-1 plus EU-RO-1 (dual-DC capacity resilience). Adaptive batch sizing preserves the ADR-019 effective batch equals 32 invariant across all GPU classes by scaling per_device_train_batch_size plus gradient_accumulation_steps together through a pre-locked BATCH_TABLE lookup keyed on detected GPU class — H100 plus H200 plus A100-80G use per_device 16 with grad_accum 2 (matches ADR-019 H100 default); A100-40G plus L40S use per_device 8 with grad_accum 4; L40 uses per_device 4 with grad_accum 8. This is NOT hyperparameter tuning (the effective batch — the actual gradient-computation hyperparameter — is held constant at 32 across all GPU classes); per_device plus grad_accum are throughput knobs that do not change the gradient computation; preserves SPEC §2 hyperparameter-immutability invariant. flash_attention_2 fallback per the runpod-deploy flash-attention-fallback recipe — model load wraps AutoModelForSequenceClassification.from_pretrained in try/except (ValueError, ImportError) catching the unsupported case on smaller GPU classes and degrading to stock SDPA without failing; per-run manifest logs which attn_impl was used so the audit trail is preserved (events.emit_event flash_attn_fallback when degraded). Cost cap is dual-layer — runpod-deploy budget.cost_cap_usd equals 125.0 enforced per-job by the orchestrator (matches A-002 upper-bound soft cap; matches A-002 envelope; one bad pod cannot exceed this without orchestrator-level intervention) plus a project-wide hard cap of 200 dollars enforced by scripts/cost_rollup.py CI-gated check aggregating across all per-pod runpod_deploy_pull_manifest.json files plus API call logs (LLM-judge gpt-4o plus claude-sonnet-4-6 spend tracked separately since API costs bypass runpod-deploy). assumed_hourly_rate_usd equals 3.50 set as H100 spot midpoint estimate (per runpod-deploy cost-reconciliation recipe, reconciled after first run by comparing manifest gpu_price_per_hour_usd to assumed rate; if actual differs materially the rate is bumped in subsequent config or split per GPU class). Preflight discipline mandates runpod-deploy validate --all (config schema plus DC reachability plus GPU stock check) plus runpod-deploy run --dry-run (cost preview without provisioning) before any billed run. Cost tracking is dual-layer — per-pod automatic via runpod_deploy_pull_manifest.json (captures wall_time_sec plus gpu_id plus gpu_price_per_hour_usd plus gpu_price_source plus estimated_cost_usd plus pod_final_state automatically; no code required) plus per-Makefile-target rolled up via evals/cost_ledger.csv (scripts/cost_rollup.py walks artifacts/runpod/star/runpod_deploy_pull_manifest.json plus API call logs and emits a timestamped per-target row with est_cost_usd plus actual_cost_usd plus gpu_hours plus api_calls plus notes). Soft-cap trigger threshold equals 80 dollars cumulative spend flags for review before next major run; soft-cap breach equals 125 dollars cumulative requires escalation discussion documented in evals/cost_decisions.md before further spend; hard-cap breach equals 200 dollars cumulative requires a superseding ADR documenting extension rationale before any further GPU or API spend.
source: SPEC_GREENFIELD.md §2 Model ledger row 338 + SPEC_GREENFIELD §Tech-Stack + Phase 0-03 walk Q8
acceptance_criterion: SPEC_GREENFIELD ledger row 338 carries locked-to-runpod-deploy-0.7.7-gpu-failover-plus-adaptive-batch-plus-dual-layer-cost-tracking (see ADR-020) status; SPEC_SHEET §4 compute section is populated with the 8-class gpu_order plus dual-DC failover plus the BATCH_TABLE specification plus the flash-attn-2 fallback policy plus the dual-layer cost-cap policy; configs/runpod/headline.yaml is the Phase 1 deliverable carrying the locked pod.gpu_order plus pod.datacenters plus budget.cost_cap_usd plus budget.assumed_hourly_rate_usd plus budget.poll_interval_sec configuration; src/training/batch_table.py is the Phase 1 deliverable implementing the pre-locked BATCH_TABLE keyed on torch.cuda.get_device_name with explicit KeyError handling (fails loudly with add this GPU class to BATCH_TABLE message rather than silently defaulting); src/training/load_modernbert.py implements the flash-attn-2 fallback recipe via try/except (ValueError, ImportError); scripts/cost_rollup.py is the Phase 1 deliverable aggregating per-pod manifests plus API call logs into evals/cost_ledger.csv with CI hard-gate on cumulative spend above 200 dollars hard-cap; tests/test_invariants.py contains skip-marked stubs test_flash_attn_fallback_present and test_effective_batch_constant_across_gpu_classes; decisions/library_imports.md runpod-deploy section is populated with the eight primitives invoked (runpod-deploy validate --all plus runpod-deploy run --dry-run plus runpod-deploy run plus runpod-deploy logs plus runpod-deploy stop plus runpod-deploy manifest-summary plus the pod.gpu_order schema plus the budget.cost_cap_usd schema plus the preflight.check_gpu_availability internal primitive plus the flash-attn-fallback recipe pattern plus the cost-reconciliation recipe pattern); evals/cost_ledger.csv schema documented with the seven columns (timestamp plus target plus est_cost_usd plus actual_cost_usd plus gpu_hours plus api_calls plus notes).
closing_commit:
supersedes:
references:
  - https://github.com/brandon-behring/runpod-deploy
  - https://www.runpod.io/pricing
  - https://resources.nvidia.com/en-us-tensor-core/nvidia-tensor-core-gpu-datasheet
  - https://openai.com/api/pricing/
  - https://docs.anthropic.com/en/docs/about-claude/models
  - https://huggingface.co/docs/transformers/main_classes/trainer
  - decisions/ADR-001-submission-deadline-and-scope-ambition.md
  - decisions/ADR-013-kit-ratify-bulk-strictness-intake-notebook-persistence.md
  - decisions/ADR-019-lora-and-transformer-training-recipe.md
transcript: transcripts/2026-05-15__phase-0-03__model-scope.md
---

# ADR-020: Compute infrastructure and cost discipline

## Status

Accepted (2026-05-15). Concretizes A-001 (runpod-deploy infrastructure assumption) and A-002 (compute budget envelope) into specific runpod-deploy 0.7.7 configuration. Complements ADR-013 (pre-teardown persistence checklist) and ADR-019 (training recipe).

## Context

A-001 originally framed runpod-deploy as the GPU-rental orchestration substrate; A-002 framed the budget at $25-$125 envelope. Phase 0-03 Q8 concretized both into a specific runpod-deploy 0.7.7 configuration.

Brandon's Phase 0-03 Q8 surfaced two concerns that the original ADR-001 plus A-002 framing did not address.

First, H100 availability fluctuates on RunPod spot — pinning to a single GPU class risks unavailability mid-Phase-2. The runpod-deploy primitive pod.gpu_order is an ordered failover list — runpod-deploy walks the list until it finds an available GPU. The 8-class failover ladder ensures we get a usable GPU even under H100 stockout.

Second, batch sizing must adapt to whatever GPU class the failover ladder lands us on. Naive single-batch-config approach risks OOM on smaller-VRAM classes (A100 40GB, L40S 48GB, L40 24GB). The methodology-aligned move is to preserve the ADR-019 effective batch invariant (32) while scaling per_device plus grad_accum together — preserves the gradient-computation hyperparameter (effective batch) while adapting throughput to memory.

Brandon also flagged that we should leverage the runpod-deploy primitives rather than hand-rolling equivalents. The Phase 0-03 walk inspected the runpod-deploy 0.7.7 source plus recipes plus reference configs and confirmed — gpu_order failover plus datacenter failover plus budget.cost_cap_usd plus preflight.check_gpu_availability plus flash-attention-fallback recipe plus cost-reconciliation recipe plus per-pod manifest capture all exist as documented primitives. The library-first discipline from CLAUDE.md plus SPEC §Tech-Stack means we invoke these primitives correctly rather than rebuild them.

## Decision

### GPU failover ladder (pod.gpu_order)

Tier 1 — 80GB, bf16 native, flash-attention-2 native — H100 family plus H200 family.
- NVIDIA H100 80GB HBM3
- NVIDIA H100 NVL
- NVIDIA H100 SXM
- NVIDIA H100 PCIe
- NVIDIA H200
- NVIDIA H200 NVL

Tier 2 — 80GB, bf16 native, flash-attention-2 native, ~50% H100 throughput — A100 80GB.
- NVIDIA A100-SXM4-80GB
- NVIDIA A100 80GB PCIe

Tier 3 — 48GB, bf16 native, flash-attention-2 with fallback — L40S.
- NVIDIA L40S

Tier 4 (emergency fallback) — 40GB, bf16 OK, may need flash-attn fallback.
- NVIDIA A100-SXM4-40GB

Avoid (no bf16, V100 / Pascal / Turing) plus avoid (too small for max_len=8192 batch — RTX 4000 / A4000 24GB).

### Datacenter failover (pod.datacenters)

[US-MD-1, EU-RO-1] — dual-DC capacity resilience matching the prompt-injection-v3 reference config plus the runpod-deploy config-reference.md documented pattern.

### Adaptive batch sizing (BATCH_TABLE)

Pre-locked lookup table keyed on detected GPU class (torch.cuda.get_device_name) preserving effective batch equals 32 across all classes.

```python
BATCH_TABLE = {
    "H100":     {"per_device": 16, "grad_accum": 2},
    "H200":     {"per_device": 16, "grad_accum": 2},
    "A100-80G": {"per_device": 16, "grad_accum": 2},
    "A100-40G": {"per_device":  8, "grad_accum": 4},
    "L40S":     {"per_device":  8, "grad_accum": 4},
    "L40":      {"per_device":  4, "grad_accum": 8},
}

gpu_name = torch.cuda.get_device_name(0)
gpu_class = classify_gpu(gpu_name)  # maps device name -> table key
try:
    cfg = BATCH_TABLE[gpu_class]
except KeyError:
    raise RuntimeError(
        f"GPU class {gpu_class!r} not in BATCH_TABLE; add explicit entry"
        f" (gpu_name={gpu_name!r})"
    )
```

NOT hyperparameter tuning — effective batch (the actual gradient-computation hyperparameter) is held constant at 32 across all GPU classes; per_device + grad_accum are throughput knobs that do not change the gradient computation. Preserves SPEC §2 hyperparameter-immutability invariant.

If runpod-deploy lands us on an unlisted GPU (e.g., a new H300 class), the script fails loudly rather than silently defaulting — add explicit BATCH_TABLE entry plus update this ADR via superseding ADR if needed.

### flash_attention_2 fallback (per runpod-deploy recipe)

```python
import torch
from transformers import AutoModelForSequenceClassification

try:
    model = AutoModelForSequenceClassification.from_pretrained(
        "answerdotai/ModernBERT-base",
        revision=SHA_PIN,  # per ADR-016 + ADR-018 manifest
        attn_implementation="flash_attention_2",
        torch_dtype=torch.bfloat16,
        num_labels=2,
    )
except (ValueError, ImportError):
    model = AutoModelForSequenceClassification.from_pretrained(
        "answerdotai/ModernBERT-base",
        revision=SHA_PIN,
        torch_dtype=torch.bfloat16,
        num_labels=2,
    )
    # Log fallback via runpod-deploy events.emit_event so audit trail captures
    # which physical config produced each per-row prediction
    log_event("flash_attn_fallback", gpu=torch.cuda.get_device_name(0))
```

### Cost cap (dual-layer)

Layer 1 — per-job orchestrator enforcement.

```yaml
budget:
  cost_cap_usd: 125.0                # = A-002 soft cap; one bad pod cannot exceed
  assumed_hourly_rate_usd: 3.50      # H100 spot midpoint; reconciled post-first-run
  poll_interval_sec: 60
```

Layer 2 — project-wide hard cap (CI-gated, ledger-driven).

```bash
# scripts/cost_rollup.py walks artifacts/runpod/*/runpod_deploy_pull_manifest.json
# plus API call logs and emits evals/cost_ledger.csv with cumulative spend
# Fails CI if cumulative > $200
```

Cost ledger schema — evals/cost_ledger.csv columns — timestamp, target, est_cost_usd, actual_cost_usd, gpu_hours, api_calls, notes.

Trigger thresholds — cumulative $80 (~64% of soft cap) flags for review; cumulative $125 (soft cap) escalation discussion documented in evals/cost_decisions.md; cumulative $200 (hard cap) STOP plus superseding ADR required.

### Preflight discipline

Before any billed run:

```bash
runpod-deploy validate --config configs/runpod/headline.yaml --all
runpod-deploy run --config configs/runpod/headline.yaml --dry-run
```

`validate --all` runs schema validation plus DC reachability plus GPU stock check. `run --dry-run` hits runpodctl + GraphQL pricing without provisioning anything; tells us "would this find a GPU at this price right now?"

### Library imports ledger update

decisions/library_imports.md runpod-deploy section populated with eight primitives we invoke.

## Consequences

### Positive

- Library-first discipline preserved — runpod-deploy primitives invoked end-to-end; no hand-rolled GPU orchestration or cost tracking
- GPU availability handled by orchestrator failover; no project code required to handle H100 stockouts
- Adaptive batch sizing preserves the ADR-019 effective-batch invariant across all GPU classes — methodology integrity preserved under GPU substitution
- flash_attention_2 fallback handles cross-GPU-class portability without code failure on smaller GPUs
- Dual-layer cost cap — per-job orchestrator enforcement plus project-wide CI-gated rollup — prevents both single-pod runaway cost AND cumulative drift
- Per-pod cost reconciliation is automatic via the runpod-deploy manifest schema; no extra code
- assumed_hourly_rate_usd reconciliation pattern (per cost-reconciliation recipe) tunes the implicit timeout after first run

### Negative

- The 8-class failover ladder means we may land on slower hardware than H100; wall-clock may extend up to ~2x on A100 80GB or L40S; still inside the cost cap because spot pricing is correspondingly lower
- Adaptive batch sizing adds modest code complexity (BATCH_TABLE lookup plus GPU classifier function); manageable
- Per-GPU-class throughput varies — for cross-rung wall-clock comparison reporting, the GPU class is captured in per-pod manifest as a confounder to acknowledge in the methodology spoke
- A new GPU class outside the BATCH_TABLE causes fail-loud (intended); requires a superseding ADR if we want to extend the table without a full Phase 0 cycle
- assumed_hourly_rate_usd=$3.50 is an estimate; if actual H100 spot averages much higher (e.g., $4.50), the implicit timeout (cost_cap / assumed_rate) shrinks; reconciliation after first run catches this

### Phase 1 deliverables

- configs/runpod/headline.yaml — locked pod.gpu_order + pod.datacenters + budget
- src/training/batch_table.py — BATCH_TABLE + classify_gpu + fail-loud KeyError
- src/training/load_modernbert.py — flash-attn-2 with SDPA fallback
- scripts/cost_rollup.py — per-pod manifest aggregation plus CI hard-cap gate
- evals/cost_ledger.csv — populated per Makefile-target invocation
- decisions/library_imports.md — runpod-deploy section populated with eight primitives

## Alternatives considered

- **Single GPU class (H100 only)** — rejected because H100 spot availability fluctuates; pinning to a single class risks unavailability mid-Phase-2. The 8-class failover is the runpod-deploy idiom and handles stockouts transparently.
- **Single datacenter (US-MD-1 only)** — rejected for the same reason; dual-DC failover is the runpod-deploy idiom plus the prompt-injection-v3 reference config pattern.
- **auto_find_batch_size=True via HF Trainer** — rejected because adds nondeterminism (binary search varies per run) plus ~30 second warmup per run. Pre-locked BATCH_TABLE is deterministic plus auditable.
- **GPU class as a config parameter (split into per-GPU-class configs)** — rejected because proliferates configs (one per GPU class times one per rung); the runtime-detected approach is simpler and matches runpod-deploy's failover semantics.
- **flash_attention_2 required (fail-loud on unsupported)** — rejected because the failover ladder may legitimately land us on smaller GPUs without flash-attn-2 support; the recipe's degrade-to-SDPA pattern is the runpod-deploy idiom for this case.
- **Single-layer cost cap (orchestrator-only via budget.cost_cap_usd)** — rejected because budget.cost_cap_usd is per-pod enforcement; without the project-wide rollup, cumulative spend across many pods could drift above the A-002 envelope. The dual-layer approach handles both runaway-pod and cumulative-drift cases.
- **Hand-rolled GPU orchestration** — rejected per CLAUDE.md library-first discipline; runpod-deploy 0.7.7 has all the primitives we need.

## References

See frontmatter references list. Primary anchors — runpod-deploy 0.7.7 source at brandon-behring/runpod-deploy GitHub (locally cloned at /home/brandon_behring/Claude/runpod-deploy); RunPod pricing page; NVIDIA H100 tensor-core whitepaper; OpenAI pricing; Anthropic model card pricing; HuggingFace TrainingArguments docs; ADR-001 deadline-plus-scope-ambition framing; ADR-013 pre-teardown persistence checklist; ADR-019 training recipe for batch-size context.
