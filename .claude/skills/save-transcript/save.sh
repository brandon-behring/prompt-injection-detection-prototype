#!/usr/bin/env bash
# Usage: save.sh <slug>
# Reads the most recent session JSONL under ~/.claude/projects/<encoded-cwd>/
# and renders user + assistant messages to transcripts/<YYYY-MM-DD>__<slug>.md.
#
# Rendered content blocks:
#   assistant: text, tool_use (name + input JSON)
#   user:      text (string or array), tool_result (success/error + content)
# Skipped (intentional): assistant `thinking` blocks (internal CoT).
#
# Dependencies: jq.
# Path-encoding convention: pwd | sed 's|[^a-zA-Z0-9]|-|g; s|^-*||; s|^|-|'
# (matches Claude Code's project-dir encoding: all non-alphanumerics → '-',
# single leading '-', no leading run of dashes).
set -euo pipefail

slug="${1:?usage: save.sh <slug>}"

proj_dir="$HOME/.claude/projects/$(pwd | sed 's|[^a-zA-Z0-9]|-|g; s|^-*||; s|^|-|')"
session_jsonl="$(ls -t "$proj_dir"/*.jsonl 2>/dev/null | head -1)"
[ -z "${session_jsonl:-}" ] && {
  echo "no session JSONL found in $proj_dir" >&2
  exit 1
}

out_dir="${OUT_DIR:-transcripts}"
mkdir -p "$out_dir"
out="$out_dir/$(date +%Y-%m-%d)__${slug}.md"

{
  echo "# Transcript: $slug ($(date +%Y-%m-%d))"
  echo ""
  echo "Source: $session_jsonl"
  echo ""
  jq -r '
    # Render a single content block. Returns "" for blocks that should be skipped.
    def render_block:
      if .type == "text" then
        .text
      elif .type == "tool_use" then
        "\n**Tool call: \(.name)**\n\n```json\n\(.input | tojson)\n```"
      elif .type == "tool_result" then
        "\n**Tool result\(if .is_error then " (error)" else "" end):**\n\n```\n\(
          if (.content | type) == "string" then
            .content
          elif (.content | type) == "array" then
            [.content[] | if .type == "text" then .text else "" end] | join("\n")
          else "" end
        )\n```"
      elif .type == "thinking" then
        ""
      else "" end;

    select(.type == "user" or .type == "assistant")
    | "## \(.type | ascii_upcase)\n\n\(
        if (.message.content | type) == "string" then
          .message.content
        elif (.message.content | type) == "array" then
          [.message.content[] | render_block] | map(select(. != "")) | join("\n")
        else "" end
      )\n"
  ' "$session_jsonl"
} > "$out"

echo "wrote $out"
