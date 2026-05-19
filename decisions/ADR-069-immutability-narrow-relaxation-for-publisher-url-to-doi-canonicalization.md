---
adr_id: "069"
slug: immutability-narrow-relaxation-for-publisher-url-to-doi-canonicalization
title: Narrow immutability relaxation for academic publisher-URL → DOI canonicalization in immutable ADRs
date: 2026-05-19
status: Accepted
claim_id: CLAIM-069
claim: >-
  ADR-067 (v1.2.2) + ADR-068 (v1.2.5) established TWO narrow exceptions to
  the CLAUDE.md ADR-immutability rule covering (i) slug typos in cross-
  references + (ii) broken external references to local-filesystem paths
  or aspirational upstream resources. The first end-to-end lychee scan at
  v1.2.4 surfaced a THIRD distinct class inside immutable ADRs: **publisher-
  URL bot-403 academic citations**. 26 markdown links across 10 immutable
  ADRs (ADR-005, ADR-006, ADR-007, ADR-011, ADR-015, ADR-021, ADR-022,
  ADR-023, ADR-024, ADR-056) cite peer-reviewed methodology papers via
  publisher landing-page URLs (`journals.sagepub.com/doi/<DOI>`,
  `tandfonline.com/doi/<DOI>`, `jstor.org/stable/<ID>`, `dl.acm.org/doi/<DOI>`,
  `ojs.aaai.org/index.php/AAAI/article/view/<ID>`, `researchgate.net/publication/<ID>`).
  These URLs work for human readers (subscription / institutional / paywall
  access) but academic publishers actively bot-403 unauthenticated CI scans.
  The bot-blocking is STRUCTURAL: it will never be fixed upstream and
  cannot be worked around with auth in CI. The canonical academic
  identifier is the **DOI** (Digital Object Identifier), resolved via
  `doi.org/<DOI>`. The DOI resolver is the durable citation target;
  where lychee follows DOI redirects into publisher pages that still
  bot-403, `.lycheeignore` carries exact DOI exceptions rather than
  broad publisher-domain ignores. Each publisher URL embeds the DOI in its
  path; canonicalization is a mechanical sed transformation that:
  preserves citation intent EXACTLY; replaces unstable publisher-page
  URLs with the AUTHORITATIVE academic identifier; narrows bot-403
  noise in CI to exact documented DOI exceptions; aligns with CrossRef
  + academic-citation best practice.
  ADR-069 codifies this as the THIRD narrow exception to the ADR-
  immutability rule, parallel to ADR-067 + ADR-068 with the same §B-style
  out-of-scope-list discipline. v1.2.6 applies the rule to fix
  26 publisher-URL citations across the 10 affected immutable ADRs.
source: v1.2.6 link-check fix-forward (root-cause analysis began during the v1.2.5 /exploring-options round) — post-execution discovery revealed 26 publisher-URL citations all in immutable ADRs; user-recommended option "Sed-based DOI canonicalization across all .md files" requires an ADR-069 cover for the immutable ADR edits.
acceptance_criterion: >-
  At v1.2.6 close: `decisions/ADR-069-immutability-narrow-relaxation-for-publisher-url-to-doi-canonicalization.md`
  exists (this file). Publisher-URL citations across the 10 affected
  immutable ADRs are replaced with `doi.org/<DOI>` equivalents where valid
  (DOI embedded in each publisher URL's path, extracted via deterministic
  sed pattern, except the one JSTOR stable reference without a valid
  `10.2307/<ID>` DOI remains as its original stable URL with an exact
  `.lycheeignore` entry). Lychee CI on the v1.2.6 push reports the
  publisher-URL bot-403 entries resolved or covered by exact documented
  DOI/stable-link exceptions. Future PR reviews flag any in-place ADR edit
  that goes beyond the three enumerated narrow scopes (ADR-067 slug
  typos + ADR-068 broken external refs + ADR-069 publisher → DOI canon).
closing_commit: v1.2.6
supersedes: []
superseded_by: []
references:
  - CLAUDE.md  # immutability rule lives here; gets triple-narrow-exception update
  - decisions/README.md  # ADR lifecycle; gets triple-narrow-exception update
  - decisions/ADR-067-immutability-clarification-and-canonical-slug-reference.md  # precedent narrow relaxation (Class A: slug typos)
  - decisions/ADR-068-immutability-narrow-relaxation-for-broken-external-references.md  # precedent narrow relaxation (Class B: broken external refs)
  - docs/GLOSSARY.md
transcript: transcripts/2026-05-19__v1-2-5-link-check-content-debt-and-immutability-extension.md
---

# ADR-069 — Narrow immutability relaxation for academic publisher-URL → DOI canonicalization in immutable ADRs

## Status

Accepted (2026-05-19; third narrow clarification of the existing CLAUDE.md immutability rule — co-equal with ADR-067 + ADR-068; covers a third class of factual defects: bot-blocked publisher URLs that would be permanently broken in CI without canonicalization to the academic-standard DOI identifier).

## §A Context — academic publisher URLs vs DOI canonicalization

The first end-to-end lychee scan at v1.2.4 surfaced 26 publisher-URL bot-403 entries across 10 immutable ADRs. The URLs cite peer-reviewed methodology papers via:

- `journals.sagepub.com/doi/<DOI>` (Sage Publications)
- `www.tandfonline.com/doi/abs/<DOI>` (Taylor & Francis)
- `www.tandfonline.com/doi/full/<DOI>` (Taylor & Francis)
- `www.jstor.org/stable/<ID>` (JSTOR)
- `dl.acm.org/doi/<DOI>` (ACM Digital Library)
- `ojs.aaai.org/index.php/AAAI/article/view/<ID>` (AAAI)
- `www.researchgate.net/publication/<ID>` (ResearchGate)

These academic publishers actively bot-block unauthenticated traffic for paywalled content (anti-scraping protection). The URLs resolve cleanly in browsers (with subscription / institutional / paywall access), but lychee CI scans receive 403 Forbidden responses. This is STRUCTURAL — not a bug to be fixed upstream; not workaroundable with auth tokens; not transient link rot.

The canonical academic identifier for each paper is the **DOI** (Digital Object Identifier), resolved via `doi.org/<DOI>`. DOI URLs are run by CrossRef as a stable redirect service and are academically authoritative — DOI is the citation identifier per CrossRef + IETF RFC 7320 conventions. Lychee follows redirects, so a DOI can still land on a publisher page that bot-403s unauthenticated CI. For that residual class, `.lycheeignore` carries exact DOI exceptions instead of broad publisher-domain ignores.

Crucially: **every publisher URL listed above embeds the DOI in its path**. Sed-based canonicalization is mechanical and lossless:

- `journals.sagepub.com/doi/10.1177/X` → `doi.org/10.1177/X`
- `tandfonline.com/doi/abs/10.1198/Y` → `doi.org/10.1198/Y`
- `dl.acm.org/doi/10.1145/Z` → `doi.org/10.1145/Z`
- JSTOR + AAAI + ResearchGate use their own internal IDs. When a valid DOI is available, the URL is replaced with the DOI-equivalent; otherwise the original stable URL is retained with an exact `.lycheeignore` entry.

## §B Decision — third narrow exception covering publisher-URL canonicalization

ADRs remain immutable for **decision content** (per CLAUDE.md + ADR-067 §B + ADR-068 §B). ADR-069 covers an additional narrow class:

### B1 — In-scope corrections (allowed in-place per this ADR-069)

**Class Z — Academic publisher-URL → DOI canonicalization.** Markdown links pointing at academic publisher landing pages that 403 bots may be replaced with `doi.org/<DOI>` equivalents where the DOI is extractable from the publisher URL path. Supported publisher patterns + canonicalization:

| Publisher URL pattern | Canonical DOI URL |
|---|---|
| `journals.sagepub.com/doi/<DOI>` | `doi.org/<DOI>` |
| `www.tandfonline.com/doi/(abs\|full)/<DOI>` | `doi.org/<DOI>` |
| `dl.acm.org/doi/<DOI>` | `doi.org/<DOI>` |
| `www.jstor.org/stable/<ID>` | `doi.org/10.2307/<ID>` when valid; otherwise retain the JSTOR stable URL with an exact ignore |
| `ojs.aaai.org/index.php/AAAI/article/view/<ID>` | Citation-by-author-year retained; URL replaced with closest DOI if available, else AAAI-published-DOI equivalent |
| `www.researchgate.net/publication/<ID>` | Citation-by-author-year retained; URL replaced with DOI if extractable from paper metadata |

Fix discipline: preserve the link text exactly; replace the link target with the DOI URL. Example transformation:

- Before target: `journals.sagepub.com/doi/10.1177/0956797613504966`
- After target: `https://doi.org/10.1177/0956797613504966`

The citation text (author-year) is unchanged. The link target is the AUTHORITATIVE academic identifier when a valid DOI exists (same paper, more durable).

### B2 — Out-of-scope changes (REQUIRE superseding ADR per existing rule)

Same as ADR-067 §B2 + ADR-068 §B2; numeric values, methodology decisions, prose rationale, alternatives considered, non-slug frontmatter fields, and table content all remain immutable. ADR-069 covers ONLY the link-target text in publisher-URL citations; the surrounding sentence + paragraph + decision content stays as written.

ADR-069 applies ONLY to IMMUTABLE ADRs. Mutable files (SPEC_SHEET.md, SPEC_GREENFIELD.md, WRITEUP/*.md, etc.) can be edited freely per their existing mutability convention and do NOT need ADR-069 cover.

### B3 — Commit message convention

In-place publisher-URL → DOI canonicalization fixes in immutable ADRs carry a commit message of the form:

```
docs: ADR-NNN publisher-URL → DOI canonicalization per ADR-069 (Class Z)

Per ADR-069 narrow-relaxation rule (Class Z): academic publisher-URL
citations that 403 bots MAY be canonicalized to DOI-equivalent
(`doi.org/<DOI>`) URLs in-place in immutable ADRs. This commit
fixes (sed-based; mechanical lossless transformation):

- decisions/ADR-XXX.md:LINE — `<publisher-url>` -> `doi.org/<DOI>`
  ...

No decision content changed. ADR audit trail preserved. Citation
preserved (same paper; more durable identifier).
```

### B4 — Future PR review discipline (unchanged from ADR-067 + ADR-068)

In-place ADR edits that go beyond the three narrow scopes (slug typos + broken external refs + publisher → DOI canon) should be flagged by PR review + require a new superseding ADR per the existing rule. ADR-069 does NOT establish a slippery slope.

## §C Decision — apply in the v1.2.6 fix-forward

Publisher-URL citations across 10 immutable ADRs are canonicalized to DOI URLs where valid in the v1.2.6 fix-forward via batch sed transformation. The commit message enumerates each per-file substitution and the retained exact stable-link exception.

## §D Decision — CLAUDE.md + decisions/README.md updates

Both documents get the TRIPLE-narrow-exception update (cites ADR-067 + ADR-068 + ADR-069). docs/GLOSSARY.md gets a parallel update.

## §E Consequences

### E1 — Reader experience improved (academic citations now durable)

After the v1.2.6 fix-forward, publisher-URL citations use DOI URLs where valid (academic-canonical identifier; durable across publisher URL changes). One JSTOR stable link without a valid DOI remains on the original stable URL with an exact lychee exception. Readers get the same cited paper identity without broad publisher-domain ignores.

### E2 — Audit-trail discipline preserved

Same paper, same author-year citation text, same scholarly content. Only the link target changes from publisher-page-URL to DOI-URL. No decision content affected.

### E3 — Documentation debt paid down

Publisher-URL bot-403 entries in immutable ADRs are eliminated from the lychee CI noise or reduced to exact DOI/stable-link exceptions. The lychee link-check workflow stops failing on inherited historical citation transport while still checking current project-owned links.

### E4 — Three-ADR symmetry

ADR-067 (slug typos) + ADR-068 (broken external refs) + ADR-069 (publisher → DOI canon) are co-equal narrow exceptions to the same CLAUDE.md immutability rule. Each covers a distinct factual-defect class with the same audit-rationale (no decision content affected; CI cannot resolve original; in-place fix strictly improves reader experience; audit trail preserved). The three-ADR set bounds the scope: ANY OTHER in-place ADR edit requires a superseding ADR per the existing rule.

### E5 — Future PRs flagged on out-of-scope edits (unchanged)

Same as ADR-067 §B4 + ADR-068 §B4. The three narrow-relaxation ADRs are NOT slippery slopes; they codify specific, well-defined factual-defect classes.

### E6 — Cost-trivial

$0. Sed-based mechanical transformation across 10 immutable ADRs.

## Linked ADRs

- **References**:
  - CLAUDE.md — the source-of-truth for immutability (clarified by ADR-067 + ADR-068 + ADR-069 triple-narrow-exception)
  - decisions/README.md — the ADR lifecycle + frontmatter schema (gets triple-citation update)
  - [ADR-067](./ADR-067-immutability-clarification-and-canonical-slug-reference.md) — precedent narrow relaxation (Class A: slug typos)
  - [ADR-068](./ADR-068-immutability-narrow-relaxation-for-broken-external-references.md) — precedent narrow relaxation (Class B: broken external refs); v1.2.5 Commit 1
- **Source**: v1.2.6 link-check fix-forward; root-cause analysis began during the v1.2.5 /exploring-options walk and post-execution discovery revealed 26 publisher-URL citations all in immutable ADRs. User-recommended option "Sed-based DOI canonicalization across all .md files" requires an ADR-069 cover.

## Transcript

`transcripts/2026-05-19__v1-2-5-link-check-content-debt-and-immutability-extension.md` — captures the multi-class link-check content-debt close + the ADR-067/068/069 triple narrow-relaxation lineage.
