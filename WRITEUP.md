---
title: "Writeup — pick your guide"
description: "Router page directing readers to one of two reading-style guides (academic IMRAD or narrative arc) covering the same content."
---

This project's writeup ships in two reading-style formats. Pick the one
that matches how you'd like to read it.

| Style | Length | Best for |
|---|---|---|
| [**Academic paper (IMRAD)**](./WRITEUP_PAPER.md) | ~20–25 min | Reviewers expecting Abstract / Introduction / Methods / Results / Discussion / Limits / Conclusion / References discipline. Formal voice, technical terminology with on-first-use definitions. |
| [**Narrative arc (story)**](./WRITEUP_NARRATIVE.md) | ~15–20 min | Readers preferring plain-English first-person prose. Same content, story-style pacing (Hook → Setup → Investigation → Revelation → Implications). |

Both guides cover the same content (problem, methods, all 7 findings,
mechanism, limitations); the style and pacing differ. Technical terms
are defined on first use in either guide and cross-referenced to
[`docs/GLOSSARY.md`](./docs/GLOSSARY.md).

## Quick pointers

- **Just the numbers** → [RESULTS.md](./RESULTS.md) — tables + 5
  figures + raw artifact pointers, no narrative prose.
- **60-second tour** → [Project at a glance](./docs/for-hiring-managers.md).
- **README + executive summary** → [README.md](./README.md) — 1-page
  distillation including the headline + mechanism + direct-detection
  check tables.
- **Methodology spokes** (deep-dive references) → 8 files under
  [WRITEUP/](./WRITEUP/) covering data decisions, evaluation design,
  model details, threshold policy, reference-scorer audit, methodology
  guarantees, reproducibility, limitations + future work.
- **Decision trail** → 81 ADRs at [decisions/](./decisions/).

## Why two guides?

The previous single-guide structure was diagnosed in the v1.3.0
restructure as "neither narrative nor academic" — informal headings
plus academic numbering, methodology after results, same content
rendered with different prose across multiple pages. The two-guide
architecture (per [ADR-078](./decisions/ADR-078-executive-summary-absorbed-into-readme.md)
+ [ADR-079](./decisions/ADR-079-two-guide-reader-architecture.md))
gives each reader-type a self-contained article in its native
register, with no cross-page redundancy.

Old WRITEUP.md (the jumbled hybrid) content is now distributed across
the two guides; the historical content remains accessible at the
reviewer URL pin (`tree/v1.0.0`) per ADR-033 (corrected from a prior
`tree/v1.2.8` mis-citation per [ADR-080](./decisions/ADR-080-reviewer-url-pin-numeric-correction-adr-078-079.md)).

## Looking for a specific section? {#section-redirects}

If you arrived here from a `tree/v1.0.0`-era deep link (e.g., from
the submission email or a bookmarked anchor), the original v1.0.0
`WRITEUP.md` had 7 sections. They are now redistributed as below.

### §Reading guide {#reading-guide}

Reading-style routing for the methodology now lives in the dedicated
[READING_GUIDE.md](./READING_GUIDE.md) (academic / narrative /
hiring-manager / reproducer / data-only paths).

<a id="1-motivation"></a>
### §1 Motivation {#motivation}

Now in [WRITEUP_PAPER §1 Introduction](./WRITEUP_PAPER.md) (academic
framing) and [WRITEUP_NARRATIVE Act 0 — Hook](./WRITEUP_NARRATIVE.md)
(narrative framing).

<a id="1-5-attack-type-taxonomy-traintest-composition"></a>
<a id="attack-type-taxonomy-traintest-composition"></a>
### §1.5 Attack-type taxonomy + train/test composition {#attack-type-taxonomy}

The train/test composition table and OOD slate breakdown now live in
[WRITEUP/data-decisions.md](./WRITEUP/data-decisions.md) and
[WRITEUP_PAPER §3 Methods](./WRITEUP_PAPER.md). The high-level
taxonomy (direct / indirect / agentic-flow / jailbreak / benign-but-
injection-shaped) is summarized in the
[README §What "OOD" means here](./README.md).

<a id="2-approach-overview"></a>
### §2 Approach overview {#approach-overview}

The detector ladder + reference-scorer slate are now in
[WRITEUP_PAPER §3 Methods](./WRITEUP_PAPER.md) and
[WRITEUP/model-rungs.md](./WRITEUP/model-rungs.md). The
multi-detector philosophy (lexical baseline → frozen probe → LoRA →
full fine-tune + reference scorers) is in
[WRITEUP_NARRATIVE Act 2 — Setup](./WRITEUP_NARRATIVE.md).

### §Results {#results}

The headline characterization (cross-family generalization failure +
mechanism) is now in [WRITEUP_PAPER §4 Results](./WRITEUP_PAPER.md),
[WRITEUP_NARRATIVE Act 3 — Revelation](./WRITEUP_NARRATIVE.md), and
the tables-only [RESULTS.md](./RESULTS.md) appendix with 5 canonical
figures.

<a id="lessons"></a>
### §Lessons (brief) {#lessons-brief}

Methodology reflections now live in
[WRITEUP_PAPER §5 Discussion](./WRITEUP_PAPER.md) and
[WRITEUP/limitations-and-future-work.md](./WRITEUP/limitations-and-future-work.md).
The "what could be wrong with this" narrative is in
[WRITEUP_NARRATIVE Act 4 — Implications](./WRITEUP_NARRATIVE.md).

<a id="12-appendix"></a>
### §12 Appendix {#appendix}

The appendix-class material (operating-point tables, calibration
detail, per-source breakdowns, raw artifact pointers) now lives in
[RESULTS.md](./RESULTS.md) and the [WRITEUP/](./WRITEUP/) spokes
(8 methodology references). The decision trail is at
[decisions/](./decisions/).

For the original single-document v1.0.0 content verbatim, see the
[`tree/v1.0.0`](https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.0.0/WRITEUP.md)
tag pin per ADR-033 — the historical reviewer URL is preserved
unchanged.
