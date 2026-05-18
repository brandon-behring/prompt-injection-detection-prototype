# Changelog — prompt-injection-detection-prototype

All notable changes to this project are documented here. Format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/); versions
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versioning convention

Named tags map to phase gates (refined at Phase 0-07 per ADR-033):

- **`v0.0.0`** — public-seed tag (immediately after the public push)
- **`v0.1.0`** — Phase 0 complete (all 50 `[OPEN]` decisions resolved + ADRs drafted + SPEC_SHEET filled + assumptions.md populated + invariant test stubs exist per Phase 0 close criterion)
- Patch versions (`v0.1.1`, `v0.1.2`, ...) — substantial work-units during Phase 1+
- **`v0.9.0-rc1`** — Phase 4 close release-candidate (per ADR-033) — fires the full publish pipeline (Quarto site build per ADR-030 + GH Pages deploy + HF Hub model card pushes per ADR-032) as a dress-rehearsal 24+ hours before submission day. Catches first-time-CI / auth / schema issues before the canonical tag fires. If rehearsal fails, fix-forward via new commits + `v0.9.0-rc2`
- **`v1.0.0`** — submission ready (Quarto site published to GH Pages per ADR-030; HF Hub model repos published per ADR-032; CHANGELOG entry committed; all WRITEUP `[TBD]` resolved; SUBMISSION_AUDIT clean)
- Post-submission patches (`v1.0.1`, `v1.0.2`, ...) — typo / link / reviewer-feedback fixes per ADR-033; reviewer URL stays pinned at `v1.0.0`; live Quarto site reflects latest patch
- Major bump (`v2.0.0`) — reserved for actual methodology revisions; requires superseding ADR with rationale + reviewer-notification step

Each release entry links closed audit findings (`SUBMISSION_AUDIT.md`) and closing ADRs.

## [1.0.2] — 2026-05-18

Governance patch — closes the two `REPO_AUDIT_2026-05-18` findings
that v1.0.0 + v1.0.1 documented as carryforwards but did not formally
supersede via ADR. Zero code changes; ADR + ledger update only.
Reviewer URL stays pinned at `tree/v1.0.0`; live Quarto site reflects
this patch.

### Added

- **`decisions/ADR-051-v1.0.x-carryforward-of-t0-and-invariant-scaffolds.md`** —
  narrow supersession of ADR-034 (T0 score-match wiring axis only;
  T1 + T3 tiers unchanged) and ADR-039 (gate 3 invariant-scaffold
  unskip axis only; gates 1+2+4+5+6 unchanged). Explicit v1.1.x
  landing conditions for both blocks. Per the audit's explicit
  invitation: *"Either finish this path or write a superseding ADR
  that explicitly waives it for submission"*; this ADR is the
  supersession path closure.

### Changed

- **`decisions/ADR-034-reproducibility-tier-full-ladder.md`** —
  frontmatter gains `superseded_by: [ADR-051]`.
- **`decisions/ADR-039-acceptance-criteria-six-gate-integration-checklist.md`** —
  same.
- **`SUBMISSION_AUDIT.md`** regenerated via
  `scripts/regenerate_audit.py` to reflect ADR-051 + the two narrow
  supersessions.

### Decisions

- 51 ADRs accepted across Phase 0-00 through v1.0.2 close.
- Reviewer URL pin stays at `tree/v1.0.0`; live Quarto site at
  `brandon-behring.github.io/prompt-injection-detection-prototype/`
  reflects v1.0.2 (and all subsequent v1.0.x patches).

## [1.0.1] — 2026-05-18

Post-submission polish patch (per ADR-033 v1.0.x patch convention).
Reviewer URL stays pinned at `tree/v1.0.0`; live Quarto site reflects
this patch.

### Added

- **HF Hub published**: canonical fold0/seed42 checkpoints for both
  rungs are now live —
  [`BBehring/prompt-injection-frozen-probe`](https://huggingface.co/BBehring/prompt-injection-frozen-probe)
  + [`BBehring/prompt-injection-lora`](https://huggingface.co/BBehring/prompt-injection-lora).
  Models published via `make publish-hub` using `HF_TOKEN_WRITE`
  from `.env.local` (write-scope token; v1.0.0 was blocked on this
  rotation). Both repos return HTTP 200; auto-generated model cards
  follow the expansive ADR-032 schema (YAML frontmatter + datasets
  pinned per ADR-016 + `model-index.results` per-slice metrics +
  intended use + limitations + ADR-005 contamination tier +
  citation + reproducibility commands).
- **README "Reading paths" subsection** with 3 navigable paths
  (Quick-skim / Audit / Reproduce) — all links resolve to the
  live Quarto site so a reviewer landing on GitHub clicks into a
  rendered page rather than a raw .md.
- **README live-site link** in the Status callout block —
  prominent above-the-fold link to
  `brandon-behring.github.io/prompt-injection-detection-prototype/`
  + the two HF Hub model-card URLs.

### Changed

- **AUPRC standardisation across WRITEUP + spokes** (was: AUROC
  headline; methodologically inconsistent with eval-design.md
  §5.1's PR-AUC preference). WRITEUP §Results headline rung-grid +
  §Results lift-vs-floor table + §Results headline claims +
  §Takeaways now lead with AUPRC; AUROC retained as a secondary
  cross-paper-comparable diagnostic. WRITEUP/model-rungs.md
  per-rung "Result:" blurbs rewritten the same way. Pooled_ood
  positive-class prevalence (0.374) computed + surfaced as the
  random-predictor AUPRC baseline; the honest finding tightens:
  even frozen-probe's `pooled_ood` AUPRC (0.364) lands ~0.01
  *below* the prevalence baseline.
- **`_quarto.yml` render allowlist expanded** to include
  `SPEC_SHEET.md`, `SUBMISSION_AUDIT.md`, `NEXT_STEPS.md`,
  `assumptions.md`, `decisions/upstream_issues.md`. These were
  previously auto-copied as raw `.md` into `_site/`; reviewer
  click resulted in raw markdown download. Now rendered as HTML;
  new "Reference" sidebar section between Evidence + Decisions
  surfaces them in the nav.
- **`scripts/publish_to_hub.py`** prefers `HF_TOKEN_WRITE` then
  `HF_TOKEN` from environment, falling back to the cached token —
  resolves the v1.0.0 publish-blocked auth path without disturbing
  the read-only token convention.
- **`WRITEUP/reproducibility.md`**: T0 "Status" block updated to
  reflect actual publication state at v1.0.1 + maintainer note on
  the still-stubbed `eval_from_hub.py` non-dry-run body (T0
  score-match wiring lands at v1.1.x). T3 vestigial "skeleton"
  label replaced with "complete" + RunPod-bootstrap pointer. Added
  the missing "Cross-references" block (now consistent with the
  other 7 spokes).
- **Hyphenation typo fix** in README L7 (`frozen probe →` →
  `frozen-probe →`) — single-occurrence drift from project naming
  convention.

### Closing

Audit-driven patch (3 parallel Explore agents at v1.0.0 close
surfaced these polish items). All gates green; live Quarto site
+ HF Hub repos resolve.

## [1.0.0] — 2026-05-18

Submission tag. Closes the `REPO_AUDIT_2026-05-18` 8-item remediation
queue with 12 commits + 2 rehearsal tags + green CI/Publish on the
v1.0.0 head. Per ADR-033, this is the reviewer URL pin
(`tree/v1.0.0`); post-submission patches land as `v1.0.1`+ and the
live Quarto site reflects the latest patch.

### Added

- `WRITEUP/` 7-spoke split (per Item 2 Q5 lock): data-decisions,
  model-rungs, eval-design, threshold-policy, reference-scorer-audit,
  methodology-guarantees, limitations-and-future-work; +
  `reproducibility.md` (T0 published-rung script-matched commands).
  Monolithic `WRITEUP.md` becomes a TOC/landing page with the §Results
  headline narrative.
- `EVIDENCE.md` full 5-section fill: ProtectAI v1/v2 contamination
  audit + `tfidf-lr` `verified_disjoint` anchor + style-confound +
  threshold-methodology + replication-invariants + sources.
- `docs/HYPERPARAMETER_DISCLOSURE.md` full 4-section fill: locked
  recipe (with per-rung knob tables from `configs/rungs/*.yaml`) +
  exploration-trajectory + axes-held-constant + caveats.
- `NEXT_STEPS.md` §3: 3 genuine Phase 0-5-surfaced open questions
  replacing template slots.
- `src/eval/slice_analysis.py`: `SINGLE_CLASS_SLICES` +
  `SINGLE_CLASS_INCOMPATIBLE_METRICS` + `is_metric_defined_for_slice()`.
  Filter applied at source in `src/eval/marginal_bootstrap.py` +
  `scripts/run_cv_clt_ci.py` so AUROC/AUPRC degenerate values
  (1.0/0.0) never land in artifacts (Item 4 Q9 lock).
- `scripts/build_results_json.py` + `scripts/generate_model_cards.py`
  + `scripts/publish_to_hub.py` + `evals/results.json` + `make
  publish-hub` (Item 5; per Q11 expansive ADR-032 schema; Q10 canonical
  fold0/seed42 per rung only). HF Hub publication outstanding pending
  write-scope token rotation.
- `make build-results-json` + `make generate-model-cards` +
  `make publish-hub` + `make publish-hub-dry-run` Makefile targets.
- `_quarto.yml` explicit `project.render:` allowlist scoping the
  site to README + CHANGELOG + WRITEUP + WRITEUP/* + EVIDENCE + ADRs
  (excludes transcripts/, data/raw/git/**, evals/, src/, scripts/,
  tests/, other docs/).
- Phase 5 closure ADRs: `ADR-049` (GPU-order priority refresh —
  A100-80G first; full-FT post-rehearsal); `ADR-050` (rung-slate
  narrowing — LLM judges dropped on cost re-estimation; full-FT OOD
  dropped on FUSE EIO crash); narrow supersession of ADR-018 +
  ADR-021. `closing_commit` populated on both.
- `gh-pages` orphan branch on origin (one-time bootstrap so
  `quarto-actions/publish@v2` works).

### Changed

- `WRITEUP.md` becomes a TOC/landing page; §1 Motivation + §2
  Approach + §Results (extracted §7 headline) + §Lessons brief +
  §12 Appendix. All 4 leftover `[OPEN: ...]` tokens resolved with
  declarative ADR-linked content.
- `SPEC_SHEET.md` rung-language aligned to ADR-050 narrowing —
  reference slate compresses from 4-rung (2 LLM judges + ProtectAI v1
  + v2) to 2-rung (ProtectAI v1 + v2). `vendor_black_box`
  contamination tier carries **0 rungs** in this submission;
  stratification gradient compresses from 4 tiers to 3. LODO 3-rung
  trained ladder retained; OOD comparison drops to 5-rung slate.
  Phase 0-4 checkboxes flipped [ ] → [x]; Phase 5 boxes ship checked
  at v1.0.0.
- `docs/HYPERPARAMETER_DISCLOSURE.md` + `docs/REPRODUCIBILITY.md` +
  `docs/THREAT_MODEL.md` placeholders fully resolved. `docs/REPRO`
  Python pin >=3.10 → >=3.13; stale `make diagnostics-smoke` /
  `make canonical-eval` → actual current Makefile targets.
- `README.md` headline-characterisation: curated 4-row punch table
  (Q3 lock) with frozen-probe/LoRA/ProtectAI-v2/tfidf-lr on
  `pooled_ood` AUPRC + 95% CI; LoRA's -0.071 AUPRC underperformance
  surfaced as the honest finding.
- `.github/workflows/ci.yml` Python pin 3.11 → 3.13 (matches
  pyproject.toml + .python-version; Item 3).
- `.github/workflows/publish.yml` env block adds HF_TOKEN +
  RUNPOD_API_KEY + OPENAI_API_KEY stubs to satisfy Quarto's dotenv
  loader (no real secrets at render time per Item 2 Q7 lock).
- `.pre-commit-config.yaml` ruff pin v0.4.0 → v0.15.13 (matches
  uv-locked ruff used by CI's `ruff format --check`; resolves the
  stash-restore loop that bit the Item 8 fix-forward).
- `Makefile` `site` + `site-preview` targets export stub env vars
  so `make site` renders without real secrets.
- `src/eval/figures.py`: explicit `cast(Figure, ...)` for upstream
  `plot_pareto_frontier` + `plot_slice_metric_heatmap` (both return
  `Any` typed); mypy strict clean.
- `src/data/audit.py:222`: explicit `cast(LeakageCheck, ...)` for
  `CrossSplitLeakageCheck` (upstream frozen-dataclass / Protocol
  settable-name mismatch).
- `tests/test_invariants.py`: docstring rewritten with v1.0.0
  honest accounting per ADR-039 gate 3 (10 invariants implemented;
  38 stubs carry forward to v1.1.x; 30 skip reasons made explicit).
  Data-gated invariants (`test_class_balance_per_fold` +
  `test_source_disjoint_train_test`) use `pytest.skip()` when
  canonical-run artifacts are absent (CI runs without data).
- `evals/bootstrap/marginal_cells.parquet`: 66 → 60 rows
  (bipia/injecagent × auprc removed by Item 4 source filter).
- `evals/audit/cross_fold_ci_audit.parquet`: 31 → 22 rows (all 3
  single-class slices × auroc/auprc removed).
- `evals/audit/mde_per_cell.parquet`: 142 → 136 rows.
- Repo-identity rewrites: `prompt-injection-detection-submission` →
  `prompt-injection-detection-prototype` in `assumptions.md` +
  `SPEC_SHEET.md` (GH Pages URL + reviewer URL pinpoints).

### Decisions

- 50 ADRs accepted across Phase 0-00 through Phase 5 close at
  ADR-050. `SUBMISSION_AUDIT.md` regenerates from frontmatter
  via `scripts/regenerate_audit.py` (CI hard gate per ADR-039).
- Reviewer URL stays pinned at `tree/v1.0.0`; live Quarto site at
  `brandon-behring.github.io/prompt-injection-detection-prototype/`
  reflects the latest patch.

## [0.9.0-rc3] — 2026-05-18

Third rehearsal — `a2fc4d9`. CI + Publish workflows green; reviewer
URLs return 200. Same content as v1.0.0; the rc3 tag is preserved
as the rehearsal-pass landmark per ADR-033 fix-forward discipline.

## [0.9.0-rc2] — 2026-05-18

Second rehearsal — `d66e3d0`. CI red on the lint hard gate (3
remaining ruff-format diffs from a pre-commit stash-restore loop) +
one data-gated invariant; Publish workflow needed an orphan `gh-pages`
branch on origin. Fix-forwarded via `0bedc80` (data-gated skipif) +
`a2fc4d9` (ruff-pre-commit v0.4.0 → v0.15.13 + format leftover).

## [0.9.0-rc1] — 2026-05-17

First rehearsal tag (per ADR-033). Catches first-time-CI / auth /
schema issues before the canonical submission. Resulted in the
`REPO_AUDIT_2026-05-18.md` 8-item remediation queue.

## [0.0.0] — 2026-05-15

### Added

- Initial public seed: SDD spec-sheet kit + literature dossier + Phase 0 infrastructure
- Kit-level discipline encoded directly in `SPEC_GREENFIELD.md` spec text + decision ledger
- Constitution split into 3 files: `docs/MISSION.md`, `docs/TECH_STACK.md`, `docs/ROADMAP.md`
- 50-row decision ledger in `SPEC_GREENFIELD.md` with reference-anchors column
- Three load-bearing libraries declared: `eval-toolkit`, `runpod-deploy`, `research_toolkit`
- Anti-hand-rolling rule + upstream-issue triage protocol locked in `docs/TECH_STACK.md`
- Tests-as-invariants stubs at `tests/test_invariants.py` (7 skip-marked)
- CI scaffolding (`Makefile`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`) with hard / soft / opt-in gate split
- Phase 0 infrastructure: `CLAUDE.md`, `AGENTS.md`, `/save-transcript` skill, `decisions/ADR_TEMPLATE.md`
- Literature dossier (16 verified files) under `docs/research/` with `MANIFEST.json` (produced via `research_toolkit` pipeline)
- `scripts/regenerate_audit.py` for ADR-as-source-of-truth audit register
- `SPEC_STRATEGY.md` (classification meta-doc), `docs/THREAT_MODEL.md`, `docs/REPRODUCIBILITY.md`, `docs/HYPERPARAMETER_DISCLOSURE.md`, `docs/GLOSSARY.md` (living)
- `docs/MANIFEST_SCHEMA.md` (eval-output schema)
- Cover-letter two-version split: `SUBMISSION_TEMPLATE.md` (committed) + `SUBMISSION.md` (gitignored, emailed separately)
- Transcripts private by default (`transcripts/*.md` gitignored; emailed separately at submission time)
- `uv.lock` committed for byte-reproducible installs
- Notebook scaffolding (jupytext + nbstripout); notebooks themselves are Phase 2+ work

### Decisions

- Phase 0 not yet started; `SPEC_GREENFIELD.md` ledger has 50 `[OPEN]` rows pending
- See `SPEC_STRATEGY.md` for the classification + alternatives-rejected rationale
- v0.0.0 is the public seed; v0.1.0 lands when Phase 0 closes
