---
adr_id: 013
slug: kit-ratify-bulk-strictness-intake-notebook-persistence
title: Kit-ratify bulk — Phase 0 strictness, brief-intake protocol, notebook role and RunPod persistence
date: 2026-05-15
status: Accepted
claim_id: CLAIM-013
claim: Phase 0 strictness ratifies the kit default (all [OPEN] rows resolved before Phase 1); brief-intake protocol is live Phase 0-00 sub-session (kit default; transcript captured for ADR linkage); repo visibility is public from start (re-affirms ADR-003 from the kit-ratify frame); notebooks are jupytext-paired (kit default) with explicit illustrative-only role — GPU training runs are Python scripts, not notebook cells, and all RunPod-generated artifacts (per-row predictions, training manifests, checkpoints, logs, results JSON) are persisted to durable storage (local + HF Hub or S3-equivalent) before any pod is torn down.
source: SPEC_GREENFIELD.md §Kit-Ratify rows 365-368 + Q9 walk surfacing notebook-role and RunPod persistence
acceptance_criterion: Phase 1 cannot start until every [OPEN] ledger row is locked or explicitly deferred; the Phase 0-00 transcript references this ADR; notebooks in this repo contain no GPU-bound training code; before any RunPod pod is torn down, a pre-teardown persistence checklist is verified (per-row predictions present at evals/predictions/, training manifests present at training/runs/, eval results at evals/results.json, checkpoints pushed to HF Hub or downloaded locally).
closing_commit:
references:
  - https://jupytext.readthedocs.io/
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-013: Kit-ratify bulk — Phase 0 strictness, brief-intake protocol, notebook role and RunPod persistence

## Status

Accepted (2026-05-15)

## Context

The §Kit-Ratify rows (365-368) ask whether the project ratifies or overrides four kit-level defaults. Q6 (Phase 0 strictness), Q7 (brief-intake protocol), Q8 (repo visibility), and Q9 (notebook format) all ratified the kit defaults during Phase 0-00. Q8 was pre-resolved by ADR-003 (no separate ADR needed). Q6, Q7, and Q9 are bundled here as a "kit-ratify bulk" ADR for efficiency — they're cheap ratifications.

Q9 carried more substantive content than a simple ratification: Brandon clarified that notebooks have an **illustrative-only** role (GPU training runs are Python scripts; notebooks load precomputed artifacts and render results), and that **pre-teardown persistence discipline** is mandatory before any RunPod pod is destroyed. This adds workflow specifics that go beyond the kit's "jupytext-paired" lock.

## Decision

### Q6 — Phase 0 strictness: ratify kit default

All `[OPEN]` ledger rows must be locked-to-X (or explicitly deferred-to-phase-N) before Phase 1 starts. No high-med-only relaxation; no iterative-as-encountered relaxation. The discipline floor matches CLAUDE.md anti-pattern "Adding a methodology component without an ADR".

### Q7 — Brief-intake protocol: ratify kit default

Live Phase 0-00 sub-session. Brandon paste-or-verbally-summarized the brief during conversation; the transcript captures the walk; ADR-001..005 + ADR-006..013 lock the brief-level decisions. No pre-read; no async-issues decomposition.

### Q8 — Repository visibility: pre-resolved by ADR-003

Public from start. This ADR cross-references ADR-003 for the §Kit-Ratify row 367 entry; no new lock content.

### Q9 — Notebook format + role + RunPod persistence discipline

**Notebook format**: jupytext-paired (kit default; `pyproject.toml [tool.jupytext]` configured).

**Notebook role**: **illustrative-only**. Notebooks load precomputed artifacts (parquet, JSON, manifests) and render figures + tables. They do not perform GPU training runs. GPU training runs are Python scripts under `scripts/` (or runpod-deploy primitive invocations), shared in the repo for reproducibility but not embedded in notebook cells.

**Pre-teardown persistence discipline** (RunPod workflow):

Before any RunPod pod is torn down, the following artifacts must be persisted to durable storage:

| Artifact | Where | Rationale |
|---|---|---|
| Per-row predictions (parquet, per rung × seed × fold) | Local download (always) + HF Hub (optional) | Banned anti-pattern: "persisting only summary metrics without per-row predictions" — already mandated by CLAUDE.md |
| Training manifests (git SHA, seed, GPU info, env, hyperparams) | Local download + repo commit | Reproducibility floor; required for canonical re-run |
| Checkpoints (per rung, per seed) | HF Hub (`BBehring/<project>/<rung>` — repo name finalized Phase 0-07) | Required for any HF-Hub-published reference checkpoint; optional but recommended |
| Training/eval logs | Local download | Audit trail; not load-bearing but useful for post-hoc debug |
| `evals/results.json` (metrics summary, schema-validated) | Local download + repo commit | Headline metrics archive |

**Mid-run persistence**: a pod that crashes mid-run reverts the rung unless artifacts have been incrementally persisted. Phase 2 entry must verify the runpod-deploy primitives support incremental persistence (or wrap them).

This pre-resolves §Tech-Stack row 311 (Dataset cache location → local + HF Hub or S3-equivalent) and pre-shapes §Submission row 353 (HF Hub checkpoint publication → likely yes; specific repo and which rungs published finalized Phase 0-07).

## Consequences

**Positive:**

- All four §Kit-Ratify rows lock in one ADR — minimal paperwork for ratifications.
- Q9 specifics (notebook role + persistence) are surfaced as explicit project workflow rules rather than buried in process narratives.
- Pre-teardown persistence aligns the train-on-GPU / analyze-on-CPU split (per ADR-006) with concrete artifact-flow plumbing.
- Notebook illustrative-only role decouples human-readable result rendering from time-consuming training runs, matching ADR-009 process mandates.

**Negative / cost:**

- Pre-teardown persistence is a workflow rule that must be enforced operationally (no automated guard inside this repo for it). Mitigation: a manual `scripts/pre_teardown_check.sh` or equivalent that lists expected artifacts and reports missing ones; Phase 2 entry creates this.
- Incremental-persistence verification (Phase 2 entry) is real work; if runpod-deploy doesn't natively support it, wrapping cost is ~half a day.
- Assumption A-003 (severity: medium) added to assumptions.md: pre-teardown checklist enforcement; if a pod crashes mid-run before checklist verification, the rung is lost.

**Neutral:**

- Phase 0-08 still walks §Tech-Stack rows 309 (GPU class), 310 (Secrets management), 312-314 (library version pins), 315 (Python version pin — already at >=3.13 in pyproject.toml).

## Alternatives Considered

- **Override Q6 to "high-med severity only"**: Faster Phase 0 close. *Rejected* under ADR-005 Principle 1 (methodology > metrics; cutting Phase 0 corners contradicts the principle).
- **Override Q7 to pre-read protocol**: Skip live conversation; pre-load brief into a file. *Rejected* because the live-walk captures decision rationale in the transcript that pre-read protocols cannot.
- **Override Q9 to no notebooks / pure scripts**: Cleanest reproducibility. *Rejected* because notebooks are valuable for reviewer-facing result illustration; jupytext-paired solves the diff-friendliness concern.
- **Override Q9 to notebook-includes-GPU-training**: Self-contained reproducibility within a single artifact. *Rejected* because GPU training takes hours and is unfit for notebook cell execution; the split is cleaner.
- **No pre-teardown persistence checklist**: Rely on RunPod's native persistence. *Rejected* because RunPod pod loss (eviction, crash) is a real failure mode; explicit checklist is the discipline floor.

## References

- jupytext — https://jupytext.readthedocs.io/
- `pyproject.toml [tool.jupytext]` (this repo) — kit-default config
- `notebooks/README.md` — kit-provided notebook convention
- `docs/ROADMAP.md` §Phase 0 close criterion — Q6 reference
- ADR-003 (Q8 pre-resolved by repo-visibility lock)
- ADR-006 (local-CPU bootstrap workflow + per-row prediction persistence)
- ADR-009 (process mandates; notebook discipline reference)
- ADR-011 (Guarantee 5 — per-row predictions for seed transparency)
