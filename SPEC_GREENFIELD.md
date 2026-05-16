# Greenfield specification — prompt-injection classifier

**Status**: `[OPEN]` (DRAFT → PROPOSED → LOCKED)
**Type**: Spec-Driven Development (Constitution + Feature Specs)
**Audience**: human and/or agent building a methodology-driven prompt-injection classifier from scratch

This document is a *decision contract*. It locks in methodology rigor, the recommended tooling stack, and the SDD discipline. It leaves most concrete choices (datasets, models, thresholds, OOD slices) `[OPEN]` so that the implementer — human, agent, or both collaborating — resolves them during Phase 0 of the roadmap.

Read end-to-end before starting any work. Every `[OPEN]` callout marks a decision you must resolve before Phase 1 begins.

> **Note**: This version of the greenfield spec absorbs 8 additional `[OPEN]` decisions that emerged from working an end-to-end iteration (see Decision ledger appendix for the 8 new rows). The additions cover reference-scorer audit methodology (for partial-disclosure sources), HF dataset revision pinning, cross-source benign dedup ordering, LoRA training axes (epoch / precision / class-weight implementation), smoke-vs-canonical eval separation, and compute cost-cap discipline.

---

## Constitution

The project Constitution is split across three files (DLAI-style 3-file Constitution pattern):

- **[`docs/MISSION.md`](./docs/MISSION.md)** — Mission / Audience / Problem classes in scope / Success criteria / Non-goals / Scope authority
- **[`docs/TECH_STACK.md`](./docs/TECH_STACK.md)** — Load-bearing libraries (eval-toolkit / runpod-deploy / research_toolkit) / Library-first discipline / Upstream-issue triage / GPU / secrets / cache
- **[`docs/ROADMAP.md`](./docs/ROADMAP.md)** — Phase 0-5 sequence with sub-session detail and replanning checkpoints

The decision ledger appendix at the bottom of this file references these by section name (e.g., `§Tech-Stack`, `§Roadmap`, `§Brief`); the section anchors now live in those three files.

---

## Feature Specs

### §0 Threat model

The classifier targets a subset of the prompt-injection attack surface. Naming the full surface here is intentional — the implementer is expected to scope explicitly, not implicitly.

**Attack classes named**:

- **Direct injection** — adversarial text in user input that attempts to override system instructions (override-style, role-play wrappers, jailbreak-via-fictional-framing).
- **Indirect injection** — adversarial text arriving via context channels (retrieved documents, tool outputs, file attachments, email bodies).
- **Multi-turn injection** — adversarial payload split across multiple conversation turns; only the cumulative effect is hostile.
- **Encoded payloads** — base64, leetspeak, hex, ROT13, Unicode confusables; the payload's semantics survive encoding but not surface n-gram matching.
- **Paraphrase attacks** — semantic equivalents of training-set injections that don't share surface features.
- **Adversarial perturbations** — gradient-guided or search-based input modifications designed to evade a specific classifier.

**Default scope** — `[OPEN]`:

> **Decision needed:** which attack classes are in initial scope.
> **Options:** direct only / direct + indirect / direct + adversarial / project-specific subset.
> **Considerations:** training data availability, evaluation-data availability, time, claim-honesty implications of scoping a class in (you'll need to evaluate it).
> **Default if unsure:** direct injection only; everything else marked `[deferred]` in the writeup's threat-model section.

**Adversarial robustness** — `[LOCKED]` named but **default-deferred**. The implementer may scope adversarial in by writing an ADR; the default is deferred, named in the eventual writeup's limitations chapter without claiming coverage. Excluding adversarial robustness from scope is *not* the same as ignoring it — naming it deferred signals awareness.

**Language scope** — `[OPEN]`:

> **Decision needed:** English-only or multilingual.
> **Considerations:** data availability per language, the classifier's transferability claim, evaluation cost.
> **Default if unsure:** English-only; multilingual deferred.

**Length cap** — `[OPEN]`:

> **Decision needed:** maximum input token length the classifier scores.
> **Considerations:** training-data length distribution, model context window, downstream use case.
> **Default if unsure:** 512 tokens, single-turn.

### §1 Data design

**Source selection** — `[OPEN]`:

> **Decision needed:** which datasets for positives, negatives, and OOD probes.
> **Considerations:** license (must allow redistribution of fixtures and predictions); size relative to the rung-ladder model capacity; label noise (verify use of dataset's own labels rather than derived heuristics); distribution-shift coverage across positives.
> **Default if unsure:** start with 2–3 public prompt-injection datasets for positives + 1 broad benign corpus for negatives + 1 held-out OOD slice from a different channel (e.g., indirect email).

**HF dataset revision pinning** — `[OPEN]`:

> **Decision needed:** pin to specific HF dataset commit SHAs at build time, or use `revision="main"`?
> **Options:** pin SHAs at build time (forward-only, reproducibility-first) / pin SHAs and lockstep-update on revision changes / use `revision="main"` and accept drift.
> **Considerations:** dataset cards on HF can be revised by maintainers (label fixes, format changes, deletions); a benchmark that floats on `main` is not bit-reproducible across builds. SHA pinning is cheap and surfaces drift as a diff.
> **Default if unsure:** pin SHAs at first canonical build, forward-only updates with an ADR per bump.

**Dedup discipline** — `[LOCKED]`: label-aware semantic dedup. Within each (source, label) cell, keep the first occurrence by deterministic ordering and drop subsequent near-duplicates. Cross-label near-duplicates within a source are *preserved* — they are minimal pairs and are exactly the informative examples a classifier needs. Cross-source label-conflicting near-duplicates are also preserved and flagged.

> **Decision needed:** dedup encoder + threshold.
> **Options:** label-blind n-gram cosine / label-aware sentence-embedding cosine (MiniLM or MPNet) / hybrid.
> **Considerations:** anisotropic-embedding pitfalls; calibrate the threshold against labelled holdouts before locking; cross-link the [methodology/text_dedup.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/text_dedup.md) chapter.
> **Default if unsure:** label-aware semantic dedup with MiniLM/MPNet bake-off, threshold chosen by 4-gate selection rule, calibration evidence persisted in `evals/dedup_calibration.json`.

**Cross-source benign dedup ordering** — `[OPEN]`:

> **Decision needed:** apply cross-source benign dedup BEFORE or AFTER the train/val/test split?
> **Options:** before (clean benign pool then split) / after (split first then audit per-fold).
> **Considerations:** if benign sources have textual overlap (e.g., overlap between a broad open-instruct corpus and a hard-benign trap set), splitting first means duplicate-but-different-fold pairs survive — invisible to within-source dedup, surfacing only as fold-level leakage audit failures. Cross-source-then-split avoids the failure mode at the cost of one extra pass.
> **Default if unsure:** cross-source benign dedup BEFORE the split.

**Leakage detection** — `[LOCKED]`: two invariant tests, plus a third for any external reference scorer.

1. Exact-hash train-test overlap scan — assert zero matches.
2. High-cosine train-test overlap scan — assert no test row has cosine ≥ `[OPEN: threshold]` to any train row of the same label.
3. **Public-model leakage audit** — for any external reference scorer (a published classifier evaluated alongside the rung ladder), audit its training-data overlap with each evaluation slice. Document overlap percentages in the writeup so the reference scorer's numbers are read as diagnostic, not as a clean baseline.

Cross-link [methodology/leakage.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/leakage.md).

**Reference-scorer audit methodology — partial-disclosure case** — `[OPEN]`:

> **Decision needed:** how to audit a reference scorer when its model card discloses training data only at category level (e.g., "open-source malicious injection datasets") rather than by named source?
> **Options:** (A) fold-pattern analysis only — report per-fold deltas as suggestive evidence; (B) fold pattern + stated scope cross-check — flag scope-mismatch as direct contamination evidence (e.g., model card says "doesn't detect jailbreaks" but scores high on a jailbreak slice); (C) cross-source same-style ablation — disambiguate "training contamination" from "attack-style difficulty"; (D) all three.
> **Considerations:** matching fold patterns across detectors is suggestive but not dispositive — could equally be attack-style difficulty. Scope mismatch is the strongest single piece of evidence when available. The same-style ablation is the gold standard but requires sufficient per-style sample size.
> **Default if unsure:** (D) all three; document each detector's audit verdict in `EVIDENCE.md` with `[VERIFIED|UNVERIFIED|REFUTED]` per claim.

**Splits** — `[LOCKED]`: source-disjoint discipline. Train and test rows must not share both a source identifier and high textual similarity.

> **Decision needed:** single-split vs k-fold.
> **Options:** single 70/15/15 / source-disjoint k-fold (k chosen against power) / source-disjoint LODO (leave-one-dataset-out) per Fomin 2025 / hybrid.
> **Considerations:** k-fold gives variance estimates but consumes test rows; single-split is simpler but doesn't estimate variance. LODO with k=number-of-positive-sources is the field standard for distribution-shift evaluation. Cross-link [methodology/splits.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/splits.md).
> **Default if unsure:** source-disjoint LODO with k = number of positive sources (typically 3–4).

### §2 Model recipe — the rung ladder

**Ladder structure** — `[LOCKED]`: an ordered sequence of classifiers of increasing complexity, designed so each step's lift over the previous rung decomposes *which capability* is responsible (linear features alone → pretrained-features alone → off-the-shelf model → adapter-tuned model, etc.). This is the "models of increasing complexity" axis referenced in Mission success criteria.

**Rung selection** — `[OPEN]`:

> **Decision needed:** how many rungs and what each represents.
> **Common pattern:** linear floor (TF-IDF + LR) → frozen-features probe (frozen transformer + linear head) → off-the-shelf transformer classifier → adapter-fine-tuned transformer.
> **Considerations:** each rung should be a meaningful capability step (not a hyperparameter variant); each rung must be cheap enough to train multiple times for variance estimation; off-the-shelf rungs need a public-model leakage audit (§1).
> **Default if unsure:** 4-rung ladder per the common pattern above. Consider including TWO reference scorers if available (one narrow-scope + one broad-scope) to reveal training-data contamination patterns more clearly.

**Hyperparameter policy** — `[LOCKED]`: lock hyperparameters per rung *before* training begins. No val-set gridsearch. Use literature defaults where available; document the source of each non-default choice as an ADR. This discipline keeps the eval honest — the test set isn't a tuning target.

**LoRA epoch policy (if a LoRA rung is included)** — `[OPEN]`:

> **Decision needed:** how many fine-tuning epochs for the LoRA rung?
> **Options:** 1 epoch / 2 epochs / 3+ epochs / early-stopping on val.
> **Considerations:** 1-epoch LoRA can dramatically undertrain on small pools (cross-source generalization may collapse). 2 epochs is a common sweet spot. Early-stopping on val introduces a tuning-on-val signal unless paired with a held-out test that the early-stop signal never touches.
> **Default if unsure:** 2 epochs with no early stopping; run a 1-epoch control on at least one fold to confirm 2-epoch is not over-fitting.

**LoRA precision policy (if a LoRA rung is included)** — `[OPEN]`:

> **Decision needed:** mixed-precision training in bf16, fp16, or fp32?
> **Options:** bf16 (modern GPUs, larger dynamic range) / fp16 (older GPUs) / fp32 (safest, slowest).
> **Considerations:** bf16 is the H100 default; modeling-accuracy delta vs fp16 is typically small on this task class. fp16 softmax can be unsupported on some inference paths (cast logits to fp32 before `torch.softmax`). fp32 is twice the memory.
> **Default if unsure:** bf16 for training and inference; explicitly cast logits to fp32 before the final softmax to avoid backend mismatches.

**LoRA class-weight implementation** — `[OPEN]`:

> **Decision needed:** how to weight the positive class in LoRA training loss?
> **Options:** sklearn-style (`w_c = N / (2 × n_c)`) applied via custom loss; HF-Trainer-style (`pos_weight = n_neg / n_pos`) via `BCEWithLogitsLoss`; uniform (no weighting).
> **Considerations:** for typical pool imbalances on this task class, sklearn-style and HF-Trainer-style are functionally equivalent (deltas <0.001 PR-AUC). Uniform may underperform on small positive classes.
> **Default if unsure:** HF-Trainer-style — it's the smoother integration with HF training loops.

**Compute budget** — `[OPEN]`:

> **Decision needed:** GPU class and per-rung training time budget.
> **Considerations:** rung complexity, dataset size, number of seeds for variance estimation. Adapter-fine-tuning on a modern GPU is usually under 1 hour for the dataset sizes typical of this domain.
> **Default if unsure:** H100 via runpod-deploy; 1 hour per rung; 3 seeds for variance estimation on the fine-tuned rung.

### §3 Eval framework

**Stance** — `[LOCKED]`: report **effect sizes and confidence intervals only**. No p-values.

> Rationale: in finite-sample settings, "what's the effect and how confident are we in it" is the answerable question. "Is this nonzero at α = 0.05" is a question whose answer depends more on the sample size than on the phenomenon. Modern best practice in applied ML evaluation prefers effect sizes + CIs; eval-toolkit's primitives are built around this preference.

**Descriptive metrics** — `[LOCKED]` minimum reporting:

- **PR-AUC** — primary ranking metric for class-imbalanced binary classification.
- **ROC-AUC** — class-prior-independent ranking; for cross-paper comparison.
- **recall @ FPR** at multiple operational points (e.g., 0.1%, 1%, 5%).
- **ECE (equal-mass + Kumar-debiased) + Brier** — calibration battery; see below.

Cross-link [methodology/comparison.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/comparison.md) for why each metric is preferred over plain F1.

**Statistical tests** — `[LOCKED]` minimum set, all from eval-toolkit:

- **Per-metric bootstrap CIs** (`bootstrap_ci`) — finite-sample uncertainty on every headline number; percentile bootstrap; pinned seed with a stability check at a second seed.
- **Paired-bootstrap differences** (`paired_bootstrap_diff`) — same-test-set rung-vs-rung comparison; accounts for paired-error correlation without requiring parametric assumptions like DeLong's. Cross-link [methodology/bootstrap.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/bootstrap.md).
- **MDE** (`mde_from_ci`) — minimum detectable effect from CI width at α = 0.05, power = 0.80. Distinguishes "no difference detected" from "no power to detect."
- **Calibration battery** — `reliability_curve`, `fit_temperature`, `fit_isotonic_calibrator`, ECE variants, Brier score. Cross-link [methodology/calibration.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/calibration.md).
- **CV-CLT CI** (`cv_clt_ci`) — when k-fold is used, CLT-based CI with Nadeau-Bengio-style variance correction handles per-fold dependence properly.

**Per-row prediction persistence** — `[LOCKED]`: every training/inference run persists per-row score predictions alongside summary metrics (e.g., `evals/predictions/<rung>__<fold>__<seed>.parquet` with columns `text_hash, y_true, y_score, source, slice`). Downstream analyses (calibration, threshold sweeps, ROC curves, recall@FPR at arbitrary pinpoints) MUST be able to operate on persisted predictions without re-running inference. Failing to persist predictions is a methodology bug — it forces all downstream analysis to re-run inference, which means most downstream analysis simply doesn't happen.

**OOD slate** — `[OPEN]`:

> **Decision needed:** which OOD slices and what each probes.
> **Common probes:** benign over-defense (a benign corpus the classifier shouldn't flag); channel shift (indirect-injection slices); external-source generalisation (a different positives dataset held out entirely).
> **Considerations:** each slice should answer a different generalisation question; per-slice n must be sufficient for meaningful CIs.
> **Default if unsure:** at least one benign-over-defense slice + one external-channel slice + one external-source slice.

### §4 Threshold policy — score-behaviour characterisation

**Operating-point framing** — `[LOCKED]`: the same classifier scores serve two operational contexts under different cost weights:

- **Detection policy** — *catch injections coming in*. False negatives are the high-cost error; tolerate false positives up to an alerting-budget.
- **Verification policy** — *confirm clean text is clean*. False positives are the high-cost error; tolerate some missed injections.

These are not two classifiers; they are two threshold policies on the same scores. Reported as **characterisation** of the score's behaviour at two cost regimes, **not as deployment recommendations** (deployment is out of scope per Mission non-goals).

Selection uses eval-toolkit's `ThresholdSelector` protocol on **validation only** (never test). Both policies use the same primitive with symmetric cost weights, so the method generalises across heterogeneous rungs whose score scales aren't comparable.

**Dual-policy applicability** — `[LOCKED]`: dual-policy threshold characterisation applies only to rungs whose scores aren't carrying training-overlap caveats. Reference scorers (off-the-shelf classifiers with contamination concerns) report recall@FPR pinpoints only, with explicit caveats. Reporting "rung X achieves Y% recall at FPR ≤ 1%" implies a deployment-ready operating point — that's misleading when the underlying score reflects memorisation rather than generalisation.

**Cost-weight targets** — `[OPEN]`:

> **Decision needed:** FPR target for detection policy; FNR target for verification policy.
> **Considerations:** symmetric targets (e.g., both 1%) make the framing clean and the comparison readable; asymmetric targets require justification.
> **Default if unsure:** detection policy targets FPR ≤ 1% on validation; verification policy targets FNR ≤ 1%. Cross-link [methodology/thresholds.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/thresholds.md).

### §5 Code architecture

**Three-repo split** — `[LOCKED]`:

- **Modelling repo** (this repo) — data loading, training, classification API, project-specific scoring code, invariant tests.
- **eval-toolkit** — evaluation harness, methodology curriculum.
- **runpod-deploy** — cloud orchestration.

This separation makes each repo independently auditable, reusable across versions, and replaceable.

**Module layout** — `[LOCKED: concern-grouped sub-packages under src/ (per ADR-026)]`: `src/{data, training, scoring, eval, utils}/` with each sub-package containing related modules; `scripts/` for CLI entrypoints (orchestrate `src/` calls; not importable); `configs/{runpod, rungs, profiles, data}/` for versioned YAML; `tests/{conftest.py, test_invariants.py, fixtures/, unit/, smoke/, integration/}` for verification. `src/` is library code (importable, no side effects); `scripts/` is entrypoint glue; `configs/` is data; `tests/` is verification. Adding or moving a top-level `src/` sub-package requires a superseding ADR.

**Configuration discipline** — `[LOCKED]`: all hyperparameters in a versioned YAML config file. An invariant test asserts the config hash is committed; mutating the config requires updating the hash in a git commit.

**Smoke vs canonical eval separation** — `[LOCKED: three Makefile targets stratified by execution context (per ADR-027)]`: (1) `make smoke` runs `pytest -m smoke` + a fixture-data end-to-end pass through `scripts/run_metrics_battery.py --config configs/profiles/fixtures.yaml` — laptop only, no GPU, no network, <10 min total; (2) `make test-integration` runs `pytest -m integration` — GPU-aware (uses CUDA via `torch.cuda.is_available()` if present, skips gracefully via `pytest.importorskip` + `pytest.mark.skipif` if not) — same target serves two execution contexts (local-GPU developer-workstation debugging AND cloud-pod pre-flight smoke check before paying for the canonical run); (3) `make headline-cloud` wraps `runpod-deploy validate --all` + `runpod-deploy run --dry-run` + `runpod-deploy run --config configs/runpod/headline.yaml` — RunPod-billed canonical evaluation deliverable, NOT a test, cost-cap-gated $125/job per ADR-020. Math-correctness rigor (Hypothesis property tests, golden-output snapshots, ≥90% coverage on math kernels) lives upstream in eval-toolkit; the local test layer is debugging-grade by design — sufficient to catch glue-layer breakage, not sufficient to substitute for upstream library validation. `WRITEUP/methodology.md` carries the honest framing paragraph so reviewers do not interpret debugging-grade local tests as production-grade methodology validation.

**SDD artefacts** — `[LOCKED]` required in the modelling repo:

- `spec.md` — this document (or its instantiated version).
- `assumptions.md` — registry of unverified assumptions with severity tags.
- `decisions/` — ADRs in Michael Nygard format; one ADR per significant decision.
- `transcripts/` — decision-conversation captures; see §7.
- `EVIDENCE.md` — audit trail for external-evidence claims (especially reference-scorer training-overlap audits).

**Tests-as-invariants** — `[LOCKED]`: every spec claim that can be made executable as a test, must be. Standard invariants to implement:

- Class-balance invariant — per-fold negative:positive ratio within tolerance.
- Source-disjoint invariant — each test slice's source not present in train sources.
- Hyperparameter-immutability invariant — config hash matches the committed value.
- Calibration-honesty invariant — temperature scaling fits only on validation, not test.
- Reporting-completeness invariant — every assumption with severity ≥ medium appears in the writeup caveats block.
- No-emoji invariant — scan for emoji code points, fail on any.
- Frozen-dataclass invariant — classes whose name ends in `Config` or `Result` are frozen + slotted.

### §6 Verification & acceptance criteria

A project instance of this spec is considered complete when:

- `[LOCKED]` `make test` passes (invariants + math correctness + smoke).
- `[LOCKED]` `make lint` is clean (formatter + linter + type-checker strict).
- `[LOCKED]` Evaluation results JSON validates against `results.v1.json` schema from eval-toolkit.
- `[LOCKED]` Per-row predictions are persisted (closes the gap where downstream analysis can't be re-run without re-inference).
- `[LOCKED]` Every assumption with severity ≥ medium in `assumptions.md` appears in the writeup caveats block.
- `[LOCKED]` `EVIDENCE.md` has an entry for every external-evidence claim in WRITEUP §7.
- `[LOCKED]` Reproducibility: a stranger can clone, install, and reproduce headline numbers via documented commands.
- `[OPEN]` Project-specific acceptance criteria.

> **Decision needed:** project-specific acceptance criteria (e.g., required reproducibility tier, runtime targets, CI gates).

**Compute cost cap** — `[OPEN]`:

> **Decision needed:** total compute-cost cap for the project (US dollars).
> **Options:** strict cap (work stops at cap) / soft cap (escalation required to exceed) / no cap.
> **Considerations:** rented GPU time accumulates fast — debugging a failing training run can burn $5-20 quickly. A cap forces explicit cost/value trade-offs and keeps "let's just re-run it" from being free. Tracking actual spend per phase enables retrospective.
> **Default if unsure:** soft cap at $50 for a methodology-validation prototype; strict cap at $200 for an extended iteration. Log all spend in a CHANGELOG-style ledger per Makefile target.

### §7 SDD process notes

The process discipline below is `[LOCKED]`. Adopting this spec means adopting this workflow.

- **Spec freeze**: once this document is `LOCKED`, changes require an ADR explaining the change and what was previously specified.
- **Phase 0 interview (mandatory)**: before any code is written, the agent reads the full spec, surfaces every `[OPEN]` decision, asks clarifying questions, the human picks options, and each decision is recorded as an ADR. Phase 1 may not begin until every `[OPEN]` decision is resolved (or explicitly deferred to a later phase with rationale).
- **Transcript capture (mandatory)**: every session where decisions are discussed produces a transcript stored at `transcripts/<YYYY-MM-DD>__<slug>.md`. Captured via `/save-transcript <slug>` (skill at `.claude/skills/save-transcript/`). ADRs that result from a conversation link to the transcript: "see `transcripts/<slug>.md` for the conversation that led to this decision." Transcripts are the decision-rationale trail; without them, ADRs lose the *why* behind the *what*.
- **Scope cap**: the spec is the scope authority. Anything not specified is out of scope. Adding scope post-spec-freeze requires an ADR with explicit "why this is in scope now" justification — never a casual addition.
- **ADR cadence**: one ADR per significant decision; Michael Nygard format (Status / Context / Decision / Consequences / Alternatives Considered). ADRs are immutable; supersede via new ADRs that update the prior's status to `superseded-by-N`. The spec is updated by editing the ledger row + SPEC_SHEET slot to reference the new ADR; the prior ADR file remains as historical record.
- **Assumption updates**: when an assumption is invalidated mid-implementation, update `assumptions.md` and write a corrective ADR. Do not silently revise.
- **Tests-as-invariants**: every spec claim that can be made executable as a test must be.
- **Evidence audit**: every external-evidence claim in the writeup gets an entry in `EVIDENCE.md` with verification status `[VERIFIED|UNVERIFIED|REFUTED]`. Reference-scorer contamination uses the three-state taxonomy: `verified_disjoint | suspected_contamination | vendor_black_box`.
- **Claim status register**: every claim in README / WRITEUP / EVIDENCE / SUBMISSION carries a status in `SUBMISSION_AUDIT.md` (`OPEN | LOCKED | TBD | DEFERRED`). The register is **script-generated from ADR frontmatter** by `scripts/regenerate_audit.py` and gated in CI (no claim ships unless status is `LOCKED` or explicitly `DEFERRED`).
- **Commit discipline**: each meaningful work unit is its own commit. Type-prefixed messages (`feat:`, `refactor:`, `docs:`, `chore:`, `test:`, `fix:`, `seed:`). `Co-Authored-By: Claude <noreply@anthropic.com>` trailer. Commits that lock or supersede a Phase 0 decision reference the ADR-NNN. **No amend / no squash / no force-push** — fix-forward with new commits; the history is meant to show real development including missteps.
- **Anti-patterns to avoid**:
  - Adding a methodology component without an ADR.
  - Adding an evaluation dataset without a leakage scan.
  - Tuning anything on test data — even informally during error analysis.
  - Treating null results as failures rather than information.
  - Persisting only summary metrics without per-row predictions (breaks downstream analysis).
  - Hand-rolling functionality already in eval-toolkit / runpod-deploy / research_toolkit.
  - Working around a library limitation without filing an upstream issue.
  - Skipping transcript capture for a multi-turn decision conversation.
  - Mutating a locked decision without writing a superseding ADR.
  - Rewriting git history (amend, squash, force-push). Fix-forward with new commits.

### §8 Open questions deferred to implementation phase

`[OPEN]` populated by the implementer as decisions surface that this spec didn't anticipate. Resolved decisions migrate from here to the Decision ledger.

---

## Appendix: Decision ledger

Track every `[OPEN]` decision raised by the spec. Phase 0 resolves each one. Status legend: `open` (not yet decided) / `locked-to-X (see ADR-NNN)` (decided) / `deferred-to-phase-N` (explicitly punted with rationale) / `superseded-by-NNN` (locked, then changed).

| Section | Decision | Options | Status | Rationale | Recorded in | Reference anchors |
|---|---|---|---|---|---|---|
| §Brief | Submission deadline / time budget | calendar date + working days available | locked-to-2026-05-18-tight-with-fallback-ladder (see ADR-001) | Long-scope ambition under Tight calendar via infra leverage; fallback ladder 2×3 → 2×2 → 1×2 → 1×1 pre-committed | ADR-001 | brief itself + project plan |
| §Brief | Deliverable format | PDF / GitHub repo / both / tarball | superseded-by-030 (originally locked-to-PDF+repo per ADR-002; superseded by ADR-030 at Phase 0-07 Q1 — repo-only with Quarto-rendered HTML site via GitHub Actions; no PDF) | repo-only with Quarto HTML site; pandoc + LaTeX removed; reviewer URL pinned at submission tag per ADR-033 | ADR-002 (superseded), ADR-030 | brief itself + Quarto websites docs |
| §Brief | Repo visibility | public / private / mixed (code public + writeup private) | locked-to-public (see ADR-003) | kit default ratified; .gitignore enforces transcripts/brief/secret privacy partition | ADR-003 | brief itself; GitHub privacy docs |
| §Brief | Reviewer profile + expected reading time | hiring manager / ML researcher / mixed; 15 min / 1 hr / longer | superseded-by-031-for-hub-artefact (originally locked-to-A1+A2/B4-hub-spoke per ADR-004; A1+A2 profile + B4 stance + hub-and-spoke structure survive; hub artefact shifts from PDF to Quarto site index.qmd + sidebar nav at Phase 0-07 Q1 via ADR-031) | dual-audience A1+A2; B4 open-ended layered; hub = index.qmd + Quarto sidebar nav; 8 spokes finalized (7 from ADR-004 + WRITEUP/reproducibility.md per ADR-034) | ADR-004 (superseded), ADR-031 | brief itself + Quarto sidebar docs |
| §Brief | Brief-mandated metrics or constraints | enumerated from brief text | locked-to-Q5-batch (see ADR-006 to ADR-012) | 4-metric headlines + 3-pinpoint Recall@FPR + estimation-over-testing + rung architecture + Cohen's kappa + public-only data + hybrid splits + process mandates + scope+extension-conditions + 8 methodology guarantees + soft-signals naming + artifact engagement set | ADR-006..012 | brief itself |
| §Tech-Stack | GPU class | H100 / A100 / consumer GPU / mixed | open | | | runpod-deploy docs; RunPod pricing page |
| §Tech-Stack | Secrets management | env file / vault / cloud secret manager | open | | | runpod-deploy secrets pattern; project policy |
| §Tech-Stack | Dataset cache location | local / shared / cloud | locked-to-local+HFHub-or-S3 (see ADR-013) | pre-teardown persistence discipline; per-row predictions local + checkpoints HF Hub | ADR-013 | runpod-deploy cache patterns |
| §Tech-Stack | eval-toolkit version | semver pin | open | | | https://github.com/brandon-behring/eval-toolkit/releases |
| §Tech-Stack | runpod-deploy version | semver pin | open | | | https://github.com/brandon-behring/runpod-deploy/releases |
| §Tech-Stack | research_toolkit version | semver pin | open | | | https://github.com/brandon-behring/research_toolkit/releases |
| §Tech-Stack | Python version pin | >=3.10 / >=3.11 / >=3.12 / >=3.13 | open | | | https://devguide.python.org/versions/ |
| §Tech-Stack | Library-first / hand-rolling | locked: library primitives only; project-specific glue allowed | locked-to-spec | anti-hand-rolling discipline; project glue exception | inline §Tech-Stack | n/a |
| §Tech-Stack | Upstream-issue triage | locked: file issues before workarounds | locked-to-spec | contribution-trail discipline | inline §Tech-Stack + decisions/upstream_issues.md | n/a |
| Roadmap | Phase tailoring | as-is / project-specific tailoring | open | | | inline §Roadmap |
| §0 Threat | Attack classes in scope | direct / direct+indirect / direct+adversarial / custom | locked-to-direct-primary+indirect-zero-shot-OOD (see ADR-014) | no labeled indirect training data in dossier-vetted slate; honest framing surfaces train/eval asymmetry as methodology finding | SPEC_SHEET §3.3 + WRITEUP/limitations-and-future-work.md | docs/research/attacks_defenses/; OWASP LLM Top 10 |
| §0 Threat | Language scope | English-only / multilingual | locked-to-english-only (see ADR-014) | every dossier-vetted eval slice is English; researcher cannot independently audit non-English samples; reaffirms ADR-010 Bound 1 | SPEC_SHEET §3 + WRITEUP/limitations-and-future-work.md | docs/research/datasets/; corpus language stats |
| §0 Threat | Length cap | tokens | locked-to-modernbert-native-8192 (see ADR-014; refined by ADR-015 single-backbone) | trained backbone ModernBERT-base at 8192 native; reference rungs at their published native caps (ProtectAI 512, LLM-judges 128K+) | SPEC_SHEET §3.3 + §4 | HF tokenizer docs; ModernBERT paper (arXiv:2412.13663) |
| §0 Threat | Truncation policy for inputs > length cap | head / tail / middle / adaptive | locked-to-adaptive-chunked-max-pool (see ADR-014) | head-truncation at training time; adaptive chunked scoring with max-pool aggregation stride=cap//2 at eval time; mandatory chunked-vs-head ablation on BIPIA slice; Phase 1 validation checkpoint at 15-percent BIPIA-outlier threshold | SPEC_SHEET §3.3 + WRITEUP/truncation-ablation.md | HF tokenizer truncation docs; docs/research/attacks_defenses/02_attack_indirect.md (Greshake 2023) |
| §1 Data | Source selection | dataset list | locked-to-Path-alpha (see ADR-016) | 4 train-positive sources + 2 train-benign sources (LMSYS + UltraChat) + 5 OOD slices; HarmBench + Tensor Trust + LLMail-Inject deferred to afterword | SPEC_SHEET §3.1 + data/source_manifest.yaml | docs/research/datasets/; HF dataset cards |
| §1 Data | HF dataset revision pinning | pin SHAs / lockstep / `revision="main"` | locked-to-SHA-pin-manifest-documented-bumps (see ADR-016) | HF + git SHA pin at Phase 1 entry; manifest-documented bumps; ADR per bump only on schema change | data/source_manifest.yaml | HF datasets revision docs |
| §1 Data | Dedup encoder + threshold | n-gram / MiniLM / MPNet / hybrid; threshold | locked-to-MiniLM-L6-v2-cosine-0.80-simplified-calibration (see ADR-016) | label-aware; simplified FPR+FNR on 50-pair holdout; MPNet + 4-gate rule in afterword | evals/dedup_calibration.json + SPEC_SHEET §3.3 | eval-toolkit methodology/text_dedup.md; sentence-transformers docs |
| §1 Data | Cross-source benign dedup ordering | before-split / after-split | locked-to-within-then-cross-source-LMSYS-priority-before-split (see ADR-016) | within-source-first then cross-source with LMSYS-priority tiebreak; before LODO split per ADR-008 direction | SPEC_SHEET §3.3 | eval-toolkit methodology/leakage.md |
| §1 Data | Splits structure | single / k-fold / source-disjoint LODO / hybrid | locked-to-LODO-k=4-plus-3-seeds-no-internal-k-fold (see ADR-016) | 4 LODO outer folds + 3 seeds = 12 obs per rung = 36 runs total; stratified-k-fold-within-LODO in afterword | SPEC_SHEET §3.2 | Fomin 2025; eval-toolkit methodology/splits.md |
| §1 Data | Reference-scorer audit for partial disclosure | fold pattern / scope cross-check / same-style ablation / all-three | locked-to-fold-pattern+scope-cross-check (see ADR-016) | option B (A+B) for Lakera + ProtectAI; cross-source same-style ablation (option C) in afterword | EVIDENCE.md §1-2 + WRITEUP/reference-scorer-audit.md | docs/research/attacks_defenses/; eval-toolkit leakage docs |
| §1 Data | Benign subsample ceilings per source | open budget / per-source caps | locked-to-3K-pos-per-source-10K-benigns-per-source-seed-42 (see ADR-016) | mosscap + HackAPrompt capped at 3K each; deepset + Lakera-gandalf use-all post-dedup; LMSYS + UltraChat capped at 10K each; quality-filtered + attack-type-stratified + length-stratified in afterword | data/source_manifest.yaml + SPEC_SHEET §3.1 | docs/research/datasets/; eval-toolkit splits.md (statistical power) |
| §2 Model | Backbone choice | DeBERTa-v3 / ModernBERT / both / other | locked-to-ModernBERT-base (see ADR-015 supersedes ADR-007) | single-backbone eliminates per-backbone-truncation confound on indirect zero-shot OOD slice; ProtectAI deberta-v3 retained as reference rung at native config | SPEC_SHEET §4 + WRITEUP/methodology.md | HF model cards; ModernBERT paper (arXiv:2412.13663) |
| §2 Model | Training-time scope | full FT / LoRA / both / frozen-only | locked-to-frozen-probe+LoRA+full-FT-plus-classical-floor (see ADR-017 complements ADR-015) | three transformer conditions uniform per ADR-015 + TF-IDF+LR classical floor rung added per Phase 0-03 Q1b; total 4 trained rungs | SPEC_SHEET §4.1-§4.4 | LoRA paper (Hu et al. 2021, arXiv:2106.09685); PEFT docs |
| §2 Model | Frozen-probe role | candidate detector / diagnostic rung / both | locked-to-both-candidate-detector-plus-diagnostic-anchor (see ADR-017) | dual role; headline-table row alongside LoRA + full-FT AND lift-delta-chain anchor in methodology spoke | SPEC_SHEET §4.2 + WRITEUP/methodology.md | eval-toolkit methodology/comparison.md; Tenney et al. 2019 BERT-rediscovers-pipeline |
| §2 Model | Matched-budget controls | yes / no / per-axis | locked-to-per-axis-match-data-and-eval-not-compute (see ADR-018) | match data + eval methodology; training compute reported as Pareto axis; handles heterogeneous LLM-judge/GPU/inference-only cost classes | SPEC_SHEET §4 + WRITEUP/methodology.md | Hooker 2021 Hardware Lottery (arXiv:2009.06489); HF PEFT comparative study |
| §2 Model | Reference scorer selection | which off-the-shelf models, if any | locked-to-gpt-4o-2024-08-06+claude-sonnet-4-6+protectai-v1-and-v2-drop-lakera (see ADR-018 partially supersedes ADR-015) | 4 reference rungs at stratified contamination levels; Lakera deferred to afterword; ProtectAI v1+v2 for internal lift comparison | SPEC_SHEET §4.5 + WRITEUP/reference-scorer-audit.md | Zheng et al. 2023 (arXiv:2306.05685); OpenAI deprecation policy; ProtectAI v2 model card |
| §2 Model | LoRA epoch policy | 1ep / 2ep / 3+ / early-stop | locked-to-2-epochs-uniform-with-per-epoch-prediction-save (see ADR-019) | 2 epochs uniform across 3 transformer rungs; per-epoch parquet predictions saved; epoch-2 headline, epoch-1 diagnostic | SPEC_SHEET §4.2-§4.4 + WRITEUP/methodology.md | LoRA paper; Mosbach 2021 (arXiv:2006.04884) |
| §2 Model | LoRA precision policy | bf16 / fp16 / fp32 | locked-to-bf16-training-and-inference-with-fp32-softmax-cast (see ADR-019) | bf16 default for H100; fp32 cast before final softmax; ModernBERT pretrained with bf16 per Warner 2024 | SPEC_SHEET §4 | Kalamkar 2019 bfloat16 study (arXiv:1905.12322); ModernBERT paper (arXiv:2412.13663) |
| §2 Model | LoRA class-weight implementation | sklearn-style / HF-Trainer-style / uniform | locked-to-sklearn-style-balanced-uniform-across-trained-rungs (see ADR-019) | uniform sklearn class_weight balanced across all 4 trained rungs; per-fold recomputed; aligns with ADR-017 Q1b | SPEC_SHEET §4 | sklearn class_weight docs; King and Zeng 2001 |
| §2 Model | Compute budget | GPU class + time per rung | locked-to-runpod-deploy-0.7.7-gpu-failover-plus-adaptive-batch-plus-dual-layer-cost-cap (see ADR-020) | 8-class gpu_order failover + dual-DC + BATCH_TABLE preserving effective-batch-32 + flash-attn-2 fallback + budget.cost_cap_usd 125 soft + scripts/cost_rollup.py hard 200 | configs/runpod/headline.yaml + SPEC_SHEET §4 | runpod-deploy 0.7.7 docs (config-reference + recipes); RunPod pricing |
| §3 Eval | OOD slate | slice list | locked-to-pooled-headline-plus-per-slice-spoke (see ADR-021) | 5 OOD slices from ADR-016 reported in two views — pooled-OOD column in PDF exec headline + 5-by-rung grid in WRITEUP/ood-analysis.md spoke; hub-and-spoke ADR-004 framing applied to OOD | SPEC_SHEET §3.4 + §5.1 | Demsar 2006 JMLR; docs/research/benchmarks/03_benchmark_hard_negative.md |
| §3 Eval | Bootstrap N | 10K / 100K / both | locked-to-10K-bootstrap-with-second-seed-stability-check (see ADR-022) | 10K @ seed=1 headline + 10K @ seed=2 stability check; >5% half-width flag; joblib parallelization on 64-core Threadripper at orchestrator layer (library-first preserved) | SPEC_SHEET §5.2 + scripts/run_bootstrap_battery.py | Efron 1979; DiCiccio-Efron 1996; eval-toolkit bootstrap.py |
| §3 Eval | Multi-comparison correction | BH-FDR / Bonferroni / none | locked-to-no-formal-correction-with-Gelman-Loken-acknowledgment-paragraph (see ADR-022) | Estimation-over-testing ratified from ADR-006; WRITEUP/methodology.md gains "family of comparisons" acknowledgment paragraph citing Gelman-Loken 2014 forking-paths + ASA 2016 statement | SPEC_SHEET §5.2 + WRITEUP/methodology.md | Gelman-Loken 2014; ASA 2016 statement; Benjamini-Hochberg 1995 (not applied) |
| §3 Eval | Recall@FPR pinpoints | {0.1%, 1%, 5%} / {1%, 5%} / other | locked-to-{0.1pct-pooled-only-plus-1pct-plus-5pct}-with-bootstrap-volatility-surfacing (see ADR-021) | ADR-006 triad ratified; 0.1% pinpoint pooled-only (per-slice n too small); 4 volatility surfaces on 0.1% (half-width col + flag marker + resample-degeneracy audit + per-resample threshold-drift dump) | SPEC_SHEET §5.1 + WRITEUP/methodology.md | PromptShield 2024-2025; InjecGuard 2024 (arXiv:2410.22770); Davis-Goadrich 2006 |
| §3 Eval | Calibration battery composition | ECE equal-mass / debiased / Brier / reliability bins | locked-to-raw-plus-temperature-plus-isotonic-with-ECE-equal-mass-and-Brier-headline-plus-full-spoke-battery (see ADR-023) | Headline: ECE-equal-mass(n_bins=15, quantile) + Brier on raw scores per rung; Spoke: 4-ECE matrix + Brier-decomp + reliability diagrams + temperature+isotonic intervention deltas | SPEC_SHEET §5.1 + WRITEUP/calibration.md | Kumar 2019 (arXiv:1909.10155); Guo 2017 (arXiv:1706.04599); eval-toolkit methodology/calibration.md |
| §3 Eval | Multi-seed protocol | count + values + paired-across-rungs | locked-to-3-seeds-paired-across-rungs-with-gap-honest-defaults (see ADR-022) | ADR-006 3-seed floor ratified; trained 12 obs (4 folds × 3 seeds) vs reference 4 obs (4 folds × no seed); row-level pairing trained-vs-trained; per-row replication of reference scores trained-vs-reference; rank-based metrics per-(fold,seed)-then-mean; per-row metrics pool; threshold per-(seed); calibrator per-(rung,fold,seed) | SPEC_SHEET §3.2 + §5.2 + ADR-022 + ADR-023 | Bouckaert 2003 ICML; eval-toolkit paired_bootstrap_diff |
| §3 Eval | Paired-test method | paired bootstrap / DeLong / McNemar / combo | locked-to-paired-bootstrap-diff-with-multi-source-LODO-rejection-rationale (see ADR-022) | eval-toolkit paired_bootstrap_diff (Efron-Tibshirani 1993 §10.3 row-level pairing) ratified; DeLong + McNemar + Cochran-Q rejected at row level with multi-source-LODO-specific rationale | SPEC_SHEET §5.2 + WRITEUP/methodology.md | DeLong et al. 1988 (the test we are not using); Efron-Tibshirani 1993 |
| §3 Eval | Cross-fold CI methodology | bootstrap-per-fold / CV-CLT (Bates 2024) / Nadeau-Bengio | locked-to-cv_clt_ci-headline-plus-block-bootstrap-on-folds-spoke-plus-conditional-stratified-k-fold (see ADR-024) | eval-toolkit cv_clt_ci (Bayle 2020 ImplementationTheorem 3.1) on 12 (fold, seed) per-rung values as headline; block-bootstrap-on-folds spoke ablation addressing LODO non-exchangeability; sensitivity flag when block-bootstrap/cv_clt halfwidth ratio > 1.5; stratified-k-fold-within-LODO conditional escalation if Phase 4 compute budget permits (~$75 cumulative threshold); Bates 2024 + Nadeau-Bengio explicitly deferred to afterword | SPEC_SHEET §5.2 + WRITEUP/methodology.md + assumptions.md A-008 | Bayle et al. 2020 Annals of Statistics; Bates et al. 2024 JASA; Nadeau-Bengio 2003; Politis-Romano 1994 (block bootstrap); eval-toolkit cv_clt_ci |
| §4 Threshold | Cost-weight targets | FPR / FNR percentages | locked-to-symmetric-1pct-with-honest-feasibility-reporting (see ADR-025) | Detection FPR ≤ 1% via TargetFPRSelector(0.01); Verification FNR ≤ 1% (recall ≥ 99%) via TargetRecallSelector(0.99); per-(rung, fold, seed) fitting on validation; trained rungs only; 96 threshold-pair instances total; paired_bootstrap_op_point_diff two-level CI propagation; +1 headline column "FPR @ recall ≥ 99%" (verification); detection-policy column relabel-in-place footnote on existing R@FPR=1%; full grid + 3 deployment scenarios + verification reachability subsection in WRITEUP/threshold-policy.md spoke; honest infeasibility reporting (asterisk + audit JSON evals/audit/verification_reachability.json) | SPEC_SHEET §5.1 + §5.3 + WRITEUP/threshold-policy.md + assumptions.md A-009 | eval-toolkit methodology/thresholds.md; Lipton-Elkan 2014; PromptShield 2024-2025; InjecGuard 2024 |
| §5 Code | Module layout | project-specific | locked-to-concern-grouped-subpackages-under-src (see ADR-026) | src/{data, training, scoring, eval, utils}/ + scripts/ + configs/{runpod, rungs, profiles, data}/ + tests/{conftest, test_invariants, fixtures/, unit/, smoke/, integration/}; src/ is library code (importable, no side effects), scripts/ is entrypoint glue (argparse + IO), configs/ is YAML data, tests/ is verification; adding a new top-level src/ sub-package post-lock requires superseding ADR | SPEC_SHEET §6 + tests/test_invariants.py | eval-toolkit src layout; Python packaging guide; src-layout rationale |
| §5 Code | Smoke vs canonical separation | profile-switch / two-targets / three-tiers | locked-to-three-makefile-targets-stratified-by-execution-context (see ADR-027) | (1) make smoke = pytest -m smoke + fixture-data E2E pass (laptop only, no GPU/network, <10 min); (2) make test-integration = pytest -m integration GPU-aware (uses CUDA if present, skips gracefully otherwise) — same target serves local-GPU dev debugging AND cloud-pod pre-flight; (3) make headline-cloud wraps runpod-deploy validate+dry-run+run (canonical evaluation deliverable, NOT a test, cost-cap-gated $125/job per ADR-020); honest debugging-grade-here-rigorous-upstream framing required in WRITEUP/methodology.md (math rigor lives upstream in eval-toolkit) | SPEC_SHEET §6 + Makefile + WRITEUP/methodology.md | eval-toolkit Makefile; runpod-deploy CLI; pytest skipping docs |
| §STYLE | Coverage floor | 70% / 80% / 90% / no floor | locked-to-70pct-flat-with-upstream-issue-filing-discipline (see ADR-028) | 70% flat across repo via `uv run pytest --cov --cov-fail-under=70 --cov-report=term-missing`; co-locked process commitment — coverage gaps better addressed upstream (eval-toolkit / runpod-deploy primitive testing) get filed as upstream issues per `decisions/upstream_issues.md` with `[test-coverage-gap]` tag rather than absorbed as low-value local tests; gaps that genuinely cannot be filed upstream get either tested locally OR documented as `[not-applicable]` deferral | STYLE.md + Makefile + decisions/upstream_issues.md | pytest-cov docs; eval-toolkit STYLE.md |
| §STYLE | Test marker strategy | which of: unit / smoke / integration / network / golden / property | locked-to-four-marker-ratification (see ADR-029) | exactly 4 markers — unit / smoke / integration / network — registered in both pyproject.toml `[tool.pytest.ini_options]` AND tests/conftest.py via pytest_configure addinivalue_line (must stay in sync — invariant test enforces); --strict-markers enabled; property + golden + slow + gpu explicitly NOT added (math rigor lives upstream per ADR-027; conditional-skip idioms handle GPU-gating); marker-add or marker-remove post-lock requires superseding ADR | STYLE.md + pyproject.toml + tests/conftest.py + tests/test_invariants.py | pytest marker docs; eval-toolkit STYLE.md |
| §Submission | PDF bundle composition (semantically replaced by Quarto site composition per Phase 0-07 Q1 pivot) | which docs concat into the deliverable PDF | locked-to-quarto-html-via-gh-actions (see ADR-030 + ADR-031) | repo-only with Quarto-rendered HTML site via GH Actions; no PDF; index.qmd entry-point + sidebar nav surfaces 8 spokes + decisions/ ADRs; reviewer URL pinned at submission tag per ADR-033 | ADR-030, ADR-031 | Quarto websites docs; Quarto GH Pages publish; quarto-actions |
| §Submission | HF Hub checkpoint publication | yes / no / which scorers | locked-to-publish-headline-rungs-only-with-model-card-discipline (see ADR-032) | publish 2-4 primary headline rungs only (frozen-probe + LoRA + conditionally full-FT + conditionally TF-IDF+LR); BBehring/prompt-injection-<rung> naming; model card schema (license + tags + datasets + model-index + intended use + limitations + citation); mechanical generation via scripts/generate_model_cards.py at Phase 5; reference scorers (per ADR-018) NOT republished | ADR-032 | HF Hub model upload + model cards docs |
| §Submission | GitHub release strategy | tag-at-submission only / multiple tags during Phase 1+ | locked-to-rehearsal-plus-submission-plus-patches (see ADR-033) | v0.9.0-rc1 rehearsal (end Phase 4) + v1.0.0 submission + optional v1.0.x post-submission patches; SemVer 2.0.0; CHANGELOG.md per Keep-a-Changelog 1.1.0; GH release v1.0.0 carries CHANGELOG + _site.tar.gz; reviewer email = 3 URLs (source pin + live site + GH release) | ADR-033 | SemVer.org; Keep-a-Changelog; GH releases docs |
| §Submission | Reproducibility tier | laptop-only smoke / GPU-rental canonical / both | locked-to-full-ladder-T0-T1-T3 (see ADR-034) | T0 eval-from-hub (laptop ~$0 ~10-30 min; verifies headline scores on published checkpoints per ADR-032) + T1 smoke (laptop ~$0 ~10 min; code health only) + T3 headline-cloud (cloud-GPU ~$125 ~hours; full retraining per ADR-020 cost cap); T2 stays developer-tool; ladder documented in WRITEUP/reproducibility.md spoke (per ADR-031); maps onto ACM artifact-badging convention | ADR-034 | ACM artifact badging; runpod-deploy reproduction; HF Hub offline-mode |
| §6 Verify | Project-specific acceptance criteria | … | open | | | inline §6 |
| §6 Verify | Compute cost cap | strict / soft / none + dollar amount | open | | | RunPod pricing; project budget |

### `§Kit-Ratify` — kit-level defaults to affirm or override at Phase 0

These rows surface kit-level defaults that the project should explicitly affirm or override at Phase 0. Each was locked at kit-creation time and is documented in spec text + `CLAUDE.md` / `AGENTS.md`; the rows here exist so a Phase 0 walker sees the kit's opinion and consciously ratifies or overrides via a new ADR. **Rapid-ratify path**: in the Phase 0-00 brief-alignment closing step, the project may "accept all kit defaults" as one bulk decision if no override is needed.

| Section | Decision | Options | Status | Rationale | Recorded in | Reference anchors |
|---|---|---|---|---|---|---|
| §Kit-Ratify | Phase 0 strictness | all [OPEN] resolved (default) / high-med only / iterative | locked-to-all-OPEN-resolved (see ADR-013) | discipline floor matches CLAUDE.md anti-pattern on untracked methodology | ADR-013 | `docs/ROADMAP.md` §Phase 0 close criterion |
| §Kit-Ratify | Brief-intake protocol | live Phase 0-00 sub-session (default) / pre-read / async-issues | locked-to-live-phase-0-00 (see ADR-013) | transcript captured for ADR linkage | ADR-013 | `docs/ROADMAP.md` §Phase 0-00 |
| §Kit-Ratify | Repository visibility | public from start (default) / private-then-public / mixed | locked-to-public (see ADR-003) | re-affirms §Brief Q3 lock | ADR-003 | `.gitignore`; `SPEC_STRATEGY.md` |
| §Kit-Ratify | Notebook format | jupytext-paired (default) / pure `.ipynb` / no notebooks | locked-to-jupytext-paired-illustrative-only (see ADR-013) | notebooks load precomputed artifacts; GPU runs are scripts | ADR-013 | `pyproject.toml [tool.jupytext]`; `notebooks/README.md` |

When status changes to `locked-to-X`, fill in **Rationale** and **Recorded in** (ADR number or "inline in spec"). The "Reference anchors" column lists `docs/research/<topic>/` dossier files + external URLs (paper / library doc / methodology guide) that informed the locked choice — populated during `/exploring-options` Phase 0 sub-sessions per the educational-references rule in §Roadmap Phase 0.
