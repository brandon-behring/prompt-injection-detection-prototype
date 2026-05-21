---
adr_id: "054"
slug: results-page-as-third-entry-artifact-extending-adr-053
title: RESULTS.md as third entry artifact — narrow supersession of ADR-053 dimension 1 (two-entry-artifacts); dimensions 2-5 unchanged
date: 2026-05-18
status: Accepted
claim_id: CLAIM-054
claim: >-
  ADR-053 (landed at v1.0.4 — one commit before v1.0.5) locked the
  Quarto reading-guide architecture in 5 governance dimensions, the
  first of which was "two entry artifacts: EXECUTIVE_SUMMARY.md
  (1-page decision-maker layer) + index.qmd (reviewer-landing
  reading guide)". Post-v1.0.4, user feedback identified that the
  actual model-run results were either missing from the Quarto
  site or hard to find: the 5-rung × 5-slice AUPRC + AUROC +
  recall@FPR1% grid was never tabulated on the rendered site
  (only the 3-row pooled_ood trio appears on index.qmd); the 7
  Phase 4 figures (`docs/plots/F*.svg`) were never embedded in
  any rendered page; and the raw-data parquets in `evals/` were
  reachable only via repo clone or manual GitHub navigation. The
  reading-guide architecture had an artifact-discovery gap.

  Decision: add a third entry artifact `RESULTS.md` with a
  distinct role from the existing two — **data-disclosure /
  artifact-discovery** (vs EXECUTIVE_SUMMARY = thesis-distillation
  and index.qmd = reviewer-orientation). Narrowly supersede
  ADR-053 dimension 1 only ("two entry artifacts" becomes "three
  entry artifacts"); dimensions 2-5 (3-path canonical order +
  Headline-finding-block requirement + interpretation pedagogy
  requirement on index.qmd + pointer convention) are unchanged.

  RESULTS.md scope: (1) full 5×5 AUPRC grid with N/A markers in
  single-class cells per ADR-050; (2) AUROC cross-paper
  diagnostic at same shape; (3) recall@FPR1% policy-relevant
  grid; (4) embedded `docs/plots/F1-F7.svg` figures with
  provenance; (5) raw-data table with GitHub blob URLs at
  tree/v1.0.5 for every parquet + JSON in `evals/`; (6)
  reproducibility commands mirroring the index.qmd T0/T1/T3
  tier table (DRY). Sidebar placement under the "Reading guide"
  section as the third entry, after EXECUTIVE_SUMMARY +
  index.qmd, so the cold reviewer arc (thesis → orientation →
  results) is one sidebar click each.

  Pointer convention extension: index.qmd Results section +
  EXECUTIVE_SUMMARY reading-path + WRITEUP §Results all
  cross-reference RESULTS.md as the canonical artifact-
  disclosure page. Interpretation pedagogy stays on index.qmd
  (ADR-053 dimension 4) and is NOT duplicated on RESULTS.md —
  RESULTS is for the reader who already knows they want the
  numbers; index.qmd is for the reader who needs the framing.
source: transcripts/2026-05-18__phase-12-05-results-page-and-badges.md (private; emailed to reviewer separately at submission per ADR-029)
acceptance_criterion: >-
  At v1.0.5 close, `RESULTS.md` exists at repo root + renders
  to `_site/RESULTS.html` + appears in the Quarto sidebar under
  "Reading guide" as the third entry after EXECUTIVE_SUMMARY +
  index.qmd. It contains: (a) §1 full 5-rung × 5-slice AUPRC
  grid with N/A markers; (b) §2 5×5 AUROC diagnostic;
  (c) §3 5×5 recall@FPR1% policy grid; (d) §4 7 embedded
  figures (F1-F7) with provenance footers; (e) §5 raw-data
  table linking every artifact in `evals/` to GitHub at
  tree/v1.0.5; (f) §6 reproducibility tier mirror. ADR-053
  frontmatter is edited in-place to add
  `superseded_by: [ADR-054]` per the established convention
  (ADR-050 had its frontmatter edited when ADR-052 narrowly
  superseded R2; same pattern here). index.qmd + EXECUTIVE_SUMMARY
  + WRITEUP §Results all carry pointers to RESULTS.md.
closing_commit: v1.0.5
supersedes: [ADR-053]
superseded_by:
  - "062"  # back-link added per ADR-076 frontmatter-backfill discipline; ADR-062 supersedes on navigation-clarity axis
references:
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/RESULTS.md
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/decisions/ADR-050-rung-slate-narrowing-llm-judges-and-full-ft-ood-dropped.md
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/decisions/ADR-046-phase-4-analysis-implementation-bundle.md
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/evals/metrics/per_cell.parquet
  - https://github.com/brandon-behring/prompt-injection-detection-prototype/blob/main/evals/bootstrap/marginal_cells.parquet
transcript: transcripts/2026-05-18__phase-12-05-results-page-and-badges.md
---

# ADR-054 — RESULTS.md as third entry artifact (narrow supersession of ADR-053 dimension 1)

## Status

Accepted (2026-05-18; landed in v1.0.5 patch alongside README
badges + cross-reference pointers).

## Context

[ADR-053](ADR-053-reading-guide-governance-and-newcomer-paths.md)
landed at v1.0.4 (commit `f744cd9`) anchoring the Quarto
reading-guide architecture in 5 governance dimensions:

1. **Two entry artifacts** — `EXECUTIVE_SUMMARY.md` (1-page
   decision-maker layer) + `index.qmd` (reviewer-landing reading
   guide).
2. **3 canonical reading paths** — A1 Quick-skim (~15 min) +
   A2 Audit (~60 min) + A3 Reproduce (~30 min CPU).
3. **Headline-finding-block-on-index** requirement.
4. **Interpretation pedagogy on index.qmd** requirement (5
   patterns: prevalence baseline, cross-family OOD, negative
   LoRA delta, ProtectAI non-monotone, val→LODO threshold).
5. **Pointer convention** — index.qmd → EXECUTIVE_SUMMARY →
   WRITEUP → spokes → ADRs.

One commit after v1.0.4 landed (the same conversation), user
surfaced a separate concern: *"in the qquatro it seems that
the actual results of our model runs are either missing or so
hard to find that no one can easily access them."* Inspection
confirmed:

- The 5-rung × 5-slice AUPRC + AUROC + recall@FPR1% grid was
  never tabulated on the rendered Quarto site. `index.qmd`
  showed a 3-row pooled_ood AUPRC trio (a curated headline,
  not the full grid). `EXECUTIVE_SUMMARY.md` showed 4 headline
  claims with select numbers. `WRITEUP.md §Results` had the
  IID-vs-OOD primary-narrative table but pointed at the
  parquet files by path, not via rendered HTML.
- The 7 Phase 4 figures (`docs/plots/F1-F7.svg` per ADR-046;
  Pareto + ROC overlay + PR per rung + reliability triptych +
  per-slice heatmap + LODO breakdown + dual-policy grid) were
  on disk + on GitHub but never embedded in any rendered
  Quarto page. A reviewer browsing the live site would not
  encounter them unless they manually opened the SVGs via
  GitHub blob URLs.
- The raw-data parquets in `evals/` (282 prediction parquets +
  bootstrap CIs + audit JSON + per-row metrics) were reachable
  only via repo clone or manual GitHub tree navigation. No
  rendered page surfaced a "here are all the artifacts + their
  blob URLs" disclosure table.

The user's framing — *"I always thought (1) was part of the
plan, but maybe it was oversight"* — is the governance
diagnosis: ADR-053 governed the reading-guide architecture but
did not govern artifact discovery. A reviewer landing cold on
the Quarto site could read the thesis (EXECUTIVE_SUMMARY) +
orient (index.qmd) + skim methodology (WRITEUP + spokes) +
audit governance (ADRs) — but could NOT reach the raw results
+ figures + parquet artifacts within the rendered site
boundary. ADR-053 needed extension.

## Decision

Add `RESULTS.md` as a **third entry artifact** in the
reading-guide architecture, with a role distinct from the
existing two:

| Entry artifact          | Role                                | Governing ADR |
|---|---|---|
| `EXECUTIVE_SUMMARY.md`  | 1-page thesis distillation          | ADR-053 + ADR-054 |
| `index.qmd`             | Reviewer orientation + headline + interpretation pedagogy | ADR-053 + ADR-054 |
| `RESULTS.md` *(new)*    | Data disclosure + artifact discovery | ADR-054 (this) |

The three artifacts form a **coordinated set** for a cold
reviewer's natural click arc: **thesis → orientation →
results**. Sidebar placement under the "Reading guide"
section reflects the coordination — `RESULTS.md` is the third
entry, one sidebar click from landing.

### What changes in ADR-053

Only dimension 1 ("two entry artifacts" → "three entry
artifacts"). Dimensions 2-5 are unchanged:

- **Dimension 2 (3-path canonical order)**: unchanged. RESULTS
  is NOT a fourth reading path; it is a destination accessed
  from any of the 3 existing paths.
- **Dimension 3 (Headline-finding-block-on-index)**: unchanged.
  index.qmd still carries the headline AUPRC trio + cross-family
  framing in its Results section. RESULTS extends that with the
  full grid but does not replace the index obligation.
- **Dimension 4 (Interpretation pedagogy on index.qmd)**:
  unchanged. The 5 interpretation patterns (prevalence baseline,
  cross-family OOD, negative LoRA delta, ProtectAI non-monotone,
  val→LODO threshold transfer) remain on index.qmd. RESULTS is
  data-disclosure; the framing the user needs to read the data
  is on the reading guide.
- **Dimension 5 (Pointer convention)**: extended (not changed).
  New rule: index.qmd Results section + EXECUTIVE_SUMMARY
  reading-path step + WRITEUP §Results all cross-reference
  RESULTS.md as the canonical artifact-disclosure page. The
  existing arrow chain (index → EXECUTIVE_SUMMARY → WRITEUP →
  spokes → ADRs) is preserved; RESULTS is a sibling-of-
  EXECUTIVE_SUMMARY accessed via cross-link from index.qmd or
  direct sidebar navigation.

### What goes in RESULTS.md

Per the v1.0.5 implementation:

1. **§1 — 5-rung × 5-slice AUPRC grid** with N/A markers in
   single-class cells (bipia, injecagent, notinject) per
   ADR-050 single-class-slice convention. Each N/A cell carries
   a pointer to the raw prediction parquet at
   `evals/predictions/<rung>__fold0__seed42__<slice>.parquet`.
   Above the grid: a "How to read this grid" callout explaining
   the prevalence-baseline convention (AUPRC's random-predictor
   floor = positive prevalence, not 0.5) + the single-class
   exclusion rationale.

2. **§2 — 5×5 AUROC grid** at the same shape. Secondary
   diagnostic per ADR-006 + WRITEUP/eval-design.md §5.1
   (AUPRC is primary under class imbalance).

3. **§3 — 5×5 recall@FPR1% grid** (mean across 4 folds × 3
   seeds = 12 cells). Operational policy-relevant slice per
   ADR-025 + WRITEUP/threshold-policy.md §7. Single-class cells
   marked N/A (recall undefined where no positives; FPR
   undefined where no negatives).

4. **§4 — 7 embedded figures** from `docs/plots/F1-F7.svg`
   (Pareto + ROC overlay + PR per rung + reliability triptych +
   per-slice heatmap + LODO breakdown + dual-policy grid).
   Provenance: commit 948c50a (v1.0.1 era; post Item-4
   single-class filter; fresh).

5. **§5 — Raw-data access table** with GitHub blob URLs at
   `tree/v1.0.5/evals/...` for every artifact: `results.json`,
   `metrics/per_cell.parquet`, `bootstrap/marginal_cells.parquet`,
   `bootstrap/paired_cells*.parquet`, `audit/cross_fold_ci_audit.parquet`,
   `audit/mde_per_cell.parquet`, `audit/verification_reachability.json`,
   `operating_points/dual_policy.parquet`, the 282-file
   `predictions/` tree, `predictions_val/`, `data_audit.json`,
   `dedup_calibration.json`, `leakage_report.json`,
   `contamination_scan.json`, `cost_ledger.csv`. Plus a
   single-class slice pointer subsection (bipia + injecagent +
   notinject predictions on disk despite N/A in §1-§3).

6. **§6 — Reproducibility** — mirrors index.qmd's T0/T1/T3
   tier table (DRY; cross-references index.qmd as canonical;
   notes the ADR-051 carryforward that `make eval-from-hub`
   non-dry-run body lands v1.1.x).

### Sidebar placement

Under the "Reading guide" section in `_quarto.yml` sidebar,
positioned as the third entry after EXECUTIVE_SUMMARY +
index.qmd:

```yaml
sidebar:
  contents:
    - section: "Reading guide"
      contents:
        - EXECUTIVE_SUMMARY.md
        - index.qmd
        - RESULTS.md   # ADR-054 third entry artifact
    - section: "Methodology"
      ...
```

Rationale (locked at /exploring-options batch 6 Q2 per the
user's "think through how this would be clearest to a new
reader" prompt): the cold-newcomer click arc is **thesis →
orientation → results → methodology → evidence → governance**.
RESULTS should be one sidebar click from landing, alongside
EXECUTIVE_SUMMARY + index.qmd. Burying it under "Evidence +
audit" (below 8 methodology spokes) or in a new "Results +
artifacts" section with 1 entry would not match the natural
reader arc.

## Consequences

### Positive

- **Artifact discoverability closed.** A cold reviewer on the
  live Quarto site reaches the full 5-rung × 5-slice grid + 7
  figures + raw-data blob URLs in 1 sidebar click. The
  rendered-site surface now contains every numeric finding the
  project produced.
- **N/A disclosure for single-class slices makes the ADR-050
  convention auditable.** Pre-v1.0.5 the single-class
  exclusion was a methodology line in WRITEUP; v1.0.5 puts the
  N/A cells in a grid with explicit pointers to the raw
  predictions. Reviewers see what was attempted + what was
  reported + where the unreported predictions are.
- **Figures move from disk-only to rendered.** F1-F7 were
  never embedded in any rendered page pre-v1.0.5. Now they
  appear on RESULTS with provenance metadata visible.
- **Raw-data discovery is now point-and-click.** Pre-v1.0.5 a
  reviewer had to `git clone` + `ls evals/` to find the
  parquets. v1.0.5 surfaces every artifact's blob URL on a
  rendered page.
- **Reading-guide architecture is now complete.** ADR-053 +
  ADR-054 together govern the 3-entry-artifact set; future
  iterations cannot drop any of them without superseding the
  governance.

### Negative

- **ADR-053 frontmatter is edited in-place.** `superseded_by:
  [ADR-054]` is added to ADR-053's YAML. Per ADR-029
  immutability convention, ADR bodies are immutable; frontmatter
  field updates for supersession tracking are the established
  exception (ADR-050 had `superseded_by: [ADR-052]` added when
  ADR-052 landed; same pattern here). Documented in the v1.0.5
  CHANGELOG entry.
- **Sidebar grows.** The "Reading guide" section now has 3
  entries instead of 2; cold reviewer sees a slightly busier
  sidebar header. Trade-off: 1 extra sidebar entry buys
  artifact discoverability that was previously impossible
  without clone-and-grep.
- **RESULTS could drift from the metric source if regen
  misses it.** RESULTS hard-codes AUPRC + AUROC + recall@FPR1%
  values from the v1.0.5-state of the parquets. If `evals/`
  is regenerated post-v1.0.5 (e.g., a v1.1.0 retraining), the
  RESULTS tables must be re-derived. Mitigation: every cell
  carries an explicit source-parquet citation; a future
  iteration can add a render-time check that the RESULTS
  values match the parquet values within a tolerance.

### Neutral

- ADR-053 body unchanged. Only frontmatter `superseded_by` updated.
- WRITEUP §Results continues to carry the IID-vs-OOD
  narrative table (the methodology-rooted primary view); RESULTS
  is the artifact-disclosure complement.
- index.qmd's Results section + interpretation pedagogy
  unchanged in scope (ADR-053 dimensions 3 + 4 preserved).

## Alternatives Considered

### A. Embed everything into existing WRITEUP §Results (no new page)

Augment WRITEUP §Results with the full 5×5 grid + embedded
figures + raw-data table. No new file; WRITEUP becomes the
canonical results-disclosure surface. **Rejected** at
/exploring-options batch 5 Q1: the user's framing ("I always
thought (1) was part of the plan") implied a dedicated artifact
was expected; merging into WRITEUP would bury the artifact-
discovery surface under methodology narrative. A reviewer
looking for "where are the results" should not need to scroll
through methodology to find them.

### B. Pointers-only — links from index.qmd / WRITEUP to GitHub blob URLs

Minimal fix — add blob-URL pointers from index.qmd Results
section + WRITEUP §Results to the raw parquets. No rendered
HTML tables; reviewer clicks through to GitHub. **Rejected**
at /exploring-options batch 5 Q1: the user's concern (*"no
one can easily access them"*) is precisely the click-through
friction. Rendered HTML tables on the Quarto site eliminate
that friction.

### C. Treat RESULTS as a methodology spoke under WRITEUP/

Place results.md under `WRITEUP/` alongside the 8 existing
spokes (`eval-design.md`, `model-rungs.md`, etc.). **Rejected**:
the spokes are topic-focused methodology decompositions
(per ADR-031); RESULTS is artifact-disclosure (a different
role). The 8 spokes establish "how the methodology works";
RESULTS surfaces "what the methodology produced." Different
governance tier.

### D. Defer RESULTS to v1.0.6 (separate patch)

Land badges in v1.0.5; land RESULTS + ADR-054 in v1.0.6.
**Rejected** at /exploring-options batch 5 Q2: bundling in
v1.0.5 closes the v1.0.4-era polish backlog atomically.
The badges (cosmetic) + RESULTS (substantive) share no
implementation dependency, but split tagging adds ~30 min
overhead per cycle.

### E. Don't write ADR-054; treat RESULTS as a new file with no governance

Add `RESULTS.md` without an ADR; rely on ADR-053 + ADR-029 to
cover the existing convention. **Rejected**: ADR-053 dimension 1
explicitly says "two entry artifacts." Adding a third without
governance violates the project's "no methodology component
without an ADR" anti-pattern. RESULTS is reader-facing
governance-load-bearing the same way the other two entry
artifacts are (reader confusion if any of the three is dropped
silently). ADR-054 captures the third-artifact role + sidebar
placement + cross-link convention in immutable form.

### F. Combined supersession (ADR-054 supersedes both ADR-050 + ADR-053)

ADR-054 could in principle cover the ADR-050 single-class
convention + the ADR-053 reading-guide architecture together
since RESULTS surfaces both. **Rejected**: ADR-050 governs the
single-class convention itself (which metrics are defined on
which slices); ADR-054 governs how to *disclose* the
convention's consequences in the rendered site. Different
governance dimensions; conflating them would muddy both.
ADR-054's `supersedes: [ADR-053]` is sufficient.

## Links

- [ADR-053 — Reading-guide governance + newcomer onboarding paths](ADR-053-reading-guide-governance-and-newcomer-paths.md) — narrowly superseded on dimension 1 by this ADR; dimensions 2-5 unchanged.
- [ADR-050 — Rung-slate narrowing + single-class-slice convention](ADR-050-rung-slate-narrowing-llm-judges-and-full-ft-ood-dropped.md) — sources the N/A markers in RESULTS §1-§3.
- [ADR-046 — Phase 4 walkthrough](ADR-046-phase-4-analysis-implementation-bundle.md) — sources the F1-F7 figure rendering pipeline.
- CLAUDE.md §"Phase 0 workflow" — ADR immutability rule (governs the in-place frontmatter `superseded_by` edit pattern; ADR-053 + ADR-050 both edited under this convention). Narrow factual-typo exception per [ADR-067](ADR-067-immutability-clarification-and-canonical-slug-reference.md).
- [ADR-032 — HF Hub model card schema](ADR-032-hf-hub-publication-headline-rungs-only.md) — `evals/results.json` source for HF Hub T0 reproducibility tier; surfaced in RESULTS §5.
- [`RESULTS.md`](../RESULTS.md) — the v1.0.5 artifact this ADR governs.
- [`index.qmd`](../index.qmd) — entry artifact 2 (orientation; ADR-053 + ADR-054).
- [`EXECUTIVE_SUMMARY.md`](../EXECUTIVE_SUMMARY.md) — entry artifact 1 (thesis distillation; ADR-053 + ADR-054).
