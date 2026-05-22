# Project-level Claude instructions

> **Public-site note.** This is an operator/agent instruction file rendered for
> transparency. It is not part of the main results narrative.

This is a case-study submission repo using SDD (spec-driven development).
Before any work, read `SPEC_GREENFIELD.md` (the binding spec).

## Phase 0 workflow

Phase 0 runs the spec lock-in interview via the `/exploring-options` skill
against `SPEC_GREENFIELD.md`'s decision ledger (~50 Phase-0 decisions across
~9 topic-focused sub-sessions; 80 ADRs at v1.3.1 close (79 at v1.3.0 close)
including post-v1.0.0 patch governance: ADR-051 carryforward + ADR-052
full-FT reframing + ADR-053 reading-guide governance + ADR-061 nav
restructure + ADR-067-070 immutability-relaxation chain consolidated in
ADR-073 + ADR-074 redaction governance + ADR-075 full-FT OOD narrative
unification + ADR-076 supersession + closing_commit frontmatter backfill
+ ADR-077 supersession-backlink and octal-quoting frontmatter backfill
+ ADR-078 EXECUTIVE_SUMMARY absorption + ADR-079 two-guide reader
architecture + ADR-080 reviewer-URL-pin numeric correction). See `SPEC_GREENFIELD.md` §Phase 0
for the recommended sub-session sequence.

**For each `[OPEN]` decision walked, Claude must surface:**

1. Concrete explanation of what the decision means
2. Options with pros/cons
3. **2-3 definitive reference URLs** (peer-reviewed paper, library docs,
   methodology guide). Primary source: `docs/research/` dossier
   (MANIFEST.json's `claim_family` field maps decisions to supporting
   research). The dossier covers methodology decisions (~30 of 50 rows);
   non-methodology rows (brief alignment, library version pinning,
   submission deliverables, repo hygiene) rely on web search.
4. Recommendation with rationale

**Fresh-investigation rule** (load-bearing): when walking each `[OPEN]`
decision, **read the relevant `docs/research/` dossier files live at
decision time**. Do not pre-load assumed candidates from training memory
or prior knowledge. The dossier is the source. Use MANIFEST.json to find
the right files via `claim_family` / `verification_status` / `tags`;
then open them and surface the actual candidates documented there.
Supplement with web search only when the dossier is silent on a specific
decision.

After each sub-session, invoke `/save-transcript phase-0-NN__<topic>` to
checkpoint the conversation to `transcripts/<YYYY-MM-DD>__<slug>.md`.

**Transcripts are private by default** (gitignored, only `transcripts/README.md`
is tracked). The brief, Phase 0 conversations, and raw rationale stay local.
For Phase 0-00 brief alignment, paste the brief (or key excerpts) into the
conversation; the brief does not need to be committed as a standalone file.
At submission time, transcripts are emailed to the reviewer separately so
they see the decision trail without the raw content appearing on the public
repo. ADRs (public) reference transcripts by filename; reviewer correlates via
the emailed bundle.

Each locked decision produces:

1. An ADR at `decisions/ADR-NNN-<slug>.md` (Michael Nygard format; see
   `decisions/README.md` for the frontmatter schema)
2. SPEC_GREENFIELD appendix row updated: `locked-to-X (see ADR-NNN)`
3. SPEC_SHEET corresponding `[OPEN]` slot updated: `[LOCKED: X (per ADR-NNN)]`
4. SUBMISSION_AUDIT.md regenerates from ADRs via
   `python scripts/regenerate_audit.py`

The **ADR is the source of truth**. ADRs are immutable; supersede via new
ADR marking prior `status: superseded-by-NNN`.

**Narrow exceptions** (per [ADR-067](decisions/ADR-067-immutability-clarification-and-canonical-slug-reference.md) + [ADR-068](decisions/ADR-068-immutability-narrow-relaxation-for-broken-external-references.md) + [ADR-069](decisions/ADR-069-immutability-narrow-relaxation-for-publisher-url-to-doi-canonicalization.md) + [ADR-070](decisions/ADR-070-quarto-render-only-markdown-corrections.md)):
FOUR factual-defect / render-defect classes MAY be corrected in-place
with a commit message citing the relevant ADR + listing per-file corrections:

1. **Cross-reference slug filename typos** (per ADR-067) — a slug
   pointing at a wrong-but-existing canonical file in `decisions/`.
2. **Broken external references** (per ADR-068) — markdown links
   pointing at local-filesystem paths (`/home/<author>/...`,
   `../../../.claude/...`) or aspirational upstream resources
   (URLs returning 404 from the upstream repo) that cannot resolve
   on any non-author machine.
3. **Publisher-URL → DOI canonicalization** (per ADR-069) — academic
   publisher landing-page URLs (`journals.sagepub.com/doi/<DOI>`,
   `tandfonline.com/doi/<DOI>`, `jstor.org/stable/<ID>`,
   `dl.acm.org/doi/<DOI>`) that 403 unauthenticated CI bots MAY be
   canonicalized to `doi.org/<DOI>` (the academic-canonical
   bot-friendly identifier; same paper, more durable).
4. **Render-only Markdown syntax corrections** (per ADR-070) — delimiter
   or equivalent markup fixes required for faithful Quarto rendering,
   with visible decision content unchanged.

ALL other content (numeric values, methodology, prose, alternatives,
non-slug frontmatter, table data) remains immutable per the rule above.
(Rule consolidated and re-stated in [ADR-073](decisions/ADR-073-adr-immutability-rule-consolidated-re-statement.md);
read that ADR for the consolidated narrative. Frontmatter-completeness
backfills — `closing_commit:` + `superseded_by:` — are governed by the
ADR-072/ADR-076 frontmatter-backfill precedent, a fifth narrow-relaxation
class adjacent to A-D.)

### Phase 0 shorthand

When the user invokes `/exploring-options phase 0-NN` (or any
`/exploring-options` whose argument contains "phase 0"), execute the
full sub-session workflow:

1. Look up the section name + row list from
   `docs/ROADMAP.md` §"Recommended sub-session sequence" (e.g.,
   `phase 0-01` → §0 Threat, 4 rows: attack classes, language, length
   cap, truncation policy).
2. Read each `[OPEN]` row from `SPEC_GREENFIELD.md`'s ledger appendix.
3. Walk each row under the **educational-references rule** above
   (concrete explanation + options + 2-3 reference URLs surfaced via
   the **fresh-investigation rule** from `docs/research/` dossier +
   recommendation) — generate all questions upfront and present them
   numbered (per `/exploring-options` skill).
4. For each lock the user accepts:
   - Write `decisions/ADR-NNN-<slug>.md` (Michael Nygard format;
     frontmatter per `decisions/README.md`; include `transcript:`
     field pointing at the file `/save-transcript` will produce).
   - Update the SPEC_GREENFIELD ledger row status to
     `locked-to-X (see ADR-NNN)`.
   - Fill the matching SPEC_SHEET slot with `[LOCKED: X (per ADR-NNN)]`.
5. Run `python scripts/regenerate_audit.py` to refresh
   `SUBMISSION_AUDIT.md`.
6. Prompt the user to invoke
   `/save-transcript phase-0-NN__<topic-slug>`.
7. Propose **one** descriptive commit covering the sub-session (e.g.,
   `feat: Phase 0-01 threat model locks (ADR-NNN to ADR-MMM)`).

If the user invokes `/exploring-options` with an argument that does not
match `phase 0-NN`, treat it as a generic exploration (no Phase 0
workflow) — the shorthand is opt-in via the "phase 0" token.

## Library-first discipline

Three load-bearing libraries (never hand-roll equivalents):

- eval-toolkit — https://github.com/brandon-behring/eval-toolkit
- runpod-deploy — https://github.com/brandon-behring/runpod-deploy
- research_toolkit — https://github.com/brandon-behring/research_toolkit

The rule bans replacing library primitives; project-specific glue (data
loaders, custom scorers using upstream primitives, project-named CLIs)
is allowed and expected.

Track every import / skill invocation in `decisions/library_imports.md`.
File upstream issues for any gap before any local workaround; ledger at
`decisions/upstream_issues.md`.

New literature dossier work uses the research_toolkit pipeline
(`/research-plan` → `/research-gather` → `/dossier-build` → `/agent-index`
→ `/dossier-audit`). The current dossier at `docs/research/` was produced
this way.

## Transcript convention

Every multi-turn decision conversation produces a transcript at
`transcripts/<YYYY-MM-DD>__<slug>.md` via `/save-transcript <slug>`.
ADRs that result from a transcript reference it in the `transcript:`
frontmatter field.

## Commit discipline

- Each meaningful work unit = its own commit
- Type-prefixed messages: `feat:` `refactor:` `docs:` `chore:` `test:` `fix:` `seed:`
- Trailer: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Reference `ADR-NNN` in commits that lock or supersede a Phase 0 decision
- **No amend / no squash / no force-push** — fix-forward with new commits.
  The history is meant to show real development including missteps.

## Anti-patterns to avoid

- Hand-rolling a primitive that belongs in `eval-toolkit` /
  `runpod-deploy` / `research_toolkit` (strengthened 2026-05-18: no
  local workarounds; missing upstream primitives **block** dependent
  work pending the upstream MR — the older "thin local glue + TODO
  marker" pattern is retired)
- Continuing dependent work on a TODO-marker local stub after filing
  the upstream issue, instead of waiting for the upstream MR to land
- Skipping transcript capture for a multi-turn decision conversation
- Mutating a locked decision without writing a superseding ADR
- Tuning on test data — even informally during error analysis
- **For design-doc audits / cross-file consistency checks / open-ended
  polish reviews**: using the Explore subagent — Explore's own docs
  explicitly forbid this use class ("Do NOT use it for code review,
  design-doc auditing, cross-file consistency checks, or open-ended
  analysis — it reads excerpts rather than whole files and will miss
  content past its read window"). Use general-purpose agents for
  audit-class tasks instead.
- Rewriting git history (amend, squash, force-push)
- Adding a methodology component without an ADR
- Adding an evaluation dataset without a leakage scan
- Persisting only summary metrics without per-row predictions
- Introducing a project-specific term without adding it to `docs/GLOSSARY.md`
