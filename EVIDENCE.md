# Evidence — audit trail

This document is the **single source of truth** for what external evidence
was verified, what couldn't be, and what was left unresolved. Every claim in
`WRITEUP.md` §7 that depends on external evidence has a corresponding entry
here.

`[LOCKED]` discipline. Reference-scorer contamination uses the three-state
taxonomy per ADR-005: `verified_disjoint | suspected_contamination |
vendor_black_box`. Per ADR-050, the `vendor_black_box` tier carries
**0 rungs** in this submission (LLM-judge reference scorers dropped at
Phase 4 cost re-estimation). The reference slate is three rungs:
`tfidf-lr` (`verified_disjoint`), `ProtectAI v1` (`suspected_contamination`),
`ProtectAI v2` (`suspected_contamination`). Verification status per
claim: `[VERIFIED|UNVERIFIED|REFUTED]`.

---

## 1. Reference scorer: `ProtectAI v1` — training-data contamination audit

**Contamination tier**: `suspected_contamination` per ADR-005.

`[VERIFIED]` ProtectAI's prompt-injection v1 model
(`protectai/deberta-v3-base-prompt-injection`) is a DeBERTa-v3-base
fine-tuned on a published mix of public prompt-injection corpora. The
ProtectAI HF model card lists the training datasets explicitly.

- **Direct training-data overlap with `deepset/prompt-injections`** —
  `[VERIFIED]` via ProtectAI's published training-data mix on the HF model
  card (`protectai/deberta-v3-base-prompt-injection`). `deepset/prompt-injections`
  is one of our 4 LODO training-pool sources per ADR-016. Overlap with
  our LODO held-out fold 0 is therefore mechanically present.
- **Direct training-data overlap with `Lakera/gandalf_ignore_instructions`** —
  `[VERIFIED]` via the same model-card disclosure. This is our LODO fold 1
  held-out source.
- **Direct training-data overlap with `Lakera/mosscap_prompt_injection`** —
  `[UNVERIFIED]`. The ProtectAI card lists "Lakera" data without naming
  the specific dataset; could be Gandalf only, could be Mosscap as well.
  Treated as `suspected_contamination` rather than `verified_disjoint`
  by default.
- **Direct training-data overlap with `hackaprompt/hackaprompt-dataset`** —
  `[UNVERIFIED]`. Not listed on the ProtectAI card; suspected absent but
  not confirmed.
- **Scope mismatch evidence** — ProtectAI v1 model card claims English-only
  + single-turn + classifier scope, which matches our submission scope per
  ADR-014. No scope-mismatch finding.

### Verdict: `suspected_contamination` — at least 2 of 4 LODO training-pool sources are explicitly in the ProtectAI training mix; reported as diagnostic reference, not as a clean OOD baseline. Per-cell numbers should be read with the contamination-tier asterisk per the README headline table.

**Sources consulted**: HF model card `protectai/deberta-v3-base-prompt-injection`
(retrieved 2026-05-15); ADR-005 taxonomy; ADR-016 LODO training-pool lock.

---

## 2. Reference scorer: `ProtectAI v2` — training-data contamination audit

**Contamination tier**: `suspected_contamination` per ADR-005.

`[VERIFIED]` ProtectAI's prompt-injection v2 model
(`protectai/deberta-v3-base-prompt-injection-v2`) is the same architecture
as v1 (DeBERTa-v3-base) trained on an expanded data mix. The v2 model card
adds further sources but retains the v1 base mix.

- **Direct training-data overlap with `deepset/prompt-injections`** —
  `[VERIFIED]` via the v2 HF model card. Same as v1 (retained).
- **Direct training-data overlap with `Lakera/gandalf_ignore_instructions`** —
  `[VERIFIED]` via the v2 HF model card.
- **Direct training-data overlap with `Lakera/mosscap_prompt_injection`** —
  `[UNVERIFIED]` (same Lakera-grouping ambiguity as v1).
- **Direct training-data overlap with `hackaprompt/hackaprompt-dataset`** —
  `[UNVERIFIED]`.
- **Indirect overlap via expanded v2 data sources** — `[UNVERIFIED]`. The
  v2 card adds additional public corpora whose individual SHAs / row
  counts are not enumerated; we cannot rule out incidental overlap with
  our OOD slate sources (`JBB-Behaviors`, `XSTest`, `NotInject`,
  `BIPIA`, `InjecAgent`).
- **Scope mismatch evidence** — v2 model card claims same scope as v1
  (English single-turn classifier). No scope-mismatch finding.

### Verdict: `suspected_contamination` — same 2-of-4 LODO training-pool overlap as v1, plus uncharacterised v2-specific expansion. Reported with the contamination-tier asterisk per the headline table.

**Sources consulted**: HF model card
`protectai/deberta-v3-base-prompt-injection-v2` (retrieved 2026-05-15);
ADR-005 taxonomy; ADR-016 OOD-slate composition.

---

## 2.5 Reference scorer: `tfidf-lr` (classical floor) — training-data verification

**Contamination tier**: `verified_disjoint` per ADR-005.

`[VERIFIED]` The `tfidf-lr` classical floor is trained in-project on the
4-source LODO training pool per ADR-017. No external training-data
provenance. The classical floor's training data is by construction
disjoint from any held-out OOD slice (since the OOD slices are LODO
held-out positives, not in the training pool) — see
`evals/leakage_report.json` per-fold `exact_hash_overlaps: 0` +
`cosine_ge_085_overlaps: 0`.

### Verdict: `verified_disjoint`. Reported without an asterisk.

**Sources consulted**: ADR-017 (classical-floor architecture lock);
`evals/leakage_report.json`; ADR-005 taxonomy.

---

## 3. Style confound — what can and can't disambiguate

Per-attack-style breakdown availability:

- **Tagger coverage** — `[VERIFIED]` regex-based per-attack-style tagger
  in `src/data/style_tagger.py` covers the 4 LODO training-pool sources
  + 5 OOD slices. Per-source per-style counts land in
  `evals/data_audit.json` per ADR-041. Tagger is **conservative** — it
  matches surface n-grams; semantic equivalents (paraphrased injection
  intent) are not caught by design.
- **Cross-source same-style ablation** — `[DEFERRED — UNVERIFIED]`. Would
  disambiguate "training-data contamination" from "attack-style
  difficulty" for the ProtectAI reference scorers (per ADR-005 audit
  framing). *Why deferred*: per-style sample sizes on the 5-slice OOD
  slate are too small for powered ablation: BIPIA n=50, InjecAgent n=62,
  JBB n=200, XSTest n=450, NotInject n=339. A powered 2×2 (in-pool
  style × in-ProtectAI-training) ablation would need ≥1000 rows per
  cell; we have ≤450. Treated as explicit limitation per WRITEUP §8.
- **LLM-as-rater rubric audit** — `[DROPPED per ADR-050]`. Phase 4 cost
  re-estimation against actual OOD slate sizing revealed an envelope
  ~16× the original ADR-018 estimate ($14 → $240) driven by per-row
  LLM-judge inference being charged at the full input-prompt token count.
  ADR-050 dropped both LLM judges and the rater-audit cohort that
  followed from them.

---

## 4. Threshold methodology choices

Threshold characterisation per rung × policy from
`evals/operating_points/dual_policy.parquet` (72 rows: 4 trained rungs ×
4 folds × 3 seeds × 2 policies; populated per ADR-025).

- **Detection policy** (target val FPR ≤ 1%) — applied to in-house rungs
  `frozen_probe` + `lora` + `tfidf-lr`. Mean val→test reachability:
  `frozen_probe` 11/12, `lora` 0/12, `tfidf-lr` see operating_points.
- **Verification policy** (target val recall ≥ 99%) — applied to same
  in-house rungs. Mean val→test reachability: `frozen_probe` 5/12,
  `lora` 0/12. Threshold-fitting set is val per ADR-025; reachability
  on val is 12/12 by construction; reachability on LODO held-out test
  drops because the LODO distribution shift moves the operating point.
- **Recall@FPR pinpoints** (no policy-fitting) — applied to all 5 rungs
  including reference scorers (`ProtectAI v1`, `ProtectAI v2`,
  `tfidf-lr`) at FPR ∈ {0.1%, 1%, 5%}. Per-cell values land in
  `evals/metrics/per_cell.parquet` (`recall_at_fpr_0_1`,
  `recall_at_fpr_1`, `recall_at_fpr_5`).
- **Rationale for excluding rungs from dual-policy**: reference scorers
  (`ProtectAI v1/v2`) excluded from dual-policy threshold characterisation
  per WRITEUP §5.3 scope bound — training-overlap caveats make
  operating-point characterisation misleading; recall@FPR pinpoints are
  the in-scope summary for those rungs.

`[VERIFIED]` All 72 dual-policy rows are present in
`evals/operating_points/dual_policy.parquet`; reachability per-cell
captured in `evals/audit/verification_reachability.json` per ADR-025.

---

## 5. Replication invariants — what holds in this version

`[VERIFIED]` Bootstrap seed re-seeding stability: Phase 7 stability check
(commit `26776dc`) re-ran the paired-bootstrap headline matrix with
`seed=2` (canonical was `seed=1`); 0 of 40 cells flagged at the 5%-of-CI
threshold. Captured at `evals/bootstrap/paired_cells_seed2.parquet`. The
bootstrap CIs are seed-stable.

`[VERIFIED]` Per-fold variance: 4 LODO folds × 3 training seeds (42, 43,
44) yield 12 cells per (rung, slice, metric). The `cv_clt_ci` headline
CI machinery (Bayle 2020 Annals of Statistics Theorem 3.1) is used per
ADR-024. LODO non-exchangeability is a real assumption violation; per
A-008, the sensitivity check `block_bootstrap_CI / cv_clt_CI` ratio is
captured in `evals/audit/cross_fold_ci_audit.parquet` for every rung.

`[VERIFIED]` Leakage invariants: `evals/leakage_report.json` reports
zero exact-hash overlaps and zero cosine-≥0.85 overlaps for every
(fold, seed) split. Cosine threshold 0.85 locked at ADR-016 Q3.

`[VERIFIED]` Dedup calibration: `evals/dedup_calibration.json` reports
locked threshold 0.80 (encoder `sentence-transformers/all-MiniLM-L6-v2`
revision `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`) calibrated against
a 50-pair golden holdout (`data/dedup_holdout.jsonl`, SHA-256
`250eb96…001f3`, 25 banded + 25 random). At locked threshold: tp=12,
fp=0, tn=32, fn=6; FPR=0, FNR=33.3%. Per ADR-016 Q4 + ADR-041 Q5 +
ADR-042.

`[VERIFIED]` Contamination scan (ADR-016 A-005 trigger 1 + A-006 +
ADR-041 Q6): 0 A-005 trigger fires across all OOD sources at cosine
threshold 0.85. Per `evals/contamination_scan.json`: bipia 0%,
injecagent 0%, notinject 0%, jbb_behaviors 0%, xstest 0.222% (1/450
rows flagged, well below the 1% trigger). Benign sources: lmsys_chat_1m
0.298%, ultrachat_200k 0.011% — both below trigger.

`[UNVERIFIED]` Factorial control runs (e.g., LoRA-vs-LoRA-with-different-
init): not run in this submission. Cross-seed variance is captured at
the 3-seed level per ADR-019 + ADR-024; higher-seed-count factorial
deferred per WRITEUP §8 + NEXT_STEPS §1.3 + §2.1.

---

## 6. What explicitly didn't do (and why)

Pointer rather than restatement. See [`WRITEUP.md` §8](./WRITEUP.md) for the
consolidated deferred list; key gaps with EVIDENCE-relevant rationale:

- **Curated adversarial probe set** (paraphrase / encoded payloads /
  multi-turn) — *Why deferred*: would expand methodology contract from
  "characterisation against fixed slate" to "ongoing adversarial probing"
  — out of case-study scope. The fixed slate already spans direct /
  indirect / jailbreak / agentic / benign-but-injection-shaped attack
  styles. See WRITEUP §5.6.
- **LLM-as-rater rubric audit** — *Why deferred*: dropped at Phase 4
  cost re-estimation per ADR-050; envelope was ~16× the original
  ADR-018 estimate. The 50-pair dedup-calibration holdout was the
  partial LLM-judge audit that survived.
- **Multi-seed factorial controls beyond 3 seeds** — *Why deferred*:
  3-seed Bayle 2020 cv_clt_ci is the in-scope headline CI machinery
  per ADR-024 + the sensitivity flag against block-bootstrap per A-008;
  expanded seed-count factorial is in NEXT_STEPS §1.3.
- **full-FT OOD inference** — *Why deferred*: dropped at Phase 5 X11
  per ADR-050 Revision 2 (FUSE EIO crash mid-training; checkpoint
  loss). full-FT remains in the LODO 3-rung trained ladder via
  surviving Phase 2 predictions.
- **Cross-source same-style ablation** — *Why deferred*: per-style
  sample sizes on the 5-slice OOD slate are too small for powered
  ablation. See §3 above.

---

## 7. Sources consulted

Model cards + dataset cards + papers + prior-version docs consulted as
evidence sources during contamination audits and methodology lock-in:

- **ProtectAI HF model cards**:
  `protectai/deberta-v3-base-prompt-injection` (v1; retrieved 2026-05-15)
  and `protectai/deberta-v3-base-prompt-injection-v2` (v2; retrieved
  2026-05-15) — training-data disclosure source for §1 + §2.
- **LODO training-pool dataset cards** (per ADR-016):
  `deepset/prompt-injections`, `Lakera/gandalf_ignore_instructions`,
  `Lakera/mosscap_prompt_injection`, `hackaprompt/hackaprompt-dataset` —
  source-disclosure cross-reference for §1 + §2.
- **OOD-slate source cards** (per ADR-021 + ADR-016):
  `wikd/NotInject`, `paul-rottger/xstest-v2-copy`,
  `JailbreakBench/JBB-Behaviors` (HF); `BIPIA` + `InjecAgent` (release-
  pinned local git repos via `source_manifest.yaml`).
- **Methodology dossier** at `docs/research/`:
  `benchmarks/` (OOD slate candidate analysis), `datasets/`
  (training-pool source dossiers), `attacks_defenses/` (attack
  taxonomy + defense literature). MANIFEST.json indexes verified files
  with `claim_family` / `verification_status` / `tags` per the
  Phase 0-04 research_toolkit dossier protocol.
- **Statistical methodology references** (in-text WRITEUP citations):
  Bayle 2020 (Annals of Statistics) Theorem 3.1 for cross-fold CLT CI
  (cv_clt_ci); DeLong 1988 for AUC-difference CI; Benjamini-Hochberg
  1995 for FDR; Efron 1987 (BCa bootstrap).

---

## How to use this file

When you make a claim in WRITEUP.md §5 / §7 that depends on external
evidence:

1. Add an entry to the relevant section above.
2. Document the source consulted and the verification status:
   `[VERIFIED|UNVERIFIED|REFUTED]`.
3. Link the WRITEUP claim back to this file with a "see EVIDENCE.md §N"
   cross-reference.

A claim without an EVIDENCE.md entry is a claim that can't be audited.
The discipline keeps `WRITEUP.md` defensible.
