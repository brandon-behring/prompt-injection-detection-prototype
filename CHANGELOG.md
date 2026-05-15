# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/); versions
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Each release entry links closed audit findings (`SUBMISSION_AUDIT.md`) and
closing ADRs.

## [0.0.0] — 2026-05-15

### Added
- Initial seed: SDD spec-sheet kit + literature dossier + Phase 0 infrastructure
- Kit-level discipline encoded directly in SPEC_GREENFIELD spec text + decision ledger
- 50-row decision ledger in SPEC_GREENFIELD with reference-anchors column
- Three load-bearing libraries declared: eval-toolkit, runpod-deploy, research_toolkit
- Tests-as-invariants stubs at `tests/test_invariants.py` (7 skip-marked)
- CI scaffolding (Makefile, ci.yml, pre-commit) with hard / soft / opt-in gate split
- Phase 0 infrastructure (CLAUDE.md, `/save-transcript` skill, `.claude/settings.local.json`)
- Literature dossier (16 verified files) under `docs/research/` with MANIFEST.json
- `scripts/regenerate_audit.py` for ADR-as-source-of-truth audit register

### Decisions
- Phase 0 not yet started; SPEC_GREENFIELD ledger has 50 [OPEN] rows pending
