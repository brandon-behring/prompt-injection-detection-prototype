---
adr_id: "026"
slug: module-layout-concern-grouped-subpackages
title: Module layout — concern-grouped sub-packages under src/
date: 2026-05-16
status: Accepted
claim_id: CLAIM-026
claim: Phase 0-06 locks the §5 Code architecture ledger row 348 (Module layout) at concern-grouped sub-packages under src/. The repo's modelling code is organized as src/{data, training, scoring, eval, utils}/ with sub-package contents per concern — src/data/ holds source loaders + dedup + LODO splits + manifest validation; src/training/ holds ModernBERT loader + LoRA configurator + trainer; src/scoring/ holds reference-scorer adapters (ProtectAI v1/v2, Lakera-API, LLM-judges); src/eval/ holds calibration_battery + operating_points + slice_analysis; src/utils/ holds config_hash + paths + logging glue. CLI entrypoints live in scripts/ (orchestrate the above; one entrypoint per top-level operation — fit_dual_policy_thresholds.py, run_metrics_battery.py, run_bootstrap_battery.py, cost_rollup.py, regenerate_audit.py, check_no_emoji.py). Configs live in configs/{runpod, rungs, data}/ as versioned YAML. Tests live in tests/{conftest.py, test_invariants.py, unit/, smoke/, integration/} with marker-based slicing (per ADR-029). This layout was already implied by file paths cited across prior ADRs (library_imports.md references src/training/load_modernbert.py + src/eval/calibration_battery.py + src/eval/operating_points.py + scripts/fit_dual_policy_thresholds.py + scripts/run_bootstrap_battery.py + configs/runpod/headline.yaml); ADR-026 ratifies as the contract that Phase 1+ implementation must follow. Adding or moving a top-level src/ sub-package post-lock requires a superseding ADR.
source: SPEC_GREENFIELD.md §5 Code architecture ledger row 348 + Phase 0-06 walk Q1
acceptance_criterion: SPEC_GREENFIELD ledger row 348 carries locked-to-concern-grouped-subpackages-under-src status (see ADR-026); SPEC_SHEET §6 Code architecture gains a "Module layout" subsection with the 5-sub-package taxonomy + scripts/ + configs/ + tests/ surface enumerated; tests/test_invariants.py contains skip-marked stub test_module_layout_taxonomy asserting (1) src/{data, training, scoring, eval, utils} directories exist as Python packages (each contains __init__.py); (2) scripts/ contains only entrypoint files (no library code); (3) configs/{runpod, rungs, data} directories exist with at least one YAML file each at Phase 1 entry; the no-emoji invariant scan globs already operate over src/ scripts/ configs/ tests/ docs/ so the layout lock does not change scan-target enumeration.
closing_commit: fa1ad33
references:
  - https://github.com/brandon-behring/eval-toolkit/tree/main/src/eval_toolkit
  - https://packaging.python.org/en/latest/tutorials/packaging-projects/
  - https://hynek.me/articles/testing-packaging/
  - decisions/ADR-013-kit-ratify-bulk-strictness-intake-notebook-persistence.md
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md
  - decisions/ADR-022-statistical-inference-apparatus.md
  - decisions/ADR-023-calibration-battery-and-interventions.md
  - decisions/ADR-025-dual-policy-threshold-characterization.md
  - decisions/library_imports.md
transcript: transcripts/2026-05-16__phase-0-06__code-test-discipline.md
---

# ADR-026: Module layout — concern-grouped sub-packages under src/

## Status

Accepted (2026-05-16). Closes the first of 4 [OPEN] rows in Phase 0-06 (§5 Code architecture + §STYLE — rows 348-351 of SPEC_GREENFIELD ledger). The other three rows close in ADR-027 (smoke vs canonical separation), ADR-028 (coverage floor), and ADR-029 (test marker strategy).

## Context

SPEC_GREENFIELD §5 pre-locks the three-repo split (modelling repo / eval-toolkit / runpod-deploy), configuration discipline (versioned YAML configs with config-hash invariant), SDD artefacts list (spec.md, assumptions.md, decisions/, transcripts/, EVIDENCE.md), and tests-as-invariants (7 enumerated invariants). What remained [OPEN] at row 348 was the directory structure within the modelling repo — file names, package boundaries, where CLI entrypoints live, where configs live, where fixture data lives.

By Phase 0-06 entry the implied layout had crystallized through file-path citations across prior ADRs and `decisions/library_imports.md`. Citations (verified at decision time):

- `src/training/load_modernbert.py` (library_imports.md runpod-deploy section, flash-attn-fallback recipe row)
- `src/eval/calibration_battery.py` (library_imports.md eval-toolkit section, calibration-battery rows)
- `src/eval/operating_points.py` (library_imports.md eval-toolkit section, dual-policy operating-point row)
- `scripts/fit_dual_policy_thresholds.py` (library_imports.md eval-toolkit section, threshold-selector rows)
- `scripts/run_bootstrap_battery.py` (library_imports.md eval-toolkit section, bootstrap rows)
- `scripts/run_metrics_battery.py` (library_imports.md eval-toolkit section, metrics rows)
- `scripts/cost_rollup.py` (library_imports.md runpod-deploy section, manifest-summary row)
- `configs/runpod/headline.yaml` (library_imports.md runpod-deploy section, schema row)

ADR-026 ratifies the implied layout as a contract so the citations above resolve to real paths once Phase 1 implementation lands, and so test-as-invariant scans (no-emoji glob, source-disjoint glob) operate over a stable taxonomy.

Three layout options were considered:

(A) **Flat packages** — single `src/` namespace with files only (`src/data_loaders.py`, `src/training.py`, etc.). Doesn't scale past ~5 modules; conflicts with prior-ADR file paths that already presume sub-packages.

(B) **Concern-grouped sub-packages** — `src/{data, training, scoring, eval, utils}/` with each sub-package containing related modules. Matches the implied layout from prior ADRs; mirrors eval-toolkit's concern-grouped style without aping it. **Selected.**

(C) **Layer-stratified** — `src/{api, domain, infra, invariants}/` separating pure-vs-IO. Theoretically cleaner but doesn't fit the glue-layer reality of this case study — pure-math kernels live upstream in eval-toolkit, so domain/ would be thin and infra/ would be most of the repo, defeating the layering.

## Decision

### Locked module layout

```
prompt-injection-detection-prototype/
├── src/
│   ├── __init__.py
│   ├── data/                            # source loaders, dedup, LODO splits, manifest
│   │   ├── __init__.py
│   │   ├── loaders.py                   # HF dataset loaders per ADR-016 source manifest
│   │   ├── dedup.py                     # MiniLM cosine-0.80 label-aware dedup per ADR-016
│   │   └── splits.py                    # 4-fold LODO + 3-seed splits per ADR-016
│   ├── training/                        # ModernBERT loader + LoRA + trainer
│   │   ├── __init__.py
│   │   ├── load_modernbert.py           # backbone load + flash-attn-fallback per ADR-020
│   │   ├── lora.py                      # LoRA configurator per ADR-019
│   │   └── trainer.py                   # multi-rung trainer per ADR-015 + ADR-017
│   ├── scoring/                         # reference-scorer adapters (one module per scorer)
│   │   ├── __init__.py
│   │   ├── protectai.py                 # ProtectAI v1 + v2 adapters per ADR-018
│   │   ├── lakera_api.py                # Lakera-API adapter per ADR-018
│   │   └── llm_judge.py                 # GPT-4o + Claude judges per ADR-018
│   ├── eval/                            # calibration, operating points, slice analysis
│   │   ├── __init__.py
│   │   ├── calibration_battery.py       # 4-ECE + Brier + reliability per ADR-023
│   │   ├── operating_points.py          # dual-policy thresholds per ADR-025
│   │   └── slice_analysis.py            # OOD slate slicing per ADR-021
│   └── utils/                           # config-hash, paths, logging glue
│       ├── __init__.py
│       ├── config_hash.py               # config-hash invariant per SPEC §5 config discipline
│       ├── paths.py                     # canonical eval/results/audit path resolution
│       └── logging.py                   # structured-logging glue
├── scripts/                             # CLI entrypoints — orchestrate src/ functions
│   ├── fit_dual_policy_thresholds.py    # per ADR-025
│   ├── run_metrics_battery.py           # per ADR-021 + ADR-023
│   ├── run_bootstrap_battery.py         # per ADR-022 + ADR-024
│   ├── cost_rollup.py                   # per ADR-020
│   ├── regenerate_audit.py              # SUBMISSION_AUDIT regeneration (already exists)
│   └── check_no_emoji.py                # no-emoji invariant scan (already exists)
├── configs/
│   ├── runpod/
│   │   └── headline.yaml                # canonical RunPod config per ADR-020
│   ├── rungs/                           # per-rung YAML hyperparameters per SPEC §5 config discipline
│   │   ├── classical_floor.yaml
│   │   ├── frozen_probe.yaml
│   │   ├── lora.yaml
│   │   └── full_ft.yaml
│   ├── profiles/                        # smoke vs canonical profile configs per ADR-027
│   │   ├── fixtures.yaml
│   │   └── full.yaml
│   └── data/
│       └── source_manifest.yaml         # per ADR-016 source manifest with HF SHAs
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # marker registration + shared fixtures
│   ├── test_invariants.py               # 7+ tests-as-invariants per SPEC §5
│   ├── fixtures/                        # smoke-test fixture data (NOT real data)
│   ├── unit/                            # pytest -m unit tests
│   ├── smoke/                           # pytest -m smoke tests
│   └── integration/                     # pytest -m integration tests
├── decisions/                           # ADRs (Michael Nygard format) — already exists
├── transcripts/                         # decision-conversation captures — already exists (gitignored)
├── docs/                                # research dossier + ROADMAP — already exists
├── data/                                # NOT for committed data; HF cache target via runpod-deploy
├── evals/                               # output JSON + audit + per-row predictions
├── WRITEUP/                             # writeup hub + spokes
└── (root files — Makefile, pyproject.toml, STYLE.md, SPEC_GREENFIELD.md, SPEC_SHEET.md, etc.)
```

### Boundaries

- **`src/` is library code** — importable, no side effects at import time, no CLI parsing.
- **`scripts/` is entrypoint glue** — argparse, file IO, orchestrates `src/` calls. Not importable.
- **`configs/` is data** — YAML; loaded by entrypoints; never executed.
- **`tests/` is verification** — including `tests/fixtures/` for smoke-data; never imports outside `src/`.

### Adding a new sub-package

If a Phase 1+ surprise reveals a concern that doesn't fit any of the 5 sub-packages — for example, a serving layer for production deployment or a notebook-only exploratory analysis surface — a superseding ADR adds the new sub-package rather than wedging into `utils/`.

## Consequences

### Positive

- **Implied layout becomes load-bearing**: prior ADR file-path citations resolve to real paths at Phase 1 entry without amendment.
- **Mirrors eval-toolkit** without copying it: reviewer onboarding leverages familiarity.
- **Clean glob targets for invariants**: no-emoji scan, source-disjoint scan, frozen-dataclass scan all operate over predictable patterns (`src/**/*.py`, `scripts/**/*.py`, etc.).
- **`scripts/` vs `src/` boundary co-locked**: the Q3 coverage floor (ADR-028) operates against the whole repo without per-package strata; the boundary discipline keeps low-value entrypoint tests from leaking into the floor calculation via the upstream-issue-filing escape hatch (per ADR-028 co-lock).

### Negative

- **5-sub-package taxonomy is a guess**: if `src/scoring/` grows to 8 files (one per reference rung) or `src/eval/` grows past calibration + operating points + slice analysis, future ADRs may need to split. Acceptable cost — the supersession pattern handles it.
- **Layout lock is not a hard CI gate** at Phase 0 close: the invariant test stub (`test_module_layout_taxonomy`) is skip-marked until Phase 1 creates the directories. A determined Phase 1 developer could land code in the wrong place; review discipline catches it.
- **`data/` directory is reserved but not populated** at Phase 0 close; eval-toolkit + HF datasets handle data caching via runpod-deploy patterns per ADR-013.

### Limitation

The 5 sub-package boundary is empirically chosen, not derived. Future ADRs may split if a sub-package grows large enough to warrant it. The structure is a starting point, not a final taxonomy.

### Extension condition for revisit

If scope extends to production deployment (currently out-of-scope per Q2 framing in ADR-027), add `src/serving/` for the deployment layer via superseding ADR.

## Alternatives considered

- **(A) Flat packages** — rejected; doesn't scale past ~5 modules; conflicts with prior-ADR file paths.
- **(C) Layer-stratified** (api/domain/infra) — rejected; doesn't fit the glue-layer reality where pure-math kernels live upstream in eval-toolkit; `domain/` would be thin and `infra/` would be most of the repo.
