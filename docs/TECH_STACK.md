# Tech Stack

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

> **Decision needed (Phase 0):** GPU class, secret-management approach, dataset cache location. **Default if unsure:** H100 via runpod-deploy; `~/.config/<project>/secrets`; project-local `data/cache/`; transcript dir at `transcripts/`; upstream issues filed to GitHub.

These map to the corresponding `[OPEN]` rows in the SPEC_GREENFIELD decision ledger (§Tech-Stack: GPU class / Secrets / Cache + library version pins).
