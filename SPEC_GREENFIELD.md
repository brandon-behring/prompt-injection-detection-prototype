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
- **Calibration battery** — `reliability_curve`, `fit_temperature`, `fit_isotonic`, ECE variants, Brier score. Cross-link [methodology/calibration.md](https://github.com/brandon-behring/eval-toolkit/blob/main/docs/methodology/calibration.md).
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

> **Decision needed:** module layout within the modelling repo (file names, package structure).

**Configuration discipline** — `[LOCKED]`: all hyperparameters in a versioned YAML config file. An invariant test asserts the config hash is committed; mutating the config requires updating the hash in a git commit.

**Smoke vs canonical eval separation** — `[OPEN]`:

> **Decision needed:** how to separate fast local-laptop smoke tests from full canonical evaluation runs?
> **Options:** (A) single Makefile target with a `--profile=fixtures|full` switch; (B) two distinct targets (`make smoke` for laptop fixtures, `make headline-cloud` for canonical); (C) three tiers (laptop smoke, CPU full, GPU canonical).
> **Considerations:** smoke must run in <10 minutes on a laptop without GPU; canonical must reproduce headline numbers from a published config. The boundary determines what a reviewer can verify locally vs needs cloud access for.
> **Default if unsure:** (B) two distinct targets — `make smoke` (laptop, fixtures profile, ~5 min) and `make headline-cloud` (RunPod, full profile). Per-rung CPU-inference paths for reference scorers can support local-full reproduction of those rungs without GPU.

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
| §Brief | Submission deadline / time budget | calendar date + working days available | open | | | brief itself + project plan |
| §Brief | Deliverable format | PDF / GitHub repo / both / tarball | open | | | brief itself + submission guidelines |
| §Brief | Repo visibility | public / private / mixed (code public + writeup private) | open | | | brief itself; GitHub privacy docs |
| §Brief | Reviewer profile + expected reading time | hiring manager / ML researcher / mixed; 15 min / 1 hr / longer | open | | | brief itself |
| §Brief | Brief-mandated metrics or constraints | enumerated from brief text | open | | | brief itself |
| §Tech-Stack | GPU class | H100 / A100 / consumer GPU / mixed | open | | | runpod-deploy docs; RunPod pricing page |
| §Tech-Stack | Secrets management | env file / vault / cloud secret manager | open | | | runpod-deploy secrets pattern; project policy |
| §Tech-Stack | Dataset cache location | local / shared / cloud | open | | | runpod-deploy cache patterns |
| §Tech-Stack | eval-toolkit version | semver pin | open | | | https://github.com/brandon-behring/eval-toolkit/releases |
| §Tech-Stack | runpod-deploy version | semver pin | open | | | https://github.com/brandon-behring/runpod-deploy/releases |
| §Tech-Stack | research_toolkit version | semver pin | open | | | https://github.com/brandon-behring/research_toolkit/releases |
| §Tech-Stack | Python version pin | >=3.10 / >=3.11 / >=3.12 / >=3.13 | open | | | https://devguide.python.org/versions/ |
| §Tech-Stack | Library-first / hand-rolling | locked: library primitives only; project-specific glue allowed | locked-to-spec | anti-hand-rolling discipline; project glue exception | inline §Tech-Stack | n/a |
| §Tech-Stack | Upstream-issue triage | locked: file issues before workarounds | locked-to-spec | contribution-trail discipline | inline §Tech-Stack + decisions/upstream_issues.md | n/a |
| Roadmap | Phase tailoring | as-is / project-specific tailoring | open | | | inline §Roadmap |
| §0 Threat | Attack classes in scope | direct / direct+indirect / direct+adversarial / custom | open | | | docs/research/attacks_defenses/; OWASP LLM Top 10 |
| §0 Threat | Language scope | English-only / multilingual | open | | | docs/research/datasets/; corpus language stats |
| §0 Threat | Length cap | tokens | open | | | HF tokenizer docs; DeBERTa/ModernBERT context limits |
| §1 Data | Source selection | dataset list | open | | | docs/research/datasets/; HF dataset cards |
| §1 Data | HF dataset revision pinning | pin SHAs / lockstep / `revision="main"` | open | | | HF datasets revision docs |
| §1 Data | Dedup encoder + threshold | n-gram / MiniLM / MPNet / hybrid; threshold | open | | | eval-toolkit methodology/text_dedup.md; sentence-transformers docs |
| §1 Data | Cross-source benign dedup ordering | before-split / after-split | open | | | eval-toolkit methodology/leakage.md |
| §1 Data | Splits structure | single / k-fold / source-disjoint LODO / hybrid | open | | | Fomin 2025 "When Benchmarks Lie"; eval-toolkit methodology/splits.md |
| §1 Data | Reference-scorer audit for partial disclosure | fold pattern / scope cross-check / same-style ablation / all-three | open | | | docs/research/attacks_defenses/; eval-toolkit leakage docs |
| §2 Model | Backbone choice | DeBERTa-v3 / ModernBERT / both / other | open | | | docs/research/attacks_defenses/; HF model cards; ModernBERT paper (arXiv:2412.13663) |
| §2 Model | Training-time scope | full FT / LoRA / both / frozen-only | open | | | LoRA paper (Hu et al. 2021, arXiv:2106.09685); PEFT docs |
| §2 Model | Frozen-probe role | candidate detector / diagnostic rung / both | open | | | eval-toolkit methodology/comparison.md |
| §2 Model | Matched-budget controls | yes / no / per-axis | open | | | docs/research/attacks_defenses/; cross-architecture-control patterns |
| §2 Model | Reference scorer selection | which off-the-shelf models, if any | open | | | HF model cards for candidate detectors |
| §2 Model | LoRA epoch policy | 1ep / 2ep / 3+ / early-stop | open | | | LoRA paper; PEFT training guides |
| §2 Model | LoRA precision policy | bf16 / fp16 / fp32 | open | | | torch.cuda.amp docs; H100 bf16 throughput note |
| §2 Model | LoRA class-weight implementation | sklearn-style / HF-Trainer-style / uniform | open | | | sklearn class_weight docs; HF Trainer docs |
| §2 Model | Compute budget | GPU class + time per rung | open | | | runpod-deploy pricing; project cost cap |
| §3 Eval | OOD slate | slice list | open | | | docs/research/benchmarks/; docs/research/datasets/ |
| §3 Eval | Bootstrap N | 10K / 100K / both | open | | | eval-toolkit methodology/bootstrap.md; Efron 1979 |
| §3 Eval | Multi-comparison correction | BH-FDR / Bonferroni / none | open | | | eval-toolkit methodology/comparison.md; Benjamini-Hochberg 1995 |
| §3 Eval | Recall@FPR pinpoints | {0.1%, 1%, 5%} / {1%, 5%} / other | open | | | docs/research/benchmarks/; PromptShield 2025 |
| §3 Eval | Calibration battery composition | ECE equal-mass / debiased / Brier / reliability bins | open | | | eval-toolkit methodology/calibration.md; Kumar 2019 (arXiv:1909.10155) |
| §3 Eval | Multi-seed protocol | count + values + paired-across-rungs | open | | | eval-toolkit bootstrap docs; reproducibility-checklist patterns |
| §3 Eval | Paired-test method | paired bootstrap / DeLong / McNemar / combo | open | | | DeLong et al. 1988; eval-toolkit methodology/comparison.md |
| §4 Threshold | Cost-weight targets | FPR / FNR percentages | open | | | eval-toolkit methodology/thresholds.md; PromptShield 2025 |
| §5 Code | Module layout | project-specific | open | | | (project-specific; no external reference) |
| §5 Code | Smoke vs canonical separation | profile-switch / two-targets / three-tiers | open | | | eval-toolkit Makefile patterns |
| §STYLE | Coverage floor | 70% / 80% / 90% / no floor | open | | | STYLE.md; pytest-cov docs |
| §STYLE | Test marker strategy | which of: unit / smoke / integration / network / golden / property | open | | | pytest marker docs |
| §Submission | PDF bundle composition | which docs concat into the deliverable PDF | open | | | brief itself; pandoc/typst docs |
| §Submission | HF Hub checkpoint publication | yes / no / which scorers | open | | | HF Hub upload docs |
| §Submission | GitHub release strategy | tag-at-submission only / multiple tags during Phase 1+ | open | | | Keep-a-Changelog; SemVer.org |
| §Submission | Reproducibility tier | laptop-only smoke / GPU-rental canonical / both | open | | | runpod-deploy reproduction patterns |
| §6 Verify | Project-specific acceptance criteria | … | open | | | inline §6 |
| §6 Verify | Compute cost cap | strict / soft / none + dollar amount | open | | | RunPod pricing; project budget |

When status changes to `locked-to-X`, fill in **Rationale** and **Recorded in** (ADR number or "inline in spec"). The "Reference anchors" column lists `docs/research/<topic>/` dossier files + external URLs (paper / library doc / methodology guide) that informed the locked choice — populated during `/exploring-options` Phase 0 sub-sessions per the educational-references rule in §Roadmap Phase 0.
