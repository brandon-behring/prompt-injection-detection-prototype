# Threat model — summary

This file is a convenience aggregator. Canonical content lives in `WRITEUP.md` §0 + §5.6; the decision ledger rows in `SPEC_GREENFIELD.md` §0 Threat are the lock points for what's in / out of scope. This file gives a single-page security-flavor entry to those.

## Attack classes named

| Class | In scope? | Spec lock |
|---|---|---|
| Direct injection — adversarial text in user input attempting to override system instructions | **In scope** | ADR-014 (Phase 0-01) |
| Indirect injection — adversarial text arriving via context channels (retrieved docs, tool outputs, file attachments) | **In scope** | ADR-014 (Phase 0-01) |
| Multi-turn injection — adversarial payload split across multiple conversation turns | Deferred | ADR-014; see WRITEUP §5.6 |
| Encoded payloads — base64 / leetspeak / hex / Unicode confusables | Deferred | ADR-014; see WRITEUP §5.6 |
| Paraphrase attacks — semantic equivalents of training-set injections | Deferred | ADR-014; see WRITEUP §5.6 |
| Adversarial perturbations — gradient-guided or search-based evasion against a specific classifier | Deferred (named, not silently dropped) | ADR-014 |

## Scope decisions (all locked at Phase 0-01 via ADR-014)

- **Attack classes in scope**: direct + indirect injection (multi-turn / encoded / paraphrase / adversarial perturbations deferred)
- **Language scope**: English-only
- **Length cap**: 512 tokens, single-turn

## Reference-scorer training-overlap audit (locked discipline)

Any external reference scorer evaluated alongside in-house rungs gets a training-data audit. Verdict per the three-state taxonomy:

- `verified_disjoint` — training data verifiably disjoint from project sources
- `suspected_contamination` — known overlap with one or more project sources
- `vendor_black_box` — training data not disclosed (audit shifts to fold-pattern + scope-mismatch analysis)

Verdicts land in `EVIDENCE.md` §1-2. The taxonomy is encoded in eval-toolkit manifests' `contamination_flags` field (see `docs/MANIFEST_SCHEMA.md`).

## Out of scope (named, not silently)

- Deployment recommendation
- SOTA chasing
- Production-readiness testing
- See WRITEUP §8 for the consolidated deferred list

## Cross-references

- `WRITEUP.md` §0 Motivation, §5.6 Adversarial robustness
- `SPEC_GREENFIELD.md` §0 Threat (Feature Specs section) + decision ledger §0 rows
- `EVIDENCE.md` §1-2 (reference scorer audits)
- `docs/MANIFEST_SCHEMA.md` (`contamination_flags` field)
- `docs/research/attacks_defenses/` (literature dossier on attack taxonomies + defenses)
