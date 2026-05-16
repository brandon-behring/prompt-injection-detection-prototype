---
adr_id: 016
slug: data-design-bundle
title: Data design bundle — source slate, splits, HF pinning, dedup, ordering, ceilings, ref-scorer audit
date: 2026-05-15
status: Accepted
claim_id: CLAIM-016
claim: Phase 0-02 locks seven §1 Data decisions as a single prototype-scoped bundle — (Q1 row 323) source slate Path α retains the ADR-008-vetted positives (deepset plus Lakera-gandalf plus Lakera-mosscap plus HackAPrompt), benigns LMSYS-Chat-1M plus UltraChat, and OOD slate NotInject plus XSTest plus JBB-Behaviors plus BIPIA plus InjecAgent (HarmBench plus Tensor Trust plus LLMail-Inject deferred to afterword as named next-iteration extensions); (Q2 row 327) splits structure is LODO k=4 over positive sources plus 3 seeds equals 12 observations per rung and 36 total trained runs across 3 ModernBERT-base conditions, with within-fold stratified k-fold deferred to afterword as the Fomin-2025-aligned variance-decomposition extension; (Q3 row 324) HF dataset revisions plus GitHub commit SHAs pinned at Phase 1 entry in unified data/source_manifest.yaml; manifest-documented bumps; ADR per bump only on schema change; (Q4 row 325) dedup encoder is all-MiniLM-L6-v2 cosine at threshold 0.80 with simplified Phase 1 calibration evidence on a 50-pair labeled holdout; MPNet-base-v2 plus full 4-gate selection rule deferred to afterword; (Q5 row 326) cross-source benign dedup order is within-source-first then cross-source with LMSYS-priority tiebreak applied before the LODO split per ADR-008 direction; (Q6 row 329) per-source ceilings are 3000 positives per source for mosscap and HackAPrompt and use-all for deepset plus Lakera-gandalf post-dedup, plus 10000 benigns per source for LMSYS plus UltraChat, with random subsample at seed equals 42; quality-filtered HackAPrompt plus attack-type-stratified plus length-stratified subsamples deferred to afterword; (Q7 row 328) reference-scorer audit pattern for partial disclosure is fold-pattern analysis plus stated-scope cross-check on both Lakera Guard and ProtectAI deberta-v3 reference rungs (option B), with cross-source same-style ablation (option C) deferred to afterword. All seven decisions cohere under the prototype framing — clear claim shape with explicit future-work axes named in WRITEUP/limitations-and-future-work.md.
source: SPEC_GREENFIELD.md §1 Data rows 323-329 + Phase 0-02 walk
acceptance_criterion: SPEC_GREENFIELD ledger rows 323/324/325/326/327/328/329 carry locked-to-X (see ADR-016) status; SPEC_SHEET §3.1 source-slate table is populated with all 11 sources and per-source roles plus licenses; SPEC_SHEET §3.2 splits section carries the LODO k=4 plus 3-seed methodology lock; SPEC_SHEET §3.4 OOD slate table is populated with the 5 OOD sources and their roles; assumptions.md carries A-005 new (Phase 1 audit revisit triggers — benign contamination above 2 percent or class-balance outside 1-to-3-to-1-to-10 or per-source labeling-quality systematic mislabeling or length-distribution divergence from dossier estimates triggers superseding ADR); tests/test_invariants.py contains skip-marked stubs test_source_manifest_schema_valid and test_dedup_calibration_persisted and test_benign_contamination_scan_clean; data/source_manifest.yaml is the Phase 1 deliverable that pins all 11 source revisions and licenses plus per-source row counts; evals/dedup_calibration.json is the Phase 1 deliverable that persists per-source plus cross-source cosine distribution histograms plus FPR plus FNR at threshold 0.80 against a 50-pair labeled holdout; WRITEUP/limitations-and-future-work.md spoke contains a prioritized Next Iteration Priorities subsection enumerating the seven afterword extensions.
closing_commit:
references:
  - https://huggingface.co/datasets/deepset/prompt-injections
  - https://huggingface.co/datasets/Lakera/gandalf_ignore_instructions
  - https://huggingface.co/datasets/Lakera/mosscap_prompt_injection
  - https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset
  - https://huggingface.co/datasets/lmsys/lmsys-chat-1m
  - https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k
  - https://huggingface.co/datasets/leolee99/NotInject
  - https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors
  - https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
  - https://arxiv.org/abs/1908.10084
  - https://arxiv.org/abs/2410.22770
  - https://arxiv.org/abs/2311.16119
  - https://arxiv.org/abs/2309.11998
  - https://arxiv.org/abs/2305.14233
  - https://link.springer.com/article/10.1023/A:1024068626366
transcript: transcripts/2026-05-15__phase-0-02__data-design.md
---

# ADR-016: Data design bundle — source slate, splits, HF pinning, dedup, ordering, ceilings, ref-scorer audit

## Status

Accepted (2026-05-15)

## Context

ADR-008 (data scope — public-only sources, hybrid splits, NotInject inclusion) locked the brief-level data-design direction. Phase 0-02 walks the methodology-specifics that ADR-008 deferred — which datasets, what dedup encoder, what split count, what subsample ceilings, what reference-scorer audit pattern. The walk surfaced a load-bearing prototype-scope reframing — under 2.5 working days plus a focused-PDF submission target, methodology depth should exceed methodology breadth, and several originally-considered methodology-extensions (stratified k-fold within LODO, broader direct-OOD coverage, full 4-gate dedup calibration, cross-source same-style ablation) are deferred to a named afterword that prioritizes them as next-iteration work.

A second load-bearing finding from the walk is the **dossier gap on training benigns** — ADR-008 line 31 noted that "a training-benigns slate is not in the dossier" and named plausible candidates (LMSYS-Chat-1M, ShareGPT, UltraChat) without verification. Phase 0-02 surfaces this gap explicitly and resolves it by locking a two-source benign mix (LMSYS-Chat-1M plus UltraChat) with mandatory Phase 1 contamination scan; the gap is named in `WRITEUP/limitations-and-future-work.md` as a methodology-honesty artifact rather than papered over.

A third finding from the walk is **researcher-auditability as a methodology constraint** — surfaced during the Phase 0-01 multilingual-scope discussion and carried into Phase 0-02 — the researcher cannot independently audit non-English samples, which combined with the all-English dossier-vetted eval slices justifies the English-only scope from ADR-014 Q2 and shapes the benign-pool English-filter requirement applied to LMSYS-Chat-1M (which contains some non-English content).

The seven sub-decisions in this ADR are presented as a single bundle because they cohere under the prototype framing — clear claim shape with explicit future-work axes named. Each sub-decision references its individual SPEC_GREENFIELD ledger row.

## Decision

### Q1 — Source slate (row 323) — Path alpha

**Train positives** (4 sources, LODO-rotational):

| Source | HF revision pin location | License | Approx N post-dedup | LODO fold |
|---|---|---|---|---|
| `deepset/prompt-injections` | Phase 1 lock | Apache-2.0 | ~500-650 (use all) | 1 |
| `Lakera/gandalf_ignore_instructions` | Phase 1 lock | MIT | ~800-1000 (use all) | 2 |
| `Lakera/mosscap_prompt_injection` | Phase 1 lock | MIT | ~3000 (cap; see Q6) | 3 |
| `hackaprompt/hackaprompt-dataset` | Phase 1 lock | per dataset card | ~3000 (cap; see Q6) | 4 |

**Train benigns** (2 sources, stratified across folds):

| Source | HF revision pin location | License | Approx N post-dedup | Filter |
|---|---|---|---|---|
| `lmsys/lmsys-chat-1m` | Phase 1 lock | CC-BY-4.0 | ~10000 (cap; see Q6) | English-only language filter applied before subsample |
| `HuggingFaceH4/ultrachat_200k` | Phase 1 lock | Apache-2.0 | ~10000 (cap; see Q6) | None |

**OOD eval slate** (5 slices, never-trained-on):

| Source | Type pin location | License | Approx N | Role |
|---|---|---|---|---|
| `leolee99/NotInject` | HF SHA at Phase 1 | MIT | 339 | OOD hard-neg (over-defense) |
| `paul-rottger/xstest` | git commit SHA at Phase 1 | per repo | 450 | OOD hard-neg (over-refusal) |
| `JailbreakBench/JBB-Behaviors` | HF SHA at Phase 1 | MIT | 200 | OOD mixed (100 harmful plus 100 benign) |
| `microsoft/BIPIA` | git commit SHA at Phase 1 | per repo | per-task | OOD indirect (zero-shot per ADR-014 Q1) |
| `uiuc-kang-lab/InjecAgent` | git commit SHA at Phase 1 | per repo | 1054 | OOD agentic (stretch probe per ADR-010 Bound 2) |

**Afterword extensions** (named in `WRITEUP/limitations-and-future-work.md`):
- HarmBench standard subset (Mazeika et al. 2024, ICML; arXiv:2402.04249) — broader direct-OOD coverage; engagement-level upgrade from ADR-012 "cite + acknowledge" to "replicate"
- Tensor Trust subsample (Toyer et al. 2023, ICLR 2024; arXiv:2311.01011) — human-adversarial-direct diversity at ~1-2K subsample
- LLMail-Inject (Abdelnabi et al. 2025; arXiv:2506.09956) — adaptive email-context indirect

### Q2 — Splits structure (row 327) — LODO k=4 plus 3 seeds; no internal k-fold

**Mechanism**: source-disjoint Leave-One-Dataset-Out at the outer level over the 4 positive sources; for each LODO fold, the in-distribution training pool is 3 positive sources plus the deduped benign pool; the held-out positive source serves as the cross-source test. Within each LODO fold there is a single 80/20 train/val random split (not nested k-fold) — val is used for threshold selection plus calibration fitting plus early-stopping per ADR-011 Guarantee 6 (no adaptive threshold selection on test).

**Variance estimation**: 3 random initialization seeds per LODO fold per trained rung — this is the ADR-006 floor; matches the Path B compute envelope.

**Per-rung total**: 4 LODO folds times 3 seeds equals 12 observations per rung.
**Submission total**: 3 ModernBERT-base trained rungs (frozen-probe, LoRA, full-FT per ADR-015) times 12 equals **36 trained runs**.

**Bootstrap CI mechanics**: per-rung aggregate AUROC is the mean over 12 observations; per-rung CI is bootstrap (10K iterations, BCa marginal) across the 12 (LODO-fold, seed) observations; rung-vs-rung paired-bootstrap differences use the same (LODO-fold, seed) pairing.

**MDE on Delta-AUROC**: approximately 0.03 (typical for n=12 paired observations) — reportable; honestly characterizes prototype precision.

**Afterword extension**: stratified k-fold within LODO (Fomin 2025 plus Nadeau-Bengio 2003 methodology) for proper within-source-variance decomposition — approximately 5x compute multiplier.

### Q3 — HF dataset revision pinning (row 324) — SHA-pin at Phase 1; unified manifest; manifest-documented bumps

**Mechanism**: At Phase 1 entry, each source's revision is pinned in `data/source_manifest.yaml` — HF datasets pin to HF revision SHA; GitHub-cloneable sources pin to git commit SHA. The manifest carries per-source row counts plus license plus role plus pin reference plus bump history.

**Bump policy**: bumps are documented as YAML diff entries in `data/source_manifest.yaml` under `bump_history`. ADR per bump is required only for schema changes (column adds, removes, type changes); label corrections plus content additions plus row removals are manifest-only.

**CI invariant**: `test_source_manifest_schema_valid` (skip-marked stub at Phase 0 close; implemented Phase 1) asserts the manifest parses, contains all 11 sources, each has SHA plus license plus role.

### Q4 — Dedup encoder plus threshold (row 325) — MiniLM-L6-v2 cosine at 0.80; simplified calibration

**Encoder**: `sentence-transformers/all-MiniLM-L6-v2` (~22M parameters, 384-dim embeddings). Within-(source, label) cosine similarity computed pairwise; pairs above threshold are deduplicated by keeping the first occurrence per the SPEC_GREENFIELD deterministic-ordering lock.

**Threshold**: 0.80 — eval-toolkit kit hint default; industry-standard starting point.

**Calibration evidence** (`evals/dedup_calibration.json`):
- Cosine distribution histogram per (source, label) pair — anisotropy sanity check (Ethayarajh 2019)
- FPR plus FNR at threshold 0.80 against a hand-curated 50-pair labeled holdout (positive pairs known near-duplicates; negative pairs known non-duplicates)
- Dedup counts at thresholds {0.75, 0.80, 0.85} for sensitivity

**Afterword extensions**: MPNet-base-v2 encoder upgrade (5x compute); full 4-gate selection rule (FPR plus FNR plus stability plus calibration-curve persistence) with larger labeled holdout (~200-500 pairs).

### Q5 — Cross-source benign dedup ordering (row 326) — within-source-first; LMSYS-priority tiebreak

**Pipeline order**:

1. Load each benign source; apply English-only language filter to LMSYS-Chat-1M; subsample each to ~10K with seed=42
2. Within-source dedup pass: MiniLM cosine at 0.80; per-source first-occurrence retention
3. Cross-source dedup pass: same MiniLM threshold; LMSYS-Chat-1M priority on cross-source near-duplicates (LMSYS is real-user data; UltraChat is synthetic — preserve real-data signal when both score near-duplicate)
4. Split into LODO folds; stratify benign assignment so each LODO fold receives approximately equal share of post-dedup LMSYS plus post-dedup UltraChat

**Rationale**: ADR-008 already locked the before-split direction; this Q5 sub-decision picks within-source-first to preserve per-source first-occurrence determinism and to keep cross-source dedup as a smaller second-pass operation over the within-source-deduplicated pools.

### Q6 — Benign subsample ceilings per source (row 329) — 3K positives per source; 10K benigns per source; random seed=42

**Per-source caps**:

| Source | Cap | Selection |
|---|---|---|
| `deepset/prompt-injections` | None (use all post-dedup, approx 500-650) | All |
| `Lakera/gandalf_ignore_instructions` | None (use all post-dedup, approx 800-1000) | All |
| `Lakera/mosscap_prompt_injection` | 3000 | Random with seed=42 |
| `hackaprompt/hackaprompt-dataset` | 3000 | Random with seed=42 |
| `lmsys/lmsys-chat-1m` | 10000 | Random with seed=42 after English-only filter |
| `HuggingFaceH4/ultrachat_200k` | 10000 | Random with seed=42 |

**Class balance under caps**: per-LODO-fold training pool is approximately 6-8K positives (3 sources of capped approximately 2-3K each) plus approximately 16K benigns (80 percent of post-dedup approximately 20K benign pool) — ratio approximately 1:2 to 1:2.7.

**Afterword extensions**: larger caps (10K mosscap plus 10K HackAPrompt), quality-filtered HackAPrompt (success-metadata filter; sensitivity vs random), attack-type-stratified subsample (preserves HackAPrompt's 29-technique diversity per Schulhoff 2023), length-stratified subsample (balanced length-bucket coverage per Phase 1 length audit).

### Q7 — Reference-scorer audit for partial disclosure (row 328) — fold-pattern plus scope cross-check

**Per-reference-rung audit deliverables** (`EVIDENCE.md` sections 1 plus 2):

**Lakera Guard (closed-source, API)**:
- Stated scope claims from public documentation
- Per-LODO-fold AUROC pattern — observe whether Lakera scores systematically better on fold X (suggesting fold X source is in Lakera training pool)
- Scope cross-check verdict per stated claim: `[VERIFIED|UNVERIFIED|REFUTED]`
- Contamination conclusion documented

**ProtectAI `deberta-v3-base-prompt-injection` (open weights, partial disclosure)**:
- Stated training-data category disclosure from model card ("open-source prompt-injection datasets plus synthetic")
- Per-LODO-fold AUROC pattern — particularly observe whether ProtectAI scores systematically higher on deepset plus Lakera-gandalf folds (likely in its training distribution)
- Scope cross-check verdict per stated claim
- Contamination conclusion documented

**Output**: `WRITEUP/reference-scorer-audit.md` spoke renders per-fold pattern figures plus claim audit verdict; cross-detector fold-pattern correlation matrix flags pairs with r > 0.7 as suggestive of shared training distribution.

**Afterword extension**: cross-source same-style ablation — train a per-attack-style oracle on each reference scorer's likely training distribution and compare; requires per-attack-style sample size and substantial additional training; future-work axis.

### Phase 1 audit revisit triggers (Assumption A-005 new)

The locked source slate plus splits plus ceilings depend on the Phase 1 empirical data audit confirming the dossier estimates. Specific Phase 1 invalidation triggers — any one of which fires the superseding-ADR requirement:

1. **Benign contamination scan**: more than 2 percent of either LMSYS or UltraChat flagged as injection-template-match (MiniLM cosine ≥ 0.85 to a known injection template); — superseding ADR adjusts source mix or filter threshold or substitutes a different benign source
2. **Class-balance**: post-dedup per-LODO-fold training-pool class-balance falls outside 1:3 to 1:10 positive:negative range — superseding ADR adjusts subsample ceilings
3. **Per-source labeling-quality**: systematic mislabeling detected in any source via spot-check (manual audit of ~50 random samples per source) — superseding ADR drops or revises the affected source
4. **Length-distribution divergence**: actual per-source length distribution diverges materially (5x or more on a percentile) from dossier estimates — superseding ADR re-walks Q4 truncation policy (ADR-014) and possibly Q6 length-stratified subsample

`evals/data_audit.{contamination,balance,length,labeling}.json` are the Phase 1 deliverables that operationalize these triggers.

### Afterword commitment

`WRITEUP/limitations-and-future-work.md` spoke contains a prioritized "Next Iteration Priorities" subsection enumerating the seven afterword extensions surfaced by this ADR plus prior Phase 0-01 ADR-014 plus ADR-015 extensions:

1. Within-fold variance decomposition (stratified k-fold within LODO per Fomin 2025 plus Nadeau-Bengio 2003)
2. Broader direct-OOD coverage (HarmBench plus Tensor Trust plus LLMail-Inject)
3. Adaptive red-team probing (GCG plus PAIR plus TAP per ADR-010 Bound 6)
4. Matched-context cross-backbone control or larger backbone variants (ModernBERT-large; matched-context DeBERTa-v3 control)
5. Multilingual extension (per ADR-014 Q2 and ADR-010 Bound 1 — requires native-speaker annotation skill set)
6. Calibration battery extensions (Phase 0-04 baseline plus temperature plus isotonic ablations)
7. Production-deployment integration (runtime classifier-in-loop)

This list is updated forward by future ADRs as new extensions are surfaced or completed extensions are crossed off.

## Consequences

**Positive:**

- Prototype-scoped methodology — clear claim shape with explicit future-work axes; aligns with ADR-005 Principle 1 (methodology over metrics — depth over breadth at this scope) and Principle 3 (structured limitations with extension conditions)
- Bit-reproducibility floor via SHA-pinned source manifest; any reviewer can re-fetch and re-run
- LODO methodology measures cross-source generalization directly; honest about distribution-shift
- Class balance approximately 1:2.7 is deployment-relevant — not so balanced it ignores production reality, not so imbalanced positive signal starves
- Phase 1 audit triggers (A-005) make the source-slate lock empirically falsifiable; revisit path is well-defined
- Researcher-auditability constraint surfaced honestly — English-only filter on LMSYS plus all-English eval slate plus dossier-vetted-English sources align coherently
- Compute fits A-002 envelope ($60-115 total estimated) — well under revised $25-125 envelope (slight stretch to upper bound acknowledged)
- All seven sub-decisions documented in single ADR-016 — reviewer reads one artifact for Phase 0-02 data design; supporting work artifacts (manifest, calibration JSON, audit JSONs, evidence sections) follow from there
- Afterword spoke produces a citable "what's next" artifact; reviewer maps deployment context to extension priorities

**Negative / cost:**

- Loses approximately 99 percent of mosscap plus HackAPrompt content via 3K cap; random subsample may miss rare attack patterns in the discarded portion — explicit limitation; afterword names attack-type-stratified subsample as the extension
- Benign contamination scan is mandatory at Phase 1 entry — if contamination rate exceeds 2 percent in LMSYS or UltraChat, the source-slate lock is invalidated and the supersession path activates (real risk; A-005 medium severity)
- Phase 1 dedup calibration uses a hand-curated 50-pair holdout — small sample; simplified rule rather than full 4-gate; afterword names the upgrade path
- LODO k=4 produces 12 observations per rung; bootstrap CIs have MDE approximately 0.03 Delta-AUROC — honestly characterizes prototype precision; afterword names stratified-k-fold-within-LODO for tighter MDE
- HarmBench (ICML 2024 canonical direct-OOD benchmark) is in afterword rather than slate; reviewer may ask "why not HarmBench?" — answer is prototype scope plus dossier-vetted-OOD-already-covers-direct-attack-class via JBB-Behaviors harmful subset
- Reference-scorer audit option C deferred — same-style ablation is the gold-standard verdict; option B (fold-pattern plus scope cross-check) is suggestive but not dispositive; explicitly framed as such in EVIDENCE.md and the spoke

**Neutral:**

- ADR-008 brief-level locks preserved unchanged; ADR-016 fills in the methodology specifics ADR-008 deferred
- ADR-012 engagement set preserved — HarmBench remains "cite + acknowledge"; afterword commits to upgrading to "replicate" in next iteration
- Phase 0-03 still walks §2 Model rows for backbone-size-specifics plus LoRA hyperparameters plus matched-budget controls plus reference-scorer-model-IDs plus compute budget
- The 2 hard-locked invariants from SPEC_GREENFIELD §1 (label-aware dedup discipline; leakage detection invariant tests) are preserved and surface as Phase 1 invariant stubs

## Alternatives Considered

- **Path gamma — add HarmBench plus Tensor Trust to OOD slate now**: stronger direct-OOD coverage; canonical ICML 2024 benchmark plus human-adversarial diversity. Rejected after prototype-scope reframing because it adds Phase 1 license verification plus dedup plus leakage-scan work for two new sources (~1 full day Phase 1 audit overhead); marginal methodology gain over current 5-source OOD slate for the prototype's claim shape; afterword names both as next-iteration priorities.
- **Stratified k-fold within LODO (Option A from Q2 walk)**: methodologically gold-standard per Fomin 2025 plus Nadeau-Bengio 2003 — proper variance decomposition. Rejected after prototype-scope reframing because 5x compute multiplier (180 runs vs 36 runs) stretches A-002 budget; bootstrap CI shape from 12 observations is adequate for prototype claim precision (MDE approximately 0.03); afterword names this as variance-decomposition extension.
- **LMSYS-only benigns (Q1 option A)**: simpler; single-source. Rejected because single-source benign-feature overfitting risk; Phase 1 LODO would conflate detector capacity with benign-source-feature overfitting.
- **UltraChat-only benigns (Q1 option B)**: simplest license; no contamination risk. Rejected because pure synthetic loses deployment-distribution realism; reviewer asks "did your detector see real user prompts?" with no honest answer.
- **3-source benign mix (Q1 option D — LMSYS plus UltraChat plus OpenAssistant)**: maximum source diversity. Rejected because OpenAssistant adds dedup plus license complexity without clear marginal benefit over LMSYS plus UltraChat mix; afterword can add if Phase 1 reveals class-balance inadequate.
- **Defer benigns selection to Phase 1 (Q1 option E)**: lower commitment now. Rejected because violates Phase 0 close criterion (every [OPEN] resolved or explicitly deferred-to-phase-N with ADR); defer-to-phase-1 lock would itself be the lock so frame it that way.
- **revision="main" no-pinning (Q3 option D)**: simplest. Rejected — explicitly banned by ADR-008 and ADR-011 Guarantee 8 (no untracked methodology components).
- **ADR per HF SHA bump (Q3 option A)**: maximum auditability. Rejected for prototype as paperwork-on-an-irrelevant-axis; bumping HF SHAs is administrative not methodology-substantive; manifest-history captures the audit trail at lower cost; reserve ADR for schema-change bumps.
- **MPNet encoder for dedup (Q4 option C)**: higher-quality semantic embeddings. Rejected because 5x compute cost; near-duplicate detection quality differential is negligible (Reimers 2022); afterword names as upgrade path.
- **n-gram cosine dedup (Q4 option A)**: simplest and cheapest. Rejected because misses paraphrases plus surface-form variants — known weakness for prompt-injection corpora where attackers explicitly paraphrase to evade.
- **Hybrid n-gram plus MiniLM cascade (Q4 option D)**: high recall on duplicates. Rejected for prototype because two thresholds to calibrate plus more complex implementation; single-encoder simplicity preferred.
- **MiniLM-MPNet bake-off per SPEC_GREENFIELD default (Q4 option E)**: empirical evidence drives choice. Rejected because bake-off does not change the prototype-headline result; methodology-paperwork; afterword names as the upgrade path.
- **After-split dedup (Q5 option d)**: rejected by ADR-008 — already banned.
- **Cross-source-first then within-source (Q5 option b)**: rejected because complicates per-source determinism rule.
- **Pool-first single dedup pass (Q5 option c)**: rejected because loses per-source dedup-rate audit.
- **Open-budget no caps (Q6 option A)**: rejected because mosscap plus HackAPrompt would dominate training; LODO measures intra-source rather than cross-source; methodologically broken.
- **Smaller caps approximately 1K positives plus approximately 5K benigns (Q6 option D)**: faster prototype. Rejected because lower per-fold positive count widens AUROC CIs; reduces statistical power for paired-bootstrap rung-vs-rung; MDE may exceed reportable threshold.
- **Quality-filtered HackAPrompt subsample (Q6 option E)**: higher-quality positives. Rejected for prototype because selection bias — "successful" depends on target LLM era; afterword names as sensitivity-analysis extension.
- **Audit option A only (Q7)** fold-pattern only: cheaper but suggestive-only. Rejected because scope cross-check option B is essentially free and produces direct evidence; preferred.
- **Audit option D (all three including C cross-source same-style ablation) per SPEC_GREENFIELD default**: gold-standard. Rejected for prototype because option C requires per-attack-style sample size plus characterization of each reference scorer's likely training-distribution; substantial additional training work; afterword names as the methodology upgrade.

## References

- LMSYS-Chat-1M (Zheng et al. 2023, ICLR 2024) — https://arxiv.org/abs/2309.11998
- UltraChat (Ding et al. 2023, ICLR 2024) — https://arxiv.org/abs/2305.14233
- HF Hub deepset/prompt-injections — https://huggingface.co/datasets/deepset/prompt-injections
- HF Hub Lakera/gandalf_ignore_instructions — https://huggingface.co/datasets/Lakera/gandalf_ignore_instructions
- HF Hub Lakera/mosscap_prompt_injection — https://huggingface.co/datasets/Lakera/mosscap_prompt_injection
- HF Hub hackaprompt/hackaprompt-dataset — https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset
- HF Hub lmsys/lmsys-chat-1m — https://huggingface.co/datasets/lmsys/lmsys-chat-1m
- HF Hub HuggingFaceH4/ultrachat_200k — https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k
- HF Hub leolee99/NotInject — https://huggingface.co/datasets/leolee99/NotInject
- HF Hub JailbreakBench/JBB-Behaviors — https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors
- Sentence-Transformers all-MiniLM-L6-v2 — https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Reimers and Gurevych 2019 "Sentence-BERT" — https://arxiv.org/abs/1908.10084
- Ethayarajh 2019 "How Contextual are Contextualized Word Representations?" (anisotropic embeddings) — https://arxiv.org/abs/1909.00512
- InjecGuard NotInject (Li and Liu 2024) — https://arxiv.org/abs/2410.22770
- HackAPrompt (Schulhoff et al. 2023, EMNLP) — https://arxiv.org/abs/2311.16119
- Nadeau and Bengio 2003 "Inference for the Generalization Error" — https://link.springer.com/article/10.1023/A:1024068626366
- ADR-005 (Principles 1 and 2 and 3 — methodology over metrics, honest evaluation preferred, structured limitations with extension conditions)
- ADR-006 (3-seed floor preserved; paired-bootstrap protocol)
- ADR-007 superseded by ADR-015 (rung architecture)
- ADR-008 (data scope brief-level locks — public-only, hybrid splits, NotInject inclusion)
- ADR-011 (methodology guarantees — leakage scan plus per-row predictions plus threshold-on-validation)
- ADR-012 (engagement set preserved — HarmBench remains cite-and-acknowledge; afterword commits to upgrade)
- ADR-014 (threat-model bundle — Q1 direct-primary plus indirect-zero-shot OOD shapes the BIPIA-as-zero-shot lock here)
- ADR-015 (rung architecture refinement — ModernBERT-base only; references the 3 trained rungs at the 36-run total)

## Transcript

See `transcripts/2026-05-15__phase-0-02__data-design.md` for the conversation that led to this decision.
