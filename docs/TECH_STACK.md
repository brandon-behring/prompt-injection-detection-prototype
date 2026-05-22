# Tech Stack

> **Public-site note.** This is one part of the historical project
> Constitution. It documents the library-first stack and process constraints,
> not the headline results.

This file is the Tech-Stack portion of the project Constitution (alongside `MISSION.md` and `ROADMAP.md`). Each component listed here is locked in as the default; substitution is possible but requires an ADR explaining the swap.

## Load-bearing libraries

- **Modelling repo** (this repo) — data loading, training, classification API, project-specific scoring code.
- **[eval-toolkit](https://github.com/brandon-behring/eval-toolkit)** — methodology-aware evaluation harness for binary classification. Provides bootstrap CIs, paired-bootstrap differences, MDE, calibration battery, threshold-selector protocol, leakage detection, slice-aware orchestration, versioned JSON schemas, and methodology notes referenced from the [eval-toolkit README](https://github.com/brandon-behring/eval-toolkit#readme). The eval-toolkit's methodology surface is the canonical reference for *why* each methodology choice in this spec exists.
- **[runpod-deploy](https://github.com/brandon-behring/runpod-deploy)** — cloud orchestration for training and evaluation runs on rented GPUs. Captures NeurIPS-aligned reproducibility manifests (seeds, git SHA, data hashes, GPU info).
- **[research_toolkit](https://github.com/brandon-behring/research_toolkit)** — dossier production pipeline. Produces verified, dual-audience research dossiers (paper synthesis + dataset discovery) via the skill chain: `/research-plan` → `/research-gather` → `/dossier-build` → `/agent-index` → `/dossier-audit` + `/url-freshness-check`. The literature dossier at `docs/research/` was produced by this toolkit; regenerable by re-running its skills.
- **Claude Code (or equivalent agent)** — SDD partner. Reads the spec, asks clarifying questions in Phase 0, drafts code, captures transcripts of decision conversations.

## Library-first discipline — anti-hand-rolling

`[LOCKED]` Use `eval-toolkit`, `runpod-deploy`, and `research_toolkit` primitives instead of writing equivalent code in this repo. The rule bans replacing library primitives, not all local code — project-specific glue (data loaders, custom scorers using upstream primitives, project-named CLIs) is allowed and expected. The rule applies when a function you're about to write is a generic primitive an upstream library should provide. Track every import / skill invocation in `decisions/library_imports.md`.

## Upstream-issue triage protocol

`[LOCKED]` Every discovered library gap, bug, or feature request is filed to the relevant upstream GitHub repo (`brandon-behring/eval-toolkit`, `brandon-behring/runpod-deploy`, or `brandon-behring/research_toolkit`) with the `tracked` label before any local workaround is written. Filed issue numbers are recorded in `decisions/upstream_issues.md` so reviewers can audit the contribution trail.

## GPU class, secrets, cache

`[LOCKED]` Per Phase 0-03 + Phase 0-08 close.

- **GPU class** — 8-tier failover ladder via `pod.gpu_order` per [ADR-020](../decisions/ADR-020-compute-infrastructure-and-cost-discipline.md): H100 / H200 family (tier 1), A100-80G (tier 2), L40S (tier 3), A100-40G (tier 4). Dual-DC failover (`US-MD-1` + `EU-RO-1`). Adaptive batch sizing via `src/training/batch_table.py` preserves `effective_batch = 32` across all GPU classes.
- **Secrets management** — three-store split per [ADR-035](../decisions/ADR-035-secrets-management-three-store-split.md): committed `.env.example` template (placeholder values) + local-only `.env.local` (gitignored) for non-CI work + GitHub Actions Secrets for CI. HF token + RunPod API key + any LLM-judge keys never committed.
- **Dataset cache** — HF default cache at `~/.cache/huggingface/` plus project-local `data/raw/` + `data/processed/` (both gitignored) per [ADR-016](../decisions/ADR-016-data-design-bundle.md) + [ADR-026](../decisions/ADR-026-module-layout-concern-grouped-subpackages.md). `HF_HOME` can override; CI uses an ephemeral cache.
- **Transcripts** — `transcripts/*.md` private-by-default (gitignored; only `transcripts/README.md` tracked).
- **Upstream issues** — filed to GitHub against `brandon-behring/eval-toolkit`, `brandon-behring/runpod-deploy`, `brandon-behring/research_toolkit` with `tracked` label; ledger at `decisions/upstream_issues.md`.

Cost discipline: hard cap `budget.cost_cap_usd = 125.0` per RunPod job + project-wide $200 hard cap via `scripts/cost_rollup.py` (per ADR-020). Soft-cap triggers at $80 cumulative.
