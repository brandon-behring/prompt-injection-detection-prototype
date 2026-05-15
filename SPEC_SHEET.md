# Specification: prompt-injection classifier — v5

**Status**: `[TBD]` (`DRAFT` → `PROPOSED` → `LOCKED`)
**Type**: Spec-Driven Development (custom hybrid: spec + ADRs + assumption registry + tests-as-invariants)
**Prior version**: v4 (see prior `spec.md` for inherited decisions)

> **Companion docs**:
> - [`code_quality.md`](../code_quality.md) — implementation discipline
> - [`assumptions.md`](../assumptions.md) — registry of unverified assumptions
> - [`decisions/`](../decisions/) — ADR audit table
> - [`EVIDENCE.md`](./EVIDENCE.md) — external-evidence audit trail

---

## Context

`[TBD: what prior versions established and what v5 specifically inherits or changes]`

- **Inherited from v4**: `[LOCKED — rung ladder, k=3 LODO, dedup recipe (MiniLM @ 0.80), LoRA recipe (r=8, hf_trainer, 2ep, bf16), 4-slice OOD slate, claim-gates discipline, effect-sizes stance, transcript-capture mandate (NEW for v5; v4 did not), prediction-persistence (NEW for v5; v4 gap)]`
- **Changed in v5**: `[TBD — list new ADRs that supersede prior decisions]`
- **Open from v4**: `[TBD — items v4 left as open questions that v5 may or may not resolve, e.g., LLM-as-rater rubric audit, multi-seed stability, ModernBERT/Llama-as-classifier, conformal prediction]`

This is an **exploration spec** for an SDD-disciplined iteration — not a production system, not a paper, not a publishable benchmark. The work is *methodology + capability characterization braided*: characterize what each capability layer adds, using an evaluation methodology rigorous enough to detect real differences and quantify uncertainty.

---

## 1. Goal & non-goals

**Goal**: `[TBD: one-paragraph statement of what v5 commits to deliver]`

**Non-goals**:
- Not optimizing for SOTA PR-AUC.
- Not building a deployable service. Deployment is not on the roadmap.
- Not creating a publishable benchmark.
- `[OPEN]` Not picking a leader rung — each rung's trade-offs are characterized, no rung is promoted as the deployment recommendation.
- `[TBD: additional non-goals specific to v5]`

**Scope authority**: the spec itself is the scope cap. Anything not specified here is out of v5 scope. Adding scope post-spec-freeze requires an ADR with explicit "Why this is in scope now" justification.

---

## 2. Phases & process gates

v5's work is structured into six phases. Each phase has a gate checklist of work-completed and tests-passing — **not metric thresholds**. The intent is to make movement between phases auditable, not to bind v5's narrative to specific numerical outcomes.

### Phase 0: Spec lock-in interview `[LOCKED: NEW for v5; v4 did not]`

- [ ] Agent reads this spec end-to-end
- [ ] Every `[OPEN]` / `[TBD]` decision is surfaced as a clarifying question
- [ ] Human picks options for each surfaced decision
- [ ] Decisions are recorded as ADRs (Michael Nygard format)
- [ ] Phase 1 cannot start until every decision is resolved or explicitly deferred

Gate: `decisions/` directory contains an ADR for every Phase-0-resolved decision; `transcripts/` directory contains the interview transcript.

### Phase 1: Data

- [ ] Sources defined and licenses verified
- [ ] Audit complete; counts and class balance documented in `evals/v5/data_audit.json`
- [ ] Semantic dedup applied per `[ADR-003 v4 inherited]` (calibrated MiniLM @ 0.80); calibration evidence persisted at `evals/v5/dedup_calibration.json`
- [ ] Cross-source benign dedup applied before split (v4 gap-closure)
- [ ] Leakage scan run; results in `evals/v5/leakage_report.json`
- [ ] Train/val/test splits locked and persisted

Gate: every checkbox ticked; `tests/test_data.py` and `tests/test_leakage.py` green.

### Phase 2: Training

- [ ] Each rung's config persisted at `config/v5/<rung>.yaml`
- [ ] All rungs trained successfully on `[TBD: (candidate) H100 via runpod-deploy]`
- [ ] Training artifacts captured per `runpod-deploy` manifest (git SHA, seed, GPU info, env)
- [ ] **Per-row predictions persisted** at `evals/v5/predictions/<rung>__<fold>__<seed>.parquet` `[LOCKED: NEW for v5; v4 gap]`
- [ ] Per-rung checkpoint persisted to `[TBD: (candidate) HF Hub at BBehring/pid-runs-v5]`

Gate: every checkbox ticked; training manifests schema-validated.

### Phase 3: Evaluation

- [ ] All rung × slice metrics computed via `eval-toolkit`
- [ ] OOD slate evaluated end-to-end (4 v4-inherited slices + any v5 additions)
- [ ] Calibration battery run (ECE + Brier + reliability) for every rung
- [ ] Thresholds selected on validation only (detection-policy and verification-policy on in-house rungs; recall@FPR pinpoints on all rungs)
- [ ] `evals/v5/results.json` schema-validated against `eval-toolkit`'s `results.v1.json` schema

Gate: every checkbox ticked; `evals/v5/results.json` parses cleanly.

### Phase 4: Analysis

- [ ] Bootstrap CIs computed for every headline metric
- [ ] Paired-bootstrap differences computed for every rung-vs-rung comparison of interest
- [ ] MDE estimated for every reported CI
- [ ] Per-source / per-style breakdowns computed (LLM-as-rater rubric audit `[OPEN]`)
- [ ] Figures 1–7 (or v5's named slate) rendered to `docs/v5-plots/`

Gate: every checkbox ticked; analysis JSON outputs match schemas.

### Phase 5: Writeup

- [ ] All WRITEUP sections drafted
- [ ] All v5 ADRs written and indexed in `decisions/README.md`
- [ ] Transcripts linked from WRITEUP appendix
- [ ] EVIDENCE.md populated for every external-evidence claim
- [ ] PDF bundled: README + WRITEUP + NEXT_STEPS + SPEC_SHEET + EVIDENCE
- [ ] All `[TBD]` / `[OPEN]` markers in submission templates resolved or justified

Gate: every checkbox ticked; PDF reads cleanly start-to-finish.

---

## 3. Data design

### 3.1 Train pool composition

`[OPEN]` 4 positive sources + 1 benign-pool source + 4 OOD slices:

| Source | Approx N | Role | License |
|---|---|---|---|
| `deepset/prompt-injections` | 347 (en-filter, post-dedup) | Train pos #1 (mixed labels per split-don't-drop) | Apache-2.0 |
| `Lakera/gandalf_ignore_instructions` | 1,000 | Train pos #2 (override style) | MIT |
| `jackhhao/jailbreak-classification` | 1,306 | Train pos #3 (jailbreak / role-play) | Apache-2.0 |
| `OpenAssistant/oasst1` | 4,000 (subsample) | Train neg | Apache-2.0 |
| `leolee99/NotInject` train-half | 170 | Train neg (hard-benigns) | MIT |
| `ai-ml-ops-eng/tensortrust-datasets` | 2,000 (subsample) | **OOD only** (cross-style probe) | Unknown on mirror |
| `microsoft/llmail-inject-challenge` Phase 2 | 500 (subsample) | **OOD only** (cross-channel indirect) | MIT |
| `leolee99/NotInject` eval-half | 169 | **OOD only** (over-defense / FPR axis) | MIT |
| `indirect_probe.yaml` (local) | 50 (45 inj + 5 benign) | **OOD only** (illustrative; underpowered) | MIT |

`[TBD: additional v5 sources]`

### 3.2 Splits

`[OPEN]` Source-disjoint **k=3 LODO** (leave-one-dataset-out). The 3 positive sources rotate through k=3 folds; benigns are shared across all folds. Per Fomin 2025. See `[ADR-004 v4 inherited]`. v5 may add `[TBD: (candidate) multi-seed stability supplement, nested LODO]`.

### 3.3 Dedup, leakage prevention, cross-source label conflicts

- **Semantic dedup**: `[LOCKED inherited from v4 ADR-003]` calibrated MiniLM @ 0.80, label-aware (cross-source minimal pairs preserved per SDD ADR-019)
- **Cross-source minimal pairs**: `[LOCKED]` preserve-and-flag
- **Cross-source benign dedup**: `[OPEN]` applied to benign pool *before* 80/20 split (v4 found this gap during full-profile audit)
- **Leakage invariants**: `tests/test_leakage.py` asserts no exact-hash and no high-cosine train-test overlap.
- **Reference-scorer training-overlap audit**: `[LOCKED]` see WRITEUP §3.3 + EVIDENCE.md §1–2 for v4's worked example.

### 3.4 OOD slate

`[OPEN]` — 4 slices:

| Slice | Source | Role | Why |
|---|---|---|---|
| `ood_indirect_probe` | local indirect_probe.yaml | Small mixed indirect probe (n=50) | Illustrative; underpowered |
| `ood_tensortrust` | TensorTrust filtered | Cross-style extraction (n=986, all pos) | Novel attack patterns |
| `ood_llmail_phase2` | LLMail Phase 2 subsample | Cross-channel indirect (n=390, all pos) | Caveated as out-of-primary-scope |
| `ood_notinject_eval` | NotInject 50% eval-half | Over-defense / FPR axis (n=169, all neg) | InjecGuard 2024-2025 |

v5 may add `[TBD: (candidate) cross-source same-style ablation; PINT benchmark; multilingual probe; ...]`.

**Linked ADRs**: ADR-001 (threat model), ADR-002 (dataset slate), ADR-003 (dedup), ADR-004 (splits + balance).

---

## 4. Model recipe (locked, no gridsearch)

Each rung is locked before training begins. No val-set hyperparameter gridsearch.

### 4.1 LR-TFIDF — *linear floor*
`[OPEN]` `TfidfVectorizer(ngram_range=(1,2), lowercase=True) + LogisticRegression(class_weight='balanced', C=1.0)`. Deterministic.

### 4.2 Frozen DeBERTa probe — *what the backbone encodes*
`[OPEN]` `microsoft/deberta-v3-base` mean-pooled embeddings + LR head. Deterministic at seed=42.

### 4.3 DeBERTa-LoRA — *fine-tuning ceiling at v4's budget*
`[OPEN]` `DeBERTa-v3-base + LoRA r=8, α=16, dropout=0.1; target modules query_proj+value_proj; modules_to_save=[classifier, pooler]; lr=5e-5; epochs=2; class-weighted loss (hf_trainer style); bf16; bs=16; max_len=512; warmup 6%; primary seed=42 + supplement n=3 seeds`. V4.1-extended factorial confirmed: epoch effect dominates; precision near-zero; class-weight implementation immaterial. v5 may add `[TBD: (candidate) r=4 sweep, modernBERT backbone, full-FT comparison]`.

### 4.4 ProtectAI v2 — *narrow-scope reference scorer*
`[OPEN]` `protectai/deberta-v3-base-prompt-injection-v2`; inference-only. Scope: "does not detect jailbreak attacks." Training-data overlap with `jackhhao` confirmed; see EVIDENCE.md §1.

### 4.5 Llama Prompt Guard 2 — *broad-scope reference scorer*
`[OPEN]` `meta-llama/Llama-Prompt-Guard-2-86M`; inference-only. Scope: prompt injections + jailbreaks. Training-data disclosure at category level only; overlap with V4/V5 sources not provably verifiable. See EVIDENCE.md §2.

### 4.6 `[TBD: additional v5 rungs if any]`

`[OPEN]` v5 candidates: ModernBERT-base + LoRA; Llama-as-classifier; calibration-of-LoRA via temperature on validation.

**Linked ADRs**: ADR-005, ADR-006, ADR-014, ADR-015.

---

## 5. Eval design

### 5.1 Primary descriptive metrics

PR-AUC, ROC-AUC, recall@FPR={0.1%, 1%, 5%} `[LOCKED inherited from v4 for 1% and 5%; 0.1% NEW for v5 — requires per-row predictions persisted]`, ECE (equal-mass + Kumar-2019 debiased), Brier. All reported with bootstrap CIs.

### 5.2 Statistical tests

**Stance**: report effect sizes and CIs only. No p-values. The work characterises differences and their uncertainty rather than claiming significance.

Anchored to [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) primitives:

- `bootstrap_ci` — per-metric finite-sample uncertainty. See [methodology/bootstrap.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/bootstrap.md).
- `paired_bootstrap_diff` — paired comparisons across rungs on the same test set. See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md).
- `mde_from_ci` — minimum detectable effect.
- Calibration battery (`reliability_curve`, `fit_temperature`, `fit_isotonic`, ECE variants, Brier). See [methodology/calibration.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/calibration.md).
- `cv_clt_ci` — CLT-based CI for cross-fold variance.

### 5.3 Operating points — detection vs verification

`[LOCKED inherited from v4 scope discipline]` Dual-policy framing on **in-house rungs only** (LR-TFIDF + Frozen + LoRA). Reference scorers (ProtectAI v2, Llama PG2) get recall@FPR pinpoints with explicit contamination caveats; no dual-policy framing (would imply deployment-ready operating points that don't survive the contamination caveat).

Detection (FPR ≤ 1%) + Verification (FNR ≤ 1%) selected on **validation only** via eval-toolkit's `ThresholdSelector` protocol. See [methodology/thresholds.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/thresholds.md).

### 5.4 Per-source and per-style breakdowns

Required for any OOD claim — aggregate metrics hide heterogeneity. Reported alongside the headline IID/OOD numbers. Per-style heuristic tagger (v4 carryover, regex-based) is conservative; v5 may `[TBD: (candidate) invest in LLM-as-rater rubric audit]`.

### 5.5 Adversarial robustness

`[TBD: (candidate) mostly deferred for v5]` — the threat model (paraphrase, encoded payloads, multi-turn injection, base64/leetspeak obfuscation) is named; what was not tested is named explicitly in WRITEUP §5.6 and §8.

**Linked ADRs**: ADR-021, ADR-022, ADR-023.

---

## 6. Code architecture

The work spans three repos:

- **`prompt-injection-sdd`** (this repo) — modelling: data loading, training, classification API, v5-specific scoring code.
- **[`eval-toolkit`](https://github.com/brandon-behring/eval-toolkit)** — evaluation harness: metrics, bootstrap, calibration, threshold selection, leakage detection, slice-aware orchestration, reproducibility manifests, versioned JSON schemas.
- **[`runpod-deploy`](https://github.com/brandon-behring/runpod-deploy)** — cloud orchestration for training/eval runs on rented GPUs. **v5 additions**: prediction-persistence pull-pattern + checkpoint upload-to-HF-Hub pattern (closes v4 gap).

The split is intentional: methodology curriculum and primitives live in `eval-toolkit` so they survive across model versions; cloud orchestration lives in `runpod-deploy` so it's reusable across projects.

---

## 7. Verification & acceptance criteria

v5 is considered complete when **all five Phase 5 gates pass**:

- All WRITEUP sections drafted with `[TBD]` markers resolved.
- All v5 ADRs written.
- Transcripts linked.
- EVIDENCE.md populated for every external-evidence claim.
- PDF bundled.
- Markers explained.

Plus the standard quality gates that apply to every phase:

- `make test` passes (incl. invariants for class balance, source-disjoint, frozen-dataclass, no-emoji, reporting-completeness).
- `make lint` clean.
- `evals/v5/results.json` schema-validated against eval-toolkit's `results.v1.json`.
- All assumptions with severity ≥ medium in `assumptions.md` appear in the WRITEUP caveats block.

---

## 8. SDD process notes

1. **Spec freeze**: once this document is `LOCKED`, changes require an ADR.
2. **Phase 0 interview**: `[LOCKED]` agent reads spec, surfaces decisions, human picks, decisions become ADRs. v4 did not formally Phase 0; v5 adds the practice.
3. **Process gates, not outcome gates**: phase gates check that work was done and tests pass — not that metrics hit a target. v5 deliberately avoids tying phase movement to outcome numbers so that the eval reports what was found rather than what was needed to advance.
4. **Transcript capture**: `[LOCKED]` every session where decisions are discussed produces a transcript in `transcripts/`. v4 did not capture transcripts; v5 closes the gap.
5. **Prediction persistence**: `[LOCKED]` per-row predictions are persisted alongside metrics. v4 didn't do this; downstream analyses (calibration, threshold sweeps, ROC curves) required re-running inference. v5 closes the gap via `runpod-deploy` pull-pattern updates.
6. **ADR cadence**: one ADR per significant decision; format per Michael Nygard.
7. **Assumption updates**: when an assumption is invalidated mid-implementation, update `assumptions.md` and write a corrective ADR.
8. **Tests-as-invariants**: every spec claim that can be made executable as a test, must be.

**Linked ADRs**: ADR-001, ADR-025, ADR-026.

---

## 9. Open questions deferred to v6+

`[TBD — populate as v5 work proceeds]`

- `[TBD]`
- `[TBD]`

---

## Appendix: decision trace

`[TBD: link to the planning artifact at ~/.claude/plans/<v5-planning-slug>.md]`
