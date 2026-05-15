---
adr_id: 009
slug: process-mandates
title: Process mandates — two-tier reproducibility, marker-based testing, compute disclosure
date: 2026-05-15
status: Accepted
claim_id: CLAIM-009
claim: Reproducibility is two-tier (laptop-only smoke + GPU-rental canonical, per SPEC_GREENFIELD row 355); testing discipline is marker-based (unit / smoke / integration / golden) with a 70% soft coverage floor on core modules; pre-commit hooks enforce discipline locally; no remote CI is set up (Tight calendar per ADR-001); notebooks are jupytext-paired with illustrative-only role (per ADR-013); GPU-hours + cost per rung are disclosed in the WRITEUP.
source: SPEC_GREENFIELD.md §Brief row 308 (Q5-C6) + §STYLE rows 350-351 + §Submission row 355
acceptance_criterion: A laptop-only smoke target completes the full pipeline (data load → minimal training → eval → analysis) on a developer laptop without RunPod access; canonical reproduction instructions are documented for GPU rental; tests carry markers selectable via pytest -m; per-rung GPU-hours + dollar cost are reported in WRITEUP.
closing_commit: e760faf
references:
  - https://neurips.cc/Conferences/2024/PaperInformation/PaperChecklist
  - https://docs.pytest.org/en/stable/example/markers.html
  - https://jupytext.readthedocs.io/
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-009: Process mandates — two-tier reproducibility, marker-based testing, compute disclosure

## Status

Accepted (2026-05-15)

## Context

Process mandates (Q5-C6) govern the *how-we-build* layer: reproducibility tier, testing discipline, CI/pre-commit, documentation depth, notebook format, compute disclosure. The Tight calendar (ADR-001) forces tradeoffs: setting up a green-on-PR GitHub Actions CI costs ~3 hours that could go to methodology depth. The kit defaults (marker-based testing, two-tier reproducibility, jupytext-paired notebooks) are well-suited to a methodology-first submission; this ADR ratifies them and adds compute disclosure as a methodology-first move.

## Decision

**Reproducibility tier**: two-tier.

- **Laptop-only smoke target**: full pipeline (data load → minimal training → eval → analysis) completes on a developer laptop without RunPod access. Demonstrates plumbing works; not a canonical reproduction. Used by A1 reviewer to verify the pipeline runs in ~5 minutes.
- **GPU-rental canonical target**: regenerates headline numbers on a rented H100 (or equivalent) via runpod-deploy primitives. Reviewer can re-run with cost ≈ Brandon's cost.

**Testing discipline**: marker-based, kit-default ratified.

- Markers: `unit`, `smoke`, `integration`, `golden` (selectable via `pytest -m`).
- Soft coverage floor: 70% on core modules. Not a strict gate; honest discipline.
- Test invariants (per SPEC_GREENFIELD §5): `tests/test_invariants.py` carries skip-marked stubs for every invariant; stubs filled phase-by-phase.

**CI / pre-commit**: pre-commit hooks only; no remote CI.

- `.pre-commit-config.yaml` already configured with gitleaks, ruff, ruff-format, mypy, nbstripout, no-emoji, SUBMISSION_AUDIT-in-sync.
- No GitHub Actions setup under Tight calendar (~3 hours saved for methodology depth).
- Tradeoff acknowledged: no visible green-badge in README; reviewer must trust local pre-commit + git history.

**Documentation depth**: README + WRITEUP + ADRs + transcripts (kit default).

- ADRs in `decisions/` (immutable; sequentially numbered).
- Transcripts in `transcripts/` (gitignored; emailed to reviewer at submission time).
- Topic-focused spokes in `WRITEUP/` per ADR-004 hub-and-spoke structure.

**Notebook format**: jupytext-paired (kit default; `pyproject.toml [tool.jupytext]` configured) with **illustrative-only role** per ADR-013.

- Notebooks load precomputed artifacts (parquet, JSON, manifests) and render figures + tables.
- GPU training runs are Python scripts (under `scripts/` or as runpod-deploy invocations), not notebook cells.

**Compute disclosure**: GPU-hours + dollar cost per rung disclosed in WRITEUP.

- Per-rung table: rung name, GPU type, training hours, dollar cost, seed count.
- Aggregated total in exec summary.
- Aligns with NeurIPS-style reproducibility checklist; explicit methodology-first signal.

## Consequences

**Positive:**

- Two-tier reproducibility honors A1+A2 dual audience: A1 verifies plumbing on a laptop in 5 minutes; A2 can rent a GPU and regenerate canonical numbers.
- Marker-based testing > coverage gaming. 70% soft floor is honest discipline without paper-chasing line-coverage targets.
- Pre-commit-only keeps the discipline floor under Tight calendar without burning the ~3 hours of CI setup.
- Compute disclosure differentiates the submission methodologically — most published work omits it.
- Jupytext + illustrative-only role decouples human-readable result rendering from time-consuming training runs.

**Negative / cost:**

- No visible green-badge on README. Mitigation: pre-commit hooks documented in CONTRIBUTING-equivalent or inline in `decisions/README.md`; reviewer can run `pre-commit run --all-files` locally.
- Two-tier reproducibility doubles the test-infrastructure work — laptop smoke target needs minimal dataset + minimal training config that's *meaningfully* different from canonical (not just smaller). Phase 0-06 finalizes the smoke-vs-canonical separation specifics.

**Neutral:**

- Phase 0-06 still walks §STYLE rows 350 (coverage floor specifics) and 351 (final marker strategy), §5 Code rows 348 (module layout) and 349 (smoke-vs-canonical separation profile). This ADR ratifies the broad direction; the implementation specifics are deferred.

## Alternatives Considered

- **GPU-rental canonical only (no laptop smoke)**: Cheaper to build. *Rejected because* reviewer-friction is too high; A1 reviewer won't rent a GPU to verify a single submission.
- **Laptop-only (no canonical GPU reproduction)**: Cheapest. *Rejected because* the headline numbers cannot be regenerated without GPU; canonical reproduction is a load-bearing reproducibility claim.
- **GitHub Actions CI**: Visible green badge; tells reviewers tests pass. *Rejected* under Tight calendar; ~3 hours of setup better spent on methodology. Pre-commit alone covers the discipline floor.
- **HF Spaces hosted demo**: Maximum reviewer engagement. *Rejected* under Tight calendar (~4+ hours of demo build).
- **Coverage floor 80% or 90% strict**: Production-leaning. *Rejected* because 70% soft is honest under Tight; coverage chasing dilutes methodology focus.
- **Pure-script (no notebooks)**: Cleanest reproducibility. *Rejected because* notebooks are valuable for reviewer-facing result illustration; jupytext-paired solves the diff-friendliness concern.

## References

- NeurIPS Paper Checklist (compute disclosure) — https://neurips.cc/Conferences/2024/PaperInformation/PaperChecklist
- pytest markers — https://docs.pytest.org/en/stable/example/markers.html
- jupytext — https://jupytext.readthedocs.io/
- `STYLE.md` (this repo) — kit-provided style discipline
- `code_quality.md` (this repo) — implementation discipline
- ADR-001 (Tight calendar argues against remote CI)
- ADR-004 (hub-and-spoke structure for compute-disclosure section)
- ADR-013 (notebook illustrative-only role + jupytext + RunPod persistence)
