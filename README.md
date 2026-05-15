# prompt-injection-detection-prototype



A prompt-injection classifier prototype, built spec-first. Every decision is locked via a structured Phase 0 interview; every claim cites evidence; every reference scorer is contamination-audited per a three-state taxonomy. **Library-first**: zero hand-rolled implementations — uses [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) (eval primitives), [runpod-deploy](https://github.com/brandon-behring/runpod-deploy) (cloud), and [research_toolkit](https://github.com/brandon-behring/research_toolkit) (dossier production).

> **Status**: `[TBD: phase status — see docs/ROADMAP.md]`. The work is characterization, not deployment — each rung's trade-offs are reported; no rung is promoted as a winner.
>
> **Full methodology**: see [`WRITEUP.md`](./WRITEUP.md).

## Getting started

After cloning + `make install`, the project is ready for Phase 0 (spec lock-in interview). In Claude Code (or another agent supporting the same skill set):

```text
# 1. Read the binding spec end-to-end
#    SPEC_GREENFIELD.md + docs/MISSION.md + docs/TECH_STACK.md + docs/ROADMAP.md
# 2. Run the Phase 0 interview (covers ~50 [OPEN] decisions in ~9 sub-sessions)
/exploring-options                          # walks SPEC_GREENFIELD decision ledger
# 3. After each sub-session, checkpoint locally
/save-transcript phase-0-NN__<topic>        # writes transcripts/<date>__<slug>.md (gitignored)
# 4. Draft ADRs from each locked decision
#    Copy decisions/ADR_TEMPLATE.md → decisions/ADR-NNN-<slug>.md, fill in
# 5. Once Phase 0 closes (all [OPEN] resolved + SPEC_SHEET filled + assumptions logged), Phase 1 may begin
```

See `docs/ROADMAP.md` for the full Phase 0-5 sequence.

## Problem

`[TBD: 1-paragraph statement populated at Phase 5]`

The brief asks for **models of increasing complexity** to characterize what each capability layer brings, plus **the right amount of OOD coverage**. The models are deliberately simple; the rigor lives in the evaluation framework — claims about each rung, including unflattering ones, are honest. Detection and verification operating modes are reported as two cost-weight characterizations of the same scores, not as deployment recommendations.

## Approach

- **Rung ladder** `[OPEN: rung ladder; resolved at Phase 0]`. Each rung answers *what does this capability layer add over the rung below?* The ladder is the brief's "models of increasing complexity"; it is also the *instrument* for the brief's OOD-coverage ask — we look at which capabilities help OOD vs only help IID.
- **OOD slate** `[OPEN: OOD slate composition; resolved at Phase 0]`. See WRITEUP §5.5 for *why each slice was chosen*. Additional slices may be added via `[OPEN]` additions.
- **Methodology rigor** via [eval-toolkit](https://github.com/brandon-behring/eval-toolkit): bootstrap CIs on every headline metric, paired-bootstrap differences for rung-vs-rung comparisons, minimum detectable effect (MDE), calibration battery (ECE + Brier + reliability), validation-set threshold selection. Effect sizes and CIs throughout — no p-values.
- **Reviewer-reproducible**: `make diagnostics-smoke` `[OPEN: smoke target; resolved at Phase 0]` runs a no-external-services smoke pass on a laptop in ~10 min; canonical numbers reproducible from the GitHub release + HF Hub checkpoints.

## Headline characterization

`[TBD: populated at Phase 5 from per-rung × per-slice numbers; operating point per the threshold-policy decision locked at Phase 0]`. No rung promoted as a winner; trade-offs are explained in WRITEUP §7. Dual-cost-weight characterization (detection vs verification operating points) lives in WRITEUP §5.3.

| Rung | fold_test PR-AUC ± CI | OOD slice 1 | OOD slice 2 | OOD slice 3 | ECE |
|---|---:|---:|---:|---:|---:|
| `[OPEN]` Rung 1 | `[TBD: value]` | `[TBD: value]` | `[TBD: value]` | `[TBD: value]` | `[TBD: value]` |
| `[OPEN]` Rung 2 | `[TBD: value]` | `[TBD: value]` | `[TBD: value]` | `[TBD: value]` | `[TBD: value]` |
| `[OPEN]` Rung 3 | `[TBD: value]` | `[TBD: value]` | `[TBD: value]` | `[TBD: value]` | `[TBD: value]` |
| `[OPEN]` Reference scorer 1 | `[TBD: value]` `†` | `[TBD: value]` `†` | `[TBD: value]` `†` | `[TBD: value]` `†` | `[TBD: value]` |
| `[OPEN]` Reference scorer 2 | `[TBD: value]` `†` | `[TBD: value]` `†` | `[TBD: value]` `†` | `[TBD: value]` `†` | `[TBD: value]` |

`†` Reference scorers may carry training-overlap caveats with public eval slices. The audit trail in EVIDENCE.md §1–2 reports a per-scorer verdict per the three-state taxonomy (`verified_disjoint` / `suspected_contamination` / `vendor_black_box`). Reported as diagnostic reference, not as a clean baseline.

`[FIGURE: PR curves all rungs, IID test slice]` → `docs/plots/figure-pr-curves-iid.png`
`[FIGURE: PR curves all rungs, OOD slate]` → `docs/plots/figure-pr-curves-ood.png`

Headline findings:

- `[TBD: populated at Phase 5]` — the IID-vs-OOD gap and what it tells us
- `[TBD: populated at Phase 5]` — which ladder rungs help OOD vs only help IID
- `[TBD: populated at Phase 5]` — calibration findings per rung
- `[TBD: populated at Phase 5]` — the score-behavior characterization at detection-policy vs verification-policy operating points

Full reading + the headline characterization claims in [`WRITEUP.md`](./WRITEUP.md). Forward-looking work in [`NEXT_STEPS.md`](./NEXT_STEPS.md). Negative results (things tried that didn't work) in WRITEUP §9. Deferred items in WRITEUP §8. Audit trail for external-evidence claims in [`EVIDENCE.md`](./EVIDENCE.md).

## Repo roadmap

| Path | Role | Read when |
|---|---|---|
| `README.md` | Project entry; skim doc | First |
| `SUBMISSION_TEMPLATE.md` | Cover-letter template (filled `SUBMISSION.md` is gitignored, emailed separately) | First (reviewer) |
| `docs/MISSION.md` | Mission + scope + non-goals | Understanding "what is this" |
| `docs/TECH_STACK.md` | Libraries + GPU + secrets discipline | Understanding "what's it built with" |
| `docs/ROADMAP.md` | Phase 0-5 sequence + replanning checkpoints | Understanding "how it gets built" |
| `SPEC_GREENFIELD.md` | Binding pre-Phase-0 spec: Feature Specs §0-§7 + 50-row decision ledger | Deep methodology dive; Phase 0 driver |
| `SPEC_SHEET.md` | Post-Phase-0 fill-in form (locks resolved during Phase 0) | After Phase 0 |
| `SPEC_STRATEGY.md` | Classification: why lightweight pack vs heavier alternatives | Reviewer wanting meta-justification of the spec structure |
| `WRITEUP.md` | Full methodology + characterization narrative | Deep dive after spec |
| `EVIDENCE.md` | External-evidence audit trail | When verifying a specific claim |
| `NEXT_STEPS.md` | Deferred work + future directions | After WRITEUP §8 |
| `SUBMISSION_AUDIT.md` | Claim-status register (script-generated from ADRs) | Verifying submission readiness |
| `docs/THREAT_MODEL.md` | Convenience aggregator — threat surface summary | Security-focused review |
| `docs/REPRODUCIBILITY.md` | Convenience aggregator — make targets + manifest schema ref | Re-running the work |
| `docs/HYPERPARAMETER_DISCLOSURE.md` | Anti-cherry-pick discipline | Verifying tuning honesty |
| `docs/MANIFEST_SCHEMA.md` | eval-output manifest schema (eval-toolkit upstream contract) | Inspecting evals/ |
| `docs/GLOSSARY.md` | Project terminology (living document) | Encountering unfamiliar jargon |
| `STYLE.md` | Coding-style discipline | Contributors / Phase 1 |
| `code_quality.md` | Lint / type / test / import / commit discipline | Contributors / Phase 1 |
| `assumptions.md` | Severity-tagged registry of unverified inputs | Verifying methodology rigor |
| `CHANGELOG.md` | Tag history (Keep-a-Changelog 1.1.0); v0.0.0 = seed | Version history |
| `CLAUDE.md`, `AGENTS.md` | Agent governance (Claude-specific + vendor-neutral) | Any agent session |
| `decisions/` | ADRs (Michael Nygard format; immutable) + library_imports + upstream_issues + ADR_TEMPLATE | Decision provenance |
| `transcripts/` | Phase 0 sub-session captures (gitignored; emailed separately) | Decision rationale trail |
| `tests/`, `scripts/` | Code (invariant stubs + audit-regenerate scripts) | Phase 1+ |
| `docs/research/` | Literature dossier (16 verified files + MANIFEST.json; produced via research_toolkit) | Phase 0 reference; Phase 5 citations |
| `.github/`, `.pre-commit-config.yaml`, `Makefile`, `pyproject.toml` | Repo plumbing | CI / setup |
| `LICENSE` | MIT | Legal |

## Run

```bash
make install        # uv sync --extra dev
make lint           # ruff + mypy strict
make test           # tests/test_invariants.py (7 skip-marked stubs at seed)
make audit          # SUBMISSION_AUDIT.md in sync with ADRs (CI hard gate)
```

Phase 1+ adds: `make diagnostics-smoke`, `make canonical-eval`, etc. — see `docs/REPRODUCIBILITY.md`.

## License

[MIT](./LICENSE).
