# Glossary

Project-specific terminology, alphabetized. **This is a living document — it expands as work continues.**

> **Convention**: when a new project-specific term is introduced in any spec / writeup / ADR / transcript / dossier file, add an entry here within the same commit (or as a follow-up `docs: glossary +<term>` commit). The anti-pattern *"Introducing a project-specific term without adding it to docs/GLOSSARY.md"* is in CLAUDE.md.

## ADR (Architecture Decision Record)

A single locked decision in Michael Nygard format: Status / Context / Decision / Consequences / Alternatives Considered. **Immutable**. See `decisions/README.md` for the lifecycle + `decisions/ADR_TEMPLATE.md` for the schema.

## AGENTS.md

Vendor-neutral agent-rules file. Mirrors `CLAUDE.md` for non-Claude agents (Codex / Cursor / OpenCode). See `AGENTS.md`.

## Anti-hand-rolling rule

`[LOCKED]` rule in `docs/TECH_STACK.md`: don't reimplement primitives that exist in `eval-toolkit` / `runpod-deploy` / `research_toolkit`. Project-specific glue is allowed; replacing library primitives is not. See also: library-first discipline.

## Brief alignment (Phase 0-00)

First Phase 0 sub-session. User pastes the brief (or key excerpts) into the conversation; `/save-transcript` captures it. Surfaces scope / deliverable / deadline / visibility / reviewer-profile / brief-mandated-metric constraints. Produces ADR-001.

## CHANGELOG

Keep-a-Changelog 1.1.0 format at `CHANGELOG.md`. v0.0.0 = seed; v0.1.0 = Phase 0 complete; v1.0.0 = submission ready (per Q12 versioning lock).

## CLAUDE.md

Auto-loaded by Claude Code at every session start in this repo. Project-level instructions: Phase 0 workflow, library-first discipline, transcript convention, commit discipline, anti-patterns. See also: AGENTS.md (vendor-neutral mirror).

## Constitution (3-file)

Project Constitution split across `docs/MISSION.md` + `docs/TECH_STACK.md` + `docs/ROADMAP.md`. Per the DLAI Spec-Driven Development course's 3-file Constitution pattern.

## ECE (Expected Calibration Error)

Calibration metric. Equal-mass variant + debiased (Kumar 2019). Reported alongside Brier score and reliability curves. See `eval-toolkit` methodology curriculum.

## Educational-references rule

Phase 0 interview discipline: for each `[OPEN]` decision walked, surface (a) concrete explanation, (b) options with pros/cons, (c) **2-3 definitive reference URLs** (paper / library docs / methodology guide), (d) recommendation with rationale. See CLAUDE.md Phase 0 workflow.

## Fresh-investigation rule

Phase 0 interview discipline (stronger version of educational-references): read `docs/research/` dossier files **live at decision time**; do not pre-load assumed candidates from training memory. See CLAUDE.md Phase 0 workflow.

## LODO (Leave-One-Dataset-Out)

Source-disjoint cross-validation. With k positive sources, k-fold LODO holds out each source in turn. Field standard for cross-source generalization per Fomin 2025 ("When Benchmarks Lie"). See `docs/research/datasets/` + `SPEC_GREENFIELD.md` §1 Data row "Splits structure".

## MDE (Minimum Detectable Effect)

The smallest true effect we have the statistical power to detect at α / β targets. Distinguishes "no difference detected" from "no power to detect." `eval-toolkit.mde_from_ci` derives MDE from observed CI width.

## OOD (Out-Of-Distribution)

Test slices that differ from the training distribution in some axis: source, channel, style, language. The IID-vs-OOD gap is the headline characterization in `WRITEUP.md` §7.

## Open / Locked / TBD (marker grammar)

3-token grammar for in-document markers (Q2 lock):

- `[OPEN]` — Phase 0 decision-ledger item; resolved during Phase 0 interview
- `[LOCKED]` — spec freeze; changing requires a superseding ADR
- `[TBD: <prose>]` — evidence pointer / draft prose / numeric value; populated at the named phase

No other tokens. Bare `[TBD]` (no qualifier) is a grammar violation.

## Paired bootstrap

Resampling-based paired-difference CI for rung-vs-rung comparison; accounts for paired-error correlation without parametric assumptions like DeLong's. `eval_toolkit.paired_bootstrap_diff`. See `eval-toolkit` `docs/methodology/bootstrap.md`.

## Phase 0 close criterion

Phase 1 cannot start until: (a) every `[OPEN]` ledger row is `locked-to-X` and references an ADR, (b) SPEC_SHEET has zero `[OPEN]` slots, (c) `assumptions.md` carries every severity-≥-medium assumption surfaced during Phase 0, (d) `tests/test_invariants.py` has skip-marked stubs for every invariant in SPEC_GREENFIELD §5.

## PR-AUC, ROC-AUC, recall@FPR

Headline ranking + operating-point metrics for class-imbalanced binary classification. PR-AUC = area under precision-recall curve. ROC-AUC = area under receiver-operating-characteristic curve. recall@FPR = recall at a specific false-positive-rate pinpoint (e.g., r@1% = recall at FPR ≤ 1%).

## Replanning checkpoint

Inserted after each phase in `docs/ROADMAP.md`: before exiting the phase, audit whether any `[LOCKED]` assumption has been invalidated. If yes: write a superseding ADR, update SPEC_SHEET slot, cascade to WRITEUP §<relevant>, commit `chore: phase-N replan`.

## SDD (Spec-Driven Development)

Methodology where a binding spec drives implementation. Decisions locked before code; ADRs document changes. Tests are invariants. See `SPEC_STRATEGY.md` for the chosen pack-size + alternatives rejected.

## SPEC_GREENFIELD.md

Binding pre-Phase-0 spec. Contains Feature Specs §0-§7 + 50-row decision ledger with reference anchors. Phase 0 walks each `[OPEN]` ledger row via `/exploring-options`.

## SPEC_SHEET.md

Post-Phase-0 fill-in form. Same skeleton as SPEC_GREENFIELD; each `[OPEN]` slot becomes `[LOCKED: X (per ADR-NNN)]` once Phase 0 resolves it. Phase 1 cannot start until SPEC_SHEET has zero `[OPEN]` slots.

## SUBMISSION_AUDIT.md

Claim-status register. **Script-generated from `decisions/ADR-*.md` frontmatter** via `scripts/regenerate_audit.py`. CI hard-gate asserts no drift between ADRs and the audit table. ADRs are the source of truth; SUBMISSION_AUDIT is derived.

## Three-state contamination taxonomy

Reference-scorer training-overlap verdict (encoded in eval-toolkit manifest `contamination_flags` field):

- `verified_disjoint` — training data verifiably disjoint from project sources
- `suspected_contamination` — known overlap with one or more project sources
- `vendor_black_box` — training data not disclosed; audit shifts to fold-pattern + scope-mismatch analysis

See `docs/THREAT_MODEL.md` + `EVIDENCE.md` §1–2 + `docs/MANIFEST_SCHEMA.md`.

## Transcript

Decision-conversation capture at `transcripts/<YYYY-MM-DD>__<slug>.md`. Produced by `/save-transcript <slug>` skill. **Private by default** (gitignored); emailed separately to reviewer at submission time. ADRs reference transcripts by filename; reviewer correlates via emailed bundle.

## Upstream-issue triage protocol

`[LOCKED]` rule in `docs/TECH_STACK.md`: every library gap / bug / feature request is filed to the relevant upstream GitHub repo with the `tracked` label before any local workaround. Ledger at `decisions/upstream_issues.md`.
