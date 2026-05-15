# AGENTS.md — agent-portable rules

This file is the vendor-neutral agent guide. Any modern coding agent (Claude Code, Codex, Cursor, OpenCode, etc.) should read this on session start.

**Claude Code** users: the canonical Claude-specific rules live in `CLAUDE.md` (auto-loaded by Claude Code). This file mirrors the key rules so agents on other platforms get the same discipline.

## Read first

Before any work in this repo, read in order:

1. **`SPEC_GREENFIELD.md`** — the binding pre-Phase-0 spec; 50-row decision ledger with reference anchors.
2. **`docs/MISSION.md`** + **`docs/TECH_STACK.md`** + **`docs/ROADMAP.md`** — the three-file Constitution.
3. **`SPEC_STRATEGY.md`** — why this pack-size was chosen; classification + escalation triggers.

## Phase 0 workflow

Phase 0 is the spec lock-in interview. It runs via `/exploring-options` (or equivalent agent skill) against `SPEC_GREENFIELD.md`'s decision ledger. Sub-sessions are topic-focused; see `docs/ROADMAP.md` for the recommended sequence (~9 sub-sessions).

**For each `[OPEN]` decision walked**: (a) explain what the decision means concretely, (b) present options with pros/cons, (c) cite 2-3 definitive reference URLs (paper / library docs / methodology guide), (d) recommend with rationale.

**Fresh-investigation rule**: read `docs/research/` dossier files live at decision time; do not pre-load assumed candidates from training memory or prior knowledge. The dossier is the source.

After each sub-session, save the transcript locally (`transcripts/<YYYY-MM-DD>__<slug>.md`). **Transcripts are private by default** (gitignored); emailed separately at submission time.

Each locked decision produces:

1. An ADR at `decisions/ADR-NNN-<slug>.md` (Michael Nygard format; see `decisions/ADR_TEMPLATE.md`)
2. SPEC_GREENFIELD appendix row updated: `locked-to-X (see ADR-NNN)`
3. SPEC_SHEET corresponding `[OPEN]` slot updated: `[LOCKED: X (per ADR-NNN)]`
4. SUBMISSION_AUDIT.md regenerates from ADRs via `python scripts/regenerate_audit.py`

ADRs are the source of truth. ADRs are immutable; supersede via new ADR.

## Library-first discipline

Three load-bearing libraries (never hand-roll equivalents):

- eval-toolkit — https://github.com/brandon-behring/eval-toolkit
- runpod-deploy — https://github.com/brandon-behring/runpod-deploy
- research_toolkit — https://github.com/brandon-behring/research_toolkit

The rule bans replacing library primitives; project-specific glue (data loaders, custom scorers using upstream primitives, project-named CLIs) is allowed and expected.

Track every import / skill invocation in `decisions/library_imports.md`. File upstream issues for any gap before any local workaround; ledger at `decisions/upstream_issues.md`.

## Commit discipline

- Each meaningful work unit = its own commit
- Type-prefixed messages: `feat:` `refactor:` `docs:` `chore:` `test:` `fix:` `seed:`
- Trailer: `Co-Authored-By: Claude <noreply@anthropic.com>` (or equivalent agent attribution)
- Reference `ADR-NNN` in commits that lock or supersede a Phase 0 decision
- **No amend / no squash / no force-push after first push** — fix-forward with new commits

## Anti-patterns to avoid

- Hand-rolling functionality already in the three libraries
- Working around a library limitation without filing an upstream issue
- Skipping transcript capture for a multi-turn decision conversation
- Mutating a locked decision without writing a superseding ADR
- Tuning on test data — even informally during error analysis
- Rewriting git history after the first public push
- Adding a methodology component without an ADR
- Adding an evaluation dataset without a leakage scan
- Persisting only summary metrics without per-row predictions
- Introducing a project-specific term without adding it to `docs/GLOSSARY.md`

## More

For platform-specific behavior (Claude Code session-start auto-load, permissions allowlist patterns), see `CLAUDE.md`.
