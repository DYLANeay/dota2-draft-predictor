# AGENTS.md

Rules for code agents working in this repository. Read this file before any change.

## Project

- IKT 110 (UiA) group assignment for the fictional client Molde Dotaklubb.
- Deliverable: a Dota 2 draft prediction web page (ML model + Flask app + LLM question agent), a technical report, and an oral presentation (technical part + club-facing part).
- Team: Dylan, Cem, Simon.
- Task split lives in `docs/plan.md`, task list in `docs/TODO.md`.
- The assignment (`docs/dota_project.pdf`) is the source of truth: follow it strictly.
- Keep the solution as simple as possible.

## Repository layout

- `docs/`: assignment PDF, working notes (`TODO.md`), team plan (`plan.md`).
- `code/`: Dota Oracle web app (Flask + LLM agent). Run from `code/` with `uv sync`, then `uv run dota-oracle`.
- `report/`: LaTeX report, arXiv style template.
- `data/`: large data files, gitignored (only `.gitkeep` is tracked).

## Data rules

- NEVER extract `data/dota_games_final.zip` (7.6 GB, 2,338,043 match JSONs) to disk. Parse it in Python with `zipfile`, streaming over entries.
- Each entry is `dota_games/<match_id>.json` containing `{"result": {...}}` (GetMatchDetails format).
- Processed outputs go to `data/processed/` (gitignored).
- Never commit data files, model artifacts, or `.env` (API keys).

## Git workflow

- Conventional Commits: `feat(scope): ...`, `fix(scope): ...`, `docs: ...`, `chore: ...`.
- Never add `Co-Authored-By`, "Generated with", or any AI attribution to commits or PRs.
- Flow: issue, then branch `<type>/<issue>-<slug>`, then PR with `Closes #N`, then merge.
- ALWAYS ask Dylan before committing: show the diff and the commit message first, commit only after approval.
- Never force-push `main`. Feature branches may be force-pushed with `--force-with-lease` only.
- No em dashes in issues or docs. Keep issue descriptions short (bullets, a few lines).

## Code conventions

- Python 3.12 managed by `uv`. From `code/`: `uv sync`, `uv run pytest`, `uv run ruff check`.
- Tests must stay green (49 tests, no network and no API key required).
- `code/doracle/model.py` is a placeholder returning random values: it gets replaced by the trained model (step 2).
- Work order: 1) data pipeline, 2) model, 3) agent tools.
- Match the surrounding style. No speculative features.

## Assignment constraints

- The ML algorithm must come from class: Logistic Regression, Linear Regression, 2-layer MLP, or Fortuna. Own implementation counts positively; scikit-learn is allowed.
- The LLM agent must answer from dataset statistics, never from model knowledge (the data does not match modern Dota 2).
- The report must answer the 12 analysis questions and list the tools exposed to the LLM.
- Never use hero IDs in the report or the presentation, always hero names.
- Deliverables: a zip with report PDF + code, and an oral presentation (technical part + business part).
