"""Publish canonical fold0/seed42 checkpoints to HF Hub per ADR-032 + Q10 lock.

Uploads:
- ``evals/checkpoints/frozen_probe/fold0/seed42/checkpoint-1090/``
  → ``BBehring/prompt-injection-frozen-probe``
- ``evals/checkpoints/lora/fold0/seed42/checkpoint-1090/``
  → ``BBehring/prompt-injection-lora``

full-FT is skipped per ADR-050 (weights missing locally; FUSE EIO crash
at X11 lost the checkpoint).

Library-first: uses ``huggingface_hub.HfApi`` for repo creation +
``upload_folder`` for the actual transfer. Authentication via the
existing ``~/.cache/huggingface/token`` per ADR-035 secrets discipline
(do not pass tokens through CLI args or env vars in this script).

Idempotent: if the HF repo already exists, the upload becomes an update
(no duplicate creation). Files unchanged on remote are deduplicated by
HF Hub's content-addressed storage.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

PUBLISHED_RUNGS = [
    (
        "frozen-probe",
        "frozen_probe",
        "BBehring/prompt-injection-frozen-probe",
    ),
    (
        "lora",
        "lora",
        "BBehring/prompt-injection-lora",
    ),
]
CANONICAL_CHECKPOINT = "checkpoint-1090"


def _upload_one(api: HfApi, rung: str, rung_key: str, repo_id: str, dry_run: bool) -> None:
    """Create + populate one HF Hub repo from the canonical local checkpoint dir."""
    src_dir = (
        _REPO_ROOT / "evals" / "checkpoints" / rung_key / "fold0" / "seed42" / CANONICAL_CHECKPOINT
    )
    if not src_dir.exists():
        raise FileNotFoundError(
            f"checkpoint directory does not exist: {src_dir}. Cannot publish {repo_id}."
        )

    print(f"[publish-hub] {rung} -> {repo_id}")
    print(f"  src: {src_dir}")
    files = sorted(p.name for p in src_dir.iterdir() if p.is_file())
    print(f"  files: {files}")

    if dry_run:
        print("  --dry-run; skipping create + upload")
        return

    # Create repo (idempotent — passes silently if it exists).
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="model",
            exist_ok=True,
            private=False,
        )
        print("  create_repo: ok")
    except HfHubHTTPError as err:
        raise RuntimeError(f"failed to create_repo {repo_id}: {err}") from err

    # Upload inference-needed files only — skip optimizer/scheduler/rng training state
    # (those are ~600 MB of throwaway weights per checkpoint; T0 reproducibility needs
    # only the deployable model + tokenizer + README per ADR-032 model card schema).
    inference_only_patterns = [
        "README.md",
        "config.json",
        "model.safetensors",
        "adapter_config.json",
        "adapter_model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
    ]
    try:
        commit_info = api.upload_folder(
            folder_path=str(src_dir),
            repo_id=repo_id,
            repo_type="model",
            commit_message=f"Publish {rung} canonical fold0/seed42 (v1.0.0 submission tag)",
            allow_patterns=inference_only_patterns,
        )
        print(f"  upload_folder: {commit_info.commit_url}")
    except HfHubHTTPError as err:
        raise RuntimeError(f"failed to upload_folder to {repo_id}: {err}") from err


def main() -> int:
    """Publish all rungs in PUBLISHED_RUNGS to HF Hub."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip create + upload; print resolved paths only.",
    )
    parser.add_argument(
        "--rung",
        choices=[r[0] for r in PUBLISHED_RUNGS],
        help="Publish only this rung (default: all).",
    )
    args = parser.parse_args()

    # Prefer the write-scope token (HF_TOKEN_WRITE per the project's .env.local
    # convention); fall back to HF_TOKEN, then to the on-disk cached token used
    # by `huggingface-cli login` (which may be read-only and trigger 403 on
    # create_repo). Per ADR-035 secrets discipline, tokens are never printed.
    token = os.environ.get("HF_TOKEN_WRITE") or os.environ.get("HF_TOKEN")
    if token:
        api = HfApi(token=token)
        print("[publish-hub] using HF_TOKEN_WRITE / HF_TOKEN from environment")
    else:
        api = HfApi()
        print("[publish-hub] using ~/.cache/huggingface/token (no env token set)")
    whoami = api.whoami()
    print(f"[publish-hub] authenticated as: {whoami.get('name', '<unknown>')}")

    rungs_to_publish = (
        [r for r in PUBLISHED_RUNGS if r[0] == args.rung] if args.rung else PUBLISHED_RUNGS
    )

    for rung, rung_key, repo_id in rungs_to_publish:
        _upload_one(api, rung=rung, rung_key=rung_key, repo_id=repo_id, dry_run=args.dry_run)

    print(f"[publish-hub] done ({len(rungs_to_publish)} rungs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
