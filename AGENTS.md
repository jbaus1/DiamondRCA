# Agent Instructions for Diamond RCA

## Core conventions

- Preserve the modular package structure under `src/diamond_rca`.
- Prefer pure functions where practical.
- Avoid hidden side effects; keep I/O explicit.
- Keep beginner readability high; avoid clever abstractions.

## Process requirements

- Update `README.md` whenever adding major features or workflow changes.
- Run formatting, linting, and tests after code changes:
  - `black .`
  - `ruff check .`
  - `pytest`
- Mirror reusable notebook logic into `src` modules.

## Data and analysis conventions

- Store raw and processed data separately.
- Keep extraction and transformation logic in dedicated modules (`data/`, `analysis/`, `rca/`).
- Use typed function signatures and docstrings for public functions.

## Scope hygiene

- Do not introduce web app frameworks yet.
- Do not overengineer orchestration or pipelines at this stage.
- Keep outputs portfolio-quality and reproducible.
