"""Data extraction helpers built on pybaseball."""

from __future__ import annotations

import logging
from datetime import date, datetime

import pandas as pd
import requests
from pybaseball import batting_stats, pitching_stats, schedule_and_record, statcast

logger = logging.getLogger(__name__)
MLB_SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule"
MLB_TEAM_IDS = {
    "ARI": 109,
    "ATH": 133,
    "ATL": 144,
    "BAL": 110,
    "BOS": 111,
    "CHC": 112,
    "CHW": 145,
    "CIN": 113,
    "CLE": 114,
    "COL": 115,
    "DET": 116,
    "HOU": 117,
    "KCR": 118,
    "LAA": 108,
    "LAD": 119,
    "MIA": 146,
    "MIL": 158,
    "MIN": 142,
    "NYM": 121,
    "NYY": 147,
    "PHI": 143,
    "PIT": 134,
    "SDP": 135,
    "SEA": 136,
    "SFG": 137,
    "STL": 138,
    "TBR": 139,
    "TEX": 140,
    "TOR": 141,
    "WSN": 120,
}


def _parse_schedule_date(value: object, season: int) -> pd.Timestamp | pd.NaT:
    """Parse pybaseball schedule date strings without noisy inference warnings."""
    raw = str(value).strip()
    if not raw or raw.lower() == "nan":
        return pd.NaT

    cleaned = raw.split(",")[-1].strip()

    for candidate, fmt in [
        (cleaned, "%b %d"),
        (raw, "%b %d %Y"),
        (raw, "%Y-%m-%d"),
        (raw, "%m/%d/%Y"),
    ]:
        try:
            parsed = datetime.strptime(candidate, fmt)
            if fmt == "%b %d":
                parsed = parsed.replace(year=season)
            return pd.Timestamp(parsed)
        except ValueError:
            continue

    return pd.NaT


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


def _lookup_team_id(team: str) -> int:
    """Translate a common MLB team abbreviation into the MLB Stats API team id."""
    team_id = MLB_TEAM_IDS.get(team.upper())
    if team_id is None:
        raise ValueError(f"Unsupported MLB team abbreviation for schedule lookup: {team}")
    return team_id


def _fetch_schedule_fallback(season: int, team: str) -> pd.DataFrame:
    """Fetch completed team game results from the MLB Stats API."""
    team_id = _lookup_team_id(team)
    response = requests.get(
        MLB_SCHEDULE_URL,
        params={"sportId": 1, "season": season, "teamId": team_id, "gameType": "R"},
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()
    rows: list[dict[str, object]] = []

    for date_block in payload.get("dates", []):
        game_date = date_block.get("date")
        for game in date_block.get("games", []):
            status = game.get("status", {})
            if status.get("abstractGameCode") != "F":
                continue

            teams = game.get("teams", {})
            home_entry = teams.get("home", {})
            away_entry = teams.get("away", {})
            home_team = home_entry.get("team", {})
            away_team = away_entry.get("team", {})

            if home_team.get("id") == team_id:
                team_entry = home_entry
                opponent_entry = away_entry
            elif away_team.get("id") == team_id:
                team_entry = away_entry
                opponent_entry = home_entry
            else:
                continue

            runs_for = team_entry.get("score")
            runs_against = opponent_entry.get("score")
            if runs_for is None or runs_against is None:
                continue

            result = "T"
            if runs_for > runs_against:
                result = "W"
            elif runs_for < runs_against:
                result = "L"

            rows.append(
                {
                    "Gm#": len(rows) + 1,
                    "Date": game_date,
                    "Opp": opponent_entry.get("team", {}).get("abbreviation"),
                    "W/L": result,
                    "R": runs_for,
                    "RA": runs_against,
                }
            )

    return pd.DataFrame(rows)


def _normalize_game_results(df: pd.DataFrame, season: int) -> pd.DataFrame:
    """Normalize raw schedule/results into the app's canonical schema."""
    if df.empty:
        return df

    out = df.copy()
    if "Gm#" in out.columns:
        out = out.loc[pd.to_numeric(out["Gm#"], errors="coerce").notna()].copy()

    out["game_date"] = out.get("Date", pd.Series(dtype=object)).map(
        lambda value: _parse_schedule_date(value, season)
    )
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
        df = _fetch_schedule_fallback(season, team)
    except Exception as exc:  # pragma: no cover - defensive around remote dependency
        logger.warning(
            "Primary MLB Stats API schedule fetch failed for %s %s; trying pybaseball fallback. Error: %s",
            team,
            season,
            exc,
        )
        try:
            df = schedule_and_record(season, team)
        except Exception as fallback_exc:  # pragma: no cover - defensive around remote dependency
            logger.exception("Failed to fetch game-level team results: %s", fallback_exc)
            return pd.DataFrame()

    try:
        return _normalize_game_results(df, season)
    except Exception as exc:  # pragma: no cover - defensive around remote dependency
        logger.exception("Failed to normalize game-level team results: %s", exc)
        return pd.DataFrame()
