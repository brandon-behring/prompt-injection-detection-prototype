# Assumptions registry

> **How to read this page.** This is an audit registry, not the main narrative. It records
> assumptions that were load-bearing while the project was built. The compact table gives
> the current interpretation; the detail blocks preserve the original historical text.

For the project story, start with [`README`](README.md), [`RESULTS`](RESULTS.md), or
[`WRITEUP`](WRITEUP.md). Use this page when auditing what could have invalidated the
methodology or the submission timeline.

## Severity

- **low** - assumption is a stylistic choice with minimal evidential impact
- **medium** - assumption affects interpretation but does not invalidate conclusions
- **high** - assumption is load-bearing; if false, conclusions need revisiting
- **critical** - assumption is foundational; if false, the project framing changes

## Current-state summary

| ID | Severity | Current state | Current interpretation |
|---|---|---|---|
| A-001 | high | Historical/resolved | Resolved historically; scope was narrowed and the live site now reports the achieved slate rather than the original ambition. |
| A-002 | medium | Historical/resolved | Resolved historically by the cost ledger; cumulative spend stayed within the ADR-020 hard cap and this patch adds no compute. |
| A-003 | medium | Historical/resolved | Historical run-safety assumption; retained to explain why per-row predictions, manifests, and provenance artifacts matter. |
| A-004 | medium | Current caveat | Current interpretation caveat for long-context indirect-injection slices; read beside the OOD and DeBERTa-ablation discussion. |
| A-005 | medium | Current caveat | Current data-audit caveat; conclusions depend on the committed leakage, dedup, class-balance, and contamination audits. |
| A-006 | medium | Current caveat | Current interpretation caveat; reference detectors and pretrained backbones carry unavoidable contamination uncertainty. |
| A-007 | medium | Historical/superseded | Historical LLM-judge caveat; the paid LLM-judge reference rungs were later dropped from the active headline slate. |
| A-008 | medium | Current caveat | Current uncertainty caveat; LODO folds are source-disjoint but not exchangeable, so CI interpretation stays conservative. |
| A-009 | medium | Current caveat | Current threshold caveat; high-recall verification operating points are characterized honestly when unreachable or unstable. |
| A-010 | high | Historical/resolved | Resolved for submission and live-site publishing; retained as historical infrastructure risk for the GitHub Pages path. |
| A-011 | medium | Historical/resolved | Resolved historically by observed RunPod spend; no new GPU work is part of this documentation patch. |
| A-012 | high | Historical/resolved | Resolved historically by completed GPU runs and fallback discipline; no active GPU-stock dependency for this patch. |
| A-013 | high | Current caveat | Partly current reproducibility caveat; Hugging Face availability still matters for artifact reproduction and model-card access. |
| A-014 | high | Historical/superseded | Historical LLM-judge availability caveat; the LLM-judge reference slate was later dropped from current headline results. |
| A-015 | medium | Current caveat | Current reference-rung caveat; ProtectAI availability and training-corpus disclosure affect interpretation of reference detectors. |
| A-016 | high | Historical/resolved | Resolved historical calendar-risk assumption; retained to explain the submission-window fallback discipline. |

## Registry discipline

- Every severity >= medium assumption appears in the WRITEUP caveats block
  or in the current-reader caveat surfaces that superseded it.
- If an assumption is invalidated during implementation, the project writes
  a corrective ADR instead of silently revising history.
- Historical `unverified` means the assumption was not mechanically verified
  at the time it was recorded. The current-state summary above says how to
  read it after the completed v1.x patch series.

## Assumption details

<details id="a-001">
<summary>A-001 - Historical/resolved (high)</summary>

**Current interpretation**

Resolved historically; scope was narrowed and the live site now reports the achieved slate
rather than the original ambition.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-001 + ADR-015 + ADR-017 + ADR-020

**Historical description**

runpod-deploy 0.7.7 + eval-toolkit infrastructure can compress a 4-trained-rung-slate (TF-IDF+LR
classical floor per ADR-017 + ModernBERT-base × {frozen-probe, LoRA, full-FT} per ADR-015) +
3-seed multi-seed + 4-fold LODO + 48-run workload (12 sklearn CPU + 36 H100/equivalent
transformer) + per-epoch prediction save + 4-reference-rung inference + full OOD slate +
paired-bootstrap into ~2.5 working days. Originally framed as 2×3=6 trained rungs per ADR-007;
refined to 1×3 per ADR-015 supersedes ADR-007; expanded to classical-floor + 3-transformer = 4
trained rungs per ADR-017 (classical-floor adds approximately 5 minutes total CPU compute).
GPU-class failover via runpod-deploy `pod.gpu_order` ladder per ADR-020 (8-class failover H100 →
H200 → A100-80G → A100-40G → L40S) plus dual-DC failover (US-MD-1 + EU-RO-1) handles H100
stockout. If false, the updated fallback ladder (transformer rungs 1×3 → 1×2 → 1×1; classical
floor always retained per ADR-017) activates and the writeup honestly reports what was achieved,
not what was attempted.

**Historical notes**

Mid-Phase-2 checkpoint triggers fallback evaluation.

</details>

<details id="a-002">
<summary>A-002 - Historical/resolved (medium)</summary>

**Current interpretation**

Resolved historically by the cost ledger; cumulative spend stayed within the ADR-020 hard cap
and this patch adds no compute.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-007 (revised by ADR-015 + ADR-017 + ADR-018 + ADR-020)

**Historical description**

Total project budget for LLM-judge reference rungs (`gpt-4o-2024-08-06` + `claude-sonnet-4-6`
per ADR-018, both at temperature=0, one call per eval row) plus GPU training compute (3
transformer rungs × 3 seeds × 4 LODO folds = 36 H100/equivalent runs at $3-3.50/hr spot via
runpod-deploy `pod.gpu_order` failover per ADR-020) plus classical-floor sklearn CPU compute (12
runs at near-zero cost per ADR-017) plus reference-rung inference (ProtectAI v1 + v2 GPU
inference per ADR-018; LLM-judge API calls ~$10-12 total for both judges across ~5K eval rows)
lands in the **$25-$125 range**. Per-job orchestrator-enforced soft cap is
`budget.cost_cap_usd=125.0` per ADR-020; project-wide hard cap $200 enforced by
`scripts/cost_rollup.py` CI gate aggregating per-pod manifests + API call logs. If actual cost
exceeds the soft cap (cumulative $125), escalation discussion documented in
`evals/cost_decisions.md` is required before further spend; if hard cap is reached ($200),
superseding ADR documenting extension rationale is required.

**Historical notes**

Verification at end of Phase 3 against cumulative API + GPU cost rolled up in
`evals/cost_ledger.csv`.

</details>

<details id="a-003">
<summary>A-003 - Historical/resolved (medium)</summary>

**Current interpretation**

Historical run-safety assumption; retained to explain why per-row predictions, manifests, and
provenance artifacts matter.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-013

**Historical description**

Pre-teardown persistence checklist is enforced for every RunPod pod before destruction (per-row
predictions + manifests + checkpoints + logs + results.json). If false, a mid-run pod loss
reverts the affected rung and the fallback ladder may activate to recover.

**Historical notes**

Phase 2 entry creates `scripts/pre_teardown_check.sh` (or equivalent) and verifies
runpod-deploy's incremental persistence support.

</details>

<details id="a-004">
<summary>A-004 - Current caveat (medium)</summary>

**Current interpretation**

Current interpretation caveat for long-context indirect-injection slices; read beside the OOD
and DeBERTa-ablation discussion.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-014 + ADR-015

**Historical description**

BIPIA samples with token-length above 8192 (ModernBERT-base native context cap) stay at or below
15 percent of the slice under the ModernBERT-base tokenizer. Per dossier characterization the
rate is approximately 5 percent (3x tolerance). If false, the adaptive-chunked-scoring policy
from ADR-014 becomes load-bearing on the headline indirect-injection slice (not just a
conditional safeguard); a future superseding ADR (ADR-017+) adjusts chunk-stride or aggregation
policy (e.g., hierarchical encoding, learned aggregator, or tighter stride). Note: ADR-014 body
references "ADR-016" as the supersession placeholder; ADR-016 was actually used for Phase 0-02
data design — the truncation-policy supersession path uses the next available ADR number.

**Historical notes**

Phase 1 length-histogram audit produces `evals/length_histograms.{train,ood}.json` with
per-slice quantiles on ModernBERT-base tokenizer.

</details>

<details id="a-005">
<summary>A-005 - Current caveat (medium)</summary>

**Current interpretation**

Current data-audit caveat; conclusions depend on the committed leakage, dedup, class-balance,
and contamination audits.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-016

**Historical description**

The Phase 0-02 data-design locks (ADR-016) depend on the Phase 1 empirical data audit confirming
dossier estimates. Specific invalidation triggers — any one of which fires the superseding-ADR
requirement: (1) benign contamination scan flags >2% of either LMSYS or UltraChat as
injection-template-match (MiniLM cosine >=0.85 to a known injection template); (2) post-dedup
per-LODO-fold training-pool class-balance falls outside 1:3 to 1:10 positive:negative range; (3)
systematic mislabeling detected in any source via spot-check (~50 random samples per source);
(4) actual per-source length distribution diverges materially (5x or more on a percentile) from
dossier estimates.

**Historical notes**

Phase 1 deliverables: `evals/data_audit.{contamination,balance,length,labeling}.json`
operationalize these triggers.

</details>

<details id="a-006">
<summary>A-006 - Current caveat (medium)</summary>

**Current interpretation**

Current interpretation caveat; reference detectors and pretrained backbones carry unavoidable
contamination uncertainty.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-018

**Historical description**

All reference rungs (and the ModernBERT-base backbone used by trained rungs 2-4) carry
uncontrolled training-data leakage relative to our eval slate. Specifically: (1) ProtectAI v1
and v2 disclose only a partial training corpus, which may include eval positive sources
(mosscap, HackAPrompt, etc.); (2) `gpt-4o-2024-08-06` and `claude-sonnet-4-6` are closed corpora
trained on web-scale text that almost certainly includes public injection-detection benchmarks
via crawl; (3) the ModernBERT-base backbone pretrain corpus (`fineweb-edu` + others per Warner
et al. 2024) may include eval sources via web crawl. Only TF-IDF + LR (trained on our LODO
splits by construction per ADR-017) is `verified_disjoint`. **Reporting consequence**: every
reference-rung headline metric is reported with explicit contamination-state tag per the ADR-005
three-state taxonomy (`verified_disjoint` / `backbone-partial-disjoint` /
`suspected_contamination` / `vendor_black_box`); the WRITEUP methodology spoke includes a
dedicated **Contamination stratification** subsection explaining the four-tier disclosure
gradient (per ADR-018); the trained-rung-vs-reference comparison is framed as "what
trained-from-scratch (TF-IDF+LR anchor) achieves versus what potentially-memorized off-the-shelf
models achieve." **Phase 1 mitigation**: contamination scan via MiniLM cosine between eval set
and known public mirrors of training data provides partial evidence of overlap for ProtectAI;
the scan cannot help for LLM judges (closed corpora).

**Historical notes**

Phase 1 deliverable: `evals/contamination_scan.json` with per-eval-row maximum cosine to known
public training-data mirrors; per-rung contamination-state column in headline-table emit.

</details>

<details id="a-007">
<summary>A-007 - Historical/superseded (medium)</summary>

**Current interpretation**

Historical LLM-judge caveat; the paid LLM-judge reference rungs were later dropped from the
active headline slate.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-022 + ADR-018

**Historical description**

LLM-judge reference rungs (`gpt-4o-2024-08-06` and `claude-sonnet-4-6` per ADR-018) at
temperature=0 are not strictly deterministic across calls. Both OpenAI and Anthropic document
that temperature=0 reduces but does not eliminate non-determinism due to GPU non-determinism,
batched scheduling, multi-region routing, etc. The "single inference per row" treatment in
ADR-022 is a simplification by fiat — reference-rung scores are cached at first call and re-run
only on cache miss; inter-call variance is not measured. If false (i.e., if reference-rung
scores drift materially between cache writes and reads), per-row predictions become
non-reproducible across submission re-runs and the comparison structure (trained-vs-reference
paired bootstrap per ADR-022) could be invalidated. **Phase 1 mitigation**: response cache
stored at `evals/audit/llm_judge_cache/<judge>__<row_hash>.json` with timestamp + temperature +
prompt-template version; re-runs verify cache hit before billing; cache hits checked against
expected hash. **Reporting consequence**: the methodology spoke at
WRITEUP/reference-scorer-audit.md gains a one-paragraph note "Reference-rung scores treated as
single-observations by fiat; inter-call variance not measured."

**Historical notes**

Phase 1 deliverable: cache infrastructure at `evals/audit/llm_judge_cache/`; cache-hit
verification scripted; per-cache-entry timestamp + temperature + prompt-template-version
recorded.

</details>

<details id="a-008">
<summary>A-008 - Current caveat (medium)</summary>

**Current interpretation**

Current uncertainty caveat; LODO folds are source-disjoint but not exchangeable, so CI
interpretation stays conservative.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-024 + ADR-016

**Historical description**

The 4 LODO folds defined by ADR-016 are not exchangeable — each fold holds out a different
positive source (`deepset/prompt-injections` ~500-650, `Lakera/gandalf_ignore_instructions`
~800-1000, `Lakera/mosscap_prompt_injection` 3K cap, `hackaprompt/hackaprompt-dataset` 3K cap)
with 1.5x to 6x size variation and distinct attack styles (classical / Gandalf-CTF / Mosscap-CTF
/ competition red-team). The eval-toolkit `cv_clt_ci` primitive (Bayle 2020 Annals of Statistics
Theorem 3.1) used as the headline cross-fold CI machinery per ADR-024 was derived for
exchangeable k-fold cross-validation; the LODO non-exchangeability is a real assumption
violation. **Reporting consequence**: the methodology spoke at WRITEUP/methodology.md reports
both `cv_clt_ci` CI and block-bootstrap-on-folds CI per rung; if the ratio
`block_bootstrap_CI_halfwidth / cv_clt_CI_halfwidth > 1.5` for any rung, the spoke flags "LODO
non-exchangeability dominates within-fold variance; headline CI may understate uncertainty" —
turning the assumption violation into a named methodology finding. **Phase 4 conditional
mitigation**: if Phase 4 entry cost ledger shows cumulative spend below ~$75 (well below ADR-020
$125 soft cap), escalate to stratified-k-fold-within-LODO (Fomin 2025 / Nadeau-Bengio 2003
variance decomposition; ~5x compute) for full LODO-source-character vs within-source variance
decomposition; else deferred to afterword.

**Historical notes**

Phase 4 deliverable: `evals/audit/cross_fold_ci_audit.parquet` with per-rung headline-CI +
spoke-ablation-CI + sensitivity-flag; conditional stratified-k-fold escalation gated on
`evals/cost_ledger.csv` cumulative state at Phase 4 entry.

</details>

<details id="a-009">
<summary>A-009 - Current caveat (medium)</summary>

**Current interpretation**

Current threshold caveat; high-recall verification operating points are characterized honestly
when unreachable or unstable.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-025 + ADR-013

**Historical description**

The verification-policy operating point locked by ADR-025 (recall ≥ 99% via
`TargetRecallSelector(0.99)` on validation per-(rung, fold, seed)) is rung-dependent and not
guaranteed to be reachable on every (rung, fold, seed) val slice. Reachability can fail when (1)
the PR curve at high-recall regime is too noisy on a small val slice (per-fold val n ≈ 250-1300
rows, especially LODO val with positive sources held out); (2) the model genuinely cannot reach
99% recall on that fold's positives without flagging nearly all benigns (recall plateaus < 99%);
(3) score quantization gaps prevent the achievable recall lattice from containing a point at
recall ≥ 99% even when the limit is approachable. **Reporting consequence**: the audit JSON
`evals/audit/verification_reachability.json` is a load-bearing surface for honest dual-policy
interpretation — every unreachable (rung, fold, seed) cell carries an asterisk in the headline
emit, the audit JSON records `target_reachable: false` plus `achieved_val_recall` plus
`fallback_threshold` plus `fallback_test_fpr`, and the `WRITEUP/threshold-policy.md` spoke gains
a "Verification-target reachability across trained rungs" subsection turning per-rung
reachability rate into a cross-rung comparison artifact. **Phase 5 mitigation pre-commit**: if
reachability is poor on the headline rungs, the persistence pre-commit (per ADR-013 + ADR-025
Q4) enables a one-commit "Recall-floor sensitivity sweep" afterword regenerating verification
operating points at recall floors {95%, 99%, 99.9%} from persisted predictions with zero new
training compute.

**Historical notes**

Phase 4 deliverable: `evals/audit/verification_reachability.json` per-(rung, fold, seed) with
target_reachable + achieved_val_recall + fallback_threshold + fallback_test_fpr; Phase 5
conditional sensitivity sweep at {95%, 99%, 99.9%} recall floors gated on reachability-rate
observations.

</details>

<details id="a-010">
<summary>A-010 - Historical/resolved (high)</summary>

**Current interpretation**

Resolved for submission and live-site publishing; retained as historical infrastructure risk for
the GitHub Pages path.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-030 + ADR-033 + ADR-039 + ADR-040

**Historical description**

GitHub Pages + GitHub Actions free-tier infrastructure (deploy workflow at
`.github/workflows/publish.yml` per ADR-030; `quarto-actions/setup@v2` +
`quarto-actions/publish@v2` actions; `gh-pages` branch serving) remains available through
submission day 2026-05-18. ADR-039 gate 6 verifies "all three reviewer URLs at v1.0.0 resolve"
including the live Quarto site at
`https://brandon-behring.github.io/prompt-injection-detection-prototype/`. If GitHub Pages
experiences a >12-hour outage spanning the submission window, gate 6 fails and submission
verification is blocked. **Phase 5 mitigation**: ADR-033 v0.9.0-rc1 rehearsal tag fires the full
publish pipeline 24+ hours before v1.0.0 submission tag — first-time-CI / GH Pages enablement /
`quarto-actions` action availability all exercised at rehearsal. **Fallback if rehearsal
fails**: fix-forward via new commits + v0.9.0-rc2; if persistent CI failure at rehearsal-tag
time, fallback is to commit `_site/` directly to a `prototype-site` branch and point reviewer
URL at a raw HTML-Preview URL per ADR-030 extension condition.

**Historical notes**

Phase 5 deliverable: v0.9.0-rc1 rehearsal tag fires successfully (verified via `gh run list
--workflow publish.yml`); rehearsal-failure runbook in `docs/REPRODUCIBILITY.md` documents the
raw-HTML-Preview fallback.

</details>

<details id="a-011">
<summary>A-011 - Historical/resolved (medium)</summary>

**Current interpretation**

Resolved historically by observed RunPod spend; no new GPU work is part of this documentation
patch.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-020 + A-002 + ADR-040

**Historical description**

RunPod H100 spot pricing remains stable at the `assumed_hourly_rate_usd=$3.50` estimate locked
by ADR-020 (H100 spot midpoint estimate from runpod-deploy cost-reconciliation recipe). Material
drift above $5/hr would shrink the cost-cap window (ADR-020 per-job soft cap $125; project-wide
hard cap $200) before training completes; cumulative spend could hit the $80 trigger flag
earlier than expected. **Phase 1+ mitigation**: ADR-020 cost-reconciliation recipe specifies
post-first-run rate update — `scripts/cost_rollup.py` compares manifest `gpu_price_per_hour_usd`
vs assumed rate; if actual differs materially (>15% drift), the assumed rate is bumped in
subsequent runs or split per GPU class. **Fallback if drift is sustained**: ADR-001 fallback
ladder (1×3 → 1×2 → 1×1 transformer rungs; classical floor always retained per ADR-017) reduces
training compute scope to fit the cost-cap window.

**Historical notes**

Phase 2 deliverable: `evals/cost_ledger.csv` first-row update against actual
`runpod_deploy_pull_manifest.json` `gpu_price_per_hour_usd` after first billed pod; rate-drift
alert if first-run rate exceeds $4.50/hr.

</details>

<details id="a-012">
<summary>A-012 - Historical/resolved (high)</summary>

**Current interpretation**

Resolved historically by completed GPU runs and fallback discipline; no active GPU-stock
dependency for this patch.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-020 + ADR-001 + ADR-040

**Historical description**

At least one of the 8 GPU classes in ADR-020's `pod.gpu_order` failover ladder (H100 family →
H200 family → A100-SXM4-80GB → A100 80GB PCIe → L40S → A100-SXM4-40GB emergency) is available at
submission-window spot pricing across the 2026-05-15 → 2026-05-18 window. RunPod spot inventory
fluctuates; full exhaustion of H100/H200/A100-80G/L40S would leave only A100-40G (emergency
tier), which may hit OOM at max_len=8192 batch despite BATCH_TABLE scaling. **Phase 2
mitigation**: `runpod-deploy validate --all` preflight + `runpod-deploy run --dry-run` cost
preview detect stockout before billing; ADR-020 dual-DC failover (US-MD-1 + EU-RO-1) doubles the
inventory surface. **Fallback if all 8 classes exhausted**: ADR-001 fallback ladder activates —
rung-count reduction (1×3 → 1×2 → 1×1) preserves the methodology contribution at smaller scale;
classical floor (TF-IDF + LR; sklearn CPU) always retained per ADR-017 as the methodology floor.

**Historical notes**

Phase 2 entry: `runpod-deploy validate --all` plus `runpod-deploy run --dry-run` outputs
persisted at `evals/audit/gpu_preflight_<timestamp>.json`; stockout-induced fallback documented
in `evals/cost_decisions.md` if triggered.

</details>

<details id="a-013">
<summary>A-013 - Current caveat (high)</summary>

**Current interpretation**

Partly current reproducibility caveat; Hugging Face availability still matters for artifact
reproduction and model-card access.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-016 + ADR-032 + ADR-034 + ADR-040

**Historical description**

HuggingFace Hub infrastructure remains available across the submission lifecycle: (a) datasets
remain accessible at pinned SHAs per ADR-016 manifest; (b) license terms don't shift mid-Phase;
(c) `HF_TOKEN` write scope continues to allow ADR-032 model publication; (d) published
`BBehring/prompt-injection-<rung>` model card schema stays backward-compatible; (e) the T0
reproducibility tier per ADR-034 (`make eval-from-hub` via `huggingface_hub.snapshot_download`)
functions for reviewer-side reproduction. HF Hub outage or license/scope change would block
dataset loading (Phase 1) or model publication (Phase 5) or T0 reproducibility
(post-submission). **Phase 1+ mitigation**: ADR-016 SHA pinning + local dataset cache means data
loading is resilient to short-term outages (cache-hit avoids HF Hub round trip); ADR-032 model
publication step runs at Phase 5 close — outage at that moment can be re-attempted up to v1.0.0
tag firing. **Fallback if persistent outage**: dataset loading falls back to local pre-fetched
cache; model publication deferred to post-v1.0.0 patch tag (v1.0.1) per ADR-033 patch-tag
discipline; T0 tier in `WRITEUP/reproducibility.md` notes the deferral.

**Historical notes**

Phase 1 deliverable: local dataset cache at `~/.cache/huggingface/datasets/` (uv handles via
HF_HOME env var if pinned); cache-hit verification at every dataset load; Phase 5 deliverable:
publication-retry loop in `scripts/generate_model_cards.py`.

</details>

<details id="a-014">
<summary>A-014 - Historical/superseded (high)</summary>

**Current interpretation**

Historical LLM-judge availability caveat; the LLM-judge reference slate was later dropped from
current headline results.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-018 + ADR-022 + ADR-040 (supplements A-007)

**Historical description**

LLM judge reference rungs remain callable across the submission lifecycle: `gpt-4o-2024-08-06`
(OpenAI; stable snapshot per ADR-018) and `claude-sonnet-4-6` (Anthropic; date-suffixed snapshot
ID pinned at Phase 1 per Anthropic API docs) snapshots are not deprecated mid-Phase-3 eval
execution. Distinct from A-007 which covers temperature=0 non-determinism: A-014 covers
availability/deprecation specifically. OpenAI has deprecated stable snapshots before (e.g.,
`gpt-3.5-turbo-0301`); if either model is discontinued before Phase 5 close, ADR-018
reference-rung slate loses 2 of 4 rungs, contamination axis (per ADR-005 + A-006) loses 2 of 4
contamination-state cells. **Phase 1+ mitigation**: per A-007 cache infrastructure
(`evals/audit/llm_judge_cache/`), all reference-rung scores are cached at first call;
deprecation mid-Phase-3 invalidates *future* calls but cached scores remain valid for reporting.
**Fallback if mid-Phase deprecation**: superseding ADR (e.g., ADR-NNN) swaps the deprecated
model for its successor snapshot (e.g., `gpt-4o-2024-11-20`); contamination caveat updated in
WRITEUP.

**Historical notes**

Phase 1 deliverable: cache infrastructure persists scores so deprecation invalidates only future
calls; Phase 3 deliverable: `evals/audit/llm_judge_cache/` populated before Phase 4 close so
cached evidence survives deprecation.

</details>

<details id="a-015">
<summary>A-015 - Current caveat (medium)</summary>

**Current interpretation**

Current reference-rung caveat; ProtectAI availability and training-corpus disclosure affect
interpretation of reference detectors.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-018 + ADR-016 + ADR-040

**Historical description**

ProtectAI `deberta-v3-base-prompt-injection` v1 + v2 HF model repos remain public with stable
revision SHAs through the submission lifecycle: (a) repos not deleted, (b) repos not relicensed
(currently MIT/Apache per HF model card; relicensing could block redistribution), (c) pinned
revision SHAs persist if ProtectAI re-trains and overwrites tags. **Phase 1 mitigation**:
ADR-016 manifest SHA-pins both v1 + v2 at Phase 1 entry; HF Hub's revision-pin mechanism
preserves access to the specific commit even after subsequent re-uploads. **Fallback if
persistent unavailability**: 2 reference rungs reduce to LLM-judges-only (OpenAI + Anthropic
remain); contamination axis (per ADR-005 + A-006) loses 2 of 4 cells but retains 2
(`vendor_black_box`); TF-IDF + LR anchor (`verified_disjoint`) unaffected; methodology still
publishable with narrower reference-rung surface. **Severity**: medium not high because other
reference rungs remain and the contamination story preserved via remaining
LLM-judges-and-classical-floor structure.

**Historical notes**

Phase 1 deliverable: `configs/data/source_manifest.yaml` SHA-pins both v1 + v2; local checkpoint
cache via `huggingface_hub.snapshot_download` at Phase 1 entry preserves model weights even if
upstream removed.

</details>

<details id="a-016">
<summary>A-016 - Historical/resolved (high)</summary>

**Current interpretation**

Resolved historical calendar-risk assumption; retained to explain the submission-window fallback
discipline.

**Historical verification status**

unverified

**Linked decisions / evidence**

ADR-001 + ADR-040

**Historical description**

Brandon Behring has approximately 16-20 productive work-hours available across the 2026-05-15 →
2026-05-18 calendar window. A-001 frames the *workload-fits-the-calendar* assumption; A-016
frames the *human-time-underneath* assumption (the load-bearing prerequisite for A-001). If
Brandon becomes unavailable for >8 contiguous hours unexpectedly (illness, emergency,
unanticipated commitments), the 2.5-day calendar from Phase 0-00 (2026-05-15) to submission
(2026-05-18) is at risk; ADR-001 fallback ladder reduces *compute* scope (rung-count reduction)
but does NOT reduce human-time required for Phase 5 writeup + ADR-039 submission-readiness gates
+ transcript capture + reviewer-email composition. **No automated recovery primitive** — this is
the only A-XXX assumption without a corresponding ADR-mechanized fallback. **Phase 5
mitigation**: ADR-033 v0.9.0-rc1 rehearsal tag fires at Phase 4 close (~24-36 hours before
v1.0.0 submission tag), providing early signal of work-time pressure; if rehearsal slips by >12
hours, the v1.0.0 tag plus submission email can be deferred to a 2026-05-19 patch window
(acknowledged in submission-readiness sign-off). **Severity**: high (load-bearing on calendar
deadline; no automated fallback) but NOT critical (project-framing-changing) because methodology
contribution is preserved if deadline slips.

**Historical notes**

Phase 0-08 close to v1.0.0 submission: implicit calendar gate; no mechanical verification
artefact (assumption inherently un-testable in CI).

</details>

## Backfill note

[Phase 0-07 (submission deliverables) + 0-08 (tech-stack remainder) + Phase 0 final audit
(ADR-040 cycle 2026-05-16) added 7 new severity-≥-medium assumptions (A-010 through A-016) that
were not surfaced at parent-ADR lock time. The backfill was prompted by a 3-agent meta-audit
(methodology consistency + unstated assumptions + source faithfulness) at user request before
Phase 1 entry. The audit produced 1 actionable finding (this backfill) plus 3 dismissed
false-alarm findings (ADR-015 acceptance_criterion staleness — point-in-time correct per
immutability discipline; Mosbach 2021 citation — defensible per ICLR 2021 publication-year
convention; test-stub count of 39 — exact `^@pytest.mark.skip` matches 39 = 32 ADR-specific + 7
kit-level). Severity calibration per ADR-040: 5 high (A-010, A-012, A-013, A-014, A-016 —
load-bearing without automated recovery) + 2 medium (A-011, A-015 — load-bearing with built-in
recovery primitive). The existing A-001 through A-009 conservative "medium"-only convention
preserved (not retro-calibrated). Phase 0-06 closed with no severity ≥ medium assumptions
because the locked decisions (concern-grouped sub-packages, three-target Makefile
execution-context stratification, 70%-flat coverage floor with upstream-issue-filing escape,
4-marker test taxonomy) are project-internal-discipline contracts whose failure modes are
reviewer-friction or code-organization drift, not methodology validity.]
