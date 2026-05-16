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

## [Unreleased]

### Added

- Phase 0-07 submission deliverables locks — ADR-030 (Quarto HTML site supersedes ADR-002 PDF + repo) + ADR-031 (reviewer reading paths via `index.qmd` supersedes ADR-004 PDF-as-hub) + ADR-032 (HF Hub publication = headline rungs only with model card discipline) + ADR-033 (release strategy = rehearsal + submission + patches) + ADR-034 (reproducibility tier = full ladder T0+T1+T3)
- `_quarto.yml` website config + sidebar nav for 8 spokes + auto-include of all ADRs
- `index.qmd` reviewer entry-point with three reading paths (A1 quick-skim ~15 min, A2 audit ~60 min, deep-dive reproduce-numbers)
- `.github/workflows/publish.yml` — `quarto-actions/setup@v2` + `quarto-actions/publish@v2` workflow auto-deploys site to GH Pages on push to `main` and on tag push `v*`
- `WRITEUP/reproducibility.md` skeleton spoke documenting the T0+T1+T3 tier ladder with verbatim commands
- `Makefile` targets — `make site` (Quarto render), `make site-preview` (live-reload dev server), `make eval-from-hub RUNG=<name>` (T0 placeholder; implementation deferred to Phase 3)

### Changed

- ADR-002 status changed from Accepted to Superseded (superseded by ADR-030)
- ADR-004 status changed from Accepted to Superseded (superseded by ADR-031)
- SPEC_GREENFIELD ledger rows 300, 302, 347, 348, 349, 350 updated with locks + supersession notes
- SPEC_SHEET §Context paragraph + Phase 5 gates + new §9 Submission deliverables + §8 Linked ADRs trailer updated to reflect Phase 0-07 locks
- Versioning convention (this file) — added `v0.9.0-rc1` rehearsal tag + `v1.0.x` post-submission patch convention per ADR-033

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
