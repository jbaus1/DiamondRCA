"""Data loading utilities for CSV and Parquet."""

from pathlib import Path

import pandas as pd


def load_csv(path: str | Path, **kwargs) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    return pd.read_csv(Path(path), **kwargs)


def load_parquet(path: str | Path, **kwargs) -> pd.DataFrame:
    """Load a Parquet file into a DataFrame."""
    return pd.read_parquet(Path(path), **kwargs)
