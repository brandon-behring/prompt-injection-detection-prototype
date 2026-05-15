# prompt-injection-detection-submission

`[TBD: CI badge]`

A take-home prompt-injection classifier for **Ciphero AI**. Methodology-first; not state-of-the-art; deliberately scoped. **The work is characterization, not deployment** — each rung's trade-offs are reported; no rung is promoted.

> **Full methodology**: see [`WRITEUP.md`](./WRITEUP.md).
> **Status**: `[TBD: phase status — see SPEC_GREENFIELD.md §Roadmap]`.

## Problem

`[TBD: 1-paragraph statement]`

The brief asked for **models of increasing complexity** to characterize what each capability layer brings, plus **the right amount of OOD coverage**. The models are deliberately simple; the rigor lives in the evaluation framework — claims about each rung, including unflattering ones, are honest. Detection and verification operating modes are reported as two cost-weight characterizations of the same scores, not as deployment recommendations.

## Approach

- **Rung ladder** `[OPEN: rung ladder; resolved at Phase 0]`. Each rung answers *what does this capability layer add over the rung below?* The ladder is the brief's "models of increasing complexity"; it is also the *instrument* for the brief's OOD-coverage ask — we look at which capabilities help OOD vs only help IID.
- **OOD slate** `[OPEN: OOD slate composition; resolved at Phase 0]`. See WRITEUP §5.5 for *why each slice was chosen*. additional slices may be added via `[OPEN]` additions.
- **Methodology rigor** via [eval-toolkit](https://github.com/brandon-behring/eval-toolkit): bootstrap CIs on every headline metric, paired-bootstrap differences for rung-vs-rung comparisons, minimum detectable effect (MDE), calibration battery (ECE + Brier + reliability), validation-set threshold selection. Effect sizes and CIs throughout — no p-values.
- **Reviewer-reproducible**: `make diagnostics-smoke` `[OPEN]` runs a no-external-services smoke pass on a laptop in ~10 min; canonical numbers reproducible from the GitHub release + HF Hub checkpoints.

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

`[FIGURE 1: PR curves all rungs, IID test slice]` → `docs/plots/figure1-pr-curves-iid.png`
`[FIGURE 2: PR curves all rungs, OOD slate]` → `docs/plots/figure2-pr-curves-ood.png`

Headline findings:

- `[TBD: value]` — the IID-vs-OOD gap and what it tells us
- `[TBD: value]` — which ladder rungs help OOD vs only help IID
- `[TBD: value]` — calibration findings per rung
- `[TBD: value]` — the score-behavior characterization at detection-policy vs verification-policy operating points

Full reading + the four characterization claims in [`WRITEUP.md`](./WRITEUP.md). Forward-looking work in [`NEXT_STEPS.md`](./NEXT_STEPS.md). Negative results (things tried that didn't work) in WRITEUP §9. Deferred items in WRITEUP §8. Audit trail for external-evidence claims in [`EVIDENCE.md`](./EVIDENCE.md).

## Read more

- [**`SUBMISSION_TEMPLATE.md`**](./SUBMISSION_TEMPLATE.md) — cover-letter template (filled version `SUBMISSION.md` is gitignored and emailed separately at submission time).
- [**`WRITEUP.md`**](./WRITEUP.md) — full methodology + capability characterization (12 sections, ~5000 words).
- [**`SPEC_SHEET.md`**](./SPEC_SHEET.md) — project specification: phase-by-phase process gates, data design, model recipe, eval design.
- [**`NEXT_STEPS.md`**](./NEXT_STEPS.md) — tactical next steps on  + aspirational future iterations + open questions.
- [**`EVIDENCE.md`**](./EVIDENCE.md) — audit trail: what was verified, what couldn't be, what was left unresolved.
- [`decisions/`](./decisions/) — ADRs (Michael Nygard format; single version-neutral sequence).
- [`evals/`](./evals/) `[TBD: value]` — evaluation matrix + analysis JSONs + REPORT.md.
- [`notebooks/`](./notebooks/) `[OPEN]` — interpretive notebooks (e.g., `evidence.ipynb`).
- [`transcripts/`](./transcripts/) `[TBD: value]` — selected Claude-Code transcripts illustrating decision points.
- [`spec.md`](./spec.md) — the prior-version specification (inherits / supersedes per ADR audit).
- **[eval-toolkit](https://github.com/brandon-behring/eval-toolkit)** — methodology-aware eval harness. Methodology curriculum at [`docs/methodology/`](https://github.com/brandon-behring/eval-toolkit/tree/main/docs/methodology).
- **[runpod-deploy](https://github.com/brandon-behring/runpod-deploy)** — cloud orchestration for training/eval runs.

## Run

```bash
make install                  # uv sync --extra dev
make lint                     # ruff check + ruff format --check + mypy strict
make test                     # invariants + math correctness + smoke
make diagnostics-smoke        # [OPEN] L1+L2A: install+lint+test+smoke (~10 min, no external services)
make preflight             # [TBD] CPU preflight — gates invariants before any GPU spend
make h100                  # [TBD] canonical H100 path via runpod-deploy
```

For cloud setup, see `[TBD: (candidate) docs/cloud-canonical-runbook.md]`. For the full reproducibility framework, see `[TBD: (candidate) docs/DIAGNOSTICS.md]`.

## What this version deliberately doesn't do

A one-line pointer; details in WRITEUP §8 (deferred) and §9 (architectures tried and abandoned). `[TBD: (candidate) short list — adversarial red-teaming, agentic-flow coverage, deployment, multi-language, ...]`

## License

[MIT](./LICENSE).
