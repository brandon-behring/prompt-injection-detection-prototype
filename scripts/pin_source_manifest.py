"""Live-fetch HF + GitHub SHAs and write data/source_manifest.yaml (per ADR-041 Q2).

This script implements the Phase 1 lock — every source in the ADR-016 slate
gets a SHA pin captured at Phase 1 entry. HF datasets pin to revision SHA via
`huggingface_hub.HfApi.dataset_info`; GitHub-cloneable sources pin to HEAD via
`git ls-remote`. Output: `data/source_manifest.yaml` (rich schema per ADR-041
Q1; 13 fields per source row; schema_version 1.0; `bump_history: []`).

Usage:
    uv run python scripts/pin_source_manifest.py [--force]

Flags:
    --force    Allow overwriting an existing manifest with mismatched SHAs.
               Without --force the script errors on any SHA mismatch and refers
               the user to ADR-036 bump-trigger policy.

Re-runs are idempotent IF upstream SHAs unchanged. If upstream has moved, the
script raises a SHAMismatchError (caller decides: bump_history entry + --force,
or investigate).

Secrets — HF_TOKEN auto-discovered from environment (per ADR-035 three-store
split). Required for gated datasets (lmsys-chat-1m, hackaprompt may require
acceptance click). Public datasets work without HF_TOKEN.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

import yaml
from huggingface_hub import HfApi

# Add repo root to sys.path so we can import src/ as a module.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.manifest_validation import (  # noqa: E402
    SCHEMA_VERSION,
    ManifestSchemaError,
    validate_manifest,
)


@dataclass(frozen=True)
class SourceSpec:
    """Declarative spec for one source — fed into the pin pipeline.

    Mirrors the rich-schema contract in src/data/manifest_validation.py.
    SHA is filled at fetch time; everything else is locked at ADR-016 + ADR-041.
    """

    name: str
    hf_id: str
    type: str  # "hf_dataset" | "git_repo"
    license: str
    role: str  # "train_positive" | "train_benign" | "ood_eval"
    expected_n: int
    cap: int | None
    selection_seed: int | None
    language_filter: str | None
    subset: str | None
    split: str | None
    citation_arxiv: str | None


# Locked source slate (per ADR-016 Q1 + ADR-016 Q6 caps).
SLATE: Final[tuple[SourceSpec, ...]] = (
    # Train positives — LODO-rotational, 4 sources.
    SourceSpec(
        name="deepset_prompt_injections",
        hf_id="deepset/prompt-injections",
        type="hf_dataset",
        license="Apache-2.0",
        role="train_positive",
        expected_n=662,
        cap=None,
        selection_seed=None,
        language_filter=None,
        subset=None,
        split="train",
        citation_arxiv=None,
    ),
    SourceSpec(
        name="lakera_gandalf_ignore_instructions",
        hf_id="Lakera/gandalf_ignore_instructions",
        type="hf_dataset",
        license="MIT",
        role="train_positive",
        expected_n=1000,
        cap=None,
        selection_seed=None,
        language_filter=None,
        subset=None,
        split="train",
        citation_arxiv=None,
    ),
    SourceSpec(
        name="lakera_mosscap_prompt_injection",
        hf_id="Lakera/mosscap_prompt_injection",
        type="hf_dataset",
        license="MIT",
        role="train_positive",
        expected_n=3000,
        cap=3000,
        selection_seed=42,
        language_filter=None,
        subset=None,
        split="train",
        citation_arxiv=None,
    ),
    SourceSpec(
        name="hackaprompt",
        hf_id="hackaprompt/hackaprompt-dataset",
        type="hf_dataset",
        license="per-dataset-card",
        role="train_positive",
        expected_n=3000,
        cap=3000,
        selection_seed=42,
        language_filter=None,
        subset=None,
        split="train",
        citation_arxiv="2311.16119",
    ),
    # Train benigns — stratified across folds, 2 sources.
    SourceSpec(
        name="lmsys_chat_1m",
        hf_id="lmsys/lmsys-chat-1m",
        type="hf_dataset",
        license="CC-BY-4.0",
        role="train_benign",
        expected_n=10000,
        cap=10000,
        selection_seed=42,
        language_filter="en",
        subset=None,
        split="train",
        citation_arxiv="2309.11998",
    ),
    SourceSpec(
        name="ultrachat_200k",
        hf_id="HuggingFaceH4/ultrachat_200k",
        type="hf_dataset",
        license="Apache-2.0",
        role="train_benign",
        expected_n=10000,
        cap=10000,
        selection_seed=42,
        language_filter=None,
        subset=None,
        split="train_sft",
        citation_arxiv="2305.14233",
    ),
    # OOD eval slate — never-trained-on, 5 sources.
    SourceSpec(
        name="notinject",
        hf_id="leolee99/NotInject",
        type="hf_dataset",
        license="MIT",
        role="ood_eval",
        expected_n=339,
        cap=None,
        selection_seed=None,
        language_filter=None,
        subset=None,
        split="train",
        citation_arxiv="2410.22770",
    ),
    SourceSpec(
        name="xstest",
        hf_id="paul-rottger/xstest",
        type="git_repo",
        license="CC-BY-4.0",
        role="ood_eval",
        expected_n=450,
        cap=None,
        selection_seed=None,
        language_filter=None,
        subset=None,
        split=None,
        citation_arxiv="2308.01263",
    ),
    SourceSpec(
        name="jbb_behaviors",
        hf_id="JailbreakBench/JBB-Behaviors",
        type="hf_dataset",
        license="MIT",
        role="ood_eval",
        expected_n=200,
        cap=None,
        selection_seed=None,
        language_filter=None,
        subset="behaviors",
        split="harmful",
        citation_arxiv="2404.01318",
    ),
    SourceSpec(
        name="bipia",
        hf_id="microsoft/BIPIA",
        type="git_repo",
        license="MIT",
        role="ood_eval",
        expected_n=150,
        cap=None,
        selection_seed=None,
        language_filter=None,
        subset=None,
        split=None,
        citation_arxiv="2312.14197",
    ),
    SourceSpec(
        name="injecagent",
        hf_id="uiuc-kang-lab/InjecAgent",
        type="git_repo",
        license="Apache-2.0",
        role="ood_eval",
        expected_n=1054,
        cap=None,
        selection_seed=None,
        language_filter=None,
        subset=None,
        split=None,
        citation_arxiv="2403.02691",
    ),
)


class SHAMismatchError(RuntimeError):
    """Raised when re-running the pin script finds upstream SHAs have moved."""


def _fetch_hf_sha(api: HfApi, repo_id: str, token: str | None) -> str:
    """Fetch the latest revision SHA for an HF dataset.

    Parameters
    ----------
    api : HfApi
        Reused HfApi client instance.
    repo_id : str
        HF dataset repo identifier (e.g., "deepset/prompt-injections").
    token : str | None
        HF auth token for gated datasets; None for public access.

    Returns
    -------
    str
        The revision SHA (typically full 40-char hash).

    Raises
    ------
    RuntimeError
        If the dataset_info call fails (gated dataset without token,
        network failure, repo deleted).
    """
    info = api.dataset_info(repo_id=repo_id, token=token)
    sha = info.sha
    if sha is None:
        raise RuntimeError(f"HF dataset {repo_id!r} returned no SHA (info.sha is None)")
    if not isinstance(sha, str):
        raise RuntimeError(f"HF dataset {repo_id!r} returned non-str SHA: {type(sha).__name__}")
    return sha


def _fetch_git_sha(github_repo: str) -> str:
    """Fetch the HEAD SHA from a GitHub repo via `git ls-remote`.

    Parameters
    ----------
    github_repo : str
        Slash-separated repo path (e.g., "microsoft/BIPIA"). Translated to
        the HTTPS clone URL — no auth required for public repos.

    Returns
    -------
    str
        The HEAD commit SHA (full 40-char hash).

    Raises
    ------
    RuntimeError
        If `git ls-remote` fails (network, repo deleted, command not installed).
    """
    url = f"https://github.com/{github_repo}.git"
    try:
        result = subprocess.run(
            ["git", "ls-remote", url, "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"git ls-remote failed for {url!r}: stderr={exc.stderr!r}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"git ls-remote timed out for {url!r}") from exc

    line = result.stdout.strip().split("\n")[0] if result.stdout else ""
    sha = line.split()[0] if line else ""
    if len(sha) < 7:
        raise RuntimeError(f"git ls-remote returned unparseable output for {url!r}: {line!r}")
    return sha


def _build_source_row(spec: SourceSpec, sha: str) -> dict[str, Any]:
    """Convert a SourceSpec + fetched SHA into the YAML row dict."""
    return {
        "name": spec.name,
        "hf_id": spec.hf_id,
        "type": spec.type,
        "revision_sha": sha,
        "license": spec.license,
        "role": spec.role,
        "expected_n": spec.expected_n,
        "cap": spec.cap,
        "selection_seed": spec.selection_seed,
        "language_filter": spec.language_filter,
        "subset": spec.subset,
        "split": spec.split,
        "citation_arxiv": spec.citation_arxiv,
    }


def _fetch_all_shas(token: str | None) -> dict[str, str]:
    """Fetch revision SHAs for every source in the locked slate.

    Parameters
    ----------
    token : str | None
        HF auth token; None for anonymous access (works on public datasets).

    Returns
    -------
    dict[str, str]
        Map of source name to fetched revision SHA.
    """
    api = HfApi()
    shas: dict[str, str] = {}
    for spec in SLATE:
        if spec.type == "hf_dataset":
            shas[spec.name] = _fetch_hf_sha(api, spec.hf_id, token)
        else:
            shas[spec.name] = _fetch_git_sha(spec.hf_id)
        print(f"  {spec.name:>36s}  {shas[spec.name][:12]}  ({spec.type})")
    return shas


def _existing_shas(manifest_path: Path) -> dict[str, str] | None:
    """Return the SHA map from an existing manifest, or None if missing.

    Parameters
    ----------
    manifest_path : Path
        Path to the manifest YAML.

    Returns
    -------
    dict[str, str] | None
        None if manifest does not exist; otherwise name -> revision_sha map.
    """
    if not manifest_path.exists():
        return None
    with manifest_path.open("r", encoding="utf-8") as fh:
        parsed = yaml.safe_load(fh)
    if not isinstance(parsed, dict):
        return None
    sources = parsed.get("sources")
    if not isinstance(sources, list):
        return None
    return {row["name"]: row["revision_sha"] for row in sources if isinstance(row, dict)}


def _diff_shas(prior: dict[str, str], fresh: dict[str, str]) -> list[tuple[str, str, str]]:
    """Return list of (name, prior_sha, fresh_sha) tuples where SHAs differ."""
    diffs: list[tuple[str, str, str]] = []
    for name, fresh_sha in fresh.items():
        prior_sha = prior.get(name, "<absent>")
        if prior_sha != fresh_sha:
            diffs.append((name, prior_sha, fresh_sha))
    return diffs


def _write_manifest(
    manifest_path: Path,
    shas: dict[str, str],
    bump_history: list[dict[str, Any]],
) -> None:
    """Serialize the manifest YAML with rich schema + bump_history."""
    rows = [_build_source_row(spec, shas[spec.name]) for spec in SLATE]
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pin_method": "live_fetch_via_pin_source_manifest_script",
        "adr_ref": "ADR-016 + ADR-041",
        "bump_history": bump_history,
        "sources": rows,
    }
    with manifest_path.open("w", encoding="utf-8") as fh:
        fh.write(
            "# data/source_manifest.yaml — Phase 1 source pin per ADR-016 Q3 + ADR-041 Q1.\n"
            "# Generated by scripts/pin_source_manifest.py; do not hand-edit row SHAs.\n"
            "# Re-run the script to bump SHAs (see ADR-036 bump-trigger policy).\n"
            "\n"
        )
        yaml.safe_dump(payload, fh, sort_keys=False, default_flow_style=False)


def main() -> int:
    """CLI entry — fetch fresh SHAs, write manifest, validate, exit 0 on success."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing manifest even when SHAs have moved (records bump_history entry)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_REPO_ROOT / "data" / "source_manifest.yaml",
        help="Output manifest path (default: data/source_manifest.yaml)",
    )
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    if token is None:
        print("[pin_source_manifest] HF_TOKEN not set — using anonymous HF access.")
        print("[pin_source_manifest] Gated datasets (lmsys-chat-1m) may fail to resolve.")

    print(f"[pin_source_manifest] Fetching SHAs for {len(SLATE)} sources...")
    fresh_shas = _fetch_all_shas(token)

    prior_shas = _existing_shas(args.output)
    bump_history: list[dict[str, Any]] = []

    if prior_shas is None:
        print(f"[pin_source_manifest] No existing manifest at {args.output} — writing fresh.")
    else:
        diffs = _diff_shas(prior_shas, fresh_shas)
        if not diffs:
            print("[pin_source_manifest] All SHAs unchanged — manifest already current.")
            # Still re-validate to surface any external schema drift.
            try:
                validate_manifest(args.output)
                print("[pin_source_manifest] Manifest validates clean. No-op.")
                return 0
            except ManifestSchemaError as err:
                print(f"[pin_source_manifest] ERROR: existing manifest fails validation: {err}")
                return 2

        print(f"[pin_source_manifest] Found {len(diffs)} SHA mismatch(es):")
        for name, prior, fresh in diffs:
            print(f"    {name:>36s}  prior={prior[:12]}  fresh={fresh[:12]}")
        if not args.force:
            print("[pin_source_manifest] Refusing to overwrite without --force.")
            print("[pin_source_manifest] If this bump is intentional, re-run with --force.")
            print("[pin_source_manifest] See ADR-036 + decisions/upstream_issues.md.")
            raise SHAMismatchError("Upstream SHAs have moved; re-run with --force to record.")

        bump_history = [
            {
                "bumped_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "trigger": "force-flag-set",
                "diffs": [
                    {"name": name, "prior": prior, "fresh": fresh} for name, prior, fresh in diffs
                ],
            }
        ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    _write_manifest(args.output, fresh_shas, bump_history)
    print(f"[pin_source_manifest] Wrote {args.output}")

    # Post-write validation pass.
    try:
        validate_manifest(args.output)
    except ManifestSchemaError as err:
        print(f"[pin_source_manifest] ERROR: post-write validation failed: {err}")
        return 2

    print("[pin_source_manifest] Manifest validates clean against rich schema.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
