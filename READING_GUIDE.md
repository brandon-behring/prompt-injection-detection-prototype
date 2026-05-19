---
title: "Reading guide — 3 reading paths + repo TOC + interpretation pedagogy"
description: "How to read this site (Quarto + GitHub) at the depth that matches your audit goal. The displaced reading-guide content that used to live on the landing page."
---

# Reading guide

This page is the **how-to-read-this-site** companion to the landing page
([`index.qmd`](index.qmd)). The landing page is intentionally short —
results + plain-language interpretation + 3 obvious drill-down links.
This page expands those drill-downs into 3 named reading paths (matched
to audit depth), the headline-ADR shortlist, the repo TOC, and the
detailed interpretation pedagogy.

This reading-guide architecture is anchored at
[ADR-053](decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md)
(dimensions 2-5 — 3-reading-paths + headline-finding-block +
interpretation pedagogy + pointer convention; the navigation dimension
1 was narrowly superseded by
[ADR-061](decisions/ADR-061-quarto-site-navigation-restructure.md) at v1.1.1).

---

## How to read the headline numbers — 5 interpretation patterns

These are the framing moves a reviewer needs in order to read the
landing-page headline table honestly. They are not "tricks" — they are
the consequences of choosing AUPRC under class imbalance + a
cross-family OOD slate.

**1. Prevalence baseline vs chance.** AUPRC's random-predictor floor
equals the positive-class prevalence — here 0.374 on `pooled_ood` (412
positives / 1101 rows). Falling BELOW the prevalence baseline means
the classifier's ranking is anti-correlated with the label *on this
slice* — worse than guessing. AUROC's chance floor is 0.5 regardless
of prevalence; under class imbalance AUROC over-states performance,
which is why AUPRC is the project's preferred ranking metric (per
[WRITEUP/eval-design.md §5.1](WRITEUP/eval-design.md)). When the
table says frozen-probe at 0.364 is *below baseline*, that's not
pedantry: the best trained rung does not beat random guessing in
expectation on the OOD slice.

**2. Cross-family vs cross-source OOD.** "In-domain test" (held-out
LODO source) is still a direct-injection attack — just an unseen
source held out by source-disjoint LODO. The 5-slice OOD slate is
something else entirely: indirect injection via email-body context
(BIPIA), multi-turn agentic-flow attacks (InjecAgent), jailbreaks
(JBB-Behaviors), and benign-but-injection-shaped texts that probe
false-positive robustness (NotInject, XSTest). The OOD wall is
cross-FAMILY, not cross-source — the trained rungs are failing on
attack types absent from training, not failing because the source
distribution drifted. This is the load-bearing framing of the
submission: see [WRITEUP §1.5 Attack-type taxonomy](WRITEUP.md#attack-type-taxonomy-traintest-composition).

**3. Negative LoRA delta — what it means.** LoRA's -0.071 AUPRC vs
frozen-probe on `pooled_ood` (paired-bootstrap CI clears zero) reads
as: **fine-tuning the classification head onto the LODO training pool
ACTIVELY HURTS cross-family OOD generalisation.** The pretrained
ModernBERT-base backbone (which frozen-probe taps before any
task-specific weight movement) carries what little OOD signal exists;
fine-tuning consumes that budget by specialising on direct-injection
structure. Per
[ADR-052](decisions/ADR-052-full-ft-ood-drop-methodological-reframing-of-adr-050-r2.md),
this is *also* the load-bearing reason full-FT OOD inference was
dropped — full-FT is a larger version of the same fine-tuning
mechanism LoRA already showed to be net-harmful on OOD; the FUSE
crash made the drop operational, but the methodological judgment came
first.

**4. ProtectAI v1 → v2 is non-monotone.** On `pooled_ood` AUPRC, v1
(0.361) slightly edges v2 (0.314). On the per-slice breakdown (see
[WRITEUP §Results](WRITEUP.md#results)) v2 wins on JBB-Behaviors
(+0.037 AUPRC) but loses on XSTest (-0.087 AUPRC). The "newer version
is better" reading fails here; publication version monotonicity is not
guaranteed under a cross-family slate. Operational implication:
detector version selection must be slice-aware, not version-monotone.

**5. val → LODO threshold transfer fails.** Thresholds tuned on the
validation slice produce detection FPRs of ~1-12 % when applied to
LODO test data — the standard "tune on val, ship to prod" recipe
under-quantifies operational FPR. The dual-policy threshold
characterisation in [WRITEUP/threshold-policy.md §7](WRITEUP/threshold-policy.md)
is the project's response: separate detection threshold (FPR ≤ 1 %)
from verification threshold (recall ≥ 99 %) and report both with
reachability flags per (rung, fold, seed).

For the full interpretation guide + diagnostic-AUROC comparisons, see
[WRITEUP/eval-design.md §5](WRITEUP/eval-design.md).

---

## Quick-skim path — A1 (hiring manager / executive, ~15 min)

For readers who want the thesis + headline finding + interpretation,
no code dive.

1. [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) — 1-page thesis + 4
   headline claims + reading-path pointer.
2. [`WRITEUP.md` §1 Motivation + §1.5 Attack-type taxonomy](WRITEUP.md) —
   the eval-fairness thesis + 5 injection types + train/test
   composition table.
3. [`WRITEUP.md` §Results headline](WRITEUP.md#results) — cross-family
   OOD framing + per-rung AUPRC table.
4. [`WRITEUP/limitations-and-future-work.md`](WRITEUP/limitations-and-future-work.md) —
   what's deferred + why.

---

## Audit path — A2 (ML researcher / due diligence, ~60 min)

For readers who want to scrutinise the methodology before trusting the
numbers.

1. Full [`WRITEUP.md`](WRITEUP.md) cover-to-cover.
2. [`WRITEUP/eval-design.md`](WRITEUP/eval-design.md) — OOD slate,
   calibration battery, paired-bootstrap protocol, AUPRC vs AUROC
   framing.
3. [`WRITEUP/methodology-guarantees.md`](WRITEUP/methodology-guarantees.md) —
   banned approaches surfaced as guarantees.
4. [`WRITEUP/reference-scorer-audit.md`](WRITEUP/reference-scorer-audit.md) —
   ProtectAI v1/v2 contamination findings + reference-rung stratification.
5. [`WRITEUP/threshold-policy.md`](WRITEUP/threshold-policy.md) —
   dual-policy detection + verification operating points + reachability
   audit.
6. [`EVIDENCE.md`](EVIDENCE.md) — external-evidence audit trail
   (contamination scan, dedup calibration, leakage scrub).
7. [`decisions/`](decisions/README.md) — full ADR ledger; Architecture
   Decision Records in Michael Nygard format. **61 ADRs at v1.1.1
   close.**

**Headline ADRs to read** (the methodology + narrowing trail; cuts
through the 61-file ledger):

- [ADR-005](decisions/ADR-005-methodology-over-metrics.md) —
  methodology-over-metrics + three-state contamination taxonomy.
- [ADR-015](decisions/ADR-015-rung-slate-and-backbone.md) —
  single-backbone slate (ModernBERT-base) + truncation-confound mitigation.
- [ADR-016](decisions/ADR-016-data-design.md) — source-disjoint LODO +
  dedup + SHA-pinned data.
- [ADR-017](decisions/ADR-017-classical-floor.md) — TF-IDF + LR
  classical floor as `verified_disjoint` anchor.
- [ADR-018](decisions/ADR-018-reference-scorers.md) — original 4-rung
  reference slate (LLM judges + ProtectAI v1/v2).
- [ADR-022](decisions/ADR-022-statistical-apparatus.md) —
  paired-bootstrap + cv_clt_ci + block-bootstrap sensitivity.
- [ADR-046](decisions/ADR-046-phase-4-walkthrough.md) — Phase 4
  analysis-pipeline implementation bundle.
- [ADR-050](decisions/ADR-050-rung-slate-narrowing-llm-judges-and-full-ft-ood-dropped.md) —
  rung-slate narrowing (LLM-judge cost drop + full-FT OOD drop).
- [ADR-051](decisions/ADR-051-v1.0.x-carryforward-of-t0-and-invariant-scaffolds.md) —
  v1.0.x carryforward governance (T0 + invariant scaffolds).
- [ADR-052](decisions/ADR-052-full-ft-ood-drop-methodological-reframing-of-adr-050-r2.md) —
  methodological reframing of full-FT OOD drop.
- [ADR-053](decisions/ADR-053-reading-guide-governance-and-newcomer-paths.md) —
  reading-guide governance (this artifact).
- [ADR-058](decisions/ADR-058-eval-from-hub-non-dry-run-body-narrow-supersession-of-adr-051-block-a.md) —
  v1.0.9 eval-from-hub T0 wiring (narrow supersession of ADR-051 Block A).
- [ADR-059](decisions/ADR-059-runpod-deploy-pypi-install-narrow-supersession-of-adr-036.md) —
  v1.1.0 runpod-deploy PyPI switch.
- [ADR-060](decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md) —
  v1.1.0 DeBERTa-v3-base methodology lock (Path B; execution v1.1.1).
- [ADR-061](decisions/ADR-061-quarto-site-navigation-restructure.md) —
  v1.1.1 navigation restructure (this page is the result).

---

## Deep-dive path — A3, reproduce the numbers (~30 min CPU; $0)

Three reproduction tiers per
[ADR-034](decisions/ADR-034-reproducibility-tier-full-ladder.md). Pick
the tier matching your audit depth + budget.

| Tier | Command | Cost | Time | What it verifies |
|---|---|---|---|---|
| **T0** — eval-from-hub | `make eval-from-hub RUNG=frozen-probe` (and `RUNG=lora`) | $0 (HF Hub bandwidth) | ~15-30 min per rung | Headline scores reproduce on the published HF Hub checkpoint within 1e-4 absolute (wired at v1.0.9 per ADR-058) |
| **T1** — smoke | `make test-smoke` | $0 | ~1-2 min | Code health; fixture pipeline runs end-to-end; no network required |
| **T3** — headline-cloud | `make headline-cloud` | ~$28+ per [ADR-020](decisions/ADR-020-runpod-orchestration-and-cost-discipline.md) | ~hours | Full retraining from scratch reproduces headline numbers |

Detailed instructions in
[`WRITEUP/reproducibility.md`](WRITEUP/reproducibility.md).

---

## Repo map

| Path | Contents |
|---|---|
| [`src/`](src/) | Library code — `data/`, `training/`, `scoring/`, `eval/`, `utils/` per [ADR-026](decisions/ADR-026-module-layout-concern-grouped-subpackages.md) |
| [`scripts/`](scripts/) | CLI entrypoint glue — argparse + IO orchestrating `src/` calls |
| [`configs/`](configs/) | YAML rung + RunPod + profile configs |
| [`decisions/`](decisions/README.md) | ADRs (immutable decision records) — 61 ADRs at v1.1.1 |
| [`evals/`](evals/) | Per-row predictions + metrics + bootstrap + audit JSON (populated Phase 1-5) |
| [`tests/`](tests/) | Invariant tests + unit/smoke/integration suites |
| [`WRITEUP.md`](WRITEUP.md) | Methodology hub document (cover narrative) |
| [`WRITEUP/`](WRITEUP/) | Topic-focused methodology spokes (8 files; detailed deep-dives) |
| [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) | 1-page decision-maker layer over WRITEUP |
| [`RESULTS.md`](RESULTS.md) | Full 5-rung × 5-slice grid + figures + raw-data pointers |

---

## Submission anchors

- **Source pin** (canonical; never drifts): [`github.com/.../tree/v1.0.0`](https://github.com/brandon-behring/prompt-injection-detection-prototype/tree/v1.0.0)
- **Live rendered site** (reflects latest patch): [`brandon-behring.github.io/prompt-injection-detection-prototype/`](https://brandon-behring.github.io/prompt-injection-detection-prototype/)
- **Release page** (CHANGELOG + offline-readable site bundle): [`github.com/.../releases/tag/v1.0.0`](https://github.com/brandon-behring/prompt-injection-detection-prototype/releases/tag/v1.0.0)
- **HF Hub model cards** (published checkpoints; T0 reproducibility): [`BBehring/prompt-injection-frozen-probe`](https://huggingface.co/BBehring/prompt-injection-frozen-probe) + [`BBehring/prompt-injection-lora`](https://huggingface.co/BBehring/prompt-injection-lora)

Per [ADR-033](decisions/ADR-033-github-release-strategy-rehearsal-plus-submission.md) —
`v0.9.0-rc1`/`rc2`/`rc3` are rehearsal tags; `v1.0.0` is the canonical
submission tag; `v1.0.x` SemVer patch tags reserved for post-submission
typo / link / clarity / reviewer-feedback fixes (reviewer URL stays
pinned at `tree/v1.0.0`; live Quarto site reflects latest patch).
`v1.1.x` MINOR tags reserved for non-methodology infrastructure +
governance updates per ADR-033.

---

## Status

Phase 5 closed at v1.0.0 (2026-05-18). Submission audit loop closed at
v1.0.2 (ADR-051 carryforward governance for T0 + invariant scaffolds).
Full-FT OOD drop reframed methodologically at v1.0.3 (ADR-052).
Reading-guide architecture anchored at v1.0.4 (ADR-053). v1.0.9 closed
ADR-051 Block A (T0 score-match wiring per ADR-058). v1.1.0 closed
the runpod-deploy modernization track (ADR-059) + locked DeBERTa-v3-base
medium ablation methodology (ADR-060; execution deferred to v1.1.1).
**v1.1.1 restructured the navigation per ADR-061 (you are reading the
v1.1.1 artifact)**. Live site reflects the latest v1.1.x tag; reviewer
URL pin stays at `tree/v1.0.0` per ADR-033. **61 ADRs** across Phase
0-00 → v1.1.1 close.
