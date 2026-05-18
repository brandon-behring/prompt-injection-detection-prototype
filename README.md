# prompt-injection-detection-prototype



A prompt-injection classifier prototype, built spec-first. Every decision is locked via a structured Phase 0 interview; every claim cites evidence; every reference scorer is contamination-audited per a three-state taxonomy. **Library-first**: zero hand-rolled implementations — uses [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) (eval primitives), [runpod-deploy](https://github.com/brandon-behring/runpod-deploy) (cloud), and [research_toolkit](https://github.com/brandon-behring/research_toolkit) (dossier production).

> **Status**: Phase 5 complete; tagged `v1.0.0` (see [`docs/ROADMAP.md`](./docs/ROADMAP.md) for the full phase trail). The work is characterisation, not deployment — each rung's trade-offs are reported; no rung is promoted as a winner.
>
> **Full methodology**: see [`WRITEUP.md`](./WRITEUP.md).

## Getting started — reviewer path

```bash
git clone https://github.com/brandon-behring/prompt-injection-detection-prototype
cd prompt-injection-detection-prototype
make install              # uv sync --extra dev
make test                 # ~220 tests; invariants + smoke
make eval-from-hub RUNG=frozen-probe     # T0 score-match (CPU; ~15 min)
make eval-from-hub RUNG=lora             # T0 score-match (CPU; ~15 min)
```

T0 verifies the published HF Hub checkpoints (`BBehring/prompt-injection-frozen-probe`,
`BBehring/prompt-injection-lora`) score-match against the canonical results
within 1e-4 absolute. See `docs/REPRODUCIBILITY.md` for T1 (full GPU re-eval
via `make headline-cloud`).

For the methodology-and-decision trail (Phase 0 → Phase 5; ~50 locked ADRs):
- `WRITEUP.md` — full methodology narrative.
- `decisions/` — 50 Michael-Nygard-format ADRs (immutable).
- `SUBMISSION_AUDIT.md` — script-regenerated claim register sourced from ADR
  frontmatter; the audit ledger is in CI as a hard gate.
- `docs/ROADMAP.md` — Phase 0-5 sequence + closing dates.

## Problem

This is a case-study submission characterising what successive capability
layers (classical TF-IDF + LR floor → frozen ModernBERT backbone with linear
probe → LoRA adapters → full fine-tune) contribute to prompt-injection
detection across an IID test slate (4-source LODO held-out positives) and
a 5-slice OOD slate (BIPIA, InjecAgent, JBB-Behaviors, XSTest, NotInject).

The brief asks for **models of increasing complexity** to characterise what each capability layer brings, plus **the right amount of OOD coverage**. The models are deliberately simple; the rigor lives in the evaluation framework — claims about each rung, including unflattering ones, are honest. Detection and verification operating modes are reported as two cost-weight characterisations of the same scores, not as deployment recommendations.

## Approach

- **Rung ladder** locked at Phase 0-03 (ADR-015 + ADR-017 + ADR-019 + ADR-050):
  TF-IDF+LR classical floor (`verified_disjoint`) → ModernBERT-base frozen-probe
  → ModernBERT-base LoRA → ModernBERT-base full-FT. Each rung answers *what does this capability layer add over the rung below?* The ladder is the brief's "models of increasing complexity"; it is also the *instrument* for the brief's OOD-coverage ask — we look at which capabilities help OOD vs only help IID. ProtectAI v1 + v2 (`suspected_contamination`) are reference scorers per ADR-018, not in the trained ladder. LLM-judge reference scorers dropped at Phase 4 cost re-estimation per ADR-050; full-FT OOD inference dropped at X11 FUSE crash per ADR-050.
- **OOD slate** locked at Phase 0-04 (ADR-016 + ADR-021): 5 slices (BIPIA, InjecAgent, JBB-Behaviors, XSTest, NotInject) selected from `docs/research/benchmarks/` candidate dossier. See WRITEUP §5.5 for *why each slice was chosen*.
- **Methodology rigor** via [eval-toolkit](https://github.com/brandon-behring/eval-toolkit): bootstrap CIs on every headline metric, paired-bootstrap differences for rung-vs-rung comparisons, minimum detectable effect (MDE), calibration battery (ECE + Brier + reliability), validation-set threshold selection. Effect sizes and CIs throughout — no p-values.
- **Reviewer-reproducible**: `make test-smoke` runs a no-external-services smoke pass on a laptop in ~1 min; canonical numbers reproducible via `make eval-from-hub` (T0; CPU; ~15 min per rung) from `BBehring/prompt-injection-<rung>` HF Hub checkpoints. T1 GPU re-eval via `make headline-cloud`.

## Headline characterisation

**The honest finding is methodologically richer than the "look at this great classifier" version.** Fine-tuning a ModernBERT-base backbone (LoRA or full-FT) on the LODO training pool delivers **no improvement** over the frozen-probe rung on the 5-slice pooled OOD slate, and LoRA actively *underperforms* the frozen probe (-0.071 AUPRC on `pooled_ood`; the paired-bootstrap CI clears zero). On IID (JBB-Behaviors), all rungs cluster around 0.55 AUPRC — capability ladder is mostly indistinguishable. Full results + per-fold variance live in [`WRITEUP.md`](./WRITEUP.md) §5; only the punch-line is below.

| Rung | `pooled_ood` AUPRC (95 % CI) | Contamination tier |
|---|---:|---|
| Frozen-probe (in-house) | 0.364 [0.353, 0.375] | `backbone-partial-disjoint` |
| LoRA (in-house) | 0.293 [0.286, 0.301] | `backbone-partial-disjoint` |
| ProtectAI v2 (reference) | 0.314 [0.283, 0.345] `†` | `suspected_contamination` |
| TF-IDF + LR (classical floor) | 0.291 [0.283, 0.298] | `verified_disjoint` |

Source: `evals/bootstrap/marginal_cells.parquet` (BCa bootstrap, mean across folds × seeds × bootstrap-resamples per ADR-022). Full rung × slice × metric grid in WRITEUP §5; per-fold variance + cross-fold-CI in `evals/audit/cross_fold_ci_audit.parquet`.

`†` Reference scorers (ProtectAI v1 / v2) carry training-overlap caveats with our LODO training pool per the three-state taxonomy in [`EVIDENCE.md`](./EVIDENCE.md) §1-2. Reported as diagnostic reference, not as a clean baseline.

**Headline findings** (deep-read in WRITEUP §5 + §7):

- The IID-vs-OOD gap is large for every trained rung (≈ 0.55 → 0.29-0.36 AUPRC).
  Per ADR-021 + ADR-050 LODO-by-construction, this is *cross-source* OOD,
  not within-source noise.
- **Fine-tuning is a negative result on OOD**: LoRA -0.071 AUPRC vs frozen-probe on `pooled_ood`; full-FT OOD inference dropped per ADR-050 X11 FUSE crash.
- Calibration (ECE equal-mass) is *worse* for LoRA (0.45) than frozen-probe (0.14) — fine-tuning collapses the calibration signal even on the slices where AUPRC is similar.
- At the detection operating point (val FPR ≤ 1 %), val→test transfer is partial: frozen-probe holds FPR ≈ 1.0 % on test but recall collapses to 0.063; LoRA blows past FPR cap to 11.5 % to recover recall to 0.42. See WRITEUP §5.3.

Full reading + the headline characterisation claims in [`WRITEUP.md`](./WRITEUP.md). Forward-looking work in [`NEXT_STEPS.md`](./NEXT_STEPS.md). Negative results (things tried that didn't work) in WRITEUP §9. Deferred items in WRITEUP §8. Audit trail for external-evidence claims in [`EVIDENCE.md`](./EVIDENCE.md).

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
make install         # uv sync --extra dev
make lint            # ruff + mypy strict
make test            # ~220 tests; invariants + smoke
make test-smoke      # no-external-services smoke pass (~1 min)
make audit           # SUBMISSION_AUDIT.md in sync with ADRs (CI hard gate)
make coverage        # pytest --cov (currently 89.82 %)
make cost-rollup     # cost ledger vs ADR-020 caps
make eval-from-hub RUNG=frozen-probe   # T0 reproducibility
make eval-from-hub RUNG=lora           # T0 reproducibility
make headline-cloud  # T1 GPU re-eval (frozen-probe + LoRA + full-FT)
make site            # Quarto static site → _site/
```

See `docs/REPRODUCIBILITY.md` for the T0 + T1 reproducibility tiers + full
Makefile target list.

## License

[MIT](./LICENSE).
