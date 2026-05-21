# Reference-scorer audit

*Part of the [WRITEUP methodology](../WRITEUP.md) — see the hub for the cover narrative + reading guide.*

> **How to read this spoke**: For a fast skim, focus on the bolded **Result** subsections + the final §Summary if present. For a full audit, read the methodology paragraphs + the ADR references in headers.

:::{.callout-note}
## Summary

- **Three-state contamination taxonomy** (per ADR-005): `verified_disjoint` / `suspected_contamination` / `vendor_black_box`. The reference slate carries 3 rungs total after Phase 4 narrowing (LLM-judges dropped per ADR-050 cost re-estimation).
- **TF-IDF + LR floor**: `verified_disjoint` — trained in-project on the LODO pool; no external training-data provenance.
- **ProtectAI v1 verdict**: `suspected_contamination` retained. HF model card lists `deepset/prompt-injections` + Lakera sources in training mix — overlap with this project's LODO training pool. Full disjointness cannot be verified; results reported with caveat.
- **ProtectAI v2 verdict**: BETTER than v1 on `jbb_behaviors` (+0.06 AUROC) and WORSE on `xstest` (-0.15 AUROC; CIs do not overlap — a clear regression). v2's broader-scope training did NOT monotonically improve across the OOD slate.
- **Dropped rungs**: LLM-judge reference scorers (gpt-4o + claude-sonnet-4-6) dropped at Phase 4 per ADR-050 (16× envelope overrun); Lakera Guard dropped at Phase 0 per ADR-018 (ToS verification overhead).
:::

This spoke covers the three-state contamination taxonomy (ADR-005)
as applied to the reference-scorer slate (ProtectAI v1 + v2 +
TF-IDF+LR classical floor) per ADR-018 + ADR-050 narrowing, plus
the adversarial-robustness scope statement (§5.6). Full per-scorer
findings are in [`../EVIDENCE.md`](../EVIDENCE.md) §1-2; headline
ladder context is in [`model-rungs.md`](./model-rungs.md).

## Contamination taxonomy (per ADR-005)

Reference-scorer contamination uses the three-state taxonomy:

- `verified_disjoint` — training data verifiably disjoint from
  project sources.
- `suspected_contamination` — known overlap with one or more
  project sources.
- `vendor_black_box` — training data not disclosed (audit shifts to
  fold-pattern + scope-mismatch analysis).

Per ADR-050, the `vendor_black_box` tier carries **0 rungs** in this
submission (LLM-judge reference scorers dropped at Phase 4 cost
re-estimation). The reference slate is three rungs:

| Rung | Tier | Reason |
|---|---|---|
| `tfidf-lr` | `verified_disjoint` | Trained in-project on LODO training pool (ADR-017); no external training-data provenance. |
| `ProtectAI v1` | `suspected_contamination` | HF model card lists `deepset/prompt-injections` + Lakera sources in training mix — overlap with this project's LODO training pool. |
| `ProtectAI v2` | `suspected_contamination` | Same overlap as v1 + uncharacterised v2-specific expansion data. |

## Per-scorer findings (summary)

### ProtectAI v1 — `suspected_contamination`

Per-slice AUROC on the OOD slate:

| Slice | AUROC | 95 % CI |
|---|---|---|
| jbb_behaviors | 0.533 | [0.464, 0.602] |
| xstest | 0.544 | [0.497, 0.589] |
| pooled_ood | 0.440 | [0.409, 0.469] |

The CI on jbb_behaviors crosses 0.50 (chance); the pooled CI does
NOT. v1 distinguishes positives from negatives at marginally-above-
chance rates on the OOD slate. Training-data disclosure is at
category level only via the HF model card; cross-source overlap
check via `data/contamination_templates.parquet` is partial; full
disjointness cannot be verified. **Result (verdict)**:
`suspected_contamination` retained; results reported with caveat.

### ProtectAI v2 — `suspected_contamination`

Per-slice AUROC on the OOD slate:

| Slice | AUROC | 95 % CI |
|---|---|---|
| jbb_behaviors | 0.594 | [0.512, 0.671] |
| xstest | 0.391 | [0.341, 0.442] |
| pooled_ood | 0.402 | [0.369, 0.437] |

**Result**: v2 is BETTER than v1 on jbb_behaviors (+0.06 AUROC; CIs
overlap but separated by ~1 SD) and WORSE on xstest (-0.15 AUROC; CIs
do not overlap — a clear regression). v2's broader-scope training did
NOT monotonically improve across the OOD slate. The contamination
caveat from v1 carries over: training scope is disclosed at category
level only.

### Dropped reference scorers (per ADR-050)

The LLM-judge rungs (gpt-4o-2024-08-06 + claude-sonnet-4-6) were
dropped post-lock when Phase 4 cost re-estimation revealed a 16×
envelope overrun against the original ADR-018 estimate ($14 →
$240) — driven by per-row LLM-judge inference being charged at the
full input-prompt token count (long injection examples hit 1k-3k
tokens routinely) plus the rater-audit disagreement-sampled cohort
scaling with total prediction volume rather than a fixed ~50-pair
cohort.

The `vendor_black_box` contamination tier therefore has 0 rungs in
this submission; the contamination-stratification gradient compresses
from 4 tiers to 3.

## §5.6 Adversarial robustness — threat model named (not exhaustively probed)

Adversarial robustness is **largely deferred** in this submission per
[`limitations-and-future-work.md`](./limitations-and-future-work.md)
§8.1 (named but not exhaustively probed beyond the in-pool LODO +
OOD attack diversity).

The adversarial threat model for a prompt-injection classifier
includes:

- **Paraphrase attacks** — semantic equivalents that don't share
  surface n-grams with training injections.
- **Encoded payloads** — base64, leetspeak, hex, Unicode confusables,
  ROT13.
- **Multi-turn injection** — payload split across multiple
  conversation turns.
- **Indirect injection via context channels** — payload arriving
  via retrieved documents, tool outputs, or user-attached files.

**What was tested**: the in-pool LODO + OOD slate already spans
(a) direct vs indirect injection (BIPIA covers indirect), (b)
jailbreak vs ignore-instructions (xstest + jbb_behaviors cover
jailbreak-as-question), (c) agentic injection (injecagent), and
(d) benign-but-injection-shaped (notinject).

**What was deliberately not tested**: curated adversarial probes
(paraphrase generation; encoded payloads at the row level; multi-
turn injection splits). *Why deferred*: would expand the methodology
contract from "characterisation against a fixed slate" to "ongoing
adversarial probing" — see
[`limitations-and-future-work.md`](./limitations-and-future-work.md)
§8.1.

This sub-section exists so that an evaluator from a security-
focused company can see the threat model is named even where the
work was not done. It is not a claim of coverage.

## Cross-references

- **Full per-scorer evidence** → [`../EVIDENCE.md`](../EVIDENCE.md) §1-2
- **Rung ladder including the reference scorers** → [`model-rungs.md`](./model-rungs.md)
- **Threat-model summary aggregator** → [`../docs/THREAT_MODEL.md`](../docs/THREAT_MODEL.md)
- **Scope-deferred future work** → [`limitations-and-future-work.md`](./limitations-and-future-work.md)

**Linked ADRs**: ADR-005 (contamination taxonomy), ADR-008 (threat
model), ADR-014 (threat-model bundle locks), ADR-018 (reference
slate — partially superseded by ADR-050), ADR-021 (slice
aggregation), ADR-050 (rung-slate narrowing — LLM judges dropped).
