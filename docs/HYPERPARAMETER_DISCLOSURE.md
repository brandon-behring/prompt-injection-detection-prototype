# Hyperparameter disclosure

`[TBD: populated at Phase 4 after any tuning runs. If no tuning ran, document the literature / inheritance source per row.]`

Per locked-process rule (`SPEC_GREENFIELD.md` §2): no val-set gridsearch. Hyperparameters are locked before training begins; non-default choices get an ADR with the literature / inheritance source.

## Per-rung knob table

| Rung | Knob | Setting | Source / Rationale | ADR |
|---|---|---|---|---|
| `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` |

## What was explored vs not explored

Reviewers may suspect cherry-picking. This section enumerates what was deliberately NOT searched, and why.

`[TBD: populated at Phase 5]`

- **Searched** — knobs / values actually swept during the project: `[TBD]`
- **Not searched (intentional)** — knobs left at literature defaults; rationale per knob: `[TBD]`
- **Not searched (out of scope)** — knobs deferred to future iterations; pointer to NEXT_STEPS.md: `[TBD]`

## Audit hook

Every claim in `WRITEUP.md` that depends on a hyperparameter choice cross-references this file. The pairing makes the anti-cherry-pick story auditable: a reviewer can match each result row to its disclosed setting.
