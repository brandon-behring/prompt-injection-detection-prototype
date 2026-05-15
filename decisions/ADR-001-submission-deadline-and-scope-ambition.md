---
adr_id: 001
slug: submission-deadline-and-scope-ambition
title: Submission deadline 2026-05-18 morning with infra-leveraged Long-scope attempt and fallback ladder
date: 2026-05-15
status: Accepted
claim_id: CLAIM-001
claim: The submission targets 2026-05-18 morning (~2.5 working days from 2026-05-15); scope ambition is Long-bucket (2×3 trained-rung grid + multi-seed + full OOD slate + paired-bootstrap) leveraging runpod-deploy + eval-toolkit infrastructure; fallback ladder shrinks rung count before sacrificing methodology integrity.
source: SPEC_GREENFIELD.md §Brief row 304 (Submission deadline / time budget)
acceptance_criterion: All Phase 1-5 work is completed by 2026-05-18 morning; or the fallback ladder activates and the writeup honestly reports the realized rung set without pretending unrealized rungs.
closing_commit:
references:
  - docs/ROADMAP.md (phase checklist = work-completed, not metric thresholds)
  - SPEC_STRATEGY.md (scope-shrink-under-pressure discipline)
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-001: Submission deadline 2026-05-18 morning with infra-leveraged Long-scope attempt and fallback ladder

## Status

Accepted (2026-05-15)

## Context

The brief mandates a submission delivered on the morning of 2026-05-18. Today is 2026-05-15. Available working window: Friday afternoon → Saturday → Sunday → Monday morning submission, ≈ 2.5 working days, weekend-heavy. By calendar alone this falls in the "Tight" bucket of the time-budget framework (≤ 5 working days), at the extreme low end.

A naive Tight-bucket interpretation would scope to a single backbone × single training rung minimal demo. However, the project's three load-bearing libraries (`eval-toolkit`, `runpod-deploy`, `research_toolkit`) provide prebuilt primitives for the full workload: GPU rental + per-row prediction persistence, bootstrap CI machinery, calibration battery, paired comparison, splits + leakage scans. Library-first discipline (CLAUDE.md) means the project is not bottlenecked by hand-rolled scaffolding.

This decision encodes the bet: heavy library infrastructure compresses what would normally be a 2-week 2×3-grid workload into 2.5 working days. It also encodes the contingency: an explicit fallback ladder so scope-shrink under deadline pressure is *pre-decided*, not improvised.

## Decision

**Submission deadline**: 2026-05-18, morning.

**Time budget**: ≈ 2.5 working days.

**Scope ambition**: Long-bucket — full 2×3 trained-rung grid (DeBERTa-v3 + ModernBERT × {frozen-probe, LoRA, full-FT}), multi-seed protocol (3 seeds paired across rungs, escalating to 5 if budget permits), full OOD slate, paired-bootstrap rung-vs-rung differences, written methodology analysis depth.

**Fallback ladder** (activates if mid-Phase-2 checkpoint shows full grid infeasible):

1. Full 2×3 grid → drop full-FT → **2×2** (frozen + LoRA, both backbones)
2. 2×2 → drop second backbone → **1×2** (single backbone, frozen + LoRA)
3. 1×2 → drop to **1×1** minimal demo
4. Multi-seed protocol degrades 3 → 2 → 1 seed in lockstep with each rung drop

**Reporting discipline**: the writeup reports what was *achieved*, not what was attempted. Honest reduction is preferred over fabrication.

## Consequences

**Positive:**

- Pre-committed fallback ladder removes scope-shrink panic at the deadline. Triggering rule (mid-Phase-2 checkpoint) is concrete.
- Library-first leverage is *the* mechanism that makes Long-scope feasible — also forces the project to use library primitives correctly (anti-hand-rolling discipline reinforced).
- Phase checklists (per `docs/ROADMAP.md`) are work-completed, not metric thresholds — failing-forward through the ladder is *built into the spec*, not an apology.

**Negative / cost:**

- The bet may fail. If infrastructure surprises emerge (RunPod queue contention; library bugs in eval-toolkit's bootstrap or splits primitives; HF dataset rate-limits), the ladder activates and the headline narrative shrinks.
- Weekend-heavy schedule means human-availability risk is high; one bad night of sleep can compress remaining hours significantly.
- Multi-seed escalation (3 → 5) is unlikely to fit; the realistic operating point is 3 seeds.

**Neutral:**

- The Long-scope-attempt framing matches reviewer expectations for a methodology-first submission (Q4 locks ADR-004). A1+A2 audience reads "attempted full grid, achieved X under time constraints" as competent scoping, not as failure.

## Alternatives Considered

- **Tight-bucket-minimal (1×1 single-rung demo)**: Conservative; guaranteed to complete; flat narrative; doesn't exercise the library infrastructure. *Rejected because* it under-uses the library leverage that distinguishes this submission, and the methodology-first framing demands enough rungs to compare.
- **Long-scope without fallback ladder**: Optimistic; commits the project to the full grid with no documented retreat path. *Rejected because* unmitigated deadline-pressure scope-shrink is the most common source of methodology corner-cutting; pre-committing the ladder removes that pressure.
- **Defer the deadline / negotiate extension**: Not the project's call. The brief is authoritative.

## References

- `docs/ROADMAP.md` §Phase 0 close criterion + §Replanning checkpoint (per-phase)
- `SPEC_STRATEGY.md` — strategy doc on scope-shrink under pressure
- `CLAUDE.md` — library-first discipline; anti-pattern rule on hand-rolling
