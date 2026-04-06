# Diamond RCA (working title)

Diamond RCA is a Python project for **root-cause analysis (RCA) of baseball team collapses**, beginning with the 2025 New York Mets as the first case study.

## Purpose

This repo provides a clean, modular foundation for baseball analytics workflows that combine:

- data extraction from `pybaseball` / Statcast-compatible sources,
- reproducible local data storage,
- reusable analysis utilities, and
- structured RCA outputs (timeline + fishbone + 5-whys).

## Why this project is interesting

Most baseball analysis focuses on *what happened* (wins, losses, stats), but less on *why a team collapsed over a specific window*. This project is designed to bridge that gap by connecting rolling performance metrics with structured RCA frameworks used in operations and engineering.

## Planned RCA layers

1. **Collapse detection layer**
   - identify candidate collapse windows from game-level results.
2. **Performance decomposition layer**
   - bullpen, rotation, offense, and context decomposition.
3. **Timeline layer**
   - event sequence and inflection-point framing.
4. **Structured RCA layer**
   - 5 Whys and fishbone-style outputs.
5. **Reporting layer**
   - simple figures and notebook-ready summaries.

## Project structure

```text
diamond_rca/
  README.md
  .gitignore
  .env.example
  pyproject.toml
  requirements.txt
  AGENTS.md
  .codex/
    config.toml
  data/
    raw/
    processed/
    external/
  notebooks/
    01_project_setup_and_data_pull.ipynb
  reports/
    figures/
  src/
    diamond_rca/
      __init__.py
      config.py
      paths.py
      logging_utils.py
      data/
        extract.py
        loaders.py
        savers.py
      analysis/
        collapse_definition.py
        rolling_metrics.py
        bullpen_analysis.py
        starter_analysis.py
        offense_analysis.py
      rca/
        framework.py
        five_whys.py
        fishbone.py
        timeline.py
      viz/
        plots.py
  tests/
    test_paths.py
    test_extract.py
    test_collapse_definition.py
```


## New in this scaffold

- `fetch_team_game_results(season, team)` now assembles game-level outcomes (date, opponent, W/L, runs for/against) to power collapse-window detection workflows.
- `RCAReport.to_markdown()` and `RCAReport.save_markdown()` now generate repeatable Markdown case-study reports.

## Setup

### 1) Create and activate a virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Install package in editable mode

```bash
pip install -e .
```

### 4) Configure environment variables

```bash
cp .env.example .env
```

## Example commands

Run tests:

```bash
pytest
```

Run lint and format checks:

```bash
ruff check .
black --check .
```

Launch notebook:

```bash
jupyter notebook
```

## Short roadmap

- Add robust team-game assembly for season-level collapse detection.
- Add bullpen/rotation/offense decomposition diagnostics.
- Add event annotation timeline for the 2025 Mets case study.
- Add templated RCA report generation (Markdown and figure exports).
- Add richer visuals (Plotly overlays) once core logic stabilizes.
