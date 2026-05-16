---
adr_id: "035"
slug: secrets-management-three-store-split
title: Secrets management — three-store split aligned with execution context (.env + RunPod pod-secrets + GH Actions repo Secrets)
date: 2026-05-16
status: Accepted
claim_id: CLAIM-035
claim: Phase 0-08 locks SPEC_GREENFIELD ledger row 305 (Secrets management) at a three-store split aligned with the three execution contexts that span the submission lifecycle — local laptop plus RunPod cloud pod plus GitHub Actions runner. Local laptop uses a gitignored .env file at repo root containing real tokens; consumer libraries (huggingface_hub plus openai plus anthropic plus runpod-deploy CLI) discover tokens via their default env-var discovery mechanism (canonical env var names HF_TOKEN plus RUNPOD_API_KEY plus OPENAI_API_KEY plus ANTHROPIC_API_KEY). RunPod cloud pod injects tokens as env vars on pod start via the runpod-deploy pod-secrets primitive declared in configs/runpod/headline.yaml per ADR-020. GitHub Actions runner accesses tokens via repo-level Settings then Secrets and variables then Actions (Web UI configuration); GITHUB_TOKEN is auto-injected by GH Actions runtime per ADR-030 publish workflow; HF_TOKEN added as a repo secret only if model card push runs in CI (per ADR-032 model card generation runs at Phase 5 close — may be local plus may be CI; secret added preemptively). A committed .env.example template at repo root (with placeholder values not real tokens) enumerates the four canonical env vars so reviewers can see the secret surface without running anything; .env.example serves the kit-level audit-friendly framing. The pre-commit gitleaks hook (already enabled and passing for all prior commits in this session) provides defense-in-depth against accidental .env commits; ADR-035 explicitly ratifies this gate as part of the secrets posture. Rotation protocol — token rotation requires updating all three stores in sequence (local .env then RunPod config then GH Actions Secrets); documented in CHANGELOG.md or a docs/secrets.md rotation runbook. Pre-flight verification — scripts/preflight_secrets.py (Phase 1 work item) asserts the four env vars are non-empty before any real-cost run (cloud dispatch plus LLM-judge API calls); fails loud per Python standards (ValueError with explicit message naming the missing token plus the consumer that would need it). Out-of-scope at this lock — cloud secret manager migration (Doppler plus Infisical plus 1Password plus AWS Secrets Manager plus GCP Secret Manager) is documented as a future-extension condition triggered by either (a) post-submission scope extension to production-grade deployment per ADR-005 plus ADR-027 framing or (b) Phase 1+ surfaces five-plus additional secrets that make the three-store rotation discipline costly. Encrypted-in-repo (git-crypt plus sops plus age) explicitly rejected — adds key management complexity plus contradicts library defaults (consumer libraries do not read encrypted blobs). Limitation — secrets in three stores means rotation discipline matters; mitigation is the preflight script. Extension condition — production-grade deployment scope extension triggers migration to a cloud secret manager via superseding ADR.
source: SPEC_GREENFIELD.md §Tech-Stack ledger row 305 + Phase 0-08 walk Q5
acceptance_criterion: SPEC_GREENFIELD ledger row 305 carries locked-to-three-store-split-aligned-with-execution-context status (see ADR-035); .env.example exists at repo root with placeholder values for the four canonical env vars (HF_TOKEN plus RUNPOD_API_KEY plus OPENAI_API_KEY plus ANTHROPIC_API_KEY); .gitignore covers .env plus .env.local plus .env.production patterns (verified via git check-ignore); pre-commit gitleaks hook is enabled in .pre-commit-config.yaml and is part of the standard pre-commit gate (verified by prior commits passing); scripts/preflight_secrets.py is captured as a Phase 1 work item in assumptions.md or a Phase 1 checklist file; tests/test_invariants.py contains skip-marked stub test_env_example_template_present asserting (1) .env.example exists at repo root; (2) the file enumerates all four canonical env vars HF_TOKEN plus RUNPOD_API_KEY plus OPENAI_API_KEY plus ANTHROPIC_API_KEY; (3) the values are placeholder-shaped not real tokens (regex check — no value matches the real-token signature for any of the four token classes); (4) .gitignore covers .env (verified via subprocess git check-ignore); SUBMISSION_AUDIT.md regenerates from the new ADR.
closing_commit:
references:
  - https://12factor.net/config
  - https://huggingface.co/docs/huggingface_hub/quick-start#authentication
  - https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions
  - https://github.com/brandon-behring/runpod-deploy
  - decisions/ADR-020-compute-infrastructure-and-cost-discipline.md
  - decisions/ADR-018-reference-scorer-slate-and-contamination-stratification.md
  - decisions/ADR-030-deliverable-format-quarto-html-site.md
  - decisions/ADR-032-hf-hub-publication-headline-rungs-only.md
transcript: transcripts/2026-05-16__phase-0-08__process-tech-stack-acceptance.md
---

# ADR-035: Secrets management — three-store split aligned with execution context

## Status

Accepted (2026-05-16). Closes the §Tech-Stack ledger row 305 (Secrets management). Companion to ADR-020 (runpod-deploy compute infrastructure + cost discipline — the RunPod-side mechanism for pod-secrets injection), ADR-030 (Quarto + GH Actions publish — the CI-side surface where GH Actions repo Secrets are consumed), and ADR-032 (HF Hub publication — the primary `HF_TOKEN` consumer at Phase 5 close).

## Context

Four-to-five API tokens span three execution contexts during the submission lifecycle.

| Secret | Required by | Local laptop | RunPod cloud pod | GH Actions runner |
|---|---|---|---|---|
| `HF_TOKEN` | ADR-016 dataset SHA pinning + ADR-032 model publication | yes (Phase 5 publish) | yes (Phase 2-3 dataset fetch) | conditional (if model card push runs in CI) |
| `RUNPOD_API_KEY` | ADR-020 runpod-deploy CLI auth | yes (Phase 2-3 dispatch) | n/a (pod itself doesn't need this) | n/a |
| `OPENAI_API_KEY` | ADR-018 R-LLM-OpenAI scorer (`gpt-4o-2024-08-06`) | conditional | yes (Phase 3 eval) | n/a |
| `ANTHROPIC_API_KEY` | ADR-018 R-LLM-Anthropic scorer (`claude-sonnet-4-6`) | conditional | yes (Phase 3 eval) | n/a |
| `GITHUB_TOKEN` | ADR-030 GH Actions publish workflow | n/a | n/a | yes (auto-injected by GH Actions runtime) |

(No `WANDB_API_KEY` — no W&B integration scoped.)

The constraint surface that drives the choice:

- **All consumer tools default to env-var discovery** — `huggingface_hub` reads `HF_TOKEN`; `openai` reads `OPENAI_API_KEY`; `anthropic` reads `ANTHROPIC_API_KEY`; `runpod-deploy` reads `RUNPOD_API_KEY`. The libraries find tokens via env vars without configuration.
- **`.env` is the universal local-dev convention** (12-factor app config principle — https://12factor.net/config).
- **RunPod has a pod-secrets primitive** — set via `runpod-deploy` config (per ADR-020); injected as env vars on pod start.
- **GH Actions has repo-level Secrets** — set via repo Settings → Secrets and variables → Actions; available as `${{ secrets.NAME }}` in workflow steps.
- **Pre-commit `gitleaks` is already enabled** — all prior commits in this session passed gitleaks; catches accidental `.env` commits.

Four options were considered (per Phase 0-08 Q5 walk):

(A) Three-store split aligned with execution context — standard 12-factor pattern.
(B) Cloud secret manager (Doppler / Infisical / 1Password / AWS Secrets Manager / GCP Secret Manager) — centralized.
(C) Encrypted-in-repo (git-crypt / sops / age) — encrypted blobs committed.
(D) HF-canonical token cache + ad-hoc for others — asymmetric across secrets.

User selection at Q5 walk: **A**.

## Decision

### Three-store split

**Local laptop** — gitignored `.env` at repo root contains real tokens. Loaded by scripts via `python-dotenv` or manual `os.environ` read; consumer libraries find tokens via their default env-var discovery.

**RunPod cloud pod** — pod-secrets injected via `runpod-deploy` config (`pod.env_vars` or equivalent per the runpod-deploy 0.7.7 schema). Tokens become env vars on pod start; consumer libraries find them.

**GitHub Actions runner** — repo Settings → Secrets and variables → Actions:
- `GITHUB_TOKEN` is auto-injected by GH Actions runtime (per ADR-030 publish workflow); no manual configuration.
- `HF_TOKEN` added as repo secret if model card push runs in CI (per ADR-032; final publication-step location TBD at Phase 5 — may be local or CI).

### Committed template — `.env.example`

A committed `.env.example` at repo root (no real tokens; placeholder values) enumerates the four canonical env vars:

```
# Required for Phase 1-5 execution; see decisions/ADR-035-secrets-management-three-store-split.md
# Copy this file to .env (gitignored) and fill in real values.
# DO NOT commit .env (.gitignore covers; gitleaks pre-commit hook catches).

HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
RUNPOD_API_KEY=YOUR_RUNPOD_API_KEY_HERE
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Reviewer reading the repo at submission tag sees the secret surface immediately without running anything.

### Pre-commit `gitleaks` gate

Already enabled in `.pre-commit-config.yaml`; all session commits pass the gate. This ADR explicitly ratifies the gate as part of the secrets posture.

### Rotation protocol

Token rotation requires updating all three stores in sequence:

1. Generate new token at the provider (HuggingFace / RunPod / OpenAI / Anthropic).
2. Update local `.env`.
3. Update `runpod-deploy` config (or RunPod pod-secret directly if config-driven injection is not used).
4. Update GH Actions repo Secrets if the token is used in CI.
5. Verify via `scripts/preflight_secrets.py` (Phase 1 work item).

Documented in `docs/secrets.md` rotation runbook (Phase 1 work item; out-of-scope for Phase 0-08 close).

### Pre-flight verification

`scripts/preflight_secrets.py` (Phase 1 work item) asserts the four env vars are non-empty before any real-cost run. Fails loud per Python standards:

```python
def preflight_secrets() -> None:
    """Verify all required secrets are present before real-cost runs.

    Raises ValueError with explicit context naming each missing token + its consumer.
    """
    required = {
        "HF_TOKEN": "huggingface_hub (ADR-016 dataset fetch + ADR-032 model publish)",
        "RUNPOD_API_KEY": "runpod-deploy CLI (ADR-020 GPU dispatch)",
        "OPENAI_API_KEY": "openai SDK (ADR-018 R-LLM-OpenAI scorer)",
        "ANTHROPIC_API_KEY": "anthropic SDK (ADR-018 R-LLM-Anthropic scorer)",
    }
    missing = [(name, consumer) for name, consumer in required.items() if not os.environ.get(name)]
    if missing:
        details = "; ".join(f"{name} (needed by {consumer})" for name, consumer in missing)
        raise ValueError(f"Missing required env vars: {details}. See .env.example.")
```

## Consequences

### Positive

- **Aligns with library defaults** — every consumer library discovers tokens via env vars natively; no glue code needed; zero adaptation cost.
- **No new infrastructure** — `.env` + gitignore + gitleaks pre-commit + RunPod pod-secrets + GH Actions repo Secrets are all standard / existing primitives.
- **Audit-friendly via `.env.example`** — reviewer sees the secret surface (which tokens, from which providers, for which consumers) without running anything.
- **Deadline-realistic** — option B (cloud secret manager) would consume 4+ hours of auth-chain setup before any real work; ADR-001 calendar doesn't have that budget.
- **Defense-in-depth** — `.gitignore` blocks accidental `.env` staging; gitleaks pre-commit hook catches any leak that slips through; preflight script catches missing tokens before real spend.
- **Honors existing posture** — the gitleaks pre-commit hook has been passing every commit in this session; this ADR ratifies that gate explicitly.

### Negative / cost

- **Secrets in three stores** means rotation discipline matters; if a token rotates and `.env` updates but RunPod pod-config doesn't, the pod fails mid-run. Mitigation: pre-flight script + rotation runbook.
- **`.env.example` placeholder values** must look obviously-not-real to avoid reviewer confusion + to avoid gitleaks false negatives. Mitigation: use `hf_xxxx...` / `sk-xxxx...` / `YOUR_..._HERE` patterns that gitleaks recognizes as placeholders.
- **GH Actions Secrets are repo-scope** — anyone with repo admin can read them. Acceptable for the public-repo + solo-maintainer posture of this submission; mitigation = rotate after submission if leaving the repo public long-term.

### Neutral

- **GH Actions `HF_TOKEN` is conditional** — added only if Phase 5 publish-side decides to run model card push in CI. Defer to Phase 5; the discipline is locked at ADR-035; the specific CI-vs-local boundary is per-step.
- **Cloud secret manager remains a future extension** — not chosen at Phase 0-08 close; revisited if scope extends to production-grade deployment or if Phase 1+ adds 5+ more secrets.

### Limitation

Three separate stores means rotation discipline is critical. The pre-flight script catches missing-token cases but cannot catch stale-token cases (where `.env` has the new token but RunPod pod-config still has the old token). Mitigation: rotation runbook documents the sequence; post-rotation runs are checked via `runpod-deploy validate --all` (per ADR-020 preflight) which fails on auth errors.

### Extension condition for revisit

- **Production-grade deployment scope extension** triggers migration to a cloud secret manager (option B from the Q5 walk) — Doppler / Infisical / 1Password / AWS Secrets Manager / GCP Secret Manager — via superseding ADR. The CI auth chain + audit logging needed at production grade exceeds what three-store split provides.
- **Phase 1+ surfaces 5+ more secrets** (e.g., a third LLM-judge ablation per ADR-018 afterword expanding to gpt-4.1 / opus-4-7 / o1 / o3) — friction of three-store rotation starts to dominate; superseding ADR migrates to a secret manager. Currently below the friction threshold (4 secrets).
- **Repo migration to a Ciphero org** post-submission — GH Actions repo Secrets must be re-provisioned at the new repo location; documented in the rotation runbook.

## Alternatives Considered

- **(B) Cloud secret manager (Doppler / Infisical / 1Password / AWS Secrets Manager / GCP Secret Manager)** — adds infrastructure dependency; auth-chain setup is hours-to-days first-time; overkill for 2-day submission with 4 tokens. Rejected per Q5 walk in favor of A.
- **(C) Encrypted-in-repo (git-crypt / sops / age)** — encrypted secrets committed; decrypt at use. Key management is its own secret problem (chicken-and-egg); consumer libraries don't read encrypted blobs; not standard for ML projects. Rejected per Q5 walk.
- **(D) HuggingFace CLI token caching (`~/.cache/huggingface/token`) + RunPod pod-secrets + GH Actions Secrets** — HF-canonical for HF only; other tokens still need `.env` or env-var injection; adds asymmetry across secrets. Rejected for inconsistency.
- **Hardcoded in scripts** — never acceptable; standard anti-pattern.

## References

- 12-Factor App config principles — https://12factor.net/config
- `huggingface_hub` token authentication — https://huggingface.co/docs/huggingface_hub/quick-start#authentication
- GitHub Actions Encrypted Secrets — https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions
- `runpod-deploy` (RunPod pod-secrets injection mechanism) — https://github.com/brandon-behring/runpod-deploy
- ADR-020 (compute infrastructure — RunPod pod-secrets primitive consumer)
- ADR-018 (reference scorer slate — `OPENAI_API_KEY` + `ANTHROPIC_API_KEY` consumers)
- ADR-030 (Quarto + GH Actions publish — `GITHUB_TOKEN` consumer)
- ADR-032 (HF Hub publication — `HF_TOKEN` consumer at Phase 5)

## Transcript

See `transcripts/2026-05-16__phase-0-08__process-tech-stack-acceptance.md` for the conversation that led to this decision (Q5 walk + option A selection).
