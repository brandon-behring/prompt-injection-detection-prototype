---
adr_id: "032"
slug: hf-hub-publication-headline-rungs-only
title: HF Hub checkpoint publication — publish primary headline rungs only with model card discipline
date: 2026-05-16
status: Accepted
claim_id: CLAIM-032
claim: Phase 0-07 locks SPEC_GREENFIELD ledger row 348 (HF Hub checkpoint publication) by publishing the primary headline rungs only (Option C of the Phase 0-07 Q2 walk) — typically 2-4 trained checkpoints corresponding to the rungs the writeup leads with, NOT every ablation rung. Reference scorers (per ADR-018 — protectai/deberta-v3-base-prompt-injection plus the rest of the reference slate) are NOT republished since they are already public artefacts authored by others. The proposed publication set at lock time — final composition revisitable at Phase 5 once the rung ladder settles — is BBehring/prompt-injection-modernbert-frozen-probe (frozen-probe baseline) plus BBehring/prompt-injection-modernbert-lora (LoRA-best rung per ADR-019) plus conditionally BBehring/prompt-injection-modernbert-fullft (full-FT-best rung if promoted to headline status per ADR-019 final composition) plus conditionally BBehring/prompt-injection-tfidf-lr-classical-floor (per ADR-017 classical floor rung if included in headline narrative). TF-IDF + LR rung publication is conditional because sklearn-pipeline serialization to HF Hub is less standardized than transformers checkpoints; Phase 5 work item — assess whether joblib pickle plus a model-card-only repo is sufficient or whether the rung stays unpublished. Naming convention — BBehring/prompt-injection-<rung-name> (lowercase, kebab-case after the prompt-injection prefix). Model cards conform to HF Hub model-card YAML frontmatter schema — license (apache-2.0 inherited from ModernBERT-base) plus tags (text-classification, prompt-injection, safety) plus datasets (HF dataset IDs at the pinned SHAs per ADR-016) plus model-index.results (per-rung headline metrics from results.json with the pooled-OOD column per ADR-021) plus intended use (research and methodology characterisation; NOT production deployment per ADR-005) plus limitations (link back to WRITEUP/limitations-and-future-work.md) plus citation (repo URL at submission tag plus author plus date). Each model card README is generated mechanically from the writeup spokes plus results.json at Phase 5 (not hand-written per checkpoint) via a scripts/generate_model_cards.py orchestrator that takes the published-rung list as input. HF Hub authentication for the publication push uses the standard huggingface_hub token discovery mechanism (env var HF_TOKEN plus ~/.cache/huggingface/token) — secrets management discipline deferred to Phase 0-08. The publication step runs once per rung at Phase 5 close (before the v1.0.0 submission tag per ADR-033) and is gated by the v0.9.0-rc1 rehearsal tag — at least one rung must publish successfully to HF Hub before the rehearsal tag is considered passed. Limitation — published checkpoints can be probed offline for adversarial blind-spot discovery (acceptable for a methodology submission scope per ADR-005; would be unacceptable for a deployed defensive classifier). Extension condition — if the Phase 3 rung ladder produces additional ablation rungs that materially shape the writeup narrative (e.g., a specific rung that demonstrates a critical failure mode), promote that rung into the publication set via Phase 5 ADR amendment without superseding this ADR (the discipline is locked; the exact list is provisional).
source: SPEC_GREENFIELD.md §Submission ledger row 348 + Phase 0-07 walk Q2
acceptance_criterion: SPEC_GREENFIELD ledger row 348 carries locked-to-publish-headline-rungs-only-with-model-card-discipline status (see ADR-032); decisions/library_imports.md notes huggingface_hub as a runtime dependency for the publication step (already noted upstream from ADR-013 and ADR-016 but the publication-side use is new); a placeholder Phase 5 work item is captured in assumptions.md or a Phase 5 checklist file noting that scripts/generate_model_cards.py and the publication push are required before the v1.0.0 submission tag; tests/test_invariants.py contains skip-marked stub test_hf_hub_publication_naming_convention asserting that any published model repo follows the BBehring/prompt-injection-<rung-name> pattern (verified at Phase 5 close via huggingface_hub.HfApi().list_repos with author BBehring filter) plus skip-marked stub test_model_card_schema_complete asserting that each published rung's model card README YAML frontmatter contains the required keys (license, tags, datasets, model-index, intended use, limitations, citation); SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit: 7979dc9
references:
  - https://huggingface.co/docs/hub/models-uploading
  - https://huggingface.co/docs/hub/model-cards
  - https://huggingface.co/answerdotai/ModernBERT-base
  - decisions/ADR-013-kit-ratify-bulk-strictness-intake-notebook-persistence.md
  - decisions/ADR-016-data-design-bundle.md
  - decisions/ADR-018-reference-scorer-slate-and-contamination-stratification.md
  - decisions/ADR-019-lora-and-transformer-training-recipe.md
  - decisions/ADR-005-methodology-principles.md
transcript: transcripts/2026-05-16__phase-0-07__submission-deliverables.md
---

# ADR-032: HF Hub checkpoint publication — publish primary headline rungs only with model card discipline

## Status

Accepted (2026-05-16). Closes the second of 4 [OPEN] rows in Phase 0-07 (§Submission — row 348). Companion to ADR-030 (deliverable format), ADR-031 (reading paths), ADR-033 (release strategy), and ADR-034 (reproducibility tier; T0 tier directly depends on this ADR's published checkpoints).

## Context

ADR-013 (cache location) established HF Hub as the *persistence* sink for trained checkpoints — weights end up on HF Hub regardless of publication choice. Ledger row 348 decides whether those checkpoints are **publicly published** (a `BBehring/<rung>` model repo with a model card, downloadable by anyone) or **kept private** (a `BBehring/private-<rung>` repo, only the maintainer can fetch).

Public publication is asymmetric:

- **Reproducibility unlock**: a reviewer can run `AutoModel.from_pretrained("BBehring/prompt-injection-modernbert-lora")` + an eval pass and verify scores match the per-row predictions in the repo, without re-training. This is the *foundation* of ADR-034's T0 (eval-from-hub) reproducibility tier.
- **Disclosure surface**: a publicly downloadable classifier can be probed offline for blind spots — an attacker could craft adversarial inputs against the *exact* model. For a **methodology submission** (per ADR-005 "deployment is not on the roadmap"), this risk is acceptable; for a deployed defensive classifier, it would not be.
- **Time cost**: each publication = `huggingface_hub` push + a model card README + license/intended-use/eval-results metadata. ~15-30 min per checkpoint done properly.

The rung ladder per ADR-007 + ADR-015 + ADR-017 + ADR-019 includes:
- 1 TF-IDF + LR classical floor rung (ADR-017)
- 3 ModernBERT-base trained rungs: frozen-probe baseline, LoRA, full-FT (ADR-019)
- 4 reference scorers per ADR-018 — already public elsewhere, NOT republished

Four publication options were considered (per Q2 walk):
- (A) No publication; checkpoints private. Defeats T0 reproducibility tier.
- (B) Publish all trained rungs. 4-6× publication time; ablation rungs add maintenance surface.
- (C) Publish primary headline rungs only. ~2-4 checkpoints; bounded time; narrative-aligned.
- (D) Single canonical "best" checkpoint. Contradicts ADR-005 + characterisation framing — picking a single "best" is a deployment recommendation; the methodology refuses to make one.

User selection at Phase 0-07 Q2 walk: **C**.

## Decision

**Publication policy**: publish the primary headline rungs only (2-4 trained checkpoints). Reference scorers per ADR-018 are NOT republished (they are public artefacts authored by others).

**Proposed publication set** (final composition revisitable at Phase 5):

| Repo name | Rung | Status |
|---|---|---|
| `BBehring/prompt-injection-modernbert-frozen-probe` | Frozen-probe baseline (ADR-019) | confirmed |
| `BBehring/prompt-injection-modernbert-lora` | LoRA-best rung (ADR-019) | confirmed |
| `BBehring/prompt-injection-modernbert-fullft` | Full-FT-best rung (ADR-019) | conditional on headline status |
| `BBehring/prompt-injection-tfidf-lr-classical-floor` | TF-IDF + LR (ADR-017) | conditional on sklearn-publication feasibility |

**Naming convention**: `BBehring/prompt-injection-<rung-name>` (lowercase kebab-case after the `prompt-injection` prefix). Stable; reviewer can construct the repo URL from the rung name in the writeup.

**Model card schema** (HF Hub YAML frontmatter; per https://huggingface.co/docs/hub/model-cards):

```yaml
---
license: apache-2.0  # inherited from ModernBERT-base
tags:
  - text-classification
  - prompt-injection
  - safety
datasets:
  - hf-internal-testing/<dataset-id>  # at pinned SHA per ADR-016
language:
  - en
model-index:
  - name: <rung-name>
    results:
      - task:
          type: text-classification
        dataset:
          name: pooled-OOD slate (5 slices per ADR-021)
        metrics:
          - type: AUPRC
            value: <from results.json>
          - type: AUROC
            value: <from results.json>
          - type: recall_at_fpr_1pct
            value: <from results.json>
---
```

Plus markdown body covering: intended use ("research and methodology characterisation; NOT production deployment per ADR-005"), limitations (link to `WRITEUP/limitations-and-future-work.md`), citation (repo URL at submission tag + author + date).

**Model card generation**: mechanical, not hand-written. Phase 5 work item — `scripts/generate_model_cards.py` orchestrator takes (published-rung list, results.json, writeup spokes) as input + emits one model card README per published rung. This keeps the cards in sync with the headline numbers; manual maintenance would risk drift.

**Authentication**: standard `huggingface_hub` token discovery mechanism (env var `HF_TOKEN` + `~/.cache/huggingface/token`). Secrets management discipline deferred to Phase 0-08 (process + tech-stack sub-session) — the *publication discipline* is locked here; the *auth mechanism* is locked there.

**Publication trigger**: publication step runs once per rung at Phase 5 close, **before** the v1.0.0 submission tag per ADR-033. The v0.9.0-rc1 rehearsal tag (per ADR-033) gates submission progression — at least one rung must publish successfully to HF Hub at rehearsal time before the rehearsal tag is considered passed. Catches HF Hub auth + model-card schema issues 24+ hours before the canonical submission tag fires.

**TF-IDF + LR rung publication conditionality**: sklearn-pipeline serialization to HF Hub is less standardized than transformers checkpoints. Phase 5 assesses whether joblib pickle + a model-card-only repo is sufficient or whether the classical rung stays unpublished (with reviewer noted of the gap). Decision deferred — discipline locked; specific format choice for the classical rung TBD-Phase-5.

## Consequences

### Positive

- **Enables ADR-034 T0 reproducibility tier** — published checkpoints are the foundation of the eval-from-hub path; without this ADR, T0 collapses to "trust the per-row predictions in the repo".
- **Contribution-trail value** — public HF Hub model repos demonstrate engineering rigor + portfolio benefit; aligns with kit-level "show your work" framing.
- **Bounded publication time** — ~1-2 hours total for 3 checkpoints (vs ~3-4 hours for option B's 4-6 rungs).
- **Reference-scorer exclusion is correct** — republishing protectai's model under `BBehring/` would be attribution-confusing + license-cascade risky; the reference slate stays at its canonical authors.
- **Mechanical model-card generation** keeps cards in sync with results.json; eliminates hand-edit drift risk.
- **Rehearsal-tag gating** catches HF Hub publication issues at v0.9.0-rc1 (per ADR-033) before the canonical v1.0.0 submission tag fires.

### Negative / cost

- **Disclosure surface** — published classifiers can be probed offline for adversarial blind spots. Acceptable for methodology submission per ADR-005; documented limitation in model card under "intended use".
- **Maintenance surface post-submission** — public model repos can attract issues / questions; need a maintenance posture statement ("research artefact; not actively maintained for production support").
- **Phase 5 work item added** — `scripts/generate_model_cards.py` orchestrator is ~50-100 LOC of glue (load results.json + load spoke YAML frontmatter + emit README per rung). Acceptable cost; smaller than the per-rung hand-written-card alternative.
- **TF-IDF + LR rung publication uncertainty** — sklearn pipeline publication is non-standard. Phase 5 may resolve to "publish via joblib pickle + model card" or "skip this rung's publication". Either is acceptable; the headline rungs (ModernBERT-based) are the load-bearing ones.

### Neutral

- **Final published-rung list** is provisional until Phase 5 — the discipline (publish headline rungs with model card) is locked; the exact list depends on which rungs the writeup leads with after Phase 3-4 analysis.
- **HF Hub org choice**: published under `BBehring` username (per MCP auth context — already authenticated). Optional alternative — create a `ciphero-take-home` org for org-namespaced repos. Not chosen now; would require account-level admin to create the org.

### Limitation

The publication set is small (3-4 rungs) by design. A reviewer who wants to audit an ablation rung that didn't make the headline narrative must re-train via T3 (per ADR-034). This is an explicit trade — the disclosure-surface budget + the publication-time budget caps the published-rung count.

### Extension condition for revisit

- **Headline-rung composition shift**: if Phase 3-4 analysis reveals a non-headline ablation rung carries methodology-interpretation weight (e.g., demonstrates a specific failure mode that's central to the writeup narrative), promote that rung into the publication set via Phase 5 ADR amendment without superseding this ADR. The discipline (publish headline rungs with model card) is locked; the exact list is provisional and revisable.
- **Disclosure-surface concern escalation**: if a Phase 1+ surprise reveals that published checkpoints expose a specific class of adversarial attack the writeup didn't anticipate, switch to option A (no publication; private retention with reviewer-on-request escalation) via superseding ADR. The reproducibility tier (per ADR-034) would then collapse to T1 + T3 only.
- **Production-deployment scope extension**: if the writeup expands to include a deployment-grade classifier claim, publication discipline tightens to include responsible-disclosure embargo period + safety review per a superseding ADR.
- **HF Hub org creation**: if maintaining 3-4 model repos under personal username proves awkward (e.g., conflates with personal hobby projects), migrate to a `ciphero-take-home` org via superseding ADR with URL-migration notes.

## Alternatives Considered

- **(A) No publication; checkpoints private** — defeats T0 reproducibility tier; loses contribution-trail value; rejected per Phase 0-07 Q2 walk in favor of option C.
- **(B) Publish all trained rungs** — 4-6× publication time; ablation-rung issues / questions add post-submission maintenance surface; option C captures the reproducibility value with less time + maintenance cost.
- **(D) Single canonical "best" checkpoint** — contradicts ADR-005 (deployment is not on the roadmap) by picking a single "best" rung; methodology refuses to make a single recommendation; option C publishes the headline rungs as a *set* not as a recommendation.
- **Publish reference scorers under `BBehring/` namespace** — attribution-confusing (these are not our models); license-cascade risky (each reference scorer has its own license terms); rejected.

## References

- HF Hub model upload — https://huggingface.co/docs/hub/models-uploading
- HF Hub model card schema — https://huggingface.co/docs/hub/model-cards
- ModernBERT-base license posture (Apache 2.0) — https://huggingface.co/answerdotai/ModernBERT-base
- ADR-013 (cache location — HF Hub as persistence sink; this ADR layers publication on top)
- ADR-016 (data design — HF dataset SHA pinning carries over to HF model SHA pinning)
- ADR-018 (reference scorer slate — explicitly excluded from publication)
- ADR-019 (LoRA + transformer training recipe — defines the headline rungs)
- ADR-005 (project-level methodology principles — "deployment is not on the roadmap" framing)

## Transcript

See `transcripts/2026-05-16__phase-0-07__submission-deliverables.md` for the conversation that led to this decision (Q2 walk + option C selection).
