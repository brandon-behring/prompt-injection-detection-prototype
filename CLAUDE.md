# Project-level Claude instructions

This is a case-study submission repo using SDD (spec-driven development).
Before any work, read `SPEC_GREENFIELD.md` (the binding spec).

## Phase 0 workflow

Phase 0 runs the spec lock-in interview via the `/exploring-options` skill
against `SPEC_GREENFIELD.md`'s decision ledger (~50 decisions across
~9 topic-focused sub-sessions). See `SPEC_GREENFIELD.md` §Phase 0 for the
recommended sub-session sequence.

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

- Hand-rolling functionality already in the three libraries
- Working around a library limitation without filing an upstream issue
- Skipping transcript capture for a multi-turn decision conversation
- Mutating a locked decision without writing a superseding ADR
- Tuning on test data — even informally during error analysis
- Rewriting git history (amend, squash, force-push)
- Adding a methodology component without an ADR
- Adding an evaluation dataset without a leakage scan
- Persisting only summary metrics without per-row predictions
- Introducing a project-specific term without adding it to `docs/GLOSSARY.md`
