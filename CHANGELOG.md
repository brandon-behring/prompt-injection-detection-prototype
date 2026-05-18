# Changelog — prompt-injection-detection-prototype

All notable changes to this project are documented here. Format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/); versions
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Versioning convention

Named tags map to phase gates (refined at Phase 0-07 per ADR-033):

- **`v0.0.0`** — public-seed tag (immediately after the public push)
- **`v0.1.0`** — Phase 0 complete (all 50 `[OPEN]` decisions resolved + ADRs drafted + SPEC_SHEET filled + assumptions.md populated + invariant test stubs exist per Phase 0 close criterion)
- Patch versions (`v0.1.1`, `v0.1.2`, ...) — substantial work-units during Phase 1+
- **`v0.9.0-rc1`** — Phase 4 close release-candidate (per ADR-033) — fires the full publish pipeline (Quarto site build per ADR-030 + GH Pages deploy + HF Hub model card pushes per ADR-032) as a dress-rehearsal 24+ hours before submission day. Catches first-time-CI / auth / schema issues before the canonical tag fires. If rehearsal fails, fix-forward via new commits + `v0.9.0-rc2`
- **`v1.0.0`** — submission ready (Quarto site published to GH Pages per ADR-030; HF Hub model repos published per ADR-032; CHANGELOG entry committed; all WRITEUP `[TBD]` resolved; SUBMISSION_AUDIT clean)
- Post-submission patches (`v1.0.1`, `v1.0.2`, ...) — typo / link / reviewer-feedback fixes per ADR-033; reviewer URL stays pinned at `v1.0.0`; live Quarto site reflects latest patch
- Major bump (`v2.0.0`) — reserved for actual methodology revisions; requires superseding ADR with rationale + reviewer-notification step

Each release entry links closed audit findings (`SUBMISSION_AUDIT.md`) and closing ADRs.

## [1.0.6] — 2026-05-18

eval-toolkit pin v0.34.0 → v0.39.0 bump consuming 3 upstream
resolutions (filed v1.0.3) + library-first refactor of hand-rolled
glue + leakage CI hard-gate + NEXT_STEPS §1 honest accounting +
upstream issue #43 filed for v1.0.8 prep. First patch of the
Path-3 NEXT_STEPS §1 closure sweep per /exploring-options batches
7-9 locks.

### Added

- **`scripts/audit_leakage.py`** — standalone CLI verifying
  `evals/leakage_report.json` shows `leakage_clean=True`. Two
  modes: `--check` (CI-friendly minimal output; exit 0/1) and
  default (human-readable summary). Wraps the same logic as the
  CI hard-gate so operators can run the check locally.

- **`tests/test_invariants.py::test_leakage_report_clean`** —
  implemented (previously named in a docstring comment but absent
  as a function). Asserts `leakage_clean=True` from
  `evals/leakage_report.json`; skips if file missing (CI runs
  the same gate separately).

- **`.github/workflows/ci.yml::leakage`** — new hard-gate job
  failing CI if `leakage_clean != True` in
  `evals/leakage_report.json`. ADR-039 gate 3 intent (leakage
  audit unskipped + green) now met for the leakage axis.

- **`Makefile::audit-leakage`** target — `make audit-leakage`
  invokes `scripts/audit_leakage.py --check`.

- **`decisions/upstream_issues.md` row for eval-toolkit
  [#43](https://github.com/brandon-behring/eval-toolkit/issues/43)** —
  filed at v1.0.6: "Add `fit_platt_binary` + `fit_beta_binary`
  calibrators (binary-class scalar-prob adapters; siblings of
  `fit_temperature_binary` shipped in v0.35.0)". Per
  /exploring-options batch 8 Q1 lock (library-first invariant:
  file upstream before local impl). v1.0.8 will consume when
  shipped; otherwise §1.4 close deferred to v1.1.x.
  (#42 was already taken by an open Croissant verification
  issue; ours got #43.)

### Changed

- **`pyproject.toml`** — eval-toolkit pin bumped
  `git+...@v0.34.0` → `git+...@v0.39.0`. `uv.lock` regenerated.
  Consumes upstream resolutions of 3 issues filed v1.0.3:
  [#39](https://github.com/brandon-behring/eval-toolkit/issues/39)
  `is_metric_defined_for_slice` primitive +
  [#40](https://github.com/brandon-behring/eval-toolkit/issues/40)
  `LeakageCheck.name` read-only `@property` +
  [#41](https://github.com/brandon-behring/eval-toolkit/issues/41)
  `parallel_map` worker-copy memory documentation. All 3 closed
  upstream on 2026-05-18 at 20:13 UTC. Bonus primitives also
  available: `fit_temperature_binary` (v0.35.0), `n_jobs` on
  `evaluate()` / `evaluate_folded()` (v0.36.0),
  `TokenizationLeakageCheck` (v0.37.0).

- **`src/eval/slice_analysis.py`** — refactored to use upstream
  `eval_toolkit.is_metric_defined_for_slice` per #39 resolution.
  Local `SINGLE_CLASS_INCOMPATIBLE_METRICS` constant **deleted**
  (uses upstream `eval_toolkit.SINGLE_CLASS_INCOMPATIBLE_METRICS`).
  Local `is_metric_defined_for_slice(slice_name, metric_name)`
  function preserved as a thin wrapper that derives
  `is_single_class=slice_name in SINGLE_CLASS_SLICES` and
  delegates to upstream. Project-specific knowledge of which
  slice names are single-class stays local (`SINGLE_CLASS_SLICES`
  frozen-set kept). `__all__` updated. No callsite changes (the
  wrapper preserves the local signature).

- **`src/data/audit.py`** — `cast(LeakageCheck, leakage_check)`
  workaround at line 222 removed per #40 resolution
  (`LeakageCheck.name` is now an `@property`; frozen-dataclass
  `CrossSplitLeakageCheck` is mypy-strict-compatible without
  cast). Unused `LeakageCheck` import removed from line 34.
  Unused `cast` import removed from line 29.

- **`decisions/upstream_issues.md`** — 3 rows for #39 / #40 /
  #41 marked **RESOLVED** with consumption notes. New row for
  #43 added (Platt + Beta calibrator request).

- **`decisions/library_imports.md`** — version pin table updated
  v0.31.0 → v0.39.0 (the v0.31.0 entry was stale since X8;
  v1.0.6 brings the doc in sync with the actual pin lifecycle).

- **`NEXT_STEPS.md` §1** — Status (v1.0.6) lines added per Path
  3 honest accounting:
  - §1.1 carryforward to v1.0.7 (4 notebooks).
  - §1.2 carryforward to v1.0.7 (CSV mirror + per_source_rates).
  - §1.3 BH-FDR primitive available since eval-toolkit v0.32
    (unused locally); DeLong + BH-FDR wired in v1.0.7
    `notebooks/02_frozen_vs_lora`.
  - §1.4 6 of 7 components landed; Platt + Beta filed
    upstream #43; v1.0.8 conditional close.
  - **§1.5 closed**: CI hard-gate + invariant + standalone CLI.
  - §1.6 closed (HYPERPARAMETER_DISCLOSURE complete at v1.0.0).
  - §1.7 closed (EXECUTIVE_SUMMARY landed v1.0.3).
  - §1.8 **closed as not-adopted** (WRITEUP uses markdown links;
    citation pattern was never load-bearing).
  - §1.9 carryforward to v1.0.8 (manifest backfill).
  - §1.10 carryforward to v1.1.0 (DeBERTa medium ablation;
    same-session per batch 8 Q3 lock).

- **`NEXT_STEPS.md` §2.4** (new) — Refactor F1/F2/F5 figures
  to upstream eval-toolkit `plot_*` primitives. Deferred from
  v1.0.7 per /exploring-options batch 8 Q4 lock (scope discipline
  on notebook patch); lands at next figure regen or v1.1.1+.

### Notes

- No methodology change. No metric values change. The v0.39.0
  eval-toolkit bump introduces no breaking changes; 171/171 smoke
  tests pass post-bump.
- The library-first invariant just paid off: 3 upstream issues
  filed v1.0.3 + waited; all 3 resolved upstream within ~2 days
  + consumed at v1.0.6 with cleaner local code.

### Files modified (10 file touches)

- `pyproject.toml` (eval-toolkit pin bump).
- `uv.lock` (regenerated via `uv sync`).
- `src/eval/slice_analysis.py` (refactor + `__all__` update).
- `src/data/audit.py` (cast workaround + 2 unused imports removed).
- `decisions/upstream_issues.md` (4 row updates: 3 RESOLVED + 1 NEW).
- `decisions/library_imports.md` (version pin table update).
- `NEXT_STEPS.md` (Status lines added to 10 rows + §2.4 new).
- `.github/workflows/ci.yml` (new leakage hard-gate job).
- `scripts/audit_leakage.py` (new standalone CLI).
- `tests/test_invariants.py` (`test_leakage_report_clean` added).
- `Makefile` (audit-leakage target + .PHONY update).
- `CHANGELOG.md` (this entry).

---

## [1.0.5] — 2026-05-18

README badges + `RESULTS.md` rendered page + ADR-054 reading-guide
governance extension. Closes two post-v1.0.4 polish gaps surfaced in
the same session:

1. **Badges**: user — *"can the documentation be a badge on the top?
   any other badges?"* — README had 0 badges. 9 text-only shields.io
   badges added under H1.
2. **Results visibility on Quarto**: user — *"in the qquatro it seems
   that the actual results of our model runs are either missing or so
   hard to find that no one can easily access them"* — the rendered
   Quarto site never surfaced the full 5-rung × 5-slice grid, the
   7 Phase 4 figures, or raw-data pointers. New `RESULTS.md` (third
   entry artifact) closes the artifact-discovery gap.

### Added

- **`README.md` 9-badge row** under H1, above the thesis blockquote:
  Documentation (live site) + CI workflow + Publish workflow +
  latest Release + HF Hub frozen-probe model card + HF Hub lora
  model card + License MIT + Python 3.13 + ADR count. Text-only
  shields.io URLs (no emoji per project no-emoji invariant; pre-
  commit catches U+1F000-0x1FAFF + U+2600-0x27BF). Documentation
  badge is the user's primary ask (live-site visibility above-
  the-fold); other 8 are standard repo signals.

- **`RESULTS.md`** (new; ~250 lines) — third entry artifact in the
  reading-guide architecture per ADR-054. Sections:
  - **§1 5-rung × 5-slice AUPRC grid** with N/A markers in
    single-class cells (bipia, injecagent, notinject) per
    ADR-050. Each N/A cell points at the raw prediction
    parquet. Above-grid "How to read this grid" callout
    explaining prevalence-baseline convention.
  - **§2 5×5 AUROC grid** (secondary diagnostic per ADR-006 +
    eval-design.md §5.1).
  - **§3 5×5 recall@FPR1% grid** (operational policy slice;
    means across 4 folds × 3 seeds per ADR-025 + threshold-
    policy.md §7).
  - **§4 7 embedded Phase 4 figures** (F1-F7 from `docs/plots/`;
    Pareto + ROC overlay + PR per rung + reliability triptych +
    per-slice heatmap + LODO breakdown + dual-policy grid).
    Provenance: commit 948c50a (v1.0.1; post Item-4 single-class
    filter; fresh).
  - **§5 Raw-data access** — direct GitHub blob URLs at
    `tree/v1.0.5/evals/...` for every artifact (results.json +
    per_cell + marginal_cells + paired_cells + paired_cells_seed2 +
    cross_fold_ci_audit + mde_per_cell + verification_reachability +
    dual_policy + 282-file predictions/ tree + predictions_val/ +
    data_audit + dedup_calibration + leakage_report +
    contamination_scan + cost_ledger). Single-class slice
    predictions accessible despite N/A in §1-§3.
  - **§6 Reproducibility** — T0/T1/T3 tier mirror.

- **`decisions/ADR-054-results-page-as-third-entry-artifact-extending-adr-053.md`**
  (new; ~320 lines) — narrow supersession of ADR-053 dimension 1
  only ("two entry artifacts" → "three entry artifacts"); dimensions
  2-5 (3-path canonical order + Headline-finding-block requirement
  + interpretation pedagogy + pointer convention) carry forward
  unchanged. RESULTS role = data-disclosure / artifact-discovery
  (distinct from EXECUTIVE_SUMMARY = thesis-distillation and
  index.qmd = reviewer-orientation). Frontmatter
  `supersedes: [ADR-053]`; `related: [ADR-050, ADR-046, ADR-029,
  ADR-032]`.

### Changed

- **`_quarto.yml`** — `RESULTS.md` added to `project.render`
  allowlist; sidebar "Reading guide" section gains RESULTS as the
  third entry (after EXECUTIVE_SUMMARY + index.qmd); navbar gains
  a "Results" link between "Reading guide" and "Methodology (TOC)"
  for top-level discoverability.

- **Cross-reference pointers added** — `index.qmd` Results
  section + `EXECUTIVE_SUMMARY.md` reading-path step 4 +
  `WRITEUP.md §Results` source-data paragraph all gain pointers
  to `RESULTS.md` as the canonical artifact-disclosure page.
  index.qmd specifically: replaces the "see WRITEUP §Results +
  WRITEUP/eval-design.md" pointer (under the 3-row trio table)
  with a RESULTS-first pointer.

- **`decisions/ADR-053-*.md` frontmatter** — `superseded_by:`
  field updated from `[]` to `["054"]` with inline note
  "narrow supersession of dimension 1 (two-entry-artifacts) only;
  dimensions 2-5 unchanged. ADR-054 adds RESULTS.md as third
  entry artifact." Body unchanged (per ADR-029 immutability;
  frontmatter field updates for supersession tracking are the
  established exception — ADR-050 had `superseded_by: [ADR-052]`
  added at v1.0.3 under the same pattern).

- **`README.md` governance trail line** — `53 ADRs` → `54 ADRs`;
  inline note adds ADR-054 narrow supersession of ADR-053
  dimension 1.

- **`SUBMISSION_AUDIT.md`** — regenerated via
  `scripts/regenerate_audit.py`. Now 54 CLAIM rows; CLAIM-054
  added.

### Governance notes

- **In-place ADR-053 frontmatter edit** documented under the
  established convention (ADR-050 + ADR-053 both edited under
  this pattern when narrowly superseded). Decision text /
  body unchanged; only `superseded_by` field updated to track
  the supersession trail. Pre-commit hooks (gitleaks, no-emoji,
  SUBMISSION_AUDIT-in-sync) verify the edit doesn't introduce
  secrets, emoji, or audit drift.

- **No methodology change.** ADR-054 governs reader-facing
  artifact-discovery, not metrics or methodology. The
  `evals/` parquets are unchanged at v1.0.5 (no re-running
  of inference); only their disclosure surface gained a
  rendered page.

### Files modified (10 file touches)

- `README.md` (badges + governance-trail count update).
- `RESULTS.md` (new; ~250 lines).
- `index.qmd` (cross-reference pointer added).
- `EXECUTIVE_SUMMARY.md` (reading-path step 4 added pointing at
  RESULTS).
- `WRITEUP.md` §Results (cross-reference paragraph added).
- `decisions/ADR-054-*.md` (new; ~320 lines).
- `decisions/ADR-053-*.md` (in-place frontmatter `superseded_by`
  edit only).
- `_quarto.yml` (render allowlist + sidebar + navbar).
- `SUBMISSION_AUDIT.md` (regenerated; 54 rows).
- `CHANGELOG.md` (this entry).

---

## [1.0.4] — 2026-05-18

Reading-guide refresh + repo-wide stale-content sweep + ADR-053
reading-guide governance. Driver: user question *"does the reading
guide clearly say what the final results were? is it organized in
a way that makes sense to someone coming to the project. Does it
conform to our initial guidance and/or does our ADRs need to be
enriched?"* — answered NO + YES (ADR enrichment needed). v1.0.4
fixes the staleness across 9 files + lands ADR-053 in a single
atomic patch. Reviewer URL stays pinned at `tree/v1.0.0`; live
Quarto site reflects this patch.

### Added

- **`decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md`** —
  new ADR governing the reading-guide architecture in 5
  dimensions: (1) two entry artifacts (EXECUTIVE_SUMMARY +
  index.qmd) with distinct roles; (2) 3-path canonical reading
  order (A1 Quick-skim / A2 Audit / A3 Reproduce); (3) Headline-
  finding-block-on-index requirement (numbers stated up-front,
  not buried behind WRITEUP pointers); (4) interpretation-
  pedagogy requirement on index.qmd (5 patterns:
  prevalence-baseline, cross-family-OOD, negative-LoRA-delta,
  ProtectAI non-monotone, val→LODO threshold transfer); (5)
  pointer convention (index.qmd → EXECUTIVE_SUMMARY → WRITEUP →
  spokes → ADRs). Retroactively anchors EXECUTIVE_SUMMARY.md
  (added v1.0.3 per NEXT_STEPS §1.7 alone — no prior ADR
  coverage). `supersedes: []` (additive enrichment); `related:
  [ADR-030, ADR-033]`. NEXT_STEPS §1.7 gains a backref to
  ADR-053.

- **`index.qmd` Results section** — verified pooled_ood AUPRC
  trio sourced from `evals/bootstrap/marginal_cells.parquet`
  (BCa CI, 10000 resamples; 12 cells per rung = 4 folds × 3
  seeds × 1101 rows): ModernBERT frozen-probe 0.364 [0.354,
  0.375]; LoRA 0.293 [0.286, 0.301]; TF-IDF+LR 0.291 [0.283,
  0.298]; ProtectAI v1 0.361 [0.330, 0.391]; v2 0.314 [0.283,
  0.345]. Plus prevalence baseline (0.3742 = 412 positives /
  1101 rows).

- **`index.qmd` "How to read these numbers" section** — 5
  interpretation patterns walking the reviewer through
  prevalence baseline vs chance, cross-family vs cross-source
  OOD, negative LoRA delta meaning, ProtectAI v1→v2 non-monotone,
  val→LODO threshold transfer.

- **`index.qmd` "Headline ADRs to read"** sub-list in the A2
  Audit path — curated 11-ADR list (ADR-005, 015, 016, 017, 018,
  022, 046, 050, 051, 052, 053) so audit-path readers don't
  face the full 53-ADR ledger.

### Changed

- **`index.qmd`** — full rewrite per the ADR-053 conventions.
  Status section anchored in v1.0.4 reality ("Phase 5 closed at
  v1.0.0; reading-guide architecture anchored at v1.0.4"; 53
  ADRs); previously read as Phase-0-time scaffolding ("At Phase
  0-07 close, the spokes are skeletons; Phase 5 populates them").
  EXECUTIVE_SUMMARY promoted as A1 Quick-skim step 1. HF Hub
  model-card URLs added as a 4th submission anchor.

- **Repo-wide stale-content sweep** — 23 stale items across 9
  files corrected:

  **URL slug** (`prompt-injection-detection-submission` →
  `…-prototype`; 9 hits across 4 files):
  - `index.qmd` lines 70-72 (3 submission-anchor URLs).
  - `decisions/ADR-030-deliverable-format-quarto-html-site.md`
    lines 62 + 68 (source-pin + release-page URLs). **In-place
    edit** — treated as typo-class factual correction (slug
    rename); the canonical-source-pin + 3-URL reviewer set
    decision is unchanged. Per [ADR-029](decisions/ADR-029-immutable-adrs-supersede-dont-edit.md)
    immutability convention, a typo-class slug rename in a URL
    component is not a decision change.
  - `decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md`
    (3 hits in claim text + governance table cells). Same
    in-place rationale.
  - `assumptions.md:30` A-010 fallback branch name
    `submission-site` → `prototype-site`.

  **ADR counts** (4 hits; actual at v1.0.4 = 53 incl. ADR-053):
  - `README.md:26` `50 ADRs` → `53 ADRs`.
  - `SPEC_SHEET.md:3` + `:481` `50 ADRs accepted` → `53 ADRs
    accepted across Phase 0-00 through v1.0.4 close (ADR-050 +
    ADR-051 + ADR-052 + ADR-053)`.
  - `CLAUDE.md:9` (project root) `~50 decisions` → `~53
    decisions`.

  **Rung-slate framing in `SPEC_SHEET.md:18` headline** (2 hits;
  line 261's `[LOCKED:…]` had post-ADR-050 R1 narrowing; the
  line-18 headline paragraph was missed at v1.0.0 Item 7):
  - `4 reference rungs … gpt-4o + claude-sonnet + ProtectAI v1
    + v2` → `2 reference rungs … ProtectAI v1 + v2 per ADR-018
    (superseded by ADR-050 R1; LLM judges dropped Phase 4 on
    cost)`.
  - `8-rung slate … LLM judges vendor_black_box` → `5-rung OOD
    slate (2 trained + 2 reference + 1 classical) + 4-rung LODO
    ladder … (vendor_black_box tier empty per ADR-050 R1; 3-tier
    gradient compressed from the original 4)`.

  **Makefile-target / rung-name references** (3 hits across 2
  files; canonical per ADR-027 + ADR-050):
  - `index.qmd:45` `RUNG=modernbert-lora` → `RUNG=frozen-probe`
    + `RUNG=lora`.
  - `index.qmd:46` `make smoke` → `make test-smoke`.
  - `SUBMISSION_TEMPLATE.md:43` `make diagnostics-smoke` →
    `make test-smoke`.

  **`index.qmd` other staleness** (5 hits):
  - Line 21 `pooled IID + pooled OOD numbers per rung` (silent
    on actual finding) → new Results table + 5 interpretation
    patterns.
  - Line 35 `34+ ADRs` → `53 ADRs` + curated Headline ADRs list.
  - Line 61 repo-map row `results/` → `evals/`.
  - Lines 78-80 Phase-0-time Status section → v1.0.4 reality.
  - EXECUTIVE_SUMMARY.md promoted to A1 Quick-skim step 1.

- **`SUBMISSION_AUDIT.md`** regenerated via
  `scripts/regenerate_audit.py` — adds the CLAIM-053 row;
  total 53 claim rows.

### Governance notes

- ADR-030 + ADR-033 received in-place URL edits per
  /exploring-options batch 2 Q1.1 lock (2026-05-18). Both
  ADRs' decision text is unchanged; only the repo-identity slug
  component of the URLs updated to match the v1.0.0 repo rename
  from `prompt-injection-detection-submission` to
  `prompt-injection-detection-prototype`. Treated as
  typo-class factual correction (not a decision change). The
  immutability convention (per ADR-029 / CLAUDE.md
  anti-patterns) targets decision changes; a URL-slug typo
  fix to match a repo rename is not in scope. Decision audit
  trail: git history of `decisions/ADR-030-*.md` + `ADR-033-*.md`
  shows the edit + this CHANGELOG entry documents the rationale.

### Files modified

- `index.qmd` (full rewrite; ~180 lines).
- `README.md` (1-line ADR count).
- `SPEC_SHEET.md` (3 edits: lines 3 + 18 + 481).
- `assumptions.md` (1-line A-010 fallback branch).
- `SUBMISSION_TEMPLATE.md` (1-line make target).
- `CLAUDE.md` project root (1-line decision count).
- `decisions/ADR-030-*.md` (2 in-place URL edits).
- `decisions/ADR-033-*.md` (3 in-place URL edits).
- `decisions/ADR-053-…-reading-guide-governance-and-newcomer-paths.md` (new ~280 lines).
- `NEXT_STEPS.md` (§1.7 backref to ADR-053).
- `SUBMISSION_AUDIT.md` (regenerated).
- `CHANGELOG.md` (this entry).

---

## [1.0.3] — 2026-05-18

Narrative-import + housekeeping patch. Reframes the full-FT OOD
drop as methodological judgment + operational trigger (ADR-052
narrow supersession of ADR-050 R2); imports the cover-letter
draft's load-bearing phrasings into README + WRITEUP; adds the
1-page EXECUTIVE_SUMMARY public artifact + the SUBMISSION.md
cover-letter (gitignored); files 3 long-standing upstream
eval-toolkit issues with real URLs. Reviewer URL stays pinned at
`tree/v1.0.0`; live Quarto site reflects this patch.

### Added

- **`decisions/ADR-052-...md`** — narrow supersession of
  ADR-050 Revision 2 (FUSE-crash-only framing of full-FT OOD
  drop). New framing: **methodological reasoning was
  load-bearing** (LoRA's -0.071 AUPRC vs frozen-probe on
  `pooled_ood` already showed fine-tuning on the LODO direct-
  injection pool was actively HURTING OOD generalization;
  expected marginal benefit of full-FT-OOD over LoRA-OOD on the
  same pool was low; cost + risk did not justify the re-fire).
  FUSE EIO crash retained as operational trigger that exposed
  the decision. Retrospective self-awareness on full-FT LODO
  investment + a v1.1.x landing condition (larger pool +
  augmentation strategy needed before revisiting). ADR-050
  Revision 1 (LLM-judge cost drop) unchanged.
- **`EXECUTIVE_SUMMARY.md`** — 1-page decision-maker-facing
  layer above the full WRITEUP per NEXT_STEPS §1.7. Thesis + 4
  headline claims + what-was-characterised + what-is-deferred +
  reading-path pointer + honest reading. Third-person register;
  no apology / personal voice (those live in SUBMISSION.md).
- **`SUBMISSION.md`** (gitignored per `.gitignore:35`) — polished
  cover letter using the user's draft language verbatim where
  applicable; first-person voice + family-emergency context
  preserved. 3 factual fixes applied (DeBERTa sentence dropped;
  full-FT framing aligned to ADR-052; URLs verified to resolve).
- **NEXT_STEPS §1.10** — DeBERTa-v3-base long-context ablation
  entry (v1.1.x scope): controlled truncation handling for a
  defensible cross-architecture comparison on BIPIA-style
  indirect injection.
- 3 upstream eval-toolkit issues filed with real URLs and
  ledger rows updated:
  [#39](https://github.com/brandon-behring/eval-toolkit/issues/39) `is_metric_defined_for_slice` primitive,
  [#40](https://github.com/brandon-behring/eval-toolkit/issues/40) `LeakageCheck` Protocol `name` read-only relaxation,
  [#41](https://github.com/brandon-behring/eval-toolkit/issues/41) `parallel_map` worker-copy memory documentation +
  shared-state pattern.

### Changed

- **`README.md` — thesis-first opening + library-first
  ecosystem block.** Eval-fairness thesis (first-person; user's
  draft voice) promoted ABOVE the 3 status callouts. The 3
  companion OSS repos (eval-toolkit / runpod-deploy /
  research_toolkit) get substantive one-line descriptors
  replacing the previous parenthetical placeholders. SDD +
  immutable Michael-Nygard ADR convention named in the opening
  paragraph. §Headline characterisation lead re-anchored to the
  cross-family OOD framing (training pool is 4 direct-injection
  sources; OOD slate probes 4 attack families absent from
  training).
- **`WRITEUP.md` §1 Motivation** — first-person thesis
  blockquote added above the existing motivation prose. §1.5
  Attack-type taxonomy gains a "Note on what 'OOD' means here"
  callout under the train/test composition table — explicitly
  contrasts "in-domain test is still direct-injection, just an
  unseen source" with "the 5-slice OOD slate probes different
  attack FAMILIES". §Results headline lead rewritten with
  "The negative result IS the result" framing tied to the
  cross-family contrast.
- **`WRITEUP/limitations-and-future-work.md` §8.1** — full-FT
  bullet rewritten to ADR-052 framing (methodological reasoning
  load-bearing; FUSE crash as operational trigger;
  retrospective self-awareness on full-FT LODO investment).
  §9.2 full-FT entry similarly updated.
- **`WRITEUP/model-rungs.md` §4.3 Note on full-FT** — reframed
  to ADR-052 language; methodological reasoning load-bearing.
- **`_quarto.yml`** — `EXECUTIVE_SUMMARY.md` added to
  `project.render` allowlist + sidebar "Reading guide" section
  (above index.qmd) + new navbar entry.
- **`decisions/ADR-050-...md`** frontmatter:
  `superseded_by: [ADR-052]` (narrow — Revision 2 axis only;
  Revision 1 LLM-judge drop axis unchanged).
- `SUBMISSION_AUDIT.md` regenerated via
  `scripts/regenerate_audit.py`.

### Decisions

- 52 ADRs accepted across Phase 0-00 through v1.0.3 close.
- Reviewer URL pin stays at `tree/v1.0.0`; live Quarto site at
  `brandon-behring.github.io/prompt-injection-detection-prototype/`
  reflects v1.0.3 (and all subsequent v1.0.x patches).

## [1.0.2] — 2026-05-18

Governance patch — closes the two `REPO_AUDIT_2026-05-18` findings
that v1.0.0 + v1.0.1 documented as carryforwards but did not formally
supersede via ADR. Zero code changes; ADR + ledger update only.
Reviewer URL stays pinned at `tree/v1.0.0`; live Quarto site reflects
this patch.

### Added

- **`decisions/ADR-051-v1.0.x-carryforward-of-t0-and-invariant-scaffolds.md`** —
  narrow supersession of ADR-034 (T0 score-match wiring axis only;
  T1 + T3 tiers unchanged) and ADR-039 (gate 3 invariant-scaffold
  unskip axis only; gates 1+2+4+5+6 unchanged). Explicit v1.1.x
  landing conditions for both blocks. Per the audit's explicit
  invitation: *"Either finish this path or write a superseding ADR
  that explicitly waives it for submission"*; this ADR is the
  supersession path closure.

### Changed

- **`decisions/ADR-034-reproducibility-tier-full-ladder.md`** —
  frontmatter gains `superseded_by: [ADR-051]`.
- **`decisions/ADR-039-acceptance-criteria-six-gate-integration-checklist.md`** —
  same.
- **`SUBMISSION_AUDIT.md`** regenerated via
  `scripts/regenerate_audit.py` to reflect ADR-051 + the two narrow
  supersessions.

### Decisions

- 51 ADRs accepted across Phase 0-00 through v1.0.2 close.
- Reviewer URL pin stays at `tree/v1.0.0`; live Quarto site at
  `brandon-behring.github.io/prompt-injection-detection-prototype/`
  reflects v1.0.2 (and all subsequent v1.0.x patches).

## [1.0.1] — 2026-05-18

Post-submission polish patch (per ADR-033 v1.0.x patch convention).
Reviewer URL stays pinned at `tree/v1.0.0`; live Quarto site reflects
this patch.

### Added

- **HF Hub published**: canonical fold0/seed42 checkpoints for both
  rungs are now live —
  [`BBehring/prompt-injection-frozen-probe`](https://huggingface.co/BBehring/prompt-injection-frozen-probe)
  + [`BBehring/prompt-injection-lora`](https://huggingface.co/BBehring/prompt-injection-lora).
  Models published via `make publish-hub` using `HF_TOKEN_WRITE`
  from `.env.local` (write-scope token; v1.0.0 was blocked on this
  rotation). Both repos return HTTP 200; auto-generated model cards
  follow the expansive ADR-032 schema (YAML frontmatter + datasets
  pinned per ADR-016 + `model-index.results` per-slice metrics +
  intended use + limitations + ADR-005 contamination tier +
  citation + reproducibility commands).
- **README "Reading paths" subsection** with 3 navigable paths
  (Quick-skim / Audit / Reproduce) — all links resolve to the
  live Quarto site so a reviewer landing on GitHub clicks into a
  rendered page rather than a raw .md.
- **README live-site link** in the Status callout block —
  prominent above-the-fold link to
  `brandon-behring.github.io/prompt-injection-detection-prototype/`
  + the two HF Hub model-card URLs.

### Changed

- **AUPRC standardisation across WRITEUP + spokes** (was: AUROC
  headline; methodologically inconsistent with eval-design.md
  §5.1's PR-AUC preference). WRITEUP §Results headline rung-grid +
  §Results lift-vs-floor table + §Results headline claims +
  §Takeaways now lead with AUPRC; AUROC retained as a secondary
  cross-paper-comparable diagnostic. WRITEUP/model-rungs.md
  per-rung "Result:" blurbs rewritten the same way. Pooled_ood
  positive-class prevalence (0.374) computed + surfaced as the
  random-predictor AUPRC baseline; the honest finding tightens:
  even frozen-probe's `pooled_ood` AUPRC (0.364) lands ~0.01
  *below* the prevalence baseline.
- **`_quarto.yml` render allowlist expanded** to include
  `SPEC_SHEET.md`, `SUBMISSION_AUDIT.md`, `NEXT_STEPS.md`,
  `assumptions.md`, `decisions/upstream_issues.md`. These were
  previously auto-copied as raw `.md` into `_site/`; reviewer
  click resulted in raw markdown download. Now rendered as HTML;
  new "Reference" sidebar section between Evidence + Decisions
  surfaces them in the nav.
- **`scripts/publish_to_hub.py`** prefers `HF_TOKEN_WRITE` then
  `HF_TOKEN` from environment, falling back to the cached token —
  resolves the v1.0.0 publish-blocked auth path without disturbing
  the read-only token convention.
- **`WRITEUP/reproducibility.md`**: T0 "Status" block updated to
  reflect actual publication state at v1.0.1 + maintainer note on
  the still-stubbed `eval_from_hub.py` non-dry-run body (T0
  score-match wiring lands at v1.1.x). T3 vestigial "skeleton"
  label replaced with "complete" + RunPod-bootstrap pointer. Added
  the missing "Cross-references" block (now consistent with the
  other 7 spokes).
- **Hyphenation typo fix** in README L7 (`frozen probe →` →
  `frozen-probe →`) — single-occurrence drift from project naming
  convention.

### Closing

Audit-driven patch (3 parallel Explore agents at v1.0.0 close
surfaced these polish items). All gates green; live Quarto site
+ HF Hub repos resolve.

## [1.0.0] — 2026-05-18

Submission tag. Closes the `REPO_AUDIT_2026-05-18` 8-item remediation
queue with 12 commits + 2 rehearsal tags + green CI/Publish on the
v1.0.0 head. Per ADR-033, this is the reviewer URL pin
(`tree/v1.0.0`); post-submission patches land as `v1.0.1`+ and the
live Quarto site reflects the latest patch.

### Added

- `WRITEUP/` 7-spoke split (per Item 2 Q5 lock): data-decisions,
  model-rungs, eval-design, threshold-policy, reference-scorer-audit,
  methodology-guarantees, limitations-and-future-work; +
  `reproducibility.md` (T0 published-rung script-matched commands).
  Monolithic `WRITEUP.md` becomes a TOC/landing page with the §Results
  headline narrative.
- `EVIDENCE.md` full 5-section fill: ProtectAI v1/v2 contamination
  audit + `tfidf-lr` `verified_disjoint` anchor + style-confound +
  threshold-methodology + replication-invariants + sources.
- `docs/HYPERPARAMETER_DISCLOSURE.md` full 4-section fill: locked
  recipe (with per-rung knob tables from `configs/rungs/*.yaml`) +
  exploration-trajectory + axes-held-constant + caveats.
- `NEXT_STEPS.md` §3: 3 genuine Phase 0-5-surfaced open questions
  replacing template slots.
- `src/eval/slice_analysis.py`: `SINGLE_CLASS_SLICES` +
  `SINGLE_CLASS_INCOMPATIBLE_METRICS` + `is_metric_defined_for_slice()`.
  Filter applied at source in `src/eval/marginal_bootstrap.py` +
  `scripts/run_cv_clt_ci.py` so AUROC/AUPRC degenerate values
  (1.0/0.0) never land in artifacts (Item 4 Q9 lock).
- `scripts/build_results_json.py` + `scripts/generate_model_cards.py`
  + `scripts/publish_to_hub.py` + `evals/results.json` + `make
  publish-hub` (Item 5; per Q11 expansive ADR-032 schema; Q10 canonical
  fold0/seed42 per rung only). HF Hub publication outstanding pending
  write-scope token rotation.
- `make build-results-json` + `make generate-model-cards` +
  `make publish-hub` + `make publish-hub-dry-run` Makefile targets.
- `_quarto.yml` explicit `project.render:` allowlist scoping the
  site to README + CHANGELOG + WRITEUP + WRITEUP/* + EVIDENCE + ADRs
  (excludes transcripts/, data/raw/git/**, evals/, src/, scripts/,
  tests/, other docs/).
- Phase 5 closure ADRs: `ADR-049` (GPU-order priority refresh —
  A100-80G first; full-FT post-rehearsal); `ADR-050` (rung-slate
  narrowing — LLM judges dropped on cost re-estimation; full-FT OOD
  dropped on FUSE EIO crash); narrow supersession of ADR-018 +
  ADR-021. `closing_commit` populated on both.
- `gh-pages` orphan branch on origin (one-time bootstrap so
  `quarto-actions/publish@v2` works).

### Changed

- `WRITEUP.md` becomes a TOC/landing page; §1 Motivation + §2
  Approach + §Results (extracted §7 headline) + §Lessons brief +
  §12 Appendix. All 4 leftover `[OPEN: ...]` tokens resolved with
  declarative ADR-linked content.
- `SPEC_SHEET.md` rung-language aligned to ADR-050 narrowing —
  reference slate compresses from 4-rung (2 LLM judges + ProtectAI v1
  + v2) to 2-rung (ProtectAI v1 + v2). `vendor_black_box`
  contamination tier carries **0 rungs** in this submission;
  stratification gradient compresses from 4 tiers to 3. LODO 3-rung
  trained ladder retained; OOD comparison drops to 5-rung slate.
  Phase 0-4 checkboxes flipped [ ] → [x]; Phase 5 boxes ship checked
  at v1.0.0.
- `docs/HYPERPARAMETER_DISCLOSURE.md` + `docs/REPRODUCIBILITY.md` +
  `docs/THREAT_MODEL.md` placeholders fully resolved. `docs/REPRO`
  Python pin >=3.10 → >=3.13; stale `make diagnostics-smoke` /
  `make canonical-eval` → actual current Makefile targets.
- `README.md` headline-characterisation: curated 4-row punch table
  (Q3 lock) with frozen-probe/LoRA/ProtectAI-v2/tfidf-lr on
  `pooled_ood` AUPRC + 95% CI; LoRA's -0.071 AUPRC underperformance
  surfaced as the honest finding.
- `.github/workflows/ci.yml` Python pin 3.11 → 3.13 (matches
  pyproject.toml + .python-version; Item 3).
- `.github/workflows/publish.yml` env block adds HF_TOKEN +
  RUNPOD_API_KEY + OPENAI_API_KEY stubs to satisfy Quarto's dotenv
  loader (no real secrets at render time per Item 2 Q7 lock).
- `.pre-commit-config.yaml` ruff pin v0.4.0 → v0.15.13 (matches
  uv-locked ruff used by CI's `ruff format --check`; resolves the
  stash-restore loop that bit the Item 8 fix-forward).
- `Makefile` `site` + `site-preview` targets export stub env vars
  so `make site` renders without real secrets.
- `src/eval/figures.py`: explicit `cast(Figure, ...)` for upstream
  `plot_pareto_frontier` + `plot_slice_metric_heatmap` (both return
  `Any` typed); mypy strict clean.
- `src/data/audit.py:222`: explicit `cast(LeakageCheck, ...)` for
  `CrossSplitLeakageCheck` (upstream frozen-dataclass / Protocol
  settable-name mismatch).
- `tests/test_invariants.py`: docstring rewritten with v1.0.0
  honest accounting per ADR-039 gate 3 (10 invariants implemented;
  38 stubs carry forward to v1.1.x; 30 skip reasons made explicit).
  Data-gated invariants (`test_class_balance_per_fold` +
  `test_source_disjoint_train_test`) use `pytest.skip()` when
  canonical-run artifacts are absent (CI runs without data).
- `evals/bootstrap/marginal_cells.parquet`: 66 → 60 rows
  (bipia/injecagent × auprc removed by Item 4 source filter).
- `evals/audit/cross_fold_ci_audit.parquet`: 31 → 22 rows (all 3
  single-class slices × auroc/auprc removed).
- `evals/audit/mde_per_cell.parquet`: 142 → 136 rows.
- Repo-identity rewrites: `prompt-injection-detection-submission` →
  `prompt-injection-detection-prototype` in `assumptions.md` +
  `SPEC_SHEET.md` (GH Pages URL + reviewer URL pinpoints).

### Decisions

- 50 ADRs accepted across Phase 0-00 through Phase 5 close at
  ADR-050. `SUBMISSION_AUDIT.md` regenerates from frontmatter
  via `scripts/regenerate_audit.py` (CI hard gate per ADR-039).
- Reviewer URL stays pinned at `tree/v1.0.0`; live Quarto site at
  `brandon-behring.github.io/prompt-injection-detection-prototype/`
  reflects the latest patch.

## [0.9.0-rc3] — 2026-05-18

Third rehearsal — `a2fc4d9`. CI + Publish workflows green; reviewer
URLs return 200. Same content as v1.0.0; the rc3 tag is preserved
as the rehearsal-pass landmark per ADR-033 fix-forward discipline.

## [0.9.0-rc2] — 2026-05-18

Second rehearsal — `d66e3d0`. CI red on the lint hard gate (3
remaining ruff-format diffs from a pre-commit stash-restore loop) +
one data-gated invariant; Publish workflow needed an orphan `gh-pages`
branch on origin. Fix-forwarded via `0bedc80` (data-gated skipif) +
`a2fc4d9` (ruff-pre-commit v0.4.0 → v0.15.13 + format leftover).

## [0.9.0-rc1] — 2026-05-17

First rehearsal tag (per ADR-033). Catches first-time-CI / auth /
schema issues before the canonical submission. Resulted in the
`REPO_AUDIT_2026-05-18.md` 8-item remediation queue.

## [0.0.0] — 2026-05-15

### Added

- Initial public seed: SDD spec-sheet kit + literature dossier + Phase 0 infrastructure
- Kit-level discipline encoded directly in `SPEC_GREENFIELD.md` spec text + decision ledger
- Constitution split into 3 files: `docs/MISSION.md`, `docs/TECH_STACK.md`, `docs/ROADMAP.md`
- 50-row decision ledger in `SPEC_GREENFIELD.md` with reference-anchors column
- Three load-bearing libraries declared: `eval-toolkit`, `runpod-deploy`, `research_toolkit`
- Anti-hand-rolling rule + upstream-issue triage protocol locked in `docs/TECH_STACK.md`
- Tests-as-invariants stubs at `tests/test_invariants.py` (7 skip-marked)
- CI scaffolding (`Makefile`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`) with hard / soft / opt-in gate split
- Phase 0 infrastructure: `CLAUDE.md`, `AGENTS.md`, `/save-transcript` skill, `decisions/ADR_TEMPLATE.md`
- Literature dossier (16 verified files) under `docs/research/` with `MANIFEST.json` (produced via `research_toolkit` pipeline)
- `scripts/regenerate_audit.py` for ADR-as-source-of-truth audit register
- `SPEC_STRATEGY.md` (classification meta-doc), `docs/THREAT_MODEL.md`, `docs/REPRODUCIBILITY.md`, `docs/HYPERPARAMETER_DISCLOSURE.md`, `docs/GLOSSARY.md` (living)
- `docs/MANIFEST_SCHEMA.md` (eval-output schema)
- Cover-letter two-version split: `SUBMISSION_TEMPLATE.md` (committed) + `SUBMISSION.md` (gitignored, emailed separately)
- Transcripts private by default (`transcripts/*.md` gitignored; emailed separately at submission time)
- `uv.lock` committed for byte-reproducible installs
- Notebook scaffolding (jupytext + nbstripout); notebooks themselves are Phase 2+ work

### Decisions

- Phase 0 not yet started; `SPEC_GREENFIELD.md` ledger has 50 `[OPEN]` rows pending
- See `SPEC_STRATEGY.md` for the classification + alternatives-rejected rationale
- v0.0.0 is the public seed; v0.1.0 lands when Phase 0 closes
