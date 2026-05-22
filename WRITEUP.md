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
