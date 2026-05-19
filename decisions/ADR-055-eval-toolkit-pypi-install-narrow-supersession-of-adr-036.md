---
adr_id: "055"
slug: eval-toolkit-pypi-install-narrow-supersession-of-adr-036
title: eval-toolkit installs from PyPI (not git+https) at v0.40.0+ — narrow supersession of ADR-036 "git URL is the only viable spec format"
date: 2026-05-19
status: Accepted
claim_id: CLAIM-055
claim: >-
  ADR-036 §Context claims "All three are own-authored on GitHub (not on PyPI)
  — git URL is the only viable spec format." This premise is false for
  eval-toolkit as of v0.40.0 (released 2026-05-18 via Trusted Publishing
  OIDC at https://pypi.org/project/eval-toolkit/). v1.0.8 switches the
  eval-toolkit pin from `git+https://github.com/brandon-behring/eval-toolkit@v0.39.0`
  to the PyPI install spec `eval-toolkit==0.40.0` (PEP 508 version
  specifier). uv.lock continues to provide byte-level reproducibility
  via SHA-256 of the PyPI wheel artifact. runpod-deploy + research_toolkit
  retain git+https tag-pin per ADR-036 (runpod-deploy v1.1.0 may also
  switch per separate v1.1.0 governance; research_toolkit not yet on PyPI).
  The remainder of ADR-036 — tag-pin convention, freeze-for-submission-
  window discipline, 3 bump triggers (blocking-bug + critical-security +
  reviewer-feedback-patch), uv.lock byte-level backstop — is unchanged.
source: transcripts/2026-05-19__phase-13-pypi-install-and-platt-beta.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.0.8 close, `pyproject.toml` specifies `eval-toolkit==0.40.0`
  (PyPI install) not `eval-toolkit @ git+https://...@v0.39.0`. `uv pip show
  eval-toolkit` reports `Version: 0.40.0` + `Location:
  .venv/lib/python3.13/site-packages/` (not git-clone source). uv.lock
  source line shows `registry = "https://pypi.org/simple"` not
  `git = "https://github.com/..."`. 171+/171+ smoke tests pass post-bump.
  ADR-036 frontmatter `superseded_by` updated to `["055"]` in-place per
  ADR-029 convention.
closing_commit: v1.0.8
supersedes: [ADR-036]
superseded_by: []
references:
  - https://pypi.org/project/eval-toolkit/0.40.0/
  - https://github.com/brandon-behring/eval-toolkit/releases/tag/v0.40.0
  - https://peps.python.org/pep-0508/
transcript: transcripts/2026-05-19__phase-13-pypi-install-and-platt-beta.md
---

# ADR-055 — eval-toolkit installs from PyPI (narrow supersession of ADR-036)

## Status

Accepted (2026-05-19; landed in v1.0.8 patch alongside Platt + Beta
calibrator wiring + manifest backfill).

## Context

[ADR-036](ADR-036-library-version-pins-tag-pin-plus-freeze.md) was
written at Phase 0-08 (2026-05-16) when none of the three own-authored
libraries (eval-toolkit + runpod-deploy + research_toolkit) had been
published to PyPI. The ADR's §Context says verbatim: *"All three are
own-authored on GitHub (not on PyPI) — git URL is the only viable spec
format."* That premise was true at 2026-05-16; it is no longer true.

**eval-toolkit v0.40.0** (released 2026-05-18; PyPI link
[here](https://pypi.org/project/eval-toolkit/0.40.0/)) is the first
PyPI publication for eval-toolkit, via Trusted Publishing OIDC (per
runpod-deploy v0.7.1's release.yml workflow pattern, adopted by
eval-toolkit). The release workflow auto-publishes sdist + wheel on
every `v*` tag push.

Three reasons we should consume from PyPI rather than git+https:

1. **Install speed**: `pip install eval-toolkit==0.40.0` from PyPI
   doesn't require a git clone + setuptools build; ~10x faster on
   cold install + uv cache.
2. **uv.lock SHA backstop is stronger via PyPI**: the lock file records
   the exact wheel SHA-256, not a git rev. PyPI artifacts are immutable
   (re-uploads of the same version are forbidden); git rev can be
   force-pushed (which we ban per CLAUDE.md but the SHA-pinning is
   defense-in-depth).
3. **Aligns with the consumer-facing pattern**: PyPI is the canonical
   install path Python consumers expect; demonstrating PyPI consumption
   sets the reproducibility bar at "any clone of this repo can
   `uv sync` without GitHub access to eval-toolkit." Methodology
   submission reviewers may not have git access to private clones
   (they don't here, but the pattern is robust).

## Decision

Switch the eval-toolkit pin in `pyproject.toml`:

```diff
- "eval-toolkit @ git+https://github.com/brandon-behring/eval-toolkit@v0.39.0",
+ "eval-toolkit==0.40.0",
```

`uv sync` regenerates `uv.lock` to reference PyPI registry source.

**Scope of supersession**: narrow — only the "git URL is the only
viable spec format" sub-claim in ADR-036 §Context. The remainder of
ADR-036 is preserved:

- **Tag-pin convention**: replaced with PEP 508 `==<version>` specifier
  (equivalent semantics; readability preserved — pyproject answers
  "what version is in scope" at a glance).
- **Freeze-for-submission-window**: preserved. We're past the original
  v1.0.0 submission tag (now at v1.0.x patch series per ADR-033); bump
  trigger #3 ("reviewer-feedback / post-submission patch") authorizes
  this bump. v1.0.8 is the closing-of-NEXT_STEPS-§1 sweep per Path 3.
- **3 bump triggers**: preserved. The bump satisfies trigger #3
  (post-submission patch; v1.0.x discipline per ADR-033).
- **uv.lock byte-level backstop**: preserved (lock now carries PyPI
  wheel SHA-256 instead of git rev SHA).
- **Per-library requires-python compatibility**: preserved
  (eval-toolkit v0.40.0 requires `python>=3.13` per its pyproject.toml;
  matches our `.python-version` pin per ADR-037).

**Out of scope**:

- **runpod-deploy**: not switched at v1.0.8 (planned for v1.1.0
  per Path 3; this ADR's scope is eval-toolkit only).
- **research_toolkit**: not yet on PyPI as of v1.0.8 audit; remains
  git+https tag-pin per ADR-036.

## Consequences

### Positive

- **PyPI-resolvable install** — any clone of this repo can `uv sync`
  without GitHub access to brandon-behring/eval-toolkit; methodology
  reviewer reproducibility improved.
- **Faster cold install** — no git clone or setuptools build step.
- **uv.lock wheel-SHA backstop** — PyPI artifacts are immutable once
  published; the lock's recorded SHA-256 of the wheel cannot be
  retroactively changed by upstream (git rev can be force-pushed
  in theory; PyPI artifact uploads are append-only).
- **Consumer-pattern alignment** — methodology submission demonstrates
  the canonical Python install path.

### Negative

- **ADR-036 §Context premise must be retired** — the "git URL is the
  only viable spec format" claim is no longer load-bearing. Handled via
  this narrow-supersession ADR + `superseded_by: [055]` frontmatter
  edit on ADR-036.
- **runpod-deploy + research_toolkit pin styles diverge** — eval-toolkit
  on `==<version>` (PyPI), runpod-deploy + research_toolkit on
  `git+https://...@v<tag>` (GitHub). Mitigation: clear comments in
  `pyproject.toml` for each; `decisions/library_imports.md` version
  pin table documents the per-library spec format.

### Neutral

- Tag-pin readability ≈ PEP 508 version-specifier readability. Both
  surface the version at a glance in pyproject.toml.
- uv.lock format is uv-internal; lock content changes (source field)
  but the byte-level-reproducibility guarantee is preserved.

## Alternatives Considered

### A. Keep git+https (do not switch)

Stay on `eval-toolkit @ git+https://...@v0.40.0`. **Rejected**: the
user explicitly asked for PyPI install ("make sure this repo uses it
from pypi"). PyPI is the consumer-expected format for Python
distribution; demonstrating it sets the better reproducibility bar.

### B. Switch but keep at v0.39.0

Switch source format but stay at v0.39.0 (which is also on PyPI as
of 2026-05-18 release wave). **Rejected**: v0.40.0 adds Platt + Beta
calibrators (eval-toolkit#43 closed; v1.0.8 Subsection C consumes them
per ADR-056). The bump + format-switch are coupled work.

### C. Switch + also re-walk ADR-036 entirely (broad supersession)

Write a single ADR superseding ADR-036 in whole (the freeze policy
plus the git URL claim plus the bump-trigger protocol). **Rejected**:
ADR-036's freeze + bump-trigger discipline is still load-bearing;
narrowly superseding only the "git URL only" sub-claim preserves the
rest of the governance trail without re-litigation.

## Links

- [ADR-036 — Library version pins (tag-pin + freeze)](ADR-036-library-version-pins-tag-pin-plus-freeze.md) — narrowly superseded on the "git URL is the only viable spec format" sub-claim only; freeze + bump-triggers + uv.lock backstop preserved.
- [ADR-033 — Github release strategy (rehearsal + submission)](ADR-033-github-release-strategy-rehearsal-plus-submission.md) — v1.0.x patch discipline that authorizes this bump under trigger #3.
- [ADR-037 — requires-python ≥ 3.13](ADR-037-python-version-pin-3-13.md) — eval-toolkit v0.40.0's requires-python matches.
- [eval-toolkit v0.40.0 PyPI](https://pypi.org/project/eval-toolkit/0.40.0/) — the artifact.
- [eval-toolkit#43](https://github.com/brandon-behring/eval-toolkit/issues/43) — Platt + Beta request that motivated the v0.40.0 bump.
