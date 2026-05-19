---
adr_id: "059"
slug: runpod-deploy-pypi-install-narrow-supersession-of-adr-036
title: runpod-deploy installs from PyPI (not git+https) at v0.8.4+ — narrow supersession of ADR-036 "git URL is the only viable spec format" sub-claim for runpod-deploy
date: 2026-05-19
status: Accepted
claim_id: CLAIM-059
claim: >-
  ADR-036 §Context claims "All three are own-authored on GitHub (not on PyPI)
  — git URL is the only viable spec format." This premise was already false
  for eval-toolkit (closed by ADR-055 at v1.0.8). It is now also false for
  runpod-deploy as of v0.7.1 (Trusted Publishing OIDC live on PyPI; v0.7.7
  through v0.8.4 all published as wheels). v1.1.0 switches the runpod-deploy
  pin from `runpod-deploy @ git+https://github.com/brandon-behring/runpod-deploy@v0.7.7`
  to the PyPI install spec `runpod-deploy==0.8.4` (PEP 508 version specifier;
  mirrors the ADR-055 pattern for eval-toolkit). uv.lock continues to provide
  byte-level reproducibility via SHA-256 of the PyPI wheel artifact. research_toolkit
  retains git+https tag-pin per ADR-036 (not yet on PyPI; will get its own
  narrow ADR when published). The remainder of ADR-036 — tag-pin convention,
  freeze-for-submission-window discipline, 3 bump triggers (blocking-bug +
  critical-security + reviewer-feedback-patch), uv.lock byte-level backstop —
  is unchanged. v0.8.x also brings a load-bearing schema break: legacy
  `stop: {on_success, on_failure}` was REMOVED in v0.8.3; the 3 affected
  headline-*.yaml configs were migrated to `lifecycle:` schema in Commit 1
  of 3 BEFORE this pin bump in Commit 2 of 3. Three /exploring-options 2026-05-19
  execution-level locks govern this commit: Q3 (narrow scope; mirror ADR-055),
  Q4 (auto-continue-on-green-CI; v1.0.9 CI green at 4m42s 2026-05-19T02:03Z
  triggered Phase B start), Q5 (3 logical sub-commits as load-bearing audit trail).
source: transcripts/2026-05-19__v1-1-0-runpod-deploy-and-deberta.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.1.0 close, `pyproject.toml` specifies `runpod-deploy==0.8.4`
  (PyPI install) not `runpod-deploy @ git+https://...@v0.7.7`. `uv pip show
  runpod-deploy` reports `Version: 0.8.4` + `Location: .venv/...site-packages/`
  (not git-clone source). uv.lock entry shows `registry = "https://pypi.org/simple"`
  not `git = "https://github.com/..."`. `make headline-dry-run` (validate
  --all on each of the 3 migrated configs) exits 0 with `[image-registry] ok`
  per #97 consumption. The runpod_deploy_long_ssh.py shim is DELETED in
  the same commit per no-orphaned-code invariant; `budget.ssh_ready_timeout_sec: 600`
  override appears in all 3 configs per #88 consumption. ADR-036 frontmatter
  `superseded_by` updated to `["055", "059"]` in-place per ADR-029 convention.
closing_commit: v1.1.0
supersedes: [ADR-036]
superseded_by: []
references:
  - decisions/ADR-036-library-version-pins-tag-pin-plus-freeze.md
  - decisions/ADR-055-eval-toolkit-pypi-install-narrow-supersession-of-adr-036.md
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md
  - https://pypi.org/project/runpod-deploy/0.8.4/
  - https://github.com/brandon-behring/runpod-deploy/issues/88
  - https://github.com/brandon-behring/runpod-deploy/issues/90
  - https://github.com/brandon-behring/runpod-deploy/issues/97
transcript: transcripts/2026-05-19__v1-1-0-runpod-deploy-and-deberta.md
---

# ADR-059 — runpod-deploy installs from PyPI (narrow supersession of ADR-036)

## Status

Accepted (2026-05-19; lands in v1.1.0 Commit 2 of 3 alongside shim
deletion + #88 / #90 / #97 consumption + 3-config lifecycle: schema
adoption that landed in Commit 1 of 3).

## Context

[ADR-036](ADR-036-library-version-pins-tag-pin-plus-freeze.md) was
written at Phase 0-08 (2026-05-16). Its §Context paragraph says:

> "All three are own-authored on GitHub (not on PyPI) — git URL is
> the only viable spec format."

That premise was true at 2026-05-16. Two PyPI publishes have since
falsified it:

1. **eval-toolkit v0.40.0** went on PyPI 2026-05-18 via Trusted
   Publishing OIDC. [ADR-055](ADR-055-eval-toolkit-pypi-install-narrow-supersession-of-adr-036.md)
   narrowly superseded ADR-036 for eval-toolkit at v1.0.8.
2. **runpod-deploy v0.7.1+** has been on PyPI since 2026-05-15 via
   Trusted Publishing OIDC. The submission-window freeze deferred
   any spec format change until v1.1.0; the v1.1.0 patch is the
   natural landing site (no submission timing constraint).

This ADR-059 is the second narrow supersession of ADR-036, scoped
**only to runpod-deploy spec format**. The 3rd own-authored library
research_toolkit remains git+https; when it eventually publishes to
PyPI, a similar narrow ADR will land. ADR-036 is not retired; only
the "git URL is the only viable spec format" sub-claim is superseded
twice (once narrowly per library).

## Decision

Switch runpod-deploy pin format from git+https to PyPI install spec.
This is one of three coupled changes that land together in Commit 2
of 3 (per /exploring-options 2026-05-19 Q5 lock):

### Subsection 1 — pin format switch

`pyproject.toml [project.optional-dependencies] dev`:

```
# OLD (v1.0.x):
"runpod-deploy @ git+https://github.com/brandon-behring/runpod-deploy@v0.7.7"

# NEW (v1.1.0):
"runpod-deploy==0.8.4"
```

`uv.lock` regenerated. `uv pip show runpod-deploy` reports `Version: 0.8.4`
from PyPI registry, not git-clone source.

### Subsection 2 — Drop scripts/runpod_deploy_long_ssh.py monkey-patch shim (#88 closed)

The v1.0.x shim (`scripts/runpod_deploy_long_ssh.py`) monkey-patched
`runpod_deploy.provider._wait_for_pod_ready` to bump the SSH-ready
timeout from 240s to 600s. v0.8.2 closed
[#88](https://github.com/brandon-behring/runpod-deploy/issues/88)
with configurable `budget.ssh_ready_timeout_sec` (default 900s). v1.1.0
deletes the shim + adds explicit override `budget.ssh_ready_timeout_sec: 600`
to all 3 headline-*.yaml configs (matches the shim's 600s value;
preserves the same effective behavior).

Per no-orphaned-code invariant + library-first invariant, the shim is
DELETED in the same commit as the pin bump. `git grep
runpod_deploy_long_ssh` returns 0 results in the post-commit tree.

### Subsection 3 — Adopt #90 lifecycle.on_success: recycle for DeBERTa (Commit 3 wiring)

[#90](https://github.com/brandon-behring/runpod-deploy/issues/90)
closed with `lifecycle.on_success: recycle` semantics: pod stays warm
after successful run, available for next-fire re-use. Per
/exploring-options 2026-05-19 Q2 lock, the v1.1.0 DeBERTa-v3-base
medium ablation uses recycle to share one pod across 2 training fires
(chunk-and-average + head-truncation), saving ~$1-2 + ~3-5 min per
retry vs full teardown. This is consumed in Commit 3 of 3 (new
`configs/runpod/headline-deberta.yaml`); the consumption is enabled
by the v0.8.4 pin bump in this commit.

### Subsection 4 — Adopt #97 validate --check-image-registry (consumed automatically)

[#97](https://github.com/brandon-behring/runpod-deploy/issues/97)
closed with `validate --all` now invoking an image-registry HEAD-check
by default in v0.8.x. Output: `[image-registry] ok: 'runpod/pytorch:...'
exists on Docker Hub`. No explicit flag required (it's the default in
`--all`); `make headline-dry-run` automatically gains pre-flight image
existence verification. Catches phantom Docker Hub tags before billing.
The HEAD-check is library-first consumption (no project-side
re-implementation needed).

## Consequences

- **Reproducibility**: uv.lock continues to record SHA-256 of the
  installed wheel; PyPI install matches git+https tag pin for
  byte-level reproducibility purposes. Source-provenance backstop is
  the v0.8.4 PyPI artifact tagged to GitHub commit SHA (verifiable
  via `pip index versions runpod-deploy` + GitHub release SHA
  cross-check, mirroring the ADR-055 verification path).
- **Install speed**: PyPI install avoids git clone overhead
  (~3-5s per `uv sync` invocation); same advantage as ADR-055.
- **ADR-036 narrow supersession scope**: this ADR adds runpod-deploy
  to the existing eval-toolkit narrow-supersession scope of ADR-055.
  ADR-036's frontmatter gains `superseded_by: ["055", "059"]` per
  ADR-029 in-place convention. The substantive content of ADR-036
  (tag-pin discipline + freeze + bump triggers + uv.lock backstop)
  is unchanged.
- **Future research_toolkit publish**: when research_toolkit
  eventually publishes to PyPI, a 3rd narrow ADR (ADR-NNN) will mirror
  this pattern. ADR-036 is not "retired" — its substantive guidance
  applies to research_toolkit (the only remaining git+https pin), and
  the spec-format sub-claim has been narrowly superseded twice (once
  per PyPI-published library).
- **Schema migration prerequisite**: Commit 1 of 3 (`stop:` → `lifecycle:`)
  was MANDATORY before this Commit 2; v0.8.3+ raises `KeyError:
  'unknown root keys: [lifecycle]'` against legacy `stop:` configs.
  The 3-sub-commit Q5 lock sequence makes the dependency explicit;
  each sub-commit is independently revertible.
- **GPU spend posture unchanged**: ADR-020 cost-cap discipline
  ($200 hard cap; $125 per-job soft) unaffected. v0.8.4 budget block
  semantics identical to v0.7.x; the new `ssh_ready_timeout_sec` is
  pure pre-flight timing, not a spend dimension.

## Linked ADRs

- **Superseded (narrow, runpod-deploy spec format only)**: ADR-036
  (the "git URL is the only viable spec format" sub-claim).
- **Referenced**: ADR-055 (the eval-toolkit precedent; this ADR mirrors
  the pattern); ADR-020 (RunPod orchestration cost discipline,
  unchanged); ADR-013 (pre-teardown checklist, now enforced via
  `lifecycle.on_success: delete` for the 3 migrated headline configs).
- **Source**: /exploring-options 2026-05-19 Q3 lock (narrow ADR-059
  mirroring ADR-055 pattern); /exploring-options preliminary-analysis
  lock (mandatory config migration before bump).

## Transcript

Decisions surfaced during the 2026-05-19 v1.1.0 planning session
(`/exploring-options` 6-question execution-lock; transcript at
`transcripts/2026-05-19__v1-1-0-runpod-deploy-and-deberta.md`).
