---
name: save-transcript
description: Save the active Claude Code session as a markdown transcript at transcripts/<YYYY-MM-DD>__<slug>.md
---

# save-transcript

Captures the active Claude Code session as a markdown transcript. Used at
the end of each Phase 0 sub-session to checkpoint the decision
conversation. See `SPEC_GREENFIELD.md` §7 (Transcript capture).

## Invocation

```
/save-transcript <slug>
```

Examples:

- `/save-transcript phase-0-00__brief-alignment`
- `/save-transcript phase-0-02__data-design`
- `/save-transcript post-phase-1-data-audit`

## Mechanism

The skill runs `.claude/skills/save-transcript/save.sh <slug>`, which:

1. Finds the active session JSONL under `~/.claude/projects/<encoded-cwd>/`
2. Extracts user + assistant messages via `jq`
3. Writes a markdown rendering to `transcripts/<YYYY-MM-DD>__<slug>.md`

Dependencies: `jq` must be installed. The bash script's path-encoding
convention follows Claude Code's
`pwd | sed 's|[^a-zA-Z0-9]|-|g; s|^-*||; s|^|-|'` pattern
(all non-alphanumerics → `-`, single leading dash). If Claude Code's
storage format changes, the script may need an update — flag as an
upstream issue against the harness rather than working around locally.

## ADR linkage

ADRs that result from a transcript reference it in frontmatter:

```yaml
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
```
