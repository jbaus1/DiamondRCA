"""Generic rolling metric helpers."""

import pandas as pd


def add_rolling_mean(
    df: pd.DataFrame,
    value_col: str,
    window: int,
    min_periods: int = 1,
    output_col: str | None = None,
) -> pd.DataFrame:
    """Return a copy of DataFrame with rolling mean column added."""
    out = df.copy()
    col = output_col or f"{value_col}_rolling_mean_{window}"
    out[col] = out[value_col].rolling(window=window, min_periods=min_periods).mean()
    return out


def add_rolling_sum(
    df: pd.DataFrame,
    value_col: str,
    window: int,
    min_periods: int = 1,
    output_col: str | None = None,
) -> pd.DataFrame:
    """Return a copy of DataFrame with rolling sum column added."""
    out = df.copy()
    col = output_col or f"{value_col}_rolling_sum_{window}"
    out[col] = out[value_col].rolling(window=window, min_periods=min_periods).sum()
    return out
