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

If `ruff` is still not available in your shell, install dev extras explicitly:

```bash
pip install -e ".[dev]"
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
python -m ruff check .
python -m black --check .
```

Auto-format code:

```bash
black .
```

Launch notebook:

```bash
jupyter notebook
```

### Initialize project directories

```python
from diamond_rca.paths import ensure_project_dirs

ensure_project_dirs()
```

### Fetch and save team data

```python
from diamond_rca.data.extract import (
    fetch_team_batting_data,
    fetch_team_pitching_data,
    fetch_team_game_results,
)
from diamond_rca.data.savers import save_csv, save_parquet
from diamond_rca.paths import RAW_DATA_DIR

# Fetch 2025 Mets batting and pitching stats
batting_df = fetch_team_batting_data(season=2025, team="NYM")
pitching_df = fetch_team_pitching_data(season=2025, team="NYM")

# Fetch game-level results (date, opponent, W/L, runs for/against)
games_df = fetch_team_game_results(season=2025, team="NYM")

# Save locally
save_csv(batting_df, RAW_DATA_DIR / "nym_2025_batting.csv")
save_parquet(pitching_df, RAW_DATA_DIR / "nym_2025_pitching.parquet")
save_csv(games_df, RAW_DATA_DIR / "nym_2025_games.csv")
```

### Reload saved data

```python
from diamond_rca.data.loaders import load_csv, load_parquet
from diamond_rca.paths import RAW_DATA_DIR

batting_df = load_csv(RAW_DATA_DIR / "nym_2025_batting.csv")
pitching_df = load_parquet(RAW_DATA_DIR / "nym_2025_pitching.parquet")
```

### Detect collapse windows

```python
from diamond_rca.data.extract import fetch_team_game_results
from diamond_rca.analysis.collapse_definition import (
    flag_collapse_windows,
    detect_threshold_collapse,
)

games_df = fetch_team_game_results(season=2025, team="NYM")

# Add rolling win % and flag collapse windows (20-game window, ≤35% threshold)
flagged_df = flag_collapse_windows(games_df, window=20, threshold=0.35)
print(flagged_df[["game_date", "opponent", "result", "rolling_win_pct", "is_collapse_window"]])

# Boolean check: did a meaningful collapse occur?
collapsed = detect_threshold_collapse(games_df, window=20, threshold=0.35, min_games_flagged=5)
print(f"Collapse detected: {collapsed}")
```

### Compute rolling metrics

```python
from diamond_rca.analysis.rolling_metrics import add_rolling_mean, add_rolling_sum

# Add a 10-game rolling mean of runs scored
games_df = add_rolling_mean(games_df, value_col="runs_for", window=10, output_col="runs_for_10g_avg")

# Add a 10-game rolling win total
games_df = add_rolling_sum(games_df, value_col="is_win", window=10, output_col="wins_last_10")
```

### Plot a rolling metric

```python
from diamond_rca.viz.plots import plot_rolling_metric

fig, ax = plot_rolling_metric(
    games_df,
    x_col="game_date",
    y_col="runs_for_10g_avg",
    title="NYM 2025 – 10-Game Rolling Runs Scored",
)
fig.savefig("reports/figures/nym_2025_rolling_runs.png", bbox_inches="tight")
```

### Build an RCA report

```python
from datetime import date
from diamond_rca.rca.five_whys import build_five_whys
from diamond_rca.rca.fishbone import Fishbone
from diamond_rca.rca.timeline import TimelineEvent, sort_timeline
from diamond_rca.rca.framework import RCAReport

# 5 Whys
five_whys = build_five_whys(
    problem_statement="The 2025 Mets collapsed after the All-Star break.",
    answers=[
        "The bullpen posted a 6.50 ERA over a 25-game stretch.",
        "Key relievers were overused and fatigued.",
        "The rotation provided short outings, increasing bullpen workload.",
        "Two starters hit the injured list within a week of each other.",
        "Injury risk signals were available but roster depth was insufficient.",
    ],
)

# Fishbone
fishbone = Fishbone(effect="Post-All-Star collapse")
fishbone.add_cause("Pitching", "Bullpen ERA spiked to 6.50+")
fishbone.add_cause("Pitching", "Two starters lost to injury")
fishbone.add_cause("Health", "Overuse and fatigue in relief corps")
fishbone.add_cause("Management", "Insufficient depth to absorb IL stints")
fishbone.add_cause("Offense", "Runs scored dropped below 3 per game")

# Timeline
events = sort_timeline([
    TimelineEvent(date(2025, 7, 20), "Starter 1 to IL", "Placed on 15-day IL with forearm strain"),
    TimelineEvent(date(2025, 7, 25), "Starter 2 to IL", "Placed on 10-day IL with shoulder inflammation"),
    TimelineEvent(date(2025, 8, 1),  "Bullpen ERA peaks", "7-day rolling ERA reaches 7.20"),
    TimelineEvent(date(2025, 8, 10), "Collapse flagged",  "20-game rolling win% drops below 35%"),
])

# Assemble and save the report
report = RCAReport(
    problem_statement="Why did the 2025 Mets collapse after the All-Star break?",
    five_whys=five_whys,
    fishbone=fishbone,
)
report.add_timeline_events(events)

out_path = report.save_markdown("reports/nym_2025_rca.md", title="2025 NYM Collapse – RCA Report")
print(f"Report saved to {out_path}")
```

## Short roadmap

- Add robust team-game assembly for season-level collapse detection.
- Add bullpen/rotation/offense decomposition diagnostics.
- Add event annotation timeline for the 2025 Mets case study.
- Add templated RCA report generation (Markdown and figure exports).
- Add richer visuals (Plotly overlays) once core logic stabilizes.
