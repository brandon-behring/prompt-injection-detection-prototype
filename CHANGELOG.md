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

## [Unreleased]

## [1.3.13] — 2026-05-26 {#v1-3-13}

**Consumer adoption of upstream `eval-toolkit` v1.3.0 Layer 3
pairing rules** (closes the v1.3.12-filed
[eval-toolkit#81](https://github.com/brandon-behring/eval-toolkit/issues/81)
adoption loop). Upstream shipped v1.3.0 ~51 minutes after #81
was filed (2026-05-26T22:27Z — fastest cycle yet in the R11→R14
sequence) with four pairing rules per upstream
[ADR 0006](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/source/adr/0006-pairing-rules-for-cross-detector-list-grammar.md),
codifying Layer 3 (pairing) as the third correctness layer
alongside ADR 0005's identity + scope:

- **Pattern A — `"for {detector}"` postfix override**: with
  intervening-value guard via v1.1.0 exclusion-ranges.
- **Pattern B — `"{detector}'s"` possessive override**: last
  possessive within 30 chars of value is authoritative.
- **Pattern C — group-subject suppression**: `"for the
  {trained|frozen|baseline|all|both|other} detectors"`
  pattern suppresses the value (group statement, not single
  binding); sentence-boundary guard via v1.2.0 sentence-positions.
- **Pattern D — metric-axis nearest-pairing**: symmetric to
  detector-axis pairing; pre-collects ALL metric positions
  across consumer-supplied `metric_aliases` keys, not just
  binding-derived metrics. Emerged during upstream's own
  dogfood (4→2 after A/B/C; metric-confusion surfaced as
  residual; Pattern D added symmetrically).

All four rules activate automatically when `scope="narrative"`
is set (which this repo already does at v1.3.11+). **Tier-1
ADDITIVE per ADR 0006 — no signature drift, no new public kwargs**.

**Adoption = pin bump only.** No script changes required.

### Dogfood result on `audit_value_bindings`

| Configuration | Warnings on this repo HEAD | Reduction vs v1.0.5 baseline |
|---|---|---|
| v1.0.5 (legacy 2-tuple) | 96 | — |
| v1.1.0 (BindingKey + scope='narrative') | 36 (this repo) | 62% |
| v1.2.0 (+ T1-T4 context filters) | 4 (this repo) | 96% |
| **v1.3.0 (+ Layer 3 pairing rules)** | **0 (this repo)** | **100%** |

**100% total noise reduction. Four-round R11→R14 cycle closed.**

### Concurrent: filed upstream eval-toolkit#82 for `audit_citation_alignment` context-awareness

The `audit_citation_alignment` validator (shipped v1.0.1, closes
#73) is one architectural layer behind `audit_value_bindings`.
On this repo's HEAD with v1.3.0 of eval-toolkit, it emits
**188 warnings** across legitimate reader-facing claim surfaces:
67 on SPEC_SHEET.md (Phase-0 lock sheet), 15 on assumptions.md,
14 on EVIDENCE.md, 12 on docs/ROADMAP.md, 10 on
WRITEUP/model-rungs.md, 10 on SPEC_GREENFIELD.md, etc.

The warnings cluster in three patterns:

1. **Pattern α — dense multi-ADR-citation list within one
   paragraph** (e.g., `"per ADR-025 + ADR-021 + ADR-034 + ADR-045"`
   where surrounding prose covers calibration + thresholds +
   reproducibility + manifest discipline simultaneously).
2. **Pattern β — spec/table per-row ADR citations** (e.g.,
   SPEC_SHEET.md row covers multiple topics but the validator
   picks one dominant keyword).
3. **Pattern γ — multi-claim sentence with ADR per-clause**
   (clause-level subject the positional heuristic can't
   disambiguate).

Same architectural class as the cross-detector list-grammar
problem #81 just solved for `audit_value_bindings` via ADR 0006
Layer 3 pairing rules. Filed
[eval-toolkit#82](https://github.com/brandon-behring/eval-toolkit/issues/82)
proposing equivalent scope+pairing extensions for
`audit_citation_alignment` (Path A: `scope='narrative'` mirror
of v1.1.0; Path B: pairing rules mirror of v1.3.0). Sixth
library-first cycle (R15-equivalent following R11→R14 closure
for audit_value_bindings).

### Gate severity

SOFT retained on BOTH validators at v1.3.13. The v1.3.8
CHANGELOG bundled-promotion plan (promote both
`audit_value_bindings` + `audit_citation_alignment` SOFT→HARD
together) is **preserved**: `audit_value_bindings` is now
HARD-credible (0 warnings) but `audit_citation_alignment` is
not yet (188 warnings on reader-facing surfaces; structural
gap to address upstream). **Bundled HARD-gate promotion
deferred to v1.3.14+ pending eval-toolkit#82 resolution.**

This is a deliberate library-first choice: per ADR 0005 Layer 2
design philosophy, context-correctness belongs in the validator,
not in consumer-side suppression regex or prose rewrites for
validator compliance.

### Tests

Existing 14 audit_value_bindings tests still PASS — Tier-1
ADDITIVE upstream guarantee held in practice (Pattern D's wider
metric-alias matching coexists cleanly with the consumer's
AUPRC + AUROC METRIC_ALIASES).

### Round 14 ledger reference

Upstream `docs/source/audit_findings.md` Round 14 entry
documents the full R11→R14 cycle with timings:

| Round | Driver | Cycle time | Closure |
|---|---|---|---|
| R11 | Consumer adopts v1.0.x audit-validator family | days | v1.0.4 |
| R12 | Consumer files #80 (BINDINGS slice-axis) | ~2 hours | v1.1.0 |
| R13 | v1.1.0 dogfood surfaces context-filter gaps | ~1 hour | v1.2.0 |
| R14 | Consumer files #81 (cross-detector list-grammar) | ~1.5 hours | v1.3.0 |

End-to-end #81 → v1.3.0 = 51 minutes. **This is the fastest
cycle in the post-v1.0 sequence.**

Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033.

### Changed

- `pyproject.toml` — `eval-toolkit>=1.2.0,<2` → `>=1.3.0,<2`.
  Tightens lower bound to require Layer 3 pairing rules shipped
  in v1.3.0.
- `uv.lock` — `eval-toolkit==1.2.0` → `eval-toolkit==1.3.0`.
- `scripts/audit_citation_alignment.py` — `SKIP_PATTERNS`
  expanded to mirror `audit_value_bindings` v1.3.11 additions
  (added `SUBMISSION.md`, `_codex.md`, `AUDIT_CLAUDE_`,
  `draft.md`, `draft_review.md` — gitignored / historical files
  that aren't reader-facing claim surfaces; parallel discipline
  between the two validators).
- `decisions/library_imports.md` — eval-toolkit row trajectory
  extended with `v1.2.0→v1.3.0 at v1.3.13 (consumed Layer 3
  pairing rules per ADR 0006; closes #81; 100% total noise
  reduction = 0 residuals; closes R11→R14 cycle on
  audit_value_bindings)`.
- `decisions/upstream_issues.md` — #81 row Status → RESOLVED in
  v1.3.0; consumed at v1.3.13. New row added for #82
  (audit_citation_alignment context-awareness; filed concurrent
  with v1.3.13).
- `CITATION.cff` — version `1.3.12` → `1.3.13`.

### Audit-driven (filed concurrent with v1.3.13 tag)

- **Filed upstream eval-toolkit#82**: `audit_citation_alignment`
  multi-ADR-citation context-awareness (Layer 2 scope + Layer 3
  pairing equivalent for the citation-alignment validator). 188
  concrete repro warnings on consumer HEAD organized into 3
  patterns (α dense multi-ADR list; β spec/table per-row; γ
  multi-claim sentence). Sixth library-first cycle.

### Updated

- Reader-surface `tree/v1.3.12` anchors advanced to `tree/v1.3.13`
  across 5 files (`index.qmd:79`, `README.md:222`,
  `READING_GUIDE.md:91`, `WRITEUP_PAPER.md:7`,
  `WRITEUP_NARRATIVE.md:7`).
- `.lycheeignore` adds `tree/v1.3.13` (chicken-and-egg per
  v1.2.13 + v1.3.2..v1.3.12 precedent).

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.12] — 2026-05-26 {#v1-3-12}

**Consumer adoption of upstream `eval-toolkit` v1.2.0 T1-T4
context-aware narrative filters**: closes the v1.1.0 → v1.2.0
follow-on adoption loop. Upstream shipped v1.2.0 ~1h after
v1.1.0 closed (2026-05-26T21:20Z; closes the
[#80](https://github.com/brandon-behring/eval-toolkit/issues/80)
deferred-residual category) with four context-aware extensions
to `scope="narrative"`:

- **T1 — Delta-context filter**: suppresses sign-prefixed values
  (`-0.071`, `+0.073`) + values near delta keywords (delta,
  drop, lift, gap, margin, regresses, improves, beats, exceeds,
  trails, underperforms, vs, versus, below).
- **T2 — Floor-context filter**: suppresses values near random /
  floor / chance / trivial keywords (asymmetric window: 50 chars
  before, 5 chars after).
- **T3 — Consume-on-match within sentence**: after a value
  produces a Match, subsequent values for the same canonical
  binding within the same sentence are suppressed.
- **T4 — Sentence-boundary detector-pair reject**: when pairing
  a detector mention with a value, if a sentence terminator
  lies between them, the pair is rejected. Uses
  paragraph-aware abbreviation guarding (vs./e.g./i.e./etc./
  fig./eq./pp./viz./ca. excluded; decimal numbers + letter-
  dot-letter patterns guarded; single `\n` soft, `\n\n` hard).

All four filters activate automatically when `scope="narrative"`
is set (which this repo already does at v1.3.11). **Tier-1
ADDITIVE per upstream ADR 0005 amendment** — no signature drift,
no new public kwargs, full backward-compat for legacy
`scope="all"` callers.

**Adoption = pin bump only.** No script changes required.

**Dogfood result**:

| Configuration | Warnings on this repo HEAD | Reduction vs v1.0.5 baseline |
|---|---|---|
| v1.0.5 (legacy 2-tuple) | 95 (upstream measurement) / 96 (this repo at v1.3.10) | — |
| v1.1.0 `BindingKey` + `scope='narrative'` | 23 (upstream) / 36 (this repo at v1.3.11) | 76% / 62% |
| **v1.2.0 + T1-T4 (this release)** | **7 (upstream) / 4 (this repo at v1.3.12)** | **93% / 96%** |

This repo's 4-warning result is better than upstream's 7 because
v1.3.10 added `SKIP_PATTERNS` for gitignored files
(`SUBMISSION.md`, `*_codex.md`, `AUDIT_CLAUDE_`, `draft.md`,
`draft_review.md`) that upstream's dogfood didn't exclude.

**Remaining 4 residuals** are all in the upstream-deferred
"cross-detector list-grammar" category — prose patterns the
v1.2.0 positional heuristic can't disambiguate:

1. `README.md:71` — `"in-pool 0.99 → cross-family 0.38 for the
   trained detectors; frozen probe's gap is 0.91 → 0.515"`
   (sentence-shift contrast; 0.38 belongs to trained detectors,
   not the next-mentioned frozen probe).
2. `RESULTS.md:171` (×2) — `"LoRA's pooled OOD AUROC is 0.383
   against frozen probe's 0.515"` (possessive comparative +
   metric-confusion).
3. `WRITEUP_PAPER.md:304` — `"versus 0.364 [...] for the frozen
   probe and 0.291 [...] for TF-IDF + LR"` (multi-detector
   "for X" list connective).

Per the library-first invariant, **a new upstream issue
[eval-toolkit#81](https://github.com/brandon-behring/eval-toolkit/issues/81)
is filed concurrent with this release** requesting the v1.3.0+
parser-level work named in upstream ADR 0005 + Round 13 ledger.
The path forward (per upstream's framing): shallow list-grammar
parsing OR markdown AST parsing.

**Gate severity**: SOFT retained at v1.3.12. HARD-gate
promotion still deferred per the v1.3.8 bundled-promotion
plan + observation window. With 4 residual FPs still in the
narrative-prose surface, HARD-gating now would block commits
on those 4 lines unless we add suppression regex (bad form per
ADR 0005 design philosophy — context-correctness belongs in the
validator, not in consumer-side line-filters) or rewrite prose
for validator compliance (bad form for reader experience).
HARD-gate becomes credible after upstream #81 lands.

**No tests changed** — the existing 14-test suite still PASSES
because the new T1-T4 filters don't change any test fixture's
expected output (the V1.3.1 ADR-080 regression fixture still
flags as designed; the clean-case fixture still passes; the
slice-disambiguation fixture still passes; the table-exclusion
fixture still passes). Upstream Tier-1 ADDITIVE guarantee held
in practice.

Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033.

### Changed

- `pyproject.toml` — `eval-toolkit>=1.1.0,<2` → `>=1.2.0,<2`.
  Tightens lower bound to require T1-T4 context filters shipped
  in v1.2.0.
- `uv.lock` — `eval-toolkit==1.1.0` → `eval-toolkit==1.2.0`.
- `decisions/library_imports.md` — eval-toolkit row trajectory
  extended with `v1.1.0→v1.2.0 at v1.3.12 (consumed T1-T4
  context-aware narrative filters; Tier-1 ADDITIVE per ADR
  0005 amendment; T1-T4 follow-on to #80; 96% total noise
  reduction from 96-warning v1.0.5 baseline = 4 residuals on
  this repo, all in upstream-deferred cross-detector list-
  grammar class)`.
- `decisions/upstream_issues.md` — #80 row extended with v1.2.0
  follow-on dogfood narrative (36→4); new row added for #81
  cross-detector list-grammar (filed concurrent with v1.3.12;
  4 concrete repro patterns from this repo).
- `CITATION.cff` — version `1.3.11` → `1.3.12`.

### Audit-driven (filed concurrent with v1.3.12 tag)

- **Filed upstream eval-toolkit#81**: cross-detector list-grammar
  v1.3.0+ follow-on. Provides 4 concrete consumer-side repro
  patterns; references upstream ADR 0005 A4 + Round 13 ledger
  framing (shallow list-grammar parsing OR markdown AST). The
  third issue in the audit_value_bindings family
  (#71→#80→#81). Consumer-side HARD-gate promotion deferred
  until upstream resolution.

### Updated

- Reader-surface `tree/v1.3.11` anchors advanced to `tree/v1.3.12`
  across 5 files (`index.qmd:79`, `README.md:222`,
  `READING_GUIDE.md:91`, `WRITEUP_PAPER.md:7`,
  `WRITEUP_NARRATIVE.md:7`).
- `.lycheeignore` adds `tree/v1.3.12` (chicken-and-egg per
  v1.2.13 + v1.3.2..v1.3.11 precedent).

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.11] — 2026-05-26 {#v1-3-11}

**Consumer adoption of upstream `eval_toolkit.BindingKey` +
`scope='narrative'`**: closes the v1.3.9-filed
[eval-toolkit#80](https://github.com/brandon-behring/eval-toolkit/issues/80)
adoption loop. Upstream shipped v1.1.0 ~2h after #80 was filed
(2026-05-26T20:11Z, end-to-end 2-hour compressed cycle) with the
proposed schema extension PLUS architectural improvements beyond
the consumer's proposal:

- **`BindingKey`** frozen-dataclass canonical identity (not bare
  3-tuple); forward-extensible for future axes (split, ci_kind,
  source_ref, ...) without breaking the dict-key schema. Avoids
  the recur-every-N-months schema-event pattern that produced #80
  itself. Codified in upstream [ADR 0005](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/source/adr/0005-structured-keys-for-audit-validators.md)
  ("structured keys over positional tuples for canonical-identity
  types in audit validators"; Accepted at v1.1.0).
- **`scope='narrative'`** content-type filter (second architectural
  layer beyond what was filed): excludes markdown table rows,
  bracketed CI expressions, and fenced code blocks from candidate
  matching. ADR 0005 frames this as the second layer of a two-layer
  correctness model (identity correctness via `BindingKey` + scope
  correctness via `scope='narrative'`).

**Consumer-side adoption** at `scripts/audit_value_bindings.py`:

- Migrated `BINDINGS` from `Mapping[tuple[str, str], float]` →
  `Mapping[BindingKey, float]` per upstream ADR 0005 recommendation
  ("New consumer code SHOULD use the canonical `BindingKey` form;
  tuple shapes are syntactic sugar / backward-compat preservation").
- Expanded `BINDINGS` from 2 entries → 15 entries covering all
  reader-facing headline bindings: direct_validation AUPRC (3
  detectors), pooled_ood AUPRC (5 detectors), pooled_ood AUROC (3
  detectors), JBB-Behaviors AUPRC (ProtectAI v1+v2), XSTest AUPRC
  (ProtectAI v1+v2).
- Added new `SLICE_ALIASES` regex map (direct_validation /
  pooled_ood / jbb / xstest) for slice surface-form matching.
- Added 3 new detectors to `DETECTOR_ALIASES` (frozen_probe,
  ProtectAI-v1, ProtectAI-v2).
- Added `AUROC` to `METRIC_ALIASES`.
- Pass `slice_aliases=SLICE_ALIASES` + `scope="narrative"` into
  the `validate_reader_value_bindings(...)` call.
- Extended `SKIP_PATTERNS` to exclude `SUBMISSION.md` (gitignored
  cover-letter draft), `*_codex.md` (gitignored Codex audit
  reports), `AUDIT_CLAUDE_*` (historical audit transcripts), and
  `draft.md` / `draft_review.md` (legacy v0.x drafts) — none of
  these are reader-facing claim surfaces.

**Dogfood result**: warning count drops from 96 (v1.3.10 pre-edit,
2-tuple schema, no scope filter) → 36 (v1.3.11, BindingKey +
`scope='narrative'` + expanded SKIP_PATTERNS) — **62% noise
reduction**. Upstream dogfood reported 76% against the smaller
v1.3.9 file set before v1.3.10 stub-anchor + hiring-page additions;
the residual 36 are all in upstream-acknowledged "known limitations"
categories (multi-detector list pairings, sub-clause sentence
boundaries, "X vs Y" comparison patterns) addressable only via
upstream v1.2.0+ parser-level work.

**Gate severity**: SOFT retained at v1.3.11. Per the v1.3.8
CHANGELOG bundled-promotion plan, HARD-gate promotion deferred to
a future v1.3.X bundled with `audit_citation_alignment` after
observation window + potential consumer-side suppression regex for
the residual 36 (upstream Round 12 ledger suggests excluding lines
containing "random floor" or "versus"; addresses the
positional-heuristic limit class until parser-level v1.2.0+).

**Tests**: `tests/scripts/test_audit_value_bindings.py` expanded
from 7 tests → 14 tests covering BindingKey schema, slice
disambiguation (same `(detector, metric)` across direct_validation
vs pooled_ood doesn't cross-flag), `scope='narrative'` filtering
(table rows + CI brackets excluded), and the additional skip
patterns. Full test suite: all 14 PASS.

Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033.

### Added

- `scripts/audit_value_bindings.py` — `SLICE_ALIASES: Mapping[str,
  Sequence[str]]` regex map with surface forms for
  direct_validation / pooled_ood / jbb / xstest slices.
- `scripts/audit_value_bindings.py` `DETECTOR_ALIASES` — 3 new
  entries (frozen_probe, ProtectAI-v1, ProtectAI-v2).
- `scripts/audit_value_bindings.py` `METRIC_ALIASES` — AUROC entry
  with surface aliases (`AUROC`, `AU-ROC`, `ROC-AUC`, `ROC AUC`).
- `tests/scripts/test_audit_value_bindings.py` — 7 new tests
  (BindingKey schema; pooled-OOD headline slate; slice aliases
  coverage; codex audit reports skip; SUBMISSION.md skip; slice
  disambiguation; scope='narrative' table exclusion). Test count
  doubled from 7 → 14; all PASS.

### Changed

- `scripts/audit_value_bindings.py` — `BINDINGS` schema migrated
  from `Mapping[tuple[str, str], float]` (2-tuple `(detector,
  metric)` keys) → `Mapping[BindingKey, float]` (frozen-dataclass
  structured keys with `slice` axis) per upstream ADR 0005.
  Expanded from 2 entries (V1.3.1 ADR-080 motivating seed only)
  to 15 entries (full headline slate). Validator call now passes
  `slice_aliases=SLICE_ALIASES` + `scope="narrative"`.
- `scripts/audit_value_bindings.py` `SKIP_PATTERNS` extended with
  `SUBMISSION.md`, `_codex.md`, `AUDIT_CLAUDE_`, `draft.md`,
  `draft_review.md` (5 new patterns; closes false-positive surface
  on gitignored / historical files).
- `pyproject.toml` — `eval-toolkit>=1.0.3,<2` → `>=1.1.0,<2`.
  Tightens lower bound to require `BindingKey` + slice-aware
  matching + `scope='narrative'` shipped in v1.1.0.
- `uv.lock` — `eval-toolkit==1.0.3` → `eval-toolkit==1.1.0`.
- `decisions/library_imports.md` — eval-toolkit row trajectory
  extended with `v1.0.3→v1.1.0 at v1.3.11 (consumed BindingKey +
  scope='narrative' per upstream ADR 0005 two-layer correctness
  model; closes #80; 62% noise reduction on this repo vs 2-tuple
  schema)`.
- `decisions/upstream_issues.md` — #80 row Status updated from
  "filed at v1.3.9 (2026-05-26); concurrent with v1.3.9
  polish-audit fix-forward" to "RESOLVED in eval-toolkit v1.1.0;
  consumed at v1.3.11" with the full 2-hour upstream cycle +
  dogfood-result narrative.
- `CITATION.cff` — version `1.3.10` → `1.3.11`.

### Updated

- Reader-surface `tree/v1.3.10` anchors advanced to `tree/v1.3.11`
  across 5 files (`index.qmd:79`, `README.md:222`,
  `READING_GUIDE.md:91`, `WRITEUP_PAPER.md:7`,
  `WRITEUP_NARRATIVE.md:7`).
- `.lycheeignore` adds `tree/v1.3.11` (chicken-and-egg per
  v1.2.13 + v1.3.2..v1.3.10 precedent).

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.10] — 2026-05-26 {#v1-3-10}

**Polish-audit second wave**: continues the independent polish-audit
work from v1.3.9 with the lower-priority items (visible polish,
deeper-dig deferred-to-v1.3.10 additions, and selective hiring-page
enhancements per Codex hiring-research). v1.3.9 covered material
correctness; v1.3.10 covers presentation polish + structured
additions.

**Audience signal expanded**: the hiring-manager page now indexes
the project's hiring-signal evidence (skills-to-evidence table) and
gives a structured 5-minute review path beyond the existing 60-second
scan. The two changes preserve the page's four-question structure;
the larger Codex hiring-expansion proposal (personal-contribution,
production-judgment, interview-prompts blocks) is intentionally
deferred — those would reposition the page from sidebar-scan to
hiring-evidence-packet, which is its own positioning decision and
out of scope for a polish patch.

Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033.

### Fixed

- **F8** `docs/for-hiring-managers.md:6` — removed duplicate
  "Four questions, ~60 seconds." body line. Quarto renders the
  frontmatter `description:` field under the H1, so this line was
  appearing twice in the rendered page.

### Changed

- **D2** `README.md:25` (§Executive summary) — frozen-probe AUROC
  framing strengthened: `stays above floor (AUROC 0.515)` →
  `stays *just* above floor (AUROC 0.515, 95% CI [0.505, 0.525] —
  lower bound clears 0.5 by only 0.005)`. The CI was already shown
  in WRITEUP_PAPER, WRITEUP_NARRATIVE, and RESULTS; the README
  executive line was the lone surface where the 0.005 lift above
  random floor wasn't surfaced. Now consistent.
- **D3** `_quarto.yml` — added a 5-line comment near line 71
  documenting the `model-rungs.md` `text:` override convention
  (only that one spoke carries an explicit override; the other 7
  have reader-friendly filenames whose H1-inferred label reads
  cleanly). Future-maintainer ergonomics.

### Added

- **S1** `WRITEUP.md` — appended a `## Looking for a specific
  section?` block with H3 redirects for all 7 v1.0.0-era anchors
  (`#reading-guide`, `#motivation` / `#1-motivation`,
  `#attack-type-taxonomy` / `#1-5-attack-type-taxonomy-traintest-composition` /
  `#attack-type-taxonomy-traintest-composition`, `#approach-overview` /
  `#2-approach-overview`, `#results`, `#lessons-brief` / `#lessons`,
  `#appendix` / `#12-appendix`). Each H3 catches one historical
  anchor and routes the reader at the current WRITEUP_PAPER /
  WRITEUP_NARRATIVE / WRITEUP/spoke / RESULTS equivalent. Closes the
  dead-anchor surface for `tree/v1.0.0`-era deep links (cover-letter
  bookmarks, etc.) without restoring the deprecated full WRITEUP.md.
- **S6** `CITATION.cff` — new file at repo root, CFF 1.2.0 schema,
  Standard + keywords (~38 lines). Enables GitHub's "Cite this
  repository" button and gives paper-citers usable metadata.
  Includes: title, authors, repository-code, url, license, version,
  date-released, type, abstract (sourced from README intro),
  keywords [prompt injection, machine learning, out-of-distribution,
  evaluation methodology, LLM security, distribution shift,
  reproducibility].
- **HM1** `docs/for-hiring-managers.md` — added skills-to-evidence
  table inline at end of §4 ("How the candidate thinks"). Maps 8
  hiring signals (evaluation design / negative-results honesty /
  methodology-before-results / confound control / reproducibility /
  library-first / multi-audience writing / audit-class
  self-discipline) to concrete repo evidence + inspection link.
  Preserves the existing four-question structure; integrates as an
  additional view of the same signals the §4 bullets already cover.
- **HM2** `docs/for-hiring-managers.md` — added new §5 "How to
  review this in 5 minutes" with a structured 5-step review path
  (this page → RESULTS → methodology-guarantees → reproducibility →
  limitations). Closes the "60-seconds-then-what" gap; the existing
  "If you want the deeper read..." paragraph stays as a longer-form
  follow-up.

### Updated

- Reader-surface `tree/v1.3.9` anchors advanced to `tree/v1.3.10`
  across 5 files (`index.qmd:79`, `README.md:222`,
  `READING_GUIDE.md:91`, `WRITEUP_PAPER.md:7`,
  `WRITEUP_NARRATIVE.md:7`).
- `.lycheeignore` adds `tree/v1.3.10` (chicken-and-egg per v1.2.13
  + v1.3.2..v1.3.9 precedent).

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.9] — 2026-05-26 {#v1-3-9}

**Independent polish-audit fix-forward**: ships correctness +
consistency fixes surfaced by an independent audit pass (Claude main
session + Codex polish-audit + Codex hiring-research). Two
material-correctness items in `WRITEUP_PAPER.md` (§7 Conclusion
value-binding swap; §3 Methods calibration figure reference); one
read-time staleness item in `docs/site-reader-map.md`; three stale
`Date:` fields; one DeBERTa-ablation wording precision item.

**Audit-discipline signal**: F1 (the TF-IDF/LoRA value-binding swap
in the paper conclusion) is the **same bug class** as the V1.3.1
ADR-080 historical case the project's own `audit_value_bindings`
validator was built to catch. The validator did flag F1 — but its
SOFT gate + the 2-tuple `(detector, metric)` schema's ~95%
false-positive rate on the current repo meant the warning hid in
noise. Concurrent with this release, upstream eval-toolkit issue
proposing a `(detector, metric, slice, expected_value)` schema
extension is filed (see `decisions/upstream_issues.md`).

**Gate severity**: no changes to audit-validator gates in v1.3.9.

Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033.

### Fixed

- **F1** `WRITEUP_PAPER.md:543–544` (§7 Conclusion): TF-IDF + LR
  direct-validation AUPRC corrected from `0.974` → `0.971`; LoRA
  binding added (`LoRA matches at 0.974`). Phrasing mirrors
  `README.md:24` for cross-doc consistency. Same bug class as
  V1.3.1 ADR-080. Verified: `audit_value_bindings` no longer
  reports the warning for this line.
- **F2** `WRITEUP_PAPER.md:253–254` (§3 Methods → Calibration):
  reliability-diagram figure reference corrected `F4` → `F5`
  (image link target `F4.svg` → `F5.svg`). Per `F4.meta.json` and
  `F5.meta.json` source artifacts: F4 = threshold-transfer
  (`evals/operating_points/dual_policy.parquet`); F5 = calibration
  (`evals/metrics/per_cell.parquet`). The same paper at line 385
  already correctly cited F5 for calibration; line 254 was the
  lone drift.
- **F3** `docs/site-reader-map.md:14`: WRITEUP_PAPER read-time
  estimate `~45 min` → `~20–25 min`; WRITEUP_NARRATIVE `~30 min`
  → `~15–20 min`. Aligns with README, `index.qmd`, and
  READING_GUIDE estimates (canonical times shrunk in v1.3.0
  restructure; this surface missed the update).
- **F6** `WRITEUP_PAPER.md:327–329` (§4.4 Context-window
  ablation): "Neither significantly differs" → "Neither materially
  differs ... in this run". The DeBERTa ablation paragraph
  displays three point estimates (0.291, 0.290, 0.293) without an
  inline CI / paired-bootstrap delta / significance test;
  "significantly" carried a formal-statistical connotation the
  paragraph did not back up. New wording preserves the practical
  conclusion (the three are within-noise of each other) without
  claiming an inline statistical test.

### Updated

- **D1** Three `Date: 2026-05-21` → `Date: 2026-05-26` fields:
  `index.qmd:4` (frontmatter), `WRITEUP_PAPER.md:6`,
  `WRITEUP_NARRATIVE.md:6`. Source mtimes + CHANGELOG `v1.3.8` +
  README submission anchors all date through 2026-05-26; the
  three reader-facing entry-point Date fields had drifted 5 days
  stale.
- Reader-surface `tree/v1.3.8` anchors advanced to `tree/v1.3.9`
  across 5 files (`index.qmd:79`, `README.md:222`,
  `READING_GUIDE.md:91`, `WRITEUP_PAPER.md:7`,
  `WRITEUP_NARRATIVE.md:7`).
- `.lycheeignore` adds `tree/v1.3.9` (chicken-and-egg per v1.2.13
  + v1.3.2..v1.3.8 precedent).

### Audit-driven (Batch F concurrent with v1.3.9 tag)

- **Filed upstream issue against `brandon-behring/eval-toolkit`**
  proposing `(detector, metric, slice, expected_value)` schema
  for `audit_value_bindings.BINDINGS`. The current 2-tuple
  `(detector, metric)` schema emits 96 warnings on this repo of
  which ~95+ are false positives — the validator cannot
  distinguish direct-validation AUPRC from pooled-OOD AUPRC,
  AUPRC from AUROC, point estimates from paired deltas, or
  detector values from random-floor values. **F1 hid in this
  noise**; the noise is the architectural blocker preventing
  SOFT→HARD gate promotion. v1.3.9 ships as the concrete repro
  case (with F1 fixed, the F1-class warning disappears; the 95+
  false-positive warnings persist until upstream lands the
  schema extension). See `decisions/upstream_issues.md` for the
  issue reference + sequencing.

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.8] — 2026-05-26 {#v1-3-8}

**Consumer adoption of upstream `eval_toolkit.audit_value_bindings`**:
ports the second member of the audit-validator family (closes
[eval-toolkit#71](https://github.com/brandon-behring/eval-toolkit/issues/71)).
Adds a new local CLI wrapper that catches the V1.3.1 ADR-080 bug class
— reader-prose pairing a detector name with the WRONG canonical value
(e.g., the historical V1.3.1 ADR-080 case: `WRITEUP_NARRATIVE.md:38`
said "TF-IDF + LR baseline reaches 0.974 AUPRC" when canonical
TF-IDF AUPRC = 0.971 and 0.974 was LoRA's value — both values exist
in the canonical table; the bug is the wrong pairing).

The existing `audit_numbers.py` + `audit_writeup_numbers.py` validate
VALUES against source data; this validator extends to validate
BINDINGS (the `(detector, metric, value)` triple itself).

Upstream pipeline summary: this project filed eval-toolkit#71 at v1.3.3
based on its own V1.3.1 ADR-080 audit findings; upstream shipped v1.0.3
on 2026-05-26 02:35Z as the second member of the audit-validator family
(after #73 / `audit_citation_alignment` at v1.0.1 / consumer v1.3.7).
The maintainer's #73→#71→#72 sequencing is being followed; #72
(`audit_sister_doc_concept_drift`) shipped upstream at v1.0.4 and will
be adopted at v1.3.9 per /exploring-options Q1 sequential-ladder lock.

**Gate severity**: SOFT at v1.3.8 (script always exits 0; CI uses
`continue-on-error: true`; pre-commit hook `stages: [manual]`). Promotes
to HARD bundled with `audit_citation_alignment` at a future v1.3.X
after observation window confirms validator output is signal-not-noise.

Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033.

### Added

- `scripts/audit_value_bindings.py` — NEW CLI wrapper around upstream
  `eval_toolkit.audit_value_bindings.validate_reader_value_bindings`.
  Carries a module-level `BINDINGS` dict (initial seed at v1.3.8: 2
  entries — `("TF-IDF", "AUPRC"): 0.971` + `("LoRA", "AUPRC"): 0.974`
  — the V1.3.1 ADR-080 motivating pair); `DETECTOR_ALIASES` +
  `METRIC_ALIASES` regex maps for surface-form matching (TF-IDF /
  TFIDF / "TF-IDF + LR" + variants for AUPRC); globs reader-facing
  surfaces (top-level `*.md`/`*.qmd` + `WRITEUP/*.md` + `docs/*.md`).
- `tests/scripts/test_audit_value_bindings.py` — **7 new tests**
  including a synthetic regression fixture for the V1.3.1 ADR-080 bug
  (asserts `validate_reader_value_bindings` flags the
  TF-IDF/0.974/AUPRC misbinding). Full test suite: **96 passed** (89
  baseline + 7 new).
- `.pre-commit-config.yaml` — new `audit-value-bindings` hook with
  `stages: [manual]` (SOFT — same pattern as v1.3.7's
  `audit-citation-alignment`).
- `.github/workflows/audit-writeup.yml` — new step inside the
  `audit-writeup-numbers` job with `continue-on-error: true`.
- `Makefile` — new `audit-value-bindings` target.

### Changed

- `pyproject.toml` — `eval-toolkit>=1.0.1,<2` → `>=1.0.3,<2`. Tightens
  lower bound to require the upstream release that ships
  `eval_toolkit.audit_value_bindings` (v1.0.3 minimum).
- `uv.lock` — `eval-toolkit==1.0.2` → `eval-toolkit==1.0.3` (latest in
  the new range; v1.0.4 not yet on PyPI at v1.3.8 cut time).
- `decisions/library_imports.md` — eval-toolkit row trajectory extended
  with `v1.0.2→v1.0.3 at v1.3.8 (consumed eval_toolkit.audit_value_bindings;
  flat-module per upstream ADR 0001; closes #71; second member of
  audit-validator family)`. `### Audit primitives` subsection extended
  with the new 4 consumed names (`validate_reader_value_bindings` +
  `Match` + `Violation` + `ValueBindingsReport`).
- `decisions/upstream_issues.md` — #71 row status updated from
  "awaiting upstream PR" to "RESOLVED in eval-toolkit v1.0.3; consumed
  at v1.3.8".

### Updated

- Reader-surface `tree/v1.3.7` anchors advanced to `tree/v1.3.8`
  across 5 files (`index.qmd`, `README.md`, `READING_GUIDE.md`,
  `WRITEUP_PAPER.md`, `WRITEUP_NARRATIVE.md`).
- `.lycheeignore` adds `tree/v1.3.8` (chicken-and-egg per v1.2.13 +
  v1.3.2..v1.3.7 precedent).

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.7] — 2026-05-25 {#v1-3-7}

**Consumer adoption of upstream `eval_toolkit.audit_citation_alignment`**:
ports the audit-script-gap follow-on (closes
[eval-toolkit#73](https://github.com/brandon-behring/eval-toolkit/issues/73)).
Adds a new local CLI wrapper that catches the v1.3.2 P1-2 bug class —
reader-facing markdown citing "per ADR-NNN" where the cited ADR's actual
subject category doesn't match the surrounding claim (e.g., the historical
v1.3.2 P1-2: `docs/REPRODUCIBILITY.md:76` cited ADR-029 = test_markers for
a reproducibility-tier-lock claim; actual reproducibility-tier ADR is
ADR-034).

Upstream pipeline summary: this project filed eval-toolkit#73 at v1.3.3
based on its own audit findings; upstream
[PR #74](https://github.com/brandon-behring/eval-toolkit/pull/74) merged
2026-05-25T22:51:15Z (commit `3820b9b`); pre-merge restructured to flat
module per upstream ADR 0001 ("stay flat through v1.x") — final import is
`from eval_toolkit.audit_citation_alignment import validate_citations`
(also re-exported at top level per Tier 1 STRICT `_EXPORTS`). v1.0.1 +
v1.0.2 both ship the module (identical blob hash; v1.0.2 adds #76 cleanup
batch).

**Gate severity**: SOFT at v1.3.7 (script always exits 0; CI uses
`continue-on-error: true`; pre-commit hook stages=[manual]). Promotes to
HARD at v1.3.8 after an observation window confirms the validator output
is signal-not-noise.

Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033.

### Added

- `scripts/audit_citation_alignment.py` — NEW CLI wrapper around upstream
  `eval_toolkit.audit_citation_alignment.validate_citations`. Carries a
  module-level `CATEGORY_KEYWORDS` dict (11 seed categories:
  `reproducibility`, `test_markers`, `cost`, `calibration`,
  `contamination`, `threshold`, `leakage`, `data`, `training`,
  `evaluation`, `reading_guide`); walks `decisions/ADR-*.md` parsing
  frontmatter (`title:` + `slug:`) into `ADRSubject` records; globs
  reader-facing surfaces (top-level `*.md`/`*.qmd` + `WRITEUP/*.md` +
  `docs/*.md`).
- `tests/scripts/test_audit_citation_alignment.py` — **8 new tests**
  including a synthetic regression fixture for the v1.3.2 P1-2 bug
  (ADR-029/test_markers cited for reproducibility-tier-lock claim;
  asserts `validate_citations` flags it). Full test suite: **89 passed**
  (81 baseline + 8 new).
- `.pre-commit-config.yaml` — new `audit-citation-alignment` hook with
  `stages: [manual]` (SOFT — doesn't run on commit; invokable via
  `pre-commit run --hook-stage manual audit-citation-alignment`).
- `.github/workflows/audit-writeup.yml` — new step inside the
  `audit-writeup-numbers` job with `continue-on-error: true` (SOFT —
  step always shows in CI logs; never blocks merges).
- `Makefile` — new `audit-citation-alignment` target for local invocation
  (`make audit-citation-alignment`).

### Changed

- `pyproject.toml` — `eval-toolkit>=1.0,<2` → `>=1.0.1,<2`. Tightens
  lower bound to require the upstream release that ships
  `eval_toolkit.audit_citation_alignment` (v1.0.1 minimum; prevents
  fresh installs from accidentally resolving to v1.0.0 which predates
  the module).
- `uv.lock` — `eval-toolkit==1.0.0` → `eval-toolkit==1.0.2` (latest in
  the `>=1.0.1,<2` range; v1.0.2 adds #76 cleanup batch + same audit
  module).
- `decisions/library_imports.md` — eval-toolkit row trajectory extended
  with `v1.0→v1.0.1→v1.0.2 at v1.3.7 (consumed
  eval_toolkit.audit_citation_alignment; flat-module per upstream ADR
  0001; closes #73)`. New `### Audit primitives` subsection under
  `## eval-toolkit imports` documents the 4 consumed names
  (`validate_citations` + `ADRSubject` + `CitationMisalignment` +
  `extract_adr_subject_category`) + their consumer glue at
  `scripts/audit_citation_alignment.py`.
- `decisions/upstream_issues.md` — #73 row status updated from "PR #74
  ready-for-review 2026-05-25 per v1.3.6 close" to "RESOLVED in
  eval-toolkit v1.0.1; consumed at v1.3.7". Captures the pre-merge
  flat-module restructure per upstream ADR 0001.

### Updated

- Reader-surface `tree/v1.3.6` anchors advanced to `tree/v1.3.7`
  across 5 files (`index.qmd`, `README.md`, `READING_GUIDE.md`,
  `WRITEUP_PAPER.md`, `WRITEUP_NARRATIVE.md`).
- `.lycheeignore` adds `tree/v1.3.7` (chicken-and-egg per v1.2.13 +
  v1.3.2/3/4/5/6 precedent).

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.6] — 2026-05-25 {#v1-3-6}

**eval-toolkit v1.0 stability-contract opt-in patch**: bumps the
eval-toolkit pin from `>=0.50.0,<2` to `>=1.0,<2`. Upstream v1.0.0
shipped 2026-05-25 17:02 GMT as a stability-contract activation per
upstream ADR 0003 — v1.0 is bit-equivalent to v0.51 codewise (Round 8
+ Round 9 + Round 10 multi-LLM audit rectification batch), but the new
thing at v1.0 is that **Tier 1 STRICT public-API signatures** captured
in `tests/golden/public_api/snapshot.json` become load-bearing —
breaking changes after v1.0 require a v2.0 major bump. The 9 strict
Tier-2 Protocols (`Scorer` + `LeakageCheck` + `Splitter` +
`ThresholdSelector` + `DatasetLoader` + `MetricSpec` + `MetaLearner` +
`Probe` + `TextTransform`) + 1 opt-in (`Versioned`) have method shapes
frozen.

This consumer release is the post-v1.0 production-evidence anchor for
the "real consumer in production" v1.0 gate. Reviewer URL pin
`tree/v1.0.0` unchanged per ADR-033.

### Changed

- `pyproject.toml` — `eval-toolkit>=0.50.0,<2` → `>=1.0,<2`
  (commit `ce64e47` on the original `chore/bump-eval-toolkit-v1.0`
  branch, preserved as the first commit on `release/v1.3.6` after the
  branch was renamed to match the v1.3.X release/* convention).
- `uv.lock` — regenerated against PyPI for `eval-toolkit==1.0.0`
  (new sdist + wheel hashes).
- `decisions/library_imports.md` — eval-toolkit ledger row refreshed
  v0.47 → v0.49 → v0.50 → v1.0 (was stale at v0.47; missed both the
  v0.50 bump at v1.3.5 and the v1.0 bump at v1.3.6). Specifier column
  updated to `eval-toolkit>=1.0,<2` to reflect the actual range-pin form.

### Verified

- **Consumer-side BREAKING-change exposure** — all 4 v0.51 BREAKING +
  1 deprecation evaluated against consumer callsites (v1.0 = v0.51
  codewise per upstream release notes); all 5 verdicts NOT AFFECTED:
  - `thresholds.recall_at_fpr(...)` fallback semantics — consumer has
    its own `compute_recall_at_fpr` at `src/eval/slice_analysis.py:111`;
    does NOT use upstream `thresholds.recall_at_fpr`.
  - `_rng.spawn_seed_sequences(rng, n)` respects Generator state — no
    callsites in consumer.
  - `harness.evaluate(..., rng=Generator)` bit-stable across `n_jobs` —
    no `harness.evaluate` callsites; bootstrap layer uses
    `paired_bootstrap_diff` directly (migrated to `rng=` at v1.3.5
    commit `da471d5`).
  - `SourceDisjointKFoldSplitter.iter_folds` caps at `min(k, n_sources)` —
    used at `src/data/splits.py:177` with `k=len(TRAIN_POSITIVE_SOURCES)=4`
    and `len(test_sources) == 1` asserted; `k == n_sources` always, so
    the new cap is a no-op.
  - `DeprecationWarning` on `evaluate_folded(seeds=[...])` without
    `reseed_splitter=` — no `evaluate_folded` callsites.
- **Empirical regression check**: `VIRTUAL_ENV=.venv make test` →
  81 passed, 38 skipped, 189 deselected, 2 warnings (parity with the
  v1.3.5 test count; no behavior regression from the v1.0 bump).
- **Upstream v1.0.1 forward-compat** — 6 items deferred to upstream
  v1.0.1 (issue [eval-toolkit#76](https://github.com/brandon-behring/eval-toolkit/issues/76))
  are all **Tier-2 ADDITIVE or Tier-3 FREE** per upstream ADR 0003;
  none affect this consumer (`SimilarityStrategy` not used; harness
  test hardening upstream-internal; `brier_score` + ECE docstring
  polish only; v0.51 doc-count reconciliation upstream-internal).

### Updated

- Reader-surface `tree/v1.3.5` anchors advanced to `tree/v1.3.6`
  across 5 files (`index.qmd:79`, `README.md:222`,
  `READING_GUIDE.md:91`, `WRITEUP_PAPER.md:7`,
  `WRITEUP_NARRATIVE.md:7`). Also reconciles the (2026-05-22/-21)
  inline dates on the 3 landing anchors to (2026-05-25) matching the
  v1.3.6 tag date — prior patches skipped this cleanup. WRITEUP
  `Date: 2026-05-21` refers to writeup-authoring date (not the live-
  site tag) and remains unchanged.
- `.lycheeignore` adds `tree/v1.3.6` (chicken-and-egg per v1.2.13 +
  v1.3.2/3/4/5 precedent).

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.5] — 2026-05-24 {#v1-3-5}

**Audit-script upstream-port readiness patch**: post-v1.3.4
eval-toolkit triage (2026-05-24 00:54 GMT) accepted the 3
audit-script-gap issues filed at v1.3.3 (#71/#72/#73) as
`enhancement,P3,tracked` post-v1.0 upstream work, with
recommended sequencing **#73 → #71 → #72**. v1.3.5 prepares
the local prototypes for upstream port by adding unit-test
coverage on the load-bearing primitive functions across all
6 `scripts/audit_*.py` and one small testability refactor.

Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033.

### Added

- `tests/scripts/` test package with one test file per audit script:
  - `test_audit_adr_count_claims.py` — 12 tests covering
    `actual_adr_count`, `should_skip`, `is_historical_snapshot`,
    `audit_file`. Seed for upstream `eval_toolkit.audit.citation_alignment`.
  - `test_audit_internal_anchors.py` — 13 tests covering
    `heading_to_anchor` (Pandoc/Quarto auto-identifier slug),
    `collect_anchors_for_file`, `collect_links_from_file`.
  - `test_audit_superseded_by_backlinks.py` — 14 tests covering
    `normalize_adr_id`, `parse_frontmatter`, `extract_id_list`.
  - `test_audit_rendered_site.py` — 13 tests covering
    `is_external_or_fragment`, `_plain_text_from_html`,
    `expected_html_paths`.
  - `test_audit_writeup_numbers.py` — 11 tests covering
    `scan_adr_slugs`, `scan_url_slugs`, `scan_version_strings`,
    `format_drift_report`.
  - `test_audit_numbers.py` — 4 tests covering the `Check`
    dataclass + tolerance semantics. (Most of `audit_numbers.py`'s
    primitives are I/O-bound; integration coverage stays in
    `tests/smoke/test_audit_smoke.py`.)
- **67 new unit tests** total. All marked `@pytest.mark.unit`;
  deterministic; no network or GPU.

### Changed

- `scripts/audit_adr_count_claims.py::audit_file` — added optional
  `repo_root: Path | None = None` parameter so tests can use
  synthetic `tmp_path` fixtures. Production behavior unchanged
  (defaults to module-level `REPO_ROOT`). NumPy-style docstring.
  Path-outside-base case now returns the absolute path as the
  display name instead of raising `ValueError`.

### Verified

- **Behavior regression diff**: pre-refactor + post-refactor stdout
  of all 6 audit scripts captured side-by-side; **0 diff lines**
  across all 6 scripts. The CLI contract is unchanged.
- **Pre-commit + CI** hooks continue to pass on the refactored
  state (audit-suite invocations are CLI-level + behavior-preserved).

### Updated

- Reader-surface `tree/v1.3.4` anchors advanced to `tree/v1.3.5`
  across `index.qmd`, `README.md`, `READING_GUIDE.md`,
  `WRITEUP_PAPER.md`, `WRITEUP_NARRATIVE.md`.
- `.lycheeignore` adds `tree/v1.3.5` (chicken-and-egg per v1.3.4
  precedent).

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.4] — 2026-05-22 {#v1-3-4}

**Visual-audit polish patch**: post-v1.3.3 visual audit
(`.scratch/VISUAL_AUDIT_CLAUDE_2026-05-22_post_v1_3_3.md`) surfaced
4 ADR-contract deviations the v1.3.2/v1.3.3 cascade missed. All 4
classified as defects via /exploring-options improvement-check.
v1.3.4 closes all 4. Reviewer URL pin `tree/v1.0.0` unchanged per
ADR-033.

### Fixed

- **§3.A Duplicate H1 sweep** — Quarto renders both the frontmatter
  `title:` field (as a styled title-block H1) AND the body `# Heading`
  line (a second H1) on the live site. v1.3.2 P3-NEW fixed only
  `index.qmd`. v1.3.4 extends the fix to 14 reader-facing pages
  with the same pattern:
  `RESULTS.md`, `WRITEUP_PAPER.md`, `WRITEUP_NARRATIVE.md`,
  `WRITEUP.md`, `READING_GUIDE.md`, `docs/for-hiring-managers.md`,
  and all 8 `WRITEUP/*.md` spokes (data-decisions / eval-design /
  limitations-and-future-work / methodology-guarantees / model-rungs /
  reference-scorer-audit / reproducibility / threshold-policy).
  Single canonical H1 per page after fix; cleaner DOM; better
  a11y / SEO. ADR pages NOT touched — the inner `# ADR-NNN: title`
  body H1 is part of the Michael Nygard convention and serves a
  distinct reader role (canonical ADR-NNN short form vs the verbose
  frontmatter title).
- **§3.B Mobile inline-`<code>` overflow** — `styles.css` mobile
  `@media (max-width: 480px)` block previously targeted only
  `table code, td code, th code` (v1.3.2 P3-2). v1.3.4 extends to
  all `<code>` and `pre code`. Fixes the 136px overflow on
  `WRITEUP/reproducibility.html` (long Python identifiers like
  `AutoModelForSequenceClassification.from_pretrained` + parquet
  paths in prose paragraphs) and any sibling spokes with similar
  inline-code-in-prose patterns.
- **§3.C GitHub repo "About" section** — populated via
  `gh repo edit` post-merge: description + homepage URL (live site) +
  6 topic tags (prompt-injection, evaluation, out-of-distribution,
  modernbert, spec-driven-development, methodology). Improves
  first-touch presentation for visitors landing on GitHub instead
  of the live site.
- **§3.D Missing GH Release objects** — backfilled `gh release create
  v1.3.0` and `gh release create v1.3.1` (both lacked release objects
  despite having tags; ADR-033 §release-flow pattern requires
  `gh release create` per tag with reader-facing content).
  v1.3.0 = 2-guide reader architecture restructure;
  v1.3.1 = audit fix-forward.

### Updated

- Reader-surface `tree/v1.3.3` anchors advanced to `tree/v1.3.4`
  across `index.qmd`, `README.md`, `READING_GUIDE.md`,
  `WRITEUP_PAPER.md`, `WRITEUP_NARRATIVE.md`.
- `.lycheeignore` adds `tree/v1.3.4` (chicken-and-egg per v1.2.13 +
  v1.3.2 + v1.3.3 precedent).

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.3] — 2026-05-22 {#v1-3-3}

**Library-first follow-up tag**: discharges the v1.3.2 locked
follow-up — file the 3 audit-script-gap proposals as upstream issues
against `brandon-behring/eval-toolkit` per the
[library-first invariant](CLAUDE.md). No project-side code change.
Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033.

### Added

- **eval-toolkit [#71](https://github.com/brandon-behring/eval-toolkit/issues/71)** — `audit.reader_value_bindings`: validate detector→value bindings in reader-prose Markdown. Test case from the v1.3.2 audit cycle: the WRITEUP_NARRATIVE Act 0 P1-1 bug where canonical AUPRC value 0.974 was bound to TF-IDF instead of LoRA. Existing `audit_numbers.py` validates source-of-truth values but not reader-prose binding correctness.
- **eval-toolkit [#72](https://github.com/brandon-behring/eval-toolkit/issues/72)** — `audit.sister_doc_concept_drift`: detect cross-doc semantic drift across linked sister docs. Test case: the v1.3.2 P1-2 contradiction where `docs/REPRODUCIBILITY.md` said `T1 = full cloud rerun ($28)` while linked sister `WRITEUP/reproducibility.md` said `T1 = laptop smoke ($0)`. Embedding-similarity clustering proposal.
- **eval-toolkit [#73](https://github.com/brandon-behring/eval-toolkit/issues/73)** — `audit.adr_citation_alignment`: validate "per ADR-NNN" citations match the cited ADR's actual subject. Test case: the v1.3.2 P1-2 defects where `docs/REPRODUCIBILITY.md:76` cited ADR-029 (test markers) for tier-lock + `:88` cited ADR-039 (integration gates) for cost. Frontmatter-driven category map proposal.

### Updated

- `decisions/upstream_issues.md` — 3 new ledger rows recording the
  filings at #71, #72, #73.
- Reader-surface `tree/v1.3.2` anchors advanced to `tree/v1.3.3`
  across `index.qmd`, `README.md`, `READING_GUIDE.md`,
  `WRITEUP_PAPER.md`, `WRITEUP_NARRATIVE.md`.
- `.lycheeignore` adds `tree/v1.3.3` (chicken-and-egg per v1.3.2 +
  v1.2.13 precedent).

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.2] — 2026-05-22 {#v1-3-2}

**Polish patch**: post-v1.3.1 multi-LLM audit cycle (Claude
self-audit + Gemini external audit + Codex external audit) surfaced
2 P1 + 4 P2 + 7 P3 reader-visible findings. v1.3.2 closes all of
them across ~12 logically-grouped commits on a single
`release/v1.3.2 → main` PR. Reviewer URL pin (`tree/v1.0.0`)
unchanged per ADR-033; no substantive content change.

### Fixed

- **P1-1 (Gemini)**: `WRITEUP_NARRATIVE.md` Act 0 (line 38) misstated
  TF-IDF + LR direct-validation AUPRC as 0.974 with a false "ties at
  0.974" claim. Canonical TF-IDF AUPRC is 0.971 per RESULTS.md table
  + `audit_numbers.py` expected values. Self-contradiction with same
  document's Act 3 (line 219) resolved. Fixed to "TF-IDF + logistic
  regression baseline reaches 0.971 AUPRC ... LoRA edges it out at
  0.974."
- **P1-2 (Codex + Claude proactive sweep)**: `docs/REPRODUCIBILITY.md`
  Reviewer reproduction tier section carried a 4-part defect:
  (1) "Two-tier reproduction" scheme contradicted T0/T1-smoke/T3-cloud
  on every active reviewer surface (README + READING_GUIDE +
  WRITEUP/reproducibility.md + index.qmd); (2) cited ADR-029 (test
  markers) for tier-lock — actual tier-lock ADR is ADR-034;
  (3) cited ~$28 cost — actual cost cap is $125 per ADR-020;
  (4) cited ADR-039 (integration gates) for cost envelope — actual
  cost ADR is ADR-020. All 4 parts rewritten to match the canonical
  contract.
- **P2-1 (Codex)**: ADR-078 + ADR-079 + ADR-060 bodies retained their
  pre-supersession prose per the ADR-073 immutability rule, but the
  rendered HTML didn't surface the supersession to direct-link
  readers. New Quarto Lua filter (`_extensions/superseded-banner/`)
  injects a `:::{.callout-warning}` banner at the top of any ADR
  whose frontmatter `superseded_by:` is non-empty. Source ADR files
  remain immutable; banner appears in rendered HTML only. Per
  /exploring-options 2026-05-22 Q1 lock (A1 + F1).
- **P2-2 (Claude self-audit)**: Reader-surface `tree/v1.3.0` anchors
  on `index.qmd:81`, `README.md:222`, `READING_GUIDE.md:93`,
  `WRITEUP_PAPER.md:9`, `WRITEUP_NARRATIVE.md:9` advanced to
  `tree/v1.3.2` + dates `2026-05-21` → `2026-05-22`. Live deploy
  state now matches the self-reported state.
- **P2-3 (Claude self-audit)**: 10 dead intra-site anchors closed.
  Root cause for the 5 CHANGELOG self-anchor failures investigated
  (per I1 lock — render `_site/CHANGELOG.html` locally + inspect
  Quarto's actual auto-anchor IDs): Pandoc's auto-identifier
  algorithm strips `## [1.2.7] — 2026-05-19` to an empty slug, so
  Quarto fell back to positional anchors `#section-N` that shift
  whenever a new version section lands. Fix: added explicit
  `{#v1-X-Y}` IDs to all 34 CHANGELOG version headings (mechanical
  sweep + future-proofing). Other 5 fixes: `docs/GLOSSARY.md` ×2
  (em-dash + slash double-dash → single-dash);
  `WRITEUP/limitations-and-future-work.md:27` (em-dash); `CHANGELOG`
  `WRITEUP.md#results` → `RESULTS.md` (router stub has no #results);
  `NEXT_STEPS.md:84` (backtick-protected markdown-link-syntax example
  was parsed by the audit script's regex as a real link — rephrased
  the prose to avoid the false-positive without needing a script
  change).
- **P2-NEW (Codex + Claude narrowing)**: 3 `docs/` files leaked
  stale Phase 0 `[OPEN]` / "Decision needed" tokens onto the live
  site even though Phase 0 closed at v1.0.0. Resolved each to
  `[LOCKED: X (per ADR-NNN)]`: `docs/MISSION.md:31,38` (metric
  targets + non-goals); `docs/MANIFEST_SCHEMA.md:14` (schema v3 per
  ADR-057); `docs/TECH_STACK.md:27-29` (GPU class + secrets + cache
  per ADR-020 + ADR-035 + ADR-016 + ADR-026). `docs/ROADMAP.md` was
  flagged by Codex but on review is meta-process documentation of
  the SDD Phase 0 workflow itself (not a defect); scope narrowed
  to 3 files.
- **P3-1 (Claude self-audit)**: Reading-time claims `~45 min` /
  `~30 min` were 2–3× over-stated. Calibration: WRITEUP_PAPER
  3877 words / 175 wpm = 22 min; WRITEUP_NARRATIVE 3730 words /
  175 wpm = 21 min. Old claims implied 86 wpm / 124 wpm (slow).
  Lowered to `~20–25 min` / `~15–20 min` across 6 reader surfaces
  (`index.qmd`, `README.md` ×4, `READING_GUIDE.md` ×3,
  `WRITEUP.md`, `docs/for-hiring-managers.md`).
- **P3-2 (Codex)**: `styles.css` mobile word-break — table cells
  containing long `<code>` tokens (e.g., parquet filepaths in
  RESULTS §7 Raw Artifacts) forced 79px horizontal viewport
  overflow at 375px-wide screens. Added `@media (max-width: 480px)`
  block applying `overflow-wrap: anywhere; word-break: break-all;
  white-space: normal` to `table code, td code, th code`.
- **P3-3 (Claude self-audit) — ADR-081 narrow-relaxation**:
  `decisions/ADR-060` frontmatter `status:` field carried non-Nygard
  verbose context (`status: Accepted (methodology lock —
  infrastructure landed; ...)`. Wrote ADR-081 authorizing a sixth
  frontmatter-backfill narrow-relaxation axis: split `status:` into
  pure-Nygard `status: Accepted` + new `lifecycle-note:` field.
  Extends ADR-072 / ADR-076 / ADR-077 frontmatter-backfill chain.
  Applied to ADR-060; `decisions/README.md` schema docs updated to
  enumerate `lifecycle-note:` as OPTIONAL.
  `scripts/audit_superseded_by_backlinks.py` `CLOSING_COMMIT_EXEMPT`
  set extended to include ADR-081 (governance-backfill chicken-and-egg).
- **P3-4 (Claude self-audit)**: `decisions/audits/REPO_AUDIT_*.md`
  files moved from git-tracked to gitignored (matches transcripts/
  private-by-default pattern). Untracked 2 pre-v1.3.2 audit files
  via `git rm --cached`; `decisions/audits/README.md` (the
  convention doc) stays tracked.
- **P3-NEW (Codex)**: `index.qmd:2` frontmatter `title:` block +
  `index.qmd:8` body H1 both rendered as `<h1>` elements (Quarto
  produces a styled title block from the frontmatter `title:`,
  then renders any body H1 separately). Removed the redundant body
  H1; the Quarto-rendered title block is the canonical page heading.

### Added

- **ADR-081**: Authorizes the frontmatter `status:` field-split
  narrow-relaxation axis (sixth axis, extending the chain ADR-072 →
  ADR-076 → ADR-077). Applied as the seed case to ADR-060 in the
  same patch; documented in `decisions/README.md` schema.
- **Quarto Lua filter** at `_extensions/superseded-banner/` — reads
  ADR frontmatter `superseded_by:` and injects a callout-warning
  banner at the top of the rendered body. Source ADR files
  untouched. Wired into `_quarto.yml` `filters:` list.

### Audit-script gap recording (durable, 4-location)

The v1.3.2 audit cycle surfaced 3 audit-tool blind spots that the
existing `scripts/audit_*.py` ecosystem does not catch:

1. **Reader-prose detector→AUPRC binding** (catches Gemini P1):
   `audit_numbers.py` + `audit_writeup_numbers.py` validate
   canonical values against source data but not that every reader-
   prose sentence pairs the canonical detector name with its
   canonical value.
2. **Cross-doc concept-semantic drift** (catches Codex P1 Part 1):
   no script compares semantic claims about the same concept
   (e.g., T1 = full cloud rerun in one doc vs T1 = laptop smoke in
   another) across linked sister docs.
3. **ADR-citation alignment** (catches Codex P1 Part 2 + Claude
   sweep P1 Part 4): no script verifies that "per ADR-NNN"
   citations match the cited ADR's actual subject.

Durable records (per user "make sure they aren't forgotten"
directive, locked at 4 locations):
- `.scratch/audit_script_gaps_2026-05-22.md` (gitignored; full
  definitions + test cases + proposed APIs)
- `AUDIT_CLAUDE_2026-05-22.md §9` (inline pointer)
- Memory entry at `~/.claude/projects/.../memory/audit_script_gaps_2026-05-22.md`
  (long-term recall across Claude sessions)
- `.scratch/upstream_issue_drafts_2026-05-22.md` (3 ready-to-file
  `gh issue create` drafts for `brandon-behring/eval-toolkit` per
  library-first invariant)

### Cumulative ADR count

81 ADRs accepted across Phase 0-00 through ADR-081. Cascade hits the
same surfaces as v1.3.1's ADR-080 cascade: README, READING_GUIDE,
WRITEUP, WRITEUP_NARRATIVE, docs/for-hiring-managers,
WRITEUP/methodology-guarantees, CLAUDE.md. `SUBMISSION_AUDIT.md`
regenerates via `scripts/regenerate_audit.py` (81 CLAIM rows).
`audit_adr_count_claims.py` invariant fires correctly on its
7th consecutive ADR-add.

### Co-Authored-By

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>

## [1.3.1] — 2026-05-22 {#v1-3-1}

**Audit fix-forward**: post-v1.3.0 fresh-eyes audit of the live
GH-Pages deployment surfaced 7+ factual / stale-reference / polish
defects. Each fix verified via independent re-derivation from
`evals/*.parquet` source-of-truth (Q2 lock: "go back to the original
resources and redo any calculation that can be independently
re-examined; do not take any written record for granted"). Plus a
new release-gate invariant (`scripts/audit_numbers.py`) to catch the
cross-guide numeric-divergence class going forward.

**Summary of the 5 sub-PRs landed into `release/v1.3.1`** (each
sub-PR section below documents its detailed fix list):

- **PR-1**: ADR-080 axis-only supersession of ADR-078 + ADR-079 on
  reviewer-URL-pin numeric axis (`tree/v1.2.8` → `tree/v1.0.0` per
  ADR-033). ADR count cascade 79 → 80 across 7 reader-facing
  surfaces.
- **PR-2**: Class-A factual + numeric fixes (PAPER §4.6 frozen-probe
  FPR 0.6% → 1.0%; PAPER §3.3 BIPIA n=56 → n=50, InjecAgent n=56 →
  n=62; F4 → F5 figure-label fix in PAPER §4.7 + NARRATIVE Finding 7;
  NARRATIVE Act 4 "Six more findings" → "Four more findings" + Act 3
  explicit Findings 1-3; NARRATIVE Finding 4 §-numbering leak fix;
  GLOSSARY rung/detector clarifier overcount + drop LLM judges;
  READING_GUIDE result-map Finding 2 row added). Includes
  `scripts/audit_numbers.py` invariant + pre-commit hook.
- **PR-3**: Class-B 3-tier mixed-by-purpose retargeting of 22+ stale
  "WRITEUP-as-hub" references across 8 WRITEUP/ spokes + 3 non-spoke
  surfaces (RESULTS.md, site-reader-map.md, for-hiring-managers.md).
- **PR-4**: Class-C/D polish (limitations §11 → §10 numbering gap
  closure; "v6" → "successor iteration"; Quarto frontmatter added to
  6 spokes missing it). Plus `scripts/audit_internal_anchors.py`
  intra-site dead-anchor detector (manual-run; Q8 lychee-in-pre-commit
  deferred to v1.3.2 candidate).
- **PR-5**: Q6 README chooser clarity (above-fold pointer + H2
  rename "Read the site" → "Pick a guide for the full methodology" +
  end-of-Executive-Summary chooser transition).

**Governance**: ADR-080 (NEW; axis-only supersession of ADR-078 +
ADR-079 on the reviewer-URL-pin numeric axis). 80 ADRs total at
v1.3.1 close. Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033.

**Preventive guardrails**: `scripts/audit_numbers.py` (release-gate
invariant; pre-commit hook; 23 numeric checks against `evals/*.parquet`)
+ `scripts/audit_internal_anchors.py` (manual-run intra-site anchor
resolver).

**Decision trail**: see `~/.claude/plans/i-want-to-audit-abundant-meerkat.md`
for the 9-question /exploring-options walk-through (Q1 ADR-fix path;
Q2 re-derivation discipline; Q3 NARRATIVE findings-count alignment;
Q4 3-tier retargeting; Q5 frontmatter polish scope; Q6 README chooser
clarity; Q7 sub-PR strategy; Q8 preventive guardrails; Q9 numbering +
v6 polish). Transcript: `transcripts/2026-05-22__v1-3-1-audit-fix.md`
(gitignored; `/save-transcript` will land post-tag).

---

### v1.3.1 sub-PR-5 — README chooser clarity (Q6 A+B+C)

**Defect**: Live README chooser was present but discoverability was
poor. A GitHub-arriving reader (who doesn't see the Quarto sidebar)
sees: title → 1-sentence framing → Executive Summary (multi-screen:
OOD table + mechanism + direct-detection tables) → "Read the site"
header. The chooser was several scrolls below the fold; the label
"Read the site" didn't telegraph that this is where you pick between
PAPER and NARRATIVE. By the time many readers reached the chooser,
they'd decided they'd gotten what they came for.

**Fix (Q6 lock A+B+C)**:

- **A. Above-the-fold pointer**: inserted a 1-line pointer immediately
  after the badges + 1-sentence framing, before `## Executive
  summary`. Names both guides with their length estimates:
  > Pick a guide for the full methodology — both cover the same
  > content: WRITEUP_PAPER.md (academic IMRAD, ~45 min) or
  > WRITEUP_NARRATIVE.md (narrative arc, ~30 min). The executive
  > summary below is the 1-page distillation; pick a guide for the
  > full read.
- **B. Renamed H2 "Read the site" → "Pick a guide for the full
  methodology"**: telegraphs reader-intent + matches `index.qmd`'s
  "Pick your reading style" H2 label. Aligns the two entry surfaces
  (README + index) on chooser-prominence framing.
- **C. End-of-Executive-Summary chooser transition**: added an inline
  transition at the close of the Executive Summary section:
  > → Continue with the academic paper (~45 min) or the narrative
  > (~30 min). Both cover the same methodology, findings, and
  > limitations in different reading styles.
  Provides a second discovery point for readers who scrolled through
  the exec-summary.

(D considered but rejected): Reorder chooser items to put the 60-sec
tour first. Rejected because current depth-first ordering matches the
academic-reviewer-first prioritization per ADR-004, and the 60-second
tour is already discoverable from the navbar Reference dropdown +
index.qmd's chooser.

### v1.3.1 sub-PR-4 — Class-C/D polish + scripts/audit_internal_anchors.py + anchor-link cleanup

**Polish (Q5 + Q9 locks)**:

- **Quarto frontmatter added to 6 spokes** that were missing it: data-decisions,
  eval-design, limitations-and-future-work, methodology-guarantees,
  reference-scorer-audit, threshold-policy. Pattern from `model-rungs.md` +
  `reproducibility.md` (the 2 spokes that had it already). Pre-fix: browser
  tab titles rendered as slug (`data-decisions – ...`); post-fix: proper
  title (`Data decisions – ...`). SEO + tab labels + bookmark titles improve.
- **`WRITEUP/limitations-and-future-work.md §11 → §10 renumber** closes the
  §10 gap (8.1, 8.2, 9.1-9.5, then jumped to §11; now flows 8.1 → 8.2 →
  9.1-9.5 → §10).
- **`WRITEUP/limitations-and-future-work.md` "v6" → "a successor iteration"**
  (4 occurrences): §9.4 header + 3 body references. "v6" was anomalous in a
  v1.x project (likely stale early-draft language); replaced with
  style-neutral wording that doesn't bind to a specific version.

**Anchor-link cleanup (post-PR-3 follow-up)**:

PR-3's spoke-retargeting introduced anchors of the form `#43-trained-...`
+ `#46-validation-...` + `#1-cross-family-ood-table-auprc` etc. (carrying
the leading section-number prefix). Quarto's auto-identifier algorithm
strips numeric prefixes — actual anchors are `#trained-...`,
`#validation-...`, `#cross-family-ood-table-auprc`. Batched all
PR-3-introduced anchors to the prefix-stripped form. Verified via the
new `scripts/audit_internal_anchors.py` (re-runs clean after the fix).

**Preventive guardrail (partial Q8 — see follow-up)**:

- `scripts/audit_internal_anchors.py` — markdown-only intra-site anchor
  resolver. Catches dead anchors of the form `[link](./RESULTS.md)`
  where the target file has no `results` anchor. The exact failure class
  Lane-3 surfaced (`WRITEUP.html#results` dead anchor). Manual-run for now.
- **Q8 lychee-in-pre-commit deferred**: lychee binary not installed
  locally + audit_internal_anchors surfaces 9 pre-existing dead anchors
  (CHANGELOG self-references to numbered headings + GLOSSARY self-references
  with em-dash slug-mismatch). These pre-date this audit. Fix-up patch
  v1.3.2 candidate; deferred to keep v1.3.1 scope tight to "audit
  fix-forward". CI lychee continues to catch these post-tag.

### v1.3.1 sub-PR-3 — Class-B stale "WRITEUP-as-hub" retargeting (3-tier rule per Q4 lock)

**Defect**: 22+ references across 8 `WRITEUP/*.md` spokes + 3 non-spoke
surfaces described WRITEUP.md as "the hub" with "cover narrative" and
linked to `WRITEUP.md §Results` — but post-v1.3.0 (per ADR-079)
WRITEUP.md is a 1-page router with no §Results, no §6, no cover
narrative. Live-verified that `WRITEUP.html#results` is a dead anchor
(`document.getElementById('results') === null`); every spoke click on
"see WRITEUP §Results" was landing on a router page with nothing to
read.

**Fix** (3-tier mixed-by-purpose retargeting per Q4 lock):

- **Tier 1 — Spoke headers (8 of 8)**: Replaced "*Part of the WRITEUP
  methodology — see the hub for the cover narrative + reading guide.*"
  with "*Deep-dive reference for the methodology in WRITEUP_PAPER.md
  (academic) and WRITEUP_NARRATIVE.md (narrative). Pick a guide for
  the cover narrative; this spoke goes deeper.*"
- **Tier 2 — Body inline "WRITEUP §X" references**: retargeted per
  reader-intent — "headline finding" → WRITEUP_PAPER §4.3 + NARRATIVE
  Act 3; "headline results" tables → RESULTS §1; "WRITEUP §6 +
  Methodology caveats" → WRITEUP_PAPER §6 Limitations; "WRITEUP §7.5
  val→test transfer" (legacy hybrid-section numbering) → RESULTS §4
  + WRITEUP_PAPER §4.6 / NARRATIVE Finding 6; "WRITEUP §Results
  §Frozen probe vs adapter fine-tuned" → RESULTS §2.
- **Tier 3 — Spoke Cross-References sections (8 of 8)**: each
  "Headline results → WRITEUP §Results" line became a two-link
  pattern: "**Headline results (interpretation)**: WRITEUP_PAPER §4
  (academic) or WRITEUP_NARRATIVE Act 3 (narrative); **Headline
  tables (data)**: RESULTS §1".
- **Non-spoke surfaces**: `RESULTS.md` line 310, `docs/site-reader-map.md`
  line 14, `docs/for-hiring-managers.md` line 96 all updated to point
  at WRITEUP_PAPER + WRITEUP_NARRATIVE instead of describing WRITEUP.md
  as the hub.

**Net effect**: every click lands at the right depth; register-matched
(academic spoke → PAPER for prose; data link → RESULTS); both-guide
chooser preserved at spoke top + bottom only (not redundantly inline).
The only remaining `WRITEUP.md` references are intentional router-page
labels ("1-page router", "Writeup chooser").

### v1.3.1 sub-PR-2 — Class-A factual + numeric fixes + scripts/audit_numbers.py invariant

**Defects** (surfaced by 2026-05-22 fresh-eyes audit; verified by
independent re-derivation from `evals/*.parquet` per `/exploring-options`
Q2 lock — "go back to the original resources and redo any calculation
that can be independently re-examined; do not take any written record
for granted"):

1. **`WRITEUP_PAPER.md` §4.6 frozen-probe Mean test FPR cited as 0.6%.**
   Actual value: 1.0% (re-derived as 1.028% mean across 12 (fold, seed)
   cells from `evals/operating_points/dual_policy.parquet`, rung
   `frozen_probe`, policy `detection`). Fixed to **1.0%**.
   Cross-checked: `WRITEUP_NARRATIVE.md` Finding 6 said "Frozen probe
   holds the 1% target" (correct); `RESULTS.md` §4 says Test FPR 0.010
   (correct). Only PAPER §4.6 was wrong; cross-guide consistency
   restored.
2. **`WRITEUP_PAPER.md` §3.3 evaluation slate table cited BIPIA n=56 +
   InjecAgent n=56.** Actual per-slice positive counts (from
   `evals/predictions/*__bipia.parquet` + `*__injecagent.parquet` row
   counts): BIPIA n=**50**, InjecAgent n=**62**. Total 112 (unchanged;
   matches pooled OOD positive arithmetic). Cross-checked:
   `WRITEUP/limitations-and-future-work.md` §8.1 said `BIPIA n=50,
   InjecAgent n=62` (correct). Only PAPER §3.3 was wrong; fixed.
3. **F4/F5 figure-label inversion.** PAPER §4.7 + NARRATIVE Finding 7
   both linked `Figure F4` for reliability diagrams. Per
   `docs/plots/F4.meta.json` source = `dual_policy.parquet`, F4 is the
   **threshold-transfer** figure; per `docs/plots/F5.meta.json` source
   = `per_cell.parquet`, F5 is the **calibration** figure. RESULTS.md
   uses both correctly (F4 caption: "Detection-threshold transfer"; F5
   caption: "Calibration comparison"). Fixed PAPER + NARRATIVE links
   to F5.
4. **`WRITEUP_NARRATIVE.md` Act 4 intro asserted "Six more findings"**
   but enumerated only Finding 4..7 (4 findings). Cross-guide finding
   parity with PAPER's 7 equal-weight findings (§4.1-4.7) restored by
   the Q3 hybrid lock: NARRATIVE Act 3 now names Findings 1 (direct
   detection learned), 2 (OOD wall is cross-family), 3 (anti-correlation
   headline) explicitly via short anchored sub-section headers; Act 4
   intro reworded to "Four more findings". 7-finding parity preserved.
5. **`WRITEUP_NARRATIVE.md` Finding 4 referenced "§4.1"** — PAPER's
   §-numbered anchor convention leaking into a narrative-arc document
   with no §4.1. Rephrased to NARRATIVE-native: "the ModernBERT advantage
   we saw on the in-pool direct-detection task (Act 3's strong
   validation numbers)".
6. **`docs/GLOSSARY.md` rung/detector clarifier overcounted** by
   listing "5 evaluated approaches" then enumerating 7 items including
   the dropped LLM-judge tier (dropped at ADR-050; never in the
   headline ladder). Rewritten to 5 ladder rungs explicitly + a note
   on the dropped LLM-judge tier.
7. **`READING_GUIDE.md` result map silently omitted PAPER §4.2** (the
   OOD wall is cross-family, not source-level — Finding 2). Added an
   explicit row mapping Finding 2 → PAPER §4.2 / NARRATIVE Act 3
   Finding 2 / WRITEUP/eval-design §5.5.

**Preventive guardrail**: `scripts/audit_numbers.py` lands as a
release-gate invariant (per Q8 lock). Re-derives every reader-visible
number from `evals/*.parquet` source-of-truth + diffs against extracted
writeup numbers; exits non-zero on drift. Hooked into pre-commit;
output to `evals/audit/numeric_audit.json`. 23 checks pass on this
commit (catches the exact defect-class that surfaced this audit).

### v1.3.1 sub-PR-1 — ADR-080 reviewer-URL-pin numeric correction (axis-only supersession of ADR-078 + ADR-079)

**Defect**: ADR-078 + ADR-079 + WRITEUP.md cited `tree/v1.2.8` as the
reviewer URL pin "per ADR-033", but ADR-033 canonically pins
`tree/v1.0.0` (never-drift discipline; CHANGELOG v1.3.0 confirmed).
ADR-078 even self-contradicted within a single paragraph
(line 163 `tree/v1.0.0`; line 164 `tree/v1.2.8`). Surfaced by the
2026-05-22 fresh-eyes audit of the live GH-Pages deployment.

**Fix**:

- **ADR-080** (`decisions/ADR-080-reviewer-url-pin-numeric-correction-adr-078-079.md`)
  — NEW; axis-only supersession of ADR-078 + ADR-079 on the
  reviewer-URL-pin numeric axis only. Bodies of ADR-078 + ADR-079
  unchanged per CLAUDE.md immutability; their `superseded_by:`
  frontmatter backfilled to `["080"]` per ADR-076 / ADR-077
  frontmatter-backfill narrow-relaxation discipline.
- **WRITEUP.md** — `tree/v1.2.8` → `tree/v1.0.0` (mutable file edit;
  cites ADR-080 for the correction trail).
- **ADR count cascade 79 → 80** across 7 reader-facing surfaces:
  README + WRITEUP + WRITEUP_NARRATIVE + READING_GUIDE +
  for-hiring-managers + WRITEUP/methodology-guarantees + CLAUDE.md.
  `scripts/audit_adr_count_claims.py` fires correctly for the 6th
  time across the v1.2.13 → v1.2.14 → v1.2.15 → v1.2.16 → v1.3.0 →
  v1.3.1 trail.
- **SUBMISSION_AUDIT.md** regenerated; CLAIM row count 79 → 80.

**Why axis-only supersession (not in-place narrow-relaxation)**:
the four CLAUDE.md narrow-relaxation classes (slug typo / broken
external ref / publisher-URL canonicalization / render-only Markdown)
cover surface defects only; the v1.2.8 claim IS the prose intent of
ADR-078 + ADR-079's Consequences sections (a factual claim about a
tag commitment). Correcting it is a meaningful claim change that
warrants supersession discipline, not in-place rewriting.

## [1.3.0] — 2026-05-22 {#v1-3-0}

**Two-guide reader architecture: WRITEUP_PAPER (academic IMRAD) +
WRITEUP_NARRATIVE (story arc) replacing the single-hybrid WRITEUP.md.**
First minor bump since v1.0.0. Substantial structural change; pure
presentation restructure (no methodology / model / data / compute
change). Governance: ADR-078 (EXECUTIVE_SUMMARY absorbed into README)
+ ADR-079 (two-guide architecture). Reviewer URL pin `tree/v1.0.0`
unchanged per ADR-033.

### Root cause for restructure

User feedback diagnosed the prior single-guide architecture as
"neither a narrative structure to quarto nor an academic structure
like in a journal paper — random parts of results all over the place
with no story". Two distinct failures: cross-page redundancy (same
content rendered 3-4 times across `index.qmd` + `EXECUTIVE_SUMMARY` +
`WRITEUP` + `RESULTS` with incidental drift); within-page register
inconsistency (`WRITEUP.md` mixed summary-style and detail-style;
methodology §9 placed AFTER findings §7; findings enumerated
academically but framed narratively). The diagnosis: enthusiastic-
explainer wearing an ill-fitting academic suit — coherent as neither.

### Added (4 sub-PRs into release/v1.3.0)

- **PR-1 (`76a0872`) — Foundation: README absorbs EXECUTIVE_SUMMARY + ADR-078.**
  - `README.md` restructured: top-fold §Executive summary section
    absorbs the 1-page distillation.
  - `EXECUTIVE_SUMMARY.md` DELETED (v1.0.0 reviewer-pin preserves
    historical access per ADR-033).
  - `_quarto.yml` navbar + sidebar updated.
  - `decisions/ADR-078-executive-summary-absorbed-into-readme.md`
    (NEW; ~200 lines) — supersedes ADR-053 dimension 2 on exec-
    summary axis only.

- **PR-2 (`97c179b`) — WRITEUP_PAPER.md (academic IMRAD; NEW; 656 lines).**
  Full IMRAD article: §0 Abstract / §1 Introduction / §2 Background /
  §3 Methods (4 subsections) / §4 Results (all 7 findings as equal-
  weight numbered subsections; Finding 3 = headline) / §5 Discussion
  (mechanism: lexical overfitting + label-relevance shift) / §6
  Limitations / §7 Conclusion / §8 References + in-paper Glossary.
  Formal academic voice.

- **PR-3 (`30de502`) — WRITEUP_NARRATIVE.md (narrative arc; NEW; 577 lines).**
  5-act story + epilogue: Act 0 Hook / Act 1 Setup / Act 2
  Investigation / Act 3 Revelation (headline as dramatic third-act
  reveal) / Act 4 The other findings (6 supporting findings as
  equal-weight enumeration) / Act 5 Implications / Epilogue.
  Plain-English first-person plural ('we') voice.

- **PR-4 (`c094218`) — WRITEUP stub + index chooser + READING_GUIDE 2-path router + ADR-079.**
  - `WRITEUP.md` rebuilt as 1-page stub-redirect router pointing at
    the two guides; preserves backward refs from 8 spokes + ADRs.
  - `index.qmd` rebuilt as 60-sec hook + 2-guide chooser.
  - `READING_GUIDE.md` rebuilt as 2-path router (5 reader paths).
  - `decisions/ADR-079-two-guide-reader-architecture.md` (NEW) —
    supersedes ADR-053 dim 1 + ADR-054 + ADR-061 on reading-guide
    axis only per narrow-relaxation discipline.

### Changed

- `scripts/audit_writeup_numbers.py` REVIEWER_FACING_FILES list:
  drops `EXECUTIVE_SUMMARY.md`; adds `WRITEUP_PAPER.md` +
  `WRITEUP_NARRATIVE.md`.
- ADR count cascade 78 → 79 across 5 reader-facing surfaces (5th
  correct firing of v1.2.14 `audit_adr_count_claims` invariant).
- `SUBMISSION_AUDIT.md` regenerated; CLAIM row count 78 → 79.

### Removed

- `EXECUTIVE_SUMMARY.md` (content absorbed into README per ADR-078).

### Governance

- **ADR-078**: EXECUTIVE_SUMMARY absorbed into README. Axis-only
  supersession of ADR-053 dimension 2.
- **ADR-079**: Two-guide reader architecture. Axis-only supersession
  of ADR-053 dim 1 + ADR-054 + ADR-061 on reading-guide axis.
- Both use axis-only narrow-relaxation pattern established in
  ADR-076/077 + v1.2.15 frontmatter-backfill precedent; supersession-
  backlink audit invariant correctly classifies as INFO not FAIL via
  axis-only comment heuristic.

### Audit-tool family fired correctly

- `audit_adr_count_claims.py` caught the 78→79 cascade — 5th correct
  firing across v1.2.13→14→15→16→1.3.0 trail.
- `audit_superseded_by_backlinks.py` caught initial axis-only-comment-
  regex mismatch on ADR-079; fix-during-development corrected pre-commit.
- `audit_writeup_numbers.py` caught EXECUTIVE_SUMMARY-removal cascade.

### Out of scope (deferred)

- 8 WRITEUP/ spokes unchanged; serve as deep-dive references for both
  new guides.
- Methodology / model / data / compute — pure presentation restructure.
- RESULTS.md deep tables-only restructure deferred to v1.3.1 polish
  if needed (current state already table-heavy).
- Reviewer URL pin (`tree/v1.0.0`) unchanged per ADR-033.

### Verification

- Audit suite green: `audit_writeup_numbers` + `audit_rendered_site` +
  `audit_leakage` + `audit_adr_count_claims` (79 ADRs) +
  `audit_superseded_by_backlinks` + `check_no_emoji`.
- pre-commit suite green.
- 4 sub-PRs CI-greenable independently; merged sequentially to
  release/v1.3.0; final merge to main + v1.3.0 tag.

## [1.2.16] — 2026-05-21 {#v1-2-16}

**eval-toolkit v0.44.0 → v0.47.0 consumer-side bump (skip 3 minors).**
Dependency/ledger maintenance per ADR-066 trigger #4; no methodology /
model / data / compute change.

### Changed

- `pyproject.toml` + `uv.lock` — `eval-toolkit==0.44.0` → `==0.47.0`.
  Skip-bumps through v0.45 + v0.46 + v0.46.1 intermediate pin states
  (all are dependency/ledger maintenance per the upstream rolling
  release plan).
- Upstream closures bundled at v1.2.16:
  - **v0.45.0** closes `#52` LogisticStacker + MetaLearner Protocol
  - **v0.46.0** closes `#36` inline CI via `scorecard()` + `Scorecard`
    + `metric_specs` (different API shape than originally proposed in
    this project's #36 contribution comment; same underlying capability)
  - **v0.46.1** Round 6 hotfix (no API surface change)
  - **v0.47.0** closes `#49` advanced-6 `character_injection` + sweep
    unification (`TextTransform` Protocol; per-module strategy Protocols
    + `character_injection`/`spotlighting` SimpleNamespaces removed
    from public API)
- v0.47.0 BREAKING removals do NOT hit our project — we use only
  submodule imports (`from eval_toolkit.metrics import pr_auc`, etc.)
  which are preserved through v0.46's `__getattr__` soft-deprecation
  shim + v0.47's hard-removal cycle.
- `decisions/library_imports.md` eval-toolkit row updated (v0.44→v0.47
  history; concise per 1200-char per-cell hard gate).
- `decisions/upstream_issues.md` updated: #36 RESOLVED-in-v0.46.0;
  #49 advanced-6 RESOLVED-in-v0.47.0; #52 RESOLVED-in-v0.45.0; scope-
  note paragraph + ledger row updates.

### Sub-commits

- `939e9cc` — chore: bump eval-toolkit pin v0.44.0 → v0.46.1 (parallel
  agent; misleading commit message says v0.46.0 → v0.46.1 but actual
  diff is v0.44.0 → v0.46.1)
- `b5402d2` — chore: bump eval-toolkit pin v0.46.1 → v0.47.0 (parallel
  agent)
- `a838f41` — chore: ledger updates for v0.44→v0.47 (library_imports +
  upstream_issues; this session)
- `52e258c` — fix: trim library_imports eval-toolkit cell under
  1200-char limit (fix-forward after CI surfaced rendered-site audit
  failure on first push; this session)
- (this commit) — CHANGELOG [1.2.16] + tag

Third parallel-agent collision incident this session (after the
v1.2.6+v1.2.7 codex-handoff incident + the v1.2.14 eval-toolkit
v0.44.0 collision). Same detect → ask → incorporate → cite pattern.

## [1.2.15] — 2026-05-21 {#v1-2-15}

**v1.2.14 visual-recheck + supersession-backlink invariant + ADR-077
backfill.** Closes the v1.2.13/v1.2.14 lesson-noted gap: v1.2.14 added
the ADR-count-claim invariant; v1.2.15 adds the sibling supersession-
backlink + closing_commit invariant that catches the OTHER class of
frontmatter chain-effect (REPO_AUDIT_2026-05-21 §P1-6 class). No
methodology, model, data, or compute change.

### Added

- `scripts/audit_superseded_by_backlinks.py` — invariant tool: for every
  ADR with `supersedes: [N]`, asserts target ADR-N has supersedeR in
  its `superseded_by:` list. Axis-only supersessions (per the v1.2.13/
  v1.2.14 narrow-relaxation discipline established by ADR-072 +
  ADR-073 + ADR-076) are EXEMPT and reported as INFO via YAML comment
  heuristic. Also asserts Accepted ADRs have populated `closing_commit`
  (small exempt set for governance/backfill ADRs).
- `.pre-commit-config.yaml` audit-superseded-by-backlinks hook (runs
  on decisions/ADR-*.md changes).
- `.github/workflows/audit-writeup.yml` step invoking the new audit
  (parallel to v1.2.14's audit_adr_count_claims).
- **ADR-077** — Supersession-backlink + frontmatter octal-quoting
  backfill. Same Michael Nygard format as ADR-072 + ADR-076; extends
  the narrow-relaxation frontmatter-backfill class.

### Changed

- **Class 1 frontmatter octal-quoting fixes** (3 fields). YAML 1.1
  parses bare integer literals with leading zero as OCTAL
  (`yaml.safe_load("015")` returns decimal 13, not the author's
  intended ADR-015 reference). Quote-fixed:
  - `ADR-007.superseded_by: 015` → `"015"`
  - `ADR-015.supersedes: 007` → `"007"` (defensive; same intent)
  - `ADR-018.supersedes: 015` → `"015"`
- **Class 2 supersession back-link gaps** (4 ADRs gained
  `superseded_by:` entries):
  - ADR-015 ← ADR-018 (partial supersession on reference-slate axis)
  - ADR-018 ← ADR-050 (rung-slate narrowing)
  - ADR-021 ← ADR-050 (eval-slate aggregation narrowing)
  - ADR-052 ← ADR-075 ("entire scope" per ADR-075 comment, not
    axis-only)
- Cascading edits (caught mechanically by v1.2.14's
  `audit_adr_count_claims.py` invariant — **validates its design
  intent**):
  - `README.md:100` + `README.md:114` — 76 ADRs → 77 ADRs
  - `docs/for-hiring-managers.md:83` — 76 ADRs → 77 ADRs
  - `WRITEUP/methodology-guarantees.md:12` — 76 ADRs ... ADR-076 →
    77 ADRs ... ADR-077
  - `CLAUDE.md:13` — 76 ADRs at v1.2.13 close → 77 ADRs at v1.2.15
    close; governance parenthetical extended with ADR-077
- `SUBMISSION_AUDIT.md` regenerated (76 → 77 CLAIM rows).

### Visual recheck on v1.2.14 (no commit; inline summary)

Playwright sweep of all 4 user-visible v1.2.14-changed pages on the
live gh-pages site: clean. All v1.2.14 changes (D1 README fix,
Phase-4 marker cleanup, eval-toolkit v0.44.0 row, upstream_issues
scope-note prose) propagated correctly. Snapshots + screenshots
gitignored at `transcripts/auto/v1-2-14-visual-recheck-*`.

### Audit-tool development note

The audit_superseded_by_backlinks.py development surfaced and
discharged 2 distinct frontmatter-debt classes (Class 1 octal-quoting
+ Class 2 backlink gaps; both via ADR-077). The script itself was
initially bit by the same YAML octal-parsing bug (4 ADRs dropped due
to adr_id collision); the fix landed via `collect_adrs` using filename
as source of truth for adr_id rather than the YAML-parsed frontmatter
field. Lesson noted: any bare-integer ID value with leading zero in
YAML 1.1 is a source bug; future ADRs should quote all bare-integer
ID values in supersedes / superseded_by / adr_id fields.

### v1.2.15 sub-commits

- C1 (`c3d1083`) — new audit-tool + pre-commit + CI wiring + ADR-077
  + frontmatter backfills + reader-facing cascade edits (per v1.2.15
  plan Q1 "bundled" + Q2 "halt + surface" + path-1 backfill lock)
- C2 (this commit) — CHANGELOG + tag

## [1.2.14] — 2026-05-21 {#v1-2-14}

**v1.2.13 visual-verification-driven polish patch.** Closes D1 from
the post-ship Playwright + curl-grep sweep of v1.2.13's rendered
site (`transcripts/2026-05-21__v1-2-13-visual-verification.md`;
gitignored) + folds in 4 deferred items from v1.2.13's out-of-scope
list. No methodology, model, data, or compute change.

### Added

- `scripts/audit_adr_count_claims.py` — invariant tool that greps
  "NN immutable Architecture Decision Records" / "NN ADRs" claims
  across reader-facing surfaces and asserts NN matches
  `ls decisions/ADR-*.md | wc -l`. Historical snapshots (claims
  near "Phase X close" / "submission gate" / "snapshot" / "through
  ADR-NNN" qualifiers within ±3-line context) are flagged INFO,
  not FAIL. Prevents future chain-effect misses where a patch adds
  an ADR but count claims on reader-facing prose go stale.
- `.pre-commit-config.yaml` audit-adr-count-claims hook (runs on
  .md / .qmd changes).
- `.github/workflows/audit-writeup.yml` step invoking the new
  audit (parallel to existing audit_writeup_numbers).

### Changed

- `README.md:100` + `README.md:114` — 75 → 76 ADRs (D1 from the
  v1.2.13 visual verification; the v1.2.13 C2 reader-facing sweep
  updated for-hiring-managers + methodology-guarantees but missed
  README because its "75" was correct at v1.2.12 — the chain effect
  of ADR-076 → README-count-bump was missed).
- `.pre-commit-config.yaml` — `mirrors-mypy` bumped v1.8.0 → v2.1.0
  (deferred from v1.2.13 C7; verified no new strict errors via
  `pre-commit run mypy --all-files` before commit).
- `pyproject.toml` + `uv.lock` — `eval-toolkit==0.43.0` → `==0.44.0`
  (dependency/ledger maintenance per ADR-066 trigger #4). Closes
  upstream #50 (RecallAtLowFPR Meta Prompt Guard 2 loss recipe) +
  #51 (spotlighting defense — delimit/datamark/encode + sweep).
  No methodology/model/data/compute change.
- `decisions/library_imports.md` — eval-toolkit row updated for
  v0.44.0; Phase-4 markers normalized ("Phase 4 deliverable" →
  "(landed; Phase 4)"; "Phase 4 Commit N" → "landed at Phase 4
  Commit N") per REPO_AUDIT_2026-05-21 P2.
- `decisions/upstream_issues.md` — v1.2.13 §"Ledger scope" updated
  to record #50/#51 as RESOLVED-and-consumed-as-dependency-maintenance
  (previously listed as out-of-scope when CLOSED-upstream-unconsumed
  at v1.2.13 close).

### v1.2.14 sub-commits

- C1 (`4c1e657`) — D1 + audit-tool + mypy bump + eval-toolkit v0.44.0
  + Phase-4 marker cleanup (bundled per v1.2.14 plan locked
  decisions Q1/Q2: "Everything" scope, 2-commit cadence)
- C2 (this commit) — CHANGELOG + tag

Parallel-agent collision noted: the eval-toolkit v0.44.0 bump's
`pyproject.toml` + `uv.lock` changes were initiated by a paused
parallel-agent session (plan file
`evaluate-all-the-work-twinkly-kite.md`); incorporated into v1.2.14
per user-locked decision after discovery.

## [1.2.13] — 2026-05-21 {#v1-2-13}

**REPO_AUDIT_2026-05-21 discharge polish patch.** Closes the
v1.2.12-close internal audit (`decisions/audits/REPO_AUDIT_2026-05-21.md`):
2 P0 + 7 P1 + ~14 P2 + ~7 P3 findings, all prose-propagation debt from
the v1.2.9-v1.2.12 polish arc. No methodology, model, data, or compute
change.

### Added

- ADR-076 — superseded_by + closing_commit frontmatter backfill
  (extends ADR-072 pattern; closes audit P1-6 + part of P2).
- `decisions/audits/REPO_AUDIT_2026-05-21.md` — full-package quality +
  polish audit at v1.2.12 close (committed at C0 = `ed3ad2a`, before
  the discharge sequence).

### Changed

- README + WRITEUP + READING_GUIDE "Current state" pin propagated
  v1.2.11/v1.2.8 → v1.2.13 (P0-1); historical v1.0.0 reviewer pin
  unchanged (per ADR-033).
- docs/for-hiring-managers.md + WRITEUP/methodology-guarantees.md ADR
  counts 70 → 76 (P0-2 + P1-1); methodology-guarantees Phase 5 prose
  qualifier clarified ("at Phase 5 close" → "at v1.0.0 submission gate").
- WRITEUP.md + index.qmd Finding 3 reframe: "actively harmful" →
  "anti-correlated with cross-family attack class" (P1-5; propagates
  the v1.2.11 reframe already at for-hiring-managers.md:34).
- CLAUDE.md ADR count 70 → 76; expand governance parenthetical with
  ADR-073/074/075/076; append ADR-073 pointer after narrow-exceptions
  block; note frontmatter-completeness backfill is a fifth class
  governed by ADR-072/076 precedent (P1-2 + P1-3).
- AGENTS.md — backport §Narrow exceptions from CLAUDE.md so
  non-Claude agents see the in-place factual-defect rule (P1-4).
- CLAUDE.md + AGENTS.md anti-patterns — strengthen library-first
  phrasing per `[[library_first_is_project_wide_invariant]]`
  (2026-05-18 strengthened form); old "thin local glue + TODO marker"
  pattern explicitly retired (P2 ledger).
- ADR-076 supersedes ADR-046 + ADR-054 + ADR-061 on frontmatter axis
  only (`superseded_by: ["062"]` backfill); ADR-071-075 closing_commit
  populated with verified SHAs.
- ADR-024:13 references — `jstor.org/stable/27033529` reverted to
  original after C4 attempted ADR-069 canonicalization (DOI
  `10.2307/27033529` 404s; not every JSTOR stable ID has a valid DOI);
  `.lycheeignore` re-adds the JSTOR pattern.
- ADR-020:206 + ADR-025:41-43 — local-fs paths canonicalized to
  github.com URLs per ADR-068 (where upstream paths resolve; 1 docs
  reference reverted to non-URL form for a path that doesn't exist
  upstream).
- ADR-061:287 + ADR-063:89 — `.claude/plans/` paths → `[PLAN_REF
  redacted]` marker per ADR-068 Class B.
- library_imports.md:85 — section header `[v0.7.7 pinned]` →
  `[v0.8.4 pinned]` matching pyproject.toml (P1-7).
- library_imports.md bump-triggers list — "exactly three" → "exactly
  four"; add ADR-066 dependency/ledger-maintenance trigger.
- upstream_issues.md — add "Ledger scope (clarified at v1.2.13)"
  subsection explaining eval-toolkit #50/#51/#52 are outside ledger
  scope.
- RESULTS.md LODO direct-source recall table — full-FT row gains
  honesty asterisk + ADR-075 footnote (P2 parity with
  EXECUTIVE_SUMMARY:92 + for-hiring-managers:55 + index.qmd:94).
- WRITEUP.md:129-130 ProtectAI rows — Read column gains "not a clean
  OOD baseline" tail caveat (P2 parity with README:39-40 +
  EXECUTIVE_SUMMARY:35-36 + index.qmd:52-53).
- docs/GLOSSARY.md:36 — question wording sync with
  docs/for-hiring-managers.md:81.
- `.github/workflows/ci.yml` + `publish.yml` — setup-uv unification:
  `pip install uv` (8 sites) → `astral-sh/setup-uv@v8.1.0` matching
  audit-writeup.yml (P3 hygiene).

### Deferred (out of v1.2.13 scope)

- mypy bump (`mirrors-mypy v1.8.0` → latest) — R3 risk: bump may
  surface new strict-mode errors. Defer to next dev-tool sweep.
- library_imports.md stale "Phase 4 deliverable" / "Phase 4 Commit N"
  markers — would require per-line consumption-status verification;
  cosmetic only (reads-as-stale, not factually wrong). Defer.
- Tooling automation for future supersession-backlink + closing_commit
  detection (audit "lessons noted" item) — portfolio-repo scope.

### Sequence

- C0 (`ed3ad2a`) — audit file standalone
- C1 (`b97b70d`) — ADR-076 + frontmatter backfill
- C2 (`9ef7993`) + C2.1 (`f1a54cb`) — reader-facing accuracy +
  lycheeignore tree/v1.2.13 forward-ref fix
- C3 (`43569a1`) — CLAUDE.md + AGENTS.md governance refresh
- C4 (`6752e4b`) + C4.1 (`bd89362`) — ADR cross-ref sweep + JSTOR/eval-toolkit
  docs URL fix-forward
- C5 (`2d2569e`) — library-first ledger refresh
- C6 (`4b63237`) — RESULTS + WRITEUP + GLOSSARY polish
- C7 (this commit) — CI hygiene + CHANGELOG + audit-trail close + tag

All 8 commits gated locally + on GitHub Actions CI green before
proceeding to the next per `[[auto-continue-on-green-ci-preferred-for-bundled-patches]]`.

## [1.2.12] — 2026-05-21 {#v1-2-12}

**README hybrid-adoption polish**: restructures the README around a
compact top-fold + `<details>`-collapsible depth, per the drafted
replacement that's been sitting in the audit appendix unadopted since
the original 2026-05-20 audit. Keeps all v1.2.10/v1.2.11 polish
(asterisks, AUROC framing, "Project at a glance" cross-refs). No
methodology, model, data, compute, or result change.

### Changed

- **README top-fold compact + `<details>` depth**: top fold drops
  from ~70 lines (with inline result tables) to ~22 lines (problem
  + 2-bullet result + 3-depth triage navigation). Recruiter-skim path
  sees the bottom-line in prose without scrolling past tables; the
  curious-reader path is one click into `<details>`.
- **"Read the site, three depths" triage**: replaces the previous
  4-bullet "How To Read The Site" with sharper 60-second / 45-minute
  / Reproduce ladder pointing at the live-site URLs.
- **Reproduce section gains explicit T0/T1/T3 ladder** with cost +
  time annotations + HF Hub checkpoint direct links + ADR-058 +
  ADR-020 citations.
- **"Why trust the result" section added**: 4-bullet covering
  source-level LODO holdout / bootstrap-CI discipline / single-class
  slice handling / reference-scorer contamination audit. Surfaces
  the trust-anchors that were previously implicit.
- **Direct Detection Check tables removed from README**: they live
  on RESULTS.md + EXECUTIVE_SUMMARY.md; duplicating them in the
  README added length without signal. The pooled OOD table stays in
  the README because it's the headline finding.
- **ADR count updated to 75** (was 70 in earlier copy; reflects
  ADR-071 through ADR-075 + new ADRs through the v1.2.11 polish
  cycle).
- **Current state pin moved to v1.2.11** in the README's Submission
  Anchors block (was v1.2.8 in the unadopted draft; current state
  is now v1.2.11 + this v1.2.12 patch).

### Decisions

- No new ADRs. README restructure is a surface-presentation fix
  citing the original audit's drafted-replacement plan (in
  `~/notes/prompt-injection-audit-2026-05-20-readme-draft.md`,
  hybrid-adoption path).

## [1.2.11] — 2026-05-20 {#v1-2-11}

**Post-remediation polish patch**: a focused polish pass on items the
post-remediation audit flagged as P2/P3 (originally deferred). User
push: "polish is important." 2 commits + this tag close the loop;
no methodology, model, data, compute, or result change.

### Changed

- **Persona-explicit naming softened**: "For hiring managers in a hurry"
  renamed to "Project at a glance" everywhere it appears (page title,
  h1, sidebar label, cross-references in WRITEUP, index.qmd,
  README, READING_GUIDE, EXECUTIVE_SUMMARY, docs/site-reader-map).
  File path unchanged to preserve external links. Reads naturally
  for any reviewer regardless of role.
- **"Hiring-manager-level skim" softened**: across 8 WRITEUP spokes'
  "How to read this spoke" callouts (data-decisions, eval-design,
  threshold-policy, reproducibility, methodology-guarantees,
  reference-scorer-audit, model-rungs, limitations) the phrasing
  "hiring-manager-level skim" became "fast skim". Consistent with
  the "Project at a glance" rename.
- **AUROC phrasing variety on table-row interpretations**: the
  phrase "fine-tuning was actively harmful" appeared in 5 reader-
  surface tables (landing, EXEC_SUMMARY, WRITEUP §7, for-hiring-
  managers, RESULTS, README). Varied the table-row interpretations
  in EXEC_SUMMARY + README + for-hiring-managers to "trained adapter
  ranks below random" / "anti-correlated with cross-family attack
  class". Canonical narrative phrasings (landing point #3,
  WRITEUP §7 Finding 3 heading) preserved as headline.
- **For-hiring-managers Q2 mechanism paragraph tightened**: was
  ~110 words after C9; now ~50 words. The full mechanism lives on
  the landing page + WRITEUP + EXEC_SUMMARY Mechanism section;
  Project-at-a-glance needs the one-sentence version, not the
  expanded one.
- **Landing page "Models" bullet internal inconsistency fixed**:
  bullet previously listed 5 detectors but the LODO direct-source
  table on the same page showed 6 (full-FT row at 0.558). Bullet
  now mentions full-FT with the "LODO direct-source only" caveat +
  ADR-075 citation.
- **ADR-064 redaction marker tightened**: "[Verbatim user feedback
  redacted 2026-05-20 per ADR-074 narrow-relaxation; verbatim user
  wording preserved in private transcript file.]" became "[Verbatim
  wording redacted per ADR-074.]". Reduces curiosity invitation.
- **§9.5 Anti-correlation finding: honest empirical-scope caveat
  added**. The "lexical overfitting + label-relevance shift"
  mechanism in WRITEUP/limitations §9.5 is *interpretation* from
  aggregate AUROC + slate composition, NOT direct empirical
  demonstration in this artifact. Per-slice score-distribution
  analysis from `evals/predictions/` is named as v6 future-work +
  cited to the prediction-persistence pattern in
  methodology-guarantees §6.2. Closes the methodology pushback
  class the v1.2.10 reporting-honesty asterisks didn't.

### Decisions

- No new ADRs. ADR-064 redaction marker tightening + AUROC table-row
  phrasing variety land under ADR-073 Class A/B narrow-relaxation
  discipline (no decision content changes; surface polish only).

## [1.2.10] — 2026-05-20 {#v1-2-10}

**Post-remediation reporting-honesty patch**: the 2026-05-20 post-remediation
audit on v1.2.9 surfaced that two headline-table caveats (ProtectAI v1+v2
training-pool contamination + full-FT incomplete OOD experiment) were sitting
unflagged. A skimming reader could treat ProtectAI scores as peer to in-house
detectors and the full-FT LODO row as a complete result. No methodology, model,
data, compute, or result change; the data + caveats were already there in
EVIDENCE.md §1-2 + ADR-050 R2 / ADR-052 / ADR-075. This release makes them
visually load-bearing.

### Changed

- **Reporting-honesty asterisks on contamination + incomplete-experiment rows**
  --- 6 entry-surface pages (landing / EXECUTIVE_SUMMARY / RESULTS §1 /
  for-hiring-managers / WRITEUP §6 / READING_GUIDE) now show ProtectAI v1+v2
  with `*` markers + footnote citing EVIDENCE §1-2 training-pool overlap, and
  full-FT LODO direct-source rows with `**` markers + footnote citing
  ADR-075 unified-narrative on the dropped pooled OOD inference. Authorization
  basis: ADR-064 §D flagged-not-fixed inventory + ADR-018 reference-scorer
  slate (existing caveats made visually load-bearing; no decision content
  changes).
- **README framing aligned with v1.2.9 narrative** --- LoRA row "fine-tuning
  hurt OOD performance" replaced with "fine-tuning was actively harmful;
  AUROC 0.383 below 0.5 floor" to match landing + EXEC_SUMMARY + WRITEUP §7
  Finding 3 + for-hiring-managers Q2 + RESULTS §6 + READING_GUIDE "How To
  Read" callout + model-rungs §4.3 + limitations §9.5. README also picks up
  the asterisk treatment for consistency with the 6 entry-surface pages.

### Decisions

- No new ADRs in this release. The asterisk additions cite ADR-064 §D + ADR-018
  as existing authorization bases (per ADR-073 Class A/B narrow-relaxation
  discipline applied to "flagged-not-fixed" inventory closure).

## [1.2.9] — 2026-05-20 {#v1-2-9}

**Audit-remediation patch release**: 2026-05-20 second-opinion audit cycle
surfaced + closed P0/P1 governance + presentation + narrative findings.
12 commits; no methodology, model, data, compute, or result change. The
new canonical source pin moves to `v1.2.9`; v1.0.0 preserved as the
original submission reviewer pin per ADR-033.

### Changed (now packaged from [Unreleased] pre-2026-05-20 work)

- **Direct-injection results co-headlined** — `README.md` and primary reader
  surfaces now show the direct-performance story alongside the OOD story:
  balanced direct+benign validation is strong, LODO direct-source recall is
  reported honestly as recall-only, and pooled OOD remains the cross-family
  failure mode.
- **Writeup result map clarified** — the methodology hub now inventories the
  major findings instead of only foregrounding pooled OOD: direct learning,
  OOD failure, LoRA-vs-frozen behavior, DeBERTa null ablation, threshold
  fragility, calibration, and reference-detector slice dependence.
- **Guide polish tightened** — `NEXT_STEPS.md` now uses real bullet lists for
  status entries, and the hiring-manager / reading-guide path is split into
  shorter scan-friendly blocks.
- **Public reference pages made legible at root cause** — Quarto source-code
  tools disabled for public docs; generated `SUBMISSION_AUDIT.md` now renders
  from `scripts/regenerate_audit.py` as a claim index plus detail sections;
  assumptions/spec/reference ledgers now carry current-state reader notes.
- **Entry-path result tables clarified** — landing page, README, executive
  summary, hiring-manager page, and reading guide now show detector-level
  direct detection checks beside the pooled OOD failure, with interpretation
  columns and undefined all-positive metrics omitted.

### Changed (2026-05-20 audit remediation)

- **AUROC anti-correlation propagated to headline framing** — landing /
  EXECUTIVE_SUMMARY / WRITEUP §7 Finding 3 / for-hiring-managers Q2 /
  RESULTS §2+§6 / READING_GUIDE Result Map / WRITEUP/model-rungs §4.3 /
  WRITEUP/limitations §9.5 (new section) all surface the sharper finding:
  LoRA pooled OOD AUROC 0.383 + TF-IDF + LR 0.371 both fall below the 0.5
  random floor with CIs that clear on the wrong side. In-pool to
  cross-family generalization gap: ~0.6 AUROC for trained detectors,
  ~0.4 for the frozen probe. Mechanism: lexical overfitting + slate-induced
  label-relevance shift (NotInject inverts the negative side; indirect/
  agentic attacks invert the positive side). Headline numbers unchanged;
  framing sharpened.
- **Canonical source pin moved to `v1.2.8`** (now `v1.2.9` with this tag) —
  READING_GUIDE.md §Submission Anchors + WRITEUP.md header updated;
  v1.0.0 preserved as historical "original submission tag" per ADR-033.
- **ADR count standardized to 70** across reader-facing docs:
  docs/for-hiring-managers.md (was 60+); WRITEUP/methodology-guarantees.md
  (was 50+); CLAUDE.md (was 53 at v1.0.4 close). CHANGELOG historical
  entries with prior counts preserved per Keep-A-Changelog convention.
- **Site polish**: favicon.svg added + referenced via `_quarto.yml`;
  styles.css updated to suppress "Anchor" text leakage in headings via
  `font-size: 0` on `.anchorjs-link` with a hover-only `#` pseudo-element
  preserving the click-to-anchor affordance.

### Added (2026-05-20 audit remediation — new ADRs)

- **ADR-071**: cross-reference slug-sweep closure. Executes the 33-pattern
  slug-mapping authorized by ADR-067 §C1 + post-2026-05-20 audit extension
  across 22 ADR files (63 substitutions). Strips the
  `/home/brandon_behring/.claude/plans/twinkly-weaving-puppy.md` local-fs
  path leak from ADR-040 (3 occurrences). Closes the
  "documented-but-unexecuted authorization" optic from the
  ADR-067-070 chain.
- **ADR-072**: backfill ADR-051 + ADR-052 frontmatter (`closing_commit`,
  template `## Status` + `## Alternatives Considered` sections). Resolves
  the structural debt that the 2026-05-18 self-audit had attributed
  (incorrectly) to ADR-049 + ADR-050; the v1.0.x patch cycle had since
  populated 049+050. The 2026-05-20 re-verification surfaced the actual
  gap was in 051+052.
- **ADR-073**: immutability rule consolidated re-statement. Collapses the
  4-ADR narrow-relaxation chain (ADR-067/068/069/070) into a single
  canonical immutability ADR with four named exception classes (A/B/C/D).
  Same authorization surface; reduced "immutability is loose" reader
  optic from 4 signals to 1 rule + 4 exceptions. ADRs 067-070 remain as
  historical artifacts; prospective citation moves to ADR-073.
- **ADR-074**: redact verbatim self-criticism quote in ADR-064. Replaces
  the publicly-readable "doesn't demonstrate clear thought" wording with
  a neutral paraphrase preserving the decision context. Original verbatim
  feedback preserved in the (private; gitignored) transcript file per
  AGENTS.md transcript discipline.
- **ADR-075**: full-FT OOD drop rationale unified narrative. Consolidates
  ADR-050 Revision 2 (FUSE-crash-forced-drop framing) + ADR-052
  (methodology-load-bearing-with-crash-as-trigger framing) into a single
  prospective citation, removing the same-day retcon optic without
  changing the underlying outcome. ADR-050 R1 (LLM-judge cost drop)
  unaffected; remains on its separate axis.

### Removed (2026-05-20 audit remediation)

- **`REPO_AUDIT_2026-05-18.md` moved from repo root** to
  `decisions/audits/REPO_AUDIT_2026-05-18.md` with a "Status: resolved"
  header. The 2026-05-18 audit's executive verdict "Not submission-ready"
  no longer headlines the repo file-tree glance. All 5 P0 blockers + most
  P1/P2 findings are resolved or explicitly carryforwarded via ADR-051 /
  ADR-052 / ADR-058. The audit remains preserved as part of the SDD audit
  trail under `decisions/audits/`.
- **Stale `chore/eval-toolkit-v0.34.0-migration` branch deleted** on
  origin. The v0.34.0 migration was applied via PR #2 (merged 2026-05-18).
- **Issue #1 closed**: v0.34.0 eval-toolkit BREAKING note resolved by
  PR #2; consumer uses positional form at `src/eval/mde.py:63` unaffected
  by the keyword rename. eval-toolkit dependency is at v0.43.0 as of
  v1.2.8.

## [1.2.8] — 2026-05-19 {#v1-2-8}

**Patch release**: rendered-site hardening plus dependency/ledger maintenance.
No compute spend; no methodology, model, data, or result change; reviewer URL
pin remains `v1.0.0`.

### Fixed

- **Notebook pages render as HTML** — Jupytext companion scripts moved to
  `notebooks/_jupytext/`; the Quarto site renders the four frozen notebooks as
  static HTML appendices without re-executing cells.
- **Raw site leaks blocked** — top-level docs, `docs/*.md`, `CLAUDE.md`, and
  `code_quality.md` are rendered as HTML; `make site-audit` fails on raw
  `.md` / `.ipynb` files, missing notebook HTML, or rendered internal links to
  raw Markdown/notebooks.
- **Publish path hardened** — CI now has a hard rendered-site gate, and the
  Pages workflow renders + audits before publishing the existing `_site/`
  output with `render: false`.
- **Quarto warnings cleaned** — `citeproc: false` suppresses false citation
  warnings from literal test decorators; ADR-070 authorizes the narrow
  render-only ADR-034 fence delimiter correction.

### Changed

- **eval-toolkit bumped to `0.43.0`** — records resolved upstream issues #48,
  #49, and #53 in the library/import and upstream-issue ledgers. This is
  dependency/library-first maintenance only.
- **Presentation/status drift cleaned** — notebook references now describe
  static rendered analysis appendices, `NEXT_STEPS.md` records the v1.2.8 site
  hardening close, and mutable docs/tests consistently treat F1-F5 as the
  reviewer-facing figure slate while F6/F7 remain diagnostic/historical paths.
- **Private artifact inventory completed** — tracked RunPod/eval/notebook
  artifacts and generated leftovers were inventoried privately. The inventory
  is not committed or rendered as public documentation.

### References

- Closing ADR: [ADR-070](decisions/ADR-070-quarto-render-only-markdown-corrections.md)
- Predecessor: [v1.2.7](#v1-2-7)
- Reviewer URL pin (unchanged): `tree/v1.0.0` per [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md)

## [1.2.7] — 2026-05-19 {#v1-2-7}

**Patch release**: fix-forward for the single CI-only lychee residue after
`v1.2.6`. Docs-only; no compute spend; reviewer URL pin remains `v1.0.0`.

### Fixed

- Added one exact `.lycheeignore` pattern for an immutable ADR-023 AAAI
  citation URL that returns 403 to the GitHub runner but did not fail in the
  local lychee reproduction.

### References

- No new ADR (CI/link-check transport exception only).
- Predecessor: [v1.2.6](#v1-2-6) (Markdown link-check content debt close)

## [1.2.6] — 2026-05-19 {#v1-2-6}

**Patch release**: fix-forward for inherited Markdown link-check content debt
surfaced after the `v1.2.5` presentation patch was already tagged. Docs-only;
no compute spend; reviewer URL pin remains `v1.0.0`.

### Fixed

- **Project-owned broken links repaired** — replaced aspirational
  `eval-toolkit/docs/methodology/*` links in mutable specs/writeup spokes with
  stable eval-toolkit README references, and fixed the `CHANGELOG.md` root
  link to the writeup hub.
- **ADR-068 narrow exception applied** — fixed the immutable ADR-025
  aspirational eval-toolkit reference and the ADR-065 local-filesystem memory
  links without changing decision content.
- **ADR-069 DOI canonicalization added** — bot-blocked publisher citation
  URLs in immutable ADRs are replaced with DOI-equivalent targets without
  changing the cited paper identity.
- **Residual historical URL policy clarified** — `.lycheeignore` now
  documents the remaining bot-blocked vendor pages and specific pre-existing
  retired citation URLs so push-time lychee catches current project drift
  instead of failing on immutable historical reference rot.

### References

- Closing ADRs: [ADR-068](decisions/ADR-068-immutability-narrow-relaxation-for-broken-external-references.md) + [ADR-069](decisions/ADR-069-immutability-narrow-relaxation-for-publisher-url-to-doi-canonicalization.md)
- Predecessor: [v1.2.5](#v1-2-5) (presentation path and NEXT_STEPS remediation)
- Reviewer URL pin (unchanged): `tree/v1.0.0` per [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md)

## [1.2.5] — 2026-05-19 {#v1-2-5}

**Patch release**: docs-only presentation + status-drift remediation for the
live/main site. No ADR (readability/status cleanup, not methodology). Layered
additively on v1.2.4.

### Changed

- **`NEXT_STEPS.md` reframed as "Carryforward log and future work"** — the
  page is now current-state-first history rather than an apparent active task
  list. The tactical section is relabeled "Completed tactical carryforward";
  each entry leads with final status before chronology.
- **Stale NEXT_STEPS status fixed** — §1.4 now records the v1.0.9 closure of
  eval-toolkit #44 (`fit_isotonic_binary` consumed; local
  `fit_isotonic_binary_local` adapter removed). The F1/F2/F5 figure-refactor
  item no longer appears as active future work; it is recorded as completed
  carryforward via ADR-066 / v1.2.2.
- **Hiring-manager-first reader path tightened** — landing page, reading guide,
  executive summary, README, and WRITEUP now make the primary path explicit:
  landing page -> 60-second hiring-manager tour -> Results -> deeper audit.
- **Quarto navigation label clarified** — `NEXT_STEPS.md` remains at the same
  URL, but the navbar/sidebar label now reads "Carryforward + future work."

### References

- No new ADR (no methodology change).
- Reviewer URL pin (unchanged): `tree/v1.0.0` per [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md)
- Cost discipline (unchanged): cumulative project compute spend stays $17.08 (within ADR-020 $200 hard cap; $0 GPU at v1.2.5)
- Live Quarto site: reflects latest patch after GitHub Pages publish

## [1.2.4] — 2026-05-19 {#v1-2-4}

**Patch release**: fix-forward for v1.2.3 — residual lychee v0.23.0 incompat (`--base .` rejected). No ADR (bug fix, not methodology). Layered additively on v1.2.3.

After v1.2.3 dropped `--exclude-mail`, the v1.2.3 push surfaced a second lychee v0.23.0 incompat: `error: invalid value '.' for '--base <BASE>': Base must either be a URL (with scheme) or an absolute local path`. v0.23.0 tightened `--base` validation to require URL or absolute path; the relative `.` that worked in v0.22.x is now rejected.

### Fixed

- **`.github/workflows/link-check.yml:47` (Markdown link check workflow; lychee v0.23.0 `--base` validation)** — deleted the `--base .` line. Verified by `grep -rE '\]\(/[a-zA-Z][^)]+\)' --include='*.md' --include='*.qmd'` (excluding `.venv/`, `_site/`, `transcripts/`) → 0 root-relative links in the markdown corpus; `--base` was not load-bearing. Default behavior (resolve relative URLs against each input file's directory) is what we want.

### Lesson noted

The v1.2.3 patch only checked the SPECIFIC error (`--exclude-mail`) from the CI log without reading the full lychee v0.23.0 CHANGELOG / CLI options source for OTHER potential incompats. A full release-notes read of a major version bump (here: v0.22.x → v0.23.0) is now the discipline for future CI tool upgrades. Cost: one extra patch cycle (~10 min).

### References

- No new ADR (bug fix, not methodology change). Same precedent as v1.2.3.
- Predecessor: [v1.2.3](#v1-2-3) (3-fix CI hygiene patch)
- Reviewer URL pin (unchanged): `tree/v1.0.0` per [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md)
- Cost discipline (unchanged): cumulative project compute spend stays $17.08 (within ADR-020 $200 hard cap; $0 GPU at v1.2.4)
- Live Quarto site: reflects v1.2.4 within ~2 min of push

## [1.2.3] — 2026-05-19 {#v1-2-3}

**Patch release**: CI hygiene — fix 3 inherited CI failures across mypy hard gate, smoke-test soft gate, and lychee link-check workflow. No ADR (bug fixes, not methodology). Layered additively on v1.2.2 — no supersession of any prior ADR. Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033; live Quarto site reflects v1.2.3.

CI red across these jobs since v1.1.3 (`ca43512`) / v1.1.4 (`d3f63d8`) / v1.1.2 (`a34128b`) — 5 patches; failures were masked because the Publish Quarto + Writeup numerical-claim audit gates stayed green on every push. Closes the inherited debt before any further patch work. CI now green end-to-end on `main`.

### Fixed

- **`scripts/render_figures.py:127` (mypy --strict hard gate)** — `plt.Axes` is not exposed as a typed attribute on `matplotlib.pyplot`; `mypy --strict` rejected it with `Name "plt.Axes" is not defined [name-defined]`. Imported `Axes` from `matplotlib.axes` (the canonical home) alongside the existing `Figure` import. Annotation changed from `_style_axes(ax: plt.Axes)` to `_style_axes(ax: Axes)`. Verified locally: `uv run mypy --strict --exclude '_site/' .` -> 92 source files clean. Closes the `lint (hard gate)` failure introduced at v1.1.3 (`ca43512`).

- **`tests/smoke/test_training_primitives_smoke.py::test_training_args_seed_propagation` (test-smoke soft gate; CPU-runner portability)** — `assert args.bf16 is True` failed on CI's CPU-only ubuntu runners because `build_training_args` correctly gates `use_bf16 = torch.cuda.is_available()` (HF Trainer raises `ValueError` on `bf16=True` without CUDA). The ADR-019 ModernBERT recipe locks bf16 on CUDA hosts; on CPU smoke runners the expected value is `False`. Test now asserts `args.bf16 is torch.cuda.is_available()`, matching the implementation's hardware-gated contract + the `build_training_args` docstring's "default: bf16 when CUDA available" comment. Test docstring documents the rationale. `import torch` placed inside the function (matches the pattern from `test_softmax_fp32_cast` / `test_sigmoid_fp32_cast` in the same file). Verified locally: full `test_training_primitives_smoke.py` -> 18/18 PASSED on CPU. Closes the `test-smoke (soft gate)` failure introduced at v1.1.2 (`a34128b`).

- **`.github/workflows/link-check.yml:48` (Markdown link check workflow; lychee v0.23.0 compat)** — lychee v0.23.0 removed the `--exclude-mail` CLI flag entirely; mailto: links are now excluded by default (opt-in via `--include-mail`). Verified by reading `lychee-bin/src/options.rs` at tag `lychee-v0.23.0`: only `include_mail: bool` exists, no `exclude_mail`. Deleted the `--exclude-mail` line; default behavior (mailto excluded) is preserved. Closes the `Markdown link check` workflow failure introduced at v1.1.4 (`d3f63d8`).

### Why CI was red for 5 patches (post-mortem note)

The 3 failures were each independently subtle:

- The mypy `plt.Axes` annotation was added at v1.1.3 as part of the Quarto writeup clarity rewrite (ADR-062); the local pre-commit hook used `mypy` without `--strict` while CI uses `--strict`, so the failure only surfaced on push.
- The bf16 test assertion worked on the development host (CUDA-enabled), and there was no CPU-runner regression test for `build_training_args` before the test was added at v1.1.2.
- The lychee `--exclude-mail` flag was valid in lychee v0.22.x; the lychee-action `lycheeVersion: v0.23.0` default rolled forward silently when v0.23.0 released.

Two compounding factors masked the red state: (a) the two visible reviewer-facing gates (Publish Quarto + Writeup numerical-claim audit) stayed green on every push, so the green PR notification fired even with red CI / Markdown jobs; (b) no patch in v1.1.x / v1.2.x had touched the failing files, so no commit in this session naturally triggered investigation. Future discipline: any patch close protocol should include a `gh run list --branch main --limit 5` check before tagging.

### References

- No new ADR (bug fixes, not methodology change). Precedent: v1.2.1 hygiene patch `74e7762` (gitignore patches) shipped without ADR; same pattern applied here.
- Predecessor: [v1.2.2](#v1-2-2) (ADR-066 + ADR-067 close)
- Reviewer URL pin (unchanged): `tree/v1.0.0` per [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md)
- Cost discipline (unchanged): cumulative project compute spend stays $17.08 per ADR-065 §E (within ADR-020 $200 hard cap; $0 GPU at v1.2.3)
- Live Quarto site: reflects v1.2.3 within ~2 min of push

## [1.2.2] — 2026-05-19 {#v1-2-2}

**Patch release**: library-first carryforward refactor + narrow immutability relaxation. Per [ADR-066](decisions/ADR-066-library-first-carryforward-refactor-v1-2-2.md) (library-first refactor) + [ADR-067](decisions/ADR-067-immutability-clarification-and-canonical-slug-reference.md) (narrow immutability relaxation for factual-typo fixes). Layered additively on v1.2.1 — no supersession of any prior ADR. Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033; live Quarto site reflects v1.2.2.

Discovery during execution: 5 of 6 refactor sites listed in ADR-066 §B were ALREADY consuming upstream primitives in prior v1.0.x carryforward sessions (per ADR-047 / ADR-056 / ADR-058). The remaining work was stale-annotation cleanup + ONE actual refactor (F6 left panel). Planned 4 source-refactor commits (3/9-6/9) consolidated into a single commit reflecting the actual scope.

### Added

- **`decisions/ADR-066-library-first-carryforward-refactor-v1-2-2.md`** — codifies the carryforward refactor methodology consuming 7 closed eval-toolkit upstream issues (#14 + #15 + #16 + #17 + #20 + #21 + #22). Pattern after ADR-047 / ADR-056 / ADR-058. §B1-B6 documents per-site mapping; §C visual-parity discipline; §D no-orphaned-code refactor commit hygiene; §E ledger updates; §F consequences.

- **`decisions/ADR-067-immutability-clarification-and-canonical-slug-reference.md`** — codifies a narrow exception to the CLAUDE.md ADR-immutability rule: factual typos in cross-reference slug filenames MAY be corrected in-place with a commit message citing ADR-067. ALL other content (numeric values, methodology, prose, alternatives, non-slug frontmatter) remains immutable. §B in-scope vs out-of-scope enumeration; §C 12 canonical-correct substitutions + 2 ADR-029 misattributions consolidated; §D CLAUDE.md / decisions/README.md updates.

- **`CLAUDE.md` immutability-rule clarification block** — Phase 0 workflow section gains the narrow-exception cite to ADR-067.

- **`decisions/README.md` Lifecycle section addendum** — same narrow-exception language as CLAUDE.md.

- **`docs/GLOSSARY.md` Immutability relaxation — factual-typo class entry** — cross-references ADR-067 §B's in-scope vs out-of-scope enumeration. Anchor link from the existing ADR entry.

### Changed

- **17+ broken ADR cross-reference slug filenames** corrected in-place per ADR-067 narrow relaxation across 9 immutable ADR files (ADR-046, ADR-048, ADR-054, ADR-055, ADR-056, ADR-057, ADR-059, ADR-060, ADR-063). 12 canonical-correct slug substitutions applied via batch sed. 1 ADR-029 misattribution at ADR-054:391 fixed via direct cite-to-CLAUDE.md replacement (no canonical-correct slug exists since "ADR-029 immutability" was a historical mis-citation; actual ADR-029 is about test markers).

- **`.lycheeignore` cleanup**: 14 patterns that were ignoring the broken slug refs deleted (no longer needed; refs now resolve cleanly). HF Hub bot-403 patterns + GitHub anchor false-positive patterns retained as those have a different rationale. Future broken-slug-refs should be FIXED IN-PLACE per ADR-067 — NOT added to `.lycheeignore`.

- **`src/eval/figures.py`** library-first stale-annotation cleanup + F6 actual refactor:
  - F1 / F2 / F5 header comments updated from "Project glue per ADR-046 Q6; pending upstream eval-toolkit issue #N" to "library-first via <primitive> (eval-toolkit #N closed; consumed at v1.0.x; ADR-066 §B<N> records the carryforward)"
  - File-level docstring table updated from "project glue (issue #N)" to "<primitive> (library-first; #N consumed v1.0.x/v1.2.2)" entries
  - F6 left panel: bare-matplotlib bars (`ax_left.bar(...)` + manual xtick rotation) replaced with `et.plot_metric_bars(per_fold_means, ax=ax_left, ...)` per #22 closure. The ONLY actual refactor in the v1.2.2 series; deleted hand-rolled code in same commit per no-orphaned-code invariant.

- **`src/eval/schemas.py::MDECellModel` docstring (line 336)** — stale "inline closed-form fallback pending upstream eval-toolkit issue #20" replaced with "eval-toolkit #20 closed; consumed at v1.0.x; ADR-066 §B5 records the carryforward".

- **`src/eval/cross_fold_ci.py:202` inline comment** — stale "inline impl pending upstream #21" replaced with "library-first via `eval_toolkit.block_bootstrap_on_folds` (eval-toolkit #21 closed; consumed at v1.0.x; ADR-066 §B6 records the carryforward)".

- **F1-F5 canonical figures re-rendered** via `make render-figures` post-refactor. SVG byte-sizes identical before/after (all 5 figures); diff is purely SVG-id auto-generation noise + `.meta.json` provenance update (new commit_sha pointing to the v1.2.2 refactor commit). ADR-locked caption discipline (random-floor annotation; CI-crossing-zero cue; N/A single-class label; subpanel mapping; ECE/Brier gloss) preserved verbatim. Per Q1 round-8 spirit-of-original threshold: comfortably cleared.

- **`decisions/upstream_issues.md`** ledger updates:
  - 7 existing rows (#14, #15, #16, #17, #20, #21, #22) Status column updated from "filed; awaiting upstream" → "**RESOLVED in eval-toolkit v0.42.0; consumed at v1.0.x or v1.2.2 per ADR-066 §B<N>**"
  - 1 new row appended for the v1.2.2 STRETCH contribution to eval-toolkit #36 (issue-comment + design-sketch posted at https://github.com/brandon-behring/eval-toolkit/issues/36#issuecomment-4490089572)

- **`SUBMISSION_AUDIT.md`** regenerates clean with 67 CLAIM rows (65 from v1.2.1 + ADR-066 + ADR-067).

### STRETCH — eval-toolkit #36 upstream contribution filed

Per Q2 round-8 Option B (issue-comment + design-sketch) + ADR-066 §B7: filed an [issue-comment](https://github.com/brandon-behring/eval-toolkit/issues/36#issuecomment-4490089572) on eval-toolkit #36 with this project's use case + concrete file:line citations (`src/eval/marginal_bootstrap.py:31-32,42-43,110` + `src/eval/calibration_battery.py:47-52`) + a proposed `with_ci=True` kwarg API sketch + an alternative scorecard-style design. P3 upstream priority ("ship if a consumer asks"); this comment is the project asking. v1.3.x consumption candidate if upstream lands the feature; no timeline pressure.

### References

- Closing ADRs: [ADR-066](decisions/ADR-066-library-first-carryforward-refactor-v1-2-2.md) + [ADR-067](decisions/ADR-067-immutability-clarification-and-canonical-slug-reference.md)
- Predecessor: [ADR-065](decisions/ADR-065-writeup-accuracy-narrative-and-callout-conventions.md) (v1.2.1 closing-polish)
- Library-first precedents: [ADR-047](decisions/ADR-047-phase-1-library-first-carryforward-refactor.md) + [ADR-056](decisions/ADR-056-binary-calibrator-refactor-and-platt-beta-narrow-supersession-of-adr-023.md) + [ADR-058](decisions/ADR-058-eval-from-hub-non-dry-run-body-narrow-supersession-of-adr-051-block-a.md)
- Reviewer URL pin (unchanged): `tree/v1.0.0` per [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md)
- Cost discipline (unchanged): cumulative project compute spend stays $17.08 per ADR-065 §E (within ADR-020 $200 hard cap; $0 GPU at v1.2.2)
- Live Quarto site: reflects v1.2.2 within ~2 min of push

## [1.2.1] — 2026-05-19 {#v1-2-1}

**Patch release**: narrative consistency + clarity + accuracy closing-polish
pass on top of v1.2.0. Per [ADR-065](decisions/ADR-065-writeup-accuracy-narrative-and-callout-conventions.md)
(layered additively on top of ADR-064 — no supersession). Reviewer URL pin
`tree/v1.0.0` unchanged per ADR-033; live Quarto site reflects v1.2.1.

Locked through 3 sequential `/exploring-options` rounds:

- **Round 3** (top-level scope): heavy pass on all three properties; every-number programmatic re-verification; Quarto callout-note "visual boxes" (not "TL;DR" per user directive); collapsible hyperparameter blocks for `WRITEUP/model-rungs.md`.
- **Round 5** (audit-script architecture): configurable `--strict` default + `--report-only` opt-out; project-internal (not upstream); on-demand local + CI hard-gate (no pre-commit hook); 7-commit hybrid cadence (Commit 4 splits into 4a + 4b + 4c).
- **Round 6** (execution mechanics): hybrid voice/tense scan (grep prefilter + spot-read + ADR-diff); Summary-box bullets distilled from `**Result**`-bolded sentences; strict swap of Commits 4a + 5 so Result-bolding lands before Summary-box distillation; cumulative-cost figure as `$17.08` with provenance footnote in ADR-065 §E.

### Added

- **`decisions/ADR-065-writeup-accuracy-narrative-and-callout-conventions.md`** — closing-polish ADR. §A Context (3 `/exploring-options` rounds; 11 locked decisions) + §B Accuracy-audit methodology (4 scan categories; `--strict` / `--report-only` flag; project-internal per Q2 round-5; CI hard-gate per Q3 round-5) + §C Quarto callout-note convention (3 callout types) + §D Narrative invariants (third-person voice; tense discipline; transitions; ADR-anchor) + §E Cumulative-cost canonical figure (`$17.08`; supersedes ADR-063's stale `$9.92`) + §F Consequences.

- **`scripts/audit_writeup_numbers.py`** (~290 LOC; project-internal per ADR-065 §B3) — programmatic numeric-claim audit on 12 reviewer-facing markdown surfaces. 4 scan categories: numbers + ADR slugs + version strings + URL slugs. Cross-checks dollar figures against `evals/cost_ledger.csv`; ADR slug refs against actual filenames in `decisions/`. Configurable `--strict` default + `--report-only` opt-out per Q1 round-5. Context-aware filters skip intentional broken-slug documentation patterns + historical cost figures whose +/-15-line context flags them as stale/superseded.

- **`.github/workflows/audit-writeup.yml`** — CI hard-gate per ADR-065 §B4. Runs default-strict on push to main + PR + weekly schedule. Mirrors lychee CI pattern from ADR-064 §C2. No pre-commit hook (matches ADR-064 §C2's "CI only; no local pre-commit hook to avoid contributor friction" discipline).

- **Canonical Quarto callout-note convention** (`docs/GLOSSARY.md` new section per ADR-065 §C) — 3-row table covering `:::{.callout-note}` Summary boxes (top of spoke; 3-5 bullets distilled from `**Result**` sentences), `:::{.callout-tip collapse="true"}` Hyperparameters (collapsible audit-detail), `:::{.callout-warning}` (caveats / limitations). "Summary" label (NOT "TL;DR" per Q3 round-3 user directive).

- **Canonical cumulative-cost figure** `$17.08` per ADR-065 §E — full precision $17.0807; sum of `actual_cost_usd` across 17 GPU-pod rows in `evals/cost_ledger.csv` as of v1.2.0 close commit `3212cc5`. Propagated to 3 places per Q3 round-4: ADR-065 §E authoritative + CHANGELOG [1.1.2] postscript patch (this commit; see below) + NEXT_STEPS.md §1.10 footnote.

- **`decisions/library_imports.md`** new "Audit tooling (project-internal; not a methodology primitive)" section — 4-script inventory table (audit_writeup_numbers + audit_leakage + audit_reference_scorers + regenerate_audit) with explicit `audit-tooling-not-primitive` / `audit-tooling-wrapping-library-primitive` / `audit-tooling-derived-artifact` tags per Q2 round-5 inventory invariant.

### Changed

- **Voice + tense + transitions pass** across 11 reviewer-facing surfaces (per ADR-065 §D + Q1 round-6 hybrid mechanism). 15 first-person hits converted to third-person prose (passive constructions; "this project" / "the harness" / "the test" referents); 0 future-tense hits remain. 3 transition sentences added at major section boundaries: WRITEUP/eval-design.md §5.2 → §5.4 (signposts §5.3 lives in its own spoke per ADR-025); WRITEUP/limitations-and-future-work.md §8.2 → §9.1 (signposts shift from defensible scope to experimental dead-ends); WRITEUP/limitations-and-future-work.md §9.4 → §11 (signposts shift to process lessons).

- **Hand-picked `**Result**` bolding** on 7 WRITEUP spokes (per Q5 round-4 lock; closes deferred Q3 round-1 lock from v1.2.0). 11 new bolds across data-decisions + eval-design + methodology-guarantees + reference-scorer-audit + reproducibility + threshold-policy. `WRITEUP/model-rungs.md` already had 5 `**Result**` bolds from v1.2.0 (per ADR-064 §B5).

- **Top-of-spoke `:::{.callout-note}` Summary boxes** added to all 8 WRITEUP spokes per ADR-065 §C1. Each Summary distills 3-5 bullet headline takeaways from existing `**Result**`-bolded subsection sentences (uniform source-strategy per Q2 round-6).

- **Collapsible `:::{.callout-tip collapse="true"}` Hyperparameter blocks** in WRITEUP/model-rungs.md §4.1 (TF-IDF + LR), §4.2 (Frozen probe — ModernBERT-base + revision SHA), §4.3 (LoRA — r/alpha/dropout/target_modules/PEFT config) per ADR-065 §C2. Reader sees a brief detector overview + can expand for hyperparameter detail. Audit-detail content preserved either way (GH blob fallback renders expanded with `:::` fences visible; acceptable per ADR-030 Quarto-as-canonical-surface).

### Postscript patch to [1.1.2] (canonical cumulative-cost figure)

The CHANGELOG `[1.1.2]` v1.1.4 postscript already flagged the stale `$9.92` cumulative-cost figure from ADR-063 but did not compute the canonical value. v1.2.1 Commit 2 patches the v1.1.4 postscript with a new sub-postscript that quotes the canonical `$17.08` (per ADR-065 §E provenance) — supersession via postscript chain since ADR-063 itself remains immutable per CLAUDE.md ADR-discipline.

### Out of scope (still deferred)

- 17 historical broken ADR slug refs in immutable ADRs (flagged in ADR-064 §D + `.lycheeignored`; ADR-immutability discipline preserved; future patches may add an "immutability clarification ADR").
- Pre-v1.1.4 CHANGELOG entries' "ADR-029 immutability" misattribution (historical narrative; corrected at v1.1.4+ onwards).

### References

- Closing ADR: [ADR-065](decisions/ADR-065-writeup-accuracy-narrative-and-callout-conventions.md).
- Predecessor: [ADR-064](decisions/ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md) (additive layer).
- Cost discipline (unchanged): [ADR-020](decisions/ADR-020-compute-infrastructure-and-cost-discipline.md) `$200` hard cap; current cumulative $17.08 well within.
- Reviewer URL pin (unchanged): `tree/v1.0.0` per [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md).
- Live Quarto site: reflects v1.2.1 within ~2 min of push.

## [1.2.0] — 2026-05-19 {#v1-2-0}

**Minor release**: heavy writeup-clarity pass + dedicated hiring-manager landing
page. Third (and final) stage of the v1.1.3 → v1.1.4 → v1.2.0 clarity-and-
consistency series. Per [ADR-064](decisions/ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md)
(layered additively on top of ADR-062 — no supersession).

Triggered by 2026-05-19 user feedback that the v1.1.1 navigation pass left the
writeup *"jargon heavy and dense and pretty unreadable to a hiring manager —
doesn't demonstrate clear thought."* Then expanded: *"take a broad look over
everything ... to make sure we are consistent throughout the guide."*

### Added

- **`decisions/ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md`**
  (NEW) — codifies the polish layer + documentation-wide consistency invariants.
  §A context; §B clarity decisions; §C consistency invariants (canonical
  terminology table); §D known errors in prior immutable ADRs flagged
  (7 broken slug refs + 1 stale cumulative-cost figure in ADR-046/048/059/060/063);
  §E consequences.
- **`docs/for-hiring-managers.md`** (NEW) — ~250 words, 4-question format
  (problem / found / trust / how the candidate thinks). Reachable from navbar
  Reference dropdown + `index.qmd` "Read Next" (first entry).
- **`RESULTS.md` §1B** "Ablation: does a longer-context backbone fix the OOD
  gap?" — full per-strategy DeBERTa table + "what shows / does not show" pair
  + backbone-dominant interpretation. Resolves the previously-broken
  `WRITEUP/limitations-and-future-work.md:161` → RESULTS §1B anchor.
- **`docs/GLOSSARY.md` Canonical terminology conventions** — 9-row table
  documenting the prose-vs-identifier split. Plus 3 new entries (Ablation,
  Confound, Rung / detector clarifier).
- **`decisions/library_imports.md` Phase 4+ inference deps** — inventories
  the deferred-from-v1.1.2-Phase-B `src/inference/windowed.py` primitives.
- **8-spoke "How to read this spoke" signposts** — every WRITEUP/*.md spoke
  gains a blockquote after the v1.1.1 back-link telling skimmers vs auditors
  where to look.

### Changed

- **F1/F2/F5 SVG axis-label rebuild** — F1 random-floor legend gains
  derivation `(0.374 = 412/1101 prevalence)`; F2 xlabel adds CI-crossing-zero
  cue; F5 ylabel inlines ECE + Brier definitions. F3/F4 unchanged (already
  adequate). SVGs + .meta.json sidecars regenerated.
- **RESULTS.md** — top-of-page "How to read this page" blockquote; §1 AUPRC
  table pre-context blockquote; §7 Raw Artifacts hiring-manager-facing intro;
  F1-F5 caption prose refinements.
- **`index.qmd`** — Pooled OOD footnote under headline table (5 OOD sources
  enumerated + random floor derivation + CI-width-as-noise-floor cue);
  "Read Next" gains the hiring-manager landing as the first link.
- **`WRITEUP.md`** line 13-14: LODO inline gloss; canonical prose triad
  "frozen-probe / LoRA / full-FT"; rung↔detector clarifier with GLOSSARY link.
- **`WRITEUP/limitations-and-future-work.md` §9.2** — DeBERTa ablation status
  updated with v1.1.2 execution result + backbone-dominant interpretation +
  residual-confounds disclaimer.
- **`WRITEUP/model-rungs.md`** — signpost includes inline rung↔detector
  clarifier.
- **`_quarto.yml`** — navbar Reference dropdown adds hiring-manager landing
  as first menu entry.
- **`NEXT_STEPS.md` §1.10** — Status (v1.2.0) paragraph appended.
- **`.lycheeignore`** — extended with 12 patterns covering stale ADR slug
  refs in immutable historical ADRs (canonical-correct slugs in ADR-064 §D
  + [1.1.2] postscript). Lychee CI now passes despite the flagged-not-fixed
  residual refs.
- **`SUBMISSION_AUDIT.md`** — regenerated; 64 CLAIM rows (CLAIM-064 added
  for ADR-064).
- **Stale ADR slug refs in CHANGELOG history** — 10+ historical CHANGELOG
  entries that cited ADRs with stale slug paths now resolve correctly
  (ADR-005, ADR-013, ADR-016, ADR-019, ADR-023, ADR-029, ADR-032, ADR-037,
  ADR-046 — full mapping in the `sed` batch documented in commit `ee2b33f`).

### Coordination

This v1.2.0 release closes the 3-stage series. The doc-agent's ADR-062 work
was committed as the v1.1.3 baseline; v1.1.4 added the documentation-wide
consistency fix-pack + lychee CI prophylaxis; v1.2.0 lands the heavy clarity
polish + hiring-manager landing page. Total: 12 commits across the three
stages. Reviewer URL pin `tree/v1.0.0` unchanged per ADR-033. Live Quarto
site reflects v1.2.0.

### References

- ADR-064 (NEW): clarity polish + consistency invariants.
- ADR-062 (v1.1.3 baseline): structural writeup rewrite layered-on.
- ADR-060 + ADR-063: DeBERTa methodology + execution; cited from RESULTS
  §1B + WRITEUP §9.2 + hiring-manager landing.
- CLAUDE.md: project ADR-discipline (the actual immutability rule source;
  older CHANGELOG entries misattribute to "ADR-029"; that historical drift
  is documented in ADR-064 §D).

---

## [1.1.4] — 2026-05-19 {#v1-1-4}

**Patch release**: documentation-wide consistency fix-pack +
markdown-link-checker CI prophylaxis. Second of a three-stage
clarity-and-consistency series (v1.1.3 baseline → v1.1.4 consistency
→ v1.2.0 heavy clarity pass + hiring-manager landing).

Triggered by 2026-05-19 full-repo markdown audit (Stage 2 Commit 1 of
the v1.1.3→v1.2.0 plan at `/home/brandon_behring/.claude/plans/i-find-that-the-toasty-puppy.md`).
The audit scanned every reviewer-facing markdown surface plus
previously-unscanned areas (SPEC_SHEET, SPEC_GREENFIELD, docs/research/,
notebooks/*.py, .github/workflows/, HF Hub model card output).
Findings: 7 broken ADR slug references in immutable ADR files +
2 broken ADR slug refs in CHANGELOG (fixable) + 1 stale ADR-count
claim in SPEC_SHEET + 2 stale version references in NEXT_STEPS +
1 stale `v1.0.x submission` comment in `notebooks/01_canonical_results.py`.
The 7 immutable broken refs are recorded in the CHANGELOG `[1.1.2]`
Postscript for reader-visibility; the others are patched here.

### Fixed

- **`CHANGELOG.md` [1.1.2] References** — corrected 2 broken ADR slug
  refs: `ADR-006-headline-metrics-and-statistical-apparatus.md` →
  `ADR-006-headline-metrics-and-statistical-apparatus.md`;
  `ADR-020-compute-infrastructure-and-cost-discipline.md` →
  `ADR-020-compute-infrastructure-and-cost-discipline.md`.
- **`SPEC_SHEET.md`** frontmatter — `53 ADRs accepted across Phase 0-00
  through v1.0.4 close` → `63 ADRs accepted through v1.1.3` with
  v1.1.x landmark closes called out (ADR-059 / ADR-060 / ADR-061 /
  ADR-062 / ADR-063).
- **`NEXT_STEPS.md`** §2.4 title + trigger — `(v1.1.1+)` →
  `(v1.2.0+)`; stale `v1.1.1 polish patch` reference updated with
  a clarifying note that the v1.1.1 slot was consumed by ADR-061
  (Quarto navigation restructure) and that the v1.1.3 canonical-figures
  rewrite (ADR-062) already adopted several library primitives.
- **`notebooks/01_canonical_results.py`** line 19 — `v1.0.x submission`
  prose comment → version-neutral `canonical submission`.

### Added

- **`.github/workflows/link-check.yml`** (NEW) — `lycheeverse/lychee-action@v2`
  workflow scanning reviewer-facing + governance markdown surfaces on
  push to main, pull-request to main, and weekly schedule (MON 09:00
  UTC). Fails the build on push/PR drift; auto-files a `documentation`+`link-rot`
  GitHub issue on scheduled-run drift (URL rot is not a merge-blocker
  but should be tracked). Caches link-check results for 1 day to keep
  CI fast.
- **`.lycheeignore`** (NEW) — pattern allowlist for verified-good URLs
  that 403 unauthenticated bots (e.g., HF Hub model pages) and GitHub
  blob/tree URLs with fragment anchors (lychee's HTML fragment check
  produces false positives because GitHub generates slug-cased anchors
  at render time; Quarto's own link-checker covers anchor refs at site
  render via `make site`).

### Postscript (in CHANGELOG `[1.1.2]`)

Added inline below the v1.1.2 References block. Documents the 7 broken
ADR slug refs in immutable ADRs (ADR-046:15,195; ADR-048:16,194;
ADR-059:47; ADR-060:64; ADR-063:60,62,268,274) that cannot be edited
per the project ADR-discipline (CLAUDE.md: "ADRs are immutable;
supersede via new ADR"). Canonical-correct slugs listed inline so
readers who hit a 404 from in-ADR cross-refs can find the right
target. Also flags ADR-063's stale cumulative-cost figure
(`$9.92`) and directs readers to `evals/cost_ledger.csv` for the
canonical sum.

### Coordination

This release intentionally ships NO clarity-prose changes (those are
v1.2.0 work). v1.1.4 is purely documentation hygiene + prophylaxis.
v1.2.0 (next) lands the heavy clarity pass (jargon glossing invariant,
figure caption refinements with SVG axis-label fixes, 8-spoke skim
signposts, DeBERTa §1B ablation callout, dedicated hiring-manager
landing page).

### References

- Audit findings: full-repo markdown audit (Stage 2 Commit 1 of the
  v1.1.3→v1.2.0 plan; audit work product captured in-session, not
  committed).
- CLAUDE.md project ADR-discipline (explains why the 7 broken refs in
  immutable ADRs must be flagged-not-fixed; older CHANGELOG entries
  cite "ADR-029" but the actual ADR-029 is about test markers — the
  immutability rule lives in CLAUDE.md).
- ADR-033 (reviewer URL pin `tree/v1.0.0` unchanged; live Quarto site
  reflects v1.1.4).
- Pre-existing CI: `ci.yml` (pre-commit + tests + audit) + `publish.yml`
  (Quarto render + GH Pages deploy). New `link-check.yml` is
  orthogonal.

---

## [1.1.3] — 2026-05-19 {#v1-1-3}

**Patch release**: ADR-062 Quarto writeup clarity rewrite — the first
of a three-stage clarity-and-consistency series (v1.1.3 baseline →
v1.1.4 consistency-only fix-pack → v1.2.0 heavy clarity pass +
hiring-manager landing). Triggered by 2026-05-19 user feedback that
the v1.1.1 navigation pass left the writeup *"jargon heavy and dense
and pretty unreadable to a hiring manager. Doesn't demonstrate clear
thought."*

This release is a bundled commit of the parallel doc-rewrite work
authored per [ADR-062](decisions/ADR-062-quarto-writeup-clarity-and-canonical-figures.md).
The doc-agent had ~85% of the rewrite landed in working tree at
v1.1.2 close; v1.1.3 packages that progress as a single coherent
release so the subsequent v1.1.4 (consistency fixes) and v1.2.0
(heavy pass) layers can build on a clean baseline.

### Added

- **`decisions/ADR-062-quarto-writeup-clarity-and-canonical-figures.md`**
  — codifies the problem-first narrative, plain-language metric
  glossing, "what each figure says AND does not say" caption
  discipline, the five-canonical-figures slate (F1–F5; F6/F7
  removed), and methodology-below-the-fold restructuring.

### Changed

- **`index.qmd`** — leads with problem → result → limits (above the
  fold = 1-paragraph thesis + headline AUPRC table + 5-bullet
  plain-language meaning + 3 obvious drill-down links).
- **`EXECUTIVE_SUMMARY.md`** — one-page executive summary with a
  "How To Read The Metrics" section defining AUPRC / AUROC / FPR /
  ECE / 95% CI for a non-ML reader.
- **`RESULTS.md`** — Metric Primer in §1 explaining AUPRC's random
  floor before the table; "What F# shows / What F# does not show"
  caption discipline added for F1–F5.
- **`WRITEUP.md`** — 2-paragraph hub-spoke primer reframing the
  cover narrative; explicit signposting that the GitHub blob view
  is executive-summary depth and full methodology requires all 8
  spokes.
- **`README.md`** — "How to read this submission" rewritten with
  3 named reading paths (5 min / 60 min / 30 min CPU reproduce).
- **`READING_GUIDE.md`** — three reader-type paths (hiring manager /
  technical reviewer / reproduce) with explicit time budgets.
- **`docs/GLOSSARY.md`** — expanded to cover ADR / AUPRC / AUROC /
  ECE / FPR / LODO / OOD / Pooled OOD / PR-AUC / ROC-AUC / recall.
- **`_quarto.yml`** — navbar Methodology dropdown houses hub +
  reading guide + 8 spokes; sidebar nests them visibly.
- **`docs/plots/F1-F5.{svg,meta.json}`** — regenerated from
  canonical eval artifacts (not synthetic scaffolds). Provenance
  sidecars record `data_mode: canonical`, ADR-062, commit SHA,
  generation timestamp, and source artifact paths.
- **`scripts/render_figures.py`** + **`src/eval/figures.py`** —
  reviewer-facing slate is F1–F5 only; synthetic scaffold rendering
  is test-only and cannot write to `docs/plots/`.
- **`tests/smoke/test_figures_smoke.py`** +
  **`tests/smoke/test_phase4_scripts_smoke.py`** — updated for the
  F1–F5 slate change.
- **`Makefile`** smoke target — comment update aligning with the
  F1–F5 test-only scaffold path.
- **`decisions/library_imports.md`** — adds
  `eval_toolkit.plotting.plot_slice_metric_heatmap` entry (used in
  F3) + ADR-062 cross-references for plot_lift_ci + save_figure +
  set_plot_style consumers.

### Removed

- **`docs/plots/F6.{svg,meta.json}`** + **`docs/plots/F7.{svg,meta.json}`**
  — removed from the reviewer-facing slate per ADR-062 (figures F6
  and F7 from the original Phase 4 plan covered diagnostic content
  that didn't earn a place in the hiring-manager-first narrative).

### Coordination

This release is a **bundled commit** of the in-progress doc-agent
work. v1.1.4 (next) lands the documentation-wide consistency fix-pack
(broken ADR slug links, stale version refs, cumulative-cost
correction, CI link-checker prophylaxis). v1.2.0 lands the heavy
clarity pass (jargon glossing invariant, figure caption refinements
with SVG axis-label fixes, 8-spoke skim signposts, DeBERTa §1B
ablation callout, dedicated hiring-manager landing page).

### References

- ADR-062 (NEW; this release): writeup clarity rewrite + canonical
  figure slate.
- Reviewer URL pin: `tree/v1.0.0` unchanged per
  [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md).
  Live Quarto site reflects v1.1.3.

---

## [1.1.2] — 2026-05-19 {#v1-1-2}

**Patch release**: closes the
[ADR-060](decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md)
DeBERTa-v3-base medium-ablation execution landing condition. The
methodology lock landed at v1.1.0 with `[v1.1.1 execution]` body
wording, but that slot was consumed by [ADR-061](decisions/ADR-061-quarto-site-navigation-restructure.md)
(Quarto navigation restructure) so execution carried forward to v1.1.2.
ADR-060 stays immutable; commit messages document the slot shift.

### Headline result

Per-cell metrics at `evals/metrics/per_cell_deberta.parquet` (epoch=2;
4 single-class slices skipped per ADR-006):

| strategy | jbb_behaviors AUPRC | xstest AUPRC | pooled_ood AUPRC |
|---|---:|---:|---:|
| `chunk_and_average` | 0.4855 | 0.3966 | 0.2912 |
| `head_truncation` | 0.4890 | 0.3912 | 0.2895 |

The 2 truncation strategies produce **essentially identical** metrics
across the 5-slice OOD slate — a publishable null result. By the
ADR-060 confound-control interpretation, this indicates the ModernBERT
advantage on the headline ladder is **backbone-dominant**, not
context-window-dominant; long-context (chunk-and-average) provides
no measurable benefit over head-truncation on this slate.

### Added

- **`src/training/load_backbone.py`** (NEW; replaces
  `src/training/load_modernbert.py`) — generic
  `load_backbone(*, hf_id, revision, num_labels=2, attn_impl_preferred,
  event_logger, torch_dtype=torch.bfloat16)` accepting an arbitrary HF
  Hub backbone identifier. The flash-attn-fallback recipe (per
  ADR-020) + `flash_attn_fallback` event emission are unchanged.
  DeBERTa-v3-base loads with `torch_dtype=torch.float32` to avoid the
  known bf16 + disentangled-attention numerical-instability
  (loss=0 + grad_norm=NaN from step 1).

- **`src/inference/windowed.py`** (NEW) — chunk-and-average +
  head-truncation truncation strategies for the ADR-060 ablation.
  Uses HF tokenizer's native sliding-window protocol
  (`return_overflowing_tokens=True` + `stride`) — no hand-rolled
  window-stride arithmetic. Reuses `src.training.softmax_cast.softmax_fp32`
  for ADR-019 numerical stability. 15 mocked-only smoke tests in
  `tests/smoke/test_windowed_inference_smoke.py`.

- **`scripts/run_deberta_ood_inference.py`** (NEW) — standalone OOD
  inference for the ADR-060 ablation. Iterates both strategies; loads
  the epoch-2 final checkpoint; dispatches each OOD slice through
  `predict_with_strategy`. Writes the 10 per-(strategy, slice)
  parquets at `evals/predictions/deberta_v3_base_<strategy>__fold0__
  seed42__<slice>.parquet`. Designed as a narrow companion to
  `run_inference_battery.py` rather than overloading the
  ModernBERT-shaped orchestrator (DeBERTa checkpoints have an extra
  strategy nesting level the existing iteration doesn't recognise).

- **`evals/metrics/per_cell_deberta.parquet`** (NEW) — aggregated 6
  cells via `make eval-deberta-v3` (run_metrics_battery.py with
  `--epoch-filter 2 --rung-pattern deberta_v3_base`); 4 single-class
  slices (iid + bipia + injecagent + notinject) correctly skip per
  ADR-006.

### Changed

- **`src/training/train_modernbert.py`** — `prepare_model` adds
  `backbone_hf_id` + `torch_dtype` kwargs; `train_one_cell` reads
  `cfg["training"]["bf16"]/["fp16"]/["learning_rate"]/["num_train_epochs"]`
  YAML overrides + threads them to `prepare_model` +
  `build_training_args`. Per-strategy `rung_id` distinguishing for
  downstream metrics aggregation (`f"{rung_id_base}_{strategy}"` for
  non-native truncation). `VALID_RUNG_NAMES` + `VALID_TRUNCATION_STRATEGIES`
  constants added.

- **`src/training/training_args.py`** — `build_training_args` accepts
  `learning_rate`/`num_train_epochs`/`bf16`/`fp16` optional overrides.
  None preserves ADR-019 ModernBERT defaults; explicit `bf16=False +
  fp16=False` selects fp32 (DeBERTa path).

- **`scripts/train_rung.py`** — `--rung` choices switched from
  `VALID_CLASSIFIER_TYPES` to `VALID_RUNG_NAMES` (adds
  `deberta_v3_base`). New `--truncation-strategy` CLI override.

- **`scripts/run_metrics_battery.py`** — new `--epoch-filter INT` arg.
  When set, restricts aggregation to that epoch BEFORE groupby.
  Default `None` preserves pre-v1.1.2 ModernBERT behaviour.

- **`Makefile`** — wired 3 DeBERTa targets (`train-deberta-v3`,
  `eval-deberta-v3`, `deberta-ablation`). The orchestration target
  fires both strategies via `--var truncation_strategy=...` (NOT shell
  env var; runpod-deploy uses `{KEY}` template-variable expansion),
  reuses the warm pod via `lifecycle.on_success: recycle`, then
  explicitly stops the pod (no per-fire `on_success` CLI override flag
  in runpod-deploy v0.8.4) and aggregates metrics.

- **`configs/rungs/deberta_v3_base.yaml`** — pinned backbone revision
  `8ccc9b6f36199bec6961081d44eb72fb3f7353f3` (live SHA from
  `huggingface_hub.HfApi.model_info`); switched `bf16: true → false`
  (DeBERTa-v3 numerical stability); `checkpoint_dir_template` stripped
  of the `evals/checkpoints/` prefix to avoid path doubling against
  `train_rung.py --checkpoint-root` default.

- **`configs/runpod/headline-deberta.yaml`** — brought to schema
  parity with `headline-frozen_probe.yaml` (the v1.1.0 scaffold was
  incomplete: missing staging/preflight blocks + wrong setup shape).
  All working files (project + HF cache + secrets + run scripts +
  logs) moved off `/workspace` (FUSE) to `/root` (container overlay
  disk) per the `fuse-workspace-needs-uv-link-mode-copy` memory entry,
  re-extending the X8 venv-on-/root workaround to all writable paths.
  Staging excludes broadened (evals/audit + evals/manifests + WRITEUP/
  + docs/ + decisions/ + analysis/ + _site/ + artifacts/ + notebooks/
  + tests/) to reduce upload time + sidestep concurrent-writer
  collisions with the in-flight doc-rewrite work. Truncation strategy
  flows via `{truncation_strategy}` template variable +
  `runpod-deploy run --var truncation_strategy=...` CLI flag.

- **`pyproject.toml`** + **`uv.lock`** — added `sentencepiece>=0.2` +
  `protobuf>=4.0` (both required by transformers' DeBERTa-v3
  AutoTokenizer load path; transformers' `SentencePieceExtractor`
  needs protobuf to parse `spm.model` independently from sentencepiece
  itself).

- **`evals/cost_ledger.csv`** — appended 9 Phase D pod rows
  (`pid-deberta-2026051*`) totalling **$1.34** actual GPU spend.
  Well under ADR-060 $5-7 expected envelope; well under ADR-020 $25
  per-job soft cap. Cumulative project spend: $9.92 / $200 hard cap.

- **`NEXT_STEPS.md`** §1.10 — Status (v1.1.2) appended with the
  per-strategy headline + null-result interpretation.

### Fixed (v1.1.2 Phase D fix-cycle)

Eight sub-commits before the closing commit cleared a cascade of
infrastructure errors:

1. **`83fd348`** — added `sentencepiece` dep (DeBERTa-v3 tokenizer).
2. **`99501ba`** — narrowed staging excludes (later superseded by
   `33387b5`; kept for audit trail).
3. **`33387b5`** — moved `/workspace` (FUSE) → `/root` (overlay disk)
   for project + HF cache + secrets + scripts + logs (the FUSE
   workaround was the load-bearing rsync-stability fix).
4. **`f660f76`** — added `protobuf` dep (second tokenizer-import
   error after sentencepiece).
5. **`60fdc53`** — bound `truncation_strategy` in
   `checkpoint_dir_template.format()` (the v1.1.2 Phase C2 dispatch
   missed this format site).
6. **`aa91067`** — DeBERTa fp32 + YAML-driven training hyperparams
   (the load-bearing numerical-stability fix; locally validated via
   forward+backward before re-firing GPU).
7. **`67679a5`** — fixed checkpoint path doubling (template prefix
   conflicted with `checkpoint_root` default); dropped the FUSE
   staging-bounce (no longer needed on /root).

### References

- Methodology lock: [ADR-060](decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md).
- Cost discipline: [ADR-020](decisions/ADR-020-compute-infrastructure-and-cost-discipline.md).
- Single-class slice handling: [ADR-006](decisions/ADR-006-headline-metrics-and-statistical-apparatus.md).
- Reviewer URL pin: `tree/v1.0.0` unchanged per
  [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md).
  Live Quarto site reflects v1.1.2.

### Postscript (added in v1.1.4)

Documentation-consistency audit at v1.1.4 surfaced **7 broken ADR slug
references** in immutable ADR files (cannot be edited per the
project ADR-discipline; CLAUDE.md states: "ADRs are immutable;
supersede via new ADR"). Canonical-correct slugs documented here for
readers who hit a 404 when clicking the in-ADR cross-refs:

- ADR-006 actual filename: `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md`
  - Broken refs in: ADR-046:15,195; ADR-048:16,194 (cite as
    `ADR-006-headline-metrics-and-statistical-floor.md`); ADR-063:60,268
    (cite as `ADR-006-headline-metrics-and-statistical-apparatus.md`).
- ADR-020 actual filename: `decisions/ADR-020-compute-infrastructure-and-cost-discipline.md`
  - Broken refs in: ADR-059:47; ADR-060:64; ADR-063:62,274 (all cite as
    `ADR-020-compute-infrastructure-and-cost-discipline.md`).

ADR-063 also contains a stale cumulative-cost figure: `$9.92 /
ADR-020 $200 hard cap`. The v1.1.2 GPU spend is correctly cited
elsewhere as `$1.34`. Cumulative cost across the full
`evals/cost_ledger.csv` is higher than $9.92 (the figure in ADR-063 was
calculated from a subset of pod rows); future v1.x patches should
consult `evals/cost_ledger.csv` for the canonical sum rather than
re-quote ADR-063's figure.

These errors are recorded in [ADR-064](decisions/ADR-064-writeup-hiring-manager-clarity-and-consistency-pass.md)
§D (lands at v1.2.0). The CI markdown-link-checker introduced at
v1.1.4 (lychee pre-commit hook) prevents recurrence of the slug-link
class of errors going forward.

### Postscript (added in v1.2.1; canonical cumulative-cost figure)

ADR-064 §D flagged the stale `$9.92` cumulative-cost figure but did not
compute the canonical value. [ADR-065](decisions/ADR-065-writeup-accuracy-narrative-and-callout-conventions.md)
§E (lands at v1.2.1) records the canonical figure:

> Canonical cumulative project compute spend as of v1.2.0 close: **`$17.08` USD**
> (full precision `$17.0807`; sum of `actual_cost_usd` across 17 GPU-pod rows in
> `evals/cost_ledger.csv` as of commit `3212cc5`, 2026-05-19). Within ADR-020's
> `$200` hard cap.

Readers consulting ADR-063's `$9.92` figure are directed to ADR-065 §E
for the canonical value. ADR-063 itself remains immutable per CLAUDE.md
ADR-discipline; the supersession is expressed via this postscript chain.
v1.2.1 also introduces `scripts/audit_writeup_numbers.py` + a CI hard-gate
at `.github/workflows/audit-writeup.yml` that prevents recurrence of the
stale-figure class of drift going forward.

---

## [1.1.1] — 2026-05-19 {#v1-1-1}

**Patch release**: Quarto site navigation restructure — landing-page
rebuild + navbar consolidation + sidebar hub-spoke nesting + hub-spoke
signposting. **No methodology content changed** — pure navigation +
discoverability fix per [ADR-061](decisions/ADR-061-quarto-site-navigation-restructure.md)
(narrow supersession of [ADR-053](decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md)
navigation dimension 1; dimensions 2-5 preserved).

Triggered by 2026-05-19 user feedback: *"the quatro documents they
seem really confusing and hard to follow, the whole points was them
to be a cleaner version. ... it isn't immdiately clear to me where
to find the results and explanations in clear language about wha
they mean."*

The reading-guide content displaced from `index.qmd` (3 reading
paths + 14 headline ADRs + repo map + submission anchors + 5
technical-interpretation patterns) moves to a new `READING_GUIDE.md`
page accessible from the Methodology dropdown but no longer
crowding the landing page.

### Added

- **`decisions/ADR-061-quarto-site-navigation-restructure.md`** —
  narrow supersession of ADR-053 dimension 1 (navbar/sidebar/landing
  architecture). Documents the 6 subsection changes (navbar 9→5 +
  sidebar hub-spoke nesting + index rebuild + WRITEUP primer + 8
  spoke back-links + README clarification) + dimensions 2-5 of
  ADR-053 preserved.

- **`READING_GUIDE.md`** (NEW) — receives the reading-guide content
  displaced from `index.qmd`: 3 named reading paths (A1 quick-skim /
  A2 audit / A3 reproduce), 14 headline ADRs, repo TOC, submission
  anchors, status, and the full technical version of the 5
  interpretation patterns.

### Changed

- **`_quarto.yml`** — navbar consolidated from 9 top-level items to 5
  (Results / Methodology dropdown / Decisions / Reference dropdown /
  Repo external link). The single Methodology dropdown carries the
  hub (`WRITEUP.md`) + reading guide (`READING_GUIDE.md`) + all 8
  spokes. Sidebar restructured with 2-level nesting: "Methodology >
  Detailed spokes (8 topics) > ..." so the hub-spoke relationship is
  visible at-a-glance.

- **`index.qmd`** — rebuilt from 137 lines to ~85 lines (results +
  meaning ONLY). Above the fold: 1-paragraph thesis + headline
  finding table + 5-bullet plain-language interpretation + 3 obvious
  drill-down links. The full technical interpretation pedagogy +
  reading paths + ADR shortlist + repo map move to READING_GUIDE.md
  (one click away).

- **`WRITEUP.md`** — 2-paragraph hub-spoke primer inserted
  immediately after the title (before the existing reading-guide
  table). Reframes the cover narrative as INTENTIONAL and signposts
  that the GitHub blob view alone is executive-summary depth; the
  full methodology requires all 8 spokes.

- **`WRITEUP/data-decisions.md`** + **`model-rungs.md`** +
  **`eval-design.md`** + **`threshold-policy.md`** +
  **`reference-scorer-audit.md`** + **`methodology-guarantees.md`** +
  **`limitations-and-future-work.md`** + **`reproducibility.md`** —
  each gains a 1-line back-link at the top: *"Part of the [WRITEUP
  methodology](WRITEUP.md) — see the hub for the cover narrative
  + reading guide."*

- **`README.md`** — "Reading paths" section rewritten as "How to
  read this submission" with explicit Quarto-vs-GitHub guidance: the
  GitHub blob view of `WRITEUP.md` is only the cover narrative; the
  live Quarto site is the canonical reading surface with hub + 8
  spokes + nested navigation. Three named reading paths (5 min / 60
  min / 30 min CPU reproduce).

- **`decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md`**
  frontmatter — `superseded_by: ["054", "061"]` (narrow supersessions
  of dimension 1 only; dimensions 2-5 unchanged).

- **`SUBMISSION_AUDIT.md`** — regenerated; 61 CLAIM rows total
  (ADR-061 added).

### References

- Supersedes (narrow, navigation dimension only): [ADR-053](decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md).
- Preserves: ADR-053 dimensions 2 (3-reading-paths; now in
  READING_GUIDE.md), 3 (headline-finding-block; preserved on
  index.qmd), 4 (interpretation pedagogy; 5-bullet plain-language
  on index.qmd + full technical version in READING_GUIDE.md), 5
  (pointer convention; markdown links unchanged). Also preserves
  ADR-054 (RESULTS as 3rd entry artifact; default landing-page link
  unchanged).
- Reviewer URL pin: `tree/v1.0.0` unchanged per [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md).
  Live Quarto site reflects v1.1.1.

---

## [1.1.0] — 2026-05-19 {#v1-1-0}

**Minor release**: closes the runpod-deploy modernization track (config
schema migration + v0.7.7→v0.8.4 PyPI switch + shim drop + 7 upstream
issues consumed) **and** lands the DeBERTa-v3-base medium ablation
**methodology lock** (ADR-060) with infrastructure scaffolds.
Execution of the DeBERTa GPU fire is deferred to v1.1.1 per the
/exploring-options 2026-05-19 **Path B** scope-mismatch resolution
(existing training pipeline is ModernBERT-specific; loader refactor +
windowed-inference module + eval-pipeline integration must precede
any GPU fire).

v1.1.0 ships as 3 sequenced commits per /exploring-options 2026-05-19
Q5 lock (each independently CI-green-able + revertible):

1. `refactor: v1.1.0 prep — migrate 3 headline-* configs from legacy
   stop: to lifecycle: schema` (6741fe4).
2. `feat: v1.1.0 — runpod-deploy v0.7.7→v0.8.4 PyPI switch + shim drop
   + #88/#90/#97 + ADR-059` (7c66222).
3. `feat: v1.1.0 — DeBERTa-v3-base methodology lock (ADR-060) + Path B
   infrastructure scaffolds + RESULTS §1B placeholder + governance
   close (execution deferred to v1.1.1)` (this commit).

### Added

- **`decisions/ADR-059-runpod-deploy-pypi-install-narrow-supersession-of-adr-036.md`**
  — runpod-deploy installs from PyPI at v0.8.4+; narrow supersession
  of ADR-036 "git URL is the only viable spec format" sub-claim for
  runpod-deploy. Mirrors the [ADR-055](decisions/ADR-055-eval-toolkit-pypi-install-narrow-supersession-of-adr-036.md)
  pattern for eval-toolkit. research_toolkit retains git+https
  (not yet on PyPI). Tag-pin discipline + freeze policy + bump-triggers
  + uv.lock backstop all preserved.

- **`decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md`**
  — DeBERTa-v3-base medium ablation methodology lock. Single fold/seed
  × 2 truncation strategies (chunk-and-average + head-truncation) ×
  full 5-slice OOD slate; ablation-appendix framing (NOT integrated as
  6th rung). Sequential single-pod 2-fire shape via
  `lifecycle.on_success: recycle` per [#90](https://github.com/brandon-behring/runpod-deploy/issues/90)
  consumption. Status: methodology accepted at v1.1.0; execution
  deferred to v1.1.1.

- **`configs/rungs/deberta_v3_base.yaml`** — DeBERTa-v3-base
  hyperparameter recipe (v1.1.0 SCAFFOLD; do not fire until v1.1.1).

- **`configs/runpod/headline-deberta.yaml`** — RunPod orchestration
  config for the DeBERTa ablation (lifecycle: recycle on_success;
  budget.ssh_ready_timeout_sec: 600 per #88; cost_cap_usd: 25.0
  generous under ADR-020 $125 soft cap).

- **`Makefile` targets**: `train-deberta-v3`, `eval-deberta-v3`,
  `deberta-ablation` — v1.1.0 stubs that exit 2 with a
  v1.1.1-carryforward message + pointer to ADR-060.

- **`RESULTS.md` §1B**: ablation-appendix placeholder section
  documenting the locked methodology + v1.1.1 execution carryforward.
  Per-strategy AUPRC + AUROC grid will populate when v1.1.1 ships.

### Changed

- **`configs/runpod/headline-frozen_probe.yaml`** +
  **`headline-lora.yaml`** + **`headline-full_ft.yaml`** — migrated
  from legacy `stop: {on_success, on_failure}` schema to v0.8.x
  `lifecycle:` schema (runpod-deploy v0.8.3 REMOVED `stop:` — migration
  was BLOCKING). Semantic equivalence preserved: `on_success: delete`
  (was `stop.on_success=true`) + `on_failure: stop` (was
  `stop.on_failure=false`). All 3 configs gain
  `budget.ssh_ready_timeout_sec: 600` per [#88](https://github.com/brandon-behring/runpod-deploy/issues/88)
  consumption (replaces the deleted monkey-patch shim).

- **`pyproject.toml`** — runpod-deploy pin
  `git+https://github.com/brandon-behring/runpod-deploy@v0.7.7` →
  `runpod-deploy==0.8.4` (PyPI install spec per PEP 508; ADR-059).

- **`uv.lock`** — regenerated (runpod-deploy entry moves to PyPI
  registry source).

- **`Makefile`** — `headline-frozen-probe` / `headline-lora` /
  `headline-full-ft` targets revert to direct
  `uv run runpod-deploy run --config ...` (deleted shim was the prior
  wrapper).

- **`decisions/ADR-036-...md`** frontmatter — `superseded_by: ["055", "059"]`
  (narrow supersessions of "git URL only" sub-claim — once per
  PyPI-published own-authored library; research_toolkit retains
  git+https tag-pin per this ADR until it publishes to PyPI).

- **`decisions/upstream_issues.md`** — 7 runpod-deploy rows
  (`#88` / `#90` / `#92` / `#93` / `#94` / `#97` / `#98`) updated to
  **RESOLVED in v0.8.x** with v1.1.0 consumption notes.

- **`decisions/library_imports.md`** — runpod-deploy version pin row
  `v0.7.7 git+https` → `v0.8.4 PyPI` with consumption summary.

- **`WRITEUP/limitations-and-future-work.md` §9.2** — update on the
  DeBERTa-v3-base drop reasoning: dropped at Phase 0 (ADR-015), now
  returns as deliberate ablation-appendix comparator at v1.1.0
  methodology lock per ADR-060.

- **`NEXT_STEPS.md` §1.10** — status updated to "methodology landed
  at v1.1.0 (ADR-060); execution v1.1.1" with Path B rationale
  documented inline.

- **`SUBMISSION_AUDIT.md`** — regenerated via `scripts/regenerate_audit.py`;
  60 CLAIM rows total (ADR-059 + ADR-060 added).

### Removed

- **`scripts/runpod_deploy_long_ssh.py`** — DELETED. The monkey-patch
  shim that bumped runpod-deploy's SSH-ready timeout from 240s to 600s
  is no longer needed since [#88](https://github.com/brandon-behring/runpod-deploy/issues/88)
  closed with configurable `budget.ssh_ready_timeout_sec`. Per
  no-orphaned-code invariant: deleted in same commit as the pin bump.

### References

- Supersedes (narrow): [ADR-036](decisions/ADR-036-library-version-pins-tag-pin-plus-freeze.md)
  "git URL is the only viable spec format" sub-claim for runpod-deploy.
- Closes [runpod-deploy#88](https://github.com/brandon-behring/runpod-deploy/issues/88)
  (SSH timeout configurable),
  [#90](https://github.com/brandon-behring/runpod-deploy/issues/90)
  (lifecycle.on_success: recycle),
  [#92](https://github.com/brandon-behring/runpod-deploy/issues/92) +
  [#93](https://github.com/brandon-behring/runpod-deploy/pull/93) +
  [#94](https://github.com/brandon-behring/runpod-deploy/issues/94)
  (FUSE workarounds),
  [#97](https://github.com/brandon-behring/runpod-deploy/issues/97)
  (validate --check-image-registry),
  [#98](https://github.com/brandon-behring/runpod-deploy/issues/98)
  (Makefile-recipe docs).
- Reviewer URL pin: `tree/v1.0.0` unchanged per [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md).
  Live Quarto site reflects v1.1.0 changes.

---

## [1.0.9] — 2026-05-19 {#v1-0-9}

`scripts/eval_from_hub.py` non-dry-run body **wired end-to-end** —
closes ADR-051 Block A (T0 score-match carryforward) per ADR-058
narrow supersession + opportunistic eval-toolkit v0.40.0 → v0.42.0
bump consuming upstream **`fit_isotonic_binary`** (eval-toolkit#44
closed; ~5 min between issue close + PyPI publish). The
v1.0.8 `fit_isotonic_binary_local` adapter is removed in the same
commit per library-first + no-orphaned-code invariants. 4-of-4
binary calibrator family (temperature + isotonic + Platt + Beta)
now lands on the canonical upstream `_binary` API.

Closes ADR-051 Block A landing condition: `make eval-from-hub
RUNG=frozen-probe` + `RUNG=lora` exit 0 with score-match summary
within 1e-4 absolute tolerance per ADR-034 §Tier T0. Strict-mode
exit code per /exploring-options 2026-05-19 Q1 lock: exit 1 on any
row exceeding tolerance (no silent failures). ADR-051 Block B
(38 invariant scaffolds) remains v1.1.x carryforward.

### Added

- **`decisions/ADR-058-eval-from-hub-non-dry-run-body-narrow-supersession-of-adr-051-block-a.md`**
  — narrow supersession of ADR-051 Block A. Documents the full
  body wiring (snapshot_download → architecture-dispatched load →
  CPU inference via library-first reuse of
  `src.training.train_modernbert._predict_proba` → per-row
  score-match within 1e-4 tolerance), the 6 execution-level locks
  from /exploring-options 2026-05-19 (Q1 strict mode, Q6 mocked-only
  smoke), and the explicit non-closure of Block B. ADR-051
  frontmatter gains `superseded_by: ["058"]` in-place per ADR-029
  convention.

- **`tests/smoke/test_eval_from_hub_smoke.py`** (NEW; 9 tests) —
  `--dry-run` subprocess coverage for both published rungs +
  score-match tolerance unit tests with synthetic numpy arrays
  (within-tol, exceeds-tol, length-mismatch) + published-rungs
  validator against `evals/results.json` + reference parquet loader
  + kebab↔underscore rung-name translation. Per Q6 lock: mocked-only
  / CI-hermetic; no real HF Hub fetch.

### Changed

- **`scripts/eval_from_hub.py`** — non-dry-run body wired
  (~250 LOC; replaces the ~7-line v1.0.x stub that exited 2).
  Architecture-dispatched model loader: `frozen-probe` / `full-ft`
  via `AutoModelForSequenceClassification.from_pretrained`; `lora`
  via base ModernBERT (pinned revision per ADR-015) +
  `PeftModel.from_pretrained`. Validates `args.rung` against
  `evals/results.json::published_rungs` before download; emits
  PredictionsRowModel-compatible parquet at
  `evals/predictions/t0_eval_from_hub.parquet`. Library-first reuse
  of `src.training.train_modernbert._predict_proba` for inference
  (softmax_fp32 cast per ADR-019).

- **`pyproject.toml`** — eval-toolkit pin bumped v0.40.0 → v0.42.0
  (PyPI install per ADR-055). v0.41.0 skipped because it predated
  the eval-toolkit#44 close at 2026-05-19T01:20Z; v0.42.0 published
  2026-05-19T01:25Z ships `fit_isotonic_binary` with the canonical
  `(None, apply)` `_binary` shape.

- **`src/eval/calibration_battery.py`** — `fit_isotonic_binary_local`
  adapter (filed v1.0.8 as upstream workaround) DELETED in same
  commit as the upstream consumption switch; orphaned
  `from collections.abc import Callable` import also removed per
  no-orphaned-code invariant. Direct upstream import:
  `from eval_toolkit.calibration import fit_isotonic_binary`.

- **`WRITEUP/reproducibility.md`** §T0 maintainer note — rewritten
  for v1.0.9 reality: "non-dry-run body is now fully wired per
  ADR-058... exit 0 with score-match summary within 1e-4 tolerance".
  Removes the v1.0.x "scaffold that exits with code 2" language.

- **`decisions/ADR-051-v1.0.x-carryforward-of-t0-and-invariant-scaffolds.md`**
  frontmatter — `superseded_by: ["058"]` in-place edit per ADR-029
  convention (Block A only; Block B remains carryforward).

- **`decisions/upstream_issues.md`** — row for eval-toolkit#44 →
  **RESOLVED in v0.42.0**; consumption notes + adapter-deletion
  trigger documented.

- **`decisions/library_imports.md`** — eval-toolkit version pin
  row updated to v0.42.0; new `fit_isotonic_binary` inventory entry
  replaces the v1.0.x `fit_isotonic_calibrator` row (4-of-4 binary
  calibrator family now on upstream `_binary` API).

- **`SUBMISSION_AUDIT.md`** — regenerated via
  `scripts/regenerate_audit.py`; 58 CLAIM rows total (ADR-058
  added).

### Tests

- 9/9 passing at `tests/smoke/test_eval_from_hub_smoke.py`.
- 186 passed / 38 skipped (ADR-051 Block B invariants; carryforward
  expected) / 1 xfailed across `tests/smoke/` + `tests/test_invariants.py`.
- `uv run mypy --strict scripts/eval_from_hub.py` returns 0.
- `uv run ruff check scripts/eval_from_hub.py
  tests/smoke/test_eval_from_hub_smoke.py src/eval/calibration_battery.py`
  reports All checks passed!.

### References

- Closes [ADR-051](decisions/ADR-051-v1.0.x-carryforward-of-t0-and-invariant-scaffolds.md)
  **Block A** (T0 score-match wiring); supersedes via
  [ADR-058](decisions/ADR-058-eval-from-hub-non-dry-run-body-narrow-supersession-of-adr-051-block-a.md).
  Block B (38 invariant scaffolds) remains v1.1.x carryforward.
- Closes [eval-toolkit#44](https://github.com/brandon-behring/eval-toolkit/issues/44)
  (`fit_isotonic_binary`).

---

## [1.0.8] — 2026-05-19 {#v1-0-8}

eval-toolkit v0.39.0 → v0.40.0 + **PyPI install switch** (out of
git+https) + **binary calibrator refactor** to upstream `_binary` API
family + **Platt + Beta calibrators landed** + **per-prediction
provenance manifest backfill** (282 manifests) + **3 new ADRs**
(055/056/057) + 2 in-place superseded_by edits on ADR-036 + ADR-023.

Closes NEXT_STEPS §1.4 (Platt + Beta deferral via upstream consume)
and §1.9 (manifest backfill pipeline) per Path 3 / /exploring-options
batches 10-11 locks.

### Added

- **`decisions/ADR-055-eval-toolkit-pypi-install-narrow-supersession-of-adr-036.md`**
  — eval-toolkit installs from PyPI at v0.40.0+ (`eval-toolkit==0.40.0`
  PEP 508 specifier); narrow supersession of ADR-036 "git URL is the
  only viable spec format" sub-claim. Tag-pin convention + freeze
  policy + bump-triggers + uv.lock backstop all preserved.
  runpod-deploy + research_toolkit retain git+https tag-pin per
  ADR-036.

- **`decisions/ADR-056-binary-calibrator-refactor-and-platt-beta-narrow-supersession-of-adr-023.md`**
  — `src/eval/calibration_battery.py` refactored to use eval-toolkit
  `_binary` API family uniformly. Replaces `fit_temperature` (multi-
  class log-prob; what we missed at earlier pin bumps) with
  `fit_temperature_binary`. Adds `fit_platt_binary` + `fit_beta_binary`
  per upstream #43 (closed ~17 min after filing — fastest turnaround
  of v1.0.x series). Local `fit_isotonic_binary_local` adapter pending
  upstream #44.

- **`decisions/ADR-057-manifest-schema-v3-backfill-conventions.md`** —
  per-prediction provenance manifest schema; `scripts/backfill_provenance.py`
  emits 282 manifest.json files at `evals/manifests/`. Schema carries
  git_sha + config_hash + contamination_flag (ADR-005 3-state taxonomy)
  + rung/fold/seed/slice/n_rows + predictions_relpath. 3 filename
  patterns supported (trained-with-tail + trained-no-tail + reference).
  Non-destructive sibling-JSON design (parquets unchanged) chosen over
  column injection.

- **`scripts/backfill_provenance.py`** (new; ~230 LOC) — backfill CLI.
  Default mode writes 282 manifests; `--check` mode verifies presence
  (CI-friendly); `--rung <rung>` filter mode. Idempotent.

- **`evals/manifests/`** (new directory; 282 JSON files; ~150 KB total)
  — per-prediction provenance manifests per ADR-057.

- **eval-toolkit#44** filed at v1.0.8 ("Add `fit_isotonic_binary` for
  shape consistency with `fit_temperature_binary` + `fit_platt_binary`
  + `fit_beta_binary`"). Library-first invariant; mirrors the
  #39/#40/#41/#43 file-first pattern.

- **Makefile targets**: `make backfill-provenance` invokes
  `scripts/backfill_provenance.py` (default mode); `--check` variant
  for CI integration.

### Changed

- **`pyproject.toml`** — eval-toolkit pin switched from
  `git+https://github.com/brandon-behring/eval-toolkit@v0.39.0`
  to `eval-toolkit==0.40.0` (PyPI install). runpod-deploy +
  research_toolkit pins unchanged.

- **`uv.lock`** — regenerated; eval-toolkit source line changes from
  `git = "https://github.com/..."` to `registry = "https://pypi.org/simple"`.
  uv.lock wheel-SHA backstop replaces the prior git-rev-SHA backstop;
  byte-level reproducibility preserved.

- **`src/eval/calibration_battery.py`** — full `_binary` API refactor
  per ADR-056. Imports `fit_temperature_binary` + `fit_platt_binary` +
  `fit_beta_binary` from `eval_toolkit.calibration`; `fit_temperature`
  (multi-class API; the one we missed) removed. `CalibratorBundle`
  NamedTuple gains 4 new fields (platt_params + test_scores_platt +
  beta_params + test_scores_beta). Hand-rolled `proba_to_logprobs`
  (23 LOC) + `apply_temperature` (28 LOC) helpers deleted per
  no-orphaned-code invariant; both duplicated upstream's internal
  apply callable.

- **`tests/smoke/test_calibration_battery_smoke.py`** — 4 helper-tests
  removed (`test_proba_to_logprobs_*` + `test_apply_temperature_*`).
  New test `test_fit_and_apply_calibrators_returns_bundle_with_4_calibrators`
  covers all 7 CalibratorBundle fields. 7/7 calibration smoke tests
  pass; full smoke suite 167/167 (171 - 4 deleted = 167).

- **`decisions/ADR-036-library-version-pins-tag-pin-plus-freeze.md`** —
  frontmatter `superseded_by: ["055"]` added in-place per ADR-029
  immutability convention. Body unchanged; narrow supersession
  documented inline + in ADR-055.

- **`decisions/ADR-023-calibration-battery-and-interventions.md`** —
  frontmatter `superseded_by: ["056"]` added in-place. Body unchanged;
  narrow supersession (Platt + Beta deferral lifted) documented inline
  + in ADR-056.

- **`decisions/library_imports.md`** — eval-toolkit version pin table
  row updated to `v0.40.0` + PyPI install spec format note (per
  ADR-055).

- **`decisions/upstream_issues.md`** — #43 row → RESOLVED (consumed
  at v1.0.8). New row for #44 (`fit_isotonic_binary` filed v1.0.8).

- **`NEXT_STEPS.md` §1.4 + §1.9** — Status (v1.0.8) lines mark both
  closed per Path 3.

- **`SUBMISSION_AUDIT.md`** — regenerated; 57 CLAIM rows (54 + 3
  new at v1.0.8).

### Governance notes

- **In-place edits to ADR-036 + ADR-023 frontmatter** — `superseded_by`
  field added; bodies unchanged. Per ADR-029 immutability convention;
  established pattern (ADR-050 received the same edit at v1.0.3 when
  ADR-052 narrowly superseded R2; ADR-053 received the same edit at
  v1.0.5 when ADR-054 narrowly superseded dimension 1).

- **Library-first invariant pattern observed twice**: filed #43 at
  v1.0.6 → resolved upstream in 17 min → consumed at v1.0.8. Filed
  #44 at v1.0.8 → workaround locally pending resolution. The pattern
  is a project-wide signal that upstream-first beats hand-roll.

### Files modified (16 file touches)

- `pyproject.toml` (eval-toolkit pin format + version).
- `uv.lock` (regenerated; PyPI source replaces git source).
- `src/eval/calibration_battery.py` (full refactor per ADR-056).
- `tests/smoke/test_calibration_battery_smoke.py` (refactor + 4 tests
  deleted, 1 added).
- `scripts/backfill_provenance.py` (new; ~230 LOC).
- `decisions/ADR-055-...md` (new; ~150 LOC).
- `decisions/ADR-056-...md` (new; ~170 LOC).
- `decisions/ADR-057-...md` (new; ~160 LOC).
- `decisions/ADR-036-...md` (frontmatter `superseded_by` in-place edit).
- `decisions/ADR-023-...md` (frontmatter `superseded_by` in-place edit).
- `decisions/library_imports.md` (version pin row + PyPI note).
- `decisions/upstream_issues.md` (#43 RESOLVED + #44 NEW).
- `NEXT_STEPS.md` (§1.4 + §1.9 status lines).
- `Makefile` (`make backfill-provenance` target + .PHONY).
- `evals/manifests/` (282 new JSON files).
- `SUBMISSION_AUDIT.md` (regenerated; 57 CLAIM rows).
- `CHANGELOG.md` (this entry).

---

## [1.0.7] — 2026-05-18 {#v1-0-7}

4 demo notebooks (jupytext-paired; pre-rendered + frozen output
cells) + DeLong + BH-FDR primitives wired + CSV analysis exports.
Closes NEXT_STEPS §1.1 + §1.2 + §1.3 per Path 3 / /exploring-options
batches 7-9 locks.

### Added

- **`notebooks/01_canonical_results.{ipynb,py}`** — headline
  5×3 AUPRC + AUROC grid sourced from
  `evals/bootstrap/marginal_cells.parquet` (BCa CI, 10000
  resamples) + prevalence baselines. 5 code cells with frozen
  output cells.

- **`notebooks/02_frozen_vs_lora.{ipynb,py}`** — paired-bootstrap
  rung-comparison + DeLong AUC-difference sanity-check + BH-FDR
  multi-comparison correction across the 40-cell paired battery.
  Surfaces the load-bearing **LoRA -0.071 vs frozen-probe AUPRC
  delta on pooled_ood** with 3 cross-method consistency checks
  (paired-bootstrap + DeLong + BH-FDR all agree). 9 code cells
  with frozen output cells. **§1.3 closure**: DeLong via
  `eval_toolkit.bootstrap.delong_roc_variance`; BH-FDR via
  `eval_toolkit.bootstrap.fdr_bh_correct` (both available since
  v0.32.0; wired here library-first).

- **`notebooks/03_calibration.{ipynb,py}`** — per-rung × per-slice
  mean ECE equal-mass + Brier score (across 12 cells per rung;
  4 folds × 3 seeds). Cross-references F4 reliability triptych
  in `docs/plots/F4.svg`. Platt/Beta deferral noted (eval-toolkit#43
  pending; v1.0.8 conditional consume).

- **`notebooks/04_ood_slate.{ipynb,py}`** — per-slice
  IID-vs-OOD gap visualization. Each rung's AUPRC compared to
  the slice's positive-prevalence baseline; per-slice
  rung-comparison; cross-family OOD finding summary. References
  F5 per-slice heatmap.

- **`scripts/export_analysis_csvs.py`** — CLI generating
  `analysis/v1.0.7_canonical/` directory with 3 CSVs per
  NEXT_STEPS §1.2:
  - `paired_tests.csv` (1:1 mirror of `paired_cells.parquet`;
    40 rows × 12 cols).
  - `ece_per_cell.csv` (1:1 mirror of `per_cell.parquet`;
    114 rows × 14 cols).
  - `per_source_rates.csv` (NEW label-audit aggregation from
    282 prediction parquets; 282 rows × 9 cols with
    positive_prevalence + mean_predicted_proba per (rung,
    fold, seed, source)).

- **`Makefile`** — 2 new targets:
  - `make notebooks` — jupytext + nbconvert re-execute all 4
    notebooks (operator workflow; pre-rendered + frozen output
    cells per /exploring-options batch 9 Q2 lock).
  - `make export-analysis-csvs` — refresh
    `analysis/v1.0.7_canonical/` CSVs.

- **`.gitattributes`** — `notebooks/*.ipynb -nbstripout` override
  so the nbstripout pre-commit hook does NOT strip output cells
  from committed notebooks. Per the batch 9 Q2 lock requirement
  that committed `.ipynb` files retain frozen output cells.

- **`pyproject.toml [project.optional-dependencies] notebook`** —
  added `jupytext>=1.17`, `nbconvert>=7.16`, `ipykernel>=6.30`.
  Pre-v1.0.7 `notebook` extra only had `jupyter` + `nbstripout`
  + `nbval`; v1.0.7 fills in jupytext + nbconvert + ipykernel for
  the `make notebooks` workflow.

### Changed

- **`_quarto.yml`** — added `notebooks/*.ipynb` to
  `project.render` allowlist + new "Notebooks" sidebar section
  between "Methodology" and "Evidence + audit" + Notebooks
  navbar dropdown menu. Reviewer can navigate from the live
  Quarto site to any of the 4 notebooks in 1 click.

- **`NEXT_STEPS.md` §1.1 + §1.2 + §1.3** — Status (v1.0.7)
  lines mark the 3 items closed (notebooks + CSV exports + DeLong/BH-FDR
  wiring all landed).

### Notes

- No methodology change. No metric values change. Notebooks are
  pure consumers of existing `evals/` artifacts.
- Pre-rendered + frozen output cells per /exploring-options
  batch 9 Q2 lock. Operator re-renders via `make notebooks` when
  underlying data changes; CI does not re-execute.
- nbstripout override at `.gitattributes` is the cleanest way
  to handle "commit with outputs" while keeping the existing
  pre-commit hook configured for any future hand-authored
  notebooks (outside the v1.0.7 4-notebook set).

### Files modified (15 file touches)

- `pyproject.toml` (notebook extra deps).
- `uv.lock` (regenerated via `uv sync --extra notebook`).
- `.gitattributes` (new; nbstripout override for notebooks/).
- `notebooks/01_canonical_results.{ipynb,py}` (new pair).
- `notebooks/02_frozen_vs_lora.{ipynb,py}` (new pair).
- `notebooks/03_calibration.{ipynb,py}` (new pair).
- `notebooks/04_ood_slate.{ipynb,py}` (new pair).
- `scripts/export_analysis_csvs.py` (new).
- `analysis/v1.0.7_canonical/paired_tests.csv` (new).
- `analysis/v1.0.7_canonical/ece_per_cell.csv` (new).
- `analysis/v1.0.7_canonical/per_source_rates.csv` (new).
- `Makefile` (notebooks + export-analysis-csvs targets + .PHONY).
- `_quarto.yml` (render allowlist + sidebar + navbar).
- `NEXT_STEPS.md` (§1.1/§1.2/§1.3 Status lines).
- `CHANGELOG.md` (this entry).

---

## [1.0.6] — 2026-05-18 {#v1-0-6}

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

## [1.0.5] — 2026-05-18 {#v1-0-5}

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

## [1.0.4] — 2026-05-18 {#v1-0-4}

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
    decision is unchanged. Per [ADR-029](decisions/../CLAUDE.md)
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

## [1.0.3] — 2026-05-18 {#v1-0-3}

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

## [1.0.2] — 2026-05-18 {#v1-0-2}

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

## [1.0.1] — 2026-05-18 {#v1-0-1}

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

## [1.0.0] — 2026-05-18 {#v1-0-0}

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

## [0.9.0-rc3] — 2026-05-18 {#v0-9-0-rc3}

Third rehearsal — `a2fc4d9`. CI + Publish workflows green; reviewer
URLs return 200. Same content as v1.0.0; the rc3 tag is preserved
as the rehearsal-pass landmark per ADR-033 fix-forward discipline.

## [0.9.0-rc2] — 2026-05-18 {#v0-9-0-rc2}

Second rehearsal — `d66e3d0`. CI red on the lint hard gate (3
remaining ruff-format diffs from a pre-commit stash-restore loop) +
one data-gated invariant; Publish workflow needed an orphan `gh-pages`
branch on origin. Fix-forwarded via `0bedc80` (data-gated skipif) +
`a2fc4d9` (ruff-pre-commit v0.4.0 → v0.15.13 + format leftover).

## [0.9.0-rc1] — 2026-05-17 {#v0-9-0-rc1}

First rehearsal tag (per ADR-033). Catches first-time-CI / auth /
schema issues before the canonical submission. Resulted in the
`REPO_AUDIT_2026-05-18.md` 8-item remediation queue.

## [0.0.0] — 2026-05-15 {#v0-0-0}

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
