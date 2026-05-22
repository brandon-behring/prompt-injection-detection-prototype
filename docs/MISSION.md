# Mission

> **Public-site note.** This is one part of the historical project
> Constitution. It explains the original scope discipline; read the README or
> Results page first for the completed-project story.

This file is the Mission portion of the project Constitution. SPEC_GREENFIELD.md links to this file (along with `TECH_STACK.md` and `ROADMAP.md`) as the three-file Constitution. Together they replace what would otherwise be the `## Constitution` section of a single-file spec.

## Vision

Build a methodology-driven prompt-injection classifier. The rigor lives in evaluation, not in the model. A reader of the eventual writeup should come away knowing what the classifier can and cannot do, with quantified uncertainty on every claim.

## Audience

Human collaborator and AI agent (e.g., Claude Code) working together via Spec-Driven Development. The spec frames decisions; the agent asks clarifying questions; the human picks options; decisions become ADRs.

## Problem classes in scope

Brief summary; full detail in `SPEC_GREENFIELD.md` §0 Threat Model:

- Direct prompt injection in user-supplied text.
- Indirect injection via context channels (retrieved documents, tool outputs, file attachments).
- Multi-turn injection, encoded payloads, paraphrase attacks, adversarial perturbations are *named but default-deferred* (see SPEC_GREENFIELD §0).

## Success criteria

- `[LOCKED]` Capability layers characterised via a rung ladder of increasing complexity (the "models of increasing complexity" axis).
- `[LOCKED]` Honest OOD assessment: IID-vs-OOD gap quantified, with CIs, across multiple OOD slices.
- `[LOCKED]` Every headline claim has a confidence interval; effect sizes reported alongside.
- `[LOCKED]` Reproducible from a fresh clone via documented commands.
- `[LOCKED]` **Primary headline metric**: AUPRC with bootstrap CIs (per ADR-006 + ADR-022). The pooled-OOD random AUPRC floor is `412 / 1101 = 0.374` and is reported as the comparison baseline for every detector. Secondary metrics: AUROC (random floor 0.5), recall@FPR pinpoints (1%, 5%), ECE / Brier calibration. No SOTA target is committed; the project characterises the ladder honestly rather than chasing a number.

## Non-goals

- `[LOCKED]` **Deployment is out of scope.** The work is *characterisation*, not a deployable service. Score-behaviour is reported under two threshold policies (§4) as characterisation, not as deployment recommendation.
- `[LOCKED]` No SOTA-chasing. The rigor lives in the evaluation methodology.
- `[LOCKED]` No leader rung crowned. Trade-offs across rungs are characterised; the implementer does not pick a winner.
- `[LOCKED]` **Out-of-scope items** are enumerated at [README "What it does not claim"](../README.md#what-it-does-not-claim) and [WRITEUP/reference-scorer-audit.md §5.6](../WRITEUP/reference-scorer-audit.md). Specifically deferred: multilingual attacks, encoded payloads (base64 / leetspeak / Unicode confusables), paraphrase robustness, adversarial perturbations, full multi-turn system behaviour, deployment threshold recommendations.

## Scope authority

`[LOCKED]` — the spec itself is the scope cap. Anything not specified in SPEC_GREENFIELD or the Constitution files is out of scope. Adding scope post-spec-freeze requires an ADR with an explicit "why this is in scope now" justification.
