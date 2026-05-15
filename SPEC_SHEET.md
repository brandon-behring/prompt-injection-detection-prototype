# Project specification (filled at end of Phase 0)

**Status**: `[OPEN]` (`DRAFT` → `PROPOSED` → `LOCKED` — locks once Phase 0 closes all decisions)
**Type**: Single-version SDD spec; revisions tracked via ADRs (Michael Nygard format)

> **Role of this document.** SPEC_GREENFIELD.md is the authoritative pre-Phase-0 spec — it defines the contract and the open decisions. SPEC_SHEET.md is the post-Phase-0 fill-in form: same skeleton, but each `[OPEN]` row gets replaced with `[LOCKED: <chosen value>]` once Phase 0 resolves it. Phase 1 cannot begin until SPEC_SHEET.md has zero `[OPEN]` rows.

> **Companion docs**:
> - [`code_quality.md`](./code_quality.md) — implementation discipline
> - [`assumptions.md`](./assumptions.md) — registry of unverified assumptions
> - [`decisions/`](./decisions/) — ADR index + immutable decision records
> - [`EVIDENCE.md`](./EVIDENCE.md) — external-evidence audit trail

---

## Context

`[TBD: one-paragraph context populated at end of Phase 0 from ADR-001 brief alignment]`

- **Locked methodology defaults**: process discipline + validated content patterns are `[LOCKED]` generically; project-specific instantiation details (datasets, rungs, hyperparams, OOD slate, budget) are `[OPEN]` for Phase 0
- **Resolved at Phase 0**: see `decisions/` for ADRs locked during the spec interview
- **Open at start of Phase 0**: see SPEC_GREENFIELD ledger appendix for the ~50 [OPEN] decisions resolved during the interview

This is an **exploration spec** for an SDD-disciplined iteration — not a production system, not a paper, not a publishable benchmark. The work is *methodology + capability characterization braided*: characterize what each capability layer adds, using an evaluation methodology rigorous enough to detect real differences and quantify uncertainty.

---

## 1. Goal & non-goals

**Goal**: `[TBD: one-paragraph statement of what  commits to deliver]`

**Non-goals**:
- Not optimizing for SOTA PR-AUC.
- Not building a deployable service. Deployment is not on the roadmap.
- Not creating a publishable benchmark.
- `[OPEN]` Not picking a leader rung — each rung's trade-offs are characterized, no rung is promoted as the deployment recommendation.
- `[TBD: additional non-goals; populated at Phase 0]`

**Scope authority**: the spec itself is the scope cap. Anything not specified here is out of  scope. Adding scope post-spec-freeze requires an ADR with explicit "Why this is in scope now" justification.

---

## 2. Phases & process gates

the project work is structured into six phases. Each phase has a gate checklist of work-completed and tests-passing — **not metric thresholds**. The intent is to make movement between phases auditable, not to bind the project's narrative to specific numerical outcomes.

### Phase 0: Spec lock-in interview `[LOCKED]`

- [ ] Agent reads this spec end-to-end
- [ ] Every `[OPEN]` / `[TBD]` decision is surfaced as a clarifying question
- [ ] Human picks options for each surfaced decision
- [ ] Decisions are recorded as ADRs (Michael Nygard format)
- [ ] Phase 1 cannot start until every decision is resolved or explicitly deferred

Gate: `decisions/` directory contains an ADR for every Phase-0-resolved decision; `transcripts/` directory contains the interview transcript.

### Phase 1: Data

- [ ] Sources defined and licenses verified
- [ ] Audit complete; counts and class balance documented in `evals/data_audit.json`
- [ ] Semantic dedup applied per `[ADR-003]` (calibrated MiniLM @ 0.80); calibration evidence persisted at `evals/dedup_calibration.json`
- [ ] Cross-source benign dedup applied before split
- [ ] Leakage scan run; results in `evals/leakage_report.json`
- [ ] Train/val/test splits locked and persisted

Gate: every checkbox ticked; `tests/test_data.py` and `tests/test_leakage.py` green.

### Phase 2: Training

- [ ] Each rung's config persisted at `config/<rung>.yaml`
- [ ] All rungs trained successfully on `[TBD: (candidate) H100 via runpod-deploy]`
- [ ] Training artifacts captured per `runpod-deploy` manifest (git SHA, seed, GPU info, env)
- [ ] **Per-row predictions persisted** at `evals/predictions/<rung>__<fold>__<seed>.parquet` `[LOCKED]`
- [ ] Per-rung checkpoint persisted to `[TBD: HF Hub at BBehring/<project>; resolved at Phase 0]`

Gate: every checkbox ticked; training manifests schema-validated.

### Phase 3: Evaluation

- [ ] All rung × slice metrics computed via `eval-toolkit`
- [ ] OOD slate evaluated end-to-end (~4 slices typical; final composition resolved at Phase 0)
- [ ] Calibration battery run (ECE + Brier + reliability) for every rung
- [ ] Thresholds selected on validation only (detection-policy and verification-policy on in-house rungs; recall@FPR pinpoints on all rungs)
- [ ] `evals/results.json` schema-validated against `eval-toolkit`'s `results.v1.json` schema

Gate: every checkbox ticked; `evals/results.json` parses cleanly.

### Phase 4: Analysis

- [ ] Bootstrap CIs computed for every headline metric
- [ ] Paired-bootstrap differences computed for every rung-vs-rung comparison of interest
- [ ] MDE estimated for every reported CI
- [ ] Per-source / per-style breakdowns computed (LLM-as-rater rubric audit `[OPEN]`)
- [ ] Figures 1–7 (or the project's named slate) rendered to `docs/plots/`

Gate: every checkbox ticked; analysis JSON outputs match schemas.

### Phase 5: Writeup

- [ ] All WRITEUP sections drafted
- [ ] All  ADRs written and indexed in `decisions/README.md`
- [ ] Transcripts linked from WRITEUP appendix
- [ ] EVIDENCE.md populated for every external-evidence claim
- [ ] PDF bundled: README + WRITEUP + NEXT_STEPS + SPEC_SHEET + EVIDENCE
- [ ] All `[TBD]` / `[OPEN]` markers in submission templates resolved or justified

Gate: every checkbox ticked; PDF reads cleanly start-to-finish.

---

## 3. Data design

### 3.1 Train pool composition

`[OPEN]` Source slate — populated at Phase 0 from `docs/research/datasets/` candidate set.

| Source | Approx N | Role | License |
|---|---|---|---|
| `[OPEN]` | `[TBD]` | Train pos | `[TBD]` |
| `[OPEN]` | `[TBD]` | Train neg | `[TBD]` |
| `[OPEN]` | `[TBD]` | OOD only | `[TBD]` |

### 3.2 Splits

`[OPEN]` Splits structure — Phase 0 selects from {single 70/15/15, k-fold, source-disjoint LODO, hybrid}. See SPEC_GREENFIELD ledger §1 Data row "Splits structure" for reference anchors.

### 3.3 Dedup, leakage prevention, cross-source label conflicts

- **Semantic dedup**: `[OPEN]` encoder + threshold; calibrate against labelled holdouts per eval-toolkit `methodology/text_dedup.md`.
- **Cross-source minimal pairs**: `[LOCKED]` preserve-and-flag.
- **Cross-source benign dedup ordering**: `[OPEN]` before-split vs after-split.
- **Leakage invariants**: `tests/test_leakage.py` asserts no exact-hash and no high-cosine train-test overlap.
- **Reference-scorer training-overlap audit**: `[LOCKED]` see WRITEUP §3.3 + EVIDENCE.md §1–2.

### 3.4 OOD slate

`[OPEN]` slice list — populated at Phase 0 from `docs/research/benchmarks/` candidate set.

| Slice | Source | Role | Why |
|---|---|---|---|
| `[OPEN]` | `[TBD]` | `[TBD]` | `[TBD]` |

**Linked ADRs**: ADR-NNN (threat model), ADR-NNN (dataset slate), ADR-NNN (dedup), ADR-NNN (splits + balance) — filled in once Phase 0 locks each row.

---

## 4. Model recipe (locked, no gridsearch)

Each rung is locked before training begins. No val-set hyperparameter gridsearch.

### 4.1 Rung 1 — *linear floor*
`[OPEN]` Linear baseline (e.g. TF-IDF + logistic regression). Deterministic.

### 4.2 Rung 2 — *frozen-features probe*
`[OPEN]` Frozen-transformer embeddings + linear head. Deterministic at a pinned seed.

### 4.3 Rung 3 — *adapter-fine-tuned*
`[OPEN]` Adapter-fine-tuned transformer recipe. Hyperparameters (r, α, dropout, target modules, lr, epochs, precision, batch, max_len, warmup, seed protocol) locked at Phase 0 per SPEC_GREENFIELD §2 Model ledger rows.

### 4.4 Rung 4 — *narrow-scope reference scorer (optional)*
`[OPEN]` Off-the-shelf classifier with narrow scope. Inference-only. Training-data overlap audit per EVIDENCE.md §1.

### 4.5 Rung 5 — *broad-scope reference scorer (optional)*
`[OPEN]` Off-the-shelf classifier with broader scope. Inference-only. Training-data audit per EVIDENCE.md §2.

### 4.6 Additional rungs

`[OPEN]` Candidates: alternate backbone + adapter; alternate classification head; calibration via validation-fit temperature.

**Linked ADRs**: filled in once Phase 0 locks each rung.

---

## 5. Eval design

### 5.1 Primary descriptive metrics

PR-AUC, ROC-AUC, recall@FPR={0.1%, 1%, 5%} `[OPEN: recall@FPR pinpoints; resolved at Phase 0]`, ECE (equal-mass + Kumar-2019 debiased), Brier. All reported with bootstrap CIs.

### 5.2 Statistical tests

**Stance**: report effect sizes and CIs only. No p-values. The work characterises differences and their uncertainty rather than claiming significance.

Anchored to [eval-toolkit](https://github.com/brandon-behring/eval-toolkit) primitives:

- `bootstrap_ci` — per-metric finite-sample uncertainty. See [methodology/bootstrap.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/bootstrap.md).
- `paired_bootstrap_diff` — paired comparisons across rungs on the same test set. See [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md).
- `mde_from_ci` — minimum detectable effect.
- Calibration battery (`reliability_curve`, `fit_temperature`, `fit_isotonic`, ECE variants, Brier). See [methodology/calibration.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/calibration.md).
- `cv_clt_ci` — CLT-based CI for cross-fold variance.

### 5.3 Operating points — detection vs verification

`[LOCKED]` Dual-policy framing on **in-house rungs only**. Reference scorers (off-the-shelf reference detectors) get recall@FPR pinpoints with explicit contamination caveats; no dual-policy framing (would imply deployment-ready operating points that don't survive the contamination caveat).

Detection (FPR ≤ 1%) + Verification (FNR ≤ 1%) selected on **validation only** via eval-toolkit's `ThresholdSelector` protocol. See [methodology/thresholds.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/thresholds.md).

### 5.4 Per-source and per-style breakdowns

Required for any OOD claim — aggregate metrics hide heterogeneity. Reported alongside the headline IID/OOD numbers. Per-style heuristic tagger regex-based) is conservative;  may `[TBD: (candidate) invest in LLM-as-rater rubric audit]`.

### 5.5 Adversarial robustness

`[TBD: largely deferred; named but not exhaustively probed]` — the threat model (paraphrase, encoded payloads, multi-turn injection, base64/leetspeak obfuscation) is named; what was not tested is named explicitly in WRITEUP §5.6 and §8.

**Linked ADRs**: ADR-021, ADR-022, ADR-023.

---

## 6. Code architecture

The work spans three repos:

- **`prompt-injection-detection-submission`** (this repo) — modelling: data loading, training, classification API, project-specific scoring code.
- **[`eval-toolkit`](https://github.com/brandon-behring/eval-toolkit)** — evaluation harness: metrics, bootstrap, calibration, threshold selection, leakage detection, slice-aware orchestration, reproducibility manifests, versioned JSON schemas.
- **[`runpod-deploy`](https://github.com/brandon-behring/runpod-deploy)** — cloud orchestration for training/eval runs on rented GPUs. **the project's additions**: prediction-persistence pull-pattern + checkpoint upload-to-HF-Hub pattern.

The split is intentional: methodology curriculum and primitives live in `eval-toolkit` so they survive across iterations; cloud orchestration lives in `runpod-deploy` so it's reusable across projects.

---

## 7. Verification & acceptance criteria

This iteration is considered complete when **all five Phase 5 gates pass**:

- All WRITEUP sections drafted with `[TBD]` markers resolved.
- All  ADRs written.
- Transcripts linked.
- EVIDENCE.md populated for every external-evidence claim.
- PDF bundled.
- Markers explained.

Plus the standard quality gates that apply to every phase:

- `make test` passes (incl. invariants for class balance, source-disjoint, frozen-dataclass, no-emoji, reporting-completeness).
- `make lint` clean.
- `evals/results.json` schema-validated against eval-toolkit's `results.v1.json`.
- All assumptions with severity ≥ medium in `assumptions.md` appear in the WRITEUP caveats block.

---

## 8. SDD process notes

1. **Spec freeze**: once this document is `LOCKED`, changes require an ADR.
2. **Phase 0 interview**: `[LOCKED]` agent reads spec, surfaces decisions, human picks, decisions become ADRs. .
3. **Process gates, not outcome gates**: phase gates check that work was done and tests pass — not that metrics hit a target.  deliberately avoids tying phase movement to outcome numbers so that the eval reports what was found rather than what was needed to advance.
4. **Transcript capture**: `[LOCKED]` every session where decisions are discussed produces a transcript in `transcripts/`. .
5. **Prediction persistence**: `[LOCKED]` per-row predictions are persisted alongside metrics. `runpod-deploy` pulls per-row score artifacts so downstream analyses (calibration, threshold sweeps, ROC curves) run from persisted predictions without re-running inference.
6. **ADR cadence**: one ADR per significant decision; format per Michael Nygard.
7. **Assumption updates**: when an assumption is invalidated mid-implementation, update `assumptions.md` and write a corrective ADR.
8. **Tests-as-invariants**: every spec claim that can be made executable as a test, must be.

**Linked ADRs**: ADR-001, ADR-025, ADR-026.

---

## 9. Open questions deferred to future iterations

`[TBD — populate as  work proceeds]`

- `[TBD]`
- `[TBD]`

---

## Appendix: decision trace

`[TBD: link to the planning artifact at ~/.claude/plans/<planning-slug>.md]`
