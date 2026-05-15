---
adr_id: 003
slug: repo-visibility-public
title: Repository visibility — public from start (kit default ratified)
date: 2026-05-15
status: Accepted
claim_id: CLAIM-003
claim: The submission GitHub repository is public from project start; the kit-level default (per .gitignore + SPEC_STRATEGY.md) is ratified without override. Transcripts remain gitignored; the brief itself is never committed.
source: SPEC_GREENFIELD.md §Brief row 306 (Repo visibility) + §Kit-Ratify row 367
acceptance_criterion: Repo is public on GitHub at submission time; transcripts/ remains gitignored except README.md; no brief contents committed.
closing_commit:
references:
  - https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility
  - .gitignore (this repo)
  - SPEC_STRATEGY.md
transcript: transcripts/2026-05-15__phase-0-00__brief-alignment.md
---

# ADR-003: Repository visibility — public from start (kit default ratified)

## Status

Accepted (2026-05-15)

## Context

The brief is silent on repo visibility. The kit default (`SPEC_STRATEGY.md` + `.gitignore`) is "public from start" with transcripts gitignored. The project must explicitly affirm or override.

A public repo carries the "show your work" optics — full commit history, ADRs, code, methodology decisions visible to anyone. Risk: history cannot be retroactively privatized after withdrawal. Mitigation: `.gitignore` already partitions sensitive content correctly (transcripts private; brief uncommitted; secrets/keys gitignored).

## Decision

**Repo visibility**: public on GitHub from project start; ratifies the kit-level `[LOCKED]` default without superseding.

**Privacy partitioning**:

- ADRs, code, ledgers, manifests — public.
- Transcripts (`transcripts/*.md`) — gitignored, private. Emailed to reviewer separately at submission time per `transcripts/README.md` convention.
- Brief itself — never committed (per `CLAUDE.md`).
- Secrets — gitignored (`.env`, `*.key`, `secrets/`).

## Consequences

**Positive:**

- Smaller paperwork burden: ratifying the kit default needs no kit-supersession ADR.
- "Show your work" optics aligned with commit-discipline rule (real development including missteps visible).
- `.gitignore` already enforces the privacy partition correctly; no code change needed.

**Negative / cost:**

- Cannot retroactively privatize history if the submission is withdrawn.
- Interview-prep style is publicly visible. Acceptable tradeoff.

**Neutral:**

- ADR-008 (Phase 0-07 GitHub release strategy) will decide the tagging cadence (tag-at-submission only vs multiple tags during Phase 1+).

## Alternatives Considered

- **Private-then-public**: Repo private during dev; flipped public at submission. *Rejected because* reviewer-link risk (forgetting the flip = dead link), and commit timestamps reveal dev history anyway.
- **Private (reviewer-invite only)**: Maximum control. *Rejected because* reviewer must accept GitHub invite; no portfolio benefit; kit default not chosen for a reason.
- **Mixed (code public, writeup private)**: Two-artifact split. *Rejected because* PDF references the public repo so writeup-privacy is mostly illusory.

## References

- GitHub visibility docs — https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility
- `.gitignore` (this repo) — already partitions transcripts, secrets, build artifacts
- `SPEC_STRATEGY.md` — kit-level visibility strategy
- ADR-002 (deliverable format references the repo)
