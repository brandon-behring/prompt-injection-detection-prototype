---
adr_id: "049"
slug: gpu-order-priority-refresh-a100-80g
title: GPU failover ladder priority refresh — A100-SXM4-80GB to position 1 + US-WA-1/US-CA-2 datacenter additions + EU-RO-1 drop (frozen-probe + LoRA canonical; full-FT deferred to post-rehearsal)
date: 2026-05-17
status: Accepted
claim_id: CLAIM-049
claim: ADR-020 locks the GPU failover ladder set + tier structure + dual-layer cost cap discipline + BATCH_TABLE invariant. ADR-049 supersedes ONLY the gpu_order POSITION within the ladder (the SET is intact) plus the pod.datacenters list — both fall outside ADR-020's locked-by-ADR layer (the ladder set is locked; the order within a tier is a config detail). Live RunPod stock observation on 2026-05-17 00:30 UTC at Phase 4 close surfaced the operational reality that the configured priority (H100/H200 at positions 1-6) is dry across every datacenter probed — US-MD-1 had no H100/H200 stock (H200 NVL present but stock empty), EU-RO-1 had no Hopper SKUs in DC at all plus A100-80G stock empty, US-CA-2 had Hopper SKUs present but stock empty, CA-MTL-1 had H100 80GB HBM3 present but stock empty, EU-NL-1 had H100 80GB HBM3 present but stock empty. Only A100-SXM4-80GB at Low stock in US-MD-1 plus US-WA-1 is a provisionable target. Refreshed pod.gpu_order per ADR-049 reorders the existing ladder set to (1) NVIDIA A100-SXM4-80GB, (2) NVIDIA A100 80GB PCIe (T2 retained), (3-6) NVIDIA H100 80GB HBM3 plus H100 NVL plus H100 SXM plus H100 PCIe (T1 retained as later fallback in case mid-Phase-2 stock recovers), (7) NVIDIA H200, (8) NVIDIA H200 NVL, (9) NVIDIA L40S (T3 retained per ADR-020 flash-attn-fallback recipe), (10) NVIDIA A100-SXM4-40GB (T4 emergency retained). Refreshed pod.datacenters per ADR-049 reorders to [US-MD-1, US-WA-1, US-CA-2] — US-WA-1 added as second A100-SXM4-80GB candidate (currently Low stock; doubles provisioning success probability); US-CA-2 added as nominal fallback (A100-SXM4-80GB present but stock empty; recovery candidate); EU-RO-1 dropped (no A100-80G stock plus no Hopper SKUs in DC; dead weight in the failover chain). Per-rung scope — frozen-probe plus LoRA canonical runs fire under the refreshed configs (cap $40 + $60 per ADR-020 retained); full-FT canonical run DEFERRED to post-rehearsal per user direction 2026-05-17 — fires after v0.9.0-rc1 dress-rehearsal completes cleanly per ADR-033 + ADR-046 Q7, gated by a follow-up ADR superseding the defer status when fired. Rationale for defer — full-FT on A100-SXM4-80GB at 12 cells times approximately 30-60 min per cell equals 6-12 hours wall-time on a Low-stock GPU class is operationally fragile (mid-run preemption plus race-with-other-customers risk grows with wall-time); frozen-probe plus LoRA together fit approximately 4-8 hours wall plus approximately $13-25 actual cost (well under $100 combined cap); validates the pipeline end-to-end without exposing the longest-running rung to the highest-risk stock conditions. Operator follow-up after this ADR lands — refresh configs/runpod/headline-{frozen_probe, lora, full_ft}.yaml with the new gpu_order + datacenters (same change to all 3 so full-FT is ready when stock improves); `make headline-dry-run` should now validate cleanly with no all-configured-GPUs-Low-stock warning; operator fires `make headline-frozen-probe` then `make headline-lora` sequentially with interactive approval gates per ADR-020.
source: Phase 4 Commit 6 close + canonical-run plan walkthrough — /AskUserQuestion 3-question session 2026-05-17 (full-FT plan + ADR-049 scope + commit batching); user-locked Defer-to-post-rehearsal + Narrow-supersession + All-3-commits-now; live runpod-deploy gpu-list + validate output across 6 RunPod datacenters captured as the rationale for the position refresh
acceptance_criterion: decisions/ADR-049-gpu-order-priority-refresh-a100-80g.md exists at this path with Accepted status; SUBMISSION_AUDIT.md regenerates via scripts/regenerate_audit.py with ADR-049 included and ADR-020 marked superseded-in-part-by-049 on the gpu_order priority axis only; configs/runpod/headline-frozen_probe.yaml + configs/runpod/headline-lora.yaml + configs/runpod/headline-full_ft.yaml all refresh pod.gpu_order to (A100-SXM4-80GB first; A100 80GB PCIe second; H100/H200 family positions 3-8; L40S position 9; A100-SXM4-40GB position 10) and pod.datacenters to [US-MD-1, US-WA-1, US-CA-2]; runpod-deploy validate --config configs/runpod/headline-frozen_probe.yaml --all passes without the "all configured GPUs are Low stock" warning that fired pre-ADR-049 (validator reports A100-SXM4-80GB at Low stock as the matched candidate instead); docs/ROADMAP.md Phase 4 close note rehearsal-tag dispatch checklist amended to add a Step 7 explicitly noting that full-FT canonical run fires post-rehearsal only and requires a follow-up ADR superseding ADR-049's defer status when fired; decisions/library_imports.md runpod-deploy section unchanged (the primitives invoked are identical; only the config payload values change); CLAUDE.md anti-pattern "Mutating a locked decision without writing a superseding ADR" satisfied — this ADR is the explicit supersession trail for the position-order half of ADR-020 GPU failover ladder; the SET + TIER STRUCTURE + dual-layer cost cap discipline + BATCH_TABLE invariant from ADR-020 are unchanged + remain locked.
closing_commit:
supersedes:
superseded_by:
references:
  - decisions/ADR-019-lora-and-transformer-training-recipe.md
  - decisions/ADR-020-cost-cap-and-runpod-deploy.md
  - decisions/ADR-033-tag-discipline-and-publish-pipeline.md
  - decisions/ADR-044-phase-2-training-implementation-bundle.md
  - decisions/ADR-046-phase-4-analysis-implementation-bundle.md
  - decisions/library_imports.md
  - https://github.com/brandon-behring/runpod-deploy
  - https://www.runpod.io/pricing
transcript:
---

# ADR-049: GPU failover ladder priority refresh — A100-80G to position 1

## Status

Accepted (2026-05-17). Supersedes ADR-020 §"GPU failover ladder (pod.gpu_order)" ONLY on the position-order axis; the SET of GPU SKUs + the four-tier structure + dual-layer cost cap discipline + BATCH_TABLE invariant from ADR-020 are unchanged and remain locked.

## Context

ADR-020 locked the GPU failover ladder at Phase 0-03 with H100/H200 family as Tier 1 (positions 1-6), A100-80GB as Tier 2 (positions 7-8), L40S as Tier 3 (position 9), and A100-40GB as Tier 4 emergency (position 10). The 2-DC failover was `[US-MD-1, EU-RO-1]`. At the time of locking (2026-05-15) H100 spot availability on RunPod was assumed sufficient for the canonical Phase 2 runs.

At Phase 4 close (2026-05-17 00:30 UTC) the canonical-run readiness audit fired `runpod-deploy gpu-list --datacenter <DC> --no-prices` against 6 RunPod datacenters + `runpod-deploy validate --config configs/runpod/headline-frozen_probe.yaml --all`. Live findings:

**Hopper / H200 stock**:
- H100 80GB HBM3: present in CA-MTL-1, EU-NL-1, US-CA-2 — all `stockStatus=""` (unavailable)
- H100 NVL / SXM / PCIe: absent or unavailable across all probed DCs
- H200 / H200 NVL: H200 NVL present in US-MD-1 + US-CA-2, both `stockStatus=""`

**Ampere stock (the configured T2 fallback)**:
- A100-SXM4-80GB: US-MD-1 **Low**, US-WA-1 **Low**, US-CA-2 `""`, EU-RO-1 `""`
- A100 80GB PCIe: EU-RO-1 only (and `""`)

**L40S (T3)**: not in any DC I probed.

**Net**: validator output `"[gpu:US-MD-1] all configured GPUs are Low stock — provisioning may fail"` + `"[gpu:EU-RO-1] no configured GPU available"`. The configured priority (H100/H200 at positions 1-6) is aspirational — none of those SKUs would actually provision; the orchestrator would walk the ladder until it hit A100-SXM4-80GB at position 7 in US-MD-1, with a Low-stock warning.

User direction 2026-05-17 via 3-question `/AskUserQuestion` session:
1. Full-FT plan → **defer to post-rehearsal** (fire after `v0.9.0-rc1` dress-rehearsal passes cleanly; gated by follow-up ADR superseding ADR-049's defer status)
2. ADR-049 scope → **narrow** (gpu_order priority + datacenters only; keep ADR-020 tier set + cap discipline + BATCH_TABLE intact)
3. Commit batching → **all 3 commits now** (X1 torch CUDA pin + X2 ADR-049 + X3 runpod-deploy to dev extras)

## Decision

### Refreshed `pod.gpu_order` (all 3 headline-* configs)

The SET is unchanged from ADR-020; the order is repositioned to align with 2026-05-17 stock reality:

| Position | SKU | Tier per ADR-020 | Stock as-of |
|---|---|---|---|
| 1 | NVIDIA A100-SXM4-80GB | T2 | US-MD-1 Low, US-WA-1 Low |
| 2 | NVIDIA A100 80GB PCIe | T2 | nominal fallback (EU-RO-1 dropped) |
| 3 | NVIDIA H100 80GB HBM3 | T1 | mid-run stock-recovery fallback |
| 4 | NVIDIA H100 NVL | T1 | " |
| 5 | NVIDIA H100 SXM | T1 | " |
| 6 | NVIDIA H100 PCIe | T1 | " |
| 7 | NVIDIA H200 | T1 | " |
| 8 | NVIDIA H200 NVL | T1 | " |
| 9 | NVIDIA L40S | T3 | flash-attn-fallback per ADR-020 |
| 10 | NVIDIA A100-SXM4-40GB | T4 | emergency per ADR-020 |

T1 SKUs are kept in the ladder (positions 3-8) so that if RunPod stock recovers mid-Phase-2 the orchestrator naturally prefers them (the orchestrator re-runs `preflight.check_gpu_availability` per pod, not per Phase). The Tier structure from ADR-020 is intact; only the priority ordering moves.

### Refreshed `pod.datacenters` (all 3 headline-* configs)

`[US-MD-1, US-WA-1, US-CA-2]` (was `[US-MD-1, EU-RO-1]`)

- **US-MD-1** kept as primary (A100-SXM4-80GB at Low stock; matches ADR-020 default).
- **US-WA-1** added as secondary (A100-SXM4-80GB at Low stock; doubles provisioning success probability via DC-level failover).
- **US-CA-2** added as nominal fallback (A100-SXM4-80GB present in DC but currently stockStatus=""; serves as a recovery candidate if stock returns mid-Phase-2).
- **EU-RO-1 dropped** (no A100-80G stock; no Hopper SKUs in DC at all; dead weight in the failover chain that would force the orchestrator to probe + reject before falling through to the actually-viable DCs).

### Per-rung scope

| Rung | Canonical run this window? | Cap | Rationale |
|---|---|---|---|
| classical-floor | already runs locally | n/a | CPU-only per ADR-017; no GPU pod fires |
| frozen-probe | yes | $40 (unchanged) | cheapest GPU rung; ~1-2h wall on A100-80G; best canary |
| LoRA | yes | $60 (unchanged) | ~3-5h wall on A100-80G; intermediate-quality rung |
| **full-FT** | **DEFERRED to post-rehearsal** | $100 (unchanged) | ~6-12h wall on A100-80G; Low-stock + long-wall = mid-run preemption risk; fires after v0.9.0-rc1 dress-rehearsal passes cleanly per ADR-046 Q7 + ADR-033 |

The full-FT defer is documented in `docs/ROADMAP.md` Phase 4 close note rehearsal-tag dispatch checklist (new Step 7); a follow-up ADR will supersede ADR-049's defer status when full-FT actually fires.

### What ADR-020 retains (unchanged)

- The SET of 10 GPU SKUs in the ladder.
- The 4-tier structure (T1 80GB+bf16+flash-attn-2-native, T2 80GB+bf16+flash-attn-2-native+~50% H100 throughput, T3 48GB+bf16+flash-attn-fallback, T4 40GB+bf16+may-need-fallback).
- Adaptive batch sizing per BATCH_TABLE keyed on detected GPU class (ADR-020 §"Adaptive batch sizing").
- Effective batch invariant (32) preserved across all GPU classes.
- flash-attn-2 fallback recipe in `src/training/load_modernbert.py`.
- Dual-layer cost cap discipline ($40/$60/$100 per-pod via `budget.cost_cap_usd`; $200 total via `scripts/cost_rollup.py --check`).
- `assumed_hourly_rate_usd: 3.50` (still a reasonable Ampere/Hopper midpoint).
- Preflight discipline (`runpod-deploy validate --all` + `runpod-deploy run --dry-run` before any billed run).
- All cost-tracking primitives + per-pod manifest capture + soft/hard cap thresholds + escalation policy.

## Consequences

**Positive:**

- `runpod-deploy validate --all` now reports A100-SXM4-80GB at Low stock as the matched candidate instead of the misleading `"all configured GPUs are Low stock — provisioning may fail"` warning that fired pre-ADR-049.
- Operator fires frozen-probe + LoRA with the actual provisionable GPU class as the priority candidate, not a phantom H100/H200 priority that wouldn't provision.
- Datacenter expansion to 3 DCs (from 2) increases mid-run preemption resilience for the canonical runs.
- T1 SKUs kept in the ladder mean future stock recovery is captured automatically without another ADR refresh.
- Tier structure + cap discipline + BATCH_TABLE invariant from ADR-020 are unchanged — the methodology contract is preserved.

**Negative / cost:**

- Full-FT defer means Phase 5 WRITEUP draft (which begins post-rehearsal) cannot include full-FT numbers in the rehearsal-tag rendering; rehearsal site renders an incomplete 3-rung comparison.
- If full-FT exposes pipeline issues that frozen-probe + LoRA did not, the fix-forward cycle pushes v1.0.0 tag by one rc bump.
- Adding US-CA-2 as a fallback DC adds preflight latency to every `runpod-deploy validate` call (one extra DC stock-check round-trip) — sub-second cost; not a real penalty.

**Neutral:**

- ADR-020 stays Accepted (not Superseded) since the SET + TIER STRUCTURE + cap discipline are unchanged; SUBMISSION_AUDIT.md notes ADR-049 as "supersedes-in-part" on the priority-order axis only.
- No code changes required in `src/training/load_modernbert.py` or `src/training/batch_table.py` since those depend on the SET + TIER STRUCTURE (unchanged), not on the order.

## Alternatives Considered

- **Broad failover refresh** (add Blackwell SKUs: B200, B300 SXM6 AC, RTX PRO 6000 Blackwell {Server, Workstation}; add consumer fallback RTX 5090/4090). *Rejected per user direction Q2*: out of scope for the immediate canonical run. May fire as a separate ADR-050 if full-FT post-rehearsal needs more provisioning options.
- **Keep ADR-020 priority + accept the "all configured GPUs are Low stock" warning + fire anyway**. *Rejected*: misleading validator output erodes the audit trail; the warning would surface in every CI run + every operator preflight.
- **Cut full-FT from submission entirely** (3-rung ladder in Phase 5). *Rejected per user direction Q1*: the LoRA-vs-full-FT comparison is a load-bearing narrative element of ADR-019 + the writeup.
- **Pre-provision a reserved A100-SXM4-80GB pod ahead of the canonical run** (skip the orchestrator's failover chain). *Rejected*: violates the runpod-deploy library-first discipline per ADR-020; the failover chain IS the resilience mechanism.

## References

- `decisions/ADR-019-lora-and-transformer-training-recipe.md` — 4-rung training recipe (classical-floor + frozen-probe + LoRA + full-FT)
- `decisions/ADR-020-cost-cap-and-runpod-deploy.md` — ADR being partially superseded (gpu_order priority axis only)
- `decisions/ADR-033-tag-discipline-and-publish-pipeline.md` — v0.9.0-rc1 rehearsal-tag dispatch + fix-forward via rc2 if rehearsal exposes issues
- `decisions/ADR-044-phase-2-training-implementation-bundle.md` — Phase 2 implementation bundle (per-rung orchestration Q6)
- `decisions/ADR-046-phase-4-analysis-implementation-bundle.md` — Phase 4 implementation bundle (Q7 phase-tailoring lock that gates Phase 5 entry on rehearsal)
- `decisions/library_imports.md` — runpod-deploy primitives invoked (unchanged by this ADR)

## Transcript

This ADR has no dedicated transcript file. The decision was made via a 3-question `/AskUserQuestion` session on 2026-05-17 in the same conversation that produced the Phase 4 Commits 2-6 implementation (transcript `transcripts/2026-05-17__phase-4-commits-2-through-6-implementation.md` captures the Q&A + the ADR-049 + X1 + X3 commit sequence).
