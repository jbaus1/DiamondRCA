"""Offensive performance analysis scaffold."""

import pandas as pd


def summarize_offense(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize key offensive totals from team/player logs."""
    if df.empty:
        return pd.DataFrame()

    columns = [col for col in ["R", "H", "HR", "BB", "SO"] if col in df.columns]
    if not columns:
        return pd.DataFrame({"metric": [], "value": []})

    totals = df[columns].sum(numeric_only=True)
    return totals.rename_axis("metric").reset_index(name="value")
