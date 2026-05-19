---
adr_id: 005
slug: methodology-principles
title: Project-level methodology principles — methodology over metrics, honest evaluation preferred, structured limitations
date: 2026-05-15
status: Accepted
claim_id: CLAIM-005
claim: The submission is governed by three project-level methodology principles surfaced during Phase 0-00 brief alignment — (1) methodology over metrics, (2) honest evaluation preferred even when models look worse, (3) structured limitations with extension conditions. These principles propagate to ADR rationale, WRITEUP tone, and downstream methodology decisions.
source: Phase 0-00 brief alignment conversation (Q4 Signals 2-3, Q7 add-on)
acceptance_criterion: Every methodology component has an ADR whose Consequences section names its extension condition; every scope-bound in the writeup is paired with the limitation it imposes and when it would or wouldn't make sense to extend; reported metrics include cases where the model looks worse under honest eval, named as such; comparisons interpreted via effect-size + uncertainty, not via dichotomous test outcomes.
closing_commit: 2a7b123
references:
  - https://doi.org/10.1177/0956797613504966
  - https://doi.org/10.1080/00031305.2016.1154108
  - docs/ROADMAP.md
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-005: Project-level methodology principles

## Status

Accepted (2026-05-15)

## Context

Three load-bearing principles surfaced during Phase 0-00 brief alignment that govern the entire submission, not just any single decision. They emerged from the user's framing of the project goal:

> *"The more important goal isn't about finding the correct answers, it is about understanding the methodology, why choices were made, what can be left to later. The most important decisions may end up being about choosing the right training data and the right evaluation data sets — and it may be doing that **right** means the models look worse because they are evaluated honestly."*

And from the Q7 (scope-limits) add-on:

> *"Make sure to discuss the limitations of each and when it would and wouldn't make sense to extend them."*

These are not decisions about *what to do* in any single phase — they are decisions about *how the project decides and reports*. They need their own ADR so downstream ADRs can cite them as the controlling rule.

## Decision

**Three project-level methodology principles**, all `Accepted` for the duration of this project:

### Principle 1 — Methodology over metrics

The submission optimizes for the *quality of the methodological narrative*, not the magnitude of the headline numbers. ADR rationale emphasizes *why* a choice was made and *what was deferred*, not just *what was decided*. WRITEUP tone is "here's how we chose, why, and what we left for v2", not "here are the numbers we got". Spokes in the hub-and-spoke structure (ADR-004) implement this — each spoke is a methodology narrative anchored on a specific decision, not a metric-trophy case.

### Principle 2 — Honest evaluation preferred even when models look worse

Source-disjoint LODO splits, OOD slices, calibration audits, and reference-scorer audits are *all* preferred over their within-distribution / partially-leaked / uncalibrated counterparts, **even when they produce lower headline numbers**. The writeup explicitly names places where the model looks worse under honest eval and explains *why that's the right framing*. Comparisons are interpreted via effect-size + uncertainty, not via dichotomous test outcomes (the estimation-over-testing stance — finalized in the Q5 ADR; see references).

### Principle 3 — Structured limitations with extension conditions

Every scope-bound, methodology choice, and metric reported is paired with **(a)** the limitation it imposes and **(b)** the conditions under which extending past it would or wouldn't make sense. Standard "future work could include X" boilerplate is rejected — extension conditions are decision-relevant: they tell the reader *under what conditions the limitation matters for them*.

## Consequences

**Positive:**

- ADRs and WRITEUP have a consistent methodological identity: *"we don't pretend, we structure."*
- A2 (ML researcher) reviewer reads the structured limitations and recognizes that the submitter thought about generalization beyond their experiment.
- A1 (hiring manager) reviewer reads decision-relevant extension conditions and can map them to their own deployment context.
- Pairs cleanly with scenario-based cost-handling (no single cost-weight ratio; three deployment scenarios) and estimation-over-testing (CIs not p-values) — both are special cases of the broader "don't pretend, structure" stance.
- Pre-resolves a Phase 0-05 over-decision (cost-weight targets becomes scenario-based) and pre-shapes Phase 0-04 §Eval decisions (multi-comparison correction = none under estimation-over-testing).

**Negative / cost:**

- More writeup surface area — every methodology choice needs its limitation + extension condition prose. Mitigation: most live inline in ADR Consequences sections; the spokes carry the extended discussion.
- "Honest eval preferred" carries reputational risk if a reviewer reads lower numbers as failure rather than methodology. Mitigation: explicit naming of the framing in the PDF exec summary and methodology narrative.

**Neutral:**

- These principles are *immutable* in the same sense as any ADR — modification requires a superseding ADR. Phase-level replanning checkpoints (per `docs/ROADMAP.md`) may surface scenarios where a principle interferes with reality; supersession is the response.

## Alternatives Considered

- **Implicit framing (principles in WRITEUP tone but no ADR)**: Each downstream methodology choice would re-argue from first principles. *Rejected because* it diffuses the rationale across many ADRs and makes the framing un-citable.
- **Single "house style" doc in WRITEUP/ (not an ADR)**: Cheaper to write; less authoritative. *Rejected because* the anti-pattern rule in `CLAUDE.md` ("adding a methodology component without an ADR") covers methodology principles too.
- **Methodology-over-metrics as the sole principle (without honest-eval and structured-limitations)**: Narrower. *Rejected because* the three principles support each other; isolating one weakens all three.

## References

- Cumming 2014 — "The New Statistics: Why and How" — https://doi.org/10.1177/0956797613504966
- Wasserstein & Lazar 2016 — ASA Statement on p-values — https://doi.org/10.1080/00031305.2016.1154108
- Gelman & Stern 2006 — "The Difference Between 'Significant' and 'Not Significant' is Not Itself Statistically Significant" — https://doi.org/10.1198/000313006X152649
- `docs/ROADMAP.md` — phase checklists are work-completed, not metric thresholds (principle-aligned)
- `CLAUDE.md` — anti-pattern: adding methodology component without ADR (principle-aligned)
- ADR-004 (reviewer profile + hub-and-spoke — implements the principles in writeup structure)
