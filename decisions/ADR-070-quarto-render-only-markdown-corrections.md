---
adr_id: "070"
slug: quarto-render-only-markdown-corrections
title: Narrow immutability relaxation for render-only Markdown corrections in immutable ADRs
date: 2026-05-19
status: Accepted
claim_id: CLAIM-070
claim: >-
  ADR-067, ADR-068, and ADR-069 established three narrow exceptions to
  the ADR immutability rule for factual defects that make locked ADRs
  misleading or unusable without changing their decisions. The v1.2.8
  rendered-site audit surfaced a fourth distinct class: Markdown syntax
  that preserves the intended source prose but is parsed incorrectly by
  Quarto when ADRs are rendered as HTML. ADR-034 contains an outer
  ```markdown fenced example that includes inner ```bash fences; Markdown
  requires a longer outer delimiter for nested fences, so Quarto emits a
  fenced-div warning and can render the page incorrectly. ADR-070 permits
  only render-only Markdown delimiter corrections inside immutable ADRs
  when the visible decision text, numeric values, links, alternatives,
  frontmatter, and methodology are unchanged. v1.2.8 applies this once:
  ADR-034's outer example fence changes from triple backticks to quadruple
  backticks so the existing inner code fences remain literal example text.
source: v1.2.8 rendered-site hardening audit; Quarto warning cleanup from `make site`
acceptance_criterion: >-
  At v1.2.8 close: ADR-070 exists; decisions/README.md, CLAUDE.md, and
  docs/GLOSSARY.md describe four narrow immutability exceptions including
  this render-only Markdown syntax class; ADR-034 changes only the outer
  fence delimiter around the existing reproducibility-spoke Markdown
  example; `make site` emits no citation-processor or fenced-div warning
  for the affected ADR; `make audit` passes after regenerating
  SUBMISSION_AUDIT.md.
closing_commit: v1.2.8
supersedes: []
superseded_by: []
references:
  - https://spec.commonmark.org/0.31.2/#fenced-code-blocks
  - https://quarto.org/docs/authoring/markdown-basics.html
  - decisions/ADR-034-reproducibility-tier-full-ladder.md
  - decisions/ADR-067-immutability-clarification-and-canonical-slug-reference.md
  - decisions/ADR-068-immutability-narrow-relaxation-for-broken-external-references.md
  - decisions/ADR-069-immutability-narrow-relaxation-for-publisher-url-to-doi-canonicalization.md
transcript: transcripts/2026-05-19__v1-2-8-full-audit-batch.md
---

# ADR-070 - Narrow immutability relaxation for render-only Markdown corrections in immutable ADRs

## Status

Accepted (2026-05-19; fourth narrow clarification of the existing ADR
immutability rule; covers render-only Markdown syntax corrections that do
not change decision content).

## Context

The v1.2.8 site audit changed ADRs from repo-only Markdown artifacts into
hard-gated rendered HTML pages. During render, Quarto reported a warning
against ADR-034 because the file uses a fenced `markdown` example that
contains fenced `bash` examples inside it. In Markdown, nested fenced code
blocks need a longer outer delimiter than their inner delimiters. ADR-034's
intended content is clear in source form, but the renderer cannot reliably
distinguish the inner fences from the outer fence.

The existing immutability rule remains correct: locked ADR decisions are
not edited in place. The issue here is narrower. The decision text, command
examples, links, alternatives, frontmatter, and methodology are unchanged;
only the fence delimiter needed by the renderer is wrong.

## Decision

Permit a fourth narrow exception to ADR immutability: render-only Markdown
syntax corrections may be made in place when all of the following are true:

1. The correction changes only Markdown delimiters or equivalent syntax
   needed for faithful rendering.
2. The visible text, numeric values, links, alternatives, frontmatter,
   decision status, and methodology remain unchanged.
3. The commit message cites ADR-070 and lists the affected ADR file.
4. The change is verified by `make site` and `make audit`.

For v1.2.8, the only in-scope edit is ADR-034's outer fenced example:
change the outer `markdown` fence from triple backticks to quadruple
backticks so the existing inner `bash` fences render as literal example
content.

## Consequences

Rendered ADR pages can be hard-gated without allowing content edits to
locked decisions.

The exception is intentionally mechanical and narrow. It does not permit
rewriting ADR prose, correcting numbers, changing links, changing
frontmatter semantics, replacing citations, or modifying decisions. Those
remain governed by the existing ADR immutability rule and require a
superseding ADR unless covered by ADR-067, ADR-068, or ADR-069.

## Alternatives Considered

**Leave ADR-034 unchanged and ignore the Quarto warning.** Rejected because
the public site is now a primary reader artifact, and warnings that indicate
misparsed Markdown undermine the rendered-site hard gate.

**Exclude immutable ADRs from the site.** Rejected because the ADR trail is
part of the methodology evidence and already appears in navigation.

**Rewrite the ADR-034 example prose.** Rejected because the needed fix is a
delimiter correction; prose changes would exceed the render-only scope.
