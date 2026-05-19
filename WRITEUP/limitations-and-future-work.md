# Limitations and future work

*Part of the [WRITEUP methodology](../WRITEUP.md) — see the hub for the cover narrative + reading guide.*

This spoke consolidates §8 scope deferrals, §8.2 methodology
caveats, §9 negative results (tried + abandoned), and §11 lessons.
The distinction matters: §8 = scope decisions we can defend; §9 =
experimental work that did not pan out; §11 = process-level
lessons. For headline characterisation that exposes these
limitations see [`../WRITEUP.md`](../WRITEUP.md) §Results.

## 8.1 Scope deferrals

These are not failures — they are scope decisions we can defend.

- **Deployment** — out of roadmap. The work is characterisation;
  no deployment recommendation; no deployment-readiness testing.
- **Adversarial red-teaming** — threat model named in
  [`reference-scorer-audit.md`](./reference-scorer-audit.md) §5.6,
  not exhaustively probed. *Why deferred*: in-scope adversarial
  inputs (the 4 LODO training sources + 5 OOD slates) already span
  a wide diversity of attack styles; expanding to a curated red-team
  set would change the methodology contract from "characterisation
  against a fixed slate" to "ongoing adversarial probing" — out of
  case-study scope.
- **Agentic-flow coverage** — multi-step / tool-use injection.
  *Why deferred*: the classifier scope is single-turn text-as-input;
  agentic-flow detection requires intermediate-state interception
  (tool-call args, function-output contamination) which is a
  deployment-stack question, not a classifier question.
- **Conformal prediction** — distribution-free uncertainty
  quantification beyond bootstrap. *Why deferred*: conformal
  calibration on LODO held-out attack sources would require a
  calibration set drawn from the same distribution as test (which
  doesn't exist by LODO design). Per-fold bootstrap CIs from
  ADR-022 are the in-scope honest uncertainty quantification.
- **Cross-language coverage** — English-only by source-slate
  construction (4 LODO + 5 OOD sources are all English). *Why
  deferred*: per ADR-016 source-slate lock; cross-language attack
  generalization is a separate dataset-design question requiring
  multilingual injection corpora.
- **Cross-source same-style ablation** — would disambiguate
  "training contamination" from "attack-style difficulty" for
  reference scorers. *Why deferred*: per-style sample size on the
  5-slice OOD slate is too small for a powered ablation (BIPIA
  n=50, InjecAgent n=62, JBB n=200, XSTest n=450, NotInject n=339).
  Treated as an explicit limitation; see
  [`../EVIDENCE.md`](../EVIDENCE.md) §3.
- **LLM-judge reference scorers** (gpt-4o-2024-08-06 +
  claude-sonnet-4-6) — dropped post-lock per ADR-050. *Why dropped*:
  Phase 4 cost re-estimation against the actual OOD slate sizing
  revealed an envelope ~16× the original ADR-018 estimate ($14 →
  $240) driven by per-row LLM-judge inference being charged at the
  full input-prompt token count (long injection examples hit 1k-3k
  tokens routinely). The `vendor_black_box` contamination tier
  therefore has 0 rungs in this submission; the contamination-
  stratification gradient compresses from 4 tiers to 3. ProtectAI
  v1 + v2 remain as `suspected_contamination` reference scorers.
- **full-FT OOD inference** — dropped at Phase 5 X11 per ADR-052
  (narrow supersession of ADR-050 Revision 2's FUSE-crash-only
  framing). *Methodological reasoning was load-bearing*: LoRA's
  -0.071 AUPRC vs frozen-probe on `pooled_ood` (paired-bootstrap
  CI clears zero per ADR-022) already showed fine-tuning on the
  LODO direct-injection training pool was actively HURTING OOD
  generalization. Full-FT is a larger version of the same
  fine-tuning mechanism (~149M parameters trainable vs LoRA's
  ~1.5M); the expected marginal benefit of full-FT-OOD over
  LoRA-OOD on the same pool was low, and the re-fire cost + risk
  (~6-12 hours wall-clock on Low-stock A100 80GB + repeat-FUSE-risk
  + ~$5-12 GPU spend) did not justify the investment. The FUSE EIO
  crash on /workspace MooseFS storage was the operational trigger
  that exposed this decision; ADR-052 makes the methodological
  reasoning explicit. *Retrospective self-awareness*: with the
  data-set sizes used (≈4.7K positives + ≈17K benigns post-dedup,
  no augmentation) the rung-ladder + CI inspection now suggests
  the full-FT LODO investment itself was likely not load-bearing
  for the characterisation conclusions; a v1.1.x iteration with a
  larger or augmented training pool would justify revisiting.
  full-FT remains in the LODO comparison (3-rung ladder narrative
  survives via the surviving Phase 2 24 LODO predictions); OOD
  comparison ships 2 trained rungs (frozen-probe + LoRA) + 1
  classical floor (tfidf-lr) + 2 reference scorers (ProtectAI v1
  + v2) = 5 rungs.

## 8.2 Methodology caveats

- **Single-class OOD slices break threshold-free metrics** —
  BIPIA + InjecAgent are all-positive attack-only datasets per
  their source design; NotInject is all-negative benign-only.
  AUROC and AUPRC are mathematically undefined on these slices and
  the metrics pipeline filters them out at source (per Item 4 of
  the v1.0.0 closure sweep). The per-cell parquet
  `evals/metrics/per_cell.parquet` covers `jbb_behaviors` +
  `xstest` + `pooled_ood`. Per-slice recall-at-threshold is
  reported on the single-class slices instead.
- **LODO test sets are intentionally all-positive** per ADR-016
  design (held-out attack source = cross-source generalization
  test). Recall@threshold is the well-defined metric on LODO;
  AUROC/AUPRC are undefined and not reported there.
- **Val-set inference for trained rungs uses max_length 2048**
  (vs the Phase 2 training max_length 8192). Covers >99 % of val
  token-length distribution per char-to-token ~4:1 ratio; p99
  token length ~1100 in val. Fidelity loss negligible for the
  dual-policy threshold-fitting purpose; the long-tail truncation
  is a tracked-but-tolerated divergence from the training-time
  configuration.

## 9.1 Hyperparameter / training dead-ends

No factorial hyperparameter sweep was conducted at the chosen
compute budget per ADR-019 (single recipe per rung locked at
Phase 0; no val-set gridsearch). Three operational findings during
canonical fires that ARE worth documenting:

- **`max_length=8192` at training + `max_length=2048` at val/OOD
  inference** is a deliberate fidelity trade-off. The trained
  checkpoints saw the full ModernBERT 8192 context at train time;
  downstream val inference on local 8 GB VRAM (RTX 2070 SUPER)
  couldn't sustain `batch=8` at `max_length=8192` without OOM on
  long examples (val text p99 token length ~1100; max ~2800).
  Lowered val inference to `max_length=2048` + `batch=4`; covers
  >99 % of val rows intact. The truncation tail is a tracked-but-
  tolerated divergence (see §8.2).
- **Two pre-training-fire bugs were caught and fix-forwarded**
  during Phase 2 (X1-X11 chain documented in
  `decisions/upstream_issues.md`): SSH-ready timeout 240s → 600s
  for cold image pulls; phantom image tag passing
  `runpod-deploy validate` without registry HEAD-check;
  `UV_LINK_MODE=copy` + `UV_CACHE_DIR=/root/uv_cache` +
  `UV_PROJECT_ENVIRONMENT=/root/.venv` all needed to escape FUSE
  `F_SETLKW` deadlocks on RunPod's MooseFS-backed `/workspace`.
- **Full-FT `cleanup_intermediate_checkpoints` policy** was locked
  at `true` per ADR-019 storage discipline (43 GB of throwaway
  weights avoided per fire) but had to be RELAXED to `false` for
  Phase 5 X11 re-fire so OOD inference could load the trained
  checkpoints. The re-fire then crashed at `shutil.copytree` on the
  598 MB `optimizer.pt` due to FUSE EIO. The lesson is operational:
  storage-discipline locks that delete weights need a
  `keep_final_only` flag to support post-train OOD inference
  workflows. Filed upstream as a runpod-deploy issue (proposed
  `lifecycle.keep_final_checkpoint` config knob).

## 9.2 Architectures evaluated and dropped

- **DeBERTa-v3-base** dropped during Phase 0 lock per ADR-015
  (formerly ADR-007) for cross-backbone context-window asymmetry
  — DeBERTa-v3 caps at 512 tokens vs ModernBERT-base 8192.
  Including both backbones would have produced an irreducible
  truncation × architecture confound on BIPIA-style indirect
  injection. Single-backbone slate (ModernBERT-base × 3
  conditions) preserves the rung-ladder narrative without
  architecture confounding.
  **Update (v1.1.0)**: DeBERTa-v3-base returns as a deliberate
  ablation-appendix comparator per [ADR-060](../decisions/ADR-060-deberta-v3-base-long-context-ablation-methodology.md).
  Methodology locked at v1.1.0 (2 truncation strategies side-by-side
  — chunk-and-average + head-truncation — to make the truncation
  handling methodologically addressable rather than load-bearing for
  the rung-vs-rung comparison); execution deferred to v1.1.1 pending
  the loader-refactor + windowed-inference module per Path B of the
  /exploring-options 2026-05-19 scope-mismatch resolution. The
  ablation lands in [`RESULTS.md` §1B](../RESULTS.md#1b-ablation-appendix-deberta-v3-base-long-context-comparator-v110-methodology-lock-v111-execution),
  NOT integrated as a 6th rung in the §1 headline ladder.
- **Lakera Guard reference scorer** dropped at Phase 0-03 per
  ADR-018 (terms-of-service verification overhead unacceptable
  for prototype scope). The reference slate gained ProtectAI v1
  in its place — internal v1→v2 lift becomes a parallel to the
  trained-rung-lift story.
- **LLM-judge reference rungs (gpt-4o + claude-sonnet-4-6)**
  dropped at Phase 4 cost re-estimation per ADR-050 (16× envelope
  overrun). See §8.1.
- **full-FT OOD inference** dropped at Phase 5 X11 re-fire per
  ADR-052 (narrow supersession of ADR-050 R2). Load-bearing
  reason: methodological — LoRA's paired-bootstrap evidence
  already showed fine-tuning on the LODO pool was hurting OOD;
  full-FT's expected marginal benefit was low. FUSE EIO crash was
  the operational trigger. full-FT remains in LODO comparison;
  OOD ships 2 trained rungs. See §8.1.

## 9.3 Data-pipeline experiments that didn't matter

- **Dedup threshold sweep** — ADR-042 locked the LLM-pre-label
  bootstrap calibration at a fixed cosine threshold per
  `evals/dedup_calibration.json`. A sensitivity sweep on threshold
  ± 0.05 was considered but deferred — the calibration's
  `human_verified_pct` operator follow-up (raise from 0 to 100
  before v1.0.0 tag per ADR-042) is the higher-leverage gate.
- **Augmentation strategies** — no synthetic augmentation was tried
  (no paraphrase generation, no back-translation, no character-
  noise injection). The case-study scope is *characterisation of
  an honest classifier slate against a fixed data slate*, not
  data-augmentation research. Tracked as out-of-scope per Phase 0
  lock.

## 9.4 What the negatives imply for v6

The OOD generalization wall is the dominant signal. Three concrete
suggestions for a successor iteration:

1. **OOD-aware training data** — the current pool is dominated by
   4 LODO sources (prompt-injection-style attacks) that share a
   stylistic core. Adding cross-style attacks (BIPIA-style indirect
   injection in training; jailbreaks-as-questions in training)
   would test whether the OOD wall is *training-distribution
   scope* or *fundamental classifier inadequacy*.
2. **Pretrained backbone scaling** — frozen ModernBERT-base
   embeddings provide more OOD generalization than LoRA fine-tuning
   does. A v6 ablation along backbone scale (ModernBERT-base 150M
   → ModernBERT-large 400M; or a different backbone family) would
   test whether the OOD ceiling is backbone-capacity-limited.
3. **OOD-aware threshold selection** — dual-policy thresholds fit
   on val do not transfer to LODO test (see
   [`threshold-policy.md`](./threshold-policy.md)). Per-source
   temperature scaling or conformal calibration with a held-out
   OOD calibration set (currently impossible by LODO design)
   would close the val→LODO gap.

## §11 Lessons & reflections

- **OOD generalization is genuinely hard, and the honest finding
  is methodologically richer than the "look at this great
  classifier" version**. The trained transformer rungs hover near
  chance on the OOD slate; LoRA fine-tuning is a *negative* result
  vs the frozen probe on `pooled_ood` (-0.132 AUROC; CI clears
  zero). A submission framed as "we built a great classifier"
  would have HIDDEN this finding; a submission framed as "we
  characterised the honest performance ladder" SURFACES it. The
  Phase 0-locked methodology (LODO + bootstrap CIs + paired-
  bootstrap rung-vs-rung + dual-policy threshold characterisation)
  forced the honest story to land.
- **The SDD process bought reproducibility + audit trail at the
  cost of a 9-decision-per-sub-session interview flow at Phase 0**.
  ~50 decisions across ~9 topic-focused sub-sessions per
  `SPEC_GREENFIELD.md`. Each open-decision lock produced an ADR;
  `SUBMISSION_AUDIT.md` regenerates from ADRs as a single source
  of truth. The cost was the time investment up front; the benefit
  was zero methodology drift later — every Phase 1-7 commit traced
  cleanly back to an ADR claim. ADR-050 (rung-slate narrowing) is
  itself the supersession-on-supersession proof point: when
  reality forced a methodology drift, the SDD discipline ate it
  cleanly via a narrow ADR-018 / ADR-021 partial supersession
  rather than a silent code change.
- **Library-first invariant retrofit happened mid-project**.
  Phase 1-3 had accumulated 4 sites where eval-toolkit primitives
  were duplicated locally; ADR-047 retrofitted them in a single
  landing rather than fix-forward per-site. The lesson: at every
  module-design step audit `eval-toolkit + runpod-deploy +
  research_toolkit` for an existing primitive BEFORE writing
  project glue.
- **The /exploring-options multi-round pattern unblocked complex
  decisions** that ExitPlanMode-on-first-attempt would have
  committed prematurely. Four rounds for the Phase 4 canonical-
  recovery plan (each round surfaced a risk the prior rounds
  didn't see). Two rounds for the GitHub-push-blocked recovery.
- **FUSE-on-RunPod is a non-deterministic bug class**. The X1-X11
  fix-forward chain documents four distinct FUSE failure modes;
  each cost a real fraction of the $15.74 cumulative spend
  (~50 % of cost is FUSE-recovery overhead). Filed upstream
  issues + PRs at brandon-behring/runpod-deploy so future
  consumers don't re-discover them. The library-first invariant
  cuts both ways: when an upstream gap surfaces, file an upstream
  issue BEFORE local workaround.
- **Per-step commits + a 2-checkpoint push cadence survived
  context auto-compaction**. The session spanned multiple Claude
  context windows + ran for many hours; commit per work-unit +
  intermediate pushes meant no work was lost when context
  boundaries hit. The discipline overhead was small; the
  resilience benefit was large.

**What surprised**: the OOD wall. Going in I expected the rung
ladder to be a positive story (each rung adds something over the
floor); the LoRA-fine-tuning regression on `pooled_ood` was the
methodologically richest finding. Going forward (v6): the §9.4
prescriptions — OOD-aware training data, backbone scaling, OOD-
aware threshold selection — would test whether the wall is
data-distribution or capacity-bounded.

## Cross-references

- **Headline characterisation that exposes these limitations** → [`../WRITEUP.md`](../WRITEUP.md) §Results
- **Adversarial robustness scope (§5.6)** → [`reference-scorer-audit.md`](./reference-scorer-audit.md)
- **NEXT_STEPS forward-looking work** → [`../NEXT_STEPS.md`](../NEXT_STEPS.md)
- **Upstream issues ledger** → [`../decisions/upstream_issues.md`](../decisions/upstream_issues.md)

**Linked ADRs**: ADR-001 (brief alignment), ADR-013 (deliverable
scope), ADR-015 (single-backbone lock — supersedes ADR-007),
ADR-016 (data design), ADR-018 (reference slate), ADR-019 (training
recipe), ADR-022 (statistical apparatus), ADR-042 (dedup
calibration), ADR-047 (library-first carryforward refactor),
ADR-050 (rung-slate narrowing).
