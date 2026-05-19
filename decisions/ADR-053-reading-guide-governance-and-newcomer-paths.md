---
adr_id: "053"
slug: reading-guide-governance-and-newcomer-paths
title: Reading-guide governance + newcomer onboarding paths — two entry artifacts + 3 reading paths + Headline-finding-block + interpretation pedagogy + pointer convention
date: 2026-05-18
status: Accepted
claim_id: CLAIM-053
claim: >-
  The Quarto site has two entry artifacts with distinct roles:
  EXECUTIVE_SUMMARY.md (1-page decision-maker layer; added at
  v1.0.3 per NEXT_STEPS §1.7) and index.qmd (reviewer-landing
  reading guide). Until v1.0.4 neither was anchored in an ADR —
  ADR-030 locks Quarto HTML as the deliverable but not reading-
  flow architecture; ADR-033 locks release-strategy URLs but not
  landing-page content. v1.0.4's stale-content audit surfaced
  that index.qmd had drifted into Phase-0-time scaffolding
  language: stale ADR count (34+), stale make commands, stale
  Status section ("spokes are skeletons; Phase 5 populates
  them"), silent on the actual headline finding. This ADR
  retroactively + prospectively anchors the reading-guide
  architecture in 5 governance dimensions so the drift cannot
  recur without an explicit superseding ADR.

  Decision (5 governance dimensions):
  (1) Two entry artifacts with distinct roles — EXECUTIVE_SUMMARY
  for decision-makers + time-constrained reviewers; index.qmd
  for reviewers clicking into the live site root.
  (2) Three reading paths canonical — A1 Quick-skim (~15 min) +
  A2 Audit (~60 min) + A3 Reproduce (~30 min CPU).
  (3) Headline-finding-block-on-index is required — index.qmd
  must state the headline numbers up-front, not bury them
  behind "see WRITEUP §5" pointers.
  (4) Interpretation pedagogy on index.qmd is required —
  reviewers shouldn't have to assemble the framing (prevalence
  baseline, cross-family OOD, negative-delta meaning,
  non-monotone versioning, threshold transfer) from spokes.
  (5) Pointer convention — index.qmd → EXECUTIVE_SUMMARY →
  WRITEUP → spokes → ADRs.

  Retroactive ADR coverage: EXECUTIVE_SUMMARY.md was added at
  v1.0.3 per NEXT_STEPS §1.7 alone (no ADR) — ADR-053 covers
  its role retroactively. NEXT_STEPS.md §1.7 gets a back-
  reference to ADR-053 in the v1.0.4 patch.

  Driver: user question "does the reading guide clearly say
  what the final results were? is it organized in a way that
  makes sense to someone coming to the project. Does it
  conform to our initial guidance and/or does our ADRs need to
  be enriched?" (2026-05-18). The honest answer at v1.0.3
  was NO (silent on results) + YES (ADRs need enrichment).
  This ADR is that enrichment + the v1.0.4 index.qmd rewrite
  is the implementation.
source: transcripts/2026-05-18__phase-12-04-reading-guide-governance.md (private; emailed to reviewer separately at submission per ADR-029)
acceptance_criterion: >-
  At v1.0.4 close, index.qmd contains: (a) a "Results" section
  with the 3-row pooled_ood AUPRC trio + CI bounds sourced from
  evals/bootstrap/marginal_cells.parquet; (b) a "How to read
  these numbers" section with 5 interpretation patterns
  (prevalence baseline, cross-family vs cross-source, negative
  LoRA delta, ProtectAI non-monotone, val→LODO threshold
  transfer); (c) all 3 reading paths labeled A1/A2/A3; (d) a
  "Headline ADRs to read" curated sub-list in the A2 audit
  path; (e) Status section anchored in v1.0.4 reality (not
  Phase-0-time scaffolding); (f) pointer at EXECUTIVE_SUMMARY
  as A1 step 1. EXECUTIVE_SUMMARY.md keeps its 1-page scope +
  retroactive ADR-053 coverage referenced in NEXT_STEPS §1.7.
  Both files render via _quarto.yml render allowlist + appear
  in the sidebar.
closing_commit: v1.0.4
supersedes: []
superseded_by: ["054", "061"]  # narrow supersessions of dimension 1 — once by ADR-054 (adds RESULTS.md as 3rd entry artifact at v1.0.5) and once by ADR-061 (navbar 9→5 / sidebar hub-spoke nesting / landing-page rebuild + READING_GUIDE.md extraction / hub-spoke signposting at v1.1.1). Dimensions 2-5 (3-reading-paths + headline-finding-block + interpretation pedagogy + pointer convention) all preserved.
references:
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/index.qmd
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/EXECUTIVE_SUMMARY.md
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/decisions/ADR-030-deliverable-format-quarto-html-site.md
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/NEXT_STEPS.md
transcript: transcripts/2026-05-18__phase-12-04-reading-guide-governance.md
---

# ADR-053 — Reading-guide governance + newcomer onboarding paths

## Status

Accepted (2026-05-18; landed in v1.0.4 patch alongside the
stale-content sweep that surfaced the gap).

## Context

The Quarto site landing page (`index.qmd`) is the highest-
visibility surface for a reviewer who clicks into the live site
root. EXECUTIVE_SUMMARY.md (added at v1.0.3 per NEXT_STEPS §1.7)
is the parallel 1-page decision-maker artifact. Until v1.0.4
neither file's content shape was governed by an ADR:

- **ADR-030** locks Quarto HTML as the deliverable format
  (vs PDF) but does not anchor reading-flow architecture,
  landing-page content, or interpretation pedagogy.
- **ADR-033** locks the GH release / reviewer-URL strategy
  (rehearsal + canonical + patch tag pattern) but does not
  anchor landing-page content.
- **NEXT_STEPS.md §1.7** documents EXECUTIVE_SUMMARY's intended
  role ("1-page decision-maker layer above the full WRITEUP")
  but is a forward-looking work-list, not a governance ADR.

The v1.0.4 stale-content audit (this re-plan turn) surfaced
that `index.qmd` had drifted materially:

1. **Silent on the actual headline finding.** The pre-v1.0.4
   index said *"pooled IID + pooled OOD numbers per rung"* —
   described WHERE to look, never WHAT the result is. A
   reviewer reading only the reading guide learned zero
   headline numbers.
2. **Stale ADR count.** Index said `34+ ADRs`; actual at
   v1.0.3 close was 52 (v1.0.4 lands ADR-053 → 53).
3. **Stale make commands.** Index said `make eval-from-hub
   RUNG=modernbert-lora` + `make smoke`; canonical targets are
   `RUNG=frozen-probe` / `RUNG=lora` + `make test-smoke`.
4. **Stale repo-identity URLs.** Submission anchors used the
   pre-rename `prompt-injection-detection-submission` slug
   (repo renamed to `prompt-injection-detection-prototype` at
   v1.0.0 Item 1; index.qmd was missed).
5. **Stale Status section.** Index said *"At Phase 0-07 close,
   the spokes are skeletons; Phase 5 populates them"* —
   Phase-0-time scaffolding language anchoring the reader in
   the wrong temporal frame; Phase 5 closed at v1.0.0.
6. **No reference to EXECUTIVE_SUMMARY.md.** The 1-page artifact
   added at v1.0.3 was sidebar-listed but never promoted as the
   A1 Quick-skim step 1 — the natural cold-newcomer arc
   (1-page thesis → reading guide → deep-dive) was not surfaced.

The user explicitly named the governance dimension:
*"Does it conform to our initial guidance and/or does our ADRs
need to be enriched?"* + *"We need in the guide to include a
few analysis of the results and how to interpret them! how did
we overlook this?"* (2026-05-18).

The "how did we overlook this" framing is the load-bearing
diagnosis: reading-guide architecture without an explicit
governance anchor for *what* the guide must contain (results +
interpretation, not just navigation) allowed the v1.0.x trail
to drift into stale-scaffolding + results-silence. ADR-053
captures the lesson.

## Decision

The reading-guide architecture is governed in 5 dimensions:

### 1. Two entry artifacts with distinct roles

- **`EXECUTIVE_SUMMARY.md`** — 1-page decision-maker /
  time-constrained-reviewer entry. Thesis sentence + 4
  headline claims + what-was-characterised + what-is-deferred +
  reading-path pointer + honest reading. ≤300 words
  public-facing. Third-person register. Personal voice +
  apology only appears in the parallel gitignored
  `SUBMISSION.md` cover letter (per `.gitignore:35`).
- **`index.qmd`** — Reading guide. Reviewer-who-clicks-into-
  live-site-root entry. Carries Results section +
  interpretation pedagogy section + 3 reading paths +
  submission anchors + Status section. ~150-200 lines.

These are NOT interchangeable. EXECUTIVE_SUMMARY is the
distillation; `index.qmd` is the orientation.

### 2. Three reading paths canonical

- **A1 Quick-skim (~15 min)** — for the hiring-manager /
  executive read. Step 1 is always EXECUTIVE_SUMMARY (the
  pointer convention; see §5).
- **A2 Audit (~60 min)** — for the ML-researcher /
  due-diligence read. Includes a "Headline ADRs to read"
  curated sub-list so audit readers don't have to grep
  through 53+ files.
- **A3 Reproduce (~30 min CPU; $0)** — for the engineer who
  wants the numbers to land on their machine. Anchors at the
  T0 `make eval-from-hub` reproducibility tier (per ADR-034);
  falls back to T1 `make test-smoke` for no-network code-
  health verification.

These 3 paths are the canonical set; superseding ADRs may
add A4+ paths or revise these, but cannot silently drop one.

### 3. Headline-finding-block-on-index is required

`index.qmd` MUST state the headline numbers up-front, in the
first screen of the rendered page. The pre-v1.0.4 pattern
("see WRITEUP §5 for the table") is banned; a reviewer reading
ONLY the reading guide must learn the cross-family OOD finding
+ the AUPRC trio + the prevalence baseline. Numbers come from
`evals/bootstrap/marginal_cells.parquet` (BCa CI, 10000
resamples) post-single-class-filter; placeholder bounds are
banned.

### 4. Interpretation pedagogy on index.qmd is required

`index.qmd` MUST include "how to read these numbers" framing
patterns. The reviewer should not need to assemble the framing
themselves by clicking through to `WRITEUP/eval-design.md` §5.
Canonical set of 5 patterns (subject to revision via
superseding ADR):

1. **Prevalence baseline vs chance** — AUPRC's random-predictor
   floor equals the positive prevalence (not 0.5).
2. **Cross-family vs cross-source OOD** — the OOD wall is on
   attack types absent from training, not source-distribution
   shift.
3. **Negative LoRA delta meaning** — fine-tuning the head on
   the LODO direct-injection pool actively hurts cross-family
   OOD; the pretrained backbone carries what little OOD signal
   exists.
4. **ProtectAI v1 → v2 non-monotone** — publication version
   monotonicity is not guaranteed under a cross-family slate;
   selection must be slice-aware.
5. **val → LODO threshold transfer fails** — standard "tune
   on val, ship to prod" recipe under-quantifies operational
   FPR; dual-policy threshold (per ADR-025 + WRITEUP/threshold-
   policy.md §7) is the project's response.

Pedagogy lives on `index.qmd` (not in `EXECUTIVE_SUMMARY`)
because the reading guide is the first contact with the
methodology; the executive summary is for readers who already
know they want results-only. WRITEUP/eval-design.md §5 carries
the deeper framing for A2 audit-path readers.

### 5. Pointer convention

```
index.qmd → EXECUTIVE_SUMMARY.md → WRITEUP.md → WRITEUP/*.md (8 spokes) → decisions/ADR-NNN-*.md
```

- `index.qmd` MUST promote EXECUTIVE_SUMMARY as A1 Quick-skim
  step 1.
- `EXECUTIVE_SUMMARY.md` MUST end with a reading-path pointer
  to WRITEUP for the full methodology narrative.
- WRITEUP + spokes MUST cross-reference each other for
  sub-topic deep dives.
- Spokes MAY direct-reference ADRs for governance trail.
- `index.qmd` MAY direct-reference ADRs in the curated
  "Headline ADRs to read" sub-list of the A2 audit path (the
  exception — without this, audit-path readers face the full
  53-ADR ledger).

## Consequences

### Positive

- **`index.qmd` becomes governance-load-bearing for newcomer
  onboarding.** Future edits must preserve the 5 governance
  dimensions or supersede ADR-053.
- **EXECUTIVE_SUMMARY.md's role is now ADR-anchored**, not
  just NEXT_STEPS-anchored. NEXT_STEPS §1.7 gets a backref to
  ADR-053 in the v1.0.4 patch.
- **The interpretation-pedagogy requirement names the
  oversight** that allowed v1.0.x to ship a reading guide
  silent on the actual results. Future iterations cannot
  re-introduce that gap without an explicit supersession.
- **The 5-pattern interpretation set is enumerated**, so a
  reviewer audit of the reading guide has a checklist to
  verify against.
- **Reviewer onboarding arc is explicit**: 1-page thesis
  (EXECUTIVE_SUMMARY) → orientation + results + interpretation
  (index.qmd) → full methodology (WRITEUP + spokes) →
  governance trail (ADRs). No reviewer should need to
  reconstruct this flow themselves.

### Negative

- **Page weight on `index.qmd`.** The v1.0.4 rewrite added ~150
  lines (Results table + 5 interpretation patterns); page is
  no longer terse-navigation-only. Mitigation: the 3 reading
  paths come AFTER the interpretation pedagogy so a reader
  who only wants navigation can skip past via the in-page
  table of contents.
- **Pointer-convention drift risk** in future patches. If a
  WRITEUP spoke is renamed without updating `index.qmd`
  cross-references, the reading guide's curated link list
  goes stale. Partial mitigation via the v1.0.4 `make site`
  render-time link check (Quarto reports broken cross-refs).
- **Locks the 5 interpretation patterns.** A future iteration
  that discovers a 6th pattern must either supersede ADR-053
  or add the pattern via patch ADR (analogous to how ADR-050
  Revisions 1 + 2 amended the rung slate). This is intentional
  — the rigidity is what prevents the silent-drift recurrence.

### Neutral

- ADR-030 (Quarto deliverable) unchanged.
- ADR-033 (release strategy) unchanged.
- NEXT_STEPS.md §1.7 (EXECUTIVE_SUMMARY origin note) keeps its
  forward-looking framing but gains a "ADR-053 retroactively
  anchors this artifact's role + interpretation-pedagogy
  requirement" reference line.

## Alternatives Considered

### A. Reading-guide as pure navigation (no results stated)

Keep `index.qmd` as a pointer-only table; results live entirely
on EXECUTIVE_SUMMARY + WRITEUP. **Rejected** because the user
explicitly asked for results + interpretation on the reading
guide ("we need analysis of the results and how to interpret
them"). The cold-newcomer cost of "two clicks to learn the
headline finding" is real; the page-weight cost of stating
results inline is acceptable.

### B. Single entry artifact (only EXECUTIVE_SUMMARY OR only index.qmd)

Eliminate the duplication; pick one. **Rejected** because the
artifacts serve distinct audiences: EXECUTIVE_SUMMARY for the
30-second decision-maker read; index.qmd for the reviewer
orienting before clicking into deeper artifacts. The 1-page
distillation + the orientation guide are not the same artifact
even when they share content.

### C. Defer the ADR to v1.0.5

Land the v1.0.4 stale-content sweep alone; write ADR-053 in a
v1.0.5 governance patch. **Rejected** in /exploring-options
batch 2 + 3 (2026-05-18): the v1.0.4 patch is already
restructuring `index.qmd` to add the Results +
interpretation-pedagogy sections; landing the governance ADR
atomically with the implementation is cleanest (one tag, one
release notes section, one commit graph entry).

### D. Narrow ADR-053 scope (entry artifacts only)

Only lock the two-entry-artifacts dimension; let the 3-path /
Headline-finding / interpretation-pedagogy / pointer
conventions stay implicit. **Rejected** in /exploring-options
batch 3 Q3 (full-scope option locked): a narrow ADR doesn't
prevent the recurrence the user diagnosed ("how did we
overlook this") — the interpretation-pedagogy requirement is
the load-bearing dimension because that's the gap that
shipped at v1.0.0/v1.0.1/v1.0.2/v1.0.3.

### E. Don't write an ADR; treat the reading guide as documentation

**Rejected** because the project's working contract (CLAUDE.md
"Anti-patterns to avoid": *"Adding a methodology component
without an ADR"*) treats reader-facing methodology surfaces as
governance-load-bearing. The reading-guide architecture
governs how reviewers consume the methodology — that's
methodology-adjacent enough to warrant an ADR.

## Links

- [ADR-030 — Deliverable format: Quarto HTML site](ADR-030-deliverable-format-quarto-html-site.md) — locks the deliverable format that this ADR's reading guide renders on.
- [ADR-033 — GitHub release strategy](ADR-033-github-release-strategy-rehearsal-plus-submission.md) — locks the 3-URL reviewer-submission set referenced from index.qmd's submission anchors.
- [ADR-050 — Rung-slate narrowing](ADR-050-rung-slate-narrowing-llm-judges-and-full-ft-ood-dropped.md) — sources the rung-slate framing the reading guide presents.
- [ADR-052 — Full-FT OOD methodological reframing](ADR-052-full-ft-ood-drop-methodological-reframing-of-adr-050-r2.md) — sources the "negative LoRA delta" interpretation pattern.
- [NEXT_STEPS.md §1.7 EXECUTIVE_SUMMARY origin](../NEXT_STEPS.md) — retroactively governed by this ADR.
- [WRITEUP/eval-design.md §5](../WRITEUP/eval-design.md) — the deeper AUPRC vs AUROC + interpretation framing that A2 audit-path readers continue into.
- [WRITEUP/threshold-policy.md §7](../WRITEUP/threshold-policy.md) — the dual-policy threshold characterisation referenced in interpretation pattern #5.
