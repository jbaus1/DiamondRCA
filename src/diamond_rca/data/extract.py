"""Data extraction helpers built on pybaseball."""

from __future__ import annotations

import logging
from datetime import date

import pandas as pd
from pybaseball import batting_stats, pitching_stats, schedule_and_record, statcast

logger = logging.getLogger(__name__)


def fetch_team_batting_data(season: int, team: str) -> pd.DataFrame:
    """Fetch season batting leaderboard rows for a specific MLB team.

    Parameters
    ----------
    season:
        The MLB season year.
    team:
        Team abbreviation matching pybaseball's `Team` column (e.g., ``NYM``).

    Returns
    -------
    pandas.DataFrame
        Filtered batting rows for the given team. Empty DataFrame on failure.
    """
    try:
        df = batting_stats(season, qual=0)
        if "Team" not in df.columns:
            logger.warning("Team column missing from batting stats output.")
            return pd.DataFrame()
        return df.loc[df["Team"] == team].copy()
    except Exception as exc:  # pragma: no cover - defensive around remote dependency
        logger.exception("Failed to fetch batting data: %s", exc)
        return pd.DataFrame()


def fetch_team_pitching_data(season: int, team: str) -> pd.DataFrame:
    """Fetch season pitching leaderboard rows for a specific MLB team."""
    try:
        df = pitching_stats(season, qual=0)
        if "Team" not in df.columns:
            logger.warning("Team column missing from pitching stats output.")
            return pd.DataFrame()
        return df.loc[df["Team"] == team].copy()
    except Exception as exc:  # pragma: no cover - defensive around remote dependency
        logger.exception("Failed to fetch pitching data: %s", exc)
        return pd.DataFrame()


def fetch_statcast_data(start_date: str | date, end_date: str | date) -> pd.DataFrame:
    """Fetch Statcast pitch-level data for a date range.

    Use narrow date windows for faster calls and easier local caching.
    """
    try:
        start = str(start_date)
        end = str(end_date)
        return statcast(start_dt=start, end_dt=end)
    except Exception as exc:  # pragma: no cover - defensive around remote dependency
        logger.exception("Failed to fetch statcast data: %s", exc)
        return pd.DataFrame()


def fetch_team_game_results(season: int, team: str = "NYM") -> pd.DataFrame:
    """Fetch game-level schedule/results for a team and normalize win/loss fields.

    Parameters
    ----------
    season:
        MLB season year.
    team:
        Team abbreviation accepted by ``pybaseball.schedule_and_record``.

    Returns
    -------
    pandas.DataFrame
        DataFrame with one row per game, sorted by date, and normalized columns:
        ``game_date``, ``opponent``, ``result``, ``is_win``, ``is_loss``, ``runs_for``,
        ``runs_against``. Empty DataFrame on failure.
    """
    try:
        df = schedule_and_record(season, team)
        if df.empty:
            return df

        out = df.copy()
        out["game_date"] = pd.to_datetime(out.get("Date"), errors="coerce")
        out = out.loc[out["game_date"].notna()].copy()

        result_series = out.get("W/L", pd.Series(dtype=str)).astype(str).str.upper()
        out["result"] = result_series.str[0]
        out["is_win"] = (out["result"] == "W").astype(int)
        out["is_loss"] = (out["result"] == "L").astype(int)

        out["runs_for"] = pd.to_numeric(out.get("R"), errors="coerce")
        out["runs_against"] = pd.to_numeric(out.get("RA"), errors="coerce")

        if "Opp" in out.columns:
            out = out.rename(columns={"Opp": "opponent"})

        normalized_columns = [
            "game_date",
            "opponent",
            "result",
            "is_win",
            "is_loss",
            "runs_for",
            "runs_against",
        ]
        for column in normalized_columns:
            if column not in out.columns:
                out[column] = pd.NA

        return out.sort_values("game_date").reset_index(drop=True)
    except Exception as exc:  # pragma: no cover - defensive around remote dependency
        logger.exception("Failed to fetch game-level team results: %s", exc)
        return pd.DataFrame()
