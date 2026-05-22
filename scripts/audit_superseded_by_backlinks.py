"""Audit that supersession back-links are bidirectional + that Accepted
ADRs have populated closing_commit fields.

Motivated by REPO_AUDIT_2026-05-21 §P1-6: ADR-062's frontmatter declared
`supersedes: [ADR-046, ADR-054, ADR-061]` but the three target ADRs had
empty `superseded_by:` fields. v1.2.14's ADR-076 backfilled the specific
gap, but no mechanical invariant existed to catch future instances.

This script installs that invariant + a sibling closing_commit invariant
(per v1.2.15 plan Q1 lock: backlink + closing_commit in one tool).

Behavior:
  1. Walk decisions/ADR-*.md. Parse YAML frontmatter from each file.
  2. Build forward map: {supersedeR_id: [supersedeE_ids]} from each
     ADR's `supersedes:` field.
  3. For each (supersedeR, supersedeE) edge, verify supersedeE's
     `superseded_by:` field contains supersedeR.
  4. Separately: for each ADR with `status: Accepted` (case-insensitive),
     verify `closing_commit:` is populated. INFO-level (not FAIL)
     because some Accepted ADRs may legitimately have no single closing
     commit (e.g., consolidation ADRs like ADR-073 that close a cluster).
  5. Exit 0 if all backlinks bidirectional AND no closing_commit gaps
     beyond known cases. Exit 1 with violations otherwise.

Halt-and-surface protocol (per v1.2.15 plan Q2 lock): if the tool surfaces
gaps beyond the ADR-046/054/061 set covered by ADR-076 + the known-empty
cases (ADR-076 itself + sibling self-referential ADRs), the patch sequence
should STOP and the user should lock the next-scope decision.

Usage:
  uv run python scripts/audit_superseded_by_backlinks.py

CI / pre-commit: invoked from .pre-commit-config.yaml +
.github/workflows/audit-writeup.yml (parallel to audit_adr_count_claims
+ audit_writeup_numbers).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DECISIONS_DIR = REPO_ROOT / "decisions"

# Normalize ADR identifiers to 3-digit strings.
# Accepts: "046", "ADR-046", 46 (int), "ADR-046  # comment".
_ADR_ID_RE = re.compile(r"(?:ADR-)?(\d{1,3})")

# Closing-commit invariant exceptions (known-legitimately-empty cases).
# These ADRs may legitimately have empty closing_commit:
# - ADR-076 itself + future backfill ADRs (chicken-and-egg per ADR-072 precedent)
# - Governance ADRs that don't have a single "closing" commit
#
# This list is intentionally small. The default discipline (per v1.2.15
# plan Q2) is: if the tool surfaces gaps beyond these known cases,
# halt and surface to the user.
CLOSING_COMMIT_EXEMPT: set[str] = {
    "072",  # frontmatter-backfill ADR; v1.2.13 historical artifact
    "076",  # frontmatter-backfill ADR; v1.2.14 historical artifact
    "077",  # frontmatter-backfill ADR; v1.2.15 historical artifact (this script's authorizing ADR)
    "078",  # EXECUTIVE_SUMMARY absorption governance; v1.3.0 PR-1; closing_commit forward-references the PR-1 SHA
    "079",  # 2-guide reader architecture governance; v1.3.0 PR-4; closing_commit forward-references the PR-4 SHA
    "080",  # reviewer-URL-pin numeric correction governance; v1.3.1 PR-1; closing_commit forward-references this PR's SHA (chicken-and-egg)
    "081",  # frontmatter `status:` field-split narrow-relaxation governance; v1.3.2 PR; closing_commit forward-references this PR's SHA (chicken-and-egg)
}


def normalize_adr_id(value: Any) -> str | None:
    """Convert various ADR-id representations to 3-digit string.

    Returns None if the value can't be parsed (caller decides what to do).
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    match = _ADR_ID_RE.search(s)
    if match is None:
        return None
    return f"{int(match.group(1)):03d}"


def parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Parse the YAML frontmatter block at the top of an ADR file.

    Returns None if the file has no `---` frontmatter delimiter.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None

    if not content.startswith("---\n"):
        return None

    end_marker = content.find("\n---\n", 4)
    if end_marker == -1:
        return None

    fm_text = content[4:end_marker]
    try:
        parsed = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        print(f"WARN: YAML parse failure on {path.name}: {exc}", file=sys.stderr)
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def extract_id_list(field: Any) -> list[str]:
    """Extract normalized 3-digit ADR ids from a frontmatter field.

    Handles all observed forms:
      - None / empty / []
      - "ADR-046" / "046" / 46
      - [ADR-046, ADR-054] (list)
      - ["046", "054"] (quoted list)
    """
    if field is None:
        return []
    if isinstance(field, (str, int)):
        normalized = normalize_adr_id(field)
        return [normalized] if normalized else []
    if isinstance(field, list):
        out: list[str] = []
        for item in field:
            normalized = normalize_adr_id(item)
            if normalized:
                out.append(normalized)
        return out
    return []


# Regex to detect "axis-only" supersession comments. Convention established
# by the v1.2.13/v1.2.14 narrow-relaxation discipline (ADR-067-070-073 chain
# + ADR-072 + ADR-076): full-axis supersessions are the default; meta /
# narrow / consolidation supersessions are explicitly marked with one of
# these phrases in the YAML comment on the same line as the list item.
_AXIS_ONLY_RE = re.compile(
    r"\b(?:axis\s+only|frontmatter[-\s]+axis|narrow[-\s]+relaxation|"
    r"consolidated|sweep\s+has\s+been\s+applied|meta[-\s]frontmatter|"
    r"same\s+axis|embedded[-\s]+quote\s+axis|empty[-\s]+frontmatter)\b",
    re.IGNORECASE,
)


def parse_supersedes_edges_with_comments(
    path: Path,
) -> list[tuple[str, str]]:
    """Walk the raw frontmatter of `path`; return (target_id, comment_text)
    for each `supersedes:` list item.

    Used to classify each supersession edge as STRICT (full-axis; backlink
    required) vs EXEMPT (axis-only / meta / consolidated; no backlink
    required). The classification is based on the YAML comment on the same
    line as the list item.

    Returns empty list if no `supersedes:` block found.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    if not content.startswith("---\n"):
        return []
    end_marker = content.find("\n---\n", 4)
    if end_marker == -1:
        return []
    fm_lines = content[4:end_marker].splitlines()

    edges: list[tuple[str, str]] = []
    in_supersedes_block = False
    for line in fm_lines:
        stripped = line.lstrip()
        # End of supersedes block: encounter another top-level key.
        if in_supersedes_block and line and not line[0].isspace():
            in_supersedes_block = False
        if line.startswith("supersedes:"):
            in_supersedes_block = True
            # Handle inline list: supersedes: [ADR-046, ADR-054]
            inline_match = re.match(r"supersedes:\s*\[(.+)\]\s*$", line)
            if inline_match:
                inline_items = inline_match.group(1).split(",")
                for item in inline_items:
                    normalized = normalize_adr_id(item.strip())
                    if normalized:
                        edges.append((normalized, ""))  # inline: no comment
                in_supersedes_block = False
            continue
        if in_supersedes_block and stripped.startswith("- "):
            # Bullet list item; may have inline comment.
            content_after_dash = stripped[2:]
            comment = ""
            if "#" in content_after_dash:
                value_part, _, comment_part = content_after_dash.partition("#")
                comment = comment_part.strip()
                value = value_part.strip()
            else:
                value = content_after_dash.strip()
            normalized = normalize_adr_id(value)
            if normalized:
                edges.append((normalized, comment))
    return edges


def is_axis_only(comment: str) -> bool:
    """Return True if the supersession comment marks an axis-only edge."""
    if not comment:
        return False
    return bool(_AXIS_ONLY_RE.search(comment))


def collect_adrs(decisions_dir: Path) -> dict[str, dict[str, Any]]:
    """Return {adr_id: frontmatter_dict} for every ADR-NNN-*.md.

    Filename is the source of truth for adr_id. The frontmatter `adr_id`
    field cannot be trusted because YAML 1.1 (and pyyaml's default loader)
    parses unquoted `adr_id: 010` as OCTAL (decimal 8), collapsing
    ADR-008 ↔ ADR-010 into the same key. Bug surfaced in v1.2.15 audit
    development; 4 ADR pairs were affected (008↔010, 009↔011, 018↔022,
    019↔023).
    """
    out: dict[str, dict[str, Any]] = {}
    for path in sorted(decisions_dir.glob("ADR-*.md")):
        fm = parse_frontmatter(path)
        if fm is None:
            continue
        # Filename is source of truth. ADR-NNN-slug.md → "NNN".
        adr_id = normalize_adr_id(path.stem.removeprefix("ADR-"))
        if adr_id is None:
            print(f"WARN: cannot determine ADR id for {path.name}", file=sys.stderr)
            continue
        # Attach the resolved path for downstream messaging.
        fm["_path"] = path
        fm["_id"] = adr_id
        out[adr_id] = fm
    return out


def audit_backlinks(adrs: dict[str, dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Return (failures, info) for supersession-backlink invariant.

    For each `supersedes: [N]` edge, verify target ADR-N has supersedeR
    in its `superseded_by:` list. Edges marked axis-only via comment
    (per parse_supersedes_edges_with_comments + is_axis_only) are
    EXEMPT from the bidirectional requirement and reported as INFO.
    """
    failures: list[str] = []
    info: list[str] = []
    for adr_id, fm in adrs.items():
        path = fm["_path"]
        # Pair each (target_id, comment) edge with the structural list.
        comment_edges = parse_supersedes_edges_with_comments(path)
        comment_by_target = {tid: cmt for tid, cmt in comment_edges}

        for target_id in extract_id_list(fm.get("supersedes")):
            target_fm = adrs.get(target_id)
            if target_fm is None:
                failures.append(
                    f"ADR-{adr_id} declares supersedes: [ADR-{target_id}] "
                    f"but ADR-{target_id} does not exist"
                )
                continue
            target_backlinks = extract_id_list(target_fm.get("superseded_by"))
            if adr_id in target_backlinks:
                continue  # bidirectional; clean

            # Classify by comment: axis-only → INFO; otherwise → FAIL
            comment = comment_by_target.get(target_id, "")
            entry = (
                f"ADR-{adr_id} declares supersedes: [ADR-{target_id}] "
                f"but ADR-{target_id}.superseded_by does not include "
                f"ADR-{adr_id} (has: {target_backlinks or 'empty'})"
            )
            if is_axis_only(comment):
                info.append(entry + f" [axis-only per comment: {comment[:60]!r}]")
            else:
                failures.append(entry)
    return failures, info


def audit_closing_commit(adrs: dict[str, dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Return (failures, info) for closing_commit invariant.

    Failures: Accepted ADRs with empty closing_commit, NOT in the
              CLOSING_COMMIT_EXEMPT set.
    Info: Accepted ADRs in the exempt set with empty closing_commit
          (documented exceptions).
    """
    failures: list[str] = []
    info: list[str] = []
    for adr_id, fm in adrs.items():
        status = str(fm.get("status", "")).strip().lower()
        if status != "accepted":
            continue
        closing = fm.get("closing_commit")
        if closing is None or str(closing).strip() == "":
            entry = f"ADR-{adr_id} (Accepted) has empty closing_commit"
            if adr_id in CLOSING_COMMIT_EXEMPT:
                info.append(entry + " — known-exempt (governance / backfill ADR)")
            else:
                failures.append(entry)
    return failures, info


def main() -> int:
    if not DECISIONS_DIR.is_dir():
        print(f"ERROR: {DECISIONS_DIR} not found", file=sys.stderr)
        return 2

    adrs = collect_adrs(DECISIONS_DIR)
    print(f"audit_superseded_by_backlinks: parsed {len(adrs)} ADR frontmatters")

    backlink_failures, backlink_info = audit_backlinks(adrs)
    closing_failures, closing_info = audit_closing_commit(adrs)

    if backlink_info:
        print(f"\nbacklink INFO (axis-only supersessions; {len(backlink_info)} entries):")
        for entry in backlink_info:
            print(f"  INFO  {entry}")

    if closing_info:
        print(f"\nclosing_commit INFO (known-exempt; {len(closing_info)} entries):")
        for entry in closing_info:
            print(f"  INFO  {entry}")

    if backlink_failures:
        print(
            f"\nBACKLINK FAILURES ({len(backlink_failures)} entries):",
            file=sys.stderr,
        )
        for entry in backlink_failures:
            print(f"  FAIL  {entry}", file=sys.stderr)

    if closing_failures:
        print(
            f"\nCLOSING_COMMIT FAILURES ({len(closing_failures)} entries):",
            file=sys.stderr,
        )
        for entry in closing_failures:
            print(f"  FAIL  {entry}", file=sys.stderr)

    if backlink_failures or closing_failures:
        print(
            "\naudit_superseded_by_backlinks: STOPPED with violations. "
            "Per v1.2.15 plan Q2: halt + surface to user; do not auto-fix.",
            file=sys.stderr,
        )
        return 1

    print(
        f"\naudit_superseded_by_backlinks: clean "
        f"({len(adrs)} ADRs checked; "
        f"{len(backlink_info)} axis-only edge(s) + "
        f"{len(closing_info)} closing_commit exemption(s) noted)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
