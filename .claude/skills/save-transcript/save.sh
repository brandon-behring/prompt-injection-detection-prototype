#!/usr/bin/env bash
# Usage: save.sh <slug>
# Reads the most recent session JSONL under ~/.claude/projects/<encoded-cwd>/
# and renders user + assistant messages to transcripts/<YYYY-MM-DD>__<slug>.md.
#
# Dependencies: jq.
# Path-encoding convention: pwd | sed 's|/|-|g; s|^-||; s|^|-|'
# (matches Claude Code's project-dir encoding).
set -euo pipefail

slug="${1:?usage: save.sh <slug>}"

proj_dir="$HOME/.claude/projects/$(pwd | sed 's|/|-|g; s|^-||; s|^|-|')"
session_jsonl="$(ls -t "$proj_dir"/*.jsonl 2>/dev/null | head -1)"
[ -z "${session_jsonl:-}" ] && {
  echo "no session JSONL found in $proj_dir" >&2
  exit 1
}

mkdir -p transcripts
out="transcripts/$(date +%Y-%m-%d)__${slug}.md"

{
  echo "# Transcript: $slug ($(date +%Y-%m-%d))"
  echo ""
  echo "Source: $session_jsonl"
  echo ""
  jq -r '
    select(.type == "user" or .type == "assistant")
    | "## \(.type | ascii_upcase)\n\n\(
        if (.message.content | type) == "string"
        then .message.content
        elif (.message.content | type) == "array"
        then [.message.content[] | select(.type == "text") | .text] | join("\n")
        else ""
        end
      )\n"
  ' "$session_jsonl"
} > "$out"

echo "wrote $out"
