# Repo audit - 2026-05-21 (v1.2.12 close)

> **Status (resolved 2026-05-21).** Internal audit conducted 2026-05-21
> at v1.2.12 close. All 2 P0 + 7 P1 + ~14 P2 + ~7 P3 findings discharged
> via the v1.2.13 polish patch sequence (C0 audit-publish + C1 ADR-076
> frontmatter backfill + C2 reader-facing accuracy sweep + C3
> CLAUDE.md/AGENTS.md governance refresh + C4 ADR cross-ref sweep per
> ADR-068/ADR-069 + C5 library-first ledger refresh + C6 RESULTS/WRITEUP/
> GLOSSARY polish + C7 CI hygiene + CHANGELOG close + tag). All 8
> v1.2.13 sub-commits gated CI-green per
> `[[auto-continue-on-green-ci-preferred-for-bundled-patches]]`. Two
> fix-forward commits landed mid-sequence: C2.1 lycheeignore for the
> tree/v1.2.13 forward-reference; C4.1 lycheeignore re-add + DOI
> revert when the proposed JSTOR canonicalization 404'd.
>
> Preserved here under `decisions/audits/` as part of the SDD audit
> trail per ADR-040; parallel to `REPO_AUDIT_2026-05-18.md`'s
> resolution-arc precedent (which closed via v1.2.9-v1.2.12).
>
> **Posture.** Polish + consistency audit at v1.2.12 close. Not a
> submission-readiness audit — the v1.0.0 submission shipped 2026-05-18
> and the prior `REPO_AUDIT_2026-05-18.md` is resolved. This audit asks:
> *given v1.2.9-v1.2.12 was itself an audit-remediation arc, what
> consistency / polish debt remains?*
>
> Preserved under `decisions/audits/` as part of the SDD audit trail
> per ADR-040 phase-0 audit-findings discipline.
>
> Scope: full breadth across 10 dimensions (terminology, cross-refs, CI
> + audit scripts, CHANGELOG/ADR/SUBMISSION_AUDIT triangulation,
> library-first ledgers, glossary, reviewer-path/URL integrity,
> CLAUDE.md/AGENTS.md staleness, no-emoji, test gates). Methodology
> per `plans/check-remote-sorted-dijkstra.md` (3 parallel
> general-purpose audit agents + 6 audit scripts + pytest +
> triangulation greps + `gh` upstream-issue queries).

## Executive verdict

**Strong polish state with 2 P0 + 7 P1 + ~14 P2 findings.** All
machine-checkable gates are green: 6 audit scripts exit 0; pytest
202 passed + 38 skipped + 1 xfailed; SUBMISSION_AUDIT.md
regenerates without diff (75 CLAIM rows = 75 ADRs); reviewer URLs
(live site + `tree/v1.2.8` + `tree/v1.2.12`) all return HTTP 200.
The remaining findings are *prose drift* introduced when the
v1.2.9-v1.2.12 polish arc didn't propagate updates across every
reader-facing surface — concentrated in three places: ADR-count
claims (4 files stale at 70 vs actual 75), version-pin headers
(3 surfaces disagree), and the Finding-3 "actively harmful"
framing (the v1.2.11 anti-correlation reframe didn't reach the
WRITEUP / landing headings).

Remediation is fully mechanical (no methodology, model, data, or
compute change). Proposed as `v1.2.13` polish patch — appendix at
the end of this file.

## Machine-checkable signal (Phase B + C, all green)

| Check                                    | Result                           |
|------------------------------------------|----------------------------------|
| `scripts/audit_writeup_numbers.py`       | `0 drifts (clean)` — exit 0      |
| `scripts/audit_rendered_site.py`         | `Rendered site audit OK` — exit 0|
| `scripts/audit_leakage.py`               | `Leakage audit: CLEAN` (0 exact-hash, 0 cosine≥0.85) — exit 0 |
| `scripts/audit_reference_scorers.py`     | 0 disagreement pairs — exit 0    |
| `scripts/check_no_emoji.py`              | clean — exit 0                   |
| `scripts/regenerate_audit.py`            | no diff vs committed (in sync) — exit 0 |
| `pytest -q`                              | 202 passed / 38 skipped / 1 xfailed / 42.48s — exit 0 |
| ADR count (`ls decisions/ADR-*.md \| wc -l`) | 75                          |
| SUBMISSION_AUDIT.md `^### CLAIM` rows    | 75 (1:1 with ADRs)               |
| `tree/v1.0.0` (historical pin)           | HTTP/2 200                       |
| `tree/v1.2.8` (canonical reviewer pin)   | HTTP/2 200                       |
| `tree/v1.2.12` (current state tag)       | HTTP/2 200                       |
| `gh-pages` live site                     | HTTP/2 200                       |

## P0 — reviewer-noticeable contradictions

### P0-1: Three top-fold surfaces disagree on "current state" pin

**Evidence**:
- `README.md:136` — `**Current state:** [tree/v1.2.11](.../tree/v1.2.11) (2026-05-20)`
- `WRITEUP.md:4` — `live-site current state tree/v1.2.8`
- `READING_GUIDE.md:141` — `[tree/v1.2.8](.../tree/v1.2.8)`

**Actual**: HEAD is `v1.2.12` (`cbfc52f`, 2026-05-21). All three
surfaces are stale; they disagree by one or three patches.

**Why P0**: A reviewer comparing the README's "current state" to the
WRITEUP / READING_GUIDE "current state" sees three different answers
on three top-fold reader-facing pages. The "current state" concept
should be canonical and version-correct (≠ the "canonical reviewer
pin" `tree/v1.2.8` per ADR-033 + ADR-064-era policy — that's a
separate fixed pin, which IS correctly held at v1.2.8 in
SUBMISSION_AUDIT.md and CHANGELOG.md).

**Fix**: Standardize all three "current state" labels to
`tree/v1.2.12 (2026-05-21)`. Preserve the historical
`tree/v1.0.0 (2026-05-18)` line untouched in each (correct per
ADR-033). Note: the canonical-reviewer-pin separately held at
`tree/v1.2.8` is for academic-URL-correlation purposes and stays
at v1.2.8 — that's a different concept from "current state".

### P0-2: docs/for-hiring-managers.md states "70 immutable ADRs"

**Evidence**: `docs/for-hiring-managers.md:83` —
`**Spec-Driven Development**: 70 immutable Architecture Decision Records`

**Actual**: 75 ADRs at v1.2.12 close (ADR-001 through ADR-075;
verified by file count and SUBMISSION_AUDIT.md row count).

**Why P0**: This is the 60-second reader-facing entry surface (per
v1.2.11 rename "Project at a glance"). A hiring manager skimming the
page sees "70 ADRs", then the README at line 100/114 says "75 ADRs"
— a direct cross-file numeric contradiction.

**Fix**: `docs/for-hiring-managers.md:83` change `70` → `75`. Single
scalar edit.

## P1 — quality-breaking inconsistencies

### P1-1: WRITEUP/methodology-guarantees.md ADR counts stale

**Evidence**:
- `WRITEUP/methodology-guarantees.md:12` — `**SDD / ADR process**: 70 ADRs accepted across Phase 0-00 through ADR-070 (immutability-relaxation closures)`
- `WRITEUP/methodology-guarantees.md:87` — `50 ADRs accepted across Phase 0-00 through Phase 5 close at ADR-050` (plausibly intentional snapshot but reads as a present-tense claim in context)

**Fix**: Line 12 → `75 ADRs accepted across Phase 0-00 through ADR-075`. Line 87 is the Phase 5 snapshot — leave at 50/ADR-050 but consider qualifier prose ("at Phase 5 close" → "at the v1.0.0 submission gate") for clarity.

### P1-2: CLAUDE.md:13 stale ADR count + governance enumeration

**Evidence**: `CLAUDE.md:13` —
`~9 topic-focused sub-sessions; 70 ADRs at v1.2.8 close including post-v1.0.0 patch governance: ADR-051 carryforward + ADR-052 full-FT reframing + ADR-053 reading-guide governance + ADR-061 nav restructure + ADR-067-070 immutability-relaxation chain`

**Actual**: 75 ADRs at v1.2.12 close. The "ADR-067-070 chain" is now a
"ADR-067-070 + ADR-073 chain" since ADR-073 is the consolidated
re-statement.

**Why P1 (not P0)**: CLAUDE.md is in the Quarto render allowlist per
`_quarto.yml`, so it's reviewer-visible. But it's primarily an
operator/agent file; the public-site note at the top labels it as
"not part of the main results narrative".

**Fix**: Update line 13 to `75 ADRs at v1.2.12 close including post-v1.0.0 patch governance: ADR-051 carryforward + ADR-052 full-FT reframing + ADR-053 reading-guide governance + ADR-061 nav restructure + ADR-067-070 immutability-relaxation chain consolidated in ADR-073 + ADR-074 redaction governance + ADR-075 full-FT OOD narrative unification`. Approx 1-line edit.

### P1-3: CLAUDE.md:64-86 "FOUR factual-defect classes" no pointer to ADR-073

**Evidence**: `CLAUDE.md:64-86` enumerates the four narrow-relaxation
classes (ADR-067 + ADR-068 + ADR-069 + ADR-070) without acknowledging
ADR-073 — the consolidated re-statement that came afterward to clean
up the rule.

**Why P1**: The CLAUDE.md text is the canonical operator instruction;
agents reading it should be pointed at the consolidated re-statement
since it's the cleanest reference.

**Fix**: After the "ALL other content remains immutable" line (≈86), add
`(rule consolidated and re-stated in [ADR-073](decisions/ADR-073-adr-immutability-rule-consolidated-re-statement.md); read that ADR for the consolidated narrative).`

### P1-4: AGENTS.md missing the "Narrow exceptions" governance section

**Evidence**: `AGENTS.md:32` ends its immutability paragraph at
`supersede via new ADR` — no parallel to CLAUDE.md's lines 64-86
narrow-exceptions section.

**Why P1**: AGENTS.md is the canonical guide for non-Claude agents
(Codex, Cursor, etc.) per the project's multi-agent collaboration
pattern (`[[multi-agent-collision-codex-handoff]]`). A
non-Claude-trained agent reading AGENTS.md alone would not learn the
in-place correction rule and could either (a) refuse legitimate
ADR-067-069-style fixes or (b) hand-roll a superseding-ADR workaround.

**Fix**: Backport CLAUDE.md's §Narrow exceptions section (lines
64-86) into AGENTS.md verbatim, OR add a one-line pointer
`See CLAUDE.md §Narrow exceptions for the four in-place
factual-defect classes (ADR-067 + ADR-068 + ADR-069 + ADR-070;
consolidated in ADR-073).` Same content; pick whichever the
maintainer prefers.

### P1-5: Finding 3 "actively harmful" framing stale on top-fold surfaces

**Evidence**:
- `WRITEUP.md:171` — `### Finding 3: Fine-tuning was actively harmful on cross-family OOD (lexical overfitting + label-relevance inversion)`
- `index.qmd:113` — `3. **Fine-tuning was actively harmful, not neutral.** Trained detectors hit...`

**Context**: v1.2.11 polish (per memory `[[v1-2-x-patch-trail-state-after-v1-2-12]]` and CHANGELOG.md [1.2.11]) reframed the bare "actively harmful" phrasing as "anti-correlated with cross-family attack class" for the cross-family OOD AUROC<0.5 result. The reframe is applied at `docs/for-hiring-managers.md:34` ("anti-correlated with cross-family attack class") but did NOT propagate to the WRITEUP / index headings.

**Why P1**: Internal terminology drift on the headline finding —
reader on README / index / WRITEUP sees "actively harmful" while
reader on Project-at-a-glance page sees the corrected framing. Same
result, two voices.

**Fix**: Reframe both `WRITEUP.md:171` and `index.qmd:113` to use
the anti-correlation framing while keeping the body prose. Suggested:
- WRITEUP.md:171 → `### Finding 3: Trained adapters anti-correlated with cross-family attack class (lexical overfitting + label-relevance inversion)`
- index.qmd:113 → `3. **Trained adapters were anti-correlated, not just neutral.**`

### P1-6: ADR-062 supersession back-links missing on ADR-046/054/061

**Evidence**:
- `ADR-062:29` — `supersedes: [ADR-046, ADR-054, ADR-061]`
- `ADR-046:13` — `superseded_by:` (empty)
- `ADR-054:69` — `superseded_by: []`
- `ADR-061:55` — `superseded_by: []`

The convention is documented inside ADR-054 itself
(`ADR-054:290-313` describes how ADR-053's `superseded_by:` was
edited in-place to point at ADR-054). Same pattern is followed at
ADR-023 (`superseded_by: ["056"]`) and ADR-036 (`superseded_by:
["055", "059"]`).

**Why P1**: Broken forward-link in supersession chain. A reviewer
reading ADR-046 or ADR-054 or ADR-061 has no machine-readable
pointer to ADR-062 (which superseded them). The
`scripts/regenerate_audit.py` doesn't auto-compute inverse links,
so this is silent stale data.

**Fix**: New ADR (proposed `ADR-076`) analogous to ADR-072 —
"frontmatter backfill for ADR-046 + ADR-054 + ADR-061 superseded_by
field". The backfill is content-bounded to frontmatter (no body
text touched), parallel to the ADR-072 pattern.

### P1-7: library_imports.md:85 runpod-deploy section header pin contradicts table row + pyproject.toml

**Evidence**:
- `decisions/library_imports.md:85` — `## runpod-deploy imports (https://github.com/brandon-behring/runpod-deploy) [v0.7.7 pinned]`
- `decisions/library_imports.md:29` (same file's table row) — `runpod-deploy | v0.8.4 | runpod-deploy==0.8.4`
- `pyproject.toml:84` — `"runpod-deploy==0.8.4"`

**Why P1 (not P2)**: Internal contradiction WITHIN the same ledger
file. The table at line 29 and the section header at line 85
disagree on the pin. Any reviewer or future maintainer reading from
the section header gets a wrong version.

**Fix**: `decisions/library_imports.md:85` change `[v0.7.7 pinned]`
→ `[v0.8.4 pinned]`.

## P2 — polish drift (terse)

- **`RESULTS.md:61`** — full-FT row `ModernBERT full fine-tune | 0.558` missing the `**` honesty asterisk + Phase-5-X11-crash footnote that EXECUTIVE_SUMMARY.md:92 + for-hiring-managers.md:55 + index.qmd:94 all carry. Fix: add marker + footnote per ADR-075.
- **`RESULTS.md:89-90 + WRITEUP.md:131`** — ProtectAI inline "Read" column truncated; misses "not a clean OOD baseline" caveat that EXECUTIVE_SUMMARY.md:35-36 + README.md:39-40 + index.qmd:52-53 include inline. Fix: backport caveat tail.
- **`docs/GLOSSARY.md:36`** — references old question wording `"What does this tell me about how the candidate thinks?"`; actual heading at `docs/for-hiring-managers.md:81` reads `"What does this say about how the candidate thinks?"`. Fix: sync prose.
- **`decisions/library_imports.md:39`** — bump-triggers list (blocking bug / CVE / reviewer-feedback patch) missing the v1.2.8 "dependency/ledger maintenance" trigger per ADR-066. Fix: add a 4th bullet referencing ADR-066.
- **`decisions/library_imports.md:57,59,60,69-76`** — multiple rows describe wiring as "Phase 4 deliverable" / "Phase 4 Commit N" though the code has been live since v1.0.x. Fix: change to "landed" (low priority; reads-as-stale, not factually wrong).
- **`decisions/upstream_issues.md`** — missing rows for eval-toolkit #50 (CLOSED 2026-05-19), #51 (OPEN), #52 (OPEN). Fix: add 3 ledger entries with rationale (e.g., not-applicable, portfolio-repo-scope, or pending-consumption).
- **`CLAUDE.md:154-161 + AGENTS.md` anti-patterns section** — uses softer "Working around a library limitation without filing an upstream issue" formulation. Per memory `[[library_first_is_project_wide_invariant]]` strengthened 2026-05-18: "NO local workarounds whatsoever; missing → upstream MR BLOCKS dependent work". Fix: update anti-pattern phrasing to match strengthened invariant.
- **`decisions/ADR-024-cross-fold-ci-methodology.md:13`** — residual JSTOR URL `https://www.jstor.org/stable/27033529`; ADR-069 authorizes canonicalization to `doi.org/10.2307/27033529`. ADR-024:16 already shows the canonical form for a sibling paper, so the convention is established. Fix: ADR-069-cited in-place commit.
- **`decisions/ADR-020:206 + ADR-025:41-43 + ADR-061:287 + ADR-063:89`** — local-fs paths (`/home/brandon_behring/...`, `../../../.claude/...`) in body prose. ADR-068 authorizes fix. Fix: ADR-068-cited in-place commit canonicalizing to github.com URLs where possible, redacting where not.
- **ADR-071, ADR-072, ADR-073, ADR-074, ADR-075** — all carry empty `closing_commit:` and `transcript:` frontmatter. ADR-072 explicitly notes the empty `transcript:` is intentional (project's gitignored-transcripts discipline) but does NOT address the empty `closing_commit:`. ADR-051 / ADR-052 populated theirs post-hoc via ADR-072 backfill. Fix: roll into the P1-6 ADR-076 frontmatter-backfill ADR (extends ADR-072's pattern).
- **Plan-vs-tool mismatch**: this audit's approved plan (`plans/check-remote-sorted-dijkstra.md`) said "Phase A: Parallel Explore agents (3 in parallel)" but Explore's own tool docs say *"Do NOT use it for code review, design-doc auditing, cross-file consistency checks, or open-ended analysis — it reads excerpts rather than whole files and will miss content past its read window."* General-purpose agents were used instead. Fix: amend the plan retrospectively OR add a project-skill note recommending general-purpose over Explore for audits.

## P3 — nice-to-have / tracked-deferred

- CI workflow inconsistency: `audit-writeup.yml:36` uses `astral-sh/setup-uv@v8.1.0` while `ci.yml` + `publish.yml` use ad-hoc `pip install uv`. Consider unifying. Out-of-scope for v1.2.13.
- `.pre-commit-config.yaml`: `mirrors-mypy v1.8.0` older relative to other hooks (ruff at v0.15.13). Not a defect; bump when convenient.
- All AUROC / AUPRC / sample-size numerics cross-file consistent (LoRA 0.383 [0.374, 0.392]; TF-IDF 0.371; Frozen 0.515; ProtectAI v1 0.361; ProtectAI v2 0.314; 412/1101 random floor 0.374). Spot-checked across README, EXECUTIVE_SUMMARY, RESULTS, WRITEUP, index.qmd, READING_GUIDE.
- Terminology clusters per ADR-064: clean across reviewer-facing surfaces. No "chunk_and_average" identifier leak in prose; "detector vs rung" clarifier pattern correctly applied at `WRITEUP.md:19`.
- CHANGELOG ADR coverage: 51 distinct ADR-NNN refs across CHANGELOG entries; covers recent ADRs (ADR-066 through ADR-075). Older ADRs landed pre-CHANGELOG-discipline. No action.
- Audit-script imports: none reference `eval_toolkit`. All use stdlib + pandas + yaml. No stale-API surface.
- `_quarto.yml`: every sidebar/navbar href resolves; favicon + styles present. Clean per A3 verification.

## Audit dimension mapping

| Dim | Dimension                              | Findings                              |
|-----|----------------------------------------|----------------------------------------|
| 1   | Terminology consistency                | P1-5 (Finding-3 framing); P2 GLOSSARY  |
| 2   | Cross-reference health                 | P1-6 (supersession back-links); P2 ADR-024 JSTOR; P2 local-fs paths |
| 3   | CI + audit-script health               | Clean (all 6 scripts + pytest exit 0); P3 workflow inconsistency |
| 4   | CHANGELOG/ADR/SUBMISSION_AUDIT triangulation | Clean (75=75=51-refs); P3 older ADRs lack CHANGELOG entries |
| 5   | Library-first ledger sync              | P1-7 runpod pin contradiction; P2 missing #50/51/52 rows; P2 ADR-066 bump-trigger; P2 "Phase 4" stale markers |
| 6   | Glossary completeness                  | P2 GLOSSARY.md:36 stale question wording |
| 7   | Reviewer-path integrity + URL resolution | Clean (3 URL checks 200; live site 200); P0-1 pin staleness on top-fold |
| 8   | CLAUDE.md / AGENTS.md staleness        | P1-2 (ADR count); P1-3 (ADR-073 pointer); P1-4 (AGENTS.md missing section); P2 anti-pattern phrasing |
| 9   | No-emoji + style gates                 | Clean (check_no_emoji.py exit 0)       |
| 10  | Test coverage + pytest                 | Clean (202 pass / 38 skip / 1 xfail)   |

---

# Proposed v1.2.13 remediation plan (appendix)

**Type**: polish patch (no methodology / model / data / compute change).
**Authority**: most changes are reader-facing prose (free); ADR changes
use ADR-068 / ADR-069 in-place authorization; one new ADR (ADR-076)
extends ADR-072's frontmatter-backfill pattern.

## Commit sequence (proposed)

### Commit 1 — Reader-facing accuracy sweep (closes P0-1, P0-2, P1-1, P1-5)

```
docs: v1.2.13 prep — reader-facing accuracy sweep + v1.2.12 pin propagation

Closes REPO_AUDIT_2026-05-21 P0-1, P0-2, P1-1, P1-5:

- README.md:136 + WRITEUP.md:4 + READING_GUIDE.md:141 — update
  "current state" to tree/v1.2.12 (2026-05-21); historical v1.0.0
  pin untouched per ADR-033.
- docs/for-hiring-managers.md:83 — "70 immutable ADRs" → "75 immutable ADRs".
- WRITEUP/methodology-guarantees.md:12 — "70 ADRs ... ADR-070" → "75
  ADRs ... ADR-075"; line 87 prose qualifier ("at Phase 5 close" →
  "at v1.0.0 submission gate") for clarity.
- WRITEUP.md:171 + index.qmd:113 — reframe Finding 3 heading + body
  from "actively harmful" to "anti-correlated with cross-family attack
  class" (consistent with for-hiring-managers.md:34 and v1.2.11 polish).
```

### Commit 2 — CLAUDE.md + AGENTS.md governance refresh (closes P1-2, P1-3, P1-4)

```
docs: v1.2.13 — CLAUDE.md + AGENTS.md governance refresh

Closes REPO_AUDIT_2026-05-21 P1-2, P1-3, P1-4:

- CLAUDE.md:13 — "70 ADRs at v1.2.8 close" → "75 ADRs at v1.2.12
  close"; append ADR-073/074/075 to governance-list parenthetical.
- CLAUDE.md:64-86 — append pointer "(rule consolidated and re-stated
  in [ADR-073](decisions/ADR-073-...md)" after the narrow-exceptions
  block.
- AGENTS.md — backport §Narrow exceptions section from CLAUDE.md
  (verbatim) so non-Claude agents see the four in-place
  factual-defect classes.
```

### Commit 3 — ADR-076 supersession-back-link backfill (closes P1-6 + part of P2 closing_commit)

```
feat: ADR-076 — superseded_by frontmatter backfill (ADR-046 + ADR-054
+ ADR-061 → ADR-062) + closing_commit population for ADR-071..075

Extends ADR-072's frontmatter-backfill pattern. Updates
ADR-046/054/061 `superseded_by: [062]` (was empty []) — matches
convention at ADR-023 + ADR-036 + ADR-053 (in-place superseded_by
edit per ADR-054 §F + CLAUDE.md immutability rule narrow exception
for frontmatter-supersession). Closes REPO_AUDIT_2026-05-21 P1-6.

Also populates ADR-071..075 closing_commit: frontmatter (the
recursive gap ADR-072 itself opened). closing_commit values:
- ADR-071: v1.2.8 close commit (slug-sweep)
- ADR-072: v1.2.9 close commit (frontmatter backfill landed)
- ADR-073: v1.2.9 close commit (consolidated re-statement)
- ADR-074: v1.2.9 close commit (ADR-064 redaction)
- ADR-075: v1.2.9 close commit (full-FT OOD unification)
Closes part of P2 (ADR-071..075 empty closing_commit).

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit 4 — ADR factual-defect sweep per ADR-068 + ADR-069 (closes P2 cross-refs)

```
docs: v1.2.13 — ADR-068 broken-external-ref + ADR-069 JSTOR-DOI
canonicalization sweep

Per ADR-068 (broken external references) + ADR-069 (publisher-URL
→ DOI canonicalization), in-place corrections:

- ADR-024:13 — jstor.org/stable/27033529 → doi.org/10.2307/27033529
  (per ADR-069; sibling DOI form already at ADR-024:16).
- ADR-020:206 — /home/brandon_behring/Claude/runpod-deploy →
  https://github.com/brandon-behring/runpod-deploy (per ADR-068).
- ADR-025:41-43 — three local-fs eval-toolkit refs → upstream
  github.com URLs (per ADR-068).
- ADR-061:287 + ADR-063:89 — ../.claude/plans/ paths → redacted +
  flagged via [PLAN_REF redacted; per ADR-068 Class Y] inline
  marker (no canonical replacement since plans are gitignored).

Body prose unchanged; only links updated. All changes in the four
ADR-067-070 narrow-relaxation classes.

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit 5 — Library-first ledger refresh (closes P1-7 + P2 ledger items)

```
docs: v1.2.13 — library_imports.md + upstream_issues.md ledger refresh

Closes REPO_AUDIT_2026-05-21 P1-7 + ledger P2 items:

- library_imports.md:85 — section header "[v0.7.7 pinned]" → "[v0.8.4
  pinned]" (matches table row line 29 + pyproject.toml line 84).
- library_imports.md:39 — bump triggers — add 4th bullet referencing
  ADR-066 (dependency/ledger maintenance trigger).
- library_imports.md:57,59,60,69-76 — "Phase 4 deliverable" /
  "Phase 4 Commit N" → "landed" (where applicable).
- upstream_issues.md — add ledger rows for eval-toolkit #50 (CLOSED;
  rationale: not-applicable / portfolio-scope), #51 (OPEN;
  spotlighting recipe — pending-consumption), #52 (OPEN; stacking —
  pending-consumption).
- CLAUDE.md + AGENTS.md anti-patterns — phrasing update per memory
  [[library_first_is_project_wide_invariant]] strengthened form.

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit 6 — Reader-facing polish (closes P2 reader-facing items)

```
docs: v1.2.13 — RESULTS + WRITEUP + GLOSSARY polish

Closes REPO_AUDIT_2026-05-21 P2 reader-facing polish items:

- RESULTS.md:61 — add ** marker + Phase-5-X11-crash footnote to
  ModernBERT full-FT row (parity with EXECUTIVE_SUMMARY:92 +
  for-hiring-managers:55 + index.qmd:94 per ADR-075).
- RESULTS.md:89-90 + WRITEUP.md:131 — add "not a clean OOD baseline"
  caveat to ProtectAI rows' "Read" column (parity with
  EXECUTIVE_SUMMARY:35-36 + README:39-40 + index.qmd:52-53).
- GLOSSARY.md:36 — update question wording to "What does this say
  about how the candidate thinks?" matching
  docs/for-hiring-managers.md:81.

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit 7 — CHANGELOG close + audit-finding cross-references

```
docs: v1.2.13 — CHANGELOG [1.2.13] entry + REPO_AUDIT_2026-05-21
audit-trail close

Closes REPO_AUDIT_2026-05-21 as resolved-by-v1.2.13.

- CHANGELOG.md [1.2.13] entry listing all 7 commit's worth of fixes.
- decisions/audits/REPO_AUDIT_2026-05-21.md — add resolution header
  noting v1.2.13 close (parallel to REPO_AUDIT_2026-05-18.md
  resolution header pattern).
- regenerate SUBMISSION_AUDIT.md (likely a no-op since CLAIM count
  unchanged; only ADR-076 added).
- bump tag → v1.2.13.

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Sequencing + gates

- **Gate after each commit**: `.venv/bin/python scripts/audit_writeup_numbers.py && .venv/bin/python scripts/check_no_emoji.py && .venv/bin/python scripts/regenerate_audit.py --check && .venv/bin/pytest -q` — all should remain exit 0.
- **Gate after Commit 4** (ADR cross-ref sweep): `.venv/bin/python scripts/audit_rendered_site.py` to confirm Quarto render still happy.
- **Gate after Commit 5**: re-run `gh issue list --repo brandon-behring/eval-toolkit --state all` and verify ledger entries match.
- **Final gate before v1.2.13 tag**: lychee link-check via the CI workflow (or local `lychee --offline` if available); confirm all 3 reviewer URLs still return 200; confirm gh-pages CI build green.

## Estimated patch cost

- ~30 lines reader-facing prose edits (Commit 1 + Commit 6)
- ~20 lines CLAUDE.md / AGENTS.md edits (Commit 2 + Commit 5 anti-patterns)
- 1 new ADR (~150-200 lines per ADR-072's precedent) + 4 frontmatter edits (Commit 3)
- ~10 ADR cross-ref / URL edits (Commit 4)
- ~15 lines ledger edits (Commit 5)
- 1 CHANGELOG entry (~30 lines) + audit-file resolution header (Commit 7)

Total ~250-300 lines across ~17 files. No GPU spend.

## Out of scope (deferred to NEXT_STEPS or later patches)

- Per-row prediction parquets per ADR-075 §9.5 (mechanism-interpretation empirical demonstration target) — portfolio-repo scope per `[[portfolio_plan_approved]]`.
- Multi-seed × multi-fold replication (NEXT_STEPS §2.1-§2.2) — portfolio-repo scope.
- eval-toolkit #36 (recall-at-low-fpr contribution) — upstream-driven; consume on next eval-toolkit release if landed.
- eval-toolkit #51 spotlighting + #52 stacking — pending v1.3.x methodology decisions; out of v1.2.13 polish scope.
- CI workflow setup-uv unification (P3) — convenience; defer.
- mypy version bump (P3) — defer until next dev-tool sweep.
- Plan-vs-tool mismatch documentation (Explore vs general-purpose for audits) — write a project skill / CLAUDE.md addendum in a follow-up session.

---

## Lessons noted from execution

- **Machine-checkable signal was 100% clean.** All 6 audit scripts +
  pytest + URL resolution + ADR/CLAIM count + regenerate-audit diff =
  green. The v1.2.9-v1.2.12 polish arc fully discharged the
  machine-checkable debt that REPO_AUDIT_2026-05-18 surfaced.
- **All remaining debt is prose-propagation debt.** Each finding is
  some flavor of "the v1.2.9-v1.2.12 polish didn't reach surface X".
  Suggests a project skill / lint hook that, when a polish patch lands,
  greps for the changed canonical phrases across all reader-facing
  surfaces — would have caught P0-1, P0-2, P1-1, P1-5 mechanically.
- **The ADR-072 frontmatter-backfill pattern is now load-bearing**:
  this audit identified two more candidates (ADR-046/054/061
  superseded_by + ADR-071-075 closing_commit) that fit the same
  pattern. ADR-076 (proposed) makes the third backfill ADR; consider
  whether a tooling hook should auto-detect this class.
- **Plan-vs-tool mismatch** (Explore vs general-purpose for audits):
  the plan templates may need a quick "audit tasks → general-purpose
  agent" note. Found mid-execution; recorded as P2 finding.
