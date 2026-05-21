---
adr_id: "064"
slug: writeup-hiring-manager-clarity-and-consistency-pass
title: Writeup hiring-manager clarity polish + documentation-wide consistency conventions — additive layer on top of ADR-062
date: 2026-05-19
status: Accepted
claim_id: CLAIM-064
claim: >-
  Post-v1.1.3 user review (ADR-062 baseline) surfaced that the Quarto
  writeup needed a hiring-manager clarity pass: jargon density,
  plot-interpretation cues, and table-context framing were under-served.
  User expansion: ensure consistency across README and other
  documentation surfaces.
  [Verbatim wording redacted per ADR-074.]
  Three /exploring-options rounds locked: heavy/fresh pass (not light/
  medium); commit doc-agent ADR-062 work as v1.1.3 baseline; DeBERTa
  null-result lives as RESULTS §1B callout (NOT a new F6 figure);
  hiring-manager landing = new standalone page; spoke density = light
  signpost + Result-bolding; figure refinements = prose + SVG axis-label
  fixes; sub-commits = logical (6 commits); full-repo audit + 3-stage
  release shape (v1.1.3 baseline + v1.1.4 consistency-only + v1.2.0
  heavy pass); ADR-063 fact-correction via CHANGELOG postscript + this
  ADR §D narrative flag (lightest ceremony respecting the project
  ADR-discipline per CLAUDE.md "ADRs are immutable; supersede via new
  ADR"); markdown-link-checker pre-commit prophylaxis (CI
  only; no local pre-commit hook to avoid contributor friction); no
  companion technical-reviewer landing page (READING_GUIDE.md already
  serves that role). The 3-audit findings + locked decisions produce a
  ~5.5-hour 6-commit heavy pass on top of ADR-062's structural
  rewrite. The pass adds reviewer-facing clarity polish (jargon
  glossing invariant + spoke skim signposts + table/plot context +
  DeBERTa §1B + figure caption + SVG axis-label refinements +
  hiring-manager landing) AND documentation-wide consistency invariants
  (canonical terminology table + project-ADR-discipline-immutable broken-slug-ref +
  cumulative-cost-figure flag for 5 prior ADRs).
source: transcripts/2026-05-19__v1-2-0-writeup-clarity-and-consistency.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.2.0 close: `docs/for-hiring-managers.md` exists (~250 words;
  4-question format: problem / found / trust / candidate-thinking) and is
  reachable from the navbar Reference dropdown + the `index.qmd` "Read
  Next" section. The READING_GUIDE.md technical-reviewer path is named
  `#technical-reviewer-path` for anchor linkage from the hiring-manager
  page. `RESULTS.md` §1B between §1 Primary Table and §2 Paired Comparison
  carries the DeBERTa ablation per-strategy table + "what §1B says / does
  not say" pair + backbone-dominant interpretation; the
  `WRITEUP/limitations-and-future-work.md:161` link to RESULTS §1B
  resolves cleanly. The 5 reviewer-facing figures (F1-F5) have
  self-documenting axis labels + sublegends (regenerated via
  `make render-figures`); RESULTS.md figure captions match the audit
  gap fixes (F1 random-floor explanation; F2 axis + CIs-crossing-zero
  cue; F3 N/A explanation; F4 subpanel mapping; F5 ECE/Brier gloss).
  All 8 `WRITEUP/*.md` spokes carry a "How to read this spoke"
  blockquote + `**Result**` bold prefixes on existing summary
  sentences. `docs/GLOSSARY.md` carries the canonical-terminology
  table from §C below plus 3+ new entries (`confound`, `ablation`,
  `detector` clarifier note). `decisions/library_imports.md` carries
  the deferred-from-v1.1.2-Phase-B entry for
  `src/inference/windowed.py`. `NEXT_STEPS.md` §1.10 status reflects
  v1.2.0 landing. `CHANGELOG.md` [1.2.0] entry exists with the
  6-commit cadence narrative + ADR-064 cross-ref + corrected ADR
  slug refs. `SUBMISSION_AUDIT.md` regenerates clean with 64 CLAIM
  rows. CI markdown-link-checker (lychee; added at v1.1.4) passes on
  the v1.2.0 push.
closing_commit: v1.2.0
supersedes: []
superseded_by: []
references:
  - CLAUDE.md  # project ADR-discipline (immutability + supersession)
  - decisions/ADR-030-deliverable-format-quarto-html-site.md
  - decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md
  - decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md
  - decisions/ADR-061-quarto-site-navigation-restructure.md
  - decisions/ADR-062-quarto-writeup-clarity-and-canonical-figures.md
  - decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md
  - decisions/ADR-063-deberta-ablation-v1-1-2-execution-and-slot-shift.md
  - NEXT_STEPS.md  # §1.10 Status (v1.2.0)
  - CHANGELOG.md  # [1.2.0]
  - docs/for-hiring-managers.md
  - docs/GLOSSARY.md
  - evals/cost_ledger.csv  # canonical cumulative-cost source-of-truth
transcript: transcripts/2026-05-19__v1-2-0-writeup-clarity-and-consistency.md
---

# ADR-064 — Writeup hiring-manager clarity polish + documentation-wide consistency conventions

## Status

Accepted (2026-05-19; additive layer on top of ADR-062 — no
supersession of ADR-062's decisions; this ADR adds a hiring-manager
clarity polish + documentation-wide consistency invariants).

## §A Context

[ADR-062](./ADR-062-quarto-writeup-clarity-and-canonical-figures.md)
shipped at v1.1.3 (the doc-agent baseline; commit `ca43512`) and
delivered the structural rewrite of the Quarto writeup —
problem-first `index.qmd` landing, one-page `EXECUTIVE_SUMMARY.md`,
Metric Primer in `RESULTS.md` §1, "what each figure says AND does
not say" caption discipline for F1-F5, expanded `docs/GLOSSARY.md`,
3 reader-type paths in `READING_GUIDE.md`, F1-F5 canonical reviewer
figure slate (F6-F7 removed).

Post-v1.1.3 user review (ADR-062 baseline) flagged that the Quarto
writeup needed a hiring-manager clarity pass: jargon density,
plot-interpretation cues, table-context framing under-served. Plus
a documentation-wide consistency review across README, RESULTS,
EXECUTIVE_SUMMARY, and reference docs.

*[Verbatim wording redacted per ADR-074.]*

Three parallel /exploring-options rounds (2026-05-19 — full transcript
above) surfaced + locked the v1.2.0 scope: heavy clarity polish
on top of ADR-062 + documentation-wide consistency invariants,
shipped in 6 logical sub-commits.

Three audits were run in parallel (writeup clarity audit; numerical +
factual consistency audit; cross-reference + link consistency audit)
to surface the specific gaps. Findings drove the precise edits.

## §B Decision — clarity polish layer (additive to ADR-062)

The v1.2.0 heavy pass layers the following on top of ADR-062's
structural rewrite. None of these decisions supersede ADR-062;
they extend it.

### B1 — Jargon-glossing invariant (gloss-on-first-use)

Every reviewer-facing markdown surface (`index.qmd`, `EXECUTIVE_SUMMARY.md`,
`WRITEUP.md`, `RESULTS.md`, `READING_GUIDE.md`, `README.md`,
`WRITEUP/*.md` spokes, `docs/GLOSSARY.md`, `docs/for-hiring-managers.md`)
satisfies the invariant: every project-specific acronym or jargon
term is either spelled out inline on first use OR linked to the
GLOSSARY entry on first use. The terms in scope (per the canonical
terminology table in §C): LODO, AUPRC, AUROC, BIPIA, InjecAgent,
JBB, XSTest, NotInject, FPR, ECE, Brier, rung, detector, confound,
ablation, calibration, OOD, IID, LoRA, frozen-probe, ModernBERT,
DeBERTa, full-FT, chunk-and-average, head-truncation, ProtectAI v1/v2.

Verification scan (manual or via grep invariant in commit-prep):
`grep -nE '\b(LODO|AUPRC|...)\b'` on each file; first occurrence
must be glossed.

### B2 — Table + plot pre-context + post-takeaway pattern

Every results table or figure embed in `RESULTS.md` / `index.qmd` /
`EXECUTIVE_SUMMARY.md` has:
- **Pre-context** (1-2 sentences): what the reader is about to look
  at; what good/bad/baseline values are; how to scan the table.
- **Post-takeaway** (1-3 sentences): the headline finding from the
  table.

Specific instances added at v1.2.0: `RESULTS.md` §1 AUPRC table
gets pre-context framing (Pooled OOD = most important test set;
0.374 = random baseline; CI width = confidence); `RESULTS.md` §7
Raw Artifacts gets hiring-manager-facing "you don't need these but
they're here for audit" framing; `RESULTS.md` opening gets a
1-sentence reading guide.

### B3 — DeBERTa null-result callout: RESULTS §1B between §1 and §2

The v1.1.2 DeBERTa-v3-base medium ablation (per ADR-060 methodology
+ ADR-063 execution) produced a publishable null result:
chunk_and_average and head_truncation truncation strategies produce
essentially identical per-slice metrics (pooled OOD AUPRC 0.2912 vs
0.2895; jbb_behaviors 0.4855 vs 0.4890; xstest 0.3966 vs 0.3912).
By the ADR-060 confound-control interpretation: the ModernBERT
advantage on the headline ladder is **backbone-dominant**, not
context-window-dominant.

This finding lives as a new section `## §1B Ablation: does a longer-
context backbone fix the OOD gap?` between RESULTS.md §1 (Primary
Table) and §2 (Paired Comparison). The section carries:
- Per-strategy headline table (2 strategies × 3 binary-class slices)
- "What §1B says / does not say" pair (per the ADR-062 caption
  discipline)
- Backbone-dominant interpretation paragraph
- Cross-refs to ADR-060 (methodology) + ADR-063 (execution) — using
  the CORRECT slug refs (audit-verified)

Placement rationale: most visible. Reader sees headline AUPRC ladder
(§1) → immediately asks "did a bigger backbone help?" → gets the
answer (§1B) → continues to Paired Comparison (§2). Demonstrates
clear thought by answering the natural follow-up question. Per
/exploring-options 2026-05-19 round 1 Q2: placement chosen over §6
(appendix-like) + §9.2-only (deeply buried).

**Critical**: §1B's `## §1B Ablation: ...` markdown heading must
produce the `#1b-ablation-...` anchor that
`WRITEUP/limitations-and-future-work.md:161` already links to. The
v1.1.3 baseline + audit surfaced this as a broken anchor; v1.2.0
Commit 3 resolves it by adding §1B.

### B4 — Figure caption refinements + SVG axis-label rebuild

F1-F5 figures are self-documenting in any context (not just within
the RESULTS.md prose), via `src/eval/figures.py` axis-label + sublegend
changes:
- F1: annotation block on random-floor derivation (0.374 = 412/1101)
- F2: xlabel `'LoRA AUPRC minus frozen-probe AUPRC (95% CI; whiskers
  crossing 0 = indistinguishable)'`
- F3: colorbar legend explicitly notes `'N/A = single-class slice;
  AUPRC undefined'`
- F4: subpanel suptitles map `'Left: FPR (1% validation target line);
  Right: Recall at fitted threshold'`
- F5: ylabel `'Error (lower better; ECE = expected calibration
  error, Brier = MSE of predicted vs actual)'`

RESULTS.md figure caption prose refinements supplement the SVG
self-documentation: per-figure caption gets explicit "what reader's
eye should look for" + "what figure does not show" cues (per the
audit gaps for F2 / F3 / F4 / F5).

Per /exploring-options 2026-05-19 round 1 Q4: SVG axis-label fixes
preferred over prose-only because figures are self-documenting in
ANY context (slide deck, social media, etc.). Re-render via
`make render-figures` (CPU-only, <2 min); SVG diff churn is acceptable.

### B5 — Spoke density: 1-paragraph signpost + Result bolding

All 8 `WRITEUP/*.md` spoke files satisfy:
1. A 3-4 line "How to read this spoke" blockquote below the existing
   1-line back-link (added at v1.1.1 per ADR-061), telling skimmers
   to focus on `**Result**` subsections + final §Summary.
2. `**Result**` bold prefix on existing summary sentences in each
   major subsection. NO existing prose is rewritten; just visibility
   tagging.

`WRITEUP/model-rungs.md` specifically gets `**Result**` bold on the
LoRA / frozen-probe / ProtectAI conclusion sentences (the dense
hyperparameter prose stays untouched).

Filename note: `WRITEUP/model-rungs.md` filename retains "rungs" (an
architectural artifact; rename risks ADR-050 anchor breakage). The
disclaimer paragraph already present (from v1.1.3 baseline)
documents the rung↔detector mapping. No rename.

Per /exploring-options 2026-05-19 round 1 Q3: light signpost +
Result-bolding chosen over Result-bolding-only (without signpost the
bolded sentences may not be recognized as the skim path) and over
medium split (TL;DR + Audit-detail; heavier rewrite; doubles up
content).

### B6 — Hiring-manager landing page: `docs/for-hiring-managers.md`

New standalone page, ~250 words, 4-question format:
1. **What problem does this project solve?** (1 paragraph)
2. **What did the candidate find?** (2 sentences: headline AUPRC
   gap + DeBERTa backbone-dominant interpretation)
3. **Why should I trust the finding?** (3 bullets: LODO + 95% CIs +
   honest single-class slice handling)
4. **What does this tell me about how the candidate thinks?** (3
   bullets: SDD + per-decision ADRs + ablation discipline)

Reachable from:
- Navbar Reference dropdown (new entry; `_quarto.yml` modification)
- `index.qmd` "Read Next" section ("For hiring managers in a hurry →")

Closing line on the page: "If you're a technical reviewer instead,
see [READING_GUIDE.md](../READING_GUIDE.md#technical-reviewer-path)
for the audit-depth path."

Per /exploring-options 2026-05-19 round 1 Q1: standalone page chosen
over EXECUTIVE_SUMMARY section (duplication risk) + index.qmd
in-place (would push index.qmd past the ADR-062 ~30-line slim target).

Per /exploring-options 2026-05-19 round 2 Q5: NO companion
`docs/for-technical-reviewers.md` page. READING_GUIDE.md already
covers the technical-reviewer path (per ADR-061 + ADR-062); adding
a parallel page would duplicate content and risk drift.

## §C Decision — documentation-wide consistency invariants

### C1 — Canonical terminology table

The project uses some terms with prose-vs-identifier splits (e.g.,
`chunk-and-average` prose / `chunk_and_average` code identifier).
Without a canonical convention, readers see inconsistent usage and
form negative judgment on the project's discipline. Per the audits:

| Term cluster | Prose form | Identifier form |
|---|---|---|
| Detector ladder | "detector" (reviewer-facing prose) | `frozen_probe` / `lora` / `full_ft` / `tfidf_lr` (code) |
| Truncation strategy | "chunk-and-average" / "head-truncation" (hyphenated) | `chunk_and_average` / `head_truncation` (snake_case) |
| Full fine-tune | "full-FT" (capitalized; matches "LoRA") | `full_ft` |
| Frozen probe | "frozen-probe" (hyphenated; matches triad with "LoRA" + "full-FT") | `frozen_probe` |
| ProtectAI v1/v2 | "ProtectAI v1", "ProtectAI v2" (space + version) | `protectai-v1`, `protectai-v2` |
| OOD | "out-of-distribution (OOD)" on first use; "OOD" thereafter | N/A |
| LODO | "leave-one-dataset-out (LODO)" on first use | N/A |
| Source/slice names | Display: "BIPIA", "InjecAgent", "JBB-Behaviors", "XSTest", "NotInject", "HackAPrompt", "LMSYS" | `bipia`, `injecagent`, `jbb_behaviors`, `xstest`, `notinject`, `hackaprompt`, `lmsys-chat-1m` |
| Metric names | "AUPRC", "AUROC", "ECE", "Brier" (all-caps acronyms) | Same |

Documented in `docs/GLOSSARY.md` (v1.2.0 Commit 1 adds the table)
so future contributors can resolve any prose-vs-identifier ambiguity
by consulting one canonical source.

Older ADRs (ADR-007 onwards) use "rung" for what reviewer-facing
prose calls "detector" — this is a deliberate prose-vs-decision-record
split; the GLOSSARY entry documents the bridge.

### C2 — Prophylaxis: markdown-link-check CI (lychee)

v1.1.4 introduced `.github/workflows/link-check.yml` (lycheeverse/
lychee-action@v2) running on push to main + PR + weekly schedule.
Catches broken-link drift at PR-time before merge. ADR-064 codifies
the CI link-checker as a permanent prophylactic invariant — future
patches that introduce broken markdown links will fail CI.

`.lycheeignore` documents the discipline: prefer fixing over
ignoring; only add an ignore when a URL is verified-good for humans
but 403s bots.

## §D Known errors in prior ADRs (flagged-not-fixed per project ADR-discipline)

The full-repo audit at v1.1.4 surfaced 9 broken ADR slug references
across 5 immutable ADR files. These cannot be edited per the project
ADR-discipline (CLAUDE.md: "ADRs are immutable; supersede via new
ADR"). Note: the project's older CHANGELOG entries cite "ADR-029" as
the immutability ADR, but the actual ADR-029 file is about test-marker
strategy; the immutability rule lives in CLAUDE.md / `decisions/README.md`.
That historical drift is itself a documentation-consistency issue not
in v1.2.0 scope; future patches may add a narrow "immutability ADR"
clarification.
Canonical-correct slugs documented here for readers who hit a 404
when clicking the in-ADR cross-refs:

**ADR-006 actual filename**:
`decisions/ADR-006-headline-metrics-and-statistical-apparatus.md`

Broken refs:
- `decisions/ADR-046-phase-4-analysis-implementation-bundle.md:15,195`
  cite as `ADR-006-headline-metrics-and-statistical-apparatus.md` (wrong slug)
- `decisions/ADR-048-llm-rater-reference-scorer-audit-protocol.md:16,194`
  cite as `ADR-006-headline-metrics-and-statistical-apparatus.md` (wrong slug)
- `decisions/ADR-063-deberta-ablation-v1-1-2-execution-and-slot-shift.md:60,268`
  cite as `ADR-006-headline-metrics-and-statistical-apparatus.md` (wrong slug)

**ADR-020 actual filename**:
`decisions/ADR-020-compute-infrastructure-and-cost-discipline.md`

Broken refs:
- `decisions/ADR-059-runpod-deploy-pypi-install-narrow-supersession-of-adr-036.md:47`
  cites as `ADR-020-compute-infrastructure-and-cost-discipline.md` (wrong slug)
- `decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md:64`
  cites as `ADR-020-compute-infrastructure-and-cost-discipline.md` (wrong slug)
- `decisions/ADR-063-deberta-ablation-v1-1-2-execution-and-slot-shift.md:62,274`
  cites as `ADR-020-compute-infrastructure-and-cost-discipline.md` (wrong slug)

**ADR-063 stale cumulative-cost figure**:

ADR-063 reads `Cumulative project spend: $9.92 / ADR-020 $200 hard
cap`. This figure was calculated from a subset of pod rows at the
time ADR-063 was authored. The canonical cumulative cost source-of-
truth is `evals/cost_ledger.csv` (sum the `actual_cost_usd` column
at any point in time). Future patches should consult the ledger
directly rather than re-quote ADR-063's figure.

The v1.1.2 DeBERTa execution GPU spend of `$1.34` (cited in NEXT_STEPS
§1.10 and CHANGELOG [1.1.2]) is correct and self-consistent.

CI markdown-link-checker (lychee; introduced at v1.1.4) prevents
recurrence of the slug-link class of errors in any future ADR or
markdown surface.

## §E Consequences

- **Reviewer experience**: a hiring manager landing fresh on the
  Quarto site can find `docs/for-hiring-managers.md` within 30
  seconds (navbar Reference dropdown OR `index.qmd` "Read Next"
  link) and answer the 4 hiring-manager questions in 60 seconds.
  Navigation to RESULTS shows §1B DeBERTa callout immediately
  after the primary table; F1-F5 figures are self-documenting in
  any extraction context.
- **No methodology drift**: ADR-064 changes only writeup prose +
  figure axis labels + SVG provenance. No methodology constraint
  changes. All headline numbers + methodology constraints from
  ADR-006 / ADR-016 / ADR-019 / ADR-020 / ADR-021 / ADR-022 /
  ADR-023 / ADR-025 / ADR-044 / ADR-060 are preserved.
- **ADR-062 immutability**: ADR-062's decisions are preserved;
  ADR-064 layers additively on top. No supersession.
- **Documentation discipline ratcheted**: the canonical terminology
  table (§C1) + the CI link-checker (§C2) raise the consistency
  floor for all future patches.
- **Audit trail clarity**: the 3-stage release (v1.1.3 baseline +
  v1.1.4 consistency-only + v1.2.0 heavy pass) gives each tag a
  coherent story. Per-stage rollback is possible.
- **Cost-trivial**: $0 GPU + CPU-only SVG re-render. ~$0 for the
  entire v1.1.3 + v1.1.4 + v1.2.0 series. CI link-checker is
  free-tier GH Actions minutes.

## Linked ADRs

- **References**:
  - `CLAUDE.md` — project ADR-discipline (immutability + supersession;
    motivates §D flagged-not-fixed pattern). (Historical note: older
    CHANGELOG entries cite "ADR-029" for immutability; the actual
    ADR-029 file is about test markers — the immutability rule lives
    in CLAUDE.md.)
  - [ADR-030](./ADR-030-deliverable-format-quarto-html-site.md) —
    Quarto site infrastructure.
  - [ADR-033](./ADR-033-github-release-strategy-rehearsal-plus-submission.md)
    — reviewer URL pin `tree/v1.0.0` (unchanged at v1.2.0).
  - [ADR-053](./ADR-053-reading-guide-governance-and-newcomer-paths.md)
    — original reading-guide governance (dimensions 2-5 unchanged;
    dimension 1 was narrowly superseded by ADR-061; this ADR layers
    on top of both).
  - [ADR-061](./ADR-061-quarto-site-navigation-restructure.md) —
    Quarto navigation restructure that consumed the original v1.1.1
    DeBERTa-execution slot.
  - [ADR-062](./ADR-062-quarto-writeup-clarity-and-canonical-figures.md)
    — Quarto writeup clarity rewrite (v1.1.3 baseline; this ADR
    layers additively on top).
  - [ADR-060](./ADR-060-deberta-v3-base-long-context-ablation-methodology.md)
    — DeBERTa methodology lock (cited in §B3 + §1B callout).
  - [ADR-063](./ADR-063-deberta-ablation-v1-1-2-execution-and-slot-shift.md)
    — DeBERTa execution record (cited in §B3 + §1B + §D).
- **Source**: /exploring-options 2026-05-19 round 1 (5 questions
  on landing form / DeBERTa placement / spoke density / figure
  scope / sub-commit cadence) + round 2 (5 questions on audit
  surface / ADR-063 fact-correction ceremony / CI prophylaxis /
  tag split / companion landing page). Full transcript at the
  source file referenced in the frontmatter.

## Transcript

`transcripts/2026-05-19__v1-2-0-writeup-clarity-and-consistency.md` —
captures the 3-audit findings + 2 /exploring-options rounds + the
full 3-stage execution (v1.1.3 baseline → v1.1.4 consistency-only
→ v1.2.0 heavy pass).
