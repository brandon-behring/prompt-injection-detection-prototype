# Literature dossier

> **Provenance.** This dossier was produced via [research_toolkit](https://github.com/brandon-behring/research_toolkit), a Claude Code skill set that turns a research topic into an audited dossier via the pipeline: `/research-plan` → `/research-gather` → `/dossier-build` → `/agent-index` → `/dossier-audit` + `/url-freshness-check`. Verification markers and frontmatter follow that toolkit's discipline. **Regenerate** by re-running the toolkit's skills against the topic seed.

## Topics

| Topic | Files | Role | Verification |
|---|---|---|---|
| `attacks_defenses/` | 6 dossier + COMPARISON + _dossier_readme | direct + indirect + optimization attacks; inference- + training-time defenses; threat-model survey | verified |
| `benchmarks/` | 4 dossier + COMPARISON + _dossier_readme | direct-injection / indirect-agentic / hard-negative / CTF-adaptive evaluation benchmarks | verified |
| `datasets/` | 2 dossier | train positives + OOD eval slates | verified |

## Per-file frontmatter

Each dossier `.md` carries YAML frontmatter (8 essential fields):

```yaml
title: <one-line human title>
dossier_id: <topic>/<file-prefix>
verification_status: verified | unverified | refuted
verified_at: <YYYY-MM-DD>
confidence_level: high | medium | low
claim_family: <anchor prefix>
tags: [...]
related_dossiers: [...]
```

## Agent navigation

Agents (Phase 0 `/exploring-options` walking the SPEC_GREENFIELD decision ledger; Phase 5 writeup synthesis) query `MANIFEST.json` for deterministic routing:

```bash
jq '.entries[] | select(.verification_status == "verified" and .confidence_level == "high")' docs/research/MANIFEST.json
jq '.entries[] | select(.claim_family == "A1")' docs/research/MANIFEST.json
jq '.entries[] | select(.tags | contains(["attacks"]))' docs/research/MANIFEST.json
```

## Verification taxonomy

Inline row-level markers within each dossier file:

- `[VERIFIED]` — row passed primary-source check
- `[REFUTED]` — claim failed checks (retained for audit-trail value)
- `[UNVERIFIED]` rows are not copied into this dossier; if present, treat as defect

## Decision-row coverage

Decisions in `SPEC_GREENFIELD.md` decision ledger map to dossier `claim_family` values (see MANIFEST.json `claim_family` field). Approximately **30 of the 50 ledger rows** are methodology decisions covered by this dossier; the remaining 20 (brief alignment, library version pinning, submission deliverables, repo hygiene) rely on web search for authoritative URLs.
