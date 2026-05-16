"""Source loaders for the 11-source data slate (per ADR-016 Q1 + ADR-041 Q4).

Public API
----------
`load_source(name: str) -> pd.DataFrame` is the single dispatch entry-point.
Given a source name from `EXPECTED_SOURCE_NAMES`, the function reads
`data/source_manifest.yaml`, resolves the HF or git_repo pin, fetches the
underlying data (HF default cache for HF datasets; clones to `data/raw/git/`
for GitHub sources), applies the per-source normalizer, and returns a
DataFrame with the uniform schema:

    columns = ["text", "label", "source", "row_idx_in_source"]

- `text` is the prompt content (str; non-empty)
- `label` is 0 (benign) or 1 (injection-positive)
- `source` is the source's `name` key from the manifest
- `row_idx_in_source` is the row's original index in the upstream source
  (used by `evals/leakage_report.json` for reverse-trace per ADR-041 Q7)

Per-source quirks (column-renames + label-encoding + benign/positive carve-outs
+ language filters) live in private `_normalize_<source>(...)` helpers in this
file. Each helper is approximately 10-30 LoC; matches the ADR-026 module-size
guideline (less than 50 LoC per module is a guideline; loaders.py is the
canonical "many small helpers" exception).

Caps + selection seeds + language filters apply per-source per ADR-016 Q6 + Q5;
the dispatch fn applies them uniformly after the per-source normalizer runs
(so normalizers stay focused on column-shape + label-encoding).
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pandas as pd
from datasets import Dataset, load_dataset

from src.data.manifest_validation import EXPECTED_SOURCE_NAMES, validate_manifest

# Uniform output schema (per docstring) — used by smoke tests + dedup + splits.
OUTPUT_COLUMNS: tuple[str, ...] = ("text", "label", "source", "row_idx_in_source")

# Repo root + locked cache paths.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_MANIFEST_PATH = _REPO_ROOT / "data" / "source_manifest.yaml"
_GIT_RAW_ROOT = _REPO_ROOT / "data" / "raw" / "git"


class SourceNotFoundError(KeyError):
    """Raised when load_source(name) receives a name not in the locked slate."""


class GitCloneError(RuntimeError):
    """Raised when a git_repo source fails to clone or checkout the pinned SHA."""


# ---------------------------------------------------------------------------
# Public dispatch
# ---------------------------------------------------------------------------


def load_source(name: str) -> pd.DataFrame:
    """Load one source from the locked slate, normalized to the uniform schema.

    Parameters
    ----------
    name : str
        One of the 11 source names from `EXPECTED_SOURCE_NAMES`
        (e.g., `"deepset_prompt_injections"`, `"lmsys_chat_1m"`).

    Returns
    -------
    pandas.DataFrame
        Columns `(text, label, source, row_idx_in_source)`. Row count after
        cap + language filter applied.

    Raises
    ------
    SourceNotFoundError
        If `name` is not in the locked slate.
    FileNotFoundError
        If `data/source_manifest.yaml` is absent (run `make data-fetch` first).
    GitCloneError
        If a git_repo source fails to clone or checkout its pinned SHA.
    """
    if name not in EXPECTED_SOURCE_NAMES:
        raise SourceNotFoundError(
            f"Source {name!r} not in locked slate. Valid: {sorted(EXPECTED_SOURCE_NAMES)}"
        )

    manifest = validate_manifest(_MANIFEST_PATH)
    spec = next(row for row in manifest["sources"] if row["name"] == name)

    if spec["type"] == "hf_dataset":
        raw_df = _normalize_hf_dispatch(name, spec)
    elif spec["type"] == "git_repo":
        raw_df = _normalize_git_dispatch(name, spec)
    else:
        raise ValueError(f"Unknown source type {spec['type']!r} for {name!r}")

    raw_df = _apply_language_filter(raw_df, spec)
    raw_df = _apply_cap(raw_df, spec)

    return _enforce_output_schema(raw_df, name)


# ---------------------------------------------------------------------------
# Filters + caps (applied uniformly after normalization)
# ---------------------------------------------------------------------------


def _apply_language_filter(df: pd.DataFrame, spec: dict[str, Any]) -> pd.DataFrame:
    """Apply the manifest's `language_filter` field (no-op when None).

    Currently supports `en` (English) — see _normalize_lmsys_chat_1m which
    handles language filtering inline because the LMSYS source carries a
    `language` column that the normalizer consumes pre-shape.

    For all other sources, language_filter is None and this is a no-op.
    """
    lang = spec.get("language_filter")
    if lang is None:
        return df
    # LMSYS filtering is applied inside _normalize_lmsys_chat_1m; this is a guard
    # for any future source that declares a language_filter without handling it.
    return df


def _apply_cap(df: pd.DataFrame, spec: dict[str, Any]) -> pd.DataFrame:
    """Apply the manifest's `cap` + `selection_seed` (no-op when cap is None).

    Random subsample without replacement; deterministic per seed.
    """
    cap = spec.get("cap")
    if cap is None or len(df) <= cap:
        return df
    seed = spec["selection_seed"]
    return df.sample(n=cap, random_state=seed).reset_index(drop=True)


def _enforce_output_schema(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """Validate + reorder columns to match OUTPUT_COLUMNS; drop empty-text rows.

    Raises
    ------
    ValueError
        If any required column is missing.
    """
    missing = set(OUTPUT_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(
            f"Source {source_name!r} normalizer missing required columns: {sorted(missing)}"
        )
    df = df[list(OUTPUT_COLUMNS)].copy()
    df = df[df["text"].astype(str).str.len() > 0].reset_index(drop=True)
    df["label"] = df["label"].astype(int)
    df["row_idx_in_source"] = df["row_idx_in_source"].astype(int)
    return df


# ---------------------------------------------------------------------------
# HF dispatch
# ---------------------------------------------------------------------------


def _load_hf_dataset(spec: dict[str, Any]) -> Dataset:
    """Generic HF `load_dataset(repo, name=subset, split=split, revision=sha)` call."""
    kwargs: dict[str, Any] = {"revision": spec["revision_sha"]}
    if spec.get("subset"):
        kwargs["name"] = spec["subset"]
    if spec.get("split"):
        kwargs["split"] = spec["split"]
    ds = load_dataset(spec["hf_id"], **kwargs)
    # When split is specified, load_dataset returns a Dataset; without split, a DatasetDict.
    if not isinstance(ds, Dataset):
        raise ValueError(
            f"Source {spec['name']!r} requires a split for load_dataset to return a Dataset; "
            f"got {type(ds).__name__}. Manifest split={spec.get('split')!r}."
        )
    return ds


def _normalize_hf_dispatch(name: str, spec: dict[str, Any]) -> pd.DataFrame:
    """Route to the per-source HF normalizer based on `name`."""
    normalizers = {
        "deepset_prompt_injections": _normalize_deepset_prompt_injections,
        "lakera_gandalf_ignore_instructions": _normalize_lakera_gandalf,
        "lakera_mosscap_prompt_injection": _normalize_lakera_mosscap,
        "hackaprompt": _normalize_hackaprompt,
        "lmsys_chat_1m": _normalize_lmsys_chat_1m,
        "ultrachat_200k": _normalize_ultrachat_200k,
        "notinject": _normalize_notinject,
        "jbb_behaviors": _normalize_jbb_behaviors,
    }
    if name not in normalizers:
        raise ValueError(f"No HF normalizer registered for {name!r}")
    return normalizers[name](spec)


# ---------------------------------------------------------------------------
# Git dispatch
# ---------------------------------------------------------------------------


def _clone_git_source(spec: dict[str, Any]) -> Path:
    """Clone (or pull) a git_repo source to data/raw/git/<name>/ at pinned SHA.

    Returns the local checkout path. Idempotent — if the local clone already
    sits at the pinned SHA, no network call is made.
    """
    name: str = spec["name"]
    sha: str = spec["revision_sha"]
    url = f"https://github.com/{spec['hf_id']}.git"
    target: Path = _GIT_RAW_ROOT / name
    target.parent.mkdir(parents=True, exist_ok=True)

    if not target.exists():
        try:
            subprocess.run(
                ["git", "clone", url, str(target)], capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as exc:
            raise GitCloneError(f"git clone failed for {url!r}: {exc.stderr!r}") from exc

    # Check current HEAD
    try:
        current = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise GitCloneError(f"git rev-parse failed in {target}: {exc.stderr!r}") from exc

    if current != sha:
        try:
            subprocess.run(
                ["git", "-C", str(target), "fetch", "--quiet"],
                capture_output=True,
                text=True,
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(target), "checkout", sha],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise GitCloneError(f"git checkout {sha} failed in {target}: {exc.stderr!r}") from exc

    return target


def _normalize_git_dispatch(name: str, spec: dict[str, Any]) -> pd.DataFrame:
    """Route to per-source git normalizer based on `name`."""
    normalizers = {
        "xstest": _normalize_xstest,
        "bipia": _normalize_bipia,
        "injecagent": _normalize_injecagent,
    }
    if name not in normalizers:
        raise ValueError(f"No git_repo normalizer registered for {name!r}")
    clone_path = _clone_git_source(spec)
    return normalizers[name](clone_path)


# ---------------------------------------------------------------------------
# Per-source normalizers — HF datasets
# ---------------------------------------------------------------------------


def _normalize_deepset_prompt_injections(spec: dict[str, Any]) -> pd.DataFrame:
    """deepset/prompt-injections — mixed benign+positive; columns `text`+`label`.

    The dataset carries both label=0 (benign) and label=1 (injection-positive).
    Per ADR-016 Q1 deepset is in the "Train positives" pool — we filter to
    label==1 only (the injection-positive subset) so the source contributes to
    the positive class as intended; the benign rows are dropped.
    """
    ds = _load_hf_dataset(spec)
    df = ds.to_pandas()
    df = df[df["label"] == 1].reset_index(drop=False)
    return pd.DataFrame(
        {
            "text": df["text"].astype(str),
            "label": 1,
            "source": "deepset_prompt_injections",
            "row_idx_in_source": df["index"],
        }
    )


def _normalize_lakera_gandalf(spec: dict[str, Any]) -> pd.DataFrame:
    """Lakera/gandalf_ignore_instructions — all positives; column `text`."""
    ds = _load_hf_dataset(spec)
    df = ds.to_pandas().reset_index(drop=False)
    return pd.DataFrame(
        {
            "text": df["text"].astype(str),
            "label": 1,
            "source": "lakera_gandalf_ignore_instructions",
            "row_idx_in_source": df["index"],
        }
    )


def _normalize_lakera_mosscap(spec: dict[str, Any]) -> pd.DataFrame:
    """Lakera/mosscap_prompt_injection — all positives; column `prompt`."""
    ds = _load_hf_dataset(spec)
    df = ds.to_pandas().reset_index(drop=False)
    text_col = "prompt" if "prompt" in df.columns else "text"
    return pd.DataFrame(
        {
            "text": df[text_col].astype(str),
            "label": 1,
            "source": "lakera_mosscap_prompt_injection",
            "row_idx_in_source": df["index"],
        }
    )


def _normalize_hackaprompt(spec: dict[str, Any]) -> pd.DataFrame:
    """hackaprompt/hackaprompt-dataset — all positives; canonical text in `user_input`.

    The HF dataset has fields including `user_input` (the prompt-injection attempt),
    `model_response`, `correct` (whether the injection succeeded against the target),
    `prompt` (the system+user template), `expected_completion`, `level`, `model`.
    Per ADR-016 we use ALL submissions (not just successful ones) — quality-filtered
    HackAPrompt subsample is named as an afterword extension.
    """
    ds = _load_hf_dataset(spec)
    df = ds.to_pandas().reset_index(drop=False)
    text_col = "user_input" if "user_input" in df.columns else "prompt"
    return pd.DataFrame(
        {
            "text": df[text_col].astype(str),
            "label": 1,
            "source": "hackaprompt",
            "row_idx_in_source": df["index"],
        }
    )


def _normalize_lmsys_chat_1m(spec: dict[str, Any]) -> pd.DataFrame:
    """lmsys/lmsys-chat-1m — benigns; extract first user turn from `conversation`.

    The dataset has `conversation` (list of {role, content} dicts) and `language`
    (str e.g. "English"). We:
      1. Filter to language == "English" (per ADR-016 Q5 English-only filter on LMSYS).
      2. Extract the FIRST user turn's content from `conversation` as the benign prompt.
      3. Label all as 0 (benign).
    Subsample cap (10000 at seed=42) is applied by _apply_cap post-normalization.
    """
    ds = _load_hf_dataset(spec)
    df = ds.to_pandas()
    # English-only filter (LMSYS uses full language names).
    df = df[df["language"] == "English"].reset_index(drop=False)
    # Extract first user turn — robust to list-of-dicts schema.
    df["text"] = df["conversation"].apply(_extract_first_user_turn)
    df = df[df["text"].str.len() > 0]
    return pd.DataFrame(
        {
            "text": df["text"].astype(str),
            "label": 0,
            "source": "lmsys_chat_1m",
            "row_idx_in_source": df["index"],
        }
    )


def _extract_first_user_turn(conversation: Any) -> str:
    """Extract the first user-turn `content` field from an LMSYS conversation iterable.

    Accepts list, tuple, or numpy.ndarray (HF datasets to_pandas converts
    list-of-dicts to ndarray; isinstance checks would miss the latter).
    """
    if conversation is None or isinstance(conversation, str):
        return ""
    try:
        iterator = iter(conversation)
    except TypeError:
        return ""
    for turn in iterator:
        if isinstance(turn, dict) and turn.get("role") == "user":
            content = turn.get("content", "")
            return str(content) if content is not None else ""
    return ""


def _normalize_ultrachat_200k(spec: dict[str, Any]) -> pd.DataFrame:
    """HuggingFaceH4/ultrachat_200k — benigns; column `prompt` (direct extract).

    Synthetic user prompts; no language filter (per ADR-016 — UltraChat is
    English by construction). All rows label=0.
    """
    ds = _load_hf_dataset(spec)
    df = ds.to_pandas().reset_index(drop=False)
    return pd.DataFrame(
        {
            "text": df["prompt"].astype(str),
            "label": 0,
            "source": "ultrachat_200k",
            "row_idx_in_source": df["index"],
        }
    )


def _normalize_notinject(spec: dict[str, Any]) -> pd.DataFrame:
    """leolee99/NotInject — OOD over-defense benigns; stack 3 splits (one + two + three).

    Per the dataset card, NotInject ships as three splits — NotInject_one / two /
    three — each with 113 rows of benign-but-injection-looking prompts. We load
    all three and stack to recover ADR-016's N=339 figure. All rows label=0
    (per InjecGuard 2024 methodology — these test over-defense). Column is `prompt`.
    """
    kwargs: dict[str, Any] = {"revision": spec["revision_sha"]}
    if spec.get("subset"):
        kwargs["name"] = spec["subset"]
    frames: list[pd.DataFrame] = []
    row_offset = 0
    for split_name in ("NotInject_one", "NotInject_two", "NotInject_three"):
        ds = load_dataset(spec["hf_id"], split=split_name, **kwargs)
        if not isinstance(ds, Dataset):
            raise ValueError(
                f"NotInject normalizer expected Dataset, got {type(ds).__name__} for {split_name}"
            )
        sdf = ds.to_pandas().reset_index(drop=False)
        text_col = next((c for c in ("prompt", "text", "sentence") if c in sdf.columns), None)
        if text_col is None:
            raise ValueError(f"NotInject normalizer cannot find text column in {list(sdf.columns)}")
        frames.append(
            pd.DataFrame(
                {
                    "text": sdf[text_col].astype(str),
                    "label": 0,
                    "source": "notinject",
                    "row_idx_in_source": sdf["index"] + row_offset,
                }
            )
        )
        row_offset += len(sdf)
    return pd.concat(frames, ignore_index=True)


def _normalize_jbb_behaviors(spec: dict[str, Any]) -> pd.DataFrame:
    """JailbreakBench/JBB-Behaviors — OOD mixed; loads both `harmful` + `benign` splits.

    Per ADR-016 Q1 — JBB-Behaviors contributes 100 harmful (label=1) + 100 benign
    (label=0). The manifest's split field is None (loader determines splits); we
    load both `harmful` and `benign` splits from the `behaviors` subset and stack.
    """
    kwargs: dict[str, Any] = {"revision": spec["revision_sha"]}
    if spec.get("subset"):
        kwargs["name"] = spec["subset"]
    harmful_ds = load_dataset(spec["hf_id"], split="harmful", **kwargs)
    benign_ds = load_dataset(spec["hf_id"], split="benign", **kwargs)
    if not isinstance(harmful_ds, Dataset) or not isinstance(benign_ds, Dataset):
        raise ValueError("JBB-Behaviors normalizer expected Dataset, got DatasetDict")

    harmful_df = harmful_ds.to_pandas().reset_index(drop=False)
    benign_df = benign_ds.to_pandas().reset_index(drop=False)
    text_col = next((c for c in ("Goal", "goal", "behavior") if c in harmful_df.columns), None)
    if text_col is None:
        raise ValueError(
            f"JBB-Behaviors normalizer cannot find text column in {list(harmful_df.columns)}"
        )

    h = pd.DataFrame(
        {
            "text": harmful_df[text_col].astype(str),
            "label": 1,
            "source": "jbb_behaviors",
            "row_idx_in_source": harmful_df["index"],
        }
    )
    b = pd.DataFrame(
        {
            "text": benign_df[text_col].astype(str),
            "label": 0,
            "source": "jbb_behaviors",
            "row_idx_in_source": benign_df["index"] + len(h),  # disjoint indices
        }
    )
    return pd.concat([h, b], ignore_index=True)


# ---------------------------------------------------------------------------
# Per-source normalizers — git_repo sources
# ---------------------------------------------------------------------------


def _normalize_xstest(clone_path: Path) -> pd.DataFrame:
    """paul-rottger/xstest — OOD over-refusal benigns; CSV at xstest_prompts.csv.

    The XSTest repo carries `xstest_prompts.csv` (250 safe + 200 unsafe = 450 rows).
    Columns include `id`, `type`, `prompt`, `focus`. We extract `prompt` and
    assign label based on `type` — types starting with "safe_" are benign (label=0);
    types starting with "contrast_" (the unsafe controls) are label=1.
    """
    # Try canonical path; fall back to alternative known paths.
    candidates = [
        clone_path / "xstest_prompts.csv",
        clone_path / "prompts" / "xstest_v2_prompts.csv",
        clone_path / "prompts.csv",
    ]
    csv_path = next((c for c in candidates if c.exists()), None)
    if csv_path is None:
        raise FileNotFoundError(
            f"XSTest CSV not found in {clone_path}; tried {[str(c) for c in candidates]}"
        )
    df = pd.read_csv(csv_path).reset_index(drop=False)
    df["label"] = df["type"].astype(str).str.startswith("contrast_").astype(int)
    return pd.DataFrame(
        {
            "text": df["prompt"].astype(str),
            "label": df["label"],
            "source": "xstest",
            "row_idx_in_source": df["index"],
        }
    )


def _normalize_bipia(clone_path: Path) -> pd.DataFrame:
    """microsoft/BIPIA — OOD indirect-injection; email-task JSONL.

    BIPIA's `benchmark/email/test.jsonl` carries columns `context` (the
    injection-bearing email body) + `question` (the user task) + `ideal`
    (expected benign output). We extract `context` since it carries the
    embedded indirect-injection content; all rows label=1.

    For broader BIPIA coverage (code/abstract/qa/table tasks) — afterword
    extension per ADR-016 (currently only email task is loaded for Phase 1).
    """
    candidates = [
        clone_path / "benchmark" / "email" / "test.jsonl",
        clone_path / "benchmark" / "email" / "train.jsonl",
        clone_path / "benchmark" / "data" / "email" / "test.json",
    ]
    json_path = next((c for c in candidates if c.exists()), None)
    if json_path is None:
        raise FileNotFoundError(
            f"BIPIA email-task JSON not found in {clone_path}; tried {[str(c) for c in candidates]}"
        )
    df = pd.read_json(json_path, lines=json_path.suffix == ".jsonl").reset_index(drop=False)
    text_col = next(
        (c for c in ("attack_str", "attack", "context", "prompt", "text") if c in df.columns),
        None,
    )
    if text_col is None:
        raise ValueError(f"BIPIA normalizer cannot find text column in {list(df.columns)}")
    return pd.DataFrame(
        {
            "text": df[text_col].astype(str),
            "label": 1,
            "source": "bipia",
            "row_idx_in_source": df["index"],
        }
    )


def _normalize_injecagent(clone_path: Path) -> pd.DataFrame:
    """uiuc-kang-lab/InjecAgent — OOD agentic injection; stack DH + DS attacker cases.

    InjecAgent ships `data/attacker_cases_dh.jsonl` (direct-harm attacker cases)
    plus `data/attacker_cases_ds.jsonl` (data-stealing attacker cases); both have
    `Attacker Instruction` as the agent-injection content. We stack both for
    full OOD agentic coverage (ADR-016 Q1 expected_n=1054 ~= DH + DS combined).
    All rows label=1.
    """
    dh_path = clone_path / "data" / "attacker_cases_dh.jsonl"
    ds_path = clone_path / "data" / "attacker_cases_ds.jsonl"
    if not dh_path.exists() and not ds_path.exists():
        raise FileNotFoundError(
            f"InjecAgent attacker-cases JSONLs not found in {clone_path}/data/; "
            f"tried {dh_path.name} + {ds_path.name}"
        )
    frames: list[pd.DataFrame] = []
    row_offset = 0
    for path in (dh_path, ds_path):
        if not path.exists():
            continue
        sub = pd.read_json(path, lines=True).reset_index(drop=False)
        text_col = next(
            (
                c
                for c in ("Attacker Instruction", "attacker_instruction", "instruction")
                if c in sub.columns
            ),
            None,
        )
        if text_col is None:
            raise ValueError(
                f"InjecAgent normalizer cannot find text column in {list(sub.columns)} ({path.name})"
            )
        frames.append(
            pd.DataFrame(
                {
                    "text": sub[text_col].astype(str),
                    "label": 1,
                    "source": "injecagent",
                    "row_idx_in_source": sub["index"] + row_offset,
                }
            )
        )
        row_offset += len(sub)
    return pd.concat(frames, ignore_index=True)
