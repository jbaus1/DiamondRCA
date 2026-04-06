"""Bullpen analysis scaffold."""

import pandas as pd


def summarize_bullpen(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize basic bullpen indicators from pitcher-level logs."""
    if df.empty:
        return pd.DataFrame()

    columns = [col for col in ["IP", "ER", "BB", "SO"] if col in df.columns]
    if not columns:
        return pd.DataFrame({"metric": [], "value": []})

    totals = df[columns].sum(numeric_only=True)
    return totals.rename_axis("metric").reset_index(name="value")
