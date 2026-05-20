# Repo audit - 2026-05-18

> **Status (resolved 2026-05-20).** Internal audit conducted 2026-05-18 in advance of
> v1.0.0 submission. All 5 P0 blockers + the majority of P1/P2 findings are now
> resolved (reviewer URLs return 200; remote CI + Publish workflows green;
> public docs `[TBD]` placeholders cleared; HF Hub T0 rungs published per ADR-058;
> Quarto render path narrowed). The remaining ADR-frontmatter governance gaps
> (`closing_commit` on ADR-051 + ADR-052) are addressed in the follow-up
> 2026-05-20 audit cycle (see new ADR-072).
>
> Preserved here under `decisions/audits/` as part of the SDD audit trail
> (per ADR-040 phase-0 audit-findings discipline). The resolution narrative
> is in `CHANGELOG.md` from v0.9.0-rc2 onward.

Internal audit. Blunt by design. Submission-readiness is judged against the repo's
own ADR-039 / Phase 5 gates, not by a looser "some artifacts exist locally"
standard.

## Executive verdict

**Not submission-ready.**

The core implementation has real substance: data artifacts exist, 282 prediction
parquets exist locally, metrics/bootstrap/MDE/figure artifacts exist, `pytest`
and smoke pass, coverage is above the declared floor, and the cost ledger is well
under cap. That is not enough for this repo's own submission gate.

The blocking problems are public-surface and governance problems: reviewer URLs
404, remote CI/Publish runs are failing, `main` is 17 commits ahead of `origin`,
the local `v0.9.0-rc1` tag has not reached `origin`, `v1.0.0` is missing, Quarto
cannot be trusted to publish the intended site, public docs still contain
placeholders, the HF Hub/T0 path is unfinished, and strict formatting/type gates
fail locally.

## P0 blockers

### P0 blocker - Reviewer URLs and remote release gates fail

ADR-039 says the `v1.0.0` source pin, live Quarto site, and release page must
resolve. They do not.

- `https://github.com/brandon-behring/prompt-injection-detection-submission/tree/v1.0.0` returns 404.
- `https://brandon-behring.github.io/prompt-injection-detection-submission/` returns 404.
- `https://github.com/brandon-behring/prompt-injection-detection-submission/releases/tag/v1.0.0` returns 404.
- The actual remote is `https://github.com/brandon-behring/prompt-injection-detection-prototype.git`, while docs point at `prompt-injection-detection-submission`.
- Local tags: `v0.0.0`, `v0.9.0-rc1`.
- Remote tags: only `v0.0.0`.
- `v1.0.0` does not exist locally or remotely.

This alone fails the submission gate.

### P0 blocker - Remote CI and Publish are failing

`gh run list` shows the latest remote CI and Publish runs are failures. The
current local head has not been pushed, so there is no green remote evidence for
the 17 local commits.

Latest observed failed runs include:

- CI failure on `main` at `ba21fa1`, run `26020271633`.
- Publish Quarto site failure on `main` at `ba21fa1`, run `26020271608`.
- Earlier CI/Publish failures at `1dc5569`, `ca21801`, and `1170805`.

ADR-039 explicitly requires green release/publish evidence. Current remote state
does not satisfy it.

### P0 blocker - Quarto site inputs are incomplete and render scope is unsafe

`_quarto.yml` declares a site that references missing files:

- `WRITEUP/eval-design.md`
- `WRITEUP/methodology-guarantees.md`
- `WRITEUP/limitations-and-future-work.md`
- `WRITEUP/data-decisions.md`
- `WRITEUP/model-rungs.md`
- `WRITEUP/threshold-policy.md`
- `WRITEUP/reference-scorer-audit.md`
- `styles.css`

Earlier render attempt without secrets failed before render because Quarto tried
to validate required env vars from `.env.example`:

- `HF_TOKEN`
- `RUNPOD_API_KEY`
- `OPENAI_API_KEY`

Earlier render attempt with dummy env vars began rendering broad repo content,
including ignored/private material such as `data/raw/git/...` and
`transcripts/*.md`, instead of only the intended site pages. That is a publish
scope problem, not just a missing-file problem.

### P0 blocker - Public-facing docs still contain unresolved placeholders

Current placeholder counts:

- `README.md`: 15 `[TBD]` / `[OPEN]` hits.
- `WRITEUP.md`: 4 `[TBD]` / `[OPEN]` hits.
- `SPEC_SHEET.md`: 23 `[TBD]` / `[OPEN]` / `in progress` / `pending commit` hits.
- `NEXT_STEPS.md`: 3 `[TBD]` / `[OPEN]` hits.

Additional docs still read like templates or older phase-state documents:

- `EVIDENCE.md` is still largely a template, including `[TBD: scorer name]` and
  `[TBD: populated at Phase 5]` sections.
- `docs/THREAT_MODEL.md` still says scope decisions are `[OPEN: resolved at
  Phase 0]`.
- `docs/REPRODUCIBILITY.md` still references
  `prompt-injection-detection-prototype`, `make diagnostics-smoke`, and
  `make canonical-eval`, while current Makefile targets differ.
- `docs/HYPERPARAMETER_DISCLOSURE.md` is still mostly `[TBD]`.

This is fatal for reviewer-readiness. The repo claims methodology discipline,
but the public narrative still exposes unresolved scaffolding.

### P0 blocker - HF Hub / T0 reproducibility is unfinished

ADR-032 and ADR-034 make HF Hub publication and `make eval-from-hub` part of the
reproducibility story. The implementation is not done.

- `scripts/eval_from_hub.py` resolves `BBehring/prompt-injection-<rung>` and
  supports `--dry-run`.
- Non-dry-run returns exit code 2 and says the HF Hub repo is not yet published.
- `scripts/generate_model_cards.py` is absent.
- No command evidence shows any model repo was published.
- `WRITEUP/reproducibility.md` still says T0 is a skeleton.

Either finish this path or write a superseding ADR that explicitly waives it for
submission.

## P1 high findings

### P1 high - Strict local quality gates fail

Current local checks:

- `uv run python scripts/regenerate_audit.py --check`: passed.
- `uv run ruff check .`: passed.
- `uv run ruff format --check .`: failed.
- `uv run mypy --strict .`: failed.

Formatting failures:

- `scripts/cost_rollup.py`
- `scripts/run_inference_battery.py`
- `scripts/run_val_inference.py`
- `tests/smoke/test_smoke_pipeline.py`
- `tests/smoke/test_splits_smoke.py`
- `tests/test_invariants.py`

Mypy failures:

- `src/eval/figures.py:101`: returning `Any` from function declared to return
  `Figure`.
- `src/eval/figures.py:242`: returning `Any` from function declared to return
  `Figure`.
- `src/data/audit.py:222`: `CrossSplitLeakageCheck` incompatible with
  `LeakageCheck` protocol because `name` is read-only where the protocol expects
  a settable variable.

### P1 high - Tests pass, but invariant readiness is not real

Current test status is good but not submission-grade:

- `uv run pytest -q`: `182 passed, 38 skipped`.
- `uv run pytest -m smoke -q`: `169 passed, 51 deselected`.
- Coverage: `89.82%`, above the 70% floor.

The problem is the 38 skipped invariant tests. ADR-039 gate 3 says invariant
stubs should be unskipped and green at submission. They are not. Passing pytest
does not prove submission readiness under the repo's own contract.

### P1 high - Metrics artifacts contradict the writeup caveat on single-class slices

`WRITEUP.md` says BIPIA and InjecAgent are all-positive, NotInject is
all-negative, and AUROC/AUPRC are mathematically undefined on single-class
slices. The metric battery itself only reports both-class slices:

- `evals/metrics/per_cell.parquet`: 114 rows, slices
  `jbb_behaviors`, `pooled_ood`, `xstest`.

But later analysis artifacts include AUPRC cells for single-class slices:

- `evals/bootstrap/marginal_cells.parquet`: 66 rows, includes
  `bipia`, `injecagent`.
- `evals/audit/cross_fold_ci_audit.parquet`: 31 rows, includes
  `bipia`, `injecagent`, `notinject`.
- `evals/audit/mde_per_cell.parquet`: 142 rows, includes
  `bipia`, `injecagent`.

Observed examples from earlier inspection showed perfect or degenerate AUPRC
values such as `1.0` for all-positive slices and `0.0` for all-negative slices.
That may be a library behavior, but it is not aligned with the writeup's stated
methodology. Fix the analysis filters or revise the writeup and explain the
chosen convention explicitly.

### P1 high - ADR/spec drift remains

ADR-049 and ADR-050 are accepted but have empty frontmatter fields:

- `closing_commit:`
- `supersedes:`
- `superseded_by:`

`SUBMISSION_AUDIT.md` regenerates cleanly, but that only proves mechanical
sync. It does not prove the frontmatter carries complete closure metadata.

`SPEC_SHEET.md` still contains older status language, including:

- Phase sections marked `in progress`.
- Phase 5 gates with unchecked boxes.
- older rung/reference-scorer language that conflicts with ADR-050 narrowing.
- placeholder sections under future/open questions.

### P1 high - Local work is not pushed

Current branch state:

- `main` is ahead of `origin/main` by 17 commits.
- Remote CI evidence is therefore for an older state.
- Latest local head: `e224e07 docs: WRITEUP §5+§10 - fill final placeholders +
  clean remaining [OPEN] locks`.

This blocks reviewer URLs and any remote Actions-based acceptance gate.

## P2 medium findings

### P2 medium - Untracked local logs remain

Seven untracked logs are present:

- `artifacts/local/bootstrap_seed1_20260518T084831Z.log`
- `artifacts/local/bootstrap_seed2_20260518T094354Z.log`
- `artifacts/local/cv_clt_ci_20260518T091956Z.log`
- `artifacts/local/marginal_bootstrap_20260518T091942Z.log`
- `artifacts/local/val_inference_20260518T075027Z.log`
- `artifacts/local/val_inference_frozen_20260518T080452Z.log`
- `artifacts/local/val_inference_lora_20260518T083008Z.log`

Decide whether these are evidence artifacts to commit or runtime logs to ignore.
Do not leave them ambiguous at submission.

### P2 medium - Repo naming is inconsistent

Local directory and documentation use `prompt-injection-detection-submission`.
The actual remote is `prompt-injection-detection-prototype`. Some docs point to
the `submission` repo, while `docs/REPRODUCIBILITY.md` points to the `prototype`
repo.

Pick one canonical public identity and update:

- remote URL or docs,
- GitHub Pages URL,
- release URLs,
- clone instructions,
- README/title text if needed.

### P2 medium - Release notes are stale

`CHANGELOG.md` still has only `[Unreleased]` and `[0.0.0]`. It describes
`v0.9.0-rc1` and `v1.0.0` as conventions but does not record the current local
`v0.9.0-rc1` tag or the 17 local commits after `origin/main`.

## What looks solid

These are not enough for submission, but they are real progress.

- Data audit exists and reports `leakage_clean: true`.
- `evals/leakage_report.json` reports zero exact-hash overlaps and zero cosine
  overlaps at threshold 0.85.
- `evals/contamination_scan.json` reports no A-005 trigger fires.
- `evals/dedup_calibration.json` exists with 50-pair holdout evidence and
  locked threshold 0.80.
- Prediction inventory exists locally:
  - total prediction parquets: 282.
  - `frozen-probe`: 24.
  - `frozen_probe`: 60.
  - `full-ft`: 24.
  - `lora`: 84.
  - `protectai-v1`: 9.
  - `protectai-v2`: 9.
  - `tfidf-lr`: 72.
  - validation prediction parquets: 36.
- Eval outputs exist:
  - `evals/metrics/per_cell.parquet`: 114 rows.
  - `evals/bootstrap/paired_cells.parquet`: 40 rows.
  - `evals/bootstrap/paired_cells_seed2.parquet`: 40 rows.
  - `evals/bootstrap/marginal_cells.parquet`: 66 rows.
  - `evals/audit/cross_fold_ci_audit.parquet`: 31 rows.
  - `evals/audit/mde_per_cell.parquet`: 142 rows.
  - `evals/operating_points/dual_policy.parquet`: 72 rows.
- `docs/plots/F1.svg` through `F7.svg` and matching `.meta.json` files exist.
- Cost rollup passes:
  - 8 runpod-deploy manifests.
  - 0 API logs.
  - cumulative spend: `$15.74`.
  - soft flag: `$80.00`.
  - soft cap: `$125.00`.
  - hard cap: `$200.00`.
- `pytest`, smoke, and coverage pass locally.

## Remediation queue

1. **Fix public docs and evidence ledger first.**
   - Replace remaining placeholders in `README.md`, `WRITEUP.md`,
     `SPEC_SHEET.md`, `NEXT_STEPS.md`, `docs/THREAT_MODEL.md`,
     `docs/REPRODUCIBILITY.md`, and `docs/HYPERPARAMETER_DISCLOSURE.md`.
   - Populate `EVIDENCE.md` with actual ProtectAI v1/v2 contamination audit
     findings or explicitly mark what is unverifiable.
   - Align README headline tables and findings with actual artifacts.

2. **Fix Quarto publishing.**
   - Either create the seven missing `WRITEUP/` spokes or remove them from
     `_quarto.yml`.
   - Add `styles.css` or remove the CSS reference.
   - Configure Quarto to render only intended site files.
   - Prevent private/ignored files such as `transcripts/*.md` and
     `data/raw/git/**` from entering the rendered site.
   - Make local `make site` work without requiring real secrets.

3. **Fix CI/runtime pins and remote workflow failures.**
   - The CI workflow currently uses Python 3.11 while `pyproject.toml` requires
     Python `>=3.13` and `.python-version` is `3.13`.
   - Move GitHub Actions to Python 3.13.
   - Re-run CI and Publish on the current local head after pushing.

4. **Fix local format/type failures.**
   - Run formatter or manually reformat the six listed files.
   - Fix or type-cast the two `src/eval/figures.py` return values.
   - Fix the `CrossSplitLeakageCheck` protocol mismatch in `src/data/audit.py`
     without weakening the library-first design.

5. **Resolve the single-class metric inconsistency.**
   - Decide whether AUPRC/AUROC on all-positive/all-negative slices are skipped,
     encoded as null, or intentionally treated as degenerate values.
   - Apply the same convention across metrics, marginal bootstrap, cross-fold
     CI, MDE, figures, and writeup.
   - Regenerate affected artifacts after the convention is fixed.

6. **Finish or waive HF Hub/T0 reproduction.**
   - If keeping ADR-032/ADR-034: implement model card generation, publish the
     selected rungs, make non-dry-run `eval_from_hub.py` work, and document
     exact commands plus expected score match.
   - If not keeping it: write a superseding ADR and remove the T0 claim from
     public docs.

7. **Update ADR and spec closure metadata.**
   - Fill `closing_commit` for ADR-049 and ADR-050 after the relevant commits
     are identified.
   - Fill `supersedes` / `superseded_by` where needed.
   - Update `SPEC_SHEET.md` to match ADR-050 and current phase reality.
   - Re-run `scripts/regenerate_audit.py --check`.

8. **Push and verify release surfaces.**
   - Push the 17 local commits.
   - Push `v0.9.0-rc1` if it remains the rehearsal tag.
   - Fix remote CI/Publish until green.
   - Create `v1.0.0` only after local and remote gates are clean.
   - Verify all reviewer URLs return 200 or expected redirects.

9. **Resolve untracked local logs.**
   - Commit them if they are reviewer evidence.
   - Add a targeted ignore rule if they are runtime logs.
   - Do not leave `git status` ambiguous.

## Evidence appendix

### Git state

Command:

```bash
git status --short --branch
git branch -vv
git remote -v
git tag --list 'v*'
git ls-remote --tags origin 'v*'
```

Observed:

```text
## main...origin/main [ahead 17]
?? artifacts/local/bootstrap_seed1_20260518T084831Z.log
?? artifacts/local/bootstrap_seed2_20260518T094354Z.log
?? artifacts/local/cv_clt_ci_20260518T091956Z.log
?? artifacts/local/marginal_bootstrap_20260518T091942Z.log
?? artifacts/local/val_inference_20260518T075027Z.log
?? artifacts/local/val_inference_frozen_20260518T080452Z.log
?? artifacts/local/val_inference_lora_20260518T083008Z.log
main e224e07 [origin/main: ahead 17] docs: WRITEUP §5+§10 - fill final placeholders + clean remaining [OPEN] locks
origin https://github.com/brandon-behring/prompt-injection-detection-prototype.git
local tags: v0.0.0, v0.9.0-rc1
remote tags: v0.0.0 only
```

### Remote CI / Publish

Command:

```bash
gh run list --limit 8 --json databaseId,workflowName,headBranch,headSha,status,conclusion,event,createdAt,url
```

Observed summary:

```text
CI failure, main, ba21fa1, run 26020271633
Publish Quarto site failure, main, ba21fa1, run 26020271608
Publish failure, main, 1dc5569, run 26010974746
CI failure, main, 1dc5569, run 26010974733
Publish failure, main, ca21801, run 26008443515
CI failure, main, ca21801, run 26008443507
CI failure, PR branch chore/eval-toolkit-v0.34.0-migration, 5eba4ac, run 26000240659
CI failure, main, 1170805, run 26000211150
```

### Reviewer URLs

Command:

```bash
curl -I -L --max-time 15 <url>
```

Observed:

```text
https://github.com/brandon-behring/prompt-injection-detection-submission/tree/v1.0.0 -> HTTP/2 404
https://brandon-behring.github.io/prompt-injection-detection-submission/ -> HTTP/2 404
https://github.com/brandon-behring/prompt-injection-detection-submission/releases/tag/v1.0.0 -> HTTP/2 404
https://github.com/brandon-behring/prompt-injection-detection-prototype -> HTTP/2 200
https://brandon-behring.github.io/prompt-injection-detection-prototype/ -> HTTP/2 404
```

### Local checks

Commands and results:

```text
uv run python scripts/regenerate_audit.py --check -> pass
uv run ruff check . -> pass
uv run ruff format --check . -> fail, 6 files would be reformatted
uv run mypy --strict . -> fail, 3 errors
uv run pytest -q -> 182 passed, 38 skipped
uv run pytest -m smoke -q -> 169 passed, 51 deselected
COVERAGE_FILE=/tmp/pid-repo-audit.coverage uv run pytest --cov --cov-fail-under=70 --cov-report=term-missing -q -> 89.82%, pass
uv run python scripts/cost_rollup.py --check -> pass, $15.74 cumulative spend
```

### Placeholder counts

Command:

```bash
rg -n "\[TBD|\[OPEN\]" <file> | wc -l
```

Observed:

```text
README.md: 15
WRITEUP.md: 4
SPEC_SHEET.md: 23 when including [TBD], [OPEN], "in progress", and "pending commit"
NEXT_STEPS.md: 3
```

### Missing Quarto inputs

Command:

```bash
for f in WRITEUP/eval-design.md WRITEUP/methodology-guarantees.md \
  WRITEUP/limitations-and-future-work.md WRITEUP/data-decisions.md \
  WRITEUP/model-rungs.md WRITEUP/threshold-policy.md \
  WRITEUP/reference-scorer-audit.md WRITEUP/reproducibility.md styles.css; do
  [ -f "$f" ] || echo "$f"
done
```

Observed missing:

```text
WRITEUP/eval-design.md
WRITEUP/methodology-guarantees.md
WRITEUP/limitations-and-future-work.md
WRITEUP/data-decisions.md
WRITEUP/model-rungs.md
WRITEUP/threshold-policy.md
WRITEUP/reference-scorer-audit.md
styles.css
```

`WRITEUP/reproducibility.md` exists.

### Artifact inventory

Command:

```bash
uv run python - <<'PY'
from pathlib import Path
import collections
import pandas as pd
preds = list(Path('evals/predictions').glob('*.parquet'))
print(len(preds))
print(collections.Counter(p.stem.split('__')[0] for p in preds))
for p in [...]:
    df = pd.read_parquet(p)
    print(p, len(df))
PY
```

Observed:

```text
prediction_files: 282
frozen-probe: 24
frozen_probe: 60
full-ft: 24
lora: 84
protectai-v1: 9
protectai-v2: 9
tfidf-lr: 72
val_prediction_files: 36
evals/metrics/per_cell.parquet: 114 rows, slices ['jbb_behaviors', 'pooled_ood', 'xstest']
evals/bootstrap/paired_cells.parquet: 40 rows, slices ['jbb_behaviors', 'xstest']
evals/bootstrap/paired_cells_seed2.parquet: 40 rows, slices ['jbb_behaviors', 'xstest']
evals/bootstrap/marginal_cells.parquet: 66 rows, slices ['bipia', 'injecagent', 'jbb_behaviors', 'pooled_ood', 'xstest']
evals/audit/cross_fold_ci_audit.parquet: 31 rows, slices ['bipia', 'iid', 'injecagent', 'jbb_behaviors', 'notinject', 'pooled_ood', 'xstest']
evals/audit/mde_per_cell.parquet: 142 rows, slices ['bipia', 'injecagent', 'jbb_behaviors', 'pooled_ood', 'xstest']
evals/operating_points/dual_policy.parquet: 72 rows
```

## Final note

This repo is close in the sense that the local computational artifacts exist and
the core scripts mostly run. It is not close in the sense that a reviewer could
open the public URL today and trust a coherent, complete submission. The next
work should be release-surface cleanup, not more model or metric work.
