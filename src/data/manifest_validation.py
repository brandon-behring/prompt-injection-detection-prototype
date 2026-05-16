"""Schema validator for data/source_manifest.yaml (per ADR-016 Q3 + ADR-041 Q1).

The manifest is the Phase 1 deliverable that pins all 11 source revisions plus
licenses plus per-source row counts plus selection seeds plus filters. Schema
version 1.0 carries 13 fields per source row (rich schema per ADR-041 Q1=B);
bump_history is a top-level list of YAML-diff records appended on revision
bumps (per ADR-016 Q3 + ADR-036 bump-trigger policy).

Validation is invoked from (1) tests/test_invariants.py:test_source_manifest_schema_valid
(at Phase 0 close + ongoing) and (2) scripts/pin_source_manifest.py (post-write
sanity check). Raises ManifestSchemaError with explicit field-level context on
any violation — no silent failures per project standards.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

import yaml

# Schema constants — locked per ADR-041 Q1.
SCHEMA_VERSION: Final[str] = "1.0"

# Per-source required fields (rich schema = Q1 option B).
REQUIRED_SOURCE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "name",
        "hf_id",
        "type",  # "hf_dataset" | "git_repo"
        "revision_sha",
        "license",
        "role",  # "train_positive" | "train_benign" | "ood_eval"
        "expected_n",
        "cap",
        "selection_seed",
        "language_filter",
        "subset",
        "split",
        "citation_arxiv",
    }
)

# Locked source-name slate (11 sources per ADR-016 Q1).
EXPECTED_SOURCE_NAMES: Final[frozenset[str]] = frozenset(
    {
        # Train positives (LODO-rotational, 4 sources)
        "deepset_prompt_injections",
        "lakera_gandalf_ignore_instructions",
        "lakera_mosscap_prompt_injection",
        "hackaprompt",
        # Train benigns (stratified across folds, 2 sources)
        "lmsys_chat_1m",
        "ultrachat_200k",
        # OOD eval slate (never-trained-on, 5 sources)
        "notinject",
        "xstest",
        "jbb_behaviors",
        "bipia",
        "injecagent",
    }
)

# Locked role-counts per ADR-016 Q1 + Q2.
EXPECTED_ROLE_COUNTS: Final[dict[str, int]] = {
    "train_positive": 4,
    "train_benign": 2,
    "ood_eval": 5,
}

ALLOWED_TYPES: Final[frozenset[str]] = frozenset({"hf_dataset", "git_repo"})
ALLOWED_ROLES: Final[frozenset[str]] = frozenset({"train_positive", "train_benign", "ood_eval"})


class ManifestSchemaError(ValueError):
    """Raised on any schema violation in data/source_manifest.yaml."""


def _require(condition: bool, message: str) -> None:
    """Raise ManifestSchemaError if condition fails."""
    if not condition:
        raise ManifestSchemaError(message)


def _validate_source_row(name: str, row: dict[str, Any]) -> None:
    """Validate a single source row against the rich-schema contract.

    Parameters
    ----------
    name : str
        The source row's name field (used in error messages).
    row : dict
        The parsed source row from manifest YAML.

    Raises
    ------
    ManifestSchemaError
        If any required field is missing, has wrong type, or carries an
        invalid value (e.g., empty SHA, unknown role).
    """
    missing = REQUIRED_SOURCE_FIELDS - set(row.keys())
    _require(
        not missing,
        f"Source '{name}' missing required fields: {sorted(missing)}",
    )

    _require(
        row["name"] == name,
        f"Source '{name}' has mismatched name field: {row['name']!r}",
    )
    _require(
        row["type"] in ALLOWED_TYPES,
        f"Source '{name}' type must be in {sorted(ALLOWED_TYPES)}, got {row['type']!r}",
    )
    _require(
        row["role"] in ALLOWED_ROLES,
        f"Source '{name}' role must be in {sorted(ALLOWED_ROLES)}, got {row['role']!r}",
    )

    sha = row["revision_sha"]
    _require(
        isinstance(sha, str) and len(sha) >= 7,
        f"Source '{name}' revision_sha must be a string of length >=7, got {sha!r}",
    )

    _require(
        isinstance(row["license"], str) and len(row["license"]) > 0,
        f"Source '{name}' license must be a non-empty string",
    )

    _require(
        isinstance(row["expected_n"], int) and row["expected_n"] > 0,
        f"Source '{name}' expected_n must be a positive int, got {row['expected_n']!r}",
    )

    # cap may be None (use-all) or a positive int.
    cap = row["cap"]
    _require(
        cap is None or (isinstance(cap, int) and cap > 0),
        f"Source '{name}' cap must be None or positive int, got {cap!r}",
    )

    # selection_seed required when cap is set (random subsample); else may be None.
    seed = row["selection_seed"]
    if cap is not None:
        _require(
            isinstance(seed, int),
            f"Source '{name}' has cap={cap} but selection_seed is not int: {seed!r}",
        )

    # language_filter is a string code or None (None = no filter).
    lang = row["language_filter"]
    _require(
        lang is None or isinstance(lang, str),
        f"Source '{name}' language_filter must be None or str, got {lang!r}",
    )

    # subset / split / citation_arxiv may be None (per HF dataset shape).
    for optional_str_field in ("subset", "split", "citation_arxiv"):
        value = row[optional_str_field]
        _require(
            value is None or isinstance(value, str),
            f"Source '{name}' {optional_str_field} must be None or str, got {value!r}",
        )


def validate_manifest(manifest_path: Path) -> dict[str, Any]:
    """Validate data/source_manifest.yaml against the rich-schema contract.

    Parameters
    ----------
    manifest_path : Path
        Absolute path to the manifest YAML file.

    Returns
    -------
    dict
        The parsed + validated manifest (top-level keys: schema_version,
        bump_history, sources).

    Raises
    ------
    FileNotFoundError
        If the manifest file does not exist.
    ManifestSchemaError
        On any schema violation — missing fields, wrong types, role-count
        mismatch versus ADR-016 Q1 lock, source-name not in the locked slate,
        schema_version mismatch.
    """
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}")

    with manifest_path.open("r", encoding="utf-8") as fh:
        parsed = yaml.safe_load(fh)

    _require(isinstance(parsed, dict), "Top-level manifest must be a mapping")
    _require(
        parsed.get("schema_version") == SCHEMA_VERSION,
        f"schema_version must be {SCHEMA_VERSION!r}, got {parsed.get('schema_version')!r}",
    )
    _require(
        isinstance(parsed.get("bump_history"), list),
        "bump_history must be a list (may be empty)",
    )
    sources = parsed.get("sources")
    _require(isinstance(sources, list), "sources must be a list")

    seen_names: set[str] = set()
    role_counts: dict[str, int] = {role: 0 for role in ALLOWED_ROLES}

    for row in sources:
        _require(
            isinstance(row, dict),
            f"Each source row must be a mapping; got {type(row).__name__}",
        )
        name = row.get("name")
        _require(
            isinstance(name, str) and len(name) > 0,
            f"Source row missing 'name': {row!r}",
        )
        _require(
            name not in seen_names,
            f"Duplicate source name: {name!r}",
        )
        seen_names.add(name)
        _validate_source_row(name, row)
        role_counts[row["role"]] += 1

    # Slate-completeness check — all 11 expected source names present.
    missing_names = EXPECTED_SOURCE_NAMES - seen_names
    _require(
        not missing_names,
        f"Manifest missing expected sources from ADR-016 slate: {sorted(missing_names)}",
    )
    unexpected_names = seen_names - EXPECTED_SOURCE_NAMES
    _require(
        not unexpected_names,
        f"Manifest contains unexpected sources not in ADR-016 slate: {sorted(unexpected_names)}",
    )

    # Role-count check — 4 train_positive + 2 train_benign + 5 ood_eval per ADR-016.
    for role, expected in EXPECTED_ROLE_COUNTS.items():
        _require(
            role_counts[role] == expected,
            f"Role '{role}' has {role_counts[role]} sources; ADR-016 expects {expected}",
        )

    # Cast for mypy; isinstance check above narrows type.
    return parsed  # type: ignore[no-any-return]
