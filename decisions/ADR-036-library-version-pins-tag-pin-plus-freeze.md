---
adr_id: "036"
slug: library-version-pins-tag-pin-plus-freeze
title: Library version pins — tag pin to latest stable plus freeze for submission window (eval-toolkit v0.31.0 + runpod-deploy v0.7.7 + research_toolkit v1.9.1)
date: 2026-05-16
status: Accepted
claim_id: CLAIM-036
claim: Phase 0-08 locks SPEC_GREENFIELD ledger rows 307 plus 308 plus 309 (the three library version pins) in a single bundled ADR at tag pin to latest stable plus freeze for submission window policy. Specific versions — eval-toolkit at v0.31.0 (latest as of 2026-05-16) plus runpod-deploy at v0.7.7 (pre-locked by ADR-020 plus matching latest) plus research_toolkit at v1.9.1 (latest as of 2026-05-16; same toolkit that produced the existing docs/research/ dossier). pyproject.toml dependencies stanza becomes the canonical pinning location with git+https URL plus tag specifier syntax — quote-eval-toolkit at git plus https github dot com slash brandon-behring slash eval-toolkit at v0.31.0 unquote plus matching specifiers for the other two libraries. uv.lock provides byte-level reproducibility on top of the tag pin (already committed per kit-level discipline). Pinning strategy — tag pin chosen over SHA pin (readability — pyproject answers what version is in scope at a glance) and over branch pin (auto-track contradicts methodology-submission audit-trail framing). Update policy — freeze for submission window (Phase 0-08 close until v1.0.0 submission tag per ADR-033); no routine bumps during Phase 1+ work; bump-triggers are exactly three — (1) blocking bug discovered upstream that breaks our use-pattern per decisions/library_imports.md, (2) critical security fix in the upstream (a CVE-grade event), or (3) reviewer-feedback-driven post-submission patch per ADR-033 v1.0.x discipline (post-submission only — submission tag freezes the pin). Routine the upstream has a new release is NOT a bump trigger. Each bump produces a new commit plus optional ADR cross-reference (the bump amends the version pin but does NOT supersede ADR-036 — the discipline is locked; the specific version moves). Freeze policy expires at v2.0.0 (per ADR-033 major-bump discipline) without superseding ADR — major-bump library pins get re-walked. Per-library requires-python compatibility — each upstream library has its own requires-python constraint; pinning above the strictest is fine; the three libraries are own-authored so Brandon controls each upstream constraint. Phase 0-08 close runs uv sync to verify all three install cleanly under the requires-python >=3.13 lock (per ADR-037); if any library blocks the >=3.13 floor, fix-forward is either (a) bump the upstream library requires-python to >=3.13 in a same-day patch, or (b) loosen ADR-037 pin to >=3.12 via superseding ADR. Limitation — tag pin trusts upstream tag immutability; force-pushed tags (which CLAUDE.md bans for own-authored repos) would invalidate the lock; defense-in-depth is uv.lock plus upstream commit discipline. Extension condition — post-submission iteration lasting longer than one patch cycle (v1.0.x) should re-evaluate the freeze policy; year-long freeze becomes a maintenance liability rather than a stability asset; freeze expires at v2.0.0.
source: SPEC_GREENFIELD.md §Tech-Stack ledger rows 307 + 308 + 309 + Phase 0-08 walk Q2
acceptance_criterion: SPEC_GREENFIELD ledger rows 307 plus 308 plus 309 each carry locked-to-tag-pin-plus-freeze-with-specific-version status (see ADR-036); pyproject.toml lines 8-14 contain the three uncommented dependency specifiers in the form library-name at git plus https URL plus tag (eval-toolkit at v0.31.0; runpod-deploy at v0.7.7; research_toolkit at v1.9.1); uv sync runs cleanly under requires-python >=3.13 at Phase 0-08 close (verified manually at sub-session close); uv.lock is updated with the three library versions plus their transitive dependencies; decisions/library_imports.md gains a "Version pinning lock" subsection documenting the freeze policy plus the bump-trigger protocol; tests/test_invariants.py contains skip-marked stub test_pyproject_library_version_pins asserting (1) pyproject.toml dependencies stanza contains the three libraries at the locked versions (regex-grep for the specific tags); (2) uv.lock includes the three libraries (verified via uv.lock parse plus version field check); (3) no library is pinned to main branch or a branch other than a tagged version (regex check excluding the at-tag pattern); SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit: 5427b95
references:
  - https://peps.python.org/pep-0508/
  - https://docs.astral.sh/uv/concepts/projects/dependencies/#git
  - https://semver.org/
  - https://github.com/brandon-behring/eval-toolkit
  - https://github.com/brandon-behring/runpod-deploy
  - https://github.com/brandon-behring/research_toolkit
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md
  - decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md
  - decisions/ADR-037-python-version-pin-3-13.md
  - decisions/library_imports.md
transcript: transcripts/2026-05-16__phase-0-08__process-tech-stack-acceptance.md
---

# ADR-036: Library version pins — tag pin to latest stable + freeze for submission window

## Status

Accepted (2026-05-16). Closes the three §Tech-Stack ledger rows for library version pins (307 eval-toolkit + 308 runpod-deploy + 309 research_toolkit) in a single bundled ADR. Companion to ADR-020 (which pre-locked `runpod-deploy 0.7.7`), ADR-033 (release strategy — freeze cadence aligns with `v0.9.0-rc1` rehearsal + `v1.0.0` submission tags), ADR-037 (Python version pin — `requires-python >=3.13`), and the library-first discipline encoded in `decisions/library_imports.md`.

## Context

The three load-bearing libraries per `SPEC_GREENFIELD.md` §Tech-Stack:

| Library | Latest tag (fetched 2026-05-16) | Pre-mentioned | Use surface |
|---|---|---|---|
| `eval-toolkit` | `v0.31.0` | Implicit via ADR-006 + ADR-021..025 | Bootstrap CIs + calibration + thresholds + paired tests (per `library_imports.md`) |
| `runpod-deploy` | `v0.7.7` | **Explicit in ADR-020** | GPU failover + cost cap + cost reconciliation + dry-run preflight |
| `research_toolkit` | `v1.9.1` | Implicit via existing `docs/research/` dossier | Dossier pipeline skills (per `library_imports.md`) |

All three are own-authored on GitHub (not on PyPI) — git URL is the only viable spec format. The pinning choice is **tag pin vs SHA pin vs branch pin**, plus the **update policy** (freeze for submission window vs on-demand bump vs auto-track-latest at Phase 1 entry).

Four strategies were considered (per Phase 0-08 Q2 walk):

(A) Tag pin to latest stable + freeze for submission window.
(B) SHA pin (40-char SHAs in pyproject) — strictest but ugly.
(C) Branch pin to `main` + auto-track — drift-risk; loses audit clarity.
(D) Tag pin with on-demand bump (no freeze) — defeats audit trail.

User selection at Q2 walk: **A**.

## Decision

### Locked versions

| Library | Tag | Rationale |
|---|---|---|
| `eval-toolkit` | `v0.31.0` | Latest stable as of 2026-05-16 — primitives in `library_imports.md` (`bootstrap_ci`, `paired_bootstrap_diff`, `cv_clt_ci`, `paired_bootstrap_op_point_diff`, calibration battery, `TargetFPRSelector`, `TargetRecallSelector`) are present in this version |
| `runpod-deploy` | `v0.7.7` | Pre-locked by ADR-020 (compute infrastructure); matches latest as of 2026-05-16; primitives (`pod.gpu_order`, `budget.cost_cap_usd`, `flash-attention-fallback` recipe, `manifest-summary`) are present |
| `research_toolkit` | `v1.9.1` | Latest as of 2026-05-16; same toolkit that produced the existing `docs/research/` dossier (per `library_imports.md` and `docs/research/README.md`) |

### `pyproject.toml` dependencies stanza

```toml
[project]
requires-python = ">=3.13"   # per ADR-037
dependencies = [
    "eval-toolkit @ git+https://github.com/brandon-behring/eval-toolkit@v0.31.0",
    "runpod-deploy @ git+https://github.com/brandon-behring/runpod-deploy@v0.7.7",
    "research_toolkit @ git+https://github.com/brandon-behring/research_toolkit@v1.9.1",
]
```

`uv.lock` (already committed per kit-level discipline) provides byte-level reproducibility on top of the tag pin — pinning a specific commit SHA + transitive-dependency tree.

### Pinning strategy rationale

**Tag pin chosen over SHA pin** because tag pin is self-documenting — a reviewer reading pyproject.toml immediately sees the version in scope; SHA pin requires `git show <sha>` to decode. Both have equivalent reproducibility when combined with `uv.lock`.

**Tag pin chosen over branch pin (`@main`)** because branch pin can't answer "what version was in scope?" without lockfile consultation; branch advances between rehearsal tag and submission tag would silently change the codebase; contradicts methodology-submission audit-trail framing.

### Freeze policy

**Library versions are frozen for the submission window** (Phase 0-08 close → `v1.0.0` submission tag per ADR-033). No routine bumps during Phase 1+ work.

**Bump-triggers** — exactly three valid triggers:

1. **Blocking bug discovered upstream** that breaks our use-pattern (per `decisions/library_imports.md`). The bump comes with a corresponding upstream issue + commit reference + an entry in `decisions/upstream_issues.md`.
2. **Critical security fix** in the upstream (a CVE-grade event affecting one of the three libraries).
3. **Reviewer-feedback-driven post-submission patch** per ADR-033 `v1.0.x` discipline (post-submission only; submission tag freezes the pin).

**Routine "the upstream has a new release" is NOT a bump trigger** — the pin stays at the locked version unless a real need surfaces.

### Bump procedure

When a valid bump trigger fires:

1. Identify the new target version (lowest version that satisfies the trigger; minimal bump).
2. Update `pyproject.toml` dependency specifier.
3. Run `uv sync` to update `uv.lock`.
4. Add a row to `decisions/upstream_issues.md` referencing the trigger (issue URL / CVE / reviewer-feedback link).
5. The bump produces a new commit; the commit message references ADR-036 + the trigger (does NOT supersede ADR-036 — the discipline is locked; the specific version moves).

### Freeze expiration

Freeze policy expires at `v2.0.0` (per ADR-033 major-bump discipline) without superseding ADR. At `v2.0.0`, library version pins get re-walked in a new ADR — the year-long-freeze maintenance liability is recognized.

## Consequences

### Positive

- **Self-documenting `pyproject.toml`** — tag pin answers "what version?" without lockfile consultation.
- **Byte-level reproducibility** — `uv.lock` + tag pin + `requires-python >=3.13` is canonical reproducible install.
- **Freeze aligns with ADR-033 cadence** — libraries lock at Phase 0-08; both `v0.9.0-rc1` rehearsal + `v1.0.0` submission use the same library versions; no mid-flight bumps.
- **Audit trail clarity** — every bump goes through `upstream_issues.md` with a trigger reference; reviewer can audit "why did this version change?" trivially.
- **Aligns with ADR-020 prior lock** — `runpod-deploy v0.7.7` consistent across ADRs.

### Negative / cost

- **Blocking bug requires explicit bump procedure** — small friction tax on real upstream fixes. Acceptable — methodology submissions favor reproducibility over fluidity.
- **Tag pin trusts upstream tag immutability** — force-pushed tags would invalidate. Defense-in-depth: `uv.lock` + CLAUDE.md no-amend / no-force-push discipline for own-authored repos.

### Neutral

- **Freeze expires at `v2.0.0`** — long-term maintenance liability is acknowledged but defers to that decision moment.
- **`runpod-deploy v0.7.7` was already pre-locked by ADR-020** — this ADR records the canonical location for that pin.

### Limitation

Per-library `requires-python` constraints might block `>=3.13` (per ADR-037). Phase 0-08 close runs `uv sync` to catch this. If any library is stuck below 3.13, fix-forward by either (a) bumping the upstream's `requires-python` to `>=3.13` in a same-day patch, or (b) loosening ADR-037's pin to `>=3.12` via superseding ADR.

### Extension condition for revisit

- **Blocking bug**: per bump-trigger #1 above; no ADR supersession.
- **Critical security fix**: per bump-trigger #2; no ADR supersession.
- **Post-submission `v1.0.x` patch**: per bump-trigger #3; no ADR supersession.
- **`v2.0.0` major bump**: freeze policy expires; new ADR re-walks the pins for that scope.
- **Library deprecation**: if one of the three libraries is deprecated or archived upstream, a superseding ADR replaces it with the successor library + updates `library_imports.md` accordingly.

## Alternatives Considered

- **(B) SHA pin** — strictest reproducibility but ugly + uv.lock + tag pin already provides byte-level reproducibility. Rejected per Q2 walk.
- **(C) Branch pin (`@main`)** — auto-tracks upstream; reproducibility comes solely from uv.lock; loses audit-trail clarity. Rejected per Q2 walk.
- **(D) Tag pin with on-demand bump (no freeze)** — flexibility for fixes but defeats audit trail. Rejected per Q2 walk.

## References

- PEP 508 dependency specification — https://peps.python.org/pep-0508/
- `uv` git-URL dependency docs — https://docs.astral.sh/uv/concepts/projects/dependencies/#git
- SemVer 2.0.0 — https://semver.org/
- `eval-toolkit` releases — https://github.com/brandon-behring/eval-toolkit
- `runpod-deploy` releases — https://github.com/brandon-behring/runpod-deploy
- `research_toolkit` releases — https://github.com/brandon-behring/research_toolkit
- ADR-020 (compute infrastructure — `runpod-deploy 0.7.7` pre-lock)
- ADR-033 (release strategy — freeze cadence aligns with submission tag lifecycle)
- ADR-037 (Python version pin — `requires-python >=3.13`)

## Transcript

See `transcripts/2026-05-16__phase-0-08__process-tech-stack-acceptance.md` for the conversation that led to this decision (Q2 walk + tag pin + freeze + specific versions).
