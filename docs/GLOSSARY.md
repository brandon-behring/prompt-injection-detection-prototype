# Glossary

Project-specific terminology, alphabetized. **This is a living document — it expands as work continues.**

> **Convention**: when a new project-specific term is introduced in any spec / writeup / ADR / transcript / dossier file, add an entry here within the same commit (or as a follow-up `docs: glossary +<term>` commit). The anti-pattern *"Introducing a project-specific term without adding it to docs/GLOSSARY.md"* is in CLAUDE.md.

## Canonical terminology conventions (added at v1.2.0 per ADR-064 §C1)

Some terms have a prose-form vs identifier-form split (e.g., `chunk-and-average` in prose vs `chunk_and_average` as the YAML config / code identifier). The split is deliberate; this table is the canonical reference so contributors and readers can resolve any ambiguity:

| Term cluster | Prose form (reviewer-facing) | Identifier form (code / YAML / file path) |
|---|---|---|
| Detector ladder | **detector** (reviewer-facing prose; the noun for what we evaluate) | `frozen_probe` / `lora` / `full_ft` / `tfidf_lr` (rung-config-file basenames in `configs/rungs/`). Older ADRs (ADR-007 onwards) use "rung" — see the [Rung / detector clarifier](#rung--detector-clarifier) below. |
| Truncation strategy | **chunk-and-average** / **head-truncation** (hyphenated prose) | `chunk_and_average` / `head_truncation` (snake_case Python identifier) |
| Full fine-tune | **full-FT** (capitalized acronym; matches "LoRA"-style capitalization) | `full_ft` (snake_case) |
| Frozen probe | **frozen-probe** (hyphenated prose; matches the prose triad "frozen-probe / LoRA / full-FT") | `frozen_probe` (snake_case) |
| ProtectAI reference scorers | **ProtectAI v1**, **ProtectAI v2** (space + version) | `protectai-v1`, `protectai-v2` (kebab-case lowercase) |
| Out-of-distribution | **out-of-distribution (OOD)** on first use; **OOD** thereafter | N/A |
| Leave-one-dataset-out | **leave-one-dataset-out (LODO)** on first use; **LODO** thereafter | N/A |
| Pooled OOD | **pooled OOD** in body prose; **Pooled OOD** in column/row headers (APA convention) | `pooled_ood` (per-cell parquet `slice_name`) |
| Source / slice display | **BIPIA**, **InjecAgent**, **JBB-Behaviors**, **XSTest**, **NotInject**, **HackAPrompt**, **LMSYS** | `bipia`, `injecagent`, `jbb_behaviors`, `xstest`, `notinject`, `hackaprompt`, `lmsys-chat-1m` |
| Metric names | **AUPRC**, **AUROC**, **ECE**, **Brier** (all-caps acronyms) | Same (used directly in column names + filenames) |

## Canonical Quarto callout-note convention (added at v1.2.1 per ADR-065 §C)

Three Quarto callout types are reserved for three specific reader-facing purposes on reviewer-facing markdown surfaces. The convention is documented here so future contributors can resolve any ambiguity by consulting one canonical source:

| Callout type | Purpose | Where used | GitHub blob fallback |
|---|---|---|---|
| `:::{.callout-note}` Summary | **3-5 bullet headline takeaways**, placed at the top of any reviewer-facing markdown spoke directly below the existing back-link + "How to read this spoke" signpost. Bullets distilled from existing `**Result**`-bolded subsection sentences (per ADR-064 §B5 + ADR-065 §C1); each bullet anchored to an existing `**Result**` claim. | Top of all 8 `WRITEUP/*.md` spokes (added at v1.2.1 Commit 4b) | Renders raw `:::` fences visible; styled box appears only on Quarto site (canonical surface per ADR-030) |
| `:::{.callout-tip collapse="true"}` Hyperparameters | **Dense audit-detail content** that the casual reader does not need but the auditor must reach. Specifically: hyperparameter blocks (`r` / `alpha` / `dropout` / `target_modules` for LoRA; `max_features` / `solver` / `class_weight` for TF-IDF; revision SHA + inference settings for reference scorers). Reader sees a summary line + can expand for detail. | `WRITEUP/model-rungs.md` per-detector hyperparameter blocks (added at v1.2.1 Commit 4c) | Renders raw `:::` fences with content expanded (no collapse behavior); acceptable since audit-detail content is preserved either way |
| `:::{.callout-warning}` | **Caveats / limitations / known-narrow-scope reservations** that the reader must NOT miss. Used sparingly. | `WRITEUP/limitations-and-future-work.md` for residual-confound caveats; reference-scorer contamination-tier reservations elsewhere as needed | Renders raw `:::` fences visible |

The Summary callout-note is NOT labeled "TL;DR" — the label "Summary" is used (per ADR-065 §C4 + Q3 round-3 user directive: "TL;DR" carries casual / informal connotation; "Summary" matches the audit-prep tone of the rest of the writeup).

`docs/for-hiring-managers.md` is the only reviewer-facing surface that intentionally adopts first-person voice in the "What does this tell me about how the candidate thinks?" section per ADR-064 §B6's hiring-manager 4-question format; all other callout content uses third-person voice per ADR-065 §D1.

## Ablation

A controlled experiment that removes or varies one factor while holding everything else constant, to isolate that factor's contribution. The DeBERTa-v3-base medium ablation per ADR-060 + ADR-063 tests whether ModernBERT's headline AUPRC advantage comes from its 8192-token native attention window (long context) or from its backbone architecture itself, by training DeBERTa-v3-base (512-token window) with two truncation strategies (chunk-and-average + head-truncation) and comparing per-strategy AUPRC on the same 5-slice OOD eval slate. The v1.1.2 result was a null (both strategies ~0.29 pooled OOD AUPRC) → ModernBERT advantage is **backbone-dominant**, not context-window-dominant. See `RESULTS.md` §1B for the per-strategy headline + interpretation.

## ADR (Architecture Decision Record)

A single locked decision in Michael Nygard format: Status / Context / Decision / Consequences / Alternatives Considered. **Immutable**, with three narrow exceptions (see [Immutability relaxation — three factual-defect classes](#immutability-relaxation--three-factual-defect-classes) below). See `decisions/README.md` for the lifecycle + `decisions/ADR_TEMPLATE.md` for the schema.

## Immutability relaxation — three factual-defect classes

Per [ADR-067](../decisions/ADR-067-immutability-clarification-and-canonical-slug-reference.md) (added at v1.2.2) + [ADR-068](../decisions/ADR-068-immutability-narrow-relaxation-for-broken-external-references.md) (added at v1.2.6) + [ADR-069](../decisions/ADR-069-immutability-narrow-relaxation-for-publisher-url-to-doi-canonicalization.md) (added at v1.2.6): the ADR-immutability rule (CLAUDE.md: *"ADRs are immutable; supersede via new ADR"*) has THREE narrow exceptions covering distinct factual-defect classes:

1. **Cross-reference slug filename typos** (per ADR-067) — a slug pointing at a wrong-but-existing canonical file in `decisions/`. Wrong slug example (cite as broken refs): `decisions/ADR-006-headline-metrics-and-statistical-floor.md` → `decisions/ADR-006-headline-metrics-and-statistical-apparatus.md`.
2. **Broken external references** (per ADR-068) — markdown links pointing at local-filesystem paths (`/home/<author>/...`, `../../../.claude/...`) or aspirational upstream resources (URLs returning 404 from the upstream repo). Cannot resolve on any non-author machine; surfaced by the lychee CI introduced at v1.1.4 but non-functional until v1.2.4.
3. **Publisher-URL → DOI canonicalization** (per ADR-069) — academic publisher landing-page URLs (sage/tandf/jstor/dl.acm) that 403 unauthenticated CI bots may be replaced with `doi.org/<DOI>` equivalents. Same paper; same author-year citation; academic-canonical + bot-friendly identifier.

All three classes MAY be corrected in-place with a commit message citing the relevant ADR + listing per-file corrections. ALL other content (numeric values, methodology decisions, prose, alternatives considered, non-slug frontmatter fields, table content) remains immutable per the existing rule — change requires a superseding ADR. The narrow exceptions do NOT establish a slippery slope; ADR-067 §B + ADR-068 §B + ADR-069 §B explicitly enumerate in-scope vs out-of-scope changes for each class.

## AUPRC

Area under the precision-recall curve. The primary ranking metric in this
project. On imbalanced data, a random ranking scores the positive-class
prevalence, not 0.5. For the pooled out-of-distribution slice (`pooled_ood`),
that random floor is 412 / 1101 = 0.374.

## AUROC

Area under the receiver-operating-characteristic curve. Secondary ranking
metric used for comparison with other work. Its random floor is 0.5, but it can
look optimistic on imbalanced tasks, so AUPRC is the headline metric here.

## AGENTS.md

Vendor-neutral agent-rules file. Mirrors `CLAUDE.md` for non-Claude agents (Codex / Cursor / OpenCode). See `AGENTS.md`.

## Anti-hand-rolling rule

`[LOCKED]` rule in `docs/TECH_STACK.md`: don't reimplement primitives that exist in `eval-toolkit` / `runpod-deploy` / `research_toolkit`. Project-specific glue is allowed; replacing library primitives is not. See also: library-first discipline.

## Brief alignment (Phase 0-00)

First Phase 0 sub-session. User pastes the brief (or key excerpts) into the conversation; `/save-transcript` captures it. Surfaces scope / deliverable / deadline / visibility / reviewer-profile / brief-mandated-metric constraints. Produces ADR-001.

## CHANGELOG

Keep-a-Changelog 1.1.0 format at `CHANGELOG.md`. v0.0.0 = seed; v0.1.0 = Phase 0 complete; v1.0.0 = submission ready (per Q12 versioning lock).

## CLAUDE.md

Auto-loaded by Claude Code at every session start in this repo. Project-level instructions: Phase 0 workflow, library-first discipline, transcript convention, commit discipline, anti-patterns. See also: AGENTS.md (vendor-neutral mirror).

## Confound

A variable that varies along with the variable you're trying to isolate, making it hard to attribute an observed effect to the right cause. In this project: ModernBERT-base (149M params; 8192-token native attention) outperforms DeBERTa-v3-base (184M params; 512-token native attention) on OOD AUPRC. The headline ladder comparison alone is confounded — the gap could be backbone-architectural, context-window-driven, or both. The ADR-060 DeBERTa medium ablation is a **confound-control experiment**: it varies the truncation strategy (chunk-and-average vs head-truncation) within DeBERTa-v3-base to isolate the context-window contribution. The v1.1.2 null result indicates context-window contributes ~nothing, so the headline ladder gap is attributable to backbone architecture. See `WRITEUP/limitations-and-future-work.md` §9.2 for the residual confounds (backbone size; training pretext; tokenizer family) that the ablation does NOT control.

## Constitution (3-file)

Project Constitution split across `docs/MISSION.md` + `docs/TECH_STACK.md` + `docs/ROADMAP.md`. Per the DLAI Spec-Driven Development course's 3-file Constitution pattern.

## ECE (Expected Calibration Error)

Calibration metric. Equal-mass variant + debiased (Kumar 2019). Reported alongside Brier score and reliability curves. See `eval-toolkit` methodology curriculum.

## False Positive Rate (FPR)

The share of benign examples incorrectly flagged as attacks. A 1% FPR target
means at most one false alarm per 100 benign examples. This project evaluates
how validation-tuned FPR targets transfer to held-out sources.

## Educational-references rule

Phase 0 interview discipline: for each `[OPEN]` decision walked, surface (a) concrete explanation, (b) options with pros/cons, (c) **2-3 definitive reference URLs** (paper / library docs / methodology guide), (d) recommendation with rationale. See CLAUDE.md Phase 0 workflow.

## Fresh-investigation rule

Phase 0 interview discipline (stronger version of educational-references): read `docs/research/` dossier files **live at decision time**; do not pre-load assumed candidates from training memory. See CLAUDE.md Phase 0 workflow.

## LODO (Leave-One-Dataset-Out)

Source-disjoint cross-validation. With k positive sources, k-fold LODO holds out each source in turn. Field standard for cross-source generalization per Fomin 2025 ("When Benchmarks Lie"). See `docs/research/datasets/` + `SPEC_GREENFIELD.md` §1 Data row "Splits structure".

## MDE (Minimum Detectable Effect)

The smallest true effect we have the statistical power to detect at α / β targets. Distinguishes "no difference detected" from "no power to detect." `eval-toolkit.mde_from_ci` derives MDE from observed CI width.

## OOD (Out-Of-Distribution)

Test slices that differ from the training distribution. In this submission, the
important OOD shift is **cross-family**: training is direct-injection-heavy,
while the OOD slate includes indirect injection, agentic-flow injection,
jailbreak-style questions, and benign text that looks injection-shaped.

## Pooled OOD

The aggregate OOD slice used for the headline AUPRC result. It combines the
OOD examples that have both positive and negative labels available for AUPRC /
AUROC computation. It has 1101 rows: 412 positive and 689 negative.

## Open / Locked / TBD (marker grammar)

3-token grammar for in-document markers (Q2 lock):

- `[OPEN]` — Phase 0 decision-ledger item; resolved during Phase 0 interview
- `[LOCKED]` — spec freeze; changing requires a superseding ADR
- `[TBD: <prose>]` — evidence pointer / draft prose / numeric value; populated at the named phase

No other tokens. Bare `[TBD]` (no qualifier) is a grammar violation.

## Paired bootstrap

Resampling-based paired-difference CI for rung-vs-rung comparison; accounts for paired-error correlation without parametric assumptions like DeLong's. `eval_toolkit.paired_bootstrap_diff`. See `eval-toolkit` `docs/methodology/bootstrap.md`.

## Phase 0 close criterion

Phase 1 cannot start until: (a) every `[OPEN]` ledger row is `locked-to-X` and references an ADR, (b) SPEC_SHEET has zero `[OPEN]` slots, (c) `assumptions.md` carries every severity-≥-medium assumption surfaced during Phase 0, (d) `tests/test_invariants.py` has skip-marked stubs for every invariant in SPEC_GREENFIELD §5.

## PR-AUC, ROC-AUC, recall@FPR

Headline ranking + operating-point metrics for class-imbalanced binary classification. PR-AUC = area under precision-recall curve. ROC-AUC = area under receiver-operating-characteristic curve. recall@FPR = recall at a specific false-positive-rate pinpoint (e.g., r@1% = recall at FPR ≤ 1%).

## Recall

The share of attack examples correctly caught. High recall means fewer missed
attacks. Recall must be interpreted together with false-positive rate; catching
more attacks by flagging almost everything is usually not useful.

## Rung / detector clarifier

Older ADRs (ADR-007 onwards) refer to the evaluated classifier approaches as **rungs** (decision-tree language from the spec-lock-in conversations). Reader-facing prose in WRITEUP / RESULTS / EXECUTIVE_SUMMARY / README calls them **detectors** (a more familiar noun for someone not steeped in the SDD vocabulary). Both terms refer to the same thing: the 5 evaluated approaches in the headline ladder (TF-IDF+LR; frozen-probe; LoRA; full-FT; reference scorers including ProtectAI v1/v2 + the LLM judges).

The prose-vs-decision-record split is deliberate; see the [Canonical terminology conventions](#canonical-terminology-conventions-added-at-v120-per-adr-064-c1) table at the top of this file for the full mapping. The `WRITEUP/model-rungs.md` filename retains "rungs" as an architectural artifact (renaming would risk ADR-050 anchor breakage); the file's opening paragraph carries the rung↔detector mapping for readers landing on the spoke directly.

## Replanning checkpoint

Inserted after each phase in `docs/ROADMAP.md`: before exiting the phase, audit whether any `[LOCKED]` assumption has been invalidated. If yes: write a superseding ADR, update SPEC_SHEET slot, cascade to WRITEUP §<relevant>, commit `chore: phase-N replan`.

## SDD (Spec-Driven Development)

Methodology where a binding spec drives implementation. Decisions locked before code; ADRs document changes. Tests are invariants. See `SPEC_STRATEGY.md` for the chosen pack-size + alternatives rejected.

## SPEC_GREENFIELD.md

Binding pre-Phase-0 spec. Contains Feature Specs §0-§7 + 50-row decision ledger with reference anchors. Phase 0 walks each `[OPEN]` ledger row via `/exploring-options`.

## SPEC_SHEET.md

Post-Phase-0 fill-in form. Same skeleton as SPEC_GREENFIELD; each `[OPEN]` slot becomes `[LOCKED: X (per ADR-NNN)]` once Phase 0 resolves it. Phase 1 cannot start until SPEC_SHEET has zero `[OPEN]` slots.

## SUBMISSION_AUDIT.md

Claim-status register. **Script-generated from `decisions/ADR-*.md` frontmatter** via `scripts/regenerate_audit.py`. CI hard-gate asserts no drift between ADRs and the audit table. ADRs are the source of truth; SUBMISSION_AUDIT is derived.

## Three-state contamination taxonomy

Reference-scorer training-overlap verdict (encoded in eval-toolkit manifest `contamination_flags` field):

- `verified_disjoint` — training data verifiably disjoint from project sources
- `suspected_contamination` — known overlap with one or more project sources
- `vendor_black_box` — training data not disclosed; audit shifts to fold-pattern + scope-mismatch analysis

See `docs/THREAT_MODEL.md` + `EVIDENCE.md` §1–2 + `docs/MANIFEST_SCHEMA.md`.

## Transcript

Decision-conversation capture at `transcripts/<YYYY-MM-DD>__<slug>.md`. Produced by `/save-transcript <slug>` skill. **Private by default** (gitignored); emailed separately to reviewer at submission time. ADRs reference transcripts by filename; reviewer correlates via emailed bundle.

## Upstream-issue triage protocol

`[LOCKED]` rule in `docs/TECH_STACK.md`: every library gap / bug / feature request is filed to the relevant upstream GitHub repo with the `tracked` label before any local workaround. Ledger at `decisions/upstream_issues.md`.
