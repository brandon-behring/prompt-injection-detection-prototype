# Evidence — audit trail

This document is the **single source of truth** for what external evidence was verified, what couldn't be, and what was left unresolved. Every claim in `WRITEUP.md` §7 that depends on external evidence should have a corresponding entry here.

`[LOCKED]` discipline for this iteration. Reference-scorer contamination uses the three-state taxonomy: `verified_disjoint | suspected_contamination | vendor_black_box`. Verification status per claim: `[VERIFIED|UNVERIFIED|REFUTED]`.

---

## 1. Reference scorer: `[TBD: scorer name]` — training-data contamination audit

`[TBD]` Research log for the first reference scorer:

- **Direct training-data overlap with `[TBD: source]`** — `[VERIFIED|UNVERIFIED|REFUTED]` via `[TBD: source — model card, public dataset list, hash overlap]`
- **Indirect overlap with `[TBD: source]`** — `[VERIFIED|UNVERIFIED|REFUTED]` via `[TBD]`
- **Scope mismatch evidence** — `[TBD: model card scope claim vs observed fold pattern]`

### Verdict: `[TBD]`

---

## 2. Reference scorer: `[TBD: scorer name]` — training-data audit

`[TBD]` Research log for the second reference scorer (if applicable). If training disclosure is at category level only, document the limit and the alternative analysis (fold pattern + stated scope + confound enumeration).

### Verdict: `[TBD]`

---

## 3. Style confound — what can and can't disambiguate

`[TBD]` Per-attack-style breakdown availability:

- **Tagger coverage** — `[TBD: e.g., regex catches X% of source Y's positives]`
- **Cross-source same-style ablation** — `[TBD: scoped in, deferred, or run + results]`
- **LLM-as-rater rubric audit** — `[TBD: status]`

---

## 4. Threshold methodology choices

`[TBD]` What threshold characterisation was applied to which rungs:

- Recall@FPR at `[TBD: pinpoints]` for `[TBD: rungs]`
- Detection (FPR≤X%) + Verification (FNR≤Y%) for `[TBD: rungs]`
- Rationale for excluding rungs from dual-policy: `[TBD]`

---

## 5. Replication invariants — what holds in this version

`[TBD]`:

- Bootstrap seeds + re-seeding stability check
- Per-fold variance
- Factorial control runs (if any)

---

## 6. What explicitly didn't do (and why)

`[TBD]`:

- `[TBD: gap]` — *Why deferred*: `[TBD]`
- `[TBD: gap]` — *Why deferred*: `[TBD]`
- `[TBD: gap]` — *Why deferred*: `[TBD]`

---

## 7. Sources consulted

`[TBD]` — list of model cards, papers, dataset cards, prior-version docs consulted as evidence sources.

- `[TBD: source 1]`
- `[TBD: source 2]`

---

## How to use this template

When you make a claim in WRITEUP.md §7 that depends on external evidence:

1. Add an entry to the relevant section above.
2. Document the source consulted and the verification status: `[VERIFIED|UNVERIFIED|REFUTED]`.
3. Link the WRITEUP claim back to this file with a "see EVIDENCE.md §N" cross-reference.

A claim without an EVIDENCE.md entry is a claim that can't be audited. The discipline keeps `WRITEUP.md` defensible.
