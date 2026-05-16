---
adr_id: "028"
slug: coverage-floor-70pct-with-upstream-issue-filing
title: Test coverage floor — 70% flat with co-locked upstream-issue-filing discipline
date: 2026-05-16
status: Accepted
claim_id: CLAIM-028
claim: Phase 0-06 locks the §STYLE ledger row 350 (Test coverage floor) at 70% flat across the repo with a co-locked upstream-issue-filing discipline. The CI command is uv run pytest --cov --cov-fail-under=70 --cov-report=term-missing — single threshold across the codebase (no src/-vs-scripts/ stratification). The Makefile coverage target is updated from the current ungated form (pytest --cov=. --cov-report=term-missing) to the gated form. The 70% threshold reflects the case-study composition layer's prototype-grade framing (per ADR-027 debugging-grade-here-rigorous-upstream split) — high enough to catch a whole-module-untested regression, low enough to avoid forcing low-value tests against orchestration glue. Co-locked process commitment extending ADR-006 + decisions/upstream_issues.md from library-primitive-gaps to test-coverage-gaps — when a local coverage gap is identified that would be better addressed by an upstream library test (e.g., a test pattern that should live in eval-toolkit's harness coverage, or a runpod-deploy preflight scenario), file an issue at the upstream repo with the proposed test pattern + rationale. Log the upstream issue in decisions/upstream_issues.md with a "test-coverage-gap" tag in the row. This prevents the 70% floor from forcing low-value local tests when the right home for the test logic is upstream. If a gap genuinely cannot be filed upstream (project-specific glue), the gap is either tested locally OR explicitly documented as deferred via comment + upstream_issues.md "not-applicable" entry pointing at the deferral rationale. STYLE.md project-deltas section is updated from the prior "[OPEN — coverage floor; resolved at Phase 0]" placeholder to the locked 70%-flat-with-upstream-filing-discipline. Limitation — 70% is empirically chosen, not derived; if Phase 1 reveals chronic failure on legitimate orchestration glue with no viable upstream home, reopen via superseding ADR with the actual data. Extension condition — production-deployment scope extension lifts floor to 85% with src/eval at 90%; currently out-of-scope.
source: SPEC_GREENFIELD.md §STYLE ledger row 350 + STYLE.md "project deltas" + Phase 0-06 walk Q3
acceptance_criterion: SPEC_GREENFIELD ledger row 350 carries locked-to-70pct-flat-with-upstream-issue-filing-discipline status (see ADR-028); STYLE.md project-deltas section first bullet is rewritten from the prior "[OPEN — coverage floor; resolved at Phase 0]" placeholder to the locked 70% with the upstream-filing-discipline pointer; Makefile coverage target is updated from the current ungated form to "uv run pytest --cov --cov-fail-under=70 --cov-report=term-missing"; decisions/upstream_issues.md ledger gains a "test-coverage-gap" tag convention documented in the "How to use this ledger" section + a worked example row in the table (or a placeholder row marked TBD-at-Phase-1-entry); tests/test_invariants.py contains skip-marked stub test_coverage_floor_enforced asserting that the Makefile coverage target invokes pytest with --cov-fail-under=70 (or the equivalent CI invocation does so) — verification is via subprocess + assert that exit code is non-zero when synthetic coverage drops below 70%; SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit: fa1ad33
references:
  - https://pytest-cov.readthedocs.io/en/latest/config.html
  - https://github.com/brandon-behring/eval-toolkit/blob/main/STYLE.md
  - https://github.com/brandon-behring/eval-toolkit/blob/main/Makefile
  - decisions/ADR-006-headline-metrics-and-statistical-apparatus.md
  - decisions/ADR-026-module-layout-concern-grouped-subpackages.md
  - decisions/ADR-027-smoke-vs-canonical-execution-context-stratification.md
  - decisions/upstream_issues.md
  - decisions/library_imports.md
transcript: transcripts/2026-05-16__phase-0-06__code-test-discipline.md
---

# ADR-028: Test coverage floor — 70% flat with co-locked upstream-issue-filing discipline

## Status

Accepted (2026-05-16). Closes the third of 4 [OPEN] rows in Phase 0-06 (§5 Code architecture + §STYLE — rows 348-351 of SPEC_GREENFIELD ledger). Companion to ADR-026 (module layout), ADR-027 (smoke vs canonical), and ADR-029 (test marker strategy).

## Context

`pytest --cov` measures source-line coverage from the test suite; a **coverage floor** is a CI gate that fails the build if coverage drops below threshold. STYLE.md's "project deltas" section explicitly defers this decision to Phase 0:

> **Test coverage floor**: `[OPEN: coverage floor; resolved at Phase 0]`. eval-toolkit uses 90%; case-study composition layer typically doesn't need foundational-library rigor.

Five options were considered:

(A) **90%** — eval-toolkit parity. Contradicts the prototype-grade framing locked by ADR-027; forces low-value tests against glue.

(B) **80%** — middle ground. Same low-value-test pressure as 90%, just delayed.

(C) **70%** — relaxed; matches STYLE.md hint. Low enough to accommodate orchestration glue, high enough to signal that critical paths get tested.

(D) **No formal floor; measure-only** — zero false positives, but no gate means coverage decay is invisible until writeup time.

(E) **Stratified floor** (70% on src/, no floor on scripts/) — most pragmatic version of C; aligns with the src/-vs-scripts/ boundary locked by ADR-026.

User feedback at decision time selected option C with an additional process commitment:

> "C, but whenever we find things that should be sent to runpod-deploy or eval-toolkit we should send issues to those repos for those tests."

This addendum extends the existing library-first discipline (don't hand-roll library primitives — file upstream issues for gaps; tracked in `decisions/upstream_issues.md`) from **library-primitive-gaps** to **test-coverage-gaps**. Rather than carving out scripts/ via stratification (option E), the simpler 70% flat threshold is paired with a process commitment: when a coverage gap is identified that would be better addressed upstream, file the gap upstream rather than write a low-value local test.

This is structurally cleaner than option E because:

1. The floor calculation is a single CLI flag (`--cov-fail-under=70`) — no per-package strata to maintain in `.coveragerc`.
2. The escape hatch (upstream filing) is a real process improvement — generates contribution-trail value for the writeup, not just a technical workaround.
3. It's load-bearing in the right direction: the floor is a forcing function for *honest engagement* with each gap (either test locally, file upstream, or document non-applicability), not a license to add anti-tests.

## Decision

### Locked threshold and CI command

**Coverage floor**: 70% flat across the repo.

**CI command**:

```bash
uv run pytest --cov --cov-fail-under=70 --cov-report=term-missing
```

**Updated `Makefile` coverage target** (replaces existing ungated form `pytest --cov=. --cov-report=term-missing`):

```makefile
coverage:
    uv run pytest --cov --cov-fail-under=70 --cov-report=term-missing
```

### Co-locked process commitment — upstream-issue-filing for test-coverage gaps

When a local coverage gap is identified during Phase 1+ work, the developer applies this triage:

1. **Local test is the right home** — write the test locally in `tests/unit/`, `tests/smoke/`, or `tests/integration/` per the Q4 marker taxonomy (ADR-029).
2. **Upstream library is the right home** — file an issue at the upstream repo (`brandon-behring/eval-toolkit` or `brandon-behring/runpod-deploy`) with:
   - The proposed test pattern (sketch, not implementation).
   - The rationale (why the test logic belongs upstream, not locally).
   - Local file:line that depends on the absent test (if any).
   - `tracked` label.
   Then add a row to `decisions/upstream_issues.md` with the issue URL + `[test-coverage-gap]` tag + local file:line.
3. **Genuinely not testable, not upstream-applicable** — leave a `# noqa: COV` style code comment with rationale + add a `decisions/upstream_issues.md` row tagged `[not-applicable]` documenting the deferral.

A workaround that ignores the gap (lets coverage drop below 70% silently, or worse, adds a no-op test to inflate coverage) is an anti-pattern.

### Updated `decisions/upstream_issues.md` ledger conventions

The ledger's "How to use this ledger" section gains:

> **Test-coverage-gap entries**: when a coverage gap is filed upstream rather than tested locally, add a row with the `[test-coverage-gap]` tag in the Title column. When a gap is documented as not-applicable rather than filed, use the `[not-applicable]` tag. Both forms preserve the discipline trail without forcing local anti-tests.

A worked example row (placeholder — populated as actual gaps surface during Phase 1+):

| Date | Repo | Issue # | Title | Local site (file:line) | Status |
|---|---|---|---|---|---|
| `[TBD-at-Phase-1-entry]` | `brandon-behring/eval-toolkit` | `[TBD]` | `[test-coverage-gap]` example placeholder for upstream-filing convention | `[TBD]` | placeholder |

### What's explicitly out of scope

- **Per-package coverage strata** (option E) — kept simple at 70% flat; the upstream-filing escape hatch handles the orchestration-glue case structurally rather than via configuration.
- **Production-grade coverage** (≥85%) — currently out-of-scope per ADR-027 prototype-grade framing; reopen via superseding ADR if scope extends.
- **Coverage on `tests/` itself** — pytest-cov's default behavior excludes test files when `--cov` has no path argument; this is preserved.

## Consequences

### Positive

- **Single CLI flag** for the floor — no `.coveragerc` per-package configuration to drift.
- **Floor as forcing function for honest engagement**: every gap gets one of three responses (local test / upstream issue / documented deferral). No silent coverage decay.
- **Contribution trail**: upstream-filed test-coverage gaps generate `decisions/upstream_issues.md` entries that double as evidence of library-first discipline for the writeup.
- **Aligns with ADR-027 prototype-grade framing**: 70% is the right number for debugging-grade testing; 90% would force the layer to do work that belongs upstream.

### Negative

- **70% is empirically chosen**, not derived. If Phase 1 reveals it's either trivially exceeded everywhere (suggesting we should raise it) or chronically failed on legitimate glue (suggesting we should rethink), reopen via ADR with the actual data.
- **Upstream filing has friction**: writing the issue + the proposed test pattern takes more developer time than writing a local anti-test. This is the *intended* friction — it forces a real "is this our problem or theirs" judgment rather than a reflex anti-test.
- **CI gate fires on coverage drops** even when the absolute level is still above 70%. Acceptable cost — drops are signal worth investigating; the upstream-filing escape hatch handles the legitimate-deferral case.

### Limitation

The 70% threshold is a heuristic, not a methodological commitment. It is calibrated for the prototype-grade context locked by ADR-027 (where the math lives upstream). If a Phase 1+ surprise reveals the threshold is mis-calibrated, the data justifies the superseding ADR — not a quiet adjustment.

### Extension condition for revisit

- **Production-deployment scope extension** lifts floor to 85% with `src/eval/` at 90% (since `src/eval/` is the most math-adjacent package and would carry production-grade calibration / threshold-fitting orchestration logic in that context).
- **First sustained Phase 1 violation** of the floor with no viable upstream home triggers a re-evaluation — possibly drop to 60% (with explanation), or move to the stratified option E variant.

## Alternatives considered

- **(A) 90%** — rejected; contradicts prototype-grade framing; forces low-value tests.
- **(B) 80%** — rejected; arbitrary middle ground with same low-value-test pressure delayed.
- **(D) No floor; measure-only** — rejected; loses the forcing-function benefit; coverage decay invisible until writeup.
- **(E) Stratified 70% on src/, no floor on scripts/** — rejected in favor of flat 70% + upstream-filing escape hatch; the escape hatch is structurally cleaner than per-package strata and provides real process value.
