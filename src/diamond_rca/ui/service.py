"""UI service layer that can later back a React/API frontend."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from diamond_rca.analysis.collapse_definition import flag_collapse_windows
from diamond_rca.data.extract import fetch_team_game_results


@dataclass
class CollapseAnalysisResult:
    """Normalized result payload for UI consumption."""

    team: str
    season: int
    total_games: int
    collapse_games: int
    collapse_rate: float
    games: pd.DataFrame


def build_collapse_analysis(
    team: str,
    season: int,
    window: int = 20,
    threshold: float = 0.35,
) -> CollapseAnalysisResult:
    """Build a collapse-analysis payload from game-level results.

    This function is intentionally UI-framework agnostic so it can be reused by
    Streamlit now and an API layer for React in the future.
    """
    games = fetch_team_game_results(season=season, team=team)
    if games.empty:
        return CollapseAnalysisResult(
            team=team,
            season=season,
            total_games=0,
            collapse_games=0,
            collapse_rate=0.0,
            games=games,
        )

    analyzed = flag_collapse_windows(
        games_df=games,
        result_col="is_win",
        window=window,
        threshold=threshold,
    )
    collapse_games = int(analyzed["is_collapse_window"].sum())
    total_games = len(analyzed)
    collapse_rate = collapse_games / total_games if total_games else 0.0

    return CollapseAnalysisResult(
        team=team,
        season=season,
        total_games=total_games,
        collapse_games=collapse_games,
        collapse_rate=collapse_rate,
        games=analyzed,
    )
