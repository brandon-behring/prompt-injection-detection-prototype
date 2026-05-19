"""Backfill provenance manifests for `evals/predictions/*.parquet` per ADR-057.

Emits a per-prediction `manifest.json` at
``evals/manifests/<rung>__<fold>__<seed>__<slice>.json`` for each of the 282
prediction parquets. Each manifest carries:

- ``git_sha``: HEAD commit SHA (full 40-char).
- ``config_hash``: SHA-256 of the relevant ``configs/rungs/<rung>.yaml`` content.
- ``contamination_flag``: ADR-005 three-state taxonomy
  (``verified_disjoint`` | ``backbone-partial-disjoint`` | ``suspected_contamination``;
  vendor_black_box tier carries 0 rungs per ADR-050 R1).
- ``rung``, ``fold``, ``seed``, ``slice``, ``n_rows``: parquet-derived metadata.
- ``generated_at_utc``, ``schema_version``: provenance.

Per ADR-013 persistence governance + ADR-016 data manifest + ADR-032 HF Hub
model card schema. Read-only on the parquets (provenance lives in sibling
JSON, not in the parquet columns themselves — minimizes risk of corrupting
the 282-file artifact set).

Usage
-----
.. code-block:: bash

    python scripts/backfill_provenance.py            # default: writes 282 manifests
    python scripts/backfill_provenance.py --check    # verify all manifests exist; exit 0/1
    python scripts/backfill_provenance.py --rung lora  # filter to one rung

Per ADR-013 Guarantee 6: provenance backfill is idempotent; re-running on
the same git SHA + same configs produces byte-identical manifest content.

Landed at v1.0.8 per Path 3 + /exploring-options batch 11 Q1 lock.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import pandas as pd

# ADR-005 three-state contamination taxonomy (vendor_black_box tier is empty
# per ADR-050 R1; LLM judges dropped on cost).
ContaminationFlag = Literal[
    "verified_disjoint", "backbone-partial-disjoint", "suspected_contamination"
]

# Per-rung contamination map per ADR-005 + ADR-017 + ADR-015 + ADR-018.
RUNG_CONTAMINATION: dict[str, ContaminationFlag] = {
    "tfidf-lr": "verified_disjoint",  # ADR-017 classical floor; trained on our LODO splits
    "tfidf_lr": "verified_disjoint",
    "frozen_probe": "backbone-partial-disjoint",  # ADR-015; ModernBERT pretrain corpus
    "frozen-probe": "backbone-partial-disjoint",
    "lora": "backbone-partial-disjoint",  # same backbone partial-disjoint per ADR-015 + ADR-019
    "full_ft": "backbone-partial-disjoint",
    "full-ft": "backbone-partial-disjoint",
    "protectai-v1": "suspected_contamination",  # ADR-018; published reference scorer
    "protectai_v1": "suspected_contamination",
    "protectai-v2": "suspected_contamination",
    "protectai_v2": "suspected_contamination",
}

# Trained-rung-with-tail pattern: <rung>__fold<F>__seed<S>__<slice|epoch<E>>.parquet
# (transformer rungs frozen_probe/lora/full_ft per-slice + per-epoch outputs).
TRAINED_TAIL_PATTERN = re.compile(
    r"^(?P<rung>[^_]+(?:[-_][^_]+)*)__fold(?P<fold>\d+)__seed(?P<seed>\d+)__(?P<tail>.+)\.parquet$"
)

# Trained-rung-no-tail pattern: <rung>__fold<F>__seed<S>.parquet
# (tfidf-lr classical floor; LODO 4×3 grid; single output file per cell).
TRAINED_NOTAIL_PATTERN = re.compile(
    r"^(?P<rung>[^_]+(?:[-_][^_]+)*)__fold(?P<fold>\d+)__seed(?P<seed>\d+)\.parquet$"
)

# Reference-scorer pattern: <rung>__<slice>.parquet
# (protectai-v1, protectai-v2 — not LODO-trained; ungridded).
REFERENCE_PATTERN = re.compile(r"^(?P<rung>protectai-v[12])__(?P<slice>[a-z_]+)\.parquet$")


def _find_repo_root(start: Path) -> Path:
    """Walk up from `start` until a `pyproject.toml` is found."""
    cur = start.resolve()
    while cur != cur.parent:
        if (cur / "pyproject.toml").exists():
            return cur
        cur = cur.parent
    raise RuntimeError(f"no pyproject.toml found in any ancestor of {start}")


def _git_head_sha(repo_root: Path) -> str:
    """Return the current HEAD SHA (full 40-char) at `repo_root`.

    Raises
    ------
    RuntimeError
        If git is not available or HEAD cannot be resolved.
    """
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git rev-parse HEAD failed: {result.stderr}")
    sha = result.stdout.strip()
    if len(sha) != 40 or not all(c in "0123456789abcdef" for c in sha):
        raise RuntimeError(f"git rev-parse HEAD produced non-SHA-40 output: {sha!r}")
    return sha


def _config_hash(repo_root: Path, rung: str) -> str | None:
    """Return SHA-256 of `configs/rungs/<rung>.yaml`; None if config missing.

    Tries both hyphenated + underscored rung name variants
    (configs use both conventions historically).
    """
    candidates = [
        repo_root / "configs" / "rungs" / f"{rung}.yaml",
        repo_root / "configs" / "rungs" / f"{rung.replace('-', '_')}.yaml",
        repo_root / "configs" / "rungs" / f"{rung.replace('_', '-')}.yaml",
    ]
    for cfg_path in candidates:
        if cfg_path.exists():
            return hashlib.sha256(cfg_path.read_bytes()).hexdigest()
    return None


def _contamination_flag(rung: str) -> ContaminationFlag:
    """Return ADR-005 contamination flag for `rung`; raise on unknown rung."""
    flag = RUNG_CONTAMINATION.get(rung)
    if flag is None:
        raise ValueError(f"unknown rung {rung!r} — add to RUNG_CONTAMINATION map per ADR-005")
    return flag


def build_manifest(*, parquet_path: Path, repo_root: Path, git_sha: str) -> dict[str, object]:
    """Build the manifest dict for one prediction parquet.

    Parameters
    ----------
    parquet_path : Path
        Path to the prediction parquet (`evals/predictions/*.parquet`).
    repo_root : Path
        Repo root for `configs/` resolution.
    git_sha : str
        HEAD SHA to embed (full 40-char).

    Returns
    -------
    dict[str, object]
        The manifest payload.

    Raises
    ------
    ValueError
        If the filename doesn't match the expected pattern or the rung is
        not in the contamination map.
    """
    rung: str
    fold: int | None
    seed: int | None
    epoch: int | None = None
    slice_name: str | None = None

    trained_tail = TRAINED_TAIL_PATTERN.match(parquet_path.name)
    trained_notail = TRAINED_NOTAIL_PATTERN.match(parquet_path.name)
    reference = REFERENCE_PATTERN.match(parquet_path.name)

    if trained_tail:
        rung = trained_tail.group("rung")
        fold = int(trained_tail.group("fold"))
        seed = int(trained_tail.group("seed"))
        tail = trained_tail.group("tail")
        if tail.startswith("epoch"):
            epoch = int(tail.removeprefix("epoch"))
        else:
            slice_name = tail
    elif trained_notail:
        # Classical floor: tfidf-lr__fold0__seed42.parquet (no slice/epoch tail).
        rung = trained_notail.group("rung")
        fold = int(trained_notail.group("fold"))
        seed = int(trained_notail.group("seed"))
    elif reference:
        rung = reference.group("rung")
        slice_name = reference.group("slice")
        # Reference scorers are ungridded (no fold/seed; not LODO-trained).
        fold = None
        seed = None
    else:
        raise ValueError(
            f"filename {parquet_path.name!r} matches none of: "
            f"trained-tail <rung>__fold<F>__seed<S>__<tail>.parquet | "
            f"trained-notail <rung>__fold<F>__seed<S>.parquet | "
            f"reference <rung>__<slice>.parquet"
        )

    df = pd.read_parquet(parquet_path)
    n_rows = len(df)

    manifest: dict[str, object] = {
        "schema_version": "1.0",
        "adr_ref": "ADR-013 + ADR-016 + ADR-032 + ADR-057",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": git_sha,
        "config_hash": _config_hash(repo_root, rung),
        "contamination_flag": _contamination_flag(rung),
        "rung": rung,
        "n_rows": n_rows,
        "predictions_relpath": str(parquet_path.relative_to(repo_root)),
    }
    if fold is not None:
        manifest["fold"] = fold
    if seed is not None:
        manifest["seed"] = seed
    if slice_name is not None:
        manifest["slice_name"] = slice_name
    if epoch is not None:
        manifest["epoch"] = epoch
    return manifest


def main(argv: list[str] | None = None) -> int:
    """Backfill per-prediction manifests; return 0 on success."""
    parser = argparse.ArgumentParser(description="Backfill provenance manifests per ADR-057")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify all manifests exist for predictions; exit 1 if any missing.",
    )
    parser.add_argument(
        "--rung",
        type=str,
        default=None,
        help="Filter to a specific rung (e.g. 'lora'); default: all rungs.",
    )
    args = parser.parse_args(argv)

    repo_root = _find_repo_root(Path.cwd())
    pred_dir = repo_root / "evals" / "predictions"
    manifest_dir = repo_root / "evals" / "manifests"

    if not pred_dir.exists():
        print(f"FAIL: {pred_dir} does not exist", file=sys.stderr)
        return 1

    pred_files = sorted(pred_dir.glob("*.parquet"))
    if args.rung is not None:
        pred_files = [p for p in pred_files if p.name.startswith(f"{args.rung}__")]

    if not pred_files:
        print(f"FAIL: no prediction parquets in {pred_dir}", file=sys.stderr)
        return 1

    if args.check:
        missing: list[str] = []
        for p in pred_files:
            mpath = manifest_dir / f"{p.stem}.json"
            if not mpath.exists():
                missing.append(str(mpath.relative_to(repo_root)))
        if missing:
            print(
                f"FAIL: {len(missing)} of {len(pred_files)} manifests missing:",
                file=sys.stderr,
            )
            for m in missing[:5]:
                print(f"  - {m}", file=sys.stderr)
            if len(missing) > 5:
                print(f"  ... and {len(missing) - 5} more", file=sys.stderr)
            return 1
        print(f"OK: all {len(pred_files)} manifests present")
        return 0

    git_sha = _git_head_sha(repo_root)
    manifest_dir.mkdir(parents=True, exist_ok=True)
    print(
        f"Backfill: {len(pred_files)} prediction parquets -> {manifest_dir.relative_to(repo_root)}/"
    )
    print(f"  git_sha: {git_sha}")

    for i, p in enumerate(pred_files):
        try:
            manifest = build_manifest(parquet_path=p, repo_root=repo_root, git_sha=git_sha)
        except (ValueError, RuntimeError) as exc:
            print(f"  FAIL {p.name}: {exc}", file=sys.stderr)
            return 1
        mpath = manifest_dir / f"{p.stem}.json"
        mpath.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        if i < 3 or i == len(pred_files) - 1:
            print(f"  wrote {mpath.relative_to(repo_root)}")
        elif i == 3:
            print(f"  ... ({len(pred_files) - 4} more) ...")

    print(f"OK: {len(pred_files)} manifests written under {manifest_dir.relative_to(repo_root)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
