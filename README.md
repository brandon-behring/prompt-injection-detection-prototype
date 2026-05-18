# prompt-injection-detection-prototype

**Methodology + capability characterisation of a 5-rung prompt-injection classifier ladder, evaluated under an honest OOD slate.** A spec-first case-study submission: every decision is locked via a structured Phase 0 interview producing 50 ADRs; every claim cites evidence + bootstrap CIs; every reference scorer is contamination-audited per a three-state taxonomy. **Library-first**: uses [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) (eval primitives), [runpod-deploy](https://github.com/brandon-behring/runpod-deploy) (cloud orchestration), and [research_toolkit](https://github.com/brandon-behring/research_toolkit) (literature-dossier production); no hand-rolled equivalents.

> **Status**: Phase 5 complete; tagged `v1.0.0` (patches via `v1.0.x` per ADR-033). The work is **characterisation**, not deployment — each rung's trade-offs are reported; no rung is promoted as a winner.
>
> **Live site**: [brandon-behring.github.io/prompt-injection-detection-prototype/](https://brandon-behring.github.io/prompt-injection-detection-prototype/) — rendered Quarto methodology site with the 7-spoke WRITEUP + 50 ADRs + EVIDENCE + reference docs. Updated on every push to `main`.
>
> **HF Hub model cards**: [BBehring/prompt-injection-frozen-probe](https://huggingface.co/BBehring/prompt-injection-frozen-probe) + [BBehring/prompt-injection-lora](https://huggingface.co/BBehring/prompt-injection-lora) — canonical fold0/seed42 checkpoints per ADR-032. Reviewer-reproduce-the-numbers (T0) via `make eval-from-hub RUNG=<rung>`.
>
> **One-paragraph goal.** Characterise what successive capability layers add to prompt-injection detection (classical → frozen-probe → LoRA → full-FT), across an Out-of-Distribution (OOD) test slate of 5 attack types (direct / indirect / agentic-flow / jailbreak-as-question / false-positive-probe). The honest finding: fine-tuning on direct-injection training data *consumes* the OOD generalization budget the pretrained backbone provides. **Full methodology** in [`WRITEUP.md`](./WRITEUP.md) (with 7 spoke files under [`WRITEUP/`](./WRITEUP/)) or on the [live Quarto site](https://brandon-behring.github.io/prompt-injection-detection-prototype/).

## What this submission delivers

- **5-rung trained ladder** (per ADR-015 + ADR-017 + ADR-050): TF-IDF + LogReg classical floor → ModernBERT-base frozen-probe (head-only training) → ModernBERT-base LoRA (~1 % trainable params) → ModernBERT-base full-FT. Plus 2 reference scorers (ProtectAI v1, ProtectAI v2) at native config. LLM-judge reference rungs were dropped at Phase 4 on cost re-estimation per ADR-050; full-FT OOD inference dropped at Phase 5 X11 on a FUSE EIO crash. The `vendor_black_box` contamination tier ships with 0 rungs in this submission.
- **5-slice OOD test slate** (per ADR-016 + ADR-021): BIPIA (indirect injection via email body, all-positive), InjecAgent (multi-turn agentic-flow injection, all-positive), JBB-Behaviors (jailbreak-style harmful elicitation, both classes), XSTest (jailbreak-as-question, both classes), NotInject (benign-but-injection-shaped false-positive probe, all-negative). The slate probes injection types deliberately *outside* the training-pool style mix.
- **4-source LODO training pool** (per ADR-016): `deepset/prompt-injections` (170 rows post-dedup), `Lakera/gandalf_ignore_instructions` (525), `Lakera/mosscap_prompt_injection` (2362), `hackaprompt/hackaprompt-dataset` (1650). **Direct-injection-heavy by composition** — see WRITEUP §1.5 for the train/test mismatch table.
- **Methodology rigor**: BCa bootstrap CIs on every headline metric; paired-bootstrap rung-vs-rung differences (Efron-Tibshirani protocol); MDE alongside every CI containing zero; calibration battery (ECE equal-mass + Kumar-2019-debiased + Brier + reliability curves; temperature / Platt / isotonic / Beta fits on val only); cross-fold CIs via Bayle-2020 `cv_clt_ci` + block-bootstrap-on-folds sensitivity per A-008; dual-policy threshold characterisation (detection FPR ≤ 1 % + verification recall ≥ 99 %); SHA-pinned data sources + leakage scan + per-fold contamination scan. Effect sizes + CIs throughout — no p-values.
- **Reviewer-reproducible** (per ADR-034): **T0** = `make eval-from-hub RUNG=<rung>` runs a CPU eval against the published HF Hub checkpoint and score-matches against `evals/results.json` within 1e-4 absolute (~15 min per rung, $0). **T1** = `make test-smoke` (laptop, no GPU, no network, ~1 min). Optional **T3** = `make headline-cloud` (RunPod A100 80GB; ~$28; full LODO matrix re-train + re-eval).
- **Governance trail**: 50 ADRs in [`decisions/`](./decisions/) (Michael Nygard format; immutable; ADR-050 is the rung-slate narrowing). `SUBMISSION_AUDIT.md` regenerates from ADR frontmatter via `scripts/regenerate_audit.py` (CI hard gate). External-evidence audit in [`EVIDENCE.md`](./EVIDENCE.md). Hyperparameter disclosure in [`docs/HYPERPARAMETER_DISCLOSURE.md`](./docs/HYPERPARAMETER_DISCLOSURE.md). 16-file literature dossier in [`docs/research/`](./docs/research/) (produced via the `research_toolkit` pipeline).

## What this submission is NOT

- **Not a deployment recommendation.** No rung is promoted as the deployment choice. Trade-offs are reported; readers with a specific deployment context map our characterisation onto their cost constraints.
- **Not a SOTA chase.** Models are deliberately simple; the rigor lives in the evaluation framework. The headline finding *includes unflattering results* by design.
- **Not a benchmark.** Slate is fixed by source-disjoint LODO + a 5-slice OOD test slate, not a sliding leaderboard.
- **Scope is single-turn English text classification only.** Multi-turn agentic flows, encoded payloads (base64 / leetspeak / hex / Unicode confusables / ROT13), paraphrase attacks, adversarial perturbations, and cross-language attacks are **out of scope** per ADR-014 + WRITEUP §1 Scope. InjecAgent appears in the test slate to *quantify* the agentic-flow gap, not because we expect the single-turn classifier to handle it.

## Reading paths

Pick the path matching your audit depth. All paths link into the [live Quarto site](https://brandon-behring.github.io/prompt-injection-detection-prototype/); each is also navigable via the repo files if you've cloned.

1. **Quick-skim (~15 min)** — for the hiring-manager / executive read.
   - [Live site index](https://brandon-behring.github.io/prompt-injection-detection-prototype/) → §Motivation + §Reading guide.
   - [WRITEUP §1.5 Attack-type taxonomy](https://brandon-behring.github.io/prompt-injection-detection-prototype/WRITEUP.html#attack-type-taxonomy-traintest-composition) — 5 injection types + the 9-column train/test composition table.
   - [WRITEUP §Results headline](https://brandon-behring.github.io/prompt-injection-detection-prototype/WRITEUP.html#results) + §Takeaways — the OOD wall finding in 3 numbered points.

2. **Audit (~60 min)** — for the ML-researcher / due-diligence read.
   - Full [WRITEUP.md](https://brandon-behring.github.io/prompt-injection-detection-prototype/WRITEUP.html) cover-to-cover.
   - All 8 [WRITEUP/ spokes](https://brandon-behring.github.io/prompt-injection-detection-prototype/WRITEUP/data-decisions.html) (data, model-rungs, eval-design, threshold-policy, reference-scorer-audit, methodology-guarantees, limitations, reproducibility).
   - [EVIDENCE.md](https://brandon-behring.github.io/prompt-injection-detection-prototype/EVIDENCE.html) — external-evidence audit trail.
   - Headline [ADRs](https://brandon-behring.github.io/prompt-injection-detection-prototype/decisions/README.html): ADR-005 (methodology over metrics), ADR-015 (single-backbone slate), ADR-016 (data design), ADR-017 (rung-slate), ADR-018 (reference scorers; superseded by ADR-050), ADR-022 (statistical apparatus), ADR-050 (rung-slate narrowing).

3. **Reproduce the numbers (~30 min CPU; $0)** — for the engineer who wants the numbers to land on their machine.
   - `make install && make eval-from-hub RUNG=frozen-probe` (CPU; ~15 min) pulls the published checkpoint from [BBehring/prompt-injection-frozen-probe](https://huggingface.co/BBehring/prompt-injection-frozen-probe) and score-matches against `evals/results.json` within 1e-4 absolute per ADR-034.
   - `make eval-from-hub RUNG=lora` — same for [BBehring/prompt-injection-lora](https://huggingface.co/BBehring/prompt-injection-lora).
   - `make test-smoke` (no GPU, no network, ~1 min) verifies code-health on fixtures.
   - Full T1 GPU re-eval via `make headline-cloud` (~$28; A100 80GB; ~7h).

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

**Fine-tuning consumes the OOD generalization budget the pretrained backbone provides.** Read against the WRITEUP §1.5 train/test composition table: the 4 LODO training sources are direct-injection-heavy; the 5-slice OOD slate probes injection types that are *not* in training (BIPIA = the only indirect-injection slate; InjecAgent = the only agentic-flow slate; NotInject = pure false-positive probe). Fine-tuning a ModernBERT-base backbone (LoRA) on this training pool delivers **no improvement** over the frozen-probe rung on `pooled_ood`, and LoRA actively *underperforms* the frozen probe (-0.071 AUPRC on `pooled_ood`; the paired-bootstrap CI clears zero). On IID (JBB-Behaviors), all rungs cluster around 0.55 AUPRC — the capability ladder is mostly indistinguishable. **The pretrained backbone — not the LODO training pool — carries what little OOD generalization budget exists.** Full results + per-fold variance live in [`WRITEUP.md`](./WRITEUP.md) §Results; only the punch-line is below.

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
