---
adr_id: "037"
slug: python-version-pin-3-13
title: Python version pin — ratify requires-python >=3.13 (matches existing .python-version + bc8ce4e commit)
date: 2026-05-16
status: Accepted
claim_id: CLAIM-037
claim: Phase 0-08 locks SPEC_GREENFIELD ledger row 310 (Python version pin) at requires-python >=3.13 — ratifying the existing pre-Phase-0-08 state. The .python-version file at repo root reads 3.13 (committed at bc8ce4e). The pyproject.toml requires-python line reads >=3.13 (committed at bc8ce4e — chore plus pin Python to >=3.13 plus add .python-version per the prior session). Phase 0-08 Q1 walk surfaced four options — (A) ratify >=3.13; (B) tighten to ==3.13 dot star; (C) loosen to >=3.12; (D) loosen to >=3.11. Option A chosen — zero churn ratification with documented rationale. Rationale — Python 3.13 in active support through October 2029 per PEP 602 release schedule; uv handles installability transparently (uv sync auto-installs Python 3.13 from the pinned .python-version regardless of reviewer's system Python); the three load-bearing libraries (eval-toolkit at v0.31.0 plus runpod-deploy at v0.7.7 plus research_toolkit at v1.9.1 per ADR-036) are own-authored so per-library requires-python constraints are under Brandon's control; the prior bc8ce4e commit selected >=3.13 with rationale baked in; uv.lock provides byte-level reproducibility on top. Phase 0-08 close runs uv sync to verify all three load-bearing libraries install cleanly under requires-python >=3.13; if any library blocks the >=3.13 floor, fix-forward is either (a) bump the upstream library requires-python to >=3.13 in a same-day patch, or (b) loosen this ADR pin to >=3.12 via superseding ADR. Tightening to ==3.13 dot star (option B) rejected — brittle; refuses 3.14+ which is overly strict; uv.lock already provides byte-level reproducibility so exact-minor pin adds no value. Loosening to >=3.12 (option C) rejected — contradicts the already-committed .python-version equals 3.13; uv handles installability transparently so the wider compatibility option C unlocks is not material. Loosening to >=3.11 (option D) rejected — same as C; bigger gap; loses 3.13 features further. Limitation — 3.13 is recent (Oct 2024 release); some downstream wheels may not have 3.13 builds yet — but uv defaults to building from source for missing wheels so installability is preserved (slower first install; not blocking). Extension condition — 3.13-only feature dependency emerges (e.g., free-threaded build for CPU-bound bootstrap loop) tightens the pin via superseding ADR; 3.13 wheel-availability issue on RunPod base images loosens to >=3.12 via superseding ADR; currently expected to not be an issue.
source: SPEC_GREENFIELD.md §Tech-Stack ledger row 310 + Phase 0-08 walk Q1 + pre-existing commit bc8ce4e
acceptance_criterion: SPEC_GREENFIELD ledger row 310 carries locked-to-requires-python-3-13 status (see ADR-037); pyproject.toml line 7 reads requires-python equals quote >=3.13 quote (unchanged from prior commit bc8ce4e); .python-version file at repo root reads 3.13 (unchanged from prior commit bc8ce4e); uv sync at Phase 0-08 close succeeds without per-library requires-python conflict (verified manually at sub-session close — if any of the three libraries blocks 3.13, this ADR cannot lock until the conflict is resolved via either upstream patch or superseding pin); tests/test_invariants.py contains skip-marked stub test_python_version_pin_at_3_13 asserting (1) pyproject.toml requires-python equals >=3.13; (2) .python-version contains exactly 3.13; (3) sys.version_info major-minor is at least (3, 13) when running pytest (the test fails if invoked on Python <3.13 even though Phase 1 plus implementation defers active enforcement); SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit:
references:
  - https://devguide.python.org/versions/
  - https://docs.astral.sh/uv/concepts/python-versions/#installing-python
  - https://peps.python.org/pep-0602/
  - decisions/ADR-036-library-version-pins-tag-pin-plus-freeze.md
transcript: transcripts/2026-05-16__phase-0-08__process-tech-stack-acceptance.md
---

# ADR-037: Python version pin — ratify `requires-python >=3.13`

## Status

Accepted (2026-05-16). Ratifies the existing state established by prior commit bc8ce4e (`chore: pin Python to >=3.13; add .python-version`). Closes SPEC_GREENFIELD ledger row 310 (Python version pin). Companion to ADR-036 (library version pins — `uv sync` verification depends on Python 3.13 + library pins being mutually compatible).

## Context

`requires-python` in `pyproject.toml` controls who can install the project. `.python-version` (consumed by `pyenv` / `uv python pin`) controls which Python version is **used** in the dev environment. The two should agree.

**Existing state at Phase 0-08 entry** (heavily pre-constraining):
- `.python-version` = `3.13` (committed at bc8ce4e).
- `pyproject.toml` line 7: `requires-python = ">=3.13"` (committed at bc8ce4e).
- Prior commit bc8ce4e: `chore: pin Python to >=3.13; add .python-version`.

So Python `>=3.13` is **already in the repo**. Row 310 is effectively a ratification with rationale, not an open choice. Four options were considered (per Phase 0-08 Q1 walk):

(A) Ratify `>=3.13` — existing state; ADR documents the lock.
(B) Tighten to `==3.13.*` — brittle.
(C) Loosen to `>=3.12` — contradicts the existing pin.
(D) Loosen to `>=3.11` — same as C; bigger gap.

User selection at Q1 walk: **A**.

## Decision

### Locked Python version pin

**`pyproject.toml`** line 7 (unchanged from bc8ce4e):

```toml
requires-python = ">=3.13"
```

**`.python-version`** (unchanged from bc8ce4e):

```
3.13
```

### Rationale

- **Active support** — Python 3.13 in active-support phase through October 2029 per PEP 602 annual release schedule. EOL is well past the submission's audit lifetime.
- **`uv` handles installability transparently** — any reviewer running `make smoke` (T1 per ADR-034) or `make eval-from-hub` (T0 per ADR-034) invokes `uv sync` which auto-installs Python 3.13 from the pinned `.python-version` regardless of the reviewer's system Python. Wider-compatibility pins (option C/D) don't materially help reviewer install friction.
- **Library compatibility** — the three load-bearing libraries (`eval-toolkit v0.31.0` + `runpod-deploy v0.7.7` + `research_toolkit v1.9.1` per ADR-036) are own-authored; per-library `requires-python` constraints are under Brandon's control. Verified at Phase 0-08 close via `uv sync` — if any library blocks `>=3.13`, this ADR cannot lock until the conflict is resolved via either upstream patch or superseding pin.
- **`uv.lock` provides byte-level reproducibility on top** — already committed per kit-level discipline; tag pin (per ADR-036) + Python pin (this ADR) + lockfile = canonical reproducible install.
- **Aligns with prior commit bc8ce4e** — ratifies a deliberate prior choice rather than introducing new constraint.

### Phase 0-08 close verification

`uv sync` runs at Phase 0-08 close (after both ADR-036 library pins are committed) to verify the full dependency tree resolves cleanly under `requires-python >=3.13`. The check is:

```bash
uv sync --extra dev
```

Success = all three load-bearing libraries + dev dependencies install. Failure = one of the libraries has a `requires-python` constraint below `>=3.13` (would block install); fix-forward per the limitation section below.

## Consequences

### Positive

- **Zero churn** — existing artefacts (`.python-version`, `pyproject.toml`, `uv.lock`) already encode this pin; ADR ratifies what's already true.
- **Active-support window through Oct 2029** — pins to a version that won't reach EOL during the submission's audit lifetime.
- **Modern type-system features available** — PEP 695 type parameter syntax + PEP 701 f-string improvements + free-threaded experimental build all available if needed.
- **`uv`-driven workflow installability** — reviewer install friction is independent of the pin width; any reviewer running `make smoke` / `make eval-from-hub` gets Python 3.13 auto-installed.

### Negative / cost

- **3.13 is recent (Oct 2024 release)** — some downstream wheels may not have 3.13 builds yet. Mitigation: `uv` defaults to building from source for missing wheels; slower first install but not blocking. Mitigation: the three load-bearing libraries are own-authored so version compatibility is under Brandon's control.
- **`requires-python >=3.13` blocks reviewers on system Python ≤3.12 from installing directly via `pip install -e .`** — but `uv` is the documented install path (per `Makefile` `install` target = `uv sync --extra dev`); reviewers using `pip` directly fall outside the supported install path.

### Neutral

- **`==3.13.*` exact-minor pin not chosen** — `uv.lock` already provides byte-level reproducibility; exact-minor adds no new value.
- **Future Python releases (3.14, 3.15)** automatically allowed by `>=3.13` — bumps are not blocked; only floor is enforced.

### Limitation

3.13 is recent — `uv sync` at Phase 0-08 close is the verification gate. If any of the three load-bearing libraries has a `requires-python` constraint below `>=3.13` that breaks compatibility (rare since 3.13 is back-compatible with most 3.10+ code), fix-forward via:

- **(a)** Bump the upstream library `requires-python` to `>=3.13` in a same-day patch (Brandon is the upstream author for all three).
- **(b)** Loosen this ADR's pin to `>=3.12` via superseding ADR; update `.python-version` to `3.12` + `pyproject.toml` to `>=3.12`.

### Extension condition for revisit

- **3.13-only feature dependency emerges** — e.g., free-threaded build for a CPU-bound bootstrap loop, PEP 695 syntax that 3.12 doesn't support — tighten pin to `>=3.13` (already there) with a note in the writeup; no ADR supersession needed for this case.
- **3.13 wheel-availability problem on RunPod base images** — observed at Phase 1+ entry — loosen pin to `>=3.12` via superseding ADR; update `.python-version` + `pyproject.toml`. Currently expected to not be an issue since RunPod base images target current Python versions.
- **Python 3.14 release (Oct 2025) becomes the new active-support floor years later** — currently no action needed; `>=3.13` accommodates 3.14 + 3.15 + future.

## Alternatives Considered

- **(B) `==3.13.*` exact-minor pin** — brittle; refuses 3.14+; `uv.lock` already provides byte-level reproducibility. Rejected per Q1 walk.
- **(C) `>=3.12` loosen** — contradicts the existing pin at bc8ce4e; doesn't materially expand reviewer base since `uv` handles installability transparently. Rejected per Q1 walk.
- **(D) `>=3.11` loosen further** — same as C; bigger gap; loses more 3.13 features. Rejected per Q1 walk.

## References

- Python release schedule (PEP 602) — https://devguide.python.org/versions/
- `uv` python pinning docs — https://docs.astral.sh/uv/concepts/python-versions/#installing-python
- PEP 602 annual release cadence — https://peps.python.org/pep-0602/
- ADR-036 (library version pins — `uv sync` verification depends on this pin)

## Transcript

See `transcripts/2026-05-16__phase-0-08__process-tech-stack-acceptance.md` for the conversation that led to this decision (Q1 walk + option A ratification).
