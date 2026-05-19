---
adr_id: "065"
slug: writeup-accuracy-narrative-and-callout-conventions
title: Writeup accuracy-audit methodology + Quarto callout-note convention + narrative invariants — additive layer on top of ADR-064
date: 2026-05-19
status: Accepted
claim_id: CLAIM-065
claim: >-
  User feedback 2026-05-19 (post-v1.2.0 ADR-064 close): one more polish
  pass focused on three properties — narrative consistency (does the
  writeup hang together as a coherent story?), clarity (visual boxes for
  skim summaries; density reduction in dense spokes), and accuracy
  (every cited number re-verified against canonical sources). Three
  parallel `/exploring-options` rounds locked the v1.2.1 scope (rounds 3
  + 5 + 6; 12 total decisions across audit-script architecture, voice
  + tense pass mechanics, callout-note content source, sub-commit
  granularity, cumulative-cost figure precision). The pass adds a
  programmatic numeric-claim audit (`scripts/audit_writeup_numbers.py`;
  configurable `--strict` / `--report-only` flag; CI hard-gate via
  `.github/workflows/audit-writeup.yml`), a Quarto callout-note
  convention for spoke Summary boxes and collapsible hyperparameter
  detail, narrative invariants (third-person voice; tense discipline;
  paragraph length cap; transition sentences), and the canonical
  cumulative-cost figure ($17.08, full precision $17.0807) computed
  from `evals/cost_ledger.csv` at v1.2.0 close — superseding ADR-063's
  stale $9.92 figure (flagged but not computed in ADR-064 §D). Result:
  a closing-polish layer on v1.2.0 that ratifies reviewer-readiness via
  programmatic drift defense + skim-path discipline + voice consistency.
source: transcripts/2026-05-19__v1-2-1-narrative-clarity-accuracy.md (private; emailed at submission)
acceptance_criterion: >-
  At v1.2.1 close: `decisions/ADR-065-writeup-accuracy-narrative-and-callout-conventions.md`
  exists (this file). `scripts/audit_writeup_numbers.py` exists
  (configurable `--strict` default + `--report-only` opt-out flag;
  scans 4 categories: numbers / ADR slugs / version strings / URLs;
  ~200 LOC) and returns 0 drifts on the reviewer-facing markdown surface.
  `.github/workflows/audit-writeup.yml` exists (runs default-strict on
  push to main + PR + weekly schedule, mirroring the lychee CI pattern
  from ADR-064 §C2). `docs/GLOSSARY.md` carries the canonical-callout
  convention section (when to use `:::{.callout-note}` Summary vs
  `:::{.callout-tip collapse="true"}` hyperparameter detail vs
  `:::{.callout-warning}` caveats). All 8 `WRITEUP/*.md` spokes carry
  a top-of-page `:::{.callout-note}` Summary box (3-5 bullets distilled
  from existing `**Result**`-bolded subsection sentences).
  `WRITEUP/model-rungs.md` carries `:::{.callout-tip collapse="true"}`
  collapsible hyperparameter blocks (LoRA / TF-IDF / ProtectAI specs).
  All reviewer-facing markdown surfaces consistently use third-person
  voice (no first-person "we" / "I" / "our") and past-tense for
  completed methodology actions / present-tense for invariants.
  `decisions/library_imports.md` carries the audit-script entry with
  the audit-tooling-not-primitive tag per the strengthened library-first
  invariant. `CHANGELOG.md` [1.2.1] entry exists with the 7-commit
  cadence narrative + ADR-065 cross-ref + the cumulative-cost figure
  propagation chain. `NEXT_STEPS.md` §1.10 carries a Status (v1.2.1)
  paragraph + a 1-line cumulative-cost-to-date footnote citing
  ADR-065 §E. `SUBMISSION_AUDIT.md` regenerates clean with 65 CLAIM
  rows. CI markdown-link-checker (lychee) + new audit-writeup workflow
  both pass on the v1.2.1 push.
closing_commit: v1.2.1
supersedes: []
superseded_by: []
references:
  - CLAUDE.md  # project ADR-discipline (immutability + supersession)
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md  # $200 hard cap (unchanged)
  - decisions/ADR-030-deliverable-format-quarto-html-site.md  # Quarto-as-canonical-surface (callout rendering)
  - decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md  # reviewer URL pin tree/v1.0.0 (unchanged)
  - decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md
  - decisions/ADR-061-quarto-site-navigation-restructure.md  # signpost blockquote precedes Summary callout
  - decisions/ADR-062-quarto-writeup-clarity-and-canonical-figures.md  # F1-F5 figure caption discipline; v1.1.3 baseline
  - decisions/ADR-063-deberta-ablation-v1-1-2-execution-and-slot-shift.md  # stale $9.92 figure superseded by §E below
  - decisions/ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md  # predecessor (additive layer)
  - evals/cost_ledger.csv  # canonical cumulative-cost source-of-truth (§E)
  - NEXT_STEPS.md  # §1.10 Status (v1.2.1) + cumulative-cost footnote
  - CHANGELOG.md  # [1.2.1] + [1.1.2] postscript patch
  - docs/GLOSSARY.md  # canonical-callout convention section
  - scripts/audit_writeup_numbers.py  # the audit tooling
  - .github/workflows/audit-writeup.yml  # CI hard-gate
transcript: transcripts/2026-05-19__v1-2-1-narrative-clarity-accuracy.md
---

# ADR-065 — Writeup accuracy-audit methodology + Quarto callout-note convention + narrative invariants

## Status

Accepted (2026-05-19; additive layer on top of [ADR-064](./ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md) — no supersession of ADR-064's decisions; this ADR adds a closing-polish accuracy + clarity + narrative layer + supersedes ADR-063's stale cumulative-cost figure via §E).

## §A Context

[ADR-064](./ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md) shipped at v1.2.0 (commit `3212cc5`; 2026-05-19) and delivered the hiring-manager clarity pass (jargon-glossing invariant + table/plot pre-context + DeBERTa §1B + figure caption refinements + spoke skim signposts + Result-bolding + hiring-manager landing page) along with documentation-wide consistency invariants (canonical terminology table + lychee CI markdown-link-checker + flagged-not-fixed broken-slug references in immutable ADRs). The v1.1.3 → v1.1.4 → v1.2.0 series shipped 12 commits across 3 tagged GH releases.

User feedback 2026-05-19 (post-v1.2.0 close): one more polish pass focused on three properties — *narrative consistency* (does the writeup hang together as a coherent story?), *clarity* (visual boxes for skim summaries; density reduction in dense spokes), and *accuracy* (every cited number re-verified against canonical sources). The framing: the project is reviewer-ready and shipping a closing-polish layer is cheaper than risking a missed drift surfacing in reviewer audit.

Three sequential `/exploring-options` rounds locked the v1.2.1 scope (full transcript in the source file referenced in the frontmatter):

- **Round 3** (top-level scope): all three properties (heavy pass) → tag `v1.2.1`; every-number programmatic re-verification → new audit script; density reduction in dense spokes via Quarto callout-note "visual boxes" (NOT labeled "TL;DR" per user directive); collapsible hyperparameter blocks for `WRITEUP/model-rungs.md`.
- **Round 4** (sub-scope): Quarto callout-note syntax (`:::{.callout-note}` / `.callout-tip collapse="true"` / `.callout-warning`); audit-script broad scope (numbers + ADR slugs + version strings + URLs; ~200 LOC; overlaps lychee for URL/slug checking but catches semantic drift lychee misses); cumulative-cost-figure 3-place propagation (ADR-065 §E authoritative + CHANGELOG `[1.1.2]` postscript patch + NEXT_STEPS §1.10 footnote); voice + tense full sweep across 11 reviewer-facing surfaces including 8 spokes (~2.5h with ADR-spot-check risk mitigation); hand-pick Result-bolding per spoke (closes deferred Q3 round-1 lock).
- **Round 5** (audit-script architecture; this session): configurable failure mode (`--strict` default + `--report-only` opt-out for local iteration); project-internal (audit tooling is meta-level, not a methodology primitive subject to the strengthened library-first invariant); on-demand local + CI hard-gate (no pre-commit hook, matching ADR-064 §C2's contributor-friction discipline); hybrid 7-commit cadence (split handoff's Commit 4 into 4a Summary boxes + 4b model-rungs collapsible-hyperparameters).
- **Round 6** (execution mechanics; this session): hybrid voice/tense pass (grep prefilter + spot-read + ADR-diff on cited paragraphs); callout-note Summary box bullets distilled from `**Result**`-bolded subsection sentences; strict swap of Commits 4a + 5 so Result-bolding lands before Summary-box distillation; cumulative-cost figure as `$17.08` with provenance footnote in ADR-065 §E + compact form downstream.

This ADR codifies the locked decisions from rounds 3-6 into the project's audit-trail discipline. Implementation lands across 7 sub-commits at v1.2.1.

## §B Decision — accuracy-audit methodology (`scripts/audit_writeup_numbers.py`)

The v1.2.1 release introduces a programmatic numeric-claim audit at `scripts/audit_writeup_numbers.py` (~200 LOC; pattern after the existing `scripts/audit_leakage.py` + `scripts/audit_reference_scorers.py`). The script extracts 4 categories of claims from reviewer-facing markdown and cross-checks them against canonical sources:

### B1 — Scan categories (Q2 round-4 lock; broad scope)

1. **Hard numerical claims**: every AUPRC / AUROC / FPR / recall value; every row count; every dollar figure; every percentage. Cross-checked against canonical parquets (`evals/metrics/per_cell.parquet` + `evals/metrics/per_cell_deberta.parquet`) and `evals/cost_ledger.csv` for dollar figures.
2. **ADR slug references**: every `decisions/ADR-NNN-<slug>.md` link target verified against actual filenames in `decisions/`. Catches the broken-slug class lychee covers AND semantically-wrong-but-existing slug refs (e.g., "ADR-029 immutability" pointing at an existing ADR-029 file that is actually about test markers — the historical drift documented in [`memory/adr-029-immutability-misattribution-historical-drift.md`](../../../.claude/projects/-home-brandon-behring-Claude-prompt-injection-detection-submission/memory/adr-029-immutability-misattribution-historical-drift.md) at the meta-level).
3. **Version strings**: stale `v1.0.x` / `v1.1.1 deferred` / "pending" / "will land" patterns that should reflect the current v1.2.0+ state.
4. **URL slugs**: HF Hub `BBehring/prompt-injection-{lora,frozen-probe}` pattern + GitHub `brandon-behring/prompt-injection-detection-prototype` repo slug. Catches typos like `-submission` → `-prototype`.

Scans 12 reviewer-facing surfaces: `index.qmd`, `EXECUTIVE_SUMMARY.md`, `README.md`, `RESULTS.md`, `WRITEUP.md`, `WRITEUP/*.md` (8 spokes), `READING_GUIDE.md`, `docs/for-hiring-managers.md`, `docs/GLOSSARY.md`, `NEXT_STEPS.md`, `CHANGELOG.md`. Prints a per-category drift report.

### B2 — Failure model (Q1 round-5 lock)

Configurable via flag. **`--strict` is the default** (exit 1 on any drift; CI uses this mode for hard-gate prevention of future regressions; aligns with the `regenerate_audit.py --check` CI hard-gate model). **`--report-only` is the opt-out** (always exit 0; print drift report for local-dev iteration while tuning false-positive filters; supports the per-handoff §Sanity-check anticipation that *"the broad-scope extraction will match things that aren't claims"*).

This split ensures the developer can iterate the script on local runs until false positives are tuned, then rely on the strict-mode CI gate to prevent regression.

### B3 — Upstreaming (Q2 round-5 lock; project-internal)

The audit script is **project-internal** and does NOT upstream to `eval-toolkit` / `runpod-deploy` / `research_toolkit`. The four scan-pattern categories are project-shaped (per-cell.parquet column names; specific ADR slug formats; HF Hub `BBehring/prompt-injection-*` URL pattern; project-specific dollar-figure context). Audit tooling is a meta-level concern (submission-prep one-off), not a methodology primitive subject to the strengthened library-first invariant in [`memory/library_first_is_project_wide_invariant.md`](../../../.claude/projects/-home-brandon-behring-Claude-prompt-injection-detection-submission/memory/library_first_is_project_wide_invariant.md). The script is logged in `decisions/library_imports.md` with the explicit `audit-tooling-not-primitive` tag.

### B4 — Invocation surface (Q3 round-5 lock; on-demand local + CI hard-gate)

The script runs in two contexts:

1. **On-demand local invocation**: `uv run python scripts/audit_writeup_numbers.py` (default `--strict`) or `uv run python scripts/audit_writeup_numbers.py --report-only` (iteration mode). Documented in `CONTRIBUTING.md` / `README.md` Verification section.
2. **CI hard-gate**: new `.github/workflows/audit-writeup.yml` runs default-strict on push to main + PR + weekly schedule. Mirrors the lychee CI pattern introduced at v1.1.4 per ADR-064 §C2.

**No pre-commit hook**. This is deliberate per ADR-064 §C2's discipline (*"CI only; no local pre-commit hook to avoid contributor friction"*); the audit-writeup workflow extends that policy.

### B5 — Reusability

The audit-script remains in `scripts/` and is reusable for future v1.X patches. ADR-065 §B1's 4-category scan-pattern is the canonical methodology; future contributors extend the script by adding scan-patterns rather than re-inventing the audit approach.

## §C Decision — Quarto callout-note convention

The v1.2.1 release introduces a canonical Quarto callout-note convention, documented in `docs/GLOSSARY.md` for future contributors. Three callout types are reserved for three specific reader-facing purposes:

### C1 — `:::{.callout-note}` — top-of-page Summary box

Reserved for **3-5 bullet headline takeaways** placed at the top of any reviewer-facing markdown spoke (especially `WRITEUP/*.md`), directly below the existing 1-line back-link + "How to read this spoke" signpost from ADR-064 §B5. The signpost stays as meta-navigation; the callout is the actual content summary.

Per Q2 round-6 lock, the bullets are **distilled from existing `**Result**`-bolded subsection sentences** (added at v1.2.0 per ADR-064 §B5; refined per Q5 round-4 hand-pick lock). Each Summary bullet is therefore anchored to an existing `**Result**` claim in the spoke body — eliminating fresh-writing drift risk. Per Q3 round-6 strict-swap lock, the Result-bolding pass (Commit 4a in v1.2.1's 7-commit cadence) lands BEFORE the Summary-box pass (Commit 4b) so the source sentences are visibility-tagged when the Summary box is drafted.

### C2 — `:::{.callout-tip collapse="true"}` — collapsible detail block

Reserved for **dense audit-detail content** that the casual reader does not need but the auditor must reach. Specifically: hyperparameter blocks (`r`, `alpha`, `dropout`, `target_modules` for LoRA; `max_features` + `solver` + `class_weight` for TF-IDF; revision SHA + inference settings for reference scorers). Reader sees a summary line + can expand for detail. Reduces visual density without losing audit-detail content.

**GH blob fallback note** (per Q1 round-4 lock + ADR-030's Quarto-as-canonical-surface rule): GitHub blob view does NOT render collapsible callouts; the content appears expanded with `:::` fence markers visible. Acceptable since the Quarto site is the canonical reading surface (per ADR-030); the audit-detail content is preserved either way.

### C3 — `:::{.callout-warning}` — caveats and limitations

Reserved for caveats / limitations / known-narrow-scope reservations. Used sparingly for content that the reader must NOT miss (e.g., reference-scorer contamination-tier reservations; ablation-result interpretation boundaries). Currently used in `WRITEUP/limitations-and-future-work.md` for residual-confound caveats.

### C4 — Convention not labeled "TL;DR"

Per Q3 round-3 lock, the Summary callout-note is NOT labeled "TL;DR" (user directive). The label "Summary" is used instead. Rationale: "TL;DR" carries a casual / informal connotation; "Summary" matches the audit-prep tone of the rest of the writeup.

## §D Decision — narrative invariants

The v1.2.1 release establishes narrative invariants for reviewer-facing markdown that future patches must preserve. These layer on top of ADR-064 §B1 (jargon-glossing invariant) + §C1 (canonical terminology table).

### D1 — Voice (third-person)

All reviewer-facing markdown uses **third-person voice**. The author/owner is referred to as "the project", "the harness", "the candidate" (in `docs/for-hiring-managers.md` only); methodology actors are referred to by their actual identifier ("the LoRA adapter", "the frozen-probe head", "the ProtectAI v1 reference scorer"). First-person ("we", "I", "our", "us", "my") is reserved for transcripts, ADRs (where the decision-maker speaks in first-person retrospectively), and the candidate's voice in `docs/for-hiring-managers.md` §"What does this tell me about how the candidate thinks?".

Implementation per Q1 round-6 hybrid mechanism: grep prefilter (`\b(we|I|our|my|us)\b`) surfaces first-person hits; spot-read for transition awkwardness; ADR-diff on paragraphs that cite an ADR (use the ADR's voice as canonical anchor per the project ADR-source-of-truth pattern).

### D2 — Tense

Past tense for **completed methodology actions** ("the model was trained on..."); present tense for **invariants** ("AUPRC requires both classes"). Future tense ("will land", "will train") is avoided in reviewer-facing prose — if work is incomplete, mark it in `NEXT_STEPS.md` §1.X with a status flag instead of embedding future-tense in the writeup.

### D3 — Transitions

Major section boundaries (especially WRITEUP §3↔§4↔§5↔§6; spoke §subsection boundaries) carry a **transition sentence** that signposts what the reader is about to encounter and how it connects to the prior section. Avoid the "blank section break" anti-pattern where a section starts mid-thought.

### D4 — Paragraph length cap

~150-word maximum paragraph on reviewer-facing surfaces. Long paragraphs are split at thematic boundaries; lists are bulleted when they enumerate items rather than build an argument.

### D5 — ADR-anchor discipline

When a paragraph cites an ADR ("per ADR-NNN"), the ADR's own voice + tense is the canonical anchor for the surrounding prose. If the spoke drifts from the ADR's wording, prefer the ADR's wording on edit. If the edit changes meaning (not just voice), escalate to a postscript-style note rather than a direct rewrite (per Q4 round-4 risk mitigation).

## §E Cumulative cost canonical figure

The canonical cumulative project compute spend as of v1.2.0 close is **`$17.08` USD** (full precision `$17.0807`; sum of `actual_cost_usd` across 17 GPU-pod rows in `evals/cost_ledger.csv` as of commit `3212cc5`, 2026-05-19). Within ADR-020's `$200` hard cap.

This figure **supersedes** ADR-063's stale `$9.92` (which was computed from a subset of pod rows at the time ADR-063 was authored in v1.1.2). ADR-064 §D flagged the stale figure but did not compute the canonical value; ADR-065 §E does. ADR-063 itself remains immutable per CLAUDE.md ADR-discipline; readers consulting ADR-063's `$9.92` figure are directed (via CHANGELOG `[1.1.2]` postscript patch landed at v1.2.1) to ADR-065 §E for the canonical figure.

### Propagation chain (Q3 round-4 lock; Q4 round-6 wording lock)

- **ADR-065 §E** — authoritative source. Carries the full clause: *"$17.08 (sum of `actual_cost_usd` across 17 GPU-pod rows in `evals/cost_ledger.csv` as of v1.2.0 close 2026-05-19, commit `3212cc5`; full precision $17.0807)"*.
- **CHANGELOG `[1.1.2]` postscript patch** (landed at v1.2.1 Commit 2) — cites `$17.08` and references ADR-065 §E for provenance.
- **NEXT_STEPS.md §1.10 footnote** (landed at v1.2.1 Commit 2) — 1-line cumulative-cost-to-date entry alongside the existing `$1.34` v1.1.2-spend line; cites `$17.08` and references ADR-065 §E for provenance.

### Future drift defense

`scripts/audit_writeup_numbers.py` (per §B) catches cost-figure drift in reviewer-facing markdown by cross-checking dollar-figure mentions against `evals/cost_ledger.csv`. Future patches that add cost rows or restate cumulative cost cannot drift undetected — the audit-writeup CI workflow blocks merge if the figure stales.

## §F Consequences

### F1 — Reviewer experience

A hiring manager or technical reviewer landing on the live Quarto site sees:

- Skim path: spoke top-of-page Summary callout-note (3-5 bullets anchored to `**Result**` claims) → can dive into subsections or stop
- Dense detail: `WRITEUP/model-rungs.md` hyperparameter blocks visually collapsed; reader expands only what they audit
- Cost figure: canonical `$17.08` propagated to 3 reader-facing places (ADR-065 §E + CHANGELOG postscript + NEXT_STEPS footnote); no `$9.92` drift surfaces in reviewer-facing prose
- Voice + tense: consistent third-person past-for-actions / present-for-invariants across 11 surfaces
- Drift defense: every cited number / ADR slug / version string / URL on every reviewer-facing surface verified at CI time via audit-writeup workflow

### F2 — Documentation discipline ratcheted

The canonical-callout convention (§C) + narrative invariants (§D) + audit-writeup CI hard-gate (§B4) raise the consistency floor for all future v1.X patches. Combined with ADR-064 §C1 (canonical terminology) + §C2 (lychee link-checker CI), the project's reviewer-facing markdown surface has 3 distinct CI-enforced consistency gates (lychee + audit-writeup + regenerate-audit-check).

### F3 — ADR-064 immutability preserved

ADR-064's decisions are not superseded by ADR-065; this ADR layers additively on top. The only supersession is the §E cumulative-cost figure superseding ADR-063's `$9.92` — and that supersession is expressed via CHANGELOG postscript patch (already in place per v1.1.4) + ADR-064 §D narrative flag, both pointing readers to ADR-065 §E. ADR-063 itself remains immutable.

### F4 — Audit-script reusability

`scripts/audit_writeup_numbers.py` is reusable for future v1.X patches. Future contributors extend the 4-category scan list rather than re-invent the audit; the CI workflow stays default-strict so the gate prevents regression.

### F5 — Cost-trivial

$0 GPU + CPU-only audit-script execution + Quarto callout-note rendering. ~$0 for the entire v1.2.1 release; cumulative project spend remains $17.08 (no new GPU rows added at v1.2.1).

### F6 — Audit trail clarity

The 7-commit cadence at v1.2.1 (1: ADR-065 + GLOSSARY → 2: audit-script + drift fixes → 3: voice/tense → 4a: Result-bolding → 4b: Summary boxes → 4c: model-rungs collapsible → 5: close) gives reviewers a coherent per-commit story. Each commit one concern; bisectable; honors the user's `manually review all of your work` directive (Q2 round-6) by isolating concern-per-commit for ease of self-review.

## Linked ADRs

- **References**:
  - `CLAUDE.md` — project ADR-discipline (immutability + supersession; motivates §E supersession via §D-flag + postscript chain rather than ADR-063 edit).
  - [ADR-020](./ADR-020-compute-infrastructure-and-cost-discipline.md) — `$200` hard cap (unchanged; current cumulative `$17.08` well within).
  - [ADR-030](./ADR-030-deliverable-format-quarto-html-site.md) — Quarto-as-canonical-surface (motivates §C2's GH-blob-fallback acceptance).
  - [ADR-033](./ADR-033-github-release-strategy-rehearsal-plus-submission.md) — reviewer URL pin `tree/v1.0.0` (unchanged at v1.2.1).
  - [ADR-053](./ADR-053-reading-guide-governance-and-newcomer-paths.md) — original reading-guide governance.
  - [ADR-061](./ADR-061-quarto-site-navigation-restructure.md) — Quarto navigation restructure that introduced the spoke back-link signpost (precedes the Summary callout-note per §C1).
  - [ADR-062](./ADR-062-quarto-writeup-clarity-and-canonical-figures.md) — Quarto writeup clarity rewrite (v1.1.3 baseline).
  - [ADR-063](./ADR-063-deberta-ablation-v1-1-2-execution-and-slot-shift.md) — DeBERTa execution record carrying the stale `$9.92` cumulative-cost figure superseded by §E above.
  - [ADR-064](./ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md) — predecessor (additive layer; ADR-065's §D narrative invariants extend ADR-064 §B1 jargon-glossing + §C1 canonical terminology).
- **Source**: `/exploring-options` rounds 3 + 5 + 6 (2026-05-19). Round 3 (3 questions: property focus / accuracy depth / rewrite depth) + Round 5 (4 questions: audit-script failure mode / upstreaming / invocation surface / sub-commit granularity) + Round 6 (4 questions: voice-pass mechanics / callout-note content source / Commit 4a-5 ordering / cost-figure precision). Full transcript at the source file referenced in the frontmatter.

## Transcript

`transcripts/2026-05-19__v1-2-1-narrative-clarity-accuracy.md` — captures the 3 `/exploring-options` rounds + the 7-commit execution + manual-self-review-at-each-commit-boundary discipline per Q2 round-6 user directive.
