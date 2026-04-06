"""Data saving utilities for CSV and Parquet."""

from pathlib import Path

import pandas as pd


def save_csv(df: pd.DataFrame, path: str | Path, index: bool = False, **kwargs) -> Path:
    """Save a DataFrame to CSV and return the output path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=index, **kwargs)
    return out


def save_parquet(df: pd.DataFrame, path: str | Path, index: bool = False, **kwargs) -> Path:
    """Save a DataFrame to Parquet and return the output path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=index, **kwargs)
    return out
