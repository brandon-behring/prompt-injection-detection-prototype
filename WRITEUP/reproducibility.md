---
title: "Reproducibility — three reproduction tiers"
description: "Documents the T0 + T1 + T3 reproducibility tier ladder per ADR-034."
---

# Reproducibility

*Part of the [WRITEUP methodology](../WRITEUP.md) — see the hub for the cover narrative + reading guide.*

> **How to read this spoke**: For a hiring-manager-level skim, focus on the bolded **Result** subsections + the final §Summary if present. For a full audit, read the methodology paragraphs + the ADR references in headers.

This submission documents three tiers of reproduction, ordered by cost. **Pick the tier matching your audit depth + budget.**

This spoke is referenced by `index.qmd`'s "Deep-dive path — reproduce the numbers" section.

---

## Tier coverage matrix

| Tier | Command | Cost | Time | Verifies | Does NOT verify |
|---|---|---|---|---|---|
| **T0** — eval-from-hub | `make eval-from-hub RUNG=<name>` | $0 (HF Hub bandwidth only) | ~10-30 min | Headline scores reproduce on the published checkpoint per [ADR-032](../decisions/ADR-032-hf-hub-publication-headline-rungs-only.md) | Data pipeline (no re-training); ablation rungs not in the published set |
| **T1** — smoke | `make smoke` | $0 | <10 min | Code health; fixture pipeline runs end-to-end per [ADR-027](../decisions/ADR-027-smoke-vs-canonical-execution-context-stratification.md) | Math correctness; real-data scoring; headline numbers |
| **T3** — headline-cloud | `make headline-cloud` | ~$125+ per [ADR-020](../decisions/ADR-020-compute-infrastructure-and-cost-discipline.md) cost cap | hours | Full retraining from scratch reproduces headline numbers within seed variance | (verifies everything in scope) |

---

## T0 — eval-from-hub (laptop, ~$0, ~10-30 min)

**Status (v1.0.1):** published rungs `frozen-probe` + `lora` per
ADR-032 + Q10 lock (canonical fold0/seed42 checkpoint per rung); HF
Hub repos go live at v1.0.1 close. Full-FT skipped per ADR-050
(FUSE EIO crash; weights missing locally).

**Result (Maintainer note v1.0.9):** the `scripts/eval_from_hub.py`
non-dry-run body is fully wired per ADR-058 (narrow supersession of
ADR-051 Block A). `make eval-from-hub RUNG=frozen-probe` + `RUNG=lora`
exit 0 with score-match summary within 1e-4 absolute tolerance per
ADR-034 §Tier T0. Per-row strict mode: exit 1 on any row exceeding tolerance
(no silent failures); per-row delta diagnostics printed to stderr on
fail. ADR-051 Block B (38 invariant scaffolds) remains carryforward
to v1.1.x.

```bash
make eval-from-hub RUNG=frozen-probe
make eval-from-hub RUNG=lora
```

What this does (per [ADR-034](../decisions/ADR-034-reproducibility-tier-full-ladder.md)):

1. Calls `huggingface_hub.snapshot_download` for
   `BBehring/prompt-injection-<rung>`.
2. Loads the model via `AutoModelForSequenceClassification.from_pretrained`
   (CPU; bf16 if CUDA available; otherwise fp32).
3. Runs scoring against the local val slate
   (`evals/predictions/<rung>__fold0__seed42__*.parquet`).
4. Emits per-row predictions to
   `evals/predictions/t0_eval_from_hub.parquet`.
5. Score-matches against `evals/results.json` headline metrics within
   1e-4 absolute tolerance (ADR-034 contract).
6. Exits non-zero if any headline metric drifts beyond tolerance.

**Full-FT note**: `make eval-from-hub RUNG=full-ft` is intentionally
unsupported — the canonical full-FT checkpoint was lost in a Phase 5
X11 FUSE EIO crash per ADR-050. The 3-rung LODO ladder narrative
survives via the 24 surviving Phase 2 LODO predictions in
`evals/predictions/full-ft__*.parquet`; OOD inference for full-FT is
methodologically impossible without a fresh 6-12 hour A100 80GB
re-fire and is out of scope for v1.0.0.

**Publishing**: maintainers refresh the published checkpoints via
`make publish-hub` (requires `HF_TOKEN` with write scope). See
`scripts/publish_to_hub.py` for the upload-folder pattern.

---

## T1 — smoke (laptop, ~$0, ~10 min)

**Status**: working at Phase 0-07 close (per [ADR-027](../decisions/ADR-027-smoke-vs-canonical-execution-context-stratification.md) — Makefile target exists).

```bash
make smoke
```

What this does:
- Runs `pytest -m smoke` + a fixture-data E2E pass through `scripts/run_metrics_battery.py` with `configs/profiles/fixtures.yaml`.
- Verifies code health — every import resolves, every entry-point runs, no schema mismatches.
- Does **NOT** verify math correctness (uses fixture data, not real data).
- Wall-clock < 10 minutes; no GPU; no network.

---

## T3 — headline-cloud (cloud-GPU, ~$125+, ~hours)

**Status (v1.0.1):** complete — verbatim commands below; RunPod
account + secrets bootstrap documented in
[`docs/REPRODUCIBILITY.md`](../docs/REPRODUCIBILITY.md). Cost-capped
per ADR-020.

```bash
# Pre-flight (free; no provisioning):
make headline-dry-run

# Canonical eval (billed; cost-capped per ADR-020):
make headline-cloud
```

What this does:
- Wraps `runpod-deploy validate --all` + `runpod-deploy run --dry-run` + `runpod-deploy run --config configs/runpod/headline.yaml`.
- Provisions H100 (or fallback per [ADR-020](../decisions/ADR-020-compute-infrastructure-and-cost-discipline.md) gpu_order ladder).
- Trains every rung from scratch + runs eval + emits per-row predictions + computes headline metrics.
- Hard cost-cap at $125 per job per [ADR-020](../decisions/ADR-020-compute-infrastructure-and-cost-discipline.md) `budget.cost_cap_usd` + project-wide $200 hard cap via `scripts/cost_rollup.py`.
- Wall-clock: hours.

---

## Why T2 (test-integration) is not a reviewer-facing tier

The Makefile per [ADR-027](../decisions/ADR-027-smoke-vs-canonical-execution-context-stratification.md) exposes a `make test-integration` target that uses `pytest.importorskip("torch")` + `pytest.mark.skipif(not torch.cuda.is_available())` for GPU-conditional skipping. T2 stays a **developer-tool tier** — not promoted to reviewer-facing — because:

1. Requires a local GPU the reviewer may not have.
2. Adds friction without enabling a new verification dimension — T0 covers eval; T3 covers full retraining; T2 only adds "subset eval on local GPU" which is strictly weaker than T3.

If a reviewer with a local GPU wants a mid-tier check, they may invoke `make test-integration` directly; the tier is documented for completeness but not part of the reviewer-facing ladder.

---

## ACM artifact-badging mapping

The tier ladder maps approximately onto [ACM Artifact Review and Badging (v1.1)](https://www.acm.org/publications/policies/artifact-review-and-badging-current) conventions:

- T0 + T1 supply *Artifacts Available* + *Functional* + *Reusable* badge levels.
- T3 supplies the *Reproducible* badge level (deepest).

**Result**: the tier ladder is recognizable to reviewers familiar with ACM artifact policies.

---

## Limitations + extension conditions

- **T0 reproduces headline scores only on the published rungs** (per [ADR-032](../decisions/ADR-032-hf-hub-publication-headline-rungs-only.md) Option C). Ablation-rung reproduction requires T3.
- **T0 verifies score-match against the published checkpoint, not data-pipeline correctness** — a reviewer who wants to verify the data preparation pipeline produces the same training tensors needs T3.
- **T3 is the only paid tier**; reviewer self-funds the RunPod cost.
- **HF Hub checkpoint SHA pinning**: if model card edits invalidate cached SHAs at Phase 5, pin SHAs in `make eval-from-hub` via `huggingface_hub.snapshot_download(revision=<SHA>)`. The HF dataset SHA-pinning discipline from [ADR-016](../decisions/ADR-016-data-design-bundle.md) carries over to model SHA-pinning.

## Cross-references

- **Methodology guarantees** (eval-toolkit + runpod-deploy + SDD discipline that backs T0/T1/T3) → [`methodology-guarantees.md`](./methodology-guarantees.md)
- **Headline results consumed by T0 score-match** → [`../WRITEUP.md`](../WRITEUP.md) §Results
- **Evaluation primitives + statistical apparatus** → [`eval-design.md`](./eval-design.md)
- **Model-rung publication scope** (canonical fold0/seed42 per ADR-032) → [`model-rungs.md`](./model-rungs.md)
- **Aggregator docs (Makefile targets + manifest schema)** → [`../docs/REPRODUCIBILITY.md`](../docs/REPRODUCIBILITY.md)

**Linked ADRs**: [ADR-027](../decisions/ADR-027-smoke-vs-canonical-execution-context-stratification.md) (Makefile execution-context stratification), [ADR-020](../decisions/ADR-020-compute-infrastructure-and-cost-discipline.md) (cost cap), [ADR-032](../decisions/ADR-032-hf-hub-publication-headline-rungs-only.md) (HF Hub publication), [ADR-034](../decisions/ADR-034-reproducibility-tier-full-ladder.md) (this spoke's source-of-truth ADR).
