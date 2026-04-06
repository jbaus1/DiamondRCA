"""Data extraction helpers built on pybaseball."""

from __future__ import annotations

import logging
from datetime import date

import pandas as pd
from pybaseball import batting_stats, pitching_stats, statcast

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
