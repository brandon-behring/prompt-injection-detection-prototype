"""Versioned LLM-judge prompt templates per ADR-018.

Templates are markdown files (reviewer-readable) rather than Python string
constants so the template version + content is auditable independently of
the calling code. The active template version is referenced by
`src/scoring/llm_judge_base.py::PROMPT_TEMPLATE_VERSION`.

Versioning policy: a new template version requires a new file
(`prompt_template_v2.md`, `_v3.md`, ...). The cache schema includes
`prompt_template_version` so cached scores stay associated with the
template they were generated under per A-007.
"""
