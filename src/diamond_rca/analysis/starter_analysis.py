"""Starter rotation analysis scaffold."""

import pandas as pd


def summarize_starters(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize basic starter indicators from game-level records."""
    if df.empty:
        return pd.DataFrame()

    columns = [col for col in ["IP", "ER", "SO", "BB"] if col in df.columns]
    if not columns:
        return pd.DataFrame({"metric": [], "value": []})

    totals = df[columns].sum(numeric_only=True)
    return totals.rename_axis("metric").reset_index(name="value")
