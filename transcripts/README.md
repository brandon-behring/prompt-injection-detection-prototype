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

## ADR linkage

ADRs that result from a transcript reference it explicitly in the frontmatter:

```yaml
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
```

Transcripts are the decision-rationale trail. Without them, ADRs lose the *why* behind the *what*. Skipping transcript capture for a multi-turn decision conversation is an anti-pattern (see `SPEC_GREENFIELD.md` §7).
