---
adr_id: 011
slug: methodology-guarantees
title: Methodology guarantees — eight banned approaches surfaced as project commitments
date: 2026-05-15
status: Accepted
claim_id: CLAIM-011
claim: Eight methodology guarantees are committed and surfaced in the writeup (1-paragraph summary in PDF + WRITEUP/methodology-guarantees.md spoke), namely — (1) no tuning on test data; (2) no train-eval overlap (leakage scan + cross-source benign dedup); (3) no closed-source datasets; (4) no hand-labeling without inter-rater agreement (audited via Cohen's kappa, per ADR-007); (5) no cherry-picking seeds (seed-aggregate + per-seed transparency); (6) no adaptive threshold selection on test data (thresholds on validation only); (7) no data leakage train→eval (Phase 5 pre-submission grep suite); (8) no untracked methodology components (every component has an ADR).
source: SPEC_GREENFIELD.md §Brief row 308 (Q5-C8) + CLAUDE.md anti-patterns
acceptance_criterion: WRITEUP/methodology-guarantees.md spoke enumerates all eight guarantees with the verification mechanism for each; the PDF exec summary or methodology narrative cites the spoke; the pre-Phase-5 grep suite runs cleanly with no leakage detected.
closing_commit: e760faf
references:
  - https://neurips.cc/Conferences/2024/PaperInformation/PaperChecklist
  - https://journals.sagepub.com/doi/10.1177/001316446002000104
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-011: Methodology guarantees — eight banned approaches surfaced as project commitments

## Status

Accepted (2026-05-15)

## Context

The most common serious methodology failures in published ML are silent: tuning on test data, train-eval leakage, cherry-picked seeds, adaptive threshold selection. CLAUDE.md anti-patterns ban these implicitly. The Q5-C8 walk asks: do we leave these implicit, or do we **explicitly surface them as project guarantees** that the writeup names?

Per ADR-005 Principles 1 and 2 (methodology over metrics; honest evaluation preferred), surfacing the guarantees is the methodology-first move. Cost is roughly one paragraph in the PDF + one spoke file ≈ 1 hour of writing. The reviewer-credibility return is disproportionate: explicit guarantees signal *methodological maturity*, not bureaucratic compliance.

## Decision

**Eight methodology guarantees**, each surfaced in the writeup with its verification mechanism:

### Guarantee 1 — No tuning on test data

- **Verification**: thresholds, hyperparameters, model selection all decided on validation splits; test splits are touched exactly once for headline reporting. Verified by code review + Phase 5 pre-submission grep suite.

### Guarantee 2 — No train-eval overlap

- **Verification**: cross-source benign dedup applied before split (per ADR-008); leakage scan run in Phase 1 (`evals/leakage_report.json`); reference-scorer training-overlap audit (Phase 0-02 + EVIDENCE.md §1-2).

### Guarantee 3 — No closed-source datasets

- **Verification**: source-slate manifest documents public-source URLs + license per dataset (per ADR-008); no proprietary data accessed.

### Guarantee 4 — No hand-labeling without inter-rater agreement

- **Verification**: any new labeling (if any) audited via LLM-judge + Cohen's kappa per ADR-007; pairwise kappa matrix in `WRITEUP/reference-scorer-audit.md` spoke.

### Guarantee 5 — No cherry-picking seeds

- **Verification**: per-row predictions persisted for every (rung, seed, fold) tuple per ADR-006 + ADR-013; seed-aggregate metrics in headlines; per-seed transparency in spoke; bootstrap CIs marginalized across seeds via paired bootstrap per ADR-006.

### Guarantee 6 — No adaptive threshold selection on test data

- **Verification**: operating-point pinpoints {0.1%, 1%, 5%} are *fixed a priori* per ADR-006; calibration-fit (temperature/isotonic) done on validation only; thresholds for any derived metric likewise validation-only.

### Guarantee 7 — No data leakage train→eval

- **Verification**: Phase 5 pre-submission grep suite (per `docs/ROADMAP.md` Phase 5 replanning checkpoint) scans for known leakage patterns (exact-hash overlap, high-cosine near-duplicates); `tests/test_leakage.py` invariants assert no overlap.

### Guarantee 8 — No untracked methodology components

- **Verification**: every methodology component has an ADR; SUBMISSION_AUDIT.md (auto-generated from ADR frontmatter via `scripts/regenerate_audit.py`) is CI-gated to stay in sync; pre-commit hook enforces.

**Writeup surfacing**:

- PDF: 1-paragraph "Methodology Guarantees" subsection in the methodology narrative section, with a forward-link to the spoke.
- Spoke: `WRITEUP/methodology-guarantees.md` enumerates all eight with verification mechanism + a short rationale ("we surface these because…").

## Consequences

**Positive:**

- Methodology-first signal: A2 (ML researcher) reviewer reads the enumeration as competence, not bureaucracy.
- Pre-empts the most common reviewer concerns — "did you tune on test?", "could there be leakage?", "what about cherry-picked seeds?"
- All eight are *already* enforced by prior ADRs or by CLAUDE.md anti-patterns; this ADR just makes them visible in the writeup.
- The pre-Phase-5 grep suite becomes a load-bearing verification artifact, not a hidden chore.

**Negative / cost:**

- Spoke writing cost (~1 hour). Bounded.
- Guarantee 4 (LLM-judge for hand-labeling) presumes the LLM-judge methodology is itself credible; if Cohen's kappa across judges is low (e.g., κ < 0.4) the audit story weakens. Mitigation: report kappa honestly per ADR-007; if it's low, that *is* the methodology finding.
- Guarantee 7 (no train→eval leakage) requires the Phase 5 grep suite to actually exist and pass; if a leakage is discovered late, the submission is in trouble. Mitigation: run the scan early (Phase 1) and again pre-submission (Phase 5).

**Neutral:**

- Each guarantee already maps to a prior ADR or anti-pattern. This ADR is the *enumeration ADR* — it consolidates the commitments into a single citable artifact.

## Alternatives Considered

- **Leave guarantees implicit** (in CLAUDE.md anti-patterns; not surfaced in writeup): Cheaper. *Rejected* because the writeup must serve A2 reviewer who reads CLAUDE.md only if curious; explicit guarantees in the writeup are the methodology-first surface.
- **Fewer guarantees** (e.g., 3-4 instead of 8): Less paperwork. *Rejected* because each of the 8 is a real failure mode that's worth pre-empting; truncating the list looks like cherry-picking the easy ones.
- **Inline guarantees scattered through the writeup**: Distributed surface. *Rejected* because consolidating into one spoke is more citable and easier for reviewers to scan.

## References

- NeurIPS Paper Checklist (most guarantees map to checklist items) — https://neurips.cc/Conferences/2024/PaperInformation/PaperChecklist
- Cohen 1960 — kappa methodology referenced in Guarantee 4 — https://journals.sagepub.com/doi/10.1177/001316446002000104
- `CLAUDE.md` — Anti-patterns enumeration
- `docs/ROADMAP.md` — Phase 5 pre-submission grep + verification suite
- ADR-005 (Principles 1 and 2 — direct rationale for surfacing guarantees)
- ADR-006 (Guarantees 5 and 6 — seed protocol and threshold-on-validation)
- ADR-007 (Guarantee 4 — Cohen's kappa methodology)
- ADR-008 (Guarantees 2 and 3 — dedup + public-only)
