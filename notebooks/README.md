# Notebooks

Phase 2+ demo / exploratory / paper-figure notebooks. Empty at seed; populated as analysis lands.

## Convention: jupytext paired files

Notebooks are paired bidirectionally with `.py` percent-script files via `jupytext`. Each notebook has two committed forms:

- **`<name>.ipynb`** — the executable notebook; outputs stripped before commit via `nbstripout` pre-commit hook
- **`<name>.py`** — Python percent-script (`# %%` cell markers) auto-generated from the .ipynb; gives reviewable diffs for notebook logic

The format pairing is declared in `pyproject.toml`:

```toml
[tool.jupytext]
formats = "ipynb,py:percent"
```

Editing either file updates the other automatically (when jupytext is installed; `pip install -e ".[notebook]"` or `uv sync --extra notebook`).

## CI gating

By default CI does NOT execute notebooks — they're heavy. The `.github/workflows/ci.yml` includes an opt-in `notebooks` job that runs `pytest --nbval notebooks/` on `workflow_dispatch` only. This means: push commits with confidence; trigger notebook re-execution explicitly when validating canonical results.

## Planned notebooks (Phase 2+)

Per `NEXT_STEPS.md` §1 tactical roadmap:

- `01_canonical_results.ipynb` — headline characterization table population (Phase 4)
- `02_frozen_vs_lora.ipynb` — paired-bootstrap rung-comparison (Phase 4)
- `03_calibration.ipynb` — reliability curves + ECE per rung (Phase 4)
- `04_ood_slate.ipynb` — per-slice IID-vs-OOD gap visualization (Phase 4)
- Additional notebooks as needed for §7 result narratives

## How to add a new notebook

```bash
# 1. Install notebook extras
uv sync --extra notebook

# 2. Create the notebook
jupyter notebook notebooks/NN_my_notebook.ipynb

# 3. First save: jupytext auto-generates the paired .py
#    Subsequent edits to either file sync to the other

# 4. Pre-commit strips outputs and runs the standard hooks
git add notebooks/NN_my_notebook.{ipynb,py}
git commit -m "feat: NN_my_notebook — <one-line description>"
```

## Library-first reminder

Notebooks should use `eval-toolkit` primitives (`bootstrap_ci`, `plot_pr_curve`, `plot_reliability_diagram`, etc.) — not hand-roll plotting / stats. The anti-hand-rolling rule applies inside notebooks too.
