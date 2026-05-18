---
adr_id: "034"
slug: reproducibility-tier-full-ladder
title: Reproducibility tier — full ladder T0 (eval-from-hub) plus T1 (smoke) plus T3 (headline-cloud)
date: 2026-05-16
status: Accepted
claim_id: CLAIM-034
claim: Phase 0-07 locks SPEC_GREENFIELD ledger row 350 (Reproducibility tier) at a layered three-tier reviewer-facing reproduction ladder (Option D of the Phase 0-07 Q4 walk) — T0 eval-from-hub (laptop; about 10-30 minutes; about zero dollars; downloads a published HF Hub checkpoint per ADR-032 and runs eval-only against fixture or held-out data; verifies headline scores reproduce without re-training) plus T1 smoke (laptop; about 10 minutes; about zero dollars; runs make smoke per ADR-027; verifies pipeline shape on fixture data; does NOT verify headline numbers — code health only) plus T3 headline-cloud (cloud-GPU; about hours; about 125 dollars per ADR-020; runs make headline-cloud; full re-training from scratch; verifies every step including training). T2 (make test-integration) stays a developer-tool tier — not promoted to reviewer-facing because it requires a local GPU the reviewer may not have and adds friction without enabling a new verification dimension (T0 covers eval; T3 covers full retraining; T2 only adds subset eval on local GPU which is strictly weaker than T3). The kit-level SPEC_GREENFIELD §6 line 249 lock — a stranger can clone install and reproduce headline numbers via documented commands — is operationally satisfied at T0 (cheapest highest-coverage for most reviewers) and stronger at T3 (full retraining). The smoke tier T1 is documented but framed as code-health-only not a math-correctness check. T0 is enabled by ADR-032 HF Hub publication; without published checkpoints T0 collapses and the reproducibility ladder reduces to T1 plus T3 only. T0 commands operationalize as make eval-from-hub (Phase 3 work item; about 30-50 lines of glue wrapping huggingface_hub.snapshot_download plus eval-toolkit scoring primitives plus per-row prediction emission) — accepts a rung name argument and downloads the corresponding BBehring/prompt-injection-modernbert-<rung> repo plus runs scoring against the eval data plus emits per-row predictions plus prints a score match table comparing against the committed results.json. The ladder maps approximately onto ACM artifact-review-and-badging conventions — T0 plus T1 supply Functional plus Reusable badge levels; T3 supplies the Reproducible badge level. WRITEUP/reproducibility.md spoke (slotted by ADR-031) documents the ladder with verbatim commands plus cost plus time plus what each tier verifies plus what each tier does NOT verify. Limitation — T0 reproduces headline scores only on the published rungs per ADR-032 Option C — ablation-rung reproduction requires T3; T0 verifies score-match against the published checkpoint not data-pipeline correctness — a reviewer who wants to verify the data preparation pipeline produces the same training tensors needs T3. Extension condition — if Phase 5 reveals T0 has correctness gaps (e.g., HF Hub checkpoint can drift due to model card edits invalidating cached SHAs), pin checkpoint SHAs in WRITEUP/reproducibility.md and make eval-from-hub via huggingface_hub.snapshot_download with the revision argument — the HF dataset SHA-pinning discipline from ADR-016 carries over to HF model SHA-pinning here; if a production-grade reproducibility scope extension lifts requirements (e.g., the writeup expands to include a deployment-grade claim), add T4 Docker-container-with-frozen-environment via superseding ADR (currently out-of-scope per ADR-005 plus ADR-027 prototype-grade framing).
source: SPEC_GREENFIELD.md §Submission ledger row 350 + SPEC_GREENFIELD §6 line 249 (kit-level reproducibility claim) + Phase 0-07 walk Q4
acceptance_criterion: SPEC_GREENFIELD ledger row 350 carries locked-to-full-ladder-T0-T1-T3 status (see ADR-034); WRITEUP/reproducibility.md spoke exists with at minimum a title plus a tier-ladder table stub (full content populated at Phase 5 — verbatim commands plus cost plus time plus what-verifies plus what-does-not-verify); Makefile has a make eval-from-hub target placeholder (Phase 3 implementation; can be a stub echo at Phase 0-07 close); tests/test_invariants.py contains skip-marked stub test_reproducibility_tier_documented asserting (1) WRITEUP/reproducibility.md exists; (2) the spoke contains all three tier names (T0 plus T1 plus T3) in section headers; (3) each tier has a verbatim command (make smoke plus make eval-from-hub plus make headline-cloud) in a code block; (4) Makefile contains all three target names (smoke plus eval-from-hub plus headline-cloud) as rules; SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit: 7979dc9
superseded_by:
  - ADR-051
references:
  - https://www.acm.org/publications/policies/artifact-review-and-badging-current
  - https://github.com/brandon-behring/runpod-deploy
  - https://github.com/brandon-behring/eval-toolkit
  - https://huggingface.co/docs/transformers/installation#offline-mode
  - decisions/ADR-027-smoke-vs-canonical-execution-context-stratification.md
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md
  - decisions/ADR-016-data-design-bundle.md
  - decisions/ADR-032-hf-hub-publication-headline-rungs-only.md
  - decisions/ADR-005-project-level-methodology-principles.md
transcript: transcripts/2026-05-16__phase-0-07__submission-deliverables.md
---

# ADR-034: Reproducibility tier — full ladder T0 + T1 + T3

## Status

Accepted (2026-05-16). Closes the fourth and final [OPEN] row in Phase 0-07 (§Submission — row 350). Companion to ADR-027 (Makefile execution-context stratification — provides T1 + T3 commands), ADR-030 (deliverable format — `WRITEUP/reproducibility.md` is a Quarto-rendered spoke), ADR-031 (reading paths — slots the spoke in the sidebar nav), and ADR-032 (HF Hub publication — enables T0).

## Context

SPEC_GREENFIELD §6 line 249 carries a kit-level pre-lock:

> `[LOCKED]` Reproducibility: a stranger can clone, install, and reproduce headline numbers via documented commands.

The kit-lock fixes the **claim** ("headline numbers reproducible") but not the **tier** at which that claim lives. Ledger row 350 picks the tier — laptop-only smoke / GPU-rental canonical / both.

ADR-027 already exposed three Makefile execution-context targets:
- `make smoke` (laptop; ~10 min; no GPU; no network; fixture data) — verifies *code structure*, NOT math correctness
- `make test-integration` (GPU-aware via `importorskip + skipif`; local OR cloud pre-flight) — verifies real-scorer / real-data paths
- `make headline-cloud` (canonical eval; NOT a test; cost-cap-gated per ADR-020) — produces the headline numbers

ADR-032 (Q2 publication = option C) adds a fourth reproduction path that didn't exist when ADR-027 was written:
- **Eval-from-HF-Hub** — `make eval-from-hub` (NEW, this ADR) downloads a published Phase-2-trained checkpoint and runs eval-only against fixture or full eval data. No re-training. Laptop-compatible if eval is CPU-feasible.

The operational reproducibility ladder has four tiers, not three:

| Tier | Command | Cost | Time | What it verifies |
|---|---|---|---|---|
| T0 — eval-from-hub | `make eval-from-hub` | $0 + HF Hub bandwidth | ~10-30 min | Headline scores reproduce on published checkpoint (verifies eval pipeline + checkpoint integrity) |
| T1 — smoke | `make smoke` | $0 | ~10 min | Code structure + fixture-pipeline runs end-to-end (verifies code health, NOT math) |
| T2 — test-integration (local-GPU) | `make test-integration` | $0 (own GPU) | varies | Real-scorer paths exercise; partial real-data run |
| T3 — headline-cloud | `make headline-cloud` | ~$125+ per ADR-020 | ~hours | Full headline-number reproduction from scratch via re-training |

Four options were considered (per Q4 walk):
- (A) Laptop-only smoke (T1 only) — narrows the kit-level claim; reviewer cannot verify scores.
- (B) GPU-rental canonical (T3 only) — gold-standard but $125+ barrier excludes most reviewers.
- (C) Both T1 + T3 — leaves T0 unused despite Q2 enabling it.
- (D) Full ladder T0 + T1 + T3 — maximizes reviewer-tier coverage given Q2's HF Hub publication.

User selection at Q4 walk: **D**.

## Decision

**Reproducibility tier ladder**: T0 + T1 + T3 (reviewer-facing). T2 stays a developer-tool tier (not promoted to reviewer-facing).

**Tier definitions** (locked):

| Tier | Command | Verifies | Does NOT verify | Cost | Time |
|---|---|---|---|---|---|
| **T0** | `make eval-from-hub RUNG=<name>` | Headline scores reproduce on the published checkpoint for the named rung. Eval pipeline integrity. Checkpoint download integrity (HF Hub SHA match). | Data-pipeline correctness (no training); ablation rungs not in published set. | $0 (HF Hub bandwidth only) | ~10-30 min (download + eval) |
| **T1** | `make smoke` | Code health; fixture-pipeline E2E shape. No imports broken; no schema mismatches. | Math correctness; real-data scoring; headline numbers. | $0 | <10 min |
| **T3** | `make headline-cloud` | Full retraining from scratch reproduces headline numbers within seed variance. Data pipeline + training + eval + threshold-fitting + bootstrap. | (verifies everything in scope) | ~$125+ per ADR-020 cost cap | hours |

**T2 (`make test-integration`)** stays a developer-tool tier. Not promoted to reviewer-facing because:
1. Requires a local GPU the reviewer may not have.
2. Adds friction without enabling a new verification dimension — T0 covers eval; T3 covers full retraining; T2 only adds "subset eval on local GPU" which is strictly weaker than T3.

**`make eval-from-hub` implementation** (Phase 3 work item):

```python
# scripts/eval_from_hub.py — ~30-50 LOC glue
# Accepts: RUNG=<rung-name> (e.g., modernbert-lora)
# Steps:
#   1. snapshot_download(f"BBehring/prompt-injection-{rung}", local_dir=...)
#   2. Load model via AutoModelForSequenceClassification.from_pretrained(local_dir)
#   3. Run scoring against configs/profiles/eval.yaml's data slate
#   4. Emit per-row predictions to results/predictions/eval-from-hub__<rung>.parquet
#   5. Print score-match table: this run's metrics vs results.json's metrics
#   6. Exit non-zero if any headline metric drifts beyond seed-variance tolerance
```

Tolerance for "score match": per-row prediction equality is too strict (different floating-point ordering can yield bit-level diffs); headline-metric match within ~1e-4 absolute is the practical bar.

**`WRITEUP/reproducibility.md`** spoke (slotted by ADR-031; full content at Phase 5) carries the tier-ladder documentation:

```markdown
# Reproducibility

This submission documents three tiers of reproduction, ordered by cost.

## T0 — eval-from-hub (laptop, ~$0, ~10-30 min)

Verifies: headline scores reproduce on the published checkpoint.
Does NOT verify: training pipeline (no re-training).

```bash
make eval-from-hub RUNG=modernbert-lora
```

## T1 — smoke (laptop, ~$0, ~10 min)

Verifies: code health; fixture pipeline runs.
Does NOT verify: headline numbers (uses fixture data).

```bash
make smoke
```

## T3 — headline-cloud (cloud-GPU, ~$125+, ~hours)

Verifies: full retraining from scratch reproduces headline numbers.

```bash
make headline-cloud
```

## Tier coverage matrix

| Tier | What you can audit | Recommended reader |
|---|---|---|
| T0 | "Are the published scores legit?" | Most reviewers |
| T1 | "Does the code run?" | Quick sanity check |
| T3 | "Does the training pipeline reproduce?" | Deep-audit reviewers |
```

**Mapping to ACM artifact badging** (https://www.acm.org/publications/policies/artifact-review-and-badging-current):
- T0 + T1 supply *Artifacts Available* + *Functional* + *Reusable* badges.
- T3 supplies the *Reproducible* badge (deepest level).

The badge vocabulary is standard in academic artifact-review; a reviewer familiar with ACM artifact policies will recognize the tier structure.

**Cost-cap discipline preserved**: T3 is the only paid tier; reviewer self-funds the RunPod cost per ADR-020 cap discipline. T0 + T1 cost only the reviewer's time.

## Consequences

### Positive

- **Maximum reviewer-tier coverage** given Q2's HF Hub publication — T0 was implicitly enabled by ADR-032 = C; this ADR makes it load-bearing rather than orphaned.
- **Honest tier ladder** — each tier explicitly verifies a different thing at different cost; reviewer picks the tier matching their interest + budget.
- **`make eval-from-hub` is a small Phase 3 work item** — ~30-50 LOC of glue; well-scoped.
- **Aligns with ACM artifact-badging convention** — reviewer-recognizable structure.
- **Honors kit-level §6 line 249 claim** — "headline numbers reproducible" satisfied at T0 (cheapest path); stronger guarantee at T3.
- **`WRITEUP/reproducibility.md` slot is justified** — ADR-031 reserved the spoke slot for exactly this content; tier-ladder documentation has a home rather than polluting WRITEUP.md proper.

### Negative / cost

- **Phase 3 work item added** — `make eval-from-hub` + `scripts/eval_from_hub.py` (~30-50 LOC). Acceptable; well-bounded.
- **`WRITEUP/reproducibility.md` content** — Phase 5 work item; tier-ladder table + commands + caveats. ~1-2 pages.
- **Three tiers vs two** — more documentation surface; reviewer must read the spoke to understand which tier suits their audit depth. Mitigation: tier-coverage matrix at top of spoke makes the choice obvious in <30 seconds.
- **HF Hub checkpoint drift risk** — if published model card is later edited, the cached SHA invalidates; T0 reproducibility fails silently. Mitigation: pin checkpoint SHAs in `make eval-from-hub` via `huggingface_hub.snapshot_download(revision=<SHA>)` once SHAs are known at Phase 5; for Phase 0-07 close, the unpinned default is acceptable since publication happens at v0.9.0-rc1 rehearsal.

### Neutral

- **T2 stays unchanged** — developer-tool tier per ADR-027; not promoted; not removed.
- **Cost-cap gating** preserved from ADR-020; no new cost surface introduced.
- **Tier renumbering risk** — T0/T1/T3 numbering skips T2 intentionally (T2 = developer-only). Reviewer who reads the spoke sees the skip and the explanation; not a presentation problem.

### Limitation

T0 reproduces headline scores only on the *published* rungs (per ADR-032 = C, the headline rungs only). Ablation-rung reproduction requires T3. This is an acceptable trade-off given Q2's disclosure-surface budget.

T0 verifies score-match against the published checkpoint, not data-pipeline correctness — if a reviewer wants to verify "the data preparation pipeline produces the same training tensors", they need T3. Documented in the spoke.

### Extension condition for revisit

- **HF Hub checkpoint SHA drift detected**: if Phase 5 (or post-submission) reveals that an HF Hub published checkpoint can drift due to model card edits invalidating cached SHAs, pin checkpoint SHAs in `WRITEUP/reproducibility.md` + `make eval-from-hub` via `huggingface_hub.snapshot_download(revision=<SHA>)`. HF dataset SHA-pinning discipline from ADR-016 carries over.
- **T4 Docker container**: if scope extends to a deployment-grade claim, add T4 Docker-container-with-frozen-environment via superseding ADR. Currently out-of-scope per ADR-005 + ADR-027 prototype-grade framing.
- **T0 correctness gap**: if Phase 5 reveals T0 produces scores that drift from results.json beyond seed-variance tolerance (e.g., due to non-deterministic kernels on a CPU eval host vs the GPU host that produced results.json), add a `T0-caveat` section to the reproducibility spoke documenting the gap + the expected drift magnitude.
- **T2 promotion**: if reviewer feedback signals "T2 (local-GPU integration) would be useful as a reviewer-facing tier" (e.g., a reviewer who has a local GPU and wants a mid-tier check), promote T2 via Phase 1+ superseding ADR.

## Alternatives Considered

- **(A) Laptop-only smoke (T1 only)** — narrows the kit-level reproducibility claim from "headline numbers" to "code health"; explicitly does NOT reproduce headline numbers. Rejected per Q4 walk; defeats the purpose of the kit-lock.
- **(B) GPU-rental canonical (T3 only)** — gold-standard but ~$125+ + RunPod account + secrets barrier; most reviewers will not pay this cost. Rejected per Q4 walk; loses the laptop-tier value entirely.
- **(C) Both T1 + T3** — leaves T0 (enabled by Q2) unused; throws away the highest-value reviewer-tier. Rejected per Q4 walk in favor of D.
- **Promote T2 to reviewer-facing** — adds friction (requires local GPU) without enabling a new verification dimension; strictly weaker than T3. Rejected.

## References

- ACM Artifact Review and Badging (v1.1) — https://www.acm.org/publications/policies/artifact-review-and-badging-current
- `runpod-deploy` reproduction patterns — https://github.com/brandon-behring/runpod-deploy
- `eval-toolkit` (scoring primitives) — https://github.com/brandon-behring/eval-toolkit
- HF Hub `AutoModel.from_pretrained` offline-eval — https://huggingface.co/docs/transformers/installation#offline-mode
- ADR-027 (Makefile execution-context stratification — provides T1 + T3 commands)
- ADR-020 (compute infrastructure + cost cap — T3 paid-tier discipline)
- ADR-016 (HF dataset SHA pinning — checkpoint SHA pinning discipline pattern)
- ADR-032 (HF Hub publication — enables T0; published rungs are what T0 downloads)
- ADR-005 (project-level methodology principles — prototype-grade framing rules out T4 currently)

## Transcript

See `transcripts/2026-05-16__phase-0-07__submission-deliverables.md` for the conversation that led to this decision (Q4 walk + option D selection).
