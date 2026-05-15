# Transcripts

Decision-conversation captures. Every multi-turn decision conversation produces a transcript here.

> **Privacy convention.** Transcripts are **private by default** and gitignored — only this README is tracked. The brief, Phase 0 conversations, and raw decision rationale stay local. ADRs (the decisions themselves) are public; the rationale conversation that produced them stays private. Transcripts are **emailed to the reviewer separately at submission time** so they see the decision trail without the raw content being republished on a public repo.

## Filename convention

`transcripts/<YYYY-MM-DD>__<slug>.md`

Examples:
- `2026-05-15__phase-0-00__brief-alignment.md`
- `2026-05-15__phase-0-02__data-design.md`
- `2026-06-01__post-phase-1-data-audit.md`

## How to capture

Invoke the `/save-transcript <slug>` skill at the end of a decision sub-session:

```
/save-transcript phase-0-00__brief-alignment
```

The skill (at `.claude/skills/save-transcript/`) reads the active Claude Code session JSONL and renders user + assistant messages to a markdown file under `transcripts/`.

## Auto-save floor (`transcripts/auto/`)

A repo-scoped `SessionEnd` hook (in `.claude/settings.json`) automatically saves one transcript per Claude Code session to `transcripts/auto/<YYYY-MM-DD>__auto__<HHMMSS>.md`. This is a safety net so no conversation is lost if you forget to run `/save-transcript`.

- Auto-saves use a **non-semantic slug** (`auto__<HHMMSS>`) and are **not ADR-linkable**.
- For every multi-turn decision conversation, still run `/save-transcript <semantic-slug>` so the resulting transcript can be referenced from an ADR's `transcript:` frontmatter field.
- `transcripts/auto/` is gitignored (same privacy convention as the rest of `transcripts/`).
- The hook is fail-safe (`|| true`) and never blocks session end.

The mechanism uses the same `save.sh` script with `OUT_DIR=transcripts/auto`.

## ADR linkage

ADRs that result from a transcript reference it explicitly in the frontmatter:

```yaml
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
```

Transcripts are the decision-rationale trail. Without them, ADRs lose the *why* behind the *what*. Skipping transcript capture for a multi-turn decision conversation is an anti-pattern (see `SPEC_GREENFIELD.md` §7).
