"""Collapse window detection helpers."""

import pandas as pd


def compute_rolling_win_pct(
    games_df: pd.DataFrame,
    result_col: str = "is_win",
    window: int = 10,
) -> pd.Series:
    """Compute rolling win percentage from binary game results."""
    if result_col not in games_df.columns:
        raise ValueError(f"Missing required result column: {result_col}")
    return games_df[result_col].rolling(window=window, min_periods=1).mean()


def flag_collapse_windows(
    games_df: pd.DataFrame,
    result_col: str = "is_win",
    window: int = 20,
    threshold: float = 0.35,
) -> pd.DataFrame:
    """Flag games where rolling win percentage falls below threshold."""
    out = games_df.copy()
    out["rolling_win_pct"] = compute_rolling_win_pct(out, result_col=result_col, window=window)
    out["is_collapse_window"] = out["rolling_win_pct"] <= threshold
    return out


def detect_threshold_collapse(
    games_df: pd.DataFrame,
    result_col: str = "is_win",
    window: int = 20,
    threshold: float = 0.35,
    min_games_flagged: int = 5,
) -> bool:
    """Simple threshold-based collapse detector.

    Returns True when the number of flagged games in collapse windows exceeds
    `min_games_flagged`.
    """
    flagged = flag_collapse_windows(
        games_df,
        result_col=result_col,
        window=window,
        threshold=threshold,
    )
    return int(flagged["is_collapse_window"].sum()) >= min_games_flagged
