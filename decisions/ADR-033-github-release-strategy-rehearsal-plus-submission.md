---
adr_id: "033"
slug: github-release-strategy-rehearsal-plus-submission
title: GitHub release strategy — rehearsal tag plus SemVer submission tag plus post-submission patches
date: 2026-05-16
status: Accepted
claim_id: CLAIM-033
claim: Phase 0-07 locks SPEC_GREENFIELD ledger row 349 (GitHub release strategy) at a two-tag-canonical plus post-submission-patches policy (Option D plus C-post-submission of the Phase 0-07 Q3 walk). Tag sequence — v0.9.0-rc1 at end of Phase 4 (release candidate; dress-rehearsal tag that fires the full publish pipeline — Quarto site build per ADR-030 plus GH Pages deploy plus HF Hub model card pushes per ADR-032 — so that any first-time-GH-Actions plus HF Hub auth plus model card schema issues surface 24-plus hours before submission day) plus v1.0.0 at submission day (canonical reviewer reference; CHANGELOG.md entry committed; GH release object created via gh release create v1.0.0 plus the title flag plus the notes flag pointing at CHANGELOG plus the generate-notes flag) plus optional v1.0.x SemVer patch tags post-submission for typo plus link plus reviewer-feedback fixes (reviewer URL stays pinned at v1.0.0; live Quarto site reflects latest patch per ADR-030 push trigger). No phase-boundary tags during Phases 1-3 — the existing ADR closing_commit SHA field per ADR already provides ADR-granular pinning at finer grain than phase tags; phase-boundary tagging would add discipline overhead under tight deadline without paying back. Tag version format — vMAJOR.MINOR.PATCH per SemVer 2.0.0 (vs annotated suffix vs calendar-versioning); chosen for gh release UI compatibility plus clean MAJOR-bump path if a post-submission methodology revision lands. GH release assets for v1.0.0 — CHANGELOG.md (default) plus _site.tar.gz (offline-readable rendered Quarto site for reviewers without internet; built from quarto render output dir plus tarred); per-row predictions parquet files NOT attached as release binaries (they stay in results/predictions/ within the repo at their natural location to avoid duplication). CHANGELOG.md committed at submission per Keep-a-Changelog 1.1.0 format — entries written in human language not git-shortlog dumps; one entry per tag going forward maintained via gh release create with the notes flag. Reviewer email at submission carries three URLs — source pin at github.com tree v1.0.0 (canonical anchor; never drifts) plus live rendered Quarto site at brandon-behring.github.io (reflects latest publish) plus GH release page at github.com releases tag v1.0.0 (CHANGELOG plus _site.tar.gz download) — plus transcripts as private email attachment per existing convention. Limitation — GH Pages serves a single live URL pinned to whatever the latest deploy was; there is no built-in this-URL-is-frozen-at-v1.0.0 affordance without snapshot tooling; mitigated by the canonical-source-pin URL pointing at tagged source plus reviewers can git checkout v1.0.0 plus quarto preview for a frozen-rendered view. Extension condition — post-submission methodology revision (not patch-grade typo fixes; actual content revisions) bumps to v2.0.0 via superseding ADR with rationale plus reviewer-notification step; patch tags v1.0.x are reserved for non-methodology fixes only.
source: SPEC_GREENFIELD.md §Submission ledger row 349 + Phase 0-07 walk Q3
acceptance_criterion: SPEC_GREENFIELD ledger row 349 carries locked-to-rehearsal-plus-submission-plus-patches status (see ADR-033); CHANGELOG.md exists at repo root in Keep-a-Changelog 1.1.0 format with an Unreleased section (populated continuously) plus a stub for v1.0.0 (populated at submission tag); the v0.9.0-rc1 tag and v1.0.0 tag are created at their respective Phase 4 close and submission day (Phase 5 work items captured in assumptions.md or Phase 5 checklist); the .github/workflows/publish.yml workflow per ADR-030 triggers on tag push v* so both rehearsal and submission tags fire the Quarto-publish plus HF Hub model card pipelines; tests/test_invariants.py contains skip-marked stub test_submission_tag_changelog_present asserting that CHANGELOG.md exists and parses (the keepachangelog Python package can validate) plus contains a v1.0.0 section at submission close plus follows Keep-a-Changelog 1.1.0 section structure (Added plus Changed plus Deprecated plus Removed plus Fixed plus Security); SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit: 7979dc9
references:
  - https://semver.org/
  - https://keepachangelog.com/en/1.1.0/
  - https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
  - https://cli.github.com/manual/gh_release_create
  - decisions/ADR-001-brief-alignment-tight-calendar-with-fallback-ladder.md
  - decisions/ADR-030-deliverable-format-quarto-html-site.md
  - decisions/ADR-032-hf-hub-publication-headline-rungs-only.md
transcript: transcripts/2026-05-16__phase-0-07__submission-deliverables.md
---

# ADR-033: GitHub release strategy — rehearsal tag + SemVer submission tag + post-submission patches

## Status

Accepted (2026-05-16). Closes the third of 4 [OPEN] rows in Phase 0-07 (§Submission — row 349). Companion to ADR-030 (deliverable format — tag push triggers Quarto publish), ADR-031 (reading paths — reviewer URLs pinned at tag), ADR-032 (HF Hub publication — gated by rehearsal tag), and ADR-034 (reproducibility tier — T0 commands reference HF Hub repos at known SHA pin).

## Context

Tags in git mark immutable point-in-time references. For this submission, tags serve three load-bearing functions:

1. **Reviewer URL stability** — ADR-031 (reading paths) requires stable cross-link permalinks; if `main` advances after submission, untagged URLs rot.
2. **Reproduction reference** — ADR-034 (reproducibility tier) anchors "a stranger can reproduce headline numbers" to a specific commit; tag = friendlier name for that commit SHA.
3. **Audit trail granularity coarser than ADR `closing_commit`** — 33+ ADRs each carry `closing_commit: <SHA>`; tags add a coarser human-readable layer on top.

ADR-030's Quarto + GH Pages workflow also triggers on tag push — so tags double as deploy triggers, not just historical markers.

Five strategy positions on the spectrum were considered (per Q3 walk):
- (A) Single submission tag only — minimal discipline; loses dress-rehearsal value.
- (B) Phase-boundary tags + submission tag — granular but adds tagging discipline overhead under tight deadline; ADR `closing_commit` already provides finer-grained pinning.
- (C) Submission + post-submission patches only — reviewer URL stable; live URL advances on patches; matches SemVer convention.
- (D) Pre-submission rehearsal + submission tag — dress-rehearsal pattern catches publish-pipeline issues before canonical submission tag.
- (E) Continuous SemVer per work unit — tag flood; pollutes releases UI.

User selection at Q3 walk: **D + C-post-submission**.

## Decision

**Tag sequence**:

| Tag | When | Trigger | Purpose |
|---|---|---|---|
| `v0.9.0-rc1` | End of Phase 4 (release candidate) | Manual `git tag v0.9.0-rc1 && git push origin v0.9.0-rc1` | Dress-rehearsal — fires full publish pipeline (Quarto site + GH Pages deploy + HF Hub model card pushes per ADR-032). Catches first-time-CI / auth / schema issues 24+ hours before submission day. If rehearsal fails, fix-forward via new commits + `v0.9.0-rc2`. |
| `v1.0.0` | Submission day (2026-05-18 per ADR-001) | Manual `gh release create v1.0.0 ...` | Canonical reviewer reference. CHANGELOG.md entry committed. GH release object with `_site.tar.gz` asset. |
| `v1.0.x` (optional) | Post-submission per patch | Manual | Typo / link / reviewer-feedback fixes. Reviewer URL stays pinned at `v1.0.0`. Live Quarto site advances. |
| `v2.0.0` (optional) | Post-submission per methodology revision | Manual + superseding ADR | Reserved for actual methodology revisions, not patch-grade fixes. Signals "the submission has been revised; re-read." |

**Tag version format**: `vMAJOR.MINOR.PATCH` per SemVer 2.0.0 (https://semver.org/). Chosen over:
- Annotated suffix `v1.0.0-submission` — less SemVer-tooling-friendly; SemVer pre-release identifier semantics confuse `gh release` defaults.
- Calendar-versioning `2026.05.18` — date-anchored but breaks SemVer-bump semantics for post-submission patches.

**CHANGELOG.md** committed at repo root in Keep-a-Changelog 1.1.0 format (https://keepachangelog.com/en/1.1.0/). Structure:

```markdown
# Changelog

All notable changes documented per Keep-a-Changelog 1.1.0.

## [Unreleased]
### Added
- (continuously populated as features land)
### Changed
- ...
### Fixed
- ...

## [v1.0.0] - 2026-05-18
### Submission
- Initial Ciphero take-home submission.
- Quarto site published to GH Pages.
- 3 trained-rung checkpoints published to HF Hub per ADR-032.
- See methodology writeup at https://brandon-behring.github.io/prompt-injection-detection-submission/

## [v0.9.0-rc1] - 2026-05-17
### Release candidate
- Dress-rehearsal tag — exercises the publish pipeline.
- Fires the Quarto + GH Pages + HF Hub model card publication workflow per ADR-030 + ADR-032.
```

**GH release for `v1.0.0`** — created via:

```bash
gh release create v1.0.0 \
  --title "Submission v1.0.0" \
  --notes-file CHANGELOG.md \
  --generate-notes \
  _site.tar.gz \
  CHANGELOG.md
```

Release assets attached:
- `CHANGELOG.md` (always attached by `--notes-file`).
- `_site.tar.gz` (offline-readable Quarto site bundle; built via `tar czf _site.tar.gz _site/` after `quarto render`).

NOT attached as release binaries:
- Per-row predictions parquet files — stay in `results/predictions/` within the repo at their natural location. Duplicating large parquet files as release binaries is wasteful + the per-row predictions are reachable from the tagged source pin.

**Reviewer email at submission** — three URLs + private attachment:

| URL | Purpose | Drift behavior |
|---|---|---|
| `https://github.com/brandon-behring/prompt-injection-detection-submission/tree/v1.0.0` | Canonical source pin | Never drifts |
| `https://brandon-behring.github.io/prompt-injection-detection-submission/` | Live rendered Quarto site | Reflects latest patch (`v1.0.x`) |
| `https://github.com/brandon-behring/prompt-injection-detection-submission/releases/tag/v1.0.0` | GH release page | CHANGELOG + `_site.tar.gz` download |

Plus transcripts as private email attachment (gitignored, per existing convention).

**No phase-boundary tags during Phases 1-3** — ADR `closing_commit` field already pins history at ADR-grain (finer than phase-grain); phase-boundary tags would add discipline overhead under tight deadline without paying back.

**Patch-tag protocol** — `v1.0.x` patches restricted to non-methodology fixes (typos, broken links, reviewer-feedback responses to questions of the form "did you mean X"). Methodology revisions require `v2.0.0` + superseding ADR.

## Consequences

### Positive

- **Rehearsal tag mitigates first-time-CI risk** — the worst moment to discover that `quarto-actions/publish@v2` permissions are misconfigured is submission day; `v0.9.0-rc1` surfaces these issues 24+ hours earlier.
- **Reviewer URL is stable forever** — `v1.0.0` source pin never drifts; reviewer can audit at exactly the submission state regardless of post-submission iteration.
- **Live URL stays useful post-submission** — `v1.0.x` patches improve the rendered site for late readers; reviewer who wants the original submission has the tagged URL.
- **CHANGELOG.md is the audit trail** — human-language entries (not git-shortlog dumps); reviewer can read the release notes without git archaeology.
- **SemVer compatibility with `gh release` tooling** — `gh release create v1.0.1` etc. works without flag adaptation; SemVer-aware tools sort releases correctly.
- **Avoids tag flood** — ~3 tags total (rehearsal + submission + maybe 1-2 patches); GH releases UI stays clean.

### Negative / cost

- **Manual tagging discipline** — both `v0.9.0-rc1` and `v1.0.0` are manual operations; risk of forgetting at the moment of submission. Mitigation: Phase 5 close-checklist explicitly enumerates the tag-push steps.
- **CHANGELOG.md maintenance overhead** — `Unreleased` section needs ongoing updates as features land; can drift if not maintained. Mitigation: `gh release create --generate-notes` flag auto-generates from commit messages as a fallback if the manual CHANGELOG falls behind.
- **`_site.tar.gz` release asset adds a build step** — `tar czf _site.tar.gz _site/` after Quarto render. Trivial; can be part of `make release-bundle` target.

### Neutral

- **GH Pages serves single live URL** — no built-in "this URL is frozen at v1.0.0" affordance. Mitigation per Limitation below; not a deal-breaker.
- **Tag versioning convention is SemVer-strict** — minor bumps (`v1.1.0`) are not currently scoped; reserved for post-submission feature additions if iteration continues.

### Limitation

GH Pages publishes a single live URL pinned to whatever the latest deploy was. There is no built-in "this URL = v1.0.0 frozen forever" pattern without extra tooling (e.g., snapshot `_site/` to a `submission-v1.0.0` branch and serve that as a separate GH Pages config — overkill for this scope). Mitigation: the canonical-submission tag URL points at *source*, not the rendered HTML site; reviewer can `git checkout v1.0.0 && quarto preview` for a frozen-rendered view; the `_site.tar.gz` release asset provides an offline-readable snapshot.

### Extension condition for revisit

- **Reviewer-feedback-driven methodology revision**: bump to `v2.0.0` via superseding ADR with rationale; signals "re-read" to anyone watching the repo.
- **Rehearsal failure cascade**: if `v0.9.0-rc1` reveals a foundational publish-pipeline issue (e.g., `quarto-actions/publish@v2` is broken on the GH runners), fall back to a manual `quarto publish gh-pages` via the developer's local machine — fix-forward, not abandon-the-format; document via Phase 5 incident note.
- **Phase 1+ surprise that requires phase-boundary tagging**: if a Phase 2-3 surprise (e.g., a training run that's particularly valuable to be able to reproduce in isolation) emerges, add a phase-boundary tag (`v0.2.0-phase2-training-complete`) via Phase 1+ ADR amendment; tag-flood-avoidance is heuristic, not absolute.
- **Multi-org / multi-account complications**: if the repo is moved to a Ciphero org post-submission, the URLs in the submission email become legacy redirects; mitigation = preserve the old URLs as GitHub repo redirects for at least 1 year.

## Alternatives Considered

- **(A) Single submission tag only** — loses the dress-rehearsal value; first-time-CI failures would surface on submission day rather than at rehearsal. Rejected per Q3 walk.
- **(B) Phase-boundary tags + submission tag** — ADR `closing_commit` already provides finer-grained pinning; phase-boundary tags would add discipline overhead under tight deadline without paying back. Rejected per Q3 walk.
- **(E) Continuous SemVer per work unit** — tag flood; pollutes `gh release` UI; loses the "what's the submission?" signal entirely. Rejected per Q3 walk.
- **Annotated suffix `v1.0.0-submission`** — less SemVer-tooling-friendly; `gh release` defaults misinterpret SemVer pre-release identifiers; rejected in favor of clean `v1.0.0`.
- **Calendar-versioning `2026.05.18`** — date-anchored but breaks SemVer-bump semantics for post-submission patches (no clean MAJOR/MINOR/PATCH ladder); rejected.
- **Per-row predictions as release asset** — duplicates files already in `results/predictions/` accessible at the tagged source pin; rejected for storage waste.

## References

- SemVer 2.0.0 spec — https://semver.org/
- Keep-a-Changelog 1.1.0 — https://keepachangelog.com/en/1.1.0/
- GitHub releases — https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
- `gh release create` manual — https://cli.github.com/manual/gh_release_create
- ADR-001 (tight calendar — informs the rehearsal-tag deadline-risk-mitigation framing)
- ADR-030 (Quarto + GH Actions publish — tag triggers the publish workflow)
- ADR-032 (HF Hub publication — gated by rehearsal tag success)

## Transcript

See `transcripts/2026-05-16__phase-0-07__submission-deliverables.md` for the conversation that led to this decision (Q3 walk + option D + C-post + version format + release assets).
