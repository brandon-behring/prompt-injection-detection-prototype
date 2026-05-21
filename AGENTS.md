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

**Narrow exceptions** (per [ADR-067](decisions/ADR-067-immutability-clarification-and-canonical-slug-reference.md) + [ADR-068](decisions/ADR-068-immutability-narrow-relaxation-for-broken-external-references.md) + [ADR-069](decisions/ADR-069-immutability-narrow-relaxation-for-publisher-url-to-doi-canonicalization.md) + [ADR-070](decisions/ADR-070-quarto-render-only-markdown-corrections.md), consolidated in [ADR-073](decisions/ADR-073-adr-immutability-rule-consolidated-re-statement.md)): FOUR factual-defect / render-defect classes MAY be corrected in-place with a commit message citing the relevant ADR:

1. **Cross-reference slug filename typos** (per ADR-067) — a slug pointing at a wrong-but-existing canonical file in `decisions/`.
2. **Broken external references** (per ADR-068) — markdown links pointing at local-filesystem paths or aspirational upstream resources (404 URLs).
3. **Publisher-URL → DOI canonicalization** (per ADR-069) — `journals.sagepub.com/doi/<DOI>`, `tandfonline.com/doi/<DOI>`, `jstor.org/stable/<ID>`, `dl.acm.org/doi/<DOI>` MAY be canonicalized to `doi.org/<DOI>`.
4. **Render-only Markdown syntax corrections** (per ADR-070) — delimiter fixes required for faithful Quarto rendering, visible decision content unchanged.

Frontmatter-completeness backfills (`closing_commit:` + `superseded_by:`) are governed separately by the [ADR-072](decisions/ADR-072-adr-051-052-frontmatter-and-structural-backfill.md) + [ADR-076](decisions/ADR-076-superseded-by-and-closing-commit-frontmatter-backfill.md) frontmatter-backfill precedent.

ALL other content (numeric values, methodology, prose, alternatives, non-slug frontmatter, table data) remains immutable per the rule above.

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
- For design-doc audits / cross-file consistency checks / open-ended polish reviews: using a fast-search subagent (e.g., Claude Code's Explore) — those agents' own docs forbid this use class (read excerpts, miss content past their read window). Use a general-purpose subagent for audit-class tasks instead.

## More

For platform-specific behavior (Claude Code session-start auto-load, permissions allowlist patterns), see `CLAUDE.md`.
