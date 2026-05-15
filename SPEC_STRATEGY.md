# Spec strategy

This document declares the SDD strategy chosen for this project. It uses the agent-output classification format from a Spec-Driven Development methodology guide: classify the repo, name the rebuild mode, justify the chosen spec pack, name alternatives explicitly rejected, and surface high-risk unknowns.

The point of this document is to make the **SDD judgment itself** legible to a reviewer in one page — so the reader sees not just the work, but the *why* of the work's structure.

## Repo classification

- **Dominant type**: Research / Proof-of-Concept prototype + Public artifact / portfolio
- **Secondary types**: ML or data system (downstream Phase 1+); Security or eval system (threat-model + reference-scorer audit)
- **Audience**: single reviewer (hiring manager); time-bound submission; not a multi-team or long-lived product
- **Cost of drift**: low (no downstream consumers, no migration path, no compatibility requirements)
- **Evidence**:
  - Single-author repo
  - Submission deadline matters
  - The classifier prototype is the artifact; methodology rigor is the demonstrated capability
  - No production deployment is on roadmap

## Rebuild mode

**Improved redesign** (greenfield case study). No prior-iteration parity to preserve; the spec is the contract for what will be built.

## Recommended spec pack

**Lightweight markdown + SDD discipline**, per the anti-overengineering rubric. Chosen because:

- Repo is small-to-medium and single-author
- Few public interfaces (no external API yet; CLI is internal-only)
- Tests + smoke tests can validate behavior
- Reviewer-as-audience makes ceremony cost > documentation benefit beyond a point

### Pack composition

- **Constitution**: split across `docs/MISSION.md` + `docs/TECH_STACK.md` + `docs/ROADMAP.md`
- **Spec**: `SPEC_GREENFIELD.md` (binding pre-Phase-0 contract; 50-row decision ledger with reference anchors)
- **Filled spec** (post-Phase-0): `SPEC_SHEET.md` (same skeleton; locked values)
- **Writeup + evidence**: `WRITEUP.md`, `EVIDENCE.md`, `NEXT_STEPS.md`, `SUBMISSION_TEMPLATE.md`, `SUBMISSION_AUDIT.md` (script-generated from ADRs)
- **Discipline**: `code_quality.md`, `STYLE.md`, `assumptions.md` (severity-tagged registry)
- **Decision records**: `decisions/` (ADR index, ADR_TEMPLATE, upstream_issues, library_imports)
- **Conversation provenance**: `transcripts/` (gitignored except README; private by default; emailed separately)
- **Tests-as-invariants**: `tests/test_invariants.py` (skip-marked stubs)
- **CI scaffolding**: `Makefile`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`
- **Glossary**: `docs/GLOSSARY.md` (living document)
- **Research dossier**: `docs/research/` (16 verified files + MANIFEST.json; produced via the research_toolkit pipeline)

### Three load-bearing libraries (library-first discipline)

- `eval-toolkit` — evaluation primitives (bootstrap CIs, paired-bootstrap, MDE, calibration, leakage)
- `runpod-deploy` — cloud orchestration
- `research_toolkit` — dossier production

Anti-hand-rolling rule: project-specific glue is allowed; replacing library primitives is not. Every gap files an upstream issue before any local workaround.

## Alternatives rejected

- **Heavier: ML/Data Pack + Security/Eval Pack + Public Artifact Pack (triple specialized pack, ~24 files)**
  - Per the SDD methodology guide, our project class technically fits all three. Rejected because: single-reviewer audience makes fragmentation hurt review flow; specialized files would duplicate WRITEUP narrative sections; the anti-overengineering rubric explicitly warns against this for low-drift, single-author submissions.
- **Spec-Kit-style multi-phase artifact set (constitution + specification + plan + tasks + implementation as separate phase repos)**
  - Rejected because: project is one focused prototype, not multi-feature; Spec-Kit's phase decomposition adds ceremony without orchestration benefit at this scale.
- **Kiro Requirements–Design–Tasks**
  - Rejected because: feature-cluster oriented; our project is one classifier, not multiple features. Constitutional SDD covers what Kiro would.
- **OpenSpec proposal/delta/archive**
  - Rejected because: capability-spec oriented and assumes the project will continue evolving. Our prototype submission is time-bounded.
- **Formal methods (TLA+ / Alloy / Lean)**
  - Rejected because: no concurrent / protocol / safety-critical subsystem warrants formalization at prototype scope.
- **Vibe coding (loose prompts, no durable spec)**
  - Rejected because: reviewer expects methodology rigor; vibe coding is unsuitable for ML evidence, public APIs, or rebuild parity.
- **Lighter: README + tests only**
  - Rejected because: methodology rigor IS the value being demonstrated; needs visible scaffolding (constitution, ADRs, audit register, dossier) to be legible to the reviewer.

## Escalation triggers

If any of the following land, upgrade the spec strategy accordingly:

- **Multi-team contributor lands** → upgrade to Spec-Kit phase artifacts
- **Classifier moves toward deployment** → add Security/Eval Pack (`THREAT_MODEL.md` deepened, `POLICY_AND_LABEL_SEMANTICS.md`, `ADVERSARIAL_VALIDATION.md`, `ERROR_POLICY.md`)
- **Paper is being written** → add ML/Data Pack (deep `DATA_PROVENANCE.md`, `LABELING_POLICY.md`, `EVAL_DESIGN.md`, deeper `REPRODUCIBILITY.md`, `CLAIMS_AND_LIMITS.md`)
- **Dossier grows past ~30 files** → add formal capability boundaries (OpenSpec-style proposal/delta/archive)

## High-risk unknowns at seed

- **Unknown**: which specific dataset slate / rung ladder / OOD slice composition the brief will support. **Default assumption**: source slate decided at Phase 0-02 from `docs/research/datasets/` candidate set. **Risk if wrong**: Phase 0 surfaces a brief-mandated source we hadn't considered; handle via kit-level supersession path (write a new ADR that supersedes the relevant SPEC_GREENFIELD ledger row).
- **Unknown**: compute budget. **Default assumption**: H100 via runpod-deploy with cost cap per Phase 0-08. **Risk if wrong**: brief mandates a cheaper / different GPU class; superseding ADR.
- **Unknown**: reviewer's methodology literacy. **Default assumption**: ML practitioner who knows LODO, bootstrap CI, calibration. **Risk if wrong**: reviewer needs more explanatory prose; `docs/GLOSSARY.md` covers the jargon load; reviewer can read SUBMISSION_TEMPLATE → README → WRITEUP §1 for the layered entry.
